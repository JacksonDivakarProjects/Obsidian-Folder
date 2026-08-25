A from-scratch, de-identified re-derivation of a real production PySpark snowball pipeline, built for [[ARR Bridge Course - Chapter 4|Chapter 4]]'s running example: **Thornfield Veterinary Group**, a fictional multi-practice veterinary care provider. Every table, column, and flag name below is generic — no company-specific naming, internal system prefixes, branded product terms, or real file paths from the original system. This note is the durable reference; Chapter 4's lessons teach the concepts and point back here rather than to any external notebook.

## The grain and the raw facts

**Grain: `dim_pet_id` × `dim_client_id` × `dim_practice_id`** — a pet (the entity receiving care), its owning client (the account holder), and the practice (branch) where care happened. Not a strict hierarchy — a pet can be seen at more than one practice over its lifetime — so all three keys travel together through every stage rather than nesting the way customer → product → service does elsewhere in this vault.

**`fact_visit_transaction`** — one row per billed transaction:

| Column | Meaning |
|---|---|
| `dim_pet_id`, `dim_client_id`, `dim_practice_id` | The grain. |
| `transaction_id` | Primary key. |
| `transaction_month` | First day of the month the transaction posted in. |
| `revenue` | Dollar amount of this transaction. |
| `is_wellness_plan_transaction` | 1 if this visit was covered by a prepaid wellness plan (so there's no separate fee-for-service charge that month even though care happened), else 0. |
| `is_inter_practice` | 1 if this transaction is an internal transfer between practices rather than real client revenue — excluded from every metric below. |

**`dim_calendar`** — the same calendar dimension used throughout this vault: one row per day, `month_roll` giving that day's first-of-month.

## Stage 1 — Standardize and scaffold (both directions)

This is the same standardize-then-scaffold pattern as [[LTM Snowball Script (No End Dates, Monthly Grain)|LTM Snowball Script]], with one addition: the scaffold extends **forward**, not just across the report window, so a pet that goes quiet still has rows to evaluate afterward — that forward buffer is what Lesson 2 builds the grace-period logic on.

```python
agg_revenue = spark.sql("""
    SELECT
        dim_pet_id, dim_practice_id, dim_client_id,
        transaction_month                                              AS month_roll,
        COUNT(DISTINCT CASE WHEN is_wellness_plan_transaction = 0
                             THEN transaction_id END)                   AS n_transactions,
        COUNT(DISTINCT CASE WHEN is_wellness_plan_transaction = 1
                             THEN transaction_id END)                   AS n_wellness_plan_transactions,
        SUM(CASE WHEN is_wellness_plan_transaction = 0
                  THEN revenue ELSE 0 END)                               AS fee_for_service_revenue,
        SUM(revenue)                                                    AS revenue
    FROM fact_visit_transaction
    WHERE is_inter_practice = 0
    GROUP BY dim_pet_id, dim_practice_id, dim_client_id, transaction_month
""")

activity_range = agg_revenue.groupBy("dim_pet_id", "dim_practice_id", "dim_client_id").agg(
    sf.min("month_roll").alias("first_txn"),
    sf.max("month_roll").alias("last_txn"),
)

# Scaffold every grain from its own first transaction through 26 months past its
# last one -- the forward buffer Lesson 2 needs to tell "one quiet month" apart
# from "actually gone."
scaffold = (
    dim_calendar.select("month_roll")
    .join(activity_range, how="cross")
    .where(
        (sf.col("month_roll") >= sf.col("first_txn")) &
        (sf.col("month_roll") <= sf.expr("add_months(last_txn, 26)"))
    )
    .select("dim_pet_id", "dim_practice_id", "dim_client_id", "month_roll")
)

stg_pet_monthly = scaffold.join(
    agg_revenue, on=["dim_pet_id", "dim_practice_id", "dim_client_id", "month_roll"], how="left"
).fillna(0, subset=["n_transactions", "n_wellness_plan_transactions", "fee_for_service_revenue"])
```

## Stage 2 — Dual rolling windows: L12M and L14M

Two rolling sums, same metric, two different widths — the mechanism Lesson 2 is built around.

```python
grain = Window.partitionBy("dim_pet_id", "dim_practice_id", "dim_client_id").orderBy("month_roll")

source_fact = (
    stg_pet_monthly
    .withColumn("l12m_revenue", sf.sum("fee_for_service_revenue").over(grain.rowsBetween(-11, 0)))
    .withColumn("l12m_transactions", sf.sum("n_transactions").over(grain.rowsBetween(-11, 0)))
    .withColumn("l14m_revenue", sf.sum("fee_for_service_revenue").over(grain.rowsBetween(-13, 0)))
    .withColumn("l14m_transactions", sf.sum("n_transactions").over(grain.rowsBetween(-13, 0)))
)
```

`rowsBetween(-11, 0)` / `rowsBetween(-13, 0)` only give a true 12- or 14-*calendar-month* sum because `stg_pet_monthly` is already dense from Stage 1 — the exact "LAG/rolling-window is safe once the data has no gaps" rule from [[LTM Snowball Script (No End Dates, Monthly Grain)|LTM Snowball Script]], demonstrated rather than just stated.

## Stage 3 — Lifecycle: join, lapse, churn, death

Explicit lifecycle event dates (`churn_date`, `death_date`, sourced from `dim_client`/`dim_pet`) combine with the behavioral L12M/L14M signal to classify every grain-month — the three-tier "gone" classification Lesson 3 covers in full.

```python
lifecycle_dates = spark.sql("""
    SELECT
        p.dim_pet_id,
        MIN(sf.month_roll)                                             AS join_month,
        add_months(MAX(sf.month_roll), 1)                              AS lapse_month,
        DATE_TRUNC('MONTH', p.death_date)                              AS death_month,
        DATE_TRUNC('MONTH', c.churn_date)                              AS churn_month
    FROM source_fact sf
    JOIN dim_pet p ON p.dim_pet_id = sf.dim_pet_id
    LEFT JOIN dim_client c ON c.dim_client_id = p.latest_client_id
    WHERE sf.l12m_transactions <> 0
    GROUP BY p.dim_pet_id, p.death_date, c.churn_date
""")

# Behavioral signal: fully lapsed (quiet in both windows) vs. partially lapsed
# (quiet in L12M but the L14M buffer still shows recent life) -- see Lesson 2.
lapse_flags = source_fact.join(lifecycle_dates, "dim_pet_id", "left").select(
    "*",
    sf.expr("month_roll = lapse_month AND l14m_transactions = 0").cast("int").alias("is_fully_lapsed"),
    sf.expr("month_roll = lapse_month AND l14m_transactions > 0").cast("int").alias("is_partially_lapsed"),
)

# Precedence: death overrides churn overrides plain lapse -- ordering is
# load-bearing here, the same CASE-arm discipline as the 8-bucket cascade.
lifecycle_flags = lapse_flags.withColumn(
    "gone_reason",
    sf.expr("""
        CASE
            WHEN (is_fully_lapsed = 1 OR is_partially_lapsed = 1) AND month_roll >= death_month
                THEN 'death'
            WHEN (is_fully_lapsed = 1 OR is_partially_lapsed = 1) AND month_roll >= churn_month
                THEN 'churn'
            WHEN is_fully_lapsed = 1 OR is_partially_lapsed = 1
                THEN 'lapse'
            ELSE NULL
        END
    """),
)
```

## Stage 4 — Expansion and contraction (month-over-month and year-over-year)

Same `LAG` technique as Stage 2's rolling sums, applied to the L12M figure itself to get a delta — safe for the same reason (dense input).

```python
deltas = source_fact.withColumn(
    "lm_l12m_revenue", sf.lag("l12m_revenue", 1).over(grain)
).withColumn(
    "ltm_l12m_revenue", sf.lag("l12m_revenue", 12).over(grain)
).fillna(0, subset=["lm_l12m_revenue", "ltm_l12m_revenue"]).withColumn(
    "lm_revenue_delta", sf.col("l12m_revenue") - sf.col("lm_l12m_revenue")
).withColumn(
    "ltm_revenue_delta", sf.col("l12m_revenue") - sf.col("ltm_l12m_revenue")
)
```

## Stage 5 — Signed dollar buckets

The same `bucket_amounts` idea from every SQL note in this folder, at production granularity: each named bucket gets the delta only when its own condition fires, `0` everywhere else, so every row sums back to the true change. A representative slice — the remaining buckets (reactivation, partial reactivation, deactivation, partial deactivation, lapse, partial lapse, death, churn) all follow the identical shape, one `CASE WHEN <condition> THEN <signed amount> ELSE 0 END` per bucket:

```python
bucket_amounts = deltas.join(lifecycle_flags.select("dim_pet_id", "month_roll", "gone_reason"),
                              ["dim_pet_id", "month_roll"], "left").select(
    "dim_pet_id", "dim_practice_id", "dim_client_id", "month_roll",
    sf.col("lm_l12m_revenue").alias("bop_revenue"),
    sf.col("l12m_revenue").alias("eop_revenue"),
    sf.when(sf.col("lm_revenue_delta") > 0, sf.col("lm_revenue_delta")).otherwise(0).alias("expansion"),
    sf.when(sf.col("lm_revenue_delta") < 0, sf.col("lm_revenue_delta")).otherwise(0).alias("contraction"),
    sf.when(sf.col("gone_reason") == "lapse", -sf.col("lm_l12m_revenue")).otherwise(0).alias("lapse_revenue"),
    sf.when(sf.col("gone_reason") == "churn", -sf.col("lm_l12m_revenue")).otherwise(0).alias("churn_revenue"),
    sf.when(sf.col("gone_reason") == "death", -sf.col("lm_l12m_revenue")).otherwise(0).alias("death_revenue"),
    # ... reactivation, partial reactivation, deactivation, partial deactivation,
    #     partial lapse: identical CASE WHEN shape, one condition each.
    # A final catch-all, computed last -- see Lesson 5:
    sf.when(
        (sf.col("lm_revenue_delta") != 0) &
        (sf.col("gone_reason").isNull()) &
        (sf.col("lm_revenue_delta") <= 0) & (sf.col("lm_revenue_delta") >= 0),  # placeholder for "no bucket matched"
        sf.col("lm_revenue_delta")
    ).otherwise(0).alias("unclassified_balance"),
)
```

## Stage 6 — One table, two periods

Instead of two separate tables (the choice the SQL Pipeline Patterns notes made), stack the monthly (`LM`) and rolling-12-month (`LTM`) versions of the same metrics into one table with a discriminator column — see Lesson 4 for the trade-off.

```python
rpt_snowball = lm_metrics.withColumn("period_type", sf.lit("LM")).unionByName(
    ltm_metrics.withColumn("period_type", sf.lit("LTM"))
)
```

## Stage 7 — Attach dimensions at BOP, then aggregate

Dimension attributes that change over time (`is_insured`, `hub_or_spoke`, `is_partnered`) are joined at the **BOP month**, not "now" — see Lesson 4 for why this matters.

```python
bop_month_expr = sf.expr("""
    CASE WHEN period_type = 'LM'  THEN add_months(month_roll, -1)
         WHEN period_type = 'LTM' THEN add_months(month_roll, -12)
    END
""")

enriched = (
    rpt_snowball.withColumn("bop_month", bop_month_expr)
    .join(dim_pet, "dim_pet_id", "left")
    .join(dim_practice_monthly, (sf.col("dim_practice_id") == dim_practice_monthly.dim_practice_id) &
                                 (sf.col("bop_month") == dim_practice_monthly.month_roll), "left")
)

report_aggregated = enriched.groupBy(
    "species", "is_insured", "hub_or_spoke", "is_partnered", "month_roll", "period_type"
).agg(sf.sum("eop_revenue").alias("eop_revenue"), sf.sum("expansion").alias("expansion"))  # + every other bucket
```

## Stage 8 — Reconciliation, with tolerance and triage

```python
recon = (
    bucket_amounts.groupBy("dim_pet_id", "month_roll")
    .agg(
        sf.sum("bop_revenue").alias("bop_revenue"),
        (sf.sum("expansion") + sf.sum("contraction") + sf.sum("lapse_revenue")
         + sf.sum("churn_revenue") + sf.sum("death_revenue")
         + sf.sum("unclassified_balance")).alias("total_delta"),
        sf.sum("eop_revenue").alias("actual_eop"),
    )
    .withColumn("calculated_eop", sf.col("bop_revenue") + sf.col("total_delta"))
    .withColumn("reconciliation_diff", sf.col("calculated_eop") - sf.col("actual_eop"))
    .where(sf.abs("reconciliation_diff") > 0.01)
    .orderBy(sf.abs("reconciliation_diff").desc())
    .limit(20)
)
```

## 🔗 Related Notes
- [[ARR Bridge Course - Chapter 4|Chapter 4]] — the course this code illustrates, lesson by lesson.
- [[LTM Snowball Script (No End Dates, Monthly Grain)|LTM Snowball Script]] — the scaffold-and-window pattern Stages 1-2 extend.
- [[Bucket Cascade Logic|Bucket Cascade Logic]] — the CASE-arm precedence discipline Stage 3 and Stage 5 both reuse.
- [[Snowball|Snowball]] — hub note for this area.

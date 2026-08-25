> One of three reference patterns in this folder. This one: **your data has real contract start/end dates.** For situations with no end date at all — just recurring monthly actuals — see [[LTM Snowball Script (No End Dates, Monthly Grain)|LTM Snowball Script]] (rolling 12-month comparison) or [[YTD Snowball Script (No End Dates, Monthly Grain)|YTD Snowball Script]] (anchored to last calendar year-end).

Everything else in this folder either teaches the concept ([[Bucket Cascade Logic|Bucket Cascade Logic]]) or hands you the cascade assuming you already have two clean inputs — `source_fact` and `activity_dates` — sitting there ready to go ([[ARR Snowball Template (ANSI SQL, Portable)|ARR Snowball Template]]). This note is the missing first half: a realistic mini warehouse — dimension tables plus one source/fact table, the way a real data warehouse is actually laid out — and the pipeline that turns it into those two clean inputs, before the cascade you already know takes over.

Five steps, theory before code at each one, then the whole thing assembled at the end.

```
DIMS                dim_customer, dim_product, dim_service, dim_calendar
SOURCE              source_contracts   (one row per contract, referencing the dims by key)
  │
  ▼  STEP 1 — STANDARDIZE
STAGING             stg_contracts   (date sentinels normalized)
  │
  ▼  STEP 2 — SNAPSHOT  (using dim_calendar, not a generated calendar)
FACT                source_fact     (one row per grain per month — the
  │                                  input every other note in this folder assumes)
  ▼  STEP 3 — LIFECYCLE DATES
                     activity_dates
  ▼  STEP 4 — THE CASCADE  (unchanged from the Template, including the date cross-check)
BRIDGE              8 buckets, BOP, EOP, GRR, NRR
  ▼  STEP 5 — ATTACH DIMENSIONS  (names joined in only now — never before the cascade)
REPORT              the bridge, with real customer/product/service names
```

## The schema

A real subscription warehouse doesn't hand you one flat table — it hands you a handful of dimension tables and a source table that references them by key. That's what this section models, kept to exactly what a snowball needs and nothing more.

**`dim_customer`** — one row per customer:

| Column | Meaning |
|---|---|
| `customer_id` | Primary key. |
| `customer_name` | Display name. |

**`dim_product`** — one row per product:

| Column | Meaning |
|---|---|
| `product_id` | Primary key. |
| `product_name` | Display name. |

**`dim_service`** — one row per service, rolling up to a product (the customer → product → service grain hierarchy from [[Bucket Cascade Logic|Bucket Cascade Logic]]):

| Column | Meaning |
|---|---|
| `service_id` | Primary key. |
| `product_id` | Which product this service belongs to. |
| `service_name` | Display name. |

**`dim_calendar`** — a real calendar table, one row per day, with the month-end already precomputed (the standard way a warehouse avoids repeating date arithmetic in every query):

| Column | Meaning |
|---|---|
| `calendar_date` | Primary key — one row per day. |
| `month_end_date` | The last calendar day of `calendar_date`'s month. |

**`source_contracts`** — the source/fact table: one row per contract, referencing the dimensions above by key rather than storing names directly (exactly how a real fact table is built):

| Column | Meaning |
|---|---|
| `contract_id` | Primary key. |
| `customer_id` | FK → `dim_customer`. |
| `product_id` | FK → `dim_product`. |
| `service_id` | FK → `dim_service`. |
| `start_date` | When this contract began. |
| `end_date` | When it ended. In real data this column is rarely clean — see below. |
| `arr_amount` | The annual value of this contract row. |

The one thing that's reliably messy even in an otherwise tidy source table: **"still active" gets written inconsistently**. Some rows use `NULL` for `end_date`, others use a far-future sentinel like `9999-12-31` — sometimes both conventions exist in the same table because two people loaded it at different times. See [[Deriving Start and End Dates|Deriving Start and End Dates]] for the full picture of why this happens. That's the only cleanup this pipeline does, deliberately — real pipelines also solve multi-source identity matching and non-standard pricing (usage-based, multi-year), but those are their own topics with their own lessons ([[Chapter 3/Lesson 1 - Profiling a Stranger's Dataset|Chapter 3, Lesson 1]] and [[Chapter 2/Lesson 4 - Taming Non-Standard ARR|Chapter 2, Lesson 4]]) — mixing them in here would bury the one thing this note exists to teach: **the shape of the pipeline**, real schema to finished bridge.

## Step 1 — Standardize

Collapse every "still active" convention to one true `NULL`, once, here — so no CTE downstream ever needs to know a sentinel existed. Only `source_contracts` needs this; the dimension tables are already clean by definition.

```sql
stg_contracts AS (
    SELECT
        customer_id,
        product_id,
        service_id,
        start_date,
        CASE WHEN end_date >= '2999-01-01' THEN NULL ELSE end_date END AS end_date,
        arr_amount
    FROM source_contracts
),
```

## Step 2 — Snapshot generation

This is [[Steps in Building an ARR Snowball|the 5-step mental model]]'s Step 2, made concrete: a contract is a *continuous span* (`start_date` to `end_date`), but a snowball needs *discrete monthly snapshots* to compare month to month. So every contract has to be checked against a fixed list of month-end dates: "were you active on this date, and for how much?"

**The calendar — read from `dim_calendar`, not generated.** This is the realistic version: a warehouse's calendar dimension already has every month-end precomputed, so getting the list is a plain lookup, not a recursive trick.

**Widen the range by 12 months before you filter.** The cascade needs a BOP for the *first* reporting month too, and that BOP lives 12 months before `@report_start`. If `month_starts` only covers `@report_start`..`@report_end`, `source_fact` never gets built for that earlier month, and the first reporting month's BOP silently comes out as 0 for customers who were genuinely active the whole time. Pull a year of extra history here; the cascade's own `WHERE` clause (Step 3) already restricts the *final* output back down to the real reporting range, so nothing extra leaks into the report.

```sql
month_starts AS (
    SELECT DISTINCT DATEFROMPARTS(YEAR(month_end_date), MONTH(month_end_date), 1) AS month_roll
    FROM dim_calendar
    WHERE month_end_date BETWEEN DATEADD(MONTH, -12, @report_start) AND @report_end
),
```

`month_roll` is the first calendar day of the month here, not the last — the same convention the LTM note uses, derived from the same `dim_calendar` column just for consistency between the two notes.

**The active-on-date test** — alive if it started on or before the snapshot and hasn't ended yet:

```sql
source_fact AS (
    SELECT
        m.month_roll,
        c.customer_id,
        c.product_id,
        c.service_id,
        SUM(c.arr_amount) AS arr
    FROM month_starts m
    JOIN stg_contracts c
      ON c.start_date <= m.month_roll
     AND (c.end_date > m.month_roll OR c.end_date IS NULL)
    GROUP BY m.month_roll, c.customer_id, c.product_id, c.service_id
),
```

One real consequence of this switch, worth knowing rather than tripping over later: the test now checks "active on the 1st of the month" instead of "active on the last day of the month." A contract starting mid-month — say the 15th — now first counts as active the *following* month (the 1st is still before its `start_date`), where the month-end version would have counted it in its actual start month (the 15th is before month-end). If your business reports EOP-style ("did this show up in this month's exit ARR"), month-end is the more standard test; if you'd rather every month key line up with a plain calendar-first-of-month label throughout, this is the tradeoff that comes with it.

That's it — `source_fact` now has exactly the shape every other note in this folder builds on: one row per grain per month.

## Step 3 — Lifecycle dates

Collapse `stg_contracts` to one row per grain: earliest start, latest end (or `NULL` if any span is still open). This feeds the cascade's date cross-check in Step 4 — the stage that stops a late invoice or a billing correction from being misread as a new logo or a churn. That check is binary (confirmed or demoted); [[ARR Bridge Course - Chapter 4|Chapter 4]] extends the same idea into a real multi-way classification — see [[Lesson 3 - Three Tiers of Gone|Lesson 3]].

```sql
activity_dates AS (
    SELECT
        customer_id, product_id, service_id,
        MIN(start_date) AS first_start,
        MAX(start_date) AS latest_start,
        CASE WHEN SUM(CASE WHEN end_date IS NULL THEN 1 ELSE 0 END) > 0
             THEN NULL ELSE MAX(end_date) END AS latest_end
    FROM stg_contracts
    GROUP BY customer_id, product_id, service_id
),
```

## Step 4 — The cascade

Exactly what you already know from [[ARR Snowball Template (ANSI SQL, Portable)|ARR Snowball Template]] and [[Bucket Cascade Logic|Bucket Cascade Logic]] — unchanged, including the lifecycle-date cross-check. The only difference here is that `source_fact` and `activity_dates` come from Steps 2–3 above instead of an already-clean external table. Notice `dim_customer`, `dim_product`, and `dim_service` haven't been touched yet — on purpose.

```sql
service_grain AS (
    SELECT
        COALESCE(eop.month_roll, DATEADD(MONTH, 12, bop.month_roll)) AS month_roll,
        COALESCE(eop.customer_id, bop.customer_id)                   AS customer_id,
        COALESCE(eop.product_id,  bop.product_id)                    AS product_id,
        COALESCE(eop.service_id,  bop.service_id)                    AS service_id,
        COALESCE(bop.arr, 0)                                         AS bop_arr,
        COALESCE(eop.arr, 0)                                         AS eop_arr
    FROM source_fact AS eop
    FULL OUTER JOIN source_fact AS bop
      ON  bop.month_roll  = DATEADD(MONTH, -12, eop.month_roll)
      AND bop.customer_id = eop.customer_id
      AND bop.product_id  = eop.product_id
      AND bop.service_id  = eop.service_id
    WHERE COALESCE(eop.month_roll, DATEADD(MONTH, 12, bop.month_roll))
              BETWEEN @report_start AND @report_end
),

plan_grain AS (
    SELECT month_roll, customer_id, product_id,
           SUM(bop_arr) AS bop_arr, SUM(eop_arr) AS eop_arr
    FROM service_grain
    GROUP BY month_roll, customer_id, product_id
),

customer_grain AS (
    SELECT month_roll, customer_id,
           SUM(bop_arr) AS bop_arr, SUM(eop_arr) AS eop_arr
    FROM plan_grain
    GROUP BY month_roll, customer_id
),

-- Buckets 1 & 2: Customer Churn / New Customer
customer_flags AS (
    SELECT month_roll, customer_id, bop_arr, eop_arr,
        CASE
            WHEN bop_arr > 0 AND eop_arr = 0 THEN 'customer_churn'
            WHEN bop_arr = 0 AND eop_arr > 0 THEN 'new_customer'
            ELSE NULL
        END AS customer_claim
    FROM customer_grain
),

-- Buckets 3 & 4: Plan Churn / Cross-sell (excludes anything customer_flags already claimed)
plan_flags AS (
    SELECT p.month_roll, p.customer_id, p.product_id, p.bop_arr, p.eop_arr, c.customer_claim,
        CASE
            WHEN c.customer_claim IS NOT NULL           THEN NULL
            WHEN p.bop_arr > 0 AND p.eop_arr = 0        THEN 'plan_churn'
            WHEN p.bop_arr = 0 AND p.eop_arr > 0        THEN 'cross_sell'
            ELSE NULL
        END AS plan_claim
    FROM plan_grain AS p
    JOIN customer_flags AS c
      ON c.month_roll = p.month_roll AND c.customer_id = p.customer_id
),

-- Buckets 5-8: Service Cross-sell / Service Churn / Downsell / Upsell.
-- The CASE arms ARE the cascade -- first match wins, ordering is load-bearing.
service_flags AS (
    SELECT s.month_roll, s.customer_id, s.product_id, s.service_id,
           s.bop_arr, s.eop_arr, pf.customer_claim, pf.plan_claim,
        CASE
            WHEN pf.customer_claim IS NOT NULL             THEN pf.customer_claim
            WHEN pf.plan_claim     IS NOT NULL             THEN pf.plan_claim
            WHEN s.bop_arr = 0 AND s.eop_arr > 0           THEN 'service_cross_sell'
            WHEN s.bop_arr > 0 AND s.eop_arr = 0           THEN 'service_churn'
            WHEN s.bop_arr > 0 AND s.eop_arr > 0
                 AND s.eop_arr < s.bop_arr                 THEN 'downsell'
            WHEN s.bop_arr > 0 AND s.eop_arr > 0
                 AND s.eop_arr > s.bop_arr                 THEN 'upsell'
            ELSE NULL
        END AS claimed_by
    FROM service_grain AS s
    JOIN plan_flags AS pf
      ON pf.month_roll = s.month_roll AND pf.customer_id = s.customer_id AND pf.product_id = s.product_id
),

-- Cross-check every claim against real lifecycle dates, so billing noise
-- (credits, promos, late invoices) isn't misread as a genuine new logo or churn.
-- EOMONTH(sf.month_roll, -12) -- not DATEADD(MONTH, -12, sf.month_roll) -- since
-- month_roll is the 1st of the month here; EOMONTH's offset form normalizes
-- both bounds to real month-end dates, keeping the window exactly 12 months
-- wide (and immune to leap-February landing a day short).
validated_flags AS (
    SELECT sf.month_roll, sf.customer_id, sf.product_id, sf.service_id,
           sf.bop_arr, sf.eop_arr, sf.claimed_by AS raw_claim,
        CASE
            WHEN sf.claimed_by IN ('new_customer', 'cross_sell', 'service_cross_sell')
                THEN CASE
                        WHEN ad.customer_id IS NULL THEN 1
                        WHEN ad.latest_start >  EOMONTH(sf.month_roll, -12)
                         AND ad.latest_start <= EOMONTH(sf.month_roll) THEN 1
                        ELSE 0
                     END
            WHEN sf.claimed_by IN ('customer_churn', 'plan_churn', 'service_churn')
                THEN CASE
                        WHEN ad.customer_id IS NULL THEN 1
                        WHEN ad.latest_end IS NULL THEN 0
                        WHEN ad.latest_end >  EOMONTH(sf.month_roll, -12)
                         AND ad.latest_end <= EOMONTH(sf.month_roll) THEN 1
                        ELSE 0
                     END
            ELSE 1
        END AS date_confirmed
    FROM service_flags AS sf
    LEFT JOIN activity_dates AS ad
      ON ad.customer_id = sf.customer_id AND ad.product_id = sf.product_id AND ad.service_id = sf.service_id
),

-- Demote any unconfirmed claim to the movement it actually is. Dollars are
-- preserved either way, so the bridge still ties out.
resolved_flags AS (
    SELECT month_roll, customer_id, product_id, service_id, bop_arr, eop_arr, raw_claim, date_confirmed,
        CASE
            WHEN raw_claim IS NULL   THEN NULL
            WHEN date_confirmed = 1  THEN raw_claim
            WHEN eop_arr > bop_arr   THEN 'upsell'
            WHEN eop_arr < bop_arr   THEN 'downsell'
            ELSE NULL
        END AS claimed_by
    FROM validated_flags
),

-- One signed dollar column per bucket. Exactly one is non-zero per row.
bucket_amounts AS (
    SELECT month_roll, customer_id, product_id, service_id, bop_arr, eop_arr,
        CASE WHEN claimed_by = 'customer_churn'     THEN -bop_arr          ELSE 0 END AS customer_churn,
        CASE WHEN claimed_by = 'new_customer'       THEN  eop_arr          ELSE 0 END AS new_customer,
        CASE WHEN claimed_by = 'plan_churn'         THEN -bop_arr          ELSE 0 END AS plan_churn,
        CASE WHEN claimed_by = 'cross_sell'         THEN  eop_arr          ELSE 0 END AS cross_sell,
        CASE WHEN claimed_by = 'service_cross_sell' THEN  eop_arr          ELSE 0 END AS service_cross_sell,
        CASE WHEN claimed_by = 'service_churn'      THEN -bop_arr          ELSE 0 END AS service_churn,
        CASE WHEN claimed_by = 'downsell'           THEN eop_arr - bop_arr ELSE 0 END AS downsell,
        CASE WHEN claimed_by = 'upsell'             THEN eop_arr - bop_arr ELSE 0 END AS upsell
    FROM resolved_flags
)
```

## Step 5 — Attach dimensions

Only now — after `bucket_amounts` already exists at the grain you want to report — do the dimension tables get joined in, purely to swap keys for names. This is the same rule from [[Dimensional Snowball Example (SQL)|Dimensional Snowball Example (SQL)]]: joining dims *before* the cascade risks fan-out during the `FULL OUTER JOIN` in Step 4 (a customer with two rows in a dim table would double its BOP/EOP arr); joining after is always safe, because the cascade has already resolved to exactly one row per grain per month.

```sql
SELECT
    ba.month_roll,
    dc.customer_name,
    dp.product_name,
    ds.service_name,
    ba.bop_arr, ba.eop_arr,
    ba.customer_churn, ba.new_customer, ba.plan_churn, ba.cross_sell,
    ba.service_cross_sell, ba.service_churn, ba.downsell, ba.upsell
FROM bucket_amounts ba
JOIN dim_customer dc ON dc.customer_id = ba.customer_id
JOIN dim_product  dp ON dp.product_id  = ba.product_id
JOIN dim_service  ds ON ds.service_id  = ba.service_id;
```

## Output and validation

```sql
SELECT
    month_roll,
    SUM(bop_arr)             AS bop_arr,
    SUM(customer_churn)      AS customer_churn,
    SUM(new_customer)        AS new_customer,
    SUM(plan_churn)          AS plan_churn,
    SUM(cross_sell)          AS cross_sell,
    SUM(service_cross_sell)  AS service_cross_sell,
    SUM(service_churn)       AS service_churn,
    SUM(downsell)            AS downsell,
    SUM(upsell)              AS upsell,
    SUM(bop_arr) + SUM(customer_churn) + SUM(plan_churn) + SUM(service_churn) + SUM(downsell) AS grr,
    SUM(bop_arr) + SUM(customer_churn) + SUM(plan_churn) + SUM(service_churn) + SUM(downsell)
                 + SUM(upsell) + SUM(cross_sell) + SUM(service_cross_sell) + SUM(new_customer) AS nrr,
    SUM(eop_arr)             AS eop_arr,
    SUM(eop_arr) - ( SUM(bop_arr) + SUM(customer_churn) + SUM(new_customer)
                   + SUM(plan_churn) + SUM(cross_sell) + SUM(service_cross_sell)
                   + SUM(service_churn) + SUM(downsell) + SUM(upsell) )        AS bridge_close
FROM bucket_amounts
GROUP BY month_roll
ORDER BY month_roll;
```

**Validation — run right after, expect zero rows from each:**

```sql
-- Check 1: tie-out. bridge_close must be 0.00 on every row of the output above.
SELECT * FROM arr_snowball_output WHERE ROUND(bridge_close, 2) <> 0.00;

-- Check 2: any row that moved without being claimed by any bucket.
SELECT month_roll, customer_id, product_id, service_id, bop_arr, eop_arr
FROM resolved_flags
WHERE claimed_by IS NULL AND bop_arr <> eop_arr;
```

If either check returns rows, work backward: a `source_fact` duplicate (Step 2) shows up here the same as a bad grain-key normalization (Step 1) — see [[Chapter 2/Lesson 6 - Testing Your Snowball Like a Data Engineer|Chapter 2, Lesson 6]] for the full diagnostic table.

---

## The full assembled script

Copy this whole block. Edit only `@report_start`, `@report_end`, and the four table names at the top if yours are named differently.

```sql
-- ============================================================================
-- ARR SNOWBALL — REAL SCHEMA TO BRIDGE
-- dim_customer, dim_product, dim_service, dim_calendar, source_contracts
-- -> standardize -> monthly snapshots (month_roll = first of month) ->
-- lifecycle dates -> the cascade (with date cross-check) -> bridge ->
-- dimensions attached last.
-- Dialect: T-SQL. See ARR Snowball Template for the date-function swaps
-- needed on Snowflake/BigQuery/Postgres/Databricks.
-- ============================================================================

DECLARE @report_start date = '2024-01-01';
DECLARE @report_end   date = '2025-12-01';

WITH

-- ---------- STEP 1: STANDARDIZE ----------
stg_contracts AS (
    SELECT
        customer_id, product_id, service_id, start_date,
        CASE WHEN end_date >= '2999-01-01' THEN NULL ELSE end_date END AS end_date,
        arr_amount
    FROM source_contracts                                            -- <<< EDIT THIS
),

-- ---------- STEP 2: SNAPSHOT GENERATION ----------
month_starts AS (
    SELECT DISTINCT DATEFROMPARTS(YEAR(month_end_date), MONTH(month_end_date), 1) AS month_roll
    FROM dim_calendar                                                -- <<< EDIT THIS
    WHERE month_end_date BETWEEN DATEADD(MONTH, -12, @report_start) AND @report_end
),
source_fact AS (
    SELECT m.month_roll, c.customer_id, c.product_id, c.service_id, SUM(c.arr_amount) AS arr
    FROM month_starts m
    JOIN stg_contracts c
      ON c.start_date <= m.month_roll
     AND (c.end_date > m.month_roll OR c.end_date IS NULL)
    GROUP BY m.month_roll, c.customer_id, c.product_id, c.service_id
),

-- ---------- STEP 3: LIFECYCLE DATES ----------
activity_dates AS (
    SELECT customer_id, product_id, service_id,
        MIN(start_date) AS first_start,
        MAX(start_date) AS latest_start,
        CASE WHEN SUM(CASE WHEN end_date IS NULL THEN 1 ELSE 0 END) > 0
             THEN NULL ELSE MAX(end_date) END AS latest_end
    FROM stg_contracts
    GROUP BY customer_id, product_id, service_id
),

-- ---------- STEP 4: THE CASCADE ----------
service_grain AS (
    SELECT
        COALESCE(eop.month_roll, DATEADD(MONTH, 12, bop.month_roll)) AS month_roll,
        COALESCE(eop.customer_id, bop.customer_id)                   AS customer_id,
        COALESCE(eop.product_id,  bop.product_id)                    AS product_id,
        COALESCE(eop.service_id,  bop.service_id)                    AS service_id,
        COALESCE(bop.arr, 0)                                         AS bop_arr,
        COALESCE(eop.arr, 0)                                         AS eop_arr
    FROM source_fact AS eop
    FULL OUTER JOIN source_fact AS bop
      ON  bop.month_roll  = DATEADD(MONTH, -12, eop.month_roll)
      AND bop.customer_id = eop.customer_id
      AND bop.product_id  = eop.product_id
      AND bop.service_id  = eop.service_id
    WHERE COALESCE(eop.month_roll, DATEADD(MONTH, 12, bop.month_roll))
              BETWEEN @report_start AND @report_end
),
plan_grain AS (
    SELECT month_roll, customer_id, product_id, SUM(bop_arr) AS bop_arr, SUM(eop_arr) AS eop_arr
    FROM service_grain GROUP BY month_roll, customer_id, product_id
),
customer_grain AS (
    SELECT month_roll, customer_id, SUM(bop_arr) AS bop_arr, SUM(eop_arr) AS eop_arr
    FROM plan_grain GROUP BY month_roll, customer_id
),
customer_flags AS (
    SELECT month_roll, customer_id, bop_arr, eop_arr,
        CASE WHEN bop_arr > 0 AND eop_arr = 0 THEN 'customer_churn'
             WHEN bop_arr = 0 AND eop_arr > 0 THEN 'new_customer'
             ELSE NULL END AS customer_claim
    FROM customer_grain
),
plan_flags AS (
    SELECT p.month_roll, p.customer_id, p.product_id, p.bop_arr, p.eop_arr, c.customer_claim,
        CASE WHEN c.customer_claim IS NOT NULL THEN NULL
             WHEN p.bop_arr > 0 AND p.eop_arr = 0 THEN 'plan_churn'
             WHEN p.bop_arr = 0 AND p.eop_arr > 0 THEN 'cross_sell'
             ELSE NULL END AS plan_claim
    FROM plan_grain AS p
    JOIN customer_flags AS c ON c.month_roll = p.month_roll AND c.customer_id = p.customer_id
),
service_flags AS (
    SELECT s.month_roll, s.customer_id, s.product_id, s.service_id, s.bop_arr, s.eop_arr,
           pf.customer_claim, pf.plan_claim,
        CASE WHEN pf.customer_claim IS NOT NULL THEN pf.customer_claim
             WHEN pf.plan_claim IS NOT NULL THEN pf.plan_claim
             WHEN s.bop_arr = 0 AND s.eop_arr > 0 THEN 'service_cross_sell'
             WHEN s.bop_arr > 0 AND s.eop_arr = 0 THEN 'service_churn'
             WHEN s.bop_arr > 0 AND s.eop_arr > 0 AND s.eop_arr < s.bop_arr THEN 'downsell'
             WHEN s.bop_arr > 0 AND s.eop_arr > 0 AND s.eop_arr > s.bop_arr THEN 'upsell'
             ELSE NULL END AS claimed_by
    FROM service_grain AS s
    JOIN plan_flags AS pf
      ON pf.month_roll = s.month_roll AND pf.customer_id = s.customer_id AND pf.product_id = s.product_id
),
validated_flags AS (
    SELECT sf.month_roll, sf.customer_id, sf.product_id, sf.service_id, sf.bop_arr, sf.eop_arr,
           sf.claimed_by AS raw_claim,
        CASE
            WHEN sf.claimed_by IN ('new_customer', 'cross_sell', 'service_cross_sell')
                THEN CASE WHEN ad.customer_id IS NULL THEN 1
                          WHEN ad.latest_start > EOMONTH(sf.month_roll, -12)
                           AND ad.latest_start <= EOMONTH(sf.month_roll) THEN 1
                          ELSE 0 END
            WHEN sf.claimed_by IN ('customer_churn', 'plan_churn', 'service_churn')
                THEN CASE WHEN ad.customer_id IS NULL THEN 1
                          WHEN ad.latest_end IS NULL THEN 0
                          WHEN ad.latest_end > EOMONTH(sf.month_roll, -12)
                           AND ad.latest_end <= EOMONTH(sf.month_roll) THEN 1
                          ELSE 0 END
            ELSE 1
        END AS date_confirmed
    FROM service_flags AS sf
    LEFT JOIN activity_dates AS ad
      ON ad.customer_id = sf.customer_id AND ad.product_id = sf.product_id AND ad.service_id = sf.service_id
),
resolved_flags AS (
    SELECT month_roll, customer_id, product_id, service_id, bop_arr, eop_arr, raw_claim, date_confirmed,
        CASE WHEN raw_claim IS NULL THEN NULL
             WHEN date_confirmed = 1 THEN raw_claim
             WHEN eop_arr > bop_arr THEN 'upsell'
             WHEN eop_arr < bop_arr THEN 'downsell'
             ELSE NULL END AS claimed_by
    FROM validated_flags
),
bucket_amounts AS (
    SELECT month_roll, customer_id, product_id, service_id, bop_arr, eop_arr,
        CASE WHEN claimed_by = 'customer_churn'     THEN -bop_arr          ELSE 0 END AS customer_churn,
        CASE WHEN claimed_by = 'new_customer'       THEN  eop_arr          ELSE 0 END AS new_customer,
        CASE WHEN claimed_by = 'plan_churn'         THEN -bop_arr          ELSE 0 END AS plan_churn,
        CASE WHEN claimed_by = 'cross_sell'         THEN  eop_arr          ELSE 0 END AS cross_sell,
        CASE WHEN claimed_by = 'service_cross_sell' THEN  eop_arr          ELSE 0 END AS service_cross_sell,
        CASE WHEN claimed_by = 'service_churn'      THEN -bop_arr          ELSE 0 END AS service_churn,
        CASE WHEN claimed_by = 'downsell'           THEN eop_arr - bop_arr ELSE 0 END AS downsell,
        CASE WHEN claimed_by = 'upsell'             THEN eop_arr - bop_arr ELSE 0 END AS upsell
    FROM resolved_flags
)

-- ---------- STEP 5: ATTACH DIMENSIONS (joined last, on purpose) ----------
SELECT
    ba.month_roll,
    dc.customer_name,
    dp.product_name,
    ds.service_name,
    ba.bop_arr, ba.eop_arr,
    ba.customer_churn, ba.new_customer, ba.plan_churn, ba.cross_sell,
    ba.service_cross_sell, ba.service_churn, ba.downsell, ba.upsell,
    ba.bop_arr + ba.customer_churn + ba.plan_churn + ba.service_churn + ba.downsell AS grr,
    ba.bop_arr + ba.customer_churn + ba.plan_churn + ba.service_churn + ba.downsell
              + ba.upsell + ba.cross_sell + ba.service_cross_sell + ba.new_customer AS nrr,
    ba.eop_arr - ( ba.bop_arr + ba.customer_churn + ba.new_customer + ba.plan_churn
                 + ba.cross_sell + ba.service_cross_sell + ba.service_churn
                 + ba.downsell + ba.upsell )                                        AS bridge_close
FROM bucket_amounts ba
JOIN dim_customer dc ON dc.customer_id = ba.customer_id                -- <<< EDIT THIS
JOIN dim_product  dp ON dp.product_id  = ba.product_id                 -- <<< EDIT THIS
JOIN dim_service  ds ON ds.service_id  = ba.service_id                 -- <<< EDIT THIS
ORDER BY ba.month_roll, dc.customer_name, dp.product_name, ds.service_name;
```

Roll this up to whatever grain you need to report at (drop the customer/product/service columns and `GROUP BY`/`SUM` the rest for a company-level bridge) — every bucket amount was already resolved at service grain in Step 4, so choosing the reporting grain is a free choice made entirely in this last query.

## 🔗 Related Notes
- [[LTM Snowball Script (No End Dates, Monthly Grain)|LTM Snowball Script (No End Dates, Monthly Grain)]] and [[YTD Snowball Script (No End Dates, Monthly Grain)|YTD Snowball Script (No End Dates, Monthly Grain)]] — the sibling patterns, for when there's no contract end date at all, just recurring monthly actuals.
- [[Steps in Building an ARR Snowball|Steps in Building an ARR Snowball]] — the 5-step mental model this whole pipeline is one worked implementation of.
- [[Deriving Start and End Dates|Deriving Start and End Dates]] — why raw `end_date` conventions are inconsistent, and the other shapes raw dates show up in.
- [[Dimensional Snowball Example (SQL)|Dimensional Snowball Example (SQL)]] — why dimension joins happen after the cascade, not before, worked through in detail.
- [[ARR Snowball Template (ANSI SQL, Portable)|ARR Snowball Template (ANSI SQL, Portable)]] — Step 4 taught stage-by-stage with the reasoning behind each design choice.
- [[Bucket Cascade Logic|Bucket Cascade Logic]] — the conceptual walkthrough with a worked multi-customer example.
- [[Chapter 2/Lesson 6 - Testing Your Snowball Like a Data Engineer|Chapter 2, Lesson 6]] — the full test suite the two validation checks above are drawn from.
- [[Snowball|Snowball]] — hub note for this area.

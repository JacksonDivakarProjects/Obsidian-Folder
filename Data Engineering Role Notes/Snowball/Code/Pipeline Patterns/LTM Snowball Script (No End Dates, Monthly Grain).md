> One of three reference patterns in this folder. This one: **your data has no contract end date at all** — just a recurring monthly actual, compared on a rolling trailing-12-month basis. For the situation where you do have real start/end dates, see [[Contract Dates Snowball Script (With Lifecycle Cross-Check)|Contract Dates Snowball Script]]. For the same no-end-date situation but anchored to the calendar year instead of rolling, see [[YTD Snowball Script (No End Dates, Monthly Grain)|YTD Snowball Script]].

## The situation this pattern is for

Picture **Driftwood Compute**, a usage-based cloud provider: customers get billed monthly for whatever compute they actually consumed. There's no contract to sign, no cancellation button, no `end_date` column anywhere in the source system. A customer "churns" simply by not using the product one month — there's no event that records it, only an absence. This is common for self-serve, credit-card-billed, usage-metered products, and it needs a different build than the contract-dates pattern in the sibling note.

The consequence: **you build the bridge by comparing this month's actual to the same customer's actual 12 months ago — not by testing a date range for "active on this date."** That difference removes the lifecycle-date stage from the pipeline you already know. It does *not* remove the need for a real calendar, though — see Step 2 below for why.

```
RAW                 raw_monthly_usage   (one row per invoice)
DIM                 dim_calendar   (the same table the sibling note uses)
  │
  ▼  STEP 1 — STANDARDIZE
STAGING             stg_monthly_arr   (one row per grain per invoiced month —
  │                                    still sparse; gaps are still gaps)
  ▼  STEP 2 — SCAFFOLD TO A DENSE MONTHLY GRAIN
FACT                source_fact   (one row per grain per month, EVERY month,
  │                                 with an explicit 0 where nothing was invoiced)
  ▼  STEP 3 — THE CASCADE   (same logic as the sibling note, minus the date cross-check —
BRIDGE                       there are no lifecycle dates left to check it against)
                    8 buckets, BOP, EOP, GRR, NRR
```

## The raw input

Two tables: the invoices, and the same calendar dimension the sibling note uses.

**`raw_monthly_usage`** — one row per invoice:

| Column | Meaning |
|---|---|
| `customer_id`, `product_id`, `service_id` | The grain. |
| `invoice_date` | The date this invoice was cut — not necessarily the 1st of the month. |
| `arr_amount` | The annualized value of this invoice (however your business turns a month of usage into an ARR figure — see [[Chapter 2/Lesson 4 - Taming Non-Standard ARR|Chapter 2, Lesson 4]] if that conversion itself is the hard part). |

**`dim_calendar`** — one row per day, month-end precomputed (see [[Contract Dates Snowball Script (With Lifecycle Cross-Check)|Contract Dates Snowball Script (With Lifecycle Cross-Check)]] for the full definition). It's needed here for the same reason it's needed there: to guarantee every month gets checked, not just the months that happen to have a row already.

Example rows for one customer, with a gap:

| customer_id | invoice_date | arr_amount |
|---|---|---|
| C100 | 2024-04-03 | 12000 |
| C100 | 2024-05-04 | 12000 |
| C100 | 2024-06-02 | 0 (no usage — often just *no row at all*) |
| C100 | 2024-07-05 | 9000 |

C100 skipped June, then came back in July at a lower amount. There is no contract to consult about what that means — the monthly actuals *are* the entire record.

## Step 1 — Standardize

Two real problems, both simple: `invoice_date` lands on whatever day billing ran (not the 1st), and a correction or late-arriving invoice can produce two rows for the same customer in the same month. Fix both at once.

```sql
stg_monthly_arr AS (
    SELECT
        customer_id,
        product_id,
        service_id,
        DATEFROMPARTS(YEAR(invoice_date), MONTH(invoice_date), 1) AS month_roll,
        SUM(arr_amount) AS arr
    FROM raw_monthly_usage
    GROUP BY customer_id, product_id, service_id,
             DATEFROMPARTS(YEAR(invoice_date), MONTH(invoice_date), 1)
),
```

`month_roll` is the first calendar day of the month, by design — not `EOMONTH`. There's no contract-span logic anywhere in this pattern that needs a period-end date, so the plainer key wins.

`stg_monthly_arr` is still **sparse** at this point — it only has a row where an invoice actually happened. That's exactly the gap you'd expect: it means the next step can't just read this table as-is.

## Step 2 — Scaffold to a dense monthly grain

This is the step the sibling note doesn't need, and it's the one this pattern lives or dies on. `stg_monthly_arr` only tells you about months that had an invoice — it says nothing about the months that didn't, and "didn't invoice" is exactly the signal this whole pattern depends on to detect churn. Left as-is, a customer who goes quiet for a stretch spanning both "this month" and "12 months ago" produces **no row at all**, anywhere — not flagged as churn, not shown as a $0, just silently missing from the output. The fix is the standard one for turning a sparse event table into a reliable time series: build every (month, grain) combination that *should* exist, then `LEFT JOIN` the actual invoices onto it and fill the gaps with 0.

```sql
grain_keys AS (
    SELECT DISTINCT customer_id, product_id, service_id
    FROM stg_monthly_arr
),
month_roll_list AS (
    SELECT DISTINCT DATEFROMPARTS(YEAR(month_end_date), MONTH(month_end_date), 1) AS month_roll
    FROM dim_calendar
    WHERE month_end_date BETWEEN DATEADD(MONTH, -12, @report_start) AND @report_end
),
scaffold AS (
    SELECT m.month_roll, g.customer_id, g.product_id, g.service_id
    FROM month_roll_list m
    CROSS JOIN grain_keys g
),
source_fact AS (
    SELECT
        sc.month_roll, sc.customer_id, sc.product_id, sc.service_id,
        COALESCE(a.arr, 0) AS arr
    FROM scaffold sc
    LEFT JOIN stg_monthly_arr a
      ON a.month_roll = sc.month_roll
     AND a.customer_id = sc.customer_id
     AND a.product_id = sc.product_id
     AND a.service_id = sc.service_id
),
```

The 12-month lookback on `month_roll_list` matters for the same reason it matters in the sibling note: the first reporting month needs a BOP that lives 12 months earlier, and that month has to exist in `source_fact` for the cascade to find it.

One deliberate simplification: `grain_keys` is every customer/product/service combination *ever* invoiced, not scoped to when each one was actually active. That means a customer who only ever appeared in 2022 gets harmless all-zero rows scaffolded for 2024-2025 too — `bop_arr` and `eop_arr` both land on 0, which matches neither the churn nor the new-customer condition below, so it produces no false bucket claim. It's a few extra rows, not a correctness problem, and it avoids adding a "first ever seen" calculation that this pattern doesn't otherwise need.

Now `source_fact` is dense — one row per grain per month, every month, exactly like the sibling note's `source_fact`, just built by filling gaps instead of testing a date range.

## Step 3 — The cascade

This is the exact same logic as [[ARR Snowball Template (ANSI SQL, Portable)|ARR Snowball Template]] and [[Bucket Cascade Logic|Bucket Cascade Logic]] through `service_flags` — copy it as-is. The theory worth slowing down on is the join that produces `bop_arr`/`eop_arr`, because it's the fix for exactly the mistake in the code you started with.

**Why `FULL OUTER JOIN ... ON month_roll = DATEADD(MONTH, -12, ...)` and not `LAG(arr, 12) OVER (ORDER BY month_roll)`:** `LAG(..., 12)` looks 12 *rows* back, not 12 *months* back. C100's June gap above means their July row is only 2 rows after April, not 3 — a `LAG(arr, 12)` computed across a full multi-year history would silently pull the wrong month the moment any customer has a gap anywhere in their history, and usage-based customers have gaps constantly. The `FULL OUTER JOIN` matches on the actual calendar date, so a gap just produces a `NULL` (correctly meaning "no invoice that month") instead of a misaligned number.

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

-- No validated_flags / resolved_flags stage here -- there is no activity_dates
-- table to cross-check against, because there are no contract dates in this
-- data at all. Read bucket_amounts directly from service_flags. This is the
-- exact shortcut the sibling note calls out as available "if you have no
-- activity_dates coverage yet" -- here, that's not a shortcut, it's the reality.
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
    FROM service_flags
)
```

## The trade-off, stated plainly

Dropping the date cross-check isn't free. In the sibling note, a customer whose ARR briefly looks like it dropped to zero gets checked against real lifecycle dates before being called "churn" — that's what catches a late invoice or a billing correction before it corrupts the bridge. Here, there's nothing to check against: **presence or absence of a monthly row is the only signal there is.** C100 from the example above will show up as `customer_churn` in June and `new_customer` in July — a "blip" — even though nothing really happened except one quiet month.

If that blip rate turns out to matter for your business, the standard fix is a **grace period**: don't call it churn on the first missing month, only after N consecutive missing months (commonly 2 or 3, matched to your typical invoice/payment-retry cycle). That needs a running "months since this grain was last seen" calculation ahead of `customer_flags`, which is a genuine extension, not a one-line tweak — worth its own note if you need it, and deliberately left out of this one so the core pattern stays the thing you actually learn first.

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
FROM service_flags
WHERE claimed_by IS NULL AND bop_arr <> eop_arr;
```

See [[Chapter 2/Lesson 6 - Testing Your Snowball Like a Data Engineer|Chapter 2, Lesson 6]] for the full diagnostic table if either check returns rows.

---

## The full assembled script

Copy this whole block. Edit only `@report_start`, `@report_end`, and the `FROM raw_monthly_usage` / `FROM dim_calendar` lines.

```sql
-- ============================================================================
-- ARR SNOWBALL — NO END DATES, MONTHLY ACTUALS
-- One raw invoice table + dim_calendar -> standardize -> scaffold to a dense
-- monthly grain -> the cascade (month vs. month-12-back) -> bridge. No
-- lifecycle-date cross-check -- there are no contract dates to build one
-- from. Dialect: T-SQL. See ARR Snowball Template for the date-function
-- swaps needed on Snowflake/BigQuery/Postgres/Databricks.
-- ============================================================================

DECLARE @report_start date = '2024-01-01';
DECLARE @report_end   date = '2025-12-01';

WITH

-- ---------- STEP 1: STANDARDIZE ----------
stg_monthly_arr AS (
    SELECT
        customer_id, product_id, service_id,
        DATEFROMPARTS(YEAR(invoice_date), MONTH(invoice_date), 1) AS month_roll,
        SUM(arr_amount) AS arr
    FROM raw_monthly_usage                                          -- <<< EDIT THIS
    GROUP BY customer_id, product_id, service_id,
             DATEFROMPARTS(YEAR(invoice_date), MONTH(invoice_date), 1)
),

-- ---------- STEP 2: SCAFFOLD TO A DENSE MONTHLY GRAIN ----------
grain_keys AS (
    SELECT DISTINCT customer_id, product_id, service_id
    FROM stg_monthly_arr
),
month_roll_list AS (
    SELECT DISTINCT DATEFROMPARTS(YEAR(month_end_date), MONTH(month_end_date), 1) AS month_roll
    FROM dim_calendar                                                -- <<< EDIT THIS
    WHERE month_end_date BETWEEN DATEADD(MONTH, -12, @report_start) AND @report_end
),
scaffold AS (
    SELECT m.month_roll, g.customer_id, g.product_id, g.service_id
    FROM month_roll_list m
    CROSS JOIN grain_keys g
),
source_fact AS (
    SELECT
        sc.month_roll, sc.customer_id, sc.product_id, sc.service_id,
        COALESCE(a.arr, 0) AS arr
    FROM scaffold sc
    LEFT JOIN stg_monthly_arr a
      ON a.month_roll = sc.month_roll
     AND a.customer_id = sc.customer_id
     AND a.product_id = sc.product_id
     AND a.service_id = sc.service_id
),

-- ---------- STEP 3: THE CASCADE ----------
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
    FROM service_flags
)

-- ---------- OUTPUT ----------
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

## 🔗 Related Notes
- [[YTD Snowball Script (No End Dates, Monthly Grain)|YTD Snowball Script (No End Dates, Monthly Grain)]] — a one-step variant of this same pipeline: same raw data and Steps 1-2, but BOP is anchored to last December 31st instead of rolled 12 months back.
- [[Contract Dates Snowball Script (With Lifecycle Cross-Check)|Contract Dates Snowball Script (With Lifecycle Cross-Check)]] — the sibling pattern, for when you do have real contract start/end dates.
- [[Steps in Building an ARR Snowball|Steps in Building an ARR Snowball]] — the 5-step mental model; this pattern's Step 2 (scaffold) is that model's "snapshot into discrete periods" step, just filling gaps in existing rows instead of testing a date range against them.
- [[ARR Snowball Template (ANSI SQL, Portable)|ARR Snowball Template (ANSI SQL, Portable)]] — the cascade this note reuses, taught stage-by-stage.
- [[Bucket Cascade Logic|Bucket Cascade Logic]] — the conceptual walkthrough with a worked multi-customer example.
- [[Chapter 2/Lesson 4 - Taming Non-Standard ARR|Chapter 2, Lesson 4]] — how to turn raw usage into an `arr_amount` in the first place, if that conversion is what's actually hard about your data.
- [[Snowball|Snowball]] — hub note for this area.

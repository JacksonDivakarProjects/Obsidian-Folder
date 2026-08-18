> A variant of [[LTM Snowball Script (No End Dates, Monthly Grain)|LTM Snowball Script (No End Dates, Monthly Grain)]] — same raw data, same first two steps. The only thing that changes is Step 3: what BOP is compared against. See [[Contract Dates Snowball Script (With Lifecycle Cross-Check)|Contract Dates Snowball Script (With Lifecycle Cross-Check)]] for the sibling pattern that has real contract dates instead.

## The situation this pattern is for

Same Driftwood Compute, same monthly-actuals-only data — but a different question. LTM asks "how much has this grain changed over the trailing twelve months, as of right now?" and slides its comparison window forward every month. **YTD asks a different question: "how much has this grain changed since January 1st of this calendar year?"** The BOP side is anchored to a fixed point — the close of the prior calendar year — and holds still all year while the window widens under it: one month wide in January, twelve months wide by December.

This isn't a cosmetic difference. Two real consequences fall out of it, covered in full in [[Chapter 2/Lesson 3 - Deriving the YTD Variant, For Real This Time|Chapter 2, Lesson 3]]:

- **YTD needs far less history.** LTM for March 2026 needs March 2025 actuals in the warehouse — a full extra year back. YTD for any month of 2026 needs only one anchor snapshot: December 31, 2025. For a young company or a system that just migrated, that's often the difference between "reportable" and "not yet."
- **YTD figures widen through the year, and that widening isn't growth.** A YTD ratio at Q1 covers three months; the same ratio at Q4 covers twelve. Watching it climb quarter over quarter is partly just the window getting wider, not the business accelerating. Never chart LTM and YTD on the same axis without labeling which is which.

```
RAW                 raw_monthly_usage   (one row per invoice)
DIM                 dim_calendar
  │
  ▼  STEP 1 — STANDARDIZE          (identical to the LTM note)
  ▼  STEP 2 — SCAFFOLD TO A DENSE MONTHLY GRAIN     (identical to the LTM note)
FACT                source_fact   (one row per grain per month, every month,
  │                                explicit $0 where nothing was invoiced)
  ▼  STEP 3 — THE CASCADE, YTD-ALIGNED   (this is the only step that changes)
BRIDGE              8 buckets, BOP fixed at last Dec 31, EOP the reporting month
```

## Steps 1–2 — Standardize, then scaffold to a dense monthly grain

These two steps are almost word-for-word what [[LTM Snowball Script (No End Dates, Monthly Grain)|LTM Snowball Script]] already builds and explains — go there for the full reasoning (why `invoice_date` needs normalizing, and why the scaffold matters at all). Reproduced here so this note runs standalone; the one line that differs is called out just below the code.

```sql
stg_monthly_arr AS (
    SELECT
        customer_id, product_id, service_id,
        DATEFROMPARTS(YEAR(invoice_date), MONTH(invoice_date), 1) AS month_roll,
        SUM(arr_amount) AS arr
    FROM raw_monthly_usage
    GROUP BY customer_id, product_id, service_id,
             DATEFROMPARTS(YEAR(invoice_date), MONTH(invoice_date), 1)
),
grain_keys AS (
    SELECT DISTINCT customer_id, product_id, service_id
    FROM stg_monthly_arr
),
month_roll_list AS (
    SELECT DISTINCT DATEFROMPARTS(YEAR(month_end_date), MONTH(month_end_date), 1) AS month_roll
    FROM dim_calendar
    WHERE month_end_date BETWEEN DATEFROMPARTS(YEAR(@report_start) - 1, 1, 1) AND @report_end
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

One change from the LTM version, worth noticing: `month_roll_list` now goes back to **January 1st of the year before `@report_start`**, not just twelve months back. Every reporting month's anchor is December of the year before it — for `@report_start` itself, the earliest reporting month, that anchor is December of `YEAR(@report_start) - 1`. Starting the scaffold at that same year's January 1st rather than pinning exactly its December gives an eleven-month safety margin for free (a few extra scaffold rows, not a performance concern) instead of relying on the boundary being exactly right.

## Step 3 — The cascade, aligned to YTD

This is the one real change, and per [[Chapter 2/Lesson 3 - Deriving the YTD Variant, For Real This Time|Chapter 2, Lesson 3]] it's a one-line diff in principle: swap the alignment predicate, leave every downstream classification stage — `customer_flags`, `plan_flags`, `service_flags`, `bucket_amounts` — completely untouched, because none of them know or care *how* `bop_arr` was chosen.

```sql
-- LTM alignment (the sibling note):
--   ON bop.month_roll = DATEADD(MONTH, -12, eop.month_roll)
--
-- YTD alignment (this note): BOP is always December of the PRIOR calendar
-- year, no matter which month is being reported.
--   ON bop.month_roll = DATEFROMPARTS(YEAR(eop.month_roll) - 1, 12, 1)
```

The lesson also flags the one real trap here, and it's worth restating rather than rediscovering the hard way: **under LTM, a churned customer's report month can be reconstructed from the BOP month** (`bop.month_roll + 12 months` — the hop is always exactly a year, so it's invertible). **Under YTD, that trick breaks**, because one December anchor feeds *up to twelve* different reporting months — "which report month does this BOP-only row belong to?" has twelve valid answers, not one. The lesson's fix is to build an explicit month-spine and `LEFT JOIN` both BOP and EOP onto it, so the spine decides which periods exist instead of trying to derive one side from the other.

This note gets that spine for free. Step 2's scaffold already made `source_fact` dense — one row per grain per month, real or `$0`, across the whole window — which *is* the spine the lesson builds by hand, just constructed one step earlier. That means every reporting month already exists directly on the `eop` side; there's no BOP-only row to reconstruct a month for, so the join is a plain `LEFT JOIN` with no `COALESCE`-on-`month_roll` trick needed at all:

```sql
service_grain AS (
    SELECT
        eop.month_roll,
        eop.customer_id,
        eop.product_id,
        eop.service_id,
        COALESCE(bop.arr, 0) AS bop_arr,
        eop.arr              AS eop_arr
    FROM source_fact AS eop
    LEFT JOIN source_fact AS bop
      ON  bop.month_roll  = DATEFROMPARTS(YEAR(eop.month_roll) - 1, 12, 1)
      AND bop.customer_id = eop.customer_id
      AND bop.product_id  = eop.product_id
      AND bop.service_id  = eop.service_id
    WHERE eop.month_roll BETWEEN @report_start AND @report_end
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

-- No date cross-check here, same as the LTM note -- there are no contract
-- dates in this data to check claims against.
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

## Read the output as cumulative, not monthly

The one thing that will trip you up if you forget it: **every bucket amount here is "since January 1st," not "this month's own movement."** February's `customer_churn` isn't "who churned in February" — it's "who was active on last December 31st but is inactive as of end of February," which necessarily includes anyone who actually churned back in January too. The number only resets when the calendar year rolls over. If you need genuine month-over-month movement alongside this, that's exactly what the LTM sibling note computes — the two are meant to be read side by side, not merged into one column.

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

See [[Chapter 2/Lesson 6 - Testing Your Snowball Like a Data Engineer|Chapter 2, Lesson 6]] for the full diagnostic table if either check returns rows. One YTD-specific check worth adding: `SUM(bop_arr)` for January of any year should exactly equal `SUM(eop_arr)` for December of the year before — the anchor is the same number by construction, so a mismatch there means the widened `month_roll_list` isn't reaching back far enough.

---

## The full assembled script

Copy this whole block. Edit only `@report_start`, `@report_end`, and the `FROM raw_monthly_usage` / `FROM dim_calendar` lines.

```sql
-- ============================================================================
-- ARR SNOWBALL — YTD, NO END DATES, MONTHLY ACTUALS
-- One raw invoice table + dim_calendar -> standardize -> scaffold to a dense
-- monthly grain -> the cascade (month vs. December of the prior calendar
-- year) -> bridge. Same pipeline as the LTM sibling note through Step 2;
-- only the alignment predicate in Step 3 differs. Dialect: T-SQL.
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
    WHERE month_end_date BETWEEN DATEFROMPARTS(YEAR(@report_start) - 1, 1, 1) AND @report_end
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

-- ---------- STEP 3: THE CASCADE (YTD-ALIGNED) ----------
service_grain AS (
    SELECT
        eop.month_roll,
        eop.customer_id,
        eop.product_id,
        eop.service_id,
        COALESCE(bop.arr, 0) AS bop_arr,
        eop.arr              AS eop_arr
    FROM source_fact AS eop
    LEFT JOIN source_fact AS bop
      ON  bop.month_roll  = DATEFROMPARTS(YEAR(eop.month_roll) - 1, 12, 1)
      AND bop.customer_id = eop.customer_id
      AND bop.product_id  = eop.product_id
      AND bop.service_id  = eop.service_id
    WHERE eop.month_roll BETWEEN @report_start AND @report_end
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
- [[LTM Snowball Script (No End Dates, Monthly Grain)|LTM Snowball Script (No End Dates, Monthly Grain)]] — the base pattern this note is a one-step variant of; read that one first.
- [[Contract Dates Snowball Script (With Lifecycle Cross-Check)|Contract Dates Snowball Script (With Lifecycle Cross-Check)]] — the sibling pattern for real contract start/end dates.
- [[Chapter 2/Lesson 3 - Deriving the YTD Variant, For Real This Time|Chapter 2, Lesson 3]] — the full theory this note's Step 3 implements: why LTM and YTD answer different questions, why the reconstruction trick breaks under YTD, and the month-spine fix.
- [[ARR Snowball Template (ANSI SQL, Portable)|ARR Snowball Template (ANSI SQL, Portable)]] — the base cascade both LTM and YTD alignments plug into.
- [[Bucket Cascade Logic|Bucket Cascade Logic]] — the conceptual walkthrough with a worked multi-customer example.
- [[Snowball|Snowball]] — hub note for this area.

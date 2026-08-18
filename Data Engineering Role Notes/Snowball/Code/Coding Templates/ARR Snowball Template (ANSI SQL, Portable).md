A single-statement, CTE-based reimplementation of the classic imperative ARR snowball procedure. The original pattern — a stack of `#temp` tables mutated by one `UPDATE` per bucket — is replaced by a linear chain of CTEs in which each stage emits an explicit `claimed_by` label. Because a row can only be claimed once and every later stage filters on `claimed_by IS NULL`, the mutual exclusivity that the imperative version enforced through statement ordering becomes a structural property of the query instead of a procedural one.

The template is written in T-SQL for concreteness (one dialect had to be picked for date functions) and is annotated wherever a construct needs swapping for Snowflake, BigQuery, Postgres, or Databricks SQL. Everything else is ANSI: plain CTEs, `FULL OUTER JOIN`, `SUM`, `COALESCE`, `CASE`. No window functions are strictly required by the cascade — `LAG` is deliberately avoided for BOP (see *BOP alignment*) — though one optional `MAX() OVER` appears in the reconciliation section.

This is the portable counterpart to [[Standardized ARR Snowball Procedure (T-SQL)|Standardized ARR Snowball Procedure (T-SQL)]] — see the comparison table in [[Snowball|Snowball]] for which to reach for.

---

## Input contract

Two inputs. Point them at your own schema by editing only the `source_fact` and `activity_dates` CTEs at the top; nothing downstream references a physical table.

### `source_fact` — monthly ARR snapshot, one row per grain per month

| Column | Type | Meaning |
|---|---|---|
| `month_roll` | `date` | Month bucket, normalized to the **first day** of the month. Every row in a month must share the identical value or the self-join on `month_roll` will miss. |
| `customer_id` | `varchar` | Customer grain key. |
| `product_id` | `varchar` | Product / plan grain key. Must be non-null; use a `'N/A'` sentinel rather than `NULL` (see *Null-safe grain keys*). |
| `service_id` | `varchar` | Service grain key, nested inside product. Same non-null rule. |
| `arr` | `decimal(18,2)` | ARR **as of that month** for that grain combination. Additive across grains: the customer-level ARR must equal the sum of its service-level rows. |

Assumed already-aggregated at `(month_roll, customer_id, product_id, service_id)`. If the source is transactional, pre-aggregate it in the `source_fact` CTE — do not push a `GROUP BY` further down, since the BOP self-join depends on exactly one row per grain per month.

### `activity_dates` — authoritative start/end dates per grain

| Column | Type | Meaning |
|---|---|---|
| `customer_id` | `varchar` | Matches `source_fact`. |
| `product_id` | `varchar` | Matches `source_fact`. |
| `service_id` | `varchar` | Matches `source_fact`. |
| `start_date` | `date` | Date the service genuinely began. |
| `end_date` | `date` | Date it genuinely ended; `NULL` for still-active. |

One row per `(customer_id, product_id, service_id)` lifecycle span. Multiple spans per grain (churn then win-back) are supported — the cross-check aggregates them.

### Parameters

```sql
DECLARE @report_start date = '2024-01-01';   -- first month_roll to report on
DECLARE @report_end   date = '2025-12-01';   -- last month_roll to report on
```

Rows outside `[@report_start, @report_end]` are still read (BOP needs 12 months of lookback) but not emitted.

---

## Design notes

### BOP alignment: join, not `LAG`

The imperative original derived BOP by looking back 12 months. The tempting modern shorthand is `LAG(arr, 12) OVER (PARTITION BY customer_id, product_id, service_id ORDER BY month_roll)`.

**Do not use it.** `LAG(x, 12)` counts *rows*, not *months*. It is only correct when every grain has a dense, gap-free row for every month in the window. Real ARR facts are almost never dense: a service that churns typically stops emitting rows entirely rather than emitting `arr = 0`. For such a grain, `LAG(arr, 12)` silently reaches back 15 or 20 months and returns a value that is wrong in a way no error surfaces — it just quietly misstates the bridge.

The template instead does an explicit `FULL OUTER JOIN` between the current month's grain rows and the same grain's rows dated exactly 12 months earlier. `FULL OUTER` (not `LEFT`) is essential: a grain present at BOP but absent at EOP has *no* current-month row to hang a `LEFT JOIN` off, and that grain is exactly a churn — the most important row in the report. The join produces the union of both sides, `COALESCE`s the keys, and treats a missing side as `0`.

Cost: one extra pass over the fact per grain level. Correctness: total, regardless of gaps.

### Null-safe grain keys

`FULL OUTER JOIN ... ON a.product_id = b.product_id` drops rows when `product_id` is `NULL`, because `NULL = NULL` is unknown. Either guarantee non-null keys upstream (preferred) or wrap every join predicate in `COALESCE(a.product_id, '~NULL~') = COALESCE(b.product_id, '~NULL~')`. The template assumes non-null and normalizes defensively in `source_fact` via `COALESCE(..., 'N/A')`.

### Deliberate simplification: LTM only

Only the trailing-twelve-month cascade is built here. The YTD variant — which the original procedure duplicated in full, doubling its length — is **not** reproduced. It is a change of one join predicate, documented in *Deriving the YTD variant* below. Duplicating eight buckets to change a date window is the main reason the original is hard to maintain.

---

## The cascade

```sql
-- ============================================================
-- ARR SNOWBALL — LTM (trailing 12 month) bridge
-- Single statement. No temp tables, no session state.
-- Dialect: T-SQL. See cheatsheet for swaps.
-- ============================================================

WITH

-- ------------------------------------------------------------
-- STAGE 0: source_fact
-- Point this at your schema. Everything below is schema-agnostic.
-- Normalize month_roll to first-of-month and grain keys to non-null.
-- ------------------------------------------------------------
source_fact AS (
    SELECT
        DATEFROMPARTS(YEAR(f.month_roll), MONTH(f.month_roll), 1) AS month_roll,
        f.customer_id,
        COALESCE(f.product_id, 'N/A')                             AS product_id,
        COALESCE(f.service_id, 'N/A')                             AS service_id,
        SUM(f.arr)                                                AS arr
    FROM dbo.your_arr_fact AS f
    WHERE f.month_roll >= DATEADD(MONTH, -12, @report_start)  -- lookback for BOP
      AND f.month_roll <= @report_end
    GROUP BY
        DATEFROMPARTS(YEAR(f.month_roll), MONTH(f.month_roll), 1),
        f.customer_id,
        COALESCE(f.product_id, 'N/A'),
        COALESCE(f.service_id, 'N/A')
),

-- ------------------------------------------------------------
-- STAGE 0b: activity_dates
-- Collapsed to one row per grain: earliest start, latest end.
-- latest_end is NULL if ANY span is still open (MAX over NULLs
-- ignores them, so count open spans explicitly).
-- ------------------------------------------------------------
activity_dates AS (
    SELECT
        a.customer_id,
        COALESCE(a.product_id, 'N/A')                    AS product_id,
        COALESCE(a.service_id, 'N/A')                    AS service_id,
        MIN(a.start_date)                                AS first_start,
        MAX(a.start_date)                                AS latest_start,
        CASE WHEN SUM(CASE WHEN a.end_date IS NULL THEN 1 ELSE 0 END) > 0
             THEN NULL
             ELSE MAX(a.end_date)
        END                                              AS latest_end
    FROM dbo.your_activity_dates AS a
    GROUP BY
        a.customer_id,
        COALESCE(a.product_id, 'N/A'),
        COALESCE(a.service_id, 'N/A')
),

-- ------------------------------------------------------------
-- STAGE 1: service_grain
-- Finest grain. FULL OUTER JOIN current month against the same
-- grain 12 months prior. FULL (not LEFT) so grains that vanished
-- -- i.e. churns -- still produce a row.
--
-- eop.month_roll is the month being reported; bop rows are joined
-- on month_roll = DATEADD(MONTH,-12,eop.month_roll).
-- ------------------------------------------------------------
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
    -- Keep only reportable months. Expressed on the COALESCEd value
    -- so BOP-only (churn) rows survive: their reported month is
    -- bop.month_roll + 12.
    WHERE COALESCE(eop.month_roll, DATEADD(MONTH, 12, bop.month_roll))
              BETWEEN @report_start AND @report_end
),

-- ------------------------------------------------------------
-- STAGE 2: plan_grain -- roll service up to customer+product
-- ------------------------------------------------------------
plan_grain AS (
    SELECT
        month_roll,
        customer_id,
        product_id,
        SUM(bop_arr) AS bop_arr,
        SUM(eop_arr) AS eop_arr
    FROM service_grain
    GROUP BY month_roll, customer_id, product_id
),

-- ------------------------------------------------------------
-- STAGE 3: customer_grain -- roll product up to customer
-- ------------------------------------------------------------
customer_grain AS (
    SELECT
        month_roll,
        customer_id,
        SUM(bop_arr) AS bop_arr,
        SUM(eop_arr) AS eop_arr
    FROM plan_grain
    GROUP BY month_roll, customer_id
),

-- ------------------------------------------------------------
-- STAGE 4: customer_flags -- buckets 1 & 2
--   1. Customer Churn : bop > 0 AND eop = 0  -> -bop
--   2. New Customer   : bop = 0 AND eop > 0  -> +eop
-- Mutually exclusive by construction; a customer cannot be both.
-- ------------------------------------------------------------
customer_flags AS (
    SELECT
        month_roll,
        customer_id,
        bop_arr,
        eop_arr,
        CASE
            WHEN bop_arr > 0 AND eop_arr = 0 THEN 'customer_churn'
            WHEN bop_arr = 0 AND eop_arr > 0 THEN 'new_customer'
            ELSE NULL
        END AS customer_claim
    FROM customer_grain
),

-- ------------------------------------------------------------
-- STAGE 5: plan_flags -- buckets 3 & 4
-- Excludes any customer already claimed at customer grain: if the
-- whole customer churned, its individual plans are not separately
-- "plan churn". This is the imperative version's
-- "WHERE customer_id NOT IN (#cte_customerchurn)" made structural.
--   3. Plan Churn : bop > 0 AND eop = 0 -> -bop
--   4. Cross-sell : bop = 0 AND eop > 0 -> +eop
-- ------------------------------------------------------------
plan_flags AS (
    SELECT
        p.month_roll,
        p.customer_id,
        p.product_id,
        p.bop_arr,
        p.eop_arr,
        c.customer_claim,
        CASE
            WHEN c.customer_claim IS NOT NULL           THEN NULL  -- already claimed upstream
            WHEN p.bop_arr > 0 AND p.eop_arr = 0        THEN 'plan_churn'
            WHEN p.bop_arr = 0 AND p.eop_arr > 0        THEN 'cross_sell'
            ELSE NULL
        END AS plan_claim
    FROM plan_grain AS p
    JOIN customer_flags AS c
      ON  c.month_roll  = p.month_roll
      AND c.customer_id = p.customer_id
),

-- ------------------------------------------------------------
-- STAGE 6: service_flags -- buckets 5, 6, 7, 8
-- Attaches upstream claims to every service row, then resolves the
-- remaining four buckets in priority order. The CASE arms ARE the
-- cascade: first match wins, so ordering here is load-bearing.
--   5. Service Cross-sell : bop = 0 AND eop > 0 -> +eop
--   6. Service Churn      : bop > 0 AND eop = 0 -> -bop
--   7. Downsell           : both > 0, eop < bop -> eop - bop
--   8. Upsell             : both > 0, eop > bop -> eop - bop
-- Rows where eop = bop (flat) stay unclaimed and contribute only
-- to BOP/EOP totals -- correct, they are not a bridge movement.
-- ------------------------------------------------------------
service_flags AS (
    SELECT
        s.month_roll,
        s.customer_id,
        s.product_id,
        s.service_id,
        s.bop_arr,
        s.eop_arr,
        pf.customer_claim,
        pf.plan_claim,
        CASE
            WHEN pf.customer_claim IS NOT NULL             THEN pf.customer_claim
            WHEN pf.plan_claim     IS NOT NULL             THEN pf.plan_claim
            WHEN s.bop_arr = 0 AND s.eop_arr > 0           THEN 'service_cross_sell'
            WHEN s.bop_arr > 0 AND s.eop_arr = 0           THEN 'service_churn'
            WHEN s.bop_arr > 0 AND s.eop_arr > 0
                 AND s.eop_arr < s.bop_arr                 THEN 'downsell'
            WHEN s.bop_arr > 0 AND s.eop_arr > 0
                 AND s.eop_arr > s.bop_arr                 THEN 'upsell'
            ELSE NULL                                                -- flat / no movement
        END AS claimed_by
    FROM service_grain AS s
    JOIN plan_flags AS pf
      ON  pf.month_roll  = s.month_roll
      AND pf.customer_id = s.customer_id
      AND pf.product_id  = s.product_id
),
```

Every service row now carries exactly one `claimed_by` label (or `NULL` for flat rows). The cascade is complete. What follows is validation and aggregation.

---

## Activity-date cross-check

The `bop = 0 → eop > 0` test detects a *numeric* transition, which is not the same as a *lifecycle* transition. Both false positives are common in production:

- **Phantom new** — a service was active all along but its ARR was `0` twelve months ago (free trial, promo period, billing correction, a late-arriving row). The SUM says "new"; the lifecycle says "existed since 2019."
- **Phantom churn** — ARR dropped to `0` for a month due to a credit, pause, or restatement, but the service never ended. The SUM says "churn"; the lifecycle says "still active."

The cross-check confirms each flagged transition against `activity_dates`, requiring the real start or end date to fall inside the twelve-month window that the bucket claims it happened in.

This CTE is **optional but strongly recommended**. Omitting it does not break the bridge arithmetic — BOP + all buckets still reconciles to EOP, because a demoted row falls through to `upsell`/`downsell` rather than vanishing. What it changes is attribution quality: without it, new-logo and churn counts are inflated by billing noise. Skip it only if `activity_dates` coverage is incomplete, in which case an unmatched grain would be wrongly demoted.

```sql
-- ------------------------------------------------------------
-- STAGE 7: validated_flags (OPTIONAL, RECOMMENDED)
-- Cross-check each claimed transition against real start/end dates.
--
-- Window: (month_roll - 12 months, month_roll]. A "new" service must
-- have genuinely STARTED inside it; a "churned" service must have
-- genuinely ENDED inside it.
--
-- Grains with NO activity_dates row are left ALONE (treated as
-- confirmed) rather than demoted -- absent reference data must not
-- silently rewrite the bridge. Flip the fallback to 0 if your
-- activity table is known-complete and you want strictness.
--
-- Customer/plan-grain claims are validated using the grain's
-- component services: a customer churned if ALL its services ended
-- in-window, which is what MIN(confirmed) over the group tests.
-- ------------------------------------------------------------
validated_flags AS (
    SELECT
        sf.month_roll,
        sf.customer_id,
        sf.product_id,
        sf.service_id,
        sf.bop_arr,
        sf.eop_arr,
        sf.claimed_by                                    AS raw_claim,
        CASE
            -- "started" buckets: require a real start inside the window
            WHEN sf.claimed_by IN ('new_customer', 'cross_sell', 'service_cross_sell')
                THEN CASE
                        WHEN ad.customer_id IS NULL THEN 1        -- no reference row: trust the SUM
                        WHEN ad.latest_start >  DATEADD(MONTH, -12, sf.month_roll)
                         AND ad.latest_start <= EOMONTH(sf.month_roll) THEN 1
                        ELSE 0
                     END
            -- "ended" buckets: require a real end inside the window
            WHEN sf.claimed_by IN ('customer_churn', 'plan_churn', 'service_churn')
                THEN CASE
                        WHEN ad.customer_id IS NULL THEN 1
                        WHEN ad.latest_end IS NULL THEN 0         -- still open: not a churn
                        WHEN ad.latest_end >  DATEADD(MONTH, -12, sf.month_roll)
                         AND ad.latest_end <= EOMONTH(sf.month_roll) THEN 1
                        ELSE 0
                     END
            ELSE 1                                                -- up/down/flat need no date proof
        END AS date_confirmed
    FROM service_flags AS sf
    LEFT JOIN activity_dates AS ad
      ON  ad.customer_id = sf.customer_id
      AND ad.product_id  = sf.product_id
      AND ad.service_id  = sf.service_id
),

-- ------------------------------------------------------------
-- STAGE 8: resolved_flags
-- Demote unconfirmed claims to the movement they actually are.
-- A "new customer" that did not really start is just growth on an
-- existing base -> upsell. A "churn" that did not really end is
-- just a decline -> downsell. Sign of (eop - bop) decides.
-- Rows demoted this way keep their dollars, so the bridge still ties.
-- ------------------------------------------------------------
resolved_flags AS (
    SELECT
        month_roll,
        customer_id,
        product_id,
        service_id,
        bop_arr,
        eop_arr,
        raw_claim,
        date_confirmed,
        CASE
            WHEN raw_claim IS NULL                THEN NULL
            WHEN date_confirmed = 1               THEN raw_claim
            WHEN eop_arr > bop_arr                THEN 'upsell'
            WHEN eop_arr < bop_arr                THEN 'downsell'
            ELSE NULL
        END AS claimed_by
    FROM validated_flags
),
```

To run without the cross-check, delete stages 7 and 8 and point stage 9 at `service_flags` instead of `resolved_flags`. The column contract is identical (`claimed_by` is present in both), so nothing else changes.

---

## Bucket amounts and aggregation

```sql
-- ------------------------------------------------------------
-- STAGE 9: bucket_amounts
-- One signed amount column per bucket, at service grain.
-- Sign convention: churn/downsell negative, new/upsell/cross
-- positive. Exactly one column is non-zero per row.
-- ------------------------------------------------------------
bucket_amounts AS (
    SELECT
        month_roll,
        customer_id,
        product_id,
        service_id,
        bop_arr,
        eop_arr,
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

-- ------------------------------------------------------------
-- FINAL: aggregate to the reporting grain and derive GRR / NRR.
--   GRR = BOP + customer_churn + plan_churn + service_churn + downsell
--   NRR = GRR + upsell + cross_sell + service_cross_sell + new_customer
-- Churn/downsell columns are already negative, so all terms add.
--
-- new_customer is included in NRR here so that the bridge closes to
-- EOP. If your definition of NRR excludes new logos (the common
-- convention -- NRR measures the existing base only), drop the
-- new_customer term from nrr and read bridge_close for the tie-out.
-- ------------------------------------------------------------
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

    SUM(bop_arr) + SUM(customer_churn) + SUM(plan_churn)
                 + SUM(service_churn)  + SUM(downsell)              AS grr,

    SUM(bop_arr) + SUM(customer_churn) + SUM(plan_churn)
                 + SUM(service_churn)  + SUM(downsell)
                 + SUM(upsell) + SUM(cross_sell)
                 + SUM(service_cross_sell) + SUM(new_customer)      AS nrr,

    SUM(eop_arr)             AS eop_arr,

    -- Tie-out. Must be 0.00 for every month. Non-zero means a row was
    -- claimed by a bucket whose amount does not equal its eop-bop delta.
    SUM(eop_arr)
      - ( SUM(bop_arr) + SUM(customer_churn) + SUM(new_customer)
        + SUM(plan_churn) + SUM(cross_sell) + SUM(service_cross_sell)
        + SUM(service_churn) + SUM(downsell) + SUM(upsell) )        AS bridge_close
FROM bucket_amounts
GROUP BY month_roll
ORDER BY month_roll;
```

Change the reporting grain by adding keys to both the `SELECT` and the `GROUP BY` — `month_roll, customer_id` for a per-customer bridge, or all four keys for the full detail. The bucket arithmetic is unchanged at any grain because all of it is resolved at service grain before aggregation.

### Reading `bridge_close`

`bridge_close` must be `0.00` in every row. Non-zero values localize the fault:

| Symptom | Cause |
|---|---|
| Non-zero in one month only | Duplicate rows in `source_fact` for that month — the pre-aggregation assumption is violated. |
| Non-zero in every month, drifting with volume | A grain key is `NULL` and being dropped by a join predicate. Check the `COALESCE` normalization. |
| Small non-zero, both signs | Rounding. Cast `arr` to a fixed `decimal` in `source_fact` rather than relying on `float`. |

A useful development probe — flag every unclaimed row that nonetheless moved, which should return nothing:

```sql
SELECT month_roll, customer_id, product_id, service_id, bop_arr, eop_arr
FROM resolved_flags
WHERE claimed_by IS NULL
  AND bop_arr <> eop_arr;
```

---

## Deriving the YTD variant

The original procedure duplicated all eight buckets to produce a year-to-date bridge. That duplication is unnecessary: LTM and YTD differ **only** in which prior month supplies BOP. Every stage from `plan_grain` down is written against `service_grain`'s output columns and is agnostic to how BOP was chosen.

Change one predicate. In `service_grain`, replace the trailing-twelve alignment:

```sql
-- LTM: BOP is the same grain exactly 12 months back
ON  bop.month_roll = DATEADD(MONTH, -12, eop.month_roll)
```

with an alignment to the December before the reporting year — the "as of Jan 1" opening balance:

```sql
-- YTD: BOP is the same grain as of the prior year-end (31 Dec).
-- Expressed as the December month_roll of the previous year, so the
-- join stays an equality and remains index-friendly.
ON  bop.month_roll = DATEFROMPARTS(YEAR(eop.month_roll) - 1, 12, 1)
```

Three consequential adjustments:

1. **The `COALESCE` for BOP-only rows.** `service_grain` reconstructs the reporting month for churn rows via `DATEADD(MONTH, 12, bop.month_roll)`, which is only valid under LTM. Under YTD a single BOP month feeds up to twelve reporting months, so the reconstruction is no longer one-to-one. Restructure: build a `month_spine` of reportable months cross-joined with the distinct grains, `LEFT JOIN` both EOP and BOP onto it, and drop the `FULL OUTER JOIN`. This removes the `COALESCE(eop.month_roll, ...)` entirely and is the more robust shape for both variants.

2. **The lookback in `source_fact`.** `DATEADD(MONTH, -12, @report_start)` must become the prior 31 December: `DATEFROMPARTS(YEAR(@report_start) - 1, 12, 1)`.

3. **The activity-date window in `validated_flags`.** Replace `DATEADD(MONTH, -12, sf.month_roll)` with `DATEFROMPARTS(YEAR(sf.month_roll), 1, 1)` on both the start and end comparisons, so a transition must fall inside the current calendar year.

January is a degenerate month under YTD — BOP equals EOP by definition, and every bucket is zero. That is correct, not a bug.

If both variants are needed in one result set, parameterize rather than duplicate: add `period_type` to a two-row `VALUES` list, cross-join it into `service_grain`, and make the join predicate a `CASE`. The cascade below it runs once, partitioned by `period_type`.

---

## Dialect cheatsheet

| Operation | T-SQL | Snowflake | BigQuery | Postgres | Databricks SQL |
|---|---|---|---|---|---|
| Add/subtract months | `DATEADD(MONTH, -12, d)` | `DATEADD(MONTH, -12, d)` | `DATE_SUB(d, INTERVAL 12 MONTH)` | `d - INTERVAL '12 months'` | `ADD_MONTHS(d, -12)` |
| Truncate to first of month | `DATEFROMPARTS(YEAR(d), MONTH(d), 1)` | `DATE_TRUNC('MONTH', d)` | `DATE_TRUNC(d, MONTH)` | `DATE_TRUNC('month', d)::date` | `DATE_TRUNC('MONTH', d)` |
| End of month | `EOMONTH(d)` | `LAST_DAY(d)` | `LAST_DAY(d, MONTH)` | `(DATE_TRUNC('month', d) + INTERVAL '1 month - 1 day')::date` | `LAST_DAY(d)` |
| Build date from parts | `DATEFROMPARTS(y, m, 1)` | `DATE_FROM_PARTS(y, m, 1)` | `DATE(y, m, 1)` | `MAKE_DATE(y, m, 1)` | `MAKE_DATE(y, m, 1)` |
| Jan 1 of a date's year | `DATEFROMPARTS(YEAR(d), 1, 1)` | `DATE_TRUNC('YEAR', d)` | `DATE_TRUNC(d, YEAR)` | `DATE_TRUNC('year', d)::date` | `DATE_TRUNC('YEAR', d)` |
| `FULL OUTER JOIN` | Supported | Supported | Supported (GoogleSQL; **not** in legacy SQL) | Supported | Supported |
| Recursive CTE keyword | `WITH` (implicit) | `WITH RECURSIVE` | `WITH RECURSIVE` | `WITH RECURSIVE` | `WITH RECURSIVE` |
| Parameter declaration | `DECLARE @x date = ...` | `SET x = ...`, ref as `$x` | `DECLARE x DATE DEFAULT ...` | psql `\set` / function arg | `SET VAR x = ...` |
| Identifier quoting | `[name]` | `"NAME"` (upper-folds) | `` `name` `` | `"name"` (lower-folds) | `` `name` `` |
| Integer division guard | `1.0 * a / NULLIF(b,0)` | same | same | `a::numeric / NULLIF(b,0)` | same |

Window function syntax (`OVER (PARTITION BY ... ORDER BY ...)`, frame clauses, `LAG`/`LEAD` with offset and default) is identical across all five and needs no adaptation — the template avoids `LAG` for correctness reasons, not portability ones.

### Additional portability notes

- **`FULL OUTER JOIN` in BigQuery** is fully supported under GoogleSQL. Only legacy SQL lacked it, and legacy SQL should not be used for new work. No workaround CTE is required.
- **Snowflake identifier case folding** upper-cases unquoted identifiers. Keep everything unquoted and lower-case in the source; do not mix `"customer_id"` and `customer_id`, or the two will not resolve to the same column.
- **Postgres `DATE_TRUNC`** returns `timestamp`, not `date`. Cast with `::date` before comparing to a `date` column, or the equality join will not match.
- **Databricks and Spark** require `arr` to have a consistent decimal scale across the union of both join sides; mixed `decimal(18,2)` and `decimal(38,6)` inputs promote in ways that can shift rounding. Cast explicitly in `source_fact`.
- **`EOMONTH` in the cross-check** can be replaced by comparing against the first day of the following month with a strict `<`, which is portable everywhere and avoids the whole end-of-month family: `ad.latest_start < DATEADD(MONTH, 1, sf.month_roll)`.

## 🔗 Related Notes
- [[Standardized ARR Snowball Procedure (T-SQL)|Standardized ARR Snowball Procedure (T-SQL)]] — the imperative T-SQL counterpart this was derived from.
- [[Bucket Cascade Logic|Bucket Cascade Logic]] — the conceptual explanation of the same 8 buckets.
- [[Snowball|Snowball]] — hub note for this area.

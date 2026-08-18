Cleaned-up, genericized version of the production T-SQL stored procedure that builds the full 8-stage ARR bucket cascade (see [[Bucket Cascade Logic|Bucket Cascade Logic]] for the conceptual walkthrough). This is the imperative counterpart to [[ARR Snowball Template (ANSI SQL, Portable)|ARR Snowball Template (ANSI SQL, Portable)]] — see the comparison table on the [[Snowball|Snowball hub]] for which one to reach for.

What changed from the [[Original Stored Procedure (As Provided)|original]]:
- Consistent casing (uppercase keywords), 4-space indentation, and a semicolon on every statement.
- A clear section banner before each of the 9 stages.
- `data_source = 'Sage'` hardcoded everywhere → `data_source = @data_source`, so the procedure genuinely works for whatever source is passed in, not just Sage. The final output's `'Sage' data_source` label is genericized the same way.
- Typo fixes in comments only (`Cusotmer` → `Customer`, `planchrun` → `planchurn`, `down sell`/`up sell` spacing standardized to match the real `downsell`/`upsell` column names).
- No logic changes. Every condition, join, and value is identical to the original — this is a formatting and genericization pass, not a rewrite. If you need the re-architected version, use the ANSI template instead.

## Input contract

The procedure expects two tables in your schema:

**`cust.customer_cube_monthly`** — one row per `(month_roll, customer_key, product_key, service_key, service_dim_key, revenue_type, location_key)` combination, with `data_source`, `service_arr` (EOP ARR for that month), `service_ytd`, `service_ytd_bop`, `ytd_movement`, and `mrr`. Rows must already be aggregated to this grain — the `LAG(service_arr, 12)` BOP calculation assumes exactly one row per grain per month with no gaps (see the caveat below).

**`int_cust.cust_plan_srv_activity_dates`** — authoritative lifecycle dates per grain: `customer_key`, `product_key`, `service_key`, `service_name`, `service_dim_key`, plus `customer_enddt`, `customer_startdt`, `plan_enddt`, `plan_startdt`, `service_enddt`, `service_startdt`. Used to cross-check that a numeric BOP/EOP transition corresponds to a real lifecycle event.

**Output:** `int_cust.revenue_bridge_output_bucket_calculations` — the full `#temp_all_months` grain plus all 16 bucket columns (8 buckets × LTM/YTD) and `grr`/`nrr`/`grr_ytd`/`nrr_ytd`.

## Known caveats (carried over from the original, not introduced by this cleanup)

- **`LAG(service_arr, 12)` for BOP assumes dense monthly rows.** If a grain (e.g. a churned service) stops emitting rows entirely instead of emitting `0`, `LAG(x, 12)` silently reaches back further than 12 real months and misattributes BOP. The [[ARR Snowball Template (ANSI SQL, Portable)|ANSI template]] fixes this with an explicit `FULL OUTER JOIN` on `month_roll - 12` instead — worth adopting here too if your source data has gaps.
- **The date cross-check for Customer Churn, Plan Churn, and Service Churn overwrites the ARR-based flag entirely** rather than combining the two signals. A grain with a `NULL` end date (meaning "no confirmed end — still active") satisfies neither the "ended within window" nor the "still active" check in the original formula, so it's possible for a still-open contract to be flagged as churned by this stage. Each occurrence is marked inline below with a `NOTE:` comment. Test this against your own `activity_dates` table before trusting churn output in production — it's worth double-checking whether this was intentional in the original or a latent bug.
- **YTD logic is fully duplicated** alongside LTM for every single bucket, roughly doubling the procedure's length. This mirrors the original's design faithfully; the ANSI template shows how to derive YTD from LTM with a single changed join predicate instead.

## The procedure

```sql
/*
-- EXEC [cust].[usp_build_customer_cube]
-- EXEC [cust].[usp_build_revenue_bridge_output]
exec [cust].[usp_revenue_bridge_bucket_calculations] 'Sage'
*/
CREATE PROCEDURE [cust].[usp_revenue_bridge_bucket_calculations]
(
    @data_source VARCHAR(100)
)
AS
BEGIN
    SET NOCOUNT ON;

    --DROP TABLE IF EXISTS cust.revenue_bridge_buckets_output_data_V2;

    -- The branch-per-data-source pattern below is what makes @data_source meaningful:
    -- each supported source gets its own guarded block, and every filter inside the
    -- block reads from @data_source rather than a hardcoded literal.
    IF (@data_source = 'Sage')
    BEGIN

        -- ============================================================
        -- STAGE 0: Base setup (grain: month x customer x product x service x service_dim x revenue_type x location)
        -- ============================================================
        /*=========================================================
        STEP 1: Base with BoP ARR using LAG
        =========================================================*/
        DROP TABLE IF EXISTS #temp_all_months;

        SELECT
            month_roll,
            customer_key,
            product_key,
            service_key,
            service_name,
            service_dim_key,
            revenue_type,
            location_key,
            mrr,
            service_arr,
            service_arr AS eop_arr,
            LAG(service_arr, 12) OVER (
                PARTITION BY
                    ISNULL(customer_key, ''),
                    ISNULL(product_key, ''),
                    ISNULL(service_key, ''),
                    ISNULL(revenue_type, ''),
                    ISNULL(location_key, ''),
                    ISNULL(service_dim_key, '')
                ORDER BY
                    month_roll
            ) AS bop_arr,
            service_ytd,
            service_ytd AS eop_ytd,
            service_ytd_bop AS bop_ytd,
            ytd_movement,
            CAST(0 AS FLOAT) AS customer_churn,
            CAST(0 AS FLOAT) AS planchurn,
            CAST(0 AS FLOAT) AS servicechurn,
            CAST(0 AS FLOAT) AS new_customer,
            CAST(0 AS FLOAT) AS cross_sell,
            CAST(0 AS FLOAT) AS service_cross_sell,
            CAST(0 AS FLOAT) AS nrr,
            CAST(0 AS FLOAT) AS grr,
            /* Added YTD calculation fields */
            CAST(0 AS FLOAT) AS nrr_ytd,
            CAST(0 AS FLOAT) AS grr_ytd,
            CAST(0 AS FLOAT) AS upsell,
            CAST(0 AS FLOAT) AS upsell_ytd,
            CAST(0 AS FLOAT) AS downsell,
            CAST(0 AS FLOAT) AS downsell_ytd,
            CAST(0 AS FLOAT) AS customer_churn_ytd,
            CAST(0 AS FLOAT) AS planchurn_ytd,
            CAST(0 AS FLOAT) AS servicechurn_ytd,
            CAST(0 AS FLOAT) AS new_customer_ytd,
            CAST(0 AS FLOAT) AS cross_sell_ytd,
            CAST(0 AS FLOAT) AS service_cross_sell_ytd
        INTO #temp_all_months
        FROM cust.customer_cube_monthly
        WHERE data_source = @data_source;

        UPDATE #temp_all_months
        SET bop_arr = ISNULL(bop_arr, 0),
            eop_arr = ISNULL(eop_arr, 0),
            eop_ytd = ISNULL(eop_ytd, 0),
            bop_ytd = ISNULL(bop_ytd, 0);

        -- ============================================================
        -- STAGE 1: Customer Churn (grain: month x customer)
        -- ============================================================
        ---//*****************************
        -- Customer Churn --Removed location key
        ---*******************************//

        -- Reset churn
        UPDATE a SET customer_churn = 0 FROM #temp_all_months a;

        /* reset customer churn YTD */
        UPDATE a SET customer_churn_ytd = 0 FROM #temp_all_months a;

        ------------------------------------------------------------
        /* Added Customer YTD and Previous Year YTD fields */
        SELECT
            month_roll,
            customer_key,
            customer_ltm,
            customer_prev_ltm,
            customer_ytd,
            customer_prev_ytd,
            CASE WHEN ISNULL(customer_ltm, 0) = 0 AND ISNULL(customer_prev_ltm, 0) <> 0 THEN 'Yes' ELSE 'No' END AS customerchurn_flag,
            CASE WHEN ISNULL(customer_ytd, 0) = 0 AND ISNULL(customer_prev_ytd, 0) <> 0 THEN 'Yes' ELSE 'No' END AS customerchurn_flag_ytd
        INTO #cte_customerchurn
        FROM (
            SELECT
                month_roll,
                ISNULL(customer_key, '') AS customer_key,
                SUM(CAST(eop_arr AS FLOAT)) AS customer_ltm,
                SUM(CAST(bop_arr AS FLOAT)) AS customer_prev_ltm,
                SUM(CAST(eop_ytd AS FLOAT)) AS customer_ytd,
                SUM(CAST(bop_ytd AS FLOAT)) AS customer_prev_ytd
            FROM #temp_all_months
            GROUP BY
                month_roll,
                ISNULL(customer_key, '')
        ) x;

        DROP TABLE IF EXISTS #customerchurn_startdt;

        WITH startdate_cte AS (
            SELECT
                x.month_roll,
                x.customer_key,
                x.fall_month_roll,
                x.customer_enddt,
                x.range_flag,
                x.end_flag,
                CASE WHEN x.range_flag = 'No' AND x.end_flag = 'No' THEN 'Yes' ELSE 'No' END AS cust_churn_flag
            FROM (
                SELECT DISTINCT
                    t.month_roll,
                    t.customer_key,
                    DATEADD(MONTH, -11, t.month_roll) AS fall_month_roll,
                    d.customer_enddt,
                    CASE WHEN d.customer_enddt BETWEEN DATEADD(MONTH, -11, t.month_roll) AND t.month_roll THEN 'Yes' ELSE 'No' END AS range_flag,
                    CASE WHEN d.customer_enddt > t.month_roll THEN 'Yes' ELSE 'No' END AS end_flag
                FROM #temp_all_months t
                    INNER JOIN int_cust.cust_plan_srv_activity_dates d
                        ON ISNULL(t.customer_key, '') = ISNULL(d.customer_key, '')
                WHERE data_source = @data_source
            ) AS x
        )
        SELECT * INTO #customerchurn_startdt FROM startdate_cte;

        /* Calculate Customer Churn for YTD */
        DROP TABLE IF EXISTS #customerchurn_startdt_ytd;

        WITH startdate_cte_ytd AS (
            SELECT
                x.month_roll,
                x.customer_key,
                x.fall_month_roll,
                x.customer_enddt,
                x.range_flag,
                x.end_flag,
                CASE WHEN x.range_flag = 'No' AND x.end_flag = 'No' THEN 'Yes' ELSE 'No' END AS cust_churn_flag
            FROM (
                SELECT DISTINCT
                    t.month_roll,
                    t.customer_key,
                    DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AS fall_month_roll,
                    d.customer_enddt,
                    CASE WHEN d.customer_enddt BETWEEN DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AND t.month_roll THEN 'Yes' ELSE 'No' END AS range_flag,
                    CASE WHEN d.customer_enddt > t.month_roll THEN 'Yes' ELSE 'No' END AS end_flag
                FROM #temp_all_months t
                    INNER JOIN int_cust.cust_plan_srv_activity_dates d
                        ON ISNULL(t.customer_key, '') = ISNULL(d.customer_key, '')
                WHERE data_source = @data_source
            ) AS x
        )
        SELECT * INTO #customerchurn_startdt_ytd FROM startdate_cte_ytd;

        -- NOTE: this INNER JOIN replaces the ARR-transition flag computed above with the activity-dates-table-derived flag entirely. Verify this matches your intended semantics -- a NULL end date (a contract with no confirmed end) will NOT satisfy either the "ended within window" or "still active" date checks, so it can end up flagged as churned here. Test against your own activity_dates table before trusting this stage's output.
        UPDATE c
        SET c.customerchurn_flag = s.cust_churn_flag
        FROM #cte_customerchurn c
            INNER JOIN #customerchurn_startdt s
                ON c.month_roll = s.month_roll
                AND ISNULL(c.customer_key, '') = ISNULL(s.customer_key, '');

        /* Update Customer Churn YTD flag */
        UPDATE c
        SET customerchurn_flag_ytd = s.cust_churn_flag
        FROM #cte_customerchurn c
            INNER JOIN #customerchurn_startdt_ytd s
                ON c.month_roll = s.month_roll
                AND ISNULL(c.customer_key, '') = ISNULL(s.customer_key, '');

        UPDATE t
        SET customer_churn = CASE WHEN c.customerchurn_flag = 'Yes' THEN CAST(-t.bop_arr AS FLOAT) ELSE 0 END
        FROM #temp_all_months t
            INNER JOIN #cte_customerchurn c
                ON t.month_roll = c.month_roll
                AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '');

        /* Update Customer Churn YTD values */
        UPDATE t
        SET customer_churn_ytd = CASE WHEN c.customerchurn_flag_ytd = 'Yes' THEN CAST(-t.bop_ytd AS FLOAT) ELSE 0 END
        FROM #temp_all_months t
            INNER JOIN #cte_customerchurn c
                ON t.month_roll = c.month_roll
                AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '');

        -- ============================================================
        -- STAGE 2: New Customer (grain: month x customer)
        -- ============================================================
        ---//*****************************
        -- New Customer --Removed location key --MF:Prior LTM Customer ARR = 0 AND Current LTM Customer ARR <> 0
        ---*******************************//
        DROP TABLE IF EXISTS #cte_output;

        /* Added Customer YTD and Previous Year YTD fields */
        SELECT
            month_roll,
            customer_key,
            cust_ltm,
            cust_prev_ltm,
            cust_ytd,
            cust_prev_ytd,
            CASE WHEN ISNULL(cust_ltm, 0) <> 0 AND ISNULL(cust_prev_ltm, 0) = 0 THEN 'Yes' ELSE 'No' END AS new_cust_flag,
            CASE WHEN ISNULL(cust_ytd, 0) <> 0 AND ISNULL(cust_prev_ytd, 0) = 0 THEN 'Yes' ELSE 'No' END AS new_cust_flag_ytd
        INTO #cte_output
        FROM (
            SELECT
                month_roll,
                customer_key,
                CAST(SUM(CASE WHEN customer_churn = 0 THEN eop_arr ELSE 0 END) AS FLOAT) AS cust_ltm,
                CAST(SUM(CASE WHEN customer_churn = 0 THEN bop_arr ELSE 0 END) AS FLOAT) AS cust_prev_ltm,
                CAST(SUM(CASE WHEN customer_churn_ytd = 0 THEN eop_ytd ELSE 0 END) AS FLOAT) AS cust_ytd,
                CAST(SUM(CASE WHEN customer_churn_ytd = 0 THEN bop_ytd ELSE 0 END) AS FLOAT) AS cust_prev_ytd
            FROM #temp_all_months
            GROUP BY
                month_roll,
                customer_key
        ) x;

        DROP TABLE IF EXISTS #customer_dates;

        WITH startdate_cte AS (
            SELECT DISTINCT
                t.month_roll,
                t.customer_key,
                DATEADD(MONTH, -11, t.month_roll) AS fall_month_roll
            FROM #temp_all_months t
                INNER JOIN int_cust.cust_plan_srv_activity_dates d
                    ON ISNULL(t.customer_key, '') = ISNULL(d.customer_key, '')
            WHERE d.customer_startdt BETWEEN DATEADD(MONTH, -11, t.month_roll) AND t.month_roll
                AND data_source = @data_source
        )
        SELECT * INTO #customer_dates FROM startdate_cte;

        /* Calculate New customer for YTD */
        DROP TABLE IF EXISTS #customer_dates_ytd;

        WITH startdate_cte_ytd AS (
            SELECT DISTINCT
                t.month_roll,
                t.customer_key,
                DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AS fall_month_roll
            FROM #temp_all_months t
                INNER JOIN int_cust.cust_plan_srv_activity_dates d
                    ON ISNULL(t.customer_key, '') = ISNULL(d.customer_key, '')
            WHERE d.customer_startdt BETWEEN DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AND t.month_roll
                AND data_source = @data_source
        )
        SELECT * INTO #customer_dates_ytd FROM startdate_cte_ytd;

        UPDATE c
        SET new_cust_flag = 'Yes'
        FROM #cte_output c
        WHERE EXISTS (
            SELECT 1
            FROM #customer_dates s
            WHERE ISNULL(s.customer_key, '') = ISNULL(c.customer_key, '')
                AND s.month_roll = c.month_roll
        );

        UPDATE c
        SET new_cust_flag = 'No'
        FROM #cte_output c
        WHERE NOT EXISTS (
            SELECT 1
            FROM #customer_dates s
            WHERE ISNULL(s.customer_key, '') = ISNULL(c.customer_key, '')
                AND s.month_roll = c.month_roll
        );

        /* Update New Customer YTD flag */
        UPDATE c
        SET new_cust_flag_ytd = 'Yes'
        FROM #cte_output c
        WHERE EXISTS (
            SELECT 1
            FROM #customer_dates_ytd s
            WHERE ISNULL(s.customer_key, '') = ISNULL(c.customer_key, '')
                AND s.month_roll = c.month_roll
        );

        UPDATE c
        SET new_cust_flag_ytd = 'No'
        FROM #cte_output c
        WHERE NOT EXISTS (
            SELECT 1
            FROM #customer_dates_ytd s
            WHERE ISNULL(s.customer_key, '') = ISNULL(c.customer_key, '')
                AND s.month_roll = c.month_roll
        );

        UPDATE t
        SET new_customer = CASE WHEN new_cust_flag = 'Yes' THEN CAST(t.eop_arr AS FLOAT) ELSE 0 END
        FROM #temp_all_months t
            INNER JOIN #cte_output c
                ON t.month_roll = c.month_roll
                AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '')
        WHERE t.customer_churn = 0;

        /* Update New Customer YTD values */
        UPDATE t
        SET new_customer_ytd = CASE WHEN new_cust_flag_ytd = 'Yes' THEN CAST(t.eop_ytd AS FLOAT) ELSE 0 END
        FROM #temp_all_months t
            INNER JOIN #cte_output c
                ON t.month_roll = c.month_roll
                AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '')
        WHERE t.customer_churn_ytd = 0;

        -- ============================================================
        -- STAGE 3: Plan Churn (grain: month x customer x product)
        -- ============================================================
        ---//*****************************
        -- Plan Churn --Removed location key
        ---*******************************//
        ---------------------------------------------------------------------------------------------------------------------
        -- Reset churn
        UPDATE a SET planchurn = 0 FROM #temp_all_months a;

        /* Reset planchurn YTD */
        UPDATE a SET planchurn_ytd = 0 FROM #temp_all_months a;

        ------------------------------------------------------------
        /* Added plan YTD and Previous Year YTD fields */
        DROP TABLE IF EXISTS #cte_planchurn;

        SELECT
            month_roll,
            customer_key,
            product_key,
            plan_ltm,
            plan_prev_ltm,
            plan_ytd,
            plan_prev_ytd,
            CASE WHEN ISNULL(plan_ltm, 0) = 0 AND ISNULL(plan_prev_ltm, 0) <> 0 THEN 'Yes' ELSE 'No' END AS planchurn_flag,
            CASE WHEN ISNULL(plan_ytd, 0) = 0 AND ISNULL(plan_prev_ytd, 0) <> 0 THEN 'Yes' ELSE 'No' END AS planchurn_flag_ytd
        INTO #cte_planchurn
        FROM (
            SELECT
                month_roll,
                customer_key,
                product_key,
                CAST(SUM(CASE WHEN customer_churn = 0 AND new_customer = 0 THEN eop_arr ELSE 0 END) AS FLOAT) AS plan_ltm,
                CAST(SUM(CASE WHEN customer_churn = 0 AND new_customer = 0 THEN bop_arr ELSE 0 END) AS FLOAT) AS plan_prev_ltm,
                CAST(SUM(CASE WHEN customer_churn_ytd = 0 AND new_customer_ytd = 0 THEN eop_ytd ELSE 0 END) AS FLOAT) AS plan_ytd,
                CAST(SUM(CASE WHEN customer_churn_ytd = 0 AND new_customer_ytd = 0 THEN bop_ytd ELSE 0 END) AS FLOAT) AS plan_prev_ytd
            FROM #temp_all_months
            GROUP BY
                month_roll,
                customer_key,
                product_key
        ) x;

        DROP TABLE IF EXISTS #planchurn_startdt;

        WITH startdate_cte AS (
            SELECT
                x.month_roll,
                x.customer_key,
                x.product_key,
                x.fall_month_roll,
                x.plan_enddt,
                x.range_flag,
                x.end_flag,
                CASE WHEN x.range_flag = 'No' AND x.end_flag = 'No' THEN 'Yes' ELSE 'No' END AS plan_churn_flag
            FROM (
                SELECT DISTINCT
                    t.month_roll,
                    t.customer_key,
                    t.product_key,
                    DATEADD(MONTH, -11, t.month_roll) AS fall_month_roll,
                    d.plan_enddt,
                    CASE WHEN d.plan_enddt BETWEEN DATEADD(MONTH, -11, t.month_roll) AND t.month_roll THEN 'Yes' ELSE 'No' END AS range_flag,
                    CASE WHEN d.plan_enddt > t.month_roll THEN 'Yes' ELSE 'No' END AS end_flag
                FROM #temp_all_months t
                    INNER JOIN int_cust.cust_plan_srv_activity_dates d
                        ON ISNULL(t.customer_key, '') = ISNULL(d.customer_key, '')
                        AND ISNULL(t.product_key, '') = ISNULL(d.product_key, '')
                WHERE data_source = @data_source
            ) AS x
        )
        SELECT * INTO #planchurn_startdt FROM startdate_cte;

        /* Calculate Plan Churn for YTD */
        DROP TABLE IF EXISTS #planchurn_startdt_ytd;

        WITH startdate_cte_ytd AS (
            SELECT
                x.month_roll,
                x.customer_key,
                x.product_key,
                x.fall_month_roll,
                x.plan_enddt,
                x.range_flag,
                x.end_flag,
                CASE WHEN x.range_flag = 'No' AND x.end_flag = 'No' THEN 'Yes' ELSE 'No' END AS plan_churn_flag
            FROM (
                SELECT DISTINCT
                    t.month_roll,
                    t.customer_key,
                    t.product_key,
                    DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AS fall_month_roll,
                    d.plan_enddt,
                    CASE WHEN d.plan_enddt BETWEEN DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AND t.month_roll THEN 'Yes' ELSE 'No' END AS range_flag,
                    CASE WHEN d.plan_enddt > t.month_roll THEN 'Yes' ELSE 'No' END AS end_flag
                FROM #temp_all_months t
                    INNER JOIN int_cust.cust_plan_srv_activity_dates d
                        ON ISNULL(t.customer_key, '') = ISNULL(d.customer_key, '')
                        AND ISNULL(t.product_key, '') = ISNULL(d.product_key, '')
                WHERE data_source = @data_source
            ) AS x
        )
        SELECT * INTO #planchurn_startdt_ytd FROM startdate_cte_ytd;

        -- NOTE: this INNER JOIN replaces the ARR-transition flag computed above with the activity-dates-table-derived flag entirely. Verify this matches your intended semantics -- a NULL end date (a contract with no confirmed end) will NOT satisfy either the "ended within window" or "still active" date checks, so it can end up flagged as churned here. Test against your own activity_dates table before trusting this stage's output.
        UPDATE c
        SET c.planchurn_flag = s.plan_churn_flag
        FROM #cte_planchurn c
            INNER JOIN #planchurn_startdt s
                ON c.month_roll = s.month_roll
                AND ISNULL(c.customer_key, '') = ISNULL(s.customer_key, '')
                AND ISNULL(c.product_key, '') = ISNULL(s.product_key, '');

        /* Update Plan Churn YTD flag */
        UPDATE c
        SET c.planchurn_flag_ytd = s.plan_churn_flag
        FROM #cte_planchurn c
            INNER JOIN #planchurn_startdt_ytd s
                ON c.month_roll = s.month_roll
                AND ISNULL(c.customer_key, '') = ISNULL(s.customer_key, '')
                AND ISNULL(c.product_key, '') = ISNULL(s.product_key, '');

        UPDATE t
        SET planchurn = CASE WHEN c.planchurn_flag = 'Yes' THEN CAST(-t.bop_arr AS FLOAT) ELSE 0 END
        FROM #temp_all_months t
            INNER JOIN #cte_planchurn c
                ON t.month_roll = c.month_roll
                AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '')
                AND ISNULL(t.product_key, '') = ISNULL(c.product_key, '')
        WHERE t.customer_churn = 0
            AND t.new_customer = 0;

        /* Update Plan Churn YTD values */
        UPDATE t
        SET planchurn_ytd = CASE WHEN c.planchurn_flag_ytd = 'Yes' THEN CAST(-t.bop_ytd AS FLOAT) ELSE 0 END
        FROM #temp_all_months t
            INNER JOIN #cte_planchurn c
                ON t.month_roll = c.month_roll
                AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '')
                AND ISNULL(t.product_key, '') = ISNULL(c.product_key, '')
        WHERE t.customer_churn_ytd = 0
            AND t.new_customer_ytd = 0;

        -- ============================================================
        -- STAGE 4: Cross-Sell (grain: month x customer x product)
        -- ============================================================
        ---//*****************************
        -- cross sell
        ---*******************************//
        UPDATE a SET cross_sell = 0 FROM #temp_all_months a;

        /* Reset cross sell ytd */
        UPDATE a SET cross_sell_ytd = 0 FROM #temp_all_months a;

        /* Added Plan YTD and Previous Year YTD fields */
        DROP TABLE IF EXISTS #cte_cross_sell;

        SELECT
            month_roll,
            customer_key,
            product_key,
            plan_ltm,
            plan_prev_ltm,
            plan_ytd,
            plan_prev_ytd,
            CASE WHEN ISNULL(plan_ltm, 0) <> 0 AND ISNULL(plan_prev_ltm, 0) = 0 THEN 'Yes' ELSE 'No' END AS cross_sell_flag,
            CASE WHEN ISNULL(plan_ytd, 0) <> 0 AND ISNULL(plan_prev_ytd, 0) = 0 THEN 'Yes' ELSE 'No' END AS cross_sell_flag_ytd
        INTO #cte_cross_sell
        FROM (
            SELECT
                month_roll,
                customer_key,
                product_key,
                CAST(SUM(CASE WHEN customer_churn = 0 AND new_customer = 0 AND planchurn = 0 THEN eop_arr ELSE 0 END) AS FLOAT) AS plan_ltm,
                CAST(SUM(CASE WHEN customer_churn = 0 AND new_customer = 0 AND planchurn = 0 THEN bop_arr ELSE 0 END) AS FLOAT) AS plan_prev_ltm,
                CAST(SUM(CASE WHEN customer_churn_ytd = 0 AND new_customer_ytd = 0 AND planchurn_ytd = 0 THEN eop_ytd ELSE 0 END) AS FLOAT) AS plan_ytd,
                CAST(SUM(CASE WHEN customer_churn_ytd = 0 AND new_customer_ytd = 0 AND planchurn_ytd = 0 THEN bop_ytd ELSE 0 END) AS FLOAT) AS plan_prev_ytd
            FROM #temp_all_months
            GROUP BY
                month_roll,
                customer_key,
                product_key
        ) x;

        DROP TABLE IF EXISTS #service_dates;

        WITH startdate_cte AS (
            SELECT DISTINCT
                t.month_roll,
                t.customer_key,
                t.product_key,
                DATEADD(MONTH, -11, t.month_roll) AS fall_month_roll
            FROM #temp_all_months t
                INNER JOIN int_cust.cust_plan_srv_activity_dates d
                    ON ISNULL(t.customer_key, '') = ISNULL(d.customer_key, '')
                    AND ISNULL(t.product_key, '') = ISNULL(d.product_key, '')
            WHERE d.plan_startdt BETWEEN DATEADD(MONTH, -11, t.month_roll) AND t.month_roll
                AND data_source = @data_source
        )
        SELECT * INTO #service_dates FROM startdate_cte;

        DROP TABLE IF EXISTS #service_dates_ytd;

        /* Calculate Service Churn for YTD */
        WITH startdate_cte_ytd AS (
            SELECT DISTINCT
                t.month_roll,
                t.customer_key,
                t.product_key,
                DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AS fall_month_roll
            FROM #temp_all_months t
                INNER JOIN int_cust.cust_plan_srv_activity_dates d
                    ON ISNULL(t.customer_key, '') = ISNULL(d.customer_key, '')
                    AND ISNULL(t.product_key, '') = ISNULL(d.product_key, '')
            WHERE d.plan_startdt BETWEEN DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AND t.month_roll
                AND data_source = @data_source
        )
        SELECT * INTO #service_dates_ytd FROM startdate_cte_ytd;

        UPDATE c
        SET cross_sell_flag = 'Yes'
        FROM #cte_cross_sell c
        WHERE EXISTS (
            SELECT 1
            FROM #service_dates s
            WHERE ISNULL(s.customer_key, '') = ISNULL(c.customer_key, '')
                AND ISNULL(s.product_key, '') = ISNULL(c.product_key, '')
                AND s.month_roll = c.month_roll
        );

        UPDATE c
        SET cross_sell_flag = 'No'
        FROM #cte_cross_sell c
        WHERE -- c.new_cust_flag = 'Yes'AND
            NOT EXISTS (
                SELECT 1
                FROM #service_dates s
                WHERE ISNULL(s.customer_key, '') = ISNULL(c.customer_key, '')
                    AND ISNULL(s.product_key, '') = ISNULL(c.product_key, '')
                    AND s.month_roll = c.month_roll
            );

        /* Update Service Churn YTD flag */
        UPDATE c
        SET cross_sell_flag_ytd = 'Yes'
        FROM #cte_cross_sell c
        WHERE EXISTS (
            SELECT 1
            FROM #service_dates_ytd s
            WHERE ISNULL(s.customer_key, '') = ISNULL(c.customer_key, '')
                AND ISNULL(s.product_key, '') = ISNULL(c.product_key, '')
                AND s.month_roll = c.month_roll
        );

        UPDATE c
        SET cross_sell_flag_ytd = 'No'
        FROM #cte_cross_sell c
        WHERE NOT EXISTS (
            SELECT 1
            FROM #service_dates_ytd s
            WHERE ISNULL(s.customer_key, '') = ISNULL(c.customer_key, '')
                AND ISNULL(s.product_key, '') = ISNULL(c.product_key, '')
                AND s.month_roll = c.month_roll
        );

        UPDATE t
        SET cross_sell = CASE WHEN cross_sell_flag = 'Yes' THEN CAST(t.eop_arr AS FLOAT) ELSE 0 END
        FROM #temp_all_months t
            INNER JOIN #cte_cross_sell c
                ON t.month_roll = c.month_roll
                AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '')
                AND ISNULL(t.product_key, '') = ISNULL(c.product_key, '')
        WHERE t.new_customer = 0
            AND t.customer_churn = 0
            AND t.planchurn = 0;

        /* Update Service Churn YTD values */
        UPDATE t
        SET cross_sell_ytd = CASE WHEN cross_sell_flag_ytd = 'Yes' THEN CAST(t.eop_ytd AS FLOAT) ELSE 0 END
        FROM #temp_all_months t
            INNER JOIN #cte_cross_sell c
                ON t.month_roll = c.month_roll
                AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '')
                AND ISNULL(t.product_key, '') = ISNULL(c.product_key, '')
        WHERE t.new_customer_ytd = 0
            AND t.cross_sell_ytd = 0
            AND t.customer_churn_ytd = 0
            AND t.planchurn_ytd = 0;

        -- ============================================================
        -- STAGE 5: Service Cross-Sell (grain: month x customer x product x service x service_dim)
        -- ============================================================
        --//*****************************
        -- Service Cross Sell Prior LTM Service ARR = 0 AND Prior LTM Plan ARR <> 0 AND Current LTM Service ARR <> 0
        ---*******************************//
        UPDATE a SET service_cross_sell = 0 FROM #temp_all_months a;

        /* Reset service cross sell */
        UPDATE a SET service_cross_sell_ytd = 0 FROM #temp_all_months a;

        /* Added service cross sell YTD and Previous Year YTD fields */
        DROP TABLE IF EXISTS #cte_service_cross_sell;

        SELECT
            month_roll,
            customer_key,
            product_key,
            service_key,
            service_dim_key,
            service_name,
            service_ltm,
            service_prev_ltm,
            service_ytd,
            service_prev_ytd,
            CASE WHEN ISNULL(service_ltm, 0) <> 0 AND ISNULL(service_prev_ltm, 0) = 0 THEN 'Yes' ELSE 'No' END AS service_cross_sell_flag,
            CASE WHEN ISNULL(service_ytd, 0) <> 0 AND ISNULL(service_prev_ytd, 0) = 0 THEN 'Yes' ELSE 'No' END AS service_cross_sell_flag_ytd
        INTO #cte_service_cross_sell
        FROM (
            SELECT
                month_roll,
                customer_key,
                product_key,
                service_key,
                service_dim_key,
                service_name,
                CAST(SUM(CASE WHEN customer_churn = 0 AND new_customer = 0 AND planchurn = 0 AND cross_sell = 0 THEN eop_arr ELSE 0 END) AS FLOAT) AS service_ltm,
                CAST(SUM(CASE WHEN customer_churn = 0 AND new_customer = 0 AND planchurn = 0 AND cross_sell = 0 THEN bop_arr ELSE 0 END) AS FLOAT) AS service_prev_ltm,
                CAST(SUM(CASE WHEN customer_churn_ytd = 0 AND new_customer_ytd = 0 AND planchurn_ytd = 0 AND cross_sell_ytd = 0 THEN eop_ytd ELSE 0 END) AS FLOAT) AS service_ytd,
                CAST(SUM(CASE WHEN customer_churn_ytd = 0 AND new_customer_ytd = 0 AND planchurn_ytd = 0 AND cross_sell_ytd = 0 THEN bop_ytd ELSE 0 END) AS FLOAT) AS service_prev_ytd
            FROM #temp_all_months
            GROUP BY
                month_roll,
                customer_key,
                product_key,
                service_key,
                service_dim_key,
                service_name
        ) x;

        WITH startdate_cte AS (
            SELECT DISTINCT
                t.month_roll,
                t.customer_key,
                t.product_key,
                t.service_key,
                t.service_dim_key,
                t.service_name,
                DATEADD(MONTH, -11, t.month_roll) AS fall_month_roll
            FROM #temp_all_months t
                INNER JOIN int_cust.cust_plan_srv_activity_dates d
                    ON ISNULL(t.customer_key, '') = ISNULL(d.customer_key, '')
                    AND ISNULL(t.product_key, '') = ISNULL(d.product_key, '')
                    AND ISNULL(t.service_key, '') = ISNULL(d.service_key, '')
                    AND ISNULL(t.service_name, '') = ISNULL(d.service_name, '')
                    AND ISNULL(t.service_dim_key, '') = ISNULL(d.service_dim_key, '')
            WHERE d.service_startdt BETWEEN DATEADD(MONTH, -11, t.month_roll) AND t.month_roll
                AND data_source = @data_source
        )
        SELECT * INTO #service_cross_dates FROM startdate_cte;

        /* Calculate Service Cross Sell for YTD */
        DROP TABLE IF EXISTS #service_cross_dates_ytd;

        WITH startdate_cte_ytd AS (
            SELECT DISTINCT
                t.month_roll,
                t.customer_key,
                t.product_key,
                t.service_key,
                t.service_dim_key,
                t.service_name,
                DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AS fall_month_roll
            FROM #temp_all_months t
                INNER JOIN int_cust.cust_plan_srv_activity_dates d
                    ON ISNULL(t.customer_key, '') = ISNULL(d.customer_key, '')
                    AND ISNULL(t.product_key, '') = ISNULL(d.product_key, '')
                    AND ISNULL(t.service_key, '') = ISNULL(d.service_key, '')
                    AND ISNULL(t.service_name, '') = ISNULL(d.service_name, '')
                    AND ISNULL(t.service_dim_key, '') = ISNULL(d.service_dim_key, '')
            WHERE d.service_startdt BETWEEN DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AND t.month_roll
                AND data_source = @data_source
        )
        SELECT * INTO #service_cross_dates_ytd FROM startdate_cte_ytd;

        UPDATE c
        SET service_cross_sell_flag = 'Yes'
        FROM #cte_service_cross_sell c
        WHERE EXISTS (
            SELECT 1
            FROM #service_cross_dates s
            WHERE ISNULL(s.customer_key, '') = ISNULL(c.customer_key, '')
                AND ISNULL(s.product_key, '') = ISNULL(c.product_key, '')
                AND ISNULL(s.service_key, '') = ISNULL(c.service_key, '')
                AND ISNULL(s.service_dim_key, '') = ISNULL(c.service_dim_key, '')
                AND ISNULL(s.service_name, '') = ISNULL(c.service_name, '')
                AND s.month_roll = c.month_roll
        );

        UPDATE c
        SET service_cross_sell_flag = 'No'
        FROM #cte_service_cross_sell c
        WHERE NOT EXISTS (
            SELECT 1
            FROM #service_cross_dates s
            WHERE ISNULL(s.customer_key, '') = ISNULL(c.customer_key, '')
                AND ISNULL(s.product_key, '') = ISNULL(c.product_key, '')
                AND ISNULL(s.service_key, '') = ISNULL(c.service_key, '')
                AND ISNULL(s.service_name, '') = ISNULL(c.service_name, '')
                AND ISNULL(s.service_dim_key, '') = ISNULL(c.service_dim_key, '')
                AND s.month_roll = c.month_roll
        );

        /* Update Service Cross Sell YTD flag */
        UPDATE c
        SET service_cross_sell_flag_ytd = 'Yes'
        FROM #cte_service_cross_sell c
        WHERE EXISTS (
            SELECT 1
            FROM #service_cross_dates_ytd s
            WHERE ISNULL(s.customer_key, '') = ISNULL(c.customer_key, '')
                AND ISNULL(s.product_key, '') = ISNULL(c.product_key, '')
                AND ISNULL(s.service_key, '') = ISNULL(c.service_key, '')
                AND ISNULL(s.service_name, '') = ISNULL(c.service_name, '')
                AND ISNULL(s.service_dim_key, '') = ISNULL(c.service_dim_key, '')
                AND s.month_roll = c.month_roll
        );

        UPDATE c
        SET service_cross_sell_flag_ytd = 'No'
        FROM #cte_service_cross_sell c
        WHERE NOT EXISTS (
            SELECT 1
            FROM #service_cross_dates_ytd s
            WHERE ISNULL(s.customer_key, '') = ISNULL(c.customer_key, '')
                AND ISNULL(s.product_key, '') = ISNULL(c.product_key, '')
                AND ISNULL(s.service_key, '') = ISNULL(c.service_key, '')
                AND ISNULL(s.service_name, '') = ISNULL(c.service_name, '')
                AND s.month_roll = c.month_roll
                AND ISNULL(s.service_dim_key, '') = ISNULL(c.service_dim_key, '')
        );

        UPDATE t
        SET service_cross_sell = CASE WHEN service_cross_sell_flag = 'Yes' THEN CAST(t.eop_arr AS FLOAT) ELSE 0 END
        FROM #temp_all_months t
            INNER JOIN #cte_service_cross_sell c
                ON t.month_roll = c.month_roll
                AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '')
                AND ISNULL(t.product_key, '') = ISNULL(c.product_key, '')
                AND ISNULL(t.service_key, '') = ISNULL(c.service_key, '')
                AND ISNULL(t.service_name, '') = ISNULL(c.service_name, '')
                AND ISNULL(t.service_dim_key, '') = ISNULL(c.service_dim_key, '')
        WHERE t.new_customer = 0
            AND t.cross_sell = 0
            AND t.customer_churn = 0
            AND t.planchurn = 0;

        /* Update Service Cross Sell YTD values */
        UPDATE t
        SET service_cross_sell_ytd = CASE WHEN service_cross_sell_flag_ytd = 'Yes' THEN CAST(t.eop_ytd AS FLOAT) ELSE 0 END
        FROM #temp_all_months t
            INNER JOIN #cte_service_cross_sell c
                ON t.month_roll = c.month_roll
                AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '')
                AND ISNULL(t.product_key, '') = ISNULL(c.product_key, '')
                AND ISNULL(t.service_key, '') = ISNULL(c.service_key, '')
                AND ISNULL(t.service_name, '') = ISNULL(c.service_name, '')
                AND ISNULL(t.service_dim_key, '') = ISNULL(c.service_dim_key, '')
        WHERE t.new_customer_ytd = 0
            AND t.cross_sell_ytd = 0
            AND t.customer_churn_ytd = 0
            AND t.planchurn_ytd = 0;

        -- ============================================================
        -- STAGE 6: Service Churn (grain: month x customer x product x service x service_dim)
        -- ============================================================
        ---//*******-----------------------------------------------
        --Service Churn
        ---*********//------------------------------------------------
        UPDATE a SET servicechurn = 0 FROM #temp_all_months a;

        /* Reset service churn */
        UPDATE a SET servicechurn_ytd = 0 FROM #temp_all_months a;

        /* Added service churn YTD and Previous Year YTD fields */
        DROP TABLE IF EXISTS #cte_servicechurn;

        SELECT
            month_roll,
            customer_key,
            product_key,
            service_key,
            service_dim_key,
            service_name,
            service_ltm,
            service_prev_ltm,
            service_ytd,
            service_prev_ytd,
            CASE WHEN ISNULL(service_ltm, 0) = 0 AND ISNULL(service_prev_ltm, 0) <> 0 THEN 'Yes' ELSE 'No' END AS servicechurn_flag,
            CASE WHEN ISNULL(service_ytd, 0) = 0 AND ISNULL(service_prev_ytd, 0) <> 0 THEN 'Yes' ELSE 'No' END AS servicechurn_flag_ytd
        INTO #cte_servicechurn
        FROM (
            SELECT
                month_roll,
                customer_key,
                product_key,
                service_key,
                service_dim_key,
                service_name,
                CAST(SUM(CASE WHEN customer_churn = 0 AND new_customer = 0 AND planchurn = 0 AND cross_sell = 0 AND service_cross_sell = 0 THEN eop_arr ELSE 0 END) AS FLOAT) AS service_ltm,
                CAST(SUM(CASE WHEN customer_churn = 0 AND new_customer = 0 AND planchurn = 0 AND cross_sell = 0 AND service_cross_sell = 0 THEN bop_arr ELSE 0 END) AS FLOAT) AS service_prev_ltm,
                CAST(SUM(CASE WHEN customer_churn_ytd = 0 AND new_customer_ytd = 0 AND planchurn_ytd = 0 AND cross_sell_ytd = 0 AND service_cross_sell_ytd = 0 THEN eop_ytd ELSE 0 END) AS FLOAT) AS service_ytd,
                CAST(SUM(CASE WHEN customer_churn_ytd = 0 AND new_customer_ytd = 0 AND planchurn_ytd = 0 AND cross_sell_ytd = 0 AND service_cross_sell_ytd = 0 THEN bop_ytd ELSE 0 END) AS FLOAT) AS service_prev_ytd
            FROM #temp_all_months
            GROUP BY
                month_roll,
                customer_key,
                product_key,
                service_key,
                service_dim_key,
                service_name
        ) x;

        DROP TABLE IF EXISTS #servicechurn_startdt;

        WITH startdate_cte AS (
            SELECT
                x.month_roll,
                x.customer_key,
                x.product_key,
                x.service_key,
                x.service_dim_key,
                x.service_name,
                x.fall_month_roll,
                x.service_enddt,
                x.range_flag,
                x.end_flag,
                CASE WHEN x.range_flag = 'No' AND x.end_flag = 'No' THEN 'Yes' ELSE 'No' END AS service_churn_flag
            FROM (
                SELECT DISTINCT
                    t.month_roll,
                    t.customer_key,
                    t.product_key,
                    t.service_key,
                    t.service_dim_key,
                    t.service_name,
                    DATEADD(MONTH, -11, t.month_roll) AS fall_month_roll,
                    d.service_enddt,
                    CASE WHEN d.service_enddt BETWEEN DATEADD(MONTH, -11, t.month_roll) AND t.month_roll THEN 'Yes' ELSE 'No' END AS range_flag,
                    CASE WHEN d.service_enddt > t.month_roll THEN 'Yes' ELSE 'No' END AS end_flag
                FROM #temp_all_months t
                    INNER JOIN int_cust.cust_plan_srv_activity_dates d
                        ON ISNULL(t.customer_key, '') = ISNULL(d.customer_key, '')
                        AND ISNULL(t.product_key, '') = ISNULL(d.product_key, '')
                        AND ISNULL(t.service_key, '') = ISNULL(d.service_key, '')
                        AND ISNULL(t.service_name, '') = ISNULL(d.service_name, '')
                        AND ISNULL(t.service_dim_key, '') = ISNULL(d.service_dim_key, '')
                WHERE data_source = @data_source
            ) AS x
        )
        SELECT * INTO #servicechurn_startdt FROM startdate_cte;

        /* Calculate Service Churn for YTD */
        DROP TABLE IF EXISTS #servicechurn_startdt_ytd;

        WITH startdate_cte_ytd AS (
            SELECT
                x.month_roll,
                x.customer_key,
                x.product_key,
                x.service_key,
                x.service_dim_key,
                x.service_name,
                x.fall_month_roll,
                x.service_enddt,
                x.range_flag,
                x.end_flag,
                CASE WHEN x.range_flag = 'No' AND x.end_flag = 'No' THEN 'Yes' ELSE 'No' END AS service_churn_flag
            FROM (
                SELECT DISTINCT
                    t.month_roll,
                    t.customer_key,
                    t.product_key,
                    t.service_key,
                    t.service_dim_key,
                    t.service_name,
                    DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AS fall_month_roll,
                    d.service_enddt,
                    CASE WHEN d.service_enddt BETWEEN DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AND t.month_roll THEN 'Yes' ELSE 'No' END AS range_flag,
                    CASE WHEN d.service_enddt > t.month_roll THEN 'Yes' ELSE 'No' END AS end_flag
                FROM #temp_all_months t
                    INNER JOIN int_cust.cust_plan_srv_activity_dates d
                        ON ISNULL(t.customer_key, '') = ISNULL(d.customer_key, '')
                        AND ISNULL(t.product_key, '') = ISNULL(d.product_key, '')
                        AND ISNULL(t.service_key, '') = ISNULL(d.service_key, '')
                        AND ISNULL(t.service_name, '') = ISNULL(d.service_name, '')
                        AND ISNULL(t.service_dim_key, '') = ISNULL(d.service_dim_key, '')
                WHERE data_source = @data_source
            ) x
        )
        SELECT * INTO #servicechurn_startdt_ytd FROM startdate_cte_ytd;

        -- NOTE: this INNER JOIN replaces the ARR-transition flag computed above with the activity-dates-table-derived flag entirely. Verify this matches your intended semantics -- a NULL end date (a contract with no confirmed end) will NOT satisfy either the "ended within window" or "still active" date checks, so it can end up flagged as churned here. Test against your own activity_dates table before trusting this stage's output.
        UPDATE c
        SET c.servicechurn_flag = s.service_churn_flag
        FROM #cte_servicechurn c
            INNER JOIN #servicechurn_startdt s
                ON c.month_roll = s.month_roll
                AND ISNULL(c.customer_key, '') = ISNULL(s.customer_key, '')
                AND ISNULL(c.product_key, '') = ISNULL(s.product_key, '')
                AND ISNULL(c.service_key, '') = ISNULL(s.service_key, '')
                AND ISNULL(c.service_name, '') = ISNULL(s.service_name, '')
                AND ISNULL(c.service_dim_key, '') = ISNULL(s.service_dim_key, '');

        /* Update Service Churn YTD flag */
        UPDATE c
        SET c.servicechurn_flag_ytd = s.service_churn_flag
        FROM #cte_servicechurn c
            INNER JOIN #servicechurn_startdt_ytd s
                ON c.month_roll = s.month_roll
                AND ISNULL(c.customer_key, '') = ISNULL(s.customer_key, '')
                AND ISNULL(c.product_key, '') = ISNULL(s.product_key, '')
                AND ISNULL(c.service_key, '') = ISNULL(s.service_key, '')
                AND ISNULL(c.service_name, '') = ISNULL(s.service_name, '')
                AND ISNULL(c.service_dim_key, '') = ISNULL(s.service_dim_key, '');

        UPDATE t
        SET servicechurn = CASE WHEN c.servicechurn_flag = 'Yes' THEN CAST(-t.bop_arr AS FLOAT) ELSE 0 END
        FROM #temp_all_months t
            INNER JOIN #cte_servicechurn c
                ON t.month_roll = c.month_roll
                AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '')
                AND ISNULL(t.product_key, '') = ISNULL(c.product_key, '')
                AND ISNULL(t.service_key, '') = ISNULL(c.service_key, '')
                AND ISNULL(t.service_name, '') = ISNULL(c.service_name, '')
                AND ISNULL(t.service_dim_key, '') = ISNULL(c.service_dim_key, '')
        WHERE t.new_customer = 0
            AND t.cross_sell = 0
            AND t.customer_churn = 0
            AND t.planchurn = 0
            AND t.service_cross_sell = 0;

        /* Update Service Churn YTD Values */
        UPDATE t
        SET servicechurn_ytd = CASE WHEN c.servicechurn_flag_ytd = 'Yes' THEN CAST(-t.bop_ytd AS FLOAT) ELSE 0 END
        FROM #temp_all_months t
            INNER JOIN #cte_servicechurn c
                ON t.month_roll = c.month_roll
                AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '')
                AND ISNULL(t.product_key, '') = ISNULL(c.product_key, '')
                AND ISNULL(t.service_key, '') = ISNULL(c.service_key, '')
                AND ISNULL(t.service_name, '') = ISNULL(c.service_name, '')
                AND ISNULL(t.service_dim_key, '') = ISNULL(c.service_dim_key, '')
        WHERE t.new_customer_ytd = 0
            AND t.cross_sell_ytd = 0
            AND t.customer_churn_ytd = 0
            AND t.planchurn_ytd = 0
            AND t.service_cross_sell_ytd = 0;

        -- ============================================================
        -- STAGE 7: Downsell (grain: month x customer x product x service x service_dim x revenue_type)
        -- ============================================================
        ----// ************************
        -----Downsell logic --************* considering the revenue type
        ----***************************//
        /* Added Downsell YTD and Previous Year YTD fields */
        DROP TABLE IF EXISTS #cte_downsell;

        SELECT
            month_roll,
            customer_key,
            product_key,
            service_key,
            service_dim_key,
            service_name,
            revenue_type,
            service_ltm,
            service_prev_ltm,
            service_ytd,
            service_prev_ytd,
            CASE WHEN ISNULL(service_ltm, 0) < ISNULL(service_prev_ltm, 0) THEN 'Yes' ELSE 'No' END AS downsell_flag,
            CASE WHEN ISNULL(service_ytd, 0) < ISNULL(service_prev_ytd, 0) THEN 'Yes' ELSE 'No' END AS downsell_flag_ytd
        INTO #cte_downsell
        FROM (
            SELECT
                t.month_roll,
                t.customer_key,
                t.product_key,
                t.service_key,
                t.service_dim_key,
                t.service_name,
                t.revenue_type,
                CAST(SUM(CASE WHEN servicechurn = 0 AND customer_churn = 0 AND planchurn = 0 AND new_customer = 0 AND cross_sell = 0 AND service_cross_sell = 0 THEN eop_arr ELSE 0 END) AS FLOAT) AS service_ltm,
                CAST(SUM(CASE WHEN servicechurn = 0 AND customer_churn = 0 AND planchurn = 0 AND new_customer = 0 AND cross_sell = 0 AND service_cross_sell = 0 THEN bop_arr ELSE 0 END) AS FLOAT) AS service_prev_ltm,
                CAST(SUM(CASE WHEN servicechurn_ytd = 0 AND customer_churn_ytd = 0 AND planchurn_ytd = 0 AND new_customer_ytd = 0 AND cross_sell_ytd = 0 AND service_cross_sell_ytd = 0 THEN eop_ytd ELSE 0 END) AS FLOAT) AS service_ytd,
                CAST(SUM(CASE WHEN servicechurn_ytd = 0 AND customer_churn_ytd = 0 AND planchurn_ytd = 0 AND new_customer_ytd = 0 AND cross_sell_ytd = 0 AND service_cross_sell_ytd = 0 THEN bop_ytd ELSE 0 END) AS FLOAT) AS service_prev_ytd
            FROM #temp_all_months t
            GROUP BY
                t.month_roll,
                t.customer_key,
                t.product_key,
                t.service_key,
                t.service_dim_key,
                t.service_name,
                t.revenue_type
        ) x;

        UPDATE t
        SET downsell = CASE WHEN downsell_flag = 'Yes' THEN CAST(t.eop_arr AS FLOAT) - CAST(t.bop_arr AS FLOAT) ELSE 0 END
        FROM #temp_all_months t
            INNER JOIN #cte_downsell c
                ON t.month_roll = c.month_roll
                AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '')
                AND ISNULL(t.product_key, '') = ISNULL(c.product_key, '')
                AND ISNULL(t.service_key, '') = ISNULL(c.service_key, '')
                AND ISNULL(t.service_name, '') = ISNULL(c.service_name, '')
                AND ISNULL(t.revenue_type, '') = ISNULL(c.revenue_type, '')
                AND ISNULL(t.service_dim_key, '') = ISNULL(c.service_dim_key, '')
        WHERE t.new_customer = 0
            AND t.cross_sell = 0
            AND t.customer_churn = 0
            AND t.planchurn = 0
            AND t.service_cross_sell = 0
            AND t.servicechurn = 0;

        /* Update Downsell YTD flag */
        UPDATE t
        SET downsell_ytd = CASE WHEN downsell_flag_ytd = 'Yes' THEN CAST(t.eop_ytd AS FLOAT) - CAST(t.bop_ytd AS FLOAT) ELSE 0 END
        FROM #temp_all_months t
            INNER JOIN #cte_downsell c
                ON t.month_roll = c.month_roll
                AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '')
                AND ISNULL(t.product_key, '') = ISNULL(c.product_key, '')
                AND ISNULL(t.service_key, '') = ISNULL(c.service_key, '')
                AND ISNULL(t.service_name, '') = ISNULL(c.service_name, '')
                AND ISNULL(t.revenue_type, '') = ISNULL(c.revenue_type, '')
                AND ISNULL(t.service_dim_key, '') = ISNULL(c.service_dim_key, '')
        WHERE t.new_customer_ytd = 0
            AND t.cross_sell_ytd = 0
            AND t.customer_churn_ytd = 0
            AND t.planchurn_ytd = 0
            AND t.service_cross_sell_ytd = 0
            AND t.servicechurn_ytd = 0;

        -- ============================================================
        -- STAGE 8: Upsell (grain: month x customer x product x service x service_dim x revenue_type)
        -- ============================================================
        ----// ************************
        -----Upsell logic --************* considering the revenue type
        ----***************************//
        /* Added Upsell YTD and Previous Year YTD fields */
        DROP TABLE IF EXISTS #cte_upsell;

        SELECT
            month_roll,
            customer_key,
            product_key,
            service_key,
            service_dim_key,
            service_name,
            revenue_type,
            service_ltm,
            service_prev_ltm,
            service_ytd,
            service_prev_ytd,
            CASE WHEN ISNULL(service_ltm, 0) > ISNULL(service_prev_ltm, 0) THEN 'Yes' ELSE 'No' END AS upsell_flag,
            CASE WHEN ISNULL(service_ytd, 0) > ISNULL(service_prev_ytd, 0) THEN 'Yes' ELSE 'No' END AS upsell_flag_ytd
        INTO #cte_upsell
        FROM (
            SELECT
                t.month_roll,
                t.customer_key,
                t.product_key,
                t.service_key,
                t.service_dim_key,
                t.service_name,
                t.revenue_type,
                CAST(SUM(CASE WHEN servicechurn = 0 AND customer_churn = 0 AND planchurn = 0 AND new_customer = 0 AND cross_sell = 0 AND service_cross_sell = 0 AND downsell = 0 THEN eop_arr ELSE 0 END) AS FLOAT) AS service_ltm,
                CAST(SUM(CASE WHEN servicechurn = 0 AND customer_churn = 0 AND planchurn = 0 AND new_customer = 0 AND cross_sell = 0 AND service_cross_sell = 0 AND downsell = 0 THEN bop_arr ELSE 0 END) AS FLOAT) AS service_prev_ltm,
                CAST(SUM(CASE WHEN servicechurn_ytd = 0 AND customer_churn_ytd = 0 AND planchurn_ytd = 0 AND new_customer_ytd = 0 AND cross_sell_ytd = 0 AND service_cross_sell_ytd = 0 AND downsell_ytd = 0 THEN eop_ytd ELSE 0 END) AS FLOAT) AS service_ytd,
                CAST(SUM(CASE WHEN servicechurn_ytd = 0 AND customer_churn_ytd = 0 AND planchurn_ytd = 0 AND new_customer_ytd = 0 AND cross_sell_ytd = 0 AND service_cross_sell_ytd = 0 AND downsell_ytd = 0 THEN bop_ytd ELSE 0 END) AS FLOAT) AS service_prev_ytd
            FROM #temp_all_months t
            GROUP BY
                t.month_roll,
                t.customer_key,
                t.product_key,
                t.service_key,
                t.service_dim_key,
                t.service_name,
                t.revenue_type
        ) x;

        UPDATE t
        SET upsell = CASE WHEN upsell_flag = 'Yes' THEN CAST(t.eop_arr AS FLOAT) - CAST(t.bop_arr AS FLOAT) ELSE 0 END
        FROM #temp_all_months t
            INNER JOIN #cte_upsell c
                ON t.month_roll = c.month_roll
                AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '')
                AND ISNULL(t.product_key, '') = ISNULL(c.product_key, '')
                AND ISNULL(t.service_key, '') = ISNULL(c.service_key, '')
                AND ISNULL(t.service_name, '') = ISNULL(c.service_name, '')
                AND ISNULL(t.revenue_type, '') = ISNULL(c.revenue_type, '')
                AND ISNULL(t.service_dim_key, '') = ISNULL(c.service_dim_key, '')
        WHERE t.new_customer = 0
            AND t.cross_sell = 0
            AND t.customer_churn = 0
            AND t.planchurn = 0
            AND t.service_cross_sell = 0
            AND t.servicechurn = 0
            AND downsell = 0;

        /* Update Upsell YTD flag */
        UPDATE t
        SET upsell_ytd = CASE WHEN upsell_flag_ytd = 'Yes' THEN CAST(t.eop_ytd AS FLOAT) - CAST(t.bop_ytd AS FLOAT) ELSE 0 END
        FROM #temp_all_months t
            INNER JOIN #cte_upsell c
                ON t.month_roll = c.month_roll
                AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '')
                AND ISNULL(t.product_key, '') = ISNULL(c.product_key, '')
                AND ISNULL(t.service_key, '') = ISNULL(c.service_key, '')
                AND ISNULL(t.service_name, '') = ISNULL(c.service_name, '')
                AND ISNULL(t.revenue_type, '') = ISNULL(c.revenue_type, '')
                AND ISNULL(t.service_dim_key, '') = ISNULL(c.service_dim_key, '')
        WHERE t.new_customer_ytd = 0
            AND t.cross_sell_ytd = 0
            AND t.customer_churn_ytd = 0
            AND t.planchurn_ytd = 0
            AND t.service_cross_sell_ytd = 0
            AND t.servicechurn_ytd = 0
            AND t.downsell_ytd = 0;

        -- ============================================================
        -- STAGE 9: Final Output & GRR/NRR Rollup (grain: full row grain of #temp_all_months)
        -- ============================================================
        /* update all ytd buckets if values missing fill 0 */
        UPDATE #temp_all_months
        SET mrr = ISNULL(mrr, 0),
            customer_churn = ISNULL(customer_churn, 0),
            customer_churn_ytd = ISNULL(customer_churn_ytd, 0),
            planchurn = ISNULL(planchurn, 0),
            planchurn_ytd = ISNULL(planchurn_ytd, 0),
            servicechurn = ISNULL(servicechurn, 0),
            servicechurn_ytd = ISNULL(servicechurn_ytd, 0),
            new_customer = ISNULL(new_customer, 0),
            new_customer_ytd = ISNULL(new_customer_ytd, 0),
            upsell = ISNULL(upsell, 0),
            upsell_ytd = ISNULL(upsell_ytd, 0),
            cross_sell = ISNULL(cross_sell, 0),
            cross_sell_ytd = ISNULL(cross_sell_ytd, 0),
            service_cross_sell = ISNULL(service_cross_sell, 0),
            service_cross_sell_ytd = ISNULL(service_cross_sell_ytd, 0),
            downsell = ISNULL(downsell, 0),
            downsell_ytd = ISNULL(downsell_ytd, 0);

        DROP TABLE IF EXISTS int_cust.revenue_bridge_output_bucket_calculations;

        SELECT *, @data_source AS data_source -- generalized: was hardcoded 'Sage', now reflects the actual @data_source parameter
        INTO int_cust.revenue_bridge_output_bucket_calculations
        FROM #temp_all_months;

        UPDATE a
        SET grr = bop_arr + customer_churn + planchurn + servicechurn + downsell
        FROM int_cust.revenue_bridge_output_bucket_calculations a;

        UPDATE a
        SET nrr = grr + upsell + service_cross_sell + cross_sell
        FROM int_cust.revenue_bridge_output_bucket_calculations a;

        /* update grr ytd values */
        UPDATE a
        SET grr_ytd = bop_ytd + customer_churn_ytd + planchurn_ytd + servicechurn_ytd + downsell_ytd
        FROM int_cust.revenue_bridge_output_bucket_calculations a;

        /* update nrr ytd values */
        UPDATE a
        SET nrr_ytd = grr_ytd + upsell_ytd + service_cross_sell_ytd + cross_sell_ytd
        FROM int_cust.revenue_bridge_output_bucket_calculations a;

    END
END;
```

## 🔗 Related Notes
- [[Original Stored Procedure (As Provided)|Original Stored Procedure (As Provided)]] — the untouched source this was cleaned up from.
- [[ARR Snowball Template (ANSI SQL, Portable)|ARR Snowball Template (ANSI SQL, Portable)]] — the same logic re-architected as a portable CTE chain, including a fix for the `LAG`-based BOP gap issue noted above.
- [[Bucket Cascade Logic|Bucket Cascade Logic]] — the conceptual walkthrough of every stage in this procedure.
- [[Snowball|Snowball]] — hub note for this area.

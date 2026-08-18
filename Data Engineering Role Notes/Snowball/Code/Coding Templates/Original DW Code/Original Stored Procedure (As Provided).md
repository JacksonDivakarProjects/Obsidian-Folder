This is the **untouched, original** version of the ARR snowball stored procedure, kept exactly as it was first added to this vault. It's preserved here for provenance and diffing — every other note in this folder should be treated as the current, actively-used version; this one exists purely so the cleanup in [[Standardized ARR Snowball Procedure (T-SQL)|Standardized ARR Snowball Procedure (T-SQL)]] can always be checked against what it started from.

Do not edit this note. If you need to make a change to the logic, make it in the standardized version instead.

```sql
/*
-- EXEC [cust].[usp_build_customer_cube]
-- EXEC [cust].[usp_build_revenue_bridge_output]
exec [cust].[usp_revenue_bridge_bucket_calculations] 'Sage'
*/
CREATE PROCEDURE [cust].[usp_revenue_bridge_bucket_calculations]
(@data_source varchar(100))
AS
BEGIN
SET NOCOUNT ON;
--DROP TABLE IF EXISTS cust.revenue_bridge_buckets_output_data_V2;
IF(@data_source='Sage')
begin
/*=========================================================
STEP 1: Base with BoP ARR using LAG
=========================================================*/
drop table if exists #temp_all_months;
select
month_roll,
customer_key,
product_key,
service_key,
service_name,
service_dim_key,
revenue_type,
location_key,
mrr ,
service_arr,
service_arr as eop_arr,
LAG(service_arr, 12) OVER (
PARTITION BY isnull(customer_key, ''),
isnull(product_key, ''),
isnull(service_key, ''),
isnull(revenue_type, ''),
isnull(location_key, ''),isnull(service_dim_key,'')
ORDER BY
month_roll
) AS bop_arr,
service_ytd,
service_ytd as eop_ytd,
service_ytd_bop as bop_ytd,
ytd_movement,
cast(0 as float) as customer_churn,
cast(0 as float) as planchurn,
cast(0 as float) as servicechurn
,
cast(0 as float) as new_customer,
cast(0 as float) as cross_sell,
cast(0 as float) as service_cross_sell
,
cast(0 as float) as nrr,
cast(0 as float) as grr,
/* Added YTD calculation fields */
cast(0 as float) as nrr_ytd,
cast(0 as float) as grr_ytd,
cast(0 as float) as upsell,
cast(0 as float) as upsell_ytd,
cast(0 as float) as downsell,
cast(0 as float) as downsell_ytd,
cast(0 as float) as customer_churn_ytd,
cast(0 as float) as planchurn_ytd,
cast(0 as float) as servicechurn_ytd,
cast(0 as float) as new_customer_ytd,
cast(0 as float) as cross_sell_ytd,
cast(0 as float) as service_cross_sell_ytd
into #temp_all_months
from cust.customer_cube_monthly
WHERE data_source='Sage';
update #temp_all_months set bop_arr = isnull(bop_arr, 0) , eop_arr = isnull(eop_arr, 0), eop_ytd = ISNULL(eop_ytd, 0), bop_ytd = ISNULL(bop_ytd, 0);
---//*****************************
-- Customer Churn --Removed location key
---*******************************//
-- Reset churn
UPDATE a SET customer_churn = 0 FROM #temp_all_months a;
/* reset customer churn YTD */
UPDATE a SET customer_churn_ytd = 0 FROM #temp_all_months a;
------------------------------------------------------------
/* Added Customer YTD and Previous Year YTD fields */
SELECT month_roll, customer_key, customer_ltm, customer_prev_ltm, customer_ytd, customer_prev_ytd,
CASE WHEN ISNULL(customer_ltm, 0) = 0 AND ISNULL(customer_prev_ltm, 0) <> 0 THEN 'Yes' ELSE 'No' END AS customerchurn_flag,
CASE WHEN ISNULL(customer_ytd, 0)= 0 AND ISNULL(customer_prev_ytd, 0)<> 0 THEN 'Yes' ELSE 'No' END AS customerchurn_flag_ytd
INTO #cte_customerchurn
FROM (
SELECT month_roll, isnull(customer_key, '')customer_key,
SUM(CAST(eop_arr AS FLOAT)) AS customer_ltm,
SUM(CAST(bop_arr AS FLOAT)) AS customer_prev_ltm,
SUM(CAST(eop_ytd AS FLOAT)) AS customer_ytd,
SUM(CAST(bop_ytd AS FLOAT)) AS customer_prev_ytd
FROM #temp_all_months
GROUP BY month_roll, isnull(customer_key, '')
) x;
DROP TABLE IF EXISTS #customerchurn_startdt;
WITH startdate_cte AS (
select x.month_roll, x.customer_key, x.fall_month_roll, x.customer_enddt, x.range_flag, x.end_flag,
case when x.range_flag = 'No' and x.end_flag = 'No' then 'Yes' else 'No' end as cust_churn_flag
from (
SELECT DISTINCT t.month_roll, t.customer_key,
DATEADD(MONTH, -11, t.month_roll) AS fall_month_roll,
d.customer_enddt,
case when d.customer_enddt BETWEEN DATEADD(MONTH, -11, t.month_roll) AND t.month_roll then 'Yes' else 'No' end as range_flag,
case when d.customer_enddt > t.month_roll then 'Yes' else 'No' end as end_flag
FROM #temp_all_months t
INNER JOIN int_cust.cust_plan_srv_activity_dates d ON isnull(t.customer_key, '') = isnull(d.customer_key, '')
where data_source = 'Sage'
) as x
)
SELECT * INTO #customerchurn_startdt FROM startdate_cte;
/* Calculate Customer Churn for YTD */
DROP TABLE IF EXISTS #customerchurn_startdt_ytd;
WITH startdate_cte_ytd AS (
select x.month_roll, x.customer_key, x.fall_month_roll, x.customer_enddt, x.range_flag, x.end_flag,
case when x.range_flag = 'No' and x.end_flag = 'No' then 'Yes' else 'No' end as cust_churn_flag
from (
SELECT DISTINCT t.month_roll, t.customer_key,
DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AS fall_month_roll,
d.customer_enddt,
case when d.customer_enddt BETWEEN DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AND t.month_roll then 'Yes' else 'No' end as range_flag,
case when d.customer_enddt > t.month_roll then 'Yes' else 'No' end as end_flag
FROM #temp_all_months t
INNER JOIN int_cust.cust_plan_srv_activity_dates d ON isnull(t.customer_key, '') = isnull(d.customer_key, '')
where data_source = 'Sage'
) as x
)
SELECT * INTO #customerchurn_startdt_ytd FROM startdate_cte_ytd;
UPDATE c SET c.customerchurn_flag = s.cust_churn_flag FROM #cte_customerchurn c inner join #customerchurn_startdt s on c.month_roll = s.month_roll and isnull(c.customer_key, '') = isnull(s.customer_key, '')
/* Update Customer Churn YTD flag */
UPDATE c SET customerchurn_flag_ytd = s.cust_churn_flag FROM #cte_customerchurn c INNER JOIN #customerchurn_startdt_ytd s ON c.month_roll = s.month_roll AND ISNULL(c.customer_key, '') = ISNULL(s.customer_key, '');
UPDATE t SET customer_churn = CASE WHEN c.customerchurn_flag = 'Yes' THEN CAST(-t.bop_arr AS FLOAT) ELSE 0 END
FROM #temp_all_months t INNER JOIN #cte_customerchurn c ON t.month_roll = c.month_roll AND isnull(t.customer_key, '') = isnull(c.customer_key, '');
/* Update Customer Churn YTD values */
UPDATE t SET customer_churn_ytd = CASE WHEN c.customerchurn_flag_ytd = 'Yes' THEN CAST(-t.bop_ytd AS FLOAT) ELSE 0 END
FROM #temp_all_months t INNER JOIN #cte_customerchurn c ON t.month_roll = c.month_roll AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '');
---//*****************************
-- New Customer --Removed location key --MF:Prior LTM Customer ARR = 0 AND Current LTM Customer ARR <> 0
---*******************************//
drop table if exists #cte_output;
/* Added Customer YTD and Previous Year YTD fields */
SELECT month_roll, customer_key, cust_ltm, cust_prev_ltm, cust_ytd, cust_prev_ytd,
CASE WHEN ISNULL(cust_ltm, 0) <> 0 AND ISNULL(cust_prev_ltm, 0) = 0 THEN 'Yes' ELSE 'No' END AS new_cust_flag,
CASE WHEN ISNULL(cust_ytd, 0) <> 0 AND ISNULL(cust_prev_ytd, 0) = 0 THEN 'Yes' ELSE 'No' END AS new_cust_flag_ytd
INTO #cte_output
FROM (
SELECT month_roll, customer_key,
CAST(SUM(CASE WHEN customer_churn = 0 THEN eop_arr ELSE 0 END) AS FLOAT) AS cust_ltm,
CAST(SUM(CASE WHEN customer_churn = 0 THEN bop_arr ELSE 0 END) AS FLOAT) AS cust_prev_ltm,
CAST(SUM(CASE WHEN customer_churn_ytd = 0 THEN eop_ytd ELSE 0 END) AS FLOAT) AS cust_ytd,
CAST(SUM(CASE WHEN customer_churn_ytd = 0 THEN bop_ytd ELSE 0 END) AS FLOAT) AS cust_prev_ytd
FROM #temp_all_months GROUP BY month_roll, customer_key
) x;
drop table if exists #customer_dates;
;WITH startdate_cte AS
(
SELECT DISTINCT t.month_roll, t.customer_key, dateadd(month, -11, t.month_roll) as fall_month_roll
FROM #temp_all_months t INNER JOIN int_cust.cust_plan_srv_activity_dates d ON isnull(t.customer_key, '') = isnull(d.customer_key, '')
WHERE d.customer_startdt BETWEEN DATEADD(MONTH, -11, t.month_roll) AND t.month_roll and data_source = 'Sage'
)
select * into #customer_dates from startdate_cte ;
/* Calculate New customer for YTD */
DROP TABLE IF EXISTS #customer_dates_ytd;
WITH startdate_cte_ytd AS
(
SELECT DISTINCT t.month_roll, t.customer_key, DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AS fall_month_roll
FROM #temp_all_months t INNER JOIN int_cust.cust_plan_srv_activity_dates d ON ISNULL(t.customer_key, '') = ISNULL(d.customer_key, '')
WHERE d.customer_startdt BETWEEN DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AND t.month_roll AND data_source = 'Sage'
)
SELECT * INTO #customer_dates_ytd FROM startdate_cte_ytd;
UPDATE c SET new_cust_flag = 'Yes' FROM #cte_output c WHERE EXISTS (SELECT 1 FROM #customer_dates s WHERE isnull(s.customer_key, '')= isnull(c.customer_key, '') AND s.month_roll = c.month_roll) ;
UPDATE c SET new_cust_flag = 'No' FROM #cte_output c WHERE NOT EXISTS (SELECT 1 FROM #customer_dates s WHERE isnull(s.customer_key, '') = isnull(c.customer_key, '') AND s.month_roll = c.month_roll) ;
/* Update New Customer YTD flag */
UPDATE c SET new_cust_flag_ytd = 'Yes' FROM #cte_output c WHERE EXISTS (SELECT 1 FROM #customer_dates_ytd s WHERE ISNULL(s.customer_key, '') = ISNULL(c.customer_key, '') AND s.month_roll = c.month_roll);
UPDATE c SET new_cust_flag_ytd = 'No' FROM #cte_output c WHERE NOT EXISTS (SELECT 1 FROM #customer_dates_ytd s WHERE ISNULL(s.customer_key, '') = ISNULL(c.customer_key, '') AND s.month_roll = c.month_roll);
update t set new_customer = case when new_cust_flag = 'Yes' then cast(t.eop_arr as float) else 0 end
from #temp_all_months t inner join #cte_output c on t.month_roll = c.month_roll and isnull(t.customer_key, '') = isnull(c.customer_key, '')
where t.customer_churn = 0;
/* Update New Cusotmer YTD values */
UPDATE t SET new_customer_ytd = CASE WHEN new_cust_flag_ytd = 'Yes' THEN CAST(t.eop_ytd AS FLOAT) ELSE 0 END
FROM #temp_all_months t INNER JOIN #cte_output c ON t.month_roll = c.month_roll AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '')
WHERE t.customer_churn_ytd = 0;
---//*****************************
-- Plan Churn --Removed location key
---*******************************//
---------------------------------------------------------------------------------------------------------------------
-- Reset churn
UPDATE a SET planchurn = 0 FROM #temp_all_months a;
/* Reset planchrun YTD */
UPDATE a SET planchurn_ytd = 0 FROM #temp_all_months a;
------------------------------------------------------------
/* Added plan YTD and Previous Year YTD fields */
DROP TABLE IF EXISTS #cte_planchurn;
SELECT month_roll, customer_key, product_key, plan_ltm, plan_prev_ltm, plan_ytd, plan_prev_ytd,
CASE WHEN ISNULL(plan_ltm, 0) = 0 AND ISNULL(plan_prev_ltm, 0) <> 0 THEN 'Yes' ELSE 'No' END AS planchurn_flag,
CASE WHEN ISNULL(plan_ytd, 0)= 0 AND ISNULL(plan_prev_ytd, 0)<> 0 THEN 'Yes' ELSE 'No' END AS planchurn_flag_ytd
INTO #cte_planchurn
FROM (
SELECT month_roll, customer_key, product_key,
CAST(SUM(CASE WHEN customer_churn = 0 AND new_customer = 0 THEN eop_arr ELSE 0 END) AS FLOAT) AS plan_ltm,
CAST(SUM(CASE WHEN customer_churn = 0 AND new_customer = 0 THEN bop_arr ELSE 0 END) AS FLOAT) AS plan_prev_ltm,
CAST(SUM(CASE WHEN customer_churn_ytd = 0 AND new_customer_ytd = 0 THEN eop_ytd ELSE 0 END) AS FLOAT) AS plan_ytd,
CAST(SUM(CASE WHEN customer_churn_ytd = 0 AND new_customer_ytd = 0 THEN bop_ytd ELSE 0 END) AS FLOAT) AS plan_prev_ytd
FROM #temp_all_months GROUP BY month_roll, customer_key, product_key
) x;
DROP TABLE IF EXISTS #planchurn_startdt;
WITH startdate_cte AS (
select x.month_roll, x.customer_key, x.product_key, x.fall_month_roll, x.plan_enddt, x.range_flag, x.end_flag,
case when x.range_flag = 'No' and x.end_flag = 'No' then 'Yes' else 'No' end as plan_churn_flag
from (
SELECT DISTINCT t.month_roll, t.customer_key, t.product_key,
DATEADD(MONTH, -11, t.month_roll) AS fall_month_roll,
d.plan_enddt,
case when d.plan_enddt BETWEEN DATEADD(MONTH, -11, t.month_roll) AND t.month_roll then 'Yes' else 'No' end as range_flag,
case when d.plan_enddt > t.month_roll then 'Yes' else 'No' end as end_flag
FROM #temp_all_months t INNER JOIN int_cust.cust_plan_srv_activity_dates d
ON isnull(t.customer_key, '')= isnull(d.customer_key, '') and isnull(t.product_key, '') = isnull(d.product_key, '')
where data_source = 'Sage'
) as x
)
SELECT * INTO #planchurn_startdt FROM startdate_cte;
/* Calculate Plan Churn for YTD */
DROP TABLE IF EXISTS #planchurn_startdt_ytd;
WITH startdate_cte_ytd AS (
select x.month_roll, x.customer_key, x.product_key, x.fall_month_roll, x.plan_enddt, x.range_flag, x.end_flag,
case when x.range_flag = 'No' and x.end_flag = 'No' then 'Yes' else 'No' end as plan_churn_flag
from (
SELECT DISTINCT t.month_roll, t.customer_key, t.product_key,
DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AS fall_month_roll,
d.plan_enddt,
case when d.plan_enddt BETWEEN DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AND t.month_roll then 'Yes' else 'No' end as range_flag,
case when d.plan_enddt > t.month_roll then 'Yes' else 'No' end as end_flag
FROM #temp_all_months t INNER JOIN int_cust.cust_plan_srv_activity_dates d
ON isnull(t.customer_key, '')= isnull(d.customer_key, '') and isnull(t.product_key, '') = isnull(d.product_key, '')
where data_source = 'Sage'
) as x
)
SELECT * INTO #planchurn_startdt_ytd FROM startdate_cte_ytd;
UPDATE c SET c.planchurn_flag = s.plan_churn_flag FROM #cte_planchurn c inner join #planchurn_startdt s on c.month_roll = s.month_roll and isnull(c.customer_key, '') = isnull(s.customer_key, '') and isnull(c.product_key, '') = isnull(s.product_key, '')
/* Update Plan Churn YTD flag */
UPDATE c SET c.planchurn_flag_ytd = s.plan_churn_flag FROM #cte_planchurn c INNER JOIN #planchurn_startdt_ytd s ON c.month_roll = s.month_roll AND ISNULL(c.customer_key, '') = ISNULL(s.customer_key, '') AND ISNULL(c.product_key, '') = ISNULL(s.product_key, '');
UPDATE t SET planchurn = CASE WHEN c.planchurn_flag = 'Yes' THEN CAST(-t.bop_arr AS FLOAT) ELSE 0 END
FROM #temp_all_months t INNER JOIN #cte_planchurn c ON t.month_roll = c.month_roll AND isnull(t.customer_key, '') = isnull(c.customer_key, '') AND isnull(t.product_key, '') = isnull(c.product_key, '')
where t.customer_churn = 0 and t.new_customer = 0;
/* Update Plan Churn YTD values */
UPDATE t SET planchurn_ytd = CASE WHEN c.planchurn_flag_ytd = 'Yes' THEN CAST(-t.bop_ytd AS FLOAT) ELSE 0 END
FROM #temp_all_months t INNER JOIN #cte_planchurn c ON t.month_roll = c.month_roll AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '') AND ISNULL(t.product_key, '') = ISNULL(c.product_key, '')
WHERE t.customer_churn_ytd = 0 AND t.new_customer_ytd = 0;
---//*****************************
-- cross sell
---*******************************//
update a set cross_sell = 0 from #temp_all_months a;
/* Reset cross sell ytd */
UPDATE a SET cross_sell_ytd = 0 FROM #temp_all_months a;
/* Added Plan YTD and Previous Year YTD fields */
drop table if exists #cte_cross_sell;
SELECT month_roll, customer_key, product_key, plan_ltm, plan_prev_ltm, plan_ytd, plan_prev_ytd,
CASE WHEN ISNULL(plan_ltm, 0) <> 0 and ISNULL(plan_prev_ltm, 0) = 0 THEN 'Yes' ELSE 'No' END AS cross_sell_flag,
CASE WHEN ISNULL(plan_ytd, 0) <> 0 AND ISNULL(plan_prev_ytd, 0) = 0 THEN 'Yes' ELSE 'No' END AS cross_sell_flag_ytd
INTO #cte_cross_sell
FROM (
SELECT month_roll, customer_key, product_key,
CAST(SUM(CASE WHEN customer_churn = 0 AND new_customer = 0 AND planchurn = 0 THEN eop_arr ELSE 0 END) AS FLOAT) AS plan_ltm,
CAST(SUM(CASE WHEN customer_churn = 0 AND new_customer = 0 AND planchurn = 0 THEN bop_arr ELSE 0 END) AS FLOAT) AS plan_prev_ltm,
CAST(SUM(CASE WHEN customer_churn_ytd = 0 AND new_customer_ytd = 0 AND planchurn_ytd = 0 THEN eop_ytd ELSE 0 END) AS FLOAT) AS plan_ytd,
CAST(SUM(CASE WHEN customer_churn_ytd = 0 AND new_customer_ytd = 0 AND planchurn_ytd = 0 THEN bop_ytd ELSE 0 END) AS FLOAT) AS plan_prev_ytd
FROM #temp_all_months GROUP BY month_roll, customer_key, product_key
) x;
drop table if exists #service_dates;
;
WITH startdate_cte AS
(
SELECT DISTINCT t.month_roll, t.customer_key, t.product_key, dateadd(month, -11, t.month_roll) as fall_month_roll
FROM #temp_all_months t INNER JOIN int_cust.cust_plan_srv_activity_dates d
ON isnull(t.customer_key, '') = isnull(d.customer_key, '') AND isnull(t.product_key, '')= isnull(d.product_key, '')
WHERE d.plan_startdt BETWEEN DATEADD(MONTH, -11, t.month_roll) AND t.month_roll and data_source = 'Sage'
)
select * into #service_dates from startdate_cte ;
drop table if exists #service_dates_ytd;
/* Calculate Service Churn for YTD */
;WITH startdate_cte_ytd AS
(
SELECT DISTINCT t.month_roll, t.customer_key, t.product_key, DATEFROMPARTS(YEAR(t.month_roll), 1, 1) as fall_month_roll
FROM #temp_all_months t INNER JOIN int_cust.cust_plan_srv_activity_dates d
ON isnull(t.customer_key, '') = isnull(d.customer_key, '') AND isnull(t.product_key, '')= isnull(d.product_key, '')
WHERE d.plan_startdt BETWEEN DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AND t.month_roll and data_source = 'Sage'
)
select * into #service_dates_ytd from startdate_cte_ytd ;
UPDATE c SET cross_sell_flag = 'Yes' FROM #cte_cross_sell c WHERE EXISTS (SELECT 1 FROM #service_dates s WHERE isnull(s.customer_key, '') = isnull(c.customer_key, '') AND isnull(s.product_key, '') = isnull(c.product_key, '') AND s.month_roll = c.month_roll) ;
UPDATE c SET cross_sell_flag = 'No' FROM #cte_cross_sell c WHERE
-- c.new_cust_flag = 'Yes'AND
NOT EXISTS (SELECT 1 FROM #service_dates s WHERE isnull(s.customer_key, '') = isnull(c.customer_key, '') AND isnull(s.product_key, '') = isnull(c.product_key, '') AND s.month_roll = c.month_roll) ;
/* Update Service Churn YTD flag */
UPDATE c SET cross_sell_flag_ytd = 'Yes' FROM #cte_cross_sell c WHERE EXISTS (SELECT 1 FROM #service_dates_ytd s WHERE ISNULL(s.customer_key, '') = ISNULL(c.customer_key, '') AND ISNULL(s.product_key, '') = ISNULL(c.product_key, '') AND s.month_roll = c.month_roll);
UPDATE c SET cross_sell_flag_ytd = 'No' FROM #cte_cross_sell c WHERE NOT EXISTS (SELECT 1 FROM #service_dates_ytd s WHERE ISNULL(s.customer_key, '') = ISNULL(c.customer_key, '') AND ISNULL(s.product_key, '') = ISNULL(c.product_key, '') AND s.month_roll = c.month_roll);
update t set cross_sell = case when cross_sell_flag = 'Yes' then cast(t.eop_arr as float) else 0 end
from #temp_all_months t inner join #cte_cross_sell c on t.month_roll = c.month_roll and isnull(t.customer_key, '') = isnull(c.customer_key, '') and isnull(t.product_key, '') = isnull(c.product_key, '')
where t.new_customer = 0 and t.customer_churn = 0 and t.planchurn = 0;
/* Update Service Churn YTD values */
UPDATE t SET cross_sell_ytd = CASE WHEN cross_sell_flag_ytd = 'Yes' THEN CAST(t.eop_ytd AS FLOAT) ELSE 0 END
FROM #temp_all_months t INNER JOIN #cte_cross_sell c ON t.month_roll = c.month_roll AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '') AND ISNULL(t.product_key, '') = ISNULL(c.product_key, '')
WHERE t.new_customer_ytd = 0 AND t.cross_sell_ytd = 0 AND t.customer_churn_ytd = 0 AND t.planchurn_ytd = 0;
--//*****************************
-- Service Cross Sell Prior LTM Service ARR = 0 AND Prior LTM Plan ARR <> 0 AND Current LTM Service ARR <> 0
---*******************************//
update a set service_cross_sell = 0 from #temp_all_months a;
/* Reset service cross sell */
UPDATE a SET service_cross_sell_ytd = 0 FROM #temp_all_months a;
/* Added service cross sell YTD and Previous Year YTD fields */
drop table if exists #cte_service_cross_sell;
SELECT month_roll, customer_key, product_key, service_key,service_dim_key, service_name, service_ltm, service_prev_ltm, service_ytd, service_prev_ytd,
CASE WHEN ISNULL(service_ltm, 0) <> 0 AND ISNULL(service_prev_ltm, 0) = 0 THEN 'Yes' ELSE 'No' END AS service_cross_sell_flag,
CASE WHEN ISNULL(service_ytd, 0) <> 0 AND ISNULL(service_prev_ytd, 0) = 0 THEN 'Yes' ELSE 'No' END AS service_cross_sell_flag_ytd
INTO #cte_service_cross_sell
FROM (
SELECT month_roll, customer_key, product_key, service_key,service_dim_key, service_name,
CAST(SUM(CASE WHEN customer_churn = 0 AND new_customer = 0 AND planchurn = 0 AND cross_sell = 0 THEN eop_arr ELSE 0 END) AS FLOAT) AS service_ltm,
CAST(SUM(CASE WHEN customer_churn = 0 AND new_customer = 0 AND planchurn = 0 AND cross_sell = 0 THEN bop_arr ELSE 0 END) AS FLOAT) AS service_prev_ltm,
CAST(SUM(CASE WHEN customer_churn_ytd = 0 AND new_customer_ytd = 0 AND planchurn_ytd = 0 AND cross_sell_ytd = 0 THEN eop_ytd ELSE 0 END) AS FLOAT) AS service_ytd,
CAST(SUM(CASE WHEN customer_churn_ytd = 0 AND new_customer_ytd = 0 AND planchurn_ytd = 0 AND cross_sell_ytd = 0 THEN bop_ytd ELSE 0 END) AS FLOAT) AS service_prev_ytd
FROM #temp_all_months GROUP BY month_roll, customer_key, product_key, service_key,service_dim_key, service_name
) x;
WITH startdate_cte AS (
SELECT DISTINCT t.month_roll, t.customer_key, t.product_key, t.service_key,t.service_dim_key, t.service_name, dateadd(month, -11, t.month_roll) as fall_month_roll
FROM #temp_all_months t INNER JOIN int_cust.cust_plan_srv_activity_dates d
ON isnull(t.customer_key, '') = isnull(d.customer_key, '') AND isnull(t.product_key, '')= isnull(d.product_key, '') and isnull(t.service_key, '') = isnull(d.service_key, '') and isnull(t.service_name, '')= isnull(d.service_name, '') and isnull(t.service_dim_key, '')= isnull(d.service_dim_key, '')
WHERE d.service_startdt BETWEEN DATEADD(MONTH, -11, t.month_roll) AND t.month_roll and data_source = 'Sage'
)
select * Into #service_cross_dates from startdate_cte ;
/* Calculate Service Cross Sell for YTD */
DROP TABLE IF EXISTS #service_cross_dates_ytd;
WITH startdate_cte_ytd AS (
SELECT DISTINCT t.month_roll, t.customer_key, t.product_key, t.service_key,t.service_dim_key, t.service_name, DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AS fall_month_roll
FROM #temp_all_months t INNER JOIN int_cust.cust_plan_srv_activity_dates d
ON ISNULL(t.customer_key, '') = ISNULL(d.customer_key, '') AND ISNULL(t.product_key, '') = ISNULL(d.product_key, '') AND ISNULL(t.service_key, '') = ISNULL(d.service_key, '') AND ISNULL(t.service_name, '') = ISNULL(d.service_name, '') AND ISNULL(t.service_dim_key, '') = ISNULL(d.service_dim_key, '')
WHERE d.service_startdt BETWEEN DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AND t.month_roll AND data_source = 'Sage'
)
SELECT * INTO #service_cross_dates_ytd FROM startdate_cte_ytd;
UPDATE c SET service_cross_sell_flag = 'Yes' FROM #cte_service_cross_sell c WHERE EXISTS (SELECT 1 FROM #service_cross_dates s WHERE isnull(s.customer_key, '') = isnull(c.customer_key, '') AND isnull(s.product_key, '') = isnull(c.product_key, '') and isnull(s.service_key, '') = isnull(c.service_key, '') and isnull(s.service_dim_key, '') = isnull(c.service_dim_key, '') and isnull(s.service_name, '') = isnull(c.service_name, '') AND s.month_roll = c.month_roll) ;
UPDATE c SET service_cross_sell_flag = 'No' FROM #cte_service_cross_sell c WHERE NOT EXISTS (SELECT 1 FROM #service_cross_dates s WHERE isnull(s.customer_key, '') = isnull(c.customer_key, '') AND isnull(s.product_key, '') = isnull(c.product_key, '') and isnull(s.service_key, '') = isnull(c.service_key, '') and isnull(s.service_name, '') = isnull(c.service_name, '') and isnull(s.service_dim_key, '') = isnull(c.service_dim_key, '') AND s.month_roll = c.month_roll) ;
/* Update Service Cross Sell YTD flag */
UPDATE c SET service_cross_sell_flag_ytd = 'Yes' FROM #cte_service_cross_sell c WHERE EXISTS (SELECT 1 FROM #service_cross_dates_ytd s WHERE ISNULL(s.customer_key, '') = ISNULL(c.customer_key, '') AND ISNULL(s.product_key, '') = ISNULL(c.product_key, '') AND ISNULL(s.service_key, '') = ISNULL(c.service_key, '') AND ISNULL(s.service_name, '') = ISNULL(c.service_name, '') AND ISNULL(s.service_dim_key, '') = ISNULL(c.service_dim_key, '') AND s.month_roll = c.month_roll);
UPDATE c SET service_cross_sell_flag_ytd = 'No' FROM #cte_service_cross_sell c WHERE NOT EXISTS
(
SELECT 1 FROM #service_cross_dates_ytd s WHERE ISNULL(s.customer_key, '') = ISNULL(c.customer_key, '') AND ISNULL(s.product_key, '') = ISNULL(c.product_key, '') AND ISNULL(s.service_key, '') = ISNULL(c.service_key, '') AND ISNULL(s.service_name, '') = ISNULL(c.service_name, '') AND s.month_roll = c.month_roll AND ISNULL(s.service_dim_key, '') = ISNULL(c.service_dim_key, '')
);
update t set service_cross_sell = case when service_cross_sell_flag = 'Yes' then cast(t.eop_arr as float) else 0 end
from #temp_all_months t inner join #cte_service_cross_sell c on t.month_roll = c.month_roll and isnull(t.customer_key, '') = isnull(c.customer_key, '') and isnull(t.product_key, '') = isnull(c.product_key, '') and isnull(t.service_key, '') = isnull(c.service_key, '') and isnull(t.service_name, '') = isnull(c.service_name, '') and isnull(t.service_dim_key, '') = isnull(c.service_dim_key, '')
where t.new_customer = 0 and t.cross_sell = 0 and t.customer_churn = 0 and t.planchurn = 0;
/* Update Service Cross Sell YTD values */
UPDATE t SET service_cross_sell_ytd = CASE WHEN service_cross_sell_flag_ytd = 'Yes' THEN CAST(t.eop_ytd AS FLOAT) ELSE 0 END
FROM #temp_all_months t INNER JOIN #cte_service_cross_sell c ON t.month_roll = c.month_roll AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '') AND ISNULL(t.product_key, '') = ISNULL(c.product_key, '') AND ISNULL(t.service_key, '') = ISNULL(c.service_key, '') AND ISNULL(t.service_name, '') = ISNULL(c.service_name, '') AND ISNULL(t.service_dim_key, '') = ISNULL(c.service_dim_key, '')
WHERE t.new_customer_ytd = 0 AND t.cross_sell_ytd = 0 AND t.customer_churn_ytd = 0 AND t.planchurn_ytd = 0;
---//*******-----------------------------------------------
--Service Churn
---*********//------------------------------------------------
UPDATE a SET servicechurn = 0 FROM #temp_all_months a;
/* Reset service churn */
UPDATE a SET servicechurn_ytd = 0 FROM #temp_all_months a;
/* Added service churn YTD and Previous Year YTD fields */
DROP TABLE IF EXISTS #cte_servicechurn;
SELECT month_roll, customer_key, product_key, service_key,service_dim_key, service_name, service_ltm, service_prev_ltm, service_ytd, service_prev_ytd,
CASE WHEN ISNULL(service_ltm, 0) = 0 AND ISNULL(service_prev_ltm, 0) <> 0 THEN 'Yes' ELSE 'No' END AS servicechurn_flag,
CASE WHEN ISNULL(service_ytd, 0) = 0 AND ISNULL(service_prev_ytd, 0) <> 0 THEN 'Yes' ELSE 'No' END AS servicechurn_flag_ytd
INTO #cte_servicechurn
FROM (
SELECT month_roll, customer_key, product_key, service_key,service_dim_key, service_name,
CAST(SUM(CASE WHEN customer_churn = 0 AND new_customer = 0 AND planchurn = 0 AND cross_sell = 0 AND service_cross_sell = 0 THEN eop_arr ELSE 0 END) AS FLOAT) AS service_ltm,
CAST(SUM(CASE WHEN customer_churn = 0 AND new_customer = 0 AND planchurn = 0 AND cross_sell = 0 AND service_cross_sell = 0 THEN bop_arr ELSE 0 END) AS FLOAT) AS service_prev_ltm,
CAST(SUM(CASE WHEN customer_churn_ytd = 0 AND new_customer_ytd = 0 AND planchurn_ytd = 0 AND cross_sell_ytd = 0 AND service_cross_sell_ytd = 0 THEN eop_ytd ELSE 0 END) AS FLOAT) AS service_ytd,
CAST(SUM(CASE WHEN customer_churn_ytd = 0 AND new_customer_ytd = 0 AND planchurn_ytd = 0 AND cross_sell_ytd = 0 AND service_cross_sell_ytd = 0 THEN bop_ytd ELSE 0 END) AS FLOAT) AS service_prev_ytd
FROM #temp_all_months GROUP BY month_roll, customer_key, product_key, service_key,service_dim_key, service_name
) x;
DROP TABLE IF EXISTS #servicechurn_startdt;
WITH startdate_cte AS (
select x.month_roll, x.customer_key, x.product_key, x.service_key,x.service_dim_key, x.service_name, x.fall_month_roll, x.service_enddt, x.range_flag, x.end_flag,
case when x.range_flag = 'No' and x.end_flag = 'No' then 'Yes' else 'No' end as service_churn_flag
from (
SELECT DISTINCT t.month_roll, t.customer_key, t.product_key, t.service_key,t.service_dim_key, t.service_name,
DATEADD(MONTH, -11, t.month_roll) AS fall_month_roll,
d.service_enddt,
case when d.service_enddt BETWEEN DATEADD(MONTH, -11, t.month_roll) AND t.month_roll then 'Yes' else 'No' end as range_flag,
case when d.service_enddt > t.month_roll then 'Yes' else 'No' end as end_flag
FROM #temp_all_months t INNER JOIN int_cust.cust_plan_srv_activity_dates d
ON isnull(t.customer_key, '') = isnull(d.customer_key, '') and isnull(t.product_key, '') = isnull(d.product_key, '') and isnull(t.service_key, '') = isnull(d.service_key, '') and isnull(t.service_name, '') = isnull(d.service_name, '') and isnull(t.service_dim_key, '') = isnull(d.service_dim_key, '')
WHERE data_source = 'Sage'
) as x
)
SELECT * INTO #servicechurn_startdt FROM startdate_cte;
/* Calculate Service Churn for YTD */
DROP TABLE IF EXISTS #servicechurn_startdt_ytd;
WITH startdate_cte_ytd AS (
SELECT x.month_roll, x.customer_key, x.product_key, x.service_key,x.service_dim_key, x.service_name, x.fall_month_roll, x.service_enddt, x.range_flag, x.end_flag,
CASE WHEN x.range_flag = 'No' AND x.end_flag = 'No' THEN 'Yes' ELSE 'No' END AS service_churn_flag
FROM (
SELECT DISTINCT t.month_roll, t.customer_key, t.product_key, t.service_key,t.service_dim_key, t.service_name,
DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AS fall_month_roll,
d.service_enddt,
CASE WHEN d.service_enddt BETWEEN DATEFROMPARTS(YEAR(t.month_roll), 1, 1) AND t.month_roll THEN 'Yes' ELSE 'No' END AS range_flag,
CASE WHEN d.service_enddt > t.month_roll THEN 'Yes' ELSE 'No' END AS end_flag
FROM #temp_all_months t INNER JOIN int_cust.cust_plan_srv_activity_dates d
ON ISNULL(t.customer_key, '') = ISNULL(d.customer_key, '') AND ISNULL(t.product_key, '') = ISNULL(d.product_key, '') AND ISNULL(t.service_key, '') = ISNULL(d.service_key, '') AND ISNULL(t.service_name, '') = ISNULL(d.service_name, '') AND ISNULL(t.service_dim_key, '') = ISNULL(d.service_dim_key, '')
WHERE data_source = 'Sage'
) x
)
SELECT * INTO #servicechurn_startdt_ytd FROM startdate_cte_ytd;
UPDATE c SET c.servicechurn_flag = s.service_churn_flag FROM #cte_servicechurn c inner join #servicechurn_startdt s on c.month_roll = s.month_roll and isnull(c.customer_key, '') = isnull(s.customer_key, '') and isnull(c.product_key, '') = isnull(s.product_key, '') and isnull(c.service_key, '') = isnull(s.service_key, '') and isnull(c.service_name, '') = isnull(s.service_name, '') and isnull(c.service_dim_key, '') = isnull(s.service_dim_key, '')
/* Update Service Churn YTD flag */
UPDATE c SET c.servicechurn_flag_ytd = s.service_churn_flag FROM #cte_servicechurn c INNER JOIN #servicechurn_startdt_ytd s ON c.month_roll = s.month_roll AND ISNULL(c.customer_key, '') = ISNULL(s.customer_key, '') AND ISNULL(c.product_key, '') = ISNULL(s.product_key, '') AND ISNULL(c.service_key, '') = ISNULL(s.service_key, '') AND ISNULL(c.service_name, '') = ISNULL(s.service_name, '') AND ISNULL(c.service_dim_key, '') = ISNULL(s.service_dim_key, '');
UPDATE t SET servicechurn = CASE WHEN c.servicechurn_flag = 'Yes' THEN CAST(-t.bop_arr AS FLOAT) ELSE 0 END
FROM #temp_all_months t INNER JOIN #cte_servicechurn c ON t.month_roll = c.month_roll AND isnull(t.customer_key, '') = isnull(c.customer_key, '') AND isnull(t.product_key, '') = isnull(c.product_key, '') AND isnull(t.service_key, '') = isnull(c.service_key, '') AND isnull(t.service_name, '') = isnull(c.service_name, '') AND isnull(t.service_dim_key, '') = isnull(c.service_dim_key, '')
where t.new_customer = 0 and t.cross_sell = 0 and t.customer_churn = 0 and t.planchurn = 0 and t.service_cross_sell = 0;
/* Update Service Churn YTD Values */
UPDATE t SET servicechurn_ytd = CASE WHEN c.servicechurn_flag_ytd = 'Yes' THEN CAST(-t.bop_ytd AS FLOAT) ELSE 0 END
FROM #temp_all_months t INNER JOIN #cte_servicechurn c ON t.month_roll = c.month_roll AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '') AND ISNULL(t.product_key, '') = ISNULL(c.product_key, '') AND ISNULL(t.service_key, '') = ISNULL(c.service_key, '') AND ISNULL(t.service_name, '') = ISNULL(c.service_name, '') AND ISNULL(t.service_dim_key, '') = ISNULL(c.service_dim_key, '')
WHERE t.new_customer_ytd = 0 AND t.cross_sell_ytd = 0 AND t.customer_churn_ytd = 0 AND t.planchurn_ytd = 0 AND t.service_cross_sell_ytd = 0;
----// ************************
-----down sell logic --************* considering the revenue type
----***************************//
/* Added downsell YTD and Previous Year YTD fields */
drop table if exists #cte_downsell;
SELECT month_roll, customer_key, product_key, service_key,service_dim_key, service_name, revenue_type, service_ltm, service_prev_ltm, service_ytd, service_prev_ytd,
CASE WHEN isnull(service_ltm, 0) < isnull(service_prev_ltm, 0) THEN 'Yes' ELSE 'No' END AS downsell_flag,
CASE WHEN ISNULL(service_ytd, 0) < ISNULL(service_prev_ytd, 0) THEN 'Yes' ELSE 'No' END AS downsell_flag_ytd
INTO #cte_downsell
FROM (
SELECT t.month_roll, t.customer_key, t.product_key, t.service_key,t.service_dim_key, t.service_name, t.revenue_type,
CAST(SUM(CASE WHEN servicechurn = 0 AND customer_churn = 0 AND planchurn = 0 AND new_customer = 0 AND cross_sell = 0 AND service_cross_sell = 0 THEN eop_arr ELSE 0 END) AS FLOAT) AS service_ltm,
CAST(SUM(CASE WHEN servicechurn = 0 AND customer_churn = 0 AND planchurn = 0 AND new_customer = 0 AND cross_sell = 0 AND service_cross_sell = 0 THEN bop_arr ELSE 0 END) AS FLOAT) AS service_prev_ltm,
CAST(SUM(CASE WHEN servicechurn_ytd = 0 AND customer_churn_ytd = 0 AND planchurn_ytd = 0 AND new_customer_ytd = 0 AND cross_sell_ytd = 0 AND service_cross_sell_ytd = 0 THEN eop_ytd ELSE 0 END) AS FLOAT) AS service_ytd,
CAST(SUM(CASE WHEN servicechurn_ytd = 0 AND customer_churn_ytd = 0 AND planchurn_ytd = 0 AND new_customer_ytd = 0 AND cross_sell_ytd = 0 AND service_cross_sell_ytd = 0 THEN bop_ytd ELSE 0 END) AS FLOAT) AS service_prev_ytd
FROM #temp_all_months t GROUP BY t.month_roll, t.customer_key, t.product_key, t.service_key,t.service_dim_key, t.service_name, t.revenue_type
) x;
update t set downsell = case when downsell_flag = 'Yes' then cast(t.eop_arr as float)-cast(t.bop_arr as float) else 0 end
from #temp_all_months t inner join #cte_downsell c on t.month_roll = c.month_roll and isnull(t.customer_key, '') = isnull(c.customer_key, '') and isnull(t.product_key, '') = isnull(c.product_key, '') and isnull(t.service_key, '') = isnull(c.service_key, '') and isnull(t.service_name, '') = isnull(c.service_name, '') and isnull(t.revenue_type, '')= isnull(c.revenue_type, '') and isnull(t.service_dim_key, '')= isnull(c.service_dim_key, '')
where t.new_customer = 0 and t.cross_sell = 0 and t.customer_churn = 0 and t.planchurn = 0 and t.service_cross_sell = 0 and t.servicechurn = 0;
/* Update downsell YTD flag */
UPDATE t SET downsell_ytd = CASE WHEN downsell_flag_ytd = 'Yes' THEN CAST(t.eop_ytd AS FLOAT) - CAST(t.bop_ytd AS FLOAT) ELSE 0 END
FROM #temp_all_months t INNER JOIN #cte_downsell c ON t.month_roll = c.month_roll AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '') AND ISNULL(t.product_key, '') = ISNULL(c.product_key, '') AND ISNULL(t.service_key, '') = ISNULL(c.service_key, '') AND ISNULL(t.service_name, '') = ISNULL(c.service_name, '') AND ISNULL(t.revenue_type, '') = ISNULL(c.revenue_type, '') AND ISNULL(t.service_dim_key, '') = ISNULL(c.service_dim_key, '')
WHERE t.new_customer_ytd = 0 AND t.cross_sell_ytd = 0 AND t.customer_churn_ytd = 0 AND t.planchurn_ytd = 0 AND t.service_cross_sell_ytd = 0 AND t.servicechurn_ytd = 0;
----// ************************
-----up sell logic --************* considering the revenue type
----***************************//
/* Added upsell YTD and Previous Year YTD fields */
drop table if exists #cte_upsell;
SELECT month_roll, customer_key, product_key, service_key,service_dim_key, service_name, revenue_type, service_ltm, service_prev_ltm, service_ytd, service_prev_ytd,
CASE WHEN isnull(service_ltm, 0) > isnull(service_prev_ltm, 0) THEN 'Yes' ELSE 'No' END AS upsell_flag,
CASE WHEN ISNULL(service_ytd, 0) > ISNULL(service_prev_ytd, 0) THEN 'Yes' ELSE 'No' END AS upsell_flag_ytd
INTO #cte_upsell
FROM (
SELECT t.month_roll, t.customer_key, t.product_key, t.service_key,t.service_dim_key, t.service_name, t.revenue_type,
CAST(SUM(CASE WHEN servicechurn = 0 AND customer_churn = 0 AND planchurn = 0 AND new_customer = 0 AND cross_sell = 0 AND service_cross_sell = 0 AND downsell = 0 THEN eop_arr ELSE 0 END) AS FLOAT) AS service_ltm,
CAST(SUM(CASE WHEN servicechurn = 0 AND customer_churn = 0 AND planchurn = 0 AND new_customer = 0 AND cross_sell = 0 AND service_cross_sell = 0 AND downsell = 0 THEN bop_arr ELSE 0 END) AS FLOAT) AS service_prev_ltm,
CAST(SUM(CASE WHEN servicechurn_ytd = 0 AND customer_churn_ytd = 0 AND planchurn_ytd = 0 AND new_customer_ytd = 0 AND cross_sell_ytd = 0 AND service_cross_sell_ytd = 0 AND downsell_ytd = 0 THEN eop_ytd ELSE 0 END) AS FLOAT) AS service_ytd,
CAST(SUM(CASE WHEN servicechurn_ytd = 0 AND customer_churn_ytd = 0 AND planchurn_ytd = 0 AND new_customer_ytd = 0 AND cross_sell_ytd = 0 AND service_cross_sell_ytd = 0 AND downsell_ytd = 0 THEN bop_ytd ELSE 0 END) AS FLOAT) AS service_prev_ytd
FROM #temp_all_months t GROUP BY t.month_roll, t.customer_key, t.product_key, t.service_key,t.service_dim_key, t.service_name, t.revenue_type
) x;
update t set upsell = case when upsell_flag = 'Yes' then cast(t.eop_arr as float)-cast(t.bop_arr as float) else 0 end
from #temp_all_months t inner join #cte_upsell c on t.month_roll = c.month_roll and isnull(t.customer_key, '') = isnull(c.customer_key, '') and isnull(t.product_key, '') = isnull(c.product_key, '') and isnull(t.service_key, '') = isnull(c.service_key, '') and isnull(t.service_name, '') = isnull(c.service_name, '') and isnull(t.revenue_type, '')= isnull(c.revenue_type, '') and isnull(t.service_dim_key, '')= isnull(c.service_dim_key, '')
where t.new_customer = 0 and t.cross_sell = 0 and t.customer_churn = 0 and t.planchurn = 0 and t.service_cross_sell = 0 and t.servicechurn = 0 and downsell = 0;
/* Update Upsell YTD flag */
UPDATE t SET upsell_ytd = CASE WHEN upsell_flag_ytd = 'Yes' THEN CAST(t.eop_ytd AS FLOAT) - CAST(t.bop_ytd AS FLOAT) ELSE 0 END
FROM #temp_all_months t INNER JOIN #cte_upsell c ON t.month_roll = c.month_roll AND ISNULL(t.customer_key, '') = ISNULL(c.customer_key, '') AND ISNULL(t.product_key, '') = ISNULL(c.product_key, '') AND ISNULL(t.service_key, '') = ISNULL(c.service_key, '') AND ISNULL(t.service_name, '') = ISNULL(c.service_name, '') AND ISNULL(t.revenue_type, '') = ISNULL(c.revenue_type, '') AND ISNULL(t.service_dim_key, '') = ISNULL(c.service_dim_key, '')
WHERE t.new_customer_ytd = 0 AND t.cross_sell_ytd = 0 AND t.customer_churn_ytd = 0 AND t.planchurn_ytd = 0 AND t.service_cross_sell_ytd = 0 AND t.servicechurn_ytd = 0 AND t.downsell_ytd = 0;
/* update all ytd buckets if values missing fill 0 */
UPDATE #temp_all_months SET mrr = ISNULL(mrr, 0), customer_churn = ISNULL(customer_churn, 0), customer_churn_ytd = ISNULL(customer_churn_ytd, 0), planchurn = ISNULL(planchurn, 0), planchurn_ytd = ISNULL(planchurn_ytd, 0), servicechurn = ISNULL(servicechurn, 0), servicechurn_ytd = ISNULL(servicechurn_ytd, 0), new_customer = ISNULL(new_customer, 0), new_customer_ytd = ISNULL(new_customer_ytd, 0), upsell = ISNULL(upsell, 0), upsell_ytd = ISNULL(upsell_ytd, 0), cross_sell = ISNULL(cross_sell, 0), cross_sell_ytd = ISNULL(cross_sell_ytd, 0), service_cross_sell = ISNULL(service_cross_sell, 0), service_cross_sell_ytd = ISNULL(service_cross_sell_ytd, 0), downsell = ISNULL(downsell, 0), downsell_ytd = ISNULL(downsell_ytd, 0);
DROP TABLE IF EXISTS int_cust.revenue_bridge_output_bucket_calculations;
SELECT *, 'Sage' data_source INTO int_cust.revenue_bridge_output_bucket_calculations FROM #temp_all_months;
update a set grr = bop_arr + customer_churn + planchurn + servicechurn + downsell from int_cust.revenue_bridge_output_bucket_calculations a;
update a set nrr = grr + upsell + service_cross_sell + cross_sell from int_cust.revenue_bridge_output_bucket_calculations a;
/* update grr ytd values */
UPDATE a SET grr_ytd =bop_ytd + customer_churn_ytd + planchurn_ytd + servicechurn_ytd + downsell_ytd FROM int_cust.revenue_bridge_output_bucket_calculations a;
/* update nrr ytd values */
UPDATE a SET nrr_ytd = grr_ytd + upsell_ytd + service_cross_sell_ytd + cross_sell_ytd FROM int_cust.revenue_bridge_output_bucket_calculations a;
end
END;
```

## 🔗 Related Notes
- [[Standardized ARR Snowball Procedure (T-SQL)|Standardized ARR Snowball Procedure (T-SQL)]] — the cleaned-up, genericized version derived from this original.
- [[Snowball|Snowball]] — hub note for this whole area.

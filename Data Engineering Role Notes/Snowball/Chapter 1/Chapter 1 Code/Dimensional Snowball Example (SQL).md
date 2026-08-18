This note demonstrates the **Dimensional Snowball** pattern: attaching a dimension (e.g. Region, Product Tier, Sales Rep) to a snowball *after* the period-over-period alignment is complete, rather than before.

Adding a mock `Dim_Customer` table with a `Region` column (North America and EMEA) shows exactly which regions drive New, Expansion, or Churn ARR.

### Why the join order matters

If you join `Dim_Customer` directly inside the snapshot CTE (before the `FULL OUTER JOIN` that aligns current-period and prior-period rows), the dimension gets tied to only one side of that join — `curr` or `prev`. `COALESCE`-ing it back together then becomes unreliable, and churned customers frequently end up with an "Unknown" region because their `curr`-side row doesn't exist.

The fix: complete the `FULL OUTER JOIN` using only the keys, and attach the dimension with a `LEFT JOIN` afterward. Every dollar of ARR — New, Expansion, or Churn — is then guaranteed to carry its region, regardless of which side of the period alignment it came from.

### A second, unrelated fix: `EOMONTH` around the month-add

The alignment join needs `curr.Snapshot_Date` to equal "one month after `prev.Snapshot_Date`." Writing that as plain `DATEADD(month, 1, prev.Snapshot_Date)` looks right and even works for the January → February pairing (`DATEADD` clamps Jan 31 + 1 month to Feb 28, matching the February snapshot). It silently breaks for February → March: `DATEADD(month, 1, '2026-02-28')` returns `2026-03-28`, not `2026-03-31` — the actual March month-end — so that pairing never matches. Every customer would appear to be a fresh New/Resurrected row in March, and a phantom churn row would appear dated `2026-03-28` for February. Wrapping the whole expression in `EOMONTH(...)` re-normalizes it back to the real month-end on both sides of the comparison, so the join matches regardless of which months have 28, 29, 30, or 31 days.

### The script

```sql
WITH
-- 1. MOCK RAW DATA (Fact & Dimensions)
Fact_Subscriptions AS (
    SELECT 'C-01' AS CustomerKey, CAST('2026-01-01' AS DATE) AS StartDate, CAST(NULL AS DATE) AS EndDate, 100 AS ARR_Amount UNION ALL
    SELECT 'C-02', '2026-01-01', '2026-02-15', 50 UNION ALL
    SELECT 'C-02', '2026-02-16', NULL, 80 UNION ALL
    SELECT 'C-03', '2026-02-01', '2026-03-15', 200 UNION ALL
    SELECT 'C-04', '2026-01-01', '2026-02-10', 150 UNION ALL
    SELECT 'C-04', '2026-03-05', NULL, 120
),

-- MOCK DIMENSION: Region per customer
Dim_Customer AS (
    SELECT 'C-01' AS CustomerKey, 'North America' AS Region UNION ALL
    SELECT 'C-02', 'EMEA' UNION ALL
    SELECT 'C-03', 'North America' UNION ALL
    SELECT 'C-04', 'EMEA'
),

-- 2. MOCK REPORTING DATES
EOM_Dates AS (
    SELECT CAST('2026-01-31' AS DATE) AS EOM_Date UNION ALL
    SELECT CAST('2026-02-28' AS DATE) UNION ALL
    SELECT CAST('2026-03-31' AS DATE)
),

-- 3. STEP 1: EOP SNAPSHOTS & FIRST ACTIVE MONTH
Customer_Snapshots AS (
    SELECT
        d.EOM_Date AS Snapshot_Date,
        s.CustomerKey,
        SUM(s.ARR_Amount) AS Active_ARR,
        MIN(d.EOM_Date) OVER (PARTITION BY s.CustomerKey) AS First_Active_Month
    FROM EOM_Dates d
    INNER JOIN Fact_Subscriptions s
        ON s.StartDate <= d.EOM_Date
        AND (s.EndDate > d.EOM_Date OR s.EndDate IS NULL)
    GROUP BY d.EOM_Date, s.CustomerKey
),

-- 4. STEP 2: PERIOD-OVER-PERIOD ALIGNMENT (the core engine)
Month_Over_Month AS (
    SELECT
        COALESCE(curr.Snapshot_Date, EOMONTH(DATEADD(month, 1, prev.Snapshot_Date))) AS Report_Month,
        COALESCE(curr.CustomerKey, prev.CustomerKey) AS CustomerKey,
        COALESCE(prev.Active_ARR, 0) AS BOP_ARR,
        COALESCE(curr.Active_ARR, 0) AS EOP_ARR,
        COALESCE(curr.First_Active_Month, prev.First_Active_Month) AS First_Active_Month
    FROM Customer_Snapshots curr
    FULL OUTER JOIN Customer_Snapshots prev
        ON curr.CustomerKey = prev.CustomerKey
        AND curr.Snapshot_Date = EOMONTH(DATEADD(month, 1, prev.Snapshot_Date))
),

-- 5. STEP 3: JOIN DIMENSIONS — only AFTER the FULL OUTER JOIN
Dimensionalized_Snowball AS (
    SELECT
        mom.*,
        c.Region -- attached here so it survives for both New and Churned customers
    FROM Month_Over_Month mom
    LEFT JOIN Dim_Customer c
        ON mom.CustomerKey = c.CustomerKey
)

-- 6. STEP 4: CATEGORIZE & GROUP BY THE DIMENSION
SELECT
    Report_Month,
    Region,
    SUM(BOP_ARR) AS Beginning_ARR,
    SUM(CASE WHEN BOP_ARR = 0 AND EOP_ARR > 0 AND Report_Month = First_Active_Month THEN EOP_ARR ELSE 0 END) AS New_ARR,
    SUM(CASE WHEN BOP_ARR = 0 AND EOP_ARR > 0 AND Report_Month > First_Active_Month THEN EOP_ARR ELSE 0 END) AS Resurrected_ARR,
    SUM(CASE WHEN BOP_ARR > 0 AND EOP_ARR > BOP_ARR THEN EOP_ARR - BOP_ARR ELSE 0 END) AS Expansion_ARR,
    SUM(CASE WHEN BOP_ARR > 0 AND EOP_ARR > 0 AND EOP_ARR < BOP_ARR THEN EOP_ARR - BOP_ARR ELSE 0 END) AS Contraction_ARR,
    SUM(CASE WHEN BOP_ARR > 0 AND EOP_ARR = 0 THEN -BOP_ARR ELSE 0 END) AS Churn_ARR,
    SUM(EOP_ARR) AS Ending_ARR
FROM Dimensionalized_Snowball
WHERE Report_Month > '2026-01-31'
GROUP BY
    Report_Month,
    Region
ORDER BY
    Report_Month,
    Region;
```

### How this relates to the full bucket cascade

This example uses a simplified 5-bucket customer-level model (New, Resurrected, Expansion, Contraction, Churn). The production procedure in [[Standardized ARR Snowball Procedure (T-SQL)|Standardized ARR Snowball Procedure]] extends the same core idea (align BOP/EOP, then categorize) across three nested grains — customer, product, and service — see [[Bucket Cascade Logic|Bucket Cascade Logic]] for how the 8-stage version narrows the population at each step. The "dimension after alignment" rule demonstrated here applies identically in that larger procedure.

## 🔗 Related Notes
- [[Steps in Building an ARR Snowball|Steps in Building an ARR Snowball]] — the 5-step process this script implements.
- [[Snowball|Snowball]] — hub note for this area.

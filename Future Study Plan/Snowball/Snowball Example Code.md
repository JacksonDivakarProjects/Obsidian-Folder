Let's build a self-contained SQL script that demonstrates the **Dimensional Snowball**.

We will add a mock `Dim_Customer` table with a `Region` column (North America and EMEA). We will then join this dimension to our snowball so we can see exactly which regions are driving New, Expansion, or Churn ARR.

### The Dimensional Snowball Script

Copy and run this self-contained script. Pay close attention to how we wait until the `Dimensionalized_Snowball` CTE to bring the `Region` data in.

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

-- MOCK DIMENSION: Adding Region data to our customers
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

-- 4. STEP 2: PERIOD-OVER-PERIOD ALIGNMENT (The Core Engine)
Month_Over_Month AS (
    SELECT 
        COALESCE(curr.Snapshot_Date, DATEADD(month, 1, prev.Snapshot_Date)) AS Report_Month,
        COALESCE(curr.CustomerKey, prev.CustomerKey) AS CustomerKey,
        COALESCE(prev.Active_ARR, 0) AS BOP_ARR,
        COALESCE(curr.Active_ARR, 0) AS EOP_ARR,
        COALESCE(curr.First_Active_Month, prev.First_Active_Month) AS First_Active_Month
    FROM Customer_Snapshots curr
    FULL OUTER JOIN Customer_Snapshots prev
        ON curr.CustomerKey = prev.CustomerKey
        AND curr.Snapshot_Date = DATEADD(month, 1, prev.Snapshot_Date)
),

-- 5. STEP 3: JOIN DIMENSIONS
-- We wait until AFTER the Full Outer Join to attach dimension attributes!
Dimensionalized_Snowball AS (
    SELECT 
        mom.*,
        c.Region -- Pulling in the region here ensures it exists for both New and Churned customers
    FROM Month_Over_Month mom
    LEFT JOIN Dim_Customer c 
        ON mom.CustomerKey = c.CustomerKey
)

-- 6. STEP 4: CATEGORIZE & GROUP BY THE DIMENSION
SELECT 
    Report_Month,
    Region, -- Now we group by our new dimension
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
    Region -- Grouping by Region creates the split
ORDER BY 
    Report_Month, 
    Region;

```

### Why this structure is so important:

If you tried to join the `Dim_Customer` table directly inside the `Customer_Snapshots` CTE, you would run into major issues during the `FULL OUTER JOIN`. The dimension would get tied to either the `curr` side or the `prev` side, making it incredibly difficult to `COALESCE` properly, resulting in "Unknown" regions when customers churned.

By completing the `FULL OUTER JOIN` cleanly using only the keys, and then applying a `LEFT JOIN` to the dimension table afterward, you guarantee that every dollar of ARR is correctly assigned to its region, regardless of whether it was New, Expansion, or Churn.
Yes. The queries against an **Accumulating Snapshot Fact Table (ASFT)** are mainly about **process progress, duration, bottlenecks, and completion**.

Using our `Fact_Order_Fulfillment` example:

```text
Order_Line_Key
Customer_Key
Product_Key

Created_Date_Key
Confirmed_Date_Key
Packed_Date_Key
Shipped_Date_Key
Delivered_Date_Key

Confirmation_Days
Packing_Days
Shipping_Days
Delivery_Days
Total_Fulfillment_Days
```

## The Pareto query types

### 1. "Where is the process currently?"

This is probably the **most natural ASFT query**.

> How many orders are currently at each stage?

```sql
SELECT
    CASE
        WHEN Delivered_Date_Key IS NOT NULL THEN 'Delivered'
        WHEN Shipped_Date_Key IS NOT NULL THEN 'Shipped'
        WHEN Packed_Date_Key IS NOT NULL THEN 'Packed'
        WHEN Confirmed_Date_Key IS NOT NULL THEN 'Confirmed'
        ELSE 'Created'
    END AS current_stage,
    COUNT(*) AS order_lines
FROM fact_order_fulfillment
GROUP BY 1;
```

This gives:

```text
Created       120
Confirmed      80
Packed         60
Shipped        40
Delivered     500
```

---

### 2. "How long does the entire process take?"

> What is the average fulfillment time?

```sql
SELECT
    AVG(Total_Fulfillment_Days) AS avg_fulfillment_days
FROM fact_order_fulfillment
WHERE Delivered_Date_Key IS NOT NULL;
```

You could also calculate:

- Average
    
- Median
    
- Minimum
    
- Maximum
    
- Percentiles
    

---

### 3. "Which stage is the bottleneck?"

This is a **very important ASFT analysis**.

```sql
SELECT
    AVG(Confirmation_Days),
    AVG(Packing_Days),
    AVG(Shipping_Days),
    AVG(Delivery_Days)
FROM fact_order_fulfillment;
```

Suppose:

```text
Confirmation = 1.2 days
Packing      = 0.8 days
Shipping     = 4.5 days  ← bottleneck
Delivery     = 1.5 days
```

You immediately know shipping is taking the longest.

---

### 4. "How many processes have completed a milestone?"

For example:

> How many orders have been shipped but not delivered?

```sql
SELECT COUNT(*)
FROM fact_order_fulfillment
WHERE Shipped_Date_Key IS NOT NULL
  AND Delivered_Date_Key IS NULL;
```

This is very common for **pipeline monitoring**.

---

### 5. "How many processes are stuck?"

For example:

> Orders confirmed more than 3 days ago but still not packed.

```sql
SELECT COUNT(*)
FROM fact_order_fulfillment
WHERE Confirmed_Date_Key IS NOT NULL
  AND Packed_Date_Key IS NULL
  AND Confirmation_Days > 3;
```

This helps identify **stuck workflows**.

---

### 6. "Compare performance across dimensions"

Because ASFT has normal dimensional foreign keys, you can slice the process by:

- Product
    
- Customer
    
- Region
    
- Store
    
- Employee
    
- Channel
    

For example:

> Which region has the longest fulfillment time?

```sql
SELECT
    r.region,
    AVG(f.Total_Fulfillment_Days) AS avg_days
FROM fact_order_fulfillment f
JOIN dim_store s
    ON f.Store_Key = s.Store_Key
JOIN dim_region r
    ON s.Region_Key = r.Region_Key
GROUP BY r.region
ORDER BY avg_days DESC;
```

So ASFT isn't limited to process-level queries.

---

# 7. "How is the process improving over time?"

Because you have milestone dates, you can analyze historical performance.

For example:

> Is average fulfillment time decreasing month by month?

```sql
SELECT
    d.year,
    d.month,
    AVG(f.Total_Fulfillment_Days) AS avg_fulfillment_days
FROM fact_order_fulfillment f
JOIN dim_date d
    ON f.Created_Date_Key = d.Date_Key
WHERE f.Delivered_Date_Key IS NOT NULL
GROUP BY d.year, d.month
ORDER BY d.year, d.month;
```

You might get:

```text
Jan   7.2 days
Feb   6.8 days
Mar   6.1 days
Apr   5.4 days
```

---

# 8. "What's the completion rate?"

For example:

> What percentage of orders have been delivered?

Conceptually:

```sql
SELECT
    COUNT(CASE WHEN Delivered_Date_Key IS NOT NULL THEN 1 END) * 100.0
    / COUNT(*) AS completion_rate
FROM fact_order_fulfillment;
```

---

# 9. "How many days has an unfinished process been running?"

This is another useful ASFT query.

Suppose:

```text
Created = Aug 1
Today = Aug 10
Delivered = NULL
```

Then:

```text
Current Age = Today - Created Date
            = 9 days
```

You can identify old/stuck processes.

---

# The Pareto mental model

Almost every ASFT query falls into these **5 buckets**:

|Question|What you query|
|---|---|
|**Where is it?**|Milestone dates / current stage|
|**How long?**|Lag/duration measures|
|**How many?**|COUNT by milestone/status|
|**Where is the problem?**|Lag + stage analysis|
|**Who/what is performing better?**|Dimensions + lag measures|

So when you see an ASFT, immediately think:

> **"This table is for analyzing the lifecycle of a process."**

Not primarily:

> "How many sales happened?"

That's more naturally a **transaction fact** question.

And not primarily:

> "What was the inventory balance every month?"

That's more naturally a **periodic snapshot** question.

**ASFT = "Where is the process, how long is it taking, and where is it getting stuck?"**
Yes. This section is introducing **Consolidated Fact Tables**. The key idea is:

> **You can combine data from different business processes into one fact table when both processes have exactly the same grain.**

Let's break it down.

---

# 1. First: What does "multiple processes" mean?

Suppose the business has two processes:

### Process 1 — Sales

Actual sales:

> What did we actually sell?

### Process 2 — Sales Forecast

Forecast:

> What did we expect to sell?

These are **different business processes**.

Normally you might create:

```text
fact_sales_actual
fact_sales_forecast
```

---

# 2. The problem with separate fact tables

Suppose actual sales:

|Month|Product|Store|ActualSales|
|---|---|---|--:|
|Aug|P1|S1|100|
|Aug|P2|S1|200|

Forecast:

|Month|Product|Store|ForecastSales|
|---|---|---|--:|
|Aug|P1|S1|120|
|Aug|P2|S1|180|

The business wants:

> **Actual vs Forecast**

You have to combine the two fact tables.

This is called a **drill-across**.

Conceptually:

```text
fact_actual
     │
     │
     ├────── JOIN / DRILL ACROSS
     │
     ▼
fact_forecast
     │
     ▼
Actual vs Forecast
```

It can be more complicated for BI tools.

---

# 3. Consolidated fact table

Instead, you can combine them into one fact table:

```text
fact_sales_performance
```

|Month|Product|Store|ActualSales|ForecastSales|
|---|---|---|--:|--:|
|Aug|P1|S1|100|120|
|Aug|P2|S1|200|180|

Now the BI query is much simpler.

```text
ActualSales
ForecastSales
Variance
```

You can calculate:

```text
Variance = ActualSales - ForecastSales
```

For P1:

```text
100 - 120 = -20
```

For P2:

```text
200 - 180 = +20
```

---

# 4. But there is one HUGE requirement

This is the most important sentence in the paragraph:

> **"if they can be expressed at the same grain."**

Both processes must have the **same grain**.

For example:

### Actual Sales

> One row = one product + store + month.

### Forecast

> One row = one product + store + month.

✅ Same grain.

Therefore they can potentially be consolidated.

---

# 5. What if the grains are different?

Suppose:

### Actual sales

> One row = one product + store + month.

But forecast:

> One row = one product category + store + month.

These are different:

```text
Actual:
Product + Store + Month

Forecast:
Category + Store + Month
```

❌ Don't simply combine them into one fact table.

Why?

Because one row would no longer have a clear meaning.

Remember your fundamental rule:

> **Every fact table must have one consistent grain.**

---

# 6. What does the consolidated table actually represent?

You need to define its grain.

For example:

> **One row = one product + one store + one month.**

Then both actual and forecast measurements must fit that grain.

```text
                   Grain
                     │
          Product + Store + Month
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
      Actual Sales          Forecast Sales
```

Both measurements describe that same combination.

---

# 7. Why does this make analysis easier?

Suppose you want:

> Actual vs Forecast by product.

With consolidated fact:

```sql
SELECT
    ProductKey,
    SUM(ActualSales),
    SUM(ForecastSales),
    SUM(ActualSales) - SUM(ForecastSales) AS Variance
FROM fact_sales_performance
GROUP BY ProductKey;
```

Everything is in one fact table.

---

# 8. What does "drill-across" mean?

Drill-across means:

> **Comparing/combining measures from separate fact tables that share common dimensions.**

For example:

```text
fact_sales_actual
       │
       │
       ├── Date
       ├── Product
       └── Store
              │
              │
       fact_sales_forecast
```

You use the common dimensions to align the results.

It is perfectly valid dimensional modeling.

But it can be more complicated for BI applications.

---

# 9. Why does the consolidated fact increase ETL burden?

Because ETL now has to bring two processes together.

You need to:

```text
Actual Source
      │
      ▼
     ETL ──────┐
               │
               ▼
       Consolidated Fact
               ▲
               │
     ETL ──────┘
      │
      ▼
Forecast Source
```

ETL has to make sure:

- dimensions are aligned
    
- grains match
    
- keys are resolved
    
- actuals and forecasts line up
    
- missing values are handled
    
- data arrives correctly
    

So:

> **More ETL complexity.**

---

# 10. But BI becomes easier

Without consolidation:

```text
BI
 │
 ├── Query Actual Fact
 │
 ├── Query Forecast Fact
 │
 ├── Align results
 │
 └── Calculate variance
```

With consolidation:

```text
BI
 │
 ▼
Consolidated Fact
 │
 ├── Actual
 ├── Forecast
 └── Variance
```

So:

> **ETL burden increases, but analytical/BI burden decreases.**

That's exactly what Kimball means by:

> "Consolidated fact tables add burden to the ETL processing, but ease the analytic burden on the BI applications."

---

# 11. When should you use one?

The book gives an important recommendation:

> **Use consolidated fact tables for cross-process metrics that are frequently analyzed together.**

So don't consolidate everything just because you can.

### Good candidate

```text
Actual Sales
     +
Sales Forecast
```

Frequently analyzed:

> Actual vs Forecast

✅ Good candidate.

Another example:

```text
Budget
+
Actual
```

Frequently analyzed:

> Budget vs Actual

✅ Good candidate.

---

# 12. When NOT to consolidate

Suppose you have:

```text
Sales
Inventory
Employee Payroll
Customer Service Calls
```

They are all numeric business processes, but their grains are completely different.

Trying to combine them into one giant fact table would be a mistake.

```text
Sales
  ≠
Inventory
  ≠
Payroll
  ≠
Customer Service
```

Different grain → separate fact tables.

---

# 13. Consolidated fact vs Aggregate fact

Don't confuse these two.

### Aggregate fact

Takes **one fact table** and summarizes it.

```text
Atomic Sales
     ↓
SUM / GROUP BY
     ↓
Aggregate Sales
```

Purpose:

> **Performance**

---

### Consolidated fact

Combines **multiple business processes** at the same grain.

```text
Actual Sales ─────┐
                  ├──→ Consolidated Fact
Forecast Sales ───┘
```

Purpose:

> **Make frequently combined cross-process analysis easier.**

---

# 14. Very important: same grain ≠ same process

This is subtle.

Two processes can be different but still have the same grain.

Example:

```text
Process 1:
Sales Actual

Process 2:
Sales Forecast
```

Different processes.

But:

```text
Both:
Product + Store + Month
```

Same grain.

Therefore consolidation is possible.

---

# ⭐ Revision Note

### Consolidated Fact Table

> A fact table that combines measurements from multiple business processes that can be represented at the **same grain**, usually because those measurements are frequently analyzed together.

### Example

```text
Sales Actual
+
Sales Forecast
        ↓
Consolidated Fact
```

Grain:

> **One product + one store + one month.**

Measures:

```text
ActualSales
ForecastSales
```

Then:

```text
Variance = ActualSales - ForecastSales
```

### Benefits

**BI becomes easier and faster:**

```text
One fact table
      ↓
Actual vs Forecast
```

### Cost

**ETL becomes more complicated:**

```text
Multiple processes
      ↓
Align grains
      ↓
Conform dimensions
      ↓
Combine data
```

### Golden rule

> **Different processes can share a fact table only when their measurements can be expressed at the same grain.**

And remember the distinction:

> **Aggregate fact = summarize one process for performance.**

> **Consolidated fact = combine multiple processes at the same grain for easier cross-process analysis.**
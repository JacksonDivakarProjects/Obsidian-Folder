# Slice vs Dice — Dimensional Modeling Guide

## 1. Basic Idea

Both **slicing** and **dicing** are ways of filtering data in a dimensional model.

```text
Dimension → filters the data
Fact      → contains the measurements
```

For example:

```text
dim_product
     ↓
category = Electronics
     ↓
fact_sales
     ↓
sales_amount
```

---

# 2. Slicing

### Definition

**Slicing means selecting a subset of the data based on one dimension or one specific dimension value.**

Think:

> **Slice = one specific cut of the data.**

### Example

Suppose we have:

**`dim_date`**

|date_key|year|month|
|--:|--:|---|
|1|2025|Jan|
|2|2026|Jan|
|3|2026|Feb|

**`fact_sales`**

|date_key|product_key|sales_amount|
|--:|--:|--:|
|1|101|10,000|
|2|101|15,000|
|3|101|20,000|

Suppose we want:

> Sales for **2026**

We filter one dimension:

```text
dim_date
   ↓
year = 2026
   ↓
fact_sales
```

Result:

|Date|Sales|
|---|--:|
|Jan 2026|15,000|
|Feb 2026|20,000|

This is **slicing**.

### SQL

```sql
SELECT
    SUM(f.sales_amount) AS total_sales
FROM fact_sales f
JOIN dim_date d
    ON f.date_key = d.date_key
WHERE d.year = 2026;
```

---

# 3. Dicing

### Definition

**Dicing means selecting a smaller subset using multiple dimensions or multiple conditions.**

Think:

> **Dice = multiple cuts producing a smaller multidimensional subset.**

Suppose we want:

> Electronics sales in Chennai during 2026 for Premium customers.

We use several dimensions:

```text
dim_product
    ↓
category = Electronics

dim_store
    ↓
city = Chennai

dim_date
    ↓
year = 2026

dim_customer
    ↓
segment = Premium
```

Conceptually:

```text
                  FACT_SALES
                 /    |    |    \
                ↓     ↓    ↓     ↓
          Product   Store Date Customer
             ↓        ↓     ↓      ↓
       Electronics Chennai 2026 Premium
```

The resulting data is a much smaller subset.

### SQL

```sql
SELECT
    SUM(f.sales_amount) AS total_sales
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
JOIN dim_store s
    ON f.store_key = s.store_key
JOIN dim_date d
    ON f.date_key = d.date_key
JOIN dim_customer c
    ON f.customer_key = c.customer_key
WHERE p.category = 'Electronics'
  AND s.city = 'Chennai'
  AND d.year = 2026
  AND c.segment = 'Premium';
```

This is **dicing**.

---

# 4. Direct Comparison

|Feature|Slicing|Dicing|
|---|---|---|
|Basic idea|Select one subset|Select a smaller multidimensional subset|
|Dimensions involved|Typically one dimension|Multiple dimensions|
|Example|`Year = 2026`|`Year = 2026 AND City = Chennai AND Category = Electronics`|
|Result|One specific view|More specific subset|
|Complexity|Simpler|More complex|

---

# 5. Visual Example

Imagine the entire sales data is:

```text
                 ALL SALES
                     │
          ┌──────────┴──────────┐
          │                     │
        SLICE                  DICE
          │                     │
     Year = 2026       Year = 2026
                              +
                         Chennai
                              +
                       Electronics
                              +
                          Premium
```

### Slice

```text
ALL DATA
   │
   └── Year = 2026
          ↓
     2026 Sales
```

### Dice

```text
ALL DATA
   │
   ├── Year = 2026
   ├── City = Chennai
   ├── Category = Electronics
   └── Customer = Premium
          ↓
   Very specific subset
```

---

# 6. Important Point: Both Operate on Fact Data

The filtering conditions usually come from **dimensions**, but the final result is a subset of the **fact rows**.

For example:

```text
dim_product
category = Electronics
       ↓
identifies relevant product_keys
       ↓
fact_sales
       ↓
sales_amount
```

So:

> **Dimensions provide the filtering context; facts provide the measurements being analyzed.**

---

# 7. Easy Way to Remember

### Slice

**One cut**

```text
Year = 2026
```

### Dice

**Multiple cuts**

```text
Year = 2026
AND
City = Chennai
AND
Category = Electronics
```

### In one sentence

> **Slicing selects a specific subset based on a dimension, while dicing creates a more specific subset by applying conditions across multiple dimensions.**
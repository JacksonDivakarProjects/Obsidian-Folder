Perfect timing, Jack. You’re now entering **advanced SQL aggregation** — a must-have skill for analytics, reporting, and interviews.

Here’s your **comprehensive guide** to:

> ✅ `GROUPING SETS`  
> ✅ `ROLLUP`  
> ✅ `CUBE`

---

## 🚀 Why These Exist

Normally, a single `GROUP BY` gives **one level of grouping**.

But for reports and dashboards, we often need:

- **Subtotals**
    
- **Grand totals**
    
- **Multiple grouping combinations**
    

These 3 tools give you that — all in one query.

---

## 🧠 1. `GROUPING SETS`

### 🔹 Definition:

`GROUPING SETS` lets you specify **exact group combinations** you want to aggregate.

### 📦 Syntax:

```sql
SELECT col1, col2, SUM(val)
FROM table
GROUP BY GROUPING SETS (
    (col1, col2),
    (col1),
    ()
);
```

### 📊 Example:

```sql
SELECT city, customer_name, SUM(amount)
FROM uber_rides
GROUP BY GROUPING SETS (
    (city, customer_name),   -- detail
    (city),                  -- subtotal per city
    ()                       -- grand total
);
```

### ✅ Output:

|city|customer_name|sum|
|---|---|---|
|Chennai|Ram|500|
|Chennai|John|450|
|Chennai|NULL|950 ← subtotal|
|NULL|NULL|2350 ← grand total|

---

## 🔁 2. `ROLLUP`

### 🔹 Definition:

`ROLLUP` is a shortcut for hierarchical subtotals → top-down aggregation.

### 📦 Syntax:

```sql
SELECT col1, col2, SUM(val)
FROM table
GROUP BY ROLLUP (col1, col2)
```

Equivalent to:

```sql
GROUPING SETS (
    (col1, col2),
    (col1),
    ()
)
```

### 📊 Example:

```sql
SELECT city, customer_name, SUM(amount)
FROM uber_rides
GROUP BY ROLLUP (city, customer_name);
```

Same output as `GROUPING SETS`, but **auto-generated hierarchy**.

---

## 🧮 3. `CUBE`

### 🔹 Definition:

`CUBE` generates **all possible combinations** of grouping columns. Think: full cross-tab report.

### 📦 Syntax:

```sql
SELECT col1, col2, SUM(val)
FROM table
GROUP BY CUBE (col1, col2);
```

Equivalent to:

```sql
GROUPING SETS (
    (col1, col2),
    (col1),
    (col2),
    ()
)
```

### 📊 Example:

```sql
SELECT city, customer_name, SUM(amount)
FROM uber_rides
GROUP BY CUBE (city, customer_name);
```

### ✅ Output:

|city|customer_name|sum|
|---|---|---|
|Chennai|Ram|500|
|Chennai|NULL|950|
|NULL|Ram|600|
|NULL|NULL|2350|

---

## 🧠 Bonus: `GROUPING()` Function

Add this to **detect** which row is subtotal or total:

```sql
GROUPING(city) AS is_city_total,
GROUPING(customer_name) AS is_customer_total
```

You can even label them:

```sql
CASE 
  WHEN GROUPING(city) = 1 AND GROUPING(customer_name) = 1 THEN 'Grand Total'
  WHEN GROUPING(customer_name) = 1 THEN 'Subtotal per City'
  WHEN GROUPING(city) = 1 THEN 'Subtotal per Customer'
  ELSE 'Detail'
END AS row_type
```

---

## 🏁 Summary Table

|Feature|What It Does|Use When|
|---|---|---|
|`GROUPING SETS`|Manual control of group combinations|You want specific subtotal logic|
|`ROLLUP`|Hierarchical totals (top-down)|Reports with subtotal → total flow|
|`CUBE`|All combinations (cross-tab style)|Multidimensional analysis|

---

## ✅ Pro Tips

- All 3 work with `GROUPING()` to help filter/label totals.
    
- You can `ORDER BY GROUPING(...)` to sort totals last.
    
- Wrap your query in a CTE or subquery for **filtering totals**.
    

---

Let me know if you want:

- Diagrams for each
    
- Real dataset examples
    
- A cheat sheet PDF for revision

## 🔗 Related Notes
- [[Data Science/SQL/Tricks and Tips/Group By and Having Tricks|Group By and Having Tricks]]
- [[Data Science/SQL/Window Functions/SQL Window Functions and Aggregate Examples|SQL Window Functions and Aggregate Examples]]

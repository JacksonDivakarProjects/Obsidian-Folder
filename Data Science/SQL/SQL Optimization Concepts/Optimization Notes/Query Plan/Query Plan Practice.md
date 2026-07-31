Below are **realistic, production-style EXPLAIN plans** (simplified for clarity) with **sharp, practical explanations** so you understand *exactly how the SQL engine thinks and why it chose that plan*.

These examples are representative of **PostgreSQL**, but the logic applies across MySQL, SQL Server, Oracle, Snowflake, etc.

---

# 🔷 **PLAN 1 — Index Seek + Nested Loop Join (Highly Selective Filter)**

### ✅ **Query**

```sql
SELECT o.order_id, o.amount, c.customer_name
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.order_id = 120035;
```

### 📌 **Plan**

```
Nested Loop
  -> Index Scan using idx_orders_order_id on orders
       Index Cond: (order_id = 120035)
  -> Index Scan using idx_customers_customer_id on customers
       Index Cond: (customer_id = o.customer_id)
```

---

### 🧠 **Explanation (Why this plan?)**

### ✔ 1. **Highly selective filter (`order_id = …`)**

This guarantees **1 row** (or very few rows), so:

* Index Seek on `orders(order_id)` is optimal
* It produces exactly 1 row → perfect for nested loops

### ✔ 2. **Nested Loop Join is ideal**

When outer side returns few rows, nested loops are the fastest join strategy.

### ✔ 3. **Second Index Seek**

For each matching order, SQL performs:

```
Lookup customer using customers.customer_id index
```

That's extremely fast.

---

### 🎯 **When you see this plan, it means:**

* Your indexes are good
* The optimizer found a highly selective path
* Joins are efficient
* No sorting needed

This is the *best possible plan* for selective queries.

---

---

# 🔷 **PLAN 2 — Hash Join + Sequential Scan (No Useful Indexes)**

### ✅ **Query**

```sql
SELECT *
FROM orders o
JOIN customers c ON c.region = o.region;
```

### 📌 **Plan**

```
Hash Join
  Hash Cond: (o.region = c.region)
  -> Seq Scan on orders
  -> Hash
       -> Seq Scan on customers
```

---

### 🧠 **Explanation**

### ✔ 1. **No index on `region`**

Joins based on `region` require reading entire tables.

### ✔ 2. **Hash Join chosen**

* Faster than Sort-Merge when no indexes exist
* No ordering needed
* Perfect for equality joins

### ✔ 3. **Both tables scanned fully**

The engine builds a hash table for the smaller table (`customers`) and probes it with the larger (`orders`).

---

### 🎯 **What this plan tells you**

* You need an index on `region` **if the join is frequent**
* Hash join is chosen because sorting would be more expensive

---

---

# 🔷 **PLAN 3 — Sort-Merge Join (Inputs Must be Sorted)**

### ✅ **Query**

```sql
SELECT *
FROM sales s
JOIN targets t ON s.product_id = t.product_id;
```

### 📌 **Plan**

```
Merge Join
  Merge Cond: (s.product_id = t.product_id)
  -> Sort  (sales)
       Sort Key: product_id
  -> Sort  (targets)
       Sort Key: product_id
```

---

### 🧠 **Explanation**

### ✔ 1. **Merge Join only works if both sides are sorted**

SQL must sort `sales.product_id` and `targets.product_id`.

### ✔ 2. **Sorting uses merge-sort internally**

This is efficient for large data.

### ✔ 3. **Why not hash join?**

Possible reasons:

* The optimizer knows these tables have **many duplicates**
* A merge join can outperform hash join for such distributions
* Or you have an ORDER BY later, so merge join reduces future sort cost

---

### 🎯 **Reading this plan tells you:**

* You’re paying the cost of **two sorts**
* Adding indexes on `product_id` may eliminate the sort altogether
* Merge join is efficient when data is already sorted or highly duplicated

---

---

# 🔷 **PLAN 4 — Bitmap Index Scan (Postgres Only)**

### ✅ **Query**

```sql
SELECT *
FROM employees
WHERE dept_id = 10
  AND salary > 50000;
```

### 📌 **Plan**

```
Bitmap Heap Scan
  Recheck Cond: (dept_id = 10 AND salary > 50000)
  -> BitmapAnd
       -> Bitmap Index Scan on idx_dept
            Index Cond: (dept_id = 10)
       -> Bitmap Index Scan on idx_salary
            Index Cond: (salary > 50000)
```

---

### 🧠 **Explanation**

### ✔ 1. **Two separate indexes**

* One on dept_id
* One on salary

SQL uses both.

### ✔ 2. **Bitmap AND merges row pointers efficiently**

Instead of two index seeks, SQL:

* Builds bitmap A (dept=10)
* Builds bitmap B (salary>50000)
* ANDs them

### ✔ 3. **No row-by-row lookups**

Bitmaps allow SQL to fetch all qualifying rows in sorted block order → fewer random I/O operations.

---

### 🎯 **When you see this plan:**

* SQL is efficiently combining multiple indexes
* This happens on medium-selective predicates
* This is optimal for large scans

---

---

# 🔷 **PLAN 5 — Painful Sort Spill (Heavy Load Situation)**

### ❌ **Query**

```sql
SELECT *
FROM logs
ORDER BY created_at;
```

### ⚠ Plan

```
Sort
  Sort Key: created_at
  Sort Method: external merge  Disk: 150MB
  -> Seq Scan on logs
```

---

### 🧠 **Explanation**

### ✔ SQL tried to sort in memory

→ Memory insufficient → spilled to disk.

### ✔ External merge sort is used

→ Much slower because of disk operations.

### ✔ Full table scan is unavoidable

No index on `created_at`.

---

### 🎯 **How to fix**

1. Create an index:

```sql
CREATE INDEX idx_logs_created ON logs(created_at);
```

2. Or increase sort memory (engine-specific):

* `work_mem` (Postgres)
* `sort_buffer_size` (MySQL)

---

---

# 🔷 **PLAN 6 — CTE Materialization (Performance Trap)**

### ❌ Query

```sql
WITH recent AS (
   SELECT * FROM orders WHERE order_date > NOW() - INTERVAL '30 days'
)
SELECT *
FROM recent
WHERE amount > 100;
```

### ⚠ Plan

```
CTE Scan on recent
   Filter: (amount > 100)
->  Materialize
        -> Seq Scan on orders
             Filter: (order_date > ...)
```

---

### 🧠 **Explanation**

### ✔ The CTE is fully materialized

* Orders are read
* Filter applied
* Results stored in temp memory
* **Second filter is applied afterward**

### ✔ Predicates cannot be pushed down

This is why people avoid CTEs for performance-sensitive workloads.

---

### 🎯 **Fix**

Use a subquery:

```sql
SELECT *
FROM (
    SELECT *
    FROM orders
    WHERE order_date > NOW() - INTERVAL '30 days'
) recent
WHERE amount > 100;
```

Or Postgres 12+:

```sql
WITH recent AS NOT MATERIALIZED ( ... )
```

---

# ⭐ FINAL EXECUTIVE SUMMARY

Here’s what plans teach you:

| Scenario                 | What the plan means        | What you can optimize             |
| ------------------------ | -------------------------- | --------------------------------- |
| Index Seek + Nested Loop | High selectivity           | Good indexing                     |
| Hash Join                | No ordering / no indexes   | Add indexes if needed             |
| Merge Join               | Input must be sorted       | Index on join keys                |
| Bitmap Scan              | Combining multiple indexes | Good for medium filters           |
| Sort Spill               | Sort too big for RAM       | Add index or increase sort memory |
| CTE Scan                 | Materialization cost       | Avoid or make NOT MATERIALIZED    |

---

If you want, I can also give you:

📘 **A library of 20+ sample plans with business-case explanations**
📈 **A visual diagram of how the optimizer chooses join methods**
🎯 **A checklist for reading plans like a senior engineer**

Just tell me **“give me more plans”** or **“give me the diagram.”**
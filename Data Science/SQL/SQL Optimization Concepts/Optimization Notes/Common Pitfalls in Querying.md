Below is a **professional-grade guide** to the **most common SQL pitfalls junior developers fall into**, *why these mistakes break the optimizer*, and *how to fix the queries the right way*.

This is exactly the type of knowledge senior engineers use to deliver 10× faster systems.

---

# 🚫 **1. Using Functions on Indexed Columns**

### ❌ Pitfall:

```sql
WHERE LOWER(name) = 'john'
WHERE YEAR(order_date) = 2024
WHERE salary + 1000 > 50000
```

### ❗ Why It Stops Optimization

Functions disable index seeks because SQL must apply the function to **every row**.

SQL cannot use:

* `INDEX(name)`
* `INDEX(order_date)`
* `INDEX(salary)`

This causes **full table scans**.

### ✅ Correct Way:

Rewrite the filter so the indexed column stays raw.

```sql
WHERE name = 'John'
WHERE order_date >= '2024-01-01'
  AND order_date <  '2025-01-01'
WHERE salary > 49000
```

---

# 🚫 **2. Using `SELECT *` in Large Queries**

### ❌ Pitfall:

```sql
SELECT *
FROM big_orders
JOIN customers USING(customer_id);
```

### ❗ Why It Stops Optimization

* Pulls unnecessary columns → bigger I/O
* Prevents covering indexes
* Reduces performance of joins and sorting

### ✅ Correct Way:

Select only what you need.

```sql
SELECT o.order_id, o.amount, c.customer_name
FROM big_orders o
JOIN customers c ON c.customer_id = o.customer_id;
```

---

# 🚫 **3. Missing Needed Indexes**

### ❌ Pitfall:

Query filters columns that have no index:

```sql
WHERE status = 'ACTIVE'
AND created_at > NOW() - INTERVAL '30 days'
```

### ❗ Why It Stops Optimization

* SQL cannot seek
* SQL must scan entire table
* Sorting and joins get slower due to more data

### ✅ Correct Way:

Add proper composite index:

```sql
CREATE INDEX idx_status_created ON users(status, created_at);
```

---

# 🚫 **4. Wrong Join Order**

### ❌ Pitfall:

```sql
SELECT ...
FROM huge_fact f
JOIN small_dim d ON f.key = d.key;
```

With **small table on the RIGHT**.

### ❗ Why It Stops Optimization

Nested loop join becomes expensive if the driver table is the large one.

### ✅ Correct Way:

Put the **small table first** or use appropriate join hints (engine dependent):

```sql
SELECT ...
FROM small_dim d
JOIN huge_fact f ON f.key = d.key;
```

---

# 🚫 **5. Using Subqueries When JOINs Are Better**

### ❌ Pitfall:

```sql
SELECT *
FROM orders
WHERE customer_id IN (SELECT id FROM customers WHERE region = 'EU');
```

### ❗ Why It Stops Optimization

* Harder for optimizer to push predicates
* Subquery executed inefficiently

### ✅ Correct Way:

Use JOIN:

```sql
SELECT o.*
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE c.region = 'EU';
```

---

# 🚫 **6. Overusing DISTINCT to Fix Bad Joins**

### ❌ Pitfall:

```sql
SELECT DISTINCT order_id
FROM orders
JOIN customers ON ...
```

### ❗ Why It Stops Optimization

* DISTINCT adds a sort or hash aggregate
* Hides incorrect joins
* Adds unnecessary load

### ✅ Correct Way:

Fix the join condition.

---

# 🚫 **7. Not Using `EXPLAIN` to Understand the Query**

### ❌ Pitfall:

Juniors write queries blindly, without checking the execution plan.

### ❗ Why It Stops Optimization

You never see:

* Why full table scan happens
* Why hash join was used
* Why sort is spilling to disk

### ✅ Correct Way:

Always inspect:

```sql
EXPLAIN ANALYZE SELECT ...
```

---

# 🚫 **8. Writing Range Filters on the Wrong Side of Index**

### ❌ Pitfall:

```sql
WHERE created_at + INTERVAL '1 day' > NOW()
```

### ❗ Why It Stops Optimization

Transforms filtered column → breaks index usage.

### ✅ Correct Way:

```sql
WHERE created_at > NOW() - INTERVAL '1 day'
```

---

# 🚫 **9. Using OR Instead of UNION When Columns Are Indexed**

### ❌ Pitfall:

```sql
WHERE status = 'ACTIVE'
   OR status = 'PENDING'
```

### ❗ Why It Stops Optimization

`OR` prevents the optimizer from using indexes efficiently.

### ✅ Correct Way:

Rewrite using UNION:

```sql
SELECT ... WHERE status = 'ACTIVE'
UNION ALL
SELECT ... WHERE status = 'PENDING'
```

---

# 🚫 **10. Forgetting to Limit Large Result Sets**

### ❌ Pitfall:

```sql
SELECT * FROM huge_table ORDER BY created_at;
```

### ❗ Why It Stops Optimization

Sorting millions of rows is expensive.

### ✅ Correct Way:

```sql
SELECT * FROM huge_table
ORDER BY created_at
LIMIT 100;
```

---

# 🚫 **11. Doing Joins on Different Data Types**

### ❌ Pitfall:

```sql
JOIN orders o ON o.customer_id = c.id  -- but one is int, the other is varchar
```

### ❗ Why It Stops Optimization

* Forces implicit casting
* Prevents index use
* Slows join dramatically

### ✅ Correct Way:

Unify data types in the schema.

Or cast explicitly:

```sql
JOIN orders o ON o.customer_id = CAST(c.id AS INT)
```

---

# 🚫 **12. Using NOT LIKE or NOT IN (Optimization Killers)**

### ❌ Pitfall:

```sql
WHERE name NOT LIKE 'A%'
```

### ❗ Why It Stops Optimization

* Negative conditions are not index-friendly
* SQL falls back to full scan

### ✅ Correct Way:

Try to restructure logic or use inclusion filters.

---

# 🚫 **13. Over-Normalizing the Schema**

### ❌ Pitfall:

Splitting data into too many tables → many joins.

### ❗ Why It Stops Optimization

* Complex join planning
* Heavy IO
* Harder for optimizer to pick the best join path

### ✅ Correct Way:

Use practical normalization + targeted denormalization.

---

# 🚫 **14. Overusing CTEs in MySQL/Postgres**

### ❌ Pitfall:

```sql
WITH temp AS (
   SELECT ...
)
SELECT ...
FROM temp;
```

### ❗ Why It Stops Optimization

Older versions of PostgreSQL materialize CTEs → no pushdown.

### ✅ Correct Way:

Use subquery unless logical separation is needed.

---

# 🔷 **📌 EXECUTIVE SUMMARY — Junior Pitfalls vs Senior Fixes**

| Junior Mistake               | Why It Breaks Optimization | Senior Fix                 |
| ---------------------------- | -------------------------- | -------------------------- |
| Writing functions on columns | Blocks indexes             | Rewrite predicate          |
| SELECT * everywhere          | Bloats I/O                 | Select only needed columns |
| Bad indexing                 | Full scans                 | Create selective indexes   |
| Wrong join direction         | Wrong join algorithm used  | Join small → large         |
| Subqueries                   | Hard to optimize           | Use JOIN                   |
| DISTINCT misused             | Extra sorting              | Fix join logic             |
| No EXPLAIN usage             | Blind queries              | Always analyze plan        |
| Mixed data types             | Forces casts               | Fix schema                 |
| OR conditions                | Breaks index               | Use UNION                  |
| NOT LIKE, NOT IN             | Not indexable              | Rewrite conditions         |

---

# ⭐ FINAL WORD

**SQL optimizes automatically — but only if you avoid patterns that confuse or block the optimizer.**
Your role is to **write queries in an optimizer-friendly style**, choose the right indexes, and inspect plans.

This is exactly how senior engineers outperform junior developers in SQL-heavy environments.

---

If you want, I can turn these into:

📘 A professional PDF "SQL Anti-Patterns Handbook"
📄 A one-page cheat sheet
🧠 A flashcard-style memory deck

Just tell me what you prefer!
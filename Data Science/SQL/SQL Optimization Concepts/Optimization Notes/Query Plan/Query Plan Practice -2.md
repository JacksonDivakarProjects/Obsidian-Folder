Below is your **professional SQL Execution Plan Library** — a complete reference that captures the **20 most important real-world execution plans**, how to read them, why the optimizer chooses them, and how to optimize them.

This is designed to be a **serious engineering asset**, the kind senior backend/data engineers rely on when diagnosing performance issues.

---

# 📘 **SQL EXECUTION PLAN LIBRARY (20 Real World Examples)**

*A complete reference for understanding how SQL engines think.*

---

# 🔵 **CATEGORY 1: INDEX ACCESS STRATEGIES**

---

## **1. Index Seek (Best Case Scenario)**

### Query:

```sql
SELECT * FROM users WHERE id = 500;
```

### Plan:

```
Index Scan using idx_users_id on users
  Index Cond: (id = 500)
```

### Meaning:

* Highly selective lookup
* Perfect index usage

### When this happens:

* Equality filters on primary/unique indexes
* Very selective predicates

### Optimize:

* Make sure `id` is indexed
* Avoid wrapping indexed column in functions

---

## **2. Index Range Scan**

### Query:

```sql
SELECT * FROM orders WHERE amount BETWEEN 1000 AND 2000;
```

### Plan:

```
Index Range Scan on idx_orders_amount
  Index Cond: (amount >= 1000 AND amount <= 2000)
```

### Meaning:

* Index used for scanning a value range
* Efficient for ordered access

### Optimize:

* Ensure range column is leading index key
* Avoid expressions like `amount + 10 > 1000`

---

## **3. Index Scan (Full Index Walk)**

### Query:

```sql
SELECT * FROM users WHERE last_name LIKE '%son';
```

### Plan:

```
Index Scan using idx_last_name on users
  Filter: last_name ~~ '%son'
```

### Meaning:

* SQL walks entire index
* Index cannot be searched directly due to wildcard prefix

### Fix:

* Avoid leading `%`
* Use trigram index (Postgres) if necessary

---

## **4. Bitmap Index Scan (Postgres Only)**

### Query:

```sql
SELECT * FROM employees WHERE dept_id = 3 AND salary > 60000;
```

### Plan:

```
BitmapAnd
   Bitmap Index Scan on idx_dept
   Bitmap Index Scan on idx_salary
Bitmap Heap Scan
```

### Meaning:

* SQL combines two indexes efficiently
* Used for medium-selective predicates

### Fix:

* Usually already optimal
* Add composite index if query is extremely frequent

---

# 🔵 **CATEGORY 2: TABLE ACCESS**

---

## **5. Sequential Scan (Full Table Scan)**

### Query:

```sql
SELECT * FROM logs WHERE message LIKE '%error%';
```

### Plan:

```
Seq Scan on logs
  Filter: message ~~ '%error%'
```

### Meaning:

* Index cannot be used
* Entire table must be read

### Fix:

* Use full-text search index
* Avoid leading wildcards

---

## **6. Index-Only Scan (Covering Index)**

### Query:

```sql
SELECT id, status FROM users WHERE status = 'ACTIVE';
```

### Plan:

```
Index Only Scan using idx_status on users
  Index Cond: (status = 'ACTIVE')
```

### Meaning:

* No table lookup needed
* Very fast

### Optimize:

* Include all needed columns in the index
* Keep table vacuumed (Postgres)

---

# 🔵 **CATEGORY 3: JOIN STRATEGIES**

---

## **7. Nested Loop Join (Good for Small → Large)**

### Query:

```sql
SELECT * FROM orders o JOIN customers c ON c.id = o.customer_id;
```

### Plan:

```
Nested Loop
  -> Index Scan on orders
  -> Index Scan on customers
```

### Meaning:

* Small outer table
* Index used on inner side
* Very fast when selective

### Fix:

* Ensure join columns are indexed
* Reduce outer rows via filtering

---

## **8. Nested Loop + Seq Scan (Bad Case)**

### Query:

```sql
SELECT * FROM orders o JOIN logs l ON o.customer_id = l.user_id;
```

### Plan:

```
Nested Loop
  -> Seq Scan on orders
  -> Seq Scan on logs
```

### Meaning:

* No indexes on join columns
* Very expensive for large tables

### Fix:

* Add indexes on join keys
* Force hash join where appropriate

---

## **9. Hash Join (Large Tables, Equality Join)**

### Query:

```sql
SELECT * FROM sales s JOIN products p ON p.id = s.product_id;
```

### Plan:

```
Hash Join
  Hash Cond: (s.product_id = p.id)
  -> Seq Scan sales
  -> Hash on products
```

### Meaning:

* Hash join chosen for large equality joins
* Index not needed

### Fix:

* Add index if join is very selective
* Increase hash memory if spill occurs

---

## **10. Sort-Merge Join (Requires Sorted Input)**

### Query:

```sql
SELECT * FROM s JOIN t ON s.id = t.id;
```

### Plan:

```
Merge Join
  Merge Cond: (s.id = t.id)
  -> Sort on s.id
  -> Sort on t.id
```

### Meaning:

* Both sides must be sorted
* Sorting happens if no index exists

### Fix:

* Add indexes on join keys
* Avoid unnecessary ORDER BY later

---

# 🔵 **CATEGORY 4: SORTING & AGGREGATION**

---

## **11. Sort (Internal / In-Memory)**

### Query:

```sql
SELECT * FROM customers ORDER BY created_at;
```

### Plan:

```
Sort
  Sort Key: created_at
  -> Seq Scan on customers
```

### Meaning:

* Sorting in RAM
* Expensive depending on row count

### Fix:

* Add index on created_at
* Limit rows

---

## **12. Sort Spilling to Disk (Bad)**

### Plan excerpt:

```
Sort Method: external merge  Disk: 200MB
```

### Meaning:

* Not enough memory
* Sorting spilled to disk
* Very slow

### Fix:

* Add index
* Increase work_mem
* Reduce dataset size

---

## **13. Hash Aggregate**

### Query:

```sql
SELECT dept_id, COUNT(*) FROM employees GROUP BY dept_id;
```

### Plan:

```
HashAggregate
  Group Key: dept_id
```

### Meaning:

* Hash table built to group rows
* Fast if memory is enough

### Fix:

* Increase memory
* Rewrite with sort aggregate if memory is low

---

## **14. Sort Aggregate**

### Query:

```sql
SELECT dept_id, COUNT(*) FROM employees GROUP BY dept_id;
```

### Plan:

```
Sort
  Sort Key: dept_id
GroupAggregate
```

### Meaning:

* Sorting then grouping
* Chosen if memory too low for hash

### Fix:

* Increase hash_mem
* Ensure index on group key

---

# 🔵 **CATEGORY 5: SUBQUERY / CTE BEHAVIOR**

---

## **15. CTE Materialization (Bad Case)**

### Query:

```sql
WITH r AS (SELECT * FROM orders WHERE status = 'PAID')
SELECT * FROM r WHERE amount > 100;
```

### Plan:

```
CTE Scan on r
  Filter: amount > 100
```

### Meaning:

* CTE fully materialized
* Filters not pushed down

### Fix:

* Use subqueries
* OR `WITH ... NOT MATERIALIZED` in PG12+

---

## **16. Inlined Subquery (Optimal)**

### Query:

```sql
SELECT *
FROM (SELECT * FROM orders WHERE status='PAID') x
WHERE amount > 100;
```

### Plan:

```
Seq Scan on orders
  Filter: status='PAID' AND amount > 100
```

### Meaning:

* Optimizer pushed down filters correctly
* Efficient

---

## **17. EXISTS (Efficient Semi-Join)**

### Query:

```sql
SELECT * FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);
```

### Plan:

```
Semi Join
  -> Index Scan on orders
```

### Meaning:

* Fast semi-join
* Only checks existence
* Stops early

---

## **18. NOT EXISTS (Efficient Anti-Join)**

### Query:

```sql
SELECT * FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM blacklist b WHERE b.id = c.id);
```

### Plan:

```
Anti Join
  -> Index Scan on blacklist
```

### Meaning:

* Efficient anti-join
* Preferred over NOT IN

---

# 🔵 **CATEGORY 6: MISC OPTIMIZER PATTERNS**

---

## **19. Predicate Pushdown**

### Query:

```sql
SELECT * 
FROM (SELECT * FROM sales) s
WHERE amount > 100;
```

### Plan:

```
Seq Scan on sales
  Filter: amount > 100
```

### Meaning:

* Filter pushed into base scan
* Very efficient

---

## **20. Cardinality Misestimate (Dangerous)**

### Query:

```sql
SELECT * FROM orders WHERE status='ACTIVE';
```

### Plan:

```
Seq Scan (cost=1000..2000 rows=10)
```

But real rows = 500,000.

### Meaning:

* Stats outdated
* SQL thinks filter is highly selective → chooses wrong plan

### Fix:

```
ANALYZE orders;
```

Or updating statistics.

---

# ⭐ **EXECUTIVE SUMMARY — What This Library Teaches You**

* SQL chooses plans based on cost, not syntax
* Index seek / bitmap / nested loop → good signs
* Sort spill / full scan / CTE materialization → bad signs
* Hash vs Merge vs Nested Loop depends on data size and distribution
* Statistics control everything

---

If you want, I can now generate:

📘 **A PDF version of this library**
🎯 **A cheat sheet summarizing all 20 patterns**
📈 **A visual flowchart showing how the optimizer picks plans**

Just tell me **which format you want next.**
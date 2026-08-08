# Common Pitfalls in Querying

The recurring query-writing habits that block the optimizer, why each one hurts, and the fix.

## 1. Functions on Indexed Columns

**Pitfall:**
```sql
WHERE LOWER(name) = 'john'
WHERE YEAR(order_date) = 2024
WHERE salary + 1000 > 50000
```

**Why it hurts:** the function/expression has to be evaluated for every row before it can be compared, so a plain index on `name`, `order_date`, or `salary` can't be seeked — the engine falls back to a full scan.

**Fix:** keep the indexed column raw on one side of the comparison.
```sql
WHERE name = 'John'
WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01'
WHERE salary > 49000
```

## 2. `SELECT *` in Large Queries

**Pitfall:**
```sql
SELECT * FROM big_orders JOIN customers USING (customer_id);
```

**Why it hurts:** pulls unnecessary columns (more I/O), and prevents a covering/index-only scan since the index can't contain every column of every table.

**Fix:** select only what's needed.
```sql
SELECT o.order_id, o.amount, c.customer_name
FROM big_orders o
JOIN customers c ON c.customer_id = o.customer_id;
```

## 3. Missing Needed Indexes

**Pitfall:** filtering on columns with no supporting index.
```sql
WHERE status = 'ACTIVE'
  AND created_at > NOW() - INTERVAL '30 days'
```

**Why it hurts:** without an index, the engine can't seek — it scans the whole table, and any downstream sort/join gets slower because it's working with more rows than necessary.

**Fix:** add a composite index matching the filter columns.
```sql
CREATE INDEX idx_status_created ON users (status, created_at);
```

## 4. Wrong Join Order / Driving Table

**Pitfall:**
```sql
SELECT ...
FROM huge_fact f
JOIN small_dim d ON f.key = d.key;
```

**Why it hurts:** in a nested-loop plan, using the huge table as the outer (driving) side means the loop runs once per row of the *large* table — the opposite of what you want.

**Fix:** in practice, a well-tuned optimizer reorders joins itself based on cost estimates, so this mostly matters when statistics are stale or the query forces a particular order. Still, writing the smaller/more-selective side first is a reasonable default and helps human readability:
```sql
SELECT ...
FROM small_dim d
JOIN huge_fact f ON f.key = d.key;
```

## 5. Subqueries Where a JOIN Is Clearer

**Pitfall:**
```sql
SELECT * FROM orders
WHERE customer_id IN (SELECT id FROM customers WHERE region = 'EU');
```

**Why it can hurt:** in older optimizers, some subquery forms were harder to flatten and could block predicate push-down. Modern PostgreSQL/MySQL optimizers generally rewrite simple `IN (SELECT ...)` into a semi-join automatically — so this is less of a hard rule than it used to be. Still, an explicit `JOIN` is usually easier to read and to reason about, and guarantees the rewrite:
```sql
SELECT o.*
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE c.region = 'EU';
```

## 6. Using `DISTINCT` to Paper Over a Bad Join

**Pitfall:**
```sql
SELECT DISTINCT order_id
FROM orders
JOIN customers ON ...
```

**Why it hurts:** `DISTINCT` adds a sort or hash-aggregate step, and — more importantly — it masks a join that's producing duplicate rows instead of fixing the actual join condition.

**Fix:** fix the join condition so it doesn't fan out rows in the first place.

## 7. Never Checking `EXPLAIN`

**Pitfall:** writing and shipping queries without ever looking at the execution plan.

**Why it hurts:** you never learn *why* a query is slow — whether it's a full table scan, an unexpectedly chosen hash join, or a sort spilling to disk.

**Fix:** get in the habit of running:
```sql
EXPLAIN ANALYZE SELECT ...
```

## 8. Filters Written on the Wrong Side of the Comparison

**Pitfall:**
```sql
WHERE created_at + INTERVAL '1 day' > NOW()
```

**Why it hurts:** the arithmetic is applied to the indexed column, which — like functions — defeats a plain index seek.

**Fix:** isolate the column, and put the arithmetic on the (non-indexed) constant side instead.
```sql
WHERE created_at > NOW() - INTERVAL '1 day'
```

## 9. `OR` Across an Indexed Column, When a `UNION` Would Do Better

**Pitfall:**
```sql
WHERE status = 'ACTIVE' OR status = 'PENDING'
```

**Why it can hurt:** some optimizers handle `OR` across multiple indexed conditions poorly, especially across *different* columns (`WHERE a = 1 OR b = 2`), falling back to a scan instead of combining two index scans. For `OR` on the *same* column with equality, `IN ('ACTIVE', 'PENDING')` is simpler and usually just as well-optimized as splitting the query. Reach for `UNION ALL` mainly when the `OR` branches use genuinely different indexes/conditions:
```sql
SELECT ... WHERE status = 'ACTIVE'
UNION ALL
SELECT ... WHERE status = 'PENDING'
```

## 10. Forgetting to Limit Large Result Sets

**Pitfall:**
```sql
SELECT * FROM huge_table ORDER BY created_at;
```

**Why it hurts:** sorting millions of rows just to display a handful of them is wasted work.

**Fix:**
```sql
SELECT * FROM huge_table
ORDER BY created_at
LIMIT 100;
```

## 11. Joining Across Mismatched Data Types

**Pitfall:**
```sql
JOIN orders o ON o.customer_id = c.id  -- one column int, the other varchar
```

**Why it hurts:** the engine has to implicitly cast one side on every row, which can prevent index use and adds real CPU overhead.

**Fix:** unify the data types in the schema, or cast explicitly and deliberately:
```sql
JOIN orders o ON o.customer_id = CAST(c.id AS INT)
```

## 12. `NOT LIKE` / `NOT IN` on Large Tables

**Pitfall:**
```sql
WHERE name NOT LIKE 'A%'
```

**Why it hurts:** negative conditions generally can't be satisfied by a plain index seek — the engine has to scan and exclude, rather than seek and include. (`NOT IN` has the additional NULL-handling trap covered in [[Data Engineering Role Notes/SQL/Other Keywords/SQL Exists and Not Exists|SQL EXISTS & NOT EXISTS]].)

**Fix:** restructure toward an inclusion filter where possible, or accept the scan if the predicate genuinely isn't selective.

## 13. Over-Normalizing the Schema

**Pitfall:** splitting data across many small tables, requiring many joins to answer common questions.

**Why it hurts:** more joins means a harder join-planning problem and more I/O, even when each individual table is well-indexed.

**Fix:** balance normalization with targeted denormalization for hot query paths.

## 14. Assuming CTEs Always Optimize Like Subqueries

**Pitfall:**
```sql
WITH temp AS (
   SELECT ...
)
SELECT ...
FROM temp;
```

**Why it can hurt:** PostgreSQL before version 12 always materialized CTEs, which blocked predicate push-down into them. PostgreSQL 12+ auto-inlines simple CTEs (equivalent to a subquery) unless the CTE is referenced multiple times, is recursive, or you explicitly force materialization.

**Fix:** on Postgres 12+, this is rarely an issue by default. On older Postgres, or when you need to force the old behavior either way, be explicit:
```sql
WITH temp AS MATERIALIZED (...)      -- force materialization
WITH temp AS NOT MATERIALIZED (...)  -- force inlining
```

## Summary: Junior Mistakes vs. Senior Fixes

| Mistake | Why it breaks optimization | Fix |
|---|---|---|
| Functions on columns | Blocks index seeks | Rewrite the predicate |
| `SELECT *` everywhere | Bloats I/O, blocks covering indexes | Select only needed columns |
| Missing indexes | Forces full scans | Add selective indexes |
| Wrong driving table | Can pick a worse nested-loop order | Filter early; check `EXPLAIN` |
| Subqueries where JOIN is clearer | Historically harder to optimize | Prefer explicit JOIN when equivalent |
| Misused `DISTINCT` | Masks a bad join; adds a sort | Fix the join logic |
| No `EXPLAIN` usage | Flying blind | Always inspect the plan |
| Mismatched data types | Forces implicit casts | Fix the schema |
| `OR` across columns | Can defeat index combination | Consider `UNION ALL` |
| `NOT LIKE`, `NOT IN` | Not seekable | Rewrite as inclusion where possible |

## Final Word

SQL optimizes automatically — but only if the query is written in a way the optimizer can reason about. The job is to write optimizer-friendly queries, provide the right indexes, and actually look at the plan.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Optimization Notes/Behaviours of SQL Engine and Tips|The SQL Engine: A Behavior Guide]]
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Optimization Notes/Role in SQL|Role in SQL]]

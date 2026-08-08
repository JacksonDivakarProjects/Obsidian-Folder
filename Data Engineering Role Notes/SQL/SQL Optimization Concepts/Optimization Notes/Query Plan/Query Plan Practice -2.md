# SQL Execution Plan Library (20 Real-World Examples)

A reference set of the execution-plan patterns that come up most often in practice: how to read each one, why the optimizer chose it, and how to act on it. Examples are PostgreSQL-flavored but the reasoning generalizes.

## Category 1: Index Access Strategies

### 1. Index Seek (best case)
```sql
SELECT * FROM users WHERE id = 500;
```
```
Index Scan using idx_users_id on users
  Index Cond: (id = 500)
```
Highly selective lookup, perfect index usage. Happens on equality filters against a primary/unique index. Keep it healthy by not wrapping the indexed column in a function.

### 2. Index Range Scan
```sql
SELECT * FROM orders WHERE amount BETWEEN 1000 AND 2000;
```
```
Index Range Scan on idx_orders_amount
  Index Cond: (amount >= 1000 AND amount <= 2000)
```
The index is walked across a key range instead of a single point. Keep the range column as the leading key of the index, and avoid expressions like `amount + 10 > 1000` that would defeat the seek.

### 3. Index Scan (full index walk)
```sql
SELECT * FROM users WHERE last_name LIKE '%son';
```
```
Index Scan using idx_last_name on users
  Filter: last_name ~~ '%son'
```
The leading `%` means the index can't be seeked to a starting point, so the engine walks the entire index checking the filter row by row. Fix: avoid leading wildcards, or use a trigram index (`pg_trgm` + GIN) if substring search is a real requirement.

### 4. Bitmap Index Scan (PostgreSQL)
```sql
SELECT * FROM employees WHERE dept_id = 3 AND salary > 60000;
```
```
BitmapAnd
   Bitmap Index Scan on idx_dept
   Bitmap Index Scan on idx_salary
Bitmap Heap Scan
```
Two indexes combined efficiently for a medium-selectivity compound filter. Usually already close to optimal; add a composite index only if this exact query is extremely frequent.

## Category 2: Table Access

### 5. Sequential Scan (full table scan)
```sql
SELECT * FROM logs WHERE message LIKE '%error%';
```
```
Seq Scan on logs
  Filter: message ~~ '%error%'
```
No index can serve a `%error%` predicate (wildcard on both sides), so the entire table is read. Fix: a full-text search index, or accept the scan if this runs rarely.

### 6. Index-Only Scan (covering index)
```sql
SELECT id, status FROM users WHERE status = 'ACTIVE';
```
```
Index Only Scan using idx_status on users
  Index Cond: (status = 'ACTIVE')
```
Every column the query needs is present in the index, so the table itself is never touched. Keep the index covering (include all needed columns), and — in PostgreSQL specifically — keep the table vacuumed, since an index-only scan still needs the visibility map to be up to date to skip heap fetches.

## Category 3: Join Strategies

### 7. Nested Loop Join (good: small → large)
```sql
SELECT * FROM orders o JOIN customers c ON c.id = o.customer_id;
```
```
Nested Loop
  -> Index Scan on orders
  -> Index Scan on customers
```
Small/selective outer side, indexed inner side — fast. Ensure join columns are indexed and that filtering keeps the outer row count small.

### 8. Nested Loop + Seq Scan (bad case)
```sql
SELECT * FROM orders o JOIN logs l ON o.customer_id = l.user_id;
```
```
Nested Loop
  -> Seq Scan on orders
  -> Seq Scan on logs
```
No index on the join columns — every outer row triggers a full scan of the inner table. Expensive at scale. Fix: index the join keys, which will let the optimizer switch to an indexed nested loop or a different strategy entirely.

### 9. Hash Join (large tables, equality join)
```sql
SELECT * FROM sales s JOIN products p ON p.id = s.product_id;
```
```
Hash Join
  Hash Cond: (s.product_id = p.id)
  -> Seq Scan sales
  -> Hash on products
```
Chosen for a large equality join with no requirement for sorted input. An index isn't strictly needed here. If a spill to disk shows up in the plan, increasing hash/work memory (or adding a selective index if the join is unusually frequent) helps.

### 10. Sort-Merge Join (requires sorted input)
```sql
SELECT * FROM s JOIN t ON s.id = t.id;
```
```
Merge Join
  Merge Cond: (s.id = t.id)
  -> Sort on s.id
  -> Sort on t.id
```
Both sides get sorted because no index provided that order already. Fix: index the join keys to remove the explicit sorts, and avoid an unnecessary later `ORDER BY` that would force a second sort.

## Category 4: Sorting & Aggregation

### 11. Sort (in-memory)
```sql
SELECT * FROM customers ORDER BY created_at;
```
```
Sort
  Sort Key: created_at
  -> Seq Scan on customers
```
Sorting happens in RAM here — fine for moderate row counts, but costly as the table grows. Fix: index `created_at` (removes the sort entirely if the plan can then just walk the index), or add a `LIMIT`.

### 12. Sort Spilling to Disk (bad)
```
Sort Method: external merge  Disk: 200MB
```
Not enough memory for the sort, so it spilled to disk — much slower. Fix: add a supporting index, raise the memory budget (`work_mem` in Postgres), or reduce the row count being sorted.

### 13. Hash Aggregate
```sql
SELECT dept_id, COUNT(*) FROM employees GROUP BY dept_id;
```
```
HashAggregate
  Group Key: dept_id
```
Groups rows via an in-memory hash table — fast as long as it fits in memory.

### 14. Sort (Group) Aggregate
```sql
SELECT dept_id, COUNT(*) FROM employees GROUP BY dept_id;
```
```
Sort
  Sort Key: dept_id
GroupAggregate
```
Sorts first, then aggregates while scanning in order — chosen when memory is too limited for a hash aggregate, or when the input is already sorted (e.g., via an index on `dept_id`), making the sort free.

## Category 5: Subquery / CTE Behavior

### 15. CTE Materialization (bad case, pre-PG12 default)
```sql
WITH r AS (SELECT * FROM orders WHERE status = 'PAID')
SELECT * FROM r WHERE amount > 100;
```
```
CTE Scan on r
  Filter: amount > 100
```
The CTE is fully computed and buffered before the outer filter runs, so `amount > 100` can't be pushed down into the base scan. Fix: use a subquery, or (PostgreSQL 12+) rely on automatic inlining / `WITH ... AS NOT MATERIALIZED`.

### 16. Inlined Subquery (optimal)
```sql
SELECT *
FROM (SELECT * FROM orders WHERE status = 'PAID') x
WHERE amount > 100;
```
```
Seq Scan on orders
  Filter: status = 'PAID' AND amount > 100
```
The optimizer pushed both filters down into a single scan — efficient, and what modern Postgres will also do automatically for an equivalent single-reference CTE.

### 17. `EXISTS` (efficient semi-join)
```sql
SELECT * FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);
```
```
Nested Loop Semi Join
  -> Index Scan on orders
```
A semi-join only needs to know whether a match exists, so it can stop scanning the inner side the moment it finds one row — cheaper than a regular join that would find every match.

### 18. `NOT EXISTS` (efficient anti-join)
```sql
SELECT * FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM blacklist b WHERE b.id = c.id);
```
```
Nested Loop Anti Join
  -> Index Scan on blacklist
```
An anti-join efficiently returns rows from the outer side that have *no* match on the inner side, and is generally preferred over `NOT IN` because it isn't tripped up by NULLs (see [[Data Engineering Role Notes/SQL/Other Keywords/SQL Exists and Not Exists|SQL EXISTS & NOT EXISTS]]).

## Category 6: Misc Optimizer Patterns

### 19. Predicate Pushdown
```sql
SELECT *
FROM (SELECT * FROM sales) s
WHERE amount > 100;
```
```
Seq Scan on sales
  Filter: amount > 100
```
The filter is pushed all the way into the base scan instead of being applied afterward — the efficient default for a simple wrapping subquery.

### 20. Cardinality Misestimate (dangerous)
```sql
SELECT * FROM orders WHERE status = 'ACTIVE';
```
```
Seq Scan (cost=1000..2000 rows=10)
```
...but the real row count turns out to be 500,000. Stale statistics led the optimizer to think this filter was highly selective, so it picked a plan suited to 10 rows instead of half a million. Fix:
```sql
ANALYZE orders;
```

## Summary

- SQL chooses plans based on cost, not on how the query happens to be written.
- Index seek, bitmap scan, and (selective) nested loop are generally good signs.
- Sort spills, unnecessary full scans, and CTE materialization on older Postgres are generally bad signs.
- The choice between hash, merge, and nested-loop join depends on data size, existing sort order, and indexes.
- Statistics drive almost every one of these decisions — stale statistics can invalidate a plan that would otherwise be correct.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Optimization Notes/Query Plan/Query Plan Practice|Query Plan Practice]]

# Query Plan Practice

Realistic `EXPLAIN` plans (simplified for clarity) with explanations of why the optimizer chose each one. Examples are PostgreSQL-flavored, but the underlying logic applies across MySQL, SQL Server, Oracle, Snowflake, and similar engines.

## Plan 1 — Index Seek + Nested Loop Join (Highly Selective Filter)

```sql
SELECT o.order_id, o.amount, c.customer_name
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.order_id = 120035;
```

```
Nested Loop
  -> Index Scan using idx_orders_order_id on orders
       Index Cond: (order_id = 120035)
  -> Index Scan using idx_customers_customer_id on customers
       Index Cond: (customer_id = o.customer_id)
```

**Why this plan:**
- The filter `order_id = 120035` is highly selective — it matches (at most) one row, so an index seek on `orders(order_id)` is optimal.
- With only ~1 outer row, a nested loop join is the fastest strategy: there's nothing to gain from building a hash table or sorting for just one probe.
- For each matching order, a second index seek finds the matching customer — also fast.

**What it tells you:** indexes are good, the optimizer found a highly selective path, and no sorting was needed. This is close to the best possible plan for a point lookup.

## Plan 2 — Hash Join + Sequential Scan (No Useful Indexes)

```sql
SELECT *
FROM orders o
JOIN customers c ON c.region = o.region;
```

```
Hash Join
  Hash Cond: (o.region = c.region)
  -> Seq Scan on orders
  -> Hash
       -> Seq Scan on customers
```

**Why this plan:**
- No index exists on `region`, so a join on it requires reading both full tables regardless of strategy.
- Given that, a hash join beats sort-merge because it avoids an explicit sort — it just builds a hash table on the smaller side (`customers`) and probes it with the larger (`orders`).

**What it tells you:** if this join runs frequently, an index on `region` might change the plan (e.g., to a nested loop over a small result), but a hash join here isn't inherently a problem — it's often already the right answer when there's no ordering to exploit.

## Plan 3 — Sort-Merge Join (Inputs Must Be Sorted)

```sql
SELECT *
FROM sales s
JOIN targets t ON s.product_id = t.product_id;
```

```
Merge Join
  Merge Cond: (s.product_id = t.product_id)
  -> Sort (sales)
       Sort Key: product_id
  -> Sort (targets)
       Sort Key: product_id
```

**Why this plan:**
- Merge join requires both inputs sorted on the join key — here neither has a supporting index, so the engine sorts both explicitly.
- Possible reasons the optimizer still chose merge over hash: it estimated many duplicate join keys (merge join handles duplicate-heavy joins predictably), or a later `ORDER BY` on the same key means the sort pays for itself twice.

**What it tells you:** you're paying for two explicit sorts. An index on `product_id` on either or both tables could eliminate them and likely shift the plan.

## Plan 4 — Bitmap Index Scan (PostgreSQL)

```sql
SELECT *
FROM employees
WHERE dept_id = 10
  AND salary > 50000;
```

```
Bitmap Heap Scan
  Recheck Cond: (dept_id = 10 AND salary > 50000)
  -> BitmapAnd
       -> Bitmap Index Scan on idx_dept
            Index Cond: (dept_id = 10)
       -> Bitmap Index Scan on idx_salary
            Index Cond: (salary > 50000)
```

**Why this plan:**
- Two separate single-column indexes exist (`dept_id`, `salary`); rather than pick just one and filter the rest by hand, Postgres builds a bitmap of matching row locations from each index and `AND`s them together.
- The combined bitmap is then used to fetch qualifying rows in physical block order, which minimizes random I/O compared to two independent index seeks.

**What it tells you:** the engine is efficiently combining multiple moderately-selective indexes. This is a normal, healthy plan for medium-selectivity multi-column filters — not a red flag.

## Plan 5 — Sort Spilling to Disk (Heavy Load)

```sql
SELECT *
FROM logs
ORDER BY created_at;
```

```
Sort
  Sort Key: created_at
  Sort Method: external merge  Disk: 150MB
  -> Seq Scan on logs
```

**Why this plan:** there's no index on `created_at`, so a full scan is unavoidable, and the in-memory sort attempt ran out of allotted memory and spilled to disk — much slower than an in-memory sort.

**Fix:**
```sql
CREATE INDEX idx_logs_created ON logs (created_at);
```
Or raise the sort memory budget (engine-specific: `work_mem` in PostgreSQL, `sort_buffer_size` in MySQL) if adding an index isn't practical.

## Plan 6 — CTE Materialization (Performance Trap)

```sql
WITH recent AS (
   SELECT * FROM orders WHERE order_date > NOW() - INTERVAL '30 days'
)
SELECT *
FROM recent
WHERE amount > 100;
```

```
CTE Scan on recent
   Filter: (amount > 100)
   -> Materialize
        -> Seq Scan on orders
             Filter: (order_date > ...)
```

**Why this plan:** on PostgreSQL versions before 12, a CTE was always materialized — computed fully in a temp buffer — before any outer filter (`amount > 100`) could be applied, so that filter couldn't be pushed down into the scan.

**Fix:** on Postgres 12+, this specific case is usually inlined automatically (the optimizer treats a single-reference, non-recursive CTE like a subquery unless told otherwise). To be explicit, or on older versions, rewrite as a subquery or force inlining:
```sql
SELECT *
FROM (
    SELECT *
    FROM orders
    WHERE order_date > NOW() - INTERVAL '30 days'
) recent
WHERE amount > 100;

-- or, PostgreSQL 12+:
WITH recent AS NOT MATERIALIZED ( ... )
```

## Summary

| Scenario | What the plan means | What to check/optimize |
|---|---|---|
| Index seek + nested loop | High selectivity | Indexing is working well |
| Hash join | No ordering / no indexes | Add an index only if this join is frequent |
| Merge join | Inputs had to be sorted | Index the join key(s) |
| Bitmap scan | Combining multiple indexes | Normal for medium-selectivity filters |
| Sort spill | Sort too big for memory | Add an index, or raise sort memory |
| CTE scan (materialized) | Materialization blocked push-down | Use a subquery or `NOT MATERIALIZED` |

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Optimization Notes/Query Plan/Query Plan Practice -2|SQL Execution Plan Library (20 Real-World Examples)]]

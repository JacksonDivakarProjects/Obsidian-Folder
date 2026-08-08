# Materialized Views – The Complete Guide (PostgreSQL)

## What is a Materialized View?

A **materialized view** is a precomputed snapshot of a query, stored physically like a table. It exists to avoid re-running an expensive query (heavy aggregation or join) every time the result is needed.

> Unlike a normal view, it does **not** reflect real-time data — it shows whatever the data looked like at the last refresh. You must explicitly `REFRESH` it to pick up changes.

## Creating, Dropping, and Refreshing

### Create

```sql
CREATE MATERIALIZED VIEW view_name AS
SELECT column1, column2, aggregate_function(column3)
FROM table_name
GROUP BY column1, column2;
```

### Drop

```sql
DROP MATERIALIZED VIEW view_name;
```

### Refresh

Materialized views must be refreshed manually (PostgreSQL has no built-in auto-refresh — scheduling one is left to you, e.g. via `pg_cron` or an external job).

```sql
REFRESH MATERIALIZED VIEW view_name;
```

By default, `REFRESH` takes an exclusive lock on the view, blocking reads while it rebuilds. To refresh without blocking concurrent `SELECT`s:

```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY view_name;
```

> `CONCURRENTLY` requires at least one **unique index** on the materialized view (so PostgreSQL can diff old vs. new rows instead of rebuilding from scratch).

**Screenshot — updating view constraints for `CONCURRENTLY` support:**

![[Data Engineering Role Notes/SQL/Materialized View/Updating View Constraints.png]]

## Worked Example

```sql
-- 1. Create the materialized view
CREATE MATERIALIZED VIEW department_sales_summary AS
SELECT department_id, SUM(sale_amount) AS total_sales
FROM sales
GROUP BY department_id;

-- 2. Query it like a table
SELECT * FROM department_sales_summary;

-- 3. Refresh it once the underlying `sales` data changes
REFRESH MATERIALIZED VIEW department_sales_summary;
```

## Read-Only Nature

Materialized views are read-only — you cannot `INSERT`, `UPDATE`, or `DELETE` against them directly. To change the data, update the base tables and refresh the view.

## Best Practices

| Practice | Reason |
|---|---|
| Use for costly aggregations or joins | Improves performance for complex, frequently-run queries |
| Schedule refresh during off-peak hours | Keeps view data current without impacting users |
| Use `CONCURRENTLY` if users are actively querying it | Avoids locking the view during refresh |
| Add a unique index on the view | Required for `CONCURRENTLY` refresh, and speeds up lookups |

## Interview-Ready Takeaways

- Materialized views store **precomputed** data — useful for reporting, analytics, and dashboards.
- Faster access for aggregated or joined data than re-computing on every query.
- PostgreSQL materialized views are **not** auto-refreshed — refresh is a manual (or externally scheduled) operation.
- Refresh with `REFRESH MATERIALIZED VIEW`; add `CONCURRENTLY` (with a unique index) to avoid blocking readers.
- Not updatable via `INSERT`/`UPDATE`/`DELETE`.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/Views in SQL/Views in SQL|SQL Views – The Complete Guide]]
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Basic SQL Optimizations|Basic SQL Optimizations]]

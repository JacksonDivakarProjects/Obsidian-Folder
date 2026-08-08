# SQL Views – The Complete Guide

## What Is a View?

A view is a virtual table created by storing a `SELECT` query under a name. It stores no data of its own — it re-runs the underlying query and shows live data from the base tables each time it's queried. Think of it as a saved query that behaves like a table.

## Creating, Replacing, and Dropping Views

**Create:**
```sql
CREATE VIEW view_name AS
SELECT column1, column2
FROM table_name
WHERE condition;
```

**Update the query behind a view without dropping it:**
```sql
CREATE OR REPLACE VIEW view_name AS
SELECT ...;
```

**Drop:**
```sql
DROP VIEW view_name;
```

## "Refreshing" a View

A plain view has nothing to refresh — since it's not materialized, it always pulls live data:

```sql
SELECT * FROM sales_summary_view;
```

This always reflects the current state of the underlying `sales` table. There's no `REFRESH` command for a plain view in any major engine, because there's nothing stored to refresh — that concept only applies to *materialized* views (see [[Data Engineering Role Notes/SQL/Materialized View/Materialized View In Postgres SQL|Materialized Views – The Complete Guide (PostgreSQL)]], which PostgreSQL and Oracle support and MySQL does not).

## Updating Data Through a View

Not every view is updatable — it must meet fairly strict conditions.

**A view is updatable only if it:**
- Is based on a single table.
- Doesn't use `DISTINCT`, `GROUP BY`, `UNION`, `JOIN`, or aggregate functions (`SUM`, `AVG`, etc.).
- Doesn't contain a subquery in the `SELECT` list, or derived/computed columns (e.g., `price * quantity`).

### Enforcing Conditions with `WITH CHECK OPTION`

Ensures every `INSERT`/`UPDATE` performed *through* the view must still satisfy its `WHERE` clause:

```sql
CREATE VIEW hr_employees AS
SELECT * FROM employees
WHERE department = 'HR'
WITH CHECK OPTION;
```

Without `WITH CHECK OPTION`, it's possible to `UPDATE` a row through the view in a way that makes it no longer match the view's filter (e.g., changing `department` away from `'HR'`) — the update succeeds, and the row simply disappears from future queries against the view. `WITH CHECK OPTION` rejects any write that would produce that outcome.

### Inserting Through a View (When Valid)

```sql
INSERT INTO hr_employees (id, name, department)
VALUES (5, 'Divakar', 'HR');
```

This inserts into the underlying `employees` table, because the new row satisfies the view's `WHERE` condition.

## Best Practices

| Practice | Reason |
|---|---|
| Name columns explicitly in `INSERT` | Safer if the underlying schema changes |
| Use `CREATE OR REPLACE VIEW` | Update a view's definition without dropping and recreating it |
| Grant least privilege via views | Hide sensitive columns from users who only need a subset |

## Interview-Ready Takeaways

- Views are virtual tables — no data of their own.
- They always show live data pulled from the base tables (no manual refresh needed, unlike a materialized view).
- Not every view is updatable — single-table, no aggregation/grouping/joins, no computed columns.
- `WITH CHECK OPTION` prevents writes through the view from producing rows the view itself wouldn't show.
- Useful for abstraction, access control, and reusing common query logic.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/Materialized View/Materialized View In Postgres SQL|Materialized Views – The Complete Guide (PostgreSQL)]]
- [[Data Engineering Role Notes/SQL/Triggers in SQL/Triggers in SQL|SQL Triggers — Comprehensive Beginner-Level Guide]]

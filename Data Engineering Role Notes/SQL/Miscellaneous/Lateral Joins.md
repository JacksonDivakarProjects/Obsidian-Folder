# `LATERAL` in SQL (PostgreSQL)

## 1. What It Is

`LATERAL` lets a subquery in the `FROM` clause reference columns from a table listed **earlier** in the same `FROM` clause. Conceptually: "for each row in the outer table, run this subquery using that row's values."

## 2. Basic Syntax

```sql
SELECT ...
FROM outer_table
JOIN LATERAL (
    SELECT ...
    WHERE sub.col = outer_table.col
) sub_alias ON true;
```

- The subquery must be given an alias.
- `ON true` is used when the correlation/filter is already expressed inside the subquery — there's nothing left for the join condition to check.

## 3. Why It's Needed

Without `LATERAL`, a subquery in `FROM` cannot see columns from a preceding table:

```sql
FROM customers c,
(
    SELECT * FROM orders WHERE orders.customer_id = c.id
) o
-- ❌ ERROR: column c.id does not exist (not visible to a plain subquery)
```

With `LATERAL`, the same subquery can reference `c.id`:

```sql
FROM customers c,
LATERAL (
    SELECT * FROM orders WHERE orders.customer_id = c.id
) o
```

## 4. Key Rules

| Rule | Explanation |
|---|---|
| Must alias the subquery | Required by SQL syntax |
| Must use `ON true` (with `JOIN LATERAL`) | Unless real join conditions are added |
| Evaluated per row | The subquery re-runs once for each row of the preceding table(s) |
| Needs `LATERAL` to see outer columns | A plain (non-lateral) subquery in `FROM` cannot reference sibling tables |

## 5. When to Use It

- The subquery needs values from an outer table in the same `FROM` clause.
- You need `ORDER BY` + `LIMIT` inside the subquery (e.g., "top N per group").
- You want row-by-row filtering that can't be expressed as a simple join condition.

## 6. Example: Latest Order per Customer

```sql
SELECT c.id, o.id
FROM customers c
JOIN LATERAL (
  SELECT *
  FROM orders o
  WHERE o.customer_id = c.id
  ORDER BY o.created_at DESC
  LIMIT 1
) o ON true;
```

This returns each customer's most recent order — a "top-1 per group" query that's awkward to express any other way in standard SQL.

## TL;DR

`LATERAL` = a subquery in `FROM` that can see the outer table's columns, and that runs once per outer row. It's the standard tool for **top-N per group**, unnesting array/JSON columns per row, and other row-wise, dynamic filtering that a plain join can't express.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL SubQueries/SQL SubQueries|Comprehensive Guide to SQL Subqueries]]
- [[Data Engineering Role Notes/SQL/Window Functions/SQL Window Function - 2|Comprehensive Guide to SQL Window Functions]]

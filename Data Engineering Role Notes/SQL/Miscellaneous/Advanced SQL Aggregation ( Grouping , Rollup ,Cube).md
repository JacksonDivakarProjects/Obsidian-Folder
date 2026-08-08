# Advanced SQL Aggregation: GROUPING SETS, ROLLUP, CUBE

## Why These Exist

A single `GROUP BY` gives one level of grouping. Reports and dashboards often need several at once — subtotals, a grand total, and multiple grouping combinations — without running separate queries and `UNION`-ing them together. `GROUPING SETS`, `ROLLUP`, and `CUBE` all solve that in one query.

## 1. `GROUPING SETS`

Lets you specify the exact group combinations to aggregate.

```sql
SELECT col1, col2, SUM(val)
FROM table
GROUP BY GROUPING SETS (
    (col1, col2),
    (col1),
    ()
);
```

Example:

```sql
SELECT city, customer_name, SUM(amount)
FROM uber_rides
GROUP BY GROUPING SETS (
    (city, customer_name),   -- detail row
    (city),                  -- subtotal per city
    ()                        -- grand total
);
```

Output:

| city | customer_name | sum |
|---|---|---|
| Chennai | Ram | 500 |
| Chennai | John | 450 |
| Chennai | NULL | 950 ← subtotal |
| NULL | NULL | 2350 ← grand total |

## 2. `ROLLUP`

A shortcut for hierarchical, top-down subtotals — it's the specific `GROUPING SETS` pattern for a strict hierarchy of columns.

```sql
SELECT col1, col2, SUM(val)
FROM table
GROUP BY ROLLUP (col1, col2);
```

Equivalent to:

```sql
GROUP BY GROUPING SETS (
    (col1, col2),
    (col1),
    ()
);
```

Example:

```sql
SELECT city, customer_name, SUM(amount)
FROM uber_rides
GROUP BY ROLLUP (city, customer_name);
```

Same output as the `GROUPING SETS` example above, but the hierarchy is generated automatically instead of listed by hand.

## 3. `CUBE`

Generates **every** combination of the grouping columns — a full cross-tab.

```sql
SELECT col1, col2, SUM(val)
FROM table
GROUP BY CUBE (col1, col2);
```

Equivalent to:

```sql
GROUP BY GROUPING SETS (
    (col1, col2),
    (col1),
    (col2),
    ()
);
```

Example:

```sql
SELECT city, customer_name, SUM(amount)
FROM uber_rides
GROUP BY CUBE (city, customer_name);
```

Output:

| city | customer_name | sum |
|---|---|---|
| Chennai | Ram | 500 |
| Chennai | NULL | 950 |
| NULL | Ram | 600 |
| NULL | NULL | 2350 |

## Bonus: the `GROUPING()` Function

`GROUPING(col)` returns `1` when `col` has been "rolled up" into a subtotal/total row for that combination, and `0` when it holds a real value. Use it to detect and label subtotal rows:

```sql
SELECT
  city, customer_name, SUM(amount),
  GROUPING(city)          AS is_city_total,
  GROUPING(customer_name) AS is_customer_total
FROM uber_rides
GROUP BY CUBE (city, customer_name);
```

Turn the flags into a readable label:

```sql
CASE
  WHEN GROUPING(city) = 1 AND GROUPING(customer_name) = 1 THEN 'Grand Total'
  WHEN GROUPING(customer_name) = 1 THEN 'Subtotal per City'
  WHEN GROUPING(city) = 1 THEN 'Subtotal per Customer'
  ELSE 'Detail'
END AS row_type
```

## Summary

| Feature | What it does | Use when |
|---|---|---|
| `GROUPING SETS` | Manual control of group combinations | You want specific, custom subtotal logic |
| `ROLLUP` | Hierarchical totals (top-down) | Reports with a subtotal → total flow |
| `CUBE` | All combinations (cross-tab style) | Multidimensional analysis |

## Pro Tips

- All three work with `GROUPING()` to filter or label totals.
- `ORDER BY GROUPING(col)` sorts detail rows before totals (since `GROUPING()` returns 0 for detail, 1 for rolled-up).
- Wrap the query in a CTE or subquery if you need to filter out (or isolate) totals with a `WHERE`/`HAVING` afterward — you can't filter on `GROUPING()` directly in the same query's `WHERE` clause.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/Tricks and Tips/Group By and Having Tricks|Group By and Having Tricks]]
- [[Data Engineering Role Notes/SQL/Window Functions/SQL Window Functions and Aggregate Examples|SQL Window Functions and Aggregate Examples]]

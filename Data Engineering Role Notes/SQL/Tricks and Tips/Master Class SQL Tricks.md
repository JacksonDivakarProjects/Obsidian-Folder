# SQL Masterclass – Comprehensive Revision Guide

High-impact SQL techniques and behaviors worth having memorized before an interview or a real-world debugging session.

## 1. Conditional Aggregation with `CASE WHEN`

Apply conditional logic inside an aggregate to compute a metric only for qualifying rows.

```sql
-- Count only employees with salary < 30000
SELECT
  department,
  COUNT(CASE WHEN salary < 30000 THEN 1 ELSE NULL END) AS low_salary_count,
  SUM(CASE WHEN dept = 'HR' THEN bonus ELSE 0 END) AS hr_bonus_total
FROM employees
GROUP BY department;
```

Key points:
- `CASE WHEN condition THEN value ELSE NULL END` makes non-matching rows evaluate to `NULL`, which `COUNT()` ignores.
- Avoid `ELSE 0` inside `COUNT()` specifically — `COUNT()` counts non-NULL values, so an `ELSE 0` would count every row, defeating the conditional filter. (`ELSE 0` is fine, and often correct, inside `SUM()`.)

## 2. `COUNT()` Behaviors

| Usage | Description |
|---|---|
| `COUNT(*)` | Counts all rows, including ones where every column is `NULL` |
| `COUNT(column)` | Counts only non-`NULL` values in that column |
| `COUNT(1)` or `COUNT(0)` | Counts all rows — a constant is never `NULL` |

```sql
SELECT
  COUNT(*)      AS total_rows,
  COUNT(salary) AS salary_not_null,
  COUNT(1)      AS constant_count
FROM employees;
```

Use `COUNT(*)` for a total row count; use `COUNT(column)` specifically when you want NULLs excluded.

## 3. `DISTINCT` Inside Aggregates

```sql
-- Count unique departments
SELECT COUNT(DISTINCT department_id) AS unique_depts
FROM employees;

-- Sum of unique salary values (not the sum of all salaries!)
SELECT SUM(DISTINCT salary) AS total_unique_payroll
FROM employees;

-- Exclude NULLs explicitly inside DISTINCT
SELECT COUNT(DISTINCT CASE WHEN department_id IS NOT NULL THEN department_id END) AS unique_depts_non_null
FROM employees;
```

Use this for deduplicated analytics metrics: unique users, unique categories, distinct transaction types. Note `SUM(DISTINCT ...)` sums each *distinct value* once — if two employees happen to earn the exact same salary, that salary is only added once, which is rarely what you actually want for a payroll total.

## 4. NULL Handling in Joins & Filters

**Joins:**
```sql
-- LEFT JOIN returns all left rows; unmatched right-side columns come back NULL
SELECT e.*, d.department_name
FROM employees e
LEFT JOIN departments d
  ON e.department_id = d.id;
```

**Filtering NULLs:**
```sql
SELECT * FROM orders WHERE shipped_date IS NULL;   -- correct

-- Never write this — it never matches, even for NULL rows:
WHERE shipped_date = NULL;
```

Always use `IS NULL` / `IS NOT NULL` — `NULL` isn't a value that `=` can compare against.

## 5. Subquery Rules & Aliasing

**Derived tables in `FROM` require an alias:**
```sql
SELECT t.*
FROM (
  SELECT * FROM orders WHERE status = 'pending'
) AS t;
```

**`WHERE` subqueries don't need an alias:**
```sql
SELECT name
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);
```

**Correlated subqueries can reference the outer query's alias:**
```sql
SELECT
  customer_id,
  COUNT(CASE
    WHEN order_date = preferred_date
     AND order_date = (
        SELECT MIN(order_date)
        FROM Delivery
        WHERE customer_id = d.customer_id
      )
    THEN 1 ELSE NULL END
  ) AS immediate_orders
FROM Delivery AS d
GROUP BY customer_id;
```
This enables row-by-row logic where the inner query's condition depends on the current outer row.

## 6. Window Function vs. `GROUP BY` + `JOIN`

**Window function version** (PostgreSQL, SQL Server, MySQL 8+):
```sql
SELECT
  e.*,
  MAX(salary) OVER (PARTITION BY department) AS dept_max_salary
FROM employees e;
```

**Equivalent using `GROUP BY` + `JOIN`:**
```sql
SELECT e.*, gm.max_salary
FROM employees AS e
JOIN (
  SELECT department, MAX(salary) AS max_salary
  FROM employees
  GROUP BY department
) AS gm
  ON e.department = gm.department;
```

The window-function version is more concise and, on modern engines, at least as fast; the `GROUP BY` + `JOIN` version is the portable fallback for engines without window function support (e.g., MySQL before 8.0).

## 7. Joining Two Preprocessed Subqueries

```sql
SELECT t.student_name, t.class_name
FROM (
  SELECT
    s.name AS student_name,
    c.class_name
  FROM (
    SELECT * FROM students WHERE name IS NOT NULL
  ) AS s
  JOIN (
    SELECT id AS class_id, class_name
    FROM classes
    WHERE class_name LIKE 'C%'
  ) AS c
    ON s.class_id = c.class_id
) AS t;
```
Filtering, renaming, or transforming both sides *before* joining keeps complex ETL/reporting queries modular and easier to read — each subquery has one clear job.

## 8. String Functions & Encoding Nuances

- `LENGTH(str)` returns the **byte** length — multi-byte characters count as more than 1.
- `CHAR_LENGTH(str)` returns the **character** count, which is usually what you actually want for user-facing text.
- `SUBSTRING(str, start, [length])` extracts a substring; `length` is optional, and indexing starts at 1 (not 0).

```sql
SELECT
  LENGTH(name) AS byte_len,
  CHAR_LENGTH(name) AS char_len,
  SUBSTRING(name, 2, 3) AS mid_str
FROM employees;
```

## 9. Scalar Subqueries with `LIMIT 1`

```sql
SELECT
  (SELECT salary FROM employees WHERE id = 100 LIMIT 1) AS salary_value;
```
Returns the value if a row matches, or `NULL` if none does — a safe way to fetch a single metric without risking a "subquery returned more than one row" error.

## 10. The `LEFT JOIN ... ON 1=1` Trick

```sql
-- Force a guaranteed result-set shape via a dummy single-row table
SELECT s.*
FROM (SELECT 1) AS dummy
LEFT JOIN sales AS s ON 1=1;
```
Returns every row of `sales`, useful when you need to guarantee at least one output row even if `sales` could be empty (e.g., as the base of a report that must render something regardless). Combine with a `CASE`-guarded `DISTINCT` to keep unwanted `NULL`s out of a count:
```sql
COUNT(DISTINCT CASE WHEN col IS NOT NULL THEN col END)
```

## 11. Window Functions: Running Totals, Rank, Dense Rank

```sql
-- Cumulative sum
SELECT
  date,
  sales,
  SUM(sales) OVER (ORDER BY date) AS cumulative_sales
FROM daily_sales;

-- Ranking
SELECT
  name,
  score,
  RANK() OVER (ORDER BY score DESC)       AS rank_position,
  DENSE_RANK() OVER (ORDER BY score DESC) AS dense_rank_position
FROM player_scores;
```

- `SUM(...) OVER (ORDER BY ...)` computes a running total.
- `RANK()` and `DENSE_RANK()` take their ordering entirely from the `OVER (ORDER BY ...)` clause — you never pass a column name into the function itself.

## Best Practices

1. Always alias derived tables and correlated subqueries clearly.
2. Use `ELSE NULL` (not `ELSE 0`) inside `CASE` when the result feeds a `COUNT()`.
3. Prefer window functions when the engine supports them; fall back to `GROUP BY` + `JOIN` otherwise.
4. Deliberately check `NULL` behavior in every aggregate and join — it's the single most common source of silently wrong results.
5. Keep queries modular: preprocess in subqueries/CTEs, then join.
6. Convert deeply nested queries into CTEs for readability:

```sql
WITH latest_delivery AS (
  SELECT customer_id, MIN(order_date) AS first_date
  FROM Delivery
  GROUP BY customer_id
), immediate_orders AS (
  SELECT d.customer_id
  FROM Delivery d
  JOIN latest_delivery ld ON d.customer_id = ld.customer_id
  WHERE d.order_date = ld.first_date
    AND d.order_date = d.preferred_date
)
SELECT COUNT(*) AS immediate_count
FROM immediate_orders;
```

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/Tricks and Tips/Master Class SQL Tricks Part -2|SQL Tricks — Counting Distinct Days and Grouping Granularity]]
- [[Data Engineering Role Notes/SQL/Tricks and Tips/Group By and Having Tricks|Group By and Having Tricks]]

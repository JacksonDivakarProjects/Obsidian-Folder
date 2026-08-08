# Comprehensive Guide to SQL Subqueries

## What Is a Subquery?

A subquery is a query nested inside another SQL statement, used to return a result the outer query depends on. Used well, subqueries add flexibility, reduce duplication, and let logic be reused inline.

## Types of Subqueries

### 1. Scalar Subquery

Returns a single value (one row, one column). Used in `SELECT`, `WHERE`, `HAVING`.

```sql
SELECT
    employee_id,
    salary,
    (SELECT AVG(salary) FROM employees) AS avg_salary
FROM employees;
```

Common in comparisons:
```sql
WHERE salary > (SELECT AVG(salary) FROM employees)
```

### 2. Column Subquery (Single Row, Multiple Columns)

```sql
SELECT *
FROM employees
WHERE (department_id, job_id) = (
    SELECT department_id, job_id
    FROM employees
    WHERE employee_id = 1001
);
```

Useful for comparing multiple fields at once.

### 3. Row Subquery (Multiple Rows, Single Column)

```sql
SELECT name
FROM students
WHERE class_id IN (
    SELECT class_id
    FROM classes
    WHERE teacher = 'Jack'
);
```

`IN`, `ANY`, `ALL`, `EXISTS` are the tools for this shape.

### 4. Table Subquery (in `FROM`)

A subquery that acts like a derived table — must be aliased (`AS recent_employees`), which SQL requires.

```sql
SELECT dept_no, AVG(salary)
FROM (
    SELECT dept_no, salary
    FROM employees
    WHERE join_year >= 2020
) AS recent_employees
GROUP BY dept_no;
```

### 5. Correlated Subquery

References columns from the outer query, so it's re-evaluated once per outer row — potentially expensive on large tables.

```sql
SELECT e1.name
FROM employees e1
WHERE salary > (
    SELECT AVG(salary)
    FROM employees e2
    WHERE e1.department_id = e2.department_id
);
```

### 6. `EXISTS` Subquery

Checks only whether any rows exist — not their values.

```sql
SELECT customer_id
FROM customers c
WHERE EXISTS (
    SELECT 1
    FROM orders o
    WHERE o.customer_id = c.customer_id
);
```

Use `EXISTS` when only existence matters, not the actual returned values.

## Comparison Operators with Subqueries

| Operator | Use Case | Example |
|---|---|---|
| `IN` | Match against a list of values | `WHERE city IN (SELECT city FROM branches)` |
| `=` | Scalar match | `WHERE salary = (SELECT MAX(salary) FROM employees)` |
| `EXISTS` | Logical presence check | `WHERE EXISTS (SELECT 1 FROM orders WHERE ...)` |
| `ANY` | True if it holds against at least one value | `WHERE salary > ANY (SELECT salary FROM interns)` |
| `ALL` | True if it holds against every value | `WHERE salary > ALL (SELECT salary FROM interns)` |

(See [[Data Engineering Role Notes/SQL/Other Keywords/ALL, ANY, LIKE Keywords|SQL Keywords Quick Reference: ALL, ANY, LIKE]] for a deeper dive on `ANY`/`ALL`.)

## Subqueries by Clause

| Clause | Purpose | Example |
|---|---|---|
| `SELECT` | Add a derived value (count, average, ranking) | `(SELECT COUNT(*) FROM ...) AS total_orders` |
| `FROM` | Use the subquery as a temporary table | `FROM (SELECT ...) AS temp` |
| `WHERE` | Filter rows against a dynamic condition | `WHERE salary > (SELECT AVG(...))` |
| `HAVING` | Filter aggregated groups against a condition | `HAVING SUM(...) > (SELECT ...)` |

## Performance Notes

| Technique | Cost/performance impact |
|---|---|
| Scalar subquery | Fast, if it truly returns a single value |
| Table subquery | Fine, but benefits from indexing on the underlying tables |
| Correlated subquery | Can be costly on large datasets — runs once per outer row |
| `EXISTS` vs. `IN` | `EXISTS` tends to be faster for large subqueries, and handles NULLs more safely than `NOT IN` |
| CTEs vs. subqueries | Prefer a CTE when the same logic is reused, for readability |

## Best Practices

- Always alias a subquery, especially in `FROM` — SQL requires it there.
- Use a CTE (`WITH`) when the subquery logic is reused more than once.
- Prefer `EXISTS` over `IN` for large subqueries.
- Avoid correlated subqueries unless the logic genuinely requires per-row correlation.
- Consider rewriting a scalar/correlated subquery as a `JOIN` where that's equivalent and clearer — modern optimizers often produce the same plan either way, but a `JOIN` is frequently easier to read.

## Summary

| Subquery type | Returns | Used in | Good for |
|---|---|---|---|
| Scalar | 1 row, 1 column | `SELECT`, `WHERE`, etc. | Single-value comparisons |
| Row (single column) | Multiple rows | `IN`, `ANY`, `ALL` | Value-list membership |
| Column (multi-column) | One row, multiple columns | `WHERE`, composite comparisons | Multi-column matching |
| Table | A whole result set | `FROM` | Derived tables for further aggregation |
| Correlated | Varies | `WHERE`, `SELECT` | Row-wise filtering logic |
| `EXISTS` | TRUE/FALSE | `WHERE` | Existence checks |

## Going Further

- Practice rewriting subqueries as `JOIN`s and comparing the resulting execution plans.
- Explore window functions (see [[Data Engineering Role Notes/SQL/Window Functions/Window Functions|Window Functions]]) as an alternative to certain correlated-subquery patterns (e.g., "top N per group").
- Practice combining CTE + subquery + JOIN together, since interview questions often blend all three.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/Miscellaneous/Lateral Joins|LATERAL in SQL (PostgreSQL)]]
- [[Data Engineering Role Notes/SQL/Other Keywords/SQL Exists and Not Exists|SQL EXISTS & NOT EXISTS: Quick Revision Guide]]
- [[Data Engineering Role Notes/SQL/Other Keywords/ALL, ANY, LIKE Keywords|SQL Keywords Quick Reference: ALL, ANY, LIKE]]
- [[Data Engineering Role Notes/SQL/Set Operation in SQL/Set Operations in SQL|Comprehensive Guide to Set Operations in SQL]]

# Group By + Window Functions, and Having + Conditional Aggregation

Reusable patterns for combining aggregation with window functions, and for filtering on aggregated conditions — the kind of query shape that comes up constantly in interviews and real analytics work.

## Part 1: GROUP BY + Window Functions

### Core Insight

- `GROUP BY` **reduces** rows — it collapses the result set.
- Window functions **do not** reduce rows — they annotate rows (the already-grouped result, or the raw result) with an extra computed value.
- The rule of thumb: **aggregate first, then apply the window function** on top of the aggregated result.

### Execution Order (Important)

```
FROM → WHERE → GROUP BY → aggregate functions → window functions → SELECT list → ORDER BY → LIMIT
```

Practical consequence: you cannot use a window function inside `WHERE` or `GROUP BY` (they haven't been computed yet at that stage) — but you can use one in `SELECT`, `HAVING` (in engines that allow it), or `ORDER BY`.

### Pattern 1: Ranking Aggregated Results

Rank departments by total salary:
```sql
SELECT
    department_id,
    SUM(salary) AS total_salary,
    RANK() OVER (ORDER BY SUM(salary) DESC) AS dept_rank
FROM employee
GROUP BY department_id;
```
Aggregate first, then rank the aggregated rows.

### Pattern 2: Top-N Groups

Return the top 3 departments by revenue:
```sql
SELECT *
FROM (
    SELECT
        department_id,
        SUM(revenue) AS total_revenue,
        RANK() OVER (ORDER BY SUM(revenue) DESC) AS rnk
    FROM department_sales
    GROUP BY department_id
) t
WHERE rnk <= 3;
```
Pattern: `GROUP BY → window RANK → filter on the rank in an outer query` (you can't filter on the window function's own alias in the same `SELECT`'s `WHERE`, so it has to move to an outer query or a `QUALIFY`-supporting engine).

### Pattern 3: Running Totals Over Aggregated Output

Cumulative department salary, ordered by salary:
```sql
SELECT
    department_id,
    SUM(salary) AS total_salary,
    SUM(SUM(salary)) OVER (ORDER BY SUM(salary)) AS running_total
FROM employee
GROUP BY department_id;
```
`SUM(SUM(salary)) OVER (...)` reads as: sum salary per department first, then compute a running total across those per-department sums.

### Pattern 4: Percent Contribution

Each department's share of total payroll:
```sql
SELECT
    department_id,
    SUM(salary) AS dept_salary,
    SUM(salary) * 100.0 / SUM(SUM(salary)) OVER () AS pct_share
FROM employee
GROUP BY department_id;
```
A staple of BI dashboards — "percent of total" metrics.

### Pattern 5: Window Functions Without Grouping

Compare each employee's salary to their department's average, without collapsing any rows:
```sql
SELECT
    name,
    department_id,
    salary,
    AVG(salary) OVER (PARTITION BY department_id) AS dept_avg,
    salary - AVG(salary) OVER (PARTITION BY department_id) AS difference
FROM employee;
```
Unlike `GROUP BY`, this keeps every row — `PARTITION BY` only changes which rows the average is computed over, not how many rows come out.

## Part 2: HAVING + Conditional Aggregation

### Core Insight

- `WHERE` filters rows **before** grouping — aggregate functions aren't available there yet.
- `HAVING` filters groups **after** aggregation — this is where aggregate-based conditions belong.

### Pattern 1: Count-Based Conditions

Customers with more than 3 orders:
```sql
SELECT customer_id, COUNT(*) AS order_count
FROM orders
GROUP BY customer_id
HAVING COUNT(*) > 3;
```

### Pattern 2: Conditional Counting

Users with more cancelled than delivered orders:
```sql
SELECT
    user_id,
    SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_cnt,
    SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_cnt
FROM orders
GROUP BY user_id
HAVING SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END)
     > SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END);
```

### Pattern 3: Ratio / Percentage Conditions

Stores with a return rate above 20%:
```sql
SELECT
    store_id,
    SUM(CASE WHEN event = 'Return' THEN 1 END) * 1.0 / COUNT(*) AS return_rate
FROM sales
GROUP BY store_id
HAVING SUM(CASE WHEN event = 'Return' THEN 1 END) * 1.0 / COUNT(*) > 0.20;
```

### Pattern 4: Category Dominance

Products sold more online than in-store:
```sql
SELECT
    product_id,
    SUM(CASE WHEN channel = 'Online' THEN quantity ELSE 0 END) AS online_qty,
    SUM(CASE WHEN channel = 'Store' THEN quantity ELSE 0 END) AS store_qty
FROM sales
GROUP BY product_id
HAVING SUM(CASE WHEN channel = 'Online' THEN quantity ELSE 0 END)
     > SUM(CASE WHEN channel = 'Store' THEN quantity ELSE 0 END);
```

## Common Mistakes

| Mistake | Correction |
|---|---|
| Using an aggregate in `WHERE` | Move the condition to `HAVING` |
| Using a window function inside `GROUP BY` | Only use it in `SELECT` or `ORDER BY` |
| Comparing to `NULL` with `=`/`!=` | Use `IS NULL` / `IS NOT NULL` |

## Performance Guidance

| Technique | Why |
|---|---|
| Aggregate before applying a window function | Reduces the row count the window function has to process |
| Prefer `col BETWEEN date1 AND date2` over `EXTRACT(YEAR FROM col) = ...` | The range form can use an index on `col`; wrapping it in a function usually can't |
| Avoid `HAVING` without a `GROUP BY` | Rarely meaningful — usually a sign the query shape is off |
| Index columns used in `PARTITION BY`/`ORDER BY` | Helps the engine avoid an explicit sort before the window function runs |

## Memory Aid

```
WHERE    → filters raw rows
GROUP BY → collapses rows into groups
HAVING   → filters on aggregated (grouped) values
WINDOW   → annotates rows with a computed value, without removing any
```

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/Miscellaneous/Advanced SQL Aggregation ( Grouping , Rollup ,Cube)|Advanced SQL Aggregation (GROUPING SETS, ROLLUP, CUBE)]]
- [[Data Engineering Role Notes/SQL/Tricks and Tips/Master Class SQL Tricks|SQL Masterclass – Comprehensive Revision Guide]]

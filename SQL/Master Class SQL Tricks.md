**SQL Masterclass – Comprehensive Revision Guide (Edition 2)**

This masterclass note consolidates all high‑impact SQL techniques, behaviors, and best practices you’ve mastered. Use this as your long‑term revision reference before interviews or real‑world problem solving.

---

## 1. Conditional Aggregation with `CASE WHEN`

**Purpose:** Apply conditional logic inside aggregates to compute metrics only for qualifying rows.

```sql
-- Count only employees with salary < 30000
SELECT
  department,
  COUNT(CASE WHEN salary < 30000 THEN 1 ELSE NULL END) AS low_salary_count,
  SUM(CASE WHEN dept = 'HR' THEN bonus ELSE 0 END) AS hr_bonus_total
FROM employees
GROUP BY department;
```

**Key Points:**

- `CASE WHEN condition THEN value ELSE NULL END` ensures non‑matching rows yield `NULL`, which `COUNT()` ignores.
    
- Avoid `ELSE 0` in `COUNT()` to prevent counting undesired rows.
    

---

## 2. Deep Dive: `COUNT()` Behaviors

|Usage|Description|
|---|---|
|`COUNT(*)`|Counts all rows, including those with `NULL` columns.|
|`COUNT(column)`|Counts non‑`NULL` values in that column.|
|`COUNT(1)` or `COUNT(0)`|Counts all rows (constants never `NULL`).|

```sql
-- Compare counts
SELECT
  COUNT(*)      AS total_rows,
  COUNT(salary) AS salary_not_null,
  COUNT(1)      AS constant_count
FROM employees;
```

**Tip:** Use `COUNT(*)` for total rows; use `COUNT(column)` when you want to ignore `NULL` values.

---

## 3. Using `DISTINCT` Inside Aggregates

**Syntax Examples:**

```sql
-- Count unique departments
SELECT COUNT(DISTINCT department_id) AS unique_depts
FROM employees;

-- Sum of unique salaries
SELECT SUM(DISTINCT salary) AS total_unique_payroll
FROM employees;

-- Exclude NULLs explicitly inside DISTINCT
SELECT COUNT(DISTINCT CASE WHEN department_id IS NOT NULL THEN department_id END) AS unique_depts_non_null
FROM employees;
```

**When to use:**

- Deduplicating values in analytics: unique users, unique categories, distinct transaction types.
    

---

## 4. NULL Handling in Joins & Filters

### a) Joins

```sql
-- Left join returns all left rows; unmatched right columns are NULL
SELECT e.*, d.department_name
FROM employees e
LEFT JOIN departments d
  ON e.department_id = d.id;
```

### b) Filtering NULLs

```sql
SELECT *
FROM orders
WHERE shipped_date IS NULL;   -- Correct

-- Never use:
WHERE shipped_date = NULL;    -- Incorrect
```

**Insight:** Always use `IS NULL` / `IS NOT NULL` when testing for `NULL` values.

---

## 5. Subquery Rules & Aliasing

### a) Derived Tables in `FROM` Require Aliases

```sql
-- Correct
SELECT t.*
FROM (
  SELECT *
  FROM orders
  WHERE status = 'pending'
) AS t;
```

### b) `WHERE` Subqueries Don't Require Aliases

```sql
SELECT name
FROM employees
WHERE salary > (
  SELECT AVG(salary) FROM employees
);
```

### c) Correlated Subqueries Can Reference Outer Aliases

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

**Benefit:** Enables row‑by‑row logic where inner query conditions depend on the outer row context.

---

## 6. Window Function Alternatives with `GROUP BY` + `JOIN`

### a) Window Version (MySQL 8+, PostgreSQL, SQL Server)

```sql
SELECT
  e.*,
  MAX(salary) OVER (PARTITION BY department) AS dept_max_salary
FROM employees e;
```

### b) Equivalent `GROUP BY` + `JOIN`

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

**Comparison:**

- Window functions are more concise and performant in modern engines.
    
- `GROUP BY` + `JOIN` works universally, including older MySQL versions.
    

---

## 7. Join Between Two Subqueries (Preprocessing Both Sides)

```sql
SELECT t.student_name, t.class_name
FROM (
  SELECT
    s.name AS student_name,
    c.class_name
  FROM (
    SELECT *
    FROM students
    WHERE name IS NOT NULL
  ) AS s
  JOIN (
    SELECT id AS class_id, class_name
    FROM classes
    WHERE class_name LIKE 'C%'
  ) AS c
    ON s.class_id = c.class_id
) AS t;
```

**Use Case:**

- Filter, rename, or transform data on both tables before joining.
    
- Improves modularity and readability in complex ETL or reporting queries.
    

---

## 8. String Functions & Encoding Nuances

- `LENGTH(str)` → Returns byte length (multi‑byte chars count >1).
    
- `CHAR_LENGTH(str)` → Returns character count.
    
- `SUBSTRING(str, start, [length])` → Extracts substring; `length` optional; indexing starts at 1.
    

```sql
SELECT
  LENGTH(name) AS byte_len,
  CHAR_LENGTH(name) AS char_len,
  SUBSTRING(name, 2, 3) AS mid_str
FROM employees;
```

---

## 9. Scalar Subqueries with `LIMIT 1`

**Syntax:**

```sql
SELECT
  (SELECT salary FROM employees WHERE id = 100 LIMIT 1) AS salary_value;
```

- Returns the **value** if present; returns **NULL** if no row matches.
    
- Handy for fetching a single metric without errors when no data exists.
    

---

## 10. Single-row Join Trick & `LEFT JOIN ON 1=1`

```sql
-- Force inclusion of all rows via dummy single-row table
SELECT s.*
FROM (SELECT 1) AS dummy
LEFT JOIN sales AS s ON 1=1;
```

- Returns all `sales` rows; helps when you need a guaranteed result set structure.
    
- Combine with `CASE WHEN` in `DISTINCT` to remove unwanted `NULL`s:
    
    ```sql
    COUNT(DISTINCT CASE WHEN col IS NOT NULL THEN col END)
    ```
    

---

## 11. Advanced Window Functions: CUMSUM, RANK, DENSE_RANK

```sql
-- Cumulative Sum
SELECT
  date,
  sales,
  SUM(sales) OVER (ORDER BY date) AS cumulative_sales
FROM daily_sales;

-- Ranking
SELECT
  name,
  score,
  RANK() OVER (ORDER BY score DESC)     AS rank_position,
  DENSE_RANK() OVER (ORDER BY score DESC) AS dense_rank_position
FROM player_scores;
```

**Key Points:**

- `SUM() OVER (ORDER BY ...)` computes running totals.
    
- `RANK()` and `DENSE_RANK()` derive their ordering from the `OVER (ORDER BY ...)` clause; you **don’t** pass the column name inside the function.
    

---

### 🏆 Masterclass Best Practices

1. **Always alias** derived tables and correlated subqueries clearly.
    
2. Use `ELSE NULL` in `CASE` for correct conditional counts.
    
3. Prefer window functions when available; fallback to `GROUP BY` + `JOIN`.
    
4. Validate `NULL` behavior in your aggregates and joins.
    
5. Keep queries modular: preprocess heavy logic in subqueries, then join.
    
6. Document your syntax patterns in a personal cheat sheet for quick recall.
    

---

> **Tip:** Convert complex nested queries into **Common Table Expressions (CTEs)** for readability:

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

Keep this masterclass guide handy and update it as you learn new techniques or encounter edge cases. Good luck with your SQL mastery and interviews!
# SQL Window Functions and Aggregate Examples

Examples using a sample `employees` table with columns `emp_id`, `department`, and `salary`.

## 1. `ROW_NUMBER()`

Assigns a unique sequential integer to rows within a partition, in a specified order.

```sql
SELECT
    emp_id,
    department,
    salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS row_num
FROM employees;
```

For each `department`, rows are ordered by `salary` descending and numbered sequentially (1, 2, 3, ...) — no ties, ever; if two rows have equal salary, one arbitrarily gets a lower number than the other.

## 2. `RANK()` and `DENSE_RANK()`

Both rank rows within a partition, but handle ties differently.

```sql
SELECT
    emp_id,
    department,
    salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rank,
    DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dense_rank
FROM employees;
```

- **`RANK()`** — tied rows on `salary` get the same rank, and the next distinct value's rank skips ahead by the number of ties (e.g., 1, 2, 2, 4).
- **`DENSE_RANK()`** — tied rows get the same rank too, but the next distinct value's rank doesn't skip (e.g., 1, 2, 2, 3).

## 3. `LAG()` and `LEAD()`

Access a row at a given offset before or after the current row, within the partition.

```sql
SELECT
    emp_id,
    department,
    salary,
    LAG(salary, 1) OVER (PARTITION BY department ORDER BY salary) AS prev_salary,
    LEAD(salary, 1) OVER (PARTITION BY department ORDER BY salary) AS next_salary
FROM employees;
```

- **`LAG(salary, 1)`** — the salary from one row earlier (in the given order) within the same department.
- **`LEAD(salary, 1)`** — the salary from one row later within the same department.

## 4. Larger Offsets with `LAG()`/`LEAD()`

The offset argument can be any positive integer, not just 1.

```sql
SELECT
    emp_id,
    department,
    salary,
    LAG(salary, 2) OVER (PARTITION BY department ORDER BY salary) AS salary_two_positions_before,
    LEAD(salary, 2) OVER (PARTITION BY department ORDER BY salary) AS salary_two_positions_after
FROM employees;
```

This retrieves the salary two rows before and two rows after the current row, within each department.

## 5. Combining `CASE` with a Windowed Aggregate

Compute the average salary per department, then compare each employee against it.

```sql
SELECT
    emp_id,
    department,
    salary,
    AVG(salary) OVER (PARTITION BY department) AS avg_dept_salary,
    CASE
        WHEN salary >= AVG(salary) OVER (PARTITION BY department) THEN 'Above Average'
        ELSE 'Below Average'
    END AS salary_status
FROM employees;
```

`AVG(salary) OVER (PARTITION BY department)` computes the departmental average without collapsing any rows; the `CASE` expression then labels each employee relative to that average. Note the `AVG(...) OVER (...)` window expression has to be repeated in the `CASE` — you can't reference the `avg_dept_salary` column alias from within the same `SELECT` list.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/Window Functions/SQL Window Function - 2|Comprehensive Guide to SQL Window Functions]]
- [[Data Engineering Role Notes/SQL/Tricks and Tips/Group By and Having Tricks|Group By and Having Tricks]]

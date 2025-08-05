
This note provides examples for several window functions using a sample `employees` table. Assume the table has the following columns:

- `emp_id` (Employee ID)
- `department` (Employee department)
- `salary` (Employee salary)

---

## 1. ROW_NUMBER()

Assigns a unique sequential integer to rows within a partition, ordered by a specific column.

```sql
SELECT 
    emp_id, 
    department, 
    salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS row_num
FROM employees;
```

> **Explanation:**  
> For each `department`, the rows are ordered by `salary` in descending order and numbered sequentially (1, 2, 3, ...).

---

## 2. RANK() and DENSE_RANK()

Both functions assign rankings within a partition, but they differ in how they handle ties.

```sql
SELECT 
    emp_id,
    department,
    salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rank,
    DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dense_rank
FROM employees;
```

> **Explanation:**
> 
> - **RANK():** If two rows tie on `salary`, they receive the same rank and the next rank will have a gap.
> - **DENSE_RANK():** Tied rows receive the same rank without gaps in the ranking sequence.

---

## 3. LAG() and LEAD()

These functions provide access to a row at a given physical offset before or after the current row in the partition.

```sql
SELECT
    emp_id,
    department,
    salary,
    LAG(salary, 1) OVER (PARTITION BY department ORDER BY salary) AS prev_salary,
    LEAD(salary, 1) OVER (PARTITION BY department ORDER BY salary) AS next_salary
FROM employees;
```

> **Explanation:**
> 
> - **LAG(salary, 1):** Returns the salary from one row prior within the same department (ordered by salary).
> - **LEAD(salary, 1):** Returns the salary from one row after within the same department.

---

## 4. Using Parameters with LAG() and LEAD()

You can adjust the offset to fetch values further back or ahead.

```sql
SELECT
    emp_id,
    department,
    salary,
    LAG(salary, 2) OVER (PARTITION BY department ORDER BY salary) AS salary_two_positions_before,
    LEAD(salary, 2) OVER (PARTITION BY department ORDER BY salary) AS salary_two_positions_after
FROM employees;
```

> **Explanation:**  
> This query retrieves the salary from two rows before and after the current row within each department.

---

## 5. Combining a CASE Statement with Aggregate Functions in a Window

Use a windowed aggregate to compute the average salary per department and then compare each employee's salary using a CASE statement.

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

> **Explanation:**
> 
> - **AVG(salary) OVER (PARTITION BY department):** Computes the average salary for each department.
> - **CASE Statement:** Compares each employee's salary to the departmental average and labels it as "Above Average" or "Below Average".

---

These examples demonstrate how to leverage window functions along with parameters, CASE logic, and aggregate functions to perform complex analytical queries. Adjust the partitioning and ordering as needed for your specific dataset and analysis requirements.
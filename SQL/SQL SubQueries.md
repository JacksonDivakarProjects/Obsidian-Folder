You got it, Jack. Let’s get you fully equipped with a **comprehensive, professional-grade guide to SQL subqueries** — a key topic for both **interviews and real-world analytics**.

---

# 📘 Comprehensive Guide to SQL Subqueries

---

## 🧠 What is a Subquery?

> A subquery is a query **nested inside another SQL statement**, used to return a result that the outer query depends on.

Subqueries **increase flexibility**, **reduce complexity**, and **enhance logic reuse** — when used right.

---

## 🔍 Types of Subqueries

### ✅ 1. **Scalar Subquery**

Returns **a single value** (one row, one column)

📌 **Used in**:

- `SELECT`
    
- `WHERE`
    
- `HAVING`
    

```sql
SELECT 
    employee_id, 
    salary,
    (SELECT AVG(salary) FROM employees) AS avg_salary
FROM employees;
```

> 💡 Common in comparisons like:

```sql
WHERE salary > (SELECT AVG(salary) FROM employees)
```

---

### ✅ 2. **Column Subquery (Single-row, multi-column)**

```sql
SELECT *
FROM employees
WHERE (department_id, job_id) = (
    SELECT department_id, job_id
    FROM employees
    WHERE employee_id = 1001
);
```

> 💡 Useful when comparing **multiple fields at once**

---

### ✅ 3. **Row Subquery (Multiple rows, single column)**

```sql
SELECT name
FROM students
WHERE class_id IN (
    SELECT class_id
    FROM classes
    WHERE teacher = 'Jack'
);
```

> 💡 `IN`, `ANY`, `ALL`, `EXISTS` are your tools here

---

### ✅ 4. **Table Subquery (in FROM clause)**

A subquery that **acts like a derived table**.

```sql
SELECT dept_no, AVG(salary)
FROM (
    SELECT dept_no, salary
    FROM employees
    WHERE join_year >= 2020
) AS recent_employees
GROUP BY dept_no;
```

> 💡 Must give alias (`AS recent_employees`) — required by SQL

---

### ✅ 5. **Correlated Subquery**

The subquery **references columns from the outer query**.

```sql
SELECT e1.name
FROM employees e1
WHERE salary > (
    SELECT AVG(salary)
    FROM employees e2
    WHERE e1.department_id = e2.department_id
);
```

> 💡 Re-evaluated **per row** of outer query → **can be expensive**

---

### ✅ 6. **EXISTS Subquery**

Checks **if any rows exist** from the subquery.

```sql
SELECT customer_id
FROM customers c
WHERE EXISTS (
    SELECT 1
    FROM orders o
    WHERE o.customer_id = c.customer_id
);
```

> ✅ Use `EXISTS` when you care **only about existence**, not actual values.

---

## 🎯 Comparison Operators with Subqueries

|Operator|Use Case|Example|
|---|---|---|
|`IN`|Match value from list|`WHERE city IN (SELECT city FROM branches)`|
|`=`|Scalar match|`WHERE salary = (SELECT MAX(salary) FROM employees)`|
|`EXISTS`|Logical presence check|`WHERE EXISTS (SELECT 1 FROM orders WHERE ...)`|
|`ANY`|Compare against **any** match|`WHERE salary > ANY (SELECT salary FROM interns)`|
|`ALL`|Compare against **all** values|`WHERE salary > ALL (SELECT salary FROM interns)`|

---

## 📦 Subqueries in Different Clauses

|Clause|Purpose|Example|
|---|---|---|
|`SELECT`|Add derived values (e.g. rankings, averages)|`(SELECT COUNT(*) FROM ...) AS total_orders`|
|`FROM`|Use subquery as a temp table|`FROM (SELECT ...) AS temp`|
|`WHERE`|Filter rows based on dynamic condition|`WHERE salary > (SELECT AVG(...))`|
|`HAVING`|Aggregate filter with condition|`HAVING SUM(...) > (SELECT ...)`|

---

## ⚠️ Performance Notes

|Technique|Cost/Performance Impact|
|---|---|
|Scalar subquery|Fast, if single value|
|Table subquery|Fine, but requires indexing|
|Correlated subquery|🚫 Costly, especially on large datasets|
|EXISTS vs IN|`EXISTS` is faster for large subqueries|
|CTEs vs Subqueries|Use CTEs for readability if reused|

---

## ✅ Best Practices

- 🧠 **Alias every subquery** (especially in `FROM`)
    
- 🔄 Use **CTEs (`WITH`)** if subquery logic is reused
    
- 💡 Use `EXISTS` over `IN` for performance on large datasets
    
- 🧮 Avoid correlated subqueries unless logically required
    
- 🛠️ Replace scalar subqueries with **JOINs** if possible
    

---

## 📘 Summary Table

|Subquery Type|Returns|Used In|Good For|
|---|---|---|---|
|Scalar|1 row, 1 column|`SELECT`, `WHERE`, etc|Single-value comparisons|
|Row (single col)|Multiple rows|`IN`, `ANY`, `ALL`|Value lists|
|Column (multi col)|One row, multi col|`WHERE`, composite compare|Multi-column match|
|Table|Whole dataset|`FROM`|Derived tables for aggregation|
|Correlated|Varies|`WHERE`, `SELECT`|Row-wise filtering logic|
|EXISTS|TRUE/FALSE|`WHERE`|Existence checks|

---

## 🔥 Want to Go Further?

- Practice rewriting subqueries using `JOIN`s for speed
    
- Explore **window functions** as an alternative
    
- Combine `CTE + Subquery + JOIN` in interview scenarios
    

---

Let me know if you'd like:

- A PDF or markdown cheatsheet
    
- 10 real-world problems using these subquery types
    
- A quiz to lock it all in!
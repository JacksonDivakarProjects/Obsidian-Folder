
---
This note covers various SQL operations such as creating tables with default constraints, altering tables, adding/dropping constraints, creating indexes, and more. Each section includes the SQL query and an explanation.

---

## 1. Creating a Table with IF NOT EXISTS and Default Constraints (MySQL)

When you create a table using the `IF NOT EXISTS` clause, it ensures that the table is only created if it doesn't already exist. Default values are specified inline.

```sql
CREATE TABLE IF NOT EXISTS sample (
    emp_id INT PRIMARY KEY AUTO_INCREMENT,
    sample_data VARCHAR(50)
);
```

> **Explanation:**
> 
> - **IF NOT EXISTS:** Ensures that if the table `sample` already exists, the statement does nothing.
> - **emp_id:** An auto-incremented primary key.
> - **sample_data:** A column for storing sample text data.

---

## 2. Creating a Table with a Foreign Key using ON DELETE SET NULL

This query creates a table with a foreign key constraint. The foreign key (`sample_emp_id`) references `sample(emp_id)`. When a record in the referenced table is deleted, the foreign key value is set to `NULL`.

```sql
CREATE TABLE IF NOT EXISTS employee (
    emp_id INT PRIMARY KEY AUTO_INCREMENT,
    col_2 VARCHAR(20),
    sample_emp_id INT NULL,
    CONSTRAINT fk_sample FOREIGN KEY (sample_emp_id)
        REFERENCES sample(emp_id) ON DELETE SET NULL
);
```

> **Explanation:**
> 
> - **employee table:** Contains its own primary key (`emp_id`) and a column (`sample_emp_id`) that references the `sample` table.
> - **ON DELETE SET NULL:** Ensures that if a row in `sample` is deleted, the corresponding `sample_emp_id` in `employee` is set to `NULL`.

---

## 3. Creating an "employees" Table with Default Constraint and Numeric Data Types

This table demonstrates default values and various numeric data types for financial data.

```sql
CREATE TABLE IF NOT EXISTS employees (
    emp_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) DEFAULT 'Unknown',
    email VARCHAR(100) UNIQUE,
    salary DECIMAL(10,2),  -- For exact numeric values like money
    hire_date DATE DEFAULT CURRENT_DATE
);
```

> **Explanation:**
> 
> - **name:** Defaults to `'Unknown'` if no value is provided.
> - **email:** Must be unique across all records.
> - **salary:** Uses the `DECIMAL` data type for precise calculations (e.g., monetary values).
> - **hire_date:** Defaults to the current date.

---

## 4. Adding a Check Constraint with ALTER TABLE

Here we add a check constraint to ensure that the `salary` is greater than 0.

```sql
ALTER TABLE employees
ADD CONSTRAINT chk_salary CHECK (salary > 0);
```

> **Explanation:**
> 
> - **chk_salary:** A custom name for the constraint.
> - **CHECK (salary > 0):** Enforces that salary values must be positive.

---

## 5. Modifying a Column to Add a Default Value

If you need to change an existing column to include a default value, use the `MODIFY` clause (MySQL syntax).

```sql
ALTER TABLE employees
MODIFY name VARCHAR(50) DEFAULT 'Unknown';
```

> **Explanation:**
> 
> - This command ensures that the `name` column will use `'Unknown'` as its default value if none is provided during insertion.

---

## 6. Adding a Primary Key Constraint (If Not Already Defined)

If the primary key is not defined during table creation, you can add it later.

```sql
ALTER TABLE employees
ADD CONSTRAINT pk_employees PRIMARY KEY (emp_id);
```

> **Explanation:**
> 
> - **pk_employees:** Custom name for the primary key constraint.
> - **emp_id:** Column being designated as the primary key.

---

## 7. Creating Indexes to Improve Query Performance

Indexes help speed up queries. Here are examples for single-column and composite indexes.

### Single-Column Index

```sql
CREATE INDEX idx_name ON employees (name);
```

> **Explanation:**
> 
> - **idx_name:** The name of the index on the `name` column to speed up search queries.

### Composite Index

```sql
CREATE INDEX idx_email_name ON employees (email, name);
```

> **Explanation:**
> 
> - **idx_email_name:** A composite index on both `email` and `name`, which is useful for queries filtering on both columns.

---

## 8. Dropping Constraints

### Dropping a Foreign Key Constraint in MySQL

```sql
ALTER TABLE employee
DROP FOREIGN KEY fk_sample;
```

> **Explanation:**
> 
> - This command removes the foreign key constraint named `fk_sample` from the `employee` table.

### Dropping a Check Constraint

_Note: The syntax to drop a check constraint may vary depending on your SQL dialect._

```sql
ALTER TABLE employees
DROP CONSTRAINT chk_salary;
```

> **Explanation:**
> 
> - This command removes the check constraint named `chk_salary` from the `employees` table.

---

## 9. Creating a Table with Various Numeric Data Types

This table demonstrates the usage of different numeric data types.

```sql
CREATE TABLE IF NOT EXISTS numeric_examples (
    id INT PRIMARY KEY AUTO_INCREMENT,
    double_value DOUBLE,          -- Approximate double-precision floating-point
    float_value FLOAT,            -- Approximate single-precision floating-point
    numeric_value NUMERIC(10, 2),   -- Exact numeric value with fixed precision
    decimal_value DECIMAL(10, 2),   -- Same as NUMERIC; used for exact calculations
    integer_value INT             -- Whole number
);
```

> **Explanation:**
> 
> - **double_value & float_value:** For approximate numeric calculations.
> - **numeric_value & decimal_value:** For exact precision, ideal for monetary values.
> - **integer_value:** For storing whole numbers.

---

## 10. Updating a Record

An example query to update a record, applying a 10% increase to the salary of a specific employee.

```sql
UPDATE employees
SET salary = salary * 1.10
WHERE emp_id = 1;
```

> **Explanation:**
> 
> - **SET salary = salary * 1.10:** Increases the salary by 10%.
> - **WHERE emp_id = 1:** Ensures only the employee with `emp_id` equal to 1 is updated.

---

## 11. Creating a Foreign Key with ON DELETE CASCADE

This example demonstrates a foreign key constraint that automatically deletes related records when the parent record is deleted.

```sql
CREATE TABLE IF NOT EXISTS order_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    CONSTRAINT fk_order FOREIGN KEY (order_id)
        REFERENCES orders(order_id) ON DELETE CASCADE
);
```

> **Explanation:**
> 
> - **order_items table:** Contains order items that reference the `orders` table.
> - **ON DELETE CASCADE:** Automatically deletes all corresponding order items when an order is deleted.

---

This complete markdown note is ready to be pasted into Obsidian. It includes code snippets and detailed explanations for each SQL operation discussed. Enjoy your learning and feel free to modify the examples as needed!
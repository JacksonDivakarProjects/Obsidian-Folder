# Comprehensive Beginner's Guide to PostgreSQL Stored Procedures

## Table of Contents
1. [Introduction to Stored Procedures](#introduction)
2. [Setting Up Your Environment](#environment-setup)
3. [Basic Syntax and Structure](#basic-syntax)
4. [Variables and Data Types](#variables-data-types)
5. [Control Structures](#control-structures)
6. [Error Handling](#error-handling)
7. [Parameters](#parameters)
8. [Practical Examples](#practical-examples)
9. [Best Practices](#best-practices)
10. [Exercises](#exercises)

## 1. Introduction to Stored Procedures <a name="introduction"></a>

### What are Stored Procedures?
Stored procedures are precompiled database programs that:
- Store business logic in the database
- Accept parameters and return results
- Improve performance by reducing network traffic
- Enhance security by controlling data access

### Why Use Stored Procedures?
- **Performance**: Execute complex operations on the server side
- **Maintainability**: Centralize business logic
- **Security**: Control data access through defined interfaces
- **Reusability**: Call the same logic from multiple applications

### Procedures vs Functions in PostgreSQL
| Procedures | Functions |
|------------|-----------|
| Can't return values (use OUT parameters) | Return values |
| Support transaction control (COMMIT/ROLLBACK) | No transaction control |
| Called with `CALL` | Called with `SELECT` |
| Better for actions that modify data | Better for computations |

## 2. Setting Up Your Environment <a name="environment-setup"></a>

### Install PostgreSQL
```bash
# On Ubuntu
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# On macOS
brew install postgresql

# On Windows: Download from postgresql.org
```

### Connect to Database
```bash
psql -U username -d database_name -h hostname -p port
```

### Create Practice Database
```sql
CREATE DATABASE stored_proc_practice;
\c stored_proc_practice;

-- Create sample tables for practice
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    salary DECIMAL(10,2),
    department_id INTEGER,
    hire_date DATE,
    active BOOLEAN DEFAULT true
);

CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    budget DECIMAL(12,2)
);

CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    action VARCHAR(50),
    record_id INTEGER,
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_name VARCHAR(100)
);
```

## 3. Basic Syntax and Structure <a name="basic-syntax"></a>

### Basic Procedure Template
```sql
CREATE OR REPLACE PROCEDURE procedure_name(parameters)
LANGUAGE plpgsql
AS $$
DECLARE
    -- Variable declarations
BEGIN
    -- Procedure logic
    -- SQL statements
    -- Control structures
END;
$$;
```

### Your First Stored Procedure
```sql
-- Simple procedure without parameters
CREATE OR REPLACE PROCEDURE hello_world()
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE NOTICE 'Hello, World!';
END;
$$;

-- Call the procedure
CALL hello_world();
```

### Procedure with Basic Logic
```sql
CREATE OR REPLACE PROCEDURE display_employee_count()
LANGUAGE plpgsql
AS $$
DECLARE
    total_employees INTEGER;
BEGIN
    -- Count employees
    SELECT COUNT(*) INTO total_employees FROM employees;
    
    -- Display result
    RAISE NOTICE 'Total employees: %', total_employees;
END;
$$;

CALL display_employee_count();
```

## 4. Variables and Data Types <a name="variables-data-types"></a>

### Variable Declaration
```sql
CREATE OR REPLACE PROCEDURE variable_demo()
LANGUAGE plpgsql
AS $$
DECLARE
    -- Basic data types
    employee_name VARCHAR(100);
    employee_salary DECIMAL(10,2);
    is_active BOOLEAN;
    hire_date DATE;
    
    -- Constants
    tax_rate CONSTANT DECIMAL(4,3) := 0.15;
    
    -- Default values
    counter INTEGER := 0;
    created_at TIMESTAMP := CURRENT_TIMESTAMP;
BEGIN
    -- Assign values
    employee_name := 'John Doe';
    employee_salary := 50000.00;
    is_active := true;
    hire_date := '2023-01-15';
    
    -- Display values
    RAISE NOTICE 'Employee: %, Salary: %, Active: %, Hire Date: %',
        employee_name, employee_salary, is_active, hire_date;
    RAISE NOTICE 'Tax Rate: %', tax_rate;
END;
$$;

CALL variable_demo();
```

### Working with Table Data
```sql
CREATE OR REPLACE PROCEDURE get_employee_details(emp_id INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
    emp_name VARCHAR(100);
    emp_salary DECIMAL(10,2);
    emp_hire_date DATE;
BEGIN
    -- Get employee data into variables
    SELECT name, salary, hire_date 
    INTO emp_name, emp_salary, emp_hire_date
    FROM employees 
    WHERE id = emp_id;
    
    -- Check if employee was found
    IF emp_name IS NOT NULL THEN
        RAISE NOTICE 'Employee: %, Salary: %, Hire Date: %',
            emp_name, emp_salary, emp_hire_date;
    ELSE
        RAISE NOTICE 'Employee with ID % not found', emp_id;
    END IF;
END;
$$;
```

## 5. Control Structures <a name="control-structures"></a>

### IF-THEN-ELSE Statements
```sql
CREATE OR REPLACE PROCEDURE check_salary_level(emp_id INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
    emp_salary DECIMAL(10,2);
    salary_level VARCHAR(20);
BEGIN
    -- Get employee salary
    SELECT salary INTO emp_salary FROM employees WHERE id = emp_id;
    
    -- Check salary level
    IF emp_salary IS NULL THEN
        salary_level := 'Unknown';
    ELSIF emp_salary > 100000 THEN
        salary_level := 'High';
    ELSIF emp_salary > 50000 THEN
        salary_level := 'Medium';
    ELSE
        salary_level := 'Low';
    END IF;
    
    RAISE NOTICE 'Employee % salary level: %', emp_id, salary_level;
END;
$$;
```

### CASE Statements
```sql
CREATE OR REPLACE PROCEDURE get_employee_status(emp_id INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
    emp_salary DECIMAL(10,2);
    emp_active BOOLEAN;
    status VARCHAR(50);
BEGIN
    SELECT salary, active INTO emp_salary, emp_active 
    FROM employees WHERE id = emp_id;
    
    status := CASE 
        WHEN emp_active = false THEN 'Inactive'
        WHEN emp_salary < 30000 THEN 'Junior'
        WHEN emp_salary BETWEEN 30000 AND 70000 THEN 'Mid-level'
        WHEN emp_salary > 70000 THEN 'Senior'
        ELSE 'Unknown'
    END;
    
    RAISE NOTICE 'Employee % status: %', emp_id, status;
END;
$$;
```

### LOOP Statements
```sql
CREATE OR REPLACE PROCEDURE number_counter()
LANGUAGE plpgsql
AS $$
DECLARE
    i INTEGER := 1;
BEGIN
    -- Basic LOOP
    LOOP
        RAISE NOTICE 'Count: %', i;
        i := i + 1;
        EXIT WHEN i > 5;
    END LOOP;
    
    -- WHILE LOOP
    i := 1;
    WHILE i <= 3 LOOP
        RAISE NOTICE 'While count: %', i;
        i := i + 1;
    END LOOP;
    
    -- FOR LOOP
    FOR i IN 1..4 LOOP
        RAISE NOTICE 'For count: %', i;
    END LOOP;
END;
$$;
```

## 6. Error Handling <a name="error-handling"></a>

### Basic Exception Handling
```sql
CREATE OR REPLACE PROCEDURE safe_division(
    numerator DECIMAL,
    denominator DECIMAL
)
LANGUAGE plpgsql
AS $$
DECLARE
    result DECIMAL;
BEGIN
    BEGIN
        result := numerator / denominator;
        RAISE NOTICE 'Result: %', result;
    EXCEPTION
        WHEN division_by_zero THEN
            RAISE NOTICE 'Error: Cannot divide by zero';
        WHEN others THEN
            RAISE NOTICE 'Unexpected error: %', SQLERRM;
    END;
END;
$$;

CALL safe_division(10, 2);  -- Works
CALL safe_division(10, 0);  -- Handles error
```

### RAISE EXCEPTION
```sql
CREATE OR REPLACE PROCEDURE validate_employee(emp_id INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
    emp_exists BOOLEAN;
BEGIN
    -- Check if employee exists
    SELECT EXISTS(SELECT 1 FROM employees WHERE id = emp_id) 
    INTO emp_exists;
    
    IF NOT emp_exists THEN
        RAISE EXCEPTION 'Employee with ID % does not exist', emp_id;
    END IF;
    
    -- Check if employee is active
    IF NOT (SELECT active FROM employees WHERE id = emp_id) THEN
        RAISE EXCEPTION 'Employee with ID % is not active', emp_id;
    END IF;
    
    RAISE NOTICE 'Employee % is valid', emp_id;
END;
$$;
```

## 7. Parameters <a name="parameters"></a>

### IN Parameters (Input)
```sql
CREATE OR REPLACE PROCEDURE add_employee(
    p_name VARCHAR,
    p_salary DECIMAL,
    p_department_id INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO employees (name, salary, department_id, hire_date)
    VALUES (p_name, p_salary, p_department_id, CURRENT_DATE);
    
    RAISE NOTICE 'Employee % added successfully', p_name;
END;
$$;

CALL add_employee('Alice Johnson', 60000, 1);
```

### OUT Parameters (Output)
```sql
CREATE OR REPLACE PROCEDURE get_employee_stats(
    dept_id INTEGER,
    OUT total_employees INTEGER,
    OUT avg_salary DECIMAL,
    OUT max_salary DECIMAL
)
LANGUAGE plpgsql
AS $$
BEGIN
    SELECT 
        COUNT(*),
        AVG(salary),
        MAX(salary)
    INTO 
        total_employees,
        avg_salary,
        max_salary
    FROM employees 
    WHERE department_id = dept_id;
END;
$$;

-- Call and get output parameters
CALL get_employee_stats(1, NULL, NULL, NULL);
```

### INOUT Parameters
```sql
CREATE OR REPLACE PROCEDURE apply_salary_bonus(
    INOUT current_salary DECIMAL,
    bonus_percent DECIMAL
)
LANGUAGE plpgsql
AS $$
BEGIN
    current_salary := current_salary * (1 + bonus_percent/100);
    RAISE NOTICE 'New salary after % percent bonus: %', 
        bonus_percent, current_salary;
END;
$$;

-- Create a function to call the procedure with INOUT parameter
CREATE OR REPLACE FUNCTION calculate_bonus(
    salary DECIMAL, 
    bonus_percent DECIMAL
) RETURNS DECIMAL
LANGUAGE plpgsql
AS $$
BEGIN
    CALL apply_salary_bonus(salary, bonus_percent);
    RETURN salary;
END;
$$;

SELECT calculate_bonus(50000, 10); -- Returns 55000
```

## 8. Practical Examples <a name="practical-examples"></a>

### Example 1: Employee Management System
```sql
-- Complete employee management procedure
CREATE OR REPLACE PROCEDURE manage_employee(
    action VARCHAR(10),
    emp_id INTEGER DEFAULT NULL,
    emp_name VARCHAR DEFAULT NULL,
    emp_salary DECIMAL DEFAULT NULL,
    emp_dept_id INTEGER DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    CASE action
        WHEN 'ADD' THEN
            INSERT INTO employees (name, salary, department_id, hire_date)
            VALUES (emp_name, emp_salary, emp_dept_id, CURRENT_DATE);
            RAISE NOTICE 'Employee added successfully';
            
        WHEN 'UPDATE' THEN
            UPDATE employees 
            SET name = COALESCE(emp_name, name),
                salary = COALESCE(emp_salary, salary),
                department_id = COALESCE(emp_dept_id, department_id)
            WHERE id = emp_id;
            
            IF FOUND THEN
                RAISE NOTICE 'Employee % updated', emp_id;
            ELSE
                RAISE NOTICE 'Employee % not found', emp_id;
            END IF;
            
        WHEN 'DELETE' THEN
            UPDATE employees SET active = false WHERE id = emp_id;
            IF FOUND THEN
                RAISE NOTICE 'Employee % deactivated', emp_id;
            ELSE
                RAISE NOTICE 'Employee % not found', emp_id;
            END IF;
            
        ELSE
            RAISE EXCEPTION 'Invalid action: %. Use ADD, UPDATE, or DELETE', action;
    END CASE;
END;
$$;

-- Usage examples
CALL manage_employee('ADD', NULL, 'Bob Smith', 75000, 1);
CALL manage_employee('UPDATE', 1, 'Bob Smith Updated', 80000, NULL);
CALL manage_employee('DELETE', 1);
```

### Example 2: Audit Logging
```sql
CREATE OR REPLACE PROCEDURE log_audit(
    p_table_name VARCHAR,
    p_action VARCHAR,
    p_record_id INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO audit_log (table_name, action, record_id, user_name)
    VALUES (p_table_name, p_action, p_record_id, current_user);
    
    RAISE NOTICE 'Audit logged: % on % table, record %', 
        p_action, p_table_name, p_record_id;
END;
$$;

-- Procedure with automatic auditing
CREATE OR REPLACE PROCEDURE update_employee_with_audit(
    emp_id INTEGER,
    new_salary DECIMAL
)
LANGUAGE plpgsql
AS $$
DECLARE
    old_salary DECIMAL;
BEGIN
    -- Get old salary for comparison
    SELECT salary INTO old_salary FROM employees WHERE id = emp_id;
    
    -- Update employee
    UPDATE employees SET salary = new_salary WHERE id = emp_id;
    
    -- Log the change
    CALL log_audit('employees', 'SALARY_UPDATE', emp_id);
    
    RAISE NOTICE 'Salary updated from % to %', old_salary, new_salary;
END;
$$;
```

### Example 3: Monthly Report Generator
```sql
CREATE OR REPLACE PROCEDURE generate_monthly_report(
    report_month INTEGER,
    report_year INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    total_employees INTEGER;
    total_salary DECIMAL;
    avg_salary DECIMAL;
    dept_record RECORD;
BEGIN
    -- Get overall statistics
    SELECT 
        COUNT(*) AS total_count,
        SUM(salary) AS total_sal,
        AVG(salary) AS average_sal
    INTO total_employees, total_salary, avg_salary
    FROM employees 
    WHERE active = true;
    
    RAISE NOTICE '=== MONTHLY REPORT %/% ===', report_month, report_year;
    RAISE NOTICE 'Total Employees: %', total_employees;
    RAISE NOTICE 'Total Salary: %', total_salary;
    RAISE NOTICE 'Average Salary: %', avg_salary;
    RAISE NOTICE '--- Department Breakdown ---';
    
    -- Department-wise breakdown
    FOR dept_record IN 
        SELECT d.name, COUNT(e.id) as emp_count, AVG(e.salary) as avg_sal
        FROM departments d
        LEFT JOIN employees e ON d.id = e.department_id AND e.active = true
        GROUP BY d.id, d.name
    LOOP
        RAISE NOTICE 'Department: %, Employees: %, Avg Salary: %',
            dept_record.name, dept_record.emp_count, dept_record.avg_sal;
    END LOOP;
    
    RAISE NOTICE '=== END OF REPORT ===';
END;
$$;

CALL generate_monthly_report(12, 2023);
```

## 9. Best Practices <a name="best-practices"></a>

### 1. Naming Conventions
```sql
-- Good naming examples
CREATE OR REPLACE PROCEDURE calculate_employee_bonus(...)
CREATE OR REPLACE PROCEDURE update_customer_status(...)
CREATE OR REPLACE PROCEDURE generate_monthly_report(...)

-- Parameter naming
CREATE OR REPLACE PROCEDURE add_employee(
    p_name VARCHAR,  -- p_ for parameters
    p_salary DECIMAL
)
```

### 2. Error Handling
```sql
CREATE OR REPLACE PROCEDURE robust_operation()
LANGUAGE plpgsql
AS $$
BEGIN
    -- Start transaction
    BEGIN
        -- Your operations here
        INSERT INTO table1 ...;
        UPDATE table2 ...;
        
        -- Commit if successful
        COMMIT;
        
    EXCEPTION
        WHEN others THEN
            -- Rollback on error
            ROLLBACK;
            RAISE NOTICE 'Operation failed: %', SQLERRM;
            -- Re-raise the exception
            RAISE;
    END;
END;
$$;
```

### 3. Documentation
```sql
/*
Procedure: calculate_employee_bonus
Description: Calculates annual bonus based on performance and salary
Parameters:
  - p_employee_id: ID of the employee
  - p_performance_rating: Rating from 1.0 to 5.0
  - p_bonus_percent: Base bonus percentage
Returns: Calculated bonus amount through OUT parameter
Author: Your Name
Created: 2024-01-01
*/
CREATE OR REPLACE PROCEDURE calculate_employee_bonus(
    p_employee_id INTEGER,
    p_performance_rating DECIMAL,
    INOUT p_bonus_amount DECIMAL
)
LANGUAGE plpgsql
AS $$
-- Implementation here
```

## 10. Exercises <a name="exercises"></a>

### Beginner Exercises

**Exercise 1**: Create a procedure that increases all salaries by a given percentage
```sql
-- Your solution here
```

**Exercise 2**: Write a procedure that finds employees in a salary range
```sql
-- Your solution here
```

**Exercise 3**: Create a procedure that transfers employees between departments
```sql
-- Your solution here
```

### Intermediate Exercises

**Exercise 4**: Implement a comprehensive employee onboarding procedure
```sql
-- Your solution here
```

**Exercise 5**: Create a procedure that generates performance reports with error handling
```sql
-- Your solution here
```

### Advanced Exercise

**Exercise 6**: Build a complete payroll system with multiple procedures
```sql
-- Your solution here
```

## Next Steps

1. **Practice regularly** with different scenarios
2. **Learn about cursors** for handling large result sets
3. **Explore dynamic SQL** for flexible queries
4. **Study performance optimization** techniques
5. **Learn about triggers** that call procedures

## Additional Resources

- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
- [PL/pgSQL Language Guide](https://www.postgresql.org/docs/current/plpgsql.html)
- Practice with real-world business scenarios
- Join PostgreSQL communities and forums

Remember: The key to mastering stored procedures is consistent practice and building real projects!
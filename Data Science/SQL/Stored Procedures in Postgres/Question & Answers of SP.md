Great questions! Let me break these down with clear explanations and examples.

## 1. The `:=` Operator (Assignment Operator)

The `:=` operator is used for **assignment** in PL/pgSQL. It assigns values to variables.

### Basic Usage
```sql
CREATE OR REPLACE PROCEDURE assignment_demo()
LANGUAGE plpgsql
AS $$
DECLARE
    counter INTEGER;
    total_salary DECIMAL;
    employee_name VARCHAR(100);
    is_active BOOLEAN;
BEGIN
    -- Assign values using :=
    counter := 10;
    total_salary := 50000.00;
    employee_name := 'John Doe';
    is_active := true;
    
    -- Display values
    RAISE NOTICE 'Counter: %, Salary: %, Name: %, Active: %',
        counter, total_salary, employee_name, is_active;
END;
$$;
```

### Assignment from Query Results
```sql
CREATE OR REPLACE PROCEDURE get_employee_data(emp_id INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
    emp_name VARCHAR(100);
    emp_salary DECIMAL;
    emp_hire_date DATE;
BEGIN
    -- Assign from query results
    SELECT name, salary, hire_date 
    INTO emp_name, emp_salary, emp_hire_date
    FROM employees 
    WHERE id = emp_id;
    
    -- Or you can assign individually
    -- SELECT name INTO emp_name FROM employees WHERE id = emp_id;
    
    RAISE NOTICE 'Name: %, Salary: %, Hire Date: %',
        emp_name, emp_salary, emp_hire_date;
END;
$$;
```

### Multiple Assignment Methods
```sql
CREATE OR REPLACE PROCEDURE assignment_methods()
LANGUAGE plpgsql
AS $$
DECLARE
    -- Method 1: Declare with DEFAULT
    counter INTEGER DEFAULT 0;
    
    -- Method 2: Declare with :=
    total INTEGER := 100;
    
    -- Method 3: Declare without initialization
    result INTEGER;
BEGIN
    -- Method 4: Assign later with :=
    result := counter + total;
    
    -- Method 5: Using SELECT INTO
    SELECT (counter + total) * 2 INTO result;
    
    RAISE NOTICE 'Result: %', result;
END;
$$;
```

## 2. Using OUT Parameters After Calling

### Method 1: Using DO Block (Recommended for Testing)
```sql
-- Procedure with OUT parameters
CREATE OR REPLACE PROCEDURE calculate_stats(
    dept_id INTEGER,
    OUT employee_count INTEGER,
    OUT total_salary DECIMAL,
    OUT average_salary DECIMAL
)
LANGUAGE plpgsql
AS $$
BEGIN
    SELECT COUNT(*), SUM(salary), AVG(salary)
    INTO employee_count, total_salary, average_salary
    FROM employees 
    WHERE department_id = dept_id;
END;
$$;

-- Method 1: Using DO block to capture OUT parameters
DO $$
DECLARE
    emp_count INTEGER;
    total_sal DECIMAL;
    avg_sal DECIMAL;
BEGIN
    -- Call procedure and capture OUT parameters
    CALL calculate_stats(1, emp_count, total_sal, avg_sal);
    
    -- Use the OUT parameters
    RAISE NOTICE 'Department 1: % employees, Total salary: %, Average: %',
        emp_count, total_sal, avg_sal;
END;
$$;
```

### Method 2: Using Function Wrapper
```sql
-- Create a function that calls the procedure and returns values
CREATE OR REPLACE FUNCTION get_department_stats(dept_id INTEGER)
RETURNS TABLE(emp_count INTEGER, total_sal DECIMAL, avg_sal DECIMAL)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Call the procedure and return OUT parameters
    CALL calculate_stats(dept_id, emp_count, total_sal, avg_sal);
    RETURN QUERY SELECT emp_count, total_sal, avg_sal;
END;
$$;

-- Use the function
SELECT * FROM get_department_stats(1);
```

### Method 3: Direct Call in psql
```sql
-- In psql, you can call directly but need to provide variables
-- This works in some PostgreSQL clients
CALL calculate_stats(1, NULL, NULL, NULL);
```

### Method 4: Using INOUT Parameters (More Flexible)
```sql
CREATE OR REPLACE PROCEDURE calculate_bonus(
    INOUT base_salary DECIMAL,
    IN performance_rating DECIMAL
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF performance_rating >= 4.5 THEN
        base_salary := base_salary * 1.15; -- 15% bonus
    ELSIF performance_rating >= 3.5 THEN
        base_salary := base_salary * 1.10; -- 10% bonus
    ELSE
        base_salary := base_salary * 1.05; -- 5% bonus
    END IF;
END;
$$;

-- Using INOUT parameter
DO $$
DECLARE
    salary DECIMAL := 50000;
BEGIN
    CALL calculate_bonus(salary, 4.7);
    RAISE NOTICE 'New salary after bonus: %', salary;
END;
$$;
```

## 3. Default Parameter Mode (IN/OUT)

### Default is IN
If you don't specify a parameter mode, it defaults to **IN** (input only).

```sql
-- These are equivalent:
CREATE OR REPLACE PROCEDURE proc1(param1 INTEGER) ...
CREATE OR REPLACE PROCEDURE proc1(IN param1 INTEGER) ...

-- Examples demonstrating default IN behavior
CREATE OR REPLACE PROCEDURE update_employee_salary(
    emp_id INTEGER,  -- Default: IN parameter
    new_salary DECIMAL  -- Default: IN parameter
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE employees 
    SET salary = new_salary 
    WHERE id = emp_id;
    
    RAISE NOTICE 'Updated employee % salary to %', emp_id, new_salary;
END;
$$;

-- You cannot modify IN parameters inside the procedure
CREATE OR REPLACE PROCEDURE try_modify_in_param(
    incoming_param INTEGER  -- This is IN by default
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- This will cause ERROR because you can't modify IN parameters
    -- incoming_param := incoming_param + 10;  -- ERROR!
    
    -- You can only use IN parameters, not modify them
    RAISE NOTICE 'Received parameter: %', incoming_param;
END;
$$;
```

### Explicit Parameter Modes
```sql
-- All parameter modes
CREATE OR REPLACE PROCEDURE parameter_modes_demo(
    IN in_param INTEGER,      -- Input only (default)
    OUT out_param TEXT,       -- Output only
    INOUT inout_param DECIMAL -- Both input and output
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Can USE in_param but not modify it
    RAISE NOTICE 'IN parameter: %', in_param;
    
    -- Can MODIFY out_param (no initial value)
    out_param := 'Processed: ' || in_param::TEXT;
    
    -- Can USE and MODIFY inout_param
    inout_param := inout_param * 1.1;
END;
$$;
```

## 4. Declaring Values in DECLARE Section

### Multiple Declaration Methods
```sql
CREATE OR REPLACE PROCEDURE declaration_demo()
LANGUAGE plpgsql
AS $$
DECLARE
    -- Method 1: Simple declaration (no initial value)
    counter INTEGER;
    
    -- Method 2: Declaration with DEFAULT
    total_count INTEGER DEFAULT 0;
    
    -- Method 3: Declaration with :=
    max_value INTEGER := 100;
    
    -- Method 4: CONSTANT declaration
    tax_rate CONSTANT DECIMAL := 0.15;
    
    -- Method 5: With NOT NULL constraint
    min_salary DECIMAL NOT NULL := 30000;
    
    -- Method 6: Complex default expressions
    current_date_var DATE := CURRENT_DATE;
    next_week DATE := CURRENT_DATE + INTERVAL '7 days';
    
    -- Method 7: Using SELECT for complex initialization
    company_name VARCHAR := (SELECT name FROM companies WHERE id = 1);
BEGIN
    -- Assign values to simply declared variables
    counter := 5;
    
    -- Use all variables
    RAISE NOTICE 'Counter: %, Total: %, Max: %', counter, total_count, max_value;
    RAISE NOTICE 'Tax Rate: %, Min Salary: %', tax_rate, min_salary;
    RAISE NOTICE 'Today: %, Next Week: %', current_date_var, next_week;
    RAISE NOTICE 'Company: %', company_name;
END;
$$;
```

### Practical Example with All Concepts
```sql
CREATE OR REPLACE PROCEDURE employee_analysis(
    IN department_id INTEGER,
    OUT dept_name VARCHAR,
    OUT employee_count INTEGER,
    OUT salary_stats TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    -- Declarations with various initialization methods
    min_salary DECIMAL := 0;
    max_salary DECIMAL DEFAULT 0;
    avg_salary DECIMAL;
    total_budget DECIMAL;
    
    -- Constants
    bonus_rate CONSTANT DECIMAL := 0.1;
BEGIN
    -- Get department name
    SELECT name INTO dept_name 
    FROM departments WHERE id = department_id;
    
    -- Get employee statistics
    SELECT 
        COUNT(*),
        MIN(salary),
        MAX(salary),
        AVG(salary),
        SUM(salary)
    INTO 
        employee_count,
        min_salary,
        max_salary,
        avg_salary,
        total_budget
    FROM employees 
    WHERE department_id = department_id AND active = true;
    
    -- Calculate bonus using :=
    total_budget := total_budget * (1 + bonus_rate);
    
    -- Prepare output
    salary_stats := format(
        'Min: %s, Max: %s, Avg: %s, Total with Bonus: %s',
        min_salary, max_salary, avg_salary, total_budget
    );
    
    RAISE NOTICE 'Analysis complete for department: %', dept_name;
END;
$$;

-- Using the procedure
DO $$
DECLARE
    dept_name VARCHAR;
    emp_count INTEGER;
    stats TEXT;
BEGIN
    CALL employee_analysis(1, dept_name, emp_count, stats);
    RAISE NOTICE 'Department: %, Employees: %, Stats: %',
        dept_name, emp_count, stats;
END;
$$;
```

## Quick Reference Summary

| Concept | Syntax | Example |
|---------|--------|---------|
| **Assignment** | `variable := value` | `counter := 10` |
| **OUT Parameter Usage** | Use in DO block | `CALL proc(OUT param)` |
| **Default Parameter** | No mode = IN | `param INTEGER` = `IN param INTEGER` |
| **Declaration with Value** | Multiple methods | `var TYPE := value` |

### Key Points to Remember:
1. **`:=`** is for assignment, **`=`** is for comparison
2. **OUT parameters** need variables to capture results
3. **Default parameter mode is IN**
4. Use **DEFAULT** or **:=** in DECLARE section for initial values
5. **CONSTANT** prevents variable modification
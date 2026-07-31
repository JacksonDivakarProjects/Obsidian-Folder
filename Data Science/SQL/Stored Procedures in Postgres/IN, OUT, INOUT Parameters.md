# Comprehensive Guide to IN, OUT, and INOUT Parameters in PostgreSQL

## Table of Contents
1. [Introduction to Parameter Modes](#introduction)
2. [IN Parameters](#in-parameters)
3. [OUT Parameters](#out-parameters)
4. [INOUT Parameters](#inout-parameters)
5. [Parameter Combinations](#parameter-combinations)
6. [Best Practices](#best-practices)
7. [Real-World Examples](#real-world-examples)
8. [Common Pitfalls](#common-pitfalls)

## 1. Introduction to Parameter Modes <a name="introduction"></a>

PostgreSQL supports three parameter modes for procedures and functions:

| Mode | Purpose | Can Read | Can Modify | Caller Sees Changes |
|------|---------|----------|------------|---------------------|
| **IN** | Input only | ✅ | ❌ | ❌ |
| **OUT** | Output only | ❌ | ✅ | ✅ |
| **INOUT** | Both input & output | ✅ | ✅ | ✅ |

### Default Behavior
- If no mode is specified, parameters default to **IN**
- IN parameters are **read-only** inside the procedure
- OUT parameters start as **NULL** and must be assigned values
- INOUT parameters retain their input values and can be modified

## 2. IN Parameters <a name="in-parameters"></a>

### Basic Syntax
```sql
CREATE OR REPLACE PROCEDURE procedure_name(IN parameter_name data_type)
```

### Characteristics
- **Input only** - values passed from caller
- **Read-only** inside the procedure
- **Cannot be modified**
- **Default mode** if not specified

### Examples

#### Simple IN Parameter
```sql
CREATE OR REPLACE PROCEDURE greet_employee(IN employee_name VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE NOTICE 'Hello, %!', employee_name;
END;
$$;

-- Calling
CALL greet_employee('John Doe');
```

#### Multiple IN Parameters
```sql
CREATE OR REPLACE PROCEDURE create_employee(
    IN first_name VARCHAR,
    IN last_name VARCHAR,
    IN salary DECIMAL,
    IN department_id INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    full_name VARCHAR;
BEGIN
    full_name := first_name || ' ' || last_name;
    
    INSERT INTO employees (name, salary, department_id, hire_date)
    VALUES (full_name, salary, department_id, CURRENT_DATE);
    
    RAISE NOTICE 'Employee % created successfully', full_name;
END;
$$;

-- Calling
CALL create_employee('Alice', 'Smith', 75000, 1);
```

#### IN Parameters with Default Values
```sql
CREATE OR REPLACE PROCEDURE update_salary(
    IN employee_id INTEGER,
    IN new_salary DECIMAL,
    IN effective_date DATE DEFAULT CURRENT_DATE
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE employees 
    SET salary = new_salary,
        last_salary_update = effective_date
    WHERE id = employee_id;
    
    RAISE NOTICE 'Salary updated for employee %', employee_id;
END;
$$;

-- Calling with all parameters
CALL update_salary(1, 80000, '2024-01-15');

-- Calling with default parameter
CALL update_salary(1, 80000);  -- Uses CURRENT_DATE
```

## 3. OUT Parameters <a name="out-parameters"></a>

### Basic Syntax
```sql
CREATE OR REPLACE PROCEDURE procedure_name(OUT parameter_name data_type)
```

### Characteristics
- **Output only** - used to return values to caller
- **Starts as NULL** - must be assigned a value
- **Cannot be read before assignment**
- **Caller receives the final value**

### Examples

#### Simple OUT Parameter
```sql
CREATE OR REPLACE PROCEDURE get_employee_count(OUT total_count INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    SELECT COUNT(*) INTO total_count FROM employees WHERE active = true;
    RAISE NOTICE 'Total active employees: %', total_count;
END;
$$;

-- Calling and capturing OUT parameter
DO $$
DECLARE
    employee_count INTEGER;
BEGIN
    CALL get_employee_count(employee_count);
    RAISE NOTICE 'Result: % employees', employee_count;
END;
$$;
```

#### Multiple OUT Parameters
```sql
CREATE OR REPLACE PROCEDURE get_department_stats(
    IN dept_id INTEGER,
    OUT employee_count INTEGER,
    OUT total_salary DECIMAL,
    OUT average_salary DECIMAL
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Initialize OUT parameters
    SELECT 
        COUNT(*),
        COALESCE(SUM(salary), 0),
        COALESCE(AVG(salary), 0)
    INTO 
        employee_count,
        total_salary,
        average_salary
    FROM employees 
    WHERE department_id = dept_id AND active = true;
    
    RAISE NOTICE 'Department %: % employees, $% total, $% average',
        dept_id, employee_count, total_salary, average_salary;
END;
$$;

-- Calling multiple OUT parameters
DO $$
DECLARE
    emp_count INTEGER;
    total_sal DECIMAL;
    avg_sal DECIMAL;
BEGIN
    CALL get_department_stats(1, emp_count, total_sal, avg_sal);
    RAISE NOTICE 'Final - Count: %, Total: %, Average: %', 
        emp_count, total_sal, avg_sal;
END;
$$;
```

#### OUT Parameters with Conditional Logic
```sql
CREATE OR REPLACE PROCEDURE analyze_salary(
    IN emp_id INTEGER,
    OUT salary_level VARCHAR,
    OUT bonus_eligible BOOLEAN,
    OUT recommendation TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    emp_salary DECIMAL;
    emp_hire_date DATE;
BEGIN
    -- Get employee data
    SELECT salary, hire_date INTO emp_salary, emp_hire_date
    FROM employees WHERE id = emp_id;
    
    -- Set OUT parameters based on logic
    IF emp_salary IS NULL THEN
        salary_level := 'Unknown';
        bonus_eligible := false;
        recommendation := 'Salary data missing';
    ELSIF emp_salary > 100000 THEN
        salary_level := 'High';
        bonus_eligible := true;
        recommendation := 'Eligible for executive bonus';
    ELSIF emp_salary > 50000 THEN
        salary_level := 'Medium';
        bonus_eligible := true;
        recommendation := 'Standard bonus applicable';
    ELSE
        salary_level := 'Low';
        bonus_eligible := false;
        recommendation := 'Consider salary review';
    END IF;
    
    -- Additional logic based on hire date
    IF emp_hire_date < CURRENT_DATE - INTERVAL '1 year' THEN
        recommendation := recommendation || ' (Tenure bonus eligible)';
    END IF;
END;
$$;

-- Testing the analysis
DO $$
DECLARE
    level VARCHAR;
    eligible BOOLEAN;
    advice TEXT;
BEGIN
    CALL analyze_salary(1, level, eligible, advice);
    RAISE NOTICE 'Level: %, Eligible: %, Advice: %', level, eligible, advice;
END;
$$;
```

## 4. INOUT Parameters <a name="inout-parameters"></a>

### Basic Syntax
```sql
CREATE OR REPLACE PROCEDURE procedure_name(INOUT parameter_name data_type)
```

### Characteristics
- **Both input and output**
- **Retains input value** at start
- **Can be read and modified**
- **Caller sees the modified value**

### Examples

#### Simple INOUT Parameter
```sql
CREATE OR REPLACE PROCEDURE apply_bonus(INOUT salary DECIMAL, IN bonus_percent DECIMAL)
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE NOTICE 'Original salary: %', salary;
    salary := salary * (1 + bonus_percent/100);
    RAISE NOTICE 'New salary after % percent bonus: %', bonus_percent, salary;
END;
$$;

-- Using INOUT parameter
DO $$
DECLARE
    current_salary DECIMAL := 50000;
BEGIN
    RAISE NOTICE 'Before call: %', current_salary;
    CALL apply_bonus(current_salary, 10);  -- 10% bonus
    RAISE NOTICE 'After call: %', current_salary;
END;
$$;
```

#### INOUT with Complex Logic
```sql
CREATE OR REPLACE PROCEDURE process_employee_rating(
    INOUT performance_score INTEGER,
    IN years_of_service INTEGER,
    OUT performance_grade CHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Adjust score based on years of service
    IF years_of_service > 5 THEN
        performance_score := performance_score + 5;  -- Loyalty bonus
    ELSIF years_of_service > 2 THEN
        performance_score := performance_score + 2;  -- Experience bonus
    END IF;
    
    -- Cap the score at 100
    IF performance_score > 100 THEN
        performance_score := 100;
    END IF;
    
    -- Set grade based on adjusted score
    IF performance_score >= 90 THEN
        performance_grade := 'A';
    ELSIF performance_score >= 75 THEN
        performance_grade := 'B';
    ELSIF performance_score >= 60 THEN
        performance_grade := 'C';
    ELSE
        performance_grade := 'D';
    END IF;
    
    RAISE NOTICE 'Adjusted score: %, Grade: %', performance_score, performance_grade;
END;
$$;

-- Testing INOUT with other parameters
DO $$
DECLARE
    score INTEGER := 85;
    grade CHAR;
BEGIN
    RAISE NOTICE 'Initial score: %', score;
    CALL process_employee_rating(score, 6, grade);  -- 6 years service
    RAISE NOTICE 'Final score: %, Grade: %', score, grade;
END;
$$;
```

## 5. Parameter Combinations <a name="parameter-combinations"></a>

### Mixed Parameter Types
```sql
CREATE OR REPLACE PROCEDURE comprehensive_employee_operation(
    IN emp_id INTEGER,                    -- Input only
    IN new_department_id INTEGER,         -- Input only
    INOUT current_salary DECIMAL,         -- Input and output
    OUT old_department_id INTEGER,        -- Output only
    OUT operation_status TEXT            -- Output only
)
LANGUAGE plpgsql
AS $$
DECLARE
    emp_name VARCHAR;
BEGIN
    -- Get current department and name
    SELECT department_id, name, salary 
    INTO old_department_id, emp_name, current_salary
    FROM employees WHERE id = emp_id;
    
    -- Perform department transfer
    UPDATE employees 
    SET department_id = new_department_id,
        salary = current_salary  -- Use the (potentially modified) INOUT value
    WHERE id = emp_id;
    
    -- Apply department transfer bonus (modify INOUT parameter)
    IF old_department_id != new_department_id THEN
        current_salary := current_salary * 1.05;  -- 5% transfer bonus
        operation_status := 'Transfer completed with bonus';
    ELSE
        operation_status := 'Department unchanged';
    END IF;
    
    RAISE NOTICE 'Employee %: % -> %, Salary: %', 
        emp_name, old_department_id, new_department_id, current_salary;
END;
$$;

-- Testing mixed parameters
DO $$
DECLARE
    salary DECIMAL := 60000;
    old_dept INTEGER;
    status TEXT;
BEGIN
    CALL comprehensive_employee_operation(1, 2, salary, old_dept, status);
    RAISE NOTICE 'Result - Salary: %, Old Dept: %, Status: %', 
        salary, old_dept, status;
END;
$$;
```

### Complex Business Logic with All Parameter Types
```sql
CREATE OR REPLACE PROCEDURE process_payroll(
    IN pay_period_start DATE,
    IN pay_period_end DATE,
    INOUT total_payroll_budget DECIMAL,
    OUT employees_processed INTEGER,
    OUT payroll_status TEXT,
    OUT error_details TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    emp_record RECORD;
    emp_cursor CURSOR FOR 
        SELECT id, name, salary, department_id 
        FROM employees 
        WHERE active = true;
BEGIN
    employees_processed := 0;
    payroll_status := 'Processing';
    error_details := '';
    
    -- Check if budget is sufficient
    IF total_payroll_budget <= 0 THEN
        payroll_status := 'Failed';
        error_details := 'Insufficient budget';
        RETURN;
    END IF;
    
    OPEN emp_cursor;
    LOOP
        FETCH emp_cursor INTO emp_record;
        EXIT WHEN NOT FOUND;
        
        BEGIN
            -- Process each employee
            INSERT INTO payroll_records (
                employee_id, 
                pay_period_start, 
                pay_period_end, 
                amount
            ) VALUES (
                emp_record.id,
                pay_period_start,
                pay_period_end,
                emp_record.salary
            );
            
            -- Deduct from budget
            total_payroll_budget := total_payroll_budget - emp_record.salary;
            
            -- Check budget
            IF total_payroll_budget < 0 THEN
                payroll_status := 'Partial';
                error_details := 'Budget exhausted after processing ' || employees_processed || ' employees';
                EXIT;
            END IF;
            
            employees_processed := employees_processed + 1;
            
        EXCEPTION
            WHEN others THEN
                error_details := 'Error processing employee ' || emp_record.id || ': ' || SQLERRM;
                payroll_status := 'Failed';
                EXIT;
        END;
    END LOOP;
    
    CLOSE emp_cursor;
    
    IF payroll_status = 'Processing' THEN
        payroll_status := 'Completed';
    END IF;
    
    RAISE NOTICE 'Payroll processed: % employees, Status: %, Remaining budget: %',
        employees_processed, payroll_status, total_payroll_budget;
END;
$$;

-- Testing complex payroll processing
DO $$
DECLARE
    budget DECIMAL := 500000;
    processed INTEGER;
    status TEXT;
    errors TEXT;
BEGIN
    CALL process_payroll(
        '2024-01-01', 
        '2024-01-15', 
        budget, 
        processed, 
        status, 
        errors
    );
    RAISE NOTICE 'Final - Budget: %, Processed: %, Status: %, Errors: %',
        budget, processed, status, errors;
END;
$$;
```

## 6. Best Practices <a name="best-practices"></a>

### 1. Naming Conventions
```sql
-- Good naming practices
CREATE OR REPLACE PROCEDURE calculate_employee_bonus(
    IN p_employee_id INTEGER,        -- p_ for parameters
    IN p_performance_rating DECIMAL,
    OUT o_bonus_amount DECIMAL,      -- o_ for OUT parameters
    INOUT io_base_salary DECIMAL     -- io_ for INOUT parameters
)
```

### 2. Parameter Validation
```sql
CREATE OR REPLACE PROCEDURE safe_employee_creation(
    IN first_name VARCHAR,
    IN last_name VARCHAR,
    IN salary DECIMAL,
    OUT employee_id INTEGER,
    OUT status_message TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Initialize OUT parameters
    employee_id := 0;
    status_message := '';
    
    -- Validate input parameters
    IF first_name IS NULL OR first_name = '' THEN
        status_message := 'First name is required';
        RETURN;
    END IF;
    
    IF last_name IS NULL OR last_name = '' THEN
        status_message := 'Last name is required';
        RETURN;
    END IF;
    
    IF salary IS NULL OR salary <= 0 THEN
        status_message := 'Valid salary is required';
        RETURN;
    END IF;
    
    -- Proceed with valid data
    INSERT INTO employees (name, salary, hire_date)
    VALUES (first_name || ' ' || last_name, salary, CURRENT_DATE)
    RETURNING id INTO employee_id;
    
    status_message := 'Employee created successfully';
    
EXCEPTION
    WHEN others THEN
        status_message := 'Error creating employee: ' || SQLERRM;
        employee_id := 0;
END;
$$;
```

### 3. Documentation
```sql
/*
Procedure: comprehensive_data_processing
Description: Processes employee data with comprehensive validation and reporting
Parameters:
  IN:
    - department_filter: Department ID to filter employees (NULL for all)
    - process_date: Date for processing
  INOUT:
    - processing_budget: Available budget (modified during processing)
  OUT:
    - records_processed: Number of records successfully processed
    - total_cost: Total cost of processing
    - processing_status: Final status of the operation
Returns: Various status and count information via OUT parameters
*/
CREATE OR REPLACE PROCEDURE comprehensive_data_processing(
    IN department_filter INTEGER,
    IN process_date DATE,
    INOUT processing_budget DECIMAL,
    OUT records_processed INTEGER,
    OUT total_cost DECIMAL,
    OUT processing_status TEXT
)
-- Implementation here
```

## 7. Real-World Examples <a name="real-world-examples"></a>

### Example 1: E-commerce Order Processing
```sql
CREATE OR REPLACE PROCEDURE process_customer_order(
    IN customer_id INTEGER,
    IN product_id INTEGER,
    IN quantity INTEGER,
    INOUT available_balance DECIMAL,
    OUT order_id INTEGER,
    OUT order_status TEXT,
    OUT shipping_date DATE
)
LANGUAGE plpgsql
AS $$
DECLARE
    product_price DECIMAL;
    total_cost DECIMAL;
    stock_quantity INTEGER;
    customer_name VARCHAR;
BEGIN
    -- Initialize OUT parameters
    order_id := 0;
    order_status := 'Processing';
    shipping_date := NULL;
    
    -- Get product information
    SELECT price, quantity_remaining INTO product_price, stock_quantity
    FROM products WHERE id = product_id;
    
    -- Validate product availability
    IF stock_quantity < quantity THEN
        order_status := 'Failed: Insufficient stock';
        RETURN;
    END IF;
    
    -- Calculate total cost
    total_cost := product_price * quantity;
    
    -- Validate customer balance
    IF available_balance < total_cost THEN
        order_status := 'Failed: Insufficient funds';
        RETURN;
    END IF;
    
    -- Process order
    BEGIN
        -- Create order
        INSERT INTO orders (customer_id, order_date, total_amount, status)
        VALUES (customer_id, CURRENT_DATE, total_cost, 'Confirmed')
        RETURNING id INTO order_id;
        
        -- Add order items
        INSERT INTO order_items (order_id, product_id, quantity, unit_price)
        VALUES (order_id, product_id, quantity, product_price);
        
        -- Update product stock
        UPDATE products 
        SET quantity_remaining = quantity_remaining - quantity
        WHERE id = product_id;
        
        -- Deduct from balance
        available_balance := available_balance - total_cost;
        
        -- Set shipping date (2 business days from now)
        shipping_date := CURRENT_DATE + INTERVAL '2 days';
        order_status := 'Confirmed';
        
    EXCEPTION
        WHEN others THEN
            order_status := 'Failed: ' || SQLERRM;
            order_id := 0;
    END;
END;
$$;

-- Test the order processing
DO $$
DECLARE
    balance DECIMAL := 1000.00;
    order_num INTEGER;
    status TEXT;
    ship_date DATE;
BEGIN
    CALL process_customer_order(1, 1, 2, balance, order_num, status, ship_date);
    RAISE NOTICE 'Order: %, Status: %, Ship Date: %, Remaining Balance: %',
        order_num, status, ship_date, balance;
END;
$$;
```

### Example 2: Inventory Management System
```sql
CREATE OR REPLACE PROCEDURE manage_inventory(
    IN action VARCHAR,  -- 'ADD', 'REMOVE', 'TRANSFER'
    IN product_code VARCHAR,
    IN quantity INTEGER,
    IN source_location VARCHAR DEFAULT NULL,
    IN destination_location VARCHAR DEFAULT NULL,
    OUT remaining_stock INTEGER,
    OUT operation_status TEXT,
    OUT transaction_id INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    current_stock INTEGER;
    product_name VARCHAR;
BEGIN
    -- Initialize OUT parameters
    remaining_stock := 0;
    operation_status := 'Unknown';
    transaction_id := 0;
    
    -- Get current product information
    SELECT name, quantity_in_stock INTO product_name, current_stock
    FROM inventory WHERE code = product_code;
    
    IF product_name IS NULL THEN
        operation_status := 'Error: Product not found';
        RETURN;
    END IF;
    
    CASE action
        WHEN 'ADD' THEN
            UPDATE inventory 
            SET quantity_in_stock = quantity_in_stock + quantity
            WHERE code = product_code
            RETURNING quantity_in_stock INTO remaining_stock;
            
            INSERT INTO inventory_transactions 
                (product_code, transaction_type, quantity, location)
            VALUES 
                (product_code, 'STOCK_ADD', quantity, source_location)
            RETURNING id INTO transaction_id;
            
            operation_status := 'Stock added successfully';
            
        WHEN 'REMOVE' THEN
            IF current_stock < quantity THEN
                operation_status := 'Error: Insufficient stock';
                remaining_stock := current_stock;
                RETURN;
            END IF;
            
            UPDATE inventory 
            SET quantity_in_stock = quantity_in_stock - quantity
            WHERE code = product_code
            RETURNING quantity_in_stock INTO remaining_stock;
            
            INSERT INTO inventory_transactions 
                (product_code, transaction_type, quantity, location)
            VALUES 
                (product_code, 'STOCK_REMOVE', quantity, source_location)
            RETURNING id INTO transaction_id;
            
            operation_status := 'Stock removed successfully';
            
        WHEN 'TRANSFER' THEN
            IF source_location IS NULL OR destination_location IS NULL THEN
                operation_status := 'Error: Source and destination locations required';
                RETURN;
            END IF;
            
            -- Complex transfer logic here
            operation_status := 'Transfer initiated';
            
        ELSE
            operation_status := 'Error: Invalid action';
    END CASE;
    
    RAISE NOTICE 'Inventory operation: % - %', action, operation_status;
END;
$$;
```

## 8. Common Pitfalls <a name="common-pitfalls"></a>

### Pitfall 1: Redeclaring OUT Parameters
```sql
-- ❌ WRONG - Redeclearing OUT parameter
CREATE OR REPLACE PROCEDURE bad_example(OUT result INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
    result INTEGER := 0;  -- ERROR: conflicting declarations
BEGIN
    -- ...
END;
$$;

-- ✅ CORRECT - OUT parameters are automatically declared
CREATE OR REPLACE PROCEDURE good_example(OUT result INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    result := 0;  -- Initialize in BEGIN section
    -- ...
END;
$$;
```

### Pitfall 2: Forgetting to Initialize OUT Parameters
```sql
-- ❌ WRONG - OUT parameter might not get initialized
CREATE OR REPLACE PROCEDURE risky_example(
    IN condition BOOLEAN, 
    OUT result INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF condition THEN
        result := 42;
    END IF;
    -- If condition is false, result remains NULL!
END;
$$;

-- ✅ CORRECT - Always initialize OUT parameters
CREATE OR REPLACE PROCEDURE safe_example(
    IN condition BOOLEAN, 
    OUT result INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    result := 0;  -- Always initialize
    IF condition THEN
        result := 42;
    END IF;
END;
$$;
```

### Pitfall 3: Misunderstanding INOUT Behavior
```sql
-- Understanding INOUT modification
CREATE OR REPLACE PROCEDURE inout_demo(INOUT value INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE NOTICE 'Initial value inside procedure: %', value;
    value := value * 2;
    RAISE NOTICE 'Modified value inside procedure: %', value;
END;
$$;

DO $$
DECLARE
    num INTEGER := 10;
BEGIN
    RAISE NOTICE 'Before call: %', num;
    CALL inout_demo(num);
    RAISE NOTICE 'After call: %', num;  -- Will show 20
END;
$$;
```

This comprehensive guide covers all aspects of using IN, OUT, and INOUT parameters in PostgreSQL. Practice with these examples to master parameter usage in your stored procedures!
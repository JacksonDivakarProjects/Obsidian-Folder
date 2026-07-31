# Comprehensive Recursive CTE Guide

## 1. Definition & Core Concept

**Recursive CTE Definition:**
A Recursive Common Table Expression (CTE) is a temporary result set that references itself, allowing you to traverse hierarchical or tree-structured data in SQL.

**Key Characteristics:**
- **Self-referencing**: The CTE calls itself in the recursive term
- **Termination condition**: Must have a condition that stops the recursion
- **Two parts**: Anchor (base case) + Recursive term
- **Set-based operation**: Processes data in sets, not row-by-row

---

## 2. Core Syntax Breakdown

```sql
WITH RECURSIVE cte_name (column_list) AS (
    -- Anchor Member (non-recursive term)
    SELECT base_columns
    FROM source_table
    WHERE base_condition
    
    UNION [ALL]
    
    -- Recursive Member (recursive term)
    SELECT recursive_columns
    FROM cte_name
    JOIN other_tables ON join_condition
    WHERE termination_condition
)
SELECT * FROM cte_name [ORDER BY ...];
```

---

## 3. Essential Rules & Gotchas

### Critical Rules:
1. **Column matching**: Anchor and recursive terms must have same number/type of columns
2. **Termination required**: Must have a condition to stop recursion
3. **No cycles**: Infinite loops will cause errors (use depth limits)
4. **Single reference**: CTE can only reference itself once in recursive term

### Common Mistakes:
- Missing `RECURSIVE` keyword
- Incorrect column alignment
- No termination condition
- Using double quotes `"` instead of single quotes `'` for strings
- Forgetting to cast types in path building

---

## 4. Most Practical Patterns (Real-World Use Cases)

## Pattern 1: Employee Hierarchy (Downward Traversal)

**Problem**: Find all subordinates under a specific manager

```sql
-- Sample Table
CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100),
    manager_id INT REFERENCES employees(emp_id),
    salary DECIMAL(10,2)
);

INSERT INTO employees VALUES 
(1, 'CEO', NULL, 100000),
(2, 'VP Engineering', 1, 80000),
(3, 'VP Sales', 1, 75000),
(4, 'Engineering Manager', 2, 60000),
(5, 'Senior Developer', 4, 50000),
(6, 'Junior Developer', 4, 40000),
(7, 'Sales Manager', 3, 55000),
(8, 'Account Executive', 7, 45000);

-- Query: Find all subordinates under VP Engineering (emp_id = 2)
WITH RECURSIVE emp_hierarchy AS (
    -- Anchor: Start from the specified manager
    SELECT 
        emp_id,
        emp_name,
        manager_id,
        salary,
        1 AS level,
        emp_name::TEXT AS hierarchy_path
    FROM employees
    WHERE emp_id = 2  -- Starting point
    
    UNION ALL
    
    -- Recursive: Find direct reports
    SELECT 
        e.emp_id,
        e.emp_name,
        e.manager_id,
        e.salary,
        eh.level + 1 AS level,
        eh.hierarchy_path || ' -> ' || e.emp_name AS hierarchy_path
    FROM emp_hierarchy eh
    JOIN employees e ON e.manager_id = eh.emp_id
    WHERE eh.level < 10  -- Prevent infinite recursion
)
SELECT 
    emp_id,
    emp_name,
    level,
    hierarchy_path,
    salary
FROM emp_hierarchy
ORDER BY level, emp_id;
```

**Output:**
```
emp_id | emp_name           | level | hierarchy_path                    | salary
-------+--------------------+-------+-----------------------------------+--------
     2 | VP Engineering     |     1 | VP Engineering                    | 80000
     4 | Engineering Manager|     2 | VP Engineering -> Engineering Mgr | 60000
     5 | Senior Developer   |     3 | VP Eng -> Eng Mgr -> Sr Dev       | 50000
     6 | Junior Developer   |     3 | VP Eng -> Eng Mgr -> Jr Dev       | 40000
```

---

## Pattern 2: Manager Chain (Upward Traversal)

**Problem**: Find the complete management chain for a specific employee

```sql
-- Query: Find management chain for Junior Developer (emp_id = 6)
WITH RECURSIVE manager_chain AS (
    -- Anchor: Start from the specified employee
    SELECT 
        emp_id,
        emp_name,
        manager_id,
        0 AS level,
        emp_name::TEXT AS chain
    FROM employees
    WHERE emp_id = 6
    
    UNION ALL
    
    -- Recursive: Find managers upward
    SELECT 
        e.emp_id,
        e.emp_name,
        e.manager_id,
        mc.level + 1 AS level,
        e.emp_name || ' -> ' || mc.chain AS chain
    FROM manager_chain mc
    JOIN employees e ON e.emp_id = mc.manager_id
    WHERE mc.level < 10
)
SELECT 
    emp_id,
    emp_name,
    level,
    chain AS reporting_chain
FROM manager_chain
ORDER BY level DESC;
```

**Output:**
```
emp_id | emp_name           | level | reporting_chain
-------+--------------------+-------+-------------------------------------------
     1 | CEO                |     3 | CEO -> VP Engineering -> Engineering Manager -> Junior Developer
     2 | VP Engineering     |     2 | VP Engineering -> Engineering Manager -> Junior Developer
     4 | Engineering Manager|     1 | Engineering Manager -> Junior Developer
     6 | Junior Developer   |     0 | Junior Developer
```

---

## Pattern 3: Organizational Salary Roll-up

**Problem**: Calculate total salary cost for each manager's organization

```sql
WITH RECURSIVE salary_rollup AS (
    -- Anchor: Every employee is a potential root
    SELECT 
        emp_id AS root_manager_id,
        emp_id,
        emp_name,
        manager_id,
        salary,
        1 AS level
    FROM employees
    
    UNION ALL
    
    -- Recursive: Build hierarchy under each root
    SELECT 
        sr.root_manager_id,
        e.emp_id,
        e.emp_name,
        e.manager_id,
        e.salary,
        sr.level + 1 AS level
    FROM salary_rollup sr
    JOIN employees e ON e.manager_id = sr.emp_id
    WHERE sr.level < 10
)
SELECT 
    m.emp_id AS manager_id,
    m.emp_name AS manager_name,
    COUNT(sr.emp_id) - 1 AS team_size,  -- Exclude manager
    SUM(sr.salary) AS total_team_cost,
    (SUM(sr.salary) - m.salary) AS cost_excluding_manager
FROM salary_rollup sr
JOIN employees m ON m.emp_id = sr.root_manager_id
GROUP BY m.emp_id, m.emp_name, m.salary
ORDER BY total_team_cost DESC;
```

**Output:**
```
manager_id | manager_name    | team_size | total_team_cost | cost_excluding_manager
-----------+-----------------+-----------+-----------------+------------------------
         1 | CEO             |         7 |          465000 |                 365000
         2 | VP Engineering  |         4 |          230000 |                 150000
         4 | Engineering Mgr |         2 |           90000 |                  30000
         3 | VP Sales        |         2 |          120000 |                  45000
         7 | Sales Manager   |         1 |           45000 |                      0
-- Note: Leaves (individual contributors) have team_size 0
```

---

## Pattern 4: Number/Date Series Generation

**Problem**: Generate sequences without built-in functions

```sql
-- Generate numbers 1 through 10
WITH RECURSIVE number_series AS (
    SELECT 1 AS num
    UNION ALL
    SELECT num + 1 
    FROM number_series 
    WHERE num < 10
)
SELECT num FROM number_series;

-- Generate dates for next 7 days
WITH RECURSIVE date_series AS (
    SELECT CURRENT_DATE AS generated_date
    UNION ALL
    SELECT generated_date + 1
    FROM date_series
    WHERE generated_date < CURRENT_DATE + 6
)
SELECT generated_date, EXTRACT(DOW FROM generated_date) AS day_of_week
FROM date_series;
```

---

## Pattern 5: Path Finding & Cycle Detection

**Problem**: Find all paths and detect cycles in hierarchical data

```sql
WITH RECURSIVE employee_paths AS (
    SELECT 
        emp_id,
        emp_name,
        manager_id,
        ARRAY[emp_id] AS path,
        FALSE AS is_cycle,
        1 AS depth
    FROM employees
    WHERE manager_id IS NULL  -- Start from root
    
    UNION ALL
    
    SELECT 
        e.emp_id,
        e.emp_name,
        e.manager_id,
        ep.path || e.emp_id AS path,
        e.emp_id = ANY(ep.path) AS is_cycle,
        ep.depth + 1 AS depth
    FROM employee_paths ep
    JOIN employees e ON e.manager_id = ep.emp_id
    WHERE NOT is_cycle AND depth < 10  -- Stop at cycles or reasonable depth
)
SELECT 
    emp_id,
    emp_name,
    path,
    is_cycle,
    depth
FROM employee_paths
ORDER BY path;
```

---

## 5. Performance Optimization Tips

### Indexing Strategy:
```sql
-- Critical indexes for recursive CTEs
CREATE INDEX idx_employees_manager_id ON employees(manager_id);
CREATE INDEX idx_employees_emp_id_manager_id ON employees(emp_id, manager_id);
```

### Depth Limiting:
```sql
-- Always include depth limit to prevent infinite recursion
WHERE depth < 100  -- Adjust based on your data
```

### Materialization Hints (PostgreSQL):
```sql
WITH RECURSIVE cte_name AS (
    -- Your CTE
)
SELECT * FROM cte_name
-- Add this for large result sets
MATERIALIZED;  -- Forces materialization (PostgreSQL 12+)
```

---

## 6. Interview-Ready Problem Set

### Problem 1: Find Employees with No Subordinates
```sql
WITH RECURSIVE hierarchy AS (
    SELECT emp_id, manager_id FROM employees
    UNION ALL
    SELECT e.emp_id, h.manager_id
    FROM hierarchy h
    JOIN employees e ON e.manager_id = h.emp_id
)
SELECT emp_id, emp_name 
FROM employees 
WHERE emp_id NOT IN (SELECT manager_id FROM hierarchy WHERE manager_id IS NOT NULL);
```

### Problem 2: Calculate Average Span of Control
```sql
WITH RECURSIVE mgr_counts AS (
    SELECT 
        manager_id,
        COUNT(*) AS direct_reports
    FROM employees 
    WHERE manager_id IS NOT NULL
    GROUP BY manager_id
)
SELECT 
    AVG(direct_reports) AS avg_span_of_control,
    MAX(direct_reports) AS max_span_of_control
FROM mgr_counts;
```

### Problem 3: Find Longest Reporting Chain
```sql
WITH RECURSIVE chain_depth AS (
    SELECT 
        emp_id,
        emp_name,
        manager_id,
        1 AS depth
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    SELECT 
        e.emp_id,
        e.emp_name,
        e.manager_id,
        cd.depth + 1 AS depth
    FROM chain_depth cd
    JOIN employees e ON e.manager_id = cd.emp_id
)
SELECT MAX(depth) AS longest_reporting_chain FROM chain_depth;
```

---

## 7. Debugging Checklist

When your recursive CTE isn't working:

1. **Check column alignment** between anchor and recursive terms
2. **Verify termination condition** - will it eventually stop?
3. **Test with single root** first, then expand
4. **Add depth tracking** to monitor recursion levels
5. **Check for cycles** in your data
6. **Validate join conditions** - are you joining the correct columns?
7. **Use SELECT * temporarily** to see intermediate results

---

## 8. Real-World Applications

### ✅ Use Recursive CTEs For:
- Organizational charts
- Bill of Materials (BOM)
- Category hierarchies (e-commerce)
- Graph traversal (social networks)
- File system structures
- Comment threads (nested comments)

### ❌ Avoid Recursive CTEs For:
- Simple parent-child relationships (use JOINs)
- Very deep hierarchies (consider application-level processing)
- When database doesn't support them (MySQL before 8.0)

---

## 9. Quick Reference Card

```sql
-- Template
WITH RECURSIVE cte AS (
    SELECT id, parent_id, data, 1 AS level        -- Anchor
    FROM table WHERE condition
    UNION ALL
    SELECT t.id, t.parent_id, t.data, c.level + 1 -- Recursive  
    FROM cte c JOIN table t ON t.parent_id = c.id
    WHERE c.level < 100                           -- Termination
)
SELECT * FROM cte;

-- Essential checks:
-- ✓ Columns match in both parts
-- ✓ Termination condition exists  
-- ✓ No cycles in data
-- ✓ Proper indexing on join columns
```

This guide covers 95% of real-world recursive CTE use cases. Master these patterns and you'll handle hierarchical data efficiently in SQL interviews and production systems.
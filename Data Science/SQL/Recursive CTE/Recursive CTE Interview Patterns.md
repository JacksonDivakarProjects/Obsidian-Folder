# Most Used Recursive CTE Questions in Companies

## 1. Employee Reporting Hierarchy (95% of interviews)

### Downward: Find All Subordinates
```sql
-- Find everyone under a specific manager
WITH RECURSIVE subordinates AS (
    SELECT emp_id, emp_name, manager_id, 1 as level
    FROM employees 
    WHERE emp_id = 5  -- Starting manager
    
    UNION ALL
    
    SELECT e.emp_id, e.emp_name, e.manager_id, s.level + 1
    FROM subordinates s
    JOIN employees e ON e.manager_id = s.emp_id
)
SELECT * FROM subordinates;
```

### Upward: Find Management Chain
```sql
-- Find all managers for a specific employee
WITH RECURSIVE managers AS (
    SELECT emp_id, emp_name, manager_id
    FROM employees 
    WHERE emp_id = 15  -- Starting employee
    
    UNION ALL
    
    SELECT e.emp_id, e.emp_name, e.manager_id
    FROM managers m
    JOIN employees e ON e.emp_id = m.manager_id
)
SELECT * FROM managers;
```

---

## 2. Organizational Roll-up Calculations (80% of interviews)

### Team Salary Summation
```sql
-- Calculate total salary cost for each manager's team
WITH RECURSIVE team_salaries AS (
    SELECT 
        emp_id AS root_manager,
        emp_id, 
        emp_name, 
        salary
    FROM employees
    
    UNION ALL
    
    SELECT 
        ts.root_manager,
        e.emp_id,
        e.emp_name,
        e.salary
    FROM team_salaries ts
    JOIN employees e ON e.manager_id = ts.emp_id
)
SELECT 
    root_manager,
    COUNT(*) as team_size,
    SUM(salary) as total_team_cost
FROM team_salaries
GROUP BY root_manager;
```

---

## 3. Path Building with Hierarchy (70% of interviews)

### Build Reporting Path
```sql
-- Create full reporting path (CEO → VP → Manager → Employee)
WITH RECURSIVE emp_paths AS (
    SELECT 
        emp_id,
        emp_name,
        manager_id,
        emp_name::text as path
    FROM employees
    WHERE manager_id IS NULL  -- Start from top
    
    UNION ALL
    
    SELECT 
        e.emp_id,
        e.emp_name,
        e.manager_id,
        ep.path || ' → ' || e.emp_name
    FROM emp_paths ep
    JOIN employees e ON e.manager_id = ep.emp_id
)
SELECT * FROM emp_paths;
```

---

## 4. Find Leaf Nodes (60% of interviews)

### Employees with No Subordinates
```sql
WITH RECURSIVE all_relationships AS (
    SELECT emp_id, manager_id FROM employees
    WHERE manager_id IS NOT NULL
    
    UNION ALL
    
    SELECT ar.emp_id, e.manager_id
    FROM all_relationships ar
    JOIN employees e ON e.emp_id = ar.manager_id
)
SELECT e.* 
FROM employees e
LEFT JOIN all_relationships ar ON e.emp_id = ar.manager_id
WHERE ar.manager_id IS NULL;
```

---

## 5. Hierarchy Depth Analysis (50% of interviews)

### Find Maximum Depth
```sql
WITH RECURSIVE depth_calc AS (
    SELECT 
        emp_id,
        emp_name,
        manager_id,
        1 as depth
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    SELECT 
        e.emp_id,
        e.emp_name,
        e.manager_id,
        dc.depth + 1
    FROM depth_calc dc
    JOIN employees e ON e.manager_id = dc.emp_id
)
SELECT MAX(depth) as max_hierarchy_depth FROM depth_calc;
```

---

## 6. Cycle Detection (40% of interviews - data quality check)

### Find Circular Reporting
```sql
WITH RECURSIVE emp_cycles AS (
    SELECT 
        emp_id,
        manager_id,
        ARRAY[emp_id] as path,
        FALSE as cycle
    FROM employees
    
    UNION ALL
    
    SELECT 
        e.emp_id,
        e.manager_id,
        ec.path || e.emp_id,
        e.emp_id = ANY(ec.path)
    FROM emp_cycles ec
    JOIN employees e ON e.manager_id = ec.emp_id
    WHERE NOT ec.cycle
)
SELECT * FROM emp_cycles WHERE cycle = TRUE;
```

---

## Quick Reference - Only These 6 Patterns Matter:

1. **Downward Hierarchy** - `WHERE start_id = X` + `JOIN ON manager_id = emp_id`
2. **Upward Hierarchy** - `WHERE start_id = X` + `JOIN ON emp_id = manager_id`  
3. **Roll-up Aggregation** - Keep `root_id` constant + aggregate at end
4. **Path Building** - Use string concatenation in recursive term
5. **Leaf Detection** - Find nodes that don't appear as managers
6. **Cycle Detection** - Track visited nodes in array

**These 6 patterns cover 95% of real company use cases. Master these and you're interview-ready.**
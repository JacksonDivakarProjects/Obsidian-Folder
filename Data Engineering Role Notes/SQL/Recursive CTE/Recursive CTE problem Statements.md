# Recursive CTE Problem Statements

Practical, interview-style recursive CTE questions for building fluency with hierarchical and self-referencing data.

## 1. Employee Hierarchy (Classic Org Chart)

Given `employees(emp_id, emp_name, manager_id)`, write a recursive CTE to display each employee along with their full reporting chain (CEO → … → employee).

## 2. Find All Subordinates of a Manager

Given the same table, return all employees under `manager_id = 10`, no matter how deep the hierarchy goes.

## 3. Generate a Number Series

Using a recursive CTE, generate numbers from 1 to 100 without a built-in sequence or `generate_series`.

## 4. Folder Structure / File Tree

Given `folders(id, folder_name, parent_id)`, write a recursive CTE to print the complete folder path for each folder, e.g. `root/docs/work/projectA`.

## 5. Sum of Salaries Under Each Manager

Given `employees(emp_id, manager_id, salary)`, calculate the total salary cost of each manager's entire team, including indirect reports.

## 6. Organization Depth Calculation

Find the maximum depth of the employee hierarchy using a recursive CTE (e.g., `max_depth = 5`).

## 7. Parent → Child Path Flattening

Given `category(id, name, parent_id)`, write a recursive CTE that returns category levels as a path, e.g. `Electronics > Mobile > Smartphones`.

## 8. Detect Cycles in Hierarchy

Using recursive CTE logic, detect whether any employee's `manager_id` chain creates a cycle.

## 9. Bill of Materials (BOM) Explosion

Given `products(component_id, child_component_id, quantity)`, generate a complete list of dependent components for a given product, including cumulative quantities.

## 10. Countdown Using Recursive CTE

Print numbers from 10 down to 1 using recursive CTE logic.

## 11. Compute Factorial Using Recursive CTE

Write a recursive CTE to compute the factorial of 10.

## 12. Pagination with Recursive CTE

Using a recursive CTE, split a table into chunks of 100 rows per page and number each page.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/Recursive CTE/Recursive CTE Notes|Comprehensive Recursive CTE Guide]]
- [[Data Engineering Role Notes/SQL/Recursive CTE/Recursive CTE Interview Patterns|Most Used Recursive CTE Questions in Companies]]

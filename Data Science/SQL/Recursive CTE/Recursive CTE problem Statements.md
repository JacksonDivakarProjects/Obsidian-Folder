Below are **practical, interview-style Recursive CTE questions** you can use to strengthen your SQL muscles. I kept them crisp, corporate, and straight to the point—these are the kind of problems that show real data-engineering maturity.

---

## **1. Employee Hierarchy (Classic Org Chart)**

**Question:**  
Given a table:

```sql
employees(emp_id, emp_name, manager_id)
```

Write a recursive CTE to display each employee along with their **full reporting chain** (CEO → … → employee).

---

## **2. Find All Subordinates of a Manager**

**Question:**  
Given the same table, return **all employees under manager_id = 10**, no matter how deep the hierarchy goes.

---

## **3. Generate a Number Series**

**Question:**  
Using a recursive CTE, generate numbers from **1 to 100** without using a built-in sequence or generate_series.

---

## **4. Folder Structure / File Tree**

**Question:**  
Given:

```sql
folders(id, folder_name, parent_id)
```

Write a recursive CTE to print the complete **folder path** for each folder, e.g.:

```
root/docs/work/projectA
```

---

## **5. Sum of Salaries Under Each Manager**

**Question:**  
Given:

```sql
employees(emp_id, manager_id, salary)
```

Calculate the **total salary cost** of each manager’s entire team (including indirect reports).

---

## **6. Organization Depth Calculation**

**Question:**  
Find the **maximum depth** of your employee hierarchy using a recursive CTE.

Example output:

```
max_depth = 5
```

---

## **7. Parent → Child Path Flattening**

**Question:**  
Given:

```sql
category(id, name, parent_id)
```

Write a recursive CTE to return category levels as:

```
Electronics > Mobile > Smartphones
```

---

## **8. Detect Cycles in Hierarchy**

**Question:**  
Using recursive CTE logic, detect if any employee’s manager_id creates a cycle.

---

## **9. Bill of Materials (BOM) Explosion**

**Question:**  
Given:

```sql
products(component_id, child_component_id, quantity)
```

Generate a **complete list of dependent components** for a given product, including cumulative quantities.

---

## **10. Countdown Using Recursive CTE**

**Question:**  
Print numbers **from 10 down to 1** using recursive CTE logic.

---

## **11. Compute Factorial Using Recursive CTE**

**Question:**  
Write a recursive CTE to compute **factorial of 10**.

---

## **12. Pagination with Recursive CTE**

**Question:**  
Using a recursive CTE, split a table into chunks of **100 rows per page** and number each page.

---

If you want, I can also provide:

✔ Fully worked-out answers  
✔ Visual diagrams of the recursion  
✔ More advanced real-world scenarios (e.g., graph traversal, lineage tracking, audit trails)

Just tell me **“give answers”** and I’ll deliver polished, ready-to-run solutions.


# 📘 SQL Views – The Complete Guide

---

## ✅ What is a View?

A **View** is a **virtual table** created by storing a SQL `SELECT` query under a name. It does **not store data itself**, but it displays real-time data from the base tables.

> Think of a view as a saved query that behaves like a table.

---

## 🔧 Syntax: Creating, Dropping, and Updating Views

### ✅ Create a View

```sql
CREATE VIEW view_name AS
SELECT column1, column2
FROM table_name
WHERE condition;
```

### ✅ Update or Replace a View

```sql
CREATE OR REPLACE VIEW view_name AS
SELECT ...;
```

This is useful when you want to **modify the query behind a view** without dropping it.

### ❌ Drop a View

```sql
DROP VIEW view_name;
```

---

## 🔄 Refreshing a View

### In MySQL:

- Views are always **virtual** — they pull **live data** from base tables.
    
- There's **no REFRESH command** because MySQL views are **not materialized**.
    
- To "refresh" a view in MySQL:
    
    > You simply **re-run the query** on the view.
    

### Example:

```sql
SELECT * FROM sales_summary_view;
```

This will always return the most current data from the `sales` table.

> ❌ No `REFRESH MATERIALIZED VIEW` in MySQL (available in PostgreSQL and Oracle).

---

## ✏️ Updating Data Through a View

### ⚠️ Not All Views Are Updatable

A view must meet strict conditions to be updatable.

### ✅ A View is Updatable **ONLY IF**:

- It is based on a **single table**
    
- It does **not use** any of the following:
    
    - `DISTINCT`
        
    - `GROUP BY`
        
    - `UNION`
        
    - `JOIN`
        
    - Aggregate functions like `SUM`, `AVG`, etc.
        
- It does **not contain**:
    
    - Subqueries in the `SELECT` clause
        
    - Derived/computed columns (e.g., `price * quantity`)
        

### 🔒 Enforcing Conditions with `WITH CHECK OPTION`

Use this to **enforce that all INSERTs and UPDATEs** through the view must match its `WHERE` clause:

```sql
CREATE VIEW hr_employees AS
SELECT * FROM employees
WHERE department = 'HR'
WITH CHECK OPTION;
```

- Ensures new/updated rows via the view cannot bypass the filter logic.
    

---

### ✅ Inserting Through a View (If Valid)

```sql
INSERT INTO hr_employees (id, name, department)
VALUES (5, 'Divakar', 'HR');
```

This inserts a row into the **employees** table **because** it satisfies the view's `WHERE` condition.

---

## 📃 Best Practices

|Practice|Reason|
|---|---|
|Use column names in `INSERT`|Safer if schema changes|
|Use `CREATE OR REPLACE`|Update views without dropping them|
|Grant least privilege|Use views to hide sensitive columns from users|

---

## 🎓 Interview-Ready Takeaways

- ✅ Views are virtual tables
    
- ✅ In MySQL, views are **auto-refreshed** by default (pull live data)
    
- ✅ Not all views are updatable
    
- ✅ Use `WITH CHECK OPTION` to prevent invalid inserts/updates
    
- ❌ No `REFRESH` in MySQL views
    
- ✅ Great for abstraction, security, and query reuse
    

---

Would you like this as a printable Markdown or PDF file?
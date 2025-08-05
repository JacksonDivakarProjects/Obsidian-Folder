

# 🧠 Materialized Views – The Complete Guide (PostgreSQL)

---

## ✅ What is a Materialized View?

A **Materialized View** is a **precomputed snapshot** of a query stored like a table in the database. It improves performance by storing the result of expensive queries.

> Unlike a normal view, it does **not show real-time data**. You need to **refresh** it to update the content.

---

## 🔧 Syntax: Creating, Dropping, and Refreshing Materialized Views

### ✅ Create a Materialized View

```sql
CREATE MATERIALIZED VIEW view_name AS
SELECT column1, column2, aggregate_function(column3)
FROM table_name
GROUP BY column1, column2;
```

### ❌ Drop a Materialized View

```sql
DROP MATERIALIZED VIEW view_name;
```

---

## 🔄 Refreshing a Materialized View

Materialized views must be **manually refreshed** to show the latest data.

### Manual Refresh

```sql
REFRESH MATERIALIZED VIEW view_name;
```

### Refresh Without Locking (Optional)

```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY view_name;
```

> Requires a **unique index** on the materialized view.

---

## 🧪 Example

### Step 1: Create the Materialized View

```sql
CREATE MATERIALIZED VIEW department_sales_summary AS
SELECT department_id, SUM(sale_amount) AS total_sales
FROM sales
GROUP BY department_id;
```

### Step 2: Query the Materialized View

```sql
SELECT * FROM department_sales_summary;
```

### Step 3: Refresh the Materialized View (to update the snapshot)

```sql
REFRESH MATERIALIZED VIEW department_sales_summary;
```

---

## 🔐 Read-Only Nature

Materialized views are usually **read-only**. You **cannot** perform:

- `INSERT`
    
- `UPDATE`
    
- `DELETE`
    

To modify data, update the base tables and then refresh the materialized view.

---

## 📃 Best Practices

|Practice|Reason|
|---|---|
|Use for costly aggregations or joins|Improves performance for complex queries|
|Schedule refresh during off-peak hours|Keeps view data up-to-date without impacting users|
|Use `CONCURRENTLY` if users are querying it|Avoids locking the view during refresh|
|Index the materialized view (if needed)|Required for concurrent refresh and better performance|

---

## 🎓 Interview-Ready Takeaways

- ✅ Materialized views store **precomputed data**
    
- ✅ Useful for **reporting, analytics, and dashboards**
    
- ✅ Faster access for aggregated or joined data
    
- ❌ PostgreSQL materialized views are **not auto-refreshed**
    
- ✅ Must be manually refreshed using `REFRESH MATERIALIZED VIEW`
    
- ❌ Not updatable via `INSERT`/`UPDATE`/`DELETE`
    
- ✅ Supports `CONCURRENTLY` refresh with a unique index
    

---

Let me know if you want to simulate materialized views in MySQL using tables + triggers.
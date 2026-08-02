
Here’s a crisp, professional note on **Change Data Feed (CDF) in Delta Lake** from a SQL perspective:

---

## **Delta Lake – Change Data Feed (CDF) in SQL**

**Definition:**  
Change Data Feed (CDF) in Delta Lake allows you to track **row-level changes** (inserts, updates, deletes) in a Delta table over time. It provides an incremental view of the changes, enabling downstream analytics, ETL, and replication processes.

---

### **Enabling Change Data Feed**

When creating a table:

```sql
CREATE TABLE sales (
    id INT,
    product STRING,
    quantity INT,
    price DECIMAL(10,2),
    updated_at TIMESTAMP
)
USING delta
TBLPROPERTIES (delta.enableChangeDataFeed = true);
```

For an **existing table**:

```sql
ALTER TABLE sales
SET TBLPROPERTIES (delta.enableChangeDataFeed = true);
```

> ✅ **Note:** CDF must be enabled before changes occur. It **cannot track changes retroactively**.

---

### **Querying Changes**

1. **Get all changes from a specific version:**
    

```sql
SELECT *
FROM table_changes('sales', 1); -- version 1 onwards
```

- `table_changes(table_name, version)` returns a **CDF view** with `_change_type` column:
    
    - `insert`
        
    - `update_preimage`
        
    - `update_postimage`
        
    - `delete`
        

2. **Filter only inserts/updates/deletes**:
    

```sql
SELECT *
FROM table_changes('sales', 1)
WHERE _change_type = 'update_postimage';
```

---

### **Use Cases**

- Incremental ETL pipelines
    
- Real-time analytics dashboards
    
- Data replication between systems
    
- Auditing and compliance
    

---

### **Best Practices**

- Retain **enough historical versions**: CDF relies on Delta Lake’s versioning.
    
- Combine with **Z-Ordering or partitioning** for better query performance.
    
- Use **time-travel** carefully for large datasets; CDF works best incrementally.
    

---

If you want, I can also draft a **compact SQL cheat-sheet for Delta Lake CDF** that covers **create, alter, query, and best practices** all in one table. It will be extremely handy for quick reference.

Do you want me to do that?

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Questions/How Versioning Works in Delta Lake|How Versioning Works in Delta Lake]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Delta Live Tables/AutoCDC API/AutoCDC in DLT|AutoCDC in DLT]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 05/Snapshots & Change Tracking|Snapshots & Change Tracking]]

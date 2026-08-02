## Delta Live Tables (DLT) CDC — Refined Guide

---

## 1. Core Concept

CDC streams contain **data rows + metadata columns**.  
`operation` is **not syntax** — it is a **column in the source data**.

Example incoming row:

```id="u6y8k3"
userId = 101
name = "Jack"
operation = "DELETE"
event_timestamp = "2024-01-01 10:00:00"
```

DLT reads this row and decides **what action to perform** based on the **value inside the `operation` column**.

---

## 2. Architecture

```id="7w7w0g"
CDC Source Table (with operation column)
        ↓
Streaming View
        ↓
Auto CDC Flow (interprets column values)
        ↓
Target Table (final state)
```

---

## 3. Complete Example

```python
dp.create_auto_cdc_flow(
  target = "users_current",
  source = "users",
  keys = ["userId"],
  sequence_by = col("event_timestamp"),
  apply_as_deletes = expr("operation = 'DELETE'"),
  apply_as_truncates = expr("operation = 'TRUNCATE'"),
  except_column_list = ["operation", "event_timestamp"],
  stored_as_scd_type = 1
)
```

---

## 4. What `operation` Actually Is

- A **column in your dataset**
    
- Contains values like:
    
    - `"INSERT"`
        
    - `"UPDATE"`
        
    - `"DELETE"`
        
    - `"TRUNCATE"`
        

DLT does **not assume meaning automatically**.  
You must define how to interpret these values.

---

## 5. `apply_as_deletes` — Clear Explanation

```python
apply_as_deletes = expr("operation = 'DELETE'")
```

### What this means

- For each row, DLT checks:
    
    - Does the **operation column value equal 'DELETE'?**
        

### If TRUE

- DLT performs a **DELETE in the target table**
    

### If FALSE

- Row is treated as normal (insert/update)
    

---

### Important interpretation

This is **not assignment**.  
It is a **condition evaluated on a column**.

Equivalent logic:

```id="2h3l0k"
if row.operation == "DELETE":
    delete from target
```

---

### Example

Incoming row:

```id="d2xk5o"
userId = 101
operation = "DELETE"
```

Action:

```id="r8o3lz"
DELETE FROM users_current WHERE userId = 101
```

---

## 6. `apply_as_truncates` — Clear Explanation

```python
apply_as_truncates = expr("operation = 'TRUNCATE'")
```

### What this means

- For each row, DLT checks:
    
    - Does `operation` column equal `"TRUNCATE"`?
        

### If TRUE

- Entire target table is cleared
    

---

### Equivalent logic

```id="m1r9yt"
if row.operation == "TRUNCATE":
    truncate entire table
```

---

### Example

Incoming row:

```id="p4k8bz"
operation = "TRUNCATE"
```

Action:

```id="4az6qv"
TRUNCATE TABLE users_current
```

---

## 7. Why Expression (`expr`) Is Used

```python
expr("operation = 'DELETE'")
```

- Defines a **boolean condition on a column**
    
- Evaluated **row by row**
    
- Can be customized
    

---

### Custom column examples

If your dataset uses different column names:

```python
expr("op_type = 'D'")
expr("event = 'REMOVE'")
expr("is_deleted = true")
```

---

## 8. Execution Order (Critical)

For each incoming row:

```id="6k2n8f"
1. Check TRUNCATE condition
2. Check DELETE condition
3. Else → UPSERT (insert/update)
```

---

## 9. UPSERT Behavior (Default)

If neither condition matches:

- INSERT → new row
    
- UPDATE → overwrite existing row
    

---

## 10. Role of `sequence_by`

```python
sequence_by = col("event_timestamp")
```

- Orders events per key
    
- Ensures latest change wins
    

Example:

```id="3s8k1q"
userId = 1 → UPDATE at 10:00
userId = 1 → DELETE at 10:05
```

Final result:

```id="j2m0nx"
Row is deleted (latest event applied)
```

---

## 11. Role of `keys`

```python
keys = ["userId"]
```

- Identifies which row to update/delete
    
- Used in merge condition
    

---

## 12. Column Removal

```python
except_column_list = ["operation", "event_timestamp"]
```

- Removes metadata columns from final table
    
- Keeps only business data
    

---

## 13. Internal Execution Model

DLT transforms logic into:

```sql
MERGE INTO users_current t
USING users s
ON t.userId = s.userId

WHEN MATCHED AND s.operation = 'DELETE' THEN DELETE
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
```

- ordering using timestamp
    

---

## 14. What Happens If You Skip These

### No `apply_as_deletes`

- DELETE rows treated as updates
    
- No deletion occurs
    

---

### No `apply_as_truncates`

- TRUNCATE ignored
    
- Table never cleared
    

---

### No `operation` column

- No way to detect delete/truncate
    
- Only upserts possible
    

---

## 15. Mental Model

Each incoming row:

```id="4n6y1r"
Read column values → Evaluate condition → Perform action
```

|operation column value|action|
|---|---|
|DELETE|delete row|
|TRUNCATE|clear table|
|others|upsert|

---

## 16. Key Insight

These lines:

```python
expr("operation = 'DELETE'")
expr("operation = 'TRUNCATE'")
```

do **not define syntax rules** —  
they define **how to interpret a column's value as a database operation**.

---

## 17. Final Principle

CDC system = **data + meaning**

- Data → rows
    
- Meaning → defined by your conditions
    

Without defining meaning → system cannot apply correct actions

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Delta Live Tables/Delta Live Tables|Delta Live Tables (DLT) Comprehensive Guide]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Important TBLProperties/Change Data Feed|Delta Lake – Change Data Feed]]

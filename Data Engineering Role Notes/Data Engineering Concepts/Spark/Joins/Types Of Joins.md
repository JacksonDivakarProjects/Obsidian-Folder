Great question 👍 — joins in Spark can be a little tricky, because Spark chooses different strategies depending on **data size** and **cluster resources**. Let’s break down **where and when Hash Join and Sort-Merge Join are applied**.

---

## **1. Types of Joins in Spark**

Spark SQL (and DataFrame/Dataset API) mainly uses three join strategies:

1. **Broadcast Hash Join (BHJ)** – if one table is small.
    
2. **Shuffle Hash Join (SHJ)** – if both tables are big, but hash join is still cheaper than sort.
    
3. **Sort-Merge Join (SMJ)** – default when both tables are large.
    

---

## **2. Hash Join (Broadcast or Shuffle)**

- Spark builds a **hash table on the join keys** from the smaller side.
    
- Then it probes this hash table with records from the larger side.
    

### **When used:**

- **Broadcast Hash Join (BHJ):**
    
    - If one side is small enough (default < **10 MB** in Spark, configurable via `spark.sql.autoBroadcastJoinThreshold`).
        
    - The small table is **broadcasted** to all executors, avoiding shuffle.
        
    - Very fast because it skips network shuffle.
        
- **Shuffle Hash Join (SHJ):**
    
    - If both tables are large but hash join is estimated to be cheaper than sort-merge.
        
    - Spark will **shuffle both tables** by join key, then do hash join per partition.
        
    - Usually chosen when join keys are well-distributed (low skew).
        

---

## **3. Sort-Merge Join (SMJ)**

- Both sides are **shuffled by join key** and then **sorted** before joining.
    
- Works well for very large datasets because sorting scales better than hashing when data is huge.
    

### **When used:**

- Default join if both sides are large and no broadcast is possible.
    
- When Spark **cannot do hash join** (e.g., due to memory limits or skew).
    
- Good for equality joins on big data.
    

---

## **4. Rule of Thumb**

- **Small + Large table → Broadcast Hash Join**
    
- **Large + Large table (fits in memory for hashing) → Shuffle Hash Join**
    
- **Large + Large table (too big for hash) → Sort-Merge Join**
    

---

## **5. Example**

```python
df1.join(df2, "id")  # Spark decides the join strategy

# Control join strategy:
spark.conf.set("spark.sql.join.preferSortMergeJoin", "false")
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)
```

---

✅ **Quick Notes:**

- **Broadcast Hash Join** = fastest, avoids shuffle, used when one side is small.
    
- **Shuffle Hash Join** = used for big-big joins when hashing is cheaper.
    
- **Sort-Merge Join** = default for large joins, robust but involves sorting overhead.
    

---

Do you want me to also show you **how to check in Spark which join strategy was actually used** (using the `explain()` plan)? That way you can see if Spark picked hash join or sort-merge for your query.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Joins/Shuffle Hash Join|Shuffle Hash Join]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Miscellaneous/Job, Stages and Tasks|Spark Execution: Job, Stages and Tasks]]

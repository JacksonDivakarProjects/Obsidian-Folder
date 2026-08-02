Perfect, Jack 👌 — let’s lock in on **Executor Out-Of-Memory (OOM)**, this time including **salting** as a mitigation technique. I’ll keep it tight, structured, and focused only on essentials.

---

# ⚡ Executor Out-Of-Memory (OOM) in Spark

---

## 1) What is Executor OOM?

- Executors run **tasks** and hold **cached/shuffled data**.
    
- Executor OOM happens when **heap / off-heap memory** is exhausted.
    
- Unlike driver OOM (which kills the app immediately), executor OOM:
    
    - Causes **task failures**, retries, and eventually job failure if retries exceed.
        

---

## 2) Common Causes of Executor OOM

### 🔹 1. Skewed Data (Biggest Culprit)

- Few keys/partitions get **huge data**, while others stay small.
    
- Example: `groupByKey()`, `reduceByKey()` → one hot key fills executor memory.
    

---

### 🔹 2. Large Shuffles

- Joins, groupBy, reduceByKey generate shuffle data.
    
- If shuffle spill > memory, disk IO explodes, and OOM may occur if buffers grow.
    

---

### 🔹 3. Wide Transformations + Caching

- Persisting large intermediate RDD/DataFrame without enough memory.
    
- Executors try to keep blocks in memory → heap fills up.
    

---

### 🔹 4. Large UDF Outputs

- Exploding data in UDFs (e.g., one input row → millions of output rows).
    

---

### 🔹 5. Insufficient Executor Memory Settings

- `spark.executor.memory` or `spark.memoryOverhead` too low.
    
- Not enough space for shuffle buffers, Python workers, Arrow, etc.
    

---

## 3) Symptoms of Executor OOM

- Logs:
    
    - `java.lang.OutOfMemoryError: Java heap space`
        
    - `java.lang.OutOfMemoryError: GC overhead limit exceeded`
        
- Frequent **task retries** → eventually job fails.
    
- Spark UI → stages show **skewed tasks** with very high runtime & spill.
    

---

## 4) Strategies to Handle Executor OOM

### 🔹 A. Handle Skew (Salting 🔑)

- **Salting** = add random prefix to skewed key → distribute load across partitions.
    

**Example (Salting for groupByKey):**

```python
from pyspark.sql import functions as F

# Add salt for skewed key
salted = df.withColumn(
    "salted_key", 
    F.concat(F.col("key"), F.lit("_"), (F.rand()*10).cast("int"))
)

# Do aggregation on salted keys
agg_salted = salted.groupBy("salted_key").agg(F.sum("value"))

# Remove salt after aggregation
final = agg_salted.withColumn(
    "key", F.split("salted_key", "_")[0]
).groupBy("key").agg(F.sum("sum(value)"))
```

- Skewed key "A" is now spread across 10 partitions instead of one.
    

---

### 🔹 B. Use Better Joins

- Replace **shuffle-heavy joins** with **broadcast joins** if one side is small.
    
    ```python
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "100MB")
    ```
    
- Avoid cartesian joins.
    

---

### 🔹 C. Optimize Caching

- Cache only when reused.
    
- Use `DISK_ONLY` or `MEMORY_AND_DISK` instead of `MEMORY_ONLY` if data is large.
    

---

### 🔹 D. Partitioning

- Repartition skewed data properly.
    
- Use `df.repartition(n)` to increase parallelism before heavy aggregations.
    

---

### 🔹 E. Executor Memory Tuning

- Increase executor memory (heap):
    
    ```bash
    --executor-memory 4g --conf spark.executor.memoryOverhead=1g
    ```
    
- Right-size number of cores per executor (too many cores = memory contention).
    

---

### 🔹 F. Spill Management

- Ensure shuffle spill writes efficiently:
    
    - Use **Kryo serialization** (`spark.serializer=org.apache.spark.serializer.KryoSerializer`).
        
    - Ensure sufficient `spark.memory.fraction` for execution vs storage.
        

---

## 5) Quick Checklist for Executor OOM

-  Identify skewed keys → **apply salting**.
    
-  Use broadcast join for small tables.
    
-  Don’t over-cache → pick smart storage levels.
    
-  Repartition data before shuffles.
    
-  Tune executor heap + memory overhead.
    
-  Monitor Spark UI → check skewed tasks & shuffle spill.
    

---

✅ **In short**:  
Executor OOM = **data skew + shuffle pressure + bad configs**.  
Fix = **spread skewed keys with salting**, use smart joins, tune executor memory, and cache wisely.

---

Jack — do you want me to also show you **a visual way to detect skewed partitions in Spark UI** (so you know when salting is needed), or keep it purely conceptual?

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Executer Memory Management|Spark Executor Memory Architecture]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Driver OOM|Driver Out-Of-Memory (OOM) in Spark]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Joins/Shuffle Hash Join|Shuffle Hash Join]]

# Executor Out-Of-Memory (OOM) in Spark

## 1. What Is Executor OOM?
- Executors run tasks and hold cached/shuffled data.
- Executor OOM happens when heap or off-heap memory is exhausted.
- Unlike driver OOM (which kills the whole app immediately), executor OOM causes task failures and retries, and only fails the job once retries are exhausted.

## 2. Common Causes

### Skewed Data (the biggest culprit)
A few keys/partitions receive a disproportionate share of the data while others stay small. Example: `groupByKey()` or `reduceByKey()` where one "hot" key fills an executor's memory.

### Large Shuffles
Joins, `groupBy`, and `reduceByKey` all generate shuffle data. If shuffle spill exceeds available memory, disk I/O explodes and OOM can still occur if buffers keep growing.

### Wide Transformations + Caching
Persisting a large intermediate RDD/DataFrame without enough memory — executors try to keep blocks in memory and the heap fills up.

### Large UDF Outputs
A UDF that explodes data (e.g., one input row producing millions of output rows).

### Insufficient Executor Memory Settings
`spark.executor.memory` or `spark.executor.memoryOverhead` set too low, leaving no room for shuffle buffers, Python workers, or Arrow buffers.

## 3. Symptoms
- `java.lang.OutOfMemoryError: Java heap space`
- `java.lang.OutOfMemoryError: GC overhead limit exceeded`
- Frequent task retries, eventually failing the job
- Spark UI shows skewed tasks with very high runtime and shuffle spill

## 4. Strategies to Handle Executor OOM

### A. Handle Skew with Salting
Salting adds a random suffix to a skewed key so its rows spread across multiple partitions instead of piling into one.

```python
from pyspark.sql import functions as F

# Add salt to spread a skewed key across partitions
salted = df.withColumn(
    "salted_key",
    F.concat(F.col("key"), F.lit("_"), (F.rand() * 10).cast("int"))
)

# Aggregate on the salted key first
agg_salted = salted.groupBy("salted_key").agg(F.sum("value"))

# Strip the salt and do the final aggregation
final = agg_salted.withColumn(
    "key", F.split("salted_key", "_")[0]
).groupBy("key").agg(F.sum("sum(value)"))
```
The skewed key `"A"` is now spread across 10 partitions instead of landing entirely in one.

### B. Use Better Joins
Replace shuffle-heavy joins with broadcast joins when one side is small:
```python
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "100MB")
```
Avoid cartesian joins.

### C. Optimize Caching
Cache only data that's actually reused. Prefer `DISK_ONLY` or `MEMORY_AND_DISK` over `MEMORY_ONLY` for large datasets.

### D. Partition Deliberately
Repartition skewed data, and use `df.repartition(n)` to raise parallelism before heavy aggregations.

### E. Tune Executor Memory
```bash
--executor-memory 4g --conf spark.executor.memoryOverhead=1g
```
Right-size the number of cores per executor — too many cores sharing one heap causes memory contention.

### F. Manage Spill
- Use Kryo serialization (`spark.serializer=org.apache.spark.serializer.KryoSerializer`) so shuffle spill writes are more compact and efficient.
- Ensure `spark.memory.fraction` leaves enough room for both execution and storage.

## 5. Quick Checklist
- [ ] Identify skewed keys and apply salting.
- [ ] Use broadcast joins for small tables.
- [ ] Don't over-cache — pick the right storage level.
- [ ] Repartition data before shuffles.
- [ ] Tune executor heap and memory overhead.
- [ ] Monitor Spark UI for skewed tasks and shuffle spill.

## In Short
Executor OOM = data skew + shuffle pressure + under-tuned configs. Fix it by spreading skewed keys with salting, using smarter joins, tuning executor memory, and caching wisely.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Executer Memory Management|Spark Executor Memory Architecture]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Driver OOM|Driver Out-Of-Memory (OOM) in Spark]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Joins/Shuffle Hash Join|Shuffle Hash Join]]

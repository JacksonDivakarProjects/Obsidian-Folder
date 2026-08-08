# Performance & Optimization in PySpark

These concepts separate beginner PySpark users from advanced practitioners — understanding them is essential for working efficiently with large datasets. This note builds on basic operations, missing data, functions, aggregations, and joins.

---

### 1. Partitioning

**Concept:** Spark splits data into partitions, distributed across nodes. Proper partitioning is critical for performance.

**Practical use:** optimize data layout to minimize data movement (shuffling) during operations.

```python
# Check current number of partitions
print(f"Current number of partitions: {df.rdd.getNumPartitions()}")

# 1. repartition() - full shuffle, expensive but balanced
# Use when you need to increase partitions or partition by a new key
df_repartitioned = df.repartition(4, "state")  # 4 partitions by state
print(f"After repartitioning: {df_repartitioned.rdd.getNumPartitions()}")

# 2. coalesce() - no shuffle, only reduces partitions
# Use after filtering out most of the data, when many partitions are now near-empty
df_coalesced = df.coalesce(2)  # Reduce to 2 partitions without shuffle
print(f"After coalescing: {df_coalesced.rdd.getNumPartitions()}")

# 3. Partitioning on disk (when writing data) - crucial for read performance later
(df
 .write
 .partitionBy("state", "department")  # Creates a folder structure
 .mode("overwrite")
 .parquet("/path/to/partitioned_data/")
)

# Reading partitioned data is much faster for filtered queries -
# Spark can skip whole folders instead of scanning every file (partition pruning)
partitioned_df = spark.read.parquet("/path/to/partitioned_data/")
ny_sales_df = partitioned_df.filter((F.col("state") == "NY") & (F.col("department") == "Sales"))
```

**When to use what:**
- `repartition()` before expensive operations that benefit from data locality (e.g. before a large join, to co-locate keys).
- `coalesce()` after filtering out a large fraction of the data.
- `partitionBy()` when writing data that will later be queried with filters on the partition columns.

---

### 2. Shuffling

**Concept:** The expensive process of moving data between executors/nodes — usually the main performance bottleneck in a Spark job.

**Practical use:** identify and minimize operations that cause shuffles.

```python
# These operations typically cause shuffles:
shuffle_operations = [
    "groupBy()", "orderBy()", "sort()", "distinct()", 
    "repartition()", "joins (unless broadcast)", "window functions with partitionBy()"
]

# Example: groupBy causes a shuffle - Spark must bring all records
# sharing a key onto the same executor
df.groupBy("state").agg(F.avg("salary")).explain()  # Check the execution plan

# Example: a join causes a shuffle unless one side is broadcast
df1.join(df2, on="state", how="inner").explain()
```

**How to minimize shuffling:**
```python
# 1. Filter early - reduce data size before shuffle operations

# WORSE: shuffle all data, then filter
df.groupBy("state").agg(F.avg("salary")).filter(F.col("state") == "NY")

# BETTER: filter first, so less data is shuffled
df.filter(F.col("state") == "NY").groupBy("state").agg(F.avg("salary"))

# 2. Use broadcast joins for small tables (avoids shuffling the large table)
from pyspark.sql.functions import broadcast

# If departments_df is small (roughly <100MB)
df.join(broadcast(departments_df), on="state", how="inner")

# 3. Avoid redundant operations
# countDistinct() is a single aggregation; distinct().count() forces a full
# shuffle to deduplicate before counting.
df.select(F.countDistinct("state"))  # Better than df.select("state").distinct().count()
```

---

### 3. Caching & Persistence

**Concept:** Store a DataFrame in memory or on disk so it isn't recomputed from scratch on every action.

**Practical use:** when the same DataFrame is reused across multiple downstream operations.

**Storage levels:**
```python
from pyspark import StorageLevel

df.persist(StorageLevel.MEMORY_ONLY)        # Memory only (fastest, but recomputes on eviction)
df.persist(StorageLevel.MEMORY_AND_DISK)    # Memory, spills to disk (safest default)
df.persist(StorageLevel.DISK_ONLY)          # Disk only (slowest)
df.persist(StorageLevel.MEMORY_ONLY_SER)    # Memory, serialized (smaller footprint, some CPU cost)

# Common shorthand
df.cache()   # Equivalent to persist(MEMORY_ONLY)
df.persist() # Equivalent to persist(MEMORY_AND_DISK)
```

**Practical example:**
```python
# Scenario: reusing a filtered dataset multiple times
expensive_filtered_df = df.filter(
    (F.col("salary") > 100000) & 
    (F.col("hire_date") > "2020-01-01") &
    (F.col("department").isin(["Engineering", "Sales"]))
)

# Cache it since it will be reused
expensive_filtered_df.cache()

# First action - computes and materializes the cache
print(f"Count: {expensive_filtered_df.count()}")

# Subsequent actions reuse the cached data (much faster)
expensive_filtered_df.groupBy("state").agg(F.avg("salary")).show()
expensive_filtered_df.select("department").distinct().show()

# Release the cache when done with it
expensive_filtered_df.unpersist()
```

**Cache when:**
- The DataFrame is used multiple times.
- Iterative algorithms (ML training loops).
- Interactive exploration.

**Don't cache when:**
- The DataFrame is used only once.
- The dataset is far larger than available memory.
- It's about to be written to disk immediately and never reused.

---

### 4. Broadcast Variables

**Concept:** Efficiently share a small, read-only dataset across all executors.

**Practical use:** join a small lookup table with a large dataset without shuffling the large table (see [[Broadcasting in Pyspark|Broadcasting in Pyspark]] for the deep dive).

```python
department_budgets = [
    ("Sales", 1000000),
    ("Engineering", 2000000), 
    ("Marketing", 500000),
    ("HR", 300000)
]

budget_df = spark.createDataFrame(department_budgets, ["department", "annual_budget"])

from pyspark.sql.functions import broadcast

# Prevents shuffling the large employees_df
result_df = employees_df.join(
    broadcast(budget_df), 
    on="department", 
    how="left"
)

result_df.show()

# Spark automatically broadcasts tables under spark.sql.autoBroadcastJoinThreshold (default: 10MB)
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 10485760)  # 10MB in bytes
```

---

### 5. Cluster Configuration

**Concept:** Tune Spark's resource usage through configuration parameters.

**Practical use:** match resource allocation to the workload and the cluster's actual capacity.

**Common configurations:**
```python
spark = (SparkSession.builder
         .appName("OptimizedApp")
         .config("spark.executor.memory", "4g")          # Memory per executor
         .config("spark.executor.cores", "2")            # Cores per executor
         .config("spark.executor.instances", "4")        # Number of executors
         .config("spark.sql.adaptive.enabled", "true")   # Enable adaptive query execution
         .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
         .getOrCreate())

# Or set at runtime
spark.conf.set("spark.sql.shuffle.partitions", "200")  # Default is 200

# Dynamic allocation (let Spark scale executors with workload)
spark.conf.set("spark.dynamicAllocation.enabled", "true")
spark.conf.set("spark.dynamicAllocation.minExecutors", "1")
spark.conf.set("spark.dynamicAllocation.maxExecutors", "10")
```

**Monitoring with the Web UI** (`http://<driver-node>:4040`):
- Stages with high shuffle read/write.
- Skewed partitions (some tasks far slower than others).
- Memory usage and garbage-collection time.
- Task execution times.

```python
# Use explain() to inspect the query plan -
# look for Exchange (shuffle) and Sort operations
df.groupBy("state").agg(F.avg("salary")).explain()
```

### Performance Checklist

1.  **Filter early** — shrink the data as soon as possible.
2.  **Partition appropriately** — especially on write.
3.  **Minimize shuffles** — avoid unnecessary `groupBy`, `orderBy`, `distinct`.
4.  **Broadcast small tables** — for joins against large datasets.
5.  **Cache strategically** — only when a DataFrame is reused.
6.  **Monitor and tune** — use the Spark UI to find real bottlenecks, don't guess.
7.  **Prefer efficient file formats** — Parquet/ORC over CSV/JSON.
8.  **Prefer vectorized operations** — built-in functions over UDFs.

## 🔗 Related Notes
- [[Broadcasting in Pyspark|Broadcasting in Pyspark]]
- [[Repartition Vs Coalesce|Repartition Vs Coalesce]]
- [[Joining DataFrames|Joining DataFrames]]
- [[Serialization and Deserialization|Serialization and Deserialization]]

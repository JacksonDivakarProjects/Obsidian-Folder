# DeltaTable Upsert in PySpark

## 1. What Is a DeltaTable Upsert?

- Delta Lake is a storage layer on top of Parquet that adds ACID transactions, schema enforcement, and versioning.
- **Upsert** = update a row if it already exists, insert it if it doesn't — the same idea as SQL's `MERGE` statement.
- Upserts matter whenever you need to stream data into a Delta table or sync batch data incrementally, without duplicating records or blowing away the whole table on every run.

## 2. Why Use Upsert?

- Prevents duplicate records when the same key can arrive more than once.
- Handles slowly-changing dimensions (SCD) efficiently.
- Fits naturally with structured streaming's `foreachBatch` for incremental updates.
- Supports idempotent writes, which matters a lot in streaming pipelines that may reprocess a batch after a failure.

## 3. How Upsert Works in DeltaTable

1. Load or create the `DeltaTable`.
2. Identify a unique key to match source rows against target rows.
3. Call `.merge()` to update matching rows and insert unmatched ones in a single atomic operation.

## 4. Practical Examples

### Example 1: Batch Upsert

```python
from delta.tables import DeltaTable
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Delta Upsert Example") \
    .getOrCreate()

# Source DataFrame (new records or updates)
source_df = spark.createDataFrame([
    (1, "Alice", 25),
    (2, "Bob", 30),
    (3, "Charlie", 35)
], ["id", "name", "age"])

# Target Delta table path
delta_path = "/delta/people"

# Check if the table already exists
if DeltaTable.isDeltaTable(spark, delta_path):
    delta_table = DeltaTable.forPath(spark, delta_path)

    # Merge (upsert)
    delta_table.alias("target").merge(
        source_df.alias("source"),
        "target.id = source.id"   # Match condition
    ).whenMatchedUpdateAll() \
     .whenNotMatchedInsertAll() \
     .execute()
else:
    # First run: no table yet, so just create it
    source_df.write.format("delta").save(delta_path)
```

**Explanation:**
- `whenMatchedUpdateAll()` updates all columns of the target row when `id` already exists.
- `whenNotMatchedInsertAll()` inserts the source row as a new record when `id` doesn't exist yet.

### Example 2: Streaming Upsert with `foreachBatch`

```python
def upsert_stream(batch_df, batch_id):
    delta_table = DeltaTable.forPath(spark, "/delta/people")
    delta_table.alias("target").merge(
        batch_df.alias("source"),
        "target.id = source.id"
    ).whenMatchedUpdateAll() \
     .whenNotMatchedInsertAll() \
     .execute()

streaming_df.writeStream \
    .foreachBatch(upsert_stream) \
    .option("checkpointLocation", "/delta/checkpoint/") \
    .start()
```

**Key notes:**
- Each micro-batch arrives as a regular batch DataFrame inside `foreachBatch`, so ordinary merge logic applies safely.
- Checkpointing tracks which offsets have been processed, which combined with the merge's idempotency gives you effectively-once semantics.

## 5. Advanced Upsert Techniques

**Conditional updates** — only update when a condition holds:

```python
delta_table.alias("target").merge(
    source_df.alias("source"),
    "target.id = source.id"
).whenMatchedUpdate(
    condition="source.age > target.age",
    set={"age": "source.age", "name": "source.name"}
).whenNotMatchedInsertAll().execute()
```

Here the update only fires when `source.age > target.age`.

**Selective column insert/update** — touch only specific columns instead of every column:

```python
delta_table.alias("target").merge(
    source_df.alias("source"),
    "target.id = source.id"
).whenMatchedUpdate(set={"age": "source.age"}) \
 .whenNotMatchedInsert(set={"id": "source.id", "name": "source.name", "age": "source.age"}) \
 .execute()
```

Useful for partial updates where you don't want to overwrite every column with the source's value.

## 6. Best Practices

| Best Practice | Explanation |
|---|---|
| Use a genuine unique key | Essential for the merge condition to match rows correctly. |
| Batch first, merge second | Avoid merging huge streams row-by-row; merge per micro-batch instead. |
| Use checkpointing | Required for streaming + idempotent upserts. |
| Minimize shuffles | Partition Delta tables sensibly to reduce merge cost. |
| Monitor file sizes | Files that are too small or too large after repeated merges degrade performance — run `OPTIMIZE` periodically. |
| Avoid unnecessary column updates | Only update columns that actually changed to reduce write amplification. |

## 7. Quick Tip

DeltaTable merges are transactional — if the cluster fails mid-merge, Delta's atomicity guarantee ensures the table is left as if the merge never started, not half-applied. In streaming, `foreachBatch` + `merge` is the standard pattern for incremental upserts.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Delta Lake Commands in Different APIs/Delta Lake Commands in Python API with Spark|Delta Lake Commands in Python API with Spark]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Schema Operations|Schema Management in Spark/Delta Lake]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Miscellaneous/Data Modeling|Data Modelling Masterclass for Data Engineers]]

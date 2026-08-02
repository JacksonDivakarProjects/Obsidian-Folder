Absolutely, Jack. Let’s do a **comprehensive, practical guide to DeltaTable upserts in PySpark**. I’ll cover **what it is, why it’s useful, how to do it, and best practices**, step by step.

---

# 🔹 DeltaTable Upsert in PySpark

## 1️⃣ What is DeltaTable Upsert?

- **Delta Lake** is a **storage layer on top of Parquet** that adds **ACID transactions, schema enforcement, and versioning**.
    
- **Upsert** = **Update if exists, Insert if not**. This is similar to SQL’s **MERGE** statement.
    
- Upserts are critical when you want to **stream data into a Delta table** or **sync batch data** without duplicating or overwriting entire tables.
    

---

## 2️⃣ Why Use Upsert?

- Prevents **duplicate records**.
    
- Handles **slow-changing dimensions** (SCD) efficiently.
    
- Works with **structured streaming + foreachBatch** for incremental updates.
    
- Supports **idempotent writes**, which is essential in streaming.
    

---

## 3️⃣ How Upsert Works in DeltaTable

**Steps:**

1. Load or create the **DeltaTable**.
    
2. Identify a **unique key** to match source and target records.
    
3. Use `.merge()` to **update matching records and insert new ones**.
    

---

## 4️⃣ Practical Example

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

# Check if table exists
if DeltaTable.isDeltaTable(spark, delta_path):
    delta_table = DeltaTable.forPath(spark, delta_path)
    
    # Merge (Upsert)
    delta_table.alias("target").merge(
        source_df.alias("source"),
        "target.id = source.id"   # Match condition
    ).whenMatchedUpdateAll() \
     .whenNotMatchedInsertAll() \
     .execute()
else:
    # If table doesn't exist, create it
    source_df.write.format("delta").save(delta_path)
```

✅ **Explanation:**

- `whenMatchedUpdateAll()` → updates all columns if `id` exists.
    
- `whenNotMatchedInsertAll()` → inserts new records if `id` doesn’t exist.
    

---

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

**Key Notes:**

- Each batch is treated as a **batch DataFrame**, so you can use **merge logic** safely.
    
- Checkpointing ensures **exactly-once processing**.
    

---

## 5️⃣ Advanced Upsert Techniques

1. **Conditional Updates**
    

```python
delta_table.alias("target").merge(
    source_df.alias("source"),
    "target.id = source.id"
).whenMatchedUpdate(
    condition="source.age > target.age",
    set={"age": "source.age", "name": "source.name"}
).whenNotMatchedInsertAll().execute()
```

- Only updates when **source.age > target.age**.
    

2. **Selective Columns Insert/Update**
    

```python
delta_table.alias("target").merge(
    source_df.alias("source"),
    "target.id = source.id"
).whenMatchedUpdate(set={"age": "source.age"}) \
 .whenNotMatchedInsert(set={"id": "source.id", "name": "source.name", "age": "source.age"}) \
 .execute()
```

- Useful for **partial updates** without overwriting all columns.
    

---

## 6️⃣ Best Practices for Delta Upsert

|Best Practice|Explanation|
|---|---|
|Use **unique keys**|Essential for accurate merge operations.|
|**Batch first, merge second**|Avoid merging huge streaming data row-by-row.|
|Use **checkpointing**|Required for streaming + idempotent upserts.|
|Minimize **shuffles**|Partition Delta tables wisely to reduce merge cost.|
|Monitor **file sizes**|Delta files that are too small/large can degrade performance.|
|Avoid updating columns unnecessarily|Only update columns that actually change.|

---

## 7️⃣ Quick Tip

- DeltaTable merges are **transactional**, so even if your cluster fails mid-merge, Delta ensures **atomicity**.
    
- In streaming, `foreachBatch + merge` is the **go-to pattern** for incremental upserts.
    

---

If you want, I can make a **diagram showing streaming → foreachBatch → Delta merge workflow**, which makes it visually crystal clear for presentations or interviews.

Do you want me to create that diagram?

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Delta Lake Commands in Different APIs/Delta Lake Commands in Python API with Spark|Delta Lake Commands in Python API with Spark]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Schema Operations|Schema Management in Spark/Delta Lake]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Miscellaneous/Data Modeling|Data Modelling Masterclass for Data Engineers]]

# Broadcasting in PySpark

**Broadcasting** is one of the most effective join optimizations in PySpark, but it is often used incorrectly or not understood beyond "makes joins faster."

### 🎯 When to Use Broadcasting

Use broadcasting when joining a **large DataFrame with a very small one**. It prevents Spark from shuffling the large DataFrame across the network — one of the most expensive operations in distributed computing.

---

### 📊 The Problem Broadcasting Solves: The Shuffle

Normally, joining two DataFrames forces Spark to **shuffle** the data:
1.  Rearrange data across partitions.
2.  Move data between executors over the network.
3.  Spill intermediate data to disk.

This is slow, resource-intensive, and often the main bottleneck in Spark jobs.

---

### 🚀 The Solution: Broadcast Join (Map-Side Join)

Broadcasting sends a **copy of the small DataFrame** to every executor. As a result:
-   The large DataFrame stays in place — no shuffle.
-   Each executor performs the join locally.
-   There's no network transfer of the large data.
-   Execution is much faster.

---

### ✅ The Practical Rule of Thumb

**Broadcast the smaller DataFrame when it's under ~10MB.** That's Spark's default threshold (`spark.sql.autoBroadcastJoinThreshold`), but you can raise it manually if you have the memory to spare.

#### Example 1: Perfect Use Case (Lookup Table)
```python
from pyspark.sql.functions import broadcast

# Large fact table (millions of rows)
transactions_df = spark.table("transactions")

# Small dimension table (a few hundred rows)
countries_df = spark.table("dim_countries")  # ~50 rows, 10KB

# Broadcast the small table to avoid shuffling the large one
result_df = transactions_df.join(
    broadcast(countries_df), 
    on="country_id", 
    how="inner"
)
```

#### Example 2: Manual Configuration for Larger Tables
```python
# If your "small" table is 20MB, raise the threshold
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 20971520)  # 20MB in bytes

# Or broadcast it explicitly
large_reference_df = spark.table("product_catalog")  # ~20MB
result_df = transactions_df.join(
    broadcast(large_reference_df),
    on="product_id",
    how="left"
)
```

---

### ❌ When NOT to Use Broadcasting

Do **not** broadcast large DataFrames. Doing so will:
-   Overwhelm the network with data transfer.
-   Cause out-of-memory errors on executors.
-   Slow the job down significantly.

```python
# BAD IDEA: broadcasting a large DataFrame
huge_df = spark.table("user_profiles")  # 50GB
small_df = spark.table("config_table")  # 1KB

# This tries to send 50GB to every executor - will likely crash
result_df = broadcast(huge_df).join(small_df, on="user_id")
```

---

### 🔍 How to Check if Broadcasting Is Working

**Check the physical plan** — look for `BroadcastHashJoin`:
```python
result_df.explain()

# == Physical Plan ==
# *(2) BroadcastHashJoin [country_id], [country_id], Inner, BuildRight
# :- *(2) Project [transaction_id, amount, country_id]
# :  +- *(2) Filter isnotnull(country_id)
# :     +- Scan ExistingRDD[transaction_id, amount, country_id]
# +- BroadcastExchange HashedRelationBroadcastMode(List(input[0, int, true]))
#    +- *(1) Project [country_id, country_name]
#       +- *(1) Filter isnotnull(country_id)
#          +- Scan ExistingRDD[country_id, country_name]
```

Alternatively, check the **SQL tab of the Spark UI** for a `BroadcastHashJoin` node.

---

### ⚙️ Automatic vs. Manual Broadcasting

Spark tries to broadcast automatically, but manual control matters:

```python
# Automatic broadcasting (Spark decides based on size)
df1.join(df2, on="key")

# Manual broadcasting (force it)
df1.join(broadcast(df2), on="key")
```

**Manual broadcasting helps when:**
1.  Spark underestimates the size of a DataFrame.
2.  You know the data distribution better than Spark's statistics do.
3.  You want to guarantee the optimization happens rather than hope for it.

---

### 🧪 Practical Example: Data Enrichment

The most common real use case — enriching a large dataset with reference data.

```python
# Large main dataset (log events, transactions, user activities)
main_df = spark.read.parquet("s3://bucket/large_dataset/")

# Small reference data (category mappings)
category_df = spark.createDataFrame([
    (1, "Electronics"),
    (2, "Clothing"),
    (3, "Books")
], ["category_id", "category_name"])

# Enrich the large dataset with category names
enriched_df = main_df.join(
    broadcast(category_df),  # <- the key line
    on="category_id",
    how="left"
)

final_df = enriched_df.filter(F.col("category_name") == "Electronics")
```

### 💡 Key Takeaways

1.  Use broadcasting for small-to-large joins (typically < 10MB on the small side).
2.  It prevents shuffling the large DataFrame.
3.  Check execution plans to confirm it's actually happening (`BroadcastHashJoin`).
4.  Never broadcast large DataFrames — it causes memory errors.
5.  Prefer manual control when you understand your data better than Spark's size estimate.

## 🔗 Related Notes
- [[Performance & Optimisation in Pyspark|Performance & Optimisation in Pyspark]]
- [[Joining DataFrames|Joining DataFrames]]
- [[Repartition Vs Coalesce|Repartition Vs Coalesce]]

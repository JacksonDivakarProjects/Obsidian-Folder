# `foreachBatch` in PySpark Structured Streaming

What `foreachBatch` is, why it exists, how it works, and how to use it in practice.

## 1️⃣ What Is `foreachBatch`?

In Structured Streaming, `foreachBatch` is a `writeStream` sink that lets you apply **custom operations on each micro-batch of streaming data**. Unlike standard sinks (`console`, `parquet`, `delta`), it hands you the micro-batch as a **plain batch DataFrame** — giving full access to every batch DataFrame API, and the ability to write to multiple destinations or apply arbitrary transformations before saving.

- **Key idea:** each micro-batch is treated like an ordinary batch DataFrame, so any batch-style code applies.

## 2️⃣ Why Use `foreachBatch`?

Reach for it when you need to:

1.  Write to **multiple destinations** in a single streaming query (e.g. S3 + a JDBC database).
2.  Apply **custom transformations or enrichment** before saving.
3.  Get **full control** over per-micro-batch DataFrame operations.
4.  Do something standard streaming sinks (`append`, `complete`, `update`) can't express directly — e.g. a Delta `MERGE`.

Think of it as a bridge between streaming and batch processing.

## 3️⃣ How It Works

- Spark runs the streaming job in **micro-batches**, as usual.
- Each batch is passed as a **DataFrame** to a **user-defined function**.
- Inside that function, you can transform the DataFrame and write it anywhere.
- The streaming engine still handles **offsets and checkpointing** around your function, so the overall query stays fault-tolerant.

**Basic syntax:**

```python
def process_batch(batch_df, batch_id):
    # batch_df is a normal DataFrame
    # batch_id is the batch number
    batch_df.show()  # Example operation
    batch_df.write.mode('append').parquet('/path/to/save')

streaming_df.writeStream \
    .foreachBatch(process_batch) \
    .option("checkpointLocation", "/path/to/checkpoint") \
    .start()
```

## 4️⃣ Key Points

|Feature|Details|
|---|---|
|`batch_df`|A standard Spark DataFrame representing the current micro-batch|
|`batch_id`|A monotonically increasing batch ID (useful for logging/auditing)|
|Fault tolerance|Checkpointing gives exactly-once *semantics* for the batch boundary itself, but your own write logic must be idempotent to actually avoid duplicates on a retried batch (e.g. write to an idempotent sink, or `MERGE` on a key)|
|Use cases|JDBC writes, multi-destination writes, batch-style transformations, Delta `MERGE`|

## 5️⃣ Practical Examples

### Write Each Batch to Parquet

```python
def write_parquet(batch_df, batch_id):
    print(f"Processing batch {batch_id}")
    batch_df.write.mode('append').parquet('/data/stream_output/')

streaming_df.writeStream \
    .foreachBatch(write_parquet) \
    .option("checkpointLocation", "/data/checkpoint/") \
    .start()
```

### Write to a JDBC Database

```python
def write_jdbc(batch_df, batch_id):
    batch_df.write \
        .format("jdbc") \
        .option("url", "jdbc:mysql://localhost:3306/mydb") \
        .option("dbtable", "stream_table") \
        .option("user", "root") \
        .option("password", "mypassword") \
        .mode("append") \
        .save()

streaming_df.writeStream \
    .foreachBatch(write_jdbc) \
    .option("checkpointLocation", "/data/checkpoint/") \
    .start()
```

**Note:** this only avoids duplicates on retry if the target table/database supports idempotent writes or upserts — a plain JDBC `append` will duplicate rows on a retried batch.

### Apply a Transformation per Batch

```python
def enrich_and_save(batch_df, batch_id):
    enriched_df = batch_df.withColumn("processed_time", current_timestamp())
    enriched_df.write.mode('append').parquet('/data/enriched/')

streaming_df.writeStream \
    .foreachBatch(enrich_and_save) \
    .option("checkpointLocation", "/data/checkpoint/") \
    .start()
```

## 6️⃣ Best Practices

1.  **Always set `checkpointLocation`** for fault tolerance.
2.  **Keep batch processing idempotent** — if Spark retries a batch, it must not duplicate data.
3.  **Avoid heavy blocking operations** inside `foreachBatch` that stall the stream; use asynchronous writes where genuinely needed.
4.  **Operate on the DataFrame as a whole** — don't process rows one at a time inside the function.
5.  **Watch batch processing time** — if a batch takes longer than the trigger interval, Spark backs up and lags behind the source.

## 7️⃣ `foreachBatch` vs. Standard Sinks

|Sink|Use Case|
|---|---|
|`console`|Debugging / development|
|`parquet` / `delta`|Simple writes to a file system|
|`foreachBatch`|Custom logic, multi-sink writes, batch transformations, JDBC writes, enrichment|

**Bottom line:** `foreachBatch` bridges batch-level control with streaming execution — maximum flexibility, without sacrificing the checkpointing that keeps the query fault-tolerant.

## 🔗 Related Notes
- [[Checkpointing And Idempotency|Checkpointing & Idempotency in PySpark Structured Streaming]]
- [[Output Modes in Streaming|Output Modes in Streaming]]
- [[Spark Streaming Foundational Concepts|Spark Streaming Foundational Concepts]]

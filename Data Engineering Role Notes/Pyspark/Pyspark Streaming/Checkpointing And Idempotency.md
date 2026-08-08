# Checkpointing & Idempotency in PySpark Structured Streaming

In real-time data processing, **fault tolerance** and **duplicate prevention** are critical. Structured Streaming provides checkpointing, which combines with an ACID-compliant sink like Delta Lake to achieve idempotent writes.

---

## 1️⃣ Checkpointing

Checkpointing is Spark's mechanism for **persisting the progress and state of a streaming query**, enabling recovery after failures.

### Why It Matters

- **Fault tolerance**: if a streaming job crashes, Spark can resume from the last processed offset.
- **Stateful operations**: required for `groupBy`, `window`, or other aggregations where intermediate state must survive across batches.
- **Micro-batch tracking**: stores metadata about previous batches to keep results consistent across restarts.

### What Spark Stores in a Checkpoint

1. **Source offsets** — which records have already been read.
2. **Aggregation state** — sums, counts, window contents, etc.
3. **Batch metadata** — helps with recovery and exactly-once-style semantics.

### Configuring Checkpointing

```python
streaming_query = df.writeStream \
    .format("delta") \
    .option("checkpointLocation", "/path/to/checkpoint") \
    .option("path", "/path/to/output_delta") \
    .trigger(once=True) \
    .start()
```

### Key Points

- The checkpoint directory must be **persistent storage** and cannot itself be a single file.
- **Always keep checkpoint and output paths separate.**
- Required for **stateful operations**: aggregation, `groupBy`, `window`.
- Contains offsets, state, and batch info — that's what makes fault-tolerant restarts possible.

---

## 2️⃣ Idempotency in Streaming Writes

Idempotency means **processing the same data multiple times doesn't produce duplicates** — essential in distributed systems, where retries are routine.

### Why It Matters

- Network failures or node crashes trigger retries.
- Without idempotency, retries risk **duplicate records**, corrupting downstream analytics.

### How Delta Lake Provides Idempotency

1. **Exactly-once-style semantics**
   - Spark tracks offsets in the checkpoint.
   - On restart, only unprocessed data is reprocessed.
2. **Atomic writes**
   - Delta writes each micro-batch atomically — either the whole batch lands, or none of it does. No partial writes.
3. **Idempotent upserts (`MERGE INTO`)**
   - With a primary key (e.g. `order_id`), Delta's `MERGE` can upsert instead of blindly appending, preventing duplicates even across multiple retries of the same batch.

### Example: Idempotent Streaming Write

```python
df.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/Volumes/sparkstreaming/default/jsondata/chkpntloc") \
    .option("path", "/Volumes/sparkstreaming/default/jsondata/output_delta") \
    .trigger(once=True) \
    .start()
```

✅ Behavior on failure: job fails mid-stream → restart → Spark reads the checkpoint → only unprocessed records get written → **no duplicates**.

---

## 3️⃣ Output Modes and Checkpointing

Output modes control **how results are written to a sink**, and interact closely with checkpointing.

|**Output Mode**|**Use Case**|**Checkpoint Requirement**|
|---|---|---|
|**append**|Append-only streams, simple writes|Works naturally with checkpointing|
|**update**|Updating existing aggregates|Requires checkpoint to track state|
|**complete**|Full aggregation output on every trigger|Requires checkpoint to maintain full state|

💡 Prefer **append mode** for simplicity and performance where it's applicable; reach for **update**/**complete** only for aggregations that genuinely need them.

---

## 4️⃣ Best Practices for Production

1. **Separate paths**
   - Output path and checkpoint path should **never overlap**:
   ```text
   /output_delta → stores data
   /chkpntloc → stores offsets & state
   ```
2. **Use ACID-compliant sinks**
   - Delta Lake (or similar) is what actually makes atomic, idempotent writes possible.
3. **Plan checkpoint storage**
   - Store checkpoints in durable, fault-tolerant storage (S3, HDFS, or persistent local storage).
4. **Monitor checkpoints**
   - Checkpoint directories can grow over time — monitor their size and the underlying state.
5. **Use `MERGE` for upserts**
   - For duplicate-sensitive streams, `MERGE INTO delta_table` on the primary key is the robust option.

---

## 5️⃣ Summary

- **Checkpointing**: enables fault tolerance, maintains state, tracks offsets — required for stateful streaming operations.
- **Idempotency**: prevents duplicates on retry, achieved via atomic writes + checkpoint tracking + (optionally) `MERGE`.
- **Output modes**: influence how checkpointed state is used — append is simplest; update/complete require full state tracking.

**Rule of thumb:**

> Checkpoint + an ACID-compliant sink (e.g. Delta Lake) = a reliable, fault-tolerant, idempotent streaming pipeline.

## 🔗 Related Notes
- [[ForEachBatch|ForEachBatch]]
- [[Output Modes in Streaming|Output Modes in Streaming]]
- [[Archive Source File|Archive Source File]]

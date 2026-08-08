# 🔥 PySpark Structured Streaming Triggers

A trigger defines *when and how often* a streaming query executes. Understanding triggers is essential for tuning **latency**, **throughput**, and **resource utilization**.

## 1️⃣ What a Trigger Does

- Controls **how and when micro-batches** are processed.
- Determines:
    - The **frequency** of batch execution.
    - Whether the query runs **continuously** or processes data **once**.
    - How late-arriving data interacts with any configured watermark.

## 2️⃣ Trigger Types

### A. `once=True`

- Executes **all currently available data once**, then stops.
- Effectively batch-like processing running on top of a streaming source.

```python
df.writeStream.trigger(once=True).start()
```

**Use case:** process everything in a directory, or all currently-available Kafka messages, then terminate.

---

### B. `processingTime="interval"`

- Executes the query **periodically**, at a fixed interval.
- Starts a new micro-batch every N seconds (or milliseconds).

```python
df.writeStream.trigger(processingTime="10 seconds").start()
```

**Use case:** near-real-time pipelines — log processing, Kafka streams.

---

### C. `continuous="interval"` (Continuous Processing)

- Processes data **record by record**, not in micro-batches.
- Achieves millisecond-level latency.
- **Limited support**: not all sources/sinks support this mode, and it only supports a restricted set of DataFrame operations (mostly map-like, stateless ones).

```python
df.writeStream.trigger(continuous="1 second").start()
```

**Use case:** ultra-low-latency systems — financial transactions, real-time analytics.

---

### D. `availableNow=True`

- Processes **all currently available data**, then stops.
- Designed for sources that support catch-up-style batch processing.
- Unlike `once`, splits that available data into multiple smaller micro-batches rather than one large one — easier on cluster resources.

```python
df.writeStream.trigger(availableNow=True).start()
```

**Use case:** catch-up runs on file-based streaming sources or other sources that support `availableNow`.

## 3️⃣ Comparison Table

|**Trigger Type**|**Behavior**|**Use Case**|
|---|---|---|
|`once=True`|Process all data once, then stop|Batch-style run on a streaming source|
|`processingTime="N sec"`|Process at fixed intervals|Regular micro-batch streaming|
|`continuous="N sec"`|Process continuously, record-level|Ultra low-latency streaming|
|`availableNow=True`|Process all available data, in several micro-batches, then stop|Catch-up batch on a streaming source|

## 4️⃣ Practical Examples

### Process everything once (batch-like)
```python
df.writeStream.format("delta") \
    .option("checkpointLocation", "/tmp/chkpt") \
    .option("path", "/tmp/output") \
    .trigger(once=True) \
    .start()
```

### Micro-batch every 30 seconds
```python
df.writeStream.format("delta") \
    .option("checkpointLocation", "/tmp/chkpt") \
    .option("path", "/tmp/output") \
    .trigger(processingTime="30 seconds") \
    .start()
```

### Continuous, low-latency (1-second epoch)
```python
df.writeStream.format("delta") \
    .option("checkpointLocation", "/tmp/chkpt") \
    .option("path", "/tmp/output") \
    .trigger(continuous="1 second") \
    .start()
```

### Process all available data now
```python
df.writeStream.format("delta") \
    .option("checkpointLocation", "/tmp/chkpt") \
    .option("path", "/tmp/output") \
    .trigger(availableNow=True) \
    .start()
```

## 5️⃣ Best Practices

- ✅ Always set a **checkpoint location** for fault tolerance and state recovery.
- ✅ Use `once=True` or `availableNow=True` for batch-style runs.
- ✅ Use `processingTime` for near-real-time pipelines.
- ⚠️ Use `continuous` only when the source/sink support it and low latency is genuinely critical.
- ⚡ Tune the interval based on throughput and latency requirements — shorter intervals mean lower latency but more per-batch overhead.

## 6️⃣ Summary

The trigger is the heartbeat of a streaming job. Picking the right one balances:

- **Latency** vs. **throughput**.
- **Batch-style processing** vs. **continuous streaming**.
- **Resource usage** vs. **real-time requirements**.

Pick the trigger mode that matches the pipeline's data-arrival pattern and business SLA.

## 🔗 Related Notes
- [[Archive Source File|Archive Source File]]
- [[Output Modes in Streaming|Output Modes in Streaming]]
- [[Spark Streaming Foundational Concepts|Spark Streaming Foundational Concepts]]

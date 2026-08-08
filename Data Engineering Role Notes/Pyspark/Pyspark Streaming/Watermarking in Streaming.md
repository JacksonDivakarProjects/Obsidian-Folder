# Watermarking in PySpark Structured Streaming

Watermarking is the mechanism for handling **late data** in streaming systems. It bounds the state kept for stateful operations (like windowed aggregations), preventing unbounded memory growth while still accepting reasonably-late events.

## 1️⃣ Key Concepts

1.  **Event Time vs. Processing Time**
    - **Event time**: the timestamp in the data when the event actually occurred (preferred for analytics).
    - **Processing time**: the time Spark actually processes the event — can be skewed for late data.
2.  **Late Data**
    - Data arriving after its event-time window has already closed. Common due to network delays or retries in distributed systems.
3.  **Watermark**
    - Defines **how long Spark should wait** for late events before considering a window final, expressed as a time interval relative to event time.

**Conceptual analogy:** a watermark says *"I'll accept late events up to 5 minutes after the window ends; anything later is ignored."*

## 2️⃣ How It Works

- Stateful aggregations (`groupBy(window(...))`) maintain state per window.
- Without a watermark, Spark **keeps state indefinitely**, risking memory overflow as more and more windows accumulate.
- With a watermark:
    - Spark **cleans up state** for windows older than the threshold.
    - Windows past that threshold are treated as **final** and no longer accept updates.

**Key points:**
- A watermark only affects **state retention**, not whether in-window events are processed immediately.
- Events beyond the watermark are **dropped**, not merely delayed.
- The watermark is always defined **relative to event time**, not processing time.

## 3️⃣ Syntax

```python
df.withWatermark("eventTimeColumn", "delayThreshold")
```

- `"eventTimeColumn"` → the timestamp column in the data.
- `"delayThreshold"` → the maximum allowed lateness (e.g. `"10 minutes"`).

**Example:**

```python
from pyspark.sql.functions import window, col

agg_df = df.withWatermark("timestamp", "5 minutes") \
           .groupBy(window(col("timestamp"), "10 minutes")) \
           .count()
```

**Explanation:** window size 10 minutes, watermark 5 minutes → windows older than `window end + 5 minutes` are finalized and their state is dropped.

## 4️⃣ Practical Examples

### A. Tumbling Window with Watermark

```python
agg_df = df.withWatermark("timestamp", "5 minutes") \
           .groupBy(window(col("timestamp"), "10 minutes")) \
           .count()

agg_df.writeStream \
    .format("console") \
    .outputMode("append") \
    .option("truncate", False) \
    .start()
```

Accepts late events up to 5 minutes past the window end; anything later is dropped.

### B. Sliding Window with Watermark

```python
agg_df = df.withWatermark("timestamp", "2 minutes") \
           .groupBy(window(col("timestamp"), "10 minutes", "5 minutes")) \
           .count()
```

10-minute windows sliding every 5 minutes; late events up to 2 minutes are still included.

### C. Session Window with Watermark

```python
from pyspark.sql.functions import session_window

agg_df = df.withWatermark("timestamp", "10 minutes") \
           .groupBy(session_window(col("timestamp"), "5 minutes"), col("user_id")) \
           .count()
```

Handles bursty data; sessions merge if events arrive within the session gap; the watermark bounds how long state for late-arriving sessions is retained.

## 5️⃣ Why Watermarking Is Essential

|Purpose|Description|
|---|---|
|**State management**|Prevents unbounded memory growth in long-running streams.|
|**Late data handling**|Ensures late events are only processed up to a tolerable delay.|
|**Accurate aggregations**|Keeps counts, sums, and averages correct even with out-of-order events.|
|**Works across window types**|Supported with tumbling, sliding, and session windows.|

## 6️⃣ Best Practices

1.  **Always use event time for analytics** — never processing time for windowed aggregations.
2.  **Set a reasonable watermark**: too short and valid late data gets dropped; too long and state grows unnecessarily.
3.  **Combine with checkpointing** — required for stateful aggregations and fault tolerance.
4.  **Monitor state size** in the Spark UI and adjust the watermark as needed.
5.  **Pair with an ACID-compliant sink** (e.g. Delta Lake) so retried writes for late data stay idempotent.

## 7️⃣ Summary

- **Watermarking** bounds state and handles late data in streaming aggregations.
- Works with tumbling, sliding, and session windows.
- Enables accurate, fault-tolerant streaming analytics without unbounded memory growth.
- Combine watermark + checkpointing + an ACID-compliant sink for production-grade pipelines.

💡 **Rule of thumb:** set the watermark to slightly exceed the expected network/data delay — this balances state size against accuracy.

## 🔗 Related Notes
- [[Types Of Windows|Window Operations in PySpark Structured Streaming]]
- [[Why Complete Mode not Working in Watermarking|Why `complete` Output Mode Doesn't Work with Watermarks]]
- [[Output Modes in Streaming|Output Modes in Streaming]]

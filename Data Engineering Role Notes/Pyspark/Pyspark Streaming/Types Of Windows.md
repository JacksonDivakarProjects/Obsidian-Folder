# Window Operations in PySpark Structured Streaming

Window operations aggregate over time intervals instead of row-by-row — essential for time-based analytics like counts, sums, averages, and event grouping.

## 1️⃣ Key Concepts

- **Window Duration**: the length of time each window covers.
- **Slide Duration**: how often the window moves forward.
- **Event Time**: the timestamp in your data used for windowing (not processing time — see [[Spark Streaming Foundational Concepts|Spark Streaming Foundational Concepts]]).
- **Watermarking**: optional mechanism for handling late data (see [[Watermarking in Streaming|Watermarking in PySpark Structured Streaming]]).

Window operations are typically expressed as `groupBy(window(...))` and are **stateful aggregations**.

## 2️⃣ Types of Windows

### A. Tumbling Window

**Definition:** fixed-size, non-overlapping windows. Each event belongs to **exactly one** window.

**Syntax:**
```python
window(timeColumn, windowDuration)
```

**Example use case:** count orders every 5 minutes.

```python
from pyspark.sql.functions import window, col

df = spark.readStream.format("json") \
    .option("multiline", True) \
    .schema(schema) \
    .load("/path/to/orders")

agg_df = df.groupBy(window(col("timestamp"), "5 minutes")) \
           .count()

agg_df.writeStream \
    .format("console") \
    .outputMode("complete") \
    .option("truncate", False) \
    .start()
```

✅ Behavior: windows are `[0–5 min)`, `[5–10 min)`, `[10–15 min)`... Each record contributes to exactly **one** window.

---

### B. Sliding Window

**Definition:** fixed-size windows that **overlap**. A single event can belong to **multiple** windows.

**Syntax:**
```python
window(timeColumn, windowDuration, slideDuration)
```

**Example use case:** count orders every 1 minute over a rolling 5-minute window.

```python
agg_df = df.groupBy(window(col("timestamp"), "5 minutes", "1 minute")) \
           .count()

agg_df.writeStream \
    .format("console") \
    .outputMode("complete") \
    .option("truncate", False) \
    .start()
```

✅ Behavior: window size 5 min, slide 1 min → windows overlap: `[0–5]`, `[1–6]`, `[2–7]`, ... Useful for rolling statistics.

---

### C. Session Window

**Definition:** dynamic windows based on periods of activity separated by inactivity. The window **closes after a gap of inactivity** (timeout) — good for bursty, unevenly-spaced events.

**Syntax:**
```python
groupBy(session_window(timeColumn, gapDuration))
```

**Example use case:** track user activity sessions, with 10 minutes of inactivity marking a session boundary.

```python
from pyspark.sql.functions import session_window

agg_df = df.groupBy(session_window(col("timestamp"), "10 minutes"), col("user_id")) \
           .count()

agg_df.writeStream \
    .format("console") \
    .outputMode("complete") \
    .option("truncate", False) \
    .start()
```

✅ Behavior: each user's sessions are separated by ≥10 minutes of inactivity; sessions merge together if activity continues before the gap elapses.

## 3️⃣ Comparison of Window Types

|Feature|Tumbling Window|Sliding Window|Session Window|
|---|---|---|---|
|**Overlap**|No|Yes|No (dynamic)|
|**Window Size**|Fixed|Fixed|Dynamic|
|**Use Case**|Periodic reports|Rolling metrics|Activity sessions|
|**Aggregation**|Simple|Complex, overlapping|Per session|
|**PySpark Function**|`window()`|`window()`|`session_window()`|

## 4️⃣ Watermarking with Windows

Watermarks handle **late data** by defining how long Spark should wait for late-arriving events before finalizing a window.

**Example with a tumbling window:**
```python
agg_df = df.withWatermark("timestamp", "5 minutes") \
           .groupBy(window(col("timestamp"), "5 minutes")) \
           .count()
```

- Late data arriving **within 5 minutes** of the watermark is still included.
- Data arriving **after** the watermark is dropped.

## 5️⃣ Best Practices

1.  **Use event time**, not processing time, for windowing.
2.  **Keep the slide interval reasonable** — a smaller slide means more overlapping windows and more compute.
3.  **Use session windows** for bursty or user-interaction data.
4.  **Always watermark production aggregations** to bound state memory.
5.  **Combine with checkpointing** — required for fault-tolerant, stateful window aggregations.

## ✅ Summary

- **Tumbling Window**: fixed, non-overlapping, simple periodic aggregations.
- **Sliding Window**: fixed, overlapping, rolling statistics.
- **Session Window**: dynamic, event-driven, detects activity sessions.
- **Watermarking + checkpointing**: essential for fault-tolerant, memory-safe windowed streaming.

## 🔗 Related Notes
- [[Watermarking in Streaming|Watermarking in PySpark Structured Streaming]]
- [[Output Modes in Streaming|Output Modes in Streaming]]
- [[Spark Streaming Foundational Concepts|Spark Streaming Foundational Concepts]]

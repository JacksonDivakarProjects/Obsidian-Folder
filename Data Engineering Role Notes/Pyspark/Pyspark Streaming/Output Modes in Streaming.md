# Output Modes in PySpark Structured Streaming

Output modes define how the results of a streaming query are written to the sink each trigger. There are three: **append**, **complete**, and **update**.

## 1. **Append Mode** (Default)
- **Only adds new rows** to the output.
- **Use case**: when you only care about new data.
- **Limitation**: requires a watermark for windowed aggregations (Spark needs to know when a window is "final" before it can append it once and never touch it again).

```python
query = df.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()
```

## 2. **Complete Mode**
- **Outputs the entire result table** after each trigger.
- **Use case**: aggregations where every key's current value is needed on every trigger.
- **Requires**: the aggregation must be one Complete Mode supports (not compatible with watermarked aggregations — see [[Why Complete Mode not Working in Watermarking|Why `complete` Output Mode Doesn't Work with Watermarks]]).

```python
# For aggregations
aggregated_df = df.groupBy("category").count()

query = aggregated_df.writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()
```

## 3. **Update Mode**
- **Outputs only rows that changed** since the last trigger.
- **Use case**: seeing changes in an aggregation as they happen.
- **Note**: if no rows changed, nothing is written that trigger.

```python
query = df.writeStream \
    .outputMode("update") \
    .format("console") \
    .start()
```

## Detailed Comparison

| Mode | Output | Aggregations | Watermark Required | Use Cases |
|------|--------|--------------|-------------------|-----------|
| **Append** | New rows only | Limited (windowed aggregations need a watermark before they can be appended) | Yes (for windowed aggregations) | ETL pipelines, simple transformations |
| **Complete** | Full result set | All types (except watermarked aggregations) | No | Dashboard updates, complete aggregations |
| **Update** | Changed rows only | All types | No | Real-time alerts, change tracking |

## Practical Examples

### Example 1: Append Mode with Watermark
```python
from pyspark.sql.functions import window, col

# With watermark for event-time based processing
windowed_counts = df \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(
        window(col("timestamp"), "5 minutes"),
        "category"
    ) \
    .count()

query = windowed_counts.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()
```

### Example 2: Complete Mode for Aggregations
```python
# Running count without a watermark
running_count = df.groupBy("user_id").count()

query = running_count.writeStream \
    .outputMode("complete") \
    .format("memory") \
    .queryName("user_counts") \
    .start()
```

### Example 3: Update Mode for Real-time Updates
```python
# Real-time word count
word_counts = df \
    .groupBy("word") \
    .count()

query = word_counts.writeStream \
    .outputMode("update") \
    .format("console") \
    .start()
```

## Output Sink Compatibility

Different sinks support different output modes:

| Sink | Append | Complete | Update |
|------|--------|----------|--------|
| **Console** | ✅ | ✅ | ✅ |
| **Memory** | ✅ | ✅ | ✅ |
| **File** | ✅ | ❌ | ❌ |
| **Kafka** | ✅ | ❌ | ❌ |
| **Foreach** | ✅ | ✅ | ✅ |

## Important Considerations

### 1. State Management
```python
# Inspect state-related metrics
spark.conf.set("spark.sql.streaming.numRowsDroppedInWatermark", "0")
spark.conf.set("spark.sql.streaming.metricsEnabled", "true")
```

### 2. Memory Considerations
- **Complete mode** holds the entire aggregation state in memory.
- Use **watermarking** (with append/update) to bound state size for windowed aggregations.
- Monitor state store metrics in the Spark UI.

### 3. Error Handling
```python
query = df.writeStream \
    .outputMode("append") \
    .option("checkpointLocation", "/path/to/checkpoint") \
    .format("console") \
    .start()

query.awaitTermination()
```

Choose the output mode based on the use case, memory constraints, and whether downstream consumers need full snapshots or just deltas.

## 🔗 Related Notes
- [[Watermarking in Streaming|Watermarking in PySpark Structured Streaming]]
- [[Why Complete Mode not Working in Watermarking|Why `complete` Output Mode Doesn't Work with Watermarks]]
- [[Types Of Windows|Window Operations in PySpark Structured Streaming]]

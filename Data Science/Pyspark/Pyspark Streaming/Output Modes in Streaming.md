In PySpark Streaming, output modes define how the results of a streaming query are written to the output sink. Here are the main output modes available:

## 1. **Append Mode** (Default)
- **Only adds new rows** to the output
- **Use case**: When you only care about new data
- **Limitation**: Requires watermark for aggregations

```python
query = df.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()
```

## 2. **Complete Mode**
- **Outputs the entire result table** after each trigger
- **Use case**: Aggregations where you need all results
- **Requires**: All aggregations must be supported

```python
# For aggregations
aggregated_df = df.groupBy("category").count()

query = aggregated_df.writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()
```

## 3. **Update Mode**
- **Outputs only rows that were updated** since last trigger
- **Use case**: When you want to see changes in aggregations
- **Note**: If no rows are updated, no output is written

```python
query = df.writeStream \
    .outputMode("update") \
    .format("console") \
    .start()
```

## Detailed Comparison

| Mode | Output | Aggregations | Watermark Required | Use Cases |
|------|--------|--------------|-------------------|-----------|
| **Append** | New rows only | Limited | Yes (for aggregations) | ETL pipelines, simple transformations |
| **Complete** | Full result set | All types | No | Dashboard updates, complete aggregations |
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
# Running count without watermark
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

Different output modes work with different sinks:

| Sink | Append | Complete | Update |
|------|--------|----------|--------|
| **Console** | ✅ | ✅ | ✅ |
| **Memory** | ✅ | ✅ | ✅ |
| **File** | ✅ | ❌ | ❌ |
| **Kafka** | ✅ | ❌ | ❌ |
| **Foreach** | ✅ | ✅ | ✅ |

## Important Considerations

### 1. **State Management**
```python
# Check state information
spark.conf.set("spark.sql.streaming.numRowsDroppedInWatermark", "0")
spark.conf.set("spark.sql.streaming.metricsEnabled", "true")
```

### 2. **Memory Considerations**
- **Complete mode** stores entire state in memory
- Use **watermarking** to limit state size
- Monitor **state store metrics**

### 3. **Error Handling**
```python
query = df.writeStream \
    .outputMode("append") \
    .option("checkpointLocation", "/path/to/checkpoint") \
    .format("console") \
    .start()

query.awaitTermination()
```

Choose the output mode based on your specific use case, memory constraints, and the type of processing you're performing.
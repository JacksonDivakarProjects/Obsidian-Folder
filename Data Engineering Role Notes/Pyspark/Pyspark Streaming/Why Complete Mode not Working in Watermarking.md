# Why `complete` Output Mode Doesn't Work with Watermarks

A common point of confusion in Structured Streaming.

## 1️⃣ Recap: Output Modes

|Mode|What It Writes|State Requirement|
|---|---|---|
|**append**|Only new rows since the last trigger|Minimal|
|**update**|Only rows that changed since the last trigger|Tracks updated state|
|**complete**|Full aggregation results for every key|Maintains full state|

## 2️⃣ Watermark Behavior

Watermarking exists to **drop old state**, preventing unbounded memory growth. Once a watermark is set, Spark removes state for windows older than `eventTime - watermark` — only "active" windows are kept.

## 3️⃣ Why `complete` Mode Breaks with Watermarks

**The problem:**
- `complete` mode requires Spark to output the **full state of the aggregation for every window**.
- With a watermark, some state has already been **dropped** (windows older than the threshold).
- Spark can't output a "complete" state that includes windows it no longer has.

**The result:** Spark raises an error, e.g.:
```
Exception: 'complete' output mode not supported with watermarking on aggregation
```

**Bottom line:** `complete` mode is incompatible with watermarking because the watermark prunes old state, and `complete` requires all state to still be present.

## 4️⃣ Workarounds

### A. Use `update` Mode

Outputs only rows that changed since the last trigger, not the full state — compatible with watermarking because Spark only needs to report on the windows it still has.

```python
agg_df = df.withWatermark("timestamp", "5 minutes") \
           .groupBy(window(col("timestamp"), "10 minutes")) \
           .count()

agg_df.writeStream \
      .format("console") \
      .outputMode("update") \
      .start()
```

✅ Works because Spark outputs only the updated windows, not the whole aggregation.

### B. Use `append` Mode

Works well for aggregations where each row should be emitted only once — typically once a window has closed and is guaranteed final (tumbling or session windows).

```python
agg_df = df.withWatermark("timestamp", "5 minutes") \
           .groupBy(window(col("timestamp"), "10 minutes")) \
           .count()

agg_df.writeStream \
      .format("console") \
      .outputMode("append") \
      .start()
```

Here, Spark emits a window's result only once it's finalized by the watermark.

## 5️⃣ Key Takeaways

1.  **Complete mode** = full state for every key/window.
2.  **Watermark** = prunes old windows to bound memory.
3.  **Conflict**: complete mode expects all state to still exist; the watermark has already discarded some of it.
4.  **Solution**: use `update` or `append` mode with watermarked aggregations — never `complete`.

💡 **Rule of thumb:** when doing windowed aggregations with watermarks, always use `update` or `append` mode.

## 🔗 Related Notes
- [[Watermarking in Streaming|Watermarking in PySpark Structured Streaming]]
- [[Output Modes in Streaming|Output Modes in Streaming]]
- [[Types Of Windows|Window Operations in PySpark Structured Streaming]]

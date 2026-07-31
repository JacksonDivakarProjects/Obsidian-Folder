Absolutely, Jack. This is a **common point of confusion** in PySpark Structured Streaming. Let’s go step by step and explain **why `complete` mode doesn’t work with watermarking in some cases**.

---

# **Why `complete` Output Mode Doesn’t Work with Watermarks**

## **1️⃣ Recap: Output Modes**

In Structured Streaming, there are three output modes:

|Mode|What it writes|State Requirement|
|---|---|---|
|**append**|Only new rows since last trigger|Minimal|
|**update**|Only rows that changed since last trigger|Tracks updated state|
|**complete**|Full aggregation results for all keys|Maintains full state|

---

## **2️⃣ Watermark Behavior**

Watermarking is designed to **drop old state** to prevent unbounded memory growth.

- When you set a watermark, Spark **removes state for windows older than `eventTime + watermark`**.
    
- This affects **aggregations**: only “active” windows are kept.
    

---

## **3️⃣ Why `complete` Mode Breaks with Watermarks**

**Problem**:

- `complete` mode **requires Spark to output the full state of the aggregation for all windows**.
    
- But with a watermark, **some state is dropped** (old windows beyond the watermark).
    
- Spark **cannot output the “complete” state** for dropped windows.
    

**Result**:

- Spark throws an **error** like:
    

```
Exception: 'complete' output mode not supported with watermarking on aggregation
```

**Bottom line**:

> `complete` mode is **incompatible with watermarking** because watermark **prunes old state**, and `complete` expects **all state to be present**.

---

## **4️⃣ Workarounds**

### **A. Use `update` Mode**

- Only outputs **rows that changed since last trigger**, not full state.
    
- Compatible with watermarking because Spark only keeps **active windows**.
    

```python
agg_df = df.withWatermark("timestamp", "5 minutes") \
           .groupBy(window(col("timestamp"), "10 minutes")) \
           .count()

agg_df.writeStream \
      .format("console") \
      .outputMode("update") \
      .start()
```

✅ This works because Spark outputs **updated windows only**, not the full aggregation.

---

### **B. Use `append` Mode**

- Works for aggregations **where each row is output only once**, e.g., when a window **closes**.
    
- Typically used with **tumbling or session windows**.
    

```python
agg_df = df.withWatermark("timestamp", "5 minutes") \
           .groupBy(window(col("timestamp"), "10 minutes")) \
           .count()

agg_df.writeStream \
      .format("console") \
      .outputMode("append") \
      .start()
```

- Here, Spark outputs **results only when the window is finalized**.
    

---

## **5️⃣ Key Takeaways**

1. **Complete mode = full state for all keys/windows**.
    
2. **Watermark = prunes old windows** to save memory.
    
3. **Conflict**: complete mode expects all state, but watermark drops some.
    
4. **Solution**: use **update** or **append mode** with watermarks.
    

---

💡 **Rule of Thumb**:

> When doing **windowed aggregations with watermarks**, **always use `update` or `append` mode**. Never use `complete` mode.

---

If you want, I can create a **diagram showing why complete mode fails with watermarking** and how update/append modes work instead — it makes this super clear visually.

Do you want me to make that diagram?
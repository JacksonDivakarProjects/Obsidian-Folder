# Driver Out-Of-Memory (OOM) in Spark

## 1. What Is Driver OOM?
- Happens when the driver process runs out of allocated JVM heap (or PySpark process memory, when using Python).
- Since the driver is the control plane, a driver OOM crashes the entire application.

## 2. Common Causes

### Collecting Too Much Data
```python
df = spark.read.parquet("big_dataset")
rows = df.collect()   # loads the entire dataset into driver memory
```
Pulls every partition from the executors into the driver, filling its heap or Python process RAM.

### Using `.toPandas()` on Large Data
Converts the entire DataFrame into a pandas DataFrame, materializing all of it in driver memory (Python process).

### Large Broadcast Variables
Broadcasting big Python objects (e.g. dictionaries of hundreds of MBs) forces the driver to serialize and hold them before distribution.

### Excessive Job Metadata / Lineage
Long-running jobs with thousands of stages or cached RDDs accumulate DAG and task metadata in the driver.

### High Concurrency of Task Results
Many tasks returning large result sets simultaneously can overwhelm Netty buffers and driver heap.

### Misconfigured Driver Memory
`spark.driver.memory` set too low, or `spark.driver.memoryOverhead` too small for native buffers and the Python process.

## 3. Symptoms
- `java.lang.OutOfMemoryError: Java heap space`
- `java.lang.OutOfMemoryError: GC overhead limit exceeded`
- Python crashes with `MemoryError` (PySpark)
- Spark UI shows the job stuck "collecting results"
- OS monitoring shows the driver process consuming all RAM before being killed

## 4. Strategies to Handle Driver OOM

### A. Reduce Data Movement to the Driver
- Avoid `.collect()` — use `.take(n)`, `.limit()`, or `.sample()` instead.
- Avoid `.toPandas()` on large datasets — use distributed operations, or write to external storage with `df.write()`.

```python
sample = df.limit(1000).toPandas()  # safe: only a small subset reaches the driver
```

### B. Control Result Size
```python
.config("spark.driver.maxResultSize", "1g")
```
Prevents executors from overwhelming the driver with a huge combined result.

### C. Manage Broadcast Variables
- Only broadcast small reference data (a few MBs).
- For large lookup tables, store them in distributed storage (Hive, Delta, Redis) instead of broadcasting.

### D. Optimize Metadata
- Checkpoint or selectively cache to cut down lineage size.
- Avoid creating thousands of small DataFrames unnecessarily.

### E. Increase Driver Memory
```bash
spark-submit --driver-memory 6g --conf spark.driver.memoryOverhead=1g ...
```
For PySpark, increase `memoryOverhead` too, since the Python process and Arrow buffers use native memory outside the JVM heap.

## 5. Quick Checklist
- [ ] Never use `collect()` or `toPandas()` on the full dataset.
- [ ] Cap result size with `spark.driver.maxResultSize`.
- [ ] Broadcast only small objects.
- [ ] Use distributed writes instead of pulling results to the driver.
- [ ] Checkpoint to cut lineage bloat.
- [ ] Monitor driver heap and Python process memory.
- [ ] Increase `spark.driver.memory` / `spark.driver.memoryOverhead` as needed.

## In Short
Driver OOM = too much data or metadata piling up in the driver. Fix it by keeping work on the executors, capping results, and configuring driver memory properly.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Driver Memory Management|Spark Driver Memory Architecture]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Executer OOM with Salting|Executor OOM in Spark (with Salting)]]

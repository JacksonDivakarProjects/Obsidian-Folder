# Spark Driver Memory Architecture

## 1. Role of the Driver
- Central coordinator of a Spark application.
- Builds DAGs, schedules tasks, tracks metadata, and communicates with executors.
- Runs inside a JVM process, plus a separate Python process when using PySpark.

## 2. Memory Layout of the Driver

### JVM Heap (primary area)
- **Scheduler & Metadata** — `SparkContext`, `DAGScheduler`, `TaskScheduler`; stores job/stage/task objects and lineage information.
- **BlockManager (driver-side)** — holds small cached blocks (rare, mostly in local mode) and keeps copies of broadcast variables before they're distributed to executors.
- **Task Results** — temporary storage for results received from executors before they're handed to user code.
- **User Objects** — any data structures created in driver code.

### JVM Non-Heap
- **Metaspace / Code Cache** — class metadata, compiled code.
- **Direct Buffers (Netty, IO)** — network communication, shuffle metadata.

### Native / Off-Heap
- Used by Spark's Tungsten engine when off-heap memory is enabled.
- Reduces GC pressure by storing serialized data outside the JVM heap.

### Python Process Memory (PySpark only)
- Runs alongside the JVM when using the Python APIs.
- Holds objects returned by `collect()` / `toPandas()`, plus pandas, NumPy, and Arrow buffers.
- Independent of the JVM heap, but still counts toward the driver's total memory footprint.

## 3. Key Configurations
- **Heap size** — `spark.driver.memory` sets the JVM heap (e.g. `--driver-memory 4g`).
- **Overhead (off-heap, native)** — `spark.driver.memoryOverhead` reserves extra memory for native buffers and the Python process.
- **Result size cap** — `spark.driver.maxResultSize` caps how much result data the driver can hold at once.

## 4. Summary Table
| Component | Purpose |
|---|---|
| JVM Heap – Scheduler | Metadata, DAGs, SparkContext |
| JVM Heap – BlockManager | Cached blocks, broadcast copies |
| JVM Heap – Task Results | Data returned from executors |
| JVM Heap – User Objects | User-created variables/data structures |
| JVM Non-Heap | Metaspace, compiled code, Netty buffers |
| Native / Off-Heap | Tungsten, direct buffers |
| Python Process (PySpark) | Pandas, NumPy, Arrow data |

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Driver OOM|Driver Out-Of-Memory (OOM) in Spark]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Executer Memory Management|Spark Executor Memory Architecture]]

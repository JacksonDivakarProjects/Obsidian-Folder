# Spark Executor Memory Architecture

## 1. Role of the Executor
- Executors are worker JVM processes launched on cluster nodes.
- They perform the actual task execution (map, filter, join, aggregate).
- They manage data caching and shuffle storage.
- Each executor has a fixed amount of memory, divided across specific regions.

## 2. Executor Memory Layout
Executors use Spark's Unified Memory Manager (since Spark 1.6), which allows flexible sharing between execution and storage memory.

```
Executor JVM Memory
+----------------------------------------------------+
| Reserved Memory (~300MB)                            |
+----------------------------------------------------+
| User Memory (~40% of usable heap)                   |
+----------------------------------------------------+
| Spark Memory (~60% of usable heap)                  |
|   +------------------+--------------------------+   |
|   | Execution Memory | Storage Memory           |   |
|   | (shuffle, sort)  | (cache, broadcast vars)  |   |
|   +------------------+--------------------------+   |
+----------------------------------------------------+
```

### Reserved Memory
- A small fixed amount (~300 MB).
- Used internally by Spark; not configurable.
- Ensures critical operations don't fail outright.

### User Memory
- The remaining share of the heap after reserved memory and Spark's unified memory are carved out — `1 - spark.memory.fraction`, about **40%** of usable heap by default.
- Stores user-defined data structures, UDF variables/objects, and internal Spark bookkeeping not managed by the Unified Memory Manager.

### Spark Memory (Unified Region)
- Governed by `spark.memory.fraction`, which defaults to **0.6** (60% of usable heap, after reserved memory).
- Split dynamically between:
  1. **Execution Memory** — computation (joins, aggregations, sorts, shuffle read/write buffers).
  2. **Storage Memory** — caching/persisting RDDs or DataFrames, and broadcast variables. Spills to disk if there isn't enough room.
- Execution and storage share this pool: if execution needs more memory, it can evict cached blocks and borrow from storage.

### Off-Heap Memory (Optional)
- Enabled via `spark.memory.offHeap.enabled=true`.
- Allocated outside the JVM heap, managed manually by Spark for Tungsten/columnar storage.
- Sized via `spark.memory.offHeap.size`.

## 3. Key Configurations
- **Heap size per executor** — `spark.executor.memory` sets the JVM heap.
- **Overhead for native buffers** — `spark.executor.memoryOverhead` (default = `max(384MB, 0.1 * executor memory)`).
- **Fraction of heap used by Spark memory** — `spark.memory.fraction` (default 0.6).
- **Storage fraction within Spark memory** — `spark.memory.storageFraction` (default 0.5).

## 4. Summary Table
| Component | Purpose |
|---|---|
| Reserved Memory | Internal Spark tasks (~300 MB, fixed) |
| User Memory | User objects, UDFs, Spark metadata |
| Execution Memory | Joins, aggregations, shuffles, sorts |
| Storage Memory | Cache, persist, broadcast variables |
| Off-Heap Memory | Optional Tungsten/Arrow storage, reduces GC load |
| Memory Overhead | Native/OS memory for the executor (buffers, Python) |

## 5. Example (PySpark Config)
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("executor-memory-demo") \
    .config("spark.executor.memory", "8g") \
    .config("spark.executor.memoryOverhead", "2g") \
    .config("spark.memory.fraction", "0.6") \
    .config("spark.memory.storageFraction", "0.5") \
    .getOrCreate()
```

## Quick Recap
- Executors = workers that run tasks and cache data.
- Memory splits into Reserved, User Memory, Spark Memory (Execution + Storage), and optional Off-Heap.
- The Unified Memory Manager allows flexible sharing between Execution and Storage.
- Key knobs: `spark.executor.memory`, `spark.executor.memoryOverhead`, `spark.memory.fraction`, `spark.memory.storageFraction`.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Driver Memory Management|Spark Driver Memory Architecture]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Executer OOM with Salting|Executor OOM in Spark (with Salting)]]

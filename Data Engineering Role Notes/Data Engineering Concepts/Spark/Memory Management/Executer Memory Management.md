Got it, Jack. Let’s now go **straight into the Spark Executor memory architecture** in the same **focused, guide-style** way we handled the Driver. No OOM discussion here, just the **core architecture and memory areas**.

---

# ⚡ Spark Executor Memory Architecture

---

## 1) Role of the Executor

- Executors are **worker JVM processes** launched on cluster nodes.
    
- They perform **actual task execution** (map, filter, join, aggregate).
    
- They manage **data caching** and **shuffle storage**.
    
- Each executor has a fixed amount of memory, divided across specific regions.
    

---

## 2) Executor Memory Layout

Executors use Spark’s **Unified Memory Manager** (post-1.6), which allows flexible sharing between execution and storage.

```
Executor JVM Memory
+----------------------------------------------------+
| Reserved Memory (~300MB)                           |
+----------------------------------------------------+
| User Memory (~25% of heap)                         |
+----------------------------------------------------+
| Spark Memory (~75% of heap)                        |
|   +------------------+--------------------------+  |
|   | Execution Memory | Storage Memory           |  |
|   | (shuffle, sort)  | (cache, broadcast vars)  |  |
|   +------------------+--------------------------+  |
+----------------------------------------------------+
```

---

### 🔹 1. Reserved Memory

- A small fixed amount (~300 MB).
    
- Used internally by Spark; not configurable.
    
- Ensures critical operations don’t fail.
    

---

### 🔹 2. User Memory

- About **25% of the heap by default** (`1 - spark.memory.fraction`).
    
- Stores:
    
    - User-defined data structures.
        
    - UDF variables and objects.
        
    - Internal Spark bookkeeping not managed by the Unified Memory Manager.
        

---

### 🔹 3. Spark Memory (Unified Region)

- About **75% of the heap** (`spark.memory.fraction`, default = 0.6 of heap).
    
- Split dynamically between:
    
    1. **Execution Memory**
        
        - For computation (joins, aggregations, sorts, shuffles).
            
        - Shuffle read/write buffers.
            
    2. **Storage Memory**
        
        - For caching/persisting RDDs or DataFrames.
            
        - For broadcast variables.
            
        - Can spill to disk if insufficient.
            

> Note: Execution and Storage share this pool. If execution needs more, it can borrow from storage (evict cached blocks).

---

### 🔹 4. Off-Heap Memory (Optional)

- Enabled via `spark.memory.offHeap.enabled=true`.
    
- Allocated outside JVM heap.
    
- Managed manually by Spark for Tungsten/columnar storage.
    
- Configured by:
    
    - `spark.memory.offHeap.size`.
        

---

## 3) Key Configurations for Executor Memory

- **Heap size per executor:**  
    `spark.executor.memory` → sets JVM heap.
    
- **Overhead for native/native buffers:**  
    `spark.executor.memoryOverhead` → extra memory (default = max(384MB, 0.1 * executor memory)).
    
- **Fraction of heap used by Spark memory:**  
    `spark.memory.fraction` (default 0.6).
    
- **Storage fraction (within Spark memory):**  
    `spark.memory.storageFraction` (default 0.5 of Spark memory).
    

---

## 4) Summary Table

|Component|Purpose|
|---|---|
|Reserved Memory|Internal Spark tasks (~300 MB, fixed)|
|User Memory|User objects, UDFs, Spark metadata|
|Execution Memory|Joins, aggregations, shuffles, sorts|
|Storage Memory|Cache, persist, broadcast variables|
|Off-Heap Memory|Optional Tungsten/Arrow storage, reduces GC load|
|Memory Overhead|Native/OS memory for executor (buffers, Python)|

---

## 5) Executor Memory Example (PySpark config)

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

---

✅ **Quick Recap**:

- Executors = workers running tasks + caching data.
    
- Memory split: Reserved, User Memory, Spark Memory (Execution + Storage), Off-Heap.
    
- Unified manager allows flexible sharing between Execution and Storage.
    
- Config knobs: `spark.executor.memory`, `spark.executor.memoryOverhead`, `spark.memory.fraction`, `spark.memory.storageFraction`.
    

---

Jack, do you want me to now **combine the Driver + Executor architecture into a side-by-side comparison table/diagram** so you can see both perspectives clearly in one place?

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Driver Memory Management|Spark Driver Memory Architecture]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Executer OOM with Salting|Executor OOM in Spark (with Salting)]]

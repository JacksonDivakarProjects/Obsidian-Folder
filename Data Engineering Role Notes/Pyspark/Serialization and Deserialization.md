# Serialization and Deserialization in Spark

Understanding serialization/deserialization matters because Spark is a distributed system spanning both the JVM and Python.

## 🔹 1. Serialization

- **Definition:** converting an object (a Python dict, DataFrame row, or other object) into a **byte stream** so it can be sent over the network or written to disk.
- Spark relies on this whenever data needs to move **between the JVM and Python** (PySpark) or **between cluster nodes**.

**Example:**

```python
import pickle

# Python object
data = {"name": "Alice", "age": 30}

# Serialized form (byte stream)
b = pickle.dumps(data)
```

`b` can now be sent to another machine or saved to disk.

---

## 🔹 2. Deserialization

- **Definition:** converting a byte stream **back into the original object** so the program can use it again.

**Example:**

```python
data_copy = pickle.loads(b)
print(data_copy)  # {'name': 'Alice', 'age': 30}
```

---

## 🔹 Why It Matters in Spark

1.  **PySpark communication**
    - Spark's core execution engine runs on the JVM (Scala/Java).
    - Python DataFrame operations need Python objects to cross the JVM ↔ Python boundary.
    - Crossing that boundary means **serialization** (Python → bytes) on one side and **deserialization** (bytes → Python) on the other.
2.  **Network communication**
    - When Spark shuffles data between nodes, rows are serialized to send across the cluster, then deserialized at the destination.
3.  **Performance impact**
    - Serialization/deserialization is **expensive**, especially for row-wise Python UDFs.
    - Native Spark functions (`F.col() * F.col()`) stay entirely inside the JVM and never cross that boundary — which is exactly why they're faster than an equivalent Python UDF. See [[Functions in Pyspark|Functions in Pyspark]] for the UDF performance comparison.

---

### Quick Analogy

- Serialization → packing luggage to send by courier.
- Deserialization → unpacking it at the destination.

---

### TL;DR

- **Serialization:** object → byte stream.
- **Deserialization:** byte stream → object.
- Spark uses this crossing **Python ↔ JVM** and **between nodes**.
- Minimizing this crossing — via native Spark functions or Pandas UDFs (which batch the transfer using Apache Arrow) — means faster execution.
- `.toPandas()` triggers a similar cost: it serializes the entire result set from the JVM to Python in one shot, which is why it's risky on large DataFrames — see [[Pyspark .collect()|Pyspark .collect()]] for the same caveat applied to `.collect()`.

## 🔗 Related Notes
- [[Performance & Optimisation in Pyspark|Performance & Optimisation in Pyspark]]
- [[Spark RDD|Spark RDD]]
- [[Functions in Pyspark|Functions in Pyspark]]

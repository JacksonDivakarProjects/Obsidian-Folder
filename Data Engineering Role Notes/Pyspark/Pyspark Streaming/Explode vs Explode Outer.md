# `explode()` vs `explode_outer()`

A common point of confusion in PySpark: both flatten array/map columns into rows, but they disagree on what happens to nulls and empty arrays.

### 🔹 `explode()`

- **Purpose:** flattens an array or map column — each element becomes a separate row.
- **Behavior:** **removes rows** where the column is `null` or an empty array `[]`. That row simply disappears from the output.

**Example:**

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode
spark = SparkSession.builder.getOrCreate()

df = spark.createDataFrame([
    (1, ["a", "b"]),
    (2, []),
    (3, None)
], ["id", "letters"])

df.select("id", explode("letters").alias("letter")).show()
```

**Output:**

```
+---+------+
| id|letter|
+---+------+
|  1|     a|
|  1|     b|
+---+------+
```

Rows with `[]` or `None` were dropped entirely.

---

### 🔹 `explode_outer()`

- **Purpose:** same as `explode()`, but **preserves rows** even when the array/map is empty or null.
- **Behavior:** for `null` or `[]`, keeps the row and fills the exploded column with `null` instead of dropping it.

**Example:**

```python
from pyspark.sql.functions import explode_outer

df.select("id", explode_outer("letters").alias("letter")).show()
```

**Output:**

```
+---+------+
| id|letter|
+---+------+
|  1|     a|
|  1|     b|
|  2|  null|
|  3|  null|
+---+------+
```

---

### ✅ Summary

|Function|Keeps rows with `null`/empty array|Output behavior|
|---|---|---|
|`explode()`|❌ No|Drops such rows|
|`explode_outer()`|✅ Yes|Keeps rows, fills with `null`|

### 👉 Rule of Thumb

- Use `explode()` when only **real, present data** matters (non-empty arrays).
- Use `explode_outer()` when row structure needs to be **preserved** — e.g. to keep consistent row counts, or to avoid silently losing records after a left join that produced empty arrays.

The same distinction applies to map columns: an empty or null map is dropped by `explode()` but kept (with null key/value) by `explode_outer()`.

## 🔗 Related Notes
- [[Spark Streaming Foundational Concepts|Spark Streaming Foundational Concepts]]
- [[Schema Operation in Pyspark|📘 Schema Operations in PySpark]]

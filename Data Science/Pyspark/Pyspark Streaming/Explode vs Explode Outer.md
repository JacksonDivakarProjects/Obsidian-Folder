Good question — this one trips up a lot of PySpark users. Let’s break it down clearly.

---

### 🔹 `.explode()` (standard explode)

- **Purpose:** Flattens an array or map column — each element becomes a separate row.
    
- **Behavior:**
    
    - **Removes `null` or empty arrays.**
        
    - So, if the column is `null` or `[]`, the row **disappears** from the output.
        

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

Rows with `[]` or `None` were dropped.

---

### 🔹 `.explode_outer()`

- **Purpose:** Similar to `.explode()`, but **preserves rows even if the array or map is empty or null.**
    
- **Behavior:**
    
    - For `null` or `[]`, keeps the row and fills the exploded value with `null`.
        

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

### ✅ **Summary Table**

|Function|Keeps rows with `null`/empty array|Output behavior|
|---|---|---|
|`explode()`|❌ No|Drops such rows|
|`explode_outer()`|✅ Yes|Keeps rows, fills with `null`|

---

**👉 Rule of Thumb:**

- Use `explode()` when you want **only real data** (non-empty arrays).
    
- Use `explode_outer()` when you want to **maintain row structure** (e.g., for left joins or consistent row counts).
    

Would you like me to include how it behaves for **map columns** (key–value pairs) too?
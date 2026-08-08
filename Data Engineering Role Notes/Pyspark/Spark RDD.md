# RDDs: What You Actually Need to Know

You do **not** need deep RDD knowledge for most modern PySpark work, but the essentials below are worth having.

### 1. The Absolute Essentials

**RDD = Resilient Distributed Dataset**
- **Resilient:** can recover from failures using lineage (Spark knows how to rebuild lost data from the transformations that produced it).
- **Distributed:** data lives across multiple machines.
- **Dataset:** a collection of your data.

**Key insight:** RDDs are Spark's low-level API. DataFrames are built on top of RDDs, but add a query optimizer (Catalyst) and better performance.

---

### 2. When You Might Actually Need RDDs

Only in these specific cases:
1.  Extremely custom algorithms that can't be expressed with DataFrame operations.
2.  Working with unstructured data (e.g. raw text needing complex parsing before it has any schema).
3.  Low-level performance tuning for very specific use cases.

**For roughly 95% of workloads: stick with DataFrames.**

---

### 3. Just Enough Syntax to Recognize It

#### Creating RDDs (common in older code):
```python
# From SparkContext (old way)
from pyspark import SparkContext
sc = SparkContext.getOrCreate()
rdd = sc.parallelize([1, 2, 3, 4, 5])

# From a DataFrame (sometimes useful)
df = spark.createDataFrame([(1, "A"), (2, "B")], ["id", "name"])
rdd = df.rdd  # Convert to RDD
```

#### Basic Operations:
```python
# Transformations (lazy - return a new RDD)
mapped = rdd.map(lambda x: x * 2)          # Apply a function to each element
filtered = rdd.filter(lambda x: x > 3)     # Keep elements matching a condition

# Actions (eager - return a result)
result = rdd.collect()    # Bring all data to the driver (be careful!)
count = rdd.count()       # Count elements
```

#### The One RDD Pattern Worth Knowing:
```python
# Word count - the classic RDD example
text_rdd = sc.textFile("file.txt")
word_counts = (text_rdd.flatMap(lambda line: line.split())
                      .map(lambda word: (word, 1))
                      .reduceByKey(lambda a, b: a + b))
```

---

### 4. Conversion Patterns

#### DataFrame → RDD (occasionally needed):
```python
df = spark.read.csv("data.csv")
rdd = df.rdd

# RDD of Row objects - access fields with row['column_name']
rdd.map(lambda row: row['name'])
```

#### RDD → DataFrame (much more common):
```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Method 1: infer schema (easy)
df = spark.createDataFrame(rdd, ["column1", "column2"])

# Method 2: specify schema (better - avoids incorrect type inference)
schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True)
])
df = spark.createDataFrame(rdd, schema)
```

---

### 5. What to Focus On Instead

Spend the time on these instead of RDDs:
1.  **DataFrame API** — the main tool for everything.
2.  **Spark SQL** — for querying data.
3.  **Performance optimization** — partitioning, caching, query planning.
4.  **Structured Streaming** — for real-time data.
5.  **MLlib's DataFrame-based API** — for machine learning.

---

### 6. Quick Reference: RDD → DataFrame Equivalent

| If You See This | What It Means | What to Use Instead |
|----------------|---------------|----------------------------|
| `sc.parallelize()` | Creating an RDD from a list | `spark.createDataFrame()` |
| `rdd.map()` | Transforming each element | DataFrame `withColumn()` or `select()` |
| `rdd.filter()` | Filtering rows | DataFrame `filter()` or `where()` |
| `rdd.collect()` | Bringing all data to the driver | `df.collect()`, but be just as careful about size |
| `reduceByKey()` | Aggregating by key | DataFrame `groupBy().agg()` |

---

### 7. The Bottom Line

Recognize RDD syntax when reading older code or examples, but rarely write new RDD code.

**Suggested time allocation:**
- **95%** → DataFrames and Spark SQL.
- **4%** → RDD concepts, enough to read old code.
- **1%** → actually writing RDD code (edge cases only).

**When you encounter RDDs in the wild, the first question should be:** *"Can this be a DataFrame instead?"*

## 🔗 Related Notes
- [[Data Engineering Role Notes/Pyspark/Miscellaneous Concepts|Miscellaneous Concepts]]
- [[Pyspark .collect()|Pyspark .collect()]]
- [[Serialization and Deserialization|Serialization and Deserialization]]

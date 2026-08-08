# Miscellaneous PySpark Concepts

Two small but common points of confusion: when `parallelize()` is actually needed, and how `PERMISSIVE` mode's `_corrupt_record` column behaves.

## 1. Why `parallelize()` Exists — and Why DataFrames Rarely Need It

`sc.parallelize()` is an **RDD API** method: it takes local data (e.g. a Python list) and distributes it across the cluster as an RDD.

```python
rdd = sc.parallelize([1, 2, 3, 4, 5])
```

A **DataFrame** is a higher-level abstraction built on top of RDDs. Rather than parallelizing local collections yourself, you use Spark's DataFrame readers, and Spark handles partitioning and distribution automatically:

```python
df = spark.read.csv("file.csv", header=True)
df = spark.read.parquet("data.parquet")
df = spark.read.json("data.json")
```

### Creating DataFrames from Local Data

Even with local Python data, you don't call `parallelize()` directly — use `spark.createDataFrame()`:

```python
data = [("Jack", 23), ("Anna", 29), ("Sam", 35)]
df = spark.createDataFrame(data, ["name", "age"])
df.show()
```

Under the hood, Spark's `createDataFrame()` uses the same distribution mechanism as `parallelize()`, but you never call it yourself.

### Rule of Thumb

- Use `parallelize()` → only when working directly with RDDs.
- Use `spark.createDataFrame()` or `spark.read.*` → for DataFrames.
- In modern PySpark, you mostly work with **DataFrames**, not raw RDDs — normal DataFrame workflows don't need `parallelize()` at all.

---

## 2. `PERMISSIVE` Mode and the `_corrupt_record` Column

A common point of confusion: why doesn't `_corrupt_record` show up in `df.columns` even though `PERMISSIVE` mode is active?

### How `PERMISSIVE` Mode Works

```python
df = spark.read.option("mode", "PERMISSIVE") \
               .option("columnNameOfCorruptRecord", "_corrupt_record") \
               .csv("file.csv")
```

- **`PERMISSIVE`** (the default mode) tries to parse each row according to the schema.
- A row that doesn't match the schema has its raw text stored in the column named by `columnNameOfCorruptRecord` — commonly `_corrupt_record`.
- If no schema is specified, Spark infers one automatically from the data.

### Why the Column Sometimes Doesn't Appear

1.  If you don't specify a schema, Spark infers one from **only the columns it can see in the data** — `_corrupt_record` is not part of that inference. It only materializes once a row actually fails parsing.
2.  Even with `inferSchema=True`, the inferred schema won't include `_corrupt_record` unless there are rows that actually fail to parse against it.

So: a clean CSV, read without an explicit schema, will simply never show `_corrupt_record` — there's nothing to flag.

### Guaranteeing the Column Exists

Explicitly define the schema and include `_corrupt_record` as a `StringType` field:

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

schema = StructType([
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True),
    StructField("_corrupt_record", StringType(), True)
])

df_with_errors = spark.read.option("mode", "PERMISSIVE") \
                           .schema(schema) \
                           .csv("potentially_bad_data/*.csv")
```

Now `_corrupt_record` is always present in `df_with_errors.columns`, and any row that doesn't match the `name`/`age` types gets its full raw text placed there.

### Key Notes

- `PERMISSIVE` is the default mode, so specifying it explicitly is optional.
- `_corrupt_record` only appears automatically when **both**: (1) it's named via `columnNameOfCorruptRecord`, and (2) there are rows Spark can't parse.
- If the source file is genuinely clean, the column won't show up unless you explicitly add it to the schema.

## 🔗 Related Notes
- [[Spark RDD|Spark RDD]]
- [[Pyspark Reading Modes|Pyspark Reading Modes]]
- [[Pyspark Programs|Pyspark Programs]]

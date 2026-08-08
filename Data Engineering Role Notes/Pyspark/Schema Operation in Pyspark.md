# 📘 Schema Operations in PySpark

Schemas define a DataFrame's structure — column names, data types, and nullability. Managing them correctly improves performance, ensures data consistency, and avoids runtime errors.

---

## 🔹 1. Viewing Schema

```python
df.printSchema()
print(df.schema)   # returns a StructType object
```

---

## 🔹 2. Defining Schema While Reading Data

### (A) DDL String Format

- A quick way to define a schema with SQL-like syntax.
- Data type keywords are case-insensitive, but conventionally written in UPPERCASE.

```python
schema = "id INT, name STRING, salary DOUBLE"

df = spark.read.format("csv") \
    .option("header", True) \
    .schema(schema) \
    .load("/path/to/file.csv")
```

### (B) StructType and StructField

- More explicit and flexible.
- Best for complex schemas (nested structs, arrays, maps).

```python
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType

schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("salary", DoubleType(), True)
])

df = spark.read.format("csv") \
    .option("header", True) \
    .schema(schema) \
    .load("/path/to/file.csv")
```

---

## 🔹 3. Inferring Schema Automatically

- Not recommended for large datasets — it forces an extra pass over the data before the real read even starts.

```python
df = spark.read.csv("/path/to/file.csv", header=True, inferSchema=True)
```

---

## 🔹 4. Working with Schema After DataFrame Creation

### (A) Casting Columns to New Types

```python
df = df.selectExpr(
    "cast(id as INT) as id",
    "cast(name as STRING) as name",
    "cast(salary as DOUBLE) as salary"
)
```

### (B) Re-applying a Schema via RDD

```python
new_schema = "id INT, name STRING, salary DOUBLE"
df = spark.createDataFrame(df.rdd, schema=new_schema)
```

---

## 🔹 5. Schema Operations Recap

- `.schema(...)` — usable **only during `spark.read`**, to apply a schema on load.
- `.schema` (property) — returns the schema of an existing DataFrame.
- **DDL string** → `"col1 INT, col2 STRING"` (quick, SQL-style).
- **StructType** → more verbose but supports nested structures.
- For an **already-created DataFrame**, use:
    - `selectExpr` or `withColumn` — for type casting.
    - `createDataFrame(df.rdd, new_schema)` — for reassigning the schema wholesale.

---

## 🔹 6. Example with CSV

```python
# Read without a schema
df = spark.read.format("csv").option("header", True).load("/path/to/BigMart Sales.csv")

# Apply a new schema using DDL
ddl_schema = "Item_Identifier STRING, Item_Weight DOUBLE, Item_Fat_Content STRING, Item_Visibility DOUBLE"
df1 = spark.createDataFrame(df.rdd, schema=ddl_schema)

df1.printSchema()
```

---

## 🔹 7. Checking and Extracting Schema Information

```python
# Get column names
df.columns  

# Get schema as JSON (useful for saving/versioning)
print(df.schema.json())

# Loop through schema fields
for field in df.schema.fields:
    print(field.name, field.dataType, field.nullable)
```

---

## 🔹 8. Modifying Schema (Column Renames)

```python
df = df.withColumnRenamed("oldName", "newName")
```

---

## 🔹 9. Nested Schemas

PySpark supports complex, nested structures:

```python
from pyspark.sql.types import ArrayType, StructType, StructField, StringType

nested_schema = StructType([
    StructField("id", StringType(), True),
    StructField("tags", ArrayType(StringType()), True),
    StructField("profile", StructType([
        StructField("age", StringType(), True),
        StructField("gender", StringType(), True)
    ]), True)
])
```

---

## 🔹 10. Saving Data with Schema

- Writing to **Parquet/Delta** automatically stores the schema alongside the data.
- **CSV** does not store schema information — you must reapply it on every read.

---

## 🔹 11. Evolving Schemas

When writing with Parquet/Delta:

```python
df.write.option("mergeSchema", "true").parquet("path/to/output")
```

This lets Spark merge in new columns that appear in later writes.

---

## 🔹 12. Performance Tip

- Defining a schema manually (`StructType` or DDL string) is **faster** than `inferSchema=True`, because Spark doesn't need to scan the data first to guess types.

---

## ✅ Best Practices

- Use **StructType** in production — clearer, and supports complex nested schemas.
- Use **DDL strings** for quick prototyping.
- Avoid `inferSchema=True` on large datasets — it's a real performance hit.

## 🔗 Related Notes
- [[Pyspark Read & Write Operations|Pyspark Read & Write Operations]]
- [[Handling Missing Values|Handling Missing Values]]
- [[Functions in Pyspark|Functions in Pyspark]]

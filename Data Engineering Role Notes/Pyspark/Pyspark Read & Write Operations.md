# Reading and Writing Data in PySpark

Reading and writing data is fundamental to any pipeline — this covers the practical surface of PySpark's I/O API.

---

### 1. Core Reading Syntax and Formats

**Concept:** PySpark offers a unified API for reading many sources and formats.

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("IOGuide").getOrCreate()

# Method 1: Format-specific shortcuts (most common)
df_csv = spark.read.csv("path/to/data.csv", header=True, inferSchema=True)
df_parquet = spark.read.parquet("path/to/data.parquet")
df_json = spark.read.json("path/to/data.json")
df_orc = spark.read.orc("path/to/data.orc")

# Method 2: Generic format method (more flexible)
df = spark.read.format("csv") \
              .option("header", "true") \
              .option("inferSchema", "true") \
              .load("path/to/data.csv")

# Method 3: Multiple files (wildcards and directories)
df_multiple = spark.read.csv("path/to/folder/*.csv", header=True)
df_all_files = spark.read.csv("path/to/folder/", header=True)  # All files in the directory
```

---

### 2. Common File Formats and Their Options

#### CSV
```python
df_csv = spark.read.format("csv") \
    .option("header", "true")           # First row as header
    .option("inferSchema", "true")      # Auto-detect data types
    .option("delimiter", ";")           # Custom delimiter
    .option("quote", "\"")              # Quote character
    .option("escape", "\\")             # Escape character
    .option("nullValue", "NA")          # Treat "NA" as null
    .option("dateFormat", "yyyy-MM-dd") # Date format
    .option("encoding", "UTF-8")        # File encoding
    .option("mode", "PERMISSIVE")       # Corrupt-record handling
    .load("path/to/data.csv")

# For multiline field values
df_multiline = spark.read.option("multiline", "true") \
                         .json("path/to/multiline.json")
```

#### Parquet (recommended for most cases)
```python
df_parquet = spark.read.parquet("path/to/data.parquet")

# Reading partitioned Parquet - directory structure like
# country=USA/state=NY/data.parquet is detected automatically
df_partitioned = spark.read.parquet("path/to/partitioned_data/")

# Merge schema across files with evolving schemas
df_merged = spark.read.option("mergeSchema", "true") \
                      .parquet("path/to/evolving_data/")
```

#### JSON
```python
df_json = spark.read.json("path/to/data.json")

# Complex nested JSON
df_json = spark.read.option("multiLine", "true") \
                    .option("mode", "PERMISSIVE") \
                    .json("path/to/complex.json")

# JSON Lines format (one JSON object per line)
df_jsonl = spark.read.json("path/to/data.jsonl")
```

---

### 3. Core Writing Syntax and Save Modes

**Concept:** PySpark offers different save modes for handling data that already exists at the destination.

```python
# Method 1: Format-specific shortcuts
df.write.csv("path/to/output.csv")
df.write.parquet("path/to/output.parquet")
df.write.json("path/to/output.json")

# Method 2: Generic format method
df.write.format("parquet").save("path/to/output.parquet")

# Method 3: With options
df.write.format("csv") \
       .option("header", "true") \
       .option("delimiter", "|") \
       .mode("overwrite") \
       .save("path/to/output.csv")
```

---

### 4. Save Modes

```python
# 1. ErrorIfExists (default) - throws if data already exists
df.write.mode("error").parquet("path/to/output")
# or
df.write.mode("errorifexists").parquet("path/to/output")

# 2. Overwrite - completely replaces existing data
df.write.mode("overwrite").parquet("path/to/output")

# 3. Append - adds to existing data
df.write.mode("append").parquet("path/to/output")

# 4. Ignore - silently does nothing if data already exists
df.write.mode("ignore").parquet("path/to/output")
```

**Practical examples:**
```python
# Daily ETL pipeline - append new data
daily_data.write.mode("append").parquet("path/to/daily_data/")

# Full refresh - overwrite the entire dataset
full_refresh_data.write.mode("overwrite").parquet("path/to/full_dataset/")

# Safe write - error if the output already exists (prevents accidental overwrite)
processed_data.write.mode("error").parquet("path/to/processed_data/")
```

---

### 5. Advanced Writing Options

#### Partitioning on Write
```python
# Extremely important for read performance later (partition pruning)
df.write.partitionBy("country", "year", "month") \
       .mode("overwrite") \
       .parquet("path/to/partitioned_data/")

# Creates: country=USA/year=2024/month=01/data.parquet

# Control the number of partitions before partitioning on write
df.repartition(10).write.partitionBy("country") \
                      .parquet("path/to/data/")
```

#### Compression
```python
df.write.option("compression", "snappy").parquet("path/to/data/")  # Default for Parquet
df.write.option("compression", "gzip").parquet("path/to/data/")    # Better ratio, slower
df.write.option("compression", "none").parquet("path/to/data/")    # No compression

# For CSV/JSON
df.write.option("compression", "gzip").csv("path/to/data.csv.gz")
```

#### File Size Control
```python
df.coalesce(1).write.parquet("path/to/single_file/")      # Single file (careful with large data)
df.repartition(4).write.parquet("path/to/four_files/")    # Exactly 4 files

# Control file size indirectly
df.write.option("maxRecordsPerFile", 100000).parquet("path/to/data/")
```

---

### 6. Working with Databases

#### JDBC
```python
jdbc_url = "jdbc:postgresql://localhost:5432/mydatabase"
connection_properties = {
    "user": "username",
    "password": "password",
    "driver": "org.postgresql.Driver"
}

# Read from a table
df_db = spark.read.jdbc(url=jdbc_url, table="employees", properties=connection_properties)

# Read with a query
df_query = spark.read.jdbc(url=jdbc_url, 
                          table="(SELECT * FROM employees WHERE salary > 50000) AS tmp",
                          properties=connection_properties)

# Write to a table
df.write.jdbc(url=jdbc_url, table="results", mode="overwrite", properties=connection_properties)
```

#### Database-Specific Options
```python
# Batch size for writes
df.write.option("batchsize", 10000) \
       .jdbc(url=jdbc_url, table="large_table", mode="append")

# Fetch size for reads
df.read.option("fetchsize", 1000) \
      .jdbc(url=jdbc_url, table="large_table")
```

---

### 7. Practical Patterns

#### Daily Data Pipeline
```python
daily_data = spark.read.parquet("path/to/daily_source/")
processed_data = daily_data.filter(F.col("quality") == "good")

from datetime import datetime
current_date = datetime.now().strftime("%Y-%m-%d")

processed_data.write \
    .partitionBy("category") \
    .mode("append") \
    .parquet(f"path/to/processed_data/date={current_date}/")
```

#### Validation Before Write
```python
def safe_write(df, path, expected_count=None):
    """Write with a lightweight row-count sanity check."""
    if expected_count and df.count() != expected_count:
        raise ValueError(f"Expected {expected_count} rows, got {df.count()}")
    
    df.write.mode("overwrite").parquet(path)
    print(f"Successfully wrote {df.count()} rows to {path}")

safe_write(processed_data, "path/to/output/", expected_count=100000)
```

#### Handling Schema Evolution
```python
df.write \
  .option("mergeSchema", "true") \
  .mode("append") \
  .parquet("path/to/evolving_data/")
```

---

### 8. Performance Optimization for I/O

- **Choose the right format** — Parquet for analytics (columnar); ORC is similar, good for Hive integration; CSV is good for interoperability but slow to read/write; JSON is good for nested data but similarly slow.
- **Partition wisely**: `df.write.partitionBy("date", "region").parquet("path/to/data/")`.
- **Aim for 100–200MB output files**: `df.repartition(200).write.parquet("path/to/data/")`.
- **Use compression appropriately**: snappy for speed, gzip for a better ratio at some CPU cost.
- **Coalesce small outputs**: `small_df.coalesce(1).write.csv("path/to/small_output.csv")`.

---

### 9. Error Handling and Data Quality

```python
# PERMISSIVE mode (default) - route corrupt records to a dedicated column
df = spark.read.option("mode", "PERMISSIVE") \
              .option("columnNameOfCorruptRecord", "_corrupt_record") \
              .json("path/to/potentially_bad_data.json")

# Drop the corrupt records once you've inspected them
clean_df = df.filter(F.col("_corrupt_record").isNull()).drop("_corrupt_record")

# Or use DROPMALFORMED to discard them automatically
df = spark.read.option("mode", "DROPMALFORMED").json("path/to/data.json")

# Or FAILFAST to stop immediately on any corrupt record
try:
    df = spark.read.option("mode", "FAILFAST").json("path/to/data.json")
except Exception as e:
    print(f"Failed to read due to malformed records: {e}")
```

See [[Pyspark Reading Modes|Pyspark Reading Modes]] for the full breakdown of these modes.

---

### 10. Cloud Storage Integration

```python
# AWS S3
df = spark.read.parquet("s3a://my-bucket/path/to/data/")
df.write.parquet("s3a://my-bucket/output/data/")
spark.conf.set("spark.hadoop.fs.s3a.access.key", "your-access-key")
spark.conf.set("spark.hadoop.fs.s3a.secret.key", "your-secret-key")

# Azure Blob Storage
df = spark.read.parquet("wasbs://container@account.blob.core.windows.net/path/")

# Google Cloud Storage
df = spark.read.parquet("gs://my-bucket/path/to/data/")
```

### Key Takeaways

1.  **Choose the right format**: Parquet for analytics, CSV for interoperability.
2.  **Understand save modes**: `overwrite`, `append`, `error`, `ignore`.
3.  **Partition on write**: critical for downstream query performance.
4.  **Balance file size**: not too many small files, not too few huge ones.
5.  **Handle errors gracefully**: pick the read mode that matches your data-quality tolerance.
6.  **Consider compression**: trade size against CPU.
7.  **Validate before writing**: catch data-quality problems before they hit production.

## 🔗 Related Notes
- [[Pyspark Reading Modes|Pyspark Reading Modes]]
- [[Schema Operation in Pyspark|📘 Schema Operations in PySpark]]
- [[Performance & Optimisation in Pyspark|Performance & Optimisation in Pyspark]]

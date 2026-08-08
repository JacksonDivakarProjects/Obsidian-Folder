# Comprehensive Guide to Delta Lake Commands in Python API with Spark

This guide covers all major Delta Lake operations using PySpark, from basic table operations to advanced features.

## Table of Contents
1. [Setup and Initialization](#setup)
2. [Basic Table Operations](#basic-ops)
3. [Read Operations](#read-ops)
4. [Write Operations](#write-ops)
5. [Table Management](#table-management)
6. [Time Travel](#time-travel)
7. [Optimization](#optimization)
8. [Schema Evolution](#schema-evolution)
9. [Change Data Feed](#change-data-feed)
10. [Utility Operations](#utility-ops)

## Setup and Initialization {#setup}

### 1. Installing Dependencies

```python
# Install required packages
# pip install pyspark delta-spark
```

### 2. Spark Session Configuration

```python
from pyspark.sql import SparkSession
from delta import *

# Configure Spark with Delta Lake
builder = SparkSession.builder \
    .appName("DeltaLakeGuide") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

spark = configure_spark_with_delta_pip(builder).getOrCreate()

# Alternative manual configuration
spark = SparkSession.builder \
    .appName("DeltaLakeGuide") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.jars.packages", "io.delta:delta-core_2.12:2.4.0") \
    .getOrCreate()
```

## Basic Table Operations {#basic-ops}

### 3. Creating Delta Tables

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from pyspark.sql.functions import current_timestamp

# Method 1: Create from DataFrame
data = [
    (1, "Alice", 25, 50000.0),
    (2, "Bob", 30, 60000.0),
    (3, "Charlie", 35, 70000.0)
]
columns = ["id", "name", "age", "salary"]

df = spark.createDataFrame(data, columns)
df.write.format("delta").save("/path/to/delta/table")

# Method 2: Create with options
df.write.format("delta") \
    .option("delta.autoOptimize.optimizeWrite", "true") \
    .mode("overwrite") \
    .save("/path/to/delta/table")

# Method 3: Create partitioned table
df.write.format("delta") \
    .partitionBy("age") \
    .mode("overwrite") \
    .save("/path/to/partitioned/delta/table")

# Method 4: Using SQL
df.createOrReplaceTempView("temp_table")
spark.sql("""
    CREATE TABLE employees 
    USING DELTA 
    LOCATION '/path/to/delta/table'
    AS SELECT * FROM temp_table
""")
```

### 4. Reading Delta Tables

```python
# Read from path
delta_df = spark.read.format("delta").load("/path/to/delta/table")

# Read with options
delta_df = spark.read.format("delta") \
    .option("versionAsOf", 0) \
    .load("/path/to/delta/table")

# Read using SQL
spark.sql("SELECT * FROM delta.`/path/to/delta/table`").show()

# Read from catalog table
spark.sql("SELECT * FROM employees").show()
```

## Read Operations {#read-ops}

### 5. Advanced Reading Options

```python
from delta.tables import DeltaTable

# Create DeltaTable instance
delta_table = DeltaTable.forPath(spark, "/path/to/delta/table")

# Read with schema enforcement
df = spark.read.format("delta") \
    .schema("id INT, name STRING, age INT, salary DOUBLE") \
    .load("/path/to/delta/table")

# Read specific columns
df = spark.read.format("delta") \
    .load("/path/to/delta/table") \
    .select("id", "name", "salary")

# Read with predicates (partition pruning)
df = spark.read.format("delta") \
    .load("/path/to/partitioned/delta/table") \
    .filter("age >= 30")

# Read with time travel
df_version = spark.read.format("delta") \
    .option("versionAsOf", 2) \
    .load("/path/to/delta/table")

df_timestamp = spark.read.format("delta") \
    .option("timestampAsOf", "2024-01-01") \
    .load("/path/to/delta/table")
```

## Write Operations {#write-ops}

### 6. Writing to Delta Tables

```python
# Append data
new_data = [
    (4, "Diana", 28, 55000.0),
    (5, "Eve", 32, 65000.0)
]
new_df = spark.createDataFrame(new_data, columns)

new_df.write.format("delta") \
    .mode("append") \
    .save("/path/to/delta/table")

# Overwrite data
overwrite_data = [
    (1, "Alice Updated", 26, 52000.0),
    (6, "Frank", 40, 80000.0)
]
overwrite_df = spark.createDataFrame(overwrite_data, columns)

overwrite_df.write.format("delta") \
    .mode("overwrite") \
    .option("replaceWhere", "id IN (1, 6)") \
    .save("/path/to/delta/table")

# Conditional overwrite
overwrite_df.write.format("delta") \
    .mode("overwrite") \
    .option("replaceWhere", "age >= 30") \
    .save("/path/to/partitioned/delta/table")
```

### 7. Upsert Operations (Merge)

```python
from delta.tables import DeltaTable
from pyspark.sql.functions import *

# Initialize DeltaTable
delta_table = DeltaTable.forPath(spark, "/path/to/delta/table")

# Data to upsert
updates_df = spark.createDataFrame([
    (1, "Alice Smith", 26, 52000.0),  # Update existing
    (7, "Grace", 29, 58000.0)         # Insert new
], columns)

# Merge operation
delta_table.alias("target") \
    .merge(updates_df.alias("source"), "target.id = source.id") \
    .whenMatchedUpdateAll() \
    .whenNotMatchedInsertAll() \
    .execute()

# Conditional merge with specific conditions
delta_table.alias("target") \
    .merge(updates_df.alias("source"), "target.id = source.id") \
    .whenMatchedUpdate(
        condition="source.salary > target.salary",
        set={
            "name": "source.name",
            "age": "source.age", 
            "salary": "source.salary"
        }
    ) \
    .whenNotMatchedInsertAll() \
    .execute()

# Complex merge with delete condition
delta_table.alias("target") \
    .merge(updates_df.alias("source"), "target.id = source.id") \
    .whenMatchedDelete(condition="source.age IS NULL") \
    .whenMatchedUpdateAll() \
    .whenNotMatchedInsertAll() \
    .execute()
```

## Table Management {#table-management}

### 8. Table Properties and Configuration

```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, "/path/to/delta/table")

# Get table details
print("Table Location:", delta_table.detail().select("location").first()[0])
print("Table Format:", delta_table.detail().select("format").first()[0])

# Set table properties
delta_table = DeltaTable.forPath(spark, "/path/to/delta/table")

# Using ALTER TABLE
spark.sql("""
    ALTER TABLE delta.`/path/to/delta/table` 
    SET TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact' = 'true',
        'comment' = 'Employee data table'
    )
""")

# Get table properties
properties = spark.sql("SHOW TBLPROPERTIES delta.`/path/to/delta/table`")
properties.show()
```

### 9. Schema Operations

```python
# Show schema
delta_table = DeltaTable.forPath(spark, "/path/to/delta/table")
delta_table.toDF().printSchema()

# Using SQL
spark.sql("DESCRIBE DETAIL delta.`/path/to/delta/table`").show()

# Add column
spark.sql("""
    ALTER TABLE delta.`/path/to/delta/table` 
    ADD COLUMN department STRING AFTER salary
""")

# Change column type (requires special handling)
spark.sql("""
    ALTER TABLE delta.`/path/to/delta/table` 
    CHANGE COLUMN age age BIGINT
""")

# Rename column
spark.sql("""
    ALTER TABLE delta.`/path/to/delta/table` 
    RENAME COLUMN salary TO annual_salary
""")
```

## Time Travel {#time-travel}

### 10. Version History and Time Travel

```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, "/path/to/delta/table")

# Get history
history = delta_table.history()
history.show()

# Detailed history with operations
history.select("version", "timestamp", "operation", "operationParameters").show()

# Time travel by version
df_v0 = spark.read.format("delta") \
    .option("versionAsOf", 0) \
    .load("/path/to/delta/table")

df_v1 = delta_table.history(1)

# Time travel by timestamp
df_timestamp = spark.read.format("delta") \
    .option("timestampAsOf", "2024-01-15 10:30:00") \
    .load("/path/to/delta/table")

# Using SQL for time travel
spark.sql("SELECT * FROM delta.`/path/to/delta/table@v0`").show()
spark.sql("SELECT * FROM delta.`/path/to/delta/table@timestamp='2024-01-15'`").show()

# Restore to previous version
spark.sql("""
    RESTORE TABLE delta.`/path/to/delta/table` 
    TO VERSION AS OF 0
""")

# Or using DataFrame API
delta_table.restoreToVersion(0)
```

## Optimization {#optimization}

### 11. Table Maintenance Operations

```python
from delta.tables import DeltaTable
from pyspark.sql.functions import *

delta_table = DeltaTable.forPath(spark, "/path/to/delta/table")

# Optimize (bin-packing)
spark.sql("""
    OPTIMIZE delta.`/path/to/delta/table`
    WHERE age >= 30
""")

# Or using Python API
delta_table.optimize().where("age >= 30").executeCompaction()

# Z-Ordering for better performance
spark.sql("""
    OPTIMIZE delta.`/path/to/delta/table`
    ZORDER BY (id, age)
""")

# Vacuum (remove old files)
# Remove files older than 7 days (default is 7 days)
spark.sql("""
    VACUUM delta.`/path/to/delta/table`
    RETAIN 168 HOURS  -- 7 days
""")

# Or using Python API
delta_table.vacuum(168)  # 168 hours = 7 days

# Force vacuum (without retention check)
delta_table.vacuum(0)

# Show vacuum status
spark.sql("VACUUM delta.`/path/to/delta/table` DRY RUN").show()
```

### 12. Auto Optimize Settings

```python
# Enable auto optimize during write
df.write.format("delta") \
    .option("delta.autoOptimize.optimizeWrite", "true") \
    .option("delta.autoOptimize.autoCompact", "true") \
    .mode("append") \
    .save("/path/to/delta/table")

# Set table properties for auto optimization
spark.sql("""
    ALTER TABLE delta.`/path/to/delta/table` 
    SET TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact' = 'true'
    )
""")
```

## Schema Evolution {#schema-evolution}

### 13. Handling Schema Changes

```python
# Automatic schema evolution during append
new_columns_data = [
    (8, "Henry", 45, 90000.0, "Engineering"),
    (9, "Ivy", 33, 75000.0, "Marketing")
]
new_columns_df = spark.createDataFrame(new_columns_data, ["id", "name", "age", "salary", "department"])

# This will automatically evolve the schema
new_columns_df.write.format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .save("/path/to/delta/table")

# Overwrite with schema evolution
overwrite_new_schema_df = spark.createDataFrame([
    (1, "Alice", 26, 52000.0, "HR", "alice@company.com")
], ["id", "name", "age", "salary", "department", "email"])

overwrite_new_schema_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .save("/path/to/delta/table")

# Check schema evolution history
delta_table.history() \
    .select("version", "timestamp", "operation", "operationParameters") \
    .where("operation = 'WRITE'") \
    .show(truncate=False)
```

## Change Data Feed {#change-data-feed}

### 14. Using Change Data Feed (CDF)

```python
# Enable Change Data Feed
spark.sql("""
    ALTER TABLE delta.`/path/to/delta/table` 
    SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

# Read change data between versions
cdf_df = spark.read.format("delta") \
    .option("readChangeFeed", "true") \
    .option("startingVersion", 0) \
    .option("endingVersion", 5) \
    .load("/path/to/delta/table")

cdf_df.show()

# Read change data between timestamps
cdf_time_df = spark.read.format("delta") \
    .option("readChangeFeed", "true") \
    .option("startingTimestamp", "2024-01-01 00:00:00") \
    .option("endingTimestamp", "2024-01-15 23:59:59") \
    .load("/path/to/delta/table")

# Process different change types
cdf_df.filter("_change_type = 'update_preimage'").show()  # Old values
cdf_df.filter("_change_type = 'update_postimage'").show() # New values
cdf_df.filter("_change_type = 'insert'").show()           # Inserted records
cdf_df.filter("_change_type = 'delete'").show()           # Deleted records
```

## Utility Operations {#utility-ops}

### 15. Table Information and Maintenance

```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, "/path/to/delta/table")

# Get table details
detail_df = delta_table.detail()
detail_df.show(truncate=False)

# Show all files in the table
files_df = delta_table.files()
files_df.show(truncate=False)

# Show files for specific partitions
delta_table.files().where("age = 30").show()

# Generate manifest for external tools
delta_table.generate("symlink_format_manifest")

# Convert Parquet to Delta
spark.sql("""
    CONVERT TO DELTA parquet.`/path/to/parquet/table`
    (id INT, name STRING, age INT, salary DOUBLE)
""")

# Clone tables
# Shallow clone (metadata only)
spark.sql("""
    CREATE TABLE employees_clone
    SHALLOW CLONE delta.`/path/to/delta/table`
    LOCATION '/path/to/clone/table'
""")

# Deep clone (data + metadata)
spark.sql("""
    CREATE TABLE employees_deep_clone
    DEEP CLONE delta.`/path/to/delta/table`
    LOCATION '/path/to/deep-clone/table'
""")
```

### 16. Data Quality and Constraints

```python
# Add constraints
spark.sql("""
    ALTER TABLE delta.`/path/to/delta/table` 
    ADD CONSTRAINT valid_age CHECK (age > 0 AND age < 150)
""")

spark.sql("""
    ALTER TABLE delta.`/path/to/delta/table` 
    ADD CONSTRAINT valid_salary CHECK (salary > 0)
""")

# Show constraints
spark.sql("SHOW TBLPROPERTIES delta.`/path/to/delta/table`") \
    .filter("key LIKE 'delta.constraints%'") \
    .show()

# Remove constraints
spark.sql("""
    ALTER TABLE delta.`/path/to/delta/table` 
    DROP CONSTRAINT valid_age
""")
```

### 17. Cleanup and Best Practices

```python
# Check table size and file statistics
spark.sql("""
    SELECT * FROM delta.`/path/to/delta/table`
    WHERE age > 30
""").explain()

# Get table statistics
spark.sql("DESCRIBE DETAIL delta.`/path/to/delta/table`").show(truncate=False)

# Proper shutdown
spark.stop()

# Graceful error handling
try:
    delta_table.optimize().executeCompaction()
except Exception as e:
    print(f"Optimization failed: {e}")
    # Handle retry or alternative logic
```

## Best Practices Summary

1. **Always use schema enforcement** for data quality.
2. **Enable Change Data Feed** for auditing and replication.
3. **Use Z-Ordering** for frequently filtered columns.
4. **Regularly run `OPTIMIZE`** for better read performance.
5. **Set appropriate `VACUUM` retention** based on compliance and time-travel needs.
6. **Use time travel** for debugging and recovery.
7. **Monitor table history** for operational insights.
8. **Use constraints** for data validation.
9. **Enable auto-optimize** for frequently written tables.
10. **Use partitioning** for large tables with predictable filter columns.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Delta Lake Commands in Different APIs/Delta Lake Commands in SQL API|Delta Lake Object Commands (SQL API)]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Upsert In DeltaLake|DeltaTable Upsert in PySpark]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Important TBLProperties/Table Utility Commands|Delta Lake Table Utility Commands]]

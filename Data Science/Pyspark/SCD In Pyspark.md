### **Comprehensive Guide to Slowly Changing Dimensions (SCDs) - PySpark (No Delta Lake)**

This guide covers SCD types 1, 2, and 3 using standard PySpark syntax, perfect for beginners.

---

## **1. Type 1 SCD (Overwrite)**
**Concept:** Simply overwrite old values with new values. No history is kept.
**Use Case:** Correcting errors, updating unimportant attributes.

```python
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Sample Data - Existing Dimension
existing_data = [
    (1, "C101", "Alice", "Seattle"), 
    (2, "C102", "Bob", "New York")
]
existing_cols = ["surrogate_key", "customer_id", "name", "city"]
existing_df = spark.createDataFrame(existing_data, existing_cols)

# New Updates - Bob moved to Boston, new customer Charlie
new_data = [
    ("C102", "Bob", "Boston"),      # Update
    ("C103", "Charlie", "Chicago")  # New customer
]
new_cols = ["customer_id", "name", "city"]
updates_df = spark.createDataFrame(new_data, new_cols)

# TYPE 1 IMPLEMENTATION: Overwrite
def scd_type_1(existing_df, updates_df, key_column="customer_id"):
    # Remove existing records that will be updated
    existing_ids = updates_df.select(key_column).distinct()
    existing_keep_df = existing_df.join(existing_ids, on=key_column, how="left_anti")
    
    # Add surrogate key to updates (simple approach)
    max_key = existing_df.agg(F.max("surrogate_key")).first()[0]
    updates_with_key = updates_df.withColumn(
        "surrogate_key", 
        F.monotonically_increasing_id() + max_key + 1
    )
    
    # Combine kept records with updates
    result_df = existing_keep_df.unionByName(updates_with_key)
    return result_df

# Execute
result_df = scd_type_1(existing_df, updates_df)
result_df.show()
```

**Output:**
```
+-------------+-----------+-------+--------+
|surrogate_key|customer_id|   name|    city|
+-------------+-----------+-------+--------+
|            1|       C101|  Alice| Seattle|
|   8589934594|       C102|    Bob|  Boston|  # Updated
|   8589934595|       C103|Charlie| Chicago|  # New
+-------------+-----------+-------+--------+
```

---

## **2. Type 2 SCD (Full History)**
**Concept:** Preserve complete history by adding new records for changes.
**Use Case:** Tracking address changes, price history, audit requirements.

```python
# Existing Dimension with SCD2 columns
existing_data = [
    (1, "C101", "Alice", "Seattle", "2023-01-01", None, 1),
    (2, "C102", "Bob", "New York", "2023-01-01", None, 1)
]
existing_cols = ["surrogate_key", "customer_id", "name", "city", "start_date", "end_date", "is_current"]
existing_df = spark.createDataFrame(existing_data, existing_cols)

# New Updates - Alice moved to Austin
new_data = [("C101", "Alice", "Austin")]
updates_df = spark.createDataFrame(new_data, ["customer_id", "name", "city"])

# TYPE 2 IMPLEMENTATION: Full History
def scd_type_2(existing_df, updates_df, natural_key="customer_id"):
    effective_date = "2024-01-15"  # Usually current date
    
    # Identify records that need to be expired
    changed_records = (
        existing_df.alias("old")
        .join(updates_df.alias("new"), natural_key)
        .filter(
            (F.col("old.is_current") == 1) & 
            (
                (F.col("old.city") != F.col("new.city")) |
                (F.col("old.name") != F.col("new.name"))
            )
        )
        .select("old.*")
    )
    
    # Expire the old records
    expired_records = changed_records.withColumn("end_date", F.lit(effective_date)) \
                                    .withColumn("is_current", F.lit(0))
    
    # Create new records for changes
    max_key = existing_df.agg(F.max("surrogate_key")).first()[0]
    new_version_records = (
        updates_df
        .withColumn("surrogate_key", F.monotonically_increasing_id() + max_key + 1)
        .withColumn("start_date", F.lit(effective_date))
        .withColumn("end_date", F.lit(None).cast("string"))
        .withColumn("is_current", F.lit(1))
    )
    
    # Get unchanged records
    unchanged_records = existing_df.join(
        changed_records.select("surrogate_key"), 
        on="surrogate_key", 
        how="left_anti"
    )
    
    # Combine all parts
    final_df = unchanged_records.unionByName(expired_records).unionByName(new_version_records)
    return final_df

# Execute
result_df = scd_type_2(existing_df, updates_df)
result_df.orderBy("customer_id", "start_date").show()
```

**Output:**
```
+-------------+-----------+-----+-------+----------+----------+----------+
|surrogate_key|customer_id| name|   city| start_date|   end_date|is_current|
+-------------+-----------+-----+-------+----------+----------+----------+
|            1|       C101|Alice|Seattle| 2023-01-01|2024-01-15|         0| # Expired
|   8589934593|       C101|Alice| Austin| 2024-01-15|      null|         1| # New version
|            2|       C102|  Bob|New York| 2023-01-01|      null|         1| # Unchanged
+-------------+-----------+-----+-------+----------+----------+----------+
```

---

## **3. Type 3 SCD (Limited History)**
**Concept:** Keep only current and previous value in separate columns.
**Use Case:** Tracking only the most recent change.

```python
# Existing Dimension with Type 3 columns
existing_data = [
    (1, "C101", "Alice", "Seattle", None),
    (2, "C102", "Bob", "New York", None)
]
existing_cols = ["surrogate_key", "customer_id", "name", "current_city", "previous_city"]
existing_df = spark.createDataFrame(existing_data, existing_cols)

# New Updates - Alice moved to Austin, Bob moved to Boston
new_data = [
    ("C101", "Alice", "Austin"),
    ("C102", "Bob", "Boston")
]
updates_df = spark.createDataFrame(new_data, ["customer_id", "name", "new_city"])

# TYPE 3 IMPLEMENTATION: Limited History
def scd_type_3(existing_df, updates_df, natural_key="customer_id", tracked_column="city"):
    current_col = f"current_{tracked_column}"
    previous_col = f"previous_{tracked_column}"
    
    # Join to find changes
    joined_df = existing_df.join(updates_df, natural_key)
    
    # Update logic
    result_df = joined_df.withColumn(
        previous_col,
        F.when(F.col(current_col) != F.col(f"new_{tracked_column}"), 
               F.col(current_col))
        .otherwise(F.col(previous_col))
    ).withColumn(
        current_col,
        F.coalesce(F.col(f"new_{tracked_column}"), F.col(current_col))
    ).drop(f"new_{tracked_column}")
    
    return result_df

# Execute
result_df = scd_type_3(existing_df, updates_df)
result_df.show()
```

**Output:**
```
+-------------+-----------+-----+------------+--------------+
|surrogate_key|customer_id| name|current_city| previous_city|
+-------------+-----------+-----+------------+--------------+
|            1|       C101|Alice|      Austin|       Seattle| # Both values kept
|            2|       C102|  Bob|      Boston|      New York| # Both values kept
+-------------+-----------+-----+------------+--------------+
```

---

## **4. Practical Industry Considerations**

### **Performance Optimization**
```python
# Use broadcasting for small dimension tables
from pyspark.sql.functions import broadcast

def optimized_scd_join(large_fact_df, small_dim_df):
    return large_fact_df.join(broadcast(small_dim_df), "customer_id")

# Use partitioning for large dimensions
def write_partitioned_dimension(df):
    (df.write
     .partitionBy("is_current")  # Partition by current flag
     .mode("overwrite")
     .parquet("dimensions/customer/"))
```

### **Data Quality Checks**
```python
def validate_scd2_integrity(df):
    """Validate SCD2 rules are maintained"""
    # Check for multiple current records per natural key
    current_records = df.filter(F.col("is_current") == 1)
    violation = (current_records.groupBy("customer_id")
                 .count()
                 .filter(F.col("count") > 1))
    
    if violation.count() > 0:
        print("ERROR: Multiple current records found!")
        violation.show()
    
    # Check for null end_dates on non-current records
    null_end_date = df.filter((F.col("is_current") == 0) & F.col("end_date").isNull())
    if null_end_date.count() > 0:
        print("ERROR: Expired records with null end_date!")
        null_end_date.show()
```

### **Incremental Processing Pattern**
```python
def incremental_scd_processing(existing_path, updates_path, scd_type=2):
    """Process updates incrementally"""
    # Read existing data
    existing_df = spark.read.parquet(existing_path)
    
    # Read only new updates
    updates_df = spark.read.parquet(updates_path).filter(F.col("batch_date") == F.current_date())
    
    # Apply SCD logic
    if scd_type == 1:
        result_df = scd_type_1(existing_df, updates_df)
    elif scd_type == 2:
        result_df = scd_type_2(existing_df, updates_df)
    elif scd_type == 3:
        result_df = scd_type_3(existing_df, updates_df)
    
    # Write result
    result_df.write.mode("overwrite").parquet(existing_path)
```

This guide provides practical, runnable PySpark code for all three SCD types without requiring advanced concepts like Delta Lake. You can use these patterns as building blocks for your data pipelines!
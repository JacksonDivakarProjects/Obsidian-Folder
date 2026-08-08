# Essential PySpark Programs and Patterns

The practical, real-world patterns every data engineer should have on hand — built on top of all the fundamentals covered elsewhere in this folder.

### 1. The Complete ETL Pipeline Pattern

The most important pattern: read, transform, write.

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.appName("CompleteETL").getOrCreate()

# EXTRACT: Read from multiple sources
df_csv = spark.read.option("header", True).option("inferSchema", True).csv("sales_data/*.csv")
df_json = spark.read.json("customer_data/*.json")

# TRANSFORM: Clean, join, and aggregate
cleaned_df = df_csv.filter(F.col("amount").isNotNull() & (F.col("amount") > 0))

joined_df = cleaned_df.join(df_json, on="customer_id", how="inner")

aggregated_df = (joined_df.groupBy("customer_id", "region")
                 .agg(F.sum("amount").alias("total_spent"),
                      F.count("transaction_id").alias("transaction_count"),
                      F.avg("amount").alias("avg_transaction")))

final_df = aggregated_df.withColumn("customer_tier", 
                                   F.when(F.col("total_spent") > 1000, "Premium")
                                    .when(F.col("total_spent") > 500, "Standard")
                                    .otherwise("Basic"))

# LOAD: Write to analytical storage
(final_df.write
 .format("parquet")
 .mode("overwrite")
 .partitionBy("region")
 .option("compression", "snappy")
 .save("output/customer_analytics/"))
```

### 2. Advanced Analytics with Window Functions

**Use case:** rank customers within their region by spending.

```python
from pyspark.sql.window import Window

window_spec = Window.partitionBy("region").orderBy(F.col("total_spent").desc())

ranked_df = (final_df
             .withColumn("regional_rank", F.rank().over(window_spec))
             .withColumn("regional_avg", F.avg("total_spent").over(Window.partitionBy("region")))
             .withColumn("spent_vs_avg", F.col("total_spent") - F.col("regional_avg")))

ranked_df.show()
```

### 3. Handling Nested JSON Data

**Use case:** extract data from complex, nested JSON structures.

```python
# Sample nested JSON: {"user": {"name": "Alice", "address": {"city": "NY", "zip": "10001"}}, "orders": [1, 2, 3]}
json_df = spark.read.option("multiLine", True).json("complex_data.json")

# Flatten the nested structure - dot notation for structs, explode() for arrays
flattened_df = (json_df
               .select(
                   F.col("user.name").alias("customer_name"),
                   F.col("user.address.city").alias("city"),
                   F.col("user.address.zip").alias("zip_code"),
                   F.explode("orders").alias("order_id")
                ))

flattened_df.show()
```

### 4. Data Quality Check Framework

**Use case:** validate data before writing to production.

```python
def run_data_quality_checks(df):
    """Run a series of data quality checks."""
    checks = {
        "total_rows": df.count(),
        "null_amounts": df.filter(F.col("amount").isNull()).count(),
        "negative_amounts": df.filter(F.col("amount") < 0).count(),
        "unique_customers": df.select("customer_id").distinct().count()
    }
    
    # Fail hard on checks that indicate broken upstream data
    if checks["null_amounts"] > 0:
        raise ValueError(f"Data quality check failed: Found {checks['null_amounts']} null amounts")
    
    if checks["negative_amounts"] > 0:
        print(f"Warning: Found {checks['negative_amounts']} negative amounts")
    
    return checks

quality_metrics = run_data_quality_checks(final_df)
print("Data Quality Metrics:", quality_metrics)
```

### 5. Incremental Load Pattern (Merge/Upsert)

**Use case:** update existing data with new records without reprocessing everything.

```python
existing_df = spark.read.parquet("output/customer_analytics/")
new_data_df = spark.read.parquet("new_customer_data/")

from pyspark.sql import DataFrame

def merge_incremental_data(existing_df: DataFrame, new_df: DataFrame, key_columns: list):
    # Identify genuinely new records (not already present by key)
    existing_keys = existing_df.select(key_columns).distinct()
    new_records = new_df.join(existing_keys, on=key_columns, how="left_anti")
    
    # Append new records to what's already there.
    # Note: this only appends - it does not update existing rows whose
    # non-key attributes changed. For true upserts, use Delta Lake's
    # MERGE INTO or the SCD patterns in [[SCD In Pyspark|SCD In Pyspark]].
    merged_df = existing_df.unionByName(new_records, allowMissingColumns=True)
    return merged_df

final_merged_df = merge_incremental_data(existing_df, new_data_df, ["customer_id"])
```

### 6. Machine Learning Feature Preparation

**Use case:** prepare data for ML models using PySpark MLlib.

```python
from pyspark.ml.feature import VectorAssembler, StringIndexer, OneHotEncoder
from pyspark.ml import Pipeline

indexer = StringIndexer(inputCol="customer_tier", outputCol="tier_index")
encoder = OneHotEncoder(inputCol="tier_index", outputCol="tier_encoded")
assembler = VectorAssembler(
    inputCols=["total_spent", "transaction_count", "tier_encoded"], 
    outputCol="features"
)

pipeline = Pipeline(stages=[indexer, encoder, assembler])
ml_ready_df = pipeline.fit(final_df).transform(final_df)

ml_ready_df.select("customer_id", "features").show(truncate=False)
```

### 7. Handling Bad Data and Error Recovery

**Use case:** process data with potential errors gracefully.

```python
df_with_errors = spark.read.option("mode", "PERMISSIVE") \
                          .option("columnNameOfCorruptRecord", "_corrupt_record") \
                          .csv("potentially_bad_data/*.csv")

# Separate good and bad records
good_data = df_with_errors.filter(F.col("_corrupt_record").isNull()).drop("_corrupt_record")
bad_data = df_with_errors.filter(F.col("_corrupt_record").isNotNull())

processed_good_data = good_data.withColumn("processing_date", F.current_date())

# Log bad records for later analysis instead of silently dropping them
bad_data_count = bad_data.count()
if bad_data_count > 0:
    print(f"Found {bad_data_count} corrupt records - saving for analysis")
    bad_data.write.mode("append").json("error_logs/bad_records/")
```

### 8. Performance-Optimized Aggregation

**Use case:** large-scale aggregation with sensible partitioning.

```python
optimized_agg = (df_csv.repartition(50, "region")  # Pre-partition by the group key
                 .groupBy("region", "product_category")
                 .agg(F.sum("amount").alias("total_sales"),
                      F.approx_count_distinct("customer_id").alias("approx_customers"))
                 .filter(F.col("total_sales") > 1000))

# Cache since it will be read by multiple downstream actions
optimized_agg.cache()
summary1 = optimized_agg.count()
summary2 = optimized_agg.filter(F.col("region") == "West").collect()

optimized_agg.unpersist()  # Release the cache when done
```

### 9. Daily Batch Processing Template

**Use case:** template for daily data processing jobs.

```python
from datetime import datetime, timedelta

def process_daily_data(process_date=None):
    """Process data for a specific date."""
    if process_date is None:
        process_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"Processing data for date: {process_date}")
    
    daily_data = spark.read.parquet(f"raw_data/date={process_date}/*")
    
    processed_data = (daily_data
                     .filter(F.col("is_valid") == True)
                     .groupBy("category")
                     .agg(F.sum("value").alias("daily_total")))
    
    (processed_data.write
     .mode("append")
     .partitionBy("category")
     .parquet(f"processed_data/"))
    
    return processed_data.count()

record_count = process_daily_data()
print(f"Processed {record_count} records")
```

### 10. Unit-Testable PySpark Function

**Use case:** write PySpark code that's easy to test in isolation.

```python
def calculate_customer_lifetime_value(df):
    """Calculate CLV. Pure function of a DataFrame - easy to unit test with fixture data."""
    clv_df = (df.groupBy("customer_id")
              .agg(F.sum("amount").alias("total_revenue"),
                   F.countDistinct("order_id").alias("order_count"),
                   F.datediff(F.current_date(), F.min("order_date")).alias("days_active")))
    
    clv_df = clv_df.withColumn("avg_order_value", F.col("total_revenue") / F.col("order_count"))
    clv_df = clv_df.withColumn("clv", F.col("avg_order_value") * F.col("order_count") * (365 / F.col("days_active")))
    
    return clv_df
```

These patterns cover the majority of day-to-day data engineering work with PySpark.

## 🔗 Related Notes
- [[Aggregation and Window Function|Aggregation and Window Function]]
- [[Pyspark Read & Write Operations|Pyspark Read & Write Operations]]
- [[Pyspark Reading Modes|Pyspark Reading Modes]]
- [[SCD In Pyspark|SCD In Pyspark]]

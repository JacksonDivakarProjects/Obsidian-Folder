# Basic DataFrame Operations

Mastering `select`, `filter`, `withColumn`, `withColumnRenamed`, `drop`, and `orderBy` is the foundation of everyday PySpark work. Each is demonstrated below against a sample `users` DataFrame.

```python
# Sample DataFrame Creation
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DateType

spark = SparkSession.builder.appName("PracticalGuide").getOrCreate()

data = [
    (1, "Alice", "Johnson", "NY", 85000, "1985-05-15"),
    (2, "Bob", "Smith", "CA", 74000, "1990-12-23"),
    (3, "Charlie", "Brown", "NY", 99000, "1982-03-08"),
    (4, "Diana", "Prince", "WA", 120000, "1978-07-01"),
    (5, "Elon", "Musk", "CA", None, "1971-06-28") # Note the null salary
]

schema = StructType([
    StructField("user_id", IntegerType(), True),
    StructField("first_name", StringType(), True),
    StructField("last_name", StringType(), True),
    StructField("state", StringType(), True),
    StructField("salary", IntegerType(), True),
    StructField("dob", StringType(), True)
])

df = spark.createDataFrame(data, schema)
# Fix the date string to a proper DateType
df = df.withColumn("dob", F.to_date(F.col("dob"), "yyyy-MM-dd"))
df.show()
```

**Output:**
```
+-------+----------+---------+-----+------+----------+
|user_id|first_name|last_name|state|salary|       dob|
+-------+----------+---------+-----+------+----------+
|      1|     Alice|  Johnson|   NY| 85000|1985-05-15|
|      2|       Bob|    Smith|   CA| 74000|1990-12-23|
|      3|   Charlie|    Brown|   NY| 99000|1982-03-08|
|      4|     Diana|   Prince|   WA|120000|1978-07-01|
|      5|      Elon|     Musk|   CA|  null|1971-06-28|
+-------+----------+---------+-----+------+----------+
```

---

### 1. `select()`: Projecting Columns
**Concept:** Choose which columns to keep in the result — the equivalent of SQL's `SELECT`.

**Practical uses:**
*   Send only the necessary columns downstream to an API or report.
*   Reorder columns for display.

```python
# Select specific columns
df.select("user_id", "first_name", "last_name").show()

# Select all columns except one (list comprehension)
all_columns = df.columns
df.select(*[col for col in all_columns if col != "salary"]).show()

# Use col() for complex expressions or to avoid ambiguity
df.select(F.col("first_name"), F.col("state")).show()

# Create new columns on-the-fly while selecting
df.select("first_name", (F.col("salary") * 0.10).alias("bonus")).show()
```

---

### 2. `filter()` / `where()`: Filtering Rows
**Concept:** `filter()` and `where()` are **identical** — the equivalent of SQL's `WHERE`.

**Practical uses:**
*   Data cleaning: drop invalid records (nulls, out-of-range values).
*   Segmenting data: analyze a subset (e.g., a specific state, high earners).

```python
# Filter users from New York (NY)
df.filter(F.col("state") == "NY").show()

# Multiple conditions: Users from CA with a salary greater than 80,000
df.filter( (F.col("state") == "CA") & (F.col("salary") > 80000) ).show()

# Filter using SQL-like syntax (note the quotes)
df.where("state = 'NY' AND salary > 80000").show()

# Filter for NULL values — must use isNull()/isNotNull()
df.filter(F.col("salary").isNull()).show() # Finds Elon Musk
df.filter("salary IS NULL").show() # SQL syntax also works
```

---

### 3. `withColumn()`: Adding/Transforming Columns
**Concept:** Adds a new column, or replaces an existing one with transformed data — one of the most frequently used operations.

**Practical uses:**
*   Feature engineering (`full_name = first_name + last_name`).
*   Standardizing formats, converting units, bucketing continuous data.
*   Deriving new fields (age from date of birth, bonus from salary).

```python
# Create a new column 'full_name'
df_with_fullname = df.withColumn("full_name", F.concat(F.col("first_name"), F.lit(" "), F.col("last_name")))
df_with_fullname.show()

# Replace the existing 'salary' column with a raised salary (10% raise)
# Reusing the column name overwrites it.
df_with_raise = df.withColumn("salary", F.col("salary") * 1.10)
df_with_raise.show()

# Create a boolean column for high earners
df_with_flag = df.withColumn("is_high_earner", F.col("salary") > 90000)
df_with_flag.show()

# Handle nulls during transformation with coalesce
df_with_safe_calc = df.withColumn("safe_salary", F.coalesce(F.col("salary"), F.lit(0)))
df_with_safe_calc.show()
```

---

### 4. `withColumnRenamed()`: Renaming Columns
**Concept:** Renames a column — important for join compatibility and schema alignment.

**Practical uses:**
*   Avoid duplicate column names after a join by renaming one side first.
*   Turn technical column names into business-friendly ones for reporting.
*   Standardize column names across multiple data sources.

```python
# Rename a single column
df_renamed = df.withColumnRenamed("dob", "date_of_birth")
df_renamed.show()

# Rename multiple columns by chaining
df_renamed = df.withColumnRenamed("first_name", "fname").withColumnRenamed("last_name", "lname")
df_renamed.show()

# For bulk renaming patterns (e.g. converting all names to uppercase),
# a loop over df.columns is cleaner than chaining withColumnRenamed calls.
```

---

### 5. `drop()`: Dropping Columns
**Concept:** Removes one or more columns, reducing memory usage and downstream data transfer.

**Practical uses:**
*   Remove PII (e.g., `email`, `phone_number`) before analysis.
*   Clean up intermediate columns created during a transformation pipeline.
*   Removing unused data is the cheapest form of optimization.

```python
# Drop a single column
df_without_salary = df.drop("salary")
df_without_salary.show()

# Drop multiple columns at once
df_minimal = df.drop("salary", "dob", "state")
df_minimal.show()

# Drop a column only if it exists (safe practice)
columns_to_drop = ["salary", "non_existent_column"]
df_safe = df
for col in columns_to_drop:
    if col in df.columns:
        df_safe = df_safe.drop(col)
df_safe.show()
```

---

### 6. `orderBy()` / `sort()`: Sorting Data
**Concept:** `orderBy()` and `sort()` are **identical** — they sort the whole DataFrame by one or more columns. This can trigger a full shuffle and be expensive on large datasets.

**Practical uses:**
*   Top-N analysis (e.g., the 10 highest-paid employees).
*   Ordering records for a report or UI.
*   Spotting patterns or anomalies during debugging.

```python
# Sort by a single column (ascending is default)
df_sorted = df.orderBy("salary")
df_sorted.show()

# Sort in descending order
df_sorted_desc = df.orderBy(F.col("salary").desc())
df_sorted_desc.show()

# Sort by multiple columns: state ascending, then salary descending
df_multi_sorted = df.orderBy("state", F.col("salary").desc())
df_multi_sorted.show()

# Using the sort() alias
df.sort("dob").show() # Sorts oldest to newest (ascending dates)
```

**Key takeaway:** these operations chain naturally into transformation pipelines:
```python
final_df = (raw_df
            .select("id", "name", "date", "revenue")
            .filter(F.col("revenue") > 1000)
            .withColumn("formatted_date", F.date_format("date", "yyyyMMdd"))
            .withColumnRenamed("id", "user_id")
            .drop("date")
            .orderBy(F.col("revenue").desc())
           )
```

## 🔗 Related Notes
- [[Aggregation and Window Function|Aggregation and Window Function]]
- [[Handling Missing Values|Handling Missing Values]]
- [[Functions in Pyspark|Functions in Pyspark]]
- [[Joining DataFrames|Joining DataFrames]]

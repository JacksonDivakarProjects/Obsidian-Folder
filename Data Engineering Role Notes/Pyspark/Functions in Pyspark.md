# `pyspark.sql.functions` (the `F` Module)

Mastering `pyspark.sql.functions` is the key to efficient, expressive data transformations in PySpark.

### Setup

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F # The key import
from pyspark.sql.types import *

spark = SparkSession.builder.appName("FunctionsGuide").getOrCreate()

data = [
    (1, "Alice", "Johnson", "NY", 85000.555, "1985-05-15", "2020-01-15"),
    (2, "Bob", "Smith", "CA", 74000.0, "1990-12-23", "2021-03-10"),
    (3, "Charlie", "Brown", "NY", 99000.123, "1982-03-08", "2019-11-01"),
    (4, "Diana", "Prince-Themyscira", "WA", 120000.999, "1978-07-01", "2022-05-22"),
    (5, "Elon", "Musk", "CA", 150000.0, "1971-06-28", "2018-12-05")
]

schema = StructType([
    StructField("emp_id", IntegerType(), True),
    StructField("first_name", StringType(), True),
    StructField("last_name", StringType(), True),
    StructField("state", StringType(), True),
    StructField("salary", DoubleType(), True),
    StructField("dob", StringType(), True),
    StructField("hire_date", StringType(), True)
])

df = spark.createDataFrame(data, schema)

# Convert string dates to DateType - a common first step
df = df.withColumn("dob", F.to_date(F.col("dob"), "yyyy-MM-dd"))\
       .withColumn("hire_date", F.to_date(F.col("hire_date"), "yyyy-MM-dd"))

df.show()
```

---

### 1. String Functions

**Concept:** Manipulate and transform text data.

**Practical uses:** data cleaning, standardization, feature engineering, report formatting.

```python
# Standardize case for consistency (e.g., before a join or group)
df_str = df.withColumn("first_name_lower", F.lower(F.col("first_name")))
df_str = df_str.withColumn("state_upper", F.upper(F.col("state")))

# Extract parts of a string
df_str = df_str.withColumn("last_name_substr", F.substring(F.col("last_name"), 1, 5)) # First 5 chars
df_str = df_str.withColumn("name_initials", F.concat(F.substring("first_name", 1, 1), F.lit(". "), F.substring("last_name", 1, 1), F.lit(".")))

# Length of a string
df_str = df_str.withColumn("last_name_len", F.length(F.col("last_name")))

# Trim whitespace (invisible leading/trailing spaces are a common data issue)
df_dirty = df.withColumn("dirty_state", F.concat(F.col("state"), F.lit("   ")))
df_clean = df_dirty.withColumn("clean_state", F.trim(F.col("dirty_state")))

# Handle complex patterns with regexp_extract / regexp_replace
df_str = df_str.withColumn("hyphen_part", F.regexp_extract(F.col("last_name"), r".*-(.*)", 1))
df_str = df_str.withColumn("last_name_no_hyphen", F.regexp_replace(F.col("last_name"), "-", " "))

# Concatenate strings - concat_ws handles nulls better than concat
df_str = df_str.withColumn("full_name", F.concat_ws(" ", F.col("first_name"), F.col("last_name")))

df_str.select("first_name", "last_name", "first_name_lower", "state_upper", "last_name_substr", "name_initials", "last_name_len", "full_name", "hyphen_part").show(truncate=False)
```

---

### 2. Date/Time Functions

**Concept:** Calculations and extractions on date and time fields.

**Practical uses:** ages, tenures, date ranges, filtering by time period.

```python
# Current date (useful for calculating elapsed time)
df_date = df.withColumn("current_date", F.current_date())

# Age and tenure (days, approximate years)
df_date = df_date.withColumn("age_days", F.datediff(F.col("current_date"), F.col("dob")))
df_date = df_date.withColumn("age_years", F.floor(F.col("age_days") / 365.25)) # Rough estimate
df_date = df_date.withColumn("tenure_days", F.datediff(F.col("current_date"), F.col("hire_date")))

# Add/subtract time periods
df_date = df_date.withColumn("hire_date_plus_1year", F.date_add(F.col("hire_date"), 365))
df_date = df_date.withColumn("review_date", F.add_months(F.col("hire_date"), 6))

# Extract parts of a date (useful for grouping)
df_date = df_date.withColumn("birth_year", F.year(F.col("dob")))
df_date = df_date.withColumn("birth_month", F.month(F.col("dob")))
df_date = df_date.withColumn("hire_dayofweek", F.dayofweek(F.col("hire_date"))) # 1=Sunday, 2=Monday...
df_date = df_date.withColumn("hire_quarter", F.quarter(F.col("hire_date")))

df_date.select("dob", "hire_date", "current_date", "age_years", "tenure_days", "hire_date_plus_1year", "birth_year", "hire_quarter").show()
```

---

### 3. Math Functions

**Concept:** Mathematical operations on numeric columns.

**Practical uses:** financial calculations, scientific data processing, scaling/normalizing for ML.

```python
# Rounding for readability or business rules
df_math = df.withColumn("salary_rounded", F.round(F.col("salary"), 0)) # Round to 0 decimal places
df_math = df_math.withColumn("salary_rounded_1000", F.round(F.col("salary"), -3)) # Round to nearest 1000

# Basic arithmetic
df_math = df_math.withColumn("salary_after_raise", F.col("salary") * 1.10)
df_math = df_math.withColumn("tax_estimate", F.col("salary") * 0.25)

# More advanced functions
df_math = df_math.withColumn("salary_sqrt", F.sqrt(F.col("salary"))) # Square root
df_math = df_math.withColumn("log_salary", F.log(10.0, F.col("salary"))) # Logarithm base 10

# Absolute value (useful for differences)
df_math = df_math.withColumn("diff_from_100k", F.abs(F.col("salary") - 100000))

df_math.select("salary", "salary_rounded", "salary_rounded_1000", "salary_after_raise", "diff_from_100k").show()
```

---

### 4. Aggregation Functions

**Concept:** Compute a single result from a group of rows. These are used inside `.agg()`, typically after a `.groupBy()`.

**Practical uses:** report summaries, KPI calculation, ML feature engineering.

```python
# Simple aggregations on the entire DataFrame (no groupBy)
df.agg(F.max("salary").alias("max_sal"),
       F.min("salary").alias("min_sal"),
       F.avg("salary").alias("avg_sal"),
       F.sum("salary").alias("total_payroll")).show()

# Counts are very common
print(f"Total number of employees: {df.count()}") # Action: returns an integer
df.select(F.count("salary").alias("non_null_salary_count")).show() # Transformation: counts non-nulls in a column
df.select(F.countDistinct("state").alias("unique_states")).show() # Counts distinct values

# The most powerful use case: grouped aggregations
state_summary_df = df.groupBy("state")\
                    .agg(F.count("emp_id").alias("num_employees"),
                         F.avg("salary").alias("average_salary"),
                         F.sum("salary").alias("total_salary"),
                         F.countDistinct("emp_id").alias("distinct_emps") # Redundant here, but shows the syntax
                        )\
                    .orderBy(F.col("average_salary").desc())
state_summary_df.show()
```

---

### 5. UDFs (User Defined Functions)

**Concept:** Custom functions for when built-in Spark functions aren't enough.

**Practical uses:** complex business logic, leveraging Python libraries (`json`, `re`), string parsing too complex for `regexp_*`.

**Critical performance implication:** a regular UDF is a **black box** to Spark's Catalyst optimizer. It can't be pushed down or vectorized, and every row must be serialized/deserialized between the JVM and the Python process. This overhead adds up fast. **Always prefer a built-in function first.**

```python
# Example: categorize salaries
def categorize_salary(sal):
    if sal is None:
        return "UNKNOWN"
    elif sal < 80000:
        return "LOW"
    elif sal < 100000:
        return "MEDIUM"
    else:
        return "HIGH"

# Step 1: Define the UDF and its return type
from pyspark.sql.types import StringType
categorize_salary_udf = F.udf(categorize_salary, StringType())

# Step 2: Use it like any other function
df_with_category = df.withColumn("salary_category", categorize_salary_udf(F.col("salary")))
df_with_category.select("emp_id", "salary", "salary_category").show()

# Alternative: register the UDF for use in Spark SQL
spark.udf.register("sql_categorize_salary", categorize_salary, StringType())
df.createOrReplaceTempView("employees")
spark.sql("SELECT emp_id, salary, sql_categorize_salary(salary) AS salary_category FROM employees").show()

# Pandas UDFs (vectorized UDFs) - faster for complex operations on whole columns.
# They use Apache Arrow to move data as columnar batches instead of row-by-row,
# so the function receives and returns a pandas Series.
import pandas as pd
from pyspark.sql.functions import pandas_udf

@pandas_udf(DoubleType()) # Decorator specifying return type
def squared_udf(s: pd.Series) -> pd.Series:
    return s * s

df.withColumn("salary_squared", squared_udf(F.col("salary"))).show()
```

### Summary: UDF Performance Implications

| Factor | Regular UDF (Python) | Pandas UDF (Vectorized) | Built-in Functions |
| :--- | :--- | :--- | :--- |
| **Performance** | Slow (row-at-a-time, SerDe overhead) | Faster (chunk-at-a-time, uses Arrow) | **Fastest (fully optimized in JVM)** |
| **Optimization** | None (black box) | Limited | Full (Catalyst optimizer, predicate pushdown) |
| **When to Use** | Only if no built-in alternative exists | For complex operations on entire columns | **Always prefer this first** |
| **Syntax** | `F.udf(func, ReturnType())` | `@pandas_udf(ReturnType()) def func(s): ...` | `F.lower()`, `F.round()`, etc. |

## 🔗 Related Notes
- [[Basic DataFrame Operation|Basic DataFrame Operation]]
- [[Aggregation and Window Function|Aggregation and Window Function]]
- [[Regexp Functions|Regexp Functions]]
- [[Schema Operation in Pyspark|📘 Schema Operations in PySpark]]

# Handling Missing Data in PySpark

Handling `null` values is a critical step in any data pipeline. PySpark provides two primary tools: `dropna()` and `fillna()`.

### Setup

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *

spark = SparkSession.builder.appName("MissingDataGuide").getOrCreate()

# Sample DataFrame with various null values
data = [
    (1, "Alice", "Johnson", "NY", 85000, "1985-05-15"),
    (2, "Bob", None, "CA", 74000, None),           # Missing last_name and dob
    (3, "Charlie", "Brown", None, 99000, "1982-03-08"), # Missing state
    (4, None, "Prince", "WA", 120000, "1978-07-01"),    # Missing first_name
    (5, "Elon", "Musk", "CA", None, "1971-06-28"),      # Missing salary
    (6, None, None, None, None, None)                   # The "all null" record
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
df = df.withColumn("dob", F.to_date(F.col("dob"), "yyyy-MM-dd"))
df.show()
```

**Output:**
```
+-------+----------+---------+-----+------+----------+
|user_id|first_name|last_name|state|salary|       dob|
+-------+----------+---------+-----+------+----------+
|      1|     Alice|  Johnson|   NY| 85000|1985-05-15|
|      2|       Bob|     null|   CA| 74000|      null|
|      3|   Charlie|    Brown| null| 99000|1982-03-08|
|      4|      null|   Prince|   WA|120000|1978-07-01|
|      5|      Elon|     Musk|   CA|  null|1971-06-28|
|      6|      null|     null| null|  null|      null|
+-------+----------+---------+-----+------+----------+
```

---

### 1. `dropna()`: Removing Records with Missing Data

**Concept:** Deletes rows containing `null` values, based on a chosen strategy.

**Practical uses:**
*   Cleaning small datasets where dropping a few nulls doesn't skew the analysis.
*   Critical analyses that require every field to be present (e.g., financial transactions).
*   Pre-processing for ML models that can't handle nulls directly.

**Key parameters:**
*   `how`: `'any'` (default) drops a row if **any** column is null. `'all'` drops a row only if **all** columns are null.
*   `thresh`: an integer — keep only rows with at least this many **non-null** values.
*   `subset`: list of columns to consider when checking for nulls.

**Examples:**

```python
# Default behavior: drop rows with ANY null value (strict)
df_clean_any = df.dropna()
df_clean_any.show()
# Keeps only record 1 (Alice) - the only fully complete row.

# Drop rows where ALL values are null
df_clean_all = df.dropna(how='all')
df_clean_all.show()
# Keeps records 1-5. Drops only record 6, the fully null row.

# Drop rows with fewer than 3 non-null values
df_clean_thresh = df.dropna(thresh=3)
df_clean_thresh.show()
# Keeps records 1-5. Record 6 has only 1 non-null value (user_id=6), so it's dropped.

# Only consider nulls in specific columns
df_clean_subset = df.dropna(subset=['salary', 'state'])
df_clean_subset.show()
# Keeps records 1, 2, 4 - each has a non-null salary AND a non-null state.
# dropna(subset=...) ignores nulls in columns outside the subset (e.g. record 4's
# missing first_name doesn't matter here). Record 3 is dropped (state is null),
# record 5 is dropped (salary is null), and record 6 is dropped (both are null).
```

### 2. `fillna()`: Replacing Missing Data (Imputation)

**Concept:** Replaces `null` values with specified non-null values — often preferable to dropping data outright.

**Practical uses:**
*   Imputation: replace missing numeric values with a mean/median, categorical values with a mode.
*   Placeholder values (`"Unknown"`, `"N/A"`, `0`) for downstream systems that require a value.
*   Preparing complete datasets for visualization tools.

**Key parameters:**
*   `value`: the replacement value — a single scalar, or a `dict` mapping column names to specific values.
*   `subset`: columns to apply the fill to. If omitted, applies to all columns of a compatible type.

**Examples:**

```python
# Fill ALL nulls in ALL columns with a single value (use with caution)
df_fill_all = df.fillna('MISSING')
df_fill_all.show()
# String columns become 'MISSING'; numeric columns stay null, because a
# string literal can't be inserted into an IntegerType column.
# This often doesn't behave as intended, due to schema type constraints.

# Fill nulls with a value, but only in specific columns (safer)
df_fill_specific = df.fillna(0, subset=['salary']).fillna('UNKNOWN', subset=['state'])
df_fill_specific.show()

# Use a dictionary to fill different columns with different values
# (most common & flexible approach)
fill_values = {
    'first_name': 'Unknown_First',
    'last_name': 'Unknown_Last',
    'state': 'N/A',
    'salary': 0, # For an integer column
}
df_fill_dict = df.fillna(fill_values)
df_fill_dict.show()

# fillna() can't take a Column expression as its value, so date columns need
# a separate coalesce() step rather than a dict entry:
df_filled_simple = df.fillna(fill_values)
df_filled_simple = df_filled_simple.withColumn("dob", F.coalesce(F.col("dob"), F.to_date(F.lit("1900-01-01"))))
df_filled_simple.show()
```

### Practical Strategy: Choosing Between `dropna()` and `fillna()`

1.  **Understand the data first** — always check the amount and pattern of missingness before deciding.
    ```python
    # Quick analysis of nulls per column
    from pyspark.sql.functions import col, sum

    df.select(*(sum(col(c).isNull().cast("int")).alias(c) for c in df.columns)).show()
    ```

2.  **Use `dropna()` when:**
    *   The number of incomplete rows is very small (<5%).
    *   The missing data is not random and the records are otherwise unusable.
    *   You're preparing data for a model that requires complete cases.

3.  **Use `fillna()` when:**
    *   You can't afford to lose records.
    *   You can make a reasonable guess about the missing value (imputation).
    *   A downstream system requires a non-null value.

4.  **For statistical imputation** (mean/median), calculate the value first, then fill with it:
    ```python
    # Calculate the mean salary (ignoring nulls)
    mean_salary = df.agg(F.mean(F.col("salary"))).collect()[0][0]
    # Fill the nulls with the calculated mean
    df_fill_mean = df.fillna(mean_salary, subset=['salary'])
    print(f"Filling salary with mean value ({mean_salary:.2f}):")
    df_fill_mean.show()
    ```

## 🔗 Related Notes
- [[Basic DataFrame Operation|Basic DataFrame Operation]]
- [[Schema Operation in Pyspark|📘 Schema Operations in PySpark]]
- [[Pyspark Programs|Pyspark Programs]]

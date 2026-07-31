Excellent! Aggregations and Window Functions are where PySpark transitions from simple data manipulation to powerful analytical processing. Let's dive into the practical usage of both.

### The Practical Guide to Aggregations and Window Functions

First, let's set up our standard DataFrame with more data to better demonstrate these concepts.

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import *

spark = SparkSession.builder.appName("AggregationsGuide").getOrCreate()

# Create a more detailed sample DataFrame for aggregations
data = [
    (1, "Alice", "Johnson", "NY", "Sales", 85000, "2020-01-15"),
    (2, "Bob", "Smith", "CA", "Sales", 74000, "2021-03-10"),
    (3, "Charlie", "Brown", "NY", "Engineering", 99000, "2019-11-01"),
    (4, "Diana", "Prince", "WA", "Engineering", 120000, "2022-05-22"),
    (5, "Elon", "Musk", "CA", "Engineering", 150000, "2018-12-05"),
    (6, "Frank", "Wright", "NY", "Sales", 92000, "2020-08-14"),
    (7, "Grace", "Hopper", "CA", "Engineering", 110000, "2021-07-30"),
    (8, "Henry", "Ford", "MI", "Sales", 78000, "2019-05-17")
]

schema = StructType([
    StructField("emp_id", IntegerType(), True),
    StructField("first_name", StringType(), True),
    StructField("last_name", StringType(), True),
    StructField("state", StringType(), True),
    StructField("department", StringType(), True),
    StructField("salary", IntegerType(), True),
    StructField("hire_date", StringType(), True)
])

df = spark.createDataFrame(data, schema)
df = df.withColumn("hire_date", F.to_date(F.col("hire_date"), "yyyy-MM-dd"))

print("Original Employee DataFrame:")
df.show()
```

---

### 1. `groupBy()` followed by `agg()`

**Concept:** Split data into groups based on one or more columns, then compute summary statistics for each group.

**Practical Usage:** Generating reports, calculating departmental KPIs, understanding data distributions, and feature engineering.

#### Basic Syntax:
```python
df.groupBy("grouping_column(s)")\
  .agg(F.function1("column1").alias("name1"),
       F.function2("column2").alias("name2"))
```

**Examples:**

```python
# Single grouping column: Department summary
dept_summary = df.groupBy("department")\
                 .agg(F.count("emp_id").alias("employee_count"),
                      F.avg("salary").alias("avg_salary"),
                      F.sum("salary").alias("total_salary"),
                      F.max("salary").alias("max_salary"),
                      F.min("salary").alias("min_salary"))\
                 .orderBy(F.col("avg_salary").desc())

print("Department Summary:")
dept_summary.show()

# Multiple grouping columns: Department and State summary
dept_state_summary = df.groupBy("department", "state")\
                       .agg(F.count("emp_id").alias("employee_count"),
                            F.avg("salary").alias("avg_salary"))\
                       .orderBy("department", F.col("avg_salary").desc())

print("Department & State Summary:")
dept_state_summary.show()

# Using multiple aggregate functions on different columns
complex_agg = df.groupBy("state")\
                .agg(F.count("emp_id").alias("total_employees"),
                     F.avg("salary").alias("avg_salary"),
                     F.countDistinct("department").alias("unique_depts"))\
                .orderBy(F.col("total_employees").desc())

print("State-level Summary:")
complex_agg.show()
```

**Output for Department Summary:**

|department |employee_count|avg_salary|total_salary|max_salary|min_salary|
|-----------|--------------|----------|------------|---------|---------|
|Engineering|             4|  119750.0|      479000|   150000|    99000|
|      Sales|             4|   82250.0|      329000|    92000|    74000|

---

### 2. Window Functions

**Concept:** Perform calculations across a set of table rows that are somehow related to the current row. Unlike `groupBy()`, window functions **do not collapse** the rows - they add new columns to each row.

**Practical Usage:** Calculating rankings, running totals, moving averages, and comparing rows to group averages.

#### Key Components:
1.  **`Window.partitionBy()`**: Defines the groups (like `GROUP BY`)
2.  **`Window.orderBy()`**: Defines the ordering within each partition
3.  **`Window.rowsBetween()`**: Defines the window frame (e.g., preceding rows)

**Examples:**

```python
# Define some common windows first
dept_window = Window.partitionBy("department")
dept_salary_window = Window.partitionBy("department").orderBy(F.col("salary").desc())
running_total_window = Window.partitionBy("department").orderBy("hire_date").rowsBetween(Window.unboundedPreceding, Window.currentRow)

# Ranking within departments
df_ranked = df.withColumn("dept_salary_rank", F.rank().over(dept_salary_window))\
              .withColumn("dept_salary_dense_rank", F.dense_rank().over(dept_salary_window))\
              .withColumn("dept_row_number", F.row_number().over(dept_salary_window))

print("Ranking Employees within Departments by Salary:")
df_ranked.select("emp_id", "first_name", "department", "salary", "dept_salary_rank", "dept_salary_dense_rank", "dept_row_number")\
         .orderBy("department", "dept_salary_rank")\
         .show()

# Compare individual salary to department statistics
df_with_stats = df.withColumn("dept_avg_salary", F.avg("salary").over(dept_window))\
                  .withColumn("dept_max_salary", F.max("salary").over(dept_window))\
                  .withColumn("salary_vs_avg", F.col("salary") - F.col("dept_avg_salary"))\
                  .withColumn("salary_percent_of_max", F.round((F.col("salary") / F.col("dept_max_salary")) * 100, 2))

print("Individual vs Department Salary Comparison:")
df_with_stats.select("emp_id", "first_name", "department", "salary", "dept_avg_salary", "salary_vs_avg", "dept_max_salary", "salary_percent_of_max")\
             .orderBy("department", "salary")\
             .show()

# Calculate running totals within departments by hire date
df_running = df.withColumn("running_hire_count", F.count("emp_id").over(running_total_window))\
               .withColumn("running_salary_total", F.sum("salary").over(running_total_window))

print("Running Totals by Hire Date within Department:")
df_running.select("emp_id", "first_name", "department", "hire_date", "salary", "running_hire_count", "running_salary_total")\
          .orderBy("department", "hire_date")\
          .show()

# Lag and Lead: Compare to previous/next value
df_lag_lead = df.withColumn("prev_hire_date", F.lag("hire_date").over(dept_salary_window))\
                .withColumn("next_salary", F.lead("salary").over(dept_salary_window))

print("Lag and Lead Examples:")
df_lag_lead.select("emp_id", "first_name", "department", "salary", "hire_date", "prev_hire_date", "next_salary")\
           .orderBy("department", "salary")\
           .show()
```

**Output for Ranking:**


|emp_id|first_name|department|salary|dept_salary_rank|dept_salary_dense_rank|dept_row_number|
|------|----------|------------|------|-----------------|-----------------------|---------------|
|     5|      Elon|Engineering|150000|                1|                      1|              1|
|     4|     Diana|Engineering|120000|                2|                      2|              2|
|     7|     Grace|Engineering|110000|                3|                      3|              3|
|     3|   Charlie|Engineering| 99000|                4|                      4|              4|
|     6|     Frank|      Sales| 92000|                1|                      1|              1|
|     1|     Alice|      Sales| 85000|                2|                      2|              2|
|     8|     Henry|      Sales| 78000|                3|                      3|              3|
|     2|       Bob|      Sales| 74000|                4|                      4|              4|



### Key Differences: `groupBy().agg()` vs Window Functions

| Aspect | `groupBy().agg()` | Window Functions |
| :--- | :--- | :--- |
| **Output** | Collapsed data (one row per group) | **All original rows** + new calculated columns |
| **Use Case** | Summary statistics, reports | Row-level calculations, rankings, comparisons |
| **Performance** | Generally faster for summaries | Can be expensive on large datasets (keeps all rows) |
| **Syntax** | `.groupBy().agg()` | `.withColumn(..., F.func().over(Window...))` |

### Practical Use Cases:

- **`groupBy().agg()`**: "What's the average salary per department?" 
- **Window Functions**: "Show me each employee's salary and how it ranks within their department." or "What's the running total of hires per department over time?"

Mastering both patterns allows you to answer virtually any analytical question about your data.
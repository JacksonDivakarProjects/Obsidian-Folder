# Pivot Operations in PySpark

**Concept:** `pivot()` reshapes data from long to wide format, turning the unique values of one column into separate output columns — the Spark equivalent of an Excel pivot table.

---

### 1. Basic Pivot Syntax and Fundamentals

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *

spark = SparkSession.builder.appName("PivotMasterGuide").getOrCreate()

sales_data = [
    ("Q1", "North", "Electronics", 100000),
    ("Q1", "North", "Clothing", 75000),
    ("Q1", "South", "Electronics", 120000),
    ("Q1", "South", "Clothing", 90000),
    ("Q2", "North", "Electronics", 110000),
    ("Q2", "North", "Clothing", 80000),
    ("Q2", "South", "Electronics", 130000),
    ("Q2", "South", "Clothing", 95000),
    ("Q3", "North", "Electronics", 105000),
    ("Q3", "North", "Clothing", 78000),
    ("Q3", "South", "Electronics", 125000),
    ("Q3", "South", "Clothing", 92000)
]

schema = StructType([
    StructField("quarter", StringType(), True),
    StructField("region", StringType(), True),
    StructField("category", StringType(), True),
    StructField("revenue", IntegerType(), True)
])

sales_df = spark.createDataFrame(sales_data, schema)
sales_df.show() # Original data, long format
```

#### Basic Pivot Examples

```python
# Example 1: Pivot categories into columns
pivot_category = sales_df.groupBy("quarter", "region") \
                        .pivot("category") \
                        .agg(F.sum("revenue"))
pivot_category.show()

# Example 2: Pivot regions into columns
pivot_region = sales_df.groupBy("quarter", "category") \
                      .pivot("region") \
                      .agg(F.sum("revenue"))
pivot_region.show()

# Example 3: Single grouping column
pivot_simple = sales_df.groupBy("quarter") \
                      .pivot("category") \
                      .agg(F.sum("revenue"))
pivot_simple.show()
```

---

### 2. Advanced Aggregation with Pivot

```python
# Multiple aggregation functions
pivot_multi_agg = sales_df.groupBy("quarter") \
                         .pivot("category") \
                         .agg(
                             F.sum("revenue").alias("total_revenue"),
                             F.avg("revenue").alias("avg_revenue"),
                             F.count("revenue").alias("transaction_count")
                         )
pivot_multi_agg.show()

# Different metrics, same pivot
enhanced_sales = sales_df.withColumn("profit", F.col("revenue") * 0.3) \
                        .withColumn("units_sold", F.col("revenue") / 100)

pivot_complex = enhanced_sales.groupBy("quarter") \
                             .pivot("category") \
                             .agg(
                                 F.sum("revenue").alias("total_rev"),
                                 F.sum("profit").alias("total_profit"),
                                 F.avg("units_sold").alias("avg_units")
                             )
pivot_complex.show()
```

---

### 3. Performance: Always Specify Pivot Values

Without an explicit value list, Spark must first compute the distinct values of the pivot column — an extra pass over the data (and an extra job) before it can even build the pivot.

```python
# Method 1: manually specify values (best for performance)
specified_pivot = sales_df.groupBy("quarter") \
                         .pivot("category", ["Electronics", "Clothing"]) \
                         .agg(F.sum("revenue"))
specified_pivot.show()

# Method 2: dynamically collect the distinct values first
distinct_categories = [row['category'] for row in sales_df.select("category").distinct().collect()]

dynamic_pivot = sales_df.groupBy("quarter") \
                       .pivot("category", distinct_categories) \
                       .agg(F.sum("revenue"))
dynamic_pivot.show()

# Method 3: for very large datasets, an approximate distinct count at least
# tells you how wide the pivot will be before committing to it
from pyspark.sql.functions import approx_count_distinct

approx_distinct = sales_df.agg(approx_count_distinct("category").alias("distinct_count")).collect()[0][0]
print(f"Approximate distinct categories: {approx_distinct}")
```

---

### 4. Handling Data Quality Issues

```python
problematic_data = [
    ("Q1", "North", "Electronics", 100000),
    ("Q1", "North", "Clothing", 75000),
    ("Q1", "North", None, 50000),  # Null category
    ("Q1", "South", "Electronics", 120000),
    ("Q1", "South", "Clothing", 90000),
    ("Q1", "South", "Furniture", 80000),  # New category
    ("Q2", "North", "Electronics", 110000),
    ("Q2", "North", "Clothing", 80000)
]

problem_df = spark.createDataFrame(problematic_data, schema)

# Handle nulls before pivoting - a null pivot column produces a
# column literally named "null", which is rarely what you want
clean_df = problem_df.filter(F.col("category").isNotNull())

pivot_clean = clean_df.groupBy("quarter") \
                     .pivot("category") \
                     .agg(F.sum("revenue")) \
                     .fillna(0)  # Fill missing combinations with 0

pivot_clean.show()
```

---

### 5. Real-World Business Use Cases

#### Sales Performance Dashboard
```python
monthly_data = [
    ("2024-01", "Electronics", 150000),
    ("2024-01", "Clothing", 90000),
    ("2024-02", "Electronics", 160000),
    ("2024-02", "Clothing", 95000),
    ("2024-03", "Electronics", 170000),
    ("2024-03", "Clothing", 100000)
]

monthly_df = spark.createDataFrame(monthly_data, ["month", "category", "revenue"])

sales_dashboard = monthly_df.groupBy("month") \
                           .pivot("category") \
                           .agg(F.sum("revenue")) \
                           .withColumn("total_revenue", 
                                      F.coalesce(F.col("Electronics"), F.lit(0)) + 
                                      F.coalesce(F.col("Clothing"), F.lit(0))) \
                           .withColumn("electronics_pct", 
                                      F.round((F.col("Electronics") / F.col("total_revenue")) * 100, 2))

sales_dashboard.show()
```

#### Customer Behavior Analysis
```python
customer_data = [
    ("18-25", "Electronics", 500),
    ("18-25", "Clothing", 1200),
    ("26-35", "Electronics", 800),
    ("26-35", "Clothing", 1500),
    ("36-45", "Electronics", 600),
    ("36-45", "Clothing", 1100)
]

customer_df = spark.createDataFrame(customer_data, ["age_group", "category", "purchase_count"])

customer_analysis = customer_df.groupBy("age_group") \
                              .pivot("category") \
                              .agg(F.sum("purchase_count")) \
                              .withColumn("total_purchases", 
                                         F.coalesce(F.col("Electronics"), F.lit(0)) + 
                                         F.coalesce(F.col("Clothing"), F.lit(0)))

customer_analysis.show()
```

#### A/B Test Results
```python
ab_test_data = [
    ("Control", "Conversion Rate", 0.15),
    ("Control", "Average Order Value", 85.50),
    ("Control", "Bounce Rate", 0.45),
    ("Variant A", "Conversion Rate", 0.18),
    ("Variant A", "Average Order Value", 92.30),
    ("Variant A", "Bounce Rate", 0.38)
]

ab_test_df = spark.createDataFrame(ab_test_data, ["variant", "metric", "value"])

ab_test_results = ab_test_df.groupBy("metric") \
                           .pivot("variant") \
                           .agg(F.first("value"))  # first() is safe here - each group has exactly one value

ab_test_results.show()
```

---

### 6. Advanced Patterns

#### Dynamic Column Generation
```python
def create_pivot_analysis(df, group_col, pivot_col, agg_func):
    """Reusable helper for one-line pivot analyses."""
    distinct_values = [row[pivot_col] for row in df.select(pivot_col).distinct().collect()]
    return df.groupBy(group_col).pivot(pivot_col, distinct_values).agg(agg_func)

dynamic_result = create_pivot_analysis(sales_df, "quarter", "category", F.sum("revenue"))
dynamic_result.show()
```

#### Pivot Combined with Window Functions
```python
from pyspark.sql.window import Window

window_spec = Window.partitionBy("quarter").orderBy("revenue")

enhanced_analysis = sales_df.withColumn("rank", F.rank().over(window_spec)) \
                           .groupBy("quarter") \
                           .pivot("category") \
                           .agg(
                               F.sum("revenue").alias("total_rev"),
                               F.avg("rank").alias("avg_rank")
                           )
enhanced_analysis.show()
```

---

### 7. Performance Best Practices and Gotchas

```python
# 1. Filter before pivoting, not after
filtered_pivot = sales_df.filter(F.col("revenue") > 80000) \
                        .groupBy("quarter") \
                        .pivot("category") \
                        .agg(F.sum("revenue"))

# 2. High-cardinality pivot columns produce very wide, sparse output.
# Bucket the values first if there are too many distinct ones.
bucketed_df = sales_df.withColumn("revenue_bucket", 
                                 F.when(F.col("revenue") < 100000, "Low")
                                  .when(F.col("revenue") < 200000, "Medium")
                                  .otherwise("High"))

bucketed_pivot = bucketed_df.groupBy("quarter") \
                           .pivot("revenue_bucket") \
                           .agg(F.count("revenue"))
bucketed_pivot.show()

# 3. Watch memory usage - wide pivots (many distinct pivot values) can
# produce a very wide row, which is expensive to shuffle and hold in memory.
```

---

### 8. Comparison with Other Approaches

```python
# groupBy twice, with a pivot at the end - equivalent result, useful when
# you already have a pre-aggregated long-format table
traditional_approach = sales_df.groupBy("quarter", "category") \
                              .agg(F.sum("revenue").alias("total_revenue")) \
                              .groupBy("quarter") \
                              .pivot("category") \
                              .agg(F.first("total_revenue"))
traditional_approach.show()
```

**When to use what:**
- `pivot()` — for reporting and visualization prep.
- `groupBy()` alone — for further analytical processing (long format is easier to keep transforming).
- Window functions — for row-level calculations that must retain the original row count.

### Key Takeaways

1.  **Pivot reshapes**: long data becomes wide, for reporting.
2.  **Always specify pivot values** when you know them — it avoids an extra distinct-value scan.
3.  **Handle nulls before pivoting**, and `.fillna()` after, to avoid a stray `"null"` column and sparse gaps.
4.  **Watch cardinality** — too many distinct pivot values create wide, unwieldy, expensive output.
5.  **Best for business reporting**: dashboards, Excel-style summaries.
6.  **Combines well** with aggregations, window functions, and upstream data cleaning.

## 🔗 Related Notes
- [[Aggregation and Window Function|Aggregation and Window Function]]
- [[Basic DataFrame Operation|Basic DataFrame Operation]]
- [[Pyspark Programs|Pyspark Programs]]

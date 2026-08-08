# Spark SQL and Temporary Views

How the DataFrame API and Spark SQL integrate, and when to reach for each.

---

### 1. Creating Temporary Views (`createOrReplaceTempView()`)

**Concept:** Register a DataFrame as a temporary table queryable with SQL syntax. The view is session-scoped and disappears when the session ends.

**Practical use:** making DataFrames accessible to SQL queries, enabling SQL-based transformations and analysis.

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.appName("SparkSQLGuide").getOrCreate()

employees_data = [
    (1, "Alice", "Johnson", "Sales", 85000, "NY"),
    (2, "Bob", "Smith", "Engineering", 95000, "CA"),
    (3, "Charlie", "Brown", "Sales", 78000, "NY"),
    (4, "Diana", "Prince", "Engineering", 110000, "WA"),
    (5, "Elon", "Musk", "Executive", 200000, "CA")
]

employees_df = spark.createDataFrame(employees_data, 
                                   ["emp_id", "first_name", "last_name", "department", "salary", "state"])

departments_data = [
    ("Sales", "John Doe", 1000000),
    ("Engineering", "Jane Smith", 2000000),
    ("Executive", "CEO", 5000000)
]

departments_df = spark.createDataFrame(departments_data, 
                                     ["department", "manager", "budget"])

employees_df.createOrReplaceTempView("employees")
departments_df.createOrReplaceTempView("departments")

spark.sql("SHOW TABLES").show()
```

**Output:**
```
+---------+--------+-----------+
|namespace|tableName|isTemporary|
+---------+--------+-----------+
|         |employees|       true|
|         |departments|       true|
+---------+--------+-----------+
```

---

### 2. Writing SQL Queries with `spark.sql()`

**Concept:** run full SQL queries against temporary views.

**Practical use:** leveraging existing SQL expertise, expressing complex queries that are cumbersome in the DataFrame API, and porting existing SQL code.

#### Basic Operations
```python
result = spark.sql("""
    SELECT emp_id, first_name, last_name, salary 
    FROM employees 
    WHERE salary > 90000
    ORDER BY salary DESC
""")
result.show()

# JOIN
join_result = spark.sql("""
    SELECT e.emp_id, e.first_name, e.last_name, e.department, 
           e.salary, d.manager, d.budget
    FROM employees e
    JOIN departments d ON e.department = d.department
    WHERE e.salary > 80000
""")
join_result.show()

# Aggregations
agg_result = spark.sql("""
    SELECT department, 
           COUNT(*) as employee_count,
           AVG(salary) as avg_salary,
           MAX(salary) as max_salary
    FROM employees
    GROUP BY department
    HAVING AVG(salary) > 85000
""")
agg_result.show()
```

#### Advanced SQL Features
```python
# Window functions
window_result = spark.sql("""
    SELECT emp_id, first_name, department, salary,
           RANK() OVER (PARTITION BY department ORDER BY salary DESC) as dept_rank,
           AVG(salary) OVER (PARTITION BY department) as dept_avg_salary
    FROM employees
""")
window_result.show()

# Common Table Expressions (CTEs)
cte_result = spark.sql("""
    WITH high_earners AS (
        SELECT * FROM employees WHERE salary > 100000
    ),
    ny_employees AS (
        SELECT * FROM employees WHERE state = 'NY'
    )
    SELECT h.first_name, h.last_name, h.salary, n.state
    FROM high_earners h
    JOIN ny_employees n ON h.emp_id = n.emp_id
""")
cte_result.show()

# Date functions and casting
spark.sql("""
    SELECT first_name, 
           salary,
           salary * 0.1 as bonus,
           CAST(salary * 1.1 AS INT) as new_salary
    FROM employees
""").show()
```

---

### 3. DataFrame API vs. Spark SQL: When to Use Which

#### Use the DataFrame API when:

**1. Programmatic, conditional logic:**
```python
df_transformed = (employees_df
                 .withColumn("salary_bucket", 
                             F.when(F.col("salary") < 80000, "Low")
                              .when(F.col("salary") < 120000, "Medium")
                              .otherwise("High"))
                 .withColumn("full_name", 
                             F.concat(F.col("first_name"), F.lit(" "), F.col("last_name")))
                 .filter(F.col("department").isin(["Sales", "Engineering"]))
                )
```

**2. Chaining operations readably:**
```python
result = (employees_df
         .filter(F.col("salary") > 80000)
         .groupBy("department")
         .agg(F.avg("salary").alias("avg_salary"),
              F.count("*").alias("count"))
         .orderBy(F.col("avg_salary").desc())
        )
```

**3. IDE support and refactoring safety:**
```python
df.select("emp_id", "first_name")  # IDE can autocomplete column names
```

**4. Programmatically generated column lists:**
```python
columns_to_select = ["emp_id", "first_name", "last_name"]
if include_salary:
    columns_to_select.append("salary")
    
result = employees_df.select(columns_to_select)
```

#### Use Spark SQL when:

**1. Team is more comfortable with SQL:**
```python
spark.sql("""
    SELECT department, AVG(salary) as avg_salary
    FROM employees 
    WHERE salary > 80000
    GROUP BY department
    HAVING AVG(salary) > 90000
    ORDER BY avg_salary DESC
""")
```

**2. Complex, naturally SQL-shaped queries:**
```python
spark.sql("""
    WITH ranked_employees AS (
        SELECT *,
               RANK() OVER (PARTITION BY department ORDER BY salary DESC) as rank
        FROM employees
    )
    SELECT * FROM ranked_employees WHERE rank <= 3
""")
```

**3. Porting existing SQL:**
```python
existing_sql_query = """
    SELECT e.*, d.manager 
    FROM employees e
    LEFT JOIN departments d ON e.department = d.department
    WHERE e.state IN ('NY', 'CA')
"""

result = spark.sql(existing_sql_query)
```

**4. Ad-hoc exploration:**
```python
spark.sql("SELECT DISTINCT department FROM employees").show()
spark.sql("SELECT state, COUNT(*) FROM employees GROUP BY state").show()
```

#### Mixed Approach (Often the Most Practical)

Combine both — DataFrame API for ETL, SQL for analysis:
```python
processed_df = (employees_df
               .filter(F.col("salary").isNotNull())
               .withColumn("tax_rate", 
                          F.when(F.col("salary") > 100000, 0.3)
                           .otherwise(0.2))
              )

processed_df.createOrReplaceTempView("processed_employees")

analysis_result = spark.sql("""
    SELECT department, 
           AVG(salary) as avg_salary,
           AVG(salary * tax_rate) as avg_tax
    FROM processed_employees
    GROUP BY department
    ORDER BY avg_tax DESC
""")
```

### Practical Recommendations

1.  **ETL pipelines:** prefer the DataFrame API for programmability and testability.
2.  **Analytical queries:** Spark SQL for complex aggregations and reporting.
3.  **Mixed environments:** DataFrame API to prepare data, then SQL to analyze it.
4.  **Team collaboration:** choose based on team skills — both compile to the same execution plan.

### Performance Note

**There is no performance difference.** Both approaches go through the same Catalyst optimizer and produce identical (or equivalent) execution plans. The choice is purely about syntax preference and readability for the task at hand.

```python
# Both of these produce the same execution plan
df_api = employees_df.filter(F.col("salary") > 80000).select("first_name", "last_name")
sql_api = spark.sql("SELECT first_name, last_name FROM employees WHERE salary > 80000")

df_api.explain()
sql_api.explain()
```

## 🔗 Related Notes
- [[Aggregation and Window Function|Aggregation and Window Function]]
- [[Joining DataFrames|Joining DataFrames]]
- [[Pyspark Pivoting|Pyspark Pivoting]]

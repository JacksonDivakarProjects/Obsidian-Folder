# Joining DataFrames

Joins are fundamental for combining data from different sources.

### Setup

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *

spark = SparkSession.builder.appName("JoinsGuide").getOrCreate()

# Employees DataFrame
employees_data = [
    (1, "Alice", "Johnson", "NY", 85000),
    (2, "Bob", "Smith", "CA", 74000),
    (3, "Charlie", "Brown", "NY", 99000),
    (4, "Diana", "Prince", "WA", 120000),
    (5, "Elon", "Musk", "TX", 150000)  # TX doesn't exist in departments
]

employees_schema = StructType([
    StructField("emp_id", IntegerType(), True),
    StructField("first_name", StringType(), True),
    StructField("last_name", StringType(), True),
    StructField("state", StringType(), True),
    StructField("salary", IntegerType(), True)
])

employees_df = spark.createDataFrame(employees_data, employees_schema)

# Departments DataFrame
departments_data = [
    ("NY", "Sales", "John Doe"),
    ("CA", "Engineering", "Jane Smith"),
    ("WA", "Marketing", "Mike Johnson"),
    ("IL", "HR", "Sarah Wilson")  # IL doesn't exist in employees
]

departments_schema = StructType([
    StructField("state", StringType(), True),
    StructField("department", StringType(), True),
    StructField("manager", StringType(), True)
])

departments_df = spark.createDataFrame(departments_data, departments_schema)

employees_df.show()
departments_df.show()
```

**Output:**
```
Employees DataFrame:
+------+----------+---------+-----+------+
|emp_id|first_name|last_name|state|salary|
+------+----------+---------+-----+------+
|     1|     Alice|  Johnson|   NY| 85000|
|     2|       Bob|    Smith|   CA| 74000|
|     3|   Charlie|    Brown|   NY| 99000|
|     4|     Diana|   Prince|   WA|120000|
|     5|      Elon|     Musk|   TX|150000|
+------+----------+---------+-----+------+

Departments DataFrame:
+-----+------------+----------+
|state|  department|   manager|
+-----+------------+----------+
|   NY|       Sales|  John Doe|
|   CA|Engineering|Jane Smith|
|   WA|   Marketing|Mike Johnson|
|   IL|          HR|Sarah Wilson|
+-----+------------+----------+
```

---

### Types of Joins

#### 1. `inner` Join
**Concept:** Returns only rows whose join key exists in **both** DataFrames.

**Use it when:** you only want matches from both tables (the most common join type).

```python
inner_join_df = employees_df.join(departments_df, on="state", how="inner")
inner_join_df.show()
```

**Output:**
```
+-----+------+----------+---------+------+------------+----------+
|state|emp_id|first_name|last_name|salary|  department|   manager|
+-----+------+----------+---------+------+------------+----------+
|   NY|     1|     Alice|  Johnson| 85000|       Sales|  John Doe|
|   NY|     3|   Charlie|    Brown| 99000|       Sales|  John Doe|
|   CA|     2|       Bob|    Smith| 74000|Engineering|Jane Smith|
|   WA|     4|     Diana|   Prince|120000|   Marketing|Mike Johnson|
+-----+------+----------+---------+------+------------+----------+
```

#### 2. `outer` / `full` / `full_outer` Join
**Concept:** Returns all rows from both DataFrames, with `null` filled in wherever no match exists.

**Use it when:** you want to see everything from both tables and identify what's missing on either side.

```python
full_outer_df = employees_df.join(departments_df, on="state", how="full_outer")
full_outer_df.show()
```

**Output:**
```
+-----+------+----------+---------+------+------------+----------+
|state|emp_id|first_name|last_name|salary|  department|   manager|
+-----+------+----------+---------+------+------------+----------+
|   IL|  null|      null|     null|  null|          HR|Sarah Wilson|
|   TX|     5|      Elon|     Musk|150000|        null|      null|
|   NY|     1|     Alice|  Johnson| 85000|       Sales|  John Doe|
|   NY|     3|   Charlie|    Brown| 99000|       Sales|  John Doe|
|   CA|     2|       Bob|    Smith| 74000|Engineering|Jane Smith|
|   WA|     4|     Diana|   Prince|120000|   Marketing|Mike Johnson|
+-----+------+----------+---------+------+------------+----------+
```

#### 3. `left` / `left_outer` Join
**Concept:** Returns all rows from the left DataFrame, with matching right-side rows or `null` if none exist.

**Use it when:** you want every record from the main table plus optional lookup data.

```python
left_join_df = employees_df.join(departments_df, on="state", how="left")
left_join_df.show()
```

**Output:**
```
+-----+------+----------+---------+------+------------+----------+
|state|emp_id|first_name|last_name|salary|  department|   manager|
+-----+------+----------+---------+------+------------+----------+
|   NY|     1|     Alice|  Johnson| 85000|       Sales|  John Doe|
|   NY|     3|   Charlie|    Brown| 99000|       Sales|  John Doe|
|   CA|     2|       Bob|    Smith| 74000|Engineering|Jane Smith|
|   WA|     4|     Diana|   Prince|120000|   Marketing|Mike Johnson|
|   TX|     5|      Elon|     Musk|150000|        null|      null|
+-----+------+----------+---------+------+------------+----------+
```

#### 4. `right` / `right_outer` Join
**Concept:** Returns all rows from the right DataFrame, with matching left-side rows or `null` if none exist.

**Use it when:** you want every record from the lookup table and want to see which main records exist for it.

```python
right_join_df = employees_df.join(departments_df, on="state", how="right")
right_join_df.show()
```

**Output:**
```
+-----+------+----------+---------+------+------------+----------+
|state|emp_id|first_name|last_name|salary|  department|   manager|
+-----+------+----------+---------+------+------------+----------+
|   NY|     1|     Alice|  Johnson| 85000|       Sales|  John Doe|
|   NY|     3|   Charlie|    Brown| 99000|       Sales|  John Doe|
|   CA|     2|       Bob|    Smith| 74000|Engineering|Jane Smith|
|   WA|     4|     Diana|   Prince|120000|   Marketing|Mike Johnson|
|   IL|  null|      null|     null|  null|          HR|Sarah Wilson|
+-----+------+----------+---------+------+------------+----------+
```

#### 5. `left_semi` Join
**Concept:** Returns only left-side rows that have a match in the right DataFrame. **No right-side columns are included.**

**Use it when:** filtering — "find all employees who work in a state that has a department."

```python
left_semi_df = employees_df.join(departments_df, on="state", how="left_semi")
left_semi_df.show()
```

**Output:**
```
+------+----------+---------+-----+------+
|emp_id|first_name|last_name|state|salary|
+------+----------+---------+-----+------+
|     1|     Alice|  Johnson|   NY| 85000|
|     3|   Charlie|    Brown|   NY| 99000|
|     2|       Bob|    Smith|   CA| 74000|
|     4|     Diana|   Prince|   WA|120000|
+------+----------+---------+-----+------+
```

#### 6. `left_anti` Join
**Concept:** Returns only left-side rows that **do NOT** have a match in the right DataFrame. **No right-side columns are included.**

**Use it when:** filtering — "find all employees who work in states without a department."

```python
left_anti_df = employees_df.join(departments_df, on="state", how="left_anti")
left_anti_df.show()
```

**Output:**
```
+------+----------+---------+-----+------+
|emp_id|first_name|last_name|state|salary|
+------+----------+---------+-----+------+
|     5|      Elon|     Musk|   TX|150000|
+------+----------+---------+-----+------+
```

---

### Handling Duplicate Column Names After a Join

**The problem:** joining on differently-named columns, or joining DataFrames that share a non-key column name, both leave you with ambiguous or duplicate columns.

**Solution 1 — Rename before joining** (clearest, and recommended by default)
```python
departments_renamed = departments_df.withColumnRenamed("manager", "dept_manager")

clean_join_df = employees_df.join(departments_renamed, on="state", how="left")
clean_join_df.show()
```

**Solution 2 — Specify the join condition explicitly** (good for complex joins)
```python
explicit_join_df = employees_df.join(departments_df, 
                                    employees_df.state == departments_df.state, 
                                    how="left")

# Note the duplicate 'state' columns in the result
explicit_join_df.show()

# Now you can choose which state column to keep
explicit_join_df = explicit_join_df.drop(departments_df.state)
explicit_join_df.show()
```

**Solution 3 — De-duplicate columns after the join**
```python
joined_with_duplicates = employees_df.join(departments_df, on="state", how="left")

all_columns = joined_with_duplicates.columns
print("All columns after join:", all_columns)

# Keep only the first occurrence of each column name
columns_to_keep = []
seen_columns = set()

for col in all_columns:
    if col not in seen_columns:
        columns_to_keep.append(col)
        seen_columns.add(col)

final_df = joined_with_duplicates.select(columns_to_keep)
final_df.show()
```

**Solution 4 — Alias entire DataFrames** (useful for complex, multi-table scenarios)
```python
emp_alias = employees_df.alias("emp")
dept_alias = departments_df.alias("dept")

joined_df = emp_alias.join(dept_alias, emp_alias.state == dept_alias.state, how="left")

# Reference columns through the alias
joined_df.select("emp.*", "dept.department", "dept.manager").show()
```

### Practical Join Tips

1.  Know your data before choosing a join type — understand what each `how=` will actually return.
2.  Prefer `inner` joins when you only want complete matches.
3.  Use `left_semi` / `left_anti` for filtering instead of joining and then dropping columns manually.
4.  Rename conflicting columns proactively, before the join.
5.  Be cautious with `outer` joins — they can significantly inflate row counts.

```python
# Common practical pattern: left join with pre-renaming
result_df = (employees_df
             .join(departments_df.withColumnRenamed("manager", "dept_manager"), 
                   on="state", 
                   how="left")
             .select("emp_id", "first_name", "last_name", "salary", "department", "dept_manager")
            )
result_df.show()
```

---

### `DataFrame.join()` Signature

```python
DataFrame.join(
    other: DataFrame,
    on: Optional[Union[str, List[str], Column]] = None,
    how: Optional[str] = None
)
```

**Arguments:**

1.  **`other`** — the second DataFrame to join.
2.  **`on`** — the column(s) or condition to join on:
    - **string** → a single column name common to both DataFrames:
      ```python
      df1.join(df2, on="id", how="inner")
      ```
    - **list of strings** → multiple common columns:
      ```python
      df1.join(df2, on=["id", "date"], how="left")
      ```
    - **Column expression** → an explicit condition (like Pandas' `left_on`/`right_on`):
      ```python
      df1.join(df2, df1["id1"] == df2["id2"], how="inner")
      ```
3.  **`how`** — join type: `"inner"`, `"outer"`, `"left"`, `"right"`, `"left_semi"`, `"left_anti"`, `"cross"`.

**More examples:**

```python
# Same column name
df1.join(df2, on="id", how="inner")

# Multiple shared columns
df1.join(df2, on=["id", "date"], how="left")

# Different column names
df1.join(df2, df1["id1"] == df2["id2"], how="inner")

# Multiple conditions
df1.join(
    df2,
    (df1["id1"] == df2["id2"]) & (df1["date"] == df2["dt"]),
    how="left"
)
```

The rule of thumb: if the join columns share a name, use `on="col"` (or a list of names); if they don't, use an explicit `df1.col == df2.col` condition.

## 🔗 Related Notes
- [[Broadcasting in Pyspark|Broadcasting in Pyspark]]
- [[Performance & Optimisation in Pyspark|Performance & Optimisation in Pyspark]]
- [[Basic DataFrame Operation|Basic DataFrame Operation]]
- [[SCD In Pyspark|SCD In Pyspark]]

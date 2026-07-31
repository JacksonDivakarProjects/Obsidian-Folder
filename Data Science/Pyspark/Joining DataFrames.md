Of course! Joins are fundamental for combining data from different sources. Let's create a comprehensive practical guide for joining DataFrames in PySpark.

### The Practical Guide to Joining DataFrames

First, let's set up our sample DataFrames to demonstrate the different join types.

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *

spark = SparkSession.builder.appName("JoinsGuide").getOrCreate()

# Create Employees DataFrame
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

# Create Departments DataFrame
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

print("Employees DataFrame:")
employees_df.show()

print("Departments DataFrame:")
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
**Concept:** Returns only rows where the join key exists in **both** DataFrames.

**Practical Usage:** When you only want matches from both tables (most common join type).

```python
inner_join_df = employees_df.join(departments_df, on="state", how="inner")
print("INNER JOIN (only matching states in both tables):")
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
**Concept:** Returns all rows from both DataFrames, with `null` where no match exists.

**Practical Usage:** When you want to see all records from both tables and identify what's missing.

```python
full_outer_df = employees_df.join(departments_df, on="state", how="full_outer")
print("FULL OUTER JOIN (all records from both tables):")
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
**Concept:** Returns all rows from the left DataFrame, with matching rows from the right DataFrame (or `null` if no match).

**Practical Usage:** When you want all records from the main table and optional information from a lookup table.

```python
left_join_df = employees_df.join(departments_df, on="state", how="left")
print("LEFT JOIN (all employees, with department info if available):")
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
**Concept:** Returns all rows from the right DataFrame, with matching rows from the left DataFrame (or `null` if no match).

**Practical Usage:** When you want all records from the lookup table and see which main records exist.

```python
right_join_df = employees_df.join(departments_df, on="state", how="right")
print("RIGHT JOIN (all departments, with employee info if available):")
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
**Concept:** Returns only rows from the left DataFrame that have a match in the right DataFrame. **No columns from the right DataFrame are included.**

**Practical Usage:** As a filter - "Find all employees who work in a state that has a department."

```python
left_semi_df = employees_df.join(departments_df, on="state", how="left_semi")
print("LEFT SEMI JOIN (employees in states with departments):")
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
**Concept:** Returns only rows from the left DataFrame that **do NOT** have a match in the right DataFrame. **No columns from the right DataFrame are included.**

**Practical Usage:** As a filter - "Find all employees who work in states without departments."

```python
left_anti_df = employees_df.join(departments_df, on="state", how="left_anti")
print("LEFT ANTI JOIN (employees in states WITHOUT departments):")
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

### Handling Duplicate Column Names After Join

**The Problem:** When joining on columns with different names, or when both DataFrames have columns with the same name that aren't join keys.

**Solution 1: Rename before join** (Recommended - Most Clear)
```python
# Rename conflicting columns before joining
departments_renamed = departments_df.withColumnRenamed("manager", "dept_manager")

clean_join_df = employees_df.join(departments_renamed, on="state", how="left")
print("Join after renaming conflicting columns:")
clean_join_df.show()
```

**Solution 2: Specify join condition explicitly** (Good for complex joins)
```python
# Explicit join condition avoids the duplicate issue for the join key
explicit_join_df = employees_df.join(departments_df, 
                                    employees_df.state == departments_df.state, 
                                    how="left")

print("Join with explicit condition (note duplicate state columns):")
explicit_join_df.show()

# Now you can select which state column to keep
explicit_join_df = explicit_join_df.drop(departments_df.state)
explicit_join_df.show()
```

**Solution 3: Use array of join keys and handle duplicates manually**
```python
# Join creates duplicate columns
joined_with_duplicates = employees_df.join(departments_df, on="state", how="left")

# List all columns and identify duplicates
all_columns = joined_with_duplicates.columns
print("All columns after join:", all_columns)

# Drop duplicate columns (keeping ones from left DataFrame)
columns_to_keep = []
seen_columns = set()

for col in all_columns:
    if col not in seen_columns:
        columns_to_keep.append(col)
        seen_columns.add(col)

final_df = joined_with_duplicates.select(columns_to_keep)
print("After removing duplicate columns:")
final_df.show()
```

**Solution 4: Use aliases for entire DataFrames** (Useful for complex scenarios)
```python
# Create aliases for the DataFrames
emp_alias = employees_df.alias("emp")
dept_alias = departments_df.alias("dept")

joined_df = emp_alias.join(dept_alias, emp_alias.state == dept_alias.state, how="left")

# Now you can reference columns with the alias
joined_df.select("emp.*", "dept.department", "dept.manager").show()
```

### Practical Join Tips:

1.  **Always know your data:** Understand what each join type will return before executing.
2.  **Prefer `inner` joins** when you only want complete matches.
3.  **Use `left_semi` and `left_anti`** for filtering instead of more complex methods.
4.  **Handle duplicate columns proactively** by renaming before joining.
5.  **Be cautious with `outer` joins** - they can significantly increase your data size.

```python
# Most common practical pattern: left join with pre-renaming
result_df = (employees_df
             .join(departments_df.withColumnRenamed("manager", "dept_manager"), 
                   on="state", 
                   how="left")
             .select("emp_id", "first_name", "last_name", "salary", "department", "dept_manager")
            )
result_df.show()
```

---

### 🔹 PySpark `DataFrame.join()`

The **function signature** is:

```python
DataFrame.join(
    other: DataFrame,
    on: Optional[Union[str, List[str], Column]] = None,
    how: Optional[str] = None
)
```

---

### 🔹 Arguments explained

1. **`other`**
    
    - The second DataFrame you want to join.
        
2. **`on`**
    
    - Column(s) or condition to join on.
        
    - Can be:
        
        - **string** → one column name common in both DataFrames
            
            ```python
            df1.join(df2, on="id", how="inner")
            ```
            
        - **list of strings** → multiple common columns
            
            ```python
            df1.join(df2, on=["id", "date"], how="left")
            ```
            
        - **Column expression** → explicit join condition (like Pandas `left_on` / `right_on`)
            
            ```python
            df1.join(df2, df1["id1"] == df2["id2"], how="inner")
            ```
            
3. **`how`**
    
    - Type of join:  
        `"inner"`, `"outer"`, `"left"`, `"right"`, `"left_semi"`, `"left_anti"`, `"cross"`
        

---

### 🔹 Examples

#### Same column name

```python
df1.join(df2, on="id", how="inner")
```

#### Multiple same columns

```python
df1.join(df2, on=["id", "date"], how="left")
```

#### Different column names

```python
df1.join(df2, df1["id1"] == df2["id2"], how="inner")
```

#### Multiple conditions

```python
df1.join(
    df2,
    (df1["id1"] == df2["id2"]) & (df1["date"] == df2["dt"]),
    how="left"
)
```

---

✅ So the key is:

- If **columns have the same name** → use `on="col"` or `on=["col1", "col2"]`
    
- If **columns differ** → use `df1.col == df2.col`
    

---

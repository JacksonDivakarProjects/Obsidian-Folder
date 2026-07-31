
Here’s a **comprehensive guide to `groupby()` in pandas**, designed for practical application with real examples and a professional tone that aligns with your learning goals and future data roles.

---

# 🔧 `groupby()` in Pandas – Comprehensive Guide

## 🔹 What is `groupby()`?

`groupby()` is used to **split data into groups** based on one or more columns. You can then **apply aggregate functions** like `sum()`, `mean()`, `count()`, `max()`, etc., to these groups.

---

## 🔹 Basic Syntax

```python
df.groupby('column_name')
```

Optional chaining:

```python
df.groupby('column_name').agg_func()
```

---

## ✅ Step-by-Step: Split → Apply → Combine

1. **Split**: Break data into groups based on keys
    
2. **Apply**: Run a function (e.g., sum, mean) on each group
    
3. **Combine**: Merge results into a new DataFrame or Series
    

---

## 🔹 Sample DataFrame

```python
import pandas as pd

data = {
    'Department': ['HR', 'HR', 'IT', 'IT', 'IT', 'Sales'],
    'Employee': ['A', 'B', 'C', 'D', 'E', 'F'],
    'Salary': [5000, 7000, 6000, 6000, 7500, 4000],
    'Gender': ['M', 'F', 'M', 'F', 'M', 'F']
}
df = pd.DataFrame(data)
```

---

## 🔹 Common Aggregation Functions

### 1. **`sum()`**

```python
df.groupby('Department')['Salary'].sum()
```

### 2. **`mean()`**

```python
df.groupby('Department')['Salary'].mean()
```

### 3. **`count()`**

```python
df.groupby('Department')['Salary'].count()
```

### 4. **`max()` / `min()`**

```python
df.groupby('Department')['Salary'].max()
```

---

## 🔹 Group by Multiple Columns

```python
df.groupby(['Department', 'Gender'])['Salary'].mean()
```

Returns the average salary for each gender in each department.

---

## 🔹 Using `.agg()` for Multiple Aggregations

```python
df.groupby('Department')['Salary'].agg(['mean', 'sum', 'max'])
```

You can also **rename**:

```python
df.groupby('Department')['Salary'].agg(
    avg_salary='mean',
    total_salary='sum'
)
```

---
## 🔹 `.agg()` with Dictionary Syntax — Core Structure

```python

df.groupby('group_col').agg({
'col1': 'sum',
'col2': 'mean',
'col3': 'nunique'
})

```

✅ Each column in the dict is a target column
✅ The value is the aggregation function to apply

---

## 🔧 Practical Examples

### 1. **Multiple columns, single aggregation each**

```python

df.groupby('Department').agg({
'Salary': 'mean',
'Employee': 'count'
})

```

➡️ Get average salary and number of employees per department.

## 🔹 Resetting Index (Optional)

```python
df.groupby('Department')['Salary'].sum().reset_index()
```

Useful for converting groupby result back to DataFrame with default index.

---

## 🔹 Filtering Groups with Conditions

```python
grouped = df.groupby('Department')
grouped.filter(lambda x: x['Salary'].mean() > 6000)
```

This returns rows **only from groups** whose average salary is > 6000.

---

## 🔹 Accessing Groups

```python
grouped = df.groupby('Department')
grouped.get_group('IT')
```

---

## 🔹 Custom Aggregation with Functions

```python
df.groupby('Department')['Salary'].agg(lambda x: x.std())
```

---

## 🔹 Named Aggregation for Multiple Columns (from pandas 0.25+)

```python
df.groupby('Department').agg(
    avg_salary=('Salary', 'mean'),
    emp_count=('Employee', 'count')
)
```

---

## 🔹 GroupBy with `as_index=False`

To keep the group column as a column (not index):

```python
df.groupby('Department', as_index=False)['Salary'].mean()
```

---

## 🔹 Transform vs. Aggregate

- `agg()` reduces rows.
    
- `transform()` returns same shape as original → useful for adding new columns.
    

```python
df['Dept_Avg'] = df.groupby('Department')['Salary'].transform('mean')
```

---

## 🔹 Rank Within Groups

```python
df['Salary_Rank'] = df.groupby('Department')['Salary'].rank(method='dense', ascending=False)
```

---

## 🔹 Value Counts per Group

```python
df.groupby('Department')['Gender'].value_counts()
```

---

## 🔹 Groupby on Index

If index is meaningful:

```python
df.set_index('Department').groupby(level=0)['Salary'].mean()
```

---

## 🔹 Caveats to Remember

|Caveat|What to Know|
|---|---|
|Group keys become index|Use `as_index=False` to prevent this|
|NA values|Default behavior: NA values in group key are excluded|
|Order of groups|Default not sorted → use `sort=True` if needed|

---

## 📊 Real-World Use Case: Salary Report

```python
summary = df.groupby(['Department', 'Gender']).agg(
    total_salary=('Salary', 'sum'),
    avg_salary=('Salary', 'mean'),
    count=('Employee', 'count')
).reset_index()
```

---

## 🧠 Summary Table of `groupby` Functions

|Function|Use|
|---|---|
|`.sum()`|Total per group|
|`.mean()`|Average per group|
|`.count()`|Non-null count|
|`.agg()`|Custom + multiple stats|
|`.transform()`|Add group-wise stats to original rows|
|`.filter()`|Filter groups by condition|
|`.get_group()`|Access a specific group|
|`.rank()`|Rank within group|

---

If you're preparing for **interviews or data tasks**, mastering `groupby()` with `agg`, `transform`, and `filter` will make your skills stand out—especially in analytics, ETL, and reporting roles.

Would you like hands-on **practice exercises** or **interview-style case studies** on this?
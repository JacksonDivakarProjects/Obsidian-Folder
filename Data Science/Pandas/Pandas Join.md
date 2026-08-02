
Here's your **professional and practical SQL joins + Pandas-style multi-condition + `isin` / `~isin` guide**, perfect for interview prep, data analysis, or brushing up quickly.

---

# 📘 SQL Joins + Pandas Multi-Condition + `isin`/`~isin` — Master Note

---

## 🔁 PART 1: SQL JOINS – Overview

### 🔹 INNER JOIN

Returns only **matching rows** from both tables.

```sql
SELECT *
FROM table1
JOIN table2
  ON table1.id = table2.id
```

🔍 **Think:** “Give me only the overlapping data.”

---

### 🔹 LEFT JOIN

Returns **all rows from the left table**, and matched rows from the right.

```sql
SELECT *
FROM table1
LEFT JOIN table2
  ON table1.id = table2.id
```

🔍 **Think:** “Keep all from `table1`, even if no match in `table2`.”

---

### 🔹 RIGHT JOIN

Returns **all rows from the right table**, and matched rows from the left.

```sql
SELECT *
FROM table1
RIGHT JOIN table2
  ON table1.id = table2.id
```

---

### 🔹 FULL OUTER JOIN

Returns **all rows from both tables**, with `NULL` where no match.

```sql
SELECT *
FROM table1
FULL OUTER JOIN table2
  ON table1.id = table2.id
```

---

### 🔹 SELF JOIN

Joins a table to itself using aliases.

```sql
SELECT A.*, B.*
FROM employees A
JOIN employees B
  ON A.manager_id = B.employee_id
```

---

### 🔹 CROSS JOIN

Returns **all combinations** (Cartesian product).

```sql
SELECT *
FROM table1
CROSS JOIN table2
```

---

## 🧠 Use Case Summary

|Join Type|Use Case|
|---|---|
|INNER JOIN|Only matching records|
|LEFT JOIN|Keep all from left|
|RIGHT JOIN|Keep all from right|
|FULL OUTER JOIN|Combine everything|
|SELF JOIN|Compare rows within the same table|
|CROSS JOIN|All possible pairs|

---

## 🔁 PART 2: Pandas-style Join (Multiple `on` Columns)

Equivalent of:

```sql
SELECT *
FROM A
JOIN B
ON A.col1 = B.col1 AND A.col2 = B.col2
```

In **Pandas**:

```python
pd.merge(df1, df2, on=['col1', 'col2'], how='inner')
```

Or when column names differ:

```python
pd.merge(df1, df2,
         left_on=['df1_col1', 'df1_col2'],
         right_on=['df2_col1', 'df2_col2'],
         how='left')
```

---

## 🔍 PART 3: `isin()` and `~isin()` — SQL Equivalent

### ✅ Pandas:

```python
df[df['city'].isin(['Chennai', 'Mumbai'])]
```

### 🟢 SQL:

```sql
SELECT *
FROM table
WHERE city IN ('Chennai', 'Mumbai')
```

---

### ❌ Pandas (NOT IN):

```python
df[~df['city'].isin(['Delhi', 'Kolkata'])]
```

### 🔴 SQL:

```sql
SELECT *
FROM table
WHERE city NOT IN ('Delhi', 'Kolkata')
```

---

## 🧠 `isin()` Tips

- Can be used on **multiple columns** in Pandas:
    
    ```python
    df[df['city'].isin(city_list) & df['state'].isin(state_list)]
    ```
    
- Combine with `merge()` to simulate **semi-joins**.
    

---

## 💡 BONUS: SQL Join + `IN` Combo Example

```sql
SELECT *
FROM sales
JOIN customers
  ON sales.customer_id = customers.id
WHERE customers.city IN ('Pune', 'Hyderabad')
```

Pandas equivalent:

```python
pd.merge(sales, customers, on='customer_id')\
  .loc[lambda df: df['city'].isin(['Pune', 'Hyderabad'])]
```

---

Let me know if you'd like this exported as a **PDF reference sheet** or need practice problems to go with it!

## 🔗 Related Notes
- [[Data Science/Pandas/Pandas Special Notes For Tips and Tricks|Pandas Special Notes For Tips and Tricks]]
- [[Data Science/Pandas/Pandas .str methods|Pandas .str methods]]

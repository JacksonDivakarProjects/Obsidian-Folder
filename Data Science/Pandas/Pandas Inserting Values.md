
**📃 Inserting into DataFrame and Series (Pandas Guide)**

---

### 🛠️ 1. Inserting a Column into a DataFrame

**Syntax:**

```python
df.insert(loc, column_name, values)
```

- `loc` → Position to insert (0 = first column)
    
- `column_name` → Name of new column
    
- `values` → List/Series of values (must match row count)
    

**Example:**

```python
import pandas as pd

df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
df.insert(1, 'X', [100, 200, 300])
```

**Result:**

```
   A    X  B
0  1  100  4
1  2  200  5
2  3  300  6
```

---

### 🔄 2. Inserting into a Series

**A. Insert at a new label:**

```python
s = pd.Series([10, 20, 30], index=['a', 'b', 'c'])
s.loc['d'] = 40  # Adds at end with new index 'd'
```

**B. Insert at a specific position:**

```python
s = pd.Series([10, 20, 30], index=['a', 'b', 'c'])
s = pd.concat([s.iloc[:1], pd.Series([99], index=['x']), s.iloc[1:]])
```

**Result:**

```
a    10
x    99
b    20
c    30
dtype: int64
```

---

### 📊 Summary Table

|Task|Method|
|---|---|
|Insert column into DataFrame|`df.insert(loc, name, val)`|
|Add row to DataFrame|`df.loc[len(df)] = row_values`|
|Insert into Series (label)|`s.loc[new_index] = value`|
|Insert at position in Series|`pd.concat([...])`|

---

Let me know if you need guidance on row insertion, appending, or dynamic inserts with conditions.
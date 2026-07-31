
### 1. isin Function with Filters
```python
import pandas as pd

# Create a sample DataFrame
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie', 'David'],
    'Age': [25, 30, 35, 40],
    'City': ['New York', 'Los Angeles', 'Chicago', 'Houston']
})

# Using isin to filter rows where 'City' is in a list of values
# This is efficient for checking membership in a set or list
cities_of_interest = ['New York', 'Chicago']
filtered_df = df[df['City'].isin(cities_of_interest)]

print(filtered_df)
# Output:
#       Name  Age      City
# 0    Alice   25  New York
# 2  Charlie   35   Chicago

# Common pitfall: isin works on Series; for DataFrames, apply it column-wise.
# If the column has NaNs, isin will return False for them unless explicitly included.
```

### 2. Difference Between apply Function in DataFrame and Series
```python
import pandas as pd
import numpy as np

# Sample DataFrame
df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6]
})

# apply on Series: Applies a function element-wise to the Series
series_result = df['A'].apply(lambda x: x * 2)
print(series_result)
# Output:
# 0    2
# 1    4
# 2    6
# Name: A, dtype: int64

# apply on DataFrame: Applies a function along an axis (default: columns, axis=0)
# Here, it computes the mean for each column
df_result = df.apply(np.mean)  # Equivalent to df.apply(np.mean, axis=0)
print(df_result)
# Output:
# A    2.0
# B    5.0
# dtype: float64

# To apply row-wise on DataFrame, use axis=1
row_sum = df.apply(lambda row: row.sum(), axis=1)
print(row_sum)
# Output:
# 0    5
# 1    7
# 2    9
# dtype: int64

# Pitfall: DataFrame.apply can be slower than vectorized operations; use it only when necessary.
# Series.apply is strictly element-wise, while DataFrame.apply operates on Series (rows/columns).
```

### 3. Concatenation of Two Column Values Using the + Operator
```python
import pandas as pd

# Sample DataFrame with string columns
df_str = pd.DataFrame({
    'First': ['John', 'Jane'],
    'Last': ['Doe', 'Smith']
})

# Concatenating strings using + operator (element-wise)
df_str['Full Name'] = df_str['First'] + ' ' + df_str['Last']
print(df_str)
# Output:
#   First   Last  Full Name
# 0  John    Doe   John Doe
# 1  Jane  Smith  Jane Smith

# Sample DataFrame with numeric columns
df_num = pd.DataFrame({
    'X': [10, 20],
    'Y': [5, 15]
})

# Arithmetic addition using + operator (element-wise)
df_num['Sum'] = df_num['X'] + df_num['Y']
print(df_num)
# Output:
#     X   Y  Sum
# 0  10   5   15
# 1  20  15   35

# Assumption: Columns must be of compatible types (both str or both numeric).
# Pitfall: If one is str and one is numeric, + will raise TypeError. Use astype(str) for mixed types.
```

### 4. Filtering with String Accessors
```python
import pandas as pd

# Sample DataFrame
df = pd.DataFrame({
    'Product': ['Apple iPhone', 'Samsung Galaxy', 'Google Pixel', 'Apple Watch'],
    'Price': [1000, 900, 800, 400]
})

# Using string accessor .str for filtering
# Example: Filter rows where 'Product' starts with 'Apple'
filtered_starts = df[df['Product'].str.startswith('Apple')]
print(filtered_starts)
# Output:
#        Product  Price
# 0  Apple iPhone   1000
# 3   Apple Watch    400

# Filter where 'Product' contains 'Galaxy'
filtered_contains = df[df['Product'].str.contains('Galaxy')]
print(filtered_contains)
# Output:
#          Product  Price
# 1  Samsung Galaxy    900

# Common methods: .str.lower(), .str.endswith(), .str.match() for regex.
# Pitfall: .str only works on object dtype (strings); convert non-string columns with .astype(str).
# NaNs will raise AttributeError if not handled (use .fillna('') first if needed).
```

### 5. Updating Multiple Row Values Using loc
```python
import pandas as pd

# Sample DataFrame
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'Status': ['Active', 'Inactive', 'Active']
})

# Incorrect way: Chained indexing creates a temporary view, leading to SettingWithCopyWarning
# df[df['Status'] == 'Active']['Age'] = df[df['Status'] == 'Active']['Age'] + 1  # Avoid this!

# Correct way: Use .loc for direct assignment to avoid warnings and ensure changes persist
df.loc[df['Status'] == 'Active', 'Age'] += 1
print(df)
# Output:
#       Name  Age    Status
# 0    Alice   26    Active
# 1      Bob   30  Inactive
# 2  Charlie   36    Active

# Pitfall: Chained filtering (without .loc) may not modify the original DataFrame due to copy/view semantics.
# Always use .loc for safe multi-row updates.
```

### 6. sort_index() Function
```python
import pandas as pd

# Sample DataFrame with custom index
df = pd.DataFrame({
    'Value': [10, 20, 30]
}, index=['C', 'A', 'B'])

print("Original:")
print(df)
# Output:
#    Value
# C     10
# A     20
# B     30

# Sorting by index (ascending by default)
sorted_df = df.sort_index()
print("Sorted by index:")
print(sorted_df)
# Output:
#    Value
# A     20
# B     30
# C     10

# Descending sort
desc_sorted = df.sort_index(ascending=False)
print("Descending:")
print(desc_sorted)
# Output:
#    Value
# C     10
# B     30
# A     20

# Works on both row and column indices (use axis=1 for columns).
# Pitfall: Multi-level indices require level parameter; ignores NaN indices.
```

### 7. Sorting Multiple Values with Ascending Parameters (asc and desc) Using Boolean
```python
import pandas as pd

# Sample DataFrame
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie', 'David'],
    'Age': [30, 25, 35, 25],
    'Score': [85, 90, 80, 95]
})

# Sorting by multiple columns: 'Age' ascending (True), 'Score' descending (False)
sorted_df = df.sort_values(by=['Age', 'Score'], ascending=[True, False])
print(sorted_df)
# Output:
#       Name  Age  Score
# 3    David   25     95
# 1      Bob   25     90
# 0    Alice   30     85
# 2  Charlie   35     80

# Assumption: 'by' list matches 'ascending' list length.
# Pitfall: Mismatched lengths raise ValueError. For stability, use kind='stable'.
```

### 8. groupby with value_counts Function
```python
import pandas as pd

# Sample DataFrame
df = pd.DataFrame({
    'Category': ['A', 'A', 'B', 'A', 'B', 'C'],
    'Value': [10, 20, 10, 30, 20, 10]
})

# Group by 'Category' and count occurrences of each 'Value'
grouped_counts = df.groupby('Category')['Value'].value_counts()
print(grouped_counts)
# Output:
# Category  Value
# A         10       1
#           20       1
#           30       1
# B         10       1
#           20       1
# C         10       1
# Name: count, dtype: int64

# Returns a Series with MultiIndex.
# Pitfall: value_counts() normalizes if normalize=True, but groupby preserves raw counts.
```

### 9. groupby with apply Function for Series Grouped by Object
```python
import pandas as pd

# Sample DataFrame
df = pd.DataFrame({
    'Group': ['X', 'X', 'Y', 'Y'],
    'Value': [1, 3, 2, 4]
})

# Group by 'Group' and apply a custom function to each Series group
# Example: Compute range (max - min) for each group
grouped_apply = df.groupby('Group')['Value'].apply(lambda s: s.max() - s.min())
print(grouped_apply)
# Output:
# Group
# X    2
# Y    2
# Name: Value, dtype: int64

# apply returns a Series/DataFrame; lambda takes a Series as input.
# Pitfall: apply can be slow for large data; prefer agg() for built-in functions like 'sum'.
```

### 10. Handling NaN Values in Type Conversions
```python
import pandas as pd
import numpy as np

# Sample Series with mixed types and NaN
s = pd.Series(['1', '2', np.nan, '4'], dtype='object')

# Attempt direct conversion to int fails due to NaN (treated as float)
# s.astype(int)  # Raises ValueError: cannot convert float NaN to integer

# Safe way: Convert to float first, then handle NaNs if needed
s_float = s.astype(float)
print(s_float)
# Output:
# 0    1.0
# 1    2.0
# 2    NaN
# 3    4.0
# dtype: float64

# To convert to int after, fill NaNs (e.g., with 0)
s_int = s_float.fillna(0).astype(int)
print(s_int)
# Output:
# 0    1
# 1    2
# 2    0
# 3    4
# dtype: int64

# Pitfall: NaNs are floats, so object-to-int fails if NaNs present. Use pd.to_numeric() with errors='coerce' for flexibility.
```
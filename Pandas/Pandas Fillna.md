Here's your **comprehensive guide** to `fillna()` in **pandas**, with **practical use cases**, **parameters explained**, and **code examples** to clarify each scenario:

---

## 🧠 What is `fillna()`?

`.fillna()` is used to **replace missing (NaN)** values in a DataFrame or Series with a specified value, method, or logic.

---

## 🔧 Syntax

```python
DataFrame.fillna(value=None, method=None, axis=None, inplace=False, limit=None, downcast=None)
```

---

## ✅ Key Parameters Explained

|Parameter|Description|
|---|---|
|`value`|Value to use for replacing NaNs. Can be scalar, dict, Series, or DataFrame.|
|`method`|Fill using a method: `'ffill'` (forward), `'bfill'` (backward).|
|`axis`|0 for rows, 1 for columns.|
|`inplace`|If `True`, modifies original object.|
|`limit`|Maximum number of NaNs to fill.|
|`downcast`|Downcast dtypes if possible (e.g., `int64` → `int32`).|

---

## 📦 Basic Usage

```python
df = pd.DataFrame({
    'A': [1, 2, np.nan, 4],
    'B': [np.nan, 2, 3, np.nan]
})

# Replace NaNs with a specific value
df.fillna(0)
```

---

## 🔄 Forward Fill (`method='ffill'`)

```python
df.fillna(method='ffill')
```

> Fills missing values with the **previous** non-null value.

---

## 🔁 Backward Fill (`method='bfill'`)

```python
df.fillna(method='bfill')
```

> Fills missing values with the **next** non-null value.

---

## 🎯 Fill Specific Column

```python
df['A'].fillna(99, inplace=True)
```

> Fills NaNs in column `'A'` only.

---

## 🧠 Fill With Mean, Median, or Mode

```python
df['A'].fillna(df['A'].mean(), inplace=True)
df['B'].fillna(df['B'].median(), inplace=True)
```

> Dynamic replacement using column stats.

---

## 🧮 Fill Different Columns with Different Values

```python
df.fillna({'A': 100, 'B': 200})
```

> Uses dictionary mapping.

---

## 🎛️ Limit the Number of Fills

```python
df.fillna(method='ffill', limit=1)
```

> Only fills **1** NaN value per forward pass.

---

## 🔧 Fill by Row Instead of Column

```python
df.fillna(method='bfill', axis=1)
```

> Works **horizontally** across columns.

---

## 🧪 Fill from Another DataFrame

```python
other = pd.DataFrame({'A': [0, 0, 0, 0], 'B': [1, 1, 1, 1]})
df.fillna(other)
```

> Replaces NaNs **positionally** from another DataFrame.

---

## 📉 Downcasting to Save Memory

```python
df.fillna(0, downcast='infer')
```

> Tries to reduce datatype memory usage.

---

## 🔍 Practical Example: Before & After

### Before:

```python
     A    B
0  1.0  NaN
1  NaN  2.0
2  3.0  3.0
3  4.0  NaN
```

### After:

```python
df.fillna(method='ffill')
```

```python
     A    B
0  1.0  NaN
1  1.0  2.0
2  3.0  3.0
3  4.0  3.0
```

---

## ⚠️ Common Mistakes

|Mistake|Fix|
|---|---|
|Using `inplace=True` without saving or checking|Double-check before in-place modifications|
|Expecting fill across rows when `axis=0`|Use `axis=1` to fill across columns|
|Using `value` and `method` together|They are **mutually exclusive**|

---

## 🚀 When to Use `fillna()`

- Cleaning datasets with missing values
    
- Preparing data for machine learning models
    
- Avoiding errors in aggregate/statistical calculations
    

---

If you want a similar guide for `dropna()`, masking, interpolation, or replacing values — just say the word.
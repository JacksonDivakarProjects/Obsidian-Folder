Great question — `.fillna()` in Pandas is extremely versatile and knowing its parameters gives you full control over missing data handling.

---

## ✅ `fillna()` — Syntax

```python
df.fillna(value=None, method=None, axis=None, inplace=False, limit=None, downcast=None)
```

---

## 🧩 Key Parameters (with Examples)

### 1. **`value`** (most used)

Fill NA with specific value(s).

```python
df.fillna(0)  # fills all NaNs with 0

df.fillna({'age': 0, 'name': 'unknown'})  # column-wise filling
```

---

### 2. **`method`** (fill using other values)

|Method|Behavior|
|---|---|
|`'ffill'`|Forward fill: propagate last valid value down|
|`'bfill'`|Backward fill: use next valid value|

```python
df.fillna(method='ffill')  # forward fill
df.fillna(method='bfill', axis=0)  # backward fill
```

---

### 3. **`axis`**

Specify whether to fill row-wise or column-wise.

|Value|Meaning|
|---|---|
|`0` / `'index'`|Fill down columns (default)|
|`1` / `'columns'`|Fill across rows|

```python
df.fillna(method='ffill', axis=1)  # fill across columns (row-wise)
```

---

### 4. **`inplace`**

Do you want to modify the original DataFrame?

```python
df.fillna(0, inplace=True)
```

---

### 5. **`limit`**

Max number of consecutive NaNs to fill.

```python
df.fillna(method='ffill', limit=1)  # only fills 1 NaN per block
```

---

### 6. **`downcast`**

Try to downcast filled data types for optimization.

```python
df.fillna(0, downcast='integer')
```

---

## 🧠 Best Practices

- Use `value` for static replacements (`0`, `'unknown'`, etc.)
    
- Use `method='ffill'` or `'bfill'` when time series or sequential logic is needed.
    
- Combine `fillna()` with `isnull().sum()` to audit missing data handling.
    

---

Do you want this explained with a **real-world use case** like customer profiles or sales logs?
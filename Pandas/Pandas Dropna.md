Absolutely! Just like `fillna()`, you can also use `.dropna()` on a **particular column** — it's super useful when you only want to drop rows where a **specific column** is null, without affecting the entire DataFrame.

---

## ✅ `.dropna()` for a Particular Column

### 🔹 **Syntax:**

```python
df.dropna(subset=['column_name'])
```

---

## 🔧 Examples

### 1. **Drop rows where a particular column has NaN**

```python
df = df.dropna(subset=['age'])
```

➡️ Drops rows **only if `age` is NaN** — other nulls in other columns are kept.

---

### 2. **Multiple columns (like SQL `WHERE col1 IS NOT NULL AND col2 IS NOT NULL`)**

```python
df = df.dropna(subset=['age', 'salary'])
```

➡️ Drops rows if **either `age` or `salary`** is null.

---

### 3. **Inplace version**

```python
df.dropna(subset=['age'], inplace=True)
```

➡️ Directly modifies the original `df`.

---

## ⚠️ Notes

|Parameter|Purpose|
|---|---|
|`subset=['col']`|Limit drop to specific column(s)|
|`inplace=True`|Apply changes directly|
|`how`|Only used when `subset` is not passed — checks if all or any columns are null|

---

## 🔄 Comparison with SQL

|SQL|Pandas|
|---|---|
|`WHERE age IS NOT NULL`|`df.dropna(subset=['age'])`|
|`WHERE age IS NOT NULL AND salary IS NOT NULL`|`df.dropna(subset=['age', 'salary'])`|

---

Let me know if you'd like `.dropna()` behavior by **group** or in **chained operations** (e.g., `df.groupby(...).dropna(...)`).
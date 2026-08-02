
**Pandas `.str` String Functions: A Comprehensive Guide**

---

### 🔹 Basic String Operations

|Function|Description|Example|
|---|---|---|
|`str.lower()`|Convert to lowercase|`"Alice" → "alice"`|
|`str.upper()`|Convert to uppercase|`"bob" → "BOB"`|
|`str.title()`|Title-case each word|`"jack smith" → "Jack Smith"`|
|`str.capitalize()`|Capitalize first letter only|`"hello world" → "Hello world"`|
|`str.strip()`|Remove leading/trailing whitespace|`" Alice " → "Alice"`|
|`str.rstrip()`|Remove trailing spaces|`"hello " → "hello"`|
|`str.lstrip()`|Remove leading spaces|`" hello" → "hello"`|
|`str.len()`|Length of string|`"David" → 5`|

---

### 🔹 Searching & Matching

|Function|Description|Example|
|---|---|---|
|`str.contains('x')`|Check if substring exists|`'email@gmail.com'.contains('@')`|
|`str.startswith('x')`|Check if string starts with x|`'Data'.startswith('D')`|
|`str.endswith('x')`|Check if string ends with x|`'file.csv'.endswith('.csv')`|
|`str.isnumeric()`|Check if string contains digits only|`'123'.isnumeric() → True`|
|`str.isalpha()`|Check if string contains letters only|`'abc'.isalpha() → True`|
|`str.isalnum()`|Check if string contains letters and digits|`'abc123'.isalnum() → True`|
|`str.isspace()`|Check if string is whitespace|`' '.isspace() → True`|

---

### 🔹 Replacing & Modifying

|Function|Description|Example|
|---|---|---|
|`str.replace('old', 'new')`|Replace substrings|`'Mr. Bob'.replace('Mr.', 'Dr.')`|
|`str.pad(width, side='left')`|Pad string with spaces|`'4'.pad(3, 'left') → " 4"`|
|`str.zfill(width)`|Pad with leading zeros|`'7'.zfill(3) → "007"`|
|`str.repeat(n)`|Repeat string n times|`'ha'.repeat(3) → 'hahaha'`|

---

### 🔹 Splitting & Joining

|Function|Description|Example|
|---|---|---|
|`str.split(' ')`|Split by delimiter|`'John Doe'.split(' ')` → `['John', 'Doe']`|
|`str.split(' ', expand=True)`|Split into DataFrame columns|`df['name'].str.split(' ', expand=True)`|
|`str.partition('x')`|Split into 3 parts (before, x, after)|`'a=b'.partition('=') → ('a', '=', 'b')`|
|`str.cat(sep='-', na_rep='')`|Concatenate strings with separator|`df['first'].str.cat(df['last'], sep=' ')`|

---

### 🔹 Regex-based Matching & Extraction

|Function|Description|Example|
|---|---|---|
|`str.extract(r'regex')`|Extract regex group as new column|`'Order123'.extract(r'(\d+)')` → `123`|
|`str.match(r'regex')`|Match entire string against regex|`'A123'.match(r'[A-Z]\d+')` → True|
|`str.contains(r'regex')`|Check if regex pattern exists|`'abc123'.contains(r'\d+')` → True|
|`str.findall(r'regex')`|Return all matches in string|`'abc123xy9'.findall(r'\d')` → ['1','2','3','9']|

---

### 🔹 Handling Missing Values & Validation

|Function|Description|
|---|---|
|`str.isna()`|Check for missing values|
|`str.fillna('')`|Replace NaN with empty string|
|`str.replace(np.nan, '')`|Replace NaN using NumPy|

---

### 🔹 Real-world Use Case Example:

```python
import pandas as pd

df = pd.DataFrame({
    'email': ['jack@example.com', 'alice@gmail.com', 'bob@yahoo.com']
})

# Extract domain
df['domain'] = df['email'].str.split('@').str[1]

# Get username
df['username'] = df['email'].str.extract(r'(\w+)')
```

**Output:**

```
              email           domain   username
0  jack@example.com   example.com      jack
1  alice@gmail.com     gmail.com      alice
2    bob@yahoo.com     yahoo.com      bob
```

---

This guide is your one-stop reference for working with text data in Pandas. Let me know if you'd like to expand it with NLP techniques or complex pattern extractions!

## 🔗 Related Notes
- [[Data Science/Pandas/Pandas Accessors|📚 Pandas Accessors – Practical Guide with Outputs]]
- [[Data Science/Pandas/Pandas Special Notes For Tips and Tricks|Pandas Special Notes For Tips and Tricks]]
- [[Data Science/Pandas/Pandas Join|Pandas Join]]

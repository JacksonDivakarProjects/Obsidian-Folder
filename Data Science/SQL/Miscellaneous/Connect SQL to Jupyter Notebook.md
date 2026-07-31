Perfect — got it, Jack. You specifically want to **use `%%sql` magic commands in Jupyter Notebook**, and then **display query results using PrettyTable**.

Let’s build this **end-to-end setup** — connecting **MySQL → Jupyter via `ipython-sql` magic → PrettyTable output formatting.**

---

## ⚙️ Step-by-Step Guide: Connect MySQL to Jupyter Notebook using `%%sql` Magic + PrettyTable

---

### **1️⃣ Install all necessary packages**

Run this in a notebook cell:

```bash
!pip install ipython-sql pymysql prettytable==3.9.0
```

> We pin `prettytable==3.9.0` because newer versions break compatibility with `ipython-sql`.

---

### **2️⃣ Load the SQL extension**

```python
%load_ext sql
```

This enables you to use the `%%sql` magic commands.

---

### **3️⃣ Connect to MySQL**

Use the correct connection string format:

```python
%sql mysql+pymysql://username:password@localhost:3306/practice_db
```

Example:

```python
%sql mysql+pymysql://root:MyPass123@localhost:3306/practice_db
```

✅ **Tip:**

- `mysql+pymysql://` → Tells `ipython-sql` to use the PyMySQL driver.
    
- Change `practice_db` to your actual DB name.
    

---

### **4️⃣ Run SQL Queries using magic**

Now you can run SQL queries directly inside notebook cells:

```sql
%%sql
SHOW TABLES;
```

or

```sql
%%sql
SELECT * FROM employees LIMIT 5;
```

You’ll see the output rendered automatically as a nice table (using PrettyTable internally).

---

### **5️⃣ Store results in a variable (for custom PrettyTable display)**

If you want to format the results yourself:

```python
result = %sql SELECT * FROM employees LIMIT 5;
```

Convert to a Pandas DataFrame:

```python
df = result.DataFrame()
df.head()
```

Or render manually with PrettyTable:

```python
from prettytable import PrettyTable

table = PrettyTable()
table.field_names = df.columns

for row in df.itertuples(index=False):
    table.add_row(row)

print(table)
```

---

### **6️⃣ Common connection issues**

|Error|Cause|Fix|
|---|---|---|
|`Unknown database`|Database doesn’t exist|`CREATE DATABASE practice_db;`|
|`KeyError: 'DEFAULT'`|PrettyTable version issue|Use `prettytable==3.9.0`|
|`ModuleNotFoundError: No module named 'pymysql'`|Driver missing|`pip install pymysql`|

---

### ✅ **Working Notebook Template**

```python
# --- Setup ---
!pip install -q ipython-sql pymysql prettytable==3.9.0

# --- Load extension ---
%load_ext sql

# --- Connect to MySQL ---
%sql mysql+pymysql://root:MyPass123@localhost:3306/practice_db

# --- Run SQL query ---
%%sql
SELECT * FROM employees LIMIT 5;

# --- Store and pretty-print ---
result = %sql SELECT * FROM employees LIMIT 5;
df = result.DataFrame()

from prettytable import PrettyTable
t = PrettyTable(df.columns)
for row in df.itertuples(index=False):
    t.add_row(row)
print(t)
```

---

Would you like me to add **a reusable `query()` function** that automatically executes a SQL query (via magic) and prints it in a PrettyTable format — no manual conversion needed? It makes notebooks much cleaner.
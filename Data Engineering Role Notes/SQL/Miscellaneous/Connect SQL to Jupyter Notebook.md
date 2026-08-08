# Connect SQL to Jupyter Notebook (`%%sql` magic + PrettyTable)

End-to-end setup for querying MySQL from a Jupyter notebook using `ipython-sql` magic commands, with results optionally rendered through PrettyTable.

## 1. Install the required packages

```bash
!pip install ipython-sql pymysql prettytable==3.9.0
```

`prettytable` is pinned to `3.9.0` because newer major versions changed their API in ways that break `ipython-sql`'s internal formatting.

## 2. Load the SQL extension

```python
%load_ext sql
```

This enables the `%sql` (line) and `%%sql` (cell) magic commands.

## 3. Connect to MySQL

```python
%sql mysql+pymysql://username:password@localhost:3306/practice_db
```

Example:

```python
%sql mysql+pymysql://root:MyPass123@localhost:3306/practice_db
```

- `mysql+pymysql://` tells `ipython-sql`/SQLAlchemy to use the PyMySQL driver.
- Replace `practice_db` with your actual database name.

## 4. Run queries with the magic

```sql
%%sql
SHOW TABLES;
```

```sql
%%sql
SELECT * FROM employees LIMIT 5;
```

The output renders automatically as a table (via PrettyTable under the hood).

## 5. Capture results for custom formatting

```python
result = %sql SELECT * FROM employees LIMIT 5;
```

Convert to a pandas DataFrame:

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

## 6. Common connection issues

| Error | Cause | Fix |
|---|---|---|
| `Unknown database` | Database doesn't exist yet | `CREATE DATABASE practice_db;` |
| `KeyError: 'DEFAULT'` | Incompatible PrettyTable version | Use `prettytable==3.9.0` |
| `ModuleNotFoundError: No module named 'pymysql'` | Driver not installed | `pip install pymysql` |

## Working Notebook Template

```python
# --- Setup ---
!pip install -q ipython-sql pymysql prettytable==3.9.0

# --- Load extension ---
%load_ext sql

# --- Connect to MySQL ---
%sql mysql+pymysql://root:MyPass123@localhost:3306/practice_db

# --- Run a query ---
%%sql
SELECT * FROM employees LIMIT 5;

# --- Capture and pretty-print ---
result = %sql SELECT * FROM employees LIMIT 5;
df = result.DataFrame()

from prettytable import PrettyTable
t = PrettyTable(df.columns)
for row in df.itertuples(index=False):
    t.add_row(row)
print(t)
```

A reusable helper worth keeping around, so you don't repeat the capture/format boilerplate per query:

```python
def query(sql_text):
    result = %sql {sql_text}
    df = result.DataFrame()
    t = PrettyTable(df.columns)
    for row in df.itertuples(index=False):
        t.add_row(row)
    print(t)
    return df
```


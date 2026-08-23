## Delta Live Tables (DLT) — AutoCDC (Change Data Capture)

## 1. Core Concept

A CDC stream contains **data columns plus metadata columns**. The `operation` column is not special syntax — it is an ordinary column in the source data, and DLT decides what to do with each row based on the *value* in that column.

Example incoming row:
```text
userId = 101
name = "Jack"
operation = "DELETE"
event_timestamp = "2024-01-01 10:00:00"
```

## 2. Architecture

```text
CDC Source Table (with an operation column)
        ↓
Streaming View
        ↓
Auto CDC Flow (interprets the operation column's values)
        ↓
Target Table (current/final state)
```

## 3. Complete Example

```python
dlt.create_auto_cdc_flow(
  target = "users_current",
  source = "users",
  keys = ["userId"],
  sequence_by = col("event_timestamp"),
  apply_as_deletes = expr("operation = 'DELETE'"),
  apply_as_truncates = expr("operation = 'TRUNCATE'"),
  except_column_list = ["operation", "event_timestamp"],
  stored_as_scd_type = 1
)
```

(`create_auto_cdc_flow` is the current API name; older documentation and existing pipelines may still use its earlier alias, `apply_changes`.)

## 4. What `operation` Actually Is

A column in the dataset holding values such as:
- `"INSERT"`
- `"UPDATE"`
- `"DELETE"`
- `"TRUNCATE"`

DLT does **not** infer meaning from these values automatically — you must tell it how to interpret them via `apply_as_deletes` and `apply_as_truncates`.

## 5. `apply_as_deletes`

```python
apply_as_deletes = expr("operation = 'DELETE'")
```

For each row, DLT evaluates the condition. If it's **true**, DLT performs a DELETE against the target table for that key; if **false**, the row is treated as a normal insert/update. This is a per-row condition, not an assignment — equivalent to:

```text
if row.operation == "DELETE":
    delete from target where key = row.key
```

Example: a row with `userId = 101, operation = "DELETE"` results in `DELETE FROM users_current WHERE userId = 101`.

## 6. `apply_as_truncates`

```python
apply_as_truncates = expr("operation = 'TRUNCATE'")
```

If the condition is true for a row, the **entire target table** is cleared — equivalent to:

```text
if row.operation == "TRUNCATE":
    truncate entire table
```

Example: a row with `operation = "TRUNCATE"` results in `TRUNCATE TABLE users_current`.

## 7. Why `expr()` Is Used

`expr("operation = 'DELETE'")` defines a boolean condition evaluated row by row. It's just a SQL expression string, so it adapts to any schema:

```python
expr("op_type = 'D'")
expr("event = 'REMOVE'")
expr("is_deleted = true")
```

## 8. Execution Order (Per Row)

```text
1. Check the TRUNCATE condition.
2. Check the DELETE condition.
3. Otherwise → UPSERT (insert or update).
```

## 9. Default UPSERT Behavior

If neither condition matches: a new key is **inserted**, an existing key is **updated** (overwritten) with the incoming row's values.

## 10. Role of `sequence_by`

```python
sequence_by = col("event_timestamp")
```

Orders events per key so the **latest** change wins, even if events arrive out of order. Example: for `userId = 1`, an UPDATE at 10:00 followed by a DELETE at 10:05 results in the row being deleted — the later event by `sequence_by` always takes precedence, regardless of arrival order.

## 11. Role of `keys`

```python
keys = ["userId"]
```

Identifies which row to update or delete — used as the join/merge condition against the target table.

## 12. Removing Metadata Columns

```python
except_column_list = ["operation", "event_timestamp"]
```

Drops the CDC metadata columns from the final table, keeping only the business columns.

## 13. Internal Execution Model

DLT compiles this logic into something equivalent to a MERGE statement:

```sql
MERGE INTO users_current t
USING users s
ON t.userId = s.userId

WHEN MATCHED AND s.operation = 'DELETE' THEN DELETE
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
```

(with row ordering per key resolved first using `sequence_by`).

## 14. What Happens If You Skip These

| Missing | Effect |
|---|---|
| `apply_as_deletes` | DELETE rows are treated as updates — nothing is ever removed from the target. |
| `apply_as_truncates` | TRUNCATE rows are ignored — the table is never cleared. |
| The `operation` column itself | No way to detect deletes/truncates at all — only upserts are possible. |

## 15. Mental Model

For every incoming row: **read the column values → evaluate the conditions → perform the matching action.**

| `operation` value | Action |
|---|---|
| `DELETE` | Delete the row |
| `TRUNCATE` | Clear the entire table |
| anything else | Upsert |

## 16. Key Insight

`expr("operation = 'DELETE'")` and `expr("operation = 'TRUNCATE'")` are not syntax rules — they define **how to interpret a column's value as a database operation**. Without that mapping, DLT has no way to know that a given row means "delete this" versus "update this."

## 17. Summary

A CDC pipeline is data plus meaning: the rows carry the data, and `apply_as_deletes` / `apply_as_truncates` supply the meaning. Without defining that meaning explicitly, DLT can only ever upsert.

## 🔗 Related Notes
- [[Delta Live Tables|Delta Live Tables (DLT) Comprehensive Guide]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Important TBLProperties/Change Data Feed|Delta Lake – Change Data Feed]]

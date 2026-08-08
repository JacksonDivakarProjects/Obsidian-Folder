# Delta Table Utility Guide

A quick-reference sheet for the core Delta table utility commands: metadata inspection, time travel, recovery, cleanup, and cloning.

## 1. DESCRIBE

**Purpose:** Basic metadata about a Delta table — columns, types, nullability.

```sql
DESCRIBE delta.`/path/to/table`;
```

**Example:**

```sql
DESCRIBE delta.`/data/sales`;
```

| Column | Type | Nullable |
|---|---|---|
| id | INT | YES |
| amount | DOUBLE | NO |

**Use case:** quick overview of table structure.

## 2. DESCRIBE EXTENDED / DESCRIBE DETAIL

**Purpose:** detailed metadata — storage location, format, partitioning, and table properties.

```sql
DESCRIBE EXTENDED delta.`/path/to/table`;
DESCRIBE DETAIL delta.`/path/to/table`;
```

**Example:**

```sql
DESCRIBE DETAIL delta.`/data/sales`;
```

Returns schema, table format, location, partition columns, file count, size, and reader/writer protocol versions.

## 3. RESTORE

**Purpose:** roll a Delta table back to a previous version or timestamp — useful for undoing accidental deletes, bad updates, or overwrites.

```sql
RESTORE TABLE delta.`/path/to/table` TO VERSION AS OF <version_number>;
-- OR
RESTORE TABLE delta.`/path/to/table` TO TIMESTAMP AS OF '<timestamp>';
```

**Example:**

```sql
RESTORE TABLE delta.`/data/sales` TO VERSION AS OF 5;
```

The table now reflects the state of version 5. `RESTORE` itself is logged as a new version — it doesn't erase history, it adds a commit that reverts the data.

## 4. Time Travel (`TIMESTAMP AS OF` / `VERSION AS OF`)

**Purpose:** query a Delta table as of a specific point in time, without restoring it.

```sql
SELECT * FROM delta.`/path/to/table` TIMESTAMP AS OF '<yyyy-MM-dd HH:mm:ss>';
SELECT * FROM delta.`/path/to/table` VERSION AS OF <version_number>;
```

**Example:**

```sql
SELECT * FROM delta.`/data/sales` TIMESTAMP AS OF '2025-10-01 12:00:00';
```

**Use case:** auditing, debugging, and read-only data recovery.

## 5. HISTORY

**Purpose:** shows the transaction history of a Delta table — every write, delete, update, merge, and schema change.

```sql
DESCRIBE HISTORY delta.`/path/to/table`;
```

Returns version, timestamp, user, operation (`WRITE`, `DELETE`, `UPDATE`, `MERGE`, ...), and operation parameters — useful for tracking how a table evolved.

## 6. VACUUM

**Purpose:** permanently deletes data files that are no longer referenced by the table's current version history, freeing storage space.

```sql
VACUUM delta.`/path/to/table` [RETAIN <hours> HOURS];
```

**Example:**

```sql
VACUUM delta.`/data/sales` RETAIN 168 HOURS; -- retain 7 days of history
```

**Notes:**

- Default retention is 7 days (168 hours).
- Avoid dropping retention below 7 days unless you're certain you won't need time travel or CDF over that window — vacuuming removes the physical files that old versions depend on, so time travel past the retention point will fail afterward.

**Use case:** storage cost control and cleanup of obsolete data files.

## 7. Cloning

**Purpose:** create a shallow or deep copy of a Delta table for testing, backups, or sandboxing.

```sql
-- Shallow clone (metadata only; data files are shared with the source)
CREATE TABLE new_table SHALLOW CLONE delta.`/path/to/source_table`;

-- Deep clone (copies both metadata and data files)
CREATE TABLE new_table DEEP CLONE delta.`/path/to/source_table`;
```

**Example:**

```sql
CREATE TABLE sales_test SHALLOW CLONE delta.`/data/sales`;
```

**Use case:**

- Test changes without touching production data.
- Quickly spin up copies for analytics or development.

## Summary

| Command | Purpose | Notes |
|---|---|---|
| DESCRIBE | View basic schema | Columns, types |
| DESCRIBE EXTENDED / DETAIL | Detailed metadata | Path, properties, partitions |
| RESTORE | Roll back to a version/timestamp | Logged as a new version; time-travel-based recovery |
| TIMESTAMP / VERSION AS OF | Query an old table state | Read-only audit/debug |
| HISTORY | Transaction history | Version, operation, user |
| VACUUM | Remove old, unreferenced files | Storage cleanup; breaks time travel past retention |
| CLONING | Copy a table (shallow/deep) | Testing/dev sandbox |

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Important TBLProperties/Table Utility Commands|Delta Lake Table Utility Commands]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Delta Lake Commands in Different APIs/Delta Lake Commands in SQL API|Delta Lake Object Commands (SQL API)]]

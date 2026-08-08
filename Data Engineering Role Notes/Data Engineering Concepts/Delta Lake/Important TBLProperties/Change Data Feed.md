# Delta Lake — Change Data Feed (CDF) in SQL

**Change Data Feed (CDF)** lets you track row-level changes (inserts, updates, deletes) on a Delta table over time, giving you an incremental view of what changed instead of forcing a full-table diff. This powers incremental ETL, replication, and auditing.

## Enabling Change Data Feed

At table creation:

```sql
CREATE TABLE sales (
    id INT,
    product STRING,
    quantity INT,
    price DECIMAL(10,2),
    updated_at TIMESTAMP
)
USING delta
TBLPROPERTIES (delta.enableChangeDataFeed = true);
```

On an existing table:

```sql
ALTER TABLE sales
SET TBLPROPERTIES (delta.enableChangeDataFeed = true);
```

> **Note:** CDF must be enabled before the changes happen — it cannot reconstruct change history retroactively for versions committed before it was turned on.

## Querying Changes

Get all changes from a specific version onward:

```sql
SELECT *
FROM table_changes('sales', 1); -- version 1 onward
```

`table_changes(table_name, starting_version[, ending_version])` returns a CDF view with a `_change_type` column, whose values are:

- `insert`
- `update_preimage` (row values before the update)
- `update_postimage` (row values after the update)
- `delete`

Filter to a specific change type:

```sql
SELECT *
FROM table_changes('sales', 1)
WHERE _change_type = 'update_postimage';
```

## Use Cases

- Incremental ETL pipelines
- Real-time analytics dashboards
- Data replication between systems
- Auditing and compliance

## Best Practices

- CDF relies on Delta's versioning, so retain enough historical versions/log entries for the lookback window you need.
- Combine with Z-Ordering or partitioning for better query performance when scanning change data.
- Use time travel carefully on large datasets — CDF is designed for incremental consumption, not repeated full scans.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Questions/How Versioning Works in Delta Lake|How Versioning Works in Delta Lake]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Delta Live Tables/AutoCDC API/AutoCDC in DLT|AutoCDC in DLT]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 05/Snapshots & Change Tracking|Snapshots & Change Tracking]]

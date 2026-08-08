# How Versioning Actually Works in Delta Lake

**Question:** Delta Lake claims to support versioning — but if the data files for a previous version are deleted or vacuumed, how does versioning still work?

## The Core Idea

Delta Lake's "versioning" does not mean it physically keeps every file forever. It means Delta tracks every version of the table's *state* in the transaction log (`_delta_log/`), so at any point you can reconstruct or query the exact view of the data as it existed at version *N* — **as long as the underlying files that version depends on still exist**.

> In short: Delta Lake versioning is *logical history reconstruction*, not automatically *infinite physical file retention*.

## How It Actually Works

Each commit in Delta Lake:

- Writes a JSON file like `0000000000000005.json` inside `_delta_log/`.
- Lists which data files were **added** and which were **removed** by that commit.
- Creates a new table version.

So the transaction log forms a chain:

```
v0 → v1 → v2 → v3 → … → vN
```

which defines the table's entire versioned history. Querying:

```python
spark.read.format("delta").option("versionAsOf", 3).load("/path/to/table")
```

makes Delta replay the log entries to figure out which files were active at version 3, then reads exactly those files.

## What If Old Files Are Deleted?

Versioning depends on the underlying data files for that version still being present. If old Parquet files have been physically deleted — typically by `VACUUM` — Delta can no longer fully reconstruct that older version, even though the log entry describing it still exists.

This is the distinction to keep straight:

| Concept | Description |
|---|---|
| **Logical versioning** | Every change is recorded in `_delta_log`. This metadata stays available unless the log itself is cleaned up. |
| **Physical versioning** | The actual Parquet files belonging to older versions — these exist only until `VACUUM` removes them. |

## The Role of VACUUM

By default, `VACUUM` removes files that are no longer referenced by the current table state and are older than the retention threshold (default 7 days / 168 hours):

```sql
VACUUM delta.`/path/to/table` RETAIN 168 HOURS;
```

After vacuuming:

- The `_delta_log` entries for older versions are still there.
- But the actual data files those versions relied on may be gone.
- So a `versionAsOf` read pointing at an older, vacuumed version fails, because the required data files are missing.

## Why We Still Call It "Versioning"

Because Delta guarantees versioning **as long as retention policies are honored**. Until `VACUUM` removes old files, you can reproduce, time-travel to, or restore any version — the transaction log itself is always fully versioned and atomic. Even after vacuuming, the metadata/lineage of what happened remains; only the ability to materialize the full old dataset is lost. It's an explicit trade-off between storage cost and reproducibility, tunable via the retention period.

## Summary

| Operation | What Happens | Can You Still Time Travel? |
|---|---|---|
| Normal write | New version created | Yes |
| Overwrite | Old files marked as removed in the log | Yes, until vacuumed |
| Vacuum (default 7-day retention) | Old, unreferenced files physically deleted | No — the physical data is gone |
| Log retained | History of operations kept regardless | Metadata-level only, once files are gone |

**Bottom line:** Delta Lake supports versioning through its transaction log, not permanent file retention. You can time travel or restore any version as long as the corresponding data files still exist — once `VACUUM` removes them, only the metadata history of what happened remains.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Durability in Delta Lake|Durability in Delta Lake]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Important TBLProperties/Table Utility Commands|Delta Lake Table Utility Commands]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Important TBLProperties/Change Data Feed|Delta Lake – Change Data Feed]]

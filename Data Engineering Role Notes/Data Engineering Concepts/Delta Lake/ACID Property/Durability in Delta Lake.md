# Durability in Delta Lake

**Durability** (the "D" in ACID) means that once a transaction is committed, its data survives — even if the system crashes immediately afterward. Delta Lake achieves this through persistent storage, an immutable transaction log, and append-only file semantics.

## 1. Persistent Storage Layer

Delta Lake doesn't hold table data in memory. All data is written as immutable Parquet files to durable storage:

- HDFS (on-prem)
- S3 / ADLS / GCS (cloud)
- DBFS (Databricks File System)
- Local disk (dev/testing)

These storage systems provide durability through replication and redundancy — if a node or disk fails, data is recovered from other copies.

## 2. Transaction Log Durability (`_delta_log`)

Each commit writes a JSON log entry (and periodically a Parquet checkpoint) under `_delta_log/`:

```
/mnt/delta/events/_delta_log/
├── 0000000000000000010.json
├── 0000000000000000011.json
└── 0000000000000000012.json
```

These logs record which Parquet files were added, which were removed, and the operation's metadata and schema. Once a commit log is successfully written, it becomes the single source of truth for the table's state — even if Spark crashes right after, that transaction is permanent and recoverable.

## 3. Write-Once, Immutable Parquet Files

Delta Lake is append-only at the file level: existing Parquet files are never modified in place. Updates and deletes write new Parquet files and mark the old ones as removed in the log. This avoids corruption from partial overwrites and keeps recovery possible even if compute fails mid-operation.

## 4. Checkpoints for Faster Recovery

Every N commits (default 10), Delta writes a checkpoint Parquet file summarizing the table's current state, e.g. `0000000000000000010.checkpoint.parquet`. On restart, Delta rebuilds the latest table version by combining the latest checkpoint with any later JSON logs — making recovery both fast and fault-tolerant.

## 5. Atomic File-System Guarantees

Durability leans on the same atomic-commit guarantee used for atomicity: a commit log file is either fully committed or not committed at all. There is no "half-commit" state to recover from.

## Summary

| Concept | Mechanism | Ensures |
|---|---|---|
| Data storage | Parquet files on durable storage | Data survives crashes |
| Metadata | `_delta_log` JSON + checkpoints | Commit history retained |
| File immutability | Append-only design | No corruption or partial updates |
| Atomic commit | Commits are all-or-nothing | No partial durability |
| Replication | Cloud/HDFS replication | Hardware fault tolerance |

Delta Lake achieves durability by storing both data and metadata on fault-tolerant, persistent storage, with immutable files and atomic commit logs. Once a transaction is committed, it is permanent — even if Spark or the cluster fails right after.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Atomicity in Delta Lake|Atomicity in Delta Lake]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Consistency in Delta Lake|Consistency in Delta Lake]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Questions/How Versioning Works in Delta Lake|How Versioning Works in Delta Lake]]

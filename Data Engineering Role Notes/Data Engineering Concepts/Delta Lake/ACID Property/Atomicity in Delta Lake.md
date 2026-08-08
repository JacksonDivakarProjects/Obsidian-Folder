# Atomicity in Delta Lake

**Atomicity** (the "A" in ACID) means a write operation either fully completes or leaves no trace at all — there is no such thing as a half-finished write landing in the table. Delta Lake enforces this through its transaction log (`_delta_log/`) and atomic file-system renames.

## How It Works

### 1. Transaction Log (`_delta_log`)

Every Delta table has a hidden `_delta_log/` folder. Each operation (write, merge, update, delete) produces a new JSON commit file:

```
_delta_log/
├── 00000000000000000010.json
├── 00000000000000000011.json
```

Each JSON file records exactly which Parquet data files were `add`ed and which were `remove`d by that operation. If a job fails before its commit JSON is written, the operation is simply discarded and the table's state is unchanged. That is atomicity in practice.

### 2. Atomic Commit Protocol

When a job writes data:

1. It first writes the new Parquet data files.
2. Once all data files are safely written, it atomically creates the next `_delta_log` JSON file (via a rename or a conditional "put-if-absent" write, depending on the storage backend) — e.g. `00000000000000000016.json`.
3. If that atomic operation doesn't succeed, the transaction is treated as if it never happened — no partial data ever becomes visible.

This relies on the underlying storage system's atomic rename / conditional-write guarantee (S3 with a commit coordinator, ADLS, HDFS, and DBFS all provide this).

### 3. Snapshot Reads Protect Readers

While a write is in progress, readers keep seeing the last committed version (e.g. version 15). The next version (16) only becomes visible once its log commit succeeds, so no reader ever sees a half-written table.

## Example Timeline

| Step | Operation | Table State |
|---|---|---|
| 1 | Job starts writing new data | Temporary Parquet files created |
| 2 | Job writes `_delta_log/...0016.json.tmp` | Not yet visible to readers |
| 3 | Commit of `_delta_log/...0016.json` succeeds | New version committed |
| 4 | Readers now see version 16 | Atomic transition complete |

## Atomicity's Place in ACID

| Property | Maintained by | How |
|---|---|---|
| Atomicity | Transaction log + atomic commit | All-or-nothing writes |
| Consistency | Schema validation + constraints | Checked before commit |
| Isolation | Snapshot reads + OCC | Versioned, conflict-checked access |
| Durability | Persistent storage + replication | Parquet + log survive after commit |

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Consistency in Delta Lake|Consistency in Delta Lake]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Isolation in Delta Lake|Isolation in Delta Lake]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Durability in Delta Lake|Durability in Delta Lake]]

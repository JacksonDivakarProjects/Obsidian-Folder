# What Is the Delta Store?

> Scope: this is a SQL Server / Azure Synapse columnstore-index concept. See [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Indexing/Difference Between Clustered Column Store and Non Clustered Column Store|Difference Between Clustered and Non-Clustered Columnstore Index]] for the broader context.

The **delta store** is a hidden, row-based (B-tree) staging area inside a Clustered Columnstore Index. It exists because compressed columnstore segments are read-only once written — you can't cheaply "tack on" a single new row to an already-compressed blob without rebuilding it. Think of the delta store as the waiting room for data that hasn't been compressed yet.

## 1. How It Works

When you `INSERT` into a table with a columnstore index, the engine handles it differently depending on the size of the insert:

- **Small inserts (< 102,400 rows):** go directly into the delta store, stored in ordinary row-based format so the insert stays fast.
- **Large inserts (≥ 102,400 rows):** bypass the delta store entirely and are compressed straight into new columnstore ("bulk load") segments.

## 2. Life Cycle: Delta → Compressed

1. **Open** — the delta rowgroup is actively accepting new rows.
2. **Closed** — once a delta rowgroup reaches the maximum size (1,048,576 rows), it's marked closed and stops accepting inserts.
3. **Compressed** — a background process called the **Tuple Mover** picks up closed rowgroups, compresses them into columnstore segments, and merges them into the main columnstore.

## 3. Why It's Necessary

Without a delta store, every single-row insert would either:
- **Fragment** the columnstore into many tiny, inefficient compressed segments, or
- **Lock** large chunks of data just to append one record, killing concurrency.

Buffering small inserts in a row-based staging area avoids both problems.

## 4. Impact on Queries

A `SELECT` against a columnstore-indexed table transparently reads from **both** places and merges the results:
1. The compressed columnstore segments (the bulk of the data).
2. The delta store (recent rows not yet compressed).

## Pro Tip

If queries against a columnstore table get slower over time, check for too many open/uncompressed delta rowgroups — a symptom of frequent small ("trickle") inserts. Force compression manually with:

```sql
ALTER INDEX MyColumnstoreIndex ON MyTable REORGANIZE;
```

To inspect exactly how many rows are sitting in the delta store, query `sys.dm_db_column_store_row_group_physical_stats`.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Indexing/Difference Between Clustered Column Store and Non Clustered Column Store|Difference Between Clustered and Non-Clustered Columnstore Index]]

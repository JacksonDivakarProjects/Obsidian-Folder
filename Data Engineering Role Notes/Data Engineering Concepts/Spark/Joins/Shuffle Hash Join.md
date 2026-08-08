# Shuffle Hash Join (SHJ)

## What It Is
Shuffle Hash Join is one of Spark's physical join strategies. It is used when both sides of a join are too large to broadcast, but each partition is small enough to build an in-memory hash table after shuffling.

## How It Works

### 1. Shuffle Step
- Both tables are shuffled across executors by the join key.
- This guarantees all rows sharing the same key land in the same partition.
- Spark can then safely hash-join within each partition independently.

### 2. Build and Probe Phase
Within each partition:
1. Spark picks the smaller side and builds a hash table keyed by the join column.
2. Spark probes that hash table with rows from the other side.

## Example: Handling Duplicate Keys

**Table A**

| id | value |
|----|-------|
| 1  | A1    |
| 1  | A2    |

**Table B**

| id | value |
|----|-------|
| 1  | B1    |
| 1  | B2    |

Steps during SHJ:

1. Spark builds a hash table from Table A: `key=1 -> [A1, A2]`.
2. Spark probes it with rows from Table B:
   - B1 matches key=1 -> emits `(A1, B1)`, `(A2, B1)`
   - B2 matches key=1 -> emits `(A1, B2)`, `(A2, B2)`
3. The result is the cross product for that key:
   ```
   (1, A1, B1)
   (1, A2, B1)
   (1, A1, B2)
   (1, A2, B2)
   ```

Duplicates aren't a problem because the hash table stores a **list of values per key**, not a single value.

## Why Spark Chooses SHJ
- Faster than Sort-Merge Join when the data isn't too large, since it skips sorting.
- Memory is the bottleneck: if one partition's hash table grows too big, Spark spills to disk or falls back to Sort-Merge Join.

## Key Takeaways
- All rows for a given key end up in the same partition after the shuffle.
- The hash table stores a list of values per key, so duplicates are handled naturally.
- Join output for a duplicate key is the cross product of both sides' values for that key.
- Skewed keys (e.g., one key with millions of rows) degrade performance badly — see [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Executer OOM with Salting|Executor OOM in Spark (with Salting)]] for mitigation.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Joins/Types Of Joins|Types Of Joins]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Executer OOM with Salting|Executor OOM in Spark (with Salting)]]

# Spark Join Strategies (Types of Joins)

Spark chooses between different physical join strategies depending on data size and cluster resources.

## 1. The Three Strategies
1. **Broadcast Hash Join (BHJ)** — used when one table is small.
2. **Shuffle Hash Join (SHJ)** — used when both tables are big but hashing is still cheaper than sorting.
3. **Sort-Merge Join (SMJ)** — the default when both tables are large.

## 2. Hash Join (Broadcast or Shuffle)
Spark builds a hash table on the join key from the smaller side, then probes it with records from the larger side.

### Broadcast Hash Join (BHJ)
- Used when one side is small enough — default threshold is **10 MB**, configurable via `spark.sql.autoBroadcastJoinThreshold`.
- The small table is broadcast to every executor, avoiding a shuffle entirely.
- Very fast because it skips the network shuffle.

### Shuffle Hash Join (SHJ)
- Used when both tables are large but a hash join is estimated to be cheaper than sort-merge.
- Both tables are shuffled by join key, then hash-joined per partition.
- Usually chosen when join keys are well-distributed (low skew) — see [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Joins/Shuffle Hash Join|Shuffle Hash Join]] for the mechanics.

## 3. Sort-Merge Join (SMJ)
Both sides are shuffled by join key and then sorted before merging.

- Default join strategy when both sides are large and broadcast isn't possible.
- Used when Spark can't do a hash join (e.g., memory limits or heavy skew).
- Scales well for large equality joins because sorting is more memory-predictable than hashing.

## 4. Rule of Thumb
| Scenario | Strategy |
|---|---|
| Small + large table | Broadcast Hash Join |
| Large + large table, fits in memory for hashing | Shuffle Hash Join |
| Large + large table, too big to hash | Sort-Merge Join |

## 5. Example

```python
df1.join(df2, "id")  # Spark decides the join strategy automatically

# Force/influence the strategy:
spark.conf.set("spark.sql.join.preferSortMergeJoin", "false")
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)  # disables broadcast join
```

Use `df1.join(df2, "id").explain()` to see which physical join Spark actually picked for a given query.

## Quick Notes
- **Broadcast Hash Join** — fastest, avoids shuffle, used when one side is small.
- **Shuffle Hash Join** — used for big-big joins when hashing is cheaper than sorting.
- **Sort-Merge Join** — default for large joins; robust but has sorting overhead.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Joins/Shuffle Hash Join|Shuffle Hash Join]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Miscellaneous/Job, Stages and Tasks|Spark Execution: Job, Stages and Tasks]]

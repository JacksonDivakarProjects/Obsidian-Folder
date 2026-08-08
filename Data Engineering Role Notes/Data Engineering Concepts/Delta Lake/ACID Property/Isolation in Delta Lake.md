# Isolation in Delta Lake

**Isolation** (the "I" in ACID) guarantees that concurrent transactions don't interfere with each other — each behaves as though it were running alone. Delta Lake achieves this through **snapshot isolation** for readers and **optimistic concurrency control (OCC)** for writers.

## 1. Snapshot Isolation — Read Consistency

Every read gets a consistent snapshot of the table pinned to a specific version. If you start reading version 25 and another job commits version 26 while you're still reading, you keep seeing version 25 until your read finishes.

You can pin this explicitly:

```python
df = spark.read.format("delta").option("versionAsOf", 25).load("/mnt/delta/events")
```

This gives repeatable reads and avoids dirty reads, the same guarantee relational databases provide with snapshot isolation.

## 2. Optimistic Concurrency Control — Write Isolation

When multiple writers target the same table, Delta uses OCC:

1. Each writer reads the table at version `X`.
2. It prepares its changes (insert/update/delete) without locking anything.
3. Before committing, Delta checks whether the table has advanced past `X`, and whether any of the same underlying data files were touched by another writer's commit.

If there is no conflict, the write commits as version `X+1`. If there is a conflict, the commit fails:

```
ConcurrentModificationException:
Conflicting files were modified since the transaction started.
```

This is Delta preventing a write-write conflict rather than silently corrupting data.

## 3. Readers and Writers Never Clash

- Readers always see a fully committed version.
- Writers work against their own snapshot and are validated only at commit time.
- A new version becomes visible only after it passes validation.

No reader ever sees uncommitted data, and no writer silently overwrites another writer's results.

## Example Timeline

| Time | Operation | Table Version | Effect |
|---|---|---|---|
| T1 | Job A starts reading version 10 | 10 | Snapshot fixed |
| T2 | Job B writes and commits new data | 11 | New version created |
| T3 | Job A still sees version 10 | 10 | Isolation preserved |
| T4 | Job A finishes its read | 10 | Consistent view maintained throughout |

## Summary

| Mechanism | Purpose | Ensures |
|---|---|---|
| Snapshot isolation | Each read is pinned to a fixed version | No dirty reads |
| Optimistic concurrency control | Detects conflicting concurrent writes | No lost updates |
| Transaction log validation | Commits are strictly ordered | Serializable-feeling isolation |

Delta Lake achieves isolation through snapshot reads for readers and optimistic concurrency control for writers — giving ACID-level isolation even across a distributed, large-scale data lake.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Atomicity in Delta Lake|Atomicity in Delta Lake]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Consistency in Delta Lake|Consistency in Delta Lake]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Durability in Delta Lake|Durability in Delta Lake]]

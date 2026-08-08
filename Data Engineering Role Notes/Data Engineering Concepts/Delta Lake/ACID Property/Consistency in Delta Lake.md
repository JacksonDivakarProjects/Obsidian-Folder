# Consistency in Delta Lake

**Consistency** (the "C" in ACID) guarantees that every transaction moves the table from one valid state to another — no corrupted data, no broken schema, no partially-applied writes. Delta Lake enforces this through schema enforcement, transaction validation, and optimistic concurrency control (OCC).

## 1. Schema Enforcement (Write-Time Consistency)

Before any write, Delta Lake validates that the incoming DataFrame's schema matches the table's schema. On a mismatch it either throws an error or, if explicitly allowed, evolves the schema.

```python
df.write.format("delta").mode("append").save("/mnt/data/events")
```

If `df` has a column that isn't in the table's schema, this fails with something like:

```
A schema mismatch detected: new column 'source' not found in existing schema.
```

To allow controlled evolution instead of failing:

```python
df.write.option("mergeSchema", "true").format("delta").mode("append").save("/mnt/data/events")
```

This keeps the table consistent — it is never left in a half-valid state.

## 2. Transaction Validation via Optimistic Concurrency Control (OCC)

For operations like `MERGE`, `UPDATE`, or `DELETE`, Delta checks whether any other transaction modified the same data files since this job started reading. If so, the commit fails:

```
ConcurrentModificationException: Files were modified since the transaction started.
```

Each writer assumes it is safe to proceed, but Delta validates before allowing the commit to land — that's the "optimistic" part of OCC.

## 3. Commit Protocol

| Step | Validation | Result |
|---|---|---|
| 1 | Check schema | Pass / fail |
| 2 | Check file conflicts (OCC) | Pass / fail |
| 3 | Write new `_delta_log` entry | Success = consistent state |
| 4 | Commit | Visible as new version |

If any step fails, the transaction rolls back automatically — nothing partial is ever committed.

## 4. Read Consistency (Snapshot Isolation)

Readers always see a stable snapshot (e.g. version 25) even while version 26 is being written concurrently. No reader ever sees a half-updated table.

## Summary

| Consistency Aspect | Mechanism | Example |
|---|---|---|
| Schema consistency | Schema enforcement + evolution | Prevents invalid data types from landing |
| Data consistency | OCC validation | Avoids overlapping/conflicting writes |
| Read consistency | Snapshot isolation | Stable view during concurrent writes |
| Metadata consistency | Atomic log commits | `_delta_log` is always in a valid state |

Delta Lake enforces consistency at both the schema level and the transaction level: every commit is validated, atomic, and versioned, so the table never lands in an invalid state.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Atomicity in Delta Lake|Atomicity in Delta Lake]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Isolation in Delta Lake|Isolation in Delta Lake]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Durability in Delta Lake|Durability in Delta Lake]]

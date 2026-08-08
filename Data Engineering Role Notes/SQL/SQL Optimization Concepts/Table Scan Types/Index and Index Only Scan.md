# Index Scan vs. Index-Only Scan

Two core index-based scan strategies for reading rows off disk.

## Index Scan

The engine uses an index to filter rows, but still fetches the matching rows from the main table (heap) whenever the query needs columns that aren't stored in the index.

**How it works:**
1. **Scan the index** — walk it to find matching row pointers based on the `WHERE` clause.
2. **Heap lookup** — for every index match, fetch the corresponding row from the table to get any columns not present in the index.

**Use case:** the query's predicate columns are indexed, but it also selects other columns.

**Pros:** far better than a full table scan when the indexed predicate is selective — it dramatically narrows down which rows need fetching.

**Cons:** if a large number of rows match, the resulting heap lookups are effectively random I/O and can add up; the engine still touches the table for every missing column.

## Index-Only Scan

An optimized variant where every column the query needs is already present in the index (a "covering index"), so the query can be answered entirely from the index — no table access at all.

**How it works:**
1. **Scan the index**, applying filters and reading the needed columns straight from the index entries.
2. **Visibility check** — in an MVCC database like PostgreSQL, the engine still has to confirm each row is visible to the current transaction. It does this cheaply via the visibility map rather than reading the heap row, as long as the relevant page is marked all-visible (i.e., no ongoing transaction could see the page in an inconsistent state — usually true for accordingly-vacuumed data).

**Use case:** the query only references columns included in the index — common in reporting/analytics queries that repeatedly touch the same narrow column set.

**Pros:** much faster reads (no heap access at all when it applies) and lower I/O overhead.

**Cons:** requires a covering index, which is larger and costs more to maintain on every `INSERT`/`UPDATE`.

## Key Differences

| Feature | Index Scan | Index-Only Scan |
|---|---|---|
| Table lookup | Yes, for missing columns | No — all data comes from the index |
| Performance | More I/O if selecting non-indexed columns | Faster — less I/O when the index covers everything needed |
| Use case | Not all required columns are indexed | All required columns are in the index |
| Index size | Smaller | Larger (must cover every needed column) |
| Ideal for | Queries needing extra columns from the table | Read-heavy reporting/analytics workloads |

## When to Optimize for Index-Only Scans

- The same set of columns gets fetched repeatedly.
- Read performance is the priority (analytics/reporting).
- You're willing to accept a bit more write overhead in exchange for faster reads.

**Best practice:** for hot read queries, build a covering index that includes every `SELECT`ed and `WHERE`d column.

## Example

Table `users(id, name, age, email)`, with an index on `(age, name)`:

**Index Scan (not covering):**
```sql
SELECT name, email FROM users WHERE age = 30;
```
The index locates rows with `age = 30`, but since `email` isn't in the index, every match still requires a heap lookup.

**Index-Only Scan (covering):**
With an index on `(age, name, email)` instead:
```sql
SELECT name, email FROM users WHERE age = 30;
```
Now every needed column is in the index — no table lookup required.

## Summary

| Scan type | What happens | When it's used |
|---|---|---|
| Index Scan | Scan the index, then fetch missing columns from the table | Query needs columns not in the index |
| Index-Only Scan | All needed data is already in the index | Query needs only columns present in the index |

## Key Takeaways

- Index Scan filters efficiently but still needs a heap lookup for any missing column.
- Index-Only Scan skips the heap entirely — but only when a covering index exists.
- Look at your frequent, performance-sensitive queries and consider covering indexes for the ones that matter most.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Table Scan Types/Differences among Scans/Difference between Index and Index Only Scan|Difference between Index and Index Only Scan]]

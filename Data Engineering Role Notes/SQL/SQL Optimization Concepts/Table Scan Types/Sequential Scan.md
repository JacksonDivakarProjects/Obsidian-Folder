# Sequential Scan

## What Is a Sequential Scan?

A sequential scan (also called a full table scan) is the simplest way to read data: the engine reads every page and every row of the table, one after another, checking each row against the query's conditions.

## How It Works

- **Reads the table in order** — starts at the beginning and processes every row in turn, ignoring any indexes.
- **Checks row validity** — for each row, evaluates the `WHERE` clause.
- **Discards or outputs** — matching rows go to the result set; the rest are skipped.

## When It's Used

- **No usable index** on the columns involved in the query — the planner falls back to it.
- **Small tables** — scanning the whole table can beat an index lookup because indexes carry their own overhead (extra I/O to read the index itself, then the heap).
- **Large result sets** — if the query needs a large fraction of the table's rows anyway, sequentially reading everything can be cheaper than hopping between index and heap for each match.
- **`SELECT *` or wide column needs** — even with indexes present, the planner may prefer a sequential scan if the query needs most columns/rows regardless.

## Performance Characteristics

- **Efficient for bulk reads** — sequential disk access minimizes random I/O and can be very fast for reading entire tables or large subsets.
- **Slow for small result sets** — if only a handful of rows are needed, examining every row is wasteful compared to an index scan.
- **Buffering and parallelism** — PostgreSQL can synchronize sequential scans across concurrent sessions reading the same table (sharing buffer reads), and can split a large sequential scan across multiple parallel worker processes.

## Typical Plan Output

Shows up in `EXPLAIN` as `Seq Scan on tablename`.

## Example Use Cases

- Reporting queries that need most/all of a table's data.
- Tables with no indexes, or after an index has been dropped.
- Debugging/testing with indexes intentionally disabled.

## Avoiding Unwanted Sequential Scans

- **Add indexes** on columns frequently used in `WHERE` or join conditions.
- **Make queries more selective** so the planner has a reason to prefer an index.
- **Check `EXPLAIN`** to confirm whether a given query is actually triggering one.

## Summary

| Situation | Sequential scan likely? |
|---|---|
| No indexes on relevant columns | Yes |
| Query returns most/all rows | Yes |
| Query is highly selective | No — index scan preferred |
| Table is very small | Yes — often faster than indexing overhead |
| Index doesn't cover all needed columns | Sometimes, if the query needs the extra columns anyway |

## Key Takeaways

- A sequential scan examines every row and is always available as a fallback, but isn't always the wrong choice.
- It can be surprisingly efficient for small tables or queries that need most of a table's data.
- For selective queries against large tables, an index (or index-only) scan usually wins.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Table Scan Types/Bitmap Scan/Bitmap Heap Scan|Comprehensive Guide: Bitmap Heap Scan in PostgreSQL]]
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Table Scan Types/Index and Index Only Scan|Comprehensive Guide: Index Scan vs Index-Only Scan in SQL]]

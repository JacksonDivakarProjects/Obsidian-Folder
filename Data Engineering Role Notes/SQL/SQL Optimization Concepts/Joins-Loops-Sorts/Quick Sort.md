# Quick Sort in SQL Engines

## What Is Quick Sort in SQL?

Quick sort isn't something you write or invoke directly in a SQL query. Database engines (SQL Server, MySQL, PostgreSQL, etc.) use it internally for in-memory sorting — for operations like `ORDER BY`, sorting data during index creation, or small-to-medium result sets that fit within the memory allotted to the query.

## How SQL Engines Use It

- **In-memory sort:** when the data to be sorted fits within available memory, the engine may pick quicksort for its speed.
- **Spill to disk:** if the sort would exceed the allotted memory, the engine falls back to an external, disk-based algorithm (typically an external merge sort) instead.

## Typical Sorting Flow (e.g., SQL Server)

1. Sorting starts in memory with quicksort as long as the memory grant is sufficient (SQL Server generally wants roughly 2x the input's row-count worth of memory available).
2. If the sort would grow beyond the granted memory, the engine abandons the in-memory approach mid-operation and completes the sort on disk using merge sort instead.

## Quick Sort Basics (the Underlying Algorithm)

- **Divide and conquer:** pick a pivot, partition the data so smaller values go left and larger values go right of the pivot, then recursively sort each partition.
- **In-place:** it sorts with minimal extra memory, which is exactly why it's attractive for in-memory work inside a database engine.

## What You Actually Control

- You never specify "use quicksort" in SQL. You write `ORDER BY ...` or `CREATE INDEX ...` as usual, and the query planner picks whichever algorithm it judges optimal given data size, available indexes, and memory.
- To observe *which* sort strategy actually ran (including whether it spilled to disk), use the engine's execution-plan tooling — e.g., SQL Server's actual execution plan (look for "Sort Warnings"), or `EXPLAIN (ANALYZE, BUFFERS)` in PostgreSQL, or `EXPLAIN` in MySQL.

## Best Use Cases

Fast sorting of moderate datasets (`ORDER BY`, index builds) that fit entirely in memory.

## When Data Exceeds Memory

The engine transparently switches to merge sort or another disk-based sort — slower, but able to handle arbitrarily large data by processing it in chunks.

## Summary

| Scenario | Algorithm typically used |
|---|---|
| Data fits in memory | Quicksort |
| Small result with a `LIMIT`/top-N | Heap sort (some engines, e.g. MySQL) |
| Data too large for memory (spills to disk) | External merge sort |
| An existing index already provides the order | No sort needed |

## Key Points

- Quicksort is one of several sorting algorithms engines use internally.
- It's picked automatically by the optimizer for in-memory sorts — there's no SQL syntax to request it.
- For large, disk-based sorts, the engine automatically switches to merge sort or a similar external algorithm.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Heap Sort|Comprehensive Guide to Heap Sort in SQL]]

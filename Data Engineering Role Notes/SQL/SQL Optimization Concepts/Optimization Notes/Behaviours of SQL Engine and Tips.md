# The SQL Engine: A Behavior Guide

A practical mental model for how SQL actually executes queries — architecture, optimizer decisions, indexing, joins, sorting, aggregation, and why queries end up slow.

## 1. SQL Engine Architecture (High Level)

Every SQL engine has three major layers:

1. **Parser** — validates syntax and builds an internal representation of the query.
2. **Optimizer** (the brain) — decides how the query should run: chooses join types, chooses indexes, applies rewrites, estimates costs (I/O, CPU, memory).
3. **Executor** (the worker) — runs the chosen plan: scans, joins, sorts, groups.

## 2. How the Optimizer Makes Decisions

The optimizer is cost-based. It estimates:

- Row counts (cardinality)
- Predicate selectivity
- Cost of using an index vs. scanning
- Cost of sorting vs. hashing
- Available memory
- Opportunities for parallelism

Based on these estimates it picks a join strategy, a scan method, sort-vs-hash-vs-index for grouping, and may rewrite parts of the query. SQL is declarative, not procedural — the engine decides the execution path; you only describe the result you want.

## 3. Index Behavior

**How indexes get used:**
- **Index seek** — fast, highly selective lookup.
- **Index range scan** — for inequalities and ranges.
- **Index scan** — reads the whole index when the predicate isn't selective enough to seek.
- **Bitmap index scan** (PostgreSQL) — combines results from multiple indexes efficiently.

**What breaks index usage:**
- Arithmetic on the indexed column: `WHERE salary * 2 > 10000`
- Functions wrapped around the column: `WHERE LOWER(name) = 'a'`
- Any expression the index doesn't natively support — fixed by a **functional (expression) index** built on that exact expression.

**Predicate rewriting.** When mathematically safe, the optimizer can rewrite a predicate to restore index usability, e.g. `salary * 2 > 10000` → `salary > 5000`. This isn't guaranteed for every expression, so don't rely on it — write the sargable (index-friendly) form yourself where it matters.

## 4. How SQL Selects Rows via an Index

1. Navigate the B-tree from root to the target leaf page.
2. Locate the specific key.
3. Retrieve the row pointers (row IDs / TIDs) stored at that key.
4. Fetch the actual rows from the table using those pointers.
5. Apply any remaining filters that the index couldn't satisfy directly.

Indexes return row *pointers*, not the row data itself (unless it's a covering/index-only scan). Bitmap scans convert those pointers into an in-memory bitmap so multiple index results can be combined efficiently before touching the table.

## 5. Join Strategies

**Nested Loop Join (NLJ)** — best when the outer table is small, an index exists on the inner table's join column, and filters are highly selective. For each outer row, look up matches in the inner table via the index.

**Hash Join (HJ)** — best for large tables with no useful index, on equality joins (`A.id = B.id`). Build a hash table on the smaller input, probe it with the larger. Avoids sorting, but needs memory.

**Sort-Merge Join (SMJ)** — best for large datasets that are already sorted (via an index or a prior step), or where join keys have many duplicates. Sort both inputs on the join key, then merge them in one sequential pass. When a sort is required, it's typically an **external merge sort** (disk-friendly for inputs too big for memory).

## 6. Sorting Behavior — Why Merge Sort Wins for Large Data

Sorting is used by `ORDER BY`, `GROUP BY`, `DISTINCT`, window functions (`OVER`), and sort-merge join.

External merge sort is the default for large sorts because it:
- Works for datasets that don't fit in memory.
- Relies on sequential I/O, which is efficient on disk.
- Supports multi-pass merging.
- Produces stable, predictable performance.

Quicksort is not used for large, disk-spilling operations because it doesn't help once data is out-of-memory, has poor random-disk-access characteristics, and (as commonly implemented) isn't stable. Engines do still use quicksort/heapsort internally for **in-memory** sorts — see [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Quick Sort|Quick Sort in SQL Engines]].

## 7. Aggregation Behavior

- **Hash aggregation** — groups rows via a hash table. Fast, but memory-heavy; best for large, unordered data.
- **Sort aggregation** — sorts by the group key first, then aggregates while scanning in sorted order. Used when the input is already sorted, or when memory is too limited for a hash table.

## 8. Window Function Behavior

Window operations need ordered data: ranking and running totals depend on `ORDER BY`, and grouping of the window depends on `PARTITION BY`. Sorting frequently happens under the hood to satisfy this.

Named windows:

```sql
SELECT *, SUM(amount) OVER w
FROM sales
WINDOW w AS (PARTITION BY region ORDER BY sale_date);
```

The `WINDOW` clause for naming a reusable window definition is supported in PostgreSQL, MySQL 8+, MariaDB, Snowflake, and SQLite — not in standard SQL Server T-SQL (which requires repeating the `OVER (...)` clause, or using a CTE, per window spec).

## 9. Predicate Push-Down

The optimizer pushes filters as close to the data source as possible:

```sql
-- As written:
SELECT * FROM (SELECT * FROM sales) t WHERE amount > 100;

-- Optimizer rewrites internally to:
SELECT * FROM sales WHERE amount > 100;
```

This cuts down rows processed, memory used, and any temporary/intermediate storage.

## 10. Execution Flow, Simplified

```sql
SELECT dept, SUM(salary)
FROM employees
WHERE age > 30
GROUP BY dept
ORDER BY dept;
```

1. Evaluate `WHERE age > 30` (pushed down as early as possible).
2. Use an index or a table scan, depending on the filter's selectivity.
3. Group the results (hash or sort aggregation).
4. Sort the final output for `ORDER BY`.
5. Return rows.

## 11. Common Optimizer Rewrites

- **Constant folding** — `WHERE 10 * 5 > salary` → `WHERE 50 > salary`.
- **Predicate simplification** — `(age > 10 AND age > 5)` → `age > 10`.
- **Join elimination** — dropping joins that provably don't affect the output (e.g., joining to a table whose columns aren't selected and whose join can't filter or duplicate rows).
- **Subquery flattening** — turning nested queries into equivalent joins.
- **Distinct elimination** — dropping a redundant `DISTINCT` when `GROUP BY` already guarantees uniqueness.

## 12. Memory and Disk Behavior

When memory runs short: sorts spill to disk, hash joins spill partitions to disk, and hash aggregations spill too. This is by design — it lets SQL operate correctly on datasets far larger than available RAM, just more slowly once it spills.

## 13. When Indexes Get Ignored

The optimizer skips an index when:
- Selectivity is low (e.g., `gender = 'M'` matches half the table).
- Using the index would cause more random I/O than a sequential table scan.
- A function or arithmetic expression wraps the indexed column.
- The comparison involves an implicit type conversion.
- Table statistics are stale, causing a bad cost estimate.

## 14. Why Queries Are Slow: Root Causes

Missing indexes, bad join order, no predicate push-down, sorting huge datasets, large hash tables spilling to disk, mismatched data types forcing casts, and stale statistics.

## 15. How to Think Like the SQL Engine

Before writing or tuning a query, ask:

1. How many rows am I working with?
2. How selective are my filters?
3. Will this force a sort?
4. Can an index avoid that sort?
5. Which join method will the optimizer likely pick?
6. Does any expression block index usage?
7. Is the data already ordered?
8. Could an aggregation spill to disk?

## Summary

The SQL engine is a cost-driven machine: it weighs row counts, index usefulness, sort/hash cost, join strategy, and available memory, then picks the plan it estimates is cheapest. Understanding these behaviors is what lets you write SQL the optimizer can actually optimize.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Optimization Notes/Common Pitfalls in Querying|Common Pitfalls in Querying]]
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Optimization Notes/Role in SQL|Role in SQL]]
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Optimization Notes/Working of Index in SQL|Working of Index in SQL]]

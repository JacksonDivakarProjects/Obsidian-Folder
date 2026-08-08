# PostgreSQL Optimization Guide

A structured path from spotting a slow query to fixing it correctly, focused on PostgreSQL.

## Part 1: Find the Problem — `EXPLAIN ANALYZE`

You can't fix what you can't see. `EXPLAIN ANALYZE` shows the actual plan Postgres uses for a query and how long each step really took (as opposed to plain `EXPLAIN`, which only estimates).

```sql
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 10;
```

Key skill: read `cost` (the planner's estimate) versus `actual time` (measured), and learn to spot the most common problem — an unwanted **Sequential Scan** on a large table.

## Part 2: The 90% Solution — Indexing

Once you spot a Sequential Scan where you expected an index, an index is almost always the fix.

- **Composite & covering indexes (Index-Only Scans).** An index-only scan is the goal state: Postgres answers the query entirely from the index without touching the table's heap. This requires a multi-column ("composite") index that covers every column the query needs.
- **Heap-based storage.** Unlike engines where the primary key defines physical row order, PostgreSQL tables are heaps — rows are stored in no particular guaranteed order, and every index (including the primary key's) is a secondary structure that points back into the heap via a row identifier (TID). This is why index design matters so much: there's no "free" clustering to lean on.

## Part 3: Fixing Anti-Patterns

Common query-writing habits that stop the optimizer from using an index that otherwise exists:

- **Functions wrapped around a column in `WHERE`** (e.g. `WHERE LOWER(name) = 'jack'`). A plain B-tree index on `name` can't be used here because the index stores raw values, not `LOWER(name)`. Fix: create an **expression index** — `CREATE INDEX ON table (LOWER(name));` — which indexes the function's *result*.
- **Leading-wildcard `LIKE`** (e.g. `WHERE email LIKE '%@gmail.com'`). A standard B-tree index can't be used for a pattern with a leading `%`. Fix: install the `pg_trgm` extension and build a GIN (or GiST) trigram index, which makes wildcard/substring search fast regardless of wildcard position.
- **Bad pagination via `OFFSET`.** `OFFSET 100000 LIMIT 20` forces Postgres to scan and discard 100,000 rows before returning any. Fix: **keyset (cursor) pagination** — filter on the last seen key (`WHERE id > :last_id ORDER BY id LIMIT 20`) instead of counting rows.
- **`IN` vs. `EXISTS` vs. `JOIN`.** These aren't universally interchangeable in performance — which one the optimizer handles best depends on selectivity, indexes, and whether duplicates matter. Don't assume; check `EXPLAIN ANALYZE` for your actual query and data.

## Part 4: Join Strategy

Once indexes are in place, the next bottleneck is how PostgreSQL joins tables. `EXPLAIN ANALYZE` will show which strategy it picked — **Nested Loop**, **Hash Join**, or **Merge Join** — and your indexes (or lack of them) directly influence that choice. See [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Joins-Loops-Sorts|Joins-Loops-Sorts]] for how each algorithm works and when the optimizer prefers it.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Optimization Notes/Working of Index in SQL|Working of Index in SQL]]
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Optimization Notes/Common Pitfalls in Querying|Common Pitfalls in Querying]]
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Joins-Loops-Sorts|Joins-Loops-Sorts]]

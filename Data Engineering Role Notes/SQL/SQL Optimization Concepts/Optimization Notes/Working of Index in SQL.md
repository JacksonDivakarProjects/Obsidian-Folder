# Working of Index in SQL

How the optimizer decides to use an index, and how index-backed row selection actually happens underneath.

## 1. How the Optimizer Decides to Use an Index

The optimizer is a cost-estimation engine. It evaluates:

1. **Selectivity** — how many rows will match this predicate? Higher selectivity (fewer matching rows) makes an index a better candidate.
2. **Available indexes** — does an index exist on the relevant column(s), and does the predicate's shape match the index structure?
3. **Predicate type** — `=` and range predicates (`>`, `<`, `BETWEEN`) are index-friendly; expressions (`col + 2`, `UPPER(name)`) or functions on the column are not, unless a matching functional/expression index exists.
4. **Physical table statistics** — row counts, page counts, value-distribution histograms, and density.
5. **Cost model** — estimated I/O, CPU, and memory cost, plus any benefit from parallelism.

The optimizer then picks whichever path it estimates is cheapest.

## 2. What's Actually Inside a B-Tree Index

A B-tree index stores sorted keys, each paired with a pointer to the row's physical location:

```
Key    RID (row pointer)
20     A15
22     B30
25     C02
27     D19
30     E44
```

Because the keys are sorted, the engine can binary-search the structure instead of scanning linearly — that's the entire source of an index's speed advantage.

## 3. How Rows Get Selected

**Case A — equality predicate:**
```sql
WHERE age = 25
```
1. Navigate the B-tree from root to leaf (O(log n)).
2. Find the leaf page containing key `25`.
3. Retrieve the row pointer(s) stored at that key.
4. Fetch the actual row(s) from the table (heap or clustered index) using those pointers.

This is an **index seek**.

**Case B — range predicate:**
```sql
WHERE age BETWEEN 20 AND 30
```
1. Seek to the first key, `20`.
2. Scan leaf pages sequentially up through key `30`.
3. Collect all row pointers along the way.
4. Fetch the corresponding rows.

This is an **index range scan**.

**Case C — non-indexable expression:**
```sql
WHERE age + 2 = 30
```
The index can't seek directly to `age = 28` unless a matching expression index exists:
```sql
CREATE INDEX idx_age_plus_2 ON employees ((age + 2));
```
Without one, the engine performs an **index scan** (reads every leaf page), computing `age + 2` for each row and applying the filter — the index only helps by providing a compact way to iterate all rows in this case, not by filtering.

## 4. Bitmap Index Scans (PostgreSQL)

When multiple indexes could each help with part of a compound filter:
```sql
WHERE age > 20 AND salary > 5000
```
PostgreSQL can:
1. Build a bitmap of row locations from the `age` index.
2. Build a second bitmap from the `salary` index.
3. `AND` the two bitmaps together.
4. Fetch only the rows present in the combined bitmap.

Bitmaps represent sets of row locations, not computed expressions — they're a way to combine multiple index results before touching the table even once.

## 5. The Optimizer's Core Decision Rule

**Will using the index retrieve fewer pages than a full table scan?**

- Yes → use an index seek, range scan, or bitmap scan.
- No → use a table scan.

## Summary

- The optimizer chooses an index based on cost, selectivity, and predicate shape.
- A B-tree index returns rows by seeking to, or scanning across, a range of sorted keys.
- Arithmetic or functions on the indexed column break a seek unless a matching functional index exists.
- Bitmap scans combine multiple index results via row-location bitmaps before fetching data.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Table Scan Types/Bitmap Scan/Bitmap Index Scan|Bitmap Index Scan]]
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Table Scan Types/Index and Index Only Scan|Comprehensive Guide: Index Scan vs Index-Only Scan in SQL]]

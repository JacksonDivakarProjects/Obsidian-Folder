# Bitmap Index Scan (PostgreSQL)

## What Is It?

A multi-step query execution technique that uses an index, but instead of fetching rows immediately, it produces a **bitmap** of qualifying row positions and fetches the actual rows in bulk afterward (via a Bitmap Heap Scan).

## How It Works

1. **Stage 1 — Bitmap creation.** The index is scanned to find every tuple ID (TID) satisfying the query condition. A match sets a `1` in the bitmap at that row's position; non-matches are `0`. The bitmap groups these by data page, not by individual row. If multiple conditions apply, multiple bitmaps get generated and combined with fast bitwise AND/OR.
2. **Stage 2 — Bitmap Heap Scan.** The combined bitmap is handed to the Bitmap Heap Scan node, which reads each flagged table page once and fetches every matching row from it — see [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Table Scan Types/Bitmap Scan/Bitmap Heap Scan|Bitmap Heap Scan]] for that half of the pipeline.

## When It's Used

- **Moderate result sets** — more rows than a plain index scan handles efficiently (too much random I/O per row), but not so many that a sequential scan wins.
- **Multi-condition queries** — combining several indexes via AND/OR logic.
- **Bulk efficiency** — when minimizing random reads and pulling many rows per page read is worth the extra bitmap-building step.

## Example

Table `orders` with indexes on `customer_id` and `order_date`:

```sql
SELECT * FROM orders WHERE customer_id = 100 AND order_date > '2023-01-01';
```

```
Bitmap Heap Scan on orders
  -> BitmapAnd
       -> Bitmap Index Scan on idx_customer_id
            Index Cond: (customer_id = 100)
       -> Bitmap Index Scan on idx_order_date
            Index Cond: (order_date > '2023-01-01')
```

Each `Bitmap Index Scan` produces its own bitmap; `BitmapAnd` combines them; the `Bitmap Heap Scan` fetches rows page-by-page only where the combined bitmap marks a match.

## Optimization and Limitations

- Highly effective for bulk reads and combining multiple indexes.
- Not ideal for very selective queries (a plain index scan is simpler and just as fast there) or for queries returning most of the table (a sequential scan wins there instead).
- Needs enough memory to hold the bitmap; if it doesn't fit, PostgreSQL falls back to a lossy bitmap, which requires extra per-row rechecking at the heap-scan stage.
- Row order isn't preserved by a bitmap scan, so a query with `ORDER BY` will still need an explicit sort afterward.

## Key Benefits

- Minimizes disk I/O via page-level bulk fetching instead of one random access per matching row.
- Efficient way to combine AND/OR conditions across multiple single-column indexes.
- Bitwise operations make the combination step itself very cheap.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Table Scan Types/Bitmap Scan/Bitmap Heap Scan|Comprehensive Guide: Bitmap Heap Scan in PostgreSQL]]
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Table Scan Types/Bitmap Scan/Explained with Analogy|Explained with Analogy]]

# Bitmap Heap Scan (PostgreSQL)

## What Is a Bitmap Heap Scan?

A step in query execution — usually following one or more Bitmap Index Scans — where PostgreSQL retrieves actual table rows based on a bitmap of qualifying row locations. It fetches only the table pages that actually contain matches, which significantly cuts disk I/O when a query needs many rows, but not most of them.

## How It Works

1. **Bitmap creation.** One or more Bitmap Index Scan nodes (optionally combined via `BitmapAnd`/`BitmapOr`) produce a bitmap — a compact map of matching row locations (TIDs) grouped by table page.
2. **Bitmap combination.** If multiple indexes contributed, their bitmaps are combined with fast bitwise AND/OR — this is how a compound `WHERE a = x AND b = y` can use two single-column indexes together.
3. **Heap scan.** The Bitmap Heap Scan reads only the pages the bitmap marks as containing a match, fetching each such page exactly once and pulling every qualifying row from it in a single pass.
4. **Recheck condition.** If memory is tight, the bitmap can become *lossy* — tracking only which *pages* have a match, not which exact rows. In that case every row on a marked page is rechecked against the condition (`Recheck Cond` in the plan) to confirm it actually qualifies. An *exact* bitmap (row-level, not just page-level) needs no recheck.

## Example

```sql
SELECT * FROM person WHERE age = 20;
```

```
Bitmap Heap Scan on person
  Recheck Cond: (age = 20)
  -> Bitmap Index Scan on idx_person_age
       Index Cond: (age = 20)
```

The `Bitmap Index Scan` finds all rows where `age = 20` and builds a bitmap of their locations; the `Bitmap Heap Scan` then fetches only the necessary pages, collecting matches and rechecking only if the bitmap turned out lossy.

## When It's Used

- **Medium-sized result sets** — too many rows for a plain index scan to be cheap (too much random I/O), but too few to justify a full sequential scan.
- **Combining multiple indexes** for a multi-condition query (e.g., `age = 20 AND active = true`).
- **Poor physical clustering** — when matching rows are scattered across many pages, so grouping fetches by page (instead of jumping row by row) pays off.

## Advantages

- Reduces random I/O — each needed page is read exactly once.
- Bulk-read efficiency improves caching, since matching rows on a page are all pulled together.
- Efficiently merges results from multiple indexes.

## Limitations

- If the bitmap doesn't fit in the available memory (`work_mem`), it degrades to lossy mode — extra per-row rechecks and more I/O.
- If nearly every row in the table qualifies, a plain sequential scan is more efficient than building and using a bitmap at all.

## Summary

| Step | What it does |
|---|---|
| Bitmap Index Scan | Builds a bitmap of qualifying row positions |
| Bitmap Heap Scan | Reads the pages the bitmap points to, retrieves matching rows (rechecking if the bitmap is lossy) |
| Lossy vs. exact bitmap | Lossy: page-level only, needs a recheck; exact: row-level, no recheck needed |

A bitmap heap scan sits between an index scan and a sequential scan in both speed and applicability — one of PostgreSQL's key tools for mid-sized result sets.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Table Scan Types/Bitmap Scan/Bitmap Index Scan|Bitmap Index Scan]]
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Table Scan Types/Bitmap Scan/Explained with Analogy|Explained with Analogy]]

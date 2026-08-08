# Bitmap Scans Explained Step by Step

How PostgreSQL gets from "an index has a matching key" to "here are the actual rows" — heap pages, tuple IDs, and why the bitmap step exists at all.

## 1. Table Storage Model (Heap)

PostgreSQL stores table data in heap pages (blocks), typically 8 KB each:

```
table
 ├─ block 0
 │   ├─ row 1
 │   ├─ row 2
 │   └─ row 3
 ├─ block 1
 │   ├─ row 1
 │   └─ row 2
 └─ block 2
     ├─ row 1
     └─ row 2
```

Every row has a **Tuple Identifier (TID)**: `(block_number, row_offset)`. Example: `(15, 3)` means block 15, row position 3.

## 2. What an Index Stores

Indexes don't store full rows — they store key values plus pointers (TIDs) to rows: `index key → TID`.

Example index on `age`:

```
age = 25 → (7,4)
age = 30 → (12,3)
age = 30 → (12,8)
age = 30 → (18,2)
age = 40 → (21,1)
```

So `age = 30` rows live at block 12 row 3, block 12 row 8, and block 18 row 2.

## 3. Two Ways PostgreSQL Uses an Index

Depending on how many rows match, PostgreSQL retrieves them via either an **Index Scan** or a **Bitmap Scan**.

## 4. Index Scan (Few Matching Rows)

```
index → row
index → row
index → row
```

```
Index Scan using users_age_idx on users
```

Following the example above:
```
age = 30 → (12,3) → read block 12
age = 30 → (12,8) → read block 12 again
age = 30 → (18,2) → read block 18
```

Problem: this is **random disk access** — block 12 gets read twice here, and in general blocks can be revisited multiple times as the index is walked in key order rather than block order.

## 5. Bitmap Scan Strategy (Many Matching Rows)

Instead of fetching rows immediately, PostgreSQL first builds a bitmap of row locations, then reads blocks in a second pass:

```
Bitmap Index Scan
        ↓
Bitmap Heap Scan
```

## 6. Bitmap Index Scan

Scans the index and collects matching row locations — without touching the table yet.

```sql
SELECT * FROM users WHERE age = 30;
```

Index scan results: `(12,3)`, `(12,8)`, `(18,2)`, `(21,5)` — grouped by block into a bitmap:

```
block 12 → rows 3, 8
block 18 → row 2
block 21 → row 5
```

```
Bitmap Index Scan on users_age_idx
  Index Cond: (age = 30)
```

## 7. Bitmap Heap Scan

Fetches the actual rows using the bitmap built above:

1. The bitmap identifies which blocks are needed.
2. Those blocks are sorted.
3. PostgreSQL reads each one exactly once, in order.
4. Matching rows are extracted from each block as it's read.

```
Bitmap Heap Scan on users
  Recheck Cond: (age = 30)
```

## 8. Why the Bitmap Step Exists

Without it, walking the index directly means reading blocks in whatever order the matching keys happen to appear — `block 12, block 21, block 12, block 18` — which is a random access pattern (note block 12 gets revisited).

With the bitmap, PostgreSQL first collects every row location, groups them by block, and *then* reads the blocks — `block 12, block 18, block 21`, sequentially, each exactly once. This reduces disk seeks substantially, at the cost of an extra bookkeeping pass.

## 9. Combining Multiple Indexes

Bitmap scans can combine results from several indexes:

```sql
SELECT * FROM users WHERE age = 30 AND city = 'Chennai';
```

```
Bitmap Heap Scan
  -> BitmapAnd
       -> Bitmap Index Scan (age_idx)
       -> Bitmap Index Scan (city_idx)
```

This computes `bitmap_age AND bitmap_city`, yielding only rows that satisfy both conditions.

For an `OR` condition:
```sql
WHERE age = 30 OR city = 'Chennai'
```
```
BitmapOr
```
This computes `bitmap_age OR bitmap_city`.

## 10. Recheck Condition

Bitmap entries can sometimes be approximate (page-level only, when memory is tight) rather than exact (row-level). PostgreSQL guards against this with a recheck:

```
Recheck Cond: (age = 30)
```

This re-verifies the condition against each candidate row to ensure correctness even when the bitmap itself was lossy.

## 11. Complete Execution Flow

```sql
SELECT * FROM users WHERE age = 30;
```

```
1. Bitmap Index Scan
      ↓
2. build bitmap of TIDs
      ↓
3. Bitmap Heap Scan
      ↓
4. read only the required table blocks
      ↓
5. return rows
```

## 12. Mental Model

```
Index  → find matching row locations
Bitmap → group those locations by block
Heap   → read only those blocks, efficiently, and extract the rows
```

## 13. Summary

| Component | Role |
|---|---|
| Heap | Actual table storage |
| TID | Pointer to a row: `(block, offset)` |
| Index | Maps key values to TIDs |
| Bitmap Index Scan | Collects matching TIDs into a bitmap |
| Bitmap Heap Scan | Reads the flagged table blocks and returns rows |
| BitmapAnd / BitmapOr | Combine bitmaps from multiple indexes |

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Table Scan Types/Bitmap Scan/Bitmap Heap Scan|Comprehensive Guide: Bitmap Heap Scan in PostgreSQL]]
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Table Scan Types/Bitmap Scan/Bitmap Index Scan|Bitmap Index Scan]]

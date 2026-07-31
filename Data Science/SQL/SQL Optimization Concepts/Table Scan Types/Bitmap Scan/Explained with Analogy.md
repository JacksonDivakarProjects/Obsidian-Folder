### 1. Table Storage Model (Heap)

PostgreSQL stores table data in **heap pages (blocks)**.

Typical page size:

```
8 KB
```

Structure:

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

Each row has a **Tuple Identifier (TID)**:

```
(block_number, row_offset)
```

Example:

```
(15,3)
```

Meaning:

```
block 15
row position 3
```

---

# 2. What an Index Stores

Indexes do **not store full rows**.  
They store **key values + pointers to rows**.

Conceptual structure:

```
index key → TID
```

Example index on `age`:

```
age = 25 → (7,4)
age = 30 → (12,3)
age = 30 → (12,8)
age = 30 → (18,2)
age = 40 → (21,1)
```

Interpretation:

```
age = 30 rows are in:
block 12 row 3
block 12 row 8
block 18 row 2
```

---

# 3. Two Ways PostgreSQL Uses Indexes

PostgreSQL can retrieve rows using:

```
Index Scan
Bitmap Scan
```

Which one is used depends on **how many rows match**.

---

# 4. Index Scan

Used when **few rows match**.

Execution pattern:

```
index → row
index → row
index → row
```

Example plan:

```
Index Scan using users_age_idx on users
```

Example process:

```
age = 30 → (12,3) → read block 12
age = 30 → (12,8) → read block 12 again
age = 30 → (18,2) → read block 18
```

Problem:

```
random disk access
```

Blocks may be read repeatedly.

---

# 5. Bitmap Scan Strategy

Used when **many rows match**.

Instead of fetching rows immediately, PostgreSQL builds a **bitmap of row locations first**.

Execution pipeline:

```
Bitmap Index Scan
        ↓
Bitmap Heap Scan
```

---

# 6. Bitmap Index Scan

Purpose:

```
Scan index and collect matching row locations
```

Example query:

```
SELECT * FROM users WHERE age = 30;
```

Index scan result:

```
(12,3)
(12,8)
(18,2)
(21,5)
```

These are grouped by block.

Bitmap representation:

```
block 12 → rows 3,8
block 18 → row 2
block 21 → row 5
```

No table rows are fetched yet.

Output:

```
bitmap of TIDs
```

Execution plan:

```
Bitmap Index Scan on users_age_idx
  Index Cond: (age = 30)
```

---

# 7. Bitmap Heap Scan

Purpose:

```
Fetch actual rows from the table using the bitmap
```

Process:

```
1. Bitmap identifies blocks
2. Blocks are sorted
3. PostgreSQL reads those blocks
4. Extracts matching rows
```

Execution:

```
read block 12
read block 18
read block 21
```

Rows extracted:

```
block 12 row 3
block 12 row 8
block 18 row 2
block 21 row 5
```

Execution plan:

```
Bitmap Heap Scan on users
  Recheck Cond: (age = 30)
```

---

# 8. Why Bitmap Scan Exists

Without bitmap:

```
index → block 12
index → block 21
index → block 12
index → block 18
```

Disk pattern:

```
random access
```

With bitmap:

```
collect row locations
group by block
read blocks sequentially
```

Disk pattern:

```
block 12
block 18
block 21
```

This reduces disk seeks dramatically.

---

# 9. Multiple Index Combination

Bitmap scans allow combining multiple indexes.

Example query:

```
SELECT *
FROM users
WHERE age = 30
AND city = 'Chennai';
```

Execution plan:

```
Bitmap Heap Scan
  -> BitmapAnd
       -> Bitmap Index Scan (age_idx)
       -> Bitmap Index Scan (city_idx)
```

Process:

```
bitmap_age
AND
bitmap_city
```

Result:

```
rows matching both conditions
```

---

Example OR condition:

```
WHERE age = 30 OR city = 'Chennai'
```

Plan:

```
BitmapOr
```

Meaning:

```
bitmap_age OR bitmap_city
```

---

# 10. Recheck Condition

Bitmap entries can sometimes be **approximate**.

Therefore PostgreSQL verifies rows again:

```
Recheck Cond: (age = 30)
```

This ensures accuracy.

---

# 11. Complete Execution Flow

Example query:

```
SELECT *
FROM users
WHERE age = 30;
```

Execution:

```
1. Bitmap Index Scan
      ↓
2. build bitmap of TIDs
      ↓
3. Bitmap Heap Scan
      ↓
4. read only required table blocks
      ↓
5. return rows
```

---

# 12. Conceptual Mental Model

Think of the process like this:

```
Index
   ↓
Find matching row locations
   ↓
Build map of blocks containing matches
   ↓
Read only those blocks from the table
   ↓
Extract rows
```

---

# 13. Summary

|Component|Role|
|---|---|
|Heap|actual table storage|
|TID|pointer to a row (block, offset)|
|Index|maps key values to TIDs|
|Bitmap Index Scan|collects matching TIDs|
|Bitmap Heap Scan|reads table blocks and returns rows|
|BitmapAnd / BitmapOr|combine results of multiple indexes|

Core idea:

```
Index → find row locations
Bitmap → group by blocks
Heap → read those blocks efficiently
```
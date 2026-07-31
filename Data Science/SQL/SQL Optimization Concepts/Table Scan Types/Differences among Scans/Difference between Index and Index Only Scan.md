**Index Only Scan** means PostgreSQL answers a query **using only the index without reading the table (heap)**.

Normal index access still fetches rows from the heap.  
Index-only scan avoids that step.

---

# 1. Normal Index Scan

Execution:

```
index → find key
      → get TID
      → read heap row
```

Plan example:

```
Index Scan using users_age_idx on users
```

Even though the index finds the row location, PostgreSQL still reads the table.

---

# 2. Index Only Scan

Execution:

```
index → find key
      → return column values directly from index
```

No heap access occurs.

Plan example:

```
Index Only Scan using users_age_idx on users
```

---

# 3. Why It Is Possible

Indexes store:

```
index key
+
TID
```

Some indexes also store the **actual column values**.

Example index on `age`:

```
age | TID
------------
25  | (7,4)
30  | (12,3)
30  | (12,8)
40  | (21,1)
```

If the query only needs `age`, PostgreSQL already has the value in the index.

Query:

```sql
SELECT age
FROM users
WHERE age = 30;
```

The table is unnecessary.

---

# 4. When PostgreSQL Can Use It

Two conditions must be satisfied.

### Condition 1 — All required columns must be in the index

Example:

```
index: (age)
query: SELECT age
```

Works.

But this query cannot use index-only scan:

```sql
SELECT name
FROM users
WHERE age = 30;
```

Because `name` is not in the index.

---

### Condition 2 — Visibility Map must allow it

PostgreSQL must ensure the row is **visible to the transaction**.

Normally that requires checking the heap.

If a page is marked **all-visible** in the **visibility map**, PostgreSQL trusts the index and skips heap access.

---

# 5. Execution Flow

Index Only Scan pipeline:

```
scan index
   ↓
check visibility map
   ↓
return values directly from index
```

---

# 6. Performance Advantage

Normal index scan:

```
index read
heap read
index read
heap read
```

Index-only scan:

```
index read
index read
index read
```

Heap access is eliminated.

---

# 7. Example Execution Plan

Query:

```sql
SELECT age
FROM users
WHERE age = 30;
```

Plan:

```
Index Only Scan using users_age_idx on users
  Index Cond: (age = 30)
```

---

# 8. Covering Index Example

Create index:

```sql
CREATE INDEX users_age_name_idx
ON users(age, name);
```

Query:

```sql
SELECT age, name
FROM users
WHERE age = 30;
```

PostgreSQL can perform an **index-only scan** because both columns exist in the index.

---

# 9. Comparison

|Feature|Index Scan|Index Only Scan|
|---|---|---|
|Uses index|yes|yes|
|Reads heap|yes|usually no|
|Requires covering index|no|yes|
|Uses visibility map|no|yes|
|Performance|good|faster|

---

# 10. Mental Model

```
Index Scan
index → TID → heap row

Index Only Scan
index → return data directly
```
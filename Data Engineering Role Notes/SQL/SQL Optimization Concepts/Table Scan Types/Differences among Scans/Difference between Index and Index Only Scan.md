# Difference Between Index Scan and Index-Only Scan

**Index-only scan** means PostgreSQL answers a query using only the index, without reading the table (heap) at all. A normal index scan still fetches rows from the heap; an index-only scan skips that step.

## 1. Normal Index Scan

```
index → find key → get TID → read heap row
```

```
Index Scan using users_age_idx on users
```

Even though the index finds the row's location, PostgreSQL still reads the table to get the actual row data.

## 2. Index-Only Scan

```
index → find key → return column values directly from the index
```

No heap access occurs.

```
Index Only Scan using users_age_idx on users
```

## 3. Why It's Possible

An index entry stores the index key plus a TID — and for many index types, the key *is* the actual column value(s). Example index on `age`:

```
age | TID
------------
25  | (7,4)
30  | (12,3)
30  | (12,8)
40  | (21,1)
```

If a query only needs `age`, PostgreSQL already has that value sitting in the index — no need to touch the table:

```sql
SELECT age FROM users WHERE age = 30;
```

## 4. When PostgreSQL Can Use It

Two conditions must both hold:

### Condition 1 — Every required column must be in the index

```
index: (age)
query: SELECT age   → works
```

But this query *cannot* use an index-only scan against that same index:
```sql
SELECT name FROM users WHERE age = 30;
```
because `name` isn't part of the index.

### Condition 2 — The visibility map must allow it

PostgreSQL must confirm each row is visible to the current transaction (MVCC), which normally means checking the heap. If a page is marked **all-visible** in the visibility map, PostgreSQL trusts that and skips the heap check — this is why routine `VACUUM` matters for keeping index-only scans effective.

## 5. Execution Flow

```
scan index
   ↓
check visibility map
   ↓
return values directly from the index
```

## 6. Performance Advantage

Normal index scan: `index read → heap read → index read → heap read → ...`

Index-only scan: `index read → index read → index read → ...`

Heap access is eliminated entirely.

## 7. Example Execution Plan

```sql
SELECT age FROM users WHERE age = 30;
```

```
Index Only Scan using users_age_idx on users
  Index Cond: (age = 30)
```

## 8. Covering Index Example

```sql
CREATE INDEX users_age_name_idx ON users (age, name);

SELECT age, name
FROM users
WHERE age = 30;
```

PostgreSQL can run this as an index-only scan because both selected columns exist in the index.

## 9. Comparison

| Feature | Index Scan | Index-Only Scan |
|---|---|---|
| Uses the index | Yes | Yes |
| Reads the heap | Yes | Usually no |
| Requires a covering index | No | Yes |
| Uses the visibility map | No | Yes |
| Performance | Good | Faster |

## 10. Mental Model

```
Index Scan:       index → TID → heap row
Index-Only Scan:  index → return data directly
```

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Table Scan Types/Index and Index Only Scan|Comprehensive Guide: Index Scan vs Index-Only Scan in SQL]]

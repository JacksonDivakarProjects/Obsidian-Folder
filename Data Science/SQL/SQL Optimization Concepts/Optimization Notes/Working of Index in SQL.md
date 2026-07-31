Let’s demystify **how SQL chooses rows using an index**.
I’ll keep it sharp, practical, and enterprise-grade so you can use this logic anytime you design or tune queries.

---

# 🔍 **1. How SQL decides to use an index (optimizer workflow)**

The SQL optimizer acts like a cost-estimation engine. It evaluates:

1. **Selectivity**
   –  How many rows will match this predicate?
   –  High selectivity = good index candidate.

2. **Available indexes**
   – Does an index exist on the column(s)?
   – Does the predicate match the index structure?

3. **Type of predicate**
   – `=` and range (`>`, `<`, `BETWEEN`) → index-friendly
   – expressions (`col + 2`, `UPPER(name)`) → not index-friendly unless functional index
   – functions on the column → break index usage

4. **Physical table stats & distribution**
   –  rows
   – page counts
   – histogram stats
   – density

5. **Cost model**
   – I/O cost
   – CPU cost
   – Memory cost
   – Parallelism benefit

Then SQL chooses the cheapest path.

---

# 🔧 **2. OK—but HOW are the “rows actually selected” from the index?**

This is the part most engineers misunderstand.

Let's break it down.

---

# 🧱 **3. Inside the index: What data actually looks like**

A B-Tree index stores:

```
Sorted keys   → pointers (Row IDs or row locations)
```

For example, index on `age`:

```
Key    RID
20     A15
22     B30
25     C02
27     D19
30     E44
```

Keys are sorted
→ This enables binary search
→ Which gives you fast row selection.

---

# 🚀 **4. How SQL selects rows using the index**

## **Case A: Equality predicate**

```sql
WHERE age = 25
```

Steps:

1. Navigate the B-tree root → leaf (log N time)
2. Find leaf page containing `25`
3. Retrieve all row pointers for key=25
4. Fetch those rows from table (heap or clustered)

This is an **Index Seek**.

---

## **Case B: Range predicate**

```sql
WHERE age BETWEEN 20 AND 30
```

Steps:

1. Seek to first key `20`
2. Scan leaf pages sequentially until key `30`
3. Collect all row pointers
4. Fetch table rows

This is an **Index Range Scan**.

---

## **Case C: Non-indexable predicate**

```sql
WHERE age + 2 = 30
```

SQL cannot seek to `age=28` unless you created:

```sql
CREATE INDEX idx_age_plus_2 ON employees((age+2));
```

Without it:

* SQL performs an **Index Scan** (read all leaf pages)
* For each row: compute `age + 2`
* Apply filter

So the index helps ordering, but not filtering.

---

# 🟦 **5. How Bitmap Index Scans choose rows (Postgres)**

When multiple indexes exist:

```sql
WHERE age > 20 AND salary > 5000
```

Postgres:

1. Builds Bitmap #1 from index(age)
2. Builds Bitmap #2 from index(salary)
3. Performs bitmap AND operation
4. The resulting bitmap contains **row locations**
5. Fetches only those rows

Bitmaps represent *row hits*, not expressions.

---

# 🧠 **6. The optimizer’s key decision rule**

### “Will the index retrieve fewer pages than a full table scan?”

If **yes →** use index seek/range/bitmap
If **no →** use table scan

Simple, brutal, effective.

---

# ⭐ Executive Summary

* SQL picks an index based on **cost**, **selectivity**, and **predicate type**.
* A B-Tree index returns rows by **seeking** or **scanning** key ranges.
* Arithmetic or functions break index seeks unless you create a **functional index**.
* Bitmap scans combine multiple index results using bitmaps of row locations.

---

If you want, I can walk you through:
✔ a **step-by-step example** with actual index pages and RID selection
✔ or a **visual diagram** of the index traversal path

Just say **“show example”** or **“show diagram”**.
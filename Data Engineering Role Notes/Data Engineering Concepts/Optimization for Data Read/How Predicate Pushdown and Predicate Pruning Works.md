# How Predicate Pushdown and Predicate Pruning Work (Spark / Delta Lake Internals)

A step-by-step look at what actually happens inside Spark and Delta Lake when a filtered query runs — how predicate pushdown and predicate pruning cooperate to minimize I/O.

## 1. Predicate Pushdown (Row-Level Filtering)

**Goal:** read only the rows that match the filter, not the whole file.

**Mechanism:**
1. You run a query:

```sql
SELECT * FROM sales WHERE region = 'EU';
```

2. Spark's Catalyst optimizer inspects the `WHERE` clause.
3. It checks whether the data source supports pushdown (Parquet, Delta, ORC, and JDBC all do).
4. If supported, Spark converts the filter into read instructions handed to the data source itself, instead of filtering everything after loading it into memory.
5. Each file is still opened, but only the rows (or row groups) matching the predicate are actually materialized.

**Internals:** Parquet stores min/max statistics for each column per row group. Spark compares the filter against these stats to skip row groups that can't contain a match, without decompressing or deserializing them.

**Example:**
- Row group 1: `region=[US–US]` → stats rule it out → skipped
- Row group 2: `region=[EU–EU]` → stats allow a match → read

Result: only rows with `region='EU'` are loaded, cutting both I/O and memory use.

## 2. Predicate Pruning (File/Partition-Level Filtering)

**Goal:** avoid opening files or partitions that cannot contain a match at all.

**Mechanism:**
1. Every file or partition carries metadata:
   - Delta Lake: min/max stats per column plus partition values, stored in the transaction log
   - Parquet: row-group-level stats within each file
2. Spark checks the query filter against this metadata **before** touching the file's actual data.
3. If the file's value range cannot possibly satisfy the filter, it's skipped entirely — zero I/O for that file.

**Example:**
- File 1: `year=[2019–2020]`, filter `year=2023` → range excludes 2023 → skipped
- File 2: `year=[2023–2023]` → matches → scanned
- File 3: `year=[2022–2024]` → range overlaps → scanned, then filtered row-by-row via pushdown

**Tip:** partitioning, sorting, and Z-ordering make pruning far more effective, because they cluster related values together — tighter min/max ranges per file mean more files can be ruled out up front.

## 3. Combined Flow (Delta + Spark)

**Query:**

```sql
SELECT customer_id, amount FROM sales WHERE region = 'EU' AND year = 2023;
```

**Execution order:**
1. **Pruning:** skip any file whose stats prove it can't satisfy the filter — i.e. its `region` range excludes `'EU'`, *or* its `year` range excludes `2023`. Since the filter is an AND, ruling out either sub-condition is enough to rule out the whole file.
2. **Pushdown:** for files that survive pruning, read only the rows matching `region='EU' AND year=2023`, using in-file statistics / row-group skipping.
3. **Column pruning:** of the rows that remain, read only the `customer_id` and `amount` columns from disk.
4. **Result:** minimal I/O, minimal memory, fastest possible query.

## Key Takeaways
- **Pushdown** operates at row level, inside a file.
- **Pruning** operates at file/partition level, skipping whole files before they're opened.
- **Column pruning** reduces which columns are read, independent of row filtering.
- Partitioning, sorting, and Z-ordering amplify pruning by tightening the value range each file covers.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Optimization for Data Read/Predicate Pruning & Predicate Pushdown|Predicate Pushdown vs Predicate Pruning]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Optimization for Data Read/Predicate Pushdown & Column Pruning|Predicate Pushdown & Column Pruning]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Optimize, ZOrdering, Liquid Clustering|Optimize, Z-Ordering, Liquid Clustering]]

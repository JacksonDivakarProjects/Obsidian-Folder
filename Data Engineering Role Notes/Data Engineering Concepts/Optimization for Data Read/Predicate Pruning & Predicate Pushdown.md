# Predicate Pushdown vs Predicate Pruning

A side-by-side comparison to keep the two concepts distinct — useful for explaining them clearly in interviews or design discussions.

## Comparison Table

| Aspect | Predicate Pushdown | Predicate Pruning (Data/File/Partition Pruning) |
|---|---|---|
| What it does | Filters rows inside each file at the data source level | Skips entire files or partitions that cannot contain matching rows |
| Level of operation | Row-level | File-level / partition-level |
| Requirement on data order | Not required | Ordering or partitioning significantly improves effectiveness |
| Performance benefit | Reduces rows read from each file | Reduces the number of files opened at all — typically the bigger win |
| How it works | Uses in-file column statistics (min/max) to filter rows while reading | Uses file metadata, partitioning scheme, or Z-ordering to skip files whose value ranges can't match |
| Supported by | Parquet, ORC, Delta, JDBC | Delta Lake (file stats), partitioned tables, Z-order optimized files |

## How Each Works

### Predicate Pushdown
1. Query:

```sql
SELECT * FROM sales WHERE year = 2023;
```

2. Spark checks file metadata (min/max per column).
3. Within each file, only rows matching `year = 2023` are actually read into memory.
4. The file itself is still scanned — pushdown reduces *rows*, not *files*.

**Example:** a file spanning `year = 2022, 2023, 2024` is opened, but pushdown reads only the `2023` rows from it.

### Predicate Pruning
1. Spark/Delta checks file-level metadata (min/max) or partition values against the filter.
2. If the entire file/partition cannot satisfy the filter, it's skipped completely — no read at all.

**Example:**
- File 1: `year=[2020–2021]` → skipped
- File 2: `year=[2023]` → read
- File 3: `year=[2022–2024]` → read, then filtered further by pushdown

**Tip:** pruning is most effective when files are clustered, partitioned, or Z-ordered — tight value ranges per file mean more files can be ruled out up front.

## Key Takeaways
- **Pushdown** — row-level filtering, works within any single file.
- **Pruning** — file/partition-level filtering; needs ordered or partitioned data to be maximally effective.
- Used together, they minimize both rows read and files scanned, for the best possible query performance.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Optimization for Data Read/How Predicate Pushdown and Predicate Pruning Works|How Predicate Pushdown and Predicate Pruning Works]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Optimization for Data Read/Predicate Pushdown & Column Pruning|Predicate Pushdown & Column Pruning]]

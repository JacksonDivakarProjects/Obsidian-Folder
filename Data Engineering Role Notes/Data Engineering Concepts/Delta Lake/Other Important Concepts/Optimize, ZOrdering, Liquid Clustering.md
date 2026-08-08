# OPTIMIZE, Z-Ordering, and Liquid Clustering

A guide to the three main techniques Delta Lake offers for controlling physical data layout: file compaction (`OPTIMIZE`), Z-order clustering, and liquid clustering (`CLUSTER BY`).

## 1. Why Optimize / Cluster / Z-order at All?

- Data lakes suffer from the **small-file problem** — many tiny Parquet files increase metadata overhead and slow down query planning and scanning.
- Query speed depends heavily on **data skipping**: Delta uses file-level statistics (min/max values, null counts) to avoid scanning files that can't possibly contain matching rows.
- How effectively skipping works depends on **layout** — how rows are grouped into files. If rows matching a filter are scattered across many files, skipping buys you little.
- Clustering (Z-order, liquid clustering) physically co-locates related rows in the same files to maximize file skipping, reduce I/O, and speed up scans.

`OPTIMIZE` and the clustering techniques below are the core tools for keeping a Delta table performant as it grows.

## 2. OPTIMIZE / File Compaction (Bin-Packing)

### What It Does

- `OPTIMIZE` rewrites data files (within a table or partition) to coalesce small files into larger ones (bin-packing), and optionally reorders data for better locality via Z-order or liquid clustering.
- It is a purely physical rewrite — no rows are added or removed, and the table's logical content is unchanged.
- Pure compaction (without `ZORDER`) is idempotent: running it twice with no new data has no effect the second time.

### Syntax (SQL)

```sql
OPTIMIZE table_name [FULL] [WHERE partition_predicate] [ZORDER BY (col1, col2, ...)]
```

- `FULL` is only valid on tables that use liquid clustering — it forces a full reclustering of all data, including older data that wouldn't normally be touched.
- `WHERE` limits optimization to specific partitions (e.g. only recent partitions on a huge table). **Not usable on liquid-clustered tables.**
- `ZORDER BY` specifies the columns to cluster by. **Not usable on liquid-clustered tables** — Z-order and liquid clustering are mutually exclusive on the same table.

**Examples:**

```sql
-- Compact the entire table
OPTIMIZE my_table;

-- Compact only partitions from 2025-01-01 onward
OPTIMIZE my_table 
 WHERE date_col >= '2025-01-01';

-- Compact + Z-order on a column
OPTIMIZE my_table 
 WHERE date_col >= '2025-01-01'
 ZORDER BY (user_id);
```

### Configuration & Tuning

- **Target file size** — configurable via the `delta.targetFileSize` table property (or the equivalent Spark config) to aim for a specific file size (e.g. 100 MB–1 GB).
- **Auto compaction / optimized writes** — newer Delta versions support automatic compaction after writes and "optimized writes" that reduce the small-file problem without requiring an explicit `OPTIMIZE` run.
- **Partitioned tables** — bin-packing happens *within* each partition; it doesn't rewrite across partition boundaries unless you use `OPTIMIZE FULL` on a liquid-clustered table.

### Best Practices

- Schedule `OPTIMIZE` regularly (e.g. nightly), targeting hot/recently-written partitions.
- Scope optimize to the partitions that actually accumulated many small files, rather than the full table every time.
- Combine with a clustering strategy (Z-order or liquid clustering) for maximum benefit.
- Don't over-optimize — frequent full rewrites burn compute for little marginal gain once files are already well-sized.

## 3. Z-Ordering (Multi-Dimensional Clustering)

### What It Is

- Z-ordering interleaves the bits of multiple column values to produce a space-filling curve, which co-locates rows with similar values across *multiple* columns in the same files. Delta uses this to make data skipping more effective for multi-column filters.
- Running `OPTIMIZE ... ZORDER BY (col1, col2, ...)` rewrites the table's data files so rows are physically ordered along that Z-curve.

### Constraints & Caveats

- Z-ordering is **not idempotent** — running it repeatedly can keep relocating data even without new writes, because each `OPTIMIZE ... ZORDER` recomputes the curve over the current file set.
- Effectiveness drops as you add more columns to `ZORDER BY`. Stick to a small number (1–2, rarely more) of columns that are genuinely used in filters.
- The Z-ordered columns need file-level statistics (min/max) collected for skipping to actually kick in.
- Cannot be combined with liquid clustering on the same table.
- Rewriting for Z-order is expensive on large tables — use it selectively (e.g. cold or newly-landed partitions) rather than on the whole table on every run.

### Example

```sql
-- Z-order on user_id and date
OPTIMIZE events
 WHERE date >= '2025-01-01'
 ZORDER BY (user_id, date);
```

A common pattern is to partition on a coarse column (like `date`) and then Z-order within each partition on a higher-cardinality column (like `user_id`) that's frequently filtered but not a good partition key itself.

## 4. Liquid Clustering (`CLUSTER BY`)

Liquid clustering is Delta's newer, more flexible alternative to partitioning + Z-order. It automates layout management instead of requiring you to hand-tune both.

### What It Is

- Liquid clustering incrementally and automatically clusters data based on declared clustering keys, adapting layout over time as data and query patterns change.
- Clustering keys can be **changed without rewriting existing data** — new writes and future `OPTIMIZE` runs simply start respecting the new keys going forward.
- Because clustering happens incrementally rather than via full-table rewrites, it suits streaming or frequently-updated tables much better than Z-order does.
- For new tables on a supporting runtime, liquid clustering is generally recommended over partitioning + Z-order.
- It is **not compatible** with Hive-style partitioning or Z-order on the same table — you pick one strategy per table.

### Enabling It

On table creation:

```sql
CREATE TABLE my_table (
  id STRING,
  region STRING,
  amount DOUBLE,
  date DATE
)
USING DELTA
CLUSTER BY (region, date);
```

Or let the platform choose clustering keys automatically (Databricks Unity Catalog):

```sql
CREATE TABLE my_table
USING DELTA
CLUSTER BY AUTO;
```

On an existing table:

```sql
ALTER TABLE my_table
CLUSTER BY (region, date);
```

To remove clustering or switch keys:

```sql
ALTER TABLE my_table
CLUSTER BY NONE;

ALTER TABLE my_table
CLUSTER BY (new_key);
```

Changing or removing clustering keys only affects future writes and optimize runs — existing data isn't rewritten immediately.

### Triggering Clustering

- Once enabled, new data is clustered incrementally as it's written — you don't need to run anything extra for new rows.
- `OPTIMIZE` still triggers compaction/layout adjustments; on a liquid-clustered table it groups files by the clustering keys instead of an explicit Z-order.
- `OPTIMIZE FULL` (available on newer runtimes) forces a full reclustering pass over all data, including older records that incremental clustering hasn't touched yet.

### Constraints & Considerations

- Typically supports up to 4 clustering columns.
- Clustering keys must have statistics collected for pruning to work (by default, Delta collects stats on the first 32 columns unless configured otherwise).
- Clustering state is stored in the transaction log, so it's maintained across commits automatically.
- Incompatible with Hive-style partitioning and Z-order — pick one layout strategy per table.
- Some streaming table operations (e.g. `ALTER TABLE ... CLUSTER BY`) may have limited support depending on the runtime.

### Choosing Clustering Columns

- Prefer columns that are commonly used in filters, especially higher-cardinality columns.
- Favor columns with a reasonably even value distribution — avoid extremely skewed columns.
- Use 1–3 good keys rather than many weak ones.
- Revisit choices over time — liquid clustering makes it cheap to evolve keys as query patterns shift.

## 5. Choosing Between the Two Approaches

| Feature | Partitioning + Z-order | Liquid Clustering |
|---|---|---|
| Compatibility | Works on all Delta Lake versions/OSS | Requires Delta 3.1+ / newer runtimes |
| Combinable | Partition, then Z-order within partitions | Cannot combine with partitioning or Z-order |
| Flexibility | Changing filter patterns often needs a rewrite | Change clustering keys without a full rewrite |
| Rewrite cost | Z-order re-clusters large portions on each run | Incremental — lower ongoing overhead |
| Streaming / evolving workloads | Needs more manual tuning | Better suited to changing ingestion patterns |
| User complexity | You manage partition + Z-order choices explicitly | More automated/abstracted |

If you're on a runtime that supports it and your workloads or query patterns shift over time, liquid clustering is generally the better long-term choice.

## 6. Putting It Together — A Typical Workflow

1. **Design the schema and decide on partitioning** (if not using liquid clustering). If you choose liquid clustering, avoid or minimize traditional partitioning.
2. **Ensure statistics are collected** on the columns you plan to filter/cluster by (`delta.dataSkippingNumIndexedCols` / `delta.dataSkippingStatsColumns`).
3. **Create the table with your layout decision**: partitioned + later `OPTIMIZE ... ZORDER`, or `CLUSTER BY` for liquid clustering.
4. **Write data** — rely on optimized writes/auto-compaction where available to limit small-file creation at write time.
5. **Schedule `OPTIMIZE` runs** — `OPTIMIZE ... ZORDER` on partitions for the traditional approach, or plain `OPTIMIZE` / `OPTIMIZE FULL` for liquid-clustered tables.
6. **Monitor and tune** — use `DESCRIBE HISTORY` and `DESCRIBE DETAIL` to see optimize/clustering operations and file counts; adjust keys if query patterns change.
7. **Keep running `VACUUM`** to clean up obsolete files per your retention policy, and keep an eye on transaction log size/checkpointing.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Optimization for Data Read/How Predicate Pushdown and Predicate Pruning Works|How Predicate Pushdown and Predicate Pruning Works]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Important TBLProperties/Table Utility Commands|Delta Lake Table Utility Commands]]


Below is a **comprehensive guide** covering **OPTIMIZE / compaction**, **Z-order**, and **Liquid Clustering / `CLUSTER BY`** in Delta Lake. I aim to present both the concepts and actionable patterns. If you tell me your Delta version / runtime (OSS, Databricks, etc.), I can tailor it further.

---

## 1. Why Optimize / Cluster / Z-order?

Before diving into commands, understand the “why”:

- Data lakes often suffer from **small file problem** (many tiny Parquet/Delta files), which increases metadata overhead and slows query planning/scanning.
    
- Query speed depends on **pruning / skipping irrelevant files**. Delta uses **data skipping** (based on file-level statistics: min/max, null counts) to avoid scanning unnecessary files. ([Delta Lake](https://docs.delta.io/latest/optimizations-oss.html?utm_source=chatgpt.com "Optimizations - Delta Lake Documentation"))
    
- Layout (how rows are grouped into files) strongly influences how effective skipping is. If rows matching a filter are scattered across many files, skipping is less helpful.
    
- Clustering (Z-order, liquid clustering) tries to **physically colocate related rows** in the same files to maximize file skipping, reduce IO, and improve scan performance.
    

Thus, Optimize + clustering techniques are core tools to keep your Delta table performant.

---

## 2. OPTIMIZE / File Compaction (Bin‐Packing)

### What it does

- `OPTIMIZE` rewrites data files (within a table or partition) to **coalesce small files** into larger ones (bin-packing) and optionally reorder data for better locality (Z-order or liquid clustering). ([Databricks Documentation](https://docs.databricks.com/aws/en/delta/optimize?utm_source=chatgpt.com "Optimize data file layout | Databricks on AWS"))
    
- It _does not_ change the logical data (i.e. no rows are added/removed). It’s a purely physical rewrite. ([Delta Lake](https://docs.delta.io/latest/optimizations-oss.html?utm_source=chatgpt.com "Optimizations - Delta Lake Documentation"))
    
- It is **idempotent** for pure compaction: if you run it twice without data changes, the second run has no effect. ([Delta Lake](https://docs.delta.io/latest/optimizations-oss.html?utm_source=chatgpt.com "Optimizations - Delta Lake Documentation"))
    

### Syntax (SQL)

```sql
OPTIMIZE table_name [FULL] [WHERE partition_predicate] [ZORDER BY (col1, col2, ...)]
```

- `FULL` is only valid when the table uses liquid clustering. It forces reclustering of all data (including older data). ([Databricks Documentation](https://docs.databricks.com/aws/en/sql/language-manual/delta-optimize?utm_source=chatgpt.com "OPTIMIZE | Databricks on AWS"))
    
- `WHERE` clause allows you to limit the optimization to certain partitions. This helps for large tables if you only want to compact recent partitions. But note: **you can’t use `WHERE` when the table uses liquid clustering**. ([Databricks Documentation](https://docs.databricks.com/aws/en/sql/language-manual/delta-optimize?utm_source=chatgpt.com "OPTIMIZE | Databricks on AWS"))
    
- `ZORDER BY` lets you specify columns to cluster by (multi-dimensional). But again when **liquid clustering is enabled**, you cannot use `ZORDER BY`. ([Databricks Documentation](https://docs.databricks.com/aws/en/sql/language-manual/delta-optimize?utm_source=chatgpt.com "OPTIMIZE | Databricks on AWS"))
    

**Examples:**

```sql
-- compact entire table
OPTIMIZE my_table;

-- compact only partitions from 2025-01-01 onwards
OPTIMIZE my_table 
 WHERE date_col >= '2025-01-01';

-- compact + Z-order on a column
OPTIMIZE my_table 
 WHERE date_col >= '2025-01-01'
 ZORDER BY (user_id);
```

### Configurations & tuning

- **Target file size**: You can set a target file size (e.g. 100 MB, 256 MB, 1 GB) via table property `delta.targetFileSize` or relevant Spark configs. ([Microsoft Learn](https://learn.microsoft.com/en-us/azure/databricks/delta/tune-file-size?utm_source=chatgpt.com "Configure Delta Lake to control data file size - Azure Databricks"))
    
- **Auto compaction / optimized writes**: In more recent versions, Delta supports _automatic compaction_ (after writes) and _optimized writes_ to reduce the small file issue without requiring explicit `OPTIMIZE`. ([Delta Lake](https://docs.delta.io/latest/optimizations-oss.html?utm_source=chatgpt.com "Optimizations - Delta Lake Documentation"))
    
- **Partitioned tables**: The `OPTIMIZE` (bin-packing) is applied _within partitions_—you don’t rewrite across partitions unless full. ([Databricks Documentation](https://docs.databricks.com/aws/en/delta/optimize?utm_source=chatgpt.com "Optimize data file layout | Databricks on AWS"))
    

### Best practices

- Schedule `OPTIMIZE` regularly (e.g. nightly) especially on hot partitions.
    
- Limit optimize to partitions that have many small files (rather than full table every time).
    
- Combine optimize with clustering strategies (Z-order or liquid) for maximum benefit.
    
- Don’t over-optimize: too frequent rewrites cost cluster resources.
    

---

## 3. Z-Ordering (Multi-dimensional Clustering)

### What is Z-order?

- Z-ordering (sometimes “multi-dimensional clustering”) is a technique to **interleave bits** of multiple column values to produce a _space-filling curve_. This helps colocate rows with similar values in multiple columns. Delta uses this to improve **data skipping**. ([Delta Lake](https://docs.delta.io/latest/optimizations-oss.html?utm_source=chatgpt.com "Optimizations - Delta Lake Documentation"))
    
- When you `OPTIMIZE … ZORDER BY (col1, col2, …)`, Delta rewrites the data files so that data is ordered along the Z-curve of those columns. ([Delta Lake](https://docs.delta.io/latest/optimizations-oss.html?utm_source=chatgpt.com "Optimizations - Delta Lake Documentation"))
    

### Constraints & caveats

- Z-ordering is **not idempotent**: running it multiple times may continue to relocate data. ([Microsoft Learn](https://learn.microsoft.com/en-us/azure/databricks/sql/language-manual/delta-optimize?utm_source=chatgpt.com "OPTIMIZE - Azure Databricks - Microsoft Learn"))
    
- If you specify multiple columns, the effectiveness of locality (i.e. clustering) drops with more columns. You should limit to a few columns (e.g. 1 or 2) that are highly used in filters. ([Delta Lake](https://docs.delta.io/latest/optimizations-oss.html?utm_source=chatgpt.com "Optimizations - Delta Lake Documentation"))
    
- The columns used in `ZORDER` must have statistics collected (min/max) in their file metadata, otherwise skipping won’t be effective. ([Microsoft Learn](https://learn.microsoft.com/en-us/azure/databricks/delta/data-skipping?utm_source=chatgpt.com "Data skipping for Delta Lake - Azure Databricks | Microsoft Learn"))
    
- You **cannot use `ZORDER BY`** if the table is using _liquid clustering_. ([Databricks Documentation](https://docs.databricks.com/aws/en/sql/language-manual/delta-optimize?utm_source=chatgpt.com "OPTIMIZE | Databricks on AWS"))
    
- Excessive Z-ordering on many columns is counterproductive; choose a small subset of frequently filtered columns.
    
- Rewriting data for Z-order is expensive on large datasets; use selectively (e.g. on cold partitions or incremental partitions).
    

### Example usage

```sql
-- Z-order on user_id and date
OPTIMIZE events
 WHERE date >= '2025-01-01'
 ZORDER BY (user_id, date);
```

You might also combine with partitioning: partition the table on date, and then Z-order within each partition on user_id (if user_id is a frequent filter).  
Z-order helps when queries filter on non-partition columns or multiple columns.

---

## 4. Liquid Clustering (`CLUSTER BY`)

Liquid clustering is a more advanced and flexible approach introduced in more recent Delta Lake versions. It aims to replace/hide the complexity of partitioning + Z-order, adapting layout automatically.

### What is Liquid Clustering?

- It automatically and incrementally clusters data based on defined _clustering keys_, using a tree-based or algorithmic clustering approach. It adapts to query patterns over time. ([delta.io](https://delta.io/blog/liquid-clustering/?utm_source=chatgpt.com "Delta Lake Liquid Clustering"))
    
- It’s designed to be more flexible: you can **change clustering columns** without rewriting existing data; new data and future `OPTIMIZE` operations will respect the new keys. ([delta.io](https://delta.io/blog/liquid-clustering/?utm_source=chatgpt.com "Delta Lake Liquid Clustering"))
    
- Because it’s incremental, it avoids full-table rewrites, making it more suitable for streaming or frequently updated tables. ([delta.io](https://delta.io/blog/liquid-clustering/?utm_source=chatgpt.com "Delta Lake Liquid Clustering"))
    
- Literature and Databricks recommend using liquid clustering instead of partition + Z-order for new tables if your environment supports it. ([Databricks Documentation](https://docs.databricks.com/aws/en/delta/clustering?utm_source=chatgpt.com "Use liquid clustering for tables | Databricks on AWS"))
    
- Note: It is **not compatible** with partitioning and with Z-order in the same table. You can’t mix them. ([Microsoft Learn](https://learn.microsoft.com/en-us/azure/databricks/delta/clustering?utm_source=chatgpt.com "Use liquid clustering for tables - Azure Databricks | Microsoft Learn"))
    

### Syntax & enabling

#### On creation:

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

This enables liquid clustering on the specified columns. ([delta.io](https://delta.io/blog/liquid-clustering/?utm_source=chatgpt.com "Delta Lake Liquid Clustering"))

Or with _auto clustering_ (Databricks Unity Catalog managed):

```sql
CREATE TABLE my_table
USING DELTA
CLUSTER BY AUTO;
```

This lets Delta/Databricks pick clustering keys automatically. ([Microsoft Learn](https://learn.microsoft.com/en-us/azure/databricks/delta/clustering?utm_source=chatgpt.com "Use liquid clustering for tables - Azure Databricks | Microsoft Learn"))

#### On existing table:

```sql
ALTER TABLE my_table
CLUSTER BY (region, date);
```

or to remove clustering or change keys:

```sql
ALTER TABLE my_table
CLUSTER BY NONE;

ALTER TABLE my_table
CLUSTER BY (new_key);
```

When clustering columns are removed, future writes/optimizes will stop clustering by those keys, but existing data is not rewritten immediately. ([Microsoft Learn](https://learn.microsoft.com/en-us/azure/databricks/delta/clustering?utm_source=chatgpt.com "Use liquid clustering for tables - Azure Databricks | Microsoft Learn"))

#### Triggering clustering / optimizing

- Once clustering is enabled, **new data ingestion** is incrementally clustered under the hood—i.e. writes obey clustering logic. ([delta.io](https://delta.io/blog/liquid-clustering/?utm_source=chatgpt.com "Delta Lake Liquid Clustering"))
    
- You can still run `OPTIMIZE` to trigger clustering compaction / layout adjustments. In tables using liquid clustering, `OPTIMIZE` will group files by clustering keys (rather than explicit Z-order). ([Databricks Documentation](https://docs.databricks.com/aws/en/delta/optimize?utm_source=chatgpt.com "Optimize data file layout | Databricks on AWS"))
    
- `OPTIMIZE FULL` is supported (Databricks Runtime 16.0+), to force reclustering of all records, including old ones. ([Databricks Documentation](https://docs.databricks.com/aws/en/sql/language-manual/delta-optimize?utm_source=chatgpt.com "OPTIMIZE | Databricks on AWS"))
    

### Constraints & considerations

- Maximum number of clustering columns: typically up to 4. ([delta.io](https://delta.io/blog/liquid-clustering/?utm_source=chatgpt.com "Delta Lake Liquid Clustering"))
    
- Clustering keys must be among the columns for which statistics are collected (so pruning / skipping works). By default statistics are collected for first 32 columns unless changed. ([Microsoft Learn](https://learn.microsoft.com/en-us/azure/databricks/delta/data-skipping?utm_source=chatgpt.com "Data skipping for Delta Lake - Azure Databricks | Microsoft Learn"))
    
- Liquid clustering is **stateful**: it uses metadata stored in the transaction log to maintain clustering layout over time. ([delta.io](https://delta.io/blog/liquid-clustering/?utm_source=chatgpt.com "Delta Lake Liquid Clustering"))
    
- It is **not compatible** with Hive-style partitioning and Z-order. If you enable clustering you cannot use Z-order or partition-based optimization in the same table. ([delta.io](https://delta.io/blog/liquid-clustering/?utm_source=chatgpt.com "Delta Lake Liquid Clustering"))
    
- Existing data is _not_ automatically reclustered when changing clustering keys; only new data and future optimize operations respect the new keys. ([delta.io](https://delta.io/blog/liquid-clustering/?utm_source=chatgpt.com "Delta Lake Liquid Clustering"))
    
- For streaming tables, some limitations exist: for example, `ALTER TABLE CLUSTER BY` may not be supported in streaming tables. ([Databricks Community](https://community.databricks.com/t5/data-engineering/best-practices-for-liquid-clustering-and-z-ordering-for-existing/td-p/89382?utm_source=chatgpt.com "Best practices for Liquid clustering and z-orderin... - 89382"))
    

### Choosing clustering columns

- Choose columns commonly used in filters, especially high-cardinality columns.
    
- Prefer columns whose distribution is fairly balanced (avoid extremely skewed columns).
    
- Avoid using many columns; 1–3 good keys are better than many.
    
- Monitor query patterns over time—liquid clustering allows evolving keys.
    

---

## 5. Comparisons & Decision Guide

Here’s a high-level guide to choosing between partitioning + Z-order vs. liquid clustering:

|Feature|Partition + Z-order|Liquid Clustering|
|---|---|---|
|Compatibility with old versions / OSS|Well-supported across Delta Lake|Requires Delta 3.1+ / newer runtimes|
|Mix / combination|You can partition, then Z-order within partitions|Cannot combine with partition / Z-order|
|Flexibility|Changing filter patterns may need rewrites|You can change clustering keys without full rewrites|
|Overhead|Z-order rewrites large portions for clustering changes|Incremental, lower overhead|
|Streaming / evolving workloads|More manual tuning needed|Better suited to evolving ingestion patterns|
|Complexity for users|More exposure (you choose partition/Z-order)|More abstracted / automatic|

If you’re on a newer runtime and your workloads are dynamic, liquid clustering is often the better long-term option.

---

## 6. Workflow / Recipe (Putting it all together)

Here’s a typical recommended workflow:

1. **Design schema and choose partitioning (if still using partitions).**  
    If you opt for liquid clustering, avoid or minimize partitions.
    
2. **Enable statistics on relevant columns**  
    Use `delta.dataSkippingNumIndexedCols` or `delta.dataSkippingStatsColumns` to ensure stats are collected on clustering predicates. ([Microsoft Learn](https://learn.microsoft.com/en-us/azure/databricks/delta/data-skipping?utm_source=chatgpt.com "Data skipping for Delta Lake - Azure Databricks | Microsoft Learn"))
    
3. **Create table with clustering / Z-order decisions**
    
    - For Z-order: create partitioned table, then later use `OPTIMIZE ... ZORDER`.
        
    - For liquid clustering: create / alter table with `CLUSTER BY`.
        
4. **Write data (uses optimized writes / auto compaction if available)**  
    In modern runtimes, `optimizeWrite` / `autoCompact` reduce small file issues during writes. ([Microsoft Learn](https://learn.microsoft.com/en-us/azure/databricks/delta/tune-file-size?utm_source=chatgpt.com "Configure Delta Lake to control data file size - Azure Databricks"))
    
5. **Schedule / trigger OPTIMIZE**
    
    - For non-clustered tables: run `OPTIMIZE ... ZORDER` on partitions.
        
    - For clustered tables: run `OPTIMIZE` or `OPTIMIZE FULL` (when you want full reclustering).
        
6. **Monitor and tune**
    
    - Use `DESCRIBE HISTORY`, `DESCRIBE DETAIL` to see clustering / optimize operations.
        
    - Monitor query performance, I/O, number of files scanned.
        
    - If query patterns change, alter clustering keys or run targeted optimize.
        
7. **Vacuum and memory maintenance**  
    Continue to run `VACUUM` to clean obsolete files (retention rules).  
    Ensure transaction log size, checkpointing, and log compaction are in good shape.
    

---

## 7. Useful References / Documentation

- Delta Lake Optimizations (OPTIMIZE, compaction) — official docs ([Delta Lake](https://docs.delta.io/latest/optimizations-oss.html?utm_source=chatgpt.com "Optimizations - Delta Lake Documentation"))
    
- Databricks / Delta “Optimize data file layout” (Databricks SQL) ([Databricks Documentation](https://docs.databricks.com/aws/en/sql/language-manual/delta-optimize?utm_source=chatgpt.com "OPTIMIZE | Databricks on AWS"))
    
- Liquid Clustering feature blog / documentation ([delta.io](https://delta.io/blog/liquid-clustering/?utm_source=chatgpt.com "Delta Lake Liquid Clustering"))
    
- Data skipping + Z-order guidelines ([Microsoft Learn](https://learn.microsoft.com/en-us/azure/databricks/delta/data-skipping?utm_source=chatgpt.com "Data skipping for Delta Lake - Azure Databricks | Microsoft Learn"))
    

---

If you like, I can build a **cheat-sheet** (SQL + patterns) or **decision flowchart** tailored to your environment (OSS vs Databricks) so you can use this at a glance. Do you want me to send that?

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Optimization for Data Read/How Predicate Pushdown and Predicate Pruning Works|How Predicate Pushdown and Predicate Pruning Works]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Important TBLProperties/Table Utility Commands|Delta Lake Table Utility Commands]]

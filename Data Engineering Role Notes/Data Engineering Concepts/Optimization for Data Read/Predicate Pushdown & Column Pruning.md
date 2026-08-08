# Predicate Pushdown & Column Pruning in Spark + Delta Lake

A practical guide to two of the most important read-optimizations in Spark/Delta Lake — enough depth to both understand and explain them in a performance-tuning or interview context.

## 1. Why They Matter

Modern data systems (Spark, Delta Lake, Parquet) routinely process terabytes of data, so reducing what's actually read from disk is critical for performance. Two optimizations make this possible:

1. **Predicate Pushdown** — filters data as early as possible, ideally at the storage layer.
2. **Column Pruning** — limits which columns are read at all.

Together they cut down disk I/O, network transfer, deserialization cost, and memory footprint.

## 2. Predicate Pushdown — Deep Dive

**Definition:** the optimization where filter conditions (`WHERE` clauses) are pushed down to the data source, so only matching rows are read into Spark instead of being filtered after the fact.

**How it works:**
1. Spark's Catalyst optimizer detects filter expressions in the query.
2. It checks whether the underlying data source (Parquet, Delta, ORC, JDBC) supports pushdown.
3. If so, filtering happens at the I/O layer itself, not in memory after a full read.

**Example:**

```sql
SELECT * FROM orders WHERE country = 'India' AND year = 2024;
```

- Without pushdown: Spark reads every row from `orders`, then applies the `WHERE` clause in memory.
- With pushdown: only rows satisfying `country='India' AND year=2024` are fetched from disk in the first place.

**Performance impact:** less data scanned, lower CPU/memory usage, better query latency.

**Supported sources:**

| Data Source | Supports Predicate Pushdown |
|---|---|
| Parquet | Yes |
| ORC | Yes |
| Delta Lake | Yes |
| JDBC | Yes (translated into SQL sent to the source) |
| JSON/CSV | Limited to none — row-oriented, no per-column stats |

**Verifying it in Spark:**

```python
df = spark.read.format("parquet").load("/data/orders")
df.filter("country = 'India'").explain(True)
```

Look for this in the physical plan:

```
PushedFilters: [IsNotNull(country), EqualTo(country,India)]
```

That confirms predicate pushdown is active.

## 3. Column Pruning — Deep Dive

**Definition:** ensures only the columns actually needed by the query are read from the data source — Spark never deserializes columns you don't select.

**How it works:**
1. The query analyzer inspects the `SELECT` clause (and anything else referencing columns, like joins or aggregations).
2. It determines the minimal set of columns actually needed.
3. The read plan is adjusted to fetch only those columns from the underlying columnar file.

**Example:**

```sql
SELECT customer_id, amount FROM transactions;
```

- Without column pruning: all columns are read from `transactions`, and the unneeded ones are dropped afterward.
- With column pruning: only `customer_id` and `amount` are read directly from the Parquet/Delta files.

**Performance impact:** smaller disk reads, less network transfer, faster deserialization — this is one of the main reasons columnar formats (Parquet, ORC) outperform row-oriented ones (CSV, JSON) for analytical queries.

**Verifying it in Spark:**

```python
df = spark.read.format("parquet").load("/data/transactions")
df.select("customer_id", "amount").explain(True)
```

Plan output:

```
PushedFilters: []
ReadSchema: struct<customer_id:int,amount:double>
```

The `ReadSchema` entry confirms column pruning was applied.

## 4. Predicate Pushdown + Column Pruning Together

These two usually work hand-in-hand:

```sql
SELECT customer_id, amount 
FROM sales 
WHERE region = 'EU' AND year = 2023;
```

- **Predicate pushdown** reads only rows matching `region='EU' AND year=2023`.
- **Column pruning** reads only the `customer_id` and `amount` columns.

Combined, this minimizes the data actually read from disk.

## 5. Predicate Pushdown and Pruning in Delta Lake

Delta Lake builds on top of Parquet's own row-group pushdown with an additional, cheaper layer: **file-level pruning, commonly called "data skipping."**

- Delta maintains per-file statistics (min/max per column) in its transaction log.
- Before any Parquet file is even opened, Delta checks these stats against the query filter and skips files that can't possibly match.

**Example:**

```
File A: year=[2020–2022]
File B: year=[2023–2024]
```

Query:

```sql
SELECT * FROM sales WHERE year = 2021;
```

Delta reads only File A — File B is skipped entirely based on transaction-log metadata, before Parquet's own row-group pushdown even runs.

Note: this "data skipping" is really file-level *pruning*, not pushdown — it happens a layer earlier, deciding which files get opened at all. Pushdown then still applies inside whichever files are opened.

## 6. Verifying Both Optimizations

```python
df.explain(True)
```

Look for:
- `PushedFilters:` → confirms predicate pushdown
- `ReadSchema:` → confirms column pruning

Example plan snippet:

```
== Physical Plan ==
*(1) FileScan parquet [customer_id,amount] 
PushedFilters: [IsNotNull(region), EqualTo(region,EU), EqualTo(year,2023)]
ReadSchema: struct<customer_id:int,amount:double>
```

Both optimizations confirmed active.

## 7. Limitations

| Limitation | Description |
|---|---|
| Complex filters | Functions like `LIKE`, `IN`, or UDFs may not push down fully, or at all |
| Non-columnar formats | CSV and JSON have weak or no pushdown/pruning support |
| Nested structures | Deeply nested columns can limit how finely pruning works |
| Caching | Once data is cached in memory, pushdown/pruning no longer apply — Spark is reading from the cache, not the original source |

## 8. Practical Recommendations
- Prefer Parquet/Delta/ORC for real pushdown and pruning support.
- Avoid wrapping filter columns in functions (e.g. `LOWER(col)`) — this usually blocks pushdown.
- Always verify with `df.explain(True)` rather than assuming an optimization applied.
- Partition large tables by frequently-filtered columns (`year`, `region`, etc.) to make pruning effective.
- Compact small files with Delta's `OPTIMIZE` — pruning is less effective across many tiny files.

## 9. Summary Table

| Concept | Scope | Optimizes | Example | Storage Impact | Visible In |
|---|---|---|---|---|---|
| Predicate Pushdown | Row level | Fewer rows read | `WHERE country='India'` | Lower I/O | `PushedFilters` |
| Column Pruning | Column level | Fewer columns read | `SELECT col1, col2` | Lower I/O | `ReadSchema` |
| Data Skipping / File Pruning (Delta) | File level | Entire files skipped | Based on transaction-log stats | Largest single gain | Delta transaction log / query plan |

## 10. TL;DR
- **Predicate Pushdown** — filters applied at the storage layer, before rows fully materialize.
- **Column Pruning** — only the referenced columns are read at all.
- **Data Skipping (Delta)** — whole files are skipped using transaction-log metadata, before either of the above even runs.
- Together, they minimize data movement and maximize query efficiency.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Optimization for Data Read/Predicate Pruning & Predicate Pushdown|Predicate Pushdown vs Predicate Pruning]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Optimization for Data Read/How Predicate Pushdown and Predicate Pruning Works|How Predicate Pushdown and Predicate Pruning Works]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Optimize, ZOrdering, Liquid Clustering|Optimize, Z-Ordering, Liquid Clustering]]

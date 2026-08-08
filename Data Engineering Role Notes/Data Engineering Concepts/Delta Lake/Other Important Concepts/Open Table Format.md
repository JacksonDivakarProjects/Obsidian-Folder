# Open Table Format

## Definition

An **Open Table Format (OTF)** is a metadata specification for large-scale analytic tables stored as files in a data lake, designed to be:

- **Open-source** — no vendor lock-in.
- **Interoperable** — readable/writable across engines (Spark, Flink, Trino, Pandas, etc.).
- **Transactional** — supports ACID guarantees like a database.
- **Versioned** — you can time-travel to earlier snapshots of the data.

In short, it brings database-like capabilities (transactions, schema evolution, auditing) to plain files sitting on object storage (S3, HDFS, ADLS, etc.).

## Why It Exists

Traditional data lakes stored raw files (Parquet, ORC, CSV) directly — fast and cheap, but with no transactional control and no schema management. Concurrent writers could easily corrupt data, and there was no reliable way to know which files made up a "table" at a given point in time.

Open Table Formats close this gap by adding a **metadata layer** on top of the file format that tracks versions, additions, deletions, and schema — turning a folder of files into something that behaves like a table.

## Popular Open Table Formats

| Format | Originated At | Key Features |
|---|---|---|
| **Delta Lake** | Databricks | Strong ACID transactions via a JSON transaction log, time travel, schema enforcement/evolution |
| **Apache Iceberg** | Netflix / Apache | Partition evolution without rewriting data, hidden metadata/manifest tables, scalable commits for huge tables |
| **Apache Hudi** | Uber | Incremental processing, built-in CDC support, optimized for streaming ingestion and upserts |

## Core Concepts

1. **Metadata layer** — tracks every data file, version, schema, and commit.
2. **Manifest / snapshot** — describes exactly which files belong to the table's current version.
3. **Transaction log** — records every insert, update, or delete as an atomic entry.
4. **Schema evolution** — lets you add or remove columns without breaking existing queries.
5. **Time travel** — lets you query past table versions for debugging, auditing, or reproducing a report.

## Example (Delta Lake)

```python
# Write a Delta table
df.write.format("delta").save("/data/sales")

# Update data
df_new.write.format("delta").mode("overwrite").save("/data/sales")

# Read a previous version
spark.read.format("delta").option("versionAsOf", 1).load("/data/sales")
```

Here, version 1 is an earlier snapshot of the dataset that you can query at any time (as long as its underlying files haven't been vacuumed).

## Why It Matters

Open Table Formats are the foundation of the **lakehouse architecture** — combining the scalability and low cost of a data lake with the reliability and structure of a data warehouse, and unifying batch and streaming processing on the same storage.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Delta Lake Uniform Format|Delta Lake Uniform Format (UniForm)]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Miscellaneous/Data Lake House|Data Lakehouse]]

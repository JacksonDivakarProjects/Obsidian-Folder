# Data Lakehouse

A **Data Lakehouse** is a **data lake plus an open table format layer** (Delta Lake, Apache Iceberg, or Apache Hudi) that adds structure, governance, and transactional capabilities on top of raw object storage.

## Why It Matters

A plain data lake is cheap and flexible but lacks the reliability guarantees — ACID transactions, schema enforcement, fast interactive queries — that a data warehouse provides. The lakehouse pattern closes that gap without requiring a separate, expensive warehouse copy of the data: one storage layer serves both cheap bulk storage and warehouse-grade querying.

## How It Works

### 1. Base Layer — Data Lake
- Stores raw data (structured, semi-structured, unstructured) in cheap object storage: S3, ADLS, GCS.
- Flexible and highly scalable.
- Limitations on its own: no ACID transactions, no schema enforcement, slower for frequent/interactive queries.

### 2. Open Table Format Layer — the "Lakehouse" Layer
Sits on top of the raw lake files and adds:
- **ACID transactions** — safe concurrent reads/writes.
- **Schema enforcement and evolution** — columns can be added or changed without breaking existing readers.
- **Versioning / time travel** — query past states of a table.
- **Query optimization** — caching, indexing, and partitioning for performance.

Tools: Delta Lake, Apache Iceberg, Apache Hudi.

### 3. Outcome — the Lakehouse
- Looks like a data warehouse to users: fast queries, structured tables, reliable results.
- Stays as cheap as a data lake, because the underlying storage is still commodity object storage.
- Supports both BI reporting and ML/analytics workloads on the same copy of data — no need to move or duplicate it into a separate warehouse.

## Key Point

> The lakehouse is not a new storage system — it's a management and transactional layer on top of an existing data lake that makes it behave like a warehouse.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Open Table Format|Open Table Format]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Miscellaneous/Fundamentals Of Data Engineering|Fundamentals Of Data Engineering]]

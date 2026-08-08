# Clustered vs. Non-Clustered Columnstore Index (CCI vs. NCCI)

> Scope: columnstore indexes are a SQL Server / Azure Synapse Analytics feature (also present in similar form in some other warehouse engines). PostgreSQL and MySQL don't have a built-in columnstore index type — this note applies specifically to SQL Server-family databases.

The core difference is what happens to the original table. Think of it like a library: a **Clustered Columnstore Index (CCI)** replaces the physical books on the shelf with digital files, while a **Non-Clustered Columnstore Index (NCCI)** adds a digital kiosk alongside the shelf — the physical books stay exactly where they were.

## 1. Clustered Columnstore Index (CCI)

A CCI *is* the table. Creating one deletes the original row-based storage (heap or B-tree) and converts the data into compressed columnstore format.

- **Storage:** the only copy of the data.
- **Columns:** automatically includes every column in the table.
- **Primary use:** large fact tables in data warehouses, where you need maximum compression and fast analytical scans.
- **Updatability:** fully updatable in modern versions, but heavy `INSERT`/`UPDATE` traffic causes rows to pile up in the delta store (see [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Indexing/What is Delta Store|What is Delta Store]]) faster than the background compressor can clear them, which shows up as degraded scan performance until it catches up.

## 2. Non-Clustered Columnstore Index (NCCI)

An NCCI is a separate object layered on top of an existing rowstore table (heap or B-tree).

- **Storage:** two copies of the data exist — the original rows (optimized for point lookups) and the columnstore index (optimized for analytics).
- **Columns:** you can index a subset of columns to save space, instead of all of them.
- **Primary use:** real-time operational analytics (HTAP) — keep the rowstore for fast OLTP transactions, and query the NCCI for reporting without slowing down the transactional workload.
- **Performance cost:** every row inserted into the base table also has to be reflected in the NCCI, adding write overhead.

## Key Comparison

| Feature | Clustered Columnstore (CCI) | Non-Clustered Columnstore (NCCI) |
|---|---|---|
| Is it the table? | Yes — replaces the underlying storage | No — a secondary copy |
| Data redundancy | Low (one copy) | High (row format + column format) |
| Column selection | All columns | A chosen subset |
| Best scenario | Data warehousing / history tables | Real-time reporting on live "active" tables |
| Read/write balance | Optimized for massive reads | Balances transactional writes with analytical reads |

## Where This Shows Up in a Data Warehouse

CCIs are typically used in the final "gold"/mart layer of a warehouse, on tables with millions or billions of rows where individual-row lookups don't matter but aggregate scans (`SUM` over a billion rows) do.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Indexing/What is Delta Store|What is Delta Store]]

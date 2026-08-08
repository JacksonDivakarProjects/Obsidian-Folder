# Optimization for Data Read

Techniques Spark and Delta Lake use to minimize how much data is actually read from disk when running a query — the foundation of query performance tuning in a lakehouse.

## 🗺️ Map of Content (auto-generated)

### Core Concepts
- [[Data Engineering Role Notes/Data Engineering Concepts/Optimization for Data Read/Predicate Pruning & Predicate Pushdown|Predicate Pushdown vs Predicate Pruning]] — side-by-side comparison table contrasting row-level pushdown with file/partition-level pruning.
- [[Data Engineering Role Notes/Data Engineering Concepts/Optimization for Data Read/How Predicate Pushdown and Predicate Pruning Works|How Predicate Pushdown and Predicate Pruning Works]] — step-by-step walkthrough of the internal mechanics in Spark/Delta, including a combined-flow example.
- [[Data Engineering Role Notes/Data Engineering Concepts/Optimization for Data Read/Predicate Pushdown & Column Pruning|Predicate Pushdown & Column Pruning]] — comprehensive guide covering pushdown, column pruning, Delta's data-skipping, verification via `explain(True)`, limitations, and best practices.

### Related (outside this folder)
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Optimize, ZOrdering, Liquid Clustering|Optimize, Z-Ordering, Liquid Clustering]] — how `OPTIMIZE`, Z-ordering, and liquid clustering make pruning more effective by physically co-locating related data.

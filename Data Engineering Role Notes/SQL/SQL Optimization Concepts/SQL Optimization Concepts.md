# SQL Optimization Concepts

Index note for this folder — query execution internals: how the engine plans and runs queries, indexing, join/sort algorithms, and table scan types.

- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Basic SQL Optimizations|Basic SQL Optimizations]] — PostgreSQL optimization roadmap: EXPLAIN ANALYZE, indexing, common anti-patterns, join strategy.
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Joins-Loops-Sorts|Joins-Loops-Sorts]] — join algorithms (nested loop, hash, merge) and the sort algorithms behind ORDER BY.
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Table Scan Types/Table Scan Types|Table Scan Types]] — sequential, index, index-only, and bitmap scans.
- **Indexing** — see [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Indexing/Difference Between Clustered Column Store and Non Clustered Column Store|clustered vs. non-clustered columnstore indexes]], [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Indexing/What is Delta Store|the columnstore delta store]], and a large [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Indexing/Indexing Images/Indexing Images|reference screenshot library]] classifying indexes by function, storage, and structure.
- **Optimization Notes** — see [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Optimization Notes/Behaviours of SQL Engine and Tips|how the SQL engine behaves]], [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Optimization Notes/Common Pitfalls in Querying|common query pitfalls]], and [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Optimization Notes/Query Plan/Query Plan Practice|real execution-plan examples]].
- **Partitioning** — reference screenshots on table/index partitioning strategies: [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Partitioning/Partitioning Images/Partitioning Images|Partitioning Images]].

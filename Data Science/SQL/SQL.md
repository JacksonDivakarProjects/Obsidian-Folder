
# Notebook Links


[[SQL DS Images]]
[[SQL Functions]]
[[Tricks and Tips]]
[[Other Important Topics]]
[[Window Functions]]
[[SQL Optimization Concepts]]
[[Recursive CTE]]
[[Stored Procedures Notes]]
[[Data Engineering Role Notes/SQL/Advanced Topics/Advanced Topics]]
[[Data Science/SQL/Miscellaneous/Miscellaneous|Miscellaneous]]


# Online Links

[Window Function Youtube Video](https://www.youtube.com/watch?v=Ww71knvhQ-s)
[Subqueries Youtube Video](https://youtu.be/nJIEIzF7tDw?si=PmxHI-l3-eWUe6yU)
[Lateral Join](https://youtu.be/NiiN63lEzvI?si=wrEEwuNrFktN49VR)
[Advanced Aggregation (Grouping set, Rollup , Cube)](https://youtu.be/Ccye_H34hBo?si=nA0-WgLnaWgh1tl3)

## 🗺️ Map of Content (auto-generated)

### Concepts To Look Next
- [[Data Science/SQL/Concepts To Look Next/Advanced Topics|Advanced Topics]] — overview roadmap of advanced SQL topics (query optimization, indexing, window functions, partitioning, transactions, joins, materialized views, JSON, big-data SQL).

### Materialized View
- [[Data Science/SQL/Materialized View/Materialized View In Postgres SQL|Materialized Views – The Complete Guide (PostgreSQL)]] — creating, refreshing, and using materialized views in PostgreSQL.

### Miscellaneous
- [[Data Science/SQL/Miscellaneous/Advanced SQL Aggregation ( Grouping , Rollup ,Cube)|Advanced SQL Aggregation ( Grouping , Rollup ,Cube)]] — GROUPING SETS, ROLLUP, and CUBE for subtotal/grand-total reporting.
- [[Data Science/SQL/Miscellaneous/Connect SQL to Jupyter Notebook|Connect SQL to Jupyter Notebook]] — using `%%sql` magic and PrettyTable to query MySQL from Jupyter.
- [[Data Science/SQL/Miscellaneous/Lateral Joins|LATERAL in SQL (PostgreSQL)]] — what LATERAL joins do and when they're needed.
- [[Data Science/SQL/Miscellaneous/Miscellaneous|Miscellaneous]] — index note linking into this folder.

### Other Keywords
- [[Data Science/SQL/Other Keywords/ALL, ANY, LIKE Keywords|SQL Keywords Quick Reference: ALL, ANY, LIKE]] — universal/existential subquery comparisons and pattern matching.
- [[Data Science/SQL/Other Keywords/SQL Exists and Not Exists|SQL EXISTS & NOT EXISTS: Quick Revision Guide]] — correlated existence checks and why NOT EXISTS beats NOT IN.

### Recursive CTE
- [[Data Science/SQL/Recursive CTE/Recursive CTE|Recursive CTE]] — index note for this folder.
- [[Data Science/SQL/Recursive CTE/Recursive CTE Notes|Comprehensive Recursive CTE Guide]] — syntax, rules, patterns (hierarchy, roll-up, path building) and performance tips.
- [[Data Science/SQL/Recursive CTE/Recursive CTE Interview Patterns|Most Used Recursive CTE Questions in Companies]] — the 6 recursive CTE patterns most asked in interviews.
- [[Data Science/SQL/Recursive CTE/Recursive CTE problem Statements|Recursive CTE problem Statements]] — practice problem list (org chart, BOM, cycles, number series, etc.).

### SQL DDL
- [[Data Science/SQL/SQL DDL/SQL DDL Examples|SQL DDL Examples]] — CREATE/ALTER TABLE, constraints, foreign keys, indexes.

### SQL DS Images
- [[Data Science/SQL/SQL DS Images/SQL DS Images|SQL DS Images]] — index linking to screenshot image collections (no textual content).
- [[Data Science/SQL/SQL DS Images/SQL DS365 Course/SQL Screenshot Images|SQL Screenshot Images]] — index of course screenshots (images only).

### SQL Functions
- [[Data Science/SQL/SQL Functions/SQL Functions|SQL Functions]] — index note for this folder.
- [[Data Science/SQL/SQL Functions/Most Frequent Functions|Most Frequent Functions]] — cheat sheet of common MySQL functions (casting, strings, numeric, aggregate, conditional, JSON).
- [[Data Science/SQL/SQL Functions/MySQL Date Functions Cheat sheet|MySQL Date Functions Cheat sheet]] — date/time retrieval, arithmetic, differences, and formatting.

### SQL Optimization Concepts
- [[Data Science/SQL/SQL Optimization Concepts/SQL Optimization Concepts|SQL Optimization Concepts]] — index note for this folder.
- [[Data Science/SQL/SQL Optimization Concepts/Basic SQL Optimizations|Basic SQL Optimizations]] — full PostgreSQL optimization roadmap (EXPLAIN ANALYZE, indexing, anti-patterns, joins).
- **Indexing**
  - [[Data Science/SQL/SQL Optimization Concepts/Indexing/Difference Between Clustered Column Store and Non Clustered Column Store|Difference Between Clustered Column Store and Non Clustered Column Store]] — CCI vs NCCI trade-offs.
  - [[Data Science/SQL/SQL Optimization Concepts/Indexing/What is Delta Store|What is Delta Store]] — the row-based staging area behind columnstore indexes.
- **Joins-Loops-Sorts**
  - [[Data Science/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Joins-Loops-Sorts|Joins-Loops-Sorts]] — index note for this sub-folder.
  - [[Data Science/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Hash Join|Hash Join]] — build/probe phases and when the optimizer picks hash joins.
  - [[Data Science/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Merge Joins|Merge Joins]] — sort-merge join algorithm and when sorted inputs make it optimal.
  - [[Data Science/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Nested Loops in SQL|Comprehensive Guide to Nested Loops in SQL]] — nested loop join mechanics and best-use cases.
  - [[Data Science/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Heap Sort|Comprehensive Guide to Heap Sort in SQL]] — how engines use heap sort internally for in-memory sorts.
  - [[Data Science/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Quick Sort|Quick Sort in SQL: A Comprehensive Guide]] — quicksort's role in in-memory ORDER BY processing.
- **Optimization Notes**
  - [[Data Science/SQL/SQL Optimization Concepts/Optimization Notes/Behaviours of SQL Engine and Tips|THE SQL ENGINE — A COMPREHENSIVE BEHAVIOR GUIDE]] — parser/optimizer/executor architecture and cost-based decision making.
  - [[Data Science/SQL/SQL Optimization Concepts/Optimization Notes/Common Pitfalls in Querying|Common Pitfalls in Querying]] — anti-patterns that block the optimizer, with fixes.
  - [[Data Science/SQL/SQL Optimization Concepts/Optimization Notes/Role in SQL|Role in SQL]] — what the engine automates vs. what the engineer is responsible for.
  - [[Data Science/SQL/SQL Optimization Concepts/Optimization Notes/Working of Index in SQL|Working of Index in SQL]] — how the optimizer chooses and traverses indexes (seek, range, bitmap).
  - [[Data Science/SQL/SQL Optimization Concepts/Optimization Notes/Query Plan/Query Plan Practice|Query Plan Practice]] — annotated real-world EXPLAIN plans (index seek, hash/merge join, sort spill, CTE materialization).
  - [[Data Science/SQL/SQL Optimization Concepts/Optimization Notes/Query Plan/Query Plan Practice -2|SQL EXECUTION PLAN LIBRARY (20 Real World Examples)]] — a 20-pattern library of execution plans across index, join, sort, and subquery categories.
- **Table Scan Types**
  - [[Data Science/SQL/SQL Optimization Concepts/Table Scan Types/Table Scan Types|Table Scan Types]] — index note for this sub-folder.
  - [[Data Science/SQL/SQL Optimization Concepts/Table Scan Types/Index and Index Only Scan|Comprehensive Guide: Index Scan vs Index-Only Scan in SQL]] — when a table lookup is needed vs. avoided via covering indexes.
  - [[Data Science/SQL/SQL Optimization Concepts/Table Scan Types/Sequential Scan|Comprehensive Guide to Sequential Scan in SQL]] — full table scans: when they occur and how to avoid unwanted ones.
  - [[Data Science/SQL/SQL Optimization Concepts/Table Scan Types/Bitmap Scan/Bitmap Heap Scan|Comprehensive Guide: Bitmap Heap Scan in PostgreSQL]] — fetching table rows from a bitmap of qualifying positions.
  - [[Data Science/SQL/SQL Optimization Concepts/Table Scan Types/Bitmap Scan/Bitmap Index Scan|Bitmap Index Scan]] — building bitmaps from index scans and combining them with AND/OR.
  - [[Data Science/SQL/SQL Optimization Concepts/Table Scan Types/Bitmap Scan/Explained with Analogy|Explained with Analogy]] — heap pages, TIDs, and bitmap scans explained conceptually.
  - [[Data Science/SQL/SQL Optimization Concepts/Table Scan Types/Differences among Scans/Difference between Index and Index Only Scan|Difference between Index and Index Only Scan]] — quick side-by-side comparison.

### SQL SubQueries
- [[Data Science/SQL/SQL SubQueries/SQL SubQueries|Comprehensive Guide to SQL Subqueries]] — scalar, correlated, EXISTS, and table subqueries with best practices.

### Set Operation in SQL
- [[Data Science/SQL/Set Operation in SQL/Set Operations in SQL|Comprehensive Guide to Set Operations in SQL]] — UNION, UNION ALL, INTERSECT, EXCEPT/MINUS with real-world use cases.

### Stored Procedures in Postgres
- [[Data Science/SQL/Stored Procedures in Postgres/Stored Procedures in Postgres|Stored Procedures in Postgres]] — index note for this folder.
- [[Data Science/SQL/Stored Procedures in Postgres/Stored Procedures Notes|Comprehensive Beginner's Guide to PostgreSQL Stored Procedures]] — full walkthrough: syntax, variables, control flow, error handling, parameters.
- [[Data Science/SQL/Stored Procedures in Postgres/IN, OUT, INOUT Parameters|Comprehensive Guide to IN, OUT, and INOUT Parameters in PostgreSQL]] — parameter modes with real-world procedure examples.
- [[Data Science/SQL/Stored Procedures in Postgres/Question & Answers of SP|Question & Answers of SP]] — Q&A on `:=` assignment, capturing OUT parameters, and default parameter modes.

### Tricks and Tips
- [[Data Science/SQL/Tricks and Tips/Tricks and Tips|Tricks and Tips]] — index note for this folder.
- [[Data Science/SQL/Tricks and Tips/Group By and Having Tricks|Group By and Having Tricks]] — GROUP BY + window functions, and HAVING + conditional aggregation patterns.
- [[Data Science/SQL/Tricks and Tips/Master Class SQL Tricks|SQL Masterclass – Comprehensive Revision Guide]] — CASE aggregation, COUNT/DISTINCT nuances, NULL handling, subquery aliasing.
- [[Data Science/SQL/Tricks and Tips/Master Class SQL Tricks Part -2|Master Class SQL Tricks Part -2]] — recent tips on COUNT(DISTINCT ...), grouping granularity, and time filters.

### Triggers in SQL
- [[Data Science/SQL/Triggers in SQL/Triggers in SQL|SQL Triggers — Comprehensive Beginner-Level Guide]] — BEFORE/AFTER triggers, NEW/OLD, and standard examples (timestamps, validation, audit logs).

### Views in SQL
- [[Data Science/SQL/Views in SQL/Views in SQL|SQL Views – The Complete Guide]] — creating/updating views, updatability rules, and WITH CHECK OPTION.

### Window Functions
- [[Data Science/SQL/Window Functions/Window Functions|Window Functions]] — index note for this folder.
- [[Data Science/SQL/Window Functions/SQL Window Functions and Aggregate Examples|SQL Window Functions and Aggregate Examples]] — ROW_NUMBER, RANK, DENSE_RANK, LAG/LEAD examples.
- [[Data Science/SQL/Window Functions/SQL Window Function - 2|Comprehensive Guide to SQL Window Functions]] — OVER() clause, FIRST/LAST/NTH_VALUE, NTILE, CUME_DIST, PERCENT_RANK, and the WINDOW clause.

# Table Scan Types

Index note for this folder — the physical strategies PostgreSQL (and similar engines) use to read rows off disk.

- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Table Scan Types/Sequential Scan|Comprehensive Guide to Sequential Scan in SQL]] — read every row of the table; the fallback when no useful index exists.
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Table Scan Types/Index and Index Only Scan|Comprehensive Guide: Index Scan vs Index-Only Scan in SQL]] — seek via an index, with or without a table (heap) lookup.
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Table Scan Types/Bitmap Scan/Bitmap Index Scan|Bitmap Index Scan]] — build a bitmap of matching row locations from an index.
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Table Scan Types/Bitmap Scan/Bitmap Heap Scan|Comprehensive Guide: Bitmap Heap Scan in PostgreSQL]] — fetch table rows using that bitmap, minimizing random I/O.
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Table Scan Types/Bitmap Scan/Explained with Analogy|Explained with Analogy]] — heap pages, TIDs, and how bitmap and index scans relate, walked through step by step.
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Table Scan Types/Differences among Scans/Difference between Index and Index Only Scan|Difference between Index and Index Only Scan]] — quick side-by-side comparison.

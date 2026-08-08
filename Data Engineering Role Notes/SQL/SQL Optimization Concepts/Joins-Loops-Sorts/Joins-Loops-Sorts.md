# Joins-Loops-Sorts

Index note for this folder — the physical algorithms a query planner chooses between when executing joins and sorts.

- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Nested Loops in SQL|Comprehensive Guide to Nested Loops in SQL]] — for every outer row, scan the inner table; simple, flexible, best with a small/indexed inner side.
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Hash Join|Hash Join]] — build a hash table from the smaller input, probe it with the larger; fast for large, unsorted, unindexed equijoins.
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Merge Joins|Merge Joins]] — walk two sorted inputs in lockstep; efficient when both sides are already ordered on the join key.
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Heap Sort|Comprehensive Guide to Heap Sort in SQL]] — an in-memory sort algorithm engines may use internally for `ORDER BY`/index builds.
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Quick Sort|Quick Sort in SQL: A Comprehensive Guide]] — the other common in-memory sort; engines fall back to external merge sort once data spills to disk.

# Hash Join

A hash join is a physical join operation the database engine uses to combine rows from two tables based on an equality condition, particularly effective on large datasets without a useful index on the join columns.

## How It Works

Hash join runs in two phases:

- **Build phase:** the engine scans the smaller of the two inputs (the "build" input) and constructs an in-memory hash table keyed on the join column.
- **Probe phase:** the engine scans the larger input (the "probe" input) row by row, computes the hash of its join key, and looks up matches in the hash table. Matches are combined into the result set.

## When It's Used

- Chosen by the optimizer when one or both tables are large and there's no useful index on the join column(s).
- Efficient specifically for **equijoins** (`=` conditions) — it doesn't help with range or inequality joins.
- Doesn't require either input to be pre-sorted (unlike a merge join).
- If the build input is too large to fit in memory, the engine falls back to a **grace hash join**: both inputs are partitioned (e.g., by a hash of the join key) and matching partition pairs are joined one at a time, so only one partition's build side needs to be in memory at once.

## Example

```sql
SELECT *
FROM Orders
JOIN Customers ON Orders.CustomerID = Customers.CustomerID;
```

If the optimizer picks a hash join here, it builds a hash table from the smaller table (say, `Customers`, keyed on `CustomerID`), then probes it once per `Orders` row.

## Advantages and Disadvantages

| Advantages | Disadvantages |
|---|---|
| Fast for large tables | Needs memory for the hash table |
| Doesn't require sorted or indexed inputs | Performance degrades (spills to disk) if the hash table doesn't fit in memory |
| Handles equijoins efficiently regardless of row order | Only works for equality conditions |

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Merge Joins|Merge Joins]]
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Nested Loops in SQL|Comprehensive Guide to Nested Loops in SQL]]

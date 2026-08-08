# Nested Loops in SQL

"Nested loop" in a SQL context can mean two different things:

1. **Procedural control structures** — loops inside loops in PL/SQL or similar procedural SQL extensions (`WHILE`/`FOR` nesting).
2. **Nested Loop Join** — a fundamental join algorithm the database engine uses to process joins.

This note focuses on the **nested loop join**, since it's the one that matters for query optimization.

## What Is a Nested Loop Join?

For every row in the outer (first) table, the engine scans the inner (second) table looking for matching rows. It's the simplest and most general-purpose join strategy — and the one every other join strategy is compared against.

## How It Works

1. **Outer scan:** take the next row of the outer table.
2. **Inner scan:** for that outer row, scan through rows of the inner table.
3. **Compare:** check the join condition (typically equality on a key, but any condition works).
4. **Output:** emit the pair if the condition holds.
5. **Repeat** for every outer row.

```sql
SELECT E.Name, D.DeptName
FROM Employees E
JOIN Departments D ON E.DeptID = D.DeptID;
```

For each `Employees` row, the engine searches `Departments` for a matching `DeptID` and emits a combined row on a match.

## Advantages

- **Simple** to implement and reason about.
- **Flexible** — works with any join condition, not just equality (unlike hash join).
- **Fast with small inputs**, especially when the inner table is indexed on the join column.
- **Supports every join type** — inner, outer, semi-, anti-joins.

## Disadvantages

- **Slow for large inputs.** Without an index, every outer row triggers a full scan of the inner table: time complexity O(n × m) for n outer rows and m inner rows.

## Indexed Nested Loop Join

If the inner table has an index on the join column, the engine uses it to jump straight to matching rows instead of scanning the whole inner table — turning the O(n × m) worst case into something close to O(n log m). This is the version the optimizer actually favors whenever a suitable index exists and the outer side is reasonably small or highly selective.

## Best Use Cases

- One table is small and the other is large, especially when the large table is indexed on the join key.
- Highly selective queries (the outer side filters down to few rows).
- Non-equality join conditions (ranges, `<`, `BETWEEN`) — hash and merge joins only handle equality.

## Join Algorithm Comparison

| Algorithm | When Used | Pros | Cons |
|---|---|---|---|
| Nested Loop Join | Small tables, indexed joins | Simple, flexible, works with any condition | Slow on large, unindexed inputs |
| Hash Join | Equality joins, large unsorted datasets | Fast for big data | Needs memory for the hash table |
| Merge Join | Sorted (or cheaply sortable) large datasets | Efficient, low memory | Requires sorted input |

## Key Takeaways

- Nested loop join is the foundational, always-available join strategy.
- It wins when inputs are small, selective, or well-indexed.
- Performance degrades as table sizes grow, because of the repeated inner-table scans — that's exactly when the optimizer switches to hash or merge join instead.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Hash Join|Hash Join]]
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Merge Joins|Merge Joins]]

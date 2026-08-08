# Merge Joins (Sort-Merge Join)

A merge join is an efficient join algorithm for inputs that are already sorted on the join key. It compares rows from each table sequentially and emits matches as it walks both inputs in a single pass.

## What Is a Merge Join?

Also called a sort-merge join: it combines rows from two tables that are both ordered by the join column, advancing a cursor over each side and matching as it goes. The hard requirement is that both inputs be sorted on the join key — via an index that already provides that order, or via an explicit sort step beforehand.

## Algorithm

1. **Sorting phase.** Ensure both inputs are sorted on the join column (via an index, or an explicit sort).
2. **Initialization.** Place a cursor at the start of each sorted input.
3. **Comparison and traversal**, repeated until one side is exhausted:
   - If the two cursors' keys match, emit the joined row(s) and advance both cursors.
   - If the left cursor's key is smaller, advance the left cursor.
   - If the right cursor's key is smaller, advance the right cursor.
4. **Duplicate keys.** When either side has duplicate join-key values, the algorithm produces every combination of matching rows from both sides before advancing past that key.

## Worked Example

`Customers(CustomerID, Name)` and `Orders(OrderID, CustomerID)`, both sorted by `CustomerID`:

| Customers | Orders |
|---|---|
| 1, Alice | 101, 1 |
| 2, Bob | 102, 2 |
| 3, Dave | 103, 3 |

The cursors start at `CustomerID = 1` on both sides, match, emit the joined row, and both advance. If the next keys don't match, whichever cursor holds the smaller key advances alone. The scan continues to the end of either input.

## When to Use It

- Both inputs are already sorted on the join key (e.g., via a supporting index), or sorting them is cheap.
- Large datasets with equi-join conditions.
- Inputs of similar size, read sequentially (e.g., off disk) rather than randomly.

## Best Practices

- Favor a merge join when the join columns are indexed or naturally ordered by the join key already.
- Avoid it when inputs are unsorted and sorting them would be expensive — a hash join or nested loop join is often cheaper in that case.
- For tables with very different sizes and no natural ordering, hash join or nested loop join usually wins.

## Typical Query Shape

Merge join is a plan the optimizer *chooses*, not something you request directly — but a query like this is a natural candidate when both tables are indexed on `CustomerID`:

```sql
SELECT Customers.Name, Orders.OrderID
FROM Customers
JOIN Orders ON Customers.CustomerID = Orders.CustomerID
ORDER BY Customers.CustomerID;
```

## Advantages and Limitations

| Aspect | Merge Join |
|---|---|
| Performance | Excellent for large, already-sorted inputs |
| Memory usage | Low — doesn't need to load all rows into memory at once |
| Parallelism | Parallelizes well when data is partitioned |
| Duplicate handling | Correctly produces all combinations of duplicate keys |
| Sorting requirement | Both inputs must be sorted on the join key |
| Join type support | Efficient for inner and outer equi-joins |

## Typical Use Cases

- Data-warehouse joins where fact and dimension tables are both sorted/indexed on the join key.
- ETL batch joins over already-sorted data sources.
- Large reporting queries against well-indexed tables.

## Summary

Merge join minimizes computational overhead on sorted inputs by scanning each side exactly once instead of repeatedly re-scanning (as nested loop does) or building an auxiliary structure (as hash join does). Its cost is the sorting requirement — when that's already satisfied, it's typically the cheapest option available to the planner.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Hash Join|Hash Join]]
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Nested Loops in SQL|Comprehensive Guide to Nested Loops in SQL]]

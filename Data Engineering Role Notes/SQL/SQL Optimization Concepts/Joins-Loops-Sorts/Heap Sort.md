# Heap Sort in SQL Engines

Heap sort is a comparison-based sorting algorithm built on the binary-heap data structure. SQL has no syntax that invokes it directly, but engines can use it internally for certain in-memory sorts — small-to-moderate result sets that fit comfortably in the memory grant for a query.

## What Is Heap Sort?

It organizes elements into a binary heap — a complete binary tree where every parent is greater than (max-heap) or less than (min-heap) its children. That property makes the max (or min) element always available at the root, so it can be pulled off in O(log n) after each removal.

## Algorithm Steps

1. **Build a heap.** Convert the unsorted values into a max-heap (for ascending output) or min-heap (for descending). In a max-heap, the largest value ends up at the root.
2. **Repeatedly remove the root.** Swap the root with the last element in the heap, shrink the heap by one, then "heapify" (sift down) to restore the heap property.
3. **Continue until the heap is empty.** The values pulled off, in order, are the sorted sequence.

### Worked Example

Input: `[4, 10, 3, 5, 1]`

1. Build max-heap → `[10, 5, 4, 3, 1]`
2. Swap root (10) with the last element, shrink, heapify → `[5, 3, 4, 1] | 10`
3. Repeat: swap root (5) with last, shrink, heapify → `[4, 3, 1] | 5, 10`
4. Continue until fully unwound → sorted ascending: `[1, 3, 4, 5, 10]`

## Where SQL Engines Use It

- For in-memory sorts backing operations like `ORDER BY` or index builds, when the working set fits in the memory allotted to the query.
- Not used for sorts that spill to disk — those fall back to an external (disk-based) merge sort instead.
- The choice of algorithm is made automatically by the engine based on data size, memory pressure, and hardware; there's no SQL syntax to force heap sort specifically.

## Strengths and Limitations

| Strengths | Limitations |
|---|---|
| Time complexity O(n log n) | Not a stable sort (doesn't guarantee original order of equal elements) |
| Space complexity O(1) — sorts in place | Usually slower in practice than quicksort for small datasets |
| Predictable, consistent performance (no quadratic worst case) | Not ideal for already-partially-sorted data |

## Heap Sort vs. Merge Sort in SQL

- **Heap sort** — small, in-memory sorts; constant extra space.
- **Merge sort** — used once data spills to disk ("external sort"); handles massive tables but needs more working space.

## Key Takeaways

- Heap sort repeatedly extracts the max (or min) from a heap structure to produce sorted output.
- It suits in-memory sorting of moderate-sized data inside the engine.
- SQL queries never expose the choice of sort algorithm directly — it's an internal execution-plan detail you can only observe via `EXPLAIN`/execution-plan tools, not control.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/Joins-Loops-Sorts/Quick Sort|Quick Sort in SQL: A Comprehensive Guide]]

# `repartition()` vs `coalesce()`

A subtle but important distinction. Both change the number of partitions in a DataFrame/RDD, but they serve different purposes and carry different performance trade-offs.

### 🔹 `repartition(n)`

- **Shuffles data across the cluster.**
- Can **increase or decrease** the number of partitions.
- Produces **evenly balanced partitions**.
- **Expensive** — triggers a full shuffle.
- Useful when:
    - You want balanced load across executors.
    - You're increasing partitions for more parallelism.
    - You're preparing data for a wide transformation (like a join).

### 🔹 `coalesce(n)`

- **Does not shuffle by default.**
- Can **only reduce** the number of partitions.
- Simply **merges existing partitions** into fewer ones.
- **Much cheaper** than `repartition()`.
- Trade-off: partitions can become **uneven** (data skew risk).
- Useful when:
    - Data is already shuffled (after a `groupBy` or `join`) and you just want fewer output files.
    - Writing final output and wanting fewer files (e.g. `coalesce(1)` for a single file).
    - Performance matters more than perfectly even distribution.

### ⚡ Why Both Exist

They trade off fairness against efficiency:

- `repartition()` → guarantees balance, at high cost.
- `coalesce()` → minimizes shuffle cost, at the risk of imbalance.

The right choice depends on the workload:
- Load balancing matters → `repartition()`.
- Shuffle cost is the bottleneck and some imbalance is tolerable → `coalesce()`.

**Mental model:**
- `repartition` = expensive restructuring, guaranteed balance.
- `coalesce` = cheap merging, possibly uneven.

### Seeing the Difference

```python
df = spark.range(0, 1000000).repartition(8)
print(df.rdd.getNumPartitions())  # 8

# coalesce only reduces, and skips the shuffle
coalesced = df.coalesce(4)
print(coalesced.rdd.getNumPartitions())  # 4
coalesced.explain()  # No Exchange node - no shuffle

# repartition can both increase and decrease, and always shuffles
repartitioned = df.repartition(4)
repartitioned.explain()  # Exchange node present - shuffle happened

# coalesce cannot increase partition count - asking for more than
# the current count is a silent no-op
same_df = df.coalesce(20)
print(same_df.rdd.getNumPartitions())  # still 8, not 20
```

Use `explain()` to confirm: a shuffle shows up as an `Exchange` node in the physical plan. `coalesce()` to fewer partitions won't produce one; `repartition()` always will.

## 🔗 Related Notes
- [[Performance & Optimisation in Pyspark|Performance & Optimisation in Pyspark]]
- [[Broadcasting in Pyspark|Broadcasting in Pyspark]]

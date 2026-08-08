# Schema Management in Spark / Delta Lake

Three related but distinct behaviors govern how a Delta table's schema reacts to incoming data: **enforcement**, **evolution**, and **overwrite**. Knowing which one is active (and which one you want) matters a lot for data quality.

## 1. Schema Enforcement (Strict Schema) — the Default

**Definition:** incoming data must strictly conform to the table's defined schema. Any mismatch — an extra column, a missing column, or a type mismatch — is rejected and the write fails.

**Key points:**
- Protects data quality by rejecting invalid records outright.
- Prevents silent schema drift.
- Applies at write time (and at table creation).

```python
df.write.format("delta").mode("append").save("/delta/table")
```

If `df` has a column that doesn't match the table's schema (wrong type, unexpected name), the write fails rather than silently coercing or dropping data.

**Pro tip:** define column types explicitly upstream — this is what prevents silent type coercion from causing subtle bugs downstream.

## 2. Schema Evolution (Flexible Schema)

**Definition:** the table automatically accepts new columns from incoming data, without breaking the existing pipeline or table.

**Key points:**
- Enables dynamic schema growth for append operations.
- Adds new columns; it does not delete or reorder existing ones.
- Opt-in via the `mergeSchema` write option:

```python
df.write.option("mergeSchema", "true").format("delta").mode("append").save("/delta/table")
```

Delta automatically adds any new columns present in `df` to the table's schema.

**Use cases:**
- Upstream JSON/Parquet sources occasionally add optional columns.
- You want the pipeline to scale without manually altering the table every time a new field shows up.

**Pro tip:** use `mergeSchema` deliberately, not by default — uncontrolled schema evolution across many pipelines can cause schema drift that's hard to reason about later.

## 3. Schema Overwrite

**Definition:** replaces the table's existing schema entirely with the incoming DataFrame's schema at write time.

**Key points:**
- Useful when a table needs a structural redesign or a column's type needs to change.
- Requires both `overwriteSchema` and `mode("overwrite")`:

```python
df.write.option("overwriteSchema", "true").format("delta").mode("overwrite").save("/delta/table")
```

- This replaces both the schema **and** the data (since it's paired with `mode("overwrite")`).

**Cautions:**
- Overwriting the schema can drop existing columns that aren't present in the new DataFrame — this is destructive if done carelessly in production.
- Always have a backup or a prior table version (time travel) available before performing a schema overwrite.

```python
# Overwrite the schema (and data)
df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .save("/delta/table")
```

## Summary

| Feature | Behavior | Spark / Delta Syntax | Use Case |
|---|---|---|---|
| Schema Enforcement | Rejects invalid/mismatched data | Default behavior | Prevent dirty data from landing |
| Schema Evolution | Adds new columns automatically | `.option("mergeSchema", "true")` | Flexible append pipelines |
| Schema Overwrite | Replaces the table's schema entirely | `.option("overwriteSchema", "true").mode("overwrite")` | Table redesign or schema correction |

## Key Takeaways

1. **Schema enforcement** — safe and strict; the right default for core tables.
2. **Schema evolution** — flexible; adds new columns dynamically for append-heavy pipelines.
3. **Schema overwrite** — powerful but destructive if misused; can silently drop columns.
4. **Best practice:** enforce on core/critical tables, evolve on append pipelines that expect optional new fields, and reserve overwrite for deliberate, backed-up schema migrations.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Consistency in Delta Lake|Consistency in Delta Lake]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Upsert In DeltaLake|DeltaTable Upsert in PySpark]]

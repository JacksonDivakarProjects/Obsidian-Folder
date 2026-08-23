# Backdated Refresh

## 1. Definition

**Backdated refresh** = reprocessing a specific historical time range to correct or recompute past data.

- Not latest-only (that's incremental load)
- Not a full rebuild (that's full load)
- It is **selective historical recomputation**

## 2. Where It Fits Among Load Strategies

| Type | Scope | Purpose |
|---|---|---|
| Incremental | New data only | Efficiency |
| Full load | Entire dataset | Rebuild |
| Backdated refresh | Past subset | Correction |

## 3. Why It's Needed

- **Data correction** — fix wrong historical values.
- **Late-arriving data** — events arrive after their actual event timestamp.
- **Logic change** — transformation rules were updated and history needs to reflect the new logic.
- **CDC inconsistency** — missed or misordered change events need to be replayed.

## 4. Core Mechanism

```text
Select time range → replay data → recompute → overwrite/merge
```

## 5. Implementation Patterns

### 5.1 Batch Pipelines (Non-CDC)

```python
df = spark.read.table("source") \
    .filter("event_date BETWEEN '2024-01-01' AND '2024-01-05'")
```

Reprocess the selected range, then overwrite or merge it into the target table.

### 5.2 Partition Overwrite (Common Pattern)

```python
df.write \
  .mode("overwrite") \
  .option("replaceWhere", "event_date BETWEEN '2024-01-01' AND '2024-01-05'") \
  .saveAsTable("target")
```

Only the affected partitions are replaced — efficient and controlled, since untouched partitions are left alone.

### 5.3 CDC Pipelines (DLT / Streaming)

Here, backdated refresh means **replaying CDC events from an earlier point in time**. Key elements that must be defined:

- `sequence_by` — ordering of events.
- Keys — row identity.
- Operation column — the action (insert/update/delete) each event represents.

## 6. In Delta Live Tables (DLT)

**Option 1 — Full refresh:** replays the table's entire history. Equivalent to a full rebuild; simple but expensive.

**Option 2 — Controlled backdated logic:** filter the source stream to just the window that needs correcting:

```python
@dp.view
def source_filtered():
    return (
        spark.readStream.table("source_cdf")
        .filter("event_timestamp >= '2024-01-01'")
    )
```

## 7. With Auto CDC

```python
dp.create_auto_cdc_flow(
  target="target_table",
  source="source_filtered",
  keys=["id"],
  sequence_by=col("event_timestamp"),
  stored_as_scd_type=1
)
```

Effect: reapplying the filtered CDC events recomputes the target table's state for that period.

## 8. Key Technical Requirements

- **Deterministic ordering** — `sequence_by = col("event_timestamp")`. Without correct ordering, replay produces inconsistent results.
- **Idempotency** — re-running the refresh must not corrupt or duplicate data; merge logic has to be stable across repeated runs.
- **Partition awareness** — target the specific partitions affected whenever possible, rather than touching the whole table.

## 9. Risks

- **Duplicate data** — if merge logic isn't used (plain append/overwrite instead).
- **Wrong state** — if event ordering is incorrect.
- **Data loss** — if overwrite conditions are wrong and unintended partitions get replaced.
- **High cost** — reprocessing historical data at scale is expensive in compute and I/O.

## 10. Best Practices

- **Use merge, not blind overwrite** — ensures correctness when replaying CDC.
- **Always define ordering** — `sequence_by` is mandatory for correct CDC replay.
- **Limit scope** — reprocess only the necessary time window, not more.
- **Validate after refresh** — check row counts, key consistency, and aggregates against expectations.

## 11. Mental Model

Past data is not immutable — it can be recomputed, as long as the system is designed to support replay (deterministic ordering, idempotent writes, scoped reprocessing).

## 12. Example Timeline

```text
Day 1 → processed
Day 2 → processed
Day 3 → processed
```

An error is found in Day 2's data. A backdated refresh reprocesses Day 2 through Day 3 (since Day 3 may depend on Day 2's corrected output).

## 13. When to Use

- Data is wrong.
- Data is incomplete.
- Transformation logic has changed.
- CDC replay is needed to fix missed/misordered events.

## 14. When Not to Use

- Only new data needs loading → use incremental load instead.
- The entire dataset is corrupted → use a full load instead.

## 15. Final Model

```text
Incremental        → forward only
Full load          → everything
Backdated refresh  → selective rewind + recompute
```

> Backdated refresh is controlled re-execution of pipeline logic on historical data, to restore correctness without rebuilding everything.

## 🔗 Related Notes
- [[AutoCDC in DLT|AutoCDC in DLT]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Questions/How Versioning Works in Delta Lake|How Versioning Works in Delta Lake]]

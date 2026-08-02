## Backdated Refresh — Comprehensive Guide

---

## 1. Definition

Backdated refresh = **reprocessing a specific historical time range** to correct or recompute past data.

```text
Not latest-only (incremental)
Not full rebuild (full load)
→ selective historical recomputation
```

---

## 2. Position among load strategies

|Type|Scope|Purpose|
|---|---|---|
|Incremental|New data only|Efficiency|
|Full load|Entire dataset|Rebuild|
|Backdated refresh|Past subset|Correction|

---

## 3. Why it is required

### 3.1 Data correction

- Fix wrong historical values
    

### 3.2 Late arriving data

- Events arrive after their actual timestamp
    

### 3.3 Logic change

- Transformation rules updated
    

### 3.4 CDC inconsistency

- Missed or misordered events
    

---

## 4. Core mechanism

```text
Select time range → replay data → recompute → overwrite/merge
```

---

## 5. Implementation patterns

### 5.1 Batch pipelines (non-CDC)

```python
df = spark.read.table("source") \
    .filter("event_date BETWEEN '2024-01-01' AND '2024-01-05'")
```

- Reprocess selected range
    
- Overwrite or merge into target
    

---

### 5.2 Partition overwrite (common pattern)

```python
df.write \
  .mode("overwrite") \
  .option("replaceWhere", "event_date BETWEEN '2024-01-01' AND '2024-01-05'") \
  .saveAsTable("target")
```

- Only affected partitions replaced
    
- Efficient and controlled
    

---

### 5.3 CDC pipelines (DLT / streaming)

Backdated refresh = **replaying CDC from earlier point**

Key elements:

- `sequence_by` → ordering
    
- keys → identity
    
- operation column → action
    

---

## 6. In Delta Live Tables (DLT)

### Option 1: Full refresh

- Replays entire history
    
- Equivalent to full rebuild
    

---

### Option 2: Controlled backdated logic

Filter source:

```python
@dp.view
def source_filtered():
    return (
        spark.readStream.table("source_cdf")
        .filter("event_timestamp >= '2024-01-01'")
    )
```

- Replays only selected range
    

---

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

Effect:

```text
Reapply CDC events → recompute table state for that period
```

---

## 8. Key technical requirements

### 8.1 Deterministic ordering

```python
sequence_by = col("event_timestamp")
```

Without ordering → inconsistent results

---

### 8.2 Idempotency

- Re-running should not corrupt data
    
- Merge logic must be stable
    

---

### 8.3 Partition awareness

- Target specific partitions when possible
    

---

## 9. Risks

### Duplicate data

- If not using merge logic
    

### Wrong state

- If ordering is incorrect
    

### Data loss

- If overwrite conditions are wrong
    

### High cost

- Reprocessing historical data is expensive
    

---

## 10. Best practices

### Use merge instead of overwrite

```text
Ensures correctness with CDC
```

---

### Always define ordering

```text
sequence_by is mandatory for CDC replay
```

---

### Limit scope

```text
Reprocess only necessary time window
```

---

### Validate after refresh

- Row counts
    
- Key consistency
    
- Aggregates
    

---

## 11. Mental model

```text
Past data is not immutable
→ can be recomputed
→ system must support replay
```

---

## 12. Example timeline

```text
Day 1 → processed
Day 2 → processed
Day 3 → processed
```

Error found in Day 2.

Backdated refresh:

```text
Reprocess Day 2 → Day 3
```

---

## 13. When to use

Use backdated refresh when:

- Data is wrong
    
- Data is incomplete
    
- Logic has changed
    
- CDC replay is needed
    

---

## 14. When not to use

Avoid when:

- Only new data is needed → use incremental
    
- Entire dataset corrupted → use full load
    

---

## 15. Final model

```text
Incremental → forward only
Full load → everything
Backdated refresh → selective rewind + recompute
```

---

## Final principle

Backdated refresh is:

> Controlled re-execution of pipeline logic on historical data to restore correctness without rebuilding everything.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Delta Live Tables/AutoCDC API/AutoCDC in DLT|AutoCDC in DLT]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Questions/How Versioning Works in Delta Lake|How Versioning Works in Delta Lake]]

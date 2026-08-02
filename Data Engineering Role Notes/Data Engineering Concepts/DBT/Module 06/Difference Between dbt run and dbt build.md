
### **`dbt run` vs `dbt build` — the real difference (no ambiguity)**

Let’s cut straight to value.

---

## Executive summary

- **`dbt run`** → _Only builds models_
    
- **`dbt build`** → _Builds models **and** enforces data quality_
    

That’s the core distinction.

---

## Side-by-side comparison

|Capability|`dbt run`|`dbt build`|
|---|---|---|
|Run models|✅|✅|
|Run tests|❌|✅|
|Run snapshots|❌|✅|
|Load seeds|❌|✅|
|Enforce DAG order|⚠️ partial|✅ full|
|Production-safe|❌|✅|

---

## What actually runs under the hood

### `dbt run`

```text
Models only
```

- Executes model SQL
    
- Creates / updates tables & views
    
- **No validation**
    
- Downstream models may build on bad data
    

Use case: **local development**, fast iteration.

---

### `dbt build`

```text
Seeds → Snapshots → Models → Tests
```

- Builds data
    
- Versions history (snapshots)
    
- **Stops the pipeline if tests fail**
    
- Respects full dependency graph
    

Use case: **CI, production, scheduled jobs**

---

## Why `dbt build` is the industry default now

Because production pipelines must:

- Prevent bad data from propagating
    
- Track historical changes
    
- Fail fast when quality breaks
    

`dbt run` cannot do that alone.

---

## Databricks-specific clarity

Both commands:

- Execute real SQL in Databricks
    
- Modify Delta tables
    
- Consume compute
    

**Difference is scope, not impact.**

---

## Straight professional phrasing (use this)

> “`dbt run` focuses on model execution, whereas `dbt build` is a full-pipeline command that includes seeds, snapshots, and tests to enforce data quality.”

That statement is interview-safe.

---

## Practical recommendation

- **Developing a model** → `dbt run --select model_name`
    
- **Merging to main / prod job** → `dbt build`
    
- **Hotfix** → targeted `dbt build --select model+`
    

---

## Final takeaway

If you care about **correctness, auditability, and governance**:  
👉 **`dbt build` is non-negotiable.**

If you want, next I can explain:

- `dbt build` vs `dbt compile`
    
- Why tests don’t change data
    
- How to reduce runtime in Databricks
    

Say the next topic.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 06/DBT Flags|dbt Flags That Actually Matter]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 04/Test Execution, Severity & the `dbt build` Command|Test Execution, Severity & the dbt build Command]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 06/Plus Dependency Operator|What `+` Means in dbt Selection]]

### **`dbt run` vs `dbt build` — the real difference**

## Executive summary

- **`dbt run`** → builds models only.
- **`dbt build`** → builds models **and** enforces data quality (tests, snapshots, seeds) in dependency order.

## Side-by-side comparison

| Capability | `dbt run` | `dbt build` |
|---|---|---|
| Run models | Yes | Yes |
| Run tests | No | Yes |
| Run snapshots | No | Yes |
| Load seeds | No | Yes |
| Enforce full DAG order across resource types | Partial (models only) | Yes |
| Stops on failing tests before downstream builds | No | Yes |

## What actually runs under the hood

### `dbt run`
- Executes model SQL only.
- Creates/updates tables and views.
- No validation: if a model's data quietly breaks a business rule, `dbt run` doesn't know and won't stop.
- Downstream models can build on top of bad data without any signal.

Use case: fast local iteration while actively developing a model.

### `dbt build`
Execution order: seeds → sources' freshness (if configured) → snapshots → models → tests, all interleaved per the DAG rather than run as separate phases.

- Builds each node and, where applicable, immediately runs its tests before moving to nodes that depend on it.
- Versions history via snapshots.
- Stops the pipeline (or that branch of the DAG) if a test fails with `severity: error`.
- Respects the full dependency graph across all resource types, not just models.

Use case: CI, production, and scheduled jobs — anywhere you need a guarantee that what got built also passed its checks.

## Why `dbt build` is the default for production

Production pipelines need to prevent bad data from propagating downstream, track historical changes, and fail fast when quality breaks. `dbt run` alone does none of that — it will happily build a model on top of upstream data that just failed a test, because it never runs tests at all.

## Databricks-specific note

Both commands execute real SQL against the warehouse and modify tables (Delta tables on Databricks) — the difference is in **scope** (what gets executed), not in how each individual SQL statement runs.

## Interview-ready phrasing

> "`dbt run` focuses on model execution, whereas `dbt build` is a full-pipeline command that includes seeds, snapshots, and tests to enforce data quality — and it stops the DAG when a test fails, so it's the safer choice for CI and production."

## Practical recommendation

- **Developing a model** → `dbt run --select model_name` (fast, no test overhead while iterating)
- **Merging to main / prod job** → `dbt build`
- **Hotfix** → targeted `dbt build --select model+`

## Final takeaway

For correctness, auditability, and governance, `dbt build` is the non-negotiable default. Reach for `dbt run` only as a faster inner-loop tool during active development.

## 🔗 Related Notes
- [[DBT Flags|dbt Flags That Actually Matter]]
- [[Test Execution, Severity & the `dbt build` Command|Test Execution, Severity & the dbt build Command]]
- [[Plus Dependency Operator|What `+` Means in dbt Selection]]

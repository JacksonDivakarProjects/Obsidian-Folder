# **dbt Flags That Actually Matter**

These flags control **what dbt runs**, **what it skips**, and **how safely it runs**. Think of them as control switches you combine with `dbt run`, `dbt test`, or (most often) `dbt build`.

## 1. `--full-refresh` — Delete and rebuild

**What it does**
- Drops and recreates existing **incremental models** from scratch.
- Old incrementally-built data is discarded and rebuilt from the full query.

```bash
dbt build --full-refresh
```

**Affects:** incremental models, seeds.
**Does not affect:** views (they're always rebuilt anyway), snapshots (their history is preserved, not replayed).

**When you must use it:**
- You changed the incremental logic or the `unique_key`.
- A column's data type changed.
- The incrementally-built data became corrupted.

**When you should not use it:** daily/normal production runs, or large tables without a specific reason — it's a destructive, expensive operation.

> **Warning:** `--full-refresh` is destructive. Always scope it with `--select`.

```bash
# Safe: scoped to one model
dbt build --select sales --full-refresh
```

## 2. `--exclude` — Run everything except this

Skips the named models, folders, or tags while running everything else normally.

```bash
dbt build --exclude int_legacy*
dbt build --exclude tag:heavy
```

**When to use:** a model is slow, broken, or deprecated, and you want to reduce risk without holding up the rest of the run.

> Mental model: "Do everything, but don't touch this."

## 3. `--select` — Run only what I choose

```bash
# Run a single model
dbt build --select fact_orders

# Run model + everything downstream of it
dbt build --select fact_orders+

# Run everything upstream of it, then the model
dbt build --select +fact_orders
```

Faster runs, safer development, less compute usage. **Golden rule:** always use `--select` in development; reserve unscoped `dbt build` for full production runs.

## 4. `state:modified` — Run only changed code (CI)

```bash
dbt build --select state:modified+
```

- Runs only models whose code changed since a reference point, plus everything downstream of them.
- Requires a previous run's `manifest.json`, passed via `--state <path>`.
- This is why CI pipelines for large dbt projects stay fast: no unnecessary rebuilds.

> Think: "Run only what I touched."

## 5. `--fail-fast` — Stop immediately on error

```bash
dbt build --fail-fast
```

Stops execution at the first failure instead of continuing through the rest of the DAG. Useful in CI pipelines, active debugging, and cost-sensitive environments where wasted compute after a known failure is pure waste.

## 6. `--defer` — Use prod data for unbuilt models in dev

```bash
dbt build --defer --state prod_manifest/
```

- For any model you *haven't* selected to build, dbt resolves `{{ ref() }}` to the **production** relation instead of failing because it doesn't exist in your dev schema.
- Lets you build and test just the models you changed without first rebuilding your entire dev environment.
- Does not overwrite or touch prod data.

> Think: "Borrow prod data for what I'm not rebuilding."

## 7. `--vars` — Pass values at runtime

```bash
dbt build --vars '{"run_date": "2025-01-01"}'
```

Sends dynamic values into models via the `var()` Jinja function. Common uses: backfills, date-based logic, conditional branches per environment.

## 8. `--threads` — Parallel execution

```bash
dbt build --threads 8
```

Controls how many models dbt tries to run concurrently (independent nodes in the DAG only — dependencies are still respected). More threads generally means faster runs but higher concurrent load on the warehouse; on consumption-billed platforms, that also means higher cost per run.

## 9. `--target` — Switch environment

```bash
dbt build --target prod
```

Swaps which set of credentials/schema from `profiles.yml` is used, without any code changes. Typical targets: `dev`, `qa`, `prod`.

## What to memorize

| Flag | Meaning |
|---|---|
| `--full-refresh` | Delete & rebuild incremental models |
| `--select` | Run only selected models |
| `--exclude` | Skip selected models |
| `state:modified` | Run only changed code (+ downstream) |
| `--fail-fast` | Stop on first error |
| `--defer` | Resolve unbuilt refs to production |

## Practical guidance

- **Production** → `dbt build`
- **Development** → `dbt build --select model`
- **Fix bad/stale incremental data** → `--full-refresh` combined with `--select`
- **CI** → `--select state:modified+`
- **Reduce blast radius** → `--exclude`

## 🔗 Related Notes
- [[Difference Between dbt run and dbt build|`dbt run` vs `dbt build`]]
- [[Plus Dependency Operator|What `+` Means in dbt Selection]]
- [[dbt Node Selection Syntax|dbt Node Selection Syntax]]

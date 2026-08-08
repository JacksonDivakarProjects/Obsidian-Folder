### **What `+` means in dbt selection**

In dbt, `+` is a **dependency operator**: it tells dbt how far to walk the DAG when selecting models, relative to a node you name. Think of it as scope expansion — which side of the `+` you put the model name on controls the direction.

## The three valid patterns

### 1. `model+` → model and all downstream

```bash
dbt build --select orders+
```

Runs:
- `orders`
- Anything that **depends on** `orders`

Use this when you change a base model and want to rebuild everything affected by that change.

### 2. `+model` → model and all upstream

```bash
dbt build --select +orders
```

Runs:
- All models that `orders` depends on
- Then `orders`

Use this when upstream data may be stale or missing and you need it rebuilt before `orders` itself.

### 3. `+model+` → full chain

```bash
dbt build --select +orders+
```

Runs:
- All parents
- The model itself
- All children

Use this for a clean, end-to-end rebuild of that slice of the DAG.

## Simple DAG example

```
raw_orders
   ↓
stg_orders
   ↓
int_orders
   ↓
fact_orders
```

| Command | What runs |
|---|---|
| `fact_orders` | only fact_orders |
| `+fact_orders` | raw → stg → int → fact |
| `fact_orders+` | fact + downstream |
| `+fact_orders+` | entire chain |

## What `+` does NOT do

- It does not mean "incremental" — it has nothing to do with materialization strategy.
- It does not change materialization.
- It does not force a full refresh (that's the separate `--full-refresh` flag).

It only controls **selection** — which nodes dbt decides to touch.

## Combine with other selectors

```bash
dbt build --select +fact_orders+ --exclude tag:heavy
```

## Professional phrasing

> "The `+` operator expands model selection upstream or downstream in the dbt DAG — prefix walks parents, suffix walks children, both walks the whole subgraph."

## Final takeaway

- `+` = dependency scope.
- Left side (`+model`) → parents.
- Right side (`model+`) → children.
- Both sides (`+model+`) → end-to-end.

For the related but distinct `@` operator (which also pulls in the ancestors of a model's children — used for safely rebuilding ephemeral-model dependents) and `state:modified+`, see [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 05/dbt Node Selection Syntax|dbt Node Selection Syntax]].

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 05/dbt Node Selection Syntax|dbt Node Selection Syntax]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 06/DBT Flags|dbt Flags That Actually Matter]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 06/Difference Between dbt run and dbt build|`dbt run` vs `dbt build`]]

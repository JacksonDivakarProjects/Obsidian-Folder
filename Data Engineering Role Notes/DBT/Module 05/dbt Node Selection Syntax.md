# **dbt Node Selection Syntax: A Practical Guide**

## **What is Node Selection?**
Node selection is how you tell dbt exactly **which models, tests, seeds, or snapshots to run**. Instead of always processing your entire project, you can target specific parts using flexible syntax. This is **essential in industry** for running smaller jobs, debugging, and implementing efficient CI/CD pipelines.

## **Core Selection Syntax Patterns**

### **1. Basic Selection by Name**
```bash
# Run a single model
dbt run --select customers

# Run multiple specific models
dbt run --select customers orders payments

# Run all models in a subdirectory
dbt run --select models/staging/
```

### **2. Key Selection Operators**

| Operator | What It Does | Example |
|----------|--------------|---------|
| **`+model`** (prefix) | Selects the model **and all its ancestors** (upstream/parents) | `dbt run --select +fct_revenue` — run everything `fct_revenue` depends on, then `fct_revenue` itself |
| **`model+`** (suffix) | Selects the model **and all its descendants** (downstream/children) | `dbt run --select stg_orders+` — run the staging model and everything that depends on it |
| **`+model+`** | Selects the model **and its entire subgraph** (ancestors and descendants) | `dbt run --select +stg_customers+` — full dependency chain for customers |
| **`@model`** | Selects the model, its descendants, **and the ancestors of those descendants** — a wider net than `model+`, mainly used to safely rebuild everything touched when an upstream (often ephemeral) model changes | `dbt run --select @stg_orders` |
| **`*`** | Wildcard matching | `dbt run --select stg_*` — run all models starting with "stg_" |

**Common mix-up:** `+model` (ancestors) is not the same as `@model`. `@` is a distinct operator for "this model, its children, and whatever else those children depend on" — it exists specifically to catch new dependency edges introduced by ephemeral models, not to walk upstream. If you just want a model's upstream lineage, use the `+` prefix.

### **3. Selection by Resource Type**
```bash
# Run only models
dbt run --select resource_type:model

# Test only sources
dbt test --select resource_type:source

# Build only seeds and their tests
dbt build --select resource_type:seed
```

### **4. Selection by Tag**
Tags are metadata you add to models in their `.sql` or `.yml` files:
```sql
-- In your model SQL file
{{ config(tags=["hourly", "finance"]) }}
```

```bash
# Run all models with a specific tag
dbt run --select tag:hourly

# Run models matching multiple selectors, unioned (OR logic)
dbt run --select tag:hourly tag:finance

# Intersect selectors (AND logic) with a comma
dbt run --select tag:hourly,tag:finance
```

### **5. Selection by Directory/Path**
```bash
# All models in a specific directory
dbt run --select path:models/staging

# Models in staging OR marts directories
dbt run --select path:models/staging path:models/marts

# Recursive selection within a directory
dbt run --select path:models/marts/finance/
```

## **Industry-Specific Selection Patterns**

### **Pattern 1: CI/CD Pipeline for Changed Models**
```bash
# Run only models modified since the last production run
dbt run --select state:modified+ --state ./prod-artifacts

# Test only changed models and their downstream tests
dbt test --select state:modified+ --state ./prod-artifacts
```
This is how teams run efficient pull request checks — only testing what changed. `state:modified` requires a previous run's `manifest.json` to compare against.

### **Pattern 2: Partial Runs for Specific Business Domains**
```bash
# Run the entire finance domain and everything downstream of it
dbt run --select tag:finance+

# Run marketing models but exclude dashboards
dbt run --select tag:marketing+ --exclude tag:dashboard

# Run a specific model and its full upstream+downstream subgraph
dbt run --select +fct_orders+
```

### **Pattern 3: Strategic Testing Approaches**
```bash
# Test sources first (catch data quality issues early)
dbt test --select source:*

# Test only critical models (tagged critical)
dbt test --select tag:critical

# Test a model and all its upstream dependencies
dbt test --select +stg_customers
```

## **Common Industry Commands Reference**

| Scenario | Command | What Happens |
|----------|---------|--------------|
| **Deploy new feature** | `dbt run --select my_new_feature+` | Runs the feature and all downstream models |
| **Data quality check** | `dbt test --select tag:critical,resource_type:model` | Tests only critical business models |
| **Debug a failing model** | `dbt run --select +failing_model` | Runs everything the failing model depends on |
| **Hourly incremental load** | `dbt run --select tag:hourly` | Runs only models tagged for hourly refresh |
| **Validate sources** | `dbt test --select source:*` | Tests all source freshness and constraints |
| **Safe production run** | `dbt build --select state:modified+ --state artifacts/` | Runs and tests only what changed, fails fast |

## **Pro Tips for Production**

1. **Always preview first**: use `dbt ls --select ...` to see what will run before executing.
2. **Combine selectors**: `--select` and `--exclude` can be used together for precise control.
3. **State comparison requires artifacts**: the `--state` flag needs a production manifest from a previous run.
4. **Selection works across all commands**: same syntax for `run`, `test`, `build`, `seed`, `snapshot`.
5. **Tag strategically**: use tags for domains (finance, marketing), refresh rates (hourly, daily), or tiers (bronze, silver, gold).

## **Real-World Example: E-commerce Company**

```bash
# Nightly full refresh of core models and everything downstream
dbt run --select tag:core+

# Hourly incremental models only
dbt run --select tag:hourly

# CI pipeline for a PR changing customer models
dbt build --select customers+ --exclude tag:legacy

# Data quality suite for finance department
dbt test --select tag:finance,tag:critical
```

Node selection is the key to efficient dbt workflows — it turns dbt from a bulk processing tool into a precise, surgical instrument for data transformation. See [[Plus Dependency Operator|What + Means in dbt Selection]] for a deeper, DAG-diagram walkthrough of the `+` operator specifically.

## 🔗 Related Notes
- [[The Ref() Function & Building DAGs|The Ref() Function & Building DAGs]]
- [[DBT Flags|dbt Flags That Actually Matter]]
- [[Plus Dependency Operator|What `+` Means in dbt Selection]]

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

| Operator | What It Does | Industry Use Case |
|----------|--------------|-------------------|
| **`+`** | Selects node **and all its descendants** (downstream) | `dbt run --select stg_orders+` - Run staging model and everything that depends on it |
| **`@`** | Selects node **and all its ancestors** (upstream) | `dbt run --select fct_revenue@` - Run revenue fact and everything it depends on |
| **`+` and `@` combined** | Selects node **and its entire subgraph** | `dbt run --select stg_customers+@` - Full dependency chain for customers |
| **`*`** | Wildcard matching | `dbt run --select stg_*` - Run all models starting with "stg_" |

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

# Run models with multiple tags (AND logic)
dbt run --select tag:hourly,tag:finance

# Run models with either tag (OR logic)
dbt run --select hourly finance
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
# Run only models modified since last production run
dbt run --select state:modified+ --state ./prod-artifacts

# Test only changed models and their downstream tests
dbt test --select state:modified+ --state ./prod-artifacts
```
*This is how teams run efficient pull request checks—only testing what changed.*

### **Pattern 2: Partial Runs for Specific Business Domains**
```bash
# Run the entire finance domain
dbt run --select tag:finance+

# Run marketing models but exclude dashboards
dbt run --select tag:marketing+ --exclude tag:dashboard

# Run specific model and its lineage
dbt run --select fct_orders+@
```

### **Pattern 3: Strategic Testing Approaches**
```bash
# Test sources first (catch data quality issues early)
dbt test --select source:*

# Test only critical models (with tag:critical)
dbt test --select tag:critical

# Test a model and all its upstream dependencies
dbt test --select stg_customers@
```

## **Common Industry Commands Reference**

| Scenario | Command | What Happens |
|----------|---------|--------------|
| **Deploy new feature** | `dbt run --select my_new_feature+` | Runs the feature and all downstream models |
| **Data quality check** | `dbt test --select tag:critical resource_type:model` | Tests only critical business models |
| **Debug a failing model** | `dbt run --select failing_model@` | Runs everything the failing model depends on |
| **Hourly incremental load** | `dbt run --select tag:hourly` | Runs only models tagged for hourly refresh |
| **Validate sources** | `dbt test --select source:*` | Tests all source freshness and constraints |
| **Safe production run** | `dbt build --select state:modified+ --state artifacts/` | Runs and tests only what changed, fails fast |

## **Pro Tips for Production**

1. **Always preview first**: Use `dbt ls --select ...` to see what will run before executing
2. **Combine selectors**: `--select` and `--exclude` can be used together for precise control
3. **State comparison requires artifacts**: The `--state` flag needs production manifest from previous run
4. **Selection works across all commands**: Same syntax for `run`, `test`, `build`, `seed`, `snapshot`
5. **Tag strategically**: Use tags for domains (finance, marketing), refresh rates (hourly, daily), or tiers (bronze, silver, gold)

## **Real-World Example: E-commerce Company**

```bash
# Nightly full refresh of core models
dbt run --select tag:core+

# Hourly incremental models only
dbt run --select tag:hourly

# CI pipeline for a PR changing customer models
dbt build --select customers+ --exclude tag:legacy

# Data quality suite for finance department
dbt test --select tag:finance,tag:critical
```

Node selection is **the key to efficient dbt workflows**—it transforms dbt from a bulk processing tool into a precise surgical instrument for data transformation.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 03/The Ref() Function & Building DAGs|The Ref() Function & Building DAGs]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 06/DBT Flags|dbt Flags That Actually Matter]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 06/Plus Dependency Operator|What `+` Means in dbt Selection]]

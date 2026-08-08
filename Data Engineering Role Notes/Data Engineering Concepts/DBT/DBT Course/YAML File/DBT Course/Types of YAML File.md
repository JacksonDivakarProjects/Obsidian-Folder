**Types of YAML files in dbt and their roles**

---

## 1. `dbt_project.yml` — **Project configuration**

**Scope:** Entire dbt project  
**Purpose:** Controls how dbt behaves

Defines:

- Project name and version
    
- Model paths
    
- Materializations
    
- Macros, seeds, tests behavior
    
- Model-level configs
    

Example:

```yaml
name: my_project
version: 1.0
models:
  my_project:
    marts:
      materialized: table
```

Mental model: **“How this dbt project is structured and executed.”**

---

## 2. `profiles.yml` — **Connection configuration**

**Scope:** Outside the project (user-level)  
**Purpose:** Database credentials and targets

Defines:

- Database type (Postgres, Snowflake, BigQuery, etc.)
    
- Host, user, password
    
- Dev / prod environments
    

Example:

```yaml
my_profile:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      user: jack
```

Mental model: **“Where dbt runs.”**

---

## 3. `models.yml` (or any `*.yml` under models/) — **Model metadata + tests**

**Scope:** Models and columns  
**Purpose:** Testing + documentation

Defines:

- Model descriptions
    
- Column descriptions
    
- Column tests
    
- Model tests
    

Example:

```yaml
models:
  - name: orders
    description: Order data
    columns:
      - name: order_id
        tests:
          - not_null
          - unique
```

Mental model: **“What this model means and what must be true.”**

---

## 4. `sources.yml` — **Source definitions**

**Scope:** Raw / external tables  
**Purpose:** Declare upstream data

Defines:

- Source databases and schemas
    
- Raw tables
    
- Freshness checks
    
- Source-level tests
    

Example:

```yaml
sources:
  - name: raw
    tables:
      - name: customers
        freshness:
          warn_after: {count: 12, period: hour}
```

Mental model: **“Where data comes from and how reliable it is.”**

---

## 5. `schema.yml` — **Generic name (conceptual)**

Not a special file.  
Any YAML file that defines **models, sources, tests, docs** is often called _schema YAML_.

Examples:

- `models.yml`
    
- `sources.yml`
    
- `orders.yml`
    

All are equivalent in function.

Mental model: **“Rules + meaning for data objects.”**

---

## Comparison table

|File|Purpose|Level|
|---|---|---|
|`dbt_project.yml`|Project behavior|Global|
|`profiles.yml`|Database connection|User|
|`models.yml`|Models tests + docs|Model|
|`sources.yml`|Raw data definition|Source|
|`schema.yml`|Generic term|Concept|

---

## One-line summary

- `dbt_project.yml` → **how dbt runs**
    
- `profiles.yml` → **where dbt connects**
    
- `models.yml` → **what models mean and enforce**
    
- `sources.yml` → **where data originates**

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/YAML File/DBT Course/YAML File and Its Structure|YAML File and Its Structure]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/YAML File/Dash in YAML|Dash in YAML]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/Documentation/Documentation in YAML|Documentation in YAML]]

# Jinja in SQL — A Practical Guide (dbt-First)

## 1. What Jinja Is

**Jinja is a templating engine, not SQL.** It runs **before** SQL hits the database, and helps you:
- Remove duplication
- Parameterize logic
- Dynamically generate SQL
- Enforce standards at scale

SQL executes in the database. Jinja executes at **compile time**. Confusing that boundary is where most Jinja bugs come from.

## 2. Jinja Execution Lifecycle

**Order of operations:**
```
Jinja renders → SQL is generated → Database executes SQL
```

**Implications:**
- Jinja cannot see query results.
- Jinja cannot inspect table data.
- Jinja only works with variables, macros, and compile-time metadata (like `target.name`).

## 3. Core Jinja Syntax

**Expressions (print values):**
```jinja
{{ variable }}
```
```sql
select * from {{ ref('fact_sales') }}
```

**Statements (logic):**
```jinja
{% if condition %}
{% endif %}
```

**Comments:**
```jinja
{# This is a Jinja comment #}
-- This is a SQL comment
```

## 4. Variables

```jinja
{% set region = 'APAC' %}
```
```sql
select *
from sales
where region = '{{ region }}'
```
**Best practice:** use `{% set %}` variables for configuration values, not for business logic that belongs in SQL.

## 5. Conditional Logic (`if / elif / else`)

```jinja
{% if target.name == 'prod' %}
  where is_active = true
{% else %}
  where is_active in (true, false)
{% endif %}
```
Common uses: dev vs. prod behavior, feature flags, safe experimentation without duplicating whole models.

## 6. Loops (`for`)

```jinja
{% for col in ['revenue', 'cost', 'profit'] %}
  sum({{ col }}) as total_{{ col }}{% if not loop.last %},{% endif %}
{% endfor %}
```
Renders to:
```sql
sum(revenue) as total_revenue,
sum(cost) as total_cost,
sum(profit) as total_profit
```
**Loop discipline:** always control trailing commas with `loop.last`.

## 7. Macros

**Define:**
```jinja
{% macro clean_string(col) %}
  lower(trim({{ col }}))
{% endmacro %}
```
**Use:**
```sql
select
  {{ clean_string('customer_name') }} as customer_name
from customers
```
Macros give you reusable logic, a single place to fix a bug, and enforced consistency across every model that uses them — the core productivity win of Jinja in dbt.

**With arguments and defaults:**
```jinja
{% macro date_filter(column, days=30) %}
  {{ column }} >= current_date - interval '{{ days }} day'
{% endmacro %}
```
```sql
where {{ date_filter('order_date', 90) }}
```

**Debug logging inside control flow:**
```jinja
{% if execute %}
  {{ log("Model is executing", info=True) }}
{% endif %}
```
`execute` is `false` during `dbt compile` / `dbt parse` and `true` during `dbt run`/`dbt build` — useful for guarding logging or side-effecting Jinja so it only fires on a real run.

## 8. dbt-Specific Jinja Functions

- **`ref()`** — `select * from {{ ref('dim_customer') }}` — creates the dependency edge that builds the DAG and lets dbt resolve the correct schema per environment.
- **`source()`** — `select * from {{ source('raw', 'orders') }}` — references a declared raw table, the root of the DAG.
- **`var()`** — `{{ var('start_date', '2023-01-01') }}` — reads a project variable, with an optional default. Used for environment configs, feature toggles, runtime behavior.

## 9. Filters (Transform Values)

```jinja
{{ 'Sales' | lower }}
{{ column_list | join(', ') }}
{{ my_list | length }}
```
```jinja
{% set cols = ['id', 'name', 'email'] %}
select {{ cols | join(', ') }} from users
```

## 10. Whitespace Control

```jinja
{%- if condition -%}
```
The `-` trims adjacent newlines/whitespace, keeping compiled SQL readable and easier to debug. Use it deliberately, not on every tag.

## 11. Advanced Pattern: Dynamic Column Selection

```jinja
{% set metrics = ['revenue', 'cost', 'profit'] %}

select
{% for m in metrics %}
  sum({{ m }}) as {{ m }}{% if not loop.last %},{% endif %}
{% endfor %}
from sales
```
This avoids copy-paste across near-identical aggregation columns.

## 12. Anti-Patterns

- Overusing Jinja for business logic that SQL could express directly.
- Deeply nested `if` trees that hide the actual query intent.
- Macros that obscure what SQL is actually running.
- Dynamic table/column names built from unchecked input, with no governance over what values are possible.

**Rule of thumb:** if SQL alone can do it cleanly, don't reach for Jinja.

## 13. Debugging Jinja

```bash
# Render Jinja to SQL without running it
dbt compile
```
Inspect the rendered output under `target/compiled/<project_name>/...` to see exactly what SQL your Jinja produced. Log values as you go:
```jinja
{{ log(my_variable, info=True) }}
```

## 14. Mental Model

Jinja is a **SQL code generator with guardrails** — not runtime logic, and not data-aware. It only ever sees what's available at compile time: variables, macros, and project metadata.

## Summary

- Jinja runs **before** SQL execution — it generates SQL, it doesn't reason about query results.
- Macros are the main productivity tool; `ref()`, `source()`, and `var()` are the dbt-specific functions you'll use constantly.
- Keep logic shallow and intention clear — clean, explicit SQL beats a clever template every time.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/Jinja/Jinja Templating Fundamentals|Jinja Templating Fundamentals]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/Jinja/Jinja Data Structures|Jinja Data Structures]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/Jinja/Length in Jinja|Length in Jinja]]

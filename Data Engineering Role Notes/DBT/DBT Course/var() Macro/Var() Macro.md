### `var()` in dbt — how to **define** and how to **use**

---

## 1. How to DEFINE a variable

There are **three valid places**. Resolution follows this order.

---

### A. Define in `dbt_project.yml` (most common)

```yml
vars:
  min_order_amount: 100
  is_dev: true
  max_wos_length: 1000
```

Scope: **entire project**

---

### B. Define via CLI (highest priority)

```bash
dbt run --vars '{min_order_amount: 200}'
```

Used for:

- temporary overrides
    
- CI/CD
    
- experiments
    

---

### C. Define a default (fallback)

```jinja
var('min_order_amount', 0)
```

Used when the variable is not defined elsewhere.

---

## 2. How to USE a variable

### Basic usage

```sql
select *
from orders
where order_amount > {{ var('min_order_amount') }}
```

Compiled SQL:

```sql
where order_amount > 100
```

---

### Use in conditional logic

```sql
{% if var('is_dev', false) %}
limit 100
{% endif %}
```

---

### Use inside macros

```jinja
{% macro windowed_sales(days) %}
  sales_date >= current_date - interval '{{ days }} days'
{% endmacro %}

{{ windowed_sales(var('window_days', 30)) }}
```

---

### Use with dbt config

```sql
{{ config(
    materialized='incremental',
    unique_key=var('order_key')
) }}
```

---

## 3. Valid variable types

```yml
vars:
  threshold: 10          # integer
  ratio: 0.75            # float
  enabled: true          # boolean
  country: "IN"          # string
  columns: ["a", "b"]    # list
```

Accessing list:

```jinja
{% for col in var('columns') %}
    {{ col }}
{% endfor %}
```

---

## 4. Where `var()` CAN be used

- `.sql` models
    
- `.yml` (tests, descriptions, configs)
    
- macros
    
- hooks
    

All are **compile-time contexts**.

---

## 5. Where `var()` CANNOT be used

❌ As a column  
❌ Inside SQL expecting row-level evaluation  
❌ To read query results

Invalid:

```sql
where {{ var('column_name') }} > 10   -- unless used as identifier
```

Valid (identifier injection):

```sql
order by {{ var('order_column') }}
```

---

## 6. Common mistakes

### Mistake 1: variable not defined

```sql
{{ var('limit') }}
```

Fix:

```sql
{{ var('limit', 100) }}
```

---

### Mistake 2: expecting runtime behavior

```sql
{{ var('row_count') }}
```

Impossible. dbt cannot read data during compilation.

---

## 7. Minimal working example

### `dbt_project.yml`

```yml
vars:
  env: dev
  row_limit: 100
```

### model.sql

```sql
select *
from orders
{% if var('env') == 'dev' %}
limit {{ var('row_limit') }}
{% endif %}
```

---

## 8. Final rule (memorize)

**Define variables outside SQL.  
Use variables inside Jinja.  
Never confuse variables with data.**

That is the complete and correct mental model.

## 🔗 Related Notes
- [[Configs and Variables|Configs & the Hierarchy]]
- [[DBT Flags|dbt Flags That Actually Matter]]

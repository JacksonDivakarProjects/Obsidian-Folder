**Types of tests in dbt: Singular and Generic (with ref() note)**

---

## 1. Singular tests (custom SQL)

### Definition

A singular test is a **SQL file** that must return **zero rows** to pass.

### Location

`tests/*.sql`

### Example: negative order amount

```sql
-- tests/orders_negative_amount.sql
select *
from {{ ref('orders') }}
where amount < 0
```

### Example: future order dates

```sql
-- tests/orders_future_date.sql
select *
from {{ ref('orders') }}
where order_date > current_date
```

**Rule**  
Returned rows = failures.

---

## 2. Generic tests (declarative, reusable)

### Definition

Generic tests are **parameterized tests** applied through YAML.

---

### Built-in generic tests

#### `not_null`

```yaml
columns:
  - name: order_id
    tests:
      - not_null
```

---

#### `unique`

```yaml
columns:
  - name: order_id
    tests:
      - unique
```

---

#### `accepted_values`

```yaml
columns:
  - name: status
    tests:
      - accepted_values:
          values: ['completed', 'cancelled']
```

---

#### `relationships`

```yaml
columns:
  - name: customer_id
    tests:
      - relationships:
          to: ref('customers')
          field: customer_id
```

### **Important note about `ref()`**

- In the `relationships` test, `ref()` is written directly as the value of `to:`, without wrapping it in `{{ }}`
- The model name inside `ref()` still needs quotes, like any Jinja string argument

Correct:

```yaml
to: ref('customers')
```

### **Other macros require quotes**

For non-relationship contexts, macros **must be quoted**.

Correct:

```yaml
description: "{{ doc('customers_table') }}"
```

Incorrect:

```yaml
description: {{ doc(customers_table) }}
```

---

### Custom generic test example

#### Define once

```jinja
-- macros/not_negative.sql
{% test not_negative(model, column_name) %}
select *
from {{ model }}
where {{ column_name }} < 0
{% endtest %}
```

#### Use anywhere

```yaml
columns:
  - name: amount
    tests:
      - not_negative
```

---

## Comparison

|Aspect|Singular|Generic|
|---|---|---|
|Written in|SQL|YAML (+ macro once)|
|Reusable|No|Yes|
|Best for|Complex logic|Standard rules|

---

## One-line summary

- **Singular tests** use SQL and must return zero rows
    
- **Generic tests** declare reusable rules in YAML
    
- **`ref()` in relationships tests is unquoted**; **other macros must be quoted**

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 04/Generic Tests & Their Types|Generic Tests & Their Types]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 04/Singular Tests|Singular Tests]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 04/Custom Generic Tests|Custom Generic Tests]]

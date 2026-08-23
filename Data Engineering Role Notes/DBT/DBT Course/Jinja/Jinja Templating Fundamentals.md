# **Module 2, Topic 2: Jinja Templating Fundamentals**

Jinja is the templating language that transforms dbt from a simple SQL runner into a powerful programming environment for your data warehouse. It lets you write **dynamic SQL** that adapts, loops, and follows logic.

## **1. What is Jinja and Why Use It?**

Think of Jinja as a way to **inject logic and variables** into your plain SQL. Instead of writing ten nearly identical queries, you write one template that generates all ten.

**Analogy**: If SQL is a static document, then **SQL + Jinja** is a mail merge. You have a template letter and a list of names; Jinja automatically creates a personalized letter for each name.

In dbt, Jinja is used to:
*   Make column references dynamic.
*   Build SQL logic conditionally (e.g., `WHERE` clauses that change based on the environment).
*   Loop over lists to avoid repetitive code.
*   Use built-in dbt functions like `{{ ref() }}` and `{{ source() }}`.

## **2. Core Jinja Syntax: The Three Delimiters**

Jinja uses three special character sets to differentiate its code from regular SQL.

| Delimiter | Name | Purpose | Example |
| :--- | :--- | :--- | :--- |
| `{{ ... }}` | **Expression** | Outputs the *result* of the code inside. This is rendered directly into your final SQL. | `{{ user_id }}` outputs the value of the variable. |
| `{% ... %}` | **Statement** | Executes logic (like loops or conditions) but does **not** output text directly. | `{% if is_incremental %} ... {% endif %}` |
| `{# ... #}` | **Comment** | Adds notes that are **not** included in the final, compiled SQL. | `{# This is a note for developers #}` |

## **3. Expressions `{{ }}`: The Workhorse**

This is how you reference variables and call functions. The content is evaluated and **printed directly** into the SQL string.

### **Variables**
You can define variables within a model or macro.
```sql
{% set currency = 'USD' %}
{% set start_date = '2024-01-01' %}

SELECT
    order_id,
    amount,
    '{{ currency }}' as currency_code -- Outputs: 'USD'
FROM orders
WHERE created_at > '{{ start_date }}' -- Outputs: WHERE created_at > '2024-01-01'
```

### **Essential dbt Functions**
These Jinja expressions are specific to dbt and are your most important tools.

*   **`{{ ref() }}`**: Builds dependencies between models. **This is the core of dbt's DAG.**
    ```sql
    -- References a model named 'stg_customers'
    SELECT * FROM {{ ref('stg_customers') }}
    -- Compiles to: SELECT * FROM analytics.stg_customers
    ```
*   **`{{ source() }}`**: References a raw table you defined in a `sources.yml` file.
    ```sql
    -- References the 'customers' table in the 'raw_database' source
    SELECT * FROM {{ source('raw_database', 'customers') }}
    -- Compiles to: SELECT * FROM raw_data.raw_customers_table
    ```

## **4. Statements `{% %}`: Adding Logic and Control Flow**

Statements control the flow of your template. They don't produce output themselves but determine what SQL gets written.

### **Conditionals (`if/elif/else`)**
Use these to write SQL that changes based on a condition.
```sql
{% if target.name == 'prod' %}
    -- This part only compiles when running in the 'prod' target
    SELECT * FROM {{ ref('orders') }} WHERE status = 'shipped'
{% elif target.name == 'dev' %}
    -- This part only compiles in 'dev' (for faster testing)
    SELECT * FROM {{ ref('orders') }} LIMIT 1000
{% else %}
    {{ exceptions.raise_compiler_error("Invalid target!") }}
{% endif %}
```

### **Loops (`for`)**
Loops are incredibly powerful for eliminating repetitive SQL, like pivoting multiple columns.
```sql
{% set payment_methods = ["credit_card", "bank_transfer", "coupon", "gift_card"] %}

SELECT
    order_id,
    {% for method in payment_methods %}
    SUM(CASE WHEN payment_method = '{{ method }}' THEN amount END) AS {{ method }}_amount
    {% if not loop.last %},{% endif %} -- Critical: Adds comma between columns
    {% endfor %}
FROM {{ ref('stg_payments') }}
GROUP BY 1
```
This compiles into a clean `SELECT` with four separate `SUM(CASE...)` columns, one for each payment method.

## **5. Whitespace Control: Cleaning Your Compiled SQL**

Jinja statements can leave unwanted spaces or newlines in your final SQL, which might cause formatting issues. Use a minus sign (`-`) inside the delimiter to trim whitespace.

```sql
{% set columns = ["id", "name", "status"] -%} {# '-' trims trailing space #}
SELECT
{%- for col in columns %} {# '-' trims leading space #}
  {{ col }}{% if not loop.last %},{% endif %}
{% endfor %}
FROM my_table
```
**Compiles to clean SQL:**
```sql
SELECT
  id,
  name,
  status
FROM my_table
```

## **6. A Practical Example: Bringing It All Together**

Here's how these concepts combine in a real model.

```sql
-- models/marts/user_report.sql

{{ config(
    materialized='table',
    tags=['reporting', 'daily']
) }}

{# Define variables for reusability #}
{% set active_statuses = ["'active'", "'pending'"] %}
{% set report_date = var("report_date", "CURRENT_DATE") %}

{% if target.name == 'prod' %}
    {% set limit_clause = "" %}
{% else %}
    {% set limit_clause = "LIMIT 10000" %}
{% endif %}

SELECT
    u.user_id,
    u.name,
    u.signup_date,
    -- Use a loop to count events by type
    {% for event in ['login', 'pageview', 'purchase'] %}
    COUNT(DISTINCT CASE WHEN e.event_type = '{{ event }}' THEN e.event_id END) AS {{ event }}_count
    {% if not loop.last %},{% endif %}
    {% endfor %}
FROM {{ ref('stg_users') }} u
LEFT JOIN {{ source('events_db', 'raw_events') }} e ON u.user_id = e.user_id
WHERE u.status IN ({{ active_statuses | join(', ') }}) -- Filters to 'active', 'pending'
  AND e.event_date = '{{ report_date }}'
{{ limit_clause }} -- Safely adds a LIMIT clause only in dev
```

**Key takeaways from this example:**
1.  **`{{ config() }}`** sets model-specific configuration.
2.  **`{# ... #}`** is a developer comment, stripped from the compiled SQL.
3.  **`{% set ... %}`** defines reusable variables.
4.  **`{% if ... %}`** changes `limit_clause` based on the target (prod vs. dev).
5.  **`{% for ... %}`** creates three count columns without copy-pasting.
6.  **`{{ ref() }}` and `{{ source() }}`** correctly build dependencies.
7.  **`{{ var() }}`** accesses a dbt variable, defined in `dbt_project.yml` or via `--vars`.

---
**Summary:** Jinja is the engine behind dynamic SQL in dbt: `{{ }}` outputs, `{% %}` controls logic, and `{# #}` comments. Combined with `ref()`/`source()` for dependencies and loops/conditionals for DRY code, it turns static SQL into a proper templating layer — one worth a dedicated editor setup, covered next.

## 🔗 Related Notes
- [[Jinja SQL|Jinja in SQL]]
- [[Jinja Data Structures|Jinja Data Structures]]
- [[Length in Jinja|Length in Jinja]]

# **Module 3, Topic 1: Building Models & Materializations**

Models are the fundamental building blocks of a dbt project. They are `.sql` files that contain a `SELECT` statement, which dbt uses to build objects in your data warehouse. The way a model is built is called its **materialization**.

## **1. What is a Model?**

At its core, a dbt model is a **single SQL `SELECT` statement** saved as a `.sql` file in your `models/` directory. This query defines the transformation logic.

*   **Input:** References to `{{ source() }}` or `{{ ref() }}` tables.
*   **Logic:** Your SQL transformation (filtering, joining, aggregating).
*   **Output:** A new table, view, or ephemeral dataset in your warehouse.

### **Basic Model Example**
```sql
-- models/staging/stg_customers.sql

-- 1. Optional: The config block (highest-priority settings)
{{
    config(
        materialized='view',
        tags=['staging', 'daily']
    )
}}

-- 2. The SQL transformation
SELECT
    customer_id,
    first_name,
    last_name,
    email,
    -- Use Jinja to call a macro for consistent logic
    {{ normalize_phone_number('phone') }} as phone_number,
    created_at,
    updated_at
FROM {{ source('raw_database', 'customers') }}
WHERE is_active = true
```

## **2. What is Materialization?**

**Materialization** is the strategy dbt uses to persist your model's dataset in the warehouse. It's the **single most important model configuration**.

It answers: **"What kind of database object should this model become?"** The choice involves a **trade-off between performance, cost, and freshness**.

## **3. The Four Core Materializations**

Here is a comparison of the four main types to help you choose:

| Materialization | Database Object | Use Case & Pros | Cons & Considerations |
| :--- | :--- | :--- | :--- |
| **`view`** | A `VIEW` (logical query). | **Lightweight exploration** or intermediate steps. Always shows fresh data. | **Slow for consumers** (query runs on read). Heavy transforms hurt performance. |
| **`table`** | A `TABLE` (physical data). | **Final datasets for end-users** (marts). Fast to query. | **Slow/expensive to rebuild** fully. Data can become stale. |
| **`incremental`** | A `TABLE`, but with **smart updates**. | **Large fact tables**. Appends/merges only new data. Saves time and cost. | **Complex logic**. Requires a `unique_key` and incremental strategy. |
| **`ephemeral`** | **No** database object. | **Reusable logic component**. Injected as a CTE into parent models. Keeps project clean. | **Cannot be queried directly**. Can make parent models very large. |

## **4. Deep Dive & Syntax for Each**

### **A. View (`materialized='view'`)**
dbt runs a `CREATE OR REPLACE VIEW ... AS` statement. Best for lightweight transformations and models that are upstream of final tables.
```sql
-- Example: A simple staging view
{{ config(materialized='view') }}

SELECT * FROM {{ source('web', 'events') }}
WHERE event_time > current_date - 30
```

### **B. Table (`materialized='table'`)**
dbt runs a `CREATE OR REPLACE TABLE ... AS` statement or a `DROP/CREATE`. Best for final, frequently queried datasets.
```sql
-- Example: A core mart table
{{ config(materialized='table') }}

SELECT
    user_id,
    count(*) as total_pageviews
FROM {{ ref('stg_events') }}
GROUP BY 1
```

### **C. Incremental (`materialized='incremental'`)**
This is the most powerful but complex pattern. It only processes new data since the last run.

**1. Required Configuration:** You must specify a `unique_key`.
**2. Core Logic:** Use the `is_incremental()` macro to conditionally filter for new records.

```sql
-- models/marts/fct_orders.sql
{{
    config(
        materialized='incremental',
        unique_key='order_id'
    )
}}

SELECT
    order_id,
    customer_id,
    order_amount,
    order_date
FROM {{ ref('stg_orders') }}

{% if is_incremental() %}
-- This WHERE clause only runs in incremental builds
WHERE order_date > (SELECT MAX(order_date) FROM {{ this }})
{% endif %}
```
**How it Works:** On the first run, the full `SELECT` runs. On subsequent runs, only rows where `order_date` is newer than the max in the target table are processed and then merged (using the `unique_key`).

### **D. Ephemeral (`materialized='ephemeral'`)**
The model is not built in the database. Instead, its SQL is injected as a Common Table Expression (CTE) into every model that references it via `{{ ref() }}`.

```sql
-- models/intermediate/int_aggregated_events.sql
{{ config(materialized='ephemeral') }}

SELECT
    session_id,
    MIN(event_time) as session_start
FROM {{ ref('stg_events') }}
GROUP BY 1
```
```sql
-- models/marts/mart_sessions.sql (a parent model)
-- The ephemeral model becomes a CTE
WITH int_aggregated_events AS (
    SELECT session_id, MIN(event_time) as session_start
    FROM raw_data.events
    GROUP BY 1
)
SELECT * FROM int_aggregated_events
```

## **5. How to Run Models & Apply Materializations**

You execute models using the `dbt run` command. The materialization logic is applied automatically based on each model's configuration.

```bash
# Run all models in the project
dbt run

# Run a specific model and its upstream dependencies
dbt run --select orders

# Run all models in a directory (using the staging/ folder config)
dbt run --select staging.*

# Run a model and force a full refresh (ignores incremental logic)
dbt run --select fct_orders --full-refresh
```

---
### **Summary & Decision Flow**

A **model** is a transformed dataset defined by a SQL `SELECT`. Its **materialization** determines how it's built in the warehouse. Use this flow to choose:

1.  **Is it a reusable component?** → Use **`ephemeral`**.
2.  **Is it a lightweight staging model?** → Use **`view`**.
3.  **Is it a final, consumable table?** → Use **`table`**.
4.  **Is it a very large fact table?** → Use **`incremental`**.

The configuration hierarchy means you can set a project-wide default (e.g., `view` for `staging/`) in `dbt_project.yml` and override it for specific models (e.g., `table` for one heavily-queried staging model) right inside their SQL file with `{{ config() }}`. The next step is understanding how models connect to each other via `ref()` — that's what builds the DAG.

## 🔗 Related Notes
- [[DBT Syllabus|dbt Learning Syllabus]]
- [[The Ref() Function & Building DAGs|The Ref() Function & Building DAGs]]
- [[Configs and Variables|Configs & the Hierarchy]]
- [[Generic Tests & Their Types|Generic Tests & Their Types]]

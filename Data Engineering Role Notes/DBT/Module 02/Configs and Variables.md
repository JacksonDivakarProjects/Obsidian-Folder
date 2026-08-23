# **Module 2, Topic 4: Configs & the Hierarchy (Project, Properties, Block)**

Configuration is what makes a dbt model behave the way it does. This topic explains the **four methods** to apply configurations and the **critical rule of precedence** that determines which setting wins when conflicts arise.

## **1. The Four Methods of Configuration**

You can configure a model at four different levels, from the broadest (entire project) to the most specific (a single model).

| Method & Syntax | Scope | Priority | Best For |
| :--- | :--- | :--- | :--- |
| **1. In `dbt_project.yml`** | Entire project or folder. | 1 (Lowest) | Setting **global defaults** (e.g., all models are views). |
| **2. In a Model Property `.yml` file** | Specific models listed in the file. | 2 | **Documenting** and configuring a group of related models. |
| **3. In a Model's SQL with `{{ config() }}`** | That specific model only. | 3 (Highest) | **Overriding** defaults for a specific, important model. |
| **4. Via Command Line `--vars`** | The entire run. | Special | Passing dynamic, run-specific values (like a date). |

## **2. Method 1: Project-Level Config (`dbt_project.yml`)**

This is your foundation. It sets defaults that cascade down to all models.

### **Syntax & Example**
In your `dbt_project.yml`, configurations are nested under the `models:` key, using your project's name.
```yaml
# dbt_project.yml
name: my_project
model-paths: ["models"]

models:
  my_project:  # This must match your project 'name'
    # Project-wide defaults
    +materialized: view
    +schema: analytics

    # Folder-specific overrides
    staging:
      +materialized: table
      +schema: staging  # All models in 'models/staging/' use this
      +tags: ['staging']

    marts:
      +materialized: incremental
      +schema: marts
      +tags: ['marts', 'daily']
```
**Key:** The `+` prefix before the config name (e.g., `+materialized`) is required in this file.

## **3. Method 2: Model Property Config (`.yml` file)**

These YAML files, typically placed in your model directories, serve two purposes: **documenting** your models and **configuring** them.

### **Syntax & Example**
```yaml
# models/staging/staging.yml
version: 2

models:
  - name: stg_customers
    description: "Cleansed raw customer data. Removes PII."
    config:  # Configuration for THIS specific model
      materialized: table
      tags: ['pii_cleaned', 'core']
    columns:  # Documentation and tests
      - name: customer_id
        description: "Primary key. Surrogate key generated from source."
        tests:
          - not_null
          - unique

  - name: stg_orders
    description: "Cleansed raw order data."
    config:
      materialized: incremental
      unique_key: order_id
```
This method is excellent for keeping documentation, tests, and configuration for a domain (like `staging`) together.

## **4. Method 3: In-Model Config Block (`{{ config() }}`)**

This is the most powerful and specific method. A `{{ config() }}` block directly inside a model's `.sql` file has the **final say**.

### **Syntax & Example**
```sql
-- models/marts/dim_customers.sql

{{ config(
    materialized = 'table',
    unique_key = 'customer_key',
    tags = ['finance', 'gold'],
    post_hook = "GRANT SELECT ON {{ this }} TO reporter"
) }}

WITH enriched_customers AS (
    SELECT
        *,
        {{ dbt_utils.surrogate_key(['customer_id', 'signup_date']) }} as customer_key
    FROM {{ ref('stg_customers') }}
)
SELECT * FROM enriched_customers
```
**Key Points:**
*   The `config()` is a **Jinja macro**, so it uses `{{ }}`.
*   It accepts **key-value pairs**.
*   The keyword `this` inside the config block refers to the model being built.

## **5. Method 4: Variables via Command Line (`--vars`)**

Variables allow you to pass dynamic values into your project. They are defined in your `dbt_project.yml` and can be overridden via command line.

**Step 1: Define variable in `dbt_project.yml`:**
```yaml
# dbt_project.yml
vars:
  # Default value
  report_timezone: 'UTC'
```

**Step 2: Use variable in a model with `{{ var() }}`:**
```sql
-- In a SQL model
SELECT
    created_at AT TIME ZONE '{{ var("report_timezone") }}' as local_time
FROM {{ ref('orders') }}
```

**Step 3: Override via command line:**
```bash
dbt run --select my_model --vars '{"report_timezone": "America/New_York"}'
```

## **6. The Golden Rule: Configuration Precedence**

When the same configuration (like `materialized`) is set in multiple places, **the most specific definition wins**.

**Precedence Order (Highest to Lowest):**
1.  **In-Model `{{ config() }}` Block** (Most Specific, **WINS**)
2.  **Model Property `.yml` File**
3.  **Folder-level in `dbt_project.yml`**
4.  **Project-level in `dbt_project.yml`** (Least Specific)

### **A Clear Example: What materialization wins?**
Imagine your project is set up like this:
*   **Project Level (`dbt_project.yml`)**: `+materialized: view`
*   **Folder Level (`dbt_project.yml` for `marts/`)**: `+materialized: incremental`
*   **Property File (`marts.yml`)**: Config for `fct_orders` says `materialized: table`
*   **SQL File (`fct_orders.sql`)**: `{{ config(materialized='ephemeral') }}`

**Result:** `fct_orders` will be **ephemeral**. The in-model config block has the highest priority.

## **7. Commonly Used Configurations**

| Configuration          | What It Controls                                                             | Common Values                                    |
| :--------------------- | :--------------------------------------------------------------------------- | :----------------------------------------------- |
| **`materialized`**     | How the model is built in the DB.                                            | `table`, `view`, `incremental`, `ephemeral`      |
| **`schema`**           | The dataset/schema the model is placed in.                                   | `analytics`, `reporting`, `staging`              |
| **`tags`**             | Labels for grouping and selection.                                           | `['daily', 'finance', 'pii']`                    |
| **`unique_key`**       | Required for `incremental` models to identify rows for the **upsert operation**. | `order_id`                                       |
| **`on_schema_change`** | How to handle new columns in incremental models.                             | `fail`, `append_new_columns`, `sync_all_columns` |
| **`post_hook`**        | SQL to run after model is built (e.g., grants).                              | `"GRANT SELECT ..."`                             |

---
**Summary:**
There are four ways to control your dbt models: the broad **project file**, the grouped **property files**, the precise **in-model config block**, and dynamic **command-line variables**. The rule that ties them together is precedence: the more specific the location, the more power it has. This lets you set smart project-wide defaults while retaining the ability to override them exactly where needed — which is what Building Models & Materializations covers next.

## 🔗 Related Notes
- [[Configuration Files|Configuration Files Overview]]
- [[Var() Macro|var() in dbt]]
- [[Building Models & Materializations|Building Models & Materializations]]

# **Module 2, Topic 1: Configuration Files Overview**

Configuration files are the blueprint of your dbt project. They define *what* your project does, *how* it connects to your data platform, and *where* your source data lives.

## **1. The Core Configuration Files**

dbt uses three essential YAML files. Each has a distinct purpose and location.

| File Name | Primary Purpose | Location |
| :--- | :--- | :--- |
| **`dbt_project.yml`** | Defines project structure, naming, and default behavior. | **Root** of your dbt project directory. |
| **`profiles.yml`** | Contains credentials and connection details for your data platform (e.g., BigQuery, Snowflake). | **Outside** the project, typically in `~/.dbt/` (your home directory). |
| **`sources.yml`** (and other `.yml` files in `models/`) | Documents and configures your raw source data tables and individual models. | **Inside** the `models/` directory (or subdirectories like `models/staging/`). |

## **2. `dbt_project.yml` - The Project Control Center**

This is the **only mandatory configuration file**. It tells dbt, "This is a dbt project," and sets up its foundational rules.

### **Key Sections & Syntax:**
```yaml
# dbt_project.yml
name: my_analytics_project  # Your project name
version: '1.0.0'            # Project version (useful for packaging)
config-version: 2           # Always use '2'

profile: my_project         # Must match a profile name in profiles.yml

# Tell dbt where to find things
model-paths: ["models"]
test-paths: ["tests"]
macro-paths: ["macros"]
seed-paths: ["seeds"]

# Project-wide configurations (applied to all models by default)
models:
  my_analytics_project:     # Must match the 'name:' above
    +materialized: view     # Default: all models are created as VIEWs
    +schema: analytics      # Default: put all models in the 'analytics' schema

    # You can override defaults for specific folders
    staging:
      +materialized: table
      +schema: staging      # Models in 'models/staging/' go to 'staging' schema
```
**Key Takeaway:** The `+` sign before a setting (like `+materialized`) is crucial for setting configurations in this file.

## **3. `profiles.yml` - The Connection Manager**

This file lives **outside your project code** to keep sensitive credentials separate. It defines connections (called "targets") to your data warehouse.

### **Basic Structure & Example:**
```yaml
# ~/.dbt/profiles.yml
my_project:                  # Profile name (must match 'profile:' in dbt_project.yml)
  target: dev               # Default target to use
  outputs:
    dev:                    # Target name: 'dev' (for development)
      type: bigquery        # Your data platform adapter
      method: service-account
      project: your-gcp-project-id
      dataset: dbt_dev      # Default dataset/schema for this target
      keyfile: /path/to/your-keyfile.json
      threads: 4            # Number of concurrent connections

    prod:                   # Another target name: 'prod' (for production)
      type: bigquery
      method: service-account
      project: your-gcp-project-id
      dataset: dbt_prod     # Different dataset for production
      keyfile: /path/to/your-keyfile.json
      threads: 8
```
You can switch targets using the command line: `dbt run --target prod`.

## **4. Property Files (like `sources.yml`) - The Data Catalog**

These files live alongside your SQL models to **declare sources** and **configure or document specific models and tests**.

### **Defining Sources:**
You must declare your raw database tables as **sources** before referencing them in models with the `{{ source() }}` function.

```yaml
# models/sources.yml
version: 2

sources:
  - name: raw_database     # Logical grouping of source tables
    schema: raw_data       # The actual schema name in your warehouse
    tables:
      - name: customers    # The actual table name
        identifier: raw_customers_table # Use if table name differs in DB
        description: "Master customer table from the production OLTP system."
        loaded_at_field: updated_at # Useful for incremental models

      - name: orders
        description: "All orders placed on the website."
```

## **5. The Configuration Hierarchy (Golden Rule)**

**A specific configuration always wins over a general one.** dbt applies settings in this order of priority (from lowest to highest):

1.  **Project Level** (`dbt_project.yml`): Sets defaults for the entire project (lowest priority).
2.  **Directory Level** (in `dbt_project.yml`): Overrides project defaults for a subfolder (e.g., all models in `models/staging/`).
3.  **Model Property Level** (in a `.yml` file): Configures a specific model or group of models defined in the YAML.
4.  **In-Model Config Block** (`{{ config() }}` in a `.sql` file): The **highest priority**. Directly inside the SQL model file.

### **Example of the Hierarchy in Action:**
Imagine you want a specific model, `models/core/important_model.sql`, to be a table.

*   **Project Level:** `dbt_project.yml` sets `+materialized: view`
*   **Directory Level:** `dbt_project.yml` for the `core/` folder sets `+materialized: ephemeral` (overrides view)
*   **In-Model Config:** Inside `important_model.sql`, you write:
    ```sql
    {{ config(materialized='table') }}
    SELECT ...
    ```
    **Result:** `important_model` is built as a **TABLE**. The in-model config block wins.

---
**Summary:** There are three key configuration files — `dbt_project.yml` (project rules), `profiles.yml` (connections), and property files like `sources.yml` (data definitions) — and one configuration hierarchy where settings in a model's SQL file (`{{ config() }}`) always win. Jinja templating is what makes those SQL files dynamic, which is the next topic.

## 🔗 Related Notes
- [[Configs and Variables|Configs & the Hierarchy]]
- [[Foundations & Setup|Module 1: Foundations & Setup]]
- [[Jinja Templating Fundamentals|Jinja Templating Fundamentals]]

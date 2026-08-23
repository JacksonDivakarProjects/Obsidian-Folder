# **Module 3, Topic 2: The Ref() Function & Building DAGs**

The true power of dbt isn't just in writing SQL, but in **orchestrating many SQL models to run in the correct order**. This is achieved through the `ref()` function, which creates a **Directed Acyclic Graph (DAG)** of dependencies.

## **1. What is the `ref()` Function?**

The `{{ ref() }}` function is the most important Jinja function in dbt. It does two critical things:

1.  **Builds Relationships**: It tells dbt, "This model *depends on* that other model."
2.  **Creates Portability**: It dynamically resolves the correct database name and schema for the referenced model, allowing your code to run in different environments (`dev`, `prod`) without changes.

### **Basic Syntax & Example**
```sql
-- In a model named models/marts/fct_orders.sql
SELECT *
FROM {{ ref('stg_orders') }} -- References a model named 'stg_orders'
```
**What dbt compiles this to (in the `dev` target):**
```sql
SELECT *
FROM analytics_dev.stg_orders
```
Notice that `ref()` resolved the full table path (`analytics_dev.stg_orders`) automatically.

## **2. How `ref()` Creates a DAG (Lineage)**

Every time you use `ref('model_name')`, you create a dependency link. dbt combines all these links to build a **dependency graph** or **lineage**.

### **Visualizing a Simple DAG**
Imagine three models:
1.  `stg_customers.sql` -> `{{ source('raw', 'users') }}`
2.  `stg_orders.sql` -> `{{ source('raw', 'orders') }}`
3.  `fct_customer_orders.sql` -> `{{ ref('stg_customers') }}` and `{{ ref('stg_orders') }}`

This creates the following execution DAG:
```
    [raw.users]       [raw.orders]
         |                  |
    stg_customers      stg_orders
          \                /
        fct_customer_orders
```
**Execution Order:** dbt will run `stg_customers` and `stg_orders` first (in parallel if possible), and only after they succeed will it run `fct_customer_orders`.

## **3. Key Related Functions & Variables**

### **`{{ source() }}` - The Starting Point**
While `ref()` points to other dbt models, `source()` points to your **raw data** that exists *outside* your dbt project (defined in `sources.yml`).
```sql
-- Referencing a source table
SELECT * FROM {{ source('jaffle_shop', 'customers') }}
-- Syntax: {{ source(<source_name>, <table_name>) }}
```

### **`{{ this }}` - Self-Reference**
The special variable `this` refers to the **model you are currently building**. It's useful in config blocks or dynamic SQL.
```sql
{{ config(post_hook="GRANT SELECT ON {{ this }} TO reporter_role") }}
```

## **4. Practical `ref()` Patterns**

### **A. Referencing Models in Subdirectories**
Your project structure is part of the reference. Use the relative path from the `models/` directory.
```sql
-- If your model is at models/marts/core/dim_customers.sql
-- To reference models/staging/stg_customers.sql:
SELECT * FROM {{ ref('staging', 'stg_customers') }}

-- For models in the same directory, just use the name:
SELECT * FROM {{ ref('dim_accounts') }}
```

### **B. Organizing with DAGs in Mind**
A well-structured DAG follows a **layered architecture**, which improves clarity, efficiency, and reuse:
```
sources -> staging -> intermediate -> marts -> (optional: analysis)
```
- **Staging (`stg_`)**: Clean and standardize raw data. Light transformations.
- **Intermediate (`int_`)**: Complex business logic, often `ephemeral`.
- **Marts (`dim_`/`fct_`)**: Business-ready tables and views for end-users.

## **5. Using the DAG: Selection Syntax**

Because dbt understands your project's DAG, you can use **selection syntax** to run specific parts of your graph.

### **Basic Selection Methods**
```bash
# Run a specific model
dbt run --select fct_orders

# Run all models in a directory
dbt run --select staging.*

# Run a model and all models UPSTREAM of it (its dependencies)
dbt run --select +fct_orders

# Run a model and all models DOWNSTREAM of it (models that depend on it)
dbt run --select stg_customers+

# Combine: Run a model and its entire DAG neighborhood
dbt run --select +fct_orders+
```

### **Real-World Selection Example**
Imagine you've modified `stg_payments`. You want to test its impact without running your entire project:
```bash
# 1. First, run the modified model
dbt run --select stg_payments

# 2. Then, run all models that depend on it, plus their dependencies
dbt run --select stg_payments+
```
This is far more efficient than `dbt run`, which rebuilds everything.

## **6. Viewing Your Project DAG**

You can visualize your DAG using these methods:

### **dbt Command Line**
```bash
# Generate and serve documentation (includes DAG visualization)
dbt docs generate
dbt docs serve
```
Then open `http://localhost:8080` to see interactive lineage graphs.

### **VS Code (dbt Power User Extension)**
Right-click on any model file and select **"Show DAG for this node"** to see a focused lineage view.

---
### **Summary: The Power of `ref()` and DAGs**

1.  **`{{ ref() }}` is the glue**: It explicitly defines dependencies between models, making relationships clear in your code.
2.  **DAGs enable automation**: dbt automatically calculates the correct execution order, preventing circular references.
3.  **Selection is powerful**: You can surgically run, test, or debug any subset of your DAG using `+` and other selectors.
4.  **Lineage is documentation**: The DAG *is* your data pipeline documentation, always up to date with your code.

**The paradigm shift**: you're no longer just writing SQL scripts — you're declaring nodes in a graph and letting dbt figure out the optimal path to build them. With models and their dependencies in place, testing them for data quality is the natural next step.

## 🔗 Related Notes
- [[Building Models & Materializations|Building Models & Materializations]]
- [[Difference Between Ref and Source Macro|Difference Between ref() and source() Macros]]
- [[dbt Node Selection Syntax|dbt Node Selection Syntax]]

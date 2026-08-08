Views in Databricks are read-only, queryable objects built on top of tables, other views, or data sources. This note covers their types, practical applications, and best practices for data architecture.

---

## 1. Definition of a View in Databricks

A **view** in Databricks is a read-only object that is composed from one or more tables, views, or other data sources. Its most important characteristic is that it is **virtual**. A view does not store the physical data itself; instead, it stores the text of a query that is executed each time the view is referenced.

**Role in Data Architecture:**
- **Abstraction and Simplification:** Views hide the complexity of underlying queries. Business analysts can query a `gold_monthly_sales` view without needing to understand the complex joins and aggregations in the silver layer.
- **Logical Data Organization:** In the Medallion architecture (Bronze, Silver, Gold), views are often used in the Silver or Gold layers to present refined, business-ready data without physical duplication.
- **Governance and Security:** Views are a cornerstone of fine-grained access control. They can be used to restrict access to specific rows or columns (e.g., redacting Personally Identifiable Information (PII)) without altering the underlying base tables.

---

## 2. Types of Views

Databricks offers several types of views, each designed for different use cases and scopes.

### **Temporary Views**
A temporary view is scoped to the current Spark session within a notebook or job. It is ideal for chaining DataFrames or breaking down complex transformations into smaller, readable steps.

- **Scope & Lifecycle:** Tied to the notebook or job's session. It is automatically dropped when the cluster is detached or the notebook is detached from the cluster.
- **Storage Behavior:** Logical only. No physical data is created.
- **Performance:** Since the data is recomputed every time the view is referenced, complex transformations can be slow if used multiple times.
- **Syntax Examples:**
    - **SQL:**
        ```sql
        CREATE OR REPLACE TEMP VIEW recent_orders AS
        SELECT * FROM catalog.schema.orders WHERE order_date > '2023-01-01';
        ```
    - **PySpark:**
        ```python
        df = spark.read.table("catalog.schema.orders")
        df.createOrReplaceTempView("recent_orders")
        ```
- **Access Limitations:** Only accessible within the current notebook or script. Cannot be shared across different jobs or SQL queries.

### **Global Temporary Views**
**Note:** This is a legacy feature from the Hive metastore. Databricks recommends against using them in favor of Temporary Views or Temp Tables.

- **Scope & Lifecycle:** Spans across multiple notebooks within the **same** Spark session/cluster. They are registered to a global temporary database (`global_temp`).
- **Syntax:** `df.createOrReplaceGlobalTempView("view_name")`.
- **Access:** Requires referencing the `global_temp` database (e.g., `SELECT * FROM global_temp.view_name`).

### **Persistent (Permanent) Views**
Persistent views are registered to a schema (database) in a Catalog (like Unity Catalog). They persist across cluster restarts and sessions.

- **Scope & Lifecycle:** Permanent until explicitly dropped. Exists within a specific catalog and schema.
- **Storage Behavior:** Logical only. Stores only the query definition in the Metastore.
- **Schema Evolution:** By default, views are static. If the underlying table schema changes (e.g., adding a new column), a standard `SELECT *` view will **not** reflect the new column. **Databricks Runtime 15.4+** introduces `WITH SCHEMA EVOLUTION` to allow views to automatically adapt to underlying table changes.
- **Performance:** Similar to temporary views; recomputed on every query. Performance depends entirely on the query plan and underlying data engine (Photon/Spark).
- **Syntax:**
    - **SQL (Unity Catalog):**
        ```sql
        -- Standard persistent view
        CREATE OR REPLACE VIEW catalog.schema.active_customers AS
        SELECT customer_id, name FROM catalog.schema.customers WHERE status = 'Active';

        -- Persistent view with Schema Evolution (DBR 15.4+)
        CREATE OR REPLACE VIEW catalog.schema.dynamic_view 
        WITH SCHEMA EVOLUTION AS
        SELECT * FROM catalog.schema.source_table;
        ```
    - **PySpark:**
        ```python
        df = spark.table("catalog.schema.source_data")
        df.createOrReplaceTempView("temp_df")
        spark.sql("CREATE OR REPLACE VIEW catalog.schema.my_view AS SELECT * FROM temp_df")
        ```

### **Materialized Views**
Materialized Views are a new feature (available in Databricks SQL and Delta Live Tables) that **store the results** of the query physically on disk.

- **Scope & Lifecycle:** Persistent and managed by Unity Catalog. Requires a SQL Warehouse or DLT pipeline.
- **Storage Behavior:** Physical. The data is stored in Delta format and **incrementally updated** as the source tables change.
- **Performance:** **Significantly faster** for read-heavy and aggregated queries because it pre-computes the results (e.g., `SUM`, `COUNT`, `JOIN`). It avoids scanning billions of rows in the base tables.
- **Key Properties:** Unlike standard views, they support fresh data without recomputing from scratch.
- **Syntax (Databricks SQL):**
        ```sql
        CREATE MATERIALIZED VIEW catalog.schema.daily_sales_summary
        AS
        SELECT date, SUM(sales) AS total_sales
        FROM catalog.schema.sales
        GROUP BY date;
        ```

### **Dynamic Views (Fine-Grained Access Control)**
A specific type of **persistent view** used for security. They leverage functions like `is_account_group_member()` to filter data at query runtime.

- **Use Case:** Row-level security and Column-level redaction.
- **Requirements:** Requires SQL Warehouse or Shared Access Mode compute. For Dedicated compute, requires DBR 15.4+ and serverless compute enabled for filtering.
- **Example (Column Masking):**
    ```sql
    CREATE VIEW catalog.schema.sales_secure AS
    SELECT 
      user_id,
      CASE WHEN 
        is_account_group_member('auditors') THEN email
        ELSE 'REDACTED'
      END AS email,
      total
    FROM catalog.schema.sales_raw;
    ```

---

## 3. Comparison of View Types

| Feature | Temporary View | Persistent (Standard) View | Materialized View | Dynamic View |
| :--- | :--- | :--- | :--- | :--- |
| **Data Storage** | Logical (None) | Logical (None) | Physical (Delta) | Logical (None) |
| **Scope** | Notebook/Session | Catalog & Schema | Catalog & Schema | Catalog & Schema |
| **Persistence** | No (lost after session) | Yes | Yes | Yes |
| **Performance** | Recomputed every time | Recomputed every time | **Pre-computed / Incremental** | Recomputed with security filters |
| **Freshness** | Real-time to source | Real-time to source | Stale until refresh (Auto or Manual) | Real-time to source |
| **DML Support** | No | No | No (Managed by system) | No |
| **Best For** | Chaining DF operations | Logical abstraction, Security | Aggregations, High-speed dashboards | Row/Column level security |

---

## 4. When to Use Each Type (Decision Criteria)

- **Use Temporary Views when:**
    - You are debugging a complex PySpark transformation.
    - You need to break down a multi-step DataFrame operation within a single notebook.
    - You do not need to share the logic across different jobs.

- **Use Persistent Views when:**
    - **Reusability:** You have a common transformation logic (e.g., "Active Customers") that multiple teams need to access.
    - **Data Governance:** You need to apply row/column level security on top of a Bronze/Silver table without copying the data.
    - **Schema Abstraction:** You want to present a stable schema to business users even if the underlying source tables change (using `WITH SCHEMA EVOLUTION` carefully).

- **Use Materialized Views when:**
    - **Performance:** You have expensive aggregation queries (e.g., `GROUP BY` over trillions of rows) that run slowly.
    - **Cost Reduction:** You want to reduce compute costs by avoiding full table scans for repeated, heavy calculations.
    - **Dashboards:** You need sub-second latency on a BI dashboard that queries aggregated results.

- **Use Dynamic Views when:**
    - You must hide specific PII columns (e.g., email, SSN) from non-privileged users.
    - You need to filter rows based on the user's group membership (e.g., "Managers see all regions, Sales Reps see only their region").

---

## 5. Best Practices

### **Naming Conventions (Medallion Layer)**
In the Lakehouse architecture, use prefixes to indicate the layer and content:
- **Silver Layer (Cleansed):** `silver_` (e.g., `silver_customers`)
- **Gold Layer (Aggregated):** `gold_` (e.g., `gold_monthly_sales`)
- **Security Views:** `secure_` or `restricted_` (e.g., `secure_employee_salary`)
- *Note:* Use lowercase and underscores for readability.

### **Security and Access Control**
- **Avoid Direct Table Access:** Do not grant `SELECT` on raw tables. Grant `SELECT` on views that have dynamic security policies.
- **Unity Catalog only:** Store all permanent views in Unity Catalog to leverage central governance.
- **Compute Requirements:** If you use Dynamic Views with Dedicated compute, be aware of the DBR requirements (15.4 LTS+) and potential serverless compute costs incurred for filtering.

### **Optimization Tips**
1.  **Avoid `SELECT *` without Schema Evolution:** In persistent views, `SELECT *` locks the column list at creation time. If you add a column to the base table, the view breaks or misses it. Use `WITH SCHEMA EVOLUTION` in DBR 15.4+ or explicitly list columns if you want stability.
2.  **Materialize for Speed:** If a view is too slow and the data does not change by the millisecond, use `CREATE TABLE AS (CTAS)` or a Materialized View instead of a standard view.
3.  **Filter Early:** When writing views, push filters (WHERE clauses) inside the view definition. This allows the query planner to prune partitions earlier.

---

## 6. Common Pitfalls and Mistakes

- **Mistake: Treating Standard Views as Performance Tools**
    - *Explanation:* Users often believe a standard view "saves" the data. In reality, **every** query against a standard view triggers a full recomputation of the logic.
    - *Solution:* If you query the same complex join multiple times, write the intermediate results to a **Temporary Table** (`CREATE TABLE ... AS`) or a Materialized View.

- **Mistake: Assuming Schema Evolution is Automatic**
    - *Explanation:* You alter a table to add a column, but the view built with `SELECT *` doesn't show it.
    - *Solution:* Recreate the view using `ALTER VIEW ... AS ...` or recreate it with the `WITH SCHEMA EVOLUTION` clause if using DBR 15.4+.

- **Mistake: Using Global Temp Views**
    - *Explanation:* These are legacy objects that can lead to namespace collisions and are not supported well in Unity Catalog.
    - *Solution:* Use standard Temporary Views if scoped to a notebook, or use a persistent database and `CREATE TEMPORARY TABLE` (materialized) if you need shared scratch space across notebooks.

- **Mistake: Overusing Dynamic Views on Dedicated Compute**
    - *Explanation:* Running complex Dynamic Views on older Dedicated Compute clusters (pre-15.4) or without serverless compute can fail or incur unexpected high costs.
    - *Solution:* Check compute requirements before deploying fine-grained access control to production.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Databricks Concepts/Views/Global Temp Views|Global Temp Views]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Delta Live Tables/View and Streaming Tables/Difference Between Views and Streaming Tables|Difference Between Views and Streaming Tables]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Databricks Concepts/Managed Vs External Tables|Managed vs External Tables (Unity Catalog)]]

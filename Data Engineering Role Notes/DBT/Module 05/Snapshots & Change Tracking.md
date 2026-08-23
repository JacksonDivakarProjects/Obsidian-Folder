# **Module 5, Topic 1: Snapshots & Change Tracking (Unified Guide)**

## **1. What is a Snapshot?**
A snapshot is a **point-in-time historical record** of a mutable dataset. It tracks changes by creating a new record each time a row is updated, along with validity timestamps. This is essential for creating **Type 2 Slowly Changing Dimensions**.

**Core System Columns** (added by dbt):
*   `dbt_scd_id`: Unique identifier for each snapshot row.
*   `dbt_valid_from`: Timestamp when this row version became current.
*   `dbt_valid_to`: Timestamp when this version was replaced (`NULL` = current).
*   `dbt_updated_at`: When dbt processed this change.

## **2. The Two Configuration Methods**

You can create snapshots using either method. The choice depends on **what you're snapshotting** and how much control you need.

| Aspect | **Method 1: SQL File (.sql)** | **Method 2: YAML Properties (.yml)** |
| :--- | :--- | :--- |
| **Primary Use** | Snapshotting **raw source tables** or creating a **custom view** of source data for history. | Snapshotting **an already materialized dbt model** (e.g., a mart or staging table). |
| **Logic & Flexibility** | Contains a full, customizable `SELECT` statement (can filter, join, transform). | **No custom SQL.** Points directly to an existing model via `relation: ref('model_name')`. |
| **File Location** | `snapshots/your_snapshot.sql` | Any `.yml` property file (e.g., `snapshots/snapshots.yml` or a model's property file). |
| **Dependency** | Typically depends on `source()` or early models. | Depends on the **model it references** being built first. |

## **3. Method 1: SQL File Snapshot (The Classic Approach)**
This is the original and most flexible method. You write a `SELECT` statement to define the dataset to track.

**File: `snapshots/snapshot_raw_customers.sql`**
```sql
{% snapshot snapshot_raw_customers %}

{{
    config(
        target_schema='snapshots',
        unique_key='customer_id',
        strategy='timestamp',
        updated_at='updated_at' -- Must exist in the SELECT
    )
}}

-- Custom SQL to define the data you want to track
SELECT
    customer_id,
    email,
    status,
    updated_at -- Critical for 'timestamp' strategy
FROM {{ source('production', 'raw_customers') }}
WHERE email IS NOT NULL -- You can add filters or logic

{% endsnapshot %}
```

## **4. Method 2: YAML Properties Snapshot (The Declarative Approach)**
This newer method is ideal for taking a historical copy of a model that is already defined and built by dbt.

**File: `snapshots/snapshots.yml` or `models/marts/marts.yml`**
```yaml
version: 2

snapshots:
  - name: gold_sales_items_snapshot  # Name of the new snapshot table
    relation: ref('gold_sales_items') # Points to EXISTING dbt model
    config:
      schema: gold                    # Target schema
      database: '{{ target.database }}' # Dynamic database from profile
      unique_key: id                  # Primary key
      strategy: timestamp             # or 'check'
      updated_at: updateDate          # Timestamp column in the model
      # Optional: Replace NULL with a far-future date for BI compatibility
      dbt_valid_to_current: "to_date('9999-12-31')"
```
**Key Parameter Explained:**
*   `relation`: This is the core of the YAML method. It uses `ref()` to specify an **already-defined model** to snapshot. The model (`gold_sales_items`) must be materialized as a table or view.
*   `dbt_valid_to_current`: An **advanced parameter**. By default, current records have `dbt_valid_to = NULL`. This changes it to a concrete date (e.g., `'9999-12-31'`), which often works better with BI tool date filters.

## **5. Snapshot Strategies: Timestamp vs. Check**
Both methods use the same two strategies for detecting changes.

| Strategy | How it Works | Configuration (Applies to Both Methods) |
| :--- | :--- | :--- |
| **`timestamp`** | Compares source `updated_at` with snapshot's `dbt_valid_from`. Creates new row if source is newer. | **Required:** `updated_at: 'column_name'` |
| **`check`** | Hashes specified columns. Creates new row if hash differs from last snapshot version. | **Required:** `check_cols: ['col1', 'col2']` or `check_cols: 'all'` |

**Example of `check` strategy in YAML:**
```yaml
snapshots:
  - name: customer_snapshot
    relation: ref('dim_customers')
    config:
      unique_key: customer_key
      strategy: check
      check_cols: ['customer_tier', 'region'] # Only track changes in these columns
```

## **6. How to Execute & The Crucial Dependency Order**
Execution uses the same command, but **dependency management differs**.

### **For SQL File Snapshots:**
```bash
# Snapshot is independent. Run it anytime.
dbt snapshot --select snapshot_raw_customers
```

### **For YAML Properties Snapshots:**
The referenced model **must exist first**. Use `dbt build` for correct ordering.

```bash
# WRONG ORDER - This will fail if gold_sales_items doesn't exist yet
dbt snapshot --select gold_sales_items_snapshot

# CORRECT APPROACH 1: Run model first, then snapshot
dbt run --select gold_sales_items
dbt snapshot --select gold_sales_items_snapshot

# CORRECT APPROACH 2: Use `dbt build` (handles dependencies automatically)
dbt build --select gold_sales_items gold_sales_items_snapshot
# OR build everything
dbt build
```

## **7. Querying Historical Data**
Query syntax is identical regardless of creation method. Use the validity columns for point-in-time analysis.

```sql
-- Get the complete history of record ID 123
SELECT *
FROM {{ ref('gold_sales_items_snapshot') }}
WHERE id = 123
ORDER BY dbt_valid_from;

-- Query state 'as of' a specific date
-- NOTE: Adjust if using dbt_valid_to_current!
SELECT *
FROM {{ ref('gold_sales_items_snapshot') }}
WHERE '2024-06-01' BETWEEN dbt_valid_from 
                    AND COALESCE(dbt_valid_to, '9999-12-31');

-- Find all price changes for a product
SELECT 
    product_id,
    price,
    dbt_valid_from as effective_from
FROM {{ ref('product_snapshot') }}
WHERE product_id = 456
  AND dbt_valid_to IS NOT NULL;
```

## **8. Decision Guide: Which Method to Use?**

**Use the SQL File Method when:**
- Snapshotting **raw source tables** (using `source()`).
- You need to **filter, join, or transform** data before tracking history.
- You want to snapshot only a **subset** of a source table's columns or rows.

**Use the YAML Properties Method when:**
- Snapshotting **an existing dbt model** (using `ref()`).
- You want to track changes to a **final mart or dimension table**.
- You prefer **declarative configuration** alongside other model properties.
- The model logic is already defined elsewhere and doesn't need alteration.

## **9. Advanced Configuration & Best Practices**

### **Handling Hard Deletes**
When a row disappears from your source, control whether to mark it as invalid.

```sql
-- In SQL File config block
{{ config(invalidate_hard_deletes=True) }}
```
```yaml
# In YAML Properties config
config:
  invalidate_hard_deletes: true
```

### **Best Practices**
1.  **Strategy Choice**: Prefer `timestamp` if you have a reliable `updated_at` column.
2.  **Run Frequency**: Schedule `dbt snapshot` runs consistently (e.g., daily) to avoid gaps in history.
3.  **Monitor Growth**: Snapshot tables grow indefinitely. Implement data retention policies.
4.  **Test Your Snapshots**: Add generic tests in a `snapshots.yml` file to validate `unique_key` and `not_null` on system columns.
5.  **Use `dbt build`**: Especially with YAML snapshots, `dbt build` ensures proper execution order.

---
## **Final Summary**

1.  **Two methods, one purpose**: SQL files offer **flexibility** for raw data; YAML properties offer **simplicity** for existing models.
2.  **Core configuration**: both methods share the same `strategy`, `unique_key`, and `updated_at`/`check_cols` settings.
3.  **Key difference**: SQL files contain the `SELECT` logic; YAML files use `relation: ref('...')` to point at an existing model.
4.  **Execution matters**: YAML snapshots depend on their referenced model being built first — use `dbt build`.
5.  **Powerful result**: either method creates a queryable history with `dbt_valid_from` and `dbt_valid_to` columns.

## 🔗 Related Notes
- [[Snapshots|Snapshots (dbt Learn links)]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Important TBLProperties/Change Data Feed|Delta Lake – Change Data Feed]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Questions/How Versioning Works in Delta Lake|How Versioning Works in Delta Lake]]
- [[dbt Node Selection Syntax|dbt Node Selection Syntax]]

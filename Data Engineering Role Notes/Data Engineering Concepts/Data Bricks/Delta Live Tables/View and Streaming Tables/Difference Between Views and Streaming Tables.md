Let's break down the three dataset types from your example. The key distinction lies in **how the data is computed and stored**.

### 1. Materialized View (Live Table)
**Syntax & Behavior**
```python
@dlt.table(name="customer_metrics", comment="Aggregated customer data")
def customer_metrics():
    return spark.read.table("sales_db.orders") \
        .groupBy("customer_id") \
        .agg({"amount": "sum", "order_id": "count"})
```
- **Definition**: Uses the `@dlt.table` decorator with a function returning a **batch DataFrame** (i.e., `spark.read.table`).
- **Update Mode**: **Full Refresh**. Every time the pipeline runs, DLT truncates the target table and recalculates the entire result from the current source data.
- **Storage**: Data is physically saved as a Delta table in the target schema/storage location.
- **When to Use**:
  - Aggregations that need to reflect the entire source table state (e.g., daily summaries, KPI snapshots).
  - Queries that are expensive to compute repeatedly and are consumed by multiple downstream processes.

### 2. Streaming Table (Incremental)
**Syntax & Behavior**
```python
@dlt.table(name="raw_orders")
def raw_orders():
    return spark.readStream.format("cloudFiles") \
        .option("cloudFiles.format", "json") \
        .load("/path/to/orders")
```
- **Definition**: Also uses `@dlt.table` but returns a **streaming DataFrame** (initiated with `spark.readStream`).
- **Update Mode**: **Incremental Append**. DLT processes only *new* data files since the last pipeline update and appends those records to the existing table. It does not reprocess old data (unless you perform a full refresh manually).
- **Storage**: Data is saved incrementally as a Delta table.
- **When to Use**:
  - Landing raw data from cloud storage (Bronze layer).
  - Low-latency ingestion where data arrives continuously.

> **⚠️ Critical Distinction**: `@dlt.table` is a *single decorator* that infers behavior based on the **source type** inside the function:
> - `spark.read` → **Materialized View** (Full Compute)
> - `spark.readStream` → **Streaming Table** (Incremental Append)

### 3. View (Temporary)
**Syntax & Behavior**
```python
@dlt.view(name="validated_orders")
def validated_orders():
    return dlt.read("raw_orders").filter("order_amount > 0")
```
- **Definition**: Uses the `@dlt.view` decorator.
- **Update Mode**: **None (Computed on read)**. The data is **not stored** on disk. It is simply a saved query definition. Every time another table reads from `LIVE.validated_orders`, DLT re-executes the filter logic on the current snapshot of `raw_orders`.
- **Storage**: **No storage cost**.
- **When to Use**:
  - Intermediate transformation logic (avoid saving intermediate tables to save cost).
  - Data quality validation that doesn't need to be persisted separately.
  - Reducing the number of materialized tables in the pipeline DAG.

### Summary of Differences

| Feature | Materialized View | Streaming Table | View |
| :--- | :--- | :--- | :--- |
| **Decorator** | `@dlt.table` | `@dlt.table` | `@dlt.view` |
| **Function Return** | Batch DataFrame | Streaming DataFrame | Batch or Streaming DF |
| **Processing** | Full recompute | Incremental append | Re-executed on every call |
| **Stored on Disk** | ✅ Yes (Delta) | ✅ Yes (Delta) | ❌ No |
| **SQL Equivalent** | `CREATE MATERIALIZED VIEW` | `CREATE STREAMING TABLE` | `CREATE TEMPORARY LIVE VIEW` |

### SQL Syntax Equivalents (For Reference)

```sql
-- Materialized View
CREATE OR REFRESH MATERIALIZED VIEW customer_metrics
AS SELECT customer_id, SUM(amount) FROM sales_db.orders GROUP BY customer_id;

-- Streaming Table
CREATE OR REFRESH STREAMING TABLE raw_orders
AS SELECT * FROM STREAM read_files('/path/to/orders', 'json');

-- View
CREATE TEMPORARY LIVE VIEW validated_orders
AS SELECT * FROM LIVE.raw_orders WHERE order_amount > 0;
```

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Databricks Concepts/Views/Views|Views]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Delta Live Tables/Delta Live Tables|Delta Live Tables (DLT) Comprehensive Guide]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Databricks Concepts/Views/Global Temp Views|Global Temp Views]]

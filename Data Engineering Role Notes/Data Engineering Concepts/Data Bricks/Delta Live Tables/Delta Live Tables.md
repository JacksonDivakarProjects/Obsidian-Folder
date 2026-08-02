## Delta Live Tables (DLT) Comprehensive Guide

### 1. What is Delta Live Tables?

Delta Live Tables (DLT) is a declarative ETL framework within Databricks that simplifies building and managing reliable data pipelines. Instead of writing complex orchestration logic, users define desired data transformations using SQL or Python. DLT automates infrastructure management, dependency resolution, error handling, performance optimization, and data quality enforcement, allowing data engineers to focus on business logic rather than operational complexities.

Key benefits include:
- **Declarative Pipelines**: Define what data to transform, not how to orchestrate it.
- **Built-in Data Quality**: Use expectations to validate, drop, or fail records based on custom rules.
- **Automated Operations**: Automatic schema management, error handling, dependency detection, and scaling.
- **Unified Experience**: Supports both Python and SQL interfaces.

### 2. Core Concepts

**Dataset Types in DLT**

DLT introduces three dataset types to optimize performance and cost:

| Type | Description | When to Use |
|------|-------------|-------------|
| **Materialized View (Live Table)** | Computed results stored as Delta table; refreshed fully each update. | Queries with high read frequency, complex aggregations, or consumed by downstream jobs. |
| **Streaming Table** | Incrementally updated table for append-only sources or CDC feeds. | Continuously growing data sources; low-latency requirements. |
| **View** | Non-materialized temporary view computed on-demand. | Intermediate transformations to break complex logic or validate data without storage cost. |

**Medallion Architecture in DLT**

DLT pipelines naturally align with the medallion architecture (Bronze → Silver → Gold):

- **Bronze Layer**: Raw ingestion with minimal transformations.
- **Silver Layer**: Cleansed, validated, and enriched data.
- **Gold Layer**: Business-ready aggregated tables for analytics.

### 3. Getting Started

**Prerequisites**:
- Databricks workspace (Premium+ for DLT; Advanced required for expectations).
- Cluster creation permissions or serverless DLT enabled.
- Unity Catalog recommended (target schema with appropriate privileges).

**Creating a Pipeline**:
1. In Databricks UI: **Workflows → Delta Live Tables → Create Pipeline**.
2. Configure pipeline settings: name, notebook path, target schema, edition, and optional configurations.
3. Run the pipeline update to execute transformations.

### 4. Core Features and Syntax

#### 4.1 Creating Tables and Views

**Python Syntax**

```python
import dlt

# Materialized View
@dlt.table(name="customer_metrics", comment="Aggregated customer data")
def customer_metrics():
    return spark.read.table("sales_db.orders") \
        .groupBy("customer_id") \
        .agg({"amount": "sum", "order_id": "count"})

# Streaming Table (Auto Loader)
@dlt.table(name="raw_orders")
def raw_orders():
    return spark.readStream.format("cloudFiles") \
        .option("cloudFiles.format", "json") \
        .load("/path/to/orders")

# View
@dlt.view(name="validated_orders")
def validated_orders():
    return dlt.read("raw_orders").filter("order_amount > 0")
```

**SQL Syntax**

```sql
-- Materialized View
CREATE OR REFRESH MATERIALIZED VIEW customer_metrics
AS SELECT customer_id, SUM(amount) AS total_spent, COUNT(order_id) AS order_count
FROM sales_db.orders
GROUP BY customer_id;

-- Streaming Table with Auto Loader
CREATE OR REFRESH STREAMING TABLE raw_orders
AS SELECT * FROM STREAM read_files('/path/to/orders', 'json');

-- View
CREATE TEMPORARY LIVE VIEW validated_orders
AS SELECT * FROM LIVE.raw_orders WHERE order_amount > 0;
```

**Important Notes**:
- Python functions with `@table` or `@view` decorators must return a DataFrame and should not include side-effect operations (e.g., `collect()`, `count()`, `save()`).
- SQL requires `STREAM` keyword for streaming reads and `LIVE` prefix to reference pipeline datasets.

#### 4.2 Data Quality with Expectations

Expectations enforce data quality rules on each record, with three possible actions: `WARN` (default), `DROP`, or `FAIL`.

**Python Example**:
```python
# Single expectation (warning)
@dlt.table
@dlt.expect("valid_order_amount", "order_amount > 0")
def orders_clean():
    return dlt.read("raw_orders")

# Multiple expectations with different actions
order_rules = {
    "valid_status": "order_status IN ('COMPLETED', 'PENDING', 'CANCELLED')",
    "valid_amount": "order_amount BETWEEN 1 AND 10000"
}

@dlt.table
@dlt.expect_all(order_rules)  # WARN by default
@dlt.expect_or_drop("non_null_customer", "customer_id IS NOT NULL")
@dlt.expect_or_fail("positive_quantity", "quantity > 0")
def silver_orders():
    return dlt.read("bronze_orders")
```

**SQL Example**:
```sql
CREATE OR REFRESH STREAMING TABLE silver_orders(
    CONSTRAINT valid_status EXPECT (order_status IN ('COMPLETED', 'PENDING', 'CANCELLED')),
    CONSTRAINT valid_amount EXPECT (order_amount > 0) ON VIOLATION DROP ROW,
    CONSTRAINT positive_quantity EXPECT (quantity > 0) ON VIOLATION FAIL UPDATE
) AS SELECT * FROM STREAM(LIVE.bronze_orders);
```

**Monitoring Expectations**: Query the DLT event log to view data quality metrics (e.g., number of records passing/failing each expectation).

#### 4.3 Change Data Capture (CDC) with APPLY CHANGES

The `APPLY CHANGES` API simplifies CDC processing, automatically handling out-of-sequence records and supporting SCD Type 1 and Type 2.

**Python Example**:
```python
import dlt

# Create target streaming table
dlt.create_streaming_table(name="customers_scd1")

# Apply changes from CDC feed
dlt.apply_changes(
    target="customers_scd1",
    source="raw_customers_cdc",
    keys=["customer_id"],
    sequence_by="event_timestamp",
    apply_as_deletes="operation = 'DELETE'",
    apply_as_truncates="operation = 'TRUNCATE'"
)

# SCD Type 2 (track history)
dlt.create_streaming_table(name="customers_scd2")
dlt.apply_changes(
    target="customers_scd2",
    source="raw_customers_cdc",
    keys=["customer_id"],
    sequence_by="event_timestamp",
    stored_as_scd_type=2,
    track_history_column_list=["address", "tier"]
)
```

**SQL Example**:
```sql
CREATE OR REFRESH STREAMING TABLE customers_scd1;

APPLY CHANGES INTO LIVE.customers_scd1
FROM STREAM(LIVE.raw_customers_cdc)
KEYS (customer_id)
SEQUENCE BY event_timestamp
WHERE operation = 'DELETE' AS DELETE
WHERE operation = 'TRUNCATE' AS TRUNCATE;
```

**Key Points**:
- Requires a monotonically increasing sequence column for ordering.
- DLT creates an internal backing table (`__apply_changes_storage_`) and a view for querying processed data.
- Use `stored_as_scd_type=2` for SCD Type 2 with automatic `__START_AT`/`__END_AT` columns.

#### 4.4 Incremental Processing with Flows and Append Flow

**Implicit Flows**: Most streaming tables automatically define a flow without explicit declaration.

**Append Flow**: Explicitly combine multiple streaming sources into a single table, enabling backfills or regional rollouts without full refresh.

**Python Example**:
```python
import dlt

# Create target table
dlt.create_streaming_table(name="unified_orders")

# Append from multiple sources
@dlt.append_flow(target="unified_orders")
def orders_region_us():
    return spark.readStream.format("cloudFiles") \
        .option("cloudFiles.format", "json") \
        .load("/path/to/orders_us/")

@dlt.append_flow(target="unified_orders")
def orders_region_eu():
    return spark.readStream.format("cloudFiles") \
        .option("cloudFiles.format", "json") \
        .load("/path/to/orders_eu/")
```

**SQL Example**:
```sql
CREATE OR REFRESH STREAMING TABLE unified_orders AS
SELECT * FROM STREAM read_files('/path/to/orders_us/', 'json');

CREATE FLOW unified_orders_eu
INSERT INTO unified_orders BY NAME
SELECT * FROM STREAM read_files('/path/to/orders_eu/', 'json');
```

### 5. Advanced Features and Patterns

#### 5.1 Enhanced Autoscaling

DLT's enhanced autoscaling dynamically adjusts cluster resources based on pending tasks and slot utilization, providing predictive scale-out and safe scale-in for streaming workloads.

**Configuration**:
- Set `spark.databricks.delta.liveTables.cluster.scaleOutWindow` and related parameters in pipeline settings.
- Monitor autoscaling behavior via DLT UI metrics (pending tasks, executor count).

#### 5.2 Pipeline Configurations and Options

**Key Pipeline Settings**:
- **Product Edition**: Core (basic), Pro (photon acceleration), Advanced (expectations).
- **Cluster Policies**: Define instance types, autoscaling, and spot instance usage.
- **Storage Location**: Custom path for Delta tables (default is managed location).
- **Continuous vs. Triggered**: Continuous pipelines run perpetually for streaming sources.

**Example Pipeline Configuration (JSON)**:
```json
{
  "name": "retail_analytics_dlt",
  "edition": "ADVANCED",
  "clusters": [{
    "label": "default",
    "autoscale": {
      "min_workers": 2,
      "max_workers": 10
    }
  }],
  "development": true,
  "continuous": false,
  "libraries": [{"notebook": {"path": "/Workspace/Users/me/dlt_pipeline.py"}}],
  "target": "retail_db"
}
```

#### 5.3 Event Hooks for External Integrations

Use event hooks to trigger actions (e.g., emails, monitoring alerts) at specific pipeline stages without affecting data processing.

```python
import dlt

@dlt.on_event("on_start")
def on_pipeline_start():
    print("Pipeline started - notify monitoring system")

@dlt.on_event("on_completion")
def on_pipeline_completion(state):
    if state == "SUCCESS":
        print("Pipeline succeeded")
    else:
        print(f"Pipeline completed with state: {state}")
```

### 6. Best Practices

1. **Leverage Medallion Architecture**: Structure pipelines in Bronze, Silver, Gold layers for clarity and maintainability.

2. **Use Views for Intermediate Logic**: Avoid materializing every transformation; use views to break complex queries and validate data without storage overhead.

3. **Apply Expectations Early**: Validate data as close to the source as possible to prevent bad data from propagating.

4. **Optimize Auto Loader**: Use `cloudFiles.schemaLocation` and `cloudFiles.schemaEvolutionMode` to manage schema drift.

5. **Monitor and Tune**: Query DLT event logs for pipeline health, data quality metrics, and performance bottlenecks.

6. **Use Append Flow Over UNION**: Append flow enables incremental updates and backfills without full refresh, improving efficiency for multi-source streaming tables.

7. **Design for Scalability**: Configure enhanced autoscaling based on workload patterns; tune `spark.sql.shuffle.partitions` appropriately.

8. **Test in Development Mode**: Set `development: true` in pipeline settings to use reusable clusters during development, reducing startup time.

9. **Adopt Unity Catalog**: Manage DLT tables as Unity Catalog objects for better governance, lineage tracking, and security.

### 7. Monitoring and Observability

- **DLT UI**: Visual DAG showing table dependencies, update status, and data quality metrics.
- **Event Log**: Query `event_log` table in pipeline storage location for detailed metrics, error messages, and lineage.
- **Databricks SQL**: Create dashboards on event log for operational monitoring.

### 8. Conclusion

Delta Live Tables provides a powerful, declarative framework for building production-grade ETL pipelines on Databricks. By abstracting orchestration complexities and integrating data quality, CDC, and incremental processing, DLT accelerates time-to-value while ensuring reliability and maintainability. Whether using Python or SQL, data engineers can define transformations intuitively and let DLT handle the rest

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Delta Live Tables/AutoCDC API/AutoCDC in DLT|AutoCDC in DLT]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Delta Live Tables/View and Streaming Tables/Difference Between Views and Streaming Tables|Difference Between Views and Streaming Tables]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Important TBLProperties/Change Data Feed|Delta Lake – Change Data Feed]]

## Global Temporary Views in Databricks

**Definition**: A global temporary view is a Spark SQL view shared across every notebook and session attached to the same cluster, registered under the special `global_temp` database.

## Core Properties

- **Scope**: Cluster-wide — visible to all notebooks attached to the same cluster.
- **Database**: Always registered under `global_temp`.
- **Persistence**: Exists until the cluster restarts (not saved anywhere permanent).
- **Storage**: None — it is a logical query definition, not physical data.
- **Visibility**: Must be queried with the `global_temp.` prefix.

## Syntax

**SQL**
```sql
CREATE OR REPLACE GLOBAL TEMP VIEW sales_view AS
SELECT * FROM sales_data;
```

**Access**
```sql
SELECT * FROM global_temp.sales_view;
```

**PySpark**
```python
df.createOrReplaceGlobalTempView("sales_view")
```

## How It Works

- No data is stored — only the query definition.
- Every time the view is queried, Spark re-executes the underlying query against the current data.
- The definition lives in a shared, cluster-scoped system database (`global_temp`), which is a legacy Hive-metastore construct, not part of Unity Catalog's three-level namespace.

## Example Flow

Notebook A (defines the view):
```sql
CREATE GLOBAL TEMP VIEW temp_kpi AS
SELECT region, SUM(revenue) AS total_revenue
FROM sales
GROUP BY region;
```

Notebook B, same cluster (reads it):
```sql
SELECT * FROM global_temp.temp_kpi;
```

## Temp View vs Global Temp View

| Feature | Temp View | Global Temp View |
|---|---|---|
| Scope | Single notebook/session | Entire cluster |
| Prefix required | No | Yes (`global_temp.`) |
| Shareable across notebooks | No | Yes |
| Lifetime | Session | Cluster lifetime |

## When to Use

- Multi-notebook workflows running on the same cluster.
- Sharing intermediate results without writing a table.
- Orchestration pipelines where separate steps run in separate notebooks but need to hand off a result.

## Gotchas

- Lost on cluster restart — not suitable for anything that needs to persist.
- No performance benefit — the query is recomputed on every read, same as a regular temp view.
- Databricks generally recommends avoiding global temp views in favor of writing to a real table when data needs to be shared reliably, since `global_temp` predates Unity Catalog and doesn't participate in its governance model.

## 🔗 Related Notes
- [[Views|Views]]
- [[Difference Between Views and Streaming Tables|Difference Between Views and Streaming Tables]]

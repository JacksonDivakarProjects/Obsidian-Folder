# Data Bricks

Overview of Databricks notes: Unity Catalog storage & governance, views/temporary objects, job parameter passing, and Delta Live Tables (DLT) pipelines including change data capture.

## 🗺️ Map of Content (auto-generated)

### Unity Catalog — Storage & Governance
- [[Managed Vs External Tables|Managed vs External Tables (Unity Catalog)]] — the catalog.schema.table hierarchy, managed vs. external storage resolution, and a real-world medallion (bronze/silver/gold) setup.
- [[Volumes|Comprehensive Guide to Volumes in Databricks Unity Catalog]] — governed storage for non-tabular files: managed vs. external volumes, path structure, and core operations.

### Views & Temporary Objects
- [[Views|Views]] — temporary, persistent, materialized, and dynamic views compared, with syntax and best practices.
- [[Global Temp Views|Global Temp Views]] — cluster-wide temporary views via the `global_temp` database.

### Job Orchestration
- [[Databricks Parameter Passing|Databricks Jobs Parameter Passing — dbutils.widgets vs dbutils.jobs.taskValues]] — passing inputs into notebooks and passing values between job tasks.

### Delta Live Tables (DLT)
- [[Delta Live Tables|Delta Live Tables (DLT) Comprehensive Guide]] — declarative pipelines, dataset types, expectations, CDC, and best practices.
- [[AutoCDC in DLT|AutoCDC in DLT]] — how `create_auto_cdc_flow` interprets CDC operation columns to delete, truncate, or upsert.
- [[Difference Between Views and Streaming Tables|Difference Between Views and Streaming Tables]] — materialized view vs. streaming table vs. view inside a DLT pipeline.

### Reference
- [[Databricks Links|Databricks Links]] — external documentation links.
- [[Databricks Training Images|Databricks Training Images]] — reference screenshots grouped by Autoloader, DLT, Unity Catalog, and Volumes.
- [[ETL Operations and SCDs|ETL Operations and SCDs]] — a Databricks notebook archive (.dbc) for practicing ETL/SCD patterns.

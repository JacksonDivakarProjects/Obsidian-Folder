# Data Bricks

Overview of Databricks notes: Unity Catalog storage & governance, views/temporary objects, job parameter passing, and Delta Live Tables (DLT) pipelines including change data capture.

## 🗺️ Map of Content (auto-generated)

### Unity Catalog — Storage & Governance
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Databricks Concepts/Managed Vs External Tables|Managed vs External Tables (Unity Catalog)]] — the catalog.schema.table hierarchy, managed vs. external storage resolution, and a real-world medallion (bronze/silver/gold) setup.
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Databricks Concepts/Volumes|Comprehensive Guide to Volumes in Databricks Unity Catalog]] — governed storage for non-tabular files: managed vs. external volumes, path structure, and core operations.

### Views & Temporary Objects
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Databricks Concepts/Views/Views|Views]] — temporary, persistent, materialized, and dynamic views compared, with syntax and best practices.
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Databricks Concepts/Views/Global Temp Views|Global Temp Views]] — cluster-wide temporary views via the `global_temp` database.

### Job Orchestration
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Databricks Concepts/Parameters Passing with DBUTILS Widgets/Databricks Parameter Passing|Databricks Jobs Parameter Passing — dbutils.widgets vs dbutils.jobs.taskValues]] — passing inputs into notebooks and passing values between job tasks.

### Delta Live Tables (DLT)
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Delta Live Tables/Delta Live Tables|Delta Live Tables (DLT) Comprehensive Guide]] — declarative pipelines, dataset types, expectations, CDC, and best practices.
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Delta Live Tables/AutoCDC API/AutoCDC in DLT|AutoCDC in DLT]] — how `create_auto_cdc_flow` interprets CDC operation columns to delete, truncate, or upsert.
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Delta Live Tables/View and Streaming Tables/Difference Between Views and Streaming Tables|Difference Between Views and Streaming Tables]] — materialized view vs. streaming table vs. view inside a DLT pipeline.

### Reference
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Databricks Links|Databricks Links]] — external documentation links.
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Databricks Training Images/Databricks Training Images|Databricks Training Images]] — reference screenshots grouped by Autoloader, DLT, Unity Catalog, and Volumes.
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/ETL Operations and SCDs .dbc File/ETL Operations and SCDs|ETL Operations and SCDs]] — a Databricks notebook archive (.dbc) for practicing ETL/SCD patterns.

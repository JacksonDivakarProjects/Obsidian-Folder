[[Spark/Spark|Spark]]
[[Data Engineering Concepts Images/Data Engineering Concept Images|Data Engineering Concept Images]]
[[Delta Lake/Delta Lake|Delta Lake]]
[[JSON File Format|JSON File Format]]
[[Data Engineering Role Notes/Data Engineering Concepts/Miscellaneous/Miscellaneous|Miscellaneous]]
[[Optimization for Data Read/Optimization for Data Read|Optimization for Data Read]]

## 🗺️ Map of Content (auto-generated)

- [[Azure Data Engineering|Azure Data Engineering]] — currently just a self-hosted file system configuration reference screenshot; no deeper Azure-specific DE tooling notes yet.
- [[DBT|DBT]] — dbt fundamentals, project configuration & Jinja, models & materializations, testing framework, snapshots & node selection, dbt commands/flags, YAML reference, dbt Python models.
- [[Data Bricks|Data Bricks]] — Unity Catalog managed/external tables & Volumes, Databricks views (temp/global temp/materialized/dynamic), job parameter passing (widgets/taskValues), Delta Live Tables & AutoCDC (CDC).
- [[Delta Lake/Delta Lake|Delta Lake]] — ACID properties, Python & SQL command APIs, table utilities/Change Data Feed, open table formats & UniForm, OPTIMIZE/Z-Ordering/Liquid Clustering, versioning & time travel internals.
- Docker — no folder overview note yet; see [[Docker Hub Practice|Docker Hub Practice]] for the login/build/push/pull workflow, plus notes on Windows installation, persistent volumes for stateful containers, and Linux users/groups for Docker permissions.
- [[Fabric|Fabric]] — Microsoft Fabric training reference screenshots (Azure-native counterpart to Databricks); no deeper notes yet.
- [[JSON File Format|JSON File Format]] — JSON fundamentals, document shapes (single-line, nested, NDJSON/JSON Lines, JSON Schema), Python's `json` module, `pandas.json_normalize` for flattening.
- Methodologies — [[Methodologies/Kimball Methodology|Kimball Methodology]]: dimensional modeling, star vs snowflake schema, fact/dimension tables, Slowly Changing Dimensions (SCD 1/2/3), surrogate vs natural keys, conformed/junk/degenerate/role-playing dimensions, Kimball layering in dbt.
- [[Data Engineering Role Notes/Data Engineering Concepts/Miscellaneous/Miscellaneous|Miscellaneous]] — backdated refresh/historical reprocessing, data lakehouse architecture, dimensional data modeling (OLTP vs OLAP), fundamentals of data engineering (warehouse layers, file formats, Azure stack).
- [[Optimization for Data Read/Optimization for Data Read|Optimization for Data Read]] — predicate pushdown, predicate pruning/data skipping, column pruning, Spark Catalyst optimizer internals, Delta Lake transaction-log statistics.
- [[Spark/Spark|Spark]] — join strategies (Broadcast/Shuffle Hash/Sort-Merge), Spark driver & executor memory architecture, driver/executor OOM causes & fixes (incl. salting for skew), execution model (Job/Stage/Task), fact table types.

## 🔗 Cross-Topic Connections (auto-generated)

- **Delta Lake is the storage layer Spark and Databricks read and write.** Databricks' Unity Catalog tables/Volumes and Delta Live Tables pipelines are built directly on Delta Lake, and Spark's join strategies and memory management determine how efficiently those Delta tables get queried and written.
- **Optimization for Data Read explains the internals behind both Spark and Delta Lake.** Predicate pushdown/pruning and column pruning are executed by Spark's Catalyst optimizer against Delta Lake's transaction-log statistics — the same mechanics that motivate Delta's OPTIMIZE/Z-Ordering/Liquid Clustering commands.
- **DBT and Spark/Databricks both operate on the dimensional models described in Methodologies and Miscellaneous.** dbt models (and the Kimball star-schema/SCD patterns in Methodologies) are typically materialized as Delta tables on Spark/Databricks compute, so the modeling vocabulary (facts, dimensions, grain, SCDs) recurs across DBT, Data Bricks, Delta Lake, and Spark notes.
- **Docker underlies local/CI deployment of the rest of the stack.** Containerized databases (e.g., the MySQL persistent-storage example) and reproducible dev environments are how dbt, Spark, and other tools in this vault typically get run outside of a managed cloud service.
- **Azure Data Engineering and Fabric are the thin Azure-native counterparts to Data Bricks.** Microsoft Fabric packages Spark, Delta Lake (as OneLake), and pipeline orchestration much like Databricks does on Azure — both folders are currently placeholders compared to the fleshed-out Data Bricks and Delta Lake notes.
- **JSON File Format is a common raw ingestion format feeding the rest of the pipeline.** Source JSON typically gets landed and then transformed by Spark/dbt into the Delta Lake tables and Kimball-style dimensional models covered elsewhere in this vault.

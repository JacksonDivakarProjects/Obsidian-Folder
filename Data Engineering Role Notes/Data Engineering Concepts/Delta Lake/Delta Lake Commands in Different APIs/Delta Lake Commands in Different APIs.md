# Delta Lake Commands in Different APIs

Delta Lake exposes the same operations (create, read, write, upsert, time travel, optimize, vacuum) through two APIs. Pick whichever fits the calling context — they operate on the same underlying tables and transaction log.

- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Delta Lake Commands in Different APIs/Delta Lake Commands in Python API with Spark|Delta Lake Commands in Python API with Spark]] — the `DeltaTable` / DataFrame API used from PySpark jobs and notebooks.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Delta Lake Commands in Different APIs/Delta Lake Commands in SQL API|Delta Lake Commands in SQL API]] — the same operations expressed as Spark SQL DDL/DML, used from notebooks, BI tools, or `spark.sql()`.

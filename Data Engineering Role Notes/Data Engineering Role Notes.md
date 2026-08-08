

[[Data Engineering Concepts]]
[[Data Science]]
[[SQL]]
[[PySpark]]
[[Linux]]
[[Git and Github]]
[[Airflow Scheduler]]
[[Web Scraping]]
[[Data Science/Miscellaneous/Miscellaneous|Miscellaneous]]
[[Excel]]





## 🗺️ Map of Content (auto-generated)
- [[Data Engineering Role Notes/Airflow Scheduler/Airflow Scheduler|Airflow Scheduler]] — Apache Airflow installation, scheduler internals, operators, and DAG concepts.
- [[Data Engineering Role Notes/Linux/Linux|Linux]] — Shell fundamentals: awk, bash scripting, compression, permissions, find, aliases, nohup, and cache/yt-dlp utilities.
- [[Data Engineering Role Notes/Web Scraping/Web Scraping|Web Scraping]] — BeautifulSoup, Selectolax, and Selenium for HTML parsing and browser automation.
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Engineering Concepts|Data Engineering Concepts]] — dbt, Databricks & Delta Live Tables, Delta Lake internals, Spark internals, read-path query optimization, Kimball dimensional modeling, Docker, and the Azure/Fabric ecosystem.
- [[Data Engineering Role Notes/SQL/SQL|SQL]] — Query optimization & execution plans, indexing internals (B-tree, columnstore), table scan types, join/sort algorithms, recursive CTEs, window functions, and procedural SQL (stored procedures, triggers, views).
- [[Data Engineering Role Notes/Pyspark/PySpark|PySpark]] — Core DataFrame operations, performance & optimization (partitioning, shuffling, broadcast joins), Structured Streaming (triggers, windows, watermarking), I/O & schema management, SCDs, and Spark standalone cluster setup.

## 🔗 Cross-Topic Connections (auto-generated)
- Airflow orchestrates the same shell/Bash tooling covered in [[Data Engineering Role Notes/Linux/Linux|Linux]] (e.g. BashOperator, nohup for long-running tasks).
- [[Data Engineering Role Notes/Web Scraping/Web Scraping|Web Scraping]] pipelines are commonly scheduled via [[Data Engineering Role Notes/Airflow Scheduler/Airflow Scheduler|Airflow Scheduler]] DAGs.
- Spark/Databricks jobs and dbt models documented in [[Data Engineering Role Notes/Data Engineering Concepts/Data Engineering Concepts|Data Engineering Concepts]] are typically orchestrated by [[Data Engineering Role Notes/Airflow Scheduler/Airflow Scheduler|Airflow Scheduler]] DAGs and run in Docker containers deployed using the [[Data Engineering Role Notes/Linux/Linux|Linux]] fundamentals covered here.
- dbt/Spark pipelines in [[Data Engineering Role Notes/Data Engineering Concepts/Data Engineering Concepts|Data Engineering Concepts]] often consume raw data gathered via the [[Data Engineering Role Notes/Web Scraping/Web Scraping|Web Scraping]] notes.
- [[Data Engineering Role Notes/Pyspark/PySpark|PySpark]] jobs (batch and Structured Streaming) are typically scheduled and monitored as tasks within [[Data Engineering Role Notes/Airflow Scheduler/Airflow Scheduler|Airflow Scheduler]] DAGs.
- [[Data Engineering Role Notes/Pyspark/PySpark|PySpark]]'s DataFrame API and the Spark internals covered in [[Data Engineering Role Notes/Data Engineering Concepts/Data Engineering Concepts|Data Engineering Concepts]] are companion references — the former is the practical API surface, the latter is the engine internals (execution plans, shuffle, caching) behind it.
- [[Data Engineering Role Notes/SQL/SQL|SQL]] query optimization concepts (execution plans, joins, indexing) directly underpin Spark SQL and dbt model design in [[Data Engineering Role Notes/Data Engineering Concepts/Data Engineering Concepts|Data Engineering Concepts]], and PySpark exposes the same relational operations covered in [[Data Engineering Role Notes/Pyspark/PySpark|PySpark]] via its DataFrame API.
- Stored procedures, triggers, and views from [[Data Engineering Role Notes/SQL/SQL|SQL]] are the procedural building blocks that ETL pipelines orchestrated by [[Data Engineering Role Notes/Airflow Scheduler/Airflow Scheduler|Airflow Scheduler]] often call into.

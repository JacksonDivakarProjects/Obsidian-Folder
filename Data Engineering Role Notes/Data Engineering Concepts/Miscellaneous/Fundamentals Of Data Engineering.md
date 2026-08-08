# Fundamentals of Data Engineering

A foundational guide to data engineering concepts — useful for beginners, business/data analysts, or engineers refreshing core knowledge. These fundamentals cover a large share of typical data engineering interview questions.

## 1. What Is Data Engineering, and Why Do We Need It?

Data engineering is the process of taking raw, messy data, refining it, transforming it, and delivering it as data models to stakeholders — similar to a chef turning raw ingredients into a finished dish. Data engineers exist because businesses increasingly rely on data-driven decisions and need people who can handle growing data volumes and serve that data in a usable format.

## 2. The Three Pillars of the Data Engineering Workflow

- **Data production/generation** — data created by everyday activity: a Google search, a phone call, an online order, any app or website interaction.
- **Data transformation** — turning raw ("garbage") data into clean, structured, usable data. Data engineers spend roughly 70–80% of their time here, producing "curated data" from raw data.
- **Data serving** — delivering transformed data to stakeholders in an easily consumable format (typically a data model), rather than handing over everything unfiltered.

## 3. Upstream and Downstream

- **Upstream** — the sources data flows *from*: DBAs, software engineers, or web developers who manage the source systems.
- **Downstream** — the people/applications the engineer serves processed data *to*: data analysts, data scientists, analytics managers.

Data flows upstream → data engineer → downstream. Maintaining good relationships on both sides matters: downstream stakeholders define requirements, upstream owners determine what data is actually available.

## 4. Data Storage: OLTP vs. OLAP

**OLTP (Online Transactional Processing)**
- Purpose: efficient writes and updates of transactional data (e.g., banking transactions, individual website clicks).
- Ownership: typically managed by DBAs/software engineers; data engineers treat it as a source, not something they build.
- Modeling: **normalization** (1NF/2NF/3NF) to minimize redundancy and preserve integrity.
- Examples: PostgreSQL, MySQL, SQL Server, Oracle.

**OLAP (Online Analytical Processing) / Data Warehouse**
- Purpose: efficient reads over large volumes of data, for reporting and analytics — querying a heavy OLTP dataset directly for reports doesn't scale, hence a separate warehouse.
- Ownership: data engineers build and maintain these.
- Modeling: **dimensional modeling** (facts and dimensions), optimized for fast analytical retrieval.
- Examples: Teradata, Snowflake, Azure Synapse Analytics, Redshift, BigQuery.

## 5. Data Warehouse Layers

- **Staging layer** — first landing spot for extracted source data, so the source system isn't repeatedly queried directly (which would hurt its performance).
  - **Transient staging** — loaded, used to build the core layer, then truncated before the next load. Used roughly 99% of the time in industry.
  - **Persistent staging** — retains history; used only for specific project requirements.
- **Core layer** — staging data transformed into facts and dimensions, forming the dimensional model.

## 6. Incremental Loading

A loading strategy that avoids re-pulling the entire source dataset on every run — only new or changed data since the last load is processed. Example: once Jan 1's data is loaded, on Jan 2 only Jan 2's new records are pulled into staging and core. This is standard practice because it saves significant compute compared to full reloads.

## 7. Dimensional Modeling

Used in OLAP/data warehouses; organizes data into fact and dimension tables.

- **Fact table** — numeric measures (price, bill amount, quantity, weight) plus foreign keys to dimension tables.
- **Dimension table** — contextual/descriptive, non-numeric attributes for a business entity (customer names, addresses, product names, categories). Data is grouped by business use case, and some redundancy is accepted.
- **Star schema** — most common, most performant: one central fact table directly surrounded by dimension tables.
- **Snowflake schema** — like a star schema, but dimensions are further normalized into sub-dimension hierarchies. Harder to manage and less performant, so used less often.

## 8. Slowly Changing Dimensions (SCD)

- **Type 0 — no change** — dimension values are assumed fixed forever.
- **Type 1 — overwrite/upsert** — the most frequently used; changed attributes overwrite the old value and history is lost. Combines update (existing rows) with insert (new rows).
- **Type 2 — preserve history** — a new row is inserted for each change, tracked with `start_date`, `expiry_date`, and an `is_in_use`/`is_current` flag.
- **Type 3 — preserve previous value** — stores the immediately prior value in a dedicated column alongside the current value: quick access to the last state, but not the full history.

## 9. Data Lake and Lakehouse

**Data lake**
- Solves the data warehouse's limitation of handling mostly structured data — lakes can store unstructured, semi-structured (CSV, JSON), and structured data.
- Schema-on-read: schema is defined *after* the data lands, unlike a warehouse's schema-on-write.
- Much cheaper storage than a warehouse, which matters at large scale.

**Lakehouse**
- Combines lake economics with warehouse-style reporting performance.
- Data sits in a data lake; a metadata/abstraction layer on top enables dimensional modeling and warehousing techniques (ETL, SCDs, incremental loads) directly over lake-stored formats (JSON, CSV, Parquet).
- Result: the flexibility and cost of a data lake with the analytical power and familiar SQL of a warehouse. (See the Data Lakehouse note for the open-table-format mechanics behind this — Delta Lake / Iceberg / Hudi.)

## 10. File Formats

- **Row-based** — data stored row by row (all columns of record 1, then record 2, …). Efficient for writing/updating; common on the OLTP side. Examples: CSV, Avro.
- **Column-based** — data stored column by column. Excellent for fast reads, especially selective-column queries over large datasets; widely used in OLAP/big data. Examples: Parquet, ORC.
- **Delta Lake format** — an open table format built on top of Parquet, adding a transaction layer to the data lake:
  - **Transaction log** — records all metadata and changes.
  - **Time travel (versioning)** — revert to or query previous data versions, undoing mistakes like accidental deletes.
  - **Schema evolution** — add columns or change schema without breaking existing pipelines.
  - **ACID transactions** — atomicity, consistency, isolation, durability, matching traditional database guarantees.

## 11. Big Data Frameworks

- **Apache Kafka** — streaming (real-time) big data.
- **Apache Airflow** — orchestration: scheduling and managing pipeline dependencies.
- **Apache Hive** — SQL-like querying over big data, often via external tables.
- **Apache Spark** — the central big data processing framework.
  - Distributed computing: work is spread across a cluster of machines running in parallel.
  - Architecture: a **driver node** (orchestrates tasks) plus multiple **worker nodes** (execute the actual processing).
- **Databricks** — a management layer on top of Spark, simplifying cluster creation/management so teams can focus on transformations instead of infrastructure.

## 12. Cloud Data Engineering

- **Cloud computing** — renting compute/storage/database resources from a provider (Azure, AWS, GCP) instead of owning physical infrastructure. Benefits: pay-as-you-go cost, elastic scaling, provider-managed security/maintenance. Concepts transfer reasonably well between providers once you know one well.
- **Medallion architecture** (cloud data lakehouse pattern) — three data-quality layers:
  - **Bronze (raw)** — ingested as-is, no transformation or schema enforcement; a landing zone.
  - **Silver (transformed)** — cleaned and structured; schema can be enforced/evolved here.
  - **Gold (curated)** — refined into aggregated tables or dimensional models for downstream consumption (analysts, scientists, reporting tools).

## 13. Azure Data Engineering Tools (Example Cloud Stack)

- **Azure Event Hub** — captures/stores real-time streaming data (e.g., IoT).
- **Azure SQL DB** — cloud relational database, suited to OLTP.
- **Azure Data Lake Storage Gen2 (ADLS Gen2)** — scalable, cost-effective data lake with hierarchical namespaces (folders within folders); stores structured/semi-structured/unstructured data.
- **Azure Data Factory (ADF)** — ETL/orchestration tool for moving and transforming data across sources and destinations; many connectors, low-code option.
- **Azure Databricks** — managed Spark platform for large-scale data processing/transformation.
- **Azure Synapse Analytics** — cloud data warehouse for building OLAP models (facts and dimensions); comparable to Snowflake or Redshift.
- **Power BI** — reporting/dashboarding tool, typically consuming curated (Gold-layer) data.
- **Azure Purview** — data governance and cataloguing.
- **Azure DevOps** — CI/CD: promoting code through dev, QA, and production environments.
- **Azure Key Vault** — secure storage for secrets.
- **Microsoft Entra ID** — identity and access management.

**Typical end-to-end flow:** source (Event Hub / SQL DB) → ADLS Gen2 (Bronze) → Databricks transforms → Synapse Analytics (Gold) → Power BI reporting.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Miscellaneous/Data Modeling|Data Modeling Masterclass for Data Engineers]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Miscellaneous/Data Lake House|Data Lakehouse]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Methodologies/Kimball Methodology|Kimball Methodology]]

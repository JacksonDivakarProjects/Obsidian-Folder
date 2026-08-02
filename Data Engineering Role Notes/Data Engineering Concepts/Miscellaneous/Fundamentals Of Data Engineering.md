This masterclass offers a comprehensive guide to the fundamentals of data engineering, covering essential concepts from scratch for beginners, business analysts, data analysts, or existing data engineers looking to refresh their knowledge. The video is designed to cover at least 50% of typical data engineering interview questions from these foundational areas.

Here is a comprehensive guide to data engineering concepts, explained in a way that is easy to understand:

### 1. What is Data Engineering and Why Do We Need It?

**Data engineering** is the process of taking raw, messy data, refining it, applying transformations, and then delivering it in the form of data models to stakeholders. It's like a chef taking raw ingredients, cooking them, and serving them as a delicious dish to clients. Data engineers are crucial because businesses are increasingly relying on data-driven decisions, and they need professionals who can handle the rapidly growing volume of data and serve it in a usable format.

### 2. The Core Workflow/Three Pillars of Data Engineering

The data engineering workflow is built on three main pillars:

- **Data Production/Generation:** This is where data is created through various activities, such as searching on Google, making a phone call, placing an online order, or interacting with websites and applications.
- **Data Transformation:** Raw data is often like "garbage" if not transformed. This stage involves "cooking" the data, applying transformations to make it clean, structured, and usable for decision-making. Data engineers spend 70-80% of their time in this area, creating "curated data" from raw data.
- **Data Serving:** Once data is transformed, it needs to be served to stakeholders in an easily consumable format, similar to a chef serving individual dishes rather than the entire pot of food. This often involves creating data models.

### 3. Upstream and Downstream

In data engineering, "Upstream" refers to the sources from which data flows _to_ the data engineer, such as database administrators (DBAs), software engineers, or web developers who manage data sources. "Downstream" refers to the individuals or applications _to whom_ the data engineer serves the processed data, such as data analysts, data scientists, or analytics managers. Data flows from upstream to downstream. Data engineers need to maintain good relationships with both to understand requirements (from downstream) and data availability (from upstream).

### 4. Data Storage: OLTP vs. OLAP (Data Warehouse)

Databases are essential for storing the generated data. There are two main types:

- **OLTP (Online Transactional Processing) Databases:**
    - **Purpose:** Primarily designed for efficient **writes and updates** of transactional information, like banking transactions or recording individual clicks on a website.
    - **Management:** Typically managed by DBAs or software engineers. Data engineers treat OLTP databases as their source.
    - **Modeling:** Uses **normalisation** (e.g., First, Second, Third Normal Form) to minimise data redundancy and ensure data integrity.
    - **Examples:** PostgreSQL, MySQL, MS SQL Server, Oracle databases.
- **OLAP (Online Analytical Processing) Databases / Data Warehouses:**
    - **Purpose:** Designed for efficient **reads** and handling large amounts of data for reporting and analytical purposes. It's challenging to query heavy OLTP datasets directly for reports, so data warehouses are created to handle high query reads.
    - **Management:** Data engineers are responsible for building and maintaining data warehouses.
    - **Modeling:** Uses **dimensional modeling** (facts and dimensions) to optimise for fast retrieval of analytical data.
    - **Examples:** Teradata, Snowflake, Azure Synapse Analytics, Redshift, Google BigQuery.

### 5. Data Warehouse Layers

When pulling data from a source to build a data warehouse, it typically passes through layers:

- **Staging Layer:** This is the first layer where data is extracted (dumped) from the source. The purpose is to avoid directly querying the source, which can slow down its performance.
    - **Transient Staging Layer:** A temporary layer where data is loaded, used to create the core layer, and then deleted (truncated) before the next load. This is used 99% of the time in the industry.
    - **Persistent Staging Layer:** Stores data and preserves its history; a rare case depending on project requirements.
- **Core Layer:** Data from the staging layer is transformed and pushed to the core layer, which contains facts and dimensions, forming the dimensional data model.

### 6. Incremental Loading

This is a data-fetching strategy that avoids pulling all data from the source every time. Instead, it **only loads the new or changed data** since the last load. For example, if data for January 1st has already been loaded, on January 2nd, only the data generated on January 2nd is pulled and incrementally loaded into the staging and core layers. This saves computation and is a standard practice in data engineering.

### 7. Dimensional Modeling

Used in OLAP databases (data warehouses), dimensional modeling organises data into **fact tables** and **dimension tables**.

- **Fact Table:** Stores **numeric values** or measures, such as price, bill amount, quantity, or weight. It contains foreign keys that link to dimension tables.
- **Dimension Tables:** Store **contextual or descriptive data** (non-numeric) related to a business entity, such as customer names, addresses, product names, or categories. Data is clustered based on business use cases, and redundancy is accepted.
- **Star Schema:** The most common and performant dimensional model. It consists of a central fact table directly surrounded by multiple dimension tables, forming a "star" shape.
- **Snowflake Schema:** Similar to a star schema, but dimensions are further normalised into sub-dimensions, creating a hierarchy of dimensions. It is harder to manage and less performant than star schema, so it's less commonly used.

### 8. Slowly Changing Dimensions (SCD)

SCDs are techniques used to manage changes in dimension data over time.

- **SCD Type 0: No Change:** Assumes the dimension data will never change. Values are fixed.
- **SCD Type 1: Overwrite (Upsert):** The most frequently used SCD. When a dimension attribute changes, the old value is overwritten with the new value, losing the history. It combines "update" (for existing records) and "insert" (for new records).
- **SCD Type 2: Preserving History:** A new row is inserted for each change in a dimension attribute, and columns like `start_date`, `expiry_date`, and an `is_in_use` flag are used to track the historical validity of records. This preserves the full history of changes.
- **SCD Type 3: Preserving Previous Value:** Stores the previous value of an attribute in a dedicated column, alongside the current value. It does not track full history but provides quick access to the immediate prior state.

### 9. Data Lake and Lakehouse

- **Data Lake:**
    - **Purpose:** Solved the limitation of data warehouses, which primarily handled structured data. Data lakes can store **unstructured, semi-structured** (e.g., CSV, JSON), and structured data efficiently.
    - **Schema:** **Schema is defined after** the data is stored (schema-on-read), unlike data warehouses where schema is defined before.
    - **Cost:** Significantly **cheaper** for storage than traditional data warehouses, making it cost-effective for massive datasets.
- **Lakehouse:**
    - **Purpose:** The future of data architecture, combining the best aspects of data lakes and data warehouses. It leverages the **cheap storage of data lakes** and the **reporting performance of data warehouses**.
    - **Architecture:** Data resides in a data lake, and a **metadata layer** (or abstraction/logical layer) is applied on top. This metadata layer enables building dimensional data models (facts and dimensions) and applying data warehousing techniques (ETL, SCDs, incremental loading) directly on data stored in the data lake, using formats like JSON, CSV, or Parquet.
    - **Benefits:** Offers the flexibility and cost-effectiveness of data lakes with the strong analytical capabilities and familiar SQL querying of data warehouses.

### 10. File Formats

How data is stored on disk impacts performance, especially for big data.

- **Row-Based File Formats:**
    - **Storage:** Data is stored row by row. For example, in a CSV, all columns for the first record are written, then all columns for the second, and so on.
    - **Use Case:** Efficient for **writing and updating** data, commonly used on the OLTP side for transactional data.
    - **Examples:** CSV, Avro.
- **Column-Based File Formats:**
    - **Storage:** Data is stored column by column. All values for the first column are written, then all values for the second column, and so on.
    - **Use Case:** Excellent for **faster reads**, especially when querying specific columns over large datasets. Widely used in OLAP databases and big data scenarios.
    - **Examples:** Parquet, ORC.
- **Delta Lake Format:**
    - **Purpose:** A highly in-demand, open-table format built on top of Parquet files. It adds a **transaction layer** to data lakes, bringing traditional database capabilities.
    - **Key Features:**
        - **Transaction Log:** Stores all metadata and changes, enabling powerful features.
        - **Data Time Travel (Versioning):** Allows users to revert to previous versions of data, undoing mistakes like accidental deletions.
        - **Schema Evolution:** Permits adding new columns or making schema changes without breaking existing data pipelines.
        - **ACID Transactions:** Provides Atomicity, Consistency, Isolation, and Durability, ensuring reliable data operations, similar to traditional databases.

### 11. Big Data Frameworks

These frameworks are used to process and manage large volumes of data:

- **Apache Kafka:** Used for handling **streaming (real-time) big data**.
- **Apache Airflow:** Used for **orchestration** – managing and scheduling complex data pipelines with dependencies.
- **Apache Hive:** Allows users to query big data using SQL-like commands, often used to create external tables.
- **Apache Spark:** A central and highly demanded Big Data framework.
    - **Distributed Computing:** Processes data by distributing tasks across **multiple machines (a "cluster")** working in parallel, significantly increasing speed and efficiency.
    - **Architecture:** Consists of a **driver node** (the brain, orchestrating tasks) and multiple **worker nodes** (machines that execute the actual data processing).
- **Databricks:** A management layer for Apache Spark, simplifying the creation and management of Spark clusters, allowing users to focus on data transformation rather than infrastructure.

### 12. Cloud Data Engineering

- **Cloud Computing:** Renting computational resources (servers, storage, databases) from a cloud provider (e.g., Azure, AWS, GCP) over the internet, rather than owning and managing them physically.
    - **Benefits:** Cost-effective (pay-as-you-go), scalable (can easily provision more resources), and handles security and maintenance.
    - **Major Providers:** Azure (Microsoft), AWS (Amazon), GCP (Google). Learning one cloud platform makes it easier to adapt to others due to similar services.
- **Medallion Architecture (Cloud Data Lakehouse Architecture):** A common architecture for cloud data engineering, often implemented using cloud data lake storage. It defines three layers of data quality:
    - **Bronze Layer (Raw Layer):** Data is ingested as-is from source systems, with no transformations or schema enforcement. It's a "landing zone" for raw data.
    - **Silver Layer (Transformed Layer):** Data from the Bronze layer is cleaned, transformed, and structured. Schema can be enforced and evolved here.
    - **Gold Layer (Curated Layer):** Data is refined into highly aggregated tables or dimensional models (facts and dimensions), ready for downstream consumption by data analysts, data scientists, and reporting tools.

### 13. Azure Data Engineering Tools (Example Cloud Services)

Azure offers a suite of tools for implementing cloud data engineering architectures:

- **Azure Event Hub:** For capturing and storing **real-time streaming data** (e.g., from IoT devices).
- **Azure SQL DB:** A cloud-based relational database service, equivalent to on-premise SQL databases, suitable for **OLTP databases**.
- **Azure Data Lake Storage Gen2 (ADLS Gen2):** Azure's scalable and cost-effective **data lake solution** that stores structured, semi-structured, and unstructured data, supporting hierarchical namespaces (folders within folders).
- **Azure Data Factory (ADF):** An Azure **ETL tool** for orchestrating data movement and transformations across various data sources and destinations. It supports numerous connectors and can perform tasks with low-code development.
- **Azure Databricks:** A unified analytics platform built on Apache Spark, providing a managed environment for **large-scale data processing and transformation**.
- **Azure Synapse Analytics:** A cloud data warehousing solution, enabling the creation of **OLAP databases/data warehouses** (facts and dimensions) in Azure. It's comparable to Snowflake or Redshift.
- **Power BI:** Microsoft's **reporting tool** used by data analysts to create dashboards and visualisations from curated data (e.g., from the Gold layer).
- **Azure Purview:** A **data governance tool** for managing and cataloguing data assets.
- **Azure DevOps:** Used for **CI/CD (Continuous Integration/Continuous Deployment)**, promoting code across development, QA, and production environments.
- **Azure Key Vault:** For securely storing **secrets** and sensitive information.
- **Microsoft Entra ID:** Manages user identities and access within an organisation in Azure.

These tools integrate to form an end-to-end cloud data engineering architecture, where data flows from sources (like Event Hub or SQL DB) through ADLS Gen2 (Bronze layer), transformed by Databricks, curated in Synapse Analytics (Gold layer), and finally reported via Power BI.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Miscellaneous/Data Modeling|Data Modelling Masterclass for Data Engineers]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Miscellaneous/Data Lake House|Data Lakehouse]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Methodologies/Kimball Methodology|Kimball Methodology]]

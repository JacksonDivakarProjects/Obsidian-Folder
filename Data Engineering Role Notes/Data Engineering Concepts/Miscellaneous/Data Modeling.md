# Data Modeling Masterclass for Data Engineers

Notes on data modeling as practiced by data engineers — a distinct, more involved discipline than modeling for data analysts or DBAs, since a data engineer has to think about the model at every stage of the pipeline (not just the final table).

## 1. Core Principles

- Data-engineering data modeling spans the whole pipeline — source, staging, transformation, serving — not just the destination schema.
- The goal is an end-to-end model: from raw source data through to the final dimensional model.

## 2. Fundamentals

**What is data modeling?**
The process of creating a blueprint / high-level architecture for how data is stored, connected, and retrieved within a system. For data engineers this means designing structures that support reporting, scalability, and performance.

**Why it matters**
- **Clarity** — makes data easier for stakeholders (analysts, data scientists) to understand and use.
- **Performance** — a well-designed model improves query performance.
- **Scalability** — new tables can be added without redesigning the whole system.

**Three-step modeling flow**
1. **Conceptual model** — high-level entities (e.g., customers, orders) and their basic relationships.
2. **Logical model** — relationships, primary keys, and join conditions, independent of database technology or data types.
3. **Physical model** — the actual implementation: data types, constraints, indexes, partitions for a specific database system.

## 3. OLTP vs. OLAP

This distinction is central to what separates a data engineer's modeling work from a DBA's.

### OLTP (Online Transactional Processing)
- Purpose: handle a high volume of frequent, rapid transactions (writes).
- Modeling approach: **normalization**, to reduce redundancy — data is split across many tables (e.g., a separate `company` table instead of repeating the company name on every employee record). Common normal forms: 1NF, 2NF, 3NF.
- Role in data engineering: OLTP databases are typically the **source systems**. Data engineers, analysts, and scientists consume them but don't usually build them.

### OLAP (Online Analytical Processing)
- Purpose: the primary focus for data engineers — complex queries, analysis, and reporting rather than rapid transactions.
- Modeling approach: **dimensional modeling**, a blend of normalized and denormalized structures. Contextual data (like a company name) is often kept inside a main table for convenience, rather than fully split out. General rule: separate contextual/descriptive data from numerical (measure) data.
- Building an OLAP model involves a multi-layered pipeline that refines raw data before the final dimensional model is built.

## 4. The Data Engineer's Workflow: ETL and the Medallion Architecture

Data engineers build ETL (Extract, Transform, Load) pipelines that move data from a source (often OLTP) to a destination OLAP model.

**Traditional ETL layers**
1. **Extract / Staging layer** — an exact, untransformed replica of the source data.
2. **Transform / Transformation layer** — the heavy lifting: cleaning data, adding columns, handling nulls, removing duplicates.
3. **Load / Serving layer** — the final, clean data; the data model is built here.

**Medallion architecture** (modern naming for the same layers, common on cloud platforms):
- **Bronze (raw)** — corresponds to staging.
- **Silver (enriched)** — corresponds to transformation. Data is often consolidated here into a "One Big Table" (OBT).
- **Gold (curated)** — corresponds to serving. The OBT from Silver is broken down into the final dimensional model here.

**Incremental loading**
- Pipelines process only new or changed records instead of reloading everything on each run — which is why the data model needs to be considered starting from the Bronze layer.
- **Transient vs. persistent staging:** a transient Bronze layer is replaced by the new incremental batch on each run; a persistent Bronze layer appends new data and keeps history. Transient is simpler and more common for incremental loading.

## 5. Practical Setup (Databricks Example)

Databricks works well as the SQL engine for practicing this, since its free edition is easy to set up and keeps the focus on modeling concepts rather than infrastructure.

1. Create a free Databricks account.
2. Create a **catalog** (e.g., `data_modeling`) — similar to a parent database.
3. Create three **schemas** inside it: `bronze`, `silver`, `gold`.
4. Use the `default` schema to create a source table that simulates a real OLTP source.
5. Write code in Databricks notebooks, which mix SQL and Python across cells.

## 6. Building the Gold Layer: Dimensional Modeling in Practice

The Gold layer is where the dimensional model is built from the cleansed "One Big Table" produced in Silver.

**Fact vs. dimension tables**
- **Fact tables** store numerical measures/metrics (e.g., revenue, sales, cost) — numbers with no context on their own. Build the fact table last, after the dimensions exist.
- **Dimension tables** provide context: descriptive attributes grouped by a common theme (e.g., all customer-related columns → `Dim_Customers`).

**Process for building dimension tables**
1. **Identify themes** — group Silver columns that share a common context.
2. **Remove duplicates** — `DISTINCT`; a dimension should never store the same entity twice.
3. **Create surrogate keys** — add a simple numeric identifier per row, typically via `ROW_NUMBER()`.
   - A **surrogate key** (e.g., `Dim_Customer_Key`) replaces complex natural business keys for joins, improving join performance.
   - Rule: generate the surrogate key *after* deduplication, or it won't correctly represent unique entities.

**Building the fact table**
- Contains only two kinds of columns: numerical measures (e.g., `quantity`, `unit_price`) and the surrogate keys pulled from each dimension table.
- Built by joining the Silver table against each dimension table to retrieve its surrogate key.

**Star vs. snowflake schema**
- **Star schema** — a central fact table connected directly to multiple dimension tables. Most common and best-performing; the default choice in industry.
- **Snowflake schema** — a star schema where a dimension is further normalized into smaller related tables (e.g., `Dim_Products` linked to a separate `Dim_Category`). Rarely used in practice — harder to maintain and can hurt query performance — but a frequent interview topic.

## 7. Advanced Topics

**Types of fact tables**
- **Transactional** — most common and granular; one row per transaction (the type built in this masterclass).
- **Periodic** — aggregated; one row per period (day/week/month) rather than per transaction.
- **Accumulating** — tracks a process's journey over time via multiple date/milestone columns (e.g., order placed → shipped → delivered).
- **Factless** — contains no numeric measures at all; used to track events or relationships between dimensions.

**Types of dimension tables**
- **Conformed dimension** — shared across multiple fact tables (e.g., `Dim_Products` used by both `Fact_Sales` and `Fact_Cancellations`).
- **Degenerate dimension** — an identifier (e.g., a customer ID) that exists in the source with no other descriptive attributes, so it's kept directly in the fact table rather than given its own dimension.
- **Junk dimension** — holds miscellaneous, low-cardinality flags (e.g., a `Dim_Payments` table with only 'Credit Card' / 'PayPal').
- **Role-playing dimension** — a single dimension joined to a fact table multiple times, each join representing a different role (e.g., one `Dim_Date` joined on both `Order_Date` and `Cancel_Date`).

**Slowly Changing Dimensions (SCD)**
- **SCD Type 1 (overwrite)** — simplest and most common; the existing record is overwritten with the new value, history is lost. Implemented as a `MERGE`/upsert (already used in the Silver layer).
- **SCD Type 2 (track history)** — a new row is added on every change, tracked with `start_date`, `end_date`, and `is_current` columns.
  - On update: expire the old record (`end_date` = now, `is_current` = 'N'), then insert a new record (`start_date` = now, `end_date` = null/far future, `is_current` = 'Y').
  - Requires a multi-stage `MERGE`: first expire the old row, then insert the new version.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Methodologies/Kimball Methodology|Kimball Methodology]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Miscellaneous/Types of Fact Table|Types of Fact Tables in Data Warehousing]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Miscellaneous/Fundamentals Of Data Engineering|Fundamentals Of Data Engineering]]

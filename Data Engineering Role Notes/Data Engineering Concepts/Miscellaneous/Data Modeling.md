Of course. Here is a comprehensive and well-formatted note covering all the concepts from the provided video transcript.

### **Comprehensive Notes: Data Modelling Masterclass for Data Engineers**

These notes summarise the key concepts, practical implementations, and advanced techniques covered in the "Data Modelling Masterclass For Data Engineers" video. The masterclass is designed for all levels, from beginners to experienced data engineers, focusing on modern data architectures and practical skills.

---

#### **1. Introduction and Core Principles**

- **Target Audience:** The course is for everyone, including those with zero experience and seasoned data engineers, as it covers fundamentals and advanced concepts often missed in other resources.
- **Unique Focus:** It specifically addresses **data modelling for data engineers**, which is distinct and more complex than modelling for data analysts or database administrators (DBAs). Data engineers must consider the data model at every stage of the data pipeline, not just at the final step.
- **Course Goal:** To provide a complete, end-to-end guide that masters data modelling within the context of data engineering pipelines, from source to final model.

---

#### **2. Fundamentals of Data Modelling**

- **What is Data Modelling?**
    
    - It is the process of creating a **blueprint or a high-level architecture** of how data is stored, connected, and retrieved within a system.
    - For data engineers, this involves designing data structures that support reporting, scalability, and performance.
- **Why Data Modelling Matters**
    
    - **Clarity:** Makes data easier for stakeholders (data analysts, data scientists) to understand and use.
    - **Performance:** A well-designed model improves query performance.
    - **Scalability:** Allows for the addition of new tables without redesigning the entire system.
- **Types of Data Models** Data modelling follows a three-step flow:
    
    1. **Conceptual Model:** A high-level overview identifying key entities (e.g., customers, orders) and their basic relationships.
    2. **Logical Model:** A more detailed stage that defines relationships, primary keys, and joining conditions without specifying database technology or data types.
    3. **Physical Model:** The actual implementation of the model. This is where data types, constraints, indexes, and partitions are defined for a specific database system.

---

#### **3. The Critical Distinction: OLTP vs. OLAP**

This is a fundamental concept that differentiates the work of a data engineer from that of a DBA.

- **OLTP (Online Transactional Processing)**
    
    - **Purpose:** Designed to efficiently handle a high volume of frequent, rapid transactions (writes).
    - **Modelling Approach:** Uses **normalisation** to reduce data redundancy. Data is split into multiple tables to avoid repetition (e.g., a separate `company` table is created instead of storing the company name in every employee record). Popular normal forms include First, Second, and Third Normal Form.
    - **Role in Data Engineering:** OLTP databases are typically treated as the **source systems** by data engineers, analysts, and scientists. Data professionals use them but do not usually create them.
- **OLAP (Online Analytical Processing)**
    
    - **Purpose:** This is the primary focus for data engineers. OLAP models are designed for complex queries, analysis, and reporting, not for rapid transactions.
    - **Modelling Approach:** Uses **dimensional data modelling**, which is a blend of normalised and denormalised structures. Unlike OLTP, contextual data (like a company name) is often kept within a main table to provide context. The general approach is to separate data based on its nature: contextual data in one table and numerical data in another.
    - **Data Journey:** Creating an OLAP model involves a multi-layered data journey to refine the data before modelling.

---

#### **4. The Data Engineer's Workflow: ETL & Medallion Architecture**

Data engineers build **ETL (Extract, Transform, Load)** pipelines to move data from a source (Point A, often OLTP) to a destination (Point B, an OLAP model).

- **ETL Layers (Traditional)**
    
    1. **Extract (Staging Layer):** An exact replica of the source data is brought into this layer without any transformation.
    2. **Transform (Transformation Layer):** This is where heavy lifting occurs: cleaning data, adding columns, handling nulls, and removing duplicates.
    3. **Load (Serving Layer):** The final, clean data is loaded, and the data model is built in this layer.
- **Medallion Architecture (Modern Naming)** This is a modern naming convention for ETL layers, especially common in cloud solutions.
    
    - **Bronze (Raw):** Corresponds to the Staging layer.
    - **Silver (Enriched):** Corresponds to the Transformation layer. At this stage, data is often consolidated into a **"One Big Table" (OBT)**.
    - **Gold (Curated):** Corresponds to the Serving layer. Data modelling occurs here, where the OBT from the Silver layer is broken down into the final dimensional model.
- **Incremental Loading**
    
    - To avoid reloading entire datasets daily, pipelines use **incremental loading**, processing only new or changed records.
    - This is why the data model must be considered from the very first (Bronze) layer.
    - **Transient vs. Persistent Staging:** The Bronze layer can be _transient_ (data is replaced with new incremental data in each run) or _persistent_ (new data is appended). The course uses a transient layer to simplify incremental loading at the Bronze stage.

---

#### **5. Practical Implementation and Setup**

- **Tooling:** The masterclass uses **Databricks** as the SQL engine because its free edition is easy to set up, allowing focus on concepts rather than environment configuration. The goal is to learn data modelling, not Databricks itself.
- **Environment Setup in Databricks:**
    1. Create a free Databricks account.
    2. Create a **catalog** (e.g., `data_modeling`), which is similar to a parent database.
    3. Create three **schemas** within the catalog: `bronze`, `silver`, and `gold`.
    4. Use the `default` schema to create a source table, simulating a real-world OLTP source.
    5. All code is written in **Databricks notebooks**, which allow for mixing SQL and Python code in different cells.

---

#### **6. Building the Gold Layer: Dimensional Modelling in Practice**

The Gold layer is where the dimensional model is constructed from the cleansed "One Big Table" in the Silver layer.

- **Fact vs. Dimension Tables**
    
    - **Fact Tables:** Store numerical measures and metrics (the "facts"), such as revenue, sales, and cost. These numbers lack context on their own. The rule is to create the fact table at the end.
    - **Dimension Tables:** Provide the **context** for the facts. They contain descriptive attributes grouped by a common theme (e.g., all customer-related columns form a `Dim_Customers` table).
- **Process for Creating Dimension Tables**
    
    1. **Identify Themes:** Group columns from the Silver table that share a common context.
    2. **Remove Duplicates:** Use `DISTINCT` to ensure each dimension table contains only unique records. A dimension should not store duplicate information (e.g., the same customer listed twice).
    3. **Create Surrogate Keys:** Add a unique, simple numerical identifier to each row using a function like `ROW_NUMBER()`.
        - A **surrogate key** (e.g., `Dim_Customer_Key`) replaces complex natural business keys for joins, improving performance.
        - **Crucial Rule:** The surrogate key must be generated _after_ removing duplicates to ensure correctness.
- **Creating the Fact Table**
    
    - The fact table contains only two types of columns: **numerical measures** (e.g., `quantity`, `unit_price`) and the **surrogate keys** from all the dimension tables.
    - It is built by joining the main Silver table with each dimension table to retrieve their respective surrogate keys.
- **Star vs. Snowflake Schema**
    
    - **Star Schema:** The model built in the course is a star schema. It features a central fact table directly connected to multiple dimension tables, resembling a star. This is the most common and preferred schema in the industry.
    - **Snowflake Schema:** An extension of the star schema where a dimension is further normalised into smaller, related tables (e.g., `Dim_Products` is linked to a separate `Dim_Category`). It is rarely used because it is hard to maintain and can hurt query performance, but it is a very common interview question.

---

#### **7. Advanced Topics and Theory**

- **Types of Fact Tables**
    
    - **Transactional:** The most common and granular type, where each row represents a single transaction. This is the type built in the masterclass.
    - **Periodic:** An aggregated fact table where each row represents a period (e.g., a day, week, or month) instead of a single transaction.
    - **Accumulating:** Describes the journey of a transaction or process over time, often containing multiple date columns to track milestones (e.g., order placed, shipped, delivered).
    - **Factless Fact Table:** A fact table that contains no numeric measures. It is used to track events or relationships between dimensions.
- **Types of Dimension Tables**
    
    - **Conformed Dimension:** A dimension that is connected to and shared by multiple fact tables (e.g., a `Dim_Products` table used by both a `Fact_Sales` and a `Fact_Cancellations` table).
    - **Degenerate Dimension:** When a dimension attribute (like a customer ID) exists in the source data without any other descriptive information (no name, age, etc.), it can be stored as a degenerate dimension.
    - **Junk Dimension:** A dimension created to hold miscellaneous, low-cardinality flags or indicators (e.g., a `Dim_Payments` table with only two values: 'Credit Card' and 'PayPal').
    - **Role-Playing Dimension:** A single dimension that is joined to a fact table multiple times, with each join representing a different "role." For example, a single `Dim_Date` table could be joined to a fact table on both `Order_Date` and `Cancel_Date`.
- **Slowly Changing Dimensions (SCDs)** SCDs are techniques for managing changes in dimension data over time.
    
    - **SCD Type 1 (Overwrite):** The simplest and most common method. When a change occurs, the existing record is **overwritten with the new value**. No history is preserved. This is the `MERGE` or "upsert" command already implemented in the Silver layer.
    - **SCD Type 2 (Track History):** Used when it is necessary to track historical changes. Instead of overwriting, a new row is added for the updated record, and history is managed with three additional columns: `start_date`, `end_date`, and `is_current`.
        - **Process on Update:**
            1. The existing (old) record is "expired" by setting its `end_date` to the current timestamp and its `is_current` flag to 'N'.
            2. A new record is inserted with the updated information, a new `start_date`, a far-future `end_date` (or null), and an `is_current` flag of 'Y'.
        - **Implementation:** This requires a more complex, multi-stage `MERGE` process to first expire old records and then insert the new versions.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Methodologies/Kimball Methodology|Kimball Methodology]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Miscellaneous/Types of Fact Table|Types of Fact Tables in Data Warehousing]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Miscellaneous/Fundamentals Of Data Engineering|Fundamentals Of Data Engineering]]

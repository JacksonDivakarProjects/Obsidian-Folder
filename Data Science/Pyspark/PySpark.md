

# File Links

[[Pyspark Introduction]]  
[[Basic DataFrame Operation]]  
[[Functions in Pyspark]]  
[[Handling Missing Values]]  
[[Schema Operation in Pyspark]]  
[[Aggregation and Window Function]]  
[[Joining DataFrames]]  
[[Pyspark Pivoting]]  
[[Spark SQL]]  
[[Pyspark Read & Write Operations]]  
[[Pyspark Reading Modes]]  
[[Pyspark Programs]]  
[[Performance & Optimisation in Pyspark]]  
[[Repartition Vs Coalesce]]  
[[Broadcasting in Pyspark]] 
[[SCD In Pyspark]]
[[Spark RDD]]  
[[Pyspark .collect()]]  
[[Serialization and Deserialization]]
[[Regexp Functions]]
[[Data Science/Pyspark/Miscellaneous Concepts]]

# Folder Links

[[Pyspark Images]]
[[Pyspark Streaming]]
[[Spark Standalone Mode]]

# Online Links

[Spark Intro](https://www.youtube.com/watch?v=iXVIPQEGZ9Y&t=989s)
[FreeCodeCamp](https://www.youtube.com/watch?v=_C8kWso4ne4)
[5 Hrs Video](https://www.youtube.com/watch?v=94w6hPk7nkM)



## 🗺️ Map of Content (auto-generated)

### Core DataFrame Operations
- [[Data Science/Pyspark/Pyspark Introduction|Pyspark Introduction]] — Roadmap of all PySpark topics from fundamentals to advanced ecosystem tools.
- [[Data Science/Pyspark/Basic DataFrame Operation|Basic DataFrame Operation]] — Core `select`, `filter`, `withColumn`, `drop`, and `orderBy` operations.
- [[Data Science/Pyspark/Functions in Pyspark|Functions in Pyspark]] — String, date, math, aggregation functions and UDFs from the `F` module.
- [[Data Science/Pyspark/Handling Missing Values|Handling Missing Values]] — Using `dropna()` and `fillna()` to manage nulls.
- [[Data Science/Pyspark/Schema Operation in Pyspark|📘 Schema Operations in PySpark]] — Defining, inferring, and evolving DataFrame schemas.
- [[Data Science/Pyspark/Regexp Functions|Regexp Functions]] — `regexp_extract`, `regexp_replace`, `split`, and `rlike` in practice.

### Aggregations, Joins & Reshaping
- [[Data Science/Pyspark/Aggregation and Window Function|Aggregation and Window Function]] — `groupBy().agg()` versus window functions for rankings and running totals.
- [[Data Science/Pyspark/Joining DataFrames|Joining DataFrames]] — All join types, syntax variants, and duplicate-column handling.
- [[Data Science/Pyspark/Pyspark Pivoting|Pyspark Pivoting]] — Reshaping long to wide data with `pivot()`.
- [[Data Science/Pyspark/Spark SQL|Spark SQL]] — Temporary views, `spark.sql()`, and when to prefer SQL over the DataFrame API.
- [[Data Science/Pyspark/SCD In Pyspark|SCD In Pyspark]] — Implementing Slowly Changing Dimension types 1–3 without Delta Lake.

### I/O
- [[Data Science/Pyspark/Pyspark Read & Write Operations|Pyspark Read & Write Operations]] — Reading/writing CSV, Parquet, JSON, JDBC, and cloud storage.
- [[Data Science/Pyspark/Pyspark Reading Modes|Pyspark Reading Modes]] — `PERMISSIVE`, `DROPMALFORMED`, `FAILFAST`, and `EXCEPTION` read modes.

### Performance & Internals
- [[Data Science/Pyspark/Performance & Optimisation in Pyspark|Performance & Optimisation in Pyspark]] — Partitioning, shuffling, caching, and cluster configuration.
- [[Data Science/Pyspark/Broadcasting in Pyspark|Broadcasting in Pyspark]] — When and how to use broadcast joins.
- [[Data Science/Pyspark/Repartition Vs Coalesce|Repartition Vs Coalesce]] — Trade-offs between full-shuffle and shuffle-free repartitioning.
- [[Data Science/Pyspark/Serialization and Deserialization|Serialization and Deserialization]] — How data moves between the JVM and Python, and its performance cost.
- [[Data Science/Pyspark/Spark RDD|Spark RDD]] — The low-level RDD API and when (rarely) you still need it.
- [[Data Science/Pyspark/Pyspark .collect()|Pyspark .collect()]] — Risks of pulling full DataFrames to the driver and safer alternatives.
- [[Data Science/Pyspark/Miscellaneous Concepts|Miscellaneous Concepts]] — `parallelize()` vs DataFrame readers, and `PERMISSIVE` mode corrupt-record handling.
- [[Data Science/Pyspark/Pyspark Programs|Pyspark Programs]] — End-to-end ETL, data quality, incremental load, and testing patterns.

### Pyspark Images
- [[Data Science/Pyspark/Pyspark Images/Pyspark Images|Pyspark Images]] — Reference image gallery for PySpark concepts.

### Pyspark Streaming
- [[Data Science/Pyspark/Pyspark Streaming/Pyspark Streaming|Pyspark Streaming]] — Folder hub linking all Structured Streaming notes.
- [[Data Science/Pyspark/Pyspark Streaming/Spark Streaming Foundational Concepts|Spark Streaming Foundational Concepts]] — Microbatching, stateful vs stateless transforms, and the unbounded-table model.
- [[Data Science/Pyspark/Pyspark Streaming/Autoloader In Spark Structured Streaming|Autoloader In Spark Structured Streaming]] — Incremental, scalable file ingestion with `cloudFiles`.
- [[Data Science/Pyspark/Pyspark Streaming/Archive Source File|Archive Source File]] — Moving processed source files out of the input directory.
- [[Data Science/Pyspark/Pyspark Streaming/Checkpointing And Idempotency|Checkpointing & Idempotency in PySpark Structured Streaming]] — Fault tolerance and exactly-once writes.
- [[Data Science/Pyspark/Pyspark Streaming/ForEachBatch|ForEachBatch]] — Custom per-micro-batch logic and multi-sink writes.
- [[Data Science/Pyspark/Pyspark Streaming/Output Modes in Streaming|Output Modes in Streaming]] — Append, complete, and update output modes compared.
- [[Data Science/Pyspark/Pyspark Streaming/Types Of Triggers|🔥 Comprehensive Guide to PySpark Structured Streaming Triggers]] — `once`, `processingTime`, `continuous`, and `availableNow`.
- [[Data Science/Pyspark/Pyspark Streaming/Types Of Windows|Window Operations in PySpark Structured Streaming]] — Tumbling, sliding, and session windows.
- [[Data Science/Pyspark/Pyspark Streaming/Watermarking in Streaming|Watermarking in PySpark Structured Streaming]] — Bounding state and handling late-arriving data.
- [[Data Science/Pyspark/Pyspark Streaming/Why Complete Mode not Working in Watermarking|Why `complete` Output Mode Doesn't Work with Watermarks]] — Why complete mode conflicts with watermark state pruning.
- [[Data Science/Pyspark/Pyspark Streaming/Explode vs Explode Outer|Explode vs Explode Outer]] — Handling null/empty arrays when flattening nested data.
- [[Data Science/Pyspark/Pyspark Streaming/Pyspark Streaming Images/Pyspark Streaming Images|Pyspark Streaming Images]] — Reference image gallery for streaming concepts.

### Spark Standalone Mode
- [[Data Science/Pyspark/Spark Standalone Mode/Spark Standalone Mode|Spark Standalone Mode]] — Folder hub linking cluster setup notes.
- [[Data Science/Pyspark/Spark Standalone Mode/Spark Installation|🚀 Comprehensive Guide: Spark Standalone (Multiple Workers, Single Machine)]] — Installing Java, Spark, and configuring a multi-worker cluster.
- [[Data Science/Pyspark/Spark Standalone Mode/Automating Spark Start and Stop|🚀 Spark Standalone Cluster on One Machine (Multi-Worker)]] — Start/stop scripts and aliases for the local cluster.

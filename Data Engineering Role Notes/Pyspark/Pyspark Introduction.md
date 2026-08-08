# PySpark Learning Roadmap

A structured path through PySpark topics, from foundational concepts to advanced ecosystem tools.

### I. Core Concepts & Fundamentals
1.  **What is Spark?**: The difference between Spark and Hadoop MapReduce (in-memory processing vs. disk-based).
2.  **Spark Architecture**: Driver, Executors, and Cluster Manager (Standalone, YARN, Mesos, Kubernetes).
3.  **Execution Model**: How Spark builds Directed Acyclic Graphs (DAGs) and uses lazy evaluation.
4.  **PySpark vs. Spark**: PySpark is a Python API for Spark; the core execution engine (JVM) is the same, but Python code talks to it via Py4J.
5.  **Spark Sessions**: The unified entry point (replacing the older `SparkContext`/`SQLContext` split). Learn to create and configure a `SparkSession`.

### II. Working with Data: The Core APIs
This is the most critical section for day-to-day work.

#### A. Spark DataFrames (Primary API)
*   **Creation**: from lists of data, Pandas DataFrames, files (CSV, JSON, Parquet, ORC, Avro), or databases (JDBC).
*   **Schema**: defining and inferring schemas explicitly vs. automatically.
*   **Basic Operations**:
    *   `select()`: projecting columns.
    *   `filter()` / `where()`: filtering rows.
    *   `withColumn()`: adding/transforming columns.
    *   `withColumnRenamed()`: renaming columns.
    *   `drop()`: dropping columns.
    *   `orderBy()` / `sort()`: sorting data.
*   **Handling Missing Data**: `dropna()`, `fillna()`.
*   **Column Expressions**: `pyspark.sql.functions` (the `F` module).
    *   String functions (`F.lower`, `F.substring`)
    *   Date/time functions (`F.current_date`, `F.to_date`, `F.date_add`)
    *   Math functions (`F.round`, `F.sqrt`)
    *   Aggregation functions (`F.sum`, `F.avg`, `F.count`, `F.countDistinct`)
    *   UDFs (User Defined Functions): how to create them, and their performance cost.
*   **Aggregations**:
    *   `groupBy()` followed by `agg()`.
    *   Window functions: `row_number`, `rank`, `lag`, running totals.
*   **Joining DataFrames**:
    *   Join types: `inner`, `outer`, `left`, `right`, `left_semi`, `left_anti`.
    *   Handling duplicate column names after a join.

#### B. Spark SQL
*   Creating temporary views (`df.createOrReplaceTempView()`).
*   Writing SQL queries directly with `spark.sql()`.
*   Choosing between the DataFrame API and Spark SQL (mostly a matter of preference — both compile to the same execution plan).

#### C. Spark RDDs (Resilient Distributed Datasets) — the low-level API
*   **Understanding RDDs**: Spark's foundational, low-level data structure.
*   **Creating RDDs**: from collections, from text files.
*   **RDD Operations**:
    *   Transformations: `map`, `flatMap`, `filter`, `distinct`, `sample`.
    *   Actions: `collect`, `count`, `take`, `reduce`, `saveAsTextFile`.
*   **Key-Value Pairs**: pair RDDs and operations like `reduceByKey`, `groupByKey`, `join`.
*   **When to use RDDs**: unstructured data or low-level control. Most everyday tasks are easier with DataFrames.

### III. Performance & Optimization (Crucial for Large Datasets)
1.  **Partitioning**: how data is split across the cluster; `repartition()` vs. `coalesce()`; partitioning by a key for faster joins and filters.
2.  **Shuffling**: the expensive process of moving data across executors. Know which operations trigger a shuffle (`groupBy`, `join`, `repartition`) and how to minimize it.
3.  **Caching & Persistence**: `df.cache()`, `df.persist()`. Know *when* to cache (a dataset reused multiple times) and at which storage level (`MEMORY_ONLY`, `DISK_ONLY`, etc.).
4.  **Broadcast Variables**: `broadcast()` / `F.broadcast()` for efficiently joining a large DataFrame with a very small one (avoids shuffling the small table).
5.  **Cluster Configuration**: tuning executors, cores, and memory (`spark.executor.memory`, `spark.executor.cores`).

### IV. Advanced Topics & Ecosystem
1.  **Structured Streaming**:
    *   Treating a stream of data as an unbounded table.
    *   Core concepts: sources (Kafka, file source), sinks (console, memory, Kafka), output modes (append, update, complete).
    *   Windowing (tumbling, sliding windows).
2.  **Machine Learning with MLlib**:
    *   The `pyspark.ml` package (DataFrame-based API — not the older RDD-based `pyspark.mllib`).
    *   ML Pipelines: `Transformer`, `Estimator`, `Pipeline`.
    *   Feature transformers: `VectorAssembler`, `StringIndexer`, `OneHotEncoder`.
    *   Training/evaluating models: Linear Regression, Logistic Regression, Random Forest.
3.  **Data Formats**:
    *   Columnar formats like **Parquet** and **ORC** (recommended for performance).
    *   **Delta Lake**: an open-source storage layer that brings ACID transactions to Spark — central to lakehouse architectures.

### V. Deployment & Operational Topics
1.  **Submitting Applications**: using `spark-submit` to run PySpark scripts on a cluster.
2.  **Monitoring**: using the Spark Web UI to inspect jobs, stages, and tasks, and to find bottlenecks.
3.  **Testing**: strategies for unit testing PySpark code (e.g., `pytest` with a throwaway `SparkSession`).

---

### Recommended Learning Path

1.  **Fundamentals & DataFrames first** — creating, transforming, and aggregating DataFrames covers roughly 80% of day-to-day work.
2.  **Optimization second** — partitioning, shuffling, and caching are what separate beginners from proficient users.
3.  **Spark SQL** — often makes complex queries more readable than the equivalent DataFrame chain.
4.  **Streaming and MLlib** — as needed, depending on whether the role leans data engineering or data science.
5.  **RDDs** — know they exist and their basic principles, but default to the DataFrame API for new work.
6.  **Deployment** — get comfortable with `spark-submit` and reading the Web UI.

## 🔗 Related Notes
- [[Basic DataFrame Operation|Basic DataFrame Operation]]
- [[Performance & Optimisation in Pyspark|Performance & Optimisation in Pyspark]]
- [[Spark RDD|Spark RDD]]
- [[Pyspark Streaming|Pyspark Streaming]]

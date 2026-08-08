# Spark

Apache Spark study notes covering the distributed execution model, driver/executor memory management, join strategies, and supporting reference material.

## 🗺️ Map of Content (auto-generated)

### Joins
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Joins/Types Of Joins|Types Of Joins]] — Broadcast Hash, Shuffle Hash, and Sort-Merge join strategies, and when Spark picks each.
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Joins/Shuffle Hash Join|Shuffle Hash Join]] — How Shuffle Hash Join builds and probes hash tables, including duplicate-key handling.
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Joins/Links For Types Of Fact Table|Links For Types Of Fact Table]] — External reading list on accumulating and periodic snapshot fact tables.

- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Joins/Joins|Joins]] — Section index for Spark's join strategies and related reference material.

### Memory Management
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Driver Memory Management|Spark Driver Memory Architecture]] — JVM heap/non-heap/off-heap layout of the driver process.
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Driver OOM|Driver Out-Of-Memory (OOM) in Spark]] — Causes, symptoms, and fixes for driver OOM.
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Executer Memory Management|Spark Executor Memory Architecture]] — Unified memory manager: reserved, user, execution, and storage memory.
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Executer OOM with Salting|Executor OOM in Spark (with Salting)]] — Causes of executor OOM and how salting fixes data skew.

### Execution Model & Reference
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Miscellaneous/Job, Stages and Tasks|Spark Execution: Job, Stages and Tasks]] — RDDs, partitions, lazy transformations, and how jobs split into stages and tasks.
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Miscellaneous/Types of Fact Table|Types of Fact Tables in Data Warehousing]] — Fact table grain types (transaction, snapshot, accumulating, factless) with SQL examples.

- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Miscellaneous/Miscellaneous|Miscellaneous]] — Section index for supporting Spark concepts outside Joins and Memory Management.

### Diagrams
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Spark Images/Spark Images|Spark Images]] — Index of supporting diagrams for memory management and the Spark SQL engine.
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Spark Images/Memory Management Images/Memory Management Image|Memory Management Image]] — Driver/executor memory layout diagrams.
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Spark Images/Spark SQL Engine/Spark SQL Engine Image|Spark SQL Engine Image]] — Spark SQL / Catalyst engine diagrams.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Pyspark/PySpark|PySpark]] — this note covers Spark internals (execution model, memory management, join strategies); PySpark covers the practical DataFrame/streaming API built on top of them.

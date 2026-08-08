# Memory Management

Spark driver and executor memory architecture, and how each runs out of memory.

- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Driver Memory Management|Spark Driver Memory Architecture]] — JVM heap/non-heap/off-heap layout of the driver process.
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Driver OOM|Driver Out-Of-Memory (OOM) in Spark]] — Causes, symptoms, and fixes for driver OOM.
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Executer Memory Management|Spark Executor Memory Architecture]] — Unified memory manager: reserved, user, execution, and storage memory.
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Executer OOM with Salting|Executor OOM in Spark (with Salting)]] — Causes of executor OOM and how salting fixes data skew.

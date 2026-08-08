# Delta Lake

Delta Lake is an open table format that adds ACID transactions, schema enforcement/evolution, and versioned (time-travel) access on top of Parquet files in a data lake — the storage layer behind the "lakehouse" architecture.

## 🗺️ Map of Content (auto-generated)

### ACID Properties
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Acid Property|ACID Property]] — overview linking the four properties below.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Atomicity in Delta Lake|Atomicity in Delta Lake]] — all-or-nothing writes via the transaction log and atomic commits.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Consistency in Delta Lake|Consistency in Delta Lake]] — schema enforcement and OCC keep the table always valid.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Isolation in Delta Lake|Isolation in Delta Lake]] — snapshot reads and optimistic concurrency control for concurrent transactions.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Durability in Delta Lake|Durability in Delta Lake]] — committed data survives crashes via persistent storage and the log.

### Commands by API
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Delta Lake Commands in Different APIs/Delta Lake Commands in Different APIs|Delta Lake Commands in Different APIs]] — overview of the Python vs. SQL command surfaces.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Delta Lake Commands in Different APIs/Delta Lake Commands in Python API with Spark|Delta Lake Commands in Python API with Spark]] — the `DeltaTable`/DataFrame API reference.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Delta Lake Commands in Different APIs/Delta Lake Commands in SQL API|Delta Lake Commands in SQL API]] — the equivalent Spark SQL DDL/DML reference.

### Table Properties & Utility Commands
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Important TBLProperties/Important TBLProperties|Important TBLProperties]] — overview of table properties and utility commands.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Important TBLProperties/Change Data Feed|Change Data Feed]] — row-level change tracking via `delta.enableChangeDataFeed` and `table_changes()`.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Important TBLProperties/Table Utility Commands|Table Utility Commands]] — full reference: `DESCRIBE`, `SHOW`, `HISTORY`, time travel, `RESTORE`, `VACUUM`, `OPTIMIZE`, `ANALYZE`, cloning.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Important TBLProperties/Table Utility Essential Commands|Table Utility Essential Commands]] — condensed cheat-sheet version of the same commands.

### Other Important Concepts
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Other Important Concepts|Other Important Concepts]] — overview of this group.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Open Table Format|Open Table Format]] — what an OTF is, and how Delta compares to Iceberg/Hudi.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Delta Lake Uniform Format|Delta Lake Uniform Format (UniForm)]] — making Delta tables readable by Iceberg/Hudi engines.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Optimize, ZOrdering, Liquid Clustering|Optimize, Z-Ordering, Liquid Clustering]] — physical layout tuning for query performance.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Schema Operations|Schema Operations]] — schema enforcement vs. evolution vs. overwrite.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Upsert In DeltaLake|Upsert in Delta Lake]] — `MERGE` for batch and streaming upserts.

### Questions & Deep Dives
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Questions/Questions|Questions]] — index of worked questions.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Questions/How Versioning Works in Delta Lake|How Versioning Works in Delta Lake]] — why versioning depends on `VACUUM` retention, not infinite file history.

### Supporting Media
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Delta Lake Images/Delta Lake Images|Delta Lake Images]] — diagrams and screenshots referenced from the notes above.

- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Delta Lake Images/Untitled|Untitled]] — empty scratch note left inside Delta Lake Images/; no content yet, flagged for cleanup or future use.

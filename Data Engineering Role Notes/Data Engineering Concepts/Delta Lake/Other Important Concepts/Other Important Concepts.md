# Other Important Delta Lake Concepts

A grab-bag of Delta Lake concepts that don't fall under ACID or core table utility commands, but come up regularly in real usage.

- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Open Table Format|Open Table Format]] — what an open table format is, and where Delta Lake, Iceberg, and Hudi fit relative to each other.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Delta Lake Uniform Format|Delta Lake Uniform Format (UniForm)]] — making a Delta table readable by Iceberg/Hudi engines without duplicating data.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Optimize, ZOrdering, Liquid Clustering|Optimize, Z-Ordering, Liquid Clustering]] — physical layout tuning: file compaction, Z-order, and liquid clustering.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Schema Operations|Schema Operations]] — schema enforcement vs. evolution vs. overwrite.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Upsert In DeltaLake|Upsert in Delta Lake]] — `MERGE` / `.merge()` for batch and streaming upserts.

# ACID Property in Delta Lake

Delta Lake brings database-style **ACID transactions** to the data lake. Each letter maps to a dedicated note with the mechanism behind it:

- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Atomicity in Delta Lake|Atomicity]] — writes are all-or-nothing, enforced via the transaction log and atomic commits.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Consistency in Delta Lake|Consistency]] — schema enforcement and transaction validation keep the table always in a valid state.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Isolation in Delta Lake|Isolation]] — snapshot reads plus optimistic concurrency control keep concurrent transactions from interfering with each other.
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/ACID Property/Durability in Delta Lake|Durability]] — committed data survives crashes via persistent storage and an immutable transaction log.

All four properties are underpinned by the same core mechanism: the `_delta_log/` transaction log plus atomic commits to it.

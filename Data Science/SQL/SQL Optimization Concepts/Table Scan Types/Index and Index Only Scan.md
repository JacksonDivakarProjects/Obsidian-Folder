# Comprehensive Guide: Index Scan vs Index-Only Scan in SQL

Understanding how databases use indexes during query execution is vital for optimizing performance—especially for read-heavy applications. Two core scan strategies are **Index Scan** and **Index-Only Scan**. Let's explore what they are, how they work, their pros and cons, and best use cases.

---

## What is an Index Scan?

**Index Scan** is a query execution strategy where the database engine uses an index to filter rows based on search criteria—**but still needs to fetch additional data from the main table (heap)** if not all requested columns are present in the index.

## How Index Scan Works

1. **Scan the Index:** The engine walks through the index to find matching row pointers, based on the query's WHERE clause conditions.
    
2. **Table (Heap) Lookup:** For every index match, it fetches the corresponding row from the main table to get any other required columns not present in the index.
    

**Use Case:**

- When the query requires columns not stored in the index.
    
- Typical for queries with predicates on indexed columns but SELECTs other columns too.
    

**Pros:**

- More efficient than a full table scan if selectivity is high on the indexed column(s).
    
- Index helps dramatically narrow down which rows to fetch.
    

**Cons:**

- Can be slower if it needs to fetch a large number of rows from the table (lots of random I/O).
    
- Still needs to access the table for missing columns, increasing I/O.
    

---

## What is an Index-Only Scan?

**Index-Only Scan** is an optimized variant where **all required columns are present in the index itself** (a "covering index"). The query can be answered entirely by scanning the index, skipping table access altogether.

## How Index-Only Scan Works

1. **Scan the Index:** The engine scans the index, applying filters and retrieving all required columns directly from the index structure.
    
2. **Visibility Checks:** The database checks whether each row is "visible" to the transaction (for MVCC databases), but without fetching the full table row data.[pganalyze+1](https://pganalyze.com/docs/explain/scan-nodes/index-only-scan)​
    

**Use Case:**

- The query only references columns that are included in the index.
    
- Especially effective for read-heavy, reporting, and analytics queries.
    

**Pros:**

- **Much faster read performance** since no table (heap) access is needed.[jsupskills+1](https://jsupskills.dev/index-scan-vs-index-only-scan-optimizing-database/)​
    
- **Lower I/O overhead**, reducing disk reads and improving throughput.
    

**Cons:**

- Requires "covering indexes," which can make indexes larger (potentially slower to update and insert).
    
- More index maintenance overhead if indexes expand to cover more columns.
    

---

## Key Differences At-a-Glance

|Feature|Index Scan|Index-Only Scan|
|---|---|---|
|Table Lookup|Yes (for missing columns)|No (all data from index)|
|Performance|Can involve more I/O if querying non-indexed columns|Faster—less I/O if index covers requested columns|
|Use Case|When not all required columns are indexed|When all required columns are **within** the index|
|Index Size|Smaller|Larger (for covering all needed columns)|
|Ideal For|Queries needing extra data from the table|Read-heavy workloads, reporting, analytics|

---

## When to Optimize for Index-Only Scans

- Queries consistently fetch the same set of columns.
    
- Read performance is critical (analytics/reporting).
    
- Willing to trade a bit more write overhead for faster reads.
    

**Best Practice:**

- Create **covering indexes** for key read queries: include all SELECTed and WHERE columns in the index.
    

---

## Example

Suppose you have a table `users(id, name, age, email)` and an index on `(age, name)`:

## Index Scan (not covering):

sql

`SELECT name, email FROM users WHERE age = 30;`

- The index helps find rows with `age = 30`, but since `email` isn't in the index, each match requires a table lookup.
    

## Index-Only Scan (covering):

Suppose you created an index on `(age, name, email)`.

sql

`SELECT name, email FROM users WHERE age = 30;`

- Now, all required columns are in the index—**no table lookup required**. This query can be served entirely from the index.
    

---

## Summary Table

|Scan Type|What Happens|When Used|
|---|---|---|
|Index Scan|Scan index, then fetch extra data from table|Query needs columns not in index|
|Index-Only Scan|All needed data in index; no table fetch|Query needs only columns present in index|

---

## Key Takeaways

- **Index Scan** helps filter efficiently, but needs table lookups for missing columns.
    
- **Index-Only Scan** avoids table lookups, boosting performance—possible only with covering indexes.
    
- Analyze your frequent queries and consider covering indexes for high-value read operations.
    


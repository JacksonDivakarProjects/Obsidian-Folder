# Comprehensive Guide to Sequential Scan in SQL

## What is a Sequential Scan?

A **sequential scan** (also known as a _full table scan_) is the simplest method for reading data in a SQL database. The engine reads every page and every row in the table, one after another, to check if each row matches the query conditions or needs to be included in the result set.[pganalyze+3](https://pganalyze.com/docs/explain/scan-nodes/sequential-scan)​

## How Sequential Scan Works

- **Reads the Table in Order:** The engine starts at the beginning of the table and processes each row in turn, regardless of any indexes or order.
    
- **Checks Row Validity:** For each row, it verifies whether it meets the filter conditions in the `WHERE` clause.[percona](https://www.percona.com/blog/decoding-sequential-scans-in-postgresql/)​
    
- **Discard or Output:** Rows satisfying the condition are sent to the result, others are skipped.
    

## When Is Sequential Scan Used?

- **No Indexes:** If the table does not have an index on the columns involved in the query, the planner uses a sequential scan.[postgresql](https://www.postgresql.org/docs/current/using-explain.html)​
    
- **Small Tables:** For small tables, scanning the whole table can be faster than using an index because there is less overhead involved.[leapcell](https://leapcell.io/blog/demystifying-postgres-explain-is-sequential-scan-always-a-performance-blocker)​
    
- **Large Result Sets:** If the query needs a large proportion of the table's data, a sequential scan may be more efficient than hopping via indexes.[postgrespro+1](https://postgrespro.com/blog/pgsql/5969403)​
    
- **Fetching All Columns:** If you want nearly all columns and rows, or perform `SELECT *`, the engine may choose a sequential scan even if indexes exist.[zen8labs](https://www.zen8labs.com/insights/development/sql/postgresql-scan-types-what-are-they/)​
    

## Performance Characteristics

- **Efficiency:** Sequential scan is very efficient for reading entire tables or large subsets because it minimizes random disk I/O and can leverage sequential disk access.[wikipedia+1](https://en.wikipedia.org/wiki/Full_table_scan)​
    
- **Slow for Small Result Sets:** If only a few rows are needed, sequential scan can be slower than index scans because it examines every row.[stackoverflow+1](https://stackoverflow.com/questions/66820661/index-scan-vs-sequential-scan-in-postgres)​
    
- **Buffering and Parallelism:** Modern engines like PostgreSQL use buffers and can synchronize sequential scans between sessions to reduce I/O if multiple queries read the same data. For very large tables, parallel sequential scans can split the work among multiple worker sessions.[dev+1](https://dev.to/franckpachot/postgresql-synchronized-sequential-scans-and-limit-without-an-order-by-1kia)​
    

## Typical Plan Output

When you run `EXPLAIN` on a query, a sequential scan is represented as `Seq Scan on tablename` or `Sequential Scan` in the output.[postgresql](https://www.postgresql.org/docs/current/using-explain.html)​

## Example Use Cases

- Reporting queries that require all or most table data
    
- Testing or debugging when indexes are disabled
    
- Tables without indexes, or after index drops
    

## How to Avoid Unwanted Sequential Scans

- **Create Indexes:** Add indexes to columns frequently used in WHERE clauses or JOIN conditions.
    
- **Selective Queries:** Make queries more selective, so the planner prefers index scans.
    
- **EXPLAIN Your Queries:** Use `EXPLAIN` to see if your query triggers a sequential scan in the plan.
    

## Summary Table

|Situation|Sequential Scan Likely?|
|---|---|
|No indexes on relevant columns|Yes|
|Query returns most/all rows|Yes|
|Query is highly selective|No (index scan preferred)|
|Table is very small|Yes (sequential scan may be faster)|
|Index is not covering all columns|Sometimes (if query requests all columns)|

## Key Takeaways

- Sequential scan examines every row of a table and is always available, but not always optimal.
    
- Sometimes it is surprisingly efficient—for small tables or queries fetching much of the data.
    
- For selective queries and large tables, indexes or index scans are usually better.
    

Let me know if you want to see a practical query example, advice for specific database systems, or guidance on EXPLAIN plan interpretation!

1. [https://pganalyze.com/docs/explain/scan-nodes/sequential-scan](https://pganalyze.com/docs/explain/scan-nodes/sequential-scan)
2. [https://en.wikipedia.org/wiki/Full_table_scan](https://en.wikipedia.org/wiki/Full_table_scan)
3. [https://stackoverflow.com/questions/66820661/index-scan-vs-sequential-scan-in-postgres](https://stackoverflow.com/questions/66820661/index-scan-vs-sequential-scan-in-postgres)
4. [https://dev.to/franckpachot/postgresql-synchronized-sequential-scans-and-limit-without-an-order-by-1kia](https://dev.to/franckpachot/postgresql-synchronized-sequential-scans-and-limit-without-an-order-by-1kia)
5. [https://leapcell.io/blog/demystifying-postgres-explain-is-sequential-scan-always-a-performance-blocker](https://leapcell.io/blog/demystifying-postgres-explain-is-sequential-scan-always-a-performance-blocker)
6. [https://www.percona.com/blog/decoding-sequential-scans-in-postgresql/](https://www.percona.com/blog/decoding-sequential-scans-in-postgresql/)
7. [https://postgrespro.com/blog/pgsql/5969403](https://postgrespro.com/blog/pgsql/5969403)
8. [https://www.zen8labs.com/insights/development/sql/postgresql-scan-types-what-are-they/](https://www.zen8labs.com/insights/development/sql/postgresql-scan-types-what-are-they/)
9. [https://www.postgresql.org/docs/current/using-explain.html](https://www.postgresql.org/docs/current/using-explain.html)
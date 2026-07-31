# Comprehensive Guide: Bitmap Heap Scan in PostgreSQL

## What Is a Bitmap Heap Scan?

A **Bitmap Heap Scan** is a step in query execution (often following a Bitmap Index Scan) where PostgreSQL retrieves actual table rows based on a bitmap of qualifying row locations. This method allows the database to fetch only relevant pages, significantly reducing disk I/O when many—but not most—rows are needed.[pganalyze+2](https://pganalyze.com/docs/explain/scan-nodes/bitmap-heap-scan)​

## How Does Bitmap Heap Scan Work?

1. **Bitmap Creation**: One or more Bitmap Index Scans (optionally via BitmapAnd/BitmapOr nodes) generate a bitmap—a compact map of row locations (TIDs) in the table that match some condition.
    
2. **Bitmap Processing**:
    
    - Each bit in the bitmap represents a row position (within a page of the table).
        
    - If multiple indexes are used, bitmaps can be combined using bitwise operations, allowing for AND/OR queries.
        
3. **Heap Scan**:
    
    - The Bitmap Heap Scan reads only the table pages that the bitmap marks as containing qualifying rows.
        
    - Each relevant page is fetched only once; PostgreSQL then retrieves all needed rows from it at once.[stackoverflow+3](https://stackoverflow.com/questions/6592626/what-is-a-bitmap-heap-scan-in-a-query-plan)​
        
4. **Recheck Condition**:
    
    - Sometimes, especially when memory is limited (`work_mem`), the bitmap may become _lossy_—tracking only which pages, but not exactly which rows, have matches.
        
    - In such cases, every row on the marked page is re-checked against the condition to ensure accuracy (`Recheck Cond`)
        
    - If the bitmap is precise (_exact_), no recheck is needed.[pgmustard+3](https://www.pgmustard.com/docs/explain/bitmap-heap-scan)​
        

## Example: Bitmap Heap Scan in Action

Suppose you run:

sql

`SELECT * FROM person WHERE age = 20;`

PostgreSQL plan:

text

`Bitmap Heap Scan on person   Recheck Cond: (age = 20)  -> Bitmap Index Scan on idx_person_age       Index Cond: (age = 20)`

- `Bitmap Index Scan` identifies rows where `age = 20` and builds a bitmap of those locations.
    
- `Bitmap Heap Scan` then fetches only the necessary pages, collecting all matching rows efficiently and rechecking conditions only if the bitmap is lossy.[eliasdorneles+2](https://eliasdorneles.com/til/posts/about-bitmap-heap-scan-on-potgresql-query-plan/)​
    

## When to Use Bitmap Heap Scan

- **Medium-sized queries**: Fetching several percent but not all of the table—too many for a plain index scan, too few for a sequential scan.[cybertec-postgresql+1](https://www.cybertec-postgresql.com/en/postgresql-indexing-index-scan-vs-bitmap-scan-vs-sequential-scan-basics/)​
    
- **Combining multiple indexes**: For queries with multiple AND/OR conditions (e.g., `age = 20` AND `active = true`), combining bitmaps from different indexes is efficient.[yugabyte](https://www.yugabyte.com/blog/bitmap-scans-on-distributed-postgresql/)​
    
- **When physical clustering is poor**: Especially useful if relevant rows are spread across many pages, making random access expensive.
    

## Advantages

- **Reduces random I/O**: Each page needed is read only once, minimizing disk seeks.
    
- **Bulk-read efficiency**: Improves caching since many matching rows are fetched together.
    
- **Combines multiple conditions**: Efficiently merges results from several indexes.
    

## Limitations

- **Memory use**: If bitmaps don’t fit in memory, PostgreSQL switches to lossy mode, potentially causing extra rechecks and more I/O.[pganalyze+2](https://pganalyze.com/docs/explain/scan-nodes/bitmap-heap-scan)​
    
- **Large result sets**: If almost every row qualifies, a sequential scan is more efficient.
    

## Quick Summary Table

|Step|What It Does|
|---|---|
|Bitmap Index Scan|Builds bitmap of qualifying row positions|
|Bitmap Heap Scan|Reads pages shown in the bitmap, retrieves matching rows (rechecks if needed)|
|Lossy vs Exact Bitmap|Lossy: page-level only (may require row checks); Exact: row-level detail (no recheck needed)|

A Bitmap Heap Scan sits between an index scan and a sequential scan in both speed and utility, and is one of PostgreSQL’s key tools for handling mid-sized result sets efficiently.

1. [https://pganalyze.com/docs/explain/scan-nodes/bitmap-heap-scan](https://pganalyze.com/docs/explain/scan-nodes/bitmap-heap-scan)
2. [https://stackoverflow.com/questions/6592626/what-is-a-bitmap-heap-scan-in-a-query-plan](https://stackoverflow.com/questions/6592626/what-is-a-bitmap-heap-scan-in-a-query-plan)
3. [https://www.pgmustard.com/docs/explain/bitmap-heap-scan](https://www.pgmustard.com/docs/explain/bitmap-heap-scan)
4. [https://eliasdorneles.com/til/posts/about-bitmap-heap-scan-on-potgresql-query-plan/](https://eliasdorneles.com/til/posts/about-bitmap-heap-scan-on-potgresql-query-plan/)
5. [https://www.percona.com/blog/one-index-three-different-postgresql-scan-types-bitmap-index-and-index-only/](https://www.percona.com/blog/one-index-three-different-postgresql-scan-types-bitmap-index-and-index-only/)
6. [https://www.yugabyte.com/blog/bitmap-scans-on-distributed-postgresql/](https://www.yugabyte.com/blog/bitmap-scans-on-distributed-postgresql/)
7. [https://www.cybertec-postgresql.com/en/postgresql-indexing-index-scan-vs-bitmap-scan-vs-sequential-scan-basics/](https://www.cybertec-postgresql.com/en/postgresql-indexing-index-scan-vs-bitmap-scan-vs-sequential-scan-basics/)
8. [https://www.postgresql.org/docs/8.1/performance-tips.html](https://www.postgresql.org/docs/8.1/performance-tips.html)
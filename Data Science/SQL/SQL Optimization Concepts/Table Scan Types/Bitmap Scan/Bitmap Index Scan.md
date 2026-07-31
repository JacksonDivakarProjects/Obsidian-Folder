Here is a comprehensive guide to Bitmap Index Scan in PostgreSQL, suitable for revision and deep understanding.[pganalyze+5](https://pganalyze.com/docs/explain/scan-nodes/bitmap-index-scan)​

---

## Guide: Bitmap Index Scan in PostgreSQL

## What is Bitmap Index Scan?

A Bitmap Index Scan is a multi-step query execution technique in PostgreSQL that leverages indexes but operates on them using bitwise logic, producing a bitmap of qualifying tuple positions before fetching them in bulk.[percona+1](https://www.percona.com/blog/one-index-three-different-postgresql-scan-types-bitmap-index-and-index-only/)​

## How it Works

1. **Stage 1: Bitmap Creation**
    
    - The index is scanned to find all positions (tuple IDs) that satisfy the query condition.[yugabyte+1](https://www.yugabyte.com/blog/bitmap-scans-on-distributed-postgresql/)​
        
    - Each matching position sets a '1' in the bitmap; non-matching are '0'. The bitmap groups these by data pages.[pgmustard](https://www.pgmustard.com/docs/explain/bitmap-index-scan)​
        
    - If multiple conditions exist, multiple bitmaps are generated and combined using fast bitwise AND/OR logic.[postgresql+1](https://www.postgresql.org/docs/current/indexes-bitmap-scans.html)​
        
2. **Stage 2: Bitmap Heap Scan**
    
    - The combined bitmap is passed to the Bitmap Heap Scan node.
        
    - The heap scan reads table pages, fetching all rows matching positions marked in the bitmap.
        
    - This ensures each page is read once, minimizing disk I/O.[percona+2](https://www.percona.com/blog/one-index-three-different-postgresql-scan-types-bitmap-index-and-index-only/)​
        

## When is it Used?

- **Moderate result set**: When a query retrieves more rows than a regular index scan is efficient for, but not enough for a sequential scan.[cybertec-postgresql+1](https://www.cybertec-postgresql.com/en/postgresql-indexing-index-scan-vs-bitmap-scan-vs-sequential-scan-basics/)​
    
- **Multi-condition queries**: When the query benefits from combining several indexes using AND/OR logic.[postgresql](https://www.postgresql.org/docs/current/indexes-bitmap-scans.html)​
    
- **Bulk efficiency**: When there’s an incentive to minimize random reads and read many rows from each data page.[pganalyze+1](https://pganalyze.com/docs/explain/scan-nodes/bitmap-index-scan)​
    

## Example Query and Plan

Suppose a table `orders` with indexes on `customer_id` and `order_date`:

sql

`SELECT * FROM orders WHERE customer_id = 100 AND order_date > '2023-01-01';`

Typical execution plan:

text

`Bitmap Heap Scan on orders   -> BitmapAnd       -> Bitmap Index Scan on idx_customer_id          Index Cond: (customer_id = 100)       -> Bitmap Index Scan on idx_order_date          Index Cond: (order_date > '2023-01-01')`

- Bitmap Index Scan nodes scan indexes, producing bitmaps.
    
- BitmapAnd node combines the bitmaps.
    
- Bitmap Heap Scan fetches rows in bulk, page-by-page, only where the bitmap marks a match.[cybertec-postgresql+2](https://www.cybertec-postgresql.com/en/postgresql-indexing-index-scan-vs-bitmap-scan-vs-sequential-scan-basics/)​
    

## Optimization and Limitations

- **Highly optimal** for bulk reads and combining indexes.
    
- Avoid for highly selective queries (prefer index scan) or queries returning most table rows (prefer sequential scan).[percona+1](https://www.percona.com/blog/one-index-three-different-postgresql-scan-types-bitmap-index-and-index-only/)​
    
- Bitmap scans require enough memory for the bitmap; if not, performance may degrade due to “lossy” bitmap or extra heap filtering.[pgmustard](https://www.pgmustard.com/docs/explain/bitmap-index-scan)​
    
- Result order is not preserved, so sorting may be needed for “ORDER BY” queries.[postgresql+1](https://www.postgresql.org/docs/current/indexes-bitmap-scans.html)​
    

## Key Benefits

- Minimize disk I/O via page-wise bulk fetching.[yugabyte](https://www.yugabyte.com/blog/bitmap-scans-on-distributed-postgresql/)​
    
- Efficient for AND/OR combination of multiple indexes.[pganalyze+1](https://pganalyze.com/docs/explain/scan-nodes/bitmap-index-scan)​
    
- Bitwise operations enable high-speed logic for query planning.[pgmustard+1](https://www.pgmustard.com/docs/explain/bitmap-index-scan)​
    

---


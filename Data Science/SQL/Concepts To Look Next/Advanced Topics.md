Advanced SQL topics represent the transition from basic querying to database system reasoning. These areas are expected for data engineers, database developers, and performance-focused roles.

---

## 1. Query Optimization and Execution Plans

Understanding how the database executes queries.

Key concepts:

- **Execution plan / Query plan**
    
- **Cost-based optimization**
    
- **Join algorithms**
    
    - Nested Loop Join
        
    - Hash Join
        
    - Merge Join
        
- **Scan types**
    
    - Sequential Scan
        
    - Index Scan
        
    - Index Only Scan
        
    - Bitmap Index Scan
        
    - Bitmap Heap Scan
        

Focus:

- How the optimizer chooses an index
    
- Why a full table scan occurs
    
- Cost estimation errors
    

Example:

```sql
EXPLAIN ANALYZE
SELECT *
FROM orders
WHERE customer_id = 10;
```

---

## 2. Indexing Internals

Indexes are the core of SQL performance.

Types:

- **B-Tree index** (most common)
    
- **Hash index**
    
- **Bitmap index**
    
- **GIN index**
    
- **GiST index**
    
- **BRIN index**
    

Advanced concepts:

- Composite indexes
    
- Covering indexes
    
- Partial indexes
    
- Index selectivity
    
- Index cardinality
    
- Index-only scans
    

Example:

```sql
CREATE INDEX idx_orders_customer_date
ON orders(customer_id, order_date);
```

---

## 3. Window Functions (Analytical SQL)

Operate across rows without collapsing them.

Common window functions:

- `ROW_NUMBER()`
    
- `RANK()`
    
- `DENSE_RANK()`
    
- `LEAD()`
    
- `LAG()`
    
- `FIRST_VALUE()`
    
- `LAST_VALUE()`
    

Example:

```sql
SELECT employee_id,
       salary,
       RANK() OVER (PARTITION BY department ORDER BY salary DESC)
FROM employees;
```

Use cases:

- Ranking
    
- Running totals
    
- Time series analysis
    

---

## 4. Common Table Expressions (CTE)

Temporary named result sets.

Types:

- Non-recursive CTE
    
- Recursive CTE
    

Example:

```sql
WITH sales_summary AS (
  SELECT product_id, SUM(amount) AS total_sales
  FROM sales
  GROUP BY product_id
)
SELECT *
FROM sales_summary
WHERE total_sales > 10000;
```

Recursive example:

```sql
WITH RECURSIVE org_chart AS (
  SELECT id, manager_id
  FROM employees
  WHERE manager_id IS NULL
  UNION ALL
  SELECT e.id, e.manager_id
  FROM employees e
  JOIN org_chart o ON e.manager_id = o.id
)
SELECT * FROM org_chart;
```

---

## 5. Partitioning

Splitting large tables into smaller physical segments.

Types:

- Range partitioning
    
- List partitioning
    
- Hash partitioning
    

Example:

```sql
CREATE TABLE sales (
  id INT,
  sale_date DATE,
  amount NUMERIC
) PARTITION BY RANGE (sale_date);
```

Use cases:

- Large datasets
    
- Time-series data
    
- Data retention policies
    

---

## 6. Transactions and Isolation Levels

Ensuring data consistency.

ACID:

- Atomicity
    
- Consistency
    
- Isolation
    
- Durability
    

Isolation levels:

- Read Uncommitted
    
- Read Committed
    
- Repeatable Read
    
- Serializable
    

Example:

```sql
BEGIN;

UPDATE accounts
SET balance = balance - 100
WHERE id = 1;

UPDATE accounts
SET balance = balance + 100
WHERE id = 2;

COMMIT;
```

Concepts:

- Dirty reads
    
- Non-repeatable reads
    
- Phantom reads
    

---

## 7. Locking and Concurrency Control

Managing multiple users accessing data.

Types:

- Row-level locks
    
- Table-level locks
    
- Deadlocks
    
- MVCC (Multi-Version Concurrency Control)
    

Example:

```sql
SELECT *
FROM orders
WHERE id = 100
FOR UPDATE;
```

---

## 8. Advanced Joins

Beyond simple inner joins.

Types:

- LATERAL joins
    
- SELF joins
    
- CROSS joins
    
- SEMI joins
    
- ANTI joins
    

Example:

```sql
SELECT *
FROM orders o
LEFT JOIN LATERAL (
  SELECT *
  FROM payments p
  WHERE p.order_id = o.id
  LIMIT 1
) p ON true;
```

---

## 9. Materialized Views

Stored query results used for performance.

```sql
CREATE MATERIALIZED VIEW monthly_sales AS
SELECT date_trunc('month', sale_date) AS month,
       SUM(amount)
FROM sales
GROUP BY month;
```

Refresh:

```sql
REFRESH MATERIALIZED VIEW monthly_sales;
```

---

## 10. Stored Procedures and Functions

Database-side programming.

Example:

```sql
CREATE FUNCTION get_total_orders(customer INT)
RETURNS INT
AS $$
SELECT COUNT(*)
FROM orders
WHERE customer_id = customer;
$$ LANGUAGE SQL;
```

Use cases:

- Encapsulating business logic
    
- Reusable queries
    

---

## 11. JSON and Semi-Structured Data

Modern databases handle JSON.

Example:

```sql
SELECT data->>'name'
FROM users
WHERE data->>'age' > '25';
```

---

## 12. SQL for Big Data Systems

Important for data engineering.

Tools:

- Apache Spark SQL
    
- Presto / Trino
    
- Hive SQL
    
- BigQuery
    
- Snowflake
    

Concepts:

- Columnar storage
    
- Distributed query execution
    
- Predicate pushdown
    
- Data skew
    

---

## Advanced SQL Topics Expected for Data Engineers

Priority order:

1. Query execution plan
    
2. Index internals
    
3. Window functions
    
4. Partitioning
    
5. Transactions and isolation
    
6. Locking and MVCC
    
7. CTE and recursion
    
8. Materialized views
    
9. Query optimization techniques
    

---

Core principle behind advanced SQL:

SQL is not only **data retrieval**.  
It is **query planning, storage structures, and computational strategy inside a database engine**.
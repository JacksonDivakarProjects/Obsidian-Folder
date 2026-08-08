Advanced SQL topics mark the transition from basic querying to reasoning about the database system itself — planning, storage, and concurrency. These areas are expected for data engineers, database developers, and performance-focused roles.

## 1. Query Optimization and Execution Plans

Understanding how the database actually executes a query, not just what it returns.

Key concepts:
- **Execution plan / query plan** — the step-by-step strategy the engine picked to run a query.
- **Cost-based optimization** — the planner estimates the cost of alternative strategies (using table statistics) and picks the cheapest.
- **Join algorithms** — Nested Loop Join, Hash Join, Merge Join.
- **Scan types** — Sequential Scan, Index Scan, Index-Only Scan, Bitmap Index Scan, Bitmap Heap Scan.

Focus areas:
- How the optimizer chooses (or refuses) an index.
- Why a full table scan happens even when an index exists (e.g., low selectivity, missing statistics, functions wrapped around a column).
- Cost-estimation errors — usually caused by stale statistics (`ANALYZE`) or bad row-count assumptions.

```sql
EXPLAIN ANALYZE
SELECT *
FROM orders
WHERE customer_id = 10;
```

## 2. Indexing Internals

Indexes are the core lever for SQL performance.

Common index types:
- **B-Tree** — the default, general-purpose index (equality and range predicates, sorting).
- **Hash** — equality-only lookups.
- **Bitmap** — used internally by the planner to combine multiple index conditions (see Bitmap Index/Heap Scan).
- **GIN** — good for arrays, full-text search, and JSONB containment queries.
- **GiST** — geometric data, ranges, and other non-linear structures.
- **BRIN** — block-range summaries; cheap and effective on huge, naturally-ordered tables (e.g., time-series by insertion date).

Advanced concepts:
- Composite indexes (multi-column, column order matters).
- Covering indexes (all columns a query needs are in the index, enabling index-only scans).
- Partial indexes (index only a filtered subset of rows).
- Selectivity and cardinality (how much an index condition narrows the row set — drives whether the optimizer bothers using the index).

```sql
CREATE INDEX idx_orders_customer_date
ON orders (customer_id, order_date);
```

## 3. Window Functions (Analytical SQL)

Compute a value across a set of related rows without collapsing them into groups — every input row still appears in the output.

Common functions: `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`, `LEAD()`, `LAG()`, `FIRST_VALUE()`, `LAST_VALUE()`.

```sql
SELECT employee_id,
       salary,
       RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank
FROM employees;
```

Typical use cases: ranking, running totals, time-series comparisons (period-over-period).

## 4. Common Table Expressions (CTEs)

Named, temporary result sets scoped to a single statement — improve readability and let a subquery be reused or made self-referential.

Types: non-recursive CTE, recursive CTE.

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

Recursive example (walking a management hierarchy):

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

## 5. Partitioning

Splitting one logical table into smaller physical segments so queries and maintenance only touch the relevant slice.

Types: range, list, hash.

```sql
CREATE TABLE sales (
  id INT,
  sale_date DATE,
  amount NUMERIC
) PARTITION BY RANGE (sale_date);

-- The parent table above only declares the partitioning strategy;
-- actual data lives in child partitions such as:
CREATE TABLE sales_2025 PARTITION OF sales
  FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

Use cases: very large tables, time-series data, data-retention policies (drop an old partition instead of a slow `DELETE`).

## 6. Transactions and Isolation Levels

Mechanisms that keep concurrent changes consistent.

ACID: Atomicity, Consistency, Isolation, Durability.

Isolation levels (weakest to strongest): Read Uncommitted, Read Committed, Repeatable Read, Serializable.

```sql
BEGIN;

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

COMMIT;
```

Anomalies each isolation level guards against: dirty reads, non-repeatable reads, phantom reads.

## 7. Locking and Concurrency Control

How the engine arbitrates multiple sessions touching the same data.

Concepts: row-level locks, table-level locks, deadlocks, MVCC (Multi-Version Concurrency Control — readers see a consistent snapshot instead of blocking on writers).

```sql
SELECT *
FROM orders
WHERE id = 100
FOR UPDATE;
```

## 8. Advanced Joins

Beyond a plain inner join:
- **LATERAL** joins — a subquery in `FROM` that can reference columns from the table listed before it.
- **SELF** joins — a table joined to itself (hierarchies, comparisons between rows).
- **CROSS** joins — full cartesian product.
- **SEMI** joins — "does a match exist" (typically expressed via `EXISTS`), without duplicating rows for multiple matches.
- **ANTI** joins — "no match exists" (typically expressed via `NOT EXISTS`).

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

## 9. Materialized Views

Query results persisted to disk for fast re-reads, at the cost of going stale until refreshed.

```sql
CREATE MATERIALIZED VIEW monthly_sales AS
SELECT date_trunc('month', sale_date) AS month,
       SUM(amount) AS total
FROM sales
GROUP BY month;

REFRESH MATERIALIZED VIEW monthly_sales;
```

## 10. Stored Procedures and Functions

Database-side programming for encapsulating and reusing business logic close to the data.

```sql
CREATE FUNCTION get_total_orders(customer INT)
RETURNS INT
AS $$
SELECT COUNT(*)
FROM orders
WHERE customer_id = customer;
$$ LANGUAGE SQL;
```

## 11. JSON and Semi-Structured Data

Modern relational databases can store and query JSON/JSONB columns directly.

```sql
SELECT data->>'name'
FROM users
WHERE (data->>'age')::int > 25;
```

Note: `data->>'age'` returns text, so numeric comparisons need an explicit cast (as above) rather than comparing text to a number.

## 12. SQL for Big Data Systems

Relevant tools: Apache Spark SQL, Presto/Trino, Hive SQL, BigQuery, Snowflake.

Concepts: columnar storage, distributed query execution, predicate pushdown, data skew.

## Priority Order for Data Engineers

1. Query execution plans
2. Index internals
3. Window functions
4. Partitioning
5. Transactions and isolation
6. Locking and MVCC
7. CTEs and recursion
8. Materialized views
9. General query-optimization technique

**Core principle:** SQL isn't only data retrieval — it's query planning, storage structures, and computational strategy inside a database engine.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/Recursive CTE/Recursive CTE|Recursive CTE]]
- [[Data Engineering Role Notes/SQL/Window Functions/Window Functions|Window Functions]]
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/SQL Optimization Concepts|SQL Optimization Concepts]]
- [[Data Engineering Role Notes/SQL/Materialized View/Materialized View In Postgres SQL|Materialized Views – The Complete Guide (PostgreSQL)]]

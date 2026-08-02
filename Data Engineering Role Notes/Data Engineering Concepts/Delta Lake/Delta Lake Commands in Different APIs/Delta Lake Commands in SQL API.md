
# Delta Lake Object Commands Comprehensive Guide

## Overview
Delta Lake object commands provide powerful capabilities for managing and manipulating Delta tables using object storage semantics. This guide covers the complete set of commands and their usage patterns.

## Core Object Commands

### 1. CREATE TABLE

**Syntax:**
```sql
CREATE TABLE [IF NOT EXISTS] table_name
[(column_name data_type [COMMENT col_comment] [, ...])]
[USING DELTA]
[LOCATION 'path']
[TBLPROPERTIES (property_name = property_value [, ...])]
```

**Examples:**
```sql
-- Basic table creation
CREATE TABLE events (
    id BIGINT,
    event_time TIMESTAMP,
    event_name STRING,
    user_id BIGINT
) USING DELTA
LOCATION 's3://bucket/events';

-- With table properties
CREATE TABLE sales (
    sale_id BIGINT,
    amount DECIMAL(10,2),
    region STRING
) USING DELTA
LOCATION 's3://bucket/sales'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);
```

### 2. CREATE OR REPLACE TABLE

**Syntax:**
```sql
CREATE OR REPLACE TABLE table_name
[(column_name data_type [COMMENT col_comment] [, ...])]
[USING DELTA]
[LOCATION 'path']
```

**Example:**
```sql
CREATE OR REPLACE TABLE customers (
    customer_id BIGINT,
    name STRING,
    email STRING,
    created_date DATE
) USING DELTA
LOCATION 's3://bucket/customers';
```

### 3. DROP TABLE

**Syntax:**
```sql
DROP TABLE [IF EXISTS] table_name
```

**Examples:**
```sql
-- Basic drop
DROP TABLE old_events;

-- Safe drop with existence check
DROP TABLE IF EXISTS temp_data;
```

### 4. ALTER TABLE

#### 4.1 ADD COLUMN
```sql
ALTER TABLE table_name ADD COLUMN column_name data_type [COMMENT 'comment']
```

#### 4.2 RENAME COLUMN
```sql
ALTER TABLE table_name RENAME COLUMN old_name TO new_name
```

#### 4.3 DROP COLUMN
```sql
ALTER TABLE table_name DROP COLUMN column_name
```

#### 4.4 CHANGE COLUMN TYPE
```sql
ALTER TABLE table_name CHANGE COLUMN column_name new_data_type
```

#### 4.5 SET TBLPROPERTIES
```sql
ALTER TABLE table_name SET TBLPROPERTIES (
    'property_name' = 'property_value'
)
```

**Examples:**
```sql
-- Add new column
ALTER TABLE events ADD COLUMN device_type STRING COMMENT 'User device type';

-- Rename column
ALTER TABLE events RENAME COLUMN user_id TO customer_id;

-- Drop column
ALTER TABLE events DROP COLUMN old_device_info;

-- Change column type
ALTER TABLE events CHANGE COLUMN event_time TIMESTAMP_NTZ;

-- Set table properties
ALTER TABLE events SET TBLPROPERTIES (
    'delta.logRetentionDuration' = 'interval 30 days',
    'delta.deletedFileRetentionDuration' = 'interval 7 days'
);
```

## Data Manipulation Commands

### 5. INSERT

**Syntax:**
```sql
INSERT INTO table_name [(column1, column2, ...)]
VALUES (value1, value2, ...), ...

-- Or from query
INSERT INTO table_name
SELECT ...
```

**Examples:**
```sql
-- Direct values
INSERT INTO events (id, event_time, event_name, user_id)
VALUES (1, '2024-01-01 10:00:00', 'login', 1001);

-- From query
INSERT INTO daily_events
SELECT 
    id,
    event_time,
    event_name,
    user_id
FROM raw_events
WHERE event_date = CURRENT_DATE();
```

### 6. UPDATE

**Syntax:**
```sql
UPDATE table_name
SET column1 = value1 [, column2 = value2 ...]
[WHERE condition]
```

**Examples:**
```sql
-- Simple update
UPDATE customers
SET email = 'new@email.com'
WHERE customer_id = 1001;

-- Conditional update with multiple columns
UPDATE sales
SET 
    amount = amount * 1.1,
    status = 'UPDATED'
WHERE region = 'North America'
AND sale_date >= '2024-01-01';
```

### 7. DELETE

**Syntax:**
```sql
DELETE FROM table_name
[WHERE condition]
```

**Examples:**
```sql
-- Delete specific records
DELETE FROM events
WHERE event_time < '2024-01-01';

-- Delete all records (truncate equivalent)
DELETE FROM temp_table;
```

### 8. MERGE (Upsert)

**Syntax:**
```sql
MERGE INTO target_table
USING source_table
ON merge_condition
WHEN MATCHED [AND condition] THEN UPDATE SET ...
WHEN MATCHED [AND condition] THEN DELETE
WHEN NOT MATCHED [AND condition] THEN INSERT ...
```

**Examples:**
```sql
-- Basic merge (upsert)
MERGE INTO customers AS target
USING new_customers AS source
ON target.customer_id = source.customer_id
WHEN MATCHED THEN
    UPDATE SET 
        target.name = source.name,
        target.email = source.email,
        target.updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
    INSERT (customer_id, name, email, created_at)
    VALUES (source.customer_id, source.name, source.email, CURRENT_TIMESTAMP());

-- Merge with delete condition
MERGE INTO inventory AS target
USING inventory_updates AS source
ON target.product_id = source.product_id
WHEN MATCHED AND source.quantity = 0 THEN DELETE
WHEN MATCHED THEN
    UPDATE SET 
        target.quantity = source.quantity,
        target.updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
    INSERT (product_id, product_name, quantity, created_at)
    VALUES (source.product_id, source.product_name, source.quantity, CURRENT_TIMESTAMP());
```

## Table Maintenance Commands

### 9. VACUUM

**Syntax:**
```sql
VACUUM table_name [RETAIN number HOURS | DRY RUN]
```

**Examples:**
```sql
-- Default vacuum (7 days retention)
VACUUM events;

-- Custom retention period
VACUUM events RETAIN 24 HOURS;

-- Dry run to see what would be deleted
VACUUM events DRY RUN;
```

### 10. OPTIMIZE

**Syntax:**
```sql
OPTIMIZE table_name [WHERE predicate]
[ZORDER BY (column1, column2, ...)]
```

**Examples:**
```sql
-- Full table optimization
OPTIMIZE events;

-- Partition-wise optimization
OPTIMIZE events WHERE event_date >= '2024-01-01';

-- With Z-ordering
OPTIMIZE events
ZORDER BY (user_id, event_time);
```

### 11. DESCRIBE DETAIL

**Syntax:**
```sql
DESCRIBE DETAIL table_name
```

**Example:**
```sql
DESCRIBE DETAIL events;
```

### 12. DESCRIBE HISTORY

**Syntax:**
```sql
DESCRIBE HISTORY table_name
[LIMIT n]
```

**Examples:**
```sql
-- Full history
DESCRIBE HISTORY events;

-- Limited history
DESCRIBE HISTORY events LIMIT 10;
```

## Time Travel Commands

### 13. Time Travel Queries

**Syntax:**
```sql
SELECT * FROM table_name TIMESTAMP AS OF timestamp_expression
SELECT * FROM table_name VERSION AS OF version
```

**Examples:**
```sql
-- Query by timestamp
SELECT * FROM events TIMESTAMP AS OF '2024-01-01 10:00:00';

-- Query by version
SELECT * FROM events VERSION AS OF 5;

-- Using subqueries for dynamic time travel
SELECT * FROM events TIMESTAMP AS OF (
    SELECT MAX(event_time) - INTERVAL 1 HOUR 
    FROM events
);
```

### 14. RESTORE TABLE

**Syntax:**
```sql
RESTORE TABLE table_name TO TIMESTAMP AS OF timestamp_expression
RESTORE TABLE table_name TO VERSION AS OF version
```

**Examples:**
```sql
-- Restore to specific timestamp
RESTORE TABLE events TO TIMESTAMP AS OF '2024-01-01 10:00:00';

-- Restore to specific version
RESTORE TABLE events TO VERSION AS OF 10;
```

## Advanced Object Commands

### 15. CLONE TABLE

**Syntax:**
```sql
CREATE TABLE clone_name [SHALLOW | DEEP] CLONE source_table
[LOCATION 'path']
```

**Examples:**
```sql
-- Shallow clone (metadata only)
CREATE TABLE events_staging SHALLOW CLONE events;

-- Deep clone (data + metadata)
CREATE TABLE events_backup DEEP CLONE events
LOCATION 's3://bucket/backups/events';
```

### 16. CONVERT TO DELTA

**Syntax:**
```sql
CONVERT TO DELTA table_name
[NO STATISTICS]
```

**Example:**
```sql
-- Convert Parquet table to Delta
CONVERT TO DELTA parquet.`s3://bucket/parquet_data`;
```

## Utility Commands

### 17. SHOW Commands

```sql
-- Show tables
SHOW TABLES [IN database_name] [LIKE 'pattern'];

-- Show columns
SHOW COLUMNS IN table_name;

-- Show partitions
SHOW PARTITIONS table_name;

-- Show table properties
SHOW TBLPROPERTIES table_name;
```

### 18. EXPLAIN

**Syntax:**
```sql
EXPLAIN [EXTENDED | CODEGEN | COST | FORMATTED] statement
```

**Examples:**
```sql
-- Basic explain
EXPLAIN SELECT * FROM events WHERE user_id = 1001;

-- Extended explain
EXPLAIN EXTENDED 
MERGE INTO customers USING updates ON customers.id = updates.id
WHEN MATCHED THEN UPDATE SET *;
```

## Best Practices

### 1. Schema Evolution
```sql
-- Use schema evolution for safe column addition
ALTER TABLE events ADD COLUMN new_feature_flag BOOLEAN;

-- Use data type evolution carefully
ALTER TABLE events CHANGE COLUMN user_id user_id STRING;
```

### 2. Partitioning Strategy
```sql
-- Create partitioned table
CREATE TABLE events_partitioned (
    id BIGINT,
    event_time TIMESTAMP,
    event_name STRING
) USING DELTA
PARTITIONED BY (date_trunc('day', event_time))
LOCATION 's3://bucket/events_partitioned';
```

### 3. Z-Ordering for Performance
```sql
-- Apply Z-ordering during optimization
OPTIMIZE events
ZORDER BY (user_id, event_date);
```

### 4. Retention Policies
```sql
-- Set appropriate retention policies
ALTER TABLE events SET TBLPROPERTIES (
    'delta.logRetentionDuration' = 'interval 30 days',
    'delta.deletedFileRetentionDuration' = 'interval 7 days'
);
```

## Error Handling and Validation

### Common Issues and Solutions

1. **Schema Mismatch**
```sql
-- Use DESCRIBE to check schema
DESCRIBE DETAIL events;

-- Handle schema evolution gracefully
SET spark.databricks.delta.schema.autoMerge.enabled = true;
```

2. **Concurrency Conflicts**
```sql
-- Use optimistic concurrency control
SET spark.databricks.delta.retryDuration.enabled = true;
```

3. **Data Quality Enforcement**
```sql
-- Add constraints
ALTER TABLE events ADD CONSTRAINT valid_timestamp 
CHECK (event_time > '2020-01-01');
```

This comprehensive guide covers the essential Delta Lake object commands for effective table management and data operations.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Delta Lake Commands in Different APIs/Delta Lake Commands in Python API with Spark|Delta Lake Commands in Python API with Spark]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Important TBLProperties/Table Utility Commands|Delta Lake Table Utility Commands]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Important TBLProperties/Table Utility Essential Commands|Delta Table Utility Guide]]

# Delta Lake Table Utility Commands Comprehensive Guide

## Overview
Delta Lake provides extensive utility commands for table maintenance, inspection, and management. These commands help optimize performance, ensure data quality, and simplify operations.

## Table Inspection & Metadata Commands

### 1. DESCRIBE Commands

**Describe Table Structure:**
```sql
-- Basic table description
DESCRIBE TABLE events;

-- Extended information with detailed properties
DESCRIBE TABLE EXTENDED events;

-- Table format and storage details
DESCRIBE DETAIL events;

-- Format-specific description
DESCRIBE FORMATTED events;
```

**DESCRIBE TABLE Output:**
```
+-------------+-----------+-------+
| col_name    | data_type | comment |
+-------------+-----------+-------+
| id          | bigint    | null  |
| event_time  | timestamp | null  |
| event_name  | string    | null  |
| user_id     | bigint    | null  |
+-------------+-----------+-------+
```

**DESCRIBE EXTENDED Output:**
```
+----------------------+-----------------------------------+
| col_name             | data_type                        |
+----------------------+-----------------------------------+
| # Detailed Table Information |                              |
| Database:            | default                          |
| Table:               | events                           |
| Owner:               | root                             |
| Created Time:        | 2024-01-15 10:00:00              |
| Last Access:         | 2024-01-20 14:30:00              |
| Location:            | s3://bucket/events               |
| Table Properties:    | [delta.autoOptimize=true]        |
+----------------------+-----------------------------------+
```

**DESCRIBE DETAIL Output:**
```
+-----------------+-----------------------------------+
| detail_type     | detail_value                      |
+-----------------+-----------------------------------+
| format          | delta                             |
| location        | s3://bucket/events                |
| numFiles        | 1250                              |
| sizeBytes       | 157286400                         |
| partitionColumns| ["partition_date"]               |
| minReaderVersion| 1                                 |
| minWriterVersion| 2                                 |
+-----------------+-----------------------------------+
```

### 2. SHOW Commands

**Show Tables:**
```sql
-- Show all tables
SHOW TABLES;

-- Show tables in specific database
SHOW TABLES IN sales_db;

-- Filter tables with pattern
SHOW TABLES LIKE 'event%';

-- Show tables with extended info
SHOW TABLES FROM default;
```

**Show Columns:**
```sql
-- Show table columns
SHOW COLUMNS IN events;

-- Show columns with extended info
SHOW COLUMNS IN events FROM sales_db;
```

**Show Partitions:**
```sql
-- Show all partitions
SHOW PARTITIONS events;

-- Show partitions with filter
SHOW PARTITIONS events WHERE partition_date >= '2024-01-01';
```

**Show Table Properties:**
```sql
-- Show all table properties
SHOW TBLPROPERTIES events;

-- Show specific property
SHOW TBLPROPERTIES events ('delta.autoOptimize.optimizeWrite');
```

### 3. HISTORY - Table Version History

**Describe History:**
```sql
-- Show full operation history
DESCRIBE HISTORY events;

-- Limit history entries
DESCRIBE HISTORY events LIMIT 10;

-- Filter by operation type
DESCRIBE HISTORY events 
WHERE operation IN ('UPDATE', 'DELETE', 'MERGE');

-- Show specific version details
DESCRIBE HISTORY events VERSION AS OF 5;
```

**Example History Output:**
```
+-------+---------------------+---------+-----------+--------------------+----------------+
| version| timestamp          | userId  | operation | operationParameters | notebookId     |
+-------+---------------------+---------+-----------+--------------------+----------------+
| 5     | 2024-01-15 10:30:00| user123 | MERGE     | {predicate: ...}   | notebook-123   |
| 4     | 2024-01-14 09:15:00| user456 | OPTIMIZE  | {zOrderBy: ...}    | notebook-456   |
| 3     | 2024-01-13 14:20:00| user789 | DELETE    | {predicate: ...}   | notebook-789   |
| 2     | 2024-01-12 11:45:00| user123 | UPDATE    | {predicate: ...}   | notebook-123   |
| 1     | 2024-01-11 08:30:00| user456 | CREATE    | {isManaged: false} | notebook-456   |
+-------+---------------------+---------+-----------+--------------------+----------------+
```

**History Analysis Queries:**
```sql
-- Find recent modifications
SELECT 
  version,
  timestamp,
  operation,
  operationParameters
FROM (DESCRIBE HISTORY events)
WHERE timestamp > current_date() - INTERVAL 7 days
ORDER BY timestamp DESC;

-- Count operations by type
SELECT 
  operation,
  COUNT(*) as operation_count
FROM (DESCRIBE HISTORY events)
GROUP BY operation
ORDER BY operation_count DESC;
```

### 4. TIMESTAMP - Time Travel Operations

**Time Travel Queries:**
```sql
-- Query by specific timestamp
SELECT * FROM events TIMESTAMP AS OF '2024-01-15 10:00:00';

-- Query by relative time
SELECT * FROM events TIMESTAMP AS OF date_sub(current_date(), 7);

-- Query using version and timestamp together
SELECT * FROM events 
TIMESTAMP AS OF '2024-01-15' 
VERSION AS OF 5;

-- Complex time travel with subqueries
SELECT * FROM events 
TIMESTAMP AS OF (
  SELECT max(event_time) - INTERVAL 1 HOUR 
  FROM events 
  WHERE event_date = current_date()
);
```

**Timestamp Format Examples:**
```sql
-- Various timestamp formats
SELECT * FROM events TIMESTAMP AS OF '2024-01-15';
SELECT * FROM events TIMESTAMP AS OF '2024-01-15 14:30:00';
SELECT * FROM events TIMESTAMP AS OF '2024-01-15T14:30:00Z';
SELECT * FROM events TIMESTAMP AS OF cast('2024-01-15 14:30:00' as timestamp);
```

### 5. RESTORE - Table Recovery

**Restore Syntax:**
```sql
RESTORE TABLE table_name TO TIMESTAMP AS OF timestamp_expression
RESTORE TABLE table_name TO VERSION AS OF version
```

**Restore Examples:**
```sql
-- Restore to specific timestamp
RESTORE TABLE events TO TIMESTAMP AS OF '2024-01-15 10:00:00';

-- Restore to specific version
RESTORE TABLE events TO VERSION AS OF 10;

-- Restore after accidental deletion
RESTORE TABLE events TO TIMESTAMP AS OF date_sub(current_timestamp(), 1);

-- Verify restore operation
DESCRIBE HISTORY events 
WHERE operation = 'RESTORE' 
ORDER BY timestamp DESC 
LIMIT 1;
```

**Restore Scenarios:**
```sql
-- Scenario 1: Accidental data deletion recovery
-- Check when deletion happened
DESCRIBE HISTORY events 
WHERE operation = 'DELETE' 
ORDER BY timestamp DESC 
LIMIT 1;

-- Restore to before deletion
RESTORE TABLE events TO TIMESTAMP AS OF '2024-01-15 09:00:00';

-- Scenario 2: Schema change rollback
-- Restore to previous schema version
RESTORE TABLE events TO VERSION AS OF 5;

-- Verify schema
DESCRIBE TABLE events;
```

### 6. VACUUM - File Cleanup

**Syntax:**
```sql
VACUUM [TABLE] table_name 
[RETAIN number HOURS] 
[DRY RUN]
```

**Examples:**
```sql
-- Default vacuum (7 days retention)
VACUUM events;

-- Custom retention period
VACUUM events RETAIN 24 HOURS;

-- Dry run to see what would be deleted
VACUUM events RETAIN 168 HOURS DRY RUN;

-- Force vacuum (careful - can break time travel)
VACUUM events RETAIN 0 HOURS;

-- Vacuum with fully qualified table name
VACUUM sales_db.events RETAIN 48 HOURS;
```

**Vacuum Monitoring:**
```sql
-- Check vacuum results in history
DESCRIBE HISTORY events 
WHERE operation = 'VACUUM' 
ORDER BY timestamp DESC 
LIMIT 5;

-- Compare file counts before and after vacuum
SELECT 
  (SELECT count(*) FROM delta.`s3://bucket/events#files`) as current_files,
  (SELECT count(*) FROM delta.`s3://bucket/events#files@v5`) as previous_files;
```

**Vacuum Safety Checks:**
```sql
-- Always dry run first
VACUUM events RETAIN 24 HOURS DRY RUN;

-- Check current retention settings
SHOW TBLPROPERTIES events ('delta.deletedFileRetentionDuration');

-- Verify time travel range
SELECT 
  min(timestamp) as earliest_time,
  max(timestamp) as latest_time
FROM (DESCRIBE HISTORY events);
```

### 7. CLONING - Table Copy Operations

**Clone Syntax:**
```sql
CREATE TABLE clone_name [SHALLOW | DEEP] CLONE source_table
[LOCATION 'path']
[VERSION AS OF version]
[TIMESTAMP AS OF timestamp_expression]
```

**Clone Examples:**
```sql
-- Shallow clone (metadata only)
CREATE TABLE events_staging SHALLOW CLONE events;

-- Deep clone (data + metadata)
CREATE TABLE events_backup DEEP CLONE events
LOCATION 's3://backup/events';

-- Clone specific version
CREATE TABLE events_v5 DEEP CLONE events
VERSION AS OF 5;

-- Clone with timestamp
CREATE TABLE events_snapshot DEEP CLONE events
TIMESTAMP AS OF '2024-01-15 10:00:00';

-- Clone to different location
CREATE TABLE events_dev DEEP CLONE events
LOCATION 's3://dev-bucket/events';
```

**Clone Management:**
```sql
-- Check clone properties
DESCRIBE DETAIL events_staging;
DESCRIBE EXTENDED events_backup;

-- Verify clone source
SHOW TBLPROPERTIES events_staging ('delta.clone.source');
SHOW TBLPROPERTIES events_staging ('delta.clone.sourceVersion');

-- Compare clone with source
SELECT 
  'source' as type,
  count(*) as file_count,
  sum(size) as total_size
FROM delta.`s3://bucket/events#files`
UNION ALL
SELECT 
  'shallow_clone' as type,
  count(*) as file_count,
  sum(size) as total_size
FROM delta.`s3://backup/events#files`;
```

**Clone Use Cases:**
```sql
-- Use case 1: Development/testing
CREATE TABLE events_dev SHALLOW CLONE events;
-- Safe experimentation on clone

-- Use case 2: Backup before major changes
CREATE TABLE events_pre_update DEEP CLONE events
LOCATION 's3://backup/events_pre_update';

-- Use case 3: Historical analysis
CREATE TABLE events_jan_snapshot DEEP CLONE events
TIMESTAMP AS OF '2024-01-31 23:59:59';
```

## Table Maintenance Commands

### 8. OPTIMIZE - File Compaction

**Syntax:**
```sql
OPTIMIZE table_name
[WHERE predicate]
[ZORDER BY (column1, column2, ...)]
```

**Examples:**
```sql
-- Full table optimization
OPTIMIZE events;

-- Partition-wise optimization
OPTIMIZE events WHERE partition_date >= '2024-01-01';

-- With Z-ordering for better performance
OPTIMIZE events 
ZORDER BY (user_id, event_time);

-- Combined partition filter and Z-ordering
OPTIMIZE events 
WHERE partition_date = '2024-01-15'
ZORDER BY (event_type, user_id);
```

**Monitor Optimization:**
```sql
-- Check optimization metrics
DESCRIBE HISTORY events 
WHERE operation = 'OPTIMIZE' 
LIMIT 5;

-- View file statistics
SELECT 
  partition_date,
  count(*) as file_count,
  sum(size_bytes) as total_size
FROM delta.`s3://bucket/events#files`
GROUP BY partition_date;
```

### 9. ANALYZE - Statistics Collection

**Syntax:**
```sql
ANALYZE TABLE table_name COMPUTE STATISTICS [FOR COLUMNS col1, col2, ...]
```

**Examples:**
```sql
-- Compute basic table statistics
ANALYZE TABLE events COMPUTE STATISTICS;

-- Compute column statistics for query optimization
ANALYZE TABLE events COMPUTE STATISTICS FOR COLUMNS user_id, event_type;

-- Compute statistics for specific partitions
ANALYZE TABLE events PARTITION (partition_date='2024-01-01') 
COMPUTE STATISTICS FOR COLUMNS user_id;
```

**View Statistics:**
```sql
-- Show table statistics
DESCRIBE EXTENDED events;

-- Query statistics directly
SELECT * FROM delta.`s3://bucket/events#stats`;
```

## Data Quality & Validation Commands

### 10. Data Validation Utilities

**Check Data Files:**
```sql
-- List all data files
SELECT * FROM delta.`s3://bucket/events#files`;

-- Check file statistics
SELECT 
  path,
  size,
  modificationTime,
  partitionValues
FROM delta.`s3://bucket/events#files`
WHERE size > 1000000;  -- Files larger than 1MB
```

**Validate Data Integrity:**
```python
# Python example for data validation
from delta.tables import DeltaTable

def validate_table_integrity(table_path):
    delta_table = DeltaTable.forPath(spark, table_path)
    
    # Check for corrupted files
    files = spark.sql(f"""
        SELECT * FROM delta.`{table_path}#files`
    """)
    
    print(f"Total files: {files.count()}")
    print(f"Total size: {files.agg({'size': 'sum'}).collect()[0][0]} bytes")
    
    # Verify we can read the data
    data = spark.read.format("delta").load(table_path)
    print(f"Record count: {data.count()}")
    
    return files.count() > 0 and data.count() > 0
```

## Performance & Monitoring Commands

### 11. Performance Analysis

**Check Table Metrics:**
```sql
-- Get table size and file information
DESCRIBE DETAIL events;

-- Check partition statistics
SELECT 
  partition_date,
  count(*) as file_count,
  avg(size) as avg_file_size,
  sum(size) as total_size
FROM delta.`s3://bucket/events#files`
GROUP BY partition_date
ORDER BY partition_date;
```

## Utility Procedures

### 12. System Procedures

**Generate DDL:**
```sql
-- Get table creation DDL (in Databricks)
SHOW CREATE TABLE events;

-- Alternative approach
CALL delta.get_ddl('default.events');
```

**Table Conversion:**
```sql
-- Convert Parquet to Delta
CONVERT TO DELTA parquet.`s3://bucket/parquet_events`;

-- Convert with custom schema
CONVERT TO DELTA parquet.`s3://bucket/parquet_events` 
(id BIGINT, event_time TIMESTAMP, event_name STRING);
```

## Best Practices Summary

### Command Usage Patterns

1. **Regular Maintenance Schedule:**
```sql
-- Weekly optimization
OPTIMIZE events ZORDER BY (user_id, event_time);

-- Monthly vacuum (keep 30 days for time travel)
VACUUM events RETAIN 720 HOURS;

-- Daily statistics collection
ANALYZE TABLE events COMPUTE STATISTICS FOR COLUMNS user_id, event_type;
```

2. **Safe Operations:**
```sql
-- Always check before destructive operations
DESCRIBE HISTORY events LIMIT 10;
VACUUM events RETAIN 168 HOURS DRY RUN;

-- Use clones for testing
CREATE TABLE test_changes SHALLOW CLONE production_table;
```

3. **Monitoring:**
```sql
-- Regular health checks
DESCRIBE DETAIL important_table;
DESCRIBE HISTORY important_table 
WHERE timestamp > current_date() - INTERVAL 1 DAY;
```

This comprehensive guide covers all essential Delta Lake table utility commands including the newly added DESCRIBE, DESCRIBE EXTENDED, RESTORE, TIMESTAMP, HISTORY, VACUUM, and CLONING commands for effective table management and maintenance.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Important TBLProperties/Table Utility Essential Commands|Delta Table Utility Guide]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Delta Lake Commands in Different APIs/Delta Lake Commands in SQL API|Delta Lake Object Commands (SQL API)]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Questions/How Versioning Works in Delta Lake|How Versioning Works in Delta Lake]]

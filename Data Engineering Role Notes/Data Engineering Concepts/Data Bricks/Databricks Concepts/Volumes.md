# Comprehensive Guide to Volumes in Databricks Unity Catalog

## Concept Overview

### What Are Volumes in Databricks?

Volumes are Unity Catalog objects that provide governance, access control, and organization for **non-tabular datasets** stored in cloud object storage. While tables govern tabular data (rows and columns), volumes govern files of any format—structured (CSV, JSON, Parquet), semi-structured (XML), or unstructured (images, PDFs, audio, video, ML models, libraries).

Volumes live alongside tables, views, and functions within a Unity Catalog schema, forming the third level of the three‑level namespace (`catalog.schema.volume`).

### Why They Exist: The Problem They Solve

Before volumes, Databricks users faced several challenges with non‑tabular data:

| Problem | Legacy Approach | How Volumes Solve It |
|---------|----------------|----------------------|
| **No governance** | DBFS root (`/FileStore`, `/user/hive/warehouse`) had coarse, workspace‑level permissions – any workspace user could read/write | Unity Catalog provides fine‑grained ACLs (`READ VOLUME`, `WRITE VOLUME`, `EXECUTE VOLUME`) |
| **No cross‑workspace access** | Workspace files are isolated to a single workspace | Volumes are accessible from any workspace connected to the same Unity Catalog metastore |
| **No audit trail** | Direct cloud URIs bypass Databricks logging | All access through volumes is logged in Unity Catalog audit records |
| **No separation of concerns** | Tables and raw files mixed in same storage | Volumes separate file storage from table storage, with independent lifecycles |
| **Legacy mount points** | `dbutils.fs.mount` required managing cloud credentials and was deprecated | Volumes abstract away cloud storage details; credentials are managed once via storage credentials and external locations |

Databricks **recommends using volumes for all non‑tabular data** in new projects.

### How Volumes Fit into Unity Catalog Architecture

```
Unity Catalog Metastore
   └── Catalog (e.g., "sales", "ml_artifacts")
        └── Schema (e.g., "bronze", "models")
             ├── Tables (tabular data)
             ├── Views
             ├── Functions
             └── Volumes (file storage) ← managed or external
```

Volumes rely on underlying Unity Catalog objects:
- **Storage credentials** – cloud IAM role or managed identity (set up once by admin)
- **External locations** – registered cloud storage paths with a storage credential (optional for managed volumes)
- **Managed storage** – for managed volumes, Databricks automatically creates storage under the schema’s managed location (no user configuration needed)

---

## Types of Volumes

### Managed Volumes

| Attribute | Description |
|-----------|-------------|
| **Definition** | A volume created inside the Unity Catalog‑managed storage location of the containing schema. You do **not** provide a `LOCATION` path. |
| **Storage location** | Automatically placed under the schema’s managed root (e.g., `/managed/schema/volume/`). You cannot see or change this path directly. |
| **Lifecycle** | Unity Catalog manages data layout and deletion. When you drop a managed volume, all files are deleted after a **7‑day retention** period. |
| **Ownership** | The creator becomes the owner. Ownership can be transferred via `ALTER VOLUME ... OWNER TO`. |
| **Governance** | All access must go through Unity Catalog. Direct cloud URIs are not supported (or require additional configuration). |
| **Typical use case** | Databricks‑only workloads where simplicity is key. Best for ML experiments, temporary staging, and data engineering within Databricks. |

### External Volumes

| Attribute | Description |
|-----------|-------------|
| **Definition** | A volume registered against an **existing directory** in an external location (cloud storage path). You provide a `LOCATION` when creating the volume. |
| **Storage location** | Any existing cloud storage path (e.g., `s3://my-bucket/data/landing`, `abfss://container@account.dfs.core.windows.net/folder/`). |
| **Lifecycle** | When you drop an external volume, the **data remains** in cloud storage. Only the Unity Catalog metadata is removed. |
| **Ownership** | Same as managed – owner can be changed. |
| **Governance** | Unity Catalog governs access **within Databricks**. External tools (e.g., AWS CLI, Azure Storage Explorer) can bypass UC governance unless you configure cloud‑native policies. |
| **Typical use case** | Mixed environments where files are produced or consumed by systems outside Databricks (e.g., IoT data landing, legacy ETL outputs, shared ML models). |

### Key Differences at a Glance

| Feature | Managed Volume | External Volume |
|---------|---------------|-----------------|
| Storage location | Auto‑created inside schema’s managed storage | User‑provided existing cloud path |
| Data lifecycle | Deleted with volume (7‑day retention) | Persists after volume deletion |
| Need external location object? | No | Yes (must reference an existing `EXTERNAL LOCATION`) |
| Access from outside Databricks | Not recommended (complex) | Yes – direct cloud URIs work (but bypass governance) |
| Setup complexity | Low | Medium (need storage credential + external location) |

---

## Path and Access Format

### Volume Path Structure

All files inside a volume are accessed using a consistent POSIX‑style path:

```
/Volumes/<catalog_name>/<schema_name>/<volume_name>/<optional_subdirectory>/<file_name>
```

**Examples:**
```
/Volumes/sales/bronze/landing/2024/transactions.csv
/Volumes/ml_artifacts/prod/models/xgboost_v2.pkl
/Volumes/my_catalog/default/raw_images/photo.jpg
```

**Important notes:**
- The path is **case‑insensitive** – Databricks normalizes identifiers to lowercase.
- The `dbfs:/` scheme is optional when using Apache Spark, so `dbfs:/Volumes/...` works identically.
- The directories `/Volumes`, `<catalog>`, `<schema>`, and `<volume>` are **read‑only and managed by Unity Catalog** – you cannot create or delete them with filesystem commands.

### Reserved Paths

The following paths are reserved and cannot be used for other purposes:
- `/Volumes`
- `dbfs:/Volumes`
- Typos like `/volumes`, `/Volume`, `/volume` (with or without `dbfs:/`) are also reserved to prevent accidental use.

**Common mistake:** Trying to use `/dbfs/Volumes/...` – this path is reserved but **does not work** for accessing volumes.

### How to Access Volumes from Different Interfaces

#### SQL (Databricks SQL Warehouse or Spark SQL)

```sql
-- Query a CSV file directly from a volume
SELECT * FROM csv.`/Volumes/my_catalog/my_schema/my_volume/data.csv`;

-- List files in a volume
LIST '/Volumes/my_catalog/my_schema/my_volume';

-- Use with COPY INTO for ingestion
COPY INTO my_catalog.bronze.my_table
FROM '/Volumes/my_catalog/my_schema/my_volume/raw_data'
FILEFORMAT = CSV;
```

#### PySpark

```python
# Read CSV
df = spark.read.format("csv") \
    .option("header", "true") \
    .load("/Volumes/my_catalog/my_schema/my_volume/data.csv")

# Write Parquet
df.write.format("parquet") \
    .mode("overwrite") \
    .save("/Volumes/my_catalog/my_schema/my_volume/output/")

# Both dbfs:/ prefix works
df2 = spark.read.json("dbfs:/Volumes/my_catalog/my_schema/my_volume/events.json")
```

#### Pandas (Python)

```python
import pandas as pd

df = pd.read_csv("/Volumes/my_catalog/my_schema/my_volume/data.csv")
df.to_parquet("/Volumes/my_catalog/my_schema/my_volume/output.parquet")
```

#### Databricks Utilities (`dbutils.fs`) and Magic Commands

```python
# List files
dbutils.fs.ls("/Volumes/my_catalog/my_schema/my_volume")

# Read file content
dbutils.fs.head("/Volumes/my_catalog/my_schema/my_volume/sample.txt")

# Copy file
dbutils.fs.cp("/Volumes/src/.../file.txt", "/Volumes/dst/.../file.txt")
```

```sql
-- %fs magic command (alias for dbutils.fs)
%fs ls /Volumes/my_catalog/my_schema/my_volume
```

```bash
# %sh magic command (bash) – limited support, prefer dbutils.fs
%sh ls /Volumes/my_catalog/my_schema/my_volume
```

### Differences vs DBFS Paths

| Aspect | DBFS Path | Volume Path |
|--------|-----------|-------------|
| Governance | Basic workspace‑level ACLs | Fine‑grained UC permissions |
| Cross‑workspace | No | Yes |
| Support for distributed writes | Yes (but no governance) | Yes (with governance) |
| `dbutils.fs` on executors | Works | **Not supported** (driver only) |
| Mount points | Supported (deprecated) | Not needed |
| Recommended for new workloads | No | Yes |

### Compute Requirements

- **Databricks Runtime 13.3 LTS or above** is required to work with volumes.
- SQL warehouses (serverless or pro) fully support volumes.
- On DBR 12.2 LTS and below, operations against `/Volumes` paths may appear to work but actually write to **ephemeral cluster storage** – data will be lost when the cluster terminates.

---

## Core Operations with Syntax

### Create a Volume

#### Managed Volume (no location needed)

```sql
CREATE VOLUME IF NOT EXISTS my_catalog.my_schema.my_managed_volume
COMMENT 'This volume stores raw ingestion files';
```

**Prerequisites:** `CREATE VOLUME` permission on the schema, `USE CATALOG` on the catalog, `USE SCHEMA` on the schema.

#### External Volume (requires existing external location)

First, an admin must create a storage credential and external location:

```sql
-- Admin setup (once)
CREATE STORAGE CREDENTIAL my_cred
  COMMENT 'Access to my-bucket'
  AWS_ROLE = 'arn:aws:iam::123456789012:role/databricks-access-role';

CREATE EXTERNAL LOCATION my_ext_location
  URL 's3://my-bucket/landing/'
  WITH (STORAGE CREDENTIAL my_cred);
```

Then create the external volume:

```sql
CREATE EXTERNAL VOLUME my_catalog.my_schema.my_external_volume
  COMMENT 'Existing bucket for external data'
  LOCATION 's3://my-bucket/landing/raw/';
```

**Note:** The `LOCATION` must be a **directory** path, not a bucket root (unless you want the volume to own the entire bucket – not recommended).

### Drop a Volume

```sql
DROP VOLUME IF EXISTS my_catalog.my_schema.my_volume;
-- For external volume, files remain in cloud storage
-- For managed volume, files are deleted after 7 days
```

### Describe a Volume

```sql
DESCRIBE VOLUME my_catalog.my_schema.my_volume;
```

Returns: volume name, catalog, schema, type (MANAGED/EXTERNAL), location, comment, owner, created time.

### List Volumes

```sql
-- List volumes in current schema
SHOW VOLUMES IN my_catalog.my_schema;

-- Using pattern matching
SHOW VOLUMES IN my_catalog.my_schema LIKE 'raw_*';
```

**Limitation:** You **cannot** list volumes using `dbutils.fs.ls("/Volumes/my_catalog/my_schema")` – this path is reserved and not enumerable. Always use `SHOW VOLUMES` or the Catalog Explorer UI.

### Grant and Revoke Permissions

Volumes support three privileges:

| Privilege | Description |
|-----------|-------------|
| `READ VOLUME` | List and read files in the volume |
| `WRITE VOLUME` | Create, modify, and delete files (implies READ VOLUME) |
| `EXECUTE VOLUME` | Required for accessing files from UDFs or libraries stored in the volume (rare) |

**Examples:**

```sql
-- Grant read access to a user or group
GRANT READ VOLUME ON VOLUME my_catalog.my_schema.my_volume TO `user@example.com`;
GRANT WRITE VOLUME ON VOLUME my_catalog.my_schema.my_volume TO data_engineers;

-- Revoke permissions
REVOKE WRITE VOLUME ON VOLUME my_catalog.my_schema.my_volume FROM data_engineers;

-- View grants
SHOW GRANTS ON VOLUME my_catalog.my_schema.my_volume;
```

**Important:** In addition to volume permissions, users need `USE CATALOG` and `USE SCHEMA` on the parent objects to navigate to the volume.

### Mounting Relevance

**Volumes eliminate the need for mount points.** Legacy workflows using `dbutils.fs.mount()` should be migrated to volumes or direct cloud URIs. Mounts are deprecated and offer no governance.

Migration path:
1. Identify all mount paths (`/mnt/...`)
2. Create an external volume pointing to the underlying cloud location
3. Update code to use `/Volumes/...` instead of `/mnt/...`

---

## Working with Files

### Supported File Operations

| Operation | Methods | Example |
|-----------|---------|---------|
| **Read** | Spark, Pandas, SQL, `dbutils.fs.head` | `spark.read.csv("/Volumes/...")` |
| **Write** | Spark, Pandas, Python `open()` | `df.write.parquet("/Volumes/...")` |
| **Copy** | `dbutils.fs.cp`, `%sh cp` (limited) | `dbutils.fs.cp(src, dst)` |
| **Move** | `dbutils.fs.mv` | `dbutils.fs.mv("/Volumes/a/f.txt", "/Volumes/b/f.txt")` |
| **Delete** | `dbutils.fs.rm`, `%sh rm` | `dbutils.fs.rm("/Volumes/.../file.txt", recurse=True)` |
| **Create directory** | `dbutils.fs.mkdirs`, `os.mkdir` | `dbutils.fs.mkdirs("/Volumes/.../newdir")` |
| **Upload (UI)** | Catalog Explorer | Drag and drop (max 5 GB) |
| **Upload (SDK)** | Databricks SDK for Python | No size limit (cloud max) |
| **Download** | UI, `dbutils.fs.head`, `GET` SQL command | `GET '/Volumes/.../file.txt' TO '/local/path/'` |

**Important limitations:**
- `dbutils.fs` commands (ls, cp, mv, rm) work **only on the driver**, not on executors. For distributed file operations, use Spark DataFrame readers/writers.
- `%sh mv` is **not supported** for moving files between volumes; use `dbutils.fs.mv` instead.
- You cannot access volumes from **RDDs** (Resilient Distributed Datasets).
- Unity Catalog UDFs do not support accessing volume file paths (in DBR < 14.3 LTS for shared access mode).

### Practical Examples

#### Reading CSV, JSON, Parquet from a Volume

**PySpark:**
```python
# CSV
df_csv = spark.read.option("header", True).csv("/Volumes/sales/bronze/landing/orders.csv")

# JSON (multi-line)
df_json = spark.read.option("multiline", True).json("/Volumes/sales/bronze/landing/events.json")

# Parquet (partitioned directory)
df_parquet = spark.read.parquet("/Volumes/sales/silver/enriched/")
```

**Pandas:**
```python
import pandas as pd
df = pd.read_csv("/Volumes/sales/bronze/landing/orders.csv")
```

**SQL (Databricks SQL):**
```sql
SELECT * FROM csv.`/Volumes/sales/bronze/landing/orders.csv`;
SELECT * FROM json.`/Volumes/sales/bronze/landing/events.json`;
SELECT * FROM parquet.`/Volumes/sales/silver/enriched/`;
```

#### Writing Data to a Volume

**PySpark:**
```python
# Write CSV (requires coalesce/repartition for single file)
df.coalesce(1).write.mode("overwrite").csv("/Volumes/sales/bronze/output/", header=True)

# Write Parquet (recommended format)
df.write.mode("append").parquet("/Volumes/sales/bronze/staging/")

# Write JSON
df.write.mode("overwrite").json("/Volumes/sales/bronze/landing/")
```

**Pandas:**
```python
df.to_csv("/Volumes/sales/bronze/output/clean_data.csv", index=False)
df.to_parquet("/Volumes/sales/bronze/output/clean_data.parquet")
```

**Python built‑in file operations:**
```python
with open("/Volumes/my_catalog/my_schema/my_volume/output.txt", "w") as f:
    f.write("Hello, volume!")
```

#### File Management with `dbutils.fs`

```python
# List files
files = dbutils.fs.ls("/Volumes/my_catalog/my_schema/my_volume/input/")
for f in files:
    print(f.path, f.size)

# Copy file
dbutils.fs.cp("/Volumes/src/.../file.parquet", "/Volumes/dst/.../file.parquet")

# Move (rename)
dbutils.fs.mv("/Volumes/.../old_name.csv", "/Volumes/.../new_name.csv")

# Delete directory (recursive)
dbutils.fs.rm("/Volumes/.../temp/", recurse=True)

# Check if path exists
dbutils.fs.ls("/Volumes/.../")  # will raise exception if not exists
```

#### Uploading Large Files (>5 GB)

The Databricks UI has a 5 GB limit. For larger files, use the Databricks SDK for Python:

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import VolumeFileUploadRequest

w = WorkspaceClient()
with open("/path/to/large_file.zip", "rb") as f:
    w.volumes.upload(
        volume_path="/Volumes/my_catalog/my_schema/my_volume/large_file.zip",
        data=f
    )
```

---

## When to Use Volumes (Real Scenarios)

| Scenario | Why Volumes? | Example |
|----------|--------------|---------|
| **ML artifact storage** | Store model files (PKL, joblib, ONNX), feature stores, experiment outputs with versioning and access control | `/Volumes/ml/prod/models/xgboost_v2.pkl` |
| **Raw file ingestion** | Landing zone for Auto Loader or `COPY INTO` from external sources (IoT, logs, third-party exports) | `/Volumes/sales/bronze/landing/2024/` with Auto Loader monitoring |
| **Unstructured data** | Images, PDFs, audio, video for AI/ML pipelines (e.g., document parsing, image classification) | `/Volumes/legal/documents/contracts/` with `ai_parse_document` |
| **Secure file sharing** | Share files across users, teams, and workspaces with fine‑grained permissions (instead of DBFS or email) | Grant `READ VOLUME` to `analysts_group` on `/Volumes/finance/reports/` |
| **Library and init script storage** | Store JARs, Python wheels, and cluster init scripts in a governed location | `/Volumes/eng/libs/my_spark_udf.jar` |
| **Checkpoint storage** | DataFrame checkpoints and Structured Streaming checkpoints (DBR 18.1+) | `spark.conf.set("spark.checkpoint.dir", "/Volumes/.../checkpoints/")` |
| **External system integration** | When files must be written by Databricks and read by external tools (use external volumes) | Databricks writes aggregates to `/Volumes/.../output/` and a separate Airflow job reads them |

---

## Advantages

| Advantage | Explanation |
|-----------|-------------|
| **Fine‑grained governance** | Row‑level? No (volumes are file‑level). But you get `READ`, `WRITE`, `EXECUTE` permissions at the volume level, plus audit logs for every access. |
| **Separation of storage vs tables** | Tables remain ACID‑compliant Delta format; volumes hold raw files. Each has independent lifecycle and access controls. |
| **Cross‑workspace accessibility** | Any workspace connected to the same Unity Catalog metastore can access volumes. No more "workspace A can't see workspace B's files." |
| **Secure sharing** | Grant `READ VOLUME` to external users or groups without sharing cloud credentials. |
| **POSIX‑style paths** | Works with Python `open()`, Pandas, and many ML frameworks that expect file system paths (unlike cloud URIs). |
| **No credential management** | For managed volumes – Databricks handles cloud access transparently. For external volumes – credentials are managed once at the external location level. |
| **Direct cloud access (external volumes)** | External tools can read/write the same underlying storage using native cloud URIs (but governance is then your responsibility). |
| **Audit logging** | All volume access via Databricks is logged. Compliance teams can track who read which file. |

---

## Disadvantages / Limitations

### Compared to Tables

| Limitation | Impact |
|------------|--------|
| **No schema enforcement** | Volumes accept any file format. You must validate schema in your code. |
| **No ACID transactions** | Concurrent writes to the same file can cause corruption. Use Delta tables for multi‑writer scenarios. |
| **No SQL query (directly)** | You can query files via `SELECT * FROM csv.\`/path\``, but this is not as optimized as Delta tables. |
| **No versioning / time travel** | Files are overwritten. For versioning, use Delta tables or implement your own file versioning scheme. |

### Technical Constraints

| Constraint | Details |
|------------|---------|
| **No distributed `dbutils.fs`** | `dbutils.fs` commands run only on the driver. For distributed file operations, use Spark DataFrames. |
| **No RDD access** | You cannot use `sc.textFile("/Volumes/...")` on RDDs. Use DataFrames or Datasets instead. |
| **UDF restrictions** | In DBR <14.3 LTS with shared access mode, Python/Scala UDFs cannot access volume paths. In dedicated access mode, Scala UDFs cannot (but Python UDFs can). |
| **No listing at catalog/schema level** | `dbutils.fs.ls("/Volumes/my_catalog/my_schema")` fails. Use `SHOW VOLUMES` instead. |
| **No `%sh mv` between volumes** | Use `dbutils.fs.mv`. |
| **Legacy `spark-submit` not supported** | If your job uses `spark-submit` with JARs stored in a volume, it fails. Use the `JAR` task type instead. |
| **Compute version requirement** | Databricks Runtime 13.3 LTS or above required. Older runtimes write to ephemeral storage instead of volumes. |
| **UI upload limit** | 5 GB via browser. Use SDK for larger files. |
| **No custom Hadoop FileSystem** | You cannot create a `new Path("dbfs:/Volumes/...")` object in Scala with custom Hadoop FS. |

### Performance Considerations

- **Small file problem:** Reading thousands of tiny files from a volume is inefficient – same as any cloud storage. Use Auto Loader with file notification mode, or coalesce files into larger batches (e.g., Parquet).
- **Latency:** Each file operation makes a cloud storage request. For high‑throughput workloads, prefer Delta tables or direct cloud URIs with optimized connectors.
- **FUSE limitations (DBR ≤14.2):** On clusters with shared access mode, FUSE (POSIX) access is only available on the driver, not executors. In dedicated access mode, Scala FUSE access is not supported at all.

---

## Best Practices

### Naming Conventions

| Object | Recommendation | Example |
|--------|----------------|---------|
| Volume name | Lowercase, underscores, descriptive | `raw_ingestion`, `ml_models_prod` |
| Subdirectories | Use date‑partitioning for time‑series data | `landing/year=2024/month=01/` |
| File names | Include timestamp or version | `orders_20250115.csv`, `model_v2.pkl` |

**Avoid:** spaces, special characters (except `_` and `-`), mixed case (normalized to lowercase anyway).

### Security Handling

1. **Principle of least privilege:** Grant `READ VOLUME` to consumers, `WRITE VOLUME` only to producers.
2. **Use groups, not individual users:** `GRANT WRITE VOLUME ON VOLUME ... TO data_engineers` instead of listing 50 email addresses.
3. **Separate volumes by sensitivity:** `finance/pii_volume` (restricted) vs `finance/anonymized_volume` (wider access).
4. **Enable audit logging:** Monitor `system.access.audit` table for volume access events.

### When to Choose Managed vs External Volume

| Scenario | Recommendation |
|----------|----------------|
| **Databricks‑only workloads** (ETL, ML training, notebooks) | **Managed volume** – simplest, no cloud setup. |
| **Files written by external systems** (IoT, legacy ETL, third‑party apps) | **External volume** – point it to the existing cloud path. |
| **Files need to be read by external systems** after Databricks processing | **External volume** – external tools can use cloud URIs. |
| **Temporary staging area** for short‑lived data | **Managed volume** – automatic cleanup after 7 days on drop. |
| **Long‑term archive** shared across Databricks and other platforms | **External volume** – data persists even if volume is dropped. |

### Integration with Medallion Architecture (Bronze/Silver/Gold)

Volumes fit naturally into the medallion pattern for **file‑based ingestion**:

```
External Source (JSON/CSV)
   │
   ▼
External Volume (Bronze Landing)
   /Volumes/sales/bronze/landing/raw_20250115.json
   │
   ├─── Auto Loader or COPY INTO
   ▼
Bronze Delta Table (managed table)
   sales.bronze.raw_events (Delta format, ACID)
   │
   ├─── Transformations
   ▼
Silver Delta Table
   sales.silver.cleaned_events
   │
   ├─── Aggregations
   ▼
Gold Delta Table
   sales.gold.daily_summary
```

**Example workflow using external volume for landing:**

```sql
-- External volume pointing to existing S3 landing path
CREATE EXTERNAL VOLUME sales.bronze.landing_volume
  LOCATION 's3://my-data-lake/raw-ingestion/sales/';

-- Auto Loader streaming read from volume
CREATE OR REFRESH STREAMING LIVE TABLE bronze_raw_events
AS SELECT * FROM cloud_files(
  "/Volumes/sales/bronze/landing_volume/",
  "json",
  map("cloudFiles.inferColumnTypes", "true")
);

-- Then transform to Silver Delta table
CREATE OR REFRESH LIVE TABLE silver_cleaned_events
AS SELECT
  event_id,
  TO_TIMESTAMP(event_time) AS event_timestamp,
  user_id,
  FROM bronze_raw_events
WHERE event_id IS NOT NULL;
```

**Real‑world example:** A CVE vulnerability pipeline used volumes to stage raw JSON files (300,000+ files) by first downloading to `/tmp`, filtering to relevant year (40,000 records), converting to a single Parquet file, and then uploading to a volume – reducing processing time from hours to minutes.

---

## Comparison Section

### Volumes vs Tables

| Aspect | Volumes | Tables (Delta) |
|--------|---------|----------------|
| **Data type** | Any file format (structured, semi‑structured, unstructured) | Tabular (rows and columns) |
| **Schema** | No schema enforcement | Schema enforced (evolvable) |
| **ACID transactions** | No – concurrent writes may corrupt files | Yes – full ACID |
| **Time travel / versioning** | No (unless you implement file versioning) | Yes – `VERSION AS OF` |
| **SQL query** | Via file‑reader functions (`csv.`, `json.`, `parquet.`) | Native – `SELECT * FROM table` |
| **Optimization** | No auto optimization (Z‑order, compaction) | Auto compaction, Z‑order, data skipping |
| **Use case** | File storage, ML artifacts, raw landing zones | Curated, queryable datasets |
| **Governance** | `READ/WRITE VOLUME` permissions | `SELECT/MODIFY` permissions |

**Rule of thumb:** If you need to `SELECT * FROM ... WHERE ...`, use a table. If you need to store a model file or a raw JSON before parsing, use a volume.

### Volumes vs DBFS

| Aspect | Volumes | DBFS (root or /FileStore) |
|--------|---------|---------------------------|
| **Governance** | Fine‑grained (UC ACLs) | Workspace‑level only (any workspace user can read) |
| **Cross‑workspace** | Yes – accessible from any UC‑enabled workspace | No – isolated per workspace |
| **Mount points** | Not needed | Required for external storage (deprecated) |
| **Recommended for new workloads** | ✅ Yes | ❌ No (except legacy datasets) |
| **Audit logging** | Yes (Unity Catalog audit) | Basic (cluster logs only) |
| **Distributed `dbutils.fs`** | No (driver only) | Yes (but no governance) |
| **POSIX paths** | Yes – `/Volumes/...` | Yes – `/dbfs/...` or `/FileStore/...` |
| **Cloud credential management** | Automatic for managed volumes; external volumes use storage credentials | Manual via mount configuration or direct URIs |

**Migration path:** Move data from DBFS to volumes using `dbutils.fs.cp`:

```python
dbutils.fs.cp("/FileStore/legacy_data.csv", "/Volumes/my_catalog/my_schema/my_volume/legacy_data.csv")
```

### Volumes vs External Locations

| Aspect | Volumes | External Locations |
|--------|---------|---------------------|
| **Abstraction level** | Logical container (within a location) | Raw cloud storage path with credential |
| **Granularity** | Per‑directory (can have multiple volumes under same external location) | Per‑path (usually a bucket or container prefix) |
| **Can create tables?** | No – volumes hold files, not tables | Yes – external tables can be created directly on external locations |
| **Use case** | Organizing and governing files | Governing the underlying storage for tables and volumes |
| **Permissions** | `READ VOLUME`, `WRITE VOLUME` | `CREATE EXTERNAL TABLE`, `CREATE EXTERNAL VOLUME` |
| **Direct cloud URI access** | Yes (for external volumes) | Yes (for any external location path) |

**Relationship:** External locations are the **foundation** for external volumes. You create an external location (with a storage credential), then create external volumes pointing to subdirectories within it.

```sql
-- External location (admin setup)
CREATE EXTERNAL LOCATION my_landing
  URL 's3://company-data-lake/landing/'
  WITH (STORAGE CREDENTIAL lake_cred);

-- Multiple external volumes under the same external location
CREATE EXTERNAL VOLUME sales.raw.incoming
  LOCATION 's3://company-data-lake/landing/sales/';

CREATE EXTERNAL VOLUME iot.raw.device_logs
  LOCATION 's3://company-data-lake/landing/iot/';
```

---

## Common Mistakes and Misconceptions

| Mistake | Why It's Wrong | Correct Approach |
|---------|----------------|------------------|
| Trying to use `/dbfs/Volumes/...` | This path is reserved but does not work. | Use `/Volumes/...` or `dbfs:/Volumes/...` (with colon). |
| Using `dbutils.fs.ls` on `/Volumes/my_catalog/` | Listing at catalog or schema level is not supported. | Use `SHOW VOLUMES IN my_catalog.my_schema` SQL command. |
| Expecting `dbutils.fs` to work on executors | `dbutils.fs` commands are driver‑only. | Use Spark DataFrame writers/readers for distributed I/O. |
| Writing small files frequently | Creates thousands of tiny files → slow reads. | Coalesce writes (e.g., `df.coalesce(1).write` or use Auto Loader with file size target). |
| Using volumes for tabular data that needs querying | No ACID, no indexing, poor performance. | Create a Delta table instead. You can still land raw files in a volume, then `COPY INTO` a table. |
| Dropping external volume thinking data is removed | Data persists in cloud storage. | Delete files manually via cloud console or `dbutils.fs.rm` before dropping the volume if cleanup is needed. |
| Running volume code on DBR 12.2 or below | Data writes to ephemeral storage – lost on cluster termination. | Upgrade to DBR 13.3 LTS or above. |
| Using `%sh mv` to move files between volumes | Not supported. | Use `dbutils.fs.mv`. |

---

## Summary

**Volumes are the modern, governed way to store any non‑tabular data in Databricks.** They replace DBFS and mount points for new workloads, providing:

- **Security** through Unity Catalog ACLs and audit logs
- **Simplicity** via POSIX paths and automatic credential management (managed volumes)
- **Flexibility** with external volumes for hybrid environments
- **Integration** with medallion architectures as landing zones for raw files

Use **managed volumes** for Databricks‑only workflows; use **external volumes** when files must be shared with external systems. Always pair volumes with Delta tables for tabular data – volumes are not a replacement for tables, but a complement for file storage.

For further reading, refer to the official Databricks documentation on [What are Unity Catalog volumes?](https://docs.databricks.com/en/volumes/index.html) and the [SQL reference for volumes](https://docs.databricks.com/en/sql/language-manual/sql-ref-volumes.html).

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Databricks Concepts/Managed Vs External Tables|Managed vs External Tables (Unity Catalog)]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Databricks Concepts/Views/Views|Views]]

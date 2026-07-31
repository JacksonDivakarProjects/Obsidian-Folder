## Auto Loader in Apache Spark Structured Streaming

### 1. Simple Definition & Purpose

**Auto Loader** (also known as `cloudFiles` source) is a feature in Apache Spark Structured Streaming that incrementally and efficiently processes new files arriving in cloud storage (e.g., S3, ADLS, GCS) without needing to manage file discovery logic manually.

**Why use it?**  
Traditional streaming from file sources (like `spark.readStream.format("parquet")`) has limitations: it relies on directory listing which becomes slow with many files, and it doesn’t handle schema evolution well. Auto Loader solves these by:
- **Scalable file discovery** using file notifications (e.g., AWS SQS, Azure Event Grid) or optimized listing.
- **Automatic schema inference & evolution** – detects changes like new columns safely.
- **Exactly-once guarantees** with checkpointing.

---

### 2. How Auto Loader Works – Step by Step

The flow from source cloud storage to destination (e.g., Delta table):

1. **Setup notification service (recommended)**  
   Configure cloud storage to send events (file creation) to a queue (SQS, Event Grid). Auto Loader subscribes to this queue. If notifications are unavailable, it falls back to **directory listing** (still optimized).

2. **Start streaming query**  
   You define a `readStream` using `format("cloudFiles")` and specify options like `cloudFiles.format` (JSON, Parquet, CSV, etc.) and path.

3. **File detection & queuing**  
   - When a new file lands in the source directory, cloud storage sends an event → queue.  
   - Auto Loader’s source pulls events from the queue.  
   - For each event, it fetches the file’s metadata (path, size, last modified).  
   - *Fallback mode*: It lists the directory and keeps a local state of processed files (using checkpointing).

4. **Schema inference & evolution**  
   - On first run, Auto Loader samples a few files (configurable) to infer the schema.  
   - With `cloudFiles.schemaEvolutionMode = "addNewColumns"`, it can detect new columns in later files and update the schema dynamically (requires a sink that supports schema evolution, e.g., Delta).

5. **Incremental processing**  
   - Auto Loader tracks processed files in a **checkpoint location** (e.g., `checkpoint/cloudFiles/`).  
   - It compares incoming file events against the processed set and ignores duplicates.  
   - Only **new, unseen files** are passed to Spark’s streaming engine as micro‑batches.

6. **Data transformation & writing**  
   - The streaming DataFrame (with the inferred or evolving schema) can be transformed (filter, join, aggregate) and then written using `writeStream` to a sink – commonly a Delta table.

---

### 3. Key Components (Plain English)

| Component | Role |
|-----------|------|
| **Cloud Storage (source)** | S3 / ADLS / GCS where raw files land. |
| **Notification Queue** (optional) | SQS / Event Grid / Pub/Sub – sends “new file” signals to Auto Loader. |
| **Checkpoint Directory** | Stores processed file names and schema history; enables exactly‑once processing. |
| **Schema Inference Engine** | Reads a few files to guess column names/types; can add new columns over time. |
| **Micro‑batch Executor** | Spark’s streaming engine that processes each batch of new files. |
| **Destination Sink** (e.g., Delta table) | Where cleaned/transformed data is appended. |

---

### 4. Conceptual Working – New File Detection

Imagine a folder `s3://data/incoming/` with JSON files.

- **Step A**: You start Auto Loader. It reads the checkpoint (first run – empty).  
- **Step B**: Auto Loader lists the directory once and remembers which files exist (e.g., `file1.json`).  
- **Step C**: Later, a new file `file2.json` is uploaded.  
- **Step D**: If notifications are on, SQS pushes a message; Auto Loader reads it and discovers `file2.json`.  
- **Step E**: It compares with checkpoint – `file2.json` is new, so it includes it in the next micro‑batch.  
- **Step F**: After processing, it writes `file2.json` to checkpoint.  
- **Step G**: `file2.json` will never be processed again, even if the stream restarts.

In **fallback (listing) mode**, Auto Loader re‑lists the directory periodically (configurable interval) but maintains an internal index to avoid listing all files every time – much more efficient than the legacy file source.

---

### 5. Sample PySpark Code

```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StringType, IntegerType
import pyspark.sql.functions as F

spark = SparkSession.builder.appName("AutoLoaderDemo").getOrCreate()

# Optional: define a base schema (if you don't want full inference)
user_schema = StructType() \
    .add("user_id", IntegerType()) \
    .add("name", StringType()) \
    .add("timestamp", StringType())

# Auto Loader streaming read
stream_df = spark.readStream \
    .format("cloudFiles") \
    .option("cloudFiles.format", "json") \               # file format
    .option("cloudFiles.schemaInference", "true") \      # infer schema on start
    .option("cloudFiles.schemaEvolutionMode", "addNewColumns") \  # handle new cols
    .option("cloudFiles.schemaLocation", "/path/checkpoint/schema") \  # store schema
    .option("cloudFiles.includeExistingFiles", "false") \ # ignore existing files
    .option("cloudFiles.maxFilesPerTrigger", "1000") \    # batch size
    .schema(user_schema) \                               # optional: fixed schema
    .load("s3a://my-bucket/raw-data/")

# Example transformation: add ingestion timestamp
transformed_df = stream_df.withColumn("ingestion_time", F.current_timestamp())

# Write to Delta table (append mode)
query = transformed_df.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/path/checkpoint/stream") \  # streaming checkpoint
    .queryName("auto_loader_to_delta") \
    .start("/path/delta-table")

query.awaitTermination()
```

**Important options explained:**

| Option | Meaning |
|--------|---------|
| `cloudFiles.format` | Format of incoming files: `json`, `parquet`, `csv`, `text`, `binaryFile`. |
| `cloudFiles.schemaInference` | Sample files to infer schema (default `true`). |
| `cloudFiles.schemaEvolutionMode` | How to handle schema changes: `none` (fail), `addNewColumns` (safe), `rescue` (collect extra cols as JSON). |
| `cloudFiles.schemaLocation` | Directory to store inferred schema across restarts. |
| `cloudFiles.includeExistingFiles` | Whether to process files already present before the stream starts (default `true` – careful!). |
| `cloudFiles.maxFilesPerTrigger` | Max files to read in one micro‑batch (controls latency & throughput). |
| `checkpointLocation` | (separate from `schemaLocation`) Stores processed file IDs for exactly‑once. |

---

### 6. When to Use Auto Loader (Practical Context)

**✅ Good use cases:**
- **Ingesting log files** (JSON, CSV, Parquet) dropped into S3 by services (e.g., AWS CloudTrail, Kinesis Firehose).
- **Event‑driven ETL pipelines** where files arrive irregularly (e.g., partner uploads).
- **CDC (Change Data Capture)** from databases dumped as files.
- **Real‑time / near‑real‑time** (latency seconds to minutes) when you want exactly‑once and schema evolution.

**❌ Avoid when:**
- You need **sub‑second latency** – Auto Loader works in micro‑batches (best for seconds to minutes). Use Kafka/Kinesis instead.
- You process **millions of tiny files** – better to batch them first (e.g., coalesce into larger files).
- Your source is a **database table** (use JDBC batch, not streaming).
- You don’t have a **durable sink** (Delta Lake recommended – supports schema evolution & upserts).

---

### 7. Advantages

| Advantage | Explanation |
|-----------|-------------|
| **Scalable file discovery** | Uses queue notifications; listing is incremental, not full scans. |
| **Automatic schema evolution** | Safely adds new columns without stopping the stream. |
| **Exactly‑once semantics** | Checkpointing ensures no duplicates after failures. |
| **Resilient to duplicate events** | CloudFiles deduplicates based on file path & modification time. |
| **Works with all cloud providers** | S3, ADLS, GCS, even local file system (with listing). |

---

### 8. Limitations & Real‑world Caveats

| Limitation | Impact & Mitigation |
|------------|----------------------|
| **Requires checkpoint location** | Must be a persistent file system (e.g., S3, HDFS). Loss of checkpoint causes reprocessing. |
| **Schema evolution limited to adding columns** | Cannot drop or rename columns; use `rescue` mode to capture malformed data. |
| **Notification queue costs** | SQS / Event Grid incur small cost; listing fallback works but is slower for large directories. |
| **No exactly‑once with non‑idempotent sinks** | Delta Lake supports it; others (Kafka, console) may duplicate on retry. |
| **File format limitations** | Nested schema evolution in JSON/Parquet may need additional handling. |
| **Initial backfill** | If `includeExistingFiles = true`, it processes all existing files – can overload cluster. Set to `false` if you only want new files. |

---

### Summary

Auto Loader (`cloudFiles`) is the recommended way to read streaming files from cloud storage in Structured Streaming. It eliminates manual file tracking, scales to millions of files, and gracefully handles schema changes. Use it when you have an append‑only stream of files landing in a cloud bucket and you need reliable, incremental processing into a Delta Lake or other sink.
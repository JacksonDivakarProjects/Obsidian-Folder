# Archiving Source Files in Spark Structured Streaming

## 🔹 Concept

When Structured Streaming reads files (JSON, CSV, Parquet, etc.), it tracks which files have already been processed — but by default, those files just **stay in the input directory**, which clutters storage and can be confusing to reason about.

Spark's **source archival** options let it automatically **move processed files to an archive folder** instead.

---

## 🔹 Purpose

Archiving source files:

* Keeps the input directory clean and organized.
* Prevents Spark from reprocessing the same files.
* Retains an audit trail / backup of processed files.
* Avoids the performance degradation that comes from too many files piling up in the input folder.

---

## 🔹 Core Options

### 1. `.option('sourceArchiveDir', path)`

Specifies **where processed files should be moved** once Spark finishes reading them.

* **Type:** String (path to the archive directory)
* **Example:**
  ```python
  .option("sourceArchiveDir", "/mnt/archive/json_data")
  ```
* **Meaning:** after processing each file, Spark moves it to `/mnt/archive/json_data`.

### 2. `.option('cleanSource', 'archive')`

Tells Spark **what to do with source files** after they're successfully processed.

* **Possible values:**
  * `"none"` — default; files remain in the source directory.
  * `"delete"` — deletes processed files.
  * `"archive"` — moves processed files to the directory named by `sourceArchiveDir`.
* **Example:**
  ```python
  .option("cleanSource", "archive")
  ```

---

## 🔹 Combined Example

```python
stream_df = (
    spark.readStream
         .format("json")
         .schema(schema)
         .option("maxFilesPerTrigger", 1)
         .option("cleanSource", "archive")
         .option("sourceArchiveDir", "/Volumes/sparkstreaming/archive/jsondata")
         .load("/Volumes/sparkstreaming/default/jsondata")
)

query = (
    stream_df.writeStream
         .format("delta")
         .option("checkpointLocation", "/Volumes/sparkstreaming/checkpoints/jsondata")
         .outputMode("append")
         .start("/Volumes/sparkstreaming/output/jsondata")
)
```

### 🔸 Workflow

1. Spark continuously monitors `/Volumes/sparkstreaming/default/jsondata`.
2. When a new file arrives:
   * Spark reads and processes it.
   * Moves it to `/Volumes/sparkstreaming/archive/jsondata`.
3. That file is **never re-read** again.

---

## 🔹 Internal Mechanism

When `cleanSource="archive"` is used:

* Spark **renames (moves)** the file after successful ingestion.
* This supports **exactly-once** processing — each file is handled once.
* If the file can't be archived (e.g. permission denied), Spark logs a warning rather than failing the batch.

---

## 🔹 Practical Notes

| Scenario                           | Behavior                                                                   |
| ----------------------------------- | --------------------------------------------------------------------------- |
| **Job restarts**                   | Spark uses checkpoint data to know which files were already processed.     |
| **No archive directory given**     | Error if `cleanSource="archive"` but `sourceArchiveDir` isn't set.          |
| **File failure during processing** | File won't be archived; it stays in the source directory.                  |
| **Performance**                    | Moving files is more I/O-heavy than deleting, but preserves traceability.  |

---

## 🔹 Example Use Case

IoT sensors uploading JSON files every few seconds to a directory. Instead of leaving 100,000 processed files sitting in the input folder, Spark archives them to a separate storage location (S3, ADLS, or HDFS) — keeping the streaming system clean, traceable, and efficient.

---

## 🔹 Summary

| Option             | Purpose                | Example Value               |
| ------------------- | ----------------------- | ---------------------------- |
| `cleanSource`      | Action after reading   | `archive`, `delete`, `none` |
| `sourceArchiveDir` | Archive directory path | `/mnt/archive/json`         |

Use both together to automate housekeeping in Spark streaming file sources.

## 🔗 Related Notes
- [[Spark Streaming Foundational Concepts|Spark Streaming Foundational Concepts]]
- [[Checkpointing And Idempotency|Checkpointing & Idempotency in PySpark Structured Streaming]]
- [[Types Of Triggers|🔥 Comprehensive Guide to PySpark Structured Streaming Triggers]]

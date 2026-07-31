Alright Jack — let’s unpack this properly and make a **comprehensive note** on Spark’s **source file archival** mechanism.

---

## 🔹 Concept: Archiving Source Files in Spark Structured Streaming

When Spark Structured Streaming reads files (e.g., from JSON, CSV, or Parquet directories), it **tracks which files have been processed**.
But what happens to those source files after they’re read?
By default, they **stay in the input directory**, which can clutter storage and cause confusion.

To manage this, Spark provides **source archival** options — allowing Spark to automatically **move processed files to an archive folder**.

---

## 🔹 Purpose

Archiving source files helps:

* Keep the input directory clean and organized.
* Prevent Spark from reprocessing the same files.
* Retain an audit trail or backup of processed files.
* Avoid performance degradation from too many files in the input folder.

---

## 🔹 Core Options

### **1. `.option('sourceArchiveDir', path)`**

This specifies **where the processed files should be moved** once Spark finishes reading them.

* **Type:** String (Path to archive directory)

* **Example:**

  ```python
  .option("sourceArchiveDir", "/mnt/archive/json_data")
  ```

* **Meaning:** After Spark processes each file, it moves it to `/mnt/archive/json_data`.

---

### **2. `.option('cleanSource', 'archive')`**

This tells Spark **what to do with the source files** after they are successfully processed.

* **Possible values:**

  * `"none"` – Default. Files remain in the source directory.
  * `"delete"` – Deletes processed files.
  * `"archive"` – Moves processed files to a directory defined by `sourceArchiveDir`.

* **Example:**

  ```python
  .option("cleanSource", "archive")
  ```

---

## 🔹 Combined Example

Here’s how you’d use both in a structured streaming job:

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

### 🔸 Workflow:

1. Spark continuously monitors `/Volumes/sparkstreaming/default/jsondata`.
2. When a new file arrives:

   * Spark reads and processes it.
   * Moves it to `/Volumes/sparkstreaming/archive/jsondata`.
3. That file is **never re-read** again.

---

## 🔹 Internal Mechanism

When `cleanSource="archive"` is used:

* Spark **renames (moves)** the file after successful ingestion.
* This ensures **exactly-once semantics** — i.e., each file is processed once.
* If the file cannot be archived (e.g., permission denied), Spark logs a warning.

---

## 🔹 Practical Notes

| Scenario                           | Behavior                                                                   |
| ---------------------------------- | -------------------------------------------------------------------------- |
| **Job restarts**                   | Spark uses checkpoint data to know which files were already processed.     |
| **No archive directory given**     | Error if `cleanSource="archive"` but `sourceArchiveDir` not set.           |
| **File failure during processing** | File won’t be archived; stays in source dir.                               |
| **Performance**                    | Moving files is more I/O heavy than deleting, but useful for traceability. |

---

## 🔹 Example Use Case

Imagine you have IoT sensors uploading JSON files every few seconds to a directory.
Instead of leaving 100,000 processed files in the input folder, Spark can archive them to a separate storage directory (S3, ADLS, or HDFS).
This keeps your streaming system **clean, traceable, and efficient.**

---

## 🔹 Summary

| Option             | Purpose                | Example Value               |
| ------------------ | ---------------------- | --------------------------- |
| `cleanSource`      | Action after reading   | `archive`, `delete`, `none` |
| `sourceArchiveDir` | Archive directory path | `/mnt/archive/json`         |

✅ Use both together to **automate housekeeping** in Spark streaming file sources.

---

Would you like me to add a **visual flow diagram** (showing how Spark reads → processes → archives files)? It helps a lot when explaining this in presentations or notes.
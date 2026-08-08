# Spark Structured Streaming: Foundational Concepts

A structured tour of the core ideas behind PySpark Structured Streaming, from the microbatch model through windowing and late-data handling.

---

### **Foundational Streaming Concepts**

#### 1. Streaming (Stream Processing)
   - **Definition:** the continuous processing of incoming data in real-time or near real-time.
   - **Key points:**
      - Deals with **infinite and unbounded data** — the source has no defined start and end point.
      - Contrasts with batch processing, which operates on fixed, bounded datasets.
   - **Example:** IoT sensors or thermostats continuously sending data are a classic streaming source — like water flowing through a pipe, requiring action as data arrives rather than waiting for it to stop.

#### 2. Microbatching
   - **Definition:** Spark's approach of grouping incoming data into small time intervals (e.g. 1 second, 2 seconds, or milliseconds) and treating each interval as a mini batch job.
   - **Key points:**
      - Replaced earlier streaming models (e.g. Apache Storm) that processed one record at a time, which was less efficient at scale.
      - Lets Spark reuse its existing batch engine under the hood.
      - Gives better **fault tolerance** than pure record-at-a-time systems.
   - **Example:** instead of processing individual sensor readings the instant they arrive, Spark collects one second's worth of readings and processes them together as a single micro-batch.

#### 3. Structured Streaming's Core Model: the Unbounded Table
   - **Definition:** Structured Streaming treats a stream source as a **structured, unbounded table** that keeps growing.
   - **Key points:**
      - New data arriving is modeled as new rows appended to this never-ending table.
      - This lets you write **the same DataFrame/SQL code for both batch and streaming** — the query itself doesn't need to know it's streaming.
   - **Example:** an IoT data feed is treated as rows being continually added to a normal table, so ordinary DataFrame transformations apply unchanged.

---

### **Transformations and State Management**

#### 4. Stateless Transformations
   - **Definition:** transformations where each executor doesn't need to know the results (state) of previous batches to process the current one.
   - **Key points:**
      - Correspond to Spark's **narrow transformations**.
      - Each partition can apply the transformation independently, without data shared across executors.
   - **Example:** a `SELECT` or `FILTER`. An executor selecting columns only needs the rows in its current partition — nothing from a previous micro-batch.

#### 5. Stateful Transformations
   - **Definition:** transformations that must persist state across micro-batches to produce correct, cumulative results.
   - **Key points:**
      - When a new batch arrives, the executor refers back to previously saved state to compute the true aggregate.
      - State lives in the executors' **cached memory** (and is checkpointed for fault tolerance).
   - **Example:** a `GROUP BY` or other aggregation (e.g. counting occurrences). If an executor sees another "blue" event, it must recall it already counted two "blue" events in earlier batches, to report a correct running total of three.

---

### **Handling Complex Data (JSON)**

#### 6. Flattening Nested JSON Data
   - **Definition:** extracting fields from hierarchical structures (nested structs, arrays) into flat, directly accessible columns.
   - **Key points:**
      - Nested structs are accessed with **dot notation** (e.g. `customer.address.city`).
      - Arrays need an explicit function to turn list elements into rows.
   - **Example:** `customer.address.city` pulls the city out of a nested `customer` struct.

#### 7. `explode` and `explode_outer`
   - **Definition:** functions that turn array elements within a column into individual rows. `explode_outer` is usually the safer default, since it keeps rows with null or empty arrays instead of silently dropping them. See [[Explode vs Explode Outer|Explode vs Explode Outer]] for the full comparison with examples.
   - **Key points:**
      - An array column must be exploded for each element to become its own row.
      - `explode` drops rows where the array is null or empty; `explode_outer` keeps them, filling the exploded column with `null` — important for not silently losing records from semi-structured JSON.
   - **Example:** an `items` column holding three purchased items becomes three separate rows after `explode_outer`.

---

### **Writing the Stream (Output Modes)**

See [[Output Modes in Streaming|Output Modes in Streaming]] for full syntax and sink-compatibility details.

#### 8. Append Mode
   - **Definition:** writes only the **new records** that arrived since the last trigger.
   - **Key points:**
      - Works only with transformations that don't require re-emitting old rows (stateless transforms, or stateful aggregations whose windows have watermarked and closed).
      - The simplest, most common mode — good for data where historical records never change (e.g. logs).
   - **Example:** ingesting into the raw layer of a data architecture, where only new incoming data should be appended, never modifying past records.

#### 9. Complete Mode
   - **Definition:** writes the **entire updated result table** on every micro-batch — typically used with aggregations.
   - **Key points:**
      - Includes every key, even ones whose value didn't change this batch.
      - Behaves like an overwrite of the destination on every trigger.
   - **Example:** counting colored balls — even if "pink"'s count didn't change this batch, Complete Mode re-emits it alongside the updated counts for other colors.

#### 10. Update Mode
   - **Definition:** writes only the rows whose **state changed** in the current micro-batch.
   - **Key points:**
      - More efficient than Complete Mode — it minimizes what's written.
      - Only outputs values where the executor's cached state was actually updated.
      - Not supported by every sink (e.g. plain file sinks don't support it).
   - **Example:** if only "blue," "red," and "green" counts changed, Update Mode emits only those three, skipping unchanged colors like "yellow."

---

### **Stream Management and Reliability**

#### 11. Checkpoint Location
   - **Definition:** where Structured Streaming stores the metadata needed for fault-tolerant, exactly-once-ish processing — the backbone of the whole mechanism. See [[Checkpointing And Idempotency|Checkpointing & Idempotency in PySpark Structured Streaming]] for the full guide.
   - **Key points:**
      - Provides **idempotency** — data already processed successfully won't be reprocessed, even if the same source file reappears.
      - Tracks the query ID (metadata), files read (sources), and successfully committed batches (commits).
      - Should never be manually edited or shared between queries.
   - **Example:** if a streaming job is interrupted, the checkpoint directory tells Spark exactly which files were already read, so it can resume without reprocessing old data.

#### 12. Triggers
   - **Definition:** mechanisms controlling how and when a streaming query executes each micro-batch. See [[Types Of Triggers|🔥 Comprehensive Guide to PySpark Structured Streaming Triggers]] for full syntax.
   - **Key points:**
      - **Default:** starts the next micro-batch immediately after the previous one finishes.
      - **`processingTime`:** runs at fixed, scheduled intervals (e.g. every 10 seconds).
      - **`once`:** processes all currently available data, then stops — behaves like a batch job.
      - **`availableNow`:** similar to `once`, but splits the available data into several smaller micro-batches instead of one large one, easing the load.
      - **`continuous`:** processes data row by row instead of in micro-batches, for millisecond-level latency; the configured interval controls how often the checkpoint/epoch marker advances, not the processing granularity.
   - **Example:** a business needing updates every 10 seconds uses `trigger(processingTime='10 seconds')`.

#### 13. Archiving Source Files
   - **Definition:** automatically moving processed source files out of the active source directory into a separate archive directory. See [[Archive Source File|Archive Source File]] for configuration details.
   - **Key points:**
      - Keeps the source folder manageable, especially with thousands of files arriving daily.
      - A processed file is only moved once a **new, unprocessed** file arrives and triggers a run — archiving isn't instantaneous.
      - A re-uploaded duplicate of an already-processed file is skipped by idempotency, but stays in the source folder until the next genuinely new file arrives and triggers cleanup.
   - **Example:** Day 1 data is processed; when Day 2 data arrives, Day 1's files move to the archive and Day 2 is processed. If Day 1's files are re-uploaded, they sit untouched in the source folder until Day 3 data arrives.

#### 14. `foreachBatch`
   - **Definition:** a sink that hands each micro-batch to you as a plain batch DataFrame, so you can run arbitrary batch-style code against it. See [[ForEachBatch|ForEachBatch]] for the full guide.
   - **Key points:**
      - Enables operations not natively supported by streaming sinks.
      - The standout use case is a **MERGE** (upsert) into a Delta table.
      - Lets a single streaming query fan out writes to **multiple destinations**.
   - **Example:** a function that takes the micro-batch DataFrame and writes it to two separate Delta tables using ordinary `df.write` batch calls.

---

### **Windowing and Late Data Handling**

#### 15. Event Time vs. Processing Time
   - **Definition:** **Event time** is when a record was generated at the source; **processing time** is when the engine actually processes it.
   - **Key points:**
      - Event time is the **source of truth** for aggregations, since processing time can be skewed by network latency or delays.
      - Windowed aggregations should always key off event time.
   - **Example:** a sensor records a reading at 11:00 AM (event time), but network delay means it's processed at 11:05 AM (processing time).

#### 16. Tumbling Window
   - **Definition:** **non-overlapping, fixed-size** time intervals used to group data for aggregation. See [[Types Of Windows|Window Operations in PySpark Structured Streaming]] for syntax and code.
   - **Key points:**
      - Each record belongs to exactly one window; it can never contribute to an adjacent window.
      - Spark auto-generates a `window` struct column based on the chosen interval.
   - **Example:** with 5-second windows, 0:00–0:05 is Window 1 and 0:05–0:10 is Window 2. A record at 0:06 belongs only to Window 2.

#### 17. Sliding Window
   - **Definition:** **overlapping, fixed-size** intervals used to group data for aggregation.
   - **Key points:**
      - Because windows overlap, a single record can belong to **multiple windows** at once.
      - That means one event contributes to multiple separate aggregation results.
   - **Example:** with a 10-minute window and a 5-minute slide, a record at 11:07 AM belongs to both the 11:00–11:10 and 11:05–11:15 windows.

#### 18. Session Window
   - **Definition:** **variable-size** windows driven entirely by data arrival, not a fixed clock.
   - **Key points:**
      - A session stays open for a defined gap duration (e.g. 10 minutes) after the last event; a new event within that gap extends the session.
      - The session only closes once the gap duration passes with no new events.
   - **Example:** with a 10-minute gap, an event at 11:02 opens a session active until 11:12. Another event at 11:08 extends it to remain active until 11:18.

#### 19. Watermarking
   - **Definition:** a mechanism for bounding how long Spark retains state for old windows, to handle **late-arriving data** without exhausting memory. See [[Watermarking in Streaming|Watermarking in PySpark Structured Streaming]] for the full guide.
   - **Key points:**
      - Without a watermark, executors would retain state for every window indefinitely, eventually running out of memory.
      - Data arriving later than the watermark threshold is **dropped** — it will never be aggregated.
      - Watermarking is compatible with **update** and **append** modes but not **complete** mode, since complete mode requires the full, un-pruned state for every window — see [[Why Complete Mode not Working in Watermarking|Why `complete` Output Mode Doesn't Work with Watermarks]].
   - **Example:** with a 60-minute watermark and a current processing time of 11:30 AM, any event with a timestamp before 10:30 AM is dropped rather than aggregated, even if it would belong to a past window.

## 🔗 Related Notes
- [[Types Of Windows|Window Operations in PySpark Structured Streaming]]
- [[Watermarking in Streaming|Watermarking in PySpark Structured Streaming]]
- [[Explode vs Explode Outer|Explode vs Explode Outer]]
- [[ForEachBatch|ForEachBatch]]

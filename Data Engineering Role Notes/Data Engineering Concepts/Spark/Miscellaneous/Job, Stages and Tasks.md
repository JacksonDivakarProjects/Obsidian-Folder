# Spark Execution: Job, Stages and Tasks

## 1. Original Data & RDD
- Original data lives in HDFS, S3, or local files.
- Spark represents it as an **RDD** — a logical representation of the data.
- The RDD is split into **partitions**, the smallest unit of parallelism.
- **Note:** 1 task = 1 partition.

## 2. Transformations (Lazy Evaluation)
- Transformations (`map`, `filter`, `flatMap`) are **lazy** — they only define what to do, they don't execute yet.
- Multiple narrow transformations can be pipelined into the same stage.
- **Narrow transformations** (no shuffle) stay in the same stage.
- **Wide transformations** (`groupByKey`, `reduceByKey`, `join`) require a shuffle, which starts a new stage.

## 3. Actions & Jobs
- An **action** (`collect()`, `count()`, `saveAsTextFile()`) triggers execution — this is a **job**.
- Each action creates a separate job, unless the RDD is cached and reused.
- A job can have multiple stages, especially when wide transformations are involved.
- A job has just one stage and one task only if its RDD has a single partition and no shuffle occurs.

## 4. Job → Stages → Tasks
- **Job** — the complete execution triggered by an action.
- **Stage** — a set of tasks that can run without a shuffle in between; stage boundaries are created at shuffle boundaries.
- **Task** — the unit of work that processes one partition.

Notes:
- Tasks run in parallel across executors.
- A `groupBy` requires at least 2 stages:
  1. **Map stage** — distributes keys.
  2. **Reduce stage** — groups values by key.
- After grouping, each key's values are aligned within a partition, and that partition isn't shuffled again unless another wide transformation follows.

## 5. Executors & Data
- An **executor** is a JVM process on a worker node that runs tasks and may hold partitioned data if it's cached/persisted.
- Tasks fetch data dynamically — either from the original data source or from shuffle files written by a previous stage.
- Executors run tasks; they don't move tasks between nodes. A shuffle moves **data**, not tasks.

## 6. Shuffle & Data Movement
- Wide transformations trigger a shuffle, transferring data across executors.
- Stages run sequentially relative to shuffles, but tasks within a stage run in parallel.
- Narrow transformations stay in the same stage; wide transformations create new stages.
- Stages are logical boundaries — the tasks within them are what actually execute on executors.
- Caching/persisting avoids recomputation and re-reading of partitions across jobs.

## 7. Summary Flow
1. Original data → RDD partitions
2. Transformations build a logical (lazy) plan
3. An action triggers a **job**
4. The job splits into **stages** at shuffle boundaries
5. Each stage splits into **tasks** (one per partition)
6. Tasks run in executors, processing partitions in parallel
7. Wide transformations trigger a shuffle → next stage
8. Executors fetch partition data dynamically as needed
9. Caching reduces repeated reads and recomputation

## 8. Key Takeaways
- 1 task = 1 partition.
- `groupBy` needs at least 2 stages (map + reduce).
- Narrow transformations don't shuffle, so they stay in the same stage.
- A shuffle moves data, not tasks.
- Executors hold data only temporarily, depending on caching.
- A stage's tasks can run on one or many executors, depending on available resources and partitioning.
- Stages define the pipeline boundaries for Spark's distributed execution.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Joins/Types Of Joins|Types Of Joins]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Memory Management/Executer Memory Management|Spark Executor Memory Architecture]]

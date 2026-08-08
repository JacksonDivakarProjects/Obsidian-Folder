## Databricks Jobs Parameter Passing — `dbutils.widgets` vs `dbutils.jobs.taskValues`

## 1. Core Definitions

- **`dbutils.widgets`** — input interface for passing *external* parameters into a notebook (job parameters, or manual values typed into the notebook UI).
- **`dbutils.jobs.taskValues`** — mechanism for passing small values *between tasks* inside a multi-task job.

They solve different problems: widgets get data **into** a notebook; taskValues move data **between** notebooks/tasks within the same job run.

## 2. Minimal Syntax

**Widgets**
```python
dbutils.widgets.text("mode", "full")
mode = dbutils.widgets.get("mode")
```

**taskValues**
```python
# set (upstream task)
dbutils.jobs.taskValues.set("row_count", count)

# get (downstream task)
count = dbutils.jobs.taskValues.get(
    taskKey="task_a",
    key="row_count",
    debugValue=0
)
```

## 3. Execution Flow

```text
Job Parameters → Widgets → Notebook Logic → taskValues.set()
                                              ↓
                                       Next Task → taskValues.get()
```

## 4. Key Parameters of `taskValues.get()`

- **`taskKey`** — the name of the *upstream task* that set the value. Must match the job's task configuration exactly.
- **`key`** — the name under which the value was stored during `set()`.

```text
taskKey = which task produced the value
key     = which variable to retrieve
```

### `debugValue`

Fallback used when there is no upstream task context — i.e., the notebook is run manually outside a job. In a real job run, the actual upstream value is returned; in a manual/interactive run, `debugValue` is returned instead.

```python
count = dbutils.jobs.taskValues.get(
    taskKey="task_a",
    key="row_count",
    debugValue=0
)
```

## 5. Widget Value Source Priority

When a widget is read, its value is resolved in this order:

1. **Job parameter** passed in at run time (a job run overrides everything else).
2. **Manually edited value** in the widget UI (interactive/manual runs).
3. **Default value** defined in the `dbutils.widgets.text(...)` call (used if nothing else set it).

## 6. Important Behaviors

**Widgets**
- Always return **strings** — cast explicitly if you need another type, e.g. `int(dbutils.widgets.get("limit"))`.
- Must be defined (via `dbutils.widgets.text/dropdown/combobox/multiselect`) before they can be read.
- Are resolved at the **start** of notebook execution.
- Do **not** pass data between tasks — each task's widgets are independent.

**taskValues**
- Work **only inside Databricks Jobs** — outside a job, `get()` falls back to `debugValue`.
- Store **small, serializable** values (counts, flags, short strings, paths) — never DataFrames or large objects.
- Are set/read **during** task execution, not before it.
- A `key` reused within the same task **silently overwrites** the previous value.

## 7. Combined Pattern

Task A:
```python
mode = dbutils.widgets.get("mode")               # read input
count = spark.table("data").count()              # process
dbutils.jobs.taskValues.set("row_count", count)  # pass downstream
```

Task B:
```python
count = dbutils.jobs.taskValues.get(
    taskKey="task_a",
    key="row_count",
    debugValue=0
)
```

What this does **not** do: it doesn't automatically use `mode` anywhere else in the job, doesn't persist data outside the job run, and doesn't itself trigger the next task — orchestration is still controlled by the job's task DAG, not by `taskValues`.

## 8. Widgets vs taskValues — Side by Side

| Aspect | Widgets | taskValues |
|---|---|---|
| Purpose | Input | Task-to-task communication |
| Direction | External → notebook | Task → task |
| Data type | String only | Small serializable value |
| Scope | Single notebook | Multi-task job |
| Timing | Resolved before execution | Set/read during execution |

## 9. Common Patterns

**Control execution based on input**
```python
mode = dbutils.widgets.get("mode")
if mode == "full":
    run_full()
```

**Pass metadata to the next task**
```python
dbutils.jobs.taskValues.set("output_path", "/mnt/output")
```

**Conditional pipeline based on an upstream result**
```python
status = dbutils.jobs.taskValues.get(
    taskKey="validation",
    key="is_valid",
    debugValue="false"
)

if status == "true":
    run_pipeline()
```

## 10. Failure Scenarios / Gotchas

- Reading a widget that was never defined → error.
- Missing `debugValue` on a manual run with no upstream task context → failure.
- Wrong `taskKey` or wrong `key` → value cannot be retrieved.
- Passing large data (a DataFrame, a big JSON blob) through `taskValues` → unsupported.
- Forgetting to cast a widget value → comparisons like `dbutils.widgets.get("limit") > 10` fail because widgets always return strings.

## 11. When to Use Which

- **Widgets** → configuration inputs: mode flags, limits, file paths, environment names.
- **taskValues** → small results passed forward: row counts, validation flags, generated paths.
- Avoid widgets for inter-task communication (they're notebook-scoped, not job-scoped); avoid taskValues for anything beyond small metadata.

## 12. Mental Model

```text
Widgets    = input API for a single notebook
Notebook   = the processing unit
taskValues = the message bus between tasks in a job
```

## 13. Quick Q&A

- **Is a widget's value set automatically?** No — it comes from a job parameter, a manually edited UI value, or the code default.
- **Does `taskValues` work outside Jobs?** No — it falls back to `debugValue`.
- **Can widgets pass values to another task?** No.
- **Can `taskValues` store large data?** No — only small metadata.
- **What happens with a wrong `taskKey`?** The value cannot be retrieved (lookup fails).

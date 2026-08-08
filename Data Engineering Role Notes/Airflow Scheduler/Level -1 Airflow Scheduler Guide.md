# Comprehensive Apache Airflow Scheduler Guide for Beginners

## Table of Contents
1. [What is Apache Airflow?](#what-is-apache-airflow)
2. [Airflow Architecture](#airflow-architecture)
3. [Installing Airflow](#installing-airflow)
4. [Core Concepts](#core-concepts)
5. [Writing Your First DAG](#writing-your-first-dag)
6. [Airflow Scheduler Deep Dive](#airflow-scheduler-deep-dive)
7. [Common Operators](#common-operators)
8. [Task Dependencies](#task-dependencies)
9. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
10. [Best Practices](#best-practices)

## What is Apache Airflow?

Apache Airflow is an open-source platform to programmatically author, schedule, and monitor workflows. Workflows are defined as Python code, which makes them versionable, testable, and easy to collaborate on compared to config-driven or GUI-driven schedulers.

**Key features:**
- Dynamic workflow generation (DAGs are Python, so they can be built programmatically)
- Extensible through plugins and provider packages
- Rich web UI for monitoring and manual intervention
- Scales from a single laptop (`LocalExecutor`) to distributed clusters (`CeleryExecutor`, `KubernetesExecutor`)

## Airflow Architecture

### Core Components
1. **Scheduler** — parses DAGs, decides which DAG runs and task instances are due, and hands them to the executor. It does not execute tasks itself.
2. **Executor** — the mechanism that actually runs tasks (`LocalExecutor` runs them as subprocesses on the scheduler machine; `CeleryExecutor` and `KubernetesExecutor` distribute them to remote workers/pods).
3. **Web Server** — the UI for inspecting DAG runs, task logs, and triggering/pausing DAGs manually.
4. **Metadata Database** — stores DAG run state, task instance state, connections, variables, and XCom values.
5. **DAGs Directory** — the folder of Python files the scheduler parses to discover DAGs.
6. **Triggerer** (Airflow 2.2+) — runs the async event loop for *deferrable* operators/sensors, so a task waiting on an external event doesn't tie up a worker slot the whole time.

## Installing Airflow

### Quick Installation
```bash
# Install Airflow
pip install apache-airflow

# Initialize/upgrade the metadata DB (Airflow 2.7+; use `airflow db init` on older versions)
airflow db migrate

# Create a user
airflow users create \
    --username admin \
    --firstname FirstName \
    --lastname LastName \
    --role Admin \
    --email admin@example.com

# Start scheduler
airflow scheduler

# Start web server (in a new terminal)
airflow webserver --port 8080
```

> See the companion note [[Data Engineering Role Notes/Airflow Scheduler/Airflow Installation|🚀 Apache Airflow: Complete Installation & Troubleshooting Guide (Local Virtualenv)]] for the fully worked local-virtualenv walkthrough, including troubleshooting stuck processes.

### Using Docker (Recommended for anything beyond a quick local test)
```yaml
# docker-compose.yml (illustrative — trimmed down)
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow

  webserver:
    image: apache/airflow:2.8.1
    command: webserver
    ports:
      - "8080:8080"
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
```

This snippet is illustrative, not a complete deployment — a real setup also needs a `scheduler` service and a one-off DB-init step. For a production-ready reference, start from the official `docker-compose.yaml` published on the Airflow docs site rather than hand-rolling one.

## Core Concepts

### DAG (Directed Acyclic Graph)
A collection of tasks with directional dependencies and no cycles — the graph structure guarantees a task can't (directly or transitively) depend on itself.

### Task
A single unit of work in a DAG — one node in the graph.

### Operator
A Python class that defines *what a task does* (e.g. `PythonOperator` runs a Python callable, `BashOperator` runs a shell command). A Task is what you get when you instantiate an Operator inside a DAG.

### Task Instance
One specific run of a Task, for one DAG run — identified by the task, the DAG, and the logical/execution date.

## Writing Your First DAG

### Basic DAG Structure
```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

def print_hello():
    print("Hello, Airflow!")

def process_data():
    # Your data processing logic here
    return "Data processed successfully"

# Default arguments applied to every task in the DAG unless overridden
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['your_email@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    'my_first_dag',
    default_args=default_args,
    description='A simple tutorial DAG',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['example'],
) as dag:

    # Task 1: Print hello
    task1 = PythonOperator(
        task_id='print_hello',
        python_callable=print_hello,
    )

    # Task 2: Process data
    task2 = PythonOperator(
        task_id='process_data',
        python_callable=process_data,
    )

    # Task 3: Bash command
    task3 = BashOperator(
        task_id='bash_example',
        bash_command='echo "Task 3 completed"',
    )

    # Set dependencies
    task1 >> task2 >> task3
```

> `schedule_interval` is the classic Airflow 1.x/2.x parameter name. Airflow 2.4+ introduced `schedule` as its replacement (accepts cron strings, `timedelta`, datasets, or presets like `'@daily'`); `schedule_interval` still works but `schedule` is the forward-compatible name.

## Airflow Scheduler Deep Dive

### How the Scheduler Works
1. **Parses DAGs** — reads and processes all DAG files in the DAGs folder.
2. **Checks the schedule** — determines which DAG runs are due to be created based on each DAG's schedule and `start_date`/`catchup` settings.
3. **Creates task instances** — generates the task instances for a triggered DAG run once their upstream dependencies are satisfied.
4. **Hands off to the executor** — queues those task instances for the configured executor to actually run.

### Scheduler Configuration
```ini
# airflow.cfg important settings

[scheduler]
# How often the scheduler loop runs / checks for new work (seconds)
scheduler_heartbeat_sec = 5

# How often the scheduler rescans the DAGs folder for new or changed files (seconds)
dag_dir_list_interval = 300

# Max number of new DAG runs the scheduler creates per scheduling loop, across all DAGs
max_dagruns_to_create_per_loop = 10

# Timeout (seconds) for importing/parsing a single DAG file — not a sync interval
dagbag_import_timeout = 30
```

### Starting and Managing the Scheduler
```bash
# Start scheduler
airflow scheduler

# Start scheduler as a daemon
airflow scheduler -D

# Check scheduler status
airflow jobs check --job-type SchedulerJob

# View scheduler logs
tail -f ~/airflow/logs/scheduler/{date}/scheduler.log
```

### Common Scheduler Commands
```bash
# Test a specific task (runs it directly, bypassing the scheduler/dependencies)
airflow tasks test my_dag_id my_task_id 2023-01-01

# List DAGs
airflow dags list

# Pause/unpause a DAG
airflow dags pause my_dag_id
airflow dags unpause my_dag_id

# Trigger a DAG run manually
airflow dags trigger my_dag_id

# Backfill a DAG over a date range
airflow dags backfill -s 2023-01-01 -e 2023-01-07 my_dag_id
```

## Common Operators

For the full operator reference with more examples, see [[Data Engineering Role Notes/Airflow Scheduler/Operators in Airflow|Operators in Airflow]]. The core ones every beginner should know first:

### PythonOperator
```python
from airflow.operators.python import PythonOperator

def process_data(**context):
    # Access execution date via the auto-injected context dict
    execution_date = context['execution_date']
    print(f"Processing data for {execution_date}")

    # Your processing logic here
    return "Success"

process_task = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
    op_kwargs={'param1': 'value1'},  # Additional arguments passed to the callable
)
```

> In Airflow 2.x, Jinja/context variables (`execution_date`, `ti`, `dag_run`, etc.) are passed to the callable automatically via `**kwargs` — the old `provide_context=True` flag from Airflow 1.x is a no-op and can be omitted.

### BashOperator
```python
from airflow.operators.bash import BashOperator

bash_task = BashOperator(
    task_id='bash_task',
    bash_command='echo "Hello World" && python my_script.py',
    env={'CUSTOM_VAR': 'value'},  # Set environment variables for the command
)
```

### EmailOperator
```python
from airflow.operators.email import EmailOperator

email_task = EmailOperator(
    task_id='send_email',
    to='recipient@example.com',
    subject='Airflow Notification',
    html_content='<p>Task completed successfully!</p>',
)
```

### File Sensors
```python
from airflow.sensors.filesystem import FileSensor

file_sensor = FileSensor(
    task_id='wait_for_file',
    filepath='/path/to/file.csv',
    poke_interval=30,  # Check every 30 seconds
    timeout=60 * 60,   # Time out after 1 hour
    mode='poke',       # Occupies a worker slot for the whole wait
)
```

> Tip: for sensors that wait a long time, use `mode='reschedule'` instead of the default `mode='poke'` — it frees the worker slot between checks instead of blocking it, which matters a lot once you have more than a handful of sensors running concurrently.

## Task Dependencies

### Setting Dependencies
```python
# Method 1: bitshift operators (most common)
task1 >> task2 >> task3

# Method 2: set_downstream / set_upstream
task1.set_downstream(task2)
task2.set_upstream(task1)

# Method 3: chain() helper, useful for long linear sequences
from airflow.models.baseoperator import chain
chain(task1, task2, task3)

# Fan-out / fan-in dependencies
(task1 >> [task2, task3] >> task4)
(task2 >> task5)
(task3 >> task6)
```

### Conditional Execution
```python
from airflow.operators.python import BranchPythonOperator

def choose_branch(**context):
    if context['execution_date'].weekday() < 5:
        return 'weekday_task'
    else:
        return 'weekend_task'

branch_task = BranchPythonOperator(
    task_id='branch_task',
    python_callable=choose_branch,
)

weekday_task = PythonOperator(task_id='weekday_task', python_callable=weekday_func)
weekend_task = PythonOperator(task_id='weekend_task', python_callable=weekend_func)

branch_task >> [weekday_task, weekend_task]
```

`BranchPythonOperator` returns the `task_id` (or list of `task_id`s) to run next; every other downstream task is marked `skipped`, not run.

## Monitoring and Troubleshooting

### Web UI Components
- **DAGs View** — overview of all DAGs and their recent run status.
- **Grid View** (formerly "Tree View" in older Airflow UI versions) — visual timeline of task runs per DAG run.
- **Graph View** — the DAG's structure with live task status.
- **Task Duration** — historical run-time metrics per task.
- **Gantt Chart** — timeline of task execution within a single DAG run, useful for spotting bottlenecks.
- **Code View** — inspects the DAG's source file directly from the UI.

### Common Scheduler Issues

#### DAG Not Triggering
```python
# Check schedule_interval / schedule and start_date
with DAG(
    'my_dag',
    schedule_interval='0 2 * * *',  # 2 AM daily (cron format)
    # or
    # schedule_interval=timedelta(hours=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:
    ...
```
A DAG with `catchup=False` and a `start_date` in the past still won't necessarily fire immediately — the scheduler only creates a run once the *scheduled interval itself* has elapsed relative to `start_date`.

#### Tasks Stuck in Queue
```ini
# In airflow.cfg
[core]
executor = LocalExecutor  # or CeleryExecutor / KubernetesExecutor

# Check parallelization settings
parallelism = 32
max_active_tasks_per_dag = 16       # renamed from dag_concurrency in Airflow 2.2+
max_active_runs_per_dag = 16
```
If tasks sit in `queued` without moving to `running`, the usual suspects are: `parallelism`/`max_active_tasks_per_dag` caps already saturated, not enough executor workers/slots, or (for Celery/Kubernetes) the workers themselves not being reachable.

#### DAG Parsing Errors
```bash
# Check DAG files for syntax errors directly
python /path/to/your_dag.py

# Confirm Airflow itself can import it
airflow dags list

# View DAG import errors in the UI (DAGs list page) or in the scheduler logs
```

### Logging and Debugging
```python
import logging

def my_task_function(**context):
    logger = logging.getLogger(__name__)

    # Log messages at different levels
    logger.info("Task started")
    logger.warning("This is a warning")
    logger.error("This is an error")

    # Access the task instance from context
    ti = context['ti']
    logger.info(f"Task id: {ti.task_id}")

    # Push/pull values through XCom to pass small data between tasks
    ti.xcom_push(key='result', value='my_result')
    previous_result = ti.xcom_pull(task_ids='previous_task', key='result')
```

## Best Practices

### 1. DAG Design — Idempotency
```python
# Good: idempotent — re-running for the same date always produces the same result
def process_data(**context):
    date = context['execution_date'].strftime('%Y-%m-%d')
    # Process data for this specific date
    return f"Processed data for {date}"

# Bad: not idempotent — depends on "whatever is latest right now",
# so retries or backfills silently reprocess the wrong data
def process_data():
    process_latest_data()
```

### 2. Error Handling
```python
from airflow.exceptions import AirflowException

def robust_task(**context):
    logger = logging.getLogger(__name__)
    try:
        result = perform_operation()
        if not result:
            raise AirflowException("Operation failed")
        return result
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        raise
```

### 3. Resource Management
```python
task = PythonOperator(
    task_id='heavy_task',
    python_callable=heavy_processing,
    execution_timeout=timedelta(hours=2),
    retries=3,
    retry_delay=timedelta(minutes=5),
    pool='heavy_tasks_pool',   # Cap concurrency for resource-hungry tasks via pools
    priority_weight=2,         # Higher weight = scheduled ahead of lower-weight tasks
)
```

### 4. Configuration Management
```python
from airflow.models import Variable

# Store configuration in Airflow Variables instead of hardcoding
database_url = Variable.get("database_url")
api_key = Variable.get("api_key", default_var="default_value")

def task_with_config(**context):
    config = Variable.get("my_dag_config", deserialize_json=True)
    # Use config in the task
```
Avoid calling `Variable.get()` at DAG *parse* time for anything expensive or frequently-changing — it runs on every scheduler parse cycle, not just at task execution time.

### 5. Testing
```python
# Test DAG structure
def test_dag_structure():
    dag = my_dag
    assert len(dag.tasks) == expected_task_count
    assert dag.schedule_interval == timedelta(days=1)

# Test individual task logic in isolation from Airflow
def test_task_logic():
    result = my_task_function()
    assert result == expected_result
```

## Advanced Scheduler Features

### Executors
- **LocalExecutor** — runs tasks as subprocesses on the same machine as the scheduler. Simple, no extra infra, good for dev and small single-node deployments.
- **CeleryExecutor** — distributes tasks to a pool of remote worker processes via a message broker (Redis or RabbitMQ). Scales horizontally across machines.
- **KubernetesExecutor** — launches a new Kubernetes pod per task. Strong isolation and elastic scaling, at the cost of per-task pod startup overhead.

### SLA Misses
```python
with DAG(
    'my_dag',
    default_args={
        'sla': timedelta(hours=2)  # SLA for every task in the DAG unless overridden
    },
) as dag:

    task_with_sla = PythonOperator(
        task_id='critical_task',
        python_callable=critical_function,
        sla=timedelta(minutes=30),  # Task-specific SLA, overrides the DAG default
    )
```
An SLA miss doesn't stop or fail the task — it just triggers an SLA-miss email (if configured) and shows up in the UI/`sla_miss_callback`, so it's a monitoring signal, not an enforcement mechanism.

### Dynamic DAG Generation
```python
from airflow.operators.empty import EmptyOperator

def create_dag(dag_id, schedule, default_args):
    with DAG(dag_id, schedule_interval=schedule, default_args=default_args) as dag:
        start = EmptyOperator(task_id='start')
        end = EmptyOperator(task_id='end')

        start >> end

    return dag

# Generate multiple similar DAGs
for i in range(5):
    dag_id = f'dynamic_dag_{i}'
    globals()[dag_id] = create_dag(dag_id, '@daily', default_args)
```
Gotcha: every DAG file the scheduler parses runs its top-level Python on *every* parse cycle. A loop that generates many DAGs (or that does expensive work — DB calls, API calls — at module level) directly slows down DAG parsing and, at scale, scheduler throughput. Prefer generating DAGs from lightweight static config (a list/JSON/YAML) rather than dynamic lookups at parse time.

## Conclusion

1. **Start simple** — begin with basic DAGs and add complexity gradually.
2. **Monitor regularly** — use the web UI to watch DAG runs and task status.
3. **Test thoroughly** — validate DAGs and task logic before deploying to production.
4. **Follow best practices** — idempotency, explicit error handling, and structured logging.
5. **Scale gradually** — start with `LocalExecutor` and move to `CeleryExecutor`/`KubernetesExecutor` only once you actually need distributed execution.

The scheduler is powerful but needs careful configuration and monitoring — the concepts above (parsing cadence, executor choice, concurrency limits) are what most real-world scheduling issues trace back to.

## Additional Resources

- [Official Airflow Documentation](https://airflow.apache.org/docs/)
- [Airflow GitHub Repository](https://github.com/apache/airflow)
- [Airflow Slack Community](https://apache-airflow.slack.com)

## 🔗 Related Notes
- [[Data Engineering Role Notes/Airflow Scheduler/Airflow Installation|🚀 Apache Airflow: Complete Installation & Troubleshooting Guide (Local Virtualenv)]]
- [[Data Engineering Role Notes/Airflow Scheduler/Operators in Airflow|Operators in Airflow]]
- [[Data Engineering Role Notes/Airflow Scheduler/Airflow Images/Airflow Images|Airflow Images]]

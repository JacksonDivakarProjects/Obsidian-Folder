# Operators in Airflow

A practical reference for the most widely used Apache Airflow operators. For each: a definition, its typical applications, and a minimal realistic example.

---

## 🧩 PythonOperator

**Definition:** Executes a Python function within a DAG task. One of the most common operators for data processing and transformation logic.

**Applications:**
- Running Python-based ETL logic.
- Making API calls or manipulating files.
- Data validation or preprocessing before loading.

**Example:**
```python
from airflow.operators.python import PythonOperator

def process_data():
    print("Processing dataset...")

task = PythonOperator(
    task_id='data_processing',
    python_callable=process_data,
    dag=dag
)
```

---

## 🧩 BashOperator

**Definition:** Executes shell commands or scripts directly from a task.

**Applications:**
- Running shell scripts for file movement or system commands.
- Triggering command-line tools (e.g. `aws s3 cp`, `curl`).
- Checking system health or cleaning up temporary files.

**Example:**
```python
from airflow.operators.bash import BashOperator

task = BashOperator(
    task_id='move_files',
    bash_command='mv /tmp/data.csv /opt/data/',
    dag=dag
)
```

---

## 🧩 EmailOperator

**Definition:** Sends an email notification or report from a DAG task.

**Applications:**
- Sending pipeline success/failure alerts.
- Sharing data-validation summaries.
- Emailing daily or weekly analytics reports.

**Example:**
```python
from airflow.operators.email import EmailOperator

email_task = EmailOperator(
    task_id='notify_team',
    to='team@company.com',
    subject='Pipeline Completed',
    html_content='<h3>All tasks finished successfully.</h3>',
    dag=dag
)
```

---

## 🧩 EmptyOperator (formerly DummyOperator)

**Definition:** A no-op placeholder used purely for DAG structuring. `DummyOperator` was renamed to `EmptyOperator` in Airflow 2.x; the old name still works via an alias but is deprecated.

**Applications:**
- Marking explicit start/end points in a DAG.
- Creating branching or grouping anchor points.
- Sketching out DAG flow/shape before the real task logic exists.

**Example:**
```python
from airflow.operators.empty import EmptyOperator

start = EmptyOperator(task_id='start', dag=dag)
end = EmptyOperator(task_id='end', dag=dag)
```

---

## 🧩 BranchPythonOperator

**Definition:** Creates conditional branching in a DAG — a Python callable decides which downstream task ID(s) to run next. Every task not returned is marked `skipped`.

**Applications:**
- Dynamic task routing based on data availability.
- Conditional ETL flow (e.g. only process if new data exists).
- Multi-path workflows driven by upstream results.

**Example:**
```python
from airflow.operators.python import BranchPythonOperator

def choose_path():
    return 'task_A' if True else 'task_B'

branch = BranchPythonOperator(
    task_id='branch_logic',
    python_callable=choose_path,
    dag=dag
)
```

---

## 🧩 SQL Operators (PostgresOperator, MySqlOperator, etc.)

**Definition:** Execute SQL statements against a database (Postgres, MySQL, and others), via the relevant provider package.

**Applications:**
- Running DDL/DML automatically as part of a pipeline.
- Loading transformed data into database tables.
- Cleaning up or updating tables before/after an ETL run.

**Example:**
```python
from airflow.providers.postgres.operators.postgres import PostgresOperator

task = PostgresOperator(
    task_id='load_to_table',
    postgres_conn_id='postgres_conn',
    sql='INSERT INTO sales SELECT * FROM staging_sales;',
    dag=dag
)
```

---

## 🧩 Cloud Storage Operators (S3, GCS, Azure)

**Definition:** Operators for cloud storage interactions — upload, download, copy, delete, list — e.g. `S3CreateObjectOperator`, `GCSListObjectsOperator`, each shipped in the matching provider package (`apache-airflow-providers-amazon`, `-google`, `-microsoft-azure`).

**Applications:**
- Moving data between local storage and the cloud.
- Triggering downstream pipelines when new data lands in a bucket.
- Archiving old data files.

**Example:**
```python
from airflow.providers.amazon.aws.operators.s3 import S3CreateObjectOperator

upload = S3CreateObjectOperator(
    task_id='upload_to_s3',
    s3_bucket='my-data-bucket',
    s3_key='raw/data.csv',
    data='sample content',
    replace=True,
    dag=dag
)
```

---

## 🧩 DockerOperator

**Definition:** Runs a task inside a Docker container for environment isolation. Ships in the `apache-airflow-providers-docker` package; the pre-2.0 `airflow.operators.docker_operator` path is obsolete.

**Applications:**
- Running ML models or scripts with dependencies that don't belong in the Airflow environment itself.
- Containerizing ETL steps for consistent, reproducible runs.
- Executing code from pre-built Docker images.

**Example:**
```python
from airflow.providers.docker.operators.docker import DockerOperator

task = DockerOperator(
    task_id='run_docker_task',
    image='python:3.9',
    command='python script.py',
    dag=dag
)
```

---

## 🧩 Sensor Operators (FileSensor, S3KeySensor, ExternalTaskSensor, ...)

**Definition:** Wait for a condition or external event before letting the DAG proceed.

**Applications:**
- Waiting for a file to land in cloud storage.
- Ensuring an upstream task/DAG has finished before continuing.
- Synchronizing dependencies across pipelines.

**Example:**
```python
from airflow.sensors.filesystem import FileSensor

wait_for_file = FileSensor(
    task_id='wait_for_data',
    filepath='/opt/data/input.csv',
    poke_interval=60,
    dag=dag
)
```

Tip: the default `mode='poke'` occupies a worker slot for the entire wait. For long waits, `mode='reschedule'` releases the slot between checks — important once several sensors run concurrently.

---

## 🧩 TriggerDagRunOperator

**Definition:** Triggers a run of another DAG from within the current DAG.

**Applications:**
- Chaining multiple DAGs together.
- Modularizing a large workflow into smaller, independently-owned DAGs.
- Kicking off dependent processes dynamically.

**Example:**
```python
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

trigger = TriggerDagRunOperator(
    task_id='trigger_downstream_dag',
    trigger_dag_id='data_cleanup_dag',
    dag=dag
)
```

---

## Summary Table

| Operator | Core Purpose | Example Use |
|---|---|---|
| PythonOperator | Run Python code | ETL, API calls |
| BashOperator | Run shell commands | Move files, cleanup |
| EmailOperator | Send email | Alerts, reports |
| EmptyOperator | Structural placeholder | Start/end anchors |
| BranchPythonOperator | Conditional branching | Dynamic DAG path |
| SQL/PostgresOperator | Run SQL | Load/transform |
| S3/GCS Operators | Cloud file ops | Upload/download |
| DockerOperator | Containerized run | ML tasks, isolated deps |
| Sensor Operators | Wait for a condition | File arrival, event, upstream task |
| TriggerDagRunOperator | Trigger another DAG | Chained/modular DAGs |

## 🔗 Related Notes
- [[Data Engineering Role Notes/Airflow Scheduler/Level -1 Airflow Scheduler Guide|Comprehensive Apache Airflow Scheduler Guide for Beginners]]
- [[Data Engineering Role Notes/Airflow Scheduler/Airflow Installation|🚀 Apache Airflow: Complete Installation & Troubleshooting Guide (Local Virtualenv)]]

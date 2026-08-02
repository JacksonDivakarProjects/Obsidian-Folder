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

Apache Airflow is an open-source platform to programmatically author, schedule, and monitor workflows. It allows you to define workflows as code, making them more maintainable, versionable, testable, and collaborative.

**Key Features:**
- Dynamic workflow generation
- Extensible through plugins
- Python-based
- Rich web UI
- Scalable

## Airflow Architecture

### Core Components:
1. **Scheduler** - Triggers scheduled workflows and submits tasks to executor
2. **Web Server** - Provides UI to inspect and manage workflows
3. **Executor** - Runs the tasks (LocalExecutor, CeleryExecutor, KubernetesExecutor)
4. **Metadata Database** - Stores workflow states, configuration, etc.
5. **DAGs Directory** - Contains your workflow definitions

## Installing Airflow

### Quick Installation
```bash
# Install Airflow
pip install apache-airflow

# Initialize database
airflow db init

# Create user
airflow users create \
    --username admin \
    --firstname FirstName \
    --lastname LastName \
    --role Admin \
    --email admin@example.com

# Start scheduler
airflow scheduler

# Start web server (in new terminal)
airflow webserver --port 8080
```

### Using Docker (Recommended)
```dockerfile
# docker-compose.yml
version: '3'
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow

  webserver:
    image: apache-airflow:2.5.0
    command: webserver
    ports:
      - "8080:8080"
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
```

## Core Concepts

### DAG (Directed Acyclic Graph)
A collection of tasks with directional dependencies.

### Task
A unit of work in a DAG.

### Operator
A template for a task (PythonOperator, BashOperator, etc.).

### Task Instance
A specific run of a task.

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

# Default arguments
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

## Airflow Scheduler Deep Dive

### How the Scheduler Works
1. **Parses DAGs** - Reads and processes all DAG files
2. **Checks Schedule** - Determines which DAG runs to trigger
3. **Creates Task Instances** - Generates task instances for execution
4. **Sends to Executor** - Queues tasks for execution

### Scheduler Configuration
```python
# airflow.cfg important settings

[scheduler]
# How often to check for new tasks (seconds)
scheduler_heartbeat_sec = 5

# How often to process DAG files (seconds)
dag_dir_list_interval = 300

# Maximum number of DAG runs per DAG to create per scheduler loop
max_dagruns_per_loop = 10

# How often to sync DAGs from filesystem (seconds)
dagbag_import_timeout = 30
```

### Starting and Managing Scheduler
```bash
# Start scheduler
airflow scheduler

# Start scheduler as daemon
airflow scheduler -D

# Check scheduler status
airflow jobs check --job-type SchedulerJob

# View scheduler logs
tail -f ~/airflow/logs/scheduler/{date}/scheduler.log
```

### Common Scheduler Commands
```bash
# Test a specific task
airflow tasks test my_dag_id my_task_id 2023-01-01

# List DAGs
airflow dags list

# Pause/Unpause DAG
airflow dags pause my_dag_id
airflow dags unpause my_dag_id

# Trigger DAG run
airflow dags trigger my_dag_id

# Backfill DAG
airflow dags backfill -s 2023-01-01 -e 2023-01-07 my_dag_id
```

## Common Operators

### PythonOperator
```python
from airflow.operators.python import PythonOperator

def process_data(**context):
    # Access execution date
    execution_date = context['execution_date']
    print(f"Processing data for {execution_date}")
    
    # Your processing logic here
    return "Success"

process_task = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
    provide_context=True,  # Passes context to function
    op_kwargs={'param1': 'value1'},  # Additional arguments
)
```

### BashOperator
```python
from airflow.operators.bash import BashOperator

bash_task = BashOperator(
    task_id='bash_task',
    bash_command='echo "Hello World" && python my_script.py',
    env={'CUSTOM_VAR': 'value'},  # Set environment variables
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
    timeout=60 * 60,   # Timeout after 1 hour
    mode='poke',
)
```

## Task Dependencies

### Setting Dependencies
```python
# Method 1: Using bitshift operators
task1 >> task2 >> task3

# Method 2: Using set_downstream/set_upstream
task1.set_downstream(task2)
task2.set_upstream(task1)

# Method 3: Using chain function
from airflow.models.baseoperator import chain
chain(task1, task2, task3)

# Complex dependencies
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
    provide_context=True,
)

weekday_task = PythonOperator(task_id='weekday_task', python_callable=weekday_func)
weekend_task = PythonOperator(task_id='weekend_task', python_callable=weekend_func)

branch_task >> [weekday_task, weekend_task]
```

## Monitoring and Troubleshooting

### Web UI Components
- **DAGs View**: Overview of all DAGs
- **Tree View**: Visual representation of task runs
- **Graph View**: DAG structure with task status
- **Task Duration**: Performance metrics
- **Gantt Chart**: Timeline of task execution
- **Code View**: DAG code inspection

### Common Scheduler Issues

#### DAG Not Triggering
```python
# Check schedule_interval
with DAG(
    'my_dag',
    schedule_interval='0 2 * * *',  # 2 AM daily (cron format)
    # or
    schedule_interval=timedelta(hours=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:
```

#### Tasks Stuck in Queue
```bash
# Check executor configuration
# In airflow.cfg
[core]
executor = LocalExecutor  # or CeleryExecutor

# Check parallelization settings
parallelism = 32
dag_concurrency = 16
max_active_runs_per_dag = 16
```

#### DAG Parsing Errors
```bash
# Check DAG files for syntax errors
python /path/to/your_dag.py

# Test DAG loading
airflow dags list

# View DAG import errors in UI or logs
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
    
    # Access task instance
    ti = context['ti']
    logger.info(f"Task id: {ti.task_id}")
    
    # Push/pull XCom values
    ti.xcom_push(key='result', value='my_result')
    previous_result = ti.xcom_pull(task_ids='previous_task', key='result')
```

## Best Practices

### 1. DAG Design
```python
# Good: Idempotent tasks
def process_data(**context):
    date = context['execution_date'].strftime('%Y-%m-%d')
    # Process data for specific date
    return f"Processed data for {date}"

# Bad: Non-idempotent tasks
def process_data():
    # Processes whatever data is available - not reproducible
    process_latest_data()
```

### 2. Error Handling
```python
from airflow.exceptions import AirflowException

def robust_task(**context):
    try:
        # Your task logic
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
# Set appropriate resources
task = PythonOperator(
    task_id='heavy_task',
    python_callable=heavy_processing,
    execution_timeout=timedelta(hours=2),
    retries=3,
    retry_delay=timedelta(minutes=5),
    pool='heavy_tasks_pool',  # Use resource pools
    priority_weight=2,
)
```

### 4. Configuration Management
```python
from airflow.models import Variable

# Store configuration in Airflow Variables
database_url = Variable.get("database_url")
api_key = Variable.get("api_key", default_var="default_value")

def task_with_config(**context):
    config = Variable.get("my_dag_config", deserialize_json=True)
    # Use config in task
```

### 5. Testing
```python
# Test DAG structure
def test_dag_structure():
    dag = my_dag
    assert len(dag.tasks) == expected_task_count
    assert dag.schedule_interval == timedelta(days=1)

# Test individual tasks
def test_task_logic():
    result = my_task_function()
    assert result == expected_result
```

## Advanced Scheduler Features

### Custom Executors
```python
# For high-volume workloads, consider:
# - CeleryExecutor (distributed)
# - KubernetesExecutor (containerized)
# - LocalExecutor (single machine)
```

### SLA Misses
```python
with DAG(
    'my_dag',
    default_args={
        'sla': timedelta(hours=2)  # SLA for entire DAG
    },
) as dag:
    
    task_with_sla = PythonOperator(
        task_id='critical_task',
        python_callable=critical_function,
        sla=timedelta(minutes=30),  # Task-specific SLA
    )
```

### Dynamic DAG Generation
```python
def create_dag(dag_id, schedule, default_args):
    with DAG(dag_id, schedule_interval=schedule, default_args=default_args) as dag:
        # Dynamically create tasks
        start = DummyOperator(task_id='start')
        end = DummyOperator(task_id='end')
        
        start >> end
    
    return dag

# Generate multiple similar DAGs
for i in range(5):
    dag_id = f'dynamic_dag_{i}'
    globals()[dag_id] = create_dag(dag_id, '@daily', default_args)
```

## Conclusion

This guide covers the essential aspects of Apache Airflow scheduler for beginners. Remember:

1. **Start Simple**: Begin with basic DAGs and gradually add complexity
2. **Monitor Regularly**: Use the web UI to monitor DAG runs and task status
3. **Test Thoroughly**: Test your DAGs and tasks before deploying to production
4. **Follow Best Practices**: Implement error handling, idempotency, and proper logging
5. **Scale Gradually**: Start with LocalExecutor and move to distributed executors as needed

The Airflow scheduler is powerful but requires careful configuration and monitoring. With practice, you'll be able to build robust, scalable data pipelines efficiently.

## Additional Resources

- [Official Airflow Documentation](https://airflow.apache.org/docs/)
- [Airflow GitHub Repository](https://github.com/apache/airflow)
- [Airflow Slack Community](https://apache-airflow.slack.com)

Happy scheduling! 🚀


## 🔗 Related Notes
- [[Data Engineering Role Notes/Airflow Scheduler/Airflow Installation|🚀 Apache Airflow: Complete Installation & Troubleshooting Guide (Local Virtualenv)]]
- [[Data Engineering Role Notes/Airflow Scheduler/Operators in Airflow|Operators in Airflow]]
- [[Data Engineering Role Notes/Airflow Scheduler/Airflow Images/Airflow Images|Airflow Images]]

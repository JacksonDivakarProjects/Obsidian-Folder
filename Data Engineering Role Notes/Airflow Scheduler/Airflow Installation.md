# 🚀 Apache Airflow: Complete Installation & Troubleshooting Guide (Local Virtualenv)

## Overview

Local setup of Apache Airflow using a Python virtual environment and `pip`, covering:

- Installing Airflow and its dependencies
- Initializing the metadata database
- Creating an admin user
- Starting the scheduler and webserver
- Handling stuck processes and stale PID files
- DAGs folder structure

> Recommended for: **Linux, WSL, or macOS** local setups — development, POCs, or personal projects. For production, prefer the official Docker Compose deployment or a managed service (MWAA, Cloud Composer, Astronomer).

---

## Step-by-Step Installation

### 🔧 Step 1: Install Prerequisites

```bash
sudo apt update
sudo apt install python3 python3-pip -y
pip3 install virtualenv
```

### 📁 Step 2: Create & Activate a Virtual Environment

```bash
mkdir airflow_project
cd airflow_project
virtualenv airflow_venv
source airflow_venv/bin/activate
```

### 📦 Step 3: Install Apache Airflow

Always install against the official **constraints file** for your Airflow + Python version — it pins compatible dependency versions and avoids the classic "pip resolves to a broken combination" problem.

```bash
AIRFLOW_VERSION=2.8.1
PYTHON_VERSION="$(python --version | cut -d ' ' -f 2 | cut -d '.' -f 1,2)"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
```

### 🛠️ Step 4: Set Environment Variable & Initialize the DB

```bash
export AIRFLOW_HOME=~/airflow
airflow db init
```

`AIRFLOW_HOME` is where Airflow writes `airflow.cfg`, its metadata DB (SQLite by default for local dev), logs, and where it looks for the `dags/` folder. Add the `export` line to your shell profile (`.bashrc`/`.zshrc`) so it persists across sessions — otherwise a fresh terminal falls back to the default `~/airflow`.

> `airflow db init` is the classic 1.x/early-2.x command. Airflow 2.7+ prefers `airflow db migrate`, which is idempotent and also safe to run when upgrading an existing metadata DB.

### 👤 Step 5: Create an Admin User

```bash
airflow users create \
  --username admin \
  --firstname Jack \
  --lastname Divakar \
  --role Admin \
  --email jack@example.com \
  --password admin123
```

### 🚀 Step 6: Start Airflow Services

Start the scheduler (terminal 1):

```bash
airflow scheduler
```

Start the webserver (terminal 2 — needs its own activated venv):

```bash
cd airflow_project
source airflow_venv/bin/activate
airflow webserver --port 8085
```

Visit **http://localhost:8085**.

Both processes need to keep running for Airflow to schedule work and serve the UI. In a real deployment they're managed by systemd, supervisor, or Docker rather than left in foreground terminals.

---

## 📂 DAGs Directory

Airflow loads DAGs from `~/airflow/dags` by default (controlled by the `[core] dags_folder` setting in `airflow.cfg`).

All `.py` DAG definition files must live under:

```bash
~/airflow/dags/
```

Example:

```bash
cp my_dag.py ~/airflow/dags/
```

The scheduler periodically rescans this folder (see `dag_dir_list_interval` in `airflow.cfg`), and the new DAG shows up in the web UI once parsed — no scheduler restart needed for a new DAG file, only for changes to `airflow.cfg` itself.

---

## ⛔️ Troubleshooting: When Airflow Gets Stuck

### 🔎 Step 1: Find Stuck Processes

```bash
ps aux | grep airflow
```

### 🔪 Step 2: Stop Processes — Graceful First, Then Force

Try a graceful stop (SIGTERM) before force-killing (SIGKILL) — SIGKILL gives the process no chance to clean up:

```bash
kill <PID>       # graceful (SIGTERM)
kill -9 <PID>    # force (SIGKILL), only if it doesn't respond
```

Or cleanly via the PID files Airflow writes on startup:

```bash
kill $(cat ~/airflow/airflow-webserver.pid)
kill $(cat ~/airflow/airflow-scheduler.pid)
```

### 🧹 Step 3: Remove Stale PID Files (if needed)

If a process died without cleaning up after itself, its stale PID file can block a fresh start:

```bash
rm -f ~/airflow/airflow-webserver.pid
rm -f ~/airflow/airflow-scheduler.pid
```

### ♻️ Step 4: Restart Services

```bash
source airflow_venv/bin/activate
airflow scheduler
airflow webserver --port 8085
```

---

## 🧬 Best Practices

| Practice | Purpose |
|---|---|
| Use a virtualenv | Keep Airflow's dependencies isolated from system Python |
| Install with the constraints file | Prevent dependency version conflicts |
| Set `AIRFLOW_HOME` explicitly | Keep config, logs, and DB in one known location |
| Try SIGTERM before SIGKILL | Give the process a chance to shut down cleanly |
| Remove stale PID files after a crash | Ensures a clean restart |
| Keep DAGs under `dags_folder` | Ensures they're auto-detected by the scheduler |

---

## 🔍 Quick Commands Reference

```bash
# Activate env
source airflow_venv/bin/activate

# Start services
airflow scheduler
airflow webserver --port 8085

# Stop services gracefully, then force if needed
kill $(cat ~/airflow/airflow-webserver.pid)
kill $(cat ~/airflow/airflow-scheduler.pid)

# Remove stale PIDs
rm -f ~/airflow/airflow-webserver.pid
rm -f ~/airflow/airflow-scheduler.pid

# Add a DAG
cp my_dag.py ~/airflow/dags/
```

---

## 📆 File Structure Snapshot

```
airflow_project/
├── airflow_venv/
└── airflow/ (~/airflow)
    ├── airflow.cfg
    ├── airflow.db
    ├── airflow-webserver.pid
    ├── airflow-scheduler.pid
    ├── dags/
    │   └── my_dag.py
    └── logs/
```

## 🔗 Related Notes
- [[Data Engineering Role Notes/Airflow Scheduler/Level -1 Airflow Scheduler Guide|Comprehensive Apache Airflow Scheduler Guide for Beginners]]
- [[Data Engineering Role Notes/Airflow Scheduler/Operators in Airflow|Operators in Airflow]]
- [[Data Engineering Role Notes/Airflow Scheduler/Airflow Scheduler|Airflow Scheduler]]

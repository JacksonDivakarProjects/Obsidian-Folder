# 🚀 Apache Airflow: Complete Installation & Troubleshooting Guide (Local Virtualenv)

---

## 🔹 Overview

This guide covers:

- Installing Airflow using Python virtual environment (`virtualenv`) and `pip`
    
- Initializing the Airflow database
    
- Creating an admin user
    
- Starting scheduler and webserver
    
- Handling stuck processes and PID files
    
- DAGs folder structure
    

> ✅ Recommended for: **Linux, WSL, or macOS local setups** for development, POCs, or personal projects.

---

## ✅ Step-by-Step Installation

### 🔧 Step 1: Install Prerequisites

```bash
sudo apt update
sudo apt install python3 python3-pip -y
pip3 install virtualenv
```

---

### 📁 Step 2: Create & Activate Virtual Environment

```bash
mkdir airflow_project
cd airflow_project
virtualenv airflow_venv
source airflow_venv/bin/activate
```

---

### 📦 Step 3: Install Apache Airflow

```bash
AIRFLOW_VERSION=2.8.1
PYTHON_VERSION="$(python --version | cut -d ' ' -f 2 | cut -d '.' -f 1,2)"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
```

---

### 🛠️ Step 4: Set Environment & Initialize DB

```bash
export AIRFLOW_HOME=~/airflow
airflow db init
```

---

### 👤 Step 5: Create Admin User

```bash
airflow users create \
  --username admin \
  --firstname Jack \
  --lastname Divakar \
  --role Admin \
  --email jack@example.com \
  --password admin123
```

---

### 🚀 Step 6: Start Airflow Services

Start scheduler (terminal 1):

```bash
airflow scheduler
```

Start webserver (terminal 2):

```bash
cd airflow_project
source airflow_venv/bin/activate
airflow webserver --port 8085
```

Visit: **[http://localhost:8085](http://localhost:8085/)**

---

## 📂 DAGs Directory

Airflow loads DAGs from the `~/airflow/dags` directory by default.

- All `.py` DAG files must be placed in:
    

```bash
~/airflow/dags/
```

Example:

```bash
cp my_dag.py ~/airflow/dags/
```

Airflow will automatically detect and list the DAGs in the web UI.

---

## ⛔️ Troubleshooting: When Airflow Gets Stuck

### 🔎 Step 1: Find Stuck Processes

```bash
ps aux | grep airflow
```

### 🔪 Step 2: Kill Processes

```bash
kill -9 <PID>
```

OR cleanly via PID file:

```bash
kill $(cat ~/airflow/airflow-webserver.pid)
kill $(cat ~/airflow/airflow-scheduler.pid)
```

### 🛃 Step 3: Remove PID Files (if needed)

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

|Practice|Purpose|
|---|---|
|Use virtualenv|Keep dependencies isolated|
|Use constraints file|Prevent version conflicts|
|Set AIRFLOW_HOME|Organize config and logs|
|Kill PID files on crash|Clean restart when stuck|
|Place DAGs in `~/airflow/dags`|Ensures DAGs are auto-detected|

---

## 🔍 Quick Commands Reference

```bash
# Activate env
source airflow_venv/bin/activate

# Start services
airflow scheduler
airflow webserver --port 8085

# Kill stuck services
kill $(cat ~/airflow/airflow-webserver.pid)
kill $(cat ~/airflow/airflow-scheduler.pid)

# Remove stale PIDs
rm -f ~/airflow/airflow-webserver.pid
rm -f ~/airflow/airflow-scheduler.pid

# Add DAGs
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

---

Let me know if you want this exported as a PDF or Markdown for Obsidian or GitHub.
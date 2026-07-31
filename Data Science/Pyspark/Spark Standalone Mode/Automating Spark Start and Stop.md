Perfect, Jack 👍 Let’s lock this down into a **refined, final note** that you can always refer back to.

---

# 🚀 Spark Standalone Cluster on One Machine (Multi-Worker)

This guide sets up a **Spark master + multiple workers** on your laptop, with simple **start/stop aliases**.

---

## 1️⃣ Create Start Script

File: `~/spark-cluster-start.sh`

```bash
#!/bin/bash
MASTER_URL="spark://localhost:7077"
NUM_WORKERS=${1:-2}    # default: 2 workers
CORES=2
MEMORY=2G

echo "🚀 Starting Spark master..."
$SPARK_HOME/sbin/start-master.sh

sleep 2  # give master a moment to start

for i in $(seq 1 $NUM_WORKERS); do
  echo "🚀 Starting worker $i..."
  SPARK_WORKER_DIR=/tmp/worker$i \
  SPARK_LOG_DIR=/tmp/worker$i-logs \
  SPARK_PID_DIR=/tmp/worker$i-pids \
  $SPARK_HOME/sbin/start-worker.sh $MASTER_URL -c $CORES -m $MEMORY
done

echo "✅ Spark cluster started with 1 master + $NUM_WORKERS workers"
echo "👉 Master UI: http://localhost:8080"
```

---

## 2️⃣ Create Stop Script

File: `~/spark-cluster-stop.sh`

```bash
#!/bin/bash
echo "🛑 Stopping all Spark workers..."
for pid in $(jps | grep Worker | awk '{print $1}'); do
  kill -9 $pid
done

echo "🛑 Stopping Spark master..."
for pid in $(jps | grep Master | awk '{print $1}'); do
  kill -9 $pid
done

echo "✅ Spark cluster stopped"
```

---

## 3️⃣ Make Scripts Executable

```bash
chmod +x ~/spark-cluster-start.sh
chmod +x ~/spark-cluster-stop.sh
```

---

## 4️⃣ Add Aliases

Edit `~/.bashrc` (or `~/.zshrc`):

```bash
alias spark-start="~/spark-cluster-start.sh"
alias spark-stop="~/spark-cluster-stop.sh"
alias spark-status="jps | egrep 'Master|Worker'"
```

Reload:

```bash
source ~/.bashrc
```

---

## 5️⃣ Usage

Start cluster (1 master + 3 workers):

```bash
spark-start 3
```

Stop cluster:

```bash
spark-stop
```

Check status:

```bash
spark-status
```

---

## 6️⃣ Verify in Web UI

- Master UI → [http://localhost:8080](http://localhost:8080/)
    
- Each worker gets its own Web UI (8081, 8082, 8083, …).
    

---

✅ With this setup, you now have a **repeatable Spark standalone cluster** on your laptop:

- 1 command to start,
    
- 1 command to stop,
    
- logs isolated per worker,
    
- no PID collisions.
    

---

Jack, do you also want me to extend the **start script** so you can customize cores and memory per worker _on the fly_ (e.g. `spark-start 3 4 6G` → 3 workers, 4 cores each, 6 GB memory)?
# 🚀 Comprehensive Guide: Spark Standalone (Multiple Workers, Single Machine)

---

## 1. Prerequisites Installation

### Install Java (OpenJDK 11)

```bash
sudo apt update
sudo apt install openjdk-11-jdk -y
```

Verify installation:
```bash
java -version
javac -version
```

### Set Up Python Virtual Environment

```bash
python3 -m venv ~/pyenv
source ~/pyenv/bin/activate
pip install --upgrade pip
pip install "pyspark==3.5.1"
```

---

## 2. Download and Install Spark

```bash
mkdir -p ~/apps && cd ~/apps
wget https://archive.apache.org/dist/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz
tar -xzf spark-3.5.1-bin-hadoop3.tgz
ln -sfn spark-3.5.1-bin-hadoop3 spark
```

---

## 3. Environment Configuration

### Permanent Environment Variables

Add to your `~/.bashrc`:
```bash
# Java configuration
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Spark configuration
export SPARK_HOME=$HOME/apps/spark
export PATH=$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH

# Python configuration for Spark
export PYSPARK_PYTHON=$HOME/pyenv/bin/python
export PYSPARK_DRIVER_PYTHON=$HOME/pyenv/bin/python
```

### Virtual Environment Activation Script

Add to your virtual environment's `activate` script (`~/pyenv/bin/activate`):
```bash
# Spark environment variables
export SPARK_HOME=$HOME/apps/spark
export PATH=$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH
export PYSPARK_PYTHON=$HOME/pyenv/bin/python
export PYSPARK_DRIVER_PYTHON=$HOME/pyenv/bin/python
```

Apply changes:
```bash
source ~/.bashrc
source ~/pyenv/bin/activate
```

---

## 4. Spark Configuration

### Create spark-env.sh

```bash
cd $SPARK_HOME/conf
cp spark-env.sh.template spark-env.sh
```

Edit `spark-env.sh`:
```bash
# Java Home
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Master host
export SPARK_MASTER_HOST=localhost

# Python executable
export PYSPARK_PYTHON=$HOME/pyenv/bin/python

# Log directory (optional)
export SPARK_LOG_DIR=$HOME/spark_logs
```

Create log directory:
```bash
mkdir -p $HOME/spark_logs
```

---

## 5. Start Spark Cluster

### Start Master Server

```bash
$SPARK_HOME/sbin/start-master.sh
```

Verify master is running:
```bash
jps | grep Master
```

Master Web UI: [http://localhost:8080](http://localhost:8080)
Note the master URL (e.g., `spark://localhost:7077`)

### Start Worker Instances

Create separate working directories:
```bash
mkdir -p /tmp/worker1 /tmp/worker2
```

Start first worker (2 cores, 4GB memory):
```bash
SPARK_WORKER_DIR=/tmp/worker1 \
$SPARK_HOME/sbin/start-worker.sh \
spark://localhost:7077 \
-c 2 -m 4g \
--webui-port 8081
```

Start second worker (2 cores, 4GB memory):
```bash
SPARK_WORKER_DIR=/tmp/worker2 \
$SPARK_HOME/sbin/start-worker.sh \
spark://localhost:7077 \
-c 2 -m 4g \
--webui-port 8082
```

Verify workers are running:
```bash
jps | grep Worker
```

Worker Web UIs: 
- Worker 1: [http://localhost:8081](http://localhost:8081)
- Worker 2: [http://localhost:8082](http://localhost:8082)

---

## 6. Test the Cluster

### Submit a Sample Job

```bash
$SPARK_HOME/bin/spark-submit \
  --master spark://localhost:7077 \
  --executor-cores 2 \
  --executor-memory 2g \
  $SPARK_HOME/examples/src/main/python/pi.py 100
```

### Interactive PySpark Shell

```bash
$SPARK_HOME/bin/pyspark \
  --master spark://localhost:7077 \
  --executor-cores 2 \
  --executor-memory 2g
```

Test in the shell:
```python
sc.parallelize(range(1000)).count()
```

---

## 7. Stop the Cluster

### Stop Workers

```bash
$SPARK_HOME/sbin/stop-worker.sh
```

### Stop Master

```bash
$SPARK_HOME/sbin/stop-master.sh
```

### Force Stop (if needed)

```bash
jps | grep -E "Master|Worker" | awk '{print $1}' | xargs kill -9
```

Clean up temporary directories:
```bash
rm -rf /tmp/worker1 /tmp/worker2
```

---

## 8. 🔧 Troubleshooting Checklist

### Common Issues and Solutions

1. **Java Not Found**
   ```bash
   # Check Java installation
   update-alternatives --config java
   # Set JAVA_HOME explicitly if needed
   ```

2. **Port Conflicts**
   ```bash
   # Check if ports 8080, 8081, 8082 are in use
   netstat -tulpn | grep :808
   # Use different ports if needed
   ```

3. **Permission Issues**
   ```bash
   # Ensure proper permissions on directories
   chmod -R 755 $HOME/apps
   chmod -R 755 /tmp/worker*
   ```

4. **Worker Not Connecting to Master**
   ```bash
   # Check master URL
   grep "spark://" $SPARK_HOME/logs/*.out
   # Verify master is running
   jps | grep Master
   ```

5. **Python Path Issues**
   ```bash
   # Verify Python paths
   echo $PYSPARK_PYTHON
   which python
   # They should match
   ```

6. **Memory Issues**
   ```bash
   # Reduce memory allocation if needed
   SPARK_WORKER_DIR=/tmp/worker1 $SPARK_HOME/sbin/start-worker.sh spark://localhost:7077 -c 1 -m 2g
   ```

7. **View Logs for Debugging**
   ```bash
   # Check master logs
   tail -f $SPARK_HOME/logs/spark-*-master-*.out
   
   # Check worker logs
   tail -f $SPARK_HOME/logs/spark-*-worker-*.out
   ```

8. **Firewall Issues (if any)**
   ```bash
   # Disable firewall temporarily for testing
   sudo ufw disable
   ```

---

## 9. Quick Reference Commands

| Command | Purpose |
|---------|---------|
| `jps` | Check Java processes |
| `start-master.sh` | Start Spark master |
| `start-worker.sh <master-url>` | Start Spark worker |
| `spark-submit` | Submit a job to cluster |
| `pyspark` | Start interactive shell |
| `stop-master.sh` | Stop Spark master |
| `stop-worker.sh` | Stop Spark workers |

---

## ✅ Completion Checklist

- [ ] Java 11 installed and verified
- [ ] Python virtual environment created and activated
- [ ] Spark downloaded and extracted
- [ ] Environment variables configured
- [ ] Spark configuration file set up
- [ ] Master server started successfully
- [ ] Two worker instances running
- [ ] Test job completed successfully
- [ ] Web UIs accessible

This comprehensive guide provides everything needed to install, configure, and run a Spark Standalone cluster with multiple workers on a single machine, along with troubleshooting tips for common issues.
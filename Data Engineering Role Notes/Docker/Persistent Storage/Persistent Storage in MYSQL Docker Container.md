# Persistent Storage in a MySQL Docker Container

## Why This Matters

Containers are ephemeral by design: when a container is removed, everything written to its writable layer is lost. For a database like MySQL, that means all your data disappears the moment you run `docker rm`. **Docker volumes** solve this by storing data outside the container's lifecycle, on the host, so it survives container restarts, removals, and even upgrades to a new image version.

## Pull vs. Build

- **Pull** — download the official, pre-built MySQL image from Docker Hub. This is what you want 99% of the time.
- **Build your own** — write a custom Dockerfile only when you need something the official image doesn't provide (custom config baked in, extra tooling, etc.).

You don't need to run `docker pull` explicitly — `docker run` automatically pulls the image if it isn't already present locally. Pulling first just makes the download step visible and separate from the run step.

```bash
# Explicit pull (optional)
docker pull mysql:latest
```

## Step-by-Step: Run MySQL with a Persistent Volume

### 1. Create the named volume
```bash
docker volume create mysql-data
```

### 2. Run the container, mounting the volume
```bash
docker run -d \
  --name mysql-db \
  -p 3306:3306 \
  -v mysql-data:/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=MyStrongPassword123! \
  mysql:latest
```
If the image isn't local yet, this pulls it automatically before starting the container.

### 3. Verify it's running
```bash
docker ps
```

### 4. Check the logs until MySQL is ready
```bash
docker logs mysql-db
```
Wait for a line like:
```
2023-... [Server] /usr/sbin/mysqld: ready for connections.
```
That confirms MySQL has finished initializing and will accept connections.

### 5. Connect and create test data
```bash
docker exec -it mysql-db mysql -u root -p
# Enter password: MyStrongPassword123!
```
```sql
CREATE DATABASE test_db;
USE test_db;
CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100));
INSERT INTO users (name) VALUES ('Alice'), ('Bob');
SELECT * FROM users;
EXIT;
```

### 6. Prove persistence: destroy and recreate the container
```bash
docker stop mysql-db
docker rm mysql-db

# Start a brand-new container, reusing the SAME volume
docker run -d \
  --name mysql-db-new \
  -p 3306:3306 \
  -v mysql-data:/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=MyStrongPassword123! \
  mysql:latest
```

### 7. Confirm the data survived
```bash
docker exec -it mysql-db-new mysql -u root -p
```
```sql
USE test_db;
SELECT * FROM users;  -- Alice and Bob are still there
EXIT;
```

The container was fully destroyed and rebuilt, but because the data lived in the `mysql-data` volume (not inside the container's own filesystem), nothing was lost.

## Command Reference

| Command | What It Does |
|---------|--------------|
| `docker pull mysql:latest` | Downloads the MySQL image from Docker Hub |
| `docker volume create mysql-data` | Creates a named, persistent storage area managed by Docker |
| `docker volume ls` | Lists all volumes on the host |
| `docker volume inspect mysql-data` | Shows where the volume's data actually lives on the host filesystem |
| `docker run ... -v mysql-data:/var/lib/mysql ...` | Mounts the volume at MySQL's data directory inside the container |

## Named Volumes vs. Bind Mounts

The `-v mysql-data:/var/lib/mysql` syntax above uses a **named volume** — Docker manages where the data actually lives on the host, and you refer to it by name (`mysql-data`). The alternative is a **bind mount**, where you point directly at a host path:
```bash
-v /host/path/mysql-data:/var/lib/mysql
```
Named volumes are generally preferred for database storage because Docker manages permissions and location for you; bind mounts are more useful when you need to inspect or edit the files directly from the host.

## Gotchas

- Always wait for the "ready for connections" log line before connecting — connecting too early during first-time initialization can fail or hang.
- If you forget `-v` entirely, the container still works, but all data lives in the container's writable layer and is lost on `docker rm`.
- `MYSQL_ROOT_PASSWORD` is only used the *first* time the volume is initialized. If you reuse a volume that already has data, changing this environment variable on a new container has no effect on the existing root password.

## 🔗 Related Notes
- [[Docker Hub Practice|Docker Beginner's Guide: Login, Create Image, Push & Pull]]
- [[Docker Installation|Docker Installation]]

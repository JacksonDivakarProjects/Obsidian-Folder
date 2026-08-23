# Docker Beginner's Guide: Login, Create Image, Push & Pull

## 📋 Prerequisites
- Docker installed on your computer
- Docker Hub account (free at hub.docker.com)
- Basic command line knowledge

---

## Part 1: Docker Login

### Step 1: Create a Docker Hub Account
1. Go to https://hub.docker.com
2. Sign up for a free account
3. Verify your email

### Step 2: Login from the Command Line
```bash
# Login to Docker Hub
docker login

# It will ask for:
# Username: your-dockerhub-username
# Password: your-dockerhub-password
```

**Expected output:**
```
Login Succeeded
```

---

## Part 2: Create a Simple Application

A basic Python web app makes a good example.

### Step 1: Create a project folder
```bash
mkdir my-first-docker-app
cd my-first-docker-app
```

### Step 2: Create the application
`app.py`:
```python
# app.py
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Docker Container!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Step 3: Create a requirements file
`requirements.txt`:
```
flask==2.0.1
```

---

## Part 3: Create a Dockerfile

Create a file named `Dockerfile` (no extension):

```dockerfile
# Use official Python image
FROM python:3.9-slim

# Set working directory in container
WORKDIR /app

# Copy requirements first (for better layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY app.py .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
```

Putting `COPY requirements.txt .` and the `RUN pip install` step before `COPY app.py .` matters: Docker caches each layer, so as long as `requirements.txt` doesn't change, the dependency-install layer is reused on rebuilds instead of re-running `pip install` every time application code changes.

---

## Part 4: Build the Docker Image

### Step 1: Build the image
```bash
# Format: docker build -t yourusername/image-name:tag .
docker build -t your-dockerhub-username/my-first-app:v1 .
```

**Example:**
```bash
docker build -t johnsmith/my-first-app:v1 .
```

**What this does:**
- `-t` = tag/name the image (`repository:tag` format)
- `yourusername/my-first-app:v1` = repository name and tag
- `.` = build context — use the Dockerfile in the current directory

### Step 2: Verify the image exists
```bash
# List all images
docker images

# Or the more detailed view
docker image ls
```

**Expected output:**
```
REPOSITORY                 TAG       IMAGE ID       CREATED         SIZE
johnsmith/my-first-app     v1        abc123def456   2 minutes ago   125MB
```

---

## Part 5: Test the Image Locally

```bash
# Run the container
docker run -p 5000:5000 your-dockerhub-username/my-first-app:v1
```

**Explanation:**
- `-p 5000:5000` = map `hostPort:containerPort` — port 5000 on the host maps to port 5000 inside the container

**Test it:** open a browser to `http://localhost:5000`

**Stop the container:** press `Ctrl+C`

### Run in detached mode (background)
```bash
docker run -d -p 5000:5000 --name my-app your-dockerhub-username/my-first-app:v1
```

**To stop and remove the detached container:**
```bash
docker stop my-app
docker rm my-app
```

---

## Part 6: Push the Image to Docker Hub

### Step 1: Push the image
```bash
docker push your-dockerhub-username/my-first-app:v1
```

### Step 2: Verify on Docker Hub
1. Go to hub.docker.com
2. Login to your account
3. Confirm the repository shows the pushed image/tag

---

## Part 7: Pull and Run from Docker Hub

On a different computer or clean environment:

```bash
# Pull the image
docker pull your-dockerhub-username/my-first-app:v1

# Run it
docker run -p 5000:5000 your-dockerhub-username/my-first-app:v1
```

---

## 📝 Common Docker Commands Cheat Sheet

### Image Commands
```bash
# List images
docker images

# Remove an image
docker rmi image-name

# Remove all unused (dangling) images
docker image prune

# Build an image
docker build -t name:tag .

# Push image
docker push username/repo:tag

# Pull image
docker pull username/repo:tag
```

### Container Commands
```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop a container
docker stop container-id

# Remove a container
docker rm container-id

# Run container with a name
docker run --name mycontainer image-name

# Run in background (detached)
docker run -d image-name

# View logs
docker logs container-id
```

### System Commands
```bash
# Login to Docker Hub
docker login

# Logout
docker logout

# Check Docker version
docker --version

# Get system info
docker info
```

---

## 🎯 Practice Exercise

1. Create a simple Node.js app instead of Python
2. Use meaningful tags (v1, v2, latest) instead of relying on a single tag
3. Build a static website image using nginx as the base
4. Experiment with different base images (e.g. `alpine` variants for smaller size)

---

## ❓ Common Issues & Solutions

### "Permission denied" running docker without sudo
**Solution:** add your user to the `docker` group (Linux/Mac):
```bash
sudo usermod -aG docker $USER
# Log out and back in for the group change to take effect
```

### "Port already in use"
**Solution:** change the host-side port:
```bash
docker run -p 5001:5000 your-image
```

### "Unable to find image locally"
This isn't necessarily an error — `docker run` automatically pulls the image from Docker Hub if it isn't found locally.

### "Docker login failed"
**Solution:** check your internet connection and credentials. If you have 2FA enabled on Docker Hub, use a personal access token instead of your account password.

---

## 📚 Best Practices for Beginners

1. **Tag images meaningfully** — use versions (`v1`, `v2`, `1.0.0`), not only `latest`
2. **Keep images small** — use slim/alpine base images where possible
3. **Use `.dockerignore`** — exclude files that shouldn't be copied into the build context
4. **One process per container** — each container should do one thing well
5. **Don't run as root in production** — create and use a non-root user inside the image

---

## Example `.dockerignore` file
```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.git
.gitignore
README.md
Dockerfile
.dockerignore
```

---

## Summary

The full lifecycle covered here — login, build, tag, push, pull — is the core Docker workflow:
1. Logged into Docker Hub
2. Wrote a Dockerfile and built an image from it
3. Ran and tested the image locally
4. Pushed the image to Docker Hub
5. Pulled and ran that same image from a different machine

## 🔗 Related Notes
- [[Docker Installation|Docker Installation]]
- [[Persistent Storage in MYSQL Docker Container|Persistent Storage in MYSQL Docker Container]]
- [[Users and Groups Syntax|Users and Groups Syntax]]

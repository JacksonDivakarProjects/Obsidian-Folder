# Docker Beginner's Guide: Login, Create Image, Push & Pull

## 📋 Prerequisites
- Docker installed on your computer
- Docker Hub account (free at hub.docker.com)
- Basic command line knowledge

---

## **Part 1: Docker Login**

### Step 1: Create Docker Hub Account
1. Go to https://hub.docker.com
2. Sign up for a free account
3. Verify your email

### Step 2: Login from Command Line
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

## **Part 2: Create a Simple Application**

Let's create a basic Python web app as an example.

### Step 1: Create project folder
```bash
# Create a new folder for your project
mkdir my-first-docker-app
cd my-first-docker-app
```

### Step 2: Create a simple application
Create a file called `app.py`:
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

### Step 3: Create requirements file
Create a file called `requirements.txt`:
```
flask==2.0.1
```

---

## **Part 3: Create Dockerfile**

Create a file named `Dockerfile` (no extension):

```dockerfile
# Use official Python image
FROM python:3.9-slim

# Set working directory in container
WORKDIR /app

# Copy requirements first (for better caching)
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

---

## **Part 4: Build Docker Image**

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
- `-t` = tag/name the image
- `yourusername/my-first-app:v1` = repository name and tag
- `.` = build from current directory

### Step 2: Verify the image exists
```bash
# List all images
docker images

# Or more detailed view
docker image ls
```

**Expected output:**
```
REPOSITORY                 TAG       IMAGE ID       CREATED         SIZE
johnsmith/my-first-app     v1        abc123def456   2 minutes ago   125MB
```

---

## **Part 5: Test Your Image Locally**

```bash
# Run the container
docker run -p 5000:5000 your-dockerhub-username/my-first-app:v1
```

**Explanation:**
- `-p 5000:5000` = map port 5000 on your computer to port 5000 in container

**Test it:** Open browser and go to `http://localhost:5000`

**Stop the container:** Press `Ctrl+C`

### Run in detached mode (background):
```bash
docker run -d -p 5000:5000 --name my-app your-dockerhub-username/my-first-app:v1
```

**To stop detached container:**
```bash
docker stop my-app
docker rm my-app
```

---

## **Part 6: Push Image to Docker Hub**

### Step 1: Push the image
```bash
docker push your-dockerhub-username/my-first-app:v1
```

### Step 2: Verify on Docker Hub
1. Go to hub.docker.com
2. Login to your account
3. You should see your repository with the pushed image

---

## **Part 7: Pull and Run from Docker Hub**

### On a different computer or clean environment:

```bash
# Pull the image
docker pull your-dockerhub-username/my-first-app:v1

# Run it
docker run -p 5000:5000 your-dockerhub-username/my-first-app:v1
```

---

## **📝 Common Docker Commands Cheat Sheet**

### Image Commands:
```bash
# List images
docker images

# Remove an image
docker rmi image-name

# Remove all unused images
docker image prune

# Build an image
docker build -t name:tag .

# Push image
docker push username/repo:tag

# Pull image
docker pull username/repo:tag
```

### Container Commands:
```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop a container
docker stop container-id

# Remove a container
docker rm container-id

# Run container with name
docker run --name mycontainer image-name

# Run in background
docker run -d image-name

# View logs
docker logs container-id
```

### System Commands:
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

## **🎯 Practice Exercise**

Try these steps on your own:
1. Create a simple Node.js app instead of Python
2. Use different tags (v1, v2, latest)
3. Try building a static website with nginx
4. Experiment with different base images

---

## **❓ Common Issues & Solutions**

### Issue: "Permission denied"
**Solution:** Add user to docker group (Linux/Mac)
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### Issue: "Port already in use"
**Solution:** Change host port
```bash
docker run -p 5001:5000 your-image
```

### Issue: "Unable to find image locally"
**Solution:** Docker will automatically pull from hub if not found locally

### Issue: "Docker login failed"
**Solution:** Check your internet connection and credentials

---

## **📚 Best Practices for Beginners**

1. **Tag images meaningfully**: Use versions (v1, v2, 1.0.0) not just 'latest'
2. **Keep images small**: Use slim versions of base images
3. **Use .dockerignore**: Create a `.dockerignore` file to exclude unnecessary files
4. **One process per container**: Each container should do one thing well
5. **Don't run as root**: Create and use a non-root user in production

---

## **Example .dockerignore file**
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

**Congratulations!** 🎉 You've successfully:
- Logged into Docker Hub
- Created a Dockerfile
- Built a Docker image
- Pushed it to Docker Hub
- Pulled and ran it from anywhere

This is the foundation of working with Docker. Practice these steps until they become second nature!

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Docker/Docker Installation|Docker Installation]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Docker/Persistent Storage/Persistent Storage in MYSQL Docker Container|Persistent Storage in MYSQL Docker Container]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Docker/Users and Groups/Users and Groups Syntax|Users and Groups Syntax]]

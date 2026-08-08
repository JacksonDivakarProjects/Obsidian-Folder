# Docker Installation on Windows

There are two main ways to get the Docker CLI working on Windows: the full **Docker Desktop** experience, or a leaner **CLI-only** setup via WSL 2. Which one to pick depends on whether you want a GUI and are fine with Docker Desktop's licensing terms, or want a lighter footprint.

---

## Option 1: Docker Desktop (Recommended for Most Users)

Docker Desktop bundles the Docker CLI, Docker Engine, and a GUI for managing containers, images, and volumes.

**Steps:**
1. Download Docker Desktop for Windows from [the official Docker documentation](https://docs.docker.com/desktop/setup/install/windows-install/).
2. Run the installer and follow the prompts.
3. Choose whether to use **WSL 2** or **Hyper-V** as the backend — WSL 2 is generally preferred (better performance, lower resource overhead, and required if you also want to use Docker directly from a WSL distro).
4. After installation, open PowerShell or Command Prompt and confirm the CLI is available:
    ```bash
    docker --version
    ```

---

## Option 2: Docker CLI Without Docker Desktop

Useful if you want to avoid Docker Desktop's resource overhead or its licensing terms for larger commercial use, and only need the engine and CLI, per [this guide](https://dev.to/julianlasso/how-to-install-docker-cli-on-windows-without-docker-desktop-and-not-die-trying-4033).

**Steps:**
1. Install WSL 2 and a Linux distribution (e.g. Ubuntu) from the Microsoft Store, or via `wsl --install` from an elevated PowerShell prompt.
2. Inside the WSL distro, install Docker Engine using the distro's package manager:
    ```bash
    sudo apt update
    sudo apt install docker.io
    ```
3. Add your user to the `docker` group so you don't need `sudo` for every command (see [[Data Engineering Role Notes/Data Engineering Concepts/Docker/Users and Groups/Users and Groups Syntax|Users and Groups Syntax]]):
    ```bash
    sudo usermod -aG docker $USER
    ```
4. Restart the WSL session (or log out/in) and confirm the install:
    ```bash
    docker run hello-world
    ```

This gives a lightweight Docker CLI setup without the Docker Desktop overhead — but note it also means no built-in GUI, and the Docker daemon needs to be started manually inside WSL (`sudo service docker start`) unless it's configured to start automatically.

---

## Which to Choose

- **Just starting out / want simplicity:** Docker Desktop — easiest setup, integrates smoothly with Windows, includes a GUI.
- **Leaner setup, avoiding licensing restrictions, or running headless (e.g. CI, servers):** the WSL-based CLI-only installation.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Docker/Docker Hub Practice|Docker Beginner's Guide: Login, Create Image, Push & Pull]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Docker/Users and Groups/Users and Groups Syntax|Users and Groups Syntax]]

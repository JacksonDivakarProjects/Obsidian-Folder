You’ve got two main options for installing Docker CLI on Windows, depending on whether you want the full **Docker Desktop** experience or just the **CLI tools**.

---

## Option 1: Install Docker Desktop (Recommended for Most Users)

Docker Desktop bundles the Docker CLI, Docker Engine, and a GUI for managing containers.  
Steps:

1. Download Docker Desktop for Windows from the official site. [Docker Documentation](https://docs.docker.com/desktop/setup/install/windows-install/)

2. Run the installer and follow the prompts.
3. Choose whether to use **WSL 2** or **Hyper-V** as the backend (WSL 2 is generally preferred).
4. After installation, open PowerShell or Command Prompt and run:
    
    ```bash
    docker --version
    ```
    
    to confirm the CLI is available. [Docker Documentation](https://docs.docker.com/desktop/setup/install/windows-install/)

---

## Option 2: Install Docker CLI Without Docker Desktop

If you don’t want Docker Desktop (e.g., due to licensing or resource constraints), you can install only the CLI:

1. Install **WSL 2** and set up a Linux distribution (like Ubuntu) from the Microsoft Store.
2. Inside WSL, install Docker Engine using your distro’s package manager:
    
    ```bash
    sudo apt update
    sudo apt install docker.io
    ```
    
3. Add your user to the `docker` group:
    
    ```bash
    sudo usermod -aG docker $USER
    ```
    
4. Restart WSL and test with:
    
    ```bash
    docker run hello-world
    ```
    

This gives you a lightweight Docker CLI setup without the Desktop overhead. [DEV Community](https://dev.to/julianlasso/how-to-install-docker-cli-on-windows-without-docker-desktop-and-not-die-trying-4033)

---

✅ **Tip:** If you’re just starting out, Docker Desktop is easier and integrates smoothly with Windows. If you want a leaner setup or need to avoid licensing restrictions, go with the WSL-based CLI installation.

Do you want me to walk you through the **WSL setup step-by-step**, or are you leaning toward the **Docker Desktop route**?

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Docker/Docker Hub Practice|Docker Beginner's Guide: Login, Create Image, Push & Pull]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Docker/Users and Groups/Users and Groups Syntax|Users and Groups Syntax]]

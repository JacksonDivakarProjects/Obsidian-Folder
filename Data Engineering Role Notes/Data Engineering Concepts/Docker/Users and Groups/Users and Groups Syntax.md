Got it — you want a **handy set of commands** for managing users and groups in Linux so you can set things up properly for Docker (or any other tool). Here’s a practical cheat sheet:

---

## 🔑 User & Group Management Commands

### 1. Add a New User

```bash
sudo adduser username
```

- Creates a new user and home directory.
- Example: `sudo adduser alex`

### 2. Add a New Group

```bash
sudo groupadd groupname
```

- Creates a new group.
- Example: `sudo groupadd docker`

### 3. Add User to a Group

```bash
sudo usermod -aG groupname username
```

- Adds a user to a group (append mode so existing groups aren’t lost).
- Example: `sudo usermod -aG docker alex`

### 4. Change a User’s Primary Group

```bash
sudo usermod -g groupname username
```

- Sets the main group for the user.

### 5. List Groups for a User

```bash
groups username
```

or for yourself:

```bash
groups
```

### 6. Verify Current User

```bash
echo $USER
```

- Shows the username of the logged-in user (environment variable).

### 7. Switch User

```bash
su - username
```

- Switches to another user account.

### 8. Delete a User

```bash
sudo deluser username
```

### 9. Delete a Group

```bash
sudo groupdel groupname
```

---

## 🚀 Useful for Docker Setup

- Create the `docker` group if it doesn’t exist:
    
    ```bash
    sudo groupadd docker
    ```
    
- Add yourself to it:
    
    ```bash
    sudo usermod -aG docker $USER
    ```
    
- Log out and back in (or restart WSL) so group membership takes effect.
- Test without `sudo`:
    
    ```bash
    docker ps
    ```
    

---

👉 This way, you’ll have full control over users and groups, and Docker will run smoothly without needing `sudo` every time.

Would you like me to also show you a **step-by-step script** that sets up Docker group permissions automatically, so you don’t have to run each command manually?

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Docker/Docker Installation|Docker Installation]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Docker/Docker Hub Practice|Docker Beginner's Guide: Login, Create Image, Push & Pull]]

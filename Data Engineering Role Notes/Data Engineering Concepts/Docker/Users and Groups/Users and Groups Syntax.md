# Linux Users and Groups: Syntax Cheat Sheet

## Why This Matters for Docker

By default, the Docker daemon socket is owned by `root` and the `docker` group, so running Docker commands normally requires `sudo`. Adding your user to the `docker` group lets you run `docker` commands without `sudo` every time — but that's a broader Linux user/group management skill worth knowing on its own, since it comes up constantly when setting up permissions for any tool, not just Docker.

## 🔑 User & Group Management Commands

### 1. Add a new user
```bash
sudo adduser username
```
Creates a new user and home directory. Example: `sudo adduser alex`

### 2. Add a new group
```bash
sudo groupadd groupname
```
Creates a new group. Example: `sudo groupadd docker`

### 3. Add a user to a group
```bash
sudo usermod -aG groupname username
```
Adds a user to a group in **append** mode. Example: `sudo usermod -aG docker alex`

**Important:** always include `-a` (append). Without it, `usermod -G groupname username` *replaces* the user's entire supplementary group list with just that one group — a common way to accidentally remove a user from every other group they belonged to.

### 4. Change a user's primary group
```bash
sudo usermod -g groupname username
```
Sets the user's main (primary) group, as opposed to a supplementary group.

### 5. List a user's groups
```bash
groups username
```
Or for the current user:
```bash
groups
```

### 6. Check the current user
```bash
echo $USER
```
Shows the logged-in username via the `$USER` environment variable.

### 7. Switch user
```bash
su - username
```
Switches to another user account. The `-` loads that user's login environment (shell, home directory, etc.) rather than just changing the UID in the current shell.

### 8. Delete a user
```bash
sudo deluser username
```
(On Debian/Ubuntu; RHEL/CentOS-based distros use `sudo userdel username` instead.)

### 9. Delete a group
```bash
sudo groupdel groupname
```

---

## Applying This to Docker Setup

1. Create the `docker` group if it doesn't already exist (it's usually created automatically by the Docker install):
    ```bash
    sudo groupadd docker
    ```
2. Add yourself to it:
    ```bash
    sudo usermod -aG docker $USER
    ```
3. Log out and back in (or restart the WSL session) so the new group membership takes effect — group membership is read when a session starts, not applied retroactively to the current shell.
4. Test that Docker works without `sudo`:
    ```bash
    docker ps
    ```

## Gotchas

- Group membership changes don't apply to your *current* shell session — you must start a new login session for `groups` to reflect the change.
- Adding a user to the `docker` group is effectively equivalent to giving them root-level access on the host, since a container can be used to mount and modify host paths. Treat `docker` group membership with the same caution as `sudo` access.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Docker/Docker Installation|Docker Installation]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Docker/Docker Hub Practice|Docker Beginner's Guide: Login, Create Image, Push & Pull]]

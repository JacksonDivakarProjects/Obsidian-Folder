# Linux — Clear Memory Cache

Command to manually flush and clear the system's memory (page) cache.

```bash
sudo sh -c "sync; echo 3 > /proc/sys/vm/drop_caches"
```

### 🔍 What it does

- `sync` — flushes filesystem buffers to disk before dropping anything, so no dirty (unwritten) data is lost.
- `echo 3 > /proc/sys/vm/drop_caches` — tells the kernel what to drop:
    - `1` — clear the page cache
    - `2` — clear dentries and inodes
    - `3` — clear **all** of the above (page cache + dentries + inodes)

### 🧠 Why `sh -c "..."` instead of running it directly

`sudo echo 3 > /proc/sys/vm/drop_caches` does **not** work: the `>` redirection is opened by your own unprivileged shell before `sudo` even runs `echo`, so the write to a root-only file fails with "Permission denied" even though `echo` itself ran as root. Wrapping the whole `sync; echo ...` pipeline inside `sudo sh -c "..."` makes a *root* shell open the redirection, which is what actually needs the privilege.

### 🧪 Checking memory usage before/after

```bash
free -m   # in MB
free -g   # in GB
```

This is mainly a sysadmin/troubleshooting tool — Linux normally manages the page cache automatically and reclaims it under memory pressure without any manual intervention.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/Miscellaneous Concepts/YT-DLP|YT-DLP]]
- [[Data Engineering Role Notes/Linux/Linux Summary Guide|Linux Masterclass Concepts]]

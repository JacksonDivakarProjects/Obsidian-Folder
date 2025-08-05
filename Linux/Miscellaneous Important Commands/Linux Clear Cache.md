
The command shown in your screenshot is used to **clear memory cache** in Linux. Here's the exact command from the image:

```bash
sudo sh -c "sync; echo 3 > /proc/sys/vm/drop_caches"
```

### 🔍 What it does:

- `sync`: flushes file system buffers to disk.
    
- `echo 3 > /proc/sys/vm/drop_caches`:
    
    - `1` = Clear page cache
        
    - `2` = Clear dentries and inodes
        
    - `3` = Clear **all** (page cache + dentries + inodes)
        

---

### 🧪 How to check before/after memory usage:

```bash
free -m   # in MB
free -g   # in GB
```

Would you like a script version of this for regular use or automation?
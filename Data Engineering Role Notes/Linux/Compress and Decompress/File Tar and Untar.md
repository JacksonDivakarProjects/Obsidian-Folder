
Here's a **clear and simple guide** to using `tar` for **archiving and extracting** files in Linux:

---

## 📦 TAR (Create Archive)

### ✅ 1. **Tar a file or folder**

```bash
tar -cvf archive.tar file_or_folder
```

**Flags:**

- `c` → Create archive
    
- `v` → Verbose (shows progress)
    
- `f` → Filename of the archive
    

---

## 📂 UNTAR (Extract Archive)

### ✅ 2. **Extract `.tar` file**

```bash
tar -xvf archive.tar
```

**Flags:**

- `x` → Extract archive
    
- `v` → Verbose
    
- `f` → Filename
    

---

## 📦🔧 Compressed TAR (.tar.gz or .tgz)

### ✅ 3. **Create compressed archive**

```bash
tar -czvf archive.tar.gz file_or_folder
```

- `z` → Gzip compression
    

### ✅ 4. **Extract compressed archive**

```bash
tar -xzvf archive.tar.gz
```

---

## 📂 Extract to Specific Directory

```bash
tar -xvf archive.tar -C /path/to/folder
```

---

## 🧪 Just View Contents

```bash
tar -tvf archive.tar
```

---

### 🧠 Tip: File Types

|Extension|Format|
|---|---|
|`.tar`|Archive only|
|`.tar.gz` / `.tgz`|Compressed (gzip)|
|`.tar.bz2`|Compressed (bzip2)|
|`.tar.xz`|Compressed (xz)|

Would you like examples using `.tar.gz` and `.tar.xz` too?

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/Compress and Decompress/File Zip and Unzip|File Zip and Unzip]]
- [[Data Engineering Role Notes/Linux/Linux Summary Guide|Linux Masterclass Concepts]]

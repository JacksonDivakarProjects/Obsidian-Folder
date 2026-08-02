
Here's how to **zip** and **unzip** files in Linux using the command line:

---

## 📦 ZIP Files in Linux

### ✅ 1. **Zip a Single File**

```bash
zip myfile.zip filename.txt
```

### ✅ 2. **Zip a Folder (recursively)**

```bash
zip -r myfolder.zip myfolder/
```

### ✅ 3. **Zip Multiple Files**

```bash
zip archive.zip file1.txt file2.jpg file3.pdf
```

---

## 📂 UNZIP Files in Linux

### ✅ 1. **Unzip to Current Directory**

```bash
unzip myfile.zip
```

### ✅ 2. **Unzip to a Specific Folder**

```bash
unzip myfile.zip -d /path/to/folder
```

---

## 💡 Useful Flags

|Command|Description|
|---|---|
|`-r`|Recursively zip folders|
|`-d`|Destination folder for `unzip`|
|`-l`|List contents of a zip without extracting: `unzip -l file.zip`|

---

## 🔧 Install if not available

```bash
sudo apt install zip unzip   # Debian/Ubuntu
sudo yum install zip unzip   # RHEL/CentOS
```

Want a bash script to zip and unzip interactively?

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/Compress and Decompress/File Tar and Untar|File Tar and Untar]]
- [[Data Engineering Role Notes/Linux/Linux Summary Guide|Linux Masterclass Concepts]]

# File Zip and Unzip

A quick, practical guide to zipping and unzipping files in Linux from the command line.

## 📦 ZIP Files

### Zip a single file
```bash
zip myfile.zip filename.txt
```

### Zip a folder (recursively)
```bash
zip -r myfolder.zip myfolder/
```

### Zip multiple files
```bash
zip archive.zip file1.txt file2.jpg file3.pdf
```

## 📂 UNZIP Files

### Unzip to the current directory
```bash
unzip myfile.zip
```

### Unzip to a specific folder
```bash
unzip myfile.zip -d /path/to/folder
```

## 💡 Useful Flags

| Flag | Description |
|---|---|
| `-r` | Recursively zip folder contents |
| `-d` | Destination folder for `unzip` |
| `-l` | List contents of a zip without extracting: `unzip -l file.zip` |

## 🔧 Install if Not Available

```bash
sudo apt install zip unzip   # Debian/Ubuntu
sudo yum install zip unzip   # RHEL/CentOS
```

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/Compress and Decompress/File Tar and Untar|File Tar and Untar]]
- [[Data Engineering Role Notes/Linux/Linux Summary Guide|Linux Masterclass Concepts]]

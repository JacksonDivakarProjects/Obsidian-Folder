# File Tar and Untar

A quick, practical guide to archiving and extracting files with `tar` in Linux.

## 📦 TAR (Create Archive)

### Tar a file or folder
```bash
tar -cvf archive.tar file_or_folder
```
**Flags:**
- `c` → create archive
- `v` → verbose (shows progress)
- `f` → filename of the archive

## 📂 UNTAR (Extract Archive)

### Extract a `.tar` file
```bash
tar -xvf archive.tar
```
**Flags:**
- `x` → extract archive
- `v` → verbose
- `f` → filename

## 📦🔧 Compressed TAR (.tar.gz or .tgz)

### Create a compressed archive
```bash
tar -czvf archive.tar.gz file_or_folder
```
- `z` → gzip compression

### Extract a compressed archive
```bash
tar -xzvf archive.tar.gz
```

## 📂 Extract to a Specific Directory

```bash
tar -xvf archive.tar -C /path/to/folder
```

## 🧪 View Contents Without Extracting

```bash
tar -tvf archive.tar
```

## 🧠 Tip: File Types

| Extension | Format |
|---|---|
| `.tar` | Archive only, no compression |
| `.tar.gz` / `.tgz` | Compressed (gzip) |
| `.tar.bz2` | Compressed (bzip2 — smaller than gzip, slower) |
| `.tar.xz` | Compressed (xz — smallest, slowest) |

For `.tar.bz2` and `.tar.xz`, swap the `z` flag for `j` (bzip2) or `J` (xz) respectively — e.g. `tar -cjvf archive.tar.bz2 folder/` or `tar -cJvf archive.tar.xz folder/`.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/Compress and Decompress/File Zip and Unzip|File Zip and Unzip]]
- [[Data Engineering Role Notes/Linux/Linux Summary Guide|Linux Masterclass Concepts]]

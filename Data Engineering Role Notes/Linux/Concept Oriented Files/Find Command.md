
Here’s a clean and practical **Obsidian note** for the `find` command — optimized for quick reference, learning, and day-to-day Linux usage.

---

## 🔍 `find` Command — Obsidian Cheat Sheet

### 🧠 Purpose:

Search files and directories recursively in a given path.

---

### 📌 Basic Syntax:

```bash
find [path] [options] [expression]
```

- `path`: Starting directory (e.g., `.`, `/home`, `/etc`)
    
- `options`: Conditions like `-type`, `-name`, etc.
    

---

## 🔹 Common Use Cases

### 📁 Find Directories by Name

```bash
find . -type d -name 'dirname'
```

### 📄 Find Files by Name

```bash
find . -type f -name 'filename.txt'
```

### 🔍 Case-Insensitive Search

```bash
find . -iname 'filename.txt'
```

---

## 🔧 Wildcard Matching

|Pattern|Meaning|
|---|---|
|`*`|Matches any characters|
|`*.txt`|All `.txt` files|
|`*log*`|Names containing "log"|

---

## 🔥 Filter by Time

### 🕒 Find files modified **in last 1 day**

```bash
find . -type f -mtime -1
```

### 🕒 Find files modified **more than 5 days ago**

```bash
find . -type f -mtime +5
```

---

## 🔑 Filter by Size

```bash
find . -type f -size +10M       # >10MB
find . -type f -size -500k      # <500KB
```

---

## 🧼 Delete Matching Files (⚠️ Caution!)

```bash
find . -type f -name '*.tmp' -delete
```

---

## 🧵 Run Command on Found Files

```bash
find . -type f -name '*.log' -exec rm {} \;
```

---

## 🧠 Tips

- Use `-type f` for files, `-type d` for directories.
    
- `-iname` is case-insensitive.
    
- Always test with `-print` before using `-delete`.
    

---

Let me know if you want a **more advanced section** on `-perm`, `-user`, or `-exec`.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/Concept Oriented Files/CHMOD|CHMOD]]
- [[Data Engineering Role Notes/Linux/Concept Oriented Files/AWK|AWK]]
- [[Data Engineering Role Notes/Linux/Linux Summary Guide|Linux Masterclass Concepts]]

# `find` Command — Cheat Sheet

## 🧠 Purpose

Recursively search for files and directories under a given path, by name, type, time, size, and other attributes.

## 📌 Basic Syntax

```bash
find [path] [options] [expression]
```
- `path` — starting directory (e.g. `.`, `/home`, `/etc`)
- `options`/`expression` — conditions such as `-type`, `-name`, `-size`, `-mtime`

## 🔹 Common Use Cases

### Find directories by name
```bash
find . -type d -name 'dirname'
```

### Find files by name
```bash
find . -type f -name 'filename.txt'
```

### Case-insensitive search
```bash
find . -iname 'filename.txt'
```

## 🔧 Wildcard Matching

| Pattern | Meaning |
|---|---|
| `*` | Matches any characters |
| `*.txt` | All `.txt` files |
| `*log*` | Names containing "log" |

## 🔥 Filter by Time

### Modified in the last 1 day
```bash
find . -type f -mtime -1
```

### Modified more than 5 days ago
```bash
find . -type f -mtime +5
```

## 🔑 Filter by Size

```bash
find . -type f -size +10M       # > 10 MB
find . -type f -size -500k      # < 500 KB
```

## 🧼 Delete Matching Files (⚠️ Caution!)

```bash
find . -type f -name '*.tmp' -delete
```

## 🧵 Run a Command on Found Files

```bash
find . -type f -name '*.log' -exec rm {} \;
```
`{}` is replaced with each matched filename; `\;` terminates the `-exec` command per match. Add `+` instead of `\;` (`-exec rm {} +`) to batch multiple matches into fewer command invocations, which is faster for large result sets.

## 🧠 Tips

- Use `-type f` for files, `-type d` for directories.
- `-iname` is the case-insensitive version of `-name`.
- Always dry-run with `-print` (or just omit `-delete`/`-exec`) before using `-delete` — there's no confirmation prompt and no undo.
- For permission-based, ownership-based, or command-execution filtering, see `-perm`, `-user`, and `-exec` in `man find`.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/Concept Oriented Files/CHMOD|CHMOD]]
- [[Data Engineering Role Notes/Linux/Concept Oriented Files/AWK|AWK]]
- [[Data Engineering Role Notes/Linux/Linux Summary Guide|Linux Masterclass Concepts]]

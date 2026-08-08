# `chmod` Command — Full Guide

## 🎯 Objective

Manage file and directory **permissions** in Linux using symbolic and numeric (octal) modes, and confidently analyze, modify, and validate them.

## 🧪 Analyze Before You Act

### Step 1: Inspect permissions
```bash
ls -l filename
```
Sample output:
```
-rwxr-xr--
```

### 🔍 Breakdown

| Symbol | Meaning |
|---|---|
| `-` | It's a file (`d` = directory) |
| `rwx` | **User** (owner): read, write, execute |
| `r-x` | **Group**: read, execute |
| `r--` | **Others**: read only |

## 🧠 Permission Mapping

| Permission | Symbol | Value |
|---|---|---|
| Read | `r` | 4 |
| Write | `w` | 2 |
| Execute | `x` | 1 |

### 🧮 Value Combinations

| Total | Meaning |
|---|---|
| 7 | `rwx` = read + write + execute |
| 6 | `rw-` = read + write |
| 5 | `r-x` = read + execute |
| 4 | `r--` = read only |
| 0 | `---` = no permission |

## 🔢 Numeric (Octal) Mode

```bash
chmod [N][N][N] filename
```

Digits, in order: **User (owner)**, **Group**, **Others**.

#### Example
```bash
chmod 755 script.sh
```

| Section | Value | Meaning |
|---|---|---|
| User | `7` | `rwx` |
| Group | `5` | `r-x` |
| Others | `5` | `r-x` |

## 🧩 Symbolic Mode

```bash
chmod [who][operator][permission] filename
```

| Component | Options |
|---|---|
| `who` | `u` (user), `g` (group), `o` (others), `a` (all) |
| `operator` | `+` (add), `-` (remove), `=` (set exactly) |
| `permission` | `r`, `w`, `x` |

### Examples
```bash
chmod u+x file       # Add execute for the owner
chmod g-w file       # Remove write from the group
chmod o=r file       # Set others to read-only
chmod a+rw file      # Give read and write to everyone
```

## 🧾 Worked Examples

### Case 1: `-rwxr-xr--`

| Who | Permissions |
|---|---|
| User | `rwx` = 7 |
| Group | `r-x` = 5 |
| Others | `r--` = 4 |

✔️ Equivalent: `chmod 754 filename`

### Case 2: `-rw-r--r--`

| Who | Permissions |
|---|---|
| User | `rw-` = 6 |
| Group | `r--` = 4 |
| Others | `r--` = 4 |

✔️ Equivalent: `chmod 644 filename`

## 🧠 Mental Model Summary

- Think in **triplets**: User | Group | Others
- Each position = sum of `r=4`, `w=2`, `x=1`
- Leading character: `-` = file, `d` = directory, `l` = symlink
- Use `ls -l` to inspect current permissions before changing them

## 🛠️ Pro Tips

- **All access for everyone** (dangerous, generally avoid): `chmod 777 file`
- **Owner-only access**: `chmod 700 file`
- **Read-only for everyone**: `chmod 444 file`
- Applying to a whole directory tree: `chmod -R <mode> <directory>` — recursively updates permissions on the directory and everything inside it (use carefully, since directories usually need the execute bit to be enterable, unlike plain files).

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/Concept Oriented Files/Find Command|Find Command]]
- [[Data Engineering Role Notes/Linux/Concept Oriented Files/Alias with .bashrc|Alias with .bashrc]]
- [[Data Engineering Role Notes/Linux/Linux Summary Guide|Linux Masterclass Concepts]]

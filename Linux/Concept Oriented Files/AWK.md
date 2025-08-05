

Absolutely, Jack. Here’s a clean and professional **Obsidian note** on `awk` — tailored for practical use, interview prep, and system scripting.

---

## 🧠 `awk` Command — Obsidian Cheat Sheet

### 🔍 Purpose:

A powerful **text processing tool** for pattern scanning, field extraction, and data transformation — line by line.

---

### 📌 Basic Syntax:

```bash
awk 'pattern { action }' file
```

- Reads input **line-by-line**
    
- Splits each line into **fields** (by default, whitespace)
    
- Executes the action `{}` if the pattern matches
    

---

## 🧾 Common Usage

### 🔹 Print All Lines

```bash
awk '{ print }' file.txt
```

### 🔹 Print a Specific Column (e.g., 1st column)

```bash
awk '{ print $1 }' file.txt
```

### 🔹 Print Multiple Columns

```bash
awk '{ print $1, $3 }' file.txt
```

---

## 📐 Field and Line Variables

|Variable|Description|
|---|---|
|`$0`|Entire line|
|`$1,$2…`|First, second… fields|
|`NF`|Number of fields|
|`NR`|Current line number|
|`FNR`|Line number (per file)|

---

## 📍 Patterns and Conditions

### 🔹 Print lines where 3rd column > 100

```bash
awk '$3 > 100 { print $0 }' file.txt
```

### 🔹 Print only if a line contains "error"

```bash
awk '/error/ { print }' file.txt
```

---

## 🧮 Built-in Functions

### 🔸 Sum a Column (e.g., 2nd column)

```bash
awk '{ sum += $2 } END { print sum }' file.txt
```

### 🔸 Average of a Column

```bash
awk '{ sum += $2 } END { print sum/NR }' file.txt
```

---

## 🧪 Field Separator (FS)

### 🔹 Use `:` as field separator (e.g., `/etc/passwd`)

```bash
awk -F ':' '{ print $1 }' /etc/passwd
```

---

## 🔁 Looping & Conditions

```bash
awk '{
    if ($2 > 50)
        print $1, $2
    else
        print $1, "LOW"
}' file.txt
```

---

## 🔧 Real-World Examples

### ✅ Show disk usage in human-readable format

```bash
df -h | awk 'NR>1 { print $1, $5 }'
```

### ✅ Add line numbers to a file

```bash
awk '{ print NR, $0 }' file.txt
```

---

## 🧠 Tips

- Wrap logic in `' '` when using directly.
    
- Use `-F` to set custom field delimiter.
    
- Use `BEGIN` and `END` for pre- and post-processing.
    

---

Let me know if you want a **deep dive on advanced `awk` scripting**, or comparison with `cut`, `sed`, etc.
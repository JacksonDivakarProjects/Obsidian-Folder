# `awk` Command — Cheat Sheet

## 🔍 Purpose

A text-processing tool for pattern scanning, field extraction, and data transformation — line by line.

## 📌 Basic Syntax

```bash
awk 'pattern { action }' file
```

- Reads input **line by line**
- Splits each line into **fields** (whitespace by default)
- Executes the action `{}` when the pattern matches

## 🧾 Common Usage

### Print all lines
```bash
awk '{ print }' file.txt
```

### Print a specific column (e.g. 1st)
```bash
awk '{ print $1 }' file.txt
```

### Print multiple columns
```bash
awk '{ print $1, $3 }' file.txt
```

## 📐 Field and Line Variables

| Variable | Description |
|---|---|
| `$0` | Entire line |
| `$1`, `$2`… | First, second… fields |
| `NF` | Number of fields |
| `NR` | Current line number (across all input files) |
| `FNR` | Current line number (resets per file) |

## 📍 Patterns and Conditions

### Print lines where the 3rd column > 100
```bash
awk '$3 > 100 { print $0 }' file.txt
```

### Print only lines containing "error"
```bash
awk '/error/ { print }' file.txt
```

## 🧮 Built-in Functions

### Sum a column (e.g. 2nd)
```bash
awk '{ sum += $2 } END { print sum }' file.txt
```

### Average of a column
```bash
awk '{ sum += $2 } END { print sum/NR }' file.txt
```

## 🧪 Field Separator (FS)

### Use `:` as the field separator (e.g. `/etc/passwd`)
```bash
awk -F ':' '{ print $1 }' /etc/passwd
```

## 🔁 Looping & Conditions

```bash
awk '{
    if ($2 > 50)
        print $1, $2
    else
        print $1, "LOW"
}' file.txt
```

## 🔧 Real-World Examples

### Disk usage, human-readable, skipping the header
```bash
df -h | awk 'NR>1 { print $1, $5 }'
```

### Add line numbers to a file
```bash
awk '{ print NR, $0 }' file.txt
```

## 🧠 Tips

- Quote the whole program in `'...'` when running it directly on the command line.
- Use `-F` to set a custom field delimiter.
- Use `BEGIN` and `END` blocks for pre- and post-processing (they run once, not per line).
- For deeper coverage (arrays, CSV workflows, log analysis), see the dedicated AWK guides linked below.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/AWK/AWK - Comprehensive Practical Guide|AWK — Comprehensive Practical Guide]]
- [[Data Engineering Role Notes/Linux/AWK/AWK Necessary Guide|AWK — Comprehensive Applied Guide (Real-World Edition)]]
- [[Data Engineering Role Notes/Linux/AWK/Arrays|AWK Arrays — What You Should Learn (Only What Matters)]]
- [[Data Engineering Role Notes/Linux/Concept Oriented Files/Find Command|Find Command]]

# Bash `if` Condition — Complete Guide (Strings, Numbers, Files)

A practical, industry-ready reference for `if` conditions in Bash, covering strings, numbers, and files.

## 1. Basic `if` Syntax

```bash
if [ condition ]; then
    command
elif [ another_condition ]; then
    command
else
    command
fi
```

**Non-negotiables:**
- Spaces **before and after** `[` and `]` are mandatory.
- `then` must be on a new line, or after a `;`.
- Use `[ ]` (POSIX `test`) or `[[ ]]` (Bash-only, preferred — see below).

## 2. String Conditions (Most Interview-Relevant)

### String equality
```bash
if [ "$name" = "Jack" ]; then
    echo "Welcome Jack"
fi
```
Use `=` (not `==`) inside single `[ ]` — `==` is a Bash-specific extension there and not portable; `[[ ]]` accepts either.

### String not equal
```bash
if [ "$role" != "admin" ]; then
    echo "Access limited"
fi
```

### Empty string
```bash
if [ -z "$username" ]; then
    echo "Username is empty"
fi
```

### Non-empty string
```bash
if [ -n "$username" ]; then
    echo "Username provided"
fi
```

### Best practice: modern Bash `[[ ]]`
```bash
if [[ "$name" == "Jack" ]]; then
    echo "Matched"
fi
```
Why `[[ ]]` is preferred:
- No need to quote/escape as defensively (word-splitting and glob expansion don't apply to the operands)
- Supports pattern matching (`==` with globs) and regex (`=~`)
- Fewer footguns overall

## 3. Numeric Conditions (Very Common in Scripts)

**Do not** use `=`, `<`, `>` for numeric comparisons in `[ ]` — those do string comparison (or, for `<`/`>`, get interpreted as shell redirection).

### Correct numeric operators

| Operator | Meaning |
|---|---|
| `-eq` | equal |
| `-ne` | not equal |
| `-gt` | greater than |
| `-ge` | greater or equal |
| `-lt` | less than |
| `-le` | less or equal |

```bash
if [ "$age" -ge 18 ]; then
    echo "Eligible"
else
    echo "Not eligible"
fi
```

### Cleaner: arithmetic-context `(( ))`
```bash
if (( age >= 18 )); then
    echo "Eligible"
fi
```
Use `(( ))` for pure numeric logic — it supports familiar operators (`>=`, `<`, etc.) directly and doesn't require quoting variables.

## 4. File & Directory Conditions

```bash
if [ -f "data.txt" ]; then echo "File exists"; fi
if [ -d "/var/log" ]; then echo "Directory found"; fi
if [ -e "config.yaml" ]; then echo "Exists"; fi        # any type
if [ -r "file.txt" ]; then echo "Readable"; fi
if [ -w "file.txt" ]; then echo "Writable"; fi
if [ -x "script.sh" ]; then echo "Executable"; fi
if [ -s "file.txt" ]; then echo "Not empty"; else echo "Empty"; fi
```

## 5. Logical AND / OR

### AND (`&&`)
```bash
if [ -f "file.txt" ] && [ -r "file.txt" ]; then
    echo "File exists and readable"
fi
```

### OR (`||`)
```bash
if [ "$role" = "admin" ] || [ "$role" = "root" ]; then
    echo "Privileged user"
fi
```

### Cleaner with `[[ ]]`
```bash
if [[ -f file.txt && -r file.txt ]]; then
    echo "Safe to read"
fi
```

## 6. Pattern Matching (Bash-only, `[[ ]]`)

```bash
if [[ "$email" == *@gmail.com ]]; then
    echo "Gmail address"
fi

if [[ "$file" == *.log ]]; then
    echo "Log file"
fi
```

## 7. Common Mistakes

❌ Missing spaces
```bash
if[$a -eq 1]   # WRONG — needs spaces around [ and ]
```
✅ Correct
```bash
if [ $a -eq 1 ]
```

❌ Comparing numbers with string operators
```bash
if [ "$a" > "$b" ]   # WRONG inside [ ]: '>' is shell redirection here, not "greater than"
```
✅ Correct
```bash
if [ "$a" -gt "$b" ]
```

❌ Unquoted variables
```bash
if [ $name = Jack ]  # Risky — breaks if $name is empty or contains spaces/glob characters
```
✅ Always quote
```bash
if [ "$name" = "Jack" ]
```

## 8. Real-World Example

```bash
#!/bin/bash

FILE="data.csv"

if [[ -f "$FILE" && -s "$FILE" ]]; then
    echo "Processing file..."
elif [[ -f "$FILE" ]]; then
    echo "File exists but empty"
else
    echo "File not found"
fi
```

This is how real Linux automation scripts are written — clean, defensive, predictable.

## 9. Mental Model

- **Strings** → `[ ]` or `[[ ]]`, compared with `=`/`!=` (or `==` in `[[ ]]`)
- **Numbers** → `-eq`, `-gt`, … or `(( ))`
- **Files** → `-f`, `-d`, `-r`, `-w`, `-x`, `-s`, `-e`
- **Complex logic** → prefer `[[ ]]` over `[ ]`

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/Bash Scripting/Looping Conditions|The Beginner's Complete Guide to Bash Loops]]
- [[Data Engineering Role Notes/Linux/Linux Summary Guide|Linux Masterclass Concepts]]

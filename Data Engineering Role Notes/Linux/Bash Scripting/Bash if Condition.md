Below is a **clear, practical, and industry-ready guide** to using **`if` conditions in Bash**—covering **strings, numbers, and files**. This is written to improve both your **Linux confidence** and your **technical English clarity**.

---

# Bash `if` Condition — Complete Guide (Strings, Numbers, Files)

## 1️⃣ Basic `if` Syntax (Foundation)

```bash
if [ condition ]; then
    command
elif [ another_condition ]; then
    command
else
    command
fi
```

**Non-negotiables (people mess this up):**

- Spaces **before and after** `[` and `]` are mandatory
    
- `then` must be on a **new line** or after `;`
    
- Use `[` (POSIX) or `[[` (Bash-preferred)
    

---

## 2️⃣ String Conditions (Most Interview-Relevant)

### ✅ String Equality

```bash
if [ "$name" = "Jack" ]; then
    echo "Welcome Jack"
fi
```

> Use `=` (not `==`) with `[ ]`

### ✅ String Not Equal

```bash
if [ "$role" != "admin" ]; then
    echo "Access limited"
fi
```

### ✅ Empty String

```bash
if [ -z "$username" ]; then
    echo "Username is empty"
fi
```

### ✅ Non-Empty String

```bash
if [ -n "$username" ]; then
    echo "Username provided"
fi
```

### ⚡ Best Practice (Modern Bash)

```bash
if [[ "$name" == "Jack" ]]; then
    echo "Matched"
fi
```

Why `[[ ]]` is better:

- No need to escape special characters
    
- Supports pattern matching
    
- Safer and cleaner
    

---

## 3️⃣ Numeric Conditions (Very Common in Scripts)

### ❌ DO NOT use `=`, `<`, `>` for numbers

### ✅ Correct Numeric Operators

|Operator|Meaning|
|---|---|
|`-eq`|equal|
|`-ne`|not equal|
|`-gt`|greater than|
|`-ge`|greater or equal|
|`-lt`|less than|
|`-le`|less or equal|

### Example

```bash
if [ "$age" -ge 18 ]; then
    echo "Eligible"
else
    echo "Not eligible"
fi
```

### ⚡ Arithmetic Style (Cleaner)

```bash
if (( age >= 18 )); then
    echo "Eligible"
fi
```

Use `(( ))` for **pure numeric logic**—it’s faster and clearer.

---

## 4️⃣ File & Directory Conditions (Real-World Scripts)

### ✅ File Exists

```bash
if [ -f "data.txt" ]; then
    echo "File exists"
fi
```

### ✅ Directory Exists

```bash
if [ -d "/var/log" ]; then
    echo "Directory found"
fi
```

### ✅ File Exists (Any Type)

```bash
if [ -e "config.yaml" ]; then
    echo "Exists"
fi
```

### ✅ Read / Write / Execute Permission

```bash
if [ -r "file.txt" ]; then echo "Readable"; fi
if [ -w "file.txt" ]; then echo "Writable"; fi
if [ -x "script.sh" ]; then echo "Executable"; fi
```

### ✅ File Is Empty / Not Empty

```bash
if [ -s "file.txt" ]; then
    echo "Not empty"
else
    echo "Empty"
fi
```

---

## 5️⃣ Logical AND / OR (Decision Control)

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

---

## 6️⃣ Pattern Matching (Advanced but Powerful)

```bash
if [[ "$email" == *@gmail.com ]]; then
    echo "Gmail address"
fi
```

```bash
if [[ "$file" == *.log ]]; then
    echo "Log file"
fi
```

---

## 7️⃣ Common Mistakes (Tell It Like It Is)

❌ Missing spaces

```bash
if[$a -eq 1]   # WRONG
```

✅ Correct

```bash
if [ $a -eq 1 ]
```

❌ Comparing numbers as strings

```bash
if [ "$a" > "$b" ]   # WRONG
```

✅ Correct

```bash
if [ "$a" -gt "$b" ]
```

❌ Unquoted variables

```bash
if [ $name = Jack ]  # Risky
```

✅ Always quote

```bash
if [ "$name" = "Jack" ]
```

---

## 8️⃣ Real-World Example (Production-Quality)

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

**Why this matters:**  
This is how **real Linux automation scripts** are written—clean, defensive, and predictable.

---

## 9️⃣ Mental Model (Remember This)

- **Strings** → `[ ]` or `[[ ]]`
    
- **Numbers** → `-eq`, `-gt` or `(( ))`
    
- **Files** → `-f`, `-d`, `-r`, `-w`
    
- **Complex logic** → always prefer `[[ ]]`
    

---

If you want next:

- `case` vs `if`
    
- validating user input
    
- bash conditions in **cron jobs**
    
- interview-ready bash questions
    
- mini practice exercises (recommended)
    

Say the word.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/Bash Scripting/Looping Conditions|The Beginner's Complete Guide to Bash Loops]]
- [[Data Engineering Role Notes/Linux/Linux Summary Guide|Linux Masterclass Concepts]]

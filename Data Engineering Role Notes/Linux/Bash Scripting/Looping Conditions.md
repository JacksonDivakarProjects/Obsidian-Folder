# 🌀 The Beginner's Complete Guide to Bash Loops

Loops are the core tool for automating repetitive tasks in Bash: write the logic once, tell Bash to repeat it, instead of copy-pasting the same commands.

## 📚 Table of Contents
1. [What Are Loops?](#what-are-loops)
2. [The For Loop](#the-for-loop)
3. [The While Loop](#the-while-loop)
4. [The Until Loop](#the-until-loop)
5. [Loop Control](#loop-control)
6. [Nested Loops](#nested-loops)
7. [Practical Examples](#practical-examples)
8. [Best Practices](#best-practices)

---

## 1. What Are Loops? 🤔

A loop repeats a block of commands multiple times without rewriting it. Instead of "take one step" repeated 100 times, you say "take steps until you reach the end."

### Why use loops?
- Automate repetitive tasks
- Process multiple files
- Handle lists of items
- Create counters
- Wait for conditions to be met

---

## 2. The For Loop 🔄

Use `for` when you know how many times to repeat, or you're iterating over a known list of items.

### Basic syntax
```bash
for variable in list_of_items
do
    # Commands to execute
    echo "Processing: $variable"
done
```

### Example 1: Simple list
```bash
#!/bin/bash
# The shebang tells the system this is a Bash script

for fruit in apple banana orange
do
    echo "I like $fruit"
done
```
Output:
```
I like apple
I like banana
I like orange
```

### Example 2: Numeric range
```bash
#!/bin/bash
for number in {1..5}
do
    echo "Count: $number"
done
```

### Example 3: Processing files (globbing)
```bash
#!/bin/bash
for file in *.txt
do
    echo "Found text file: $file"
done
```

### Example 4: C-style for loop
```bash
#!/bin/bash
for (( i=1; i<=5; i++ ))
do
    echo "Iteration $i"
done
```

---

## 3. The While Loop ⏳

`while` keeps running **as long as a condition stays true**. Use it when you don't know the iteration count in advance.

### Basic syntax
```bash
while [ condition ]
do
    # Commands to execute
    echo "Looping..."
done
```

### Example 1: Simple counter
```bash
#!/bin/bash
counter=1

while [ $counter -le 5 ]
do
    echo "Counter: $counter"
    ((counter++))  # Increment the counter
done
```

### Example 2: Reading user input
```bash
#!/bin/bash
answer=""

while [ "$answer" != "yes" ]
do
    echo "Do you want to continue? (yes/no)"
    read answer
done
echo "Finally!"
```

### Example 3: Reading a file line by line
```bash
#!/bin/bash
while read line
do
    echo "Line: $line"
done < file.txt
```

---

## 4. The Until Loop 🔄

`until` is the mirror image of `while` — it runs **until a condition becomes true** (i.e., while it's still false).

### Basic syntax
```bash
until [ condition ]
do
    # Commands to execute
    echo "Waiting..."
done
```

### Example: waiting for a file to appear
```bash
#!/bin/bash
until [ -f /tmp/myfile.txt ]
do
    echo "File doesn't exist yet. Waiting..."
    sleep 2
done
echo "File found!"
```

---

## 5. Loop Control 🎮

Bash gives you three ways to change loop behavior mid-run:

### `break` — exit the loop early
```bash
#!/bin/bash
for number in {1..10}
do
    if [ $number -eq 5 ]
    then
        echo "Breaking at 5!"
        break
    fi
    echo "Number: $number"
done
```

### `continue` — skip to the next iteration
```bash
#!/bin/bash
for number in {1..5}
do
    if [ $number -eq 3 ]
    then
        echo "Skipping 3!"
        continue
    fi
    echo "Number: $number"
done
```

### `exit` — terminate the entire script (not just the loop)
```bash
#!/bin/bash
for number in {1..5}
do
    if [ $number -eq 3 ]
    then
        echo "Exiting script!"
        exit 1
    fi
    echo "Number: $number"
done
```

---

## 6. Nested Loops 🔄🔄

Loops can contain other loops — useful for grids or multi-dimensional data.

### Example: multiplication table
```bash
#!/bin/bash
echo "Simple Multiplication Table:"
echo "---------------------------"

for i in {1..3}
do
    for j in {1..3}
    do
        result=$((i * j))
        echo -n "$i x $j = $result   "
    done
    echo ""  # New line after each row
done
```
Output:
```
Simple Multiplication Table:
---------------------------
1 x 1 = 1   1 x 2 = 2   1 x 3 = 3   
2 x 1 = 2   2 x 2 = 4   2 x 3 = 6   
3 x 1 = 3   3 x 2 = 6   3 x 3 = 9   
```

---

## 7. Practical Examples 🛠️

### Example 1: Backup script
```bash
#!/bin/bash
# Backup important files
backup_dir="/backup"
files_to_backup="/home/user/documents/*.pdf"

for file in $files_to_backup
do
    if [ -f "$file" ]
    then
        cp "$file" "$backup_dir"
        echo "Backed up: $(basename $file)"
    fi
done
```

### Example 2: System monitoring
```bash
#!/bin/bash
# Check disk usage every minute until it's too high
threshold=80

while true
do
    usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')

    if [ $usage -gt $threshold ]
    then
        echo "WARNING: Disk usage is $usage%"
        echo "Sending alert..."
        # Add your alert command here
        break
    fi

    echo "Disk usage: $usage% - OK"
    sleep 60
done
```

### Example 3: User management
```bash
#!/bin/bash
# Create multiple user accounts
usernames="alice bob charlie diana"

for user in $usernames
do
    echo "Creating account for $user"
    # In a real script: sudo useradd $user
    # For now, just simulate:
    echo "Account $user created successfully!"
done
```

### Example 4: File organizer
```bash
#!/bin/bash
# Organize files by extension
for file in *
do
    if [ -f "$file" ]
    then
        extension="${file##*.}"
        mkdir -p "$extension" 2>/dev/null
        mv "$file" "$extension/"
        echo "Moved $file to $extension/"
    fi
done
```

---

## 8. Best Practices & Tips 💡

### 1. Always quote variables
```bash
# Good:
for file in "$file_list"
do
    echo "Processing: $file"
done

# Bad (breaks with spaces in filenames):
for file in $file_list
do
    echo "Processing: $file"
done
```

### 2. Use meaningful variable names
```bash
# Good:
for student_name in $student_list

# Confusing:
for x in $y
```

### 3. Add comments
```bash
#!/bin/bash
# This script processes log files
# Created by: Your Name
# Date: 2024

for logfile in /var/log/*.log
do
    # Check if file exists and is readable
    if [ -r "$logfile" ]
    then
        echo "Processing: $logfile"
        # Add processing commands here
    fi
done
```

### 4. Use `set -x` for debugging
```bash
#!/bin/bash
set -x  # Shows each command before executing

for i in {1..3}
do
    echo "Iteration $i"
done

set +x  # Turns off debugging
```

### 5. Handle errors
```bash
#!/bin/bash
set -e  # Exit on any error

for file in /important/files/*
do
    if [ ! -f "$file" ]
    then
        echo "Error: $file not found!" >&2
        continue  # Skip to next file instead of exiting
    fi
    # Process the file
done
```

### 6. Common pitfalls to avoid
- **Infinite loops** — always have an exit condition
- **Unquoted variables** — breaks on filenames with spaces
- **Forgetting to increment counters** in `while` loops
- **Using `ls` in loops** — use globbing (`*.txt`) instead; `ls` output is fragile to parse (breaks on filenames with spaces/newlines)

---

## 🎯 Quick Reference Cheat Sheet

| Loop Type | When to Use | Example |
|-----------|-------------|---------|
| `for` | Known iterations, list processing | `for file in *.txt` |
| `while` | Unknown iterations, conditions | `while [ $x -lt 10 ]` |
| `until` | Wait for a condition | `until [ -f file.txt ]` |
| `break` | Exit loop early | `break` |
| `continue` | Skip an iteration | `continue` |

---

## 🚀 Practice Exercises

1. **Countdown timer** — write a script that counts from 10 to 1
2. **File counter** — count how many `.txt` files are in a directory
3. **Number guesser** — create a simple number-guessing game
4. **Directory creator** — create directories named `week01` through `week52`

---

## 📖 Next Steps

1. Combine loops with conditionals (`if`, `case`) — see [[Data Engineering Role Notes/Linux/Bash Scripting/Bash if Condition|Bash if Condition]]
2. Use loops with functions to create reusable code
3. Explore arrays for more complex data handling
4. Learn command substitution to feed command output into loops

**Pro tip:** run these examples directly:
1. Create a file: `nano myscript.sh`
2. Add the code
3. Make it executable: `chmod +x myscript.sh`
4. Run it: `./myscript.sh`

Or test a small loop directly in the terminal:
```bash
for i in {1..3}; do echo "Test $i"; done
```

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/Bash Scripting/Bash if Condition|Bash if Condition — Complete Guide (Strings, Numbers, Files)]]
- [[Data Engineering Role Notes/Linux/nohup (Background Process)/nohup Guide|The Complete nohup Guide for Beginners]]
- [[Data Engineering Role Notes/Linux/Linux Summary Guide|Linux Masterclass Concepts]]

# 🌀 The Beginner's Complete Guide to Bash Loops

Welcome to the world of Bash scripting! Loops are fundamental tools that let you automate repetitive tasks. This guide will walk you through everything you need to know about loops in Bash, with simple explanations and practical examples.

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

**Loops** let you repeat a set of commands multiple times. Instead of writing the same code over and over, you write it once and tell Bash to repeat it.

Think of it like this: Instead of telling someone "Take one step" 100 times, you say "Take steps until you reach the end."

### Why Use Loops?
- **Automate repetitive tasks**
- **Process multiple files**
- **Handle lists of items**
- **Create counters**
- **Wait for conditions to be met**

---

## 2. The For Loop 🔄

The `for` loop is perfect when you know exactly how many times you want to repeat something, or when you're working with a list of items.

### Basic Syntax:
```bash
for variable in list_of_items
do
    # Commands to execute
    echo "Processing: $variable"
done
```

### Example 1: Simple List
```bash
#!/bin/bash
# This is called a shebang - it tells the system this is a Bash script

for fruit in apple banana orange
do
    echo "I like $fruit"
done
```

**Output:**
```
I like apple
I like banana
I like orange
```

### Example 2: Using a Range
```bash
#!/bin/bash
for number in {1..5}
do
    echo "Count: $number"
done
```

### Example 3: Processing Files
```bash
#!/bin/bash
for file in *.txt
do
    echo "Found text file: $file"
done
```

### Example 4: C-Style For Loop
```bash
#!/bin/bash
for (( i=1; i<=5; i++ ))
do
    echo "Iteration $i"
done
```

---

## 3. The While Loop ⏳

The `while` loop keeps running **as long as a condition is true**. It's great when you don't know exactly how many times you need to loop.

### Basic Syntax:
```bash
while [ condition ]
do
    # Commands to execute
    echo "Looping..."
done
```

### Example 1: Simple Counter
```bash
#!/bin/bash
counter=1

while [ $counter -le 5 ]
do
    echo "Counter: $counter"
    ((counter++))  # Increment the counter
done
```

### Example 2: Reading User Input
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

### Example 3: Reading a File Line by Line
```bash
#!/bin/bash
while read line
do
    echo "Line: $line"
done < file.txt
```

---

## 4. The Until Loop 🔄

The `until` loop is the opposite of `while` - it runs **until a condition becomes true**.

### Basic Syntax:
```bash
until [ condition ]
do
    # Commands to execute
    echo "Waiting..."
done
```

### Example: Waiting for a File to Exist
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

Sometimes you need to change how a loop behaves. Bash provides special commands for this:

### `break` - Exit the Loop Early
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

### `continue` - Skip to Next Iteration
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

### `exit` - Exit the Entire Script
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

You can put loops inside other loops! This is useful for working with grids or multiple dimensions.

### Example: Multiplication Table
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

**Output:**
```
Simple Multiplication Table:
---------------------------
1 x 1 = 1   1 x 2 = 2   1 x 3 = 3   
2 x 1 = 2   2 x 2 = 4   2 x 3 = 6   
3 x 1 = 3   3 x 2 = 6   3 x 3 = 9   
```

---

## 7. Practical Examples 🛠️

Let's look at some real-world scenarios:

### Example 1: Backup Script
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

### Example 2: System Monitoring
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

### Example 3: User Management
```bash
#!/bin/bash
# Create multiple user accounts
usernames="alice bob charlie diana"

for user in $usernames
do
    echo "Creating account for $user"
    # In real script: sudo useradd $user
    # For now, just simulate:
    echo "Account $user created successfully!"
done
```

### Example 4: File Organizer
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

### 1. **Always Quote Variables**
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

### 2. **Use Meaningful Variable Names**
```bash
# Good:
for student_name in $student_list

# Confusing:
for x in $y
```

### 3. **Add Comments**
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

### 4. **Test with `set -x` for Debugging**
```bash
#!/bin/bash
set -x  # Shows each command before executing

for i in {1..3}
do
    echo "Iteration $i"
done

set +x  # Turns off debugging
```

### 5. **Handle Errors**
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

### 6. **Common Pitfalls to Avoid**
- **Infinite loops**: Always have an exit condition!
- **Unquoted variables**: Causes problems with spaces
- **Forgetting to increment counters** in while loops
- **Using `ls` in loops**: Use globbing (`*.txt`) instead

---

## 🎯 Quick Reference Cheat Sheet

| Loop Type | When to Use | Example |
|-----------|-------------|---------|
| `for` | Known iterations, list processing | `for file in *.txt` |
| `while` | Unknown iterations, conditions | `while [ $x -lt 10 ]` |
| `until` | Wait for condition | `until [ -f file.txt ]` |
| `break` | Exit loop early | `break` |
| `continue` | Skip iteration | `continue` |

---

## 🚀 Practice Exercises

Try these to test your understanding:

1. **Countdown Timer**: Write a script that counts from 10 to 1
2. **File Counter**: Count how many `.txt` files are in a directory
3. **Number Guesser**: Create a simple number guessing game
4. **Directory Creator**: Create directories named `week01` through `week52`

---

## 📖 Next Steps

Now that you understand loops, you can:
1. Combine loops with **conditionals** (`if`, `case`)
2. Use loops with **functions** to create reusable code
3. Explore **arrays** for more complex data handling
4. Learn about **command substitution** to use command output in loops

Remember: Practice makes perfect! Start with simple loops and gradually build up to more complex scripts. Happy scripting! 🐚✨

---

**Pro Tip**: You can run these examples directly in your terminal by:
1. Creating a file: `nano myscript.sh`
2. Adding the code
3. Making it executable: `chmod +x myscript.sh`
4. Running it: `./myscript.sh`

Or test small loops directly in the terminal:
```bash
for i in {1..3}; do echo "Test $i"; done
```

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/Bash Scripting/Bash if Condition|Bash if Condition — Complete Guide (Strings, Numbers, Files)]]
- [[Data Engineering Role Notes/Linux/nohup (Background Process)/nohup Guide|The Complete nohup Guide for Beginners]]
- [[Data Engineering Role Notes/Linux/Linux Summary Guide|Linux Masterclass Concepts]]

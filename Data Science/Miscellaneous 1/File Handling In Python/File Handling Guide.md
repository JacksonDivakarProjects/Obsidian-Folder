# Comprehensive Guide to File Handling in Python

File handling is a crucial aspect of programming that allows you to store data persistently and work with external files. Python provides robust and intuitive file handling capabilities.

## Table of Contents
1. [Basic File Operations](#basic-file-operations)
2. [File Modes](#file-modes)
3. [Reading Files](#reading-files)
4. [Writing Files](#writing-files)
5. [Working with Binary Files](#working-with-binary-files)
6. [File Positioning](#file-positioning)
7. [File and Directory Management](#file-and-directory-management)
8. [Context Managers](#context-managers)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)

## Basic File Operations

### Opening a File
```python
# Basic syntax
file = open(filename, mode)

# Example
file = open("example.txt", "r")
```

### Closing a File
```python
file = open("example.txt", "r")
# Perform operations
file.close()  # Always close files when done
```

## File Modes

| Mode | Description |
|------|-------------|
| `r` | Read (default) - opens for reading |
| `w` | Write - creates new file or truncates existing |
| `a` | Append - writes to end of file |
| `x` | Exclusive creation - fails if file exists |
| `b` | Binary mode |
| `t` | Text mode (default) |
| `+` | Reading and writing |

### Common Mode Combinations
```python
# Read and write text file
file = open("file.txt", "r+")

# Write binary file
file = open("image.jpg", "wb")

# Append to text file
file = open("log.txt", "a")

# Read, write, create if doesn't exist
file = open("data.txt", "w+")
```

## Reading Files

### Reading Entire Content
```python
# Read entire file as string
with open("example.txt", "r") as file:
    content = file.read()
    print(content)
```

### Reading Line by Line
```python
# Read all lines into list
with open("example.txt", "r") as file:
    lines = file.readlines()
    for line in lines:
        print(line.strip())  # strip() removes newline characters

# More memory-efficient for large files
with open("example.txt", "r") as file:
    for line in file:
        print(line.strip())
```

### Reading Specific Amount
```python
# Read first 100 characters
with open("example.txt", "r") as file:
    chunk = file.read(100)
    print(chunk)

# Read line with limit
with open("example.txt", "r") as file:
    line = file.readline(50)  # Read at most 50 characters from line
```

## Writing Files

### Writing Text
```python
# Write to file (overwrites existing content)
with open("output.txt", "w") as file:
    file.write("Hello, World!\n")
    file.write("This is a new line.\n")

# Writing multiple lines
lines = ["Line 1\n", "Line 2\n", "Line 3\n"]
with open("output.txt", "w") as file:
    file.writelines(lines)
```

### Appending to Files
```python
# Append to existing file
with open("log.txt", "a") as file:
    file.write("New log entry\n")
    file.write("Another entry\n")
```

## Working with Binary Files

### Reading Binary Files
```python
# Read image file
with open("image.jpg", "rb") as file:
    binary_data = file.read()
    # Process binary data

# Read binary file in chunks
with open("large_file.bin", "rb") as file:
    while True:
        chunk = file.read(1024)  # Read 1KB at a time
        if not chunk:
            break
        # Process chunk
```

### Writing Binary Files
```python
# Write binary data
binary_data = b'\x48\x65\x6c\x6c\x6f'  # Hello in bytes
with open("binary_file.bin", "wb") as file:
    file.write(binary_data)

# Copy binary file
with open("source.jpg", "rb") as source:
    with open("copy.jpg", "wb") as destination:
        for chunk in iter(lambda: source.read(4096), b""):
            destination.write(chunk)
```

## File Positioning

### Getting and Setting Position
```python
with open("example.txt", "r") as file:
    # Get current position
    position = file.tell()
    print(f"Current position: {position}")
    
    # Read some content
    content = file.read(10)
    
    # Get new position
    position = file.tell()
    print(f"New position: {position}")
    
    # Move to specific position
    file.seek(0)  # Beginning of file
    file.seek(5)  # 5th byte from beginning
    file.seek(10, 1)  # 10 bytes from current position
    file.seek(-5, 2)  # 5 bytes from end
```

### Practical Example: Random Access
```python
def read_specific_lines(filename, line_numbers):
    """Read specific lines from a file"""
    with open(filename, 'r') as file:
        lines = []
        for i, line in enumerate(file):
            if i + 1 in line_numbers:
                lines.append(line.strip())
        return lines

# Usage
lines = read_specific_lines("example.txt", [1, 3, 5])
```

## File and Directory Management

### Using os module
```python
import os

# Check if file exists
if os.path.exists("file.txt"):
    print("File exists")

# Get file size
size = os.path.getsize("file.txt")

# Rename file
os.rename("old_name.txt", "new_name.txt")

# Remove file
os.remove("file.txt")

# Working with directories
os.mkdir("new_directory")
os.rmdir("empty_directory")
os.listdir(".")  # List directory contents
```

### Using pathlib (Modern Approach)
```python
from pathlib import Path

# Create Path object
file_path = Path("example.txt")

# Check existence
if file_path.exists():
    print("File exists")

# Get file info
print(f"File name: {file_path.name}")
print(f"Parent directory: {file_path.parent}")
print(f"File extension: {file_path.suffix}")

# Read file
content = file_path.read_text()

# Write file
file_path.write_text("New content")

# Working with directories
dir_path = Path("my_directory")
dir_path.mkdir(exist_ok=True)
```

## Context Managers

### The `with` Statement
```python
# Automatically closes file
with open("example.txt", "r") as file:
    content = file.read()
# File is automatically closed here

# Equivalent to:
try:
    file = open("example.txt", "r")
    content = file.read()
finally:
    file.close()
```

### Multiple Files
```python
# Working with multiple files simultaneously
with open("source.txt", "r") as source, open("destination.txt", "w") as dest:
    content = source.read()
    dest.write(content)
```

## Error Handling

### Basic Exception Handling
```python
try:
    with open("nonexistent.txt", "r") as file:
        content = file.read()
except FileNotFoundError:
    print("File not found!")
except PermissionError:
    print("Permission denied!")
except IOError as e:
    print(f"I/O error occurred: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Robust File Handling Function
```python
def safe_file_operation(filename, operation="read", data=None):
    """
    Safely perform file operations with error handling
    """
    try:
        if operation == "read":
            with open(filename, 'r') as file:
                return file.read()
        elif operation == "write":
            with open(filename, 'w') as file:
                file.write(data)
                return True
        elif operation == "append":
            with open(filename, 'a') as file:
                file.write(data)
                return True
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except PermissionError:
        print(f"Error: Permission denied for '{filename}'.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# Usage
content = safe_file_operation("example.txt", "read")
success = safe_file_operation("output.txt", "write", "Hello World")
```

## Best Practices

### 1. Always Use Context Managers
```python
# ✅ Good
with open("file.txt", "r") as file:
    content = file.read()

# ❌ Avoid
file = open("file.txt", "r")
content = file.read()
file.close()  # Might be forgotten
```

### 2. Handle Different Encodings
```python
# Specify encoding for text files
with open("file.txt", "r", encoding="utf-8") as file:
    content = file.read()

with open("file.txt", "w", encoding="utf-8") as file:
    file.write("Some text")
```

### 3. Use Pathlib for Path Operations
```python
from pathlib import Path

file_path = Path("data") / "subfolder" / "file.txt"
file_path.parent.mkdir(parents=True, exist_ok=True)  # Create directories if needed
file_path.write_text("Hello World")
```

### 4. Process Large Files in Chunks
```python
def process_large_file(filename, chunk_size=8192):
    """Process large files efficiently"""
    with open(filename, 'r') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            # Process chunk
            process_chunk(chunk)

def process_large_file_by_lines(filename):
    """Process large files line by line"""
    with open(filename, 'r') as file:
        for line in file:
            process_line(line.strip())
```

### 5. Comprehensive File Operations Class
```python
class FileHandler:
    """A comprehensive file handling utility class"""
    
    def __init__(self, filename):
        self.filename = Path(filename)
    
    def read(self):
        """Read entire file content"""
        try:
            return self.filename.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    
    def write(self, content):
        """Write content to file"""
        try:
            self.filename.parent.mkdir(parents=True, exist_ok=True)
            self.filename.write_text(content, encoding='utf-8')
            return True
        except Exception as e:
            print(f"Error writing file: {e}")
            return False
    
    def append(self, content):
        """Append content to file"""
        try:
            with open(self.filename, 'a', encoding='utf-8') as file:
                file.write(content)
            return True
        except Exception as e:
            print(f"Error appending to file: {e}")
            return False
    
    def copy(self, destination):
        """Copy file to destination"""
        try:
            import shutil
            shutil.copy2(self.filename, destination)
            return True
        except Exception as e:
            print(f"Error copying file: {e}")
            return False
    
    def get_info(self):
        """Get file information"""
        if self.filename.exists():
            return {
                'size': self.filename.stat().st_size,
                'modified': self.filename.stat().st_mtime,
                'is_file': self.filename.is_file(),
                'is_dir': self.filename.is_dir()
            }
        return None

# Usage
file_handler = FileHandler("example.txt")
content = file_handler.read()
file_handler.write("New content")
info = file_handler.get_info()
```

## Practical Examples

### 1. CSV File Processing
```python
import csv

# Reading CSV
with open('data.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)

# Writing CSV
data = [['Name', 'Age'], ['Alice', 30], ['Bob', 25]]
with open('output.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data)
```

### 2. JSON File Handling
```python
import json

# Reading JSON
with open('data.json', 'r') as file:
    data = json.load(file)

# Writing JSON
data = {'name': 'Alice', 'age': 30, 'city': 'New York'}
with open('output.json', 'w') as file:
    json.dump(data, file, indent=4)
```

### 3. Configuration File
```python
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# Get value
database_host = config['database']['host']

# Write configuration
config['database'] = {'host': 'localhost', 'port': '5432'}
with open('config.ini', 'w') as configfile:
    config.write(configfile)
```

### 4. Log File Rotation
```python
import logging
from logging.handlers import RotatingFileHandler

# Setup rotating file handler
logger = logging.getLogger('my_app')
handler = RotatingFileHandler('app.log', maxBytes=1000000, backupCount=5)
logger.addHandler(handler)

logger.info("This is a log message")
```

This comprehensive guide covers all essential aspects of file handling in Python. Remember to always handle files responsibly by closing them properly and implementing error handling to make your code robust and reliable.
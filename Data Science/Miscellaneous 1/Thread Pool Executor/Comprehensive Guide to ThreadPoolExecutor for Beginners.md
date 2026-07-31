
## Table of Contents
1. [What is ThreadPoolExecutor?](#what-is-threadpoolexecutor)
2. [Why Use ThreadPoolExecutor?](#why-use-threadpoolexecutor)
3. [Basic Usage](#basic-usage)
4. [Key Parameters](#key-parameters)
5. [Practical Functions and Methods](#practical-functions-and-methods)
6. [Common Patterns and Best Practices](#common-patterns-and-best-practices)
7. [Error Handling](#error-handling)
8. [Real-World Examples](#real-world-examples)

## What is ThreadPoolExecutor?

ThreadPoolExecutor is a high-level interface for managing threads in Python. It's part of the `concurrent.futures` module and provides a simple way to execute functions asynchronously using a pool of worker threads.

Think of it as having a team of workers (threads) ready to perform tasks. Instead of creating a new worker for each task, you reuse existing workers, which is much more efficient.

## Why Use ThreadPoolExecutor?

- **Efficiency**: Reuses threads instead of creating new ones
- **Simplicity**: Easy-to-use interface for parallel execution
- **Control**: Manage the number of concurrent threads
- **Future-based**: Get results when they're ready

## Basic Usage

### Importing and Simple Example

```python
from concurrent.futures import ThreadPoolExecutor
import time

def simple_task(name, duration):
    """A simple function that simulates work by sleeping"""
    print(f"Task {name} starting")
    time.sleep(duration)
    print(f"Task {name} completed")
    return f"Result from {name}"

# Basic usage
with ThreadPoolExecutor(max_workers=3) as executor:
    # Submit tasks to the executor
    future1 = executor.submit(simple_task, "A", 2)
    future2 = executor.submit(simple_task, "B", 1)
    future3 = executor.submit(simple_task, "C", 3)
    
    # Get results
    print(future1.result())
    print(future2.result())
    print(future3.result())
```

## Key Parameters

### max_workers
The maximum number of threads that can be used

```python
# Different ways to set max_workers
executor1 = ThreadPoolExecutor()  # Default (usually 5 * number of CPUs)
executor2 = ThreadPoolExecutor(max_workers=10)  # Specific number
executor3 = ThreadPoolExecutor(max_workers=None)  # Let executor decide
```

### thread_name_prefix
Name your threads for debugging

```python
executor = ThreadPoolExecutor(
    max_workers=3, 
    thread_name_prefix="DownloadWorker"
)
```

## Practical Functions and Methods

### 1. submit() - Most Commonly Used

```python
def download_file(url, filename):
    """Simulate downloading a file"""
    import requests
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)
    return f"Downloaded {filename}"

with ThreadPoolExecutor(max_workers=3) as executor:
    # Submit individual tasks
    future1 = executor.submit(download_file, "http://example.com/1", "file1.txt")
    future2 = executor.submit(download_file, "http://example.com/2", "file2.txt")
    
    # Get results when ready
    result1 = future1.result(timeout=30)  # Wait max 30 seconds
    result2 = future2.result()
```

### 2. map() - Process Collections

```python
def process_item(item):
    """Process a single item"""
    return item.upper()

items = ["apple", "banana", "cherry", "date", "elderberry"]

# Process all items in parallel
with ThreadPoolExecutor(max_workers=2) as executor:
    results = list(executor.map(process_item, items))
    print(results)  # ['APPLE', 'BANANA', 'CHERRY', 'DATE', 'ELDERBERRY']

# With timeout
with ThreadPoolExecutor(max_workers=2) as executor:
    results = list(executor.map(process_item, items, timeout=10))
```

### 3. as_completed() - Process Results as They Complete

```python
import random
from concurrent.futures import as_completed

def random_duration_task(name):
    duration = random.uniform(0.5, 3.0)
    time.sleep(duration)
    return f"{name} completed in {duration:.2f}s"

tasks = [f"Task_{i}" for i in range(5)]

with ThreadPoolExecutor(max_workers=3) as executor:
    # Submit all tasks
    futures = [executor.submit(random_duration_task, task) for task in tasks]
    
    # Process results in completion order (not submission order)
    for future in as_completed(futures):
        result = future.result()
        print(f"Got result: {result}")
```

### 4. shutdown() - Managing Executor Lifecycle

```python
# Manual management (not recommended for beginners)
executor = ThreadPoolExecutor(max_workers=3)

try:
    future = executor.submit(simple_task, "manual", 1)
    result = future.result()
    print(result)
finally:
    executor.shutdown(wait=True)  # Wait for all threads to complete

# Context manager (recommended)
with ThreadPoolExecutor(max_workers=3) as executor:
    future = executor.submit(simple_task, "auto", 1)
    result = future.result()
    print(result)
# Executor automatically shuts down here
```

## Common Patterns and Best Practices

### Pattern 1: URL Checking with Timeouts

```python
def check_url(url, timeout=5):
    """Check if a URL is accessible"""
    import requests
    try:
        response = requests.get(url, timeout=timeout)
        return url, response.status_code, len(response.content)
    except Exception as e:
        return url, "ERROR", str(e)

urls = [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
    "https://invalid-url-that-does-not-exist.com"
]

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(check_url, url) for url in urls]
    
    for future in as_completed(futures):
        url, status, info = future.result()
        print(f"URL: {url} | Status: {status} | Info: {info}")
```

### Pattern 2: Batch Processing with Progress Tracking

```python
def process_with_progress(data_chunk, chunk_id):
    """Process data chunk and return progress info"""
    time.sleep(1)  # Simulate work
    return {
        'chunk_id': chunk_id,
        'processed_items': len(data_chunk),
        'result': sum(data_chunk)  # Example processing
    }

# Split data into chunks
data = list(range(1000))
chunk_size = 100
chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

with ThreadPoolExecutor(max_workers=4) as executor:
    # Submit all chunks
    futures = {
        executor.submit(process_with_progress, chunk, i): i 
        for i, chunk in enumerate(chunks)
    }
    
    completed = 0
    total = len(chunks)
    
    for future in as_completed(futures):
        result = future.result()
        completed += 1
        print(f"Progress: {completed}/{total} - Chunk {result['chunk_id']} done")
```

### Pattern 3: Configurable Worker Pattern

```python
class DataProcessor:
    def __init__(self, max_workers=None):
        self.max_workers = max_workers or 4
    
    def process_data(self, data_items, process_function):
        """Process data items using ThreadPoolExecutor"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(process_function, item) 
                for item in data_items
            ]
            
            results = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Error processing item: {e}")
            
            return results

# Usage
processor = DataProcessor(max_workers=3)

def square_number(x):
    return x * x

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
squared = processor.process_data(numbers, square_number)
print(squared)
```

## Error Handling

### Basic Error Handling

```python
def risky_operation(x):
    """A function that might fail"""
    if x % 3 == 0:
        raise ValueError(f"Number {x} is divisible by 3!")
    return x * 2

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]

with ThreadPoolExecutor(max_workers=2) as executor:
    futures = [executor.submit(risky_operation, num) for num in numbers]
    
    for future in as_completed(futures):
        try:
            result = future.result()
            print(f"Success: {result}")
        except Exception as e:
            print(f"Failed: {e}")
```

### Advanced Error Handling with Custom Wrapper

```python
def safe_execute(func, *args, **kwargs):
    """Wrapper function for safe execution"""
    try:
        return func(*args, **kwargs), None  # (result, error)
    except Exception as e:
        return None, e

def process_data(data):
    if data < 0:
        raise ValueError("Negative numbers not allowed")
    return data ** 2

data_points = [1, 2, -3, 4, 5, -6]

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(safe_execute, process_data, data) 
        for data in data_points
    ]
    
    successful = []
    errors = []
    
    for future in as_completed(futures):
        result, error = future.result()
        if error:
            errors.append(error)
        else:
            successful.append(result)
    
    print(f"Successful: {successful}")
    print(f"Errors: {[str(e) for e in errors]}")
```

## Real-World Examples

### Example 1: Web Scraping Multiple Pages

```python
import requests
from bs4 import BeautifulSoup

def scrape_page(url):
    """Scrape title from a webpage"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string.strip() if soup.title else "No title"
        return url, title, "SUCCESS"
    except Exception as e:
        return url, None, f"ERROR: {str(e)}"

urls = [
    "https://httpbin.org/html",
    "https://httpbin.org/json", 
    "https://example.com",
    "https://invalid-url-test.com"
]

print("Scraping multiple pages...")
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(scrape_page, url) for url in urls]
    
    for future in as_completed(futures):
        url, title, status = future.result()
        if status == "SUCCESS":
            print(f"✓ {url} -> {title}")
        else:
            print(f"✗ {url} -> {status}")
```

### Example 2: File Processing Pipeline

```python
import os
from pathlib import Path

def process_single_file(file_path, output_dir):
    """Process a single file (simulated)"""
    try:
        # Simulate reading and processing
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Simulate some processing
        processed_content = content.upper()
        
        # Write to output
        output_path = Path(output_dir) / f"processed_{file_path.name}"
        with open(output_path, 'w') as f:
            f.write(processed_content)
        
        return file_path, "SUCCESS", len(processed_content)
    except Exception as e:
        return file_path, f"ERROR: {str(e)}", 0

# Simulate multiple files
file_paths = [Path(f"file_{i}.txt") for i in range(10)]
output_dir = "processed_files"

# Create sample files
os.makedirs(output_dir, exist_ok=True)
for file_path in file_paths:
    with open(file_path, 'w') as f:
        f.write(f"Content of {file_path.name}")

# Process files in parallel
print("Processing files...")
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(process_single_file, fp, output_dir) 
        for fp in file_paths
    ]
    
    total_size = 0
    for future in as_completed(futures):
        file_path, status, size = future.result()
        if status == "SUCCESS":
            print(f"✓ Processed {file_path} ({size} bytes)")
            total_size += size
        else:
            print(f"✗ Failed {file_path}: {status}")

print(f"Total processed: {total_size} bytes")
```

### Example 3: Database Operations

```python
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    """Context manager for database connection"""
    conn = sqlite3.connect(':memory:')  # In-memory database for demo
    try:
        yield conn
    finally:
        conn.close()

def setup_database():
    """Setup sample database"""
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        ''')
        
        # Insert sample data
        users = [(f"User_{i}", f"user_{i}@example.com") for i in range(100)]
        conn.executemany(
            'INSERT INTO users (name, email) VALUES (?, ?)', 
            users
        )
        conn.commit()

def query_user(user_id):
    """Query a single user (simulate slow query)"""
    time.sleep(0.1)  # Simulate network/database latency
    with get_db_connection() as conn:
        cursor = conn.execute(
            'SELECT * FROM users WHERE id = ?', 
            (user_id,)
        )
        result = cursor.fetchone()
        return user_id, result

# Setup and run queries
setup_database()
user_ids = list(range(1, 21))  # Query first 20 users

print("Querying users in parallel...")
with ThreadPoolExecutor(max_workers=5) as executor:
    start_time = time.time()
    
    futures = [executor.submit(query_user, uid) for uid in user_ids]
    
    for future in as_completed(futures):
        user_id, user_data = future.result()
        if user_data:
            print(f"User {user_id}: {user_data[1]} ({user_data[2]})")
    
    end_time = time.time()
    print(f"Completed {len(user_ids)} queries in {end_time - start_time:.2f} seconds")
```

## Key Takeaways for Beginners

1. **Always use context manager** (`with ThreadPoolExecutor...`) for automatic cleanup
2. **Choose appropriate max_workers** - too many can be worse than too few
3. **Use `submit()` for individual tasks**, `map()` for collections
4. **Use `as_completed()`** when you need results as they become available
5. **Always handle exceptions** in your worker functions
6. **Use timeouts** to prevent hanging indefinitely
7. **Monitor resource usage** - threads consume memory

## Common Pitfalls to Avoid

1. **Not handling exceptions** in worker functions
2. **Creating too many threads** (memory overhead)
3. **Forgetting to call `.result()`** on futures
4. **Not using timeouts** on blocking operations
5. **Mixing I/O-bound and CPU-bound tasks** (use ProcessPoolExecutor for CPU-bound)

This guide covers the most practical and commonly used aspects of ThreadPoolExecutor. Start with simple examples and gradually move to more complex patterns as you become comfortable with the concepts!
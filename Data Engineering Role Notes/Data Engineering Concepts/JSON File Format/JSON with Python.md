
Of course! Here is your comprehensive guide to working with JSON in Python, covering the built-in `json` module and the powerful `pandas.json_normalize` function.

### What is JSON? 🧐

JSON (JavaScript Object Notation) is a lightweight, text-based format for data interchange. It's easy for humans to read and write and easy for machines to parse and generate. It's the de facto standard for sending data between web servers and clients, especially in APIs.

A JSON object consists of key-value pairs, similar to a Python dictionary.

- **Keys** must be strings in double quotes.
    
- **Values** can be a string, number, boolean (`true`/`false`), array (like a Python list), or another JSON object (like a Python dictionary).
    

---

## The `json` Module: Your Go-To for Basic JSON 🐍

Python's built-in `json` module provides the essential tools to work with JSON data. The four main functions you'll use can be split into two groups:

1. Working with **JSON strings**: `dumps` and `loads` (notice the 's' for 'string').
    
2. Working with **JSON files**: `dump` and `load` (no 's').
    

### `json.dumps()`: Python Object ➡️ JSON String

The `json.dumps()` function **serializes** a Python object (like a dictionary or list) into a JSON-formatted string.

- `dump` + `s` = Dump to **s**tring.
    

Python

```
import json

# A Python dictionary
python_data = {
    "name": "John Doe",
    "age": 30,
    "isStudent": False,
    "courses": [
        {"title": "History", "credits": 3},
        {"title": "Math", "credits": 4}
    ]
}

# Convert the Python dictionary to a JSON formatted string
json_string = json.dumps(python_data, indent=4) # indent makes it human-readable

print("--- Type of output ---")
print(type(json_string))

print("\n--- JSON String Output ---")
print(json_string)
```

**Output:**

```
--- Type of output ---
<class 'str'>

--- JSON String Output ---
{
    "name": "John Doe",
    "age": 30,
    "isStudent": false,
    "courses": [
        {
            "title": "History",
            "credits": 3
        },
        {
            "title": "Math",
            "credits": 4
        }
    ]
}
```

**Note:** `json.dumps()` converted the Python `False` to the JSON `false`.

---

### `json.loads()`: JSON String ➡️ Python Object

The `json.loads()` function does the reverse. It **deserializes** a JSON-formatted string into a Python object.

- `load` + `s` = Load from **s**tring.
    

This is extremely useful when you get data from an API call.

Python

```
import json
import requests # To make an API request

# Example using the requests module to get data from a public API
try:
    response = requests.get("https://api.agify.io/?name=michael")
    response.raise_for_status() # Raises an error for bad status codes (4xx or 5xx)
    
    # response.text is a JSON formatted string
    json_api_string = response.text
    print("--- API Response (as a string) ---")
    print(json_api_string)
    print(type(json_api_string))

    # Now, parse this string into a Python dictionary
    python_dict_from_api = json.loads(json_api_string)
    
    print("\n--- Parsed Python Dictionary ---")
    print(python_dict_from_api)
    print(type(python_dict_from_api))

    # Now you can access data like a normal dictionary
    print(f"\nMichael's predicted age is: {python_dict_from_api['age']}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")

```

**Output:**

```
--- API Response (as a string) ---
{"name":"michael","age":68,"count":299131}
<class 'str'>

--- Parsed Python Dictionary ---
{'name': 'michael', 'age': 68, 'count': 299131}
<class 'dict'>

Michael's predicted age is: 68
```

---

### `json.dump()`: Python Object ➡️ JSON File 📄

The `json.dump()` function writes a Python object directly to a file-like object (like a file opened in write mode).

- `dump` (no 's') = Dump to **file**.
    

Python

```
import json

# The same Python dictionary from before
python_data = {
    "name": "John Doe",
    "age": 30,
    "isStudent": False,
    "courses": [
        {"title": "History", "credits": 3},
        {"title": "Math", "credits": 4}
    ]
}

# Open a file in write mode ('w') and dump the data into it
with open('data.json', 'w') as f:
    json.dump(python_data, f, indent=4)

print("Data successfully written to data.json")
```

After running this, you'll have a new file named `data.json` in your directory with the formatted JSON content.

---

### `json.load()`: JSON File ➡️ Python Object

The `json.load()` function reads from a file-like object containing JSON and parses it into a Python object.

- `load` (no 's') = Load from **file**.
    

Python

```
import json

# Open the JSON file we just created in read mode ('r')
with open('data.json', 'r') as f:
    # Load the data from the file into a Python object
    loaded_data = json.load(f)

print("--- Type of loaded data ---")
print(type(loaded_data))

print("\n--- Content of loaded data ---")
print(loaded_data)

# Accessing data is now easy
print(f"\nThe student's name is {loaded_data['name']}.")
```

**Output:**

```
--- Type of loaded data ---
<class 'dict'>

--- Content of loaded data ---
{'name': 'John Doe', 'age': 30, 'isStudent': False, 'courses': [{'title': 'History', 'credits': 3}, {'title': 'Math', 'credits': 4}]}

The student's name is John Doe.
```

---

## `pandas.json_normalize()`: Handling Complex, Nested JSON 📊

Real-world JSON, especially from APIs, is often nested. This means some values are themselves objects or lists of objects. While you can parse this with the `json` module, it's cumbersome to turn into a flat table for analysis. This is where **Pandas** shines.

The `pandas.json_normalize()` function is a powerful tool to **flatten** semi-structured JSON data into a flat table (a DataFrame).

### The Problem: Nested JSON

Imagine you have data like this, where each user has a nested dictionary for their address:

Python

```
nested_data = [
    {'id': 1, 'name': 'Alice', 'address': {'street': '123 Main St', 'city': 'Anytown'}},
    {'id': 2, 'name': 'Bob', 'address': {'street': '456 Oak Ave', 'city': 'Someplace'}},
    {'id': 3, 'name': 'Charlie', 'address': {'street': '789 Pine Ln', 'city': 'Elsewhere'}}
]
```

Trying to put this directly into a DataFrame isn't ideal:

Python

```
import pandas as pd
df_bad = pd.DataFrame(nested_data)
print(df_bad)
```

**Output (not ideal):**

```
   id     name                                    address
0   1    Alice  {'street': '123 Main St', 'city': 'Anytown'}
1   2      Bob  {'street': '456 Oak Ave', 'city': 'Somepl...
2   3  Charlie  {'street': '789 Pine Ln', 'city': 'Elsewh...
```

The `address` column contains dictionaries, which is hard to work with.

### The Solution: `json_normalize()`

`json_normalize()` automatically expands nested dictionaries into their own columns.

Python

```
import pandas as pd

nested_data = [
    {'id': 1, 'name': 'Alice', 'address': {'street': '123 Main St', 'city': 'Anytown'}},
    {'id': 2, 'name': 'Bob', 'address': {'street': '456 Oak Ave', 'city': 'Someplace'}},
    {'id': 3, 'name': 'Charlie', 'address': {'street': '789 Pine Ln', 'city': 'Elsewhere'}}
]

# Use json_normalize to flatten the data
df_good = pd.json_normalize(nested_data)

print(df_good)
```

**Output (perfectly flat!):**

```
   id     name    address.street address.city
0   1    Alice       123 Main St      Anytown
1   2      Bob       456 Oak Ave    Someplace
2   3  Charlie       789 Pine Ln    Elsewhere
```

Notice how `address.street` and `address.city` are now proper columns.

### Advanced `json_normalize` with `record_path` and `meta`

Sometimes, the data you want to tabulate is buried inside a key, and you want to include some top-level metadata with each record.

- `record_path`: The path to the list of records you want to flatten.
    
- `meta`: Top-level keys whose values you want to repeat for each record.
    

Python

```
import pandas as pd

api_like_response = {
    "source": "Official Gov API",
    "last_updated": "2025-10-12",
    "data": {
        "schools": [
            {"id": 101, "name": "Lincoln High", "principal": {"name": "Ms. Davis", "since": 2018}},
            {"id": 102, "name": "Washington Middle", "principal": {"name": "Mr. Smith", "since": 2021}}
        ]
    }
}

# Flatten this complex structure
df_advanced = pd.json_normalize(
    api_like_response,
    record_path=['data', 'schools'], # Path to the list of schools
    meta=['source', 'last_updated'] # Metadata to include
)

print(df_advanced)
```

**Output:**

```
    id               name     source last_updated principal.name  principal.since
0  101       Lincoln High  Official Gov API   2025-10-12      Ms. Davis             2018
1  102  Washington Middle  Official Gov API   2025-10-12      Mr. Smith             2021
```

Here, `json_normalize` dove into `data` -> `schools`, flattened each school record (including the nested `principal` info), and added the `source` and `last_updated` metadata to every single row. This is incredibly efficient for cleaning API data for analysis.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/JSON File Format/Types of JSON|Types of JSON]]

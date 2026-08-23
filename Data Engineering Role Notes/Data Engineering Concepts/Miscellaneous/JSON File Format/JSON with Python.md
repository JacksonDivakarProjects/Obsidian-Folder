## What Is JSON?

JSON (JavaScript Object Notation) is a lightweight, text-based format for data interchange. It's easy for humans to read and write, and easy for machines to parse and generate. It's the de facto standard for sending data between web servers and clients, especially in APIs.

A JSON object is a collection of key-value pairs, similar to a Python dictionary:

- **Keys** must be strings in double quotes.
- **Values** can be a string, number, boolean (`true`/`false`), `null`, an array (like a Python list), or another JSON object (like a Python dictionary).

---

## The `json` Module 🐍

Python's built-in `json` module provides the essential tools for working with JSON data. Its four main functions split into two pairs:

1. Working with **JSON strings**: `dumps` and `loads` (notice the trailing `s`, for "string").
2. Working with **JSON files**: `dump` and `load` (no `s`).

| Function | Direction | Mnemonic |
|---|---|---|
| `json.dumps()` | Python object → JSON string | dump + **s**tring |
| `json.loads()` | JSON string → Python object | load + **s**tring |
| `json.dump()` | Python object → JSON file | dump to file |
| `json.load()` | JSON file → Python object | load from file |

### `json.dumps()`: Python Object → JSON String

`json.dumps()` **serializes** a Python object (dict, list, etc.) into a JSON-formatted string.

```python
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
json_string = json.dumps(python_data, indent=4)  # indent makes it human-readable

print("--- Type of output ---")
print(type(json_string))

print("\n--- JSON String Output ---")
print(json_string)
```

**Output:**

```text
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

Note that `json.dumps()` converted the Python `False` to the JSON `false` (JSON's booleans and `null` are lowercase, unlike Python's `False`/`True`/`None`).

### `json.loads()`: JSON String → Python Object

`json.loads()` does the reverse: it **deserializes** a JSON-formatted string into a Python object. This is extremely useful when you get data back from an API call.

```python
import json
import requests  # to make an API request

try:
    response = requests.get("https://api.agify.io/?name=michael")
    response.raise_for_status()  # raises an error for bad status codes (4xx or 5xx)

    # response.text is a JSON-formatted string
    json_api_string = response.text
    print("--- API Response (as a string) ---")
    print(json_api_string)
    print(type(json_api_string))

    # Parse this string into a Python dictionary
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

```text
--- API Response (as a string) ---
{"name":"michael","age":68,"count":299131}
<class 'str'>

--- Parsed Python Dictionary ---
{'name': 'michael', 'age': 68, 'count': 299131}
<class 'dict'>

Michael's predicted age is: 68
```

### `json.dump()`: Python Object → JSON File 📄

`json.dump()` writes a Python object directly to a file-like object (a file opened in write mode) — there's no intermediate string.

```python
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

After running this, `data.json` exists in the working directory with the formatted JSON content.

### `json.load()`: JSON File → Python Object

`json.load()` reads from a file-like object containing JSON and parses it into a Python object.

```python
import json

# Open the JSON file created above in read mode ('r')
with open('data.json', 'r') as f:
    loaded_data = json.load(f)

print("--- Type of loaded data ---")
print(type(loaded_data))

print("\n--- Content of loaded data ---")
print(loaded_data)

# Accessing data is now easy
print(f"\nThe student's name is {loaded_data['name']}.")
```

**Output:**

```text
--- Type of loaded data ---
<class 'dict'>

--- Content of loaded data ---
{'name': 'John Doe', 'age': 30, 'isStudent': False, 'courses': [{'title': 'History', 'credits': 3}, {'title': 'Math', 'credits': 4}]}

The student's name is John Doe.
```

---

## Flattening Nested JSON with `pandas.json_normalize()` 📊

Real-world JSON — especially from APIs — is often nested: some values are themselves objects or lists of objects. Parsing this with the `json` module is fine, but turning it into a flat table for analysis is cumbersome by hand. This is where **pandas** helps.

`pandas.json_normalize()` **flattens** semi-structured JSON into a flat table (a DataFrame).

### The Problem: Nested JSON

Imagine data like this, where each user has a nested dictionary for their address:

```python
nested_data = [
    {'id': 1, 'name': 'Alice', 'address': {'street': '123 Main St', 'city': 'Anytown'}},
    {'id': 2, 'name': 'Bob', 'address': {'street': '456 Oak Ave', 'city': 'Someplace'}},
    {'id': 3, 'name': 'Charlie', 'address': {'street': '789 Pine Ln', 'city': 'Elsewhere'}}
]
```

Putting this directly into a DataFrame isn't ideal:

```python
import pandas as pd
df_bad = pd.DataFrame(nested_data)
print(df_bad)
```

**Output (not ideal — `address` is still a dict per cell):**

```text
   id     name                                    address
0   1    Alice  {'street': '123 Main St', 'city': 'Anytown'}
1   2      Bob  {'street': '456 Oak Ave', 'city': 'Somepl...
2   3  Charlie  {'street': '789 Pine Ln', 'city': 'Elsewh...
```

### The Fix: `json_normalize()`

`json_normalize()` automatically expands nested dictionaries into their own columns, named `parent.child`:

```python
import pandas as pd

nested_data = [
    {'id': 1, 'name': 'Alice', 'address': {'street': '123 Main St', 'city': 'Anytown'}},
    {'id': 2, 'name': 'Bob', 'address': {'street': '456 Oak Ave', 'city': 'Someplace'}},
    {'id': 3, 'name': 'Charlie', 'address': {'street': '789 Pine Ln', 'city': 'Elsewhere'}}
]

df_good = pd.json_normalize(nested_data)
print(df_good)
```

**Output (flat):**

```text
   id     name    address.street address.city
0   1    Alice       123 Main St      Anytown
1   2      Bob       456 Oak Ave    Someplace
2   3  Charlie       789 Pine Ln    Elsewhere
```

`address.street` and `address.city` are now proper columns.

### Advanced Usage: `record_path` and `meta`

Sometimes the records you want to tabulate are buried inside a key, and you want to repeat some top-level metadata alongside each record.

- `record_path`: the path (list of keys) to the list of records you want to flatten.
- `meta`: top-level keys whose values should be repeated for every resulting row.

```python
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
    record_path=['data', 'schools'],  # path to the list of schools
    meta=['source', 'last_updated']   # metadata to include on every row
)

print(df_advanced)
```

**Output:**

```text
    id               name             source last_updated principal.name  principal.since
0  101       Lincoln High  Official Gov API   2025-10-12      Ms. Davis             2018
1  102  Washington Middle  Official Gov API   2025-10-12      Mr. Smith             2021
```

`json_normalize` dove into `data` → `schools`, flattened each school record (including the nested `principal` info), and stamped `source` and `last_updated` onto every row. This pattern is a common first step when cleaning API responses for analysis.

## 🔗 Related Notes
- [[Types of JSON|Types of JSON]]

In YAML (and specifically in dbt), that little dash (`-`) is the difference between a **list** and a **key-value pair**.

Think of it as the difference between a single labeled box and a bulleted list inside that box.

---

### 1. No Dash: The Key-Value Pair (Mappings)

When a line doesn't have a dash, it defines a **property** or a **category**. It’s like a variable name followed by its value. In dbt, these are used for configuration names.

YAML

```
version: 2
name: my_project
```

- `version` is the key; `2` is the value.
    
- This is a "dictionary" or "map."
    

### 2. The Dash: The List (Sequences)

The dash represents an **item in a list**. If you have multiple things that belong under one category (like multiple models, multiple columns, or multiple tests), you use a dash to separate them.

YAML

```
models:
  - name: orders
    description: "Table of sales"
  - name: customers
    description: "Customer lookup"
```

- `models:` is the category.
    
- The `-` tells dbt: "Here is the first model object," and "Here is the second model object."
    

---

### How they work together

In dbt `schema.yml` files, you’ll often see these nested together. The structure usually follows this logic:

1. **Top-level key** (No dash)
    
2. **List of objects** (Starts with a dash)
    
3. **Properties of that object** (No dash, indented under the dash)
    

|**Feature**|**No Dash (key: value)**|**With Dash (- item)**|
|---|---|---|
|**YAML Term**|Mapping / Dictionary|Sequence / List|
|**Analogy**|A label on a drawer|One of many items inside the drawer|
|**dbt Example**|`name: orders`|`- name: orders`|
|**Quantity**|Usually unique per section|Used when there are 1 or more items|

### Common Pitfall

The most common error in dbt is forgetting the dash when defining columns.

- **Wrong:** Listing `columns:` and then just writing the names on their own lines — dbt won't know where one column ends and the next begins.
- **Right:** Each new column starts with a `- name: column_name`.

## 🔗 Related Notes
- [[YAML File and Its Structure|YAML File and Its Structure]]
- [[Types of YAML File|Types of YAML File]]
- [[Documentation in YAML|Documentation in YAML]]

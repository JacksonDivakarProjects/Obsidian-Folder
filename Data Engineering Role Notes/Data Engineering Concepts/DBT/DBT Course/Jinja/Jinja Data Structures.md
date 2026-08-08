**Jinja data structures and control constructs**

### Core data types

- **Dictionary (map)**

```jinja
{% set user = {"name": "Jack", "age": 22} %}
{{ user.name }}
{{ user["age"] }}
```

- **List**

```jinja
{% set nums = [1, 2, 3] %}
{{ nums[0] }}
```

- **Tuple**
    Exists. Immutable sequence.

```jinja
{% set coords = (10, 20) %}
{{ coords[0] }}
```

- **Boolean / None**

```jinja
{% set flag = true %}
{% set nothing = none %}
```

**No native set literal:** unlike Python, Jinja has no `{1, 2, 3}` set syntax — writing that is a syntax error, since Jinja's `{}` literal is reserved for dictionaries (`key: value` pairs). For unique values, dedupe a list with the `unique` filter instead:

```jinja
{% set uniq = [1, 2, 2, 3] | unique | list %}
```

### Loops

- **Loop over list**
    

```jinja
{% for n in nums %}
  {{ n }}
{% endfor %}
```

- **Loop over dictionary**
    

```jinja
{% for key, value in user.items() %}
  {{ key }}: {{ value }}
{% endfor %}
```

- **Loop helpers**
    

```jinja
loop.index      # 1-based
loop.index0     # 0-based
loop.first
loop.last
```

---

### Functions / filters commonly used with dictionaries

```jinja
user.keys()
user.values()
user.items()
|length
|default("N/A")
|join(", ")
```

---

### Conditionals

```jinja
{% if user.age > 18 %}
  Adult
{% elif user.age == 18 %}
  Exactly 18
{% else %}
  Minor
{% endif %}
```

---

### Mutability rule (critical)

- **Lists and dictionaries**: mutable.
    
- **Tuples**: immutable.
    

```jinja
{% set t = (1, 2) %}
{# t[0] = 5 → invalid #}
```

---

### dbt-specific note

In dbt (Jinja + SQL), tuples are valid but **lists are preferred** for iteration and macros.

```jinja
{% set cols = ["id", "name"] %}
select {{ cols | join(", ") }} from table
```

---

### Summary

- Jinja natively supports **tuple**, **list**, **dict**, **boolean**, and **none** literals — but not a set literal.
- Tuples exist but are rarely needed in practice.
- Lists and dicts dominate real-world Jinja/dbt usage; use the `unique` filter when you need set-like deduplication.
- Control flow mirrors Python, with reduced mutability (tuples are immutable) and no custom class definitions.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/Jinja/Jinja Templating Fundamentals|Jinja Templating Fundamentals]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/Jinja/Jinja SQL|Jinja in SQL]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/Jinja/Length in Jinja|Length in Jinja]]

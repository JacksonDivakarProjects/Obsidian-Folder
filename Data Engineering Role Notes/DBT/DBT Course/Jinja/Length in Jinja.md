**`length` in Jinja**

`length` returns the number of elements in a sequence or keys in a dictionary.

### Syntax

```jinja
{{ variable | length }}
```

### Works on

- **List**
    

```jinja
{% set items = [1, 2, 3] %}
{{ items | length }}   {# 3 #}
```

- **Tuple**
    

```jinja
{% set t = (10, 20) %}
{{ t | length }}       {# 2 #}
```

- **Dictionary**
    

```jinja
{% set d = {"a": 1, "b": 2} %}
{{ d | length }}       {# 2 #}
```

- **String**
    

```jinja
{% set s = "data" %}
{{ s | length }}       {# 4 #}
```

### In conditionals

```jinja
{% if items | length > 0 %}
  not empty
{% endif %}
```

### In loops

```jinja
{% for i in items %}
  {{ loop.index }} / {{ items | length }}
{% endfor %}
```

### Notes

- Equivalent to Python’s `len()`.
    
- Safe for lists, tuples, dicts, strings.
    
- `none | length` is invalid unless guarded with `default`.
    

```jinja
{{ maybe_list | default([]) | length }}
```

## 🔗 Related Notes
- [[Jinja Data Structures|Jinja Data Structures]]
- [[Jinja SQL|Jinja in SQL]]
- [[Jinja Templating Fundamentals|Jinja Templating Fundamentals]]

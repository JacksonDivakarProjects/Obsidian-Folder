**Two documentation types in dbt**

---

## 1. Single-line documentation (inline)

**What it is**  
A short text description written directly in YAML.

**Where it lives**

- `models.yml`
    
- `sources.yml`
    

**Example**

```yaml
models:
  - name: orders
    description: "Contains cleaned customer order data"
```

**Properties**

- One sentence
    
- No formatting
    
- Not reusable
    
- Fast to read
    

**Purpose**  
Labeling and basic meaning.

---

## 2. Markdown documentation (doc blocks)

**What it is**  
Multi-line, formatted documentation written once and referenced.

**Where it lives**

- `docs/*.md` (or any file parsed by dbt)
    

**Doc block**

```jinja
{% docs orders_model %}
This model contains **cleaned order data**.

### Grain
One row per order

### Business rules
- Cancelled orders excluded
{% enddocs %}
```

**Referenced in YAML**

```yaml
models:
  - name: orders
    description: "{{ doc('orders_model') }}"
```

**Properties**

- Multi-line
    
- Markdown formatting
    
- Reusable
    
- Rich context
    

**Purpose**  
Explain logic, grain, assumptions.

---

## Comparison

|Aspect|Single-line|Doc block|
|---|---|---|
|Length|Short|Long|
|Formatting|No|Yes (Markdown)|
|Reusable|No|Yes|
|Use case|Simple meaning|Business logic|

---

## One-line summary

dbt documentation has **inline single-line descriptions for quick meaning** and **Markdown doc blocks for structured, reusable explanations** rendered in dbt Docs.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/YAML File/DBT Course/Types of YAML File|Types of YAML File]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/YAML File/DBT Course/YAML File and Its Structure|YAML File and Its Structure]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/YAML File/Dash in YAML|Dash in YAML]]

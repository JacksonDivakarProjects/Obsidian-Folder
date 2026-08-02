**YAML — clear, functional explanation**

### What YAML is

**YAML (YAML Ain’t Markup Language)** is a human-readable data format used to **define configuration, structure tests, and document metadata**.  
It stores **data only**. No logic, no execution.

---

## 1. YAML for **configuration**

Primary use.

YAML defines **settings, parameters, and behavior switches** for tools and systems.

Example:

```yaml
database:
  host: localhost
  port: 5432
  name: analytics
```

Why YAML is used for configuration:

- Readable by humans
    
- Easy to edit
    
- Easy for programs to parse
    
- Supports nesting (hierarchy)
    

Common configuration use cases:

- Application settings
    
- Environment variables
    
- Pipeline definitions
    
- Tool configuration (dbt, Docker, GitHub Actions)
    

---

## 2. YAML for **testing**

YAML defines **test rules**, not test logic.

Example (dbt-style):

```yaml
columns:
  - name: user_id
    tests:
      - not_null
      - unique
```

What YAML does here:

- Declares **what should be tested**
    
- Lists **constraints and expectations**
    

What YAML does NOT do:

- Does not run tests
    
- Does not define algorithms
    
- Does not contain assertions code
    

Execution is handled by the tool reading the YAML.

---

## 3. YAML for **documentation**

YAML acts as **structured documentation** that tools and humans can read.

Example:

```yaml
models:
  - name: orders
    description: "Contains customer order data"
```

Why this counts as documentation:

- Describes purpose and meaning
    
- Tied directly to real objects (models, columns)
    
- Keeps documentation close to implementation
    
- Can be auto-generated into docs
    

This avoids outdated external documentation.

---

## 4. Core YAML building blocks

### Key–value pairs

```yaml
name: Jack
```

### Lists

```yaml
skills:
  - SQL
  - Python
```

### Dictionaries (maps)

```yaml
user:
  id: 1
  role: admin
```

### Nesting (indentation is syntax)

```yaml
app:
  logging:
    level: debug
```

Indentation replaces `{}` and `;`.

---

## 5. What YAML is **not**

- Not a programming language
    
- Not executable
    
- No loops, conditions, or functions
    
- No calculations
    

YAML = **structure + intent**, nothing more.

---

## 6. Mental model (important)

Think of YAML as:

- A **contract** between humans and systems
    
- A **declaration of truth**
    
- A **schema-free data description**
    

Code decides **how**.  
YAML declares **what**.

---

## One-line summary

YAML is a human-readable format used to **configure systems, declare tests, and document data structures**, without containing logic or execution.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/YAML File/DBT Course/Types of YAML File|Types of YAML File]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/YAML File/Dash in YAML|Dash in YAML]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/Documentation/Documentation in YAML|Documentation in YAML]]

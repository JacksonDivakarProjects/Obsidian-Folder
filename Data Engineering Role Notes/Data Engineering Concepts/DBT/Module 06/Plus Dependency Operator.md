### **What `+` means in dbt selection — crystal clear**

In dbt, `+` is a **dependency operator**.  
It tells dbt **how far to walk the DAG** when selecting models.

Think of it as **scope expansion**.

---

## The three valid patterns

### 1️⃣ `model+` → model **and all downstream**

```bash
dbt build --select orders+
```

Runs:

- `orders`
    
- Anything that **depends on** `orders`
    

📌 Use this when you change a base model and want to rebuild everything affected.

---

### 2️⃣ `+model` → model **and all upstream**

```bash
dbt build --select +orders
```

Runs:

- All models that `orders` depends on
    
- Then `orders`
    

📌 Use this when upstream data may be stale or missing.

---

### 3️⃣ `+model+` → **full chain**

```bash
dbt build --select +orders+
```

Runs:

- All parents
    
- The model itself
    
- All children
    

📌 Use this when you want a **clean, end-to-end rebuild** of that slice.

---

## Simple DAG example

```
raw_orders
   ↓
stg_orders
   ↓
int_orders
   ↓
fact_orders
```

|Command|What runs|
|---|---|
|`fact_orders`|only fact_orders|
|`+fact_orders`|raw → stg → int → fact|
|`fact_orders+`|fact + downstream|
|`+fact_orders+`|entire chain|

---

## What `+` does NOT do

- ❌ It does not mean “incremental”
    
- ❌ It does not change materialization
    
- ❌ It does not force full refresh
    

It only controls **selection**.

---

## Combine with other selectors (power move)

```bash
dbt build --select +fact_orders+ --exclude tag:heavy
```

---

## Professional phrasing (use this)

> “The `+` operator expands model selection upstream or downstream in the dbt DAG.”

Short. Correct. Confident.

---

## Final takeaway

- `+` = **dependency scope**
    
- Left side → **parents**
    
- Right side → **children**
    
- Both sides → **end-to-end**
    

If you want, I can next explain:

- `@` selector
    
- `state:modified+`
    
- How selection impacts runtime in Databricks
    

Just say where to go next.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 05/dbt Node Selection Syntax|dbt Node Selection Syntax]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 06/DBT Flags|dbt Flags That Actually Matter]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 06/Difference Between dbt run and dbt build|`dbt run` vs `dbt build`]]

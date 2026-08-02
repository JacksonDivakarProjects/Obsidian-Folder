Understood, Jack 👍  
Below is an **exclusive, clean, and crystal-clear guide ONLY for dbt flags** you mentioned.  
I’ll explain **one flag at a time**, using **simple words**, **why it exists**, and **when to use it**.  
No extra dbt theory. No distractions.

---

# 📘 **dbt Flags That Actually Matter (Clear & Exclusive Guide)**

These flags control **WHAT dbt runs**, **WHAT it skips**, and **HOW safely it runs**.

Think of them as **control switches**.

---

## 1️⃣ `--full-refresh` → **Delete and rebuild**

### What it does (simple)

- Deletes existing **incremental tables**
    
- Recreates them from scratch
    
- Old data is **lost and rebuilt**
    

```bash
dbt build --full-refresh
```

### What it affects

✅ Incremental models  
✅ Seeds

### What it does NOT affect

❌ Views (they always rebuild anyway)  
❌ Snapshots (history is preserved)

### When you MUST use it

- You changed incremental logic
    
- Column type changed
    
- Data became corrupted
    

### When you should NOT use it

- Daily runs
    
- Normal production runs
    
- Large tables without reason
    

⚠️ **Key warning**

> `--full-refresh` is destructive. Always combine with `--select`.

Example (safe):

```bash
dbt build --select sales --full-refresh
```

---

## 2️⃣ `--exclude` → **Run everything EXCEPT this**

### What it does

- Skips models, folders, or tags
    
- Everything else runs normally
    

```bash
dbt build --exclude int_legacy*
```

```bash
dbt build --exclude tag:heavy
```

### When to use

- Model is slow
    
- Model is broken
    
- Model is deprecated
    
- Reduce production risk
    

📌 **Mental model**

> “Do everything, but don’t touch this.”

---

## 3️⃣ `--select` → **Run ONLY what I choose**

### Run a single model

```bash
dbt build --select fact_orders
```

### Run model + downstream models

```bash
dbt build --select fact_orders+
```

### Run upstream + model

```bash
dbt build --select +fact_orders
```

### Why this flag is critical

- Faster runs
    
- Safer development
    
- Less compute usage
    

📌 **Golden rule**

> Always use `--select` in development.

---

## 4️⃣ `state:modified` → **Run only changed code (CI use)**

```bash
dbt build --select state:modified+
```

### What it does

- Runs only models whose code changed
    
- Also runs dependent models
    
- Needs previous `manifest.json`
    

### Why teams love it

- Very fast CI
    
- No unnecessary rebuilds
    
- Scales well for big projects
    

📌 Think:

> “Run only what I touched.”

---

## 5️⃣ `--fail-fast` → **Stop immediately on error**

```bash
dbt build --fail-fast
```

### What it does

- Stops execution at first failure
    
- Prevents wasted compute
    
- Faster feedback
    

### When to use

- CI pipelines
    
- Debugging failures
    
- Cost-sensitive environments
    

---

## 6️⃣ `--defer` → **Use prod data in dev**

```bash
dbt build --defer --state prod_manifest/
```

### What it does

- Uses **production tables** for unchanged models
    
- Builds only modified models
    
- Does NOT overwrite prod data
    

### Why this matters

- Faster development
    
- No full rebuilds
    
- Enterprise-level workflow
    

📌 Think:

> “Borrow prod data, don’t recreate it.”

---

## 7️⃣ `--vars` → **Pass values at runtime**

```bash
dbt build --vars '{run_date: "2025-01-01"}'
```

### What it does

- Sends dynamic values to models
    
- Used inside SQL via `var()`
    

### Use cases

- Backfills
    
- Date-based logic
    
- Conditional behavior
    

---

## 8️⃣ `--threads` → **Parallel execution**

```bash
dbt build --threads 8
```

### What it does

- Controls how many models run at once
    
- More threads = faster, but costlier
    

⚠️ In Databricks:

> More threads = more compute cost

---

## 9️⃣ `--target` → **Switch environment**

```bash
dbt build --target prod
```

### What it does

- Uses credentials & schema from `profiles.yml`
    
- No code change needed
    

### Typical targets

- `dev`
    
- `qa`
    
- `prod`
    

---

## 🧠 What to MEMORIZE (very important)

|Flag|Meaning|
|---|---|
|`--full-refresh`|Delete & rebuild incremental models|
|`--select`|Run only selected models|
|`--exclude`|Skip selected models|
|`state:modified`|Run only changed code|
|`--fail-fast`|Stop on first error|
|`--defer`|Use prod data in dev|

---

## 💼 Professional one-liner (use this confidently)

> “We control dbt execution using `--select` and `--exclude`, apply `--full-refresh` only when incremental logic changes, and rely on state-based selection and defer for efficient CI and development.”

---

## ✅ Final clear guidance

- **Production** → `dbt build`
    
- **Development** → `dbt build --select model`
    
- **Fix bad data** → `--full-refresh + --select`
    
- **CI** → `state:modified+`
    
- **Avoid risk** → use `--exclude`
    

---

If you want next, I can:

- Convert this into a **1-page cheat sheet**
    
- Give **real Databricks job examples**
    
- Explain **backfill without full-refresh**
    
- Draw a **mental flow diagram**
    

Just tell me what you want next 👍

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 06/Difference Between dbt run and dbt build|`dbt run` vs `dbt build`]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 06/Plus Dependency Operator|What `+` Means in dbt Selection]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 05/dbt Node Selection Syntax|dbt Node Selection Syntax]]

**`uniq` — clear, practical explanation**

**`uniq`** is a Linux command that **finds and handles duplicate adjacent lines** in text.

👉 Key truth upfront: **`uniq` works only on consecutive (adjacent) lines**.  
If lines are not next to each other, `uniq` will **not** detect duplicates.

---

## What `uniq` actually does

### 1. Remove duplicate lines

```bash
uniq file.txt
```

Removes **repeated adjacent lines**.

---

### 2. Count duplicates

```bash
uniq -c file.txt
```

Shows how many times each line repeats.

---

### 3. Show only duplicates

```bash
uniq -d file.txt
```

---

### 4. Show only unique lines

```bash
uniq -u file.txt
```

---

## The golden rule (very important)

Most of the time, you must use **`sort` before `uniq`**:

```bash
sort file.txt | uniq
```

Why?

- `sort` brings identical lines together
    
- `uniq` then removes or counts them
    

---

## Real-world examples

### Count unique IP addresses

```bash
awk '{print $1}' access.log | sort | uniq -c
```

---

### Find duplicate records

```bash
sort users.txt | uniq -d
```

---

### Count word frequency

```bash
tr ' ' '\n' < file.txt | sort | uniq -c | sort -nr
```

---

## `uniq` vs `awk` (clear difference)

|Task|Better tool|
|---|---|
|Simple dedup|`uniq`|
|Counting adjacent lines|`uniq -c`|
|Complex grouping|`awk`|
|No sorting allowed|`awk`|

---

## Common mistake (don’t do this ❌)

```bash
uniq file.txt   # Wrong if file is not sorted
```

---

## Mental model

- `sort` → **groups**
    
- `uniq` → **collapses**
    
- `awk` → **analyzes**
    

---

### Bottom line

`uniq` is **simple, fast, and sharp**, but **limited**.  
Use it **after sorting**, or pair it with **`awk`** when logic is needed.

If you want, next I can show:

- `uniq` vs `awk` side-by-side
    
- `uniq` interview traps
    
- A one-page Unix pipelines cheat sheet

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/AWK/AWK - Comprehensive Practical Guide|AWK — Comprehensive Practical Guide]]
- [[Data Engineering Role Notes/Linux/AWK/AWK Necessary Guide|AWK — Comprehensive Applied Guide (Real-World Edition)]]
- [[Data Engineering Role Notes/Linux/AWK/Arrays|AWK Arrays — What You Should Learn (Only What Matters)]]

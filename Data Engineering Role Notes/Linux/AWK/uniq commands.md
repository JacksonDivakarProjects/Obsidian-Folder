# `uniq` Command

`uniq` is a Linux command that finds and handles **duplicate adjacent lines** in text.

Key fact up front: **`uniq` only detects duplicates that are directly next to each other**. If matching lines aren't adjacent, `uniq` will not catch them.

## What `uniq` Actually Does

### 1. Remove duplicate lines
```bash
uniq file.txt
```
Removes repeated adjacent lines (keeps the first occurrence).

### 2. Count duplicates
```bash
uniq -c file.txt
```
Prefixes each line with how many times it repeats consecutively.

### 3. Show only duplicated lines
```bash
uniq -d file.txt
```

### 4. Show only lines with no adjacent duplicate
```bash
uniq -u file.txt
```

## The Golden Rule

Because `uniq` only compares neighboring lines, you almost always need to **`sort` first**:

```bash
sort file.txt | uniq
```

Why: `sort` brings identical lines together so `uniq` can actually collapse or count them.

## Real-World Examples

### Count unique IP addresses
```bash
awk '{print $1}' access.log | sort | uniq -c
```

### Find duplicate records
```bash
sort users.txt | uniq -d
```

### Count word frequency
```bash
tr ' ' '\n' < file.txt | sort | uniq -c | sort -nr
```

## `uniq` vs. `awk`

| Task | Better tool |
|---|---|
| Simple dedup | `uniq` |
| Counting adjacent duplicates | `uniq -c` |
| Complex grouping/aggregation | `awk` |
| Dedup without sorting first | `awk '{seen[$0]++} ... '` (`awk` can dedupe without pre-sorting since it tracks lines in an array) |

## Common Mistake

```bash
uniq file.txt   # Wrong if file.txt isn't already sorted — duplicates that
                # aren't adjacent will be missed silently.
```

## Mental Model

- `sort` → **groups** matching lines together
- `uniq` → **collapses** or counts adjacent groups
- `awk` → **analyzes** with arbitrary logic (including dedup without sorting)

## Key Takeaway

`uniq` is simple, fast, and sharp, but limited to adjacent lines. Use it after `sort`, or reach for `awk` when the logic (grouping, non-adjacent dedup) is more than `uniq` can express.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/AWK/AWK - Comprehensive Practical Guide|AWK — Comprehensive Practical Guide]]
- [[Data Engineering Role Notes/Linux/AWK/AWK Necessary Guide|AWK — Comprehensive Applied Guide (Real-World Edition)]]
- [[Data Engineering Role Notes/Linux/AWK/Arrays|AWK Arrays — What You Should Learn (Only What Matters)]]

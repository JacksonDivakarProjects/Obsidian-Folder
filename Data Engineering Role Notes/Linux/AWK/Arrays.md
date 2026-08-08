# AWK Arrays — What You Should Learn (Only What Matters)

Arrays are the part of AWK that actually raises your capability level — everything else is mostly syntax. This is a tight guide to what to learn and what to skip.

## 1. What an AWK Array Really Is

AWK arrays are **associative arrays** (key → value):

- No numeric-index guarantees
- No fixed size
- Keys are usually strings

Mental model: *a hashmap, not a list.*

## 2. Creating & Updating Elements (Must Know)

```bash
awk '{ count[$1]++ }' file.txt
```

- `$1` → key
- `count[$1]` → value
- `++` → increment

This single line covers most array usage in practice.

## 3. Iterating Over Arrays (Essential)

```bash
awk '{
  count[$1]++
}
END {
  for (k in count)
    print k, count[k]
}' file.txt
```

Used for frequency counts, log analysis, CSV summaries. Note: `for (k in count)` iterates in an unspecified order — pipe into `sort` afterward if you need a stable/ranked order.

## 4. Arrays With Conditions (Very Common)

```bash
awk '$3 > 50 { sum[$1] += $3 } END { for (k in sum) print k, sum[k] }' file.txt
```

Use cases: total sales per product, marks per student, hits per IP.

## 5. Counting Unique Values (Critical Skill)

```bash
awk '{ seen[$1] } END { print length(seen) }' file.txt
```

Use cases: unique users, unique errors, unique IDs.

## 6. Tracking Max/Min Per Key

```bash
awk '{
  if ($2 > max[$1]) max[$1] = $2
}
END {
  for (k in max) print k, max[k]
}' file.txt
```

Use cases: highest score per student, max response time per service.

## 7. Storing Multiple Values Per Key

```bash
awk '{
  data[$1] = data[$1] "," $2
}
END {
  for (k in data) print k, data[k]
}' file.txt
```

Use this pattern when grouping values or building a report per key.

## 8. Checking Whether a Key Exists

```bash
awk '{
  if ($1 in seen)
    print "Duplicate:", $1
  else
    seen[$1]
}' file.txt
```

Use cases: duplicate detection, "first occurrence only" logic.

## 9. Deleting Array Elements

```bash
delete count[$1]
```

Rare in practice, but useful for cleanup within a long-running script.

## 10. Arrays + Sorting (Practical Combo)

```bash
awk '{count[$1]++} END {for (k in count) print count[k], k}' file.txt | sort -nr
```

Use cases: top users, top errors, ranked summaries.

## What to Deliberately Skip (For Now)

- Multi-dimensional arrays
- `PROCINFO`
- `asort` / `asorti`
- Passing arrays to functions
- GNU-specific array extensions

These add complexity without much everyday leverage.

## Mastery Checklist

You're done with AWK arrays once you can:
- Count occurrences
- Group by a field
- Detect duplicates
- Compute totals per key
- Find max/min per group
- Sort aggregated results

## Key Takeaway

Arrays are the ceiling of useful AWK. Once you're comfortable here, AWK stops being a limited text tool and becomes a genuine data-processing weapon — a natural next step is a log-analysis project or a CSV aggregation exercise using exactly these patterns.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/AWK/AWK - Comprehensive Practical Guide|AWK — Comprehensive Practical Guide]]
- [[Data Engineering Role Notes/Linux/AWK/AWK Necessary Guide|AWK — Comprehensive Applied Guide (Real-World Edition)]]
- [[Data Engineering Role Notes/Linux/AWK/uniq commands|uniq commands]]

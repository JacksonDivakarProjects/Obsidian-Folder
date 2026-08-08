# AWK — Comprehensive Practical Guide

A clear, end-to-end, practical tour of AWK — how it's actually used in real Linux and data work, without theory overload.

## 1. What AWK Is (Mental Model)

**AWK is a pattern–action language for processing text line by line.**

Think: *"if a line matches a condition → do something with its fields."*

Default behavior:
- Reads **one line at a time**
- Splits the line into **fields**
- Executes the matching action(s)

## 2. Basic Structure

```bash
awk 'pattern { action }' file
```

Example:

```bash
awk '{ print $1 }' file.txt
```

Prints the first column of every line.

## 3. Fields and Variables (Core Knowledge)

| Element | Meaning |
|---|---|
| `$0` | Entire line |
| `$1` | First field |
| `$2` | Second field |
| `NF` | Number of fields |
| `NR` | Line number |
| `FS` | Field separator |
| `OFS` | Output field separator |

## 4. Field Separators

### Default (whitespace)
```bash
awk '{print $1, $3}' file.txt
```

### Custom delimiter (CSV)
```bash
awk -F',' '{print $1, $3}' file.csv
```
or
```bash
awk 'BEGIN{FS=","} {print $1}' file.csv
```

## 5. BEGIN and END Blocks

Used for **initialization and final summary** — they run once, before/after the main line-by-line processing.

```bash
awk '
BEGIN { print "Start processing" }
{ print $1 }
END { print "Done" }
' file.txt
```

## 6. Filtering Lines (Conditions)

### Print lines matching a condition
```bash
awk '$3 > 50 { print $1, $3 }' data.txt
```

### Pattern matching (regex)
```bash
awk '/error/ { print }' log.txt
```

### Exclude a pattern
```bash
awk '!/debug/' log.txt
```

## 7. If–Else Logic

```bash
awk '{
  if ($2 >= 60)
    print $1, "PASS"
  else
    print $1, "FAIL"
}' marks.txt
```

## 8. Arithmetic and Calculations

```bash
awk '{ total += $2 } END { print total }' sales.txt
```

Average:
```bash
awk '{ sum += $2 } END { print sum/NR }' sales.txt
```

## 9. Working With CSV Headers

Skip the header:
```bash
awk -F',' 'NR > 1 { print $1, $3 }' file.csv
```

Keep the header, filter the data:
```bash
awk -F',' 'NR==1 || $3 > 50' file.csv
```

## 10. String Functions

| Function | Example |
|---|---|
| `length()` | `length($1)` |
| `tolower()` | `tolower($1)` |
| `toupper()` | `toupper($1)` |
| `substr()` | `substr($1,1,4)` |
| `index()` | `index($0,"error")` |

```bash
awk '{ print toupper($1) }' file.txt
```

## 11. Built-in Looping

```bash
awk '{
  for (i=1; i<=NF; i++)
    print $i
}' file.txt
```

## 12. Arrays (This Is the Power Feature)

```bash
awk '{ count[$1]++ } END { for (k in count) print k, count[k] }' file.txt
```

Used for frequency counts and log analysis. See [[Data Engineering Role Notes/Linux/AWK/Arrays|AWK Arrays]] for the deep dive.

## 13. Sorting Output

```bash
awk '{print $2, $1}' file.txt | sort -n
```

AWK piped into standard Unix tools is where the real leverage is.

## 14. Formatting Output

```bash
awk '{ printf "%-10s %5d\n", $1, $2 }' file.txt
```

## 15. Editing Files Safely

Test first (read-only):
```bash
awk '{ print }' file.txt
```

Only overwrite via a temp file — never redirect `awk` output back into its own input file directly, since that truncates the input before `awk` finishes reading it:
```bash
awk '{ print }' file.txt > tmp && mv tmp file.txt
```

## 16. AWK vs. Other Tools

| Tool | Best for |
|---|---|
| `grep` | Searching |
| `sed` | Text substitution |
| **`awk`** | Column-based logic |
| `csvkit` | CSV-correctness (quoting, embedded commas) |
| `jq` | JSON |

## 17. Real-World Use Cases

- Log filtering
- CSV cleanup
- Report generation
- Quick data analysis
- Automation scripts
- Interview questions

## 18. Common Mistakes to Avoid

- Forgetting `-F` when the input isn't whitespace-delimited
- Reaching for `sed` when the task actually needs AWK's field/logic support
- Overcomplicating a task that a one-liner `awk` handles
- Redirecting output directly back into the input file (see §15)

## 19. Professional Best Practice

- One-liners for quick, throwaway tasks
- Multi-line scripts (with comments) for anything meant to be reread later
- Combine AWK with `sort`, `uniq`, `cut` rather than reimplementing their logic in AWK

## 20. A 7-Day Learning Roadmap

- **Day 1–2:** fields, filters, `FS`
- **Day 3:** conditions & arithmetic
- **Day 4:** arrays
- **Day 5:** CSV handling
- **Day 6:** log analysis
- **Day 7:** mini-project

## Key Takeaway

Mastering AWK means you can think in columns, automate text/data processing quickly, and skip reaching for heavier tools (Python, pandas) for tasks AWK already handles in one line.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/AWK/AWK Necessary Guide|AWK — Comprehensive Applied Guide (Real-World Edition)]]
- [[Data Engineering Role Notes/Linux/AWK/Arrays|AWK Arrays — What You Should Learn (Only What Matters)]]
- [[Data Engineering Role Notes/Linux/AWK/uniq commands|uniq commands]]
- [[Data Engineering Role Notes/Linux/Concept Oriented Files/AWK|AWK]]
- [[Data Engineering Role Notes/Linux/Linux Summary Guide|Linux Masterclass Concepts]]

# AWK — Comprehensive Applied Guide (Real-World Edition)

Production-grade AWK — the kind that actually gets used day to day. This guide focuses only on:

- Filtering CSV rows
- Extracting & computing columns
- Counting occurrences
- Summarizing logs
- Combining AWK with `sort`, `uniq`, `grep`

## 1. Filter CSV Rows (Daily Work)

### Basic filtering by value
```bash
awk -F',' '$3 > 50' data.csv
```
Prints rows where column 3 > 50.

### Skip header, apply filter
```bash
awk -F',' 'NR==1 || $3 > 50' data.csv
```
Keeps the header, filters the data.

### Filter by exact string match
```bash
awk -F',' '$2 == "ACTIVE"' users.csv
```

### Filter using regex
```bash
awk -F',' '$4 ~ /India/' users.csv
```

### Exclude rows
```bash
awk -F',' '$5 != "NULL"' data.csv
```

## 2. Extract & Compute Columns (Core AWK Strength)

### Extract selected columns
```bash
awk -F',' '{ print $1, $3 }' data.csv
```

### Compute a new column
```bash
awk -F',' '{ print $1, $2 * $3 }' sales.csv
```
Example: quantity × price.

### Add labels for readable output
```bash
awk -F',' '{ print "User:", $1, "Score:", $3 }' scores.csv
```

### Sum a column
```bash
awk -F',' '{ sum += $4 } END { print sum }' sales.csv
```

### Average a column
```bash
awk -F',' '{ sum += $4 } END { print sum/NR }' sales.csv
```

## 3. Count Occurrences (Arrays = Power)

### Count values in a column
```bash
awk -F',' '{ count[$2]++ } END { for (k in count) print k, count[k] }' data.csv
```

### Count words
```bash
awk '{ for (i=1; i<=NF; i++) freq[$i]++ } END { for (w in freq) print w, freq[w] }' file.txt
```

### Count unique rows
```bash
awk '{ seen[$0]++ } END { print length(seen) }' file.txt
```

### Top-N results
```bash
awk '{count[$1]++} END {for (k in count) print count[k], k}' log.txt | sort -nr | head
```

## 4. Summarize Logs (Real Ops Use Cases)

### Extract error lines
```bash
awk '/ERROR/' app.log
```

### Count errors per type
```bash
awk '/ERROR/ { err[$3]++ } END { for (e in err) print e, err[e] }' app.log
```

### Requests per IP
```bash
awk '{ ip[$1]++ } END { for (i in ip) print i, ip[i] }' access.log
```

### Response-time analysis (average per key)
```bash
awk '{ sum[$1]+=$NF; cnt[$1]++ } END { for (k in sum) print k, sum[k]/cnt[k] }' perf.log
```

### Daily summaries
```bash
awk '{ day[$1]++ } END { for (d in day) print d, day[d] }' log.txt
```

## 5. Combining AWK With Other Unix Tools (This Is Leverage)

### AWK + grep (filter first)
```bash
grep ERROR app.log | awk '{count[$3]++} END {for (k in count) print k, count[k]}'
```

### AWK + sort
```bash
awk '{count[$1]++} END {for (k in count) print count[k], k}' file.txt | sort -nr
```

### AWK + uniq (clean data)
```bash
awk '{print $1}' file.txt | sort | uniq -c
```

### AWK + cut (pre-trim input)
```bash
cut -d',' -f1,3 data.csv | awk '{sum+=$2} END {print sum}'
```

### A realistic full pipeline
```bash
grep ERROR app.log |
awk '{count[$4]++} END {for (k in count) print count[k], k}' |
sort -nr |
head
```
Filter → aggregate → rank → output.

## 6. Formatting Output

```bash
awk '{ printf "%-20s %5d\n", $1, $2 }' report.txt
```
Readable reports matter for anything a human will actually read.

## 7. Safety & Best Practice

- Always test without a redirect first
- Never overwrite the input file directly (write to a temp file, then `mv`)
- Prefer pipelines over one giant monolithic AWK command
- Comment multi-line AWK scripts

## 8. Self-Check

You're solid on applied AWK if you can:
- Filter CSV rows by value or regex
- Compute totals and averages
- Count occurrences with arrays
- Summarize logs by key
- Pipe AWK output into `sort`, `uniq`, `grep`

## Key Takeaway

This level of AWK solves the large majority of everyday text/data problems, comes up often in interviews, and saves real scripting time. Natural next steps: Bash scripting (to wrap these pipelines into reusable scripts), Python (once the data/logic gets too complex for one-liners), and SQL (for anything that needs to persist).

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/AWK/AWK - Comprehensive Practical Guide|AWK — Comprehensive Practical Guide]]
- [[Data Engineering Role Notes/Linux/AWK/Arrays|AWK Arrays — What You Should Learn (Only What Matters)]]
- [[Data Engineering Role Notes/Linux/AWK/uniq commands|uniq commands]]
- [[Data Engineering Role Notes/Linux/Concept Oriented Files/AWK|AWK]]

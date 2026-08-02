Perfect. This is the **second AWK guide** — designed **only to tick these boxes** and nothing extra:

✔ Filter CSV rows  
✔ Extract & compute columns  
✔ Count occurrences  
✔ Summarize logs  
✔ Combine with `sort`, `uniq`, `grep`

This is **production-grade AWK**, the kind that actually gets used.

---

# **AWK — Comprehensive Applied Guide (Real-World Edition)**

---

## 1. Filter CSV rows (this is daily work)

### Basic filtering by value

```bash
awk -F',' '$3 > 50' data.csv
```

→ Prints rows where column 3 > 50

---

### Skip header, apply filter

```bash
awk -F',' 'NR==1 || $3 > 50' data.csv
```

✔ Keeps header  
✔ Filters data

---

### Filter by string match

```bash
awk -F',' '$2 == "ACTIVE"' users.csv
```

---

### Filter using regex

```bash
awk -F',' '$4 ~ /India/' users.csv
```

---

### Exclude rows

```bash
awk -F',' '$5 != "NULL"' data.csv
```

---

## 2. Extract & compute columns (core AWK strength)

### Extract selected columns

```bash
awk -F',' '{ print $1, $3 }' data.csv
```

---

### Compute new column

```bash
awk -F',' '{ print $1, $2 * $3 }' sales.csv
```

Example: quantity × price

---

### Add labels (professional output)

```bash
awk -F',' '{ print "User:", $1, "Score:", $3 }' scores.csv
```

---

### Sum a column

```bash
awk -F',' '{ sum += $4 } END { print sum }' sales.csv
```

---

### Average

```bash
awk -F',' '{ sum += $4 } END { print sum/NR }' sales.csv
```

---

## 3. Count occurrences (arrays = power)

### Count values in a column

```bash
awk -F',' '{ count[$2]++ } END { for (k in count) print k, count[k] }' data.csv
```

---

### Count words

```bash
awk '{ for (i=1; i<=NF; i++) freq[$i]++ } END { for (w in freq) print w, freq[w] }' file.txt
```

---

### Count unique rows

```bash
awk '{ seen[$0]++ } END { print length(seen) }' file.txt
```

---

### Top-N results

```bash
awk '{count[$1]++} END {for (k in count) print count[k], k}' log.txt | sort -nr | head
```

---

## 4. Summarize logs (real ops use cases)

### Extract error lines

```bash
awk '/ERROR/' app.log
```

---

### Count errors per type

```bash
awk '/ERROR/ { err[$3]++ } END { for (e in err) print e, err[e] }' app.log
```

---

### Requests per IP

```bash
awk '{ ip[$1]++ } END { for (i in ip) print i, ip[i] }' access.log
```

---

### Response time analysis

```bash
awk '{ sum[$1]+=$NF; cnt[$1]++ } END { for (k in sum) print k, sum[k]/cnt[k] }' perf.log
```

---

### Daily summaries

```bash
awk '{ day[$1]++ } END { for (d in day) print d, day[d] }' log.txt
```

---

## 5. Combining AWK with other Unix tools (this is leverage)

### AWK + grep (filter first)

```bash
grep ERROR app.log | awk '{count[$3]++} END {for (k in count) print k, count[k]}'
```

---

### AWK + sort

```bash
awk '{count[$1]++} END {for (k in count) print count[k], k}' file.txt | sort -nr
```

---

### AWK + uniq (clean data)

```bash
awk '{print $1}' file.txt | sort | uniq -c
```

---

### AWK + cut (pre-trim input)

```bash
cut -d',' -f1,3 data.csv | awk '{sum+=$2} END {print sum}'
```

---

### Full pipeline (realistic)

```bash
grep ERROR app.log |
awk '{count[$4]++} END {for (k in count) print count[k], k}' |
sort -nr |
head
```

✔ Filter  
✔ Aggregate  
✔ Rank  
✔ Output

---

## 6. Formatting output (professional touch)

```bash
awk '{ printf "%-20s %5d\n", $1, $2 }' report.txt
```

Readable reports matter.

---

## 7. Safety & best practice (important)

- Always **test without redirect**
    
- Never overwrite input directly
    
- Prefer pipelines over monolithic commands
    
- Use comments in multi-line AWK scripts
    

---

## 8. Self-check: you’re DONE if you can do this

✔ Filter CSV rows by value or regex  
✔ Compute totals and averages  
✔ Count occurrences with arrays  
✔ Summarize logs by key  
✔ Pipe AWK output into `sort`, `uniq`, `grep`

If yes → **stop learning AWK**. This is enough.

---

## Straight truth (career clarity)

This level of AWK:

- Solves **80–90%** of text/data problems
    
- Is respected in interviews
    
- Saves hours of scripting time
    
- Makes you look senior without noise
    

---

### What you should learn next (don’t delay)

➡️ Bash scripting (wrap these pipelines)  
➡️ Python for when data gets complex  
➡️ SQL for persistent data

If you want, next I can:

- Give **10 real interview problems**
    
- Design a **log-analysis mini project**
    
- Convert this into a **one-page cheat sheet**
    

Your move.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/AWK/AWK - Comprehensive Practical Guide|AWK — Comprehensive Practical Guide]]
- [[Data Engineering Role Notes/Linux/AWK/Arrays|AWK Arrays — What You Should Learn (Only What Matters)]]
- [[Data Engineering Role Notes/Linux/AWK/uniq commands|uniq commands]]
- [[Data Engineering Role Notes/Linux/Concept Oriented Files/AWK|AWK]]

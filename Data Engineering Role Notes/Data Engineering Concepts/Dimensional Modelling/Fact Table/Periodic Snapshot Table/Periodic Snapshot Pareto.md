Yes. If you want the **Pareto 80/20** for periodic snapshot fact tables, don't try to memorize dozens of techniques. Focus on these **7 concepts**.

## The 80/20 of Periodic Snapshot Tables

### 1. Get the grain absolutely right — #1 priority

Most important:

> **One row = one snapshot period × dimensional combination.**

For example:

```text
Customer × Month
Account × Day
Product × Week
```

Everything else follows from this.

If your grain is:

```text
Customer + Month
```

then you should never accidentally treat the rows as individual transactions.

---

### 2. Know which facts are additive, semi-additive, and non-additive

This is probably the **most important calculation concept**.

#### Additive

Can be summed across dimensions **and time**.

Example:

```text
Monthly Sales
Monthly Orders
Monthly Returns
```

January = 100  
February = 200  
March = 300

Quarter sales:

```text
100 + 200 + 300 = 600
```

---

#### Semi-additive

Can be summed across some dimensions, **but not across time**.

Classic examples:

```text
Ending Balance
Inventory
Account Balance
Headcount
```

Suppose:

|Month|Ending Balance|
|---|--:|
|Jan|100|
|Feb|150|
|Mar|200|

You **don't** calculate Q1 ending balance as:

```text
100 + 150 + 200 = 450 ❌
```

You take:

```text
March = 200 ✅
```

This is one of the most important things to understand about snapshot facts.

---

### 3. Period-over-period calculations

This is probably the **most common analytical technique**.

You compare one snapshot with the previous snapshot.

For example:

```text
Current Month Sales - Previous Month Sales
```

or:

```text
Current Balance - Previous Balance
```

or:

```text
MoM Growth =
(Current Month - Previous Month)
/
Previous Month
```

Example:

|Month|Sales|
|---|--:|
|Jan|100|
|Feb|120|
|Mar|150|

February growth:

```text
(120 - 100) / 100
= 20%
```

March:

```text
(150 - 120) / 120
= 25%
```

In SQL, this often means using:

```sql
LAG()
```

Example:

```sql
LAG(sales) OVER (
    PARTITION BY customer_id
    ORDER BY month
)
```

**Learn `LAG()` extremely well.**

---

### 4. Point-in-time / period-end calculations

Another extremely common requirement:

> "What was the state as of March?"

For snapshot tables, this is natural.

You identify the latest snapshot:

```text
MAX(snapshot_date)
```

and retrieve the corresponding facts.

For example:

```text
Customer C1
Jan → 100
Feb → 150
Mar → 180
```

"As of March" = **180**.

This is especially common for:

- Account balance
    
- Inventory
    
- Customer status
    
- Employee headcount
    
- Outstanding receivables
    
- Assets under management
    

---

### 5. Average snapshots

This one is very common but requires care.

Suppose:

|Month|Headcount|
|---|--:|
|Jan|100|
|Feb|120|
|Mar|140|

Average quarterly headcount:

```text
(100 + 120 + 140) / 3
= 120
```

But you need to know **what the business definition means**.

For example:

> Average monthly inventory

might be:

```text
AVG(month_end_inventory)
```

while:

> Average daily inventory

requires a daily snapshot or another appropriate calculation.

So don't blindly `AVG()` every snapshot measure.

---

### 6. Distinct counts — especially with dense snapshots

This is another area where people make mistakes.

Suppose your snapshot is:

```text
Customer × Month
```

and you want:

> "How many customers were active during Q1?"

If you simply sum monthly active customers:

```text
Jan = 100
Feb = 110
Mar = 120

100 + 110 + 120 = 330 ❌
```

because the **same customer can appear in multiple months**.

You may need:

```sql
COUNT(DISTINCT customer_id)
```

depending on the business definition.

This is a major distinction:

> **Number of customer-months ≠ number of unique customers.**

---

### 7. Handle zero-activity periods correctly

This is the unique advantage of periodic snapshots.

Suppose:

|Month|Customer|Sales|
|---|---|--:|
|Jan|C1|100|
|Jan|C2|0|
|Jan|C3|50|

C2 didn't disappear from the dataset.

Instead:

```text
C2 → 0
```

That allows calculations like:

```text
Active customers
Inactive customers
Zero-sales customers
Retention
Churn
Utilization
Coverage
```

without trying to infer missing rows.

---

# Your Pareto priority

If you're learning dimensional modeling, I'd prioritize them like this:

|Priority|Technique|Importance|
|---|---|---|
|🔴 1|**Understand grain**|⭐⭐⭐⭐⭐|
|🔴 2|**Additive vs semi-additive facts**|⭐⭐⭐⭐⭐|
|🔴 3|**Period-over-period / `LAG()`**|⭐⭐⭐⭐⭐|
|🟠 4|**Point-in-time / latest snapshot**|⭐⭐⭐⭐|
|🟠 5|**Distinct counts**|⭐⭐⭐⭐|
|🟠 6|**Averages across snapshots**|⭐⭐⭐|
|🟡 7|**Zero/no-activity handling**|⭐⭐⭐|

If you master **1–5**, you've probably covered **80%+ of what you'll encounter** with periodic snapshot tables.

---

## One mental model to keep

When you encounter a periodic snapshot, ask these **four questions**:

```text
1. What is the grain?
       ↓
2. Is this fact additive, semi-additive, or non-additive?
       ↓
3. Am I measuring activity during a period
   or state at a point in time?
       ↓
4. Am I comparing periods or aggregating periods?
```

That framework will prevent most snapshot-table calculation mistakes.

### One particularly important distinction

Consider:

```text
Customer × Month
```

with:

```text
Sales
Ending Balance
```

**Sales:**

```text
Jan 100
Feb 200
Mar 300

Q1 Sales = 600 ✅
```

**Ending Balance:**

```text
Jan 100
Feb 200
Mar 300

Q1 Ending Balance = 300 ✅
```

Same table. Same three rows. **Completely different aggregation logic.**

That's why Kimball puts so much emphasis on correctly defining the **grain and the meaning of each fact**.
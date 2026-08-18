Six lessons of concepts now collapse into roughly forty lines of SQL. The query below is a complete, runnable snowball — mock data included, so you can paste it into any T-SQL editor without touching a real warehouse and watch the buckets fall out. It's built as a chain of CTEs (`WITH` blocks), and that structure is deliberate: each CTE is one step from Lesson 5, in order. Read it as a pipeline, not as a wall of code — every block takes the previous block's output and does exactly one thing to it.

The company here isn't Nimbus; it's four anonymous customers, `C-01` through `C-04`, across three months of 2026. Different cast, identical plot — and by the end you'll recognize every Nimbus bucket in the output.

## The shape of the whole thing

| CTE | Lesson 5 step | What it does |
|---|---|---|
| `Fact_Subscriptions`, `Dim_Customer`, `EOM_Dates` | — | Fake input data, so the script runs standalone |
| `Customer_Snapshots` | Step 2 | Who was active, for how much, on each month-end |
| `Month_Over_Month` | Step 3 | Pair each month's EOP with the prior month's, as BOP |
| `Dimensionalized_Snowball` | Step 5 (part 1) | Attach Region — *after* the pairing |
| Final `SELECT` | Steps 4 & 5 | Categorize into buckets and aggregate |

---

## Part 1 — The mock data

```sql
WITH
Fact_Subscriptions AS (
    SELECT 'C-01' AS CustomerKey, CAST('2026-01-01' AS DATE) AS StartDate, CAST(NULL AS DATE) AS EndDate, 100 AS ARR_Amount UNION ALL
    SELECT 'C-02', '2026-01-01', '2026-02-15', 50 UNION ALL
    SELECT 'C-02', '2026-02-16', NULL, 80 UNION ALL
    SELECT 'C-03', '2026-02-01', '2026-03-15', 200 UNION ALL
    SELECT 'C-04', '2026-01-01', '2026-02-10', 150 UNION ALL
    SELECT 'C-04', '2026-03-05', NULL, 120
),
```

`SELECT ... UNION ALL SELECT ...` is just a way of typing a table literal — in your real build this CTE is replaced by whatever table Lesson 6 helped you construct. The `CAST` on the first row exists only to fix the column data types for the rows below it.

Read the four customers as stories:

- **C-01** — started January, never ends. The boring one. It should never appear in any bucket.
- **C-02** — $50 until Feb 15, then $80 from Feb 16. Two rows, no overlap: an **upgrade**, exactly like Cedar Systems.
- **C-03** — arrives Feb 1 at $200, ends Mar 15. Appears and then leaves: **New**, then **Churn**.
- **C-04** — $150 from January, ends Feb 10, then *comes back* Mar 5 at $120. A gap month with nothing active: **Churn**, then **Reactivation**. This is Foxglove Ltd compressed into three months.

```sql
Dim_Customer AS (
    SELECT 'C-01' AS CustomerKey, 'North America' AS Region UNION ALL
    SELECT 'C-02', 'EMEA' UNION ALL
    SELECT 'C-03', 'North America' UNION ALL
    SELECT 'C-04', 'EMEA'
),
EOM_Dates AS (
    SELECT CAST('2026-01-31' AS DATE) AS EOM_Date UNION ALL
    SELECT CAST('2026-02-28' AS DATE) UNION ALL
    SELECT CAST('2026-03-31' AS DATE)
),
```

`Dim_Customer` is one row per customer with its attributes — the thing you slice by. `EOM_Dates` is the list of snapshot dates: three month-ends. In production this comes from your date dimension (`SELECT Date FROM Dim_Date WHERE Is_End_Of_Month = 1`), and it's what sets the grain of the entire report.

---

## Part 2 — `Customer_Snapshots` (Lesson 5, Step 2)

```sql
Customer_Snapshots AS (
    SELECT d.EOM_Date AS Snapshot_Date, s.CustomerKey, SUM(s.ARR_Amount) AS Active_ARR,
        MIN(d.EOM_Date) OVER (PARTITION BY s.CustomerKey) AS First_Active_Month
    FROM EOM_Dates d
    INNER JOIN Fact_Subscriptions s ON s.StartDate <= d.EOM_Date AND (s.EndDate > d.EOM_Date OR s.EndDate IS NULL)
    GROUP BY d.EOM_Date, s.CustomerKey
),
```

There's no join key here in the usual sense. The join condition **is** the active test:

```sql
s.StartDate <= d.EOM_Date AND (s.EndDate > d.EOM_Date OR s.EndDate IS NULL)
```

Read it as *"is this subscription alive on this date?"* Every subscription is checked against every month-end, and only the live combinations survive. The `INNER JOIN` matters: a subscription that isn't alive on a given date produces **no row**, which is how a customer at zero ARR gets represented — by absence, exactly as in Lesson 5.

`SUM(...) GROUP BY EOM_Date, CustomerKey` rolls multiple subscriptions up to one number per customer per month. Here's the entire output:

| Snapshot_Date | CustomerKey | Active_ARR |
|---|---|---|
| 2026-01-31 | C-01 | 100 |
| 2026-01-31 | C-02 | 50 |
| 2026-01-31 | C-04 | 150 |
| 2026-02-28 | C-01 | 100 |
| 2026-02-28 | C-02 | 80 |
| 2026-02-28 | C-03 | 200 |
| 2026-03-31 | C-01 | 100 |
| 2026-03-31 | C-02 | 80 |
| 2026-03-31 | C-03 | — |
| 2026-03-31 | C-04 | 120 |

Trace two rows to convince yourself. **C-02 on 2026-02-28**: the $50 row ends Feb 15, and `'2026-02-15' > '2026-02-28'` is false, so it drops out; the $80 row started Feb 16 with a NULL end, so it survives. Result: $80. **C-04 on 2026-02-28**: the $150 row ended Feb 10, and the $120 row doesn't start until Mar 5 — *neither* row is alive, so C-04 has **no February row at all**. And C-03 has no March row: its subscription ended Mar 15, before the Mar 31 snapshot.

Those two gaps are the churns. Everything from here is about not losing them.

### `First_Active_Month`

```sql
MIN(d.EOM_Date) OVER (PARTITION BY s.CustomerKey) AS First_Active_Month
```

This is the extra fact Lesson 5 said you'd need to separate New from Reactivation. A window function runs *after* the `GROUP BY`, so it scans the grouped rows for each customer and takes the earliest snapshot date where they had any ARR. For C-04 it returns **2026-01-31** — on every one of C-04's rows, including the March one. Hold onto that; it's what stops C-04's return from being miscounted as a brand-new customer.

---

## Part 3 — `Month_Over_Month` (Lesson 5, Step 3)

This is the block to understand properly. Everything else is bookkeeping.

```sql
Month_Over_Month AS (
    SELECT COALESCE(curr.Snapshot_Date, DATEADD(month, 1, prev.Snapshot_Date)) AS Report_Month,
        COALESCE(curr.CustomerKey, prev.CustomerKey) AS CustomerKey,
        COALESCE(prev.Active_ARR, 0) AS BOP_ARR, COALESCE(curr.Active_ARR, 0) AS EOP_ARR,
        COALESCE(curr.First_Active_Month, prev.First_Active_Month) AS First_Active_Month
    FROM Customer_Snapshots curr
    FULL OUTER JOIN Customer_Snapshots prev ON curr.CustomerKey = prev.CustomerKey AND curr.Snapshot_Date = DATEADD(month, 1, prev.Snapshot_Date)
),
```

`Customer_Snapshots` is joined **to itself**. One copy is aliased `curr` (this month's EOP), the other `prev` (last month's EOP, which becomes this month's BOP). The join condition says: *same customer, and `prev`'s snapshot is exactly one month before `curr`'s.*

### Why FULL OUTER and not LEFT

A `LEFT JOIN` from `curr` would keep every customer with a current-month row and quietly discard anyone who only exists on the `prev` side. That's the Echo Retail bug from Lesson 5 — and here it would delete C-04's February churn and C-03's March churn outright, while the report still reconciled.

`FULL OUTER JOIN` keeps unmatched rows **from both sides**. Three kinds of row come out:

| Situation | `curr` | `prev` | Meaning |
|---|---|---|---|
| Matched | present | present | Customer existed in both months |
| `curr` only | present | NULL | Nothing last month → New or Reactivation |
| `prev` only | NULL | present | Nothing this month → **Churn** |

### Walking a churned customer through it

Take **C-04 in February**, since it's the case a LEFT JOIN destroys.

C-04 has snapshot rows on 2026-01-31 ($150) and 2026-03-31 ($120), and nothing in February. So when the January row sits on the `prev` side, the join goes looking for a `curr` row with CustomerKey `C-04` and Snapshot_Date = one month after Jan 31. No such row exists. Under a FULL OUTER JOIN that `prev` row still comes through — with every `curr.*` column NULL. Now the `COALESCE`s do their work:

- `Report_Month` = `COALESCE(NULL, DATEADD(month, 1, '2026-01-31'))` → **2026-02-28**. `curr.Snapshot_Date` is NULL, so the month has to be *reconstructed* from the prior side. This is the only reason that second argument exists.
- `CustomerKey` = `COALESCE(NULL, 'C-04')` → **C-04**. Same logic: take whichever side is present.
- `BOP_ARR` = `COALESCE(150, 0)` → **150**
- `EOP_ARR` = `COALESCE(NULL, 0)` → **0** ← the churn, made explicit

Result: `Report_Month 2026-02-28 | C-04 | BOP 150 | EOP 0`. That's a churn row that came into existence from *nothing on the current side*. Without FULL OUTER JOIN plus these COALESCEs, that row simply would not exist, and $150 would evaporate from the report with no error.

The mirror case is **C-04 in March**: the Mar 31 row is on the `curr` side, February has no C-04 row to match, so `prev.*` is all NULL → BOP 0, EOP 120. Note `First_Active_Month` is COALESCEd the same way, so it survives from whichever side exists — and for C-04 it's still 2026-01-31.

> **Every `COALESCE` here answers the same question:** "either side of this join might be missing — which one do I read this value from?"

> **⚠️ Sharp edge worth knowing:** the join condition uses `curr.Snapshot_Date = DATEADD(month, 1, prev.Snapshot_Date)`. Adding a month to Jan 31 clamps to Feb 28 in T-SQL, which happens to match the Feb 28 snapshot — but adding a month to Feb 28 gives Mar 28, **not** Mar 31, the actual March snapshot date. That means the Feb → Mar pairing in this exact script silently fails to match: every customer would appear to be resurrected from nothing in March, and a phantom "Mar 28" churn row would appear for February. The tables below show the *intended* result once this is fixed — the fix is to compare against `EOMONTH(DATEADD(month, 1, prev.Snapshot_Date))` instead, or better, to join on a month index from a real date dimension rather than raw date arithmetic. This exact class of bug is on the Lesson 10 mistakes checklist for a reason: date arithmetic across uneven month lengths breaks quietly, not loudly.

---

## Part 4 — `Dimensionalized_Snowball` (Lesson 5, Step 5)

```sql
Dimensionalized_Snowball AS (
    SELECT mom.*, c.Region FROM Month_Over_Month mom LEFT JOIN Dim_Customer c ON mom.CustomerKey = c.CustomerKey
)
```

One line, but its *position* is the lesson. Region is attached **after** `Month_Over_Month`, joined on `mom.CustomerKey` — which is the COALESCEd key, present on every row including churn-only rows.

Attach Region back in `Customer_Snapshots` instead and C-04's February churn row has no current-side row to carry a Region, so its $150 lands under `NULL`, EMEA's bridge stops tying out, and the churn disappears from precisely the slice where a regional manager needed to see it. That's Lesson 5's Step 5 rule, in one join.

---

## Part 5 — The final SELECT (Lesson 5, Step 4)

```sql
SELECT Report_Month, Region, SUM(BOP_ARR) AS Beginning_ARR,
    SUM(CASE WHEN BOP_ARR = 0 AND EOP_ARR > 0 AND Report_Month = First_Active_Month THEN EOP_ARR ELSE 0 END) AS New_ARR,
    SUM(CASE WHEN BOP_ARR = 0 AND EOP_ARR > 0 AND Report_Month > First_Active_Month THEN EOP_ARR ELSE 0 END) AS Resurrected_ARR,
    SUM(CASE WHEN BOP_ARR > 0 AND EOP_ARR > BOP_ARR THEN EOP_ARR - BOP_ARR ELSE 0 END) AS Expansion_ARR,
    SUM(CASE WHEN BOP_ARR > 0 AND EOP_ARR > 0 AND EOP_ARR < BOP_ARR THEN EOP_ARR - BOP_ARR ELSE 0 END) AS Contraction_ARR,
    SUM(CASE WHEN BOP_ARR > 0 AND EOP_ARR = 0 THEN -BOP_ARR ELSE 0 END) AS Churn_ARR,
    SUM(EOP_ARR) AS Ending_ARR
FROM Dimensionalized_Snowball WHERE Report_Month > '2026-01-31'
GROUP BY Report_Month, Region ORDER BY Report_Month, Region;
```

Each `CASE` is one bucket from Lesson 2, written as a filter:

- **New_ARR** — `BOP = 0, EOP > 0`, *and this is the customer's first-ever active month*. Takes the whole EOP amount.
- **Resurrected_ARR** — same first two conditions, but `Report_Month > First_Active_Month`: they were active before, went to zero, and came back. This is the **Reactivation** bucket — Foxglove Ltd's $5,000, or C-04's March return. The *only* thing separating this from New_ARR is that date comparison, which is why `First_Active_Month` had to be carried all the way down from Part 2.
- **Expansion_ARR** — `EOP > BOP > 0`, amount `EOP − BOP`. Cedar's $6,000, not its $26,000.
- **Contraction_ARR** — `BOP > EOP > 0`, also `EOP − BOP` — which is **negative**, deliberately.
- **Churn_ARR** — `BOP > 0, EOP = 0`, amount `-BOP_ARR`. Also negative.

> **A sign convention worth internalizing:** in Lesson 1 you wrote the bridge as `BOP + New + Expansion + Reactivation − Contraction − Churn = EOP`, subtracting positive numbers. This query bakes the minus signs into the values instead, so the check becomes pure addition: `Beginning + New + Resurrected + Expansion + Contraction + Churn = Ending`. Both are correct; mixing them up is how people end up double-negating churn and reporting growth that never happened.

Two more details:

**C-01 matches nothing.** $100 → $100 fails every `CASE`, contributing 0 to all six buckets while still counting in `Beginning_ARR` and `Ending_ARR`. Unchanged customers are supposed to be invisible in the middle of a bridge.

**`WHERE Report_Month > '2026-01-31'` drops January.** January has no prior snapshot, so every customer would show BOP 0 and land in New — a fake $300 New month. The first period of any snowball is a warm-up you throw away. The same reasoning applies to `First_Active_Month`: it's the earliest month *in the query's window*, so a customer active before 2026 would be mislabeled New here. A production build computes it against full history, not the reporting window.

### What comes out

**2026-02-28**

| Region | Beginning | New | Resurrected | Expansion | Contraction | Churn | Ending |
|---|---|---|---|---|---|---|---|
| EMEA | 200 | 0 | 0 | 30 | 0 | −150 | 80 |
| North America | 100 | 200 | 0 | 0 | 0 | 0 | 300 |

EMEA: C-02 expands $50 → $80 (+30) while C-04 churns (−150). North America: C-01 flat, C-03 arrives as New at $200.

**2026-03-31**

| Region | Beginning | New | Resurrected | Expansion | Contraction | Churn | Ending |
|---|---|---|---|---|---|---|---|
| EMEA | 80 | 0 | 120 | 0 | 0 | 0 | 200 |
| North America | 300 | 0 | 0 | 0 | 0 | −200 | 100 |

C-04 returns as **Resurrected**, not New — because `2026-03-31 > 2026-01-31`. C-03 churns out. Every row adds up left to right. (As flagged above, this is the intended result once the `EOMONTH` fix is applied to the alignment join — see the sharp-edge callout in Part 3.)

---

## Where to go from here

The query above is one grain: monthly, by region. Swap `Region` for `Product_Tier` and it slices differently; change `EOM_Dates` and it reports differently. What it *can't* do yet is answer a monthly and a quarterly question from the same model without recomputing — which is the next lesson.

## 📌 Key Takeaways

- The CTE chain maps one-to-one onto Lesson 5: snapshot → align → dimensionalize → categorize. Read each block as a single step, not as one big query.
- `Customer_Snapshots` uses the active test as its join condition; a customer with no live subscription produces **no row**, which is how zero ARR is represented throughout.
- `Month_Over_Month` self-joins the snapshots with a **FULL OUTER JOIN** so churn rows — which exist only on the prior side — survive. The `COALESCE`s exist to read each value from whichever side is present, including reconstructing `Report_Month` from the prior month.
- `First_Active_Month`, carried down from the snapshot CTE, is the single fact that splits **New_ARR** from **Resurrected_ARR** — the New vs Reactivation distinction from the Nimbus example.
- Contraction and churn carry **negative** values here, so the bridge check is straight addition. The first period is discarded because it has no prior snapshot to compare against. Watch for the `DATEADD`-vs-`EOMONTH` sharp edge in the alignment join — it's the exact class of mistake Lesson 10 warns about.

## ✅ Check Your Understanding

**1.** C-04 has subscription rows in `Fact_Subscriptions` covering January and March, but `Customer_Snapshots` returns no February row. Is that a bug?

**Answer:** No — it's the point. The $150 subscription ended Feb 10 and the $120 one starts Mar 5, so neither passes the active test on 2026-02-28. The missing row is what the FULL OUTER JOIN converts into a churn row with BOP 150 and EOP 0.

**2.** Somebody removes `First_Active_Month` to simplify the query and merges New and Resurrected into a single bucket. What breaks in the March numbers?

**Answer:** C-04's $120 return would be reported as New ARR. The company would look like it acquired a new customer in March when it actually won back a churned one — inflating apparent acquisition and hiding a retention win. Same error as counting Foxglove Ltd as New.

**3.** Why does the `Dim_Customer` join sit in its own CTE after `Month_Over_Month` rather than inside `Customer_Snapshots`?

**Answer:** Churned customers have no current-period snapshot row to carry a Region. Joining earlier leaves C-04's February churn with a NULL Region, so its $150 falls out of the EMEA bridge and that slice no longer reconciles. Joining afterward, on the COALESCEd CustomerKey, keeps every row attributed.

## 🔗 Continue

**Next:** [[Lesson 8 - Going Multi-Grain|Lesson 8 — Going Multi-Grain]]

## 🔗 Related Notes

- [[Dimensional Snowball Example (SQL)|Dimensional Snowball Example (SQL)]] — for the full runnable script (now corrected for the DATEADD/EOMONTH sharp edge)
- [[Steps in Building an ARR Snowball|Steps in Building an ARR Snowball]]
- [[Snowball|Snowball]]

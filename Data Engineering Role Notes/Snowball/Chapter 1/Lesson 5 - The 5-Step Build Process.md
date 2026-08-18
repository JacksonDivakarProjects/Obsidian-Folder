Everything so far has been about reading a bridge that already exists. Somebody handed you the Nimbus numbers, and you learned to interpret them. Now the direction reverses: you have a table of subscription records and you have to *produce* those numbers yourself. The good news is that this is a fixed, five-step recipe — the same five steps whether the company has six customers or sixty thousand. This lesson walks each step against the Nimbus data you already know, so you can see exactly what each step does to real rows.

## The five steps at a glance

1. **Standardize the input data** — get every subscription into a common shape.
2. **Generate period-end snapshots (EOP)** — "who was active, and for how much, on this date?"
3. **Align period over period** — last period's EOP becomes this period's BOP.
4. **Categorize** — turn each BOP/EOP pair into a bucket.
5. **Dimensionalize and aggregate** — roll up, optionally sliced by region, product, or rep.

Steps 3 and 5 are where beginners lose money out of the bridge without noticing. Watch those two closely.

---

## Step 1 — Standardize the input data

Before anything else, every subscription record needs three things: a **CustomerKey** (a stable ID, not a company name that changes spelling), a **StartDate**, and an **EndDate**.

Here is what the Nimbus data looks like once it's standardized. Nimbus's Q1 is Jan–Mar 2026 and Q2 is Apr–Jun 2026:

| SubscriptionID | CustomerKey | StartDate | EndDate | ARR_Amount |
|---|---|---|---|---|
| S-001 | Atlas Corp | 2024-03-01 | NULL | 12,000 |
| S-002 | Cedar Systems | 2024-08-01 | 2026-04-30 | 20,000 |
| S-003 | Cedar Systems | 2026-05-01 | NULL | 26,000 |
| S-004 | Delta Tech | 2025-01-15 | 2026-05-31 | 15,000 |
| S-005 | Delta Tech | 2026-06-01 | NULL | 9,000 |
| S-006 | Echo Retail | 2024-11-01 | 2026-05-20 | 10,000 |
| S-007 | Bramble Inc | 2026-04-15 | NULL | 8,000 |
| S-008 | Foxglove Ltd | 2024-02-01 | 2025-03-31 | 4,000 |
| S-009 | Foxglove Ltd | 2026-06-01 | NULL | 5,000 |

Two things to notice, because they explain a lot of later confusion:

**A change is two rows, not one edited row.** Cedar Systems didn't "become" $26,000. The $20,000 subscription *ended* and a $26,000 subscription *began*. Same for Delta Tech's downgrade. The bridge is built by comparing snapshots, so the raw data only ever has to answer "what was live on this date" — it never has to know the word "upgrade."

**Foxglove Ltd has two rows separated by a gap.** That gap — Apr 2025 through May 2026 with nothing active — is the entire reason Reactivation exists as a bucket. Keep the old row; don't let anyone "clean up" the history by deleting it.

### The one rule people break

**EndDate must be either always NULL or always a far-future sentinel (like `9999-12-31`) for open-ended contracts — never a mix.**

Why it matters: your snapshot test will be something like `EndDate > snapshot_date OR EndDate IS NULL`. That handles both conventions, so a mix appears to work. But the moment somebody writes a simpler rule elsewhere in the pipeline — "active means EndDate IS NULL" — every sentinel-dated customer silently churns. Pick one convention, write it down, and enforce it at the point the data lands.

---

## Step 2 — Generate period-end snapshots

A snapshot answers one question, once per customer, per date: *how much ARR did this customer have live on this date?*

First pick a cadence. Month-end (EOM) is the standard, because you can always roll months up into quarters but you can never split a quarter back into months. Nimbus reports quarterly, so the two snapshot dates that matter here are **2026-03-31** (Q1 EOP) and **2026-06-30** (Q2 EOP).

Then test every subscription against every snapshot date with this condition:

```
StartDate <= snapshot_date
AND (EndDate > snapshot_date OR EndDate IS NULL)
```

Read it out loud as: *"it had already started, and it hadn't finished yet."*

Applying that to Nimbus on **2026-03-31**:

| CustomerKey | Rows that pass | Active_ARR |
|---|---|---|
| Atlas Corp | S-001 | 12,000 |
| Cedar Systems | S-002 (ends 2026-04-30, still in the future) | 20,000 |
| Delta Tech | S-004 (ends 2026-05-31) | 15,000 |
| Echo Retail | S-006 (ends 2026-05-20) | 10,000 |
| **Total** | | **57,000** |

Bramble Inc doesn't appear — it hasn't started. Foxglove doesn't appear either: S-008 ended in Mar 2025, S-009 hasn't started. **Customers with no ARR produce no row at all.** That's normal, and it is the thing Step 3 has to survive.

Now **2026-06-30**:

| CustomerKey | Rows that pass | Active_ARR |
|---|---|---|
| Atlas Corp | S-001 | 12,000 |
| Cedar Systems | S-003 (S-002 ended in April) | 26,000 |
| Delta Tech | S-005 (S-004 ended in May) | 9,000 |
| Bramble Inc | S-007 | 8,000 |
| Foxglove Ltd | S-009 | 5,000 |
| **Total** | | **60,000** |

Echo Retail has now vanished from the snapshot. Those are the $57,000 and $60,000 you've been using since Lesson 1 — they aren't given to you by anyone, they're computed right here.

> **Beginner confusion:** notice the snapshot sums *per customer*, not per subscription. Cedar's two rows would both be live if their dates overlapped; summing to the customer grain first is what makes "did this customer grow or shrink" a meaningful question.

---

## Step 3 — Align period over period

This is the step where bridges quietly break.

The idea is simple: **the previous period's EOP becomes this period's BOP.** So you put the two snapshots side by side, matched on CustomerKey:

| CustomerKey | BOP (Q1 EOP) | EOP (Q2 EOP) |
|---|---|---|
| Atlas Corp | 12,000 | 12,000 |
| Cedar Systems | 20,000 | 26,000 |
| Delta Tech | 15,000 | 9,000 |
| Echo Retail | 10,000 | **0** |
| Bramble Inc | **0** | 8,000 |
| Foxglove Ltd | **0** | 5,000 |

The bolded zeros are the problem. **Echo Retail has no Q2 row. Bramble and Foxglove have no Q1 row.** There is nothing to match them against, so the join type you choose decides whether they exist at all.

### Walk through what each join actually does

**`INNER JOIN`** keeps only customers present in *both* snapshots — Atlas, Cedar, Delta. Echo, Bramble, and Foxglove all disappear. BOP becomes $47,000, EOP becomes $47,000, and your bridge reports that absolutely nothing happened this quarter. This one is at least obviously wrong.

**`LEFT JOIN` from the current period to the prior period** is the dangerous one, and it's the mistake almost everyone makes first. It keeps every Q2 customer, so Bramble and Foxglove come through fine as New and Reactivation. But Echo Retail has no Q2 row to be the "left" side, so **Echo is never in the result set at all**. Look at what your bridge would say:

```
BOP 47,000 + New 8,000 + Reactivation 5,000 + Expansion 6,000 − Contraction 6,000 − Churn 0 = EOP 60,000
```

**It reconciles.** BOP plus movements equals EOP exactly, so every sanity check you'd think to run passes. And yet the report is wrong twice over: your beginning ARR is understated by $10,000, and your churn is reported as **zero** in a quarter where a customer walked out the door. Recall from Lesson 3 that GRR is driven entirely by churn and contraction — this bug would show Nimbus at a GRR of 87.2% instead of the true 71.9%, and nothing in the arithmetic would object.

**`FULL OUTER JOIN`** keeps every customer that appears in *either* snapshot. Echo arrives from the prior side with no current match; Bramble and Foxglove arrive from the current side with no prior match. Fill the missing side with zero (`COALESCE(..., 0)`) and you get exactly the six-row table above — $57,000 → $60,000 with a real $10,000 churn.

> **The rule:** churn is an *absence*, and you cannot join to an absence. Only a FULL OUTER JOIN (or, in DAX, iterating the complete `Dim_Customer` table rather than the fact table) sees a customer who isn't there anymore.

One more detail: because either side can be missing, the CustomerKey and the reporting period both have to be taken from "whichever side exists." That's what all the `COALESCE` calls do in a real query — Lesson 7 shows them line by line.

---

## Step 4 — Apply the categorization logic

With a clean BOP/EOP pair per customer, categorization is pure arithmetic:

| Condition | Bucket |
|---|---|
| BOP = 0, EOP > 0 | **New** (or Reactivation) |
| BOP > 0, EOP > BOP | **Expansion** — the amount is the *delta*, EOP − BOP |
| BOP > 0, 0 < EOP < BOP | **Contraction** — again the delta |
| BOP > 0, EOP = 0 | **Churn** — the full BOP amount |
| BOP > 0, EOP = BOP | No movement — contributes nothing |

Nimbus, row by row: Atlas ($12,000 → $12,000) falls through every condition and contributes nothing, which is correct — its ARR simply flows from BOP to EOP. Cedar is Expansion of $6,000 (the delta, *not* the $26,000). Delta Tech is Contraction of $6,000. Echo Retail is Churn of $10,000. Bramble and Foxglove both match "BOP = 0, EOP > 0."

**And that's the catch:** New and Reactivation share a condition. Bramble has never existed before; Foxglove was a customer back in 2024. The rule above can't tell them apart because it only looks at two periods. To split them you need one extra fact — *the first period this customer was ever active* — and then: if it equals the current period it's New, if it's earlier it's Reactivation. Lesson 7 shows exactly how a query computes that.

---

## Step 5 — Dimensionalize and aggregate

The company-level total is just a `SUM ... GROUP BY period`. The interesting part is slicing: bridges by Region, Product Tier, or Sales Rep are usually the whole point, because "we grew $3,000" is a much less useful sentence than "EMEA lost $10,000 while North America gained $13,000."

**Join your dimension tables *after* Step 3, never before.**

Say Echo Retail is an EMEA account. If you attach Region to the Q2 snapshot and *then* align periods, Echo has no Q2 row — so it has no Region either. Its $10,000 of churn lands in a `NULL` / "Unknown" bucket, EMEA's bridge doesn't tie out, and the churn is invisible in exactly the slice where somebody needed to see it. Attach the dimension after alignment, keyed on the coalesced CustomerKey, and Echo carries its EMEA tag into the churn row where it belongs.

Same reasoning as Step 3, restated: **churned customers only exist on the prior-period side, so anything you attach using the current period will miss them.**

---

## 📌 Key Takeaways

- The build is a fixed five-step recipe: standardize → snapshot → align → categorize → dimensionalize. The scale of the company changes nothing about the order.
- A snapshot is one question — `StartDate <= date AND (EndDate > date OR EndDate IS NULL)` — asked per customer per date. Customers at zero produce **no row**, which is the source of most downstream bugs.
- Period alignment must use a **FULL OUTER JOIN**. A LEFT JOIN from the current period drops churned customers while still producing a bridge that reconciles perfectly — a silent, self-validating error.
- Categorization is a five-way comparison of BOP and EOP; splitting New from Reactivation needs one extra fact, the customer's first-ever active period.
- Join dimension tables **after** alignment, or churned customers lose their attribution and per-slice bridges stop tying out.

## ✅ Check Your Understanding

**1.** In Step 2 you build the 2026-03-31 snapshot and Echo Retail shows $10,000, but Bramble Inc doesn't appear in the output at all. Is something wrong?

**Answer:** No. Bramble's subscription starts 2026-04-15, so it fails the `StartDate <= snapshot_date` test and correctly produces no row. Absence from a snapshot *is* how zero ARR is represented.

**2.** A colleague's bridge uses a LEFT JOIN from the current period to the prior period. They point out that BOP + movements = EOP exactly, so it must be right. What do you tell them?

**Answer:** Reconciling proves the arithmetic is internally consistent, not that the population is complete. Churned customers have no current-period row, so they're excluded from *both* the BOP total and the churn bucket — the error cancels itself out. Their churn will read $0 and their BOP will be understated. They need a FULL OUTER JOIN.

**3.** Why can't Step 4 alone tell you that Foxglove Ltd is a Reactivation rather than a New customer?

**Answer:** Step 4 only sees two numbers, BOP = 0 and EOP = $5,000, which is identical to Bramble Inc's brand-new signup. Distinguishing them requires history from outside the current comparison — the earliest period the customer was ever active.

## 🔗 Continue

**Next:** [[Lesson 6 - Getting Real-World Dates Right|Lesson 6 — Getting Real-World Dates Right]]

## 🔗 Related Notes

- [[Steps in Building an ARR Snowball|Steps in Building an ARR Snowball]] — for the complete technical writeup of these five steps
- [[Snowball|Snowball]]

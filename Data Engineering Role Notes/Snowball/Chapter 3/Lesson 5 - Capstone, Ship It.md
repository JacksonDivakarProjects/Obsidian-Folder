Eighteen lessons ago, the question on the table was simply "our ARR went up — why?" and there wasn't a good answer available. Since then you've built a snowball, decomposed a bridge into buckets, wrestled with dates that lie, ARR that doesn't come in neat annual chunks, data that shows up late, and tests that pass while the numbers underneath are wrong. This lesson is where all of it gets used at once. Corvid Systems handed over two raw exports and a broken crosswalk. Nobody is going to tell you which rows are the traps. You're going to build the bridge, and it's going to be correct.

---

## Where we left this dataset

In **Chapter 3, Lesson 1** you profiled this exact export and came away with six flagged issues — not resolved, just flagged, because profiling is about *finding* problems, not fixing them. In **Lesson 2** you scoped the ask: what period, what grain, what definition of ARR, and which judgment calls need a human decision rather than a default.

Now the scoping is done and the profiling notes are in hand. The deliverable is a Q1→Q2 ARR bridge for Corvid Systems:

- **BOP snapshot: 2026-03-31** (Q1 end)
- **EOP snapshot: 2026-06-30** (Q2 end)

Same calendar we've been using for Nimbus Cloud Storage all along, so every date rule you already wrote still applies.

---

## What you were handed

### `crm_contracts`

One row per contract. Not one row per customer — that distinction matters for at least one account below.

| contract_id | customer_name | customer_id | contract_type | start_date | end_date | annual_value | contract_years |
|---|---|---|---|---|---|---|---|
| C-001 | Anchor Corp | CUST-001 | fixed | 2025-01-01 | NULL | $18,000 | 1 |
| C-002 | Bramwell & Sons | CUST-002 | fixed | 2024-06-01 | 2026-04-30 | $22,000 | 1 |
| C-002b | Bramwell & Sons | CUST-002 | fixed | 2026-05-01 | NULL | $28,000 | 1 |
| C-003 | Coral Bay Legal | CUST-003 | usage | 2025-02-01 | NULL | N/A — see billing_invoices | — |
| C-004 | Driftwood Partners | CUST-004 | multiyear | 2026-04-01 | 2028-03-31 | TCV $96,000 total | 2 |
| C-005 | Elmsworth Group | CUST-005 | fixed | 2026-05-15 | NULL | $36,000 | 1 |
| C-006 | Gable Restoration | CUST-006 | fixed | 2023-01-01 | 2026-05-10 | $16,000 | 1 |
| C-007 | Harlow Digital | CUST-007 | fixed | 2025-07-01 | 9999-12-31 | $10,000 | 1 |
| C-008 | Fenwick & Co | CUST-008 | fixed | 2024-09-01 | NULL | $14,000 | 1 |
| C-009 | Ivywood Studios | CUST-009 | fixed | 2025-11-01 | NULL | $8,000 | 1 |
| C-010 | Juniper Creative | CUST-010 | fixed | 2026-06-01 | NULL | $12,000 | 1 |

### `billing_invoices`

Only the rows relevant to this exercise. Note the `load_date` column — that's when the row landed in the warehouse, not when the invoice was issued.

| invoice_id | customer_name | customer_id | invoice_date | amount_billed | period_covered | load_date |
|---|---|---|---|---|---|---|
| INV-101 | Coral Bay Legal | CUST-003 | 2026-03-01 | $1,850 | 2026-02 (usage) | 2026-03-05 |
| INV-102 | Coral Bay Legal | CUST-003 | 2026-06-01 | $2,100 | 2026-05 (usage) | 2026-06-05 |
| INV-201 | Elmsworth Group | CUST-005 | 2026-05-16 | $1,500 | partial May (prorated) | 2026-05-18 |
| INV-301 | Driftwood Partners | CUST-004 | 2026-04-01 | $96,000 | full 2-year term, billed at signing | 2026-04-02 |
| INV-501 | Ivywood Studios | CUST-009 | 2026-02-15 | $8,000 | annual invoice, Nov 2025 – Oct 2026 | **2026-07-10** |

### `customer_id_crosswalk`

Maps CRM `customer_id` to billing-system `customer_id`. It covers every account **except CUST-008**.

Separately, the billing system's own customer master lists a real-world account called **"Fenwick and Co"** (no ampersand) under billing `customer_id` **CUST-008B**. There is no row anywhere linking CUST-008 to CUST-008B. The crosswalk simply doesn't know they're related.

---

## 🛠️ Try it yourself first

Stop here. Genuinely — open a scratch file and build the bridge before you read the walkthrough. You will learn roughly ten times more from getting Elmsworth wrong on your own than from watching me get it right.

Your task: produce BOP ARR and EOP ARR for all ten customers, assign each to a bucket (New / Expansion / Contraction / Churn / Reactivation / flat), and verify that the bridge ties out.

Six things are wrong with this data. Use your Lesson 1 profiling categories as a checklist:

- [ ] **Non-standard ARR shapes** — is every `annual_value` actually an annual value? Is every customer's ARR even *in* the CRM table?
- [ ] **Billing amounts that aren't ARR** — does every invoice represent a full, normal period?
- [ ] **Identity resolution** — does every row that looks like one customer *belong* to one customer, and vice versa?
- [ ] **Mixed date conventions** — does "still active" get expressed the same way in every row?
- [ ] **Data timing** — was every relevant row actually *in the warehouse* when the report was due?
- [ ] **Clean controls** — which customers are genuinely uncomplicated? Find these first; they're your anchor.

That last one is real advice, not filler. Four of these ten customers are completely clean: Anchor Corp (flat), Bramwell & Sons (expansion), Gable Restoration (churn), and Juniper Creative (new). Resolve them immediately, park them, and spend your energy on the other six. When something later doesn't tie out, you'll know the error isn't hiding in the easy half.

---

## The worked walkthrough

### Issue 1 — Coral Bay Legal: usage-based revenue has no contract value

`crm_contracts` gives contract_type `usage` and an `annual_value` of "N/A". There is no annual number to read, because there is no annual commitment — Coral Bay pays for what they use, invoiced monthly in arrears.

This is the **Chapter 2, Lesson 4** problem: ARR is a *convention* for non-contractual revenue, and you have to pick one and state it. The convention we scoped in Lesson 2 is the standard one: **annualize the most recent completed month at each snapshot.**

At **BOP (2026-03-31)**, the most recent completed usage month with an invoice is February, billed on INV-101 at $1,850:

> $1,850 × 12 = **$22,200**

At **EOP (2026-06-30)**, the most recent completed usage month is May, billed on INV-102 at $2,100:

> $2,100 × 12 = **$25,200**

Movement: **+$3,000 Expansion.**

```sql
-- Annualize the latest completed-month usage invoice as of a snapshot
SELECT
    customer_id,
    amount_billed * 12 AS arr
FROM (
    SELECT
        customer_id,
        amount_billed,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY invoice_date DESC
        ) AS rn
    FROM billing_invoices
    WHERE invoice_date <= @snapshot_date
      AND period_type = 'usage'
) latest
WHERE rn = 1;
```

One thing you must carry into the writeup: **flag this expansion as usage-driven.** A contractual expansion means someone signed something — it's durable and it will still be there next quarter. A usage expansion means Coral Bay had a busier May than February. It might reverse in July with nobody doing anything. It belongs in the Expansion bucket, but it does not deserve the same confidence as Bramwell's signed upgrade, and a reader who can't tell the two apart will over-forecast. This is precisely the caveat Chapter 2, Lesson 4 told you to attach.

### Issue 2 — Driftwood Partners: a lump sum that isn't annual

INV-301 is a $96,000 invoice. The naive read — invoice amount equals ARR — gives $96,000 and it is wrong by a factor of two.

Look at `period_covered`: "full 2-year term, billed at signing." Look at `crm_contracts`: `contract_type` is `multiyear`, the term runs 2026-04-01 to 2028-03-31, and `annual_value` is explicitly labeled **TCV $96,000 total** with `contract_years = 2`. That's Total Contract Value, not annual value. ARR normalizes to a *year*:

> $96,000 ÷ 2 = **$48,000**

Now the dates. The contract starts **2026-04-01**, which is one day after the BOP snapshot of 2026-03-31 — so at BOP, Driftwood is not a customer at all.

- BOP = **$0**
- EOP = **$48,000**
- Movement: **+$48,000 New**

```sql
-- Normalize multi-year TCV to annual value
SELECT
    customer_id,
    CASE
        WHEN contract_type = 'multiyear'
            THEN total_contract_value / NULLIF(contract_years, 0)
        ELSE annual_value
    END AS arr
FROM crm_contracts;
```

The `NULLIF` isn't decoration. A `contract_years` of 0 or NULL in a real export will either divide-by-zero or silently produce garbage, and this is exactly the kind of field that gets left blank on hand-entered records.

### Issue 3 — Elmsworth Group: a prorated stub is not a period

INV-201 bills Elmsworth $1,500 for "partial May (prorated)". The contract started 2026-05-15 — mid-month — so the first invoice covers roughly half a month.

The trap is mechanical: apply the same annualization logic you just wrote for Coral Bay and you get $1,500 × 12 = $18,000. That number is exactly half of the truth, and it looks completely plausible sitting in a bridge.

Elmsworth is not usage-based. It's a `fixed` contract with a stated `annual_value` of $36,000 sitting right there in `crm_contracts`. **The prorated invoice should be ignored entirely for ARR purposes.** ARR asks "what is this customer worth on an annualized run-rate basis," and the answer is the contracted annual value, not a partial-month billing artifact.

- ARR = **$36,000**
- Contract starts 2026-05-15, inside the EOP quarter → BOP = **$0**, EOP = **$36,000**
- Movement: **+$36,000 New**

The general rule from Chapter 2, Lesson 4: **annualize only full, normal periods.** Partial periods, one-time fees, setup charges, and credits are all invoice-level events that must never be multiplied up into a run rate. When a contract carries an explicit annual value, that value wins over anything derived from billing.

```sql
-- Exclude partial/prorated periods before any annualization
WHERE period_type = 'usage'
  AND is_prorated = 0
  AND is_one_time = 0
```

### Issue 4 — Fenwick & Co: the same customer wearing two names

CRM has **CUST-008, "Fenwick & Co"**, $14,000/year, started 2024-09-01, `end_date` NULL — active at both snapshots. Billing has **CUST-008B, "Fenwick and Co."** The crosswalk has no row connecting them. Join on `customer_id` and the database will cheerfully tell you these are two unrelated companies.

Play out what that does to your bridge. One identity appears at BOP and vanishes at EOP → a **fake -$14,000 churn**. The other appears at EOP with no BOP history → a **fake +$14,000 new**. Nothing about this customer changed. They didn't churn, they didn't sign, they didn't expand. They paid $14,000 in Q1 and $14,000 in Q2.

Here's the part worth sitting with, and it's the whole reason this customer is in the dataset:

> **The company-wide total still ties out perfectly.** −$14,000 and +$14,000 cancel. BOP + New + Expansion − Churn = EOP passes. Your test suite goes green. And your Churn number is wrong, your New number is wrong, your net revenue retention is wrong, and if anyone acts on that Churn figure they will go investigate a customer who is perfectly happy.

That is **Chapter 2, Lesson 6** made physical: a passing tie-out proves your arithmetic is internally consistent, not that your data is correct. Offsetting errors are invisible to a total-level check. Catching Fenwick requires a *different* class of test — customer-count reconciliation between periods, or a churn-list review, or a fuzzy-name duplicate scan — not a stronger version of the tie-out you already have.

**The correct resolution:** recognize via fuzzy name matching (or a manual crosswalk patch) that CUST-008 and CUST-008B are one real-world account. Use the **CRM record as authoritative** — it holds the actual contract terms, and billing's record is a downstream shadow of it. Fenwick is **flat: BOP $14,000 → EOP $14,000, no bucket.**

```sql
-- Fall back to normalized-name matching where the crosswalk has no row
SELECT
    c.customer_id                     AS crm_id,
    COALESCE(x.billing_customer_id, b.customer_id) AS resolved_billing_id
FROM crm_contracts        AS c
LEFT JOIN customer_id_crosswalk AS x
       ON x.crm_customer_id = c.customer_id
LEFT JOIN billing_customers AS b
       ON x.billing_customer_id IS NULL
      AND LOWER(REPLACE(REPLACE(REPLACE(b.customer_name, ' and ', ' & '), '.', ''), ',', ''))
        = LOWER(REPLACE(REPLACE(c.customer_name, '.', ''), ',', ''));
```

Fuzzy matching is a *detection* tool, not an *authority*. Use it to surface candidate duplicates, then have a human confirm them and write the confirmed pair back into the crosswalk permanently. Never let a name-similarity heuristic silently merge accounts in production — the day it merges "Acme Holdings" with "Acme Holdings (EMEA)" you will have manufactured a much worse problem than the one you solved.

### Issue 5 — Harlow Digital: two conventions for "still active"

Every other contract in `crm_contracts` says "still active, no end date" by leaving `end_date` NULL. Harlow's row says the same thing with `end_date = '9999-12-31'` — a far-future sentinel value. Two conventions, one table, identical meaning.

Apply the full activity comparison and Harlow behaves correctly:

```sql
-- The correct activity test — handles both conventions
WHERE start_date <= @snapshot_date
  AND (end_date > @snapshot_date OR end_date IS NULL)
```

`9999-12-31 > 2026-03-31` is true, and `9999-12-31 > 2026-06-30` is also true. Harlow is active at both snapshots: **BOP $10,000 → EOP $10,000, flat, no bucket.**

The failure mode is a downstream shortcut. It is extremely common to see `WHERE end_date IS NULL` used as shorthand for "currently active" — it's shorter, it reads naturally, and on a table where every active row really does have a NULL end date, it gives the right answer every time. Right up until one row doesn't follow the convention. Under that shorthand, Harlow has a non-NULL end date, which reads as "this contract has a defined end" — so Harlow gets treated as churning or already churned, and you invent a $10,000 churn out of a customer who never left.

This is the mixed-convention trap from **Chapter 1, Lesson 6**, and note where the danger actually lives: not in the main snapshot query, which probably uses the full comparison, but in the *ad hoc* query someone writes three weeks later to answer "who's active right now?" The defensive move is to profile `end_date` for sentinel values before you trust any convention (`MAX(end_date)` returning 9999-12-31 is a very loud signal), and better still, normalize sentinels to NULL in your staging layer so there is only ever one convention downstream.

### Issue 6 — Ivywood Studios: the row that arrived after the deadline

INV-501 is an $8,000 annual invoice covering Nov 2025 – Oct 2026, issued 2026-02-15. It proves Ivywood has been a paying $8,000/year customer since well before the BOP snapshot of 2026-03-31.

Now look at `load_date`: **2026-07-10.** That row did not exist in the warehouse until ten days *after* the EOP snapshot of 2026-06-30.

So picture the analyst who built this bridge on July 1st, on deadline, with the data as it existed that morning. No invoice for Ivywood covering the BOP quarter. Nothing in billing to establish Q1 revenue. The reasonable-looking conclusion: BOP = $0, EOP = $8,000, **+$8,000 New.** A brand-new customer in Q2 who has in fact been a customer since November.

Once the late-arriving invoice is included, the truth is: **BOP $8,000 → EOP $8,000, flat, no bucket.** Nothing happened. There was never any change to report.

This is **Chapter 2, Lesson 5's** late-arriving-data problem, and encountering it hands-on lands differently than reading about it. Two practical consequences:

1. **`invoice_date` and `load_date` answer different questions.** "What was true as of the snapshot?" uses `invoice_date`. "What did we *know* as of the reporting run?" uses `load_date`. If you need a bridge that reproduces exactly what was reported on July 1st — for an audit, or to explain why last quarter's deck disagrees with today's dashboard — you need `WHERE load_date <= @as_of_date` in the query, and you need to store that as-of date with the output.
2. **Restatement is normal and must be planned for.** Late data means a period's numbers can legitimately change after you publish them. The incremental snowball you built in Chapter 2, Lesson 5 handles this by reprocessing a trailing window rather than freezing history the moment it's written. Without that, Ivywood's correction never propagates and the phantom "+$8,000 New" lives in your reporting forever.

---

## The final bridge

Ten customers, six traps resolved, four clean controls:

| Customer | BOP ARR | EOP ARR | Bucket | Amount |
|---|---|---|---|---|
| Anchor Corp | $18,000 | $18,000 | flat | — |
| Bramwell & Sons | $22,000 | $28,000 | Expansion | +$6,000 |
| Coral Bay Legal | $22,200 | $25,200 | Expansion (usage-flagged) | +$3,000 |
| Driftwood Partners | $0 | $48,000 | New | +$48,000 |
| Elmsworth Group | $0 | $36,000 | New | +$36,000 |
| Fenwick & Co | $14,000 | $14,000 | flat | — |
| Gable Restoration | $16,000 | $0 | Churn | -$16,000 |
| Harlow Digital | $10,000 | $10,000 | flat | — |
| Ivywood Studios | $8,000 | $8,000 | flat | — |
| Juniper Creative | $0 | $12,000 | New | +$12,000 |
| **TOTAL** | **$110,200** | **$199,200** | | |

**Bucket totals:**

| Bucket | Amount | Made up of |
|---|---|---|
| New | **$96,000** | Driftwood $48,000 + Elmsworth $36,000 + Juniper $12,000 |
| Expansion | **$9,000** | Bramwell $6,000 + Coral Bay $3,000 |
| Contraction | **$0** | — |
| Churn | **-$16,000** | Gable $16,000 |
| Reactivation | **$0** | — |

**Tie-out check:**

```
  $110,200   BOP
+  $96,000   New
+   $9,000   Expansion
+       $0   Contraction
-  $16,000   Churn
+       $0   Reactivation
─────────────
  $199,200   EOP  ✓
```

Step by step: 110,200 + 96,000 = 206,200; 206,200 + 9,000 = 215,200; 215,200 − 16,000 = **199,200**. That matches the EOP column sum exactly.

A note on the four clean cases, because they're doing real work here. **Anchor Corp** never changes — flat, no end date, no ambiguity. **Bramwell & Sons** is a genuine contractual expansion: C-002 at $22,000 runs out 2026-04-30, C-002b at $28,000 picks up 2026-05-01, no gap, same `customer_id` — that's one customer renewing upward, +$6,000, and it's why the table is one row per *contract* rather than per customer. **Gable Restoration** has a hard `end_date` of 2026-05-10, inside the EOP quarter, so it's date-verified genuine churn with no gotcha attached. **Juniper Creative** starts 2026-06-01, inside the quarter, clean New. Those four give you a stable floor. When your first attempt came out to something other than $199,200, the four clean rows are the ones you *don't* re-check.

And notice how loudly the traps announce themselves once you have the right answer next to the wrong one: mishandle everything and you'd report New = $96,000 + $8,000 (Ivywood) + $14,000 (Fenwick) with Churn at −$16,000 − $14,000 (Fenwick) − $10,000 (Harlow), Elmsworth at half value, Driftwood at double. A bridge can be wrong in six independent places and still look like a perfectly ordinary quarter.

---

## What you'd actually deliver

The bridge is correct. It isn't finished — a table of numbers in a query window is not a deliverable, and this is where **Chapter 3, Lessons 3 and 4** take over.

**Per Lesson 3**, this becomes a waterfall: BOP $110,200 on the left, EOP $199,200 on the right, and the four movement bars between them, with New at $96,000 obviously dominating the story. The one-line headline writes itself — Corvid grew 81% quarter over quarter, and nearly all of it is new logos, not expansion of the existing base. That's a very different business narrative than the same growth arriving through expansion, and the chart should make the distinction unmissable at a glance.

**Per Lesson 4**, the methodology doc travels with it, and the judgment calls go near the top rather than buried in an appendix:

- **The usage-ARR convention for Coral Bay** — annualizing the latest completed month. State the rule, state that the +$3,000 expansion is usage-driven and may reverse without any customer action, and state what the alternative conventions (trailing-3-month average, trailing-12) would have produced.
- **The Fenwick identity fix** — CUST-008 and CUST-008B were manually merged because the crosswalk was missing a row. Name it as a manual intervention, note that the crosswalk should be patched permanently upstream, and note that the total would have tied out even if this had been missed.
- **The Driftwood TCV normalization** — $96,000 TCV over 2 years booked as $48,000 ARR. Anyone comparing your bridge against a cash or bookings report will see $96,000 there and needs to know why the two differ.
- **The Ivywood restatement** — if any version of this bridge was circulated before 2026-07-10, it showed Ivywood as +$8,000 New and the New bucket as $104,000. Say so explicitly. A number that changes after publication without explanation destroys more trust than the original error did.

Undocumented judgment calls are how correct analysis gets overturned in a meeting by someone with a different assumption and more confidence.

---

## What would have gone wrong without each chapter

Six issues, six lessons, and each one maps to something specific you learned earlier:

| Issue | Without the skill | Where you learned it |
|---|---|---|
| **Harlow Digital** — `9999-12-31` sentinel | `end_date IS NULL` shorthand reads a non-NULL end date as a defined end → phantom $10,000 churn | Chapter 1, Lesson 6 — mixed date conventions |
| **Coral Bay Legal** — usage ARR | No `annual_value` to read → customer dropped entirely, or a raw $1,850 invoice booked as ARR | Chapter 2, Lesson 4 — non-standard ARR |
| **Driftwood Partners** — TCV lump sum | $96,000 booked as ARR → New bucket overstated by $48,000 | Chapter 2, Lesson 4 — non-standard ARR |
| **Elmsworth Group** — prorated stub | $1,500 × 12 = $18,000 → understated by exactly half, and plausible enough that nobody questions it | Chapter 2, Lesson 4 — non-standard ARR |
| **Ivywood Studios** — `load_date` 2026-07-10 | Invoice absent at report time → phantom +$8,000 New for a customer of five months' standing | Chapter 2, Lesson 5 — incremental snowball and late-arriving data |
| **Fenwick & Co** — split identity | Fake −$14,000 churn and fake +$14,000 new, **tie-out still passes**, buckets silently wrong | Chapter 2, Lesson 6 — a passing test is not a correct number |

Read that column of failure modes as a set. Not one of them is a coding error. Every one is a *reasonable interpretation of ambiguous data* — which is exactly why they're dangerous, and exactly why none of them would be caught by code review, type checking, or a tie-out test. They're caught by knowing what ARR means well enough to notice when a number is answering a slightly different question than the one you asked.

---

## 📌 Key Takeaways

- **Real datasets don't label their traps.** Corvid's six issues sit in ordinary-looking columns among four perfectly clean customers. Profiling first (Chapter 3, Lesson 1) is what turns "eleven rows of contracts" into "six things I need to decide about."
- **Not every number that looks annual is annual.** $96,000 TCV over two years is $48,000 ARR; a $1,500 prorated stub is not $18,000 ARR; a $2,100 usage invoice *is* $25,200 ARR by convention. The unit of the source number has to be established before any arithmetic happens.
- **Identity resolution is an ARR problem, not just a data-hygiene problem.** Fenwick & Co proves that a broken join can produce a fake churn and a fake new that perfectly cancel — leaving the total correct and every bucket wrong.
- **A passing tie-out is a floor, not a ceiling.** It proves internal consistency. Catching offsetting errors needs a different class of check: customer-count reconciliation, churn-list review, duplicate-name scans.
- **Ask when the data arrived, not just what it says.** `invoice_date` and `load_date` answer different questions, and the gap between them is where phantom New customers and unexplained restatements come from.
- **Correct numbers are half a deliverable.** The waterfall communicates the story and the methodology doc protects the judgment calls. Undocumented assumptions get overturned by whoever is most confident in the room.

---

## ✅ Check Your Understanding

**1.** Your Corvid bridge ties out perfectly: BOP $110,200 + $96,000 New + $9,000 Expansion − $16,000 Churn = $199,200 EOP. A colleague says the numbers must therefore be right. What single customer in this dataset disproves that claim, and what check would actually catch the problem?

**Answer:** Fenwick & Co. If CUST-008 and CUST-008B are treated as separate customers, you get a fake −$14,000 churn under one identity and a fake +$14,000 new under the other. They cancel exactly, so BOP + movements still equals EOP and the tie-out passes — while Churn and New are both overstated by $14,000. A tie-out can never catch offsetting errors. What catches it is a check on a different dimension: reconciling customer counts between periods (an account appearing in the churn list *and* a same-value account appearing in the new list is a red flag), reviewing the churn list by name, or running a fuzzy-name duplicate scan across CRM and billing. This is Chapter 2, Lesson 6's point encountered in the wild.

**2.** Coral Bay Legal and Elmsworth Group both have invoices smaller than their ARR. Coral Bay's $2,100 gets multiplied by 12; Elmsworth's $1,500 gets ignored entirely. Why the different treatment?

**Answer:** Because the invoices represent different things. Coral Bay is a usage contract with no committed annual value — the invoice is the *only* evidence of run rate, and INV-102's $2,100 covers a full, normal month of May usage, so annualizing it to $25,200 is the agreed convention for turning non-contractual revenue into ARR. Elmsworth is a fixed contract with a stated `annual_value` of $36,000 already in the CRM, and INV-201's $1,500 covers a *partial* month (the contract started mid-month on 2026-05-15). Annualizing a partial period gives $18,000 — exactly half the truth. The rules: annualize only full, normal periods, and when an explicit contracted annual value exists, it outranks anything derived from billing.

**3.** Harlow Digital's contract has `end_date = '9999-12-31'`. Your main snapshot query uses `end_date > @snapshot_date OR end_date IS NULL` and handles it correctly, giving flat $10,000 → $10,000. So why is this still flagged as a risk worth fixing upstream?

**Answer:** Because the main query isn't the only query. `WHERE end_date IS NULL` is a natural and extremely common shorthand for "currently active," and it gives correct results on every other row in the table. The moment someone writes an ad hoc query, a data-quality check, or a downstream model using that shorthand, Harlow reads as having a defined (non-NULL) end date — treated as churning or already churned — inventing a $10,000 churn. One row that breaks the convention makes the shorthand a landmine for everyone downstream. The durable fix is normalizing sentinel dates to NULL in the staging layer so only one convention ever exists, rather than relying on every future query author to remember the exception.

---

## 🎓 Course Complete

That's the whole thing. You started at "our ARR went up and I can't explain why," and you now have the complete chain: you know what a snowball is and why the bridge decomposes into New, Expansion, Contraction, Churn, and Reactivation. You can get the dates right when the source system is inconsistent about them. You can handle ARR that arrives as usage, as multi-year TCV, as prorated stubs, and as nothing at all. You can build it incrementally and survive data that shows up late. You can test it like an engineer, and — harder — you know why a passing test isn't proof. You can walk into a dataset you've never seen, profile it, scope the ask, resolve what's actually wrong with it, and hand back a waterfall and a methodology doc that will hold up when someone pushes back.

That's the real graduation: not "I can build an ARR bridge," but "hand me your data and I will tell you what's wrong with it before I tell you what it says."

Keep [[Snowball|Snowball]] as your home base. It's the permanent index for everything here — go back to it when you hit a case in the wild that doesn't fit, and add to it when you find one that isn't covered yet. There will be one. There always is.

---

## 🔗 Related Notes

- [[Snowball|Snowball]]
- [[Lesson 6 - Getting Real-World Dates Right|Chapter 1, Lesson 6]]
- [[Lesson 4 - Taming Non-Standard ARR|Chapter 2, Lesson 4]]
- [[Lesson 5 - Making the Snowball Incremental|Chapter 2, Lesson 5]]
- [[Lesson 6 - Testing Your Snowball Like a Data Engineer|Chapter 2, Lesson 6]]
- [[Lesson 1 - Profiling a Stranger's Dataset|Chapter 3, Lesson 1]]

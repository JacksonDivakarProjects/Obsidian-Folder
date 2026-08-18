Every dataset you've worked with in this course so far was built to teach you something — the columns were clean, the conventions were consistent, and the gotchas were announced in the lesson title. Real work does not arrive that way. Someone drops two CSV exports in a shared folder, says "here's our contract data, can you build us an ARR bridge by end of quarter," and disappears into a meeting. Before you write a single line of snowball SQL against that data, you owe yourself an hour of systematic interrogation. This lesson is that hour: a repeatable profiling checklist you can run against any subscription or billing dataset, and a full worked pass of it against the raw exports from **Corvid Systems**, a contract/e-signature SaaS company whose data will be the running example for the rest of this chapter.

---

## Why profiling comes before modeling

The temptation with a new dataset is to find the columns that look like `customer_id`, `arr`, and `start_date`, wire them into the 5-step build process from Chapter 1, and see what falls out. That works right up until the moment someone in finance asks why the churn number is wrong, and you discover the answer three layers down in a `WHERE end_date IS NULL` filter you wrote in the first ten minutes.

Profiling flips the order. You spend the first pass learning what the data *actually says* — including all the places where it says something different from what the column name implies — and you write down every anomaly before you commit to a model. The output of profiling is not code. It's a **list of flagged issues**, each of which becomes either a scoping question for a stakeholder (next lesson) or a documented modeling decision (Lesson 5).

The critical discipline: **profiling flags, it does not fix.** You will be tempted to resolve each anomaly the moment you find it. Don't. Half of these are business-policy questions that you are not authorized to answer alone, and the other half have answers that depend on what the deliverable turns out to be.

---

## Corvid Systems: the raw exports

Corvid's data lands in two exports plus a mapping table:

**`crm_contracts`** — one row per contract:

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

**`billing_invoices`** — one row per invoice (relevant rows shown):

| invoice_id | customer_name | customer_id | invoice_date | amount_billed | period_covered | load_date |
|---|---|---|---|---|---|---|
| INV-101 | Coral Bay Legal | CUST-003 | 2026-03-01 | $1,850 | 2026-02 (usage) | 2026-03-05 |
| INV-102 | Coral Bay Legal | CUST-003 | 2026-06-01 | $2,100 | 2026-05 (usage) | 2026-06-05 |
| INV-201 | Elmsworth Group | CUST-005 | 2026-05-16 | $1,500 | partial May (prorated) | 2026-05-18 |
| INV-301 | Driftwood Partners | CUST-004 | 2026-04-01 | $96,000 | full 2-year term, billed at signing | 2026-04-02 |
| INV-501 | Ivywood Studios | CUST-009 | 2026-02-15 | $8,000 | annual invoice, Nov 2025 – Oct 2026 | **2026-07-10** |

**`customer_id_crosswalk`** — maps CRM `customer_id` to the billing system's own `customer_id`.

The reporting ask: a snowball from **BOP 2026-03-31** to **EOP 2026-06-30** — the same quarter-end calendar used throughout this course.

---

## The profiling checklist

Nine checks, in the order I run them. Each one is cheap, each one is reusable across any subscription dataset, and each one has caught a real production bug at least once.

### 1. Shape and claimed grain

Confirm the row count, and confirm that the key you *think* is unique actually is.

```sql
SELECT COUNT(*) AS row_count,
       COUNT(DISTINCT contract_id)  AS distinct_contracts,
       COUNT(DISTINCT customer_id)  AS distinct_customers
FROM crm_contracts;
```

If `distinct_customers < distinct_contracts`, the table is **contract-grain, not customer-grain** — which means a naive join to a customer-grain snapshot will fan out. Chapter 1's multi-grain cascade exists precisely for this situation, but you need to know you're in it before you pick a grain.

### 2. Coverage window vs. reporting window

```sql
SELECT MIN(start_date), MAX(start_date), MIN(end_date), MAX(end_date)
FROM crm_contracts;
```

Does the data actually span your BOP and EOP dates? A dataset whose earliest `start_date` is *after* your BOP will make every customer look new.

### 3. Distinct values on every type/status/category column

```sql
SELECT contract_type, COUNT(*) AS n
FROM crm_contracts
GROUP BY contract_type
ORDER BY n DESC;
```

Run this on *every* low-cardinality column, not just the ones you plan to use. Category columns are where non-standard pricing models hide.

### 4. Null-vs-sentinel convention audit

Never assume `NULL` is the only way a table says "no value." Count the competing conventions explicitly:

```sql
SELECT
  SUM(CASE WHEN end_date IS NULL                THEN 1 ELSE 0 END) AS null_end,
  SUM(CASE WHEN end_date >= '2999-01-01'        THEN 1 ELSE 0 END) AS far_future_sentinel,
  SUM(CASE WHEN end_date = '1900-01-01'         THEN 1 ELSE 0 END) AS epoch_sentinel,
  SUM(CASE WHEN end_date < start_date           THEN 1 ELSE 0 END) AS impossible_range
FROM crm_contracts;
```

If more than one of those buckets is non-zero, the table has **two conventions for the same meaning**, and every downstream filter has to handle both.

### 5. Column-type and format audit

Check that numeric-looking columns are actually numeric, and that no free text has snuck into them:

```sql
SELECT annual_value, COUNT(*) AS n
FROM crm_contracts
GROUP BY annual_value
ORDER BY n DESC;
```

Currency symbols, thousands separators, `N/A`, and prose annotations all mean the column is text and someone has been using it as a comment field.

### 6. Customer identity reconciliation across source systems

Two directions, plus a fuzzy pass. First, crosswalk completeness:

```sql
-- CRM customers with no crosswalk row
SELECT c.customer_id, c.customer_name
FROM crm_contracts c
LEFT JOIN customer_id_crosswalk x ON c.customer_id = x.crm_customer_id
WHERE x.crm_customer_id IS NULL;

-- Billing customers that resolve to no CRM contract
SELECT b.customer_id, b.customer_name
FROM billing_invoices b
LEFT JOIN customer_id_crosswalk x ON b.customer_id = x.billing_customer_id
WHERE x.billing_customer_id IS NULL;
```

Then a fuzzy name pass over the *unmatched* residue from both sides — normalize aggressively (lowercase, strip punctuation, collapse ` and ` / ` & `, drop `inc`/`llc`/`co`/`ltd` suffixes) and look for near-collisions:

```sql
SELECT crm_name, billing_name
FROM (unmatched_crm CROSS JOIN unmatched_billing)
WHERE normalize(crm_name) = normalize(billing_name);
```

An unmatched-on-both-sides pair whose normalized names collide is almost always one real company recorded twice.

### 7. Load-date vs. business-date freshness

Any table with both an event date and a warehouse `load_date` can deliver rows *about* the past *after* you've already reported on it:

```sql
SELECT invoice_id, customer_id, invoice_date, load_date,
       DATEDIFF(day, invoice_date, load_date) AS lag_days
FROM billing_invoices
WHERE load_date > '2026-06-30'      -- the EOP reporting deadline
   OR DATEDIFF(day, invoice_date, load_date) > 30;
```

Rows returned here are rows a bridge built on the reporting deadline **could not have seen**.

### 8. Invoice amount vs. contract-stated value plausibility

Where both sources carry an amount for the same account, compare them. The ratio is the signal:

```sql
SELECT c.customer_name, c.contract_type, c.annual_value, c.contract_years,
       i.amount_billed, i.period_covered,
       i.amount_billed / NULLIF(c.annual_value_numeric, 0) AS billed_to_annual_ratio
FROM crm_contracts c
JOIN billing_invoices i ON <resolved identity>
WHERE i.amount_billed > c.annual_value_numeric * 1.5    -- lump-sum suspects
   OR i.amount_billed < c.annual_value_numeric * 0.25;  -- proration suspects
```

A ratio near `contract_years` means a multi-year lump sum. A ratio far below 1 means a partial period. Neither is an error in the data — both are errors waiting to happen in your model.

### 9. Orphans in both directions

Customers with contracts but no invoices, and invoices with no contract. Each orphan is either a data gap, an identity break, or a pricing model you haven't accounted for.

---

## Running the checklist on Corvid

**Check 1** returns 11 rows, 11 distinct `contract_id`, 10 distinct `customer_id`. Bramwell & Sons holds two contracts — C-002 ending 2026-04-30 and C-002b starting 2026-05-01 at a higher value. This is contract grain. Whether that pair is an upsell or a renewal is a modeling decision, not a profiling one; see [[Lesson 6 - Getting Real-World Dates Right|Chapter 1, Lesson 6 — Getting Real-World Dates Right]] for why back-to-back contracts with adjacent dates are the classic false-churn trap.

**Check 3** returns three values in `contract_type`: `fixed` (9), `usage` (1), `multiyear` (1). Two rows out of eleven do not follow the pricing model your ARR logic assumes. That single `GROUP BY` has just surfaced two of the six issues on this dataset:

- 🚩 **Coral Bay Legal (`usage`)** — no fixed annual value exists in the contract at all. ARR has to be derived from billing. And the derivation is not obvious: their two invoices are $1,850 (Feb usage) and $2,100 (May usage), so annualizing the earlier one and annualizing the later one give materially different answers, and neither is more "correct" without a stated convention.
- 🚩 **Driftwood Partners (`multiyear`)** — a 2-year term with a total contract value, not an annual one.

**Check 4** returns `null_end = 8`, `far_future_sentinel = 1`. Harlow Digital carries `end_date = 9999-12-31` while every other open contract in the same column uses `NULL`.

- 🚩 **Harlow Digital** — two conventions for "still active" in one column. The danger isn't the sentinel itself; it's the shorthand. Any downstream logic that treats `end_date IS NULL` as a synonym for "active" silently drops Harlow, while the correct form — `end_date > snapshot_date OR end_date IS NULL` — handles both conventions without needing to know the sentinel exists. Write the full comparison everywhere and the sentinel becomes harmless.

**Check 5** shows `annual_value` is not numeric. Two rows carry prose: `N/A — see billing_invoices` and `TCV $96,000 total`. Someone used a value column to leave a note for a human reader. Every other value carries a `$` and a comma, so even the "clean" rows need parsing.

**Check 6** returns a CRM customer with no crosswalk row: **CUST-008, Fenwick & Co**. The billing-side query returns an unmatched billing customer, **CUST-008B, "Fenwick and Co"**. Normalizing both names (`fenwick and co` ↔ `fenwick & co` → `fenwick co`) collides them exactly.

- 🚩 **Fenwick** — one real company, two customer records, two IDs, no crosswalk row joining them. A naive join treats this as two customers, and depending on which side each record lands on, it can manufacture a churn and a new logo out of a single continuing account.

**Check 7** returns **INV-501 (Ivywood Studios)** — `invoice_date` 2026-02-15, `load_date` **2026-07-10**. A 145-day lag, landing ten days after the EOP reporting deadline.

- 🚩 **Ivywood Studios** — the invoice proves Ivywood was a paying customer covering Nov 2025 – Oct 2026, i.e. active well before the BOP snapshot of 2026-03-31. But anyone who built this bridge on 2026-06-30 saw no BOP-period invoice for Ivywood and would have classified them as **New** rather than **Existing**. This is exactly the failure mode that [[Lesson 5 - Making the Snowball Incremental|Chapter 2, Lesson 5 — Making the Snowball Incremental]] builds restatement windows to absorb.

**Check 8** returns two rows:

- 🚩 **Driftwood** — `amount_billed` $96,000 against a 2-year term. The ratio to a *per-year* rate is 2. Booking the invoice as ARR overstates Driftwood by exactly 2x.
- 🚩 **Elmsworth Group** — `amount_billed` $1,500 against a stated `annual_value` of $36,000, a ratio of about 0.04. The invoice is a prorated stub for a mid-May start. Note the trap on both sides: the raw $1,500 is not ARR, *and* naively annualizing it ($1,500 × 12 = $18,000) is also not ARR. The contract's stated annual rate is the honest answer here — but "use the contract when it disagrees with the invoice" is a policy, not a fact, and it directly contradicts what you have to do for Coral Bay, where no contract value exists at all.

The three pricing anomalies — usage, multi-year, and proration — are all cases of the normalization work covered in [[Lesson 4 - Taming Non-Standard ARR|Chapter 2, Lesson 4 — Taming Non-Standard ARR]]. What's new here is that nobody told you they were in the dataset. You found them.

---

## The profiling log

Write the output up as a table, not a narrative. This artifact does double duty: it's your scoping agenda for the next conversation, and it's the audit trail when someone asks in six months why Coral Bay is calculated the way it is.

| # | Account | Issue | Found by | Needs a decision from |
|---|---|---|---|---|
| 1 | Coral Bay Legal | Usage pricing, no contract ARR; annualization basis ambiguous | Check 3, 5 | Finance |
| 2 | Driftwood Partners | Multi-year TCV billed as lump sum | Check 3, 8 | Finance |
| 3 | Elmsworth Group | Prorated first invoice ≠ annual rate | Check 8 | Finance |
| 4 | Fenwick & Co | Duplicate identity across CRM and billing, crosswalk gap | Check 6 | Data owner / Finance |
| 5 | Harlow Digital | Sentinel `9999-12-31` vs `NULL` for "active" | Check 4 | Engineering (convention) |
| 6 | Ivywood Studios | Late-arriving invoice loaded after EOP deadline | Check 7 | Finance (restatement policy) |

Six issues, one hour, zero lines of bridge SQL written. That's a good trade.

And to be explicit about it: **everything above is flagged, not fixed.** No ARR values have been assigned, no customer has been bucketed, no join has been finalized. Three of these six issues can't even be resolved responsibly until you know what the deliverable is — if finance wants Coral Bay reported separately from the headline number, the usage-annualization convention stops being load-bearing entirely. That's why scoping ([[Lesson 2 - Scoping the Ask|Lesson 2 — Scoping the Ask]]) comes next, and why the actual resolution of all six — the normalization rules, the identity merge, the restatement handling, and the finished bridge — happens in [[Lesson 5 - Capstone, Ship It|Chapter 3, Lesson 5 — Capstone, Ship It]].

---

## 📌 Key Takeaways

- Profiling is a separate phase with its own output: a **list of flagged issues**, not code and not fixes. Resolving an anomaly the moment you find it commits you to a policy decision you probably don't own.
- Nine cheap checks catch most of what will hurt you: grain/uniqueness, coverage window, distinct values on category columns, null-vs-sentinel audits, column-type/format audits, cross-system identity reconciliation, load-date freshness, amount-vs-contract plausibility, and orphans in both directions.
- Category columns like `contract_type` are where non-standard pricing hides. One `GROUP BY` surfaced both Corvid's usage account and its multi-year account.
- A value column containing prose (`N/A — see billing_invoices`, `TCV $96,000 total`) is a warning that humans have been annotating a field your parser will treat as a number.
- `end_date IS NULL` is a shorthand, not a definition of "active." Writing the full `end_date > snapshot_date OR end_date IS NULL` comparison makes sentinel values like `9999-12-31` harmless without needing to know they exist.
- A `load_date` later than your reporting deadline means a bridge built on time could not have seen that row — which is a data-availability problem, not a data-quality one, and it needs a restatement policy rather than a cleanup script.

---

## ✅ Check Your Understanding

**1.** Harlow Digital's contract has `end_date = '9999-12-31'` while eight other open contracts use `NULL`. Which profiling check catches this, and why is the *fix* a change to how you write active-customer logic rather than a change to the data?

**Answer:** The null-vs-sentinel convention audit (Check 4) — counting how many distinct representations of "no end date" exist in the same column. It returns 8 NULLs and 1 far-future sentinel, proving the column carries two conventions for one meaning. The durable fix isn't cleaning the sentinel out of the source (you don't control that export, and it may reappear on the next load); it's writing every activity test as `end_date > snapshot_date OR end_date IS NULL`, which correctly evaluates both representations. A `WHERE end_date IS NULL` shorthand silently drops Harlow from the active population and manufactures a phantom churn.

**2.** Coral Bay Legal has two usage invoices, $1,850 for February and $2,100 for May. Profiling has told you there's no contract ARR to fall back on. Why does the lesson insist you stop at flagging rather than picking an annualization method now?

**Answer:** Because the choice between annualizing February, annualizing May, averaging a trailing window, or using actual billed dollars over a trailing twelve months is a **finance policy decision**, not a technical one — each is defensible and they produce different answers on both sides of the bridge. Worse, the decision may turn out to be moot: if scoping reveals that finance wants usage accounts reported as a separate line rather than blended into the headline snowball, the annualization convention stops driving the top-line number at all. Choosing before scoping risks doing work that gets thrown away and, more dangerously, burying a policy assumption inside SQL where no one will find it.

**3.** Ivywood Studios' invoice has `invoice_date` 2026-02-15 but `load_date` 2026-07-10. Why wouldn't a standard data-quality check on `invoice_date` ranges catch this, and what does it do to the BOP snapshot?

**Answer:** Nothing about `invoice_date` is anomalous — 2026-02-15 falls squarely inside the expected window, so any check that only looks at business dates sees a perfectly normal row. The problem is visible only in the *gap* between the business date and the warehouse `load_date`: the row didn't exist in the warehouse until ten days after the 2026-06-30 EOP deadline. A bridge built on time would find no BOP-period invoice for Ivywood, classify them as a **New** customer in Q2, and overstate new ARR while understating the BOP base — even though Ivywood had been paying since November 2025. Catching it requires comparing `load_date` against the reporting deadline, and handling it requires a restatement policy for prior periods.

---

## 🔗 Continue

[[Lesson 2 - Scoping the Ask|Lesson 2 — Scoping the Ask]]

---

## 🔗 Related Notes

- [[Snowball|Snowball]] — course hub
- [[Lesson 6 - Getting Real-World Dates Right|Chapter 1, Lesson 6 — Getting Real-World Dates Right]] — the date scenarios profiling has to identify
- [[Lesson 4 - Taming Non-Standard ARR|Chapter 2, Lesson 4 — Taming Non-Standard ARR]] — normalization rules for usage, multi-year, and prorated contracts
- [[Lesson 5 - Making the Snowball Incremental|Chapter 2, Lesson 5 — Making the Snowball Incremental]] — restatement windows for late-arriving data
- [[Lesson 5 - Capstone, Ship It|Chapter 3, Lesson 5 — Capstone, Ship It]] — where all six Corvid issues get resolved

Lesson 5 opened with a tidy table of subscriptions, each with a StartDate and an EndDate sitting right there in the columns. Real source systems almost never hand you that. You get a pile of invoices, or a subscription table with a start date and no end date, or a cancellations log kept somewhere else entirely. The whole snapshot step depends on those two dates, so before you can build anything you have to *manufacture* them. There are three situations you'll realistically be in, and this lesson is a decision guide for figuring out which one is yours.

## Start here: which situation are you in?

Look at the raw table your subscriptions live in and answer one question at a time:

| Does your source data have… | You're in | What you do |
|---|---|---|
| Explicit validity columns (`Valid_From` / `Valid_To`, or `Effective_Date` / `Expiry_Date`) | **Scenario 1 — SCD Type 2** | Map them straight across |
| Only invoices, payments, or charges — one row per billing event, no end date anywhere | **Scenario 2 — Transaction dates** | Derive the end date from the *next* invoice |
| Subscription rows with a start date but no end date, and a separate cancellations table | **Scenario 3 — Month-to-month** | Build the end date from the cancellations table |

If more than one describes your data, prefer the one higher in the table — explicit dates always beat derived ones.

---

## Scenario 1 — Your data already tracks history (SCD Type 2)

**What it looks like:** your CRM or warehouse keeps a row per *version* of a subscription. When Cedar Systems upgraded, the old row got closed out and a new one opened. The columns are usually called `Valid_From` and `Valid_To`, sometimes with an `Is_Current` flag.

| CustomerKey | ARR_Amount | Valid_From | Valid_To | Is_Current |
|---|---|---|---|---|
| Cedar Systems | 20,000 | 2024-08-01 | 2026-04-30 | 0 |
| Cedar Systems | 26,000 | 2026-05-01 | NULL | 1 |

**What you do:** almost nothing. `Valid_From` → StartDate, `Valid_To` → EndDate. That's the whole mapping — which is exactly why the Lesson 5 table looked the way it did. This is the shape everything else is trying to get to.

**Three things to check before you trust it:**

- **Is the end date inclusive or exclusive?** Your snapshot test is `EndDate > snapshot_date`, which treats EndDate as *the first day no longer covered*. If your source means "the last day covered," a subscription ending on 2026-03-31 will look alive on the 2026-03-31 snapshot and churn a month late. Check one known cancellation against the report and see which way it falls.
- **NULL or sentinel — but not both.** Recall the Lesson 5 Step 1 rule. Run a quick count of rows where `Valid_To IS NULL` versus `Valid_To = '9999-12-31'`. If both counts are non-zero, you have a mixed convention and it will bite something eventually.
- **Is it actually Type 2?** Some tables *look* like history but only keep the current row, silently overwriting on change. If Cedar shows only the $26,000 row and the $20,000 row is gone, you can't build a bridge from this table at all — its past is unrecoverable, and you'll need snapshots taken going forward or a different source.

---

## Scenario 2 — You only have invoices

**What it looks like:** the billing system gives you one row per charge. Suppose Nimbus's finance stack works this way — nobody stores contracts, just invoices:

| CustomerKey | InvoiceDate | ARR_Amount |
|---|---|---|
| Cedar Systems | 2026-01-15 | 20,000 |
| Cedar Systems | 2026-02-15 | 20,000 |
| Cedar Systems | 2026-03-15 | 20,000 |
| Cedar Systems | 2026-04-15 | 20,000 |
| Cedar Systems | 2026-05-15 | 26,000 |
| Cedar Systems | 2026-06-15 | 26,000 |

(If your invoices carry a monthly amount instead of an annualized one, multiply by 12 first — the snowball only ever speaks ARR.)

There is no end date anywhere. But there's an implicit one: **each invoice is valid until the next invoice replaces it.** That's a job for `LEAD`:

```sql
SELECT
    CustomerKey,
    InvoiceDate AS StartDate,
    LEAD(InvoiceDate) OVER (PARTITION BY CustomerKey ORDER BY InvoiceDate) AS EndDate,
    ARR_Amount
FROM Fact_Invoices
```

`LEAD` reaches down to the next row for that same customer, in date order, and hands you its InvoiceDate. Cedar's 2026-04-15 row now ends on 2026-05-15 — the exact day the $26,000 invoice takes over. Run it against a 2026-03-31 snapshot and Cedar shows $20,000; run it against 2026-06-30 and Cedar shows $26,000. That's the Lesson 5 result, rebuilt from invoices alone.

> **Optional refinement:** this produces one row per invoice, so Cedar gets four consecutive $20,000 rows instead of one. That's harmless — the snapshot only ever picks the single row covering each date. If you want tidier output, collapse runs of consecutive identical amounts into one row before storing.

### The part that actually causes trouble: the last invoice

Look at Echo Retail:

| CustomerKey | InvoiceDate | ARR_Amount | LEAD result |
|---|---|---|---|
| Echo Retail | 2026-03-10 | 10,000 | 2026-04-10 |
| Echo Retail | 2026-04-10 | 10,000 | 2026-05-10 |
| Echo Retail | 2026-05-10 | 10,000 | **NULL** |

There's no next invoice, so `LEAD` returns NULL — and NULL EndDate means "still active, forever." Echo Retail cancelled in May, but this pipeline will happily report $10,000 of Echo ARR in 2027. **Every customer's most recent invoice looks identical to an open-ended subscription.**

The fix is a **staleness rule**: a NULL EndDate is only genuinely "active" if the customer isn't overdue for their next invoice.

```
IF LEAD is NULL AND (today − InvoiceDate) > (billing cycle + grace period)
    THEN treat as churned, EndDate = InvoiceDate + billing cycle
    ELSE leave EndDate NULL (genuinely still active)
```

For monthly billing, "30 days plus a few days of grace" is the usual starting point. Two warnings:

- **Match the grace period to the billing cycle.** A 30-day rule applied to annual contracts will churn your entire enterprise book eleven months early. Key the rule off each customer's own cadence, not a global constant.
- **You are inferring, not observing.** A customer whose invoice run is two days late is indistinguishable from one who quit. This is the fundamental weakness of Scenario 2: churn can only be *suspected* until enough time passes, which means your most recent month or two will restate as invoices arrive. Tell your stakeholders that up front, and if a real cancellation signal exists anywhere in the business, go find it — which brings us to Scenario 3.

---

## Scenario 3 — Month-to-month, with cancellations kept separately

**What it looks like:** the subscription table has a start date and an amount, and that's it. There's no end date column because month-to-month plans just roll until somebody stops them. Cancellation lives in its own table, often owned by support or ops:

`Fact_Subscriptions`

| SubscriptionID | CustomerKey | StartDate | ARR_Amount |
|---|---|---|---|
| S-006 | Echo Retail | 2024-11-01 | 10,000 |
| S-007 | Bramble Inc | 2026-04-15 | 8,000 |
| S-008 | Foxglove Ltd | 2024-02-01 | 4,000 |
| S-009 | Foxglove Ltd | 2026-06-01 | 5,000 |

`Fact_Cancellations`

| SubscriptionID | CustomerKey | Cancellation_Date |
|---|---|---|
| S-006 | Echo Retail | 2026-05-20 |
| S-008 | Foxglove Ltd | 2025-03-31 |

**What you do:** `LEFT JOIN` the cancellations onto the subscriptions and let the cancellation date *become* the EndDate.

```sql
SELECT
    s.CustomerKey,
    s.StartDate,
    c.Cancellation_Date AS EndDate,
    s.ARR_Amount
FROM Fact_Subscriptions s
LEFT JOIN Fact_Cancellations c
    ON s.SubscriptionID = c.SubscriptionID
```

The `LEFT` is doing real work here. Anyone who never cancelled has no matching row, so `c.Cancellation_Date` comes back NULL — and NULL EndDate is precisely what the snapshot logic wants for "still active." Bramble Inc gets a NULL and stays alive; Echo Retail gets 2026-05-20 and drops out of the Q2 snapshot. The result is byte-for-byte the Lesson 5 input table.

> **The trap in that JOIN:** notice it's keyed on `SubscriptionID`, not `CustomerKey`. Join on the customer instead and Foxglove Ltd's 2025 cancellation attaches itself to *both* Foxglove rows — including S-009, the brand-new 2026 subscription. Foxglove would be born already dead, and you'd lose the $5,000 Reactivation you've been tracking since Lesson 1. Always join a cancellation to the specific thing that was cancelled.

**Also worth confirming:** is `Cancellation_Date` when they *asked* to cancel, or when service actually *ended*? A customer who cancels on 2026-05-20 with paid access through 2026-06-30 has one date that belongs in a churn-warning report and a different date that belongs in the ARR bridge. Use the service-end date; ARR is about revenue you actually hold.

---

## Once you have the dates

All three scenarios converge on the same destination: a table with CustomerKey, StartDate, EndDate, and ARR_Amount, with a single consistent convention for open-ended contracts. That's Step 1 of Lesson 5 complete. From here the remaining four steps don't care at all where the dates came from — which is exactly why it's worth doing this part properly.

## 📌 Key Takeaways

- Identify your scenario before writing any SQL: explicit validity columns (Type 2), invoices only, or start-dates-plus-a-cancellations-table. The rest of the build is identical once dates exist.
- SCD Type 2 data is a direct mapping, but verify three things: inclusive vs exclusive end dates, one consistent NULL-or-sentinel convention, and that the table really retains history rather than overwriting it.
- With invoice data, `LEAD(InvoiceDate) OVER (PARTITION BY CustomerKey ORDER BY InvoiceDate)` derives the end date — but the final invoice always returns NULL, which looks exactly like an active subscription.
- That NULL needs a **staleness rule** scaled to the billing cycle. Invoice-derived churn is inferred rather than observed, so recent periods will restate.
- With a cancellations table, `LEFT JOIN` it on the **subscription**, not the customer — otherwise an old cancellation kills a customer's later reactivation, and NULL correctly means "never cancelled, still active."

## ✅ Check Your Understanding

**1.** Your invoice-derived pipeline shows a customer as active with $40,000 ARR, but their last invoice was eight months ago. What happened, and what's missing?

**Answer:** `LEAD` returned NULL for their final invoice because there's no next row, and a NULL EndDate reads as "open-ended, still active." There's no staleness rule in place — eight months past a monthly billing cycle should have converted that NULL into a churn with an EndDate around one cycle after the last invoice.

**2.** You join a cancellations table to subscriptions on CustomerKey. Which Nimbus customer breaks, and how?

**Answer:** Foxglove Ltd. Its 2025-03-31 cancellation would attach to both the old subscription and the new 2026 one, giving the new $5,000 subscription an EndDate before its own StartDate. It would never appear in any snapshot, and the $5,000 Reactivation would vanish from the bridge. Join on SubscriptionID instead.

**3.** Your source table has `Valid_To = '2026-03-31'` for a cancelled customer, and they still show ARR in the 2026-03-31 snapshot. What's the likely cause?

**Answer:** An inclusive/exclusive mismatch. The snapshot test `EndDate > snapshot_date` assumes EndDate is the first uncovered day, but the source means 2026-03-31 was the last *covered* day. Either add a day when mapping, or change the test to `>=` — consistently, everywhere.

## 🔗 Continue

**Next:** [[Lesson 7 - Writing Your First Snowball Query|Lesson 7 — Writing Your First Snowball Query]]

## 🔗 Related Notes

- [[Deriving Start and End Dates|Deriving Start and End Dates]] — for the complete technical writeup of all three scenarios
- [[Snowball|Snowball]]

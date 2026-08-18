Every lesson up to this point has quietly leaned on an assumption so basic it never got stated out loud: that on any given date, each customer has one clean, unambiguous number called "ARR," and your job is just to compare that number across two dates. Nimbus made that easy — Atlas Corp had $12,000, Cedar had a number that went up, Delta had a number that went down, and nobody ever asked where those numbers came from. Real contracts are not so obliging. A meaningful share of the customers in any actual subscription business hand you something that is *not* an annual recurring number, and you have to convert it into one before the bridge will mean anything. Get that conversion wrong and every bucket downstream inherits the error, because the entire snowball rests on one unspoken premise: that the ARR values being differenced are genuinely comparable measurements of the same thing.

That premise is fragile in three specific, extremely common situations.

## 1. Usage-Based and Consumption Pricing

A customer pays $0.03 per GB stored per month, or $0.0004 per API call. There is no contract amount anywhere in the system. There is only a bill, and the bill is different every month because usage is different every month.

The standard convention is to annualize the most recent completed period's actual charge:

```
usage_arr = last_month_charge × 12
```

If a customer was billed $1,850 in June, their ARR for June is $22,200. This is defensible, widely used, and worth being honest about: it is a **run-rate estimate**, not a committed contract value. Nobody has promised to pay you $22,200. You are asserting "if this month repeated twelve times, that's what we'd collect."

The consequence for the bridge is real and it is not cosmetic. A usage customer's ARR can swing every single month with zero change in the underlying relationship — a seasonal traffic spike, one heavy batch job, a customer's own product launch. Feed that straight into the snowball and you manufacture Expansion in June and Contraction in July for a customer whose behavior toward you never changed at all. Recall from Chapter 1 that we read Cedar Systems' +$6,000 as a *signal* — the account deepened. For a usage customer, that same +$6,000 might be noise wearing a signal's clothes.

Two practical mitigations, both common:

- **Smooth the input.** Use a trailing-3-month average of usage charges, annualized, rather than a single month's snapshot. This costs you some responsiveness — a genuine step-change in usage takes a quarter to fully register — in exchange for killing most of the month-to-month jitter.
- **Separate the output.** Carry a distinct `usage_arr` column alongside `committed_arr`, and report retention both blended and pure-subscription. This keeps a headline NRR from being dragged around by consumption volatility that a fixed-fee-only view would never show. Nimbus's 82.5% NRR meant something precise because every dollar in it was contractual; blend in a volatile usage book and the same number stops being a clean statement about customer behavior.

Whichever you choose, choose it deliberately. The failure mode isn't picking the "wrong" one — it's not knowing which one you picked.

## 2. Multi-Year Contracts Paid in One Lump Sum

A customer signs a three-year deal worth $180,000 total, billed as a single $180,000 invoice at signing.

The naive move — and it is a very frequent one — is to record $180,000 as that customer's ARR in the signing month. That number is **Total Contract Value (TCV)**. It is not ARR, and putting it in the ARR column inflates New ARR by 3x for that account.

The correct figure:

```
ARR = TCV ÷ contract_years = $180,000 ÷ 3 = $60,000
```

$60,000 is the annualized run-rate the contract actually implies, and $60,000 is what should land in the New (or Expansion) bucket. If this customer had shown up in Nimbus's Q2 bridge alongside Bramble Inc's +$8,000 New, they'd contribute +$60,000 — not +$180,000.

This mistake is one of the most reliable ways a company's reported ARR growth gets quietly inflated. It compounds badly, too: the inflation lands entirely in one period, so a single large multi-year signing can make one quarter look spectacular and the next four look like a collapse, all from an accounting choice rather than anything the business did. And because the total *does* tie out against the invoice, a naive reconciliation against billing won't flag it.

## 3. Mid-Period Starts and Proration

A customer signs a $24,000/year contract on the 15th of the month. Their first invoice is a prorated half-month — roughly $1,000 instead of the full $2,000 monthly figure.

Is their ARR $24,000, or something scaled down to reflect the partial period?

It is $24,000. ARR is a **run-rate metric, not a cash metric.** It describes what the contract is worth annualized once fully active, and the fact that the first invoice happened to be small is a billing-calendar artifact with no bearing on the contract's terms. Record the prorated figure and you get a phantom Expansion the following month when the customer "grows" from $12,000 to $24,000 without doing anything — and your bridge will disagree with any downstream MRR reconciliation for reasons that trace to nothing real.

This reduces to one principle that resolves all three cases above:

> **ARR answers "if this contract's current terms held steady for a full year, what would we collect?" — never "what did we actually bill this specific period."**

Billing and ARR are related, they should be reconcilable, and they are not the same number. The bridge is built entirely from the latter. Whenever a normalization question comes up that this lesson didn't cover, run it through that sentence and the answer usually falls out.

## A Caution on Changing Your Mind

Every normalization above is a **judgment call**, not a derivation. Reasonable companies land differently — some amortize multi-year deals monthly, some recognize at signing; some annualize the latest usage month, some use a trailing quarter. There is no universally correct answer, only a consistently applied and documented one.

The genuine danger is *changing* the convention. Switch from lump-sum-at-signing to amortized-monthly recognition for multi-year deals, and the ARR bridge will show a step-change discontinuity in the transition period that has nothing whatsoever to do with business performance. Someone will see it, ask what happened in the market that quarter, and the answer will be "we changed a spreadsheet rule." Anyone auditing historical trends needs to know exactly when the convention changed and what it changed from — so write it down, date it, and keep the old definition alongside the new one. A methodology change that isn't documented is indistinguishable, six months later, from a business event.

## 📌 Key Takeaways

- The snowball assumes ARR values are comparable measurements across periods; non-standard pricing breaks that assumption before any SQL runs.
- Usage-based ARR is a run-rate estimate (`last_month_charge × 12`), inherently noisy — smooth it with a trailing average, report it separately, or both, so consumption jitter doesn't masquerade as Expansion and Contraction.
- A $180,000 three-year contract is $60,000 of ARR, not $180,000 — TCV is not ARR, and confusing them inflates New ARR and distorts growth trends.
- ARR is a run-rate metric, not a cash metric: a prorated first invoice does not reduce ARR. The test is always "what would a full year of current terms collect?"
- Normalization conventions are judgment calls that must be documented and held constant; a convention change creates a bridge discontinuity that looks exactly like a business event and isn't one.

## ✅ Check Your Understanding

**Q1.** A customer signs a 2-year, $150,000 contract, invoiced as a single payment on the signing date. What ARR figure belongs in the New bucket, and what would go wrong if you used the invoice amount?

**Answer:** $75,000 ($150,000 ÷ 2 years). Using the $150,000 invoice amount would record Total Contract Value as ARR, doubling this customer's contribution to New ARR — inflating that period's growth and, because the overstatement is confined to one period, making subsequent periods look artificially weak by comparison.

**Q2.** A pure usage-based customer was billed $4,000 in April, $9,000 in May, and $4,200 in June, driven entirely by one large batch migration in May. Using single-month annualization, what does the bridge show for May and June, and why is that a problem?

**Answer:** May ARR is $108,000 vs April's $48,000, producing +$60,000 of Expansion; June ARR is $50,400, producing roughly -$57,600 of Contraction. The bridge reports a dramatic expansion followed by a near-total collapse for a customer whose relationship never changed — a one-off workload rendered as two false signals. A trailing-3-month average (or a separately reported usage ARR column) would largely absorb the spike instead of amplifying it.

**Q3.** Why is a prorated first invoice the wrong basis for ARR, even though it's the actual amount collected?

**Answer:** Because ARR measures run-rate, not cash. The prorated amount reflects when in the calendar the contract started, not what the contract is worth annually. Using it understates ARR at signing and then generates a phantom Expansion the following month as the customer "grows" to their true contracted value without any actual change in terms.

## 🔗 Continue

[[Lesson 5 - Making the Snowball Incremental|Lesson 5 — Making the Snowball Incremental]]

## 🔗 Related Notes

- [[Snowball|Snowball]]

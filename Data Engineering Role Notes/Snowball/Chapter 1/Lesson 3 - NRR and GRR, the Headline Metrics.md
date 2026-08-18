Six buckets is exactly the right level of detail for diagnosing a quarter and exactly the wrong level of detail for a board meeting, a fundraise, or a Monday morning check-in. Nobody can hold six numbers in their head across four quarters and spot a trend. So the industry compresses the retention story into two percentages that answer the two questions that matter most about your existing customers: *are we keeping them*, and *are we growing them*. Those are GRR and NRR, and together they are the most scrutinised pair of numbers in SaaS.

## The cohort is the whole trick

Both metrics test one thing: what happened to the customers **you already had** at the start of the period. That means the first step is not arithmetic, it is drawing a boundary.

For Nimbus in Q1, the customers with ARR > $0 at BOP are:

| Customer | Q1 (BOP) ARR |
|---|---|
| Atlas Corp | $12,000 |
| Cedar Systems | $20,000 |
| Delta Tech | $15,000 |
| Echo Retail | $10,000 |
| **Cohort BOP total** | **$57,000** |

**Bramble Inc and Foxglove Ltd are excluded.** Both had $0 at BOP, so neither is part of the base being tested. This exclusion trips up nearly everyone at first, so it is worth being explicit about the logic:

- **New Business is excluded** because retention asks "did we hold onto what we had." Bramble was not something you had — you acquired it. Letting new sales into a retention metric would mean a company could paper over catastrophic churn by selling harder, which is precisely the confusion these metrics exist to prevent.
- **Reactivation is excluded** for the same structural reason: Foxglove had $0 at BOP, so there is no BOP dollar for its $5,000 to be "retained" relative to. You cannot retain what you did not have.

Retention metrics are deliberately blind to your acquisition engine. That is a feature. It is what lets you look at the base in isolation and see whether the product itself holds.

## Gross Revenue Retention (GRR)

GRR asks the narrow question: **of the ARR we started with, how much did we keep?** It counts losses only — churn and contraction — and gives no credit whatsoever for expansion.

```
GRR = (Cohort BOP ARR − Churn − Contraction) / Cohort BOP ARR
```

For Nimbus:

```
GRR = ($57,000 − $10,000 − $6,000) / $57,000
    = $41,000 / $57,000
    = 71.9%
```

Nimbus kept 71.9 cents of every dollar it started the quarter with. Because expansion is excluded and losses can only ever subtract, **GRR can never exceed 100%** — a ceiling, not a target. It is a pure leak measurement.

## Net Revenue Retention (NRR)

NRR asks the broader question: **what is that same cohort worth now?** It takes the identical set of customers and simply compares their end-of-period ARR to their beginning-of-period ARR, letting expansion offset the losses.

```
NRR = Cohort EOP ARR / Cohort BOP ARR
```

Walk the same four customers forward to Q2:

| Customer | Q1 (BOP) | Q2 (EOP) |
|---|---|---|
| Atlas Corp | $12,000 | $12,000 |
| Cedar Systems | $20,000 | $26,000 |
| Delta Tech | $15,000 | $9,000 |
| Echo Retail | $10,000 | $0 |
| **Cohort total** | **$57,000** | **$47,000** |

```
NRR = $47,000 / $57,000 = 82.5%
```

Note that Atlas, which appeared in no bucket at all in Lesson 2, matters enormously here — its $12,000 sits in both the numerator and denominator and is a stabilising force. Flat customers are invisible in the bridge and highly visible in retention.

Equivalently, in bucket terms:

```
NRR = ($57,000 + $6,000 expansion − $6,000 contraction − $10,000 churn) / $57,000 = 82.5%
```

Unlike GRR, **NRR can exceed 100%** — if the cohort's expansion outruns its losses, the same customers are worth more than they were a year ago and the company grows without selling anything to anyone new. That is the compounding machine every SaaS business is trying to build.

## Reading the gap between them

```
GRR 71.9%  ─────────────►  NRR 82.5%
           the 10.6-point gap
           is expansion ($6,000 / $57,000)
```

The distance between GRR and NRR is exactly your expansion contribution. This makes the pair diagnostic in a way neither number is alone:

- **High GRR, high NRR** — you keep customers and they grow. The healthy case.
- **High GRR, NRR near GRR** — customers stay but never buy more. A monetisation or product-roadmap problem, not a retention one.
- **Low GRR, high NRR** — a leaky base being masked by a handful of large upsells. Fragile: if one big expansion account stalls or churns, the whole picture collapses.
- **Low GRR, low NRR** — Nimbus.

## Benchmarks, and the honest read on Nimbus

The widely cited framework from Bessemer Venture Partners sets three NRR thresholds: **100% is Good, 110% is Better, 120%+ is Best.** Anything at or above 100% means the existing base is self-sustaining or self-growing.

The realistic target depends heavily on who you sell to, because expansion is much easier when contracts are large and seat-based:

| Segment | Typical NRR |
|---|---|
| Enterprise (>$100K ACV) | ~118% median |
| Mid-Market ($25K–$100K ACV) | ~108% |
| SMB (<$25K ACV) | ~97% |
| Best-in-class public SaaS | 120–125% |
| Private / bootstrapped B2B median | ~101–104% |

For GRR, 90%+ is generally considered healthy, with private B2B SaaS medians running around 88–91%.

Now place Nimbus against that:

| Metric | Nimbus | Healthy | Verdict |
|---|---|---|---|
| NRR | **82.5%** | 100%+ | Well below the floor |
| GRR | **71.9%** | 90%+ | Severely below |

This is a bad quarter, and it is worth sitting with rather than glossing over. At 82.5% NRR, the existing base shrinks by roughly 17.5% per period on its own. Nimbus must sell $10,000 of brand-new ARR every quarter *just to stand still* — and this quarter it barely managed that, landing +$3,000 net only because a reactivation happened to coincide with a new logo. That is not growth; it is a treadmill with the speed climbing.

The 71.9% GRR is the sharper alarm. It says the losses are not a rounding error caused by one unlucky account: over a quarter of the base leaked out. And because NRR is being propped up 10.6 points by a *single* expansion at Cedar Systems, Nimbus's headline retention number depends on one customer's continued goodwill. If Cedar had done nothing this quarter, NRR would have been 71.9% — identical to GRR.

The fix this points at is unambiguous: fix retention before spending another dollar on acquisition. Pouring new logos into a base that loses 28% of its revenue per quarter is the most expensive possible way to grow.

## Why outsiders care as much as you do

Retention metrics are not just internal hygiene — they are among the first things investors and acquirers ask for, because NRR is the closest available proxy for *whether growth is durable*.

The **Rule of 40** (growth rate % + profit margin % ≥ 40) is the standard quick test of SaaS health, and a company with strong NRR clears it far more easily: when the existing base grows on its own, you can hit the growth half of the rule without burning sales and marketing spend on constant new-logo acquisition, protecting the margin half at the same time.

But Rule of 40 alone can be passed by a company with a serious growth-quality problem — one growing fast purely by acquiring new customers as fast as it loses old ones. That is why analysts look at the two together, and the valuation spread is stark: one analysis found companies combining a Rule of 40 above 50 with NRR above 120% commanded roughly **21x EV/revenue**, against roughly **9x** for otherwise comparable companies below 120% NRR. Same revenue, more than double the valuation, because one company's growth compounds and the other's has to be repurchased every year.

For Nimbus at 82.5%, this is not an abstract multiple discussion. Any diligence process would find that number in the first hour and treat everything else in the deck as provisional.

## 📌 Key Takeaways

- Both metrics are computed on the **BOP cohort only** — customers with ARR > $0 at the start. New Business and Reactivation are excluded because you cannot retain what you did not have.
- **GRR** = (BOP − churn − contraction) / BOP. Losses only, no expansion credit, and it can never exceed 100%. Nimbus: **71.9%**.
- **NRR** = cohort EOP / cohort BOP. Includes expansion, so it can exceed 100%. Nimbus: **82.5%**.
- The gap between them *is* your expansion contribution (10.6 points for Nimbus, all of it from one customer) — which makes the pair far more diagnostic than either number alone.
- Against benchmarks (NRR 100% good / 110% better / 120% best; GRR 90%+ healthy), Nimbus is in trouble: the base shrinks on its own and growth depends entirely on continuous new acquisition — exactly the pattern investors discount most heavily.

## ✅ Check Your Understanding

**1. Why are Bramble Inc ($8,000 New) and Foxglove Ltd ($5,000 Reactivation) left out of both NRR and GRR?**

**Answer:** Both had $0 ARR at BOP, so neither is part of the base being tested. Retention measures what happened to revenue you already had. Including new sales would let a company hide severe churn by selling harder — which defeats the entire purpose of the metric.

**2. Nimbus's GRR is 71.9% and NRR is 82.5%. What single event accounts for the 10.6-point difference, and why is that a fragile position?**

**Answer:** Cedar Systems' $6,000 expansion ($6,000 / $57,000 = 10.5%). It is fragile because Nimbus's entire retention improvement over its raw loss rate rests on one customer — if Cedar had stayed flat, NRR would equal GRR at 71.9%.

**3. Could Nimbus ever report a GRR of 105%? Why or why not?**

**Answer:** No. GRR only subtracts (churn and contraction) from the beginning balance and gives no credit for expansion, so 100% is a hard ceiling reached only when nothing at all is lost. A retention figure above 100% is necessarily NRR.

## 🔗 Continue

**Next:** [[Lesson 4 - Logo Churn vs Revenue Churn|Lesson 4 — Logo Churn vs Revenue Churn]]

## 🔗 Related Notes

- [[Snowball|Snowball]]
- [[Bucket Cascade Logic|Bucket Cascade Logic]]

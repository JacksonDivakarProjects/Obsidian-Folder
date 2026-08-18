Every metric you've computed so far has had a blind spot built into its definition. NRR and GRR, as you learned back in Chapter 1, Lesson 3, deliberately fence off a single cohort — the customers who already existed at the beginning of the period — and ask what happened to *them*. New business is excluded on purpose, because mixing acquisition into a retention metric would let a big sales quarter paper over a collapsing base. That fence is a feature. But it leaves an obvious question unanswered: across the whole business, is money coming in faster than it's leaking out? That's the question the Quick Ratio exists to answer, and it's the one metric in this series that puts acquisition and retention on the same scale.

## The Formula

```
Quick Ratio = (New ARR + Expansion ARR) / (Churned ARR + Contraction ARR)
```

Growth on top, losses on the bottom. The result is a plain multiplier: *for every dollar we lose, how many dollars do we replace or add?* A Quick Ratio of 3.0 means three dollars gained for every one lost. A Quick Ratio of 1.0 means you're running on a treadmill — every dollar the sales and success teams win is exactly offset by a dollar walking out the door.

Notice what the formula does that nothing in Chapter 1 did. Recall the six buckets from Chapter 1, Lesson 2: New, Expansion, Contraction, Churn, Reactivation, Cross-sell. NRR and GRR use only the ones that touch the existing cohort. The Quick Ratio reaches across the whole bridge and grabs the growth buckets on one side and the loss buckets on the other. It is, in a real sense, the ARR bridge compressed into a single number.

## Reading the Benchmark

The widely-cited target is **4.0 or above** — four dollars gained for every one lost. That's the number venture investors and SaaS operators tend to anchor on for a company that is genuinely compounding, and it's the figure that shows up most often in the benchmark literature as the "excellent" threshold.

Between **1.0 and 4.0** you're in a moderate band. The business is still growing in gross terms, but inefficiently: a meaningful share of every dollar the go-to-market engine wins is being spent just to stand still. A company at 1.5 is acquiring aggressively *and* leaking badly, and the leak is quietly taxing every dollar of acquisition spend.

**Below 1.0** is the genuinely alarming zone, and it deserves emphasis because it can hide behind a growing top line. A Quick Ratio under 1.0 means losses exceed gains in the period — the business is structurally shrinking on the flows, regardless of what the headline ARR total happens to say in any single quarter. Timing, a large one-off deal, or an accounting quirk can hold the total up for a while, but the underlying motion is downward.

One nuance that trips people up: industry-wide average Quick Ratios have been *declining* over the past several years, drifting from the low-2s down toward the high-1s as growth conditions tightened. Which means "we're at the industry average" is not the reassurance it sounds like. Read your number against the top-tier target, not against the mean — the mean is a description of how the market is doing, not a definition of health.

## Nimbus, Scored

Take the Q1 → Q2 2026 bridge you know cold from Chapter 1: New $8,000 (Bramble Inc), Expansion $6,000 (Cedar Systems), Contraction -$6,000 (Delta Tech), Churn -$10,000 (Echo Retail), Reactivation $5,000 (Foxglove Ltd).

```
Quick Ratio = ($8,000 + $6,000) / ($10,000 + $6,000)
            = $14,000 / $16,000
            = 0.875
```

Below 1.0. Nimbus lost sixteen thousand dollars of ARR in the quarter and won back only fourteen thousand of it through new and expanded business.

Now line that up against what you already computed in Chapter 1, Lesson 3: NRR 82.5%, GRR 71.9%. Three metrics, three completely different constructions — one cohort-restricted with expansion, one cohort-restricted without, one whole-business flow-based — and all three land on the same verdict. That convergence is the useful signal. When metrics built on different foundations agree, you're looking at a structural problem, not a definitional artifact. The ARR total went *up* by $3,000 this quarter. Every underlying flow metric says that increase is not evidence of health.

## A Definitional Wrinkle Worth Knowing

Here's where practitioners diverge, and where you should be careful before comparing your number to anyone else's.

Some operators fold **Reactivation into the numerator**, alongside New — the reasoning being that a win-back is a dollar the go-to-market motion brought in, functionally indistinguishable from a fresh logo for the purpose of "did we add or did we lose." Under that convention, Nimbus looks like this:

```
Quick Ratio = ($8,000 + $6,000 + $5,000) / ($10,000 + $6,000)
            = $19,000 / $16,000
            = 1.1875
```

That's not a rounding difference. It's a different verdict. Foxglove Ltd's $5,000 reactivation moves Nimbus from "below 1.0, structurally shrinking" to "above 1.0, in the moderate-but-inefficient band." Same company, same quarter, same underlying data — two defensible conventions, two different stories a reader would take away.

The teaching point is not that one convention is right. It's that **a Quick Ratio quoted without its convention is not a number you can compare to anything.** Before you benchmark against 4.0, before you put your figure next to a competitor's in a board deck, before you trend your own number across quarters — establish which definition is in play, state it on the slide, and hold it constant. A company that quietly starts including reactivation in Q3 will show a Quick Ratio "improvement" that is pure definitional drift.

## Why It Doesn't Replace NRR and GRR

Read alongside, not instead. The Quick Ratio has a symmetric blind spot to the one it fixes: because New sits in the numerator, a company with an enormous sales engine can post a healthy-looking 4.0 while its existing base rots. Imagine $500,000 of New against $120,000 of churn — the ratio looks excellent, and yet GRR might be sitting at 60%. That's a leaky bucket being refilled by a firehose, and it works exactly as long as the acquisition spend holds up. NRR and GRR see the rot; the Quick Ratio sees the refill rate. You need both instruments pointed at the same engine.

## 📌 Key Takeaways

- The Quick Ratio, `(New + Expansion) / (Churn + Contraction)`, is the one headline metric that puts acquisition and retention on the same scale — NRR and GRR deliberately exclude new business, so they cannot answer "are we replacing what we lose?"
- Above 4.0 is the widely-cited excellent target; 1.0–4.0 is growing-but-inefficient; below 1.0 means the business is structurally shrinking on the flows even if the ARR total happens to rise.
- Industry averages have drifted from the low-2s toward the high-1s, so benchmark against the top-tier target rather than the mean — "average" and "healthy" are not the same claim.
- Nimbus scores 0.875, below 1.0, converging with the NRR of 82.5% and GRR of 71.9% from Chapter 1, Lesson 3 — three differently-constructed metrics agreeing is strong evidence of a structural problem.
- Whether Reactivation belongs in the numerator is a live definitional split: including it moves Nimbus from 0.875 to 1.1875 and flips the verdict. Always know and state which convention a Quick Ratio is using.

## ✅ Check Your Understanding

**1.** A company reports New ARR of $500,000, Expansion of $100,000, Churn of $120,000, and Contraction of $30,000. What is its Quick Ratio, and how would you characterize it against the benchmark?

**Answer:** ($500,000 + $100,000) / ($120,000 + $30,000) = $600,000 / $150,000 = **4.0** — exactly at the widely-cited "excellent" threshold. Six dollars gained for every one and a half lost.

**2.** Can a company have a Quick Ratio above 4.0 and an NRR below 100% at the same time? Explain why or why not.

**Answer:** Yes, easily — and the company above is a candidate. The Quick Ratio's numerator is dominated by New ARR, which NRR excludes entirely by construction. If $500,000 of that $600,000 numerator is new logos, the existing cohort could be shedding revenue steadily (Expansion $100,000 against Churn + Contraction of $150,000, giving an NRR well under 100%) while the overall ratio still looks excellent. This is precisely why the two metrics are read together: one measures the refill rate, the other measures the leak.

**3.** Nimbus's Quick Ratio is 0.875 under the strict definition and 1.1875 when Reactivation is included. If you were presenting to Nimbus's board, which would you show, and what would you have to do either way?

**Answer:** Either is defensible; what is *not* defensible is presenting one without labeling it. The strict version is the more conservative read and better matches the story the NRR and GRR figures tell, so it's the safer choice for a diagnostic conversation. Whichever you pick, you must state the convention explicitly on the slide and apply it consistently across every period you trend — otherwise a future quarter's "improvement" may be nothing but a change in definition.

## 🔗 Continue

[[Lesson 2 - Cohort Retention Curves|Lesson 2 — Cohort Retention Curves]]

## 🔗 Related Notes

- [[Snowball|Snowball]]
- [[Lesson 3 - NRR and GRR, the Headline Metrics|Chapter 1, Lesson 3 — NRR and GRR]]

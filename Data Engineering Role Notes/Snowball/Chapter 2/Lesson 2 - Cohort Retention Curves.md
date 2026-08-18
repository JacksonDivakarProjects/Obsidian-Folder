Here is an uncomfortable fact about everything you have computed up to this point. The NRR of 82.5%, the GRR of 71.9%, the Quick Ratio of 0.875 — every one of them describes a single quarter. Q1 2026 to Q2 2026. One hop. They are photographs, and a photograph cannot tell you whether the person in it is falling or jumping. A customer base whose revenue dips in its first quarter and then climbs steadily for three years looks identical, in a one-period snapshot taken at the wrong moment, to a customer base that is bleeding out on a straight line to zero. To tell those two apart you need to stop taking snapshots and start tracking the same group of customers forward through time. That's a cohort retention curve, and it's the first genuinely two-dimensional thing in this series.

## The Construction

A cohort is a fixed group, defined by *when its members first started paying you*. Every customer who signed in Q2 2026 belongs to the Q2 2026 cohort, permanently, no matter what happens afterward. You do not add members to a cohort later. You do not remove them when they churn. The membership list is frozen at birth.

Then you track that frozen group's **combined ARR** forward, period by period, and express each period's total as a percentage of the cohort's own starting total. Not as a percentage of company ARR, not against a moving baseline — against the number the cohort itself was worth on day one. That denominator never changes, which is what makes the resulting series a *curve* rather than a sequence of unrelated ratios.

## The Q2 2026 Nimbus Cohort

Bramble Inc, the $8,000 New logo you met in the Chapter 1 bridge, wasn't the only company that signed with Nimbus that quarter. Two others came in alongside it. Here is the full cohort, tracked forward five periods:

| Customer | Q2 2026 (cohort month 0) | Q3 2026 | Q4 2026 | Q5 2026 | Q6 2026 |
|---|---|---|---|---|---|
| Bramble Inc | $8,000 | $10,000 | $10,000 | $12,000 | $12,000 |
| Garnet Analytics | $15,000 | $15,000 | $18,000 | $18,000 | $16,000 |
| Hollow Peak Media | $6,000 | $0 | $0 | $0 | $0 |
| **Cohort total** | **$29,000** | **$25,000** | **$28,000** | **$30,000** | **$28,000** |

Three customers, $29,000 of combined starting ARR. That $29,000 is now the fixed denominator for every calculation that follows.

## Computing the Curve

Divide each period's cohort total by the cohort's own month-0 total of $29,000:

| Period | Cohort ARR | Calculation | Cohort NRR |
|---|---|---|---|
| Q2 2026 (month 0) | $29,000 | $29,000 / $29,000 | 100.0% |
| Q3 2026 | $25,000 | $25,000 / $29,000 | **86.2%** |
| Q4 2026 | $28,000 | $28,000 / $29,000 | **96.6%** |
| Q5 2026 | $30,000 | $30,000 / $29,000 | **103.4%** |
| Q6 2026 | $28,000 | $28,000 / $29,000 | **96.6%** |

Now look at the *shape*, because the shape is the entire point.

The curve **drops hard immediately** — 100% to 86.2% in one period. That's Hollow Peak Media churning in its very first quarter after signing, taking $6,000 with it. Early-lifecycle churn like this is one of the most common patterns in SaaS cohort data, and it usually points at something upstream of the product: a bad-fit deal that sales shouldn't have closed, an onboarding process that lost the customer before it ever delivered value, a champion who left. It's rarely a pricing problem and rarely a feature problem. It's a *did this customer ever actually get started* problem.

Then the curve **recovers**: 86.2% → 96.6% → 103.4%. The two survivors expand. Garnet Analytics grows $15,000 → $18,000, Bramble grows $8,000 → $10,000 → $12,000. By Q5 the cohort is worth more than it was the day it signed, despite having lost a third of its logos. This dip-then-recover-then-exceed shape is well recognized in cohort analysis and gets informally called a **J-curve** once it crosses back above 100%.

Then it **eases back** to 96.6% as Garnet contracts from $18,000 to $16,000 in Q6. Curves are not obligated to be monotonic.

Here is the punchline. A single-period snapshot taken at Q3 shows a cohort at 86.2% — struggling, a retention problem, escalate to the CS team. A single-period snapshot taken at Q5 shows the same cohort at 103.4% — thriving, net expansion, a case study for the sales deck. **Both readings are factually correct.** Neither is "the" number for this cohort, because this cohort does not have one number. It has a trajectory, and the trajectory is the finding.

## The Ceiling Nobody Mentions

Now the methodologically harder point, and the one worth slowing down for.

Hollow Peak Media's $6,000 is gone from this cohort **permanently**. Not "gone until they come back" — permanently, as a matter of definition. If Hollow Peak Media reactivates in Q7, that revenue belongs to the **Q7 cohort**, the one matching when they actually returned. It does not flow back into the Q2 2026 curve. Recall from Chapter 1, Lesson 2 that Reactivation is its own bucket precisely because a returning customer is a distinct event from a continuing one; cohort analysis takes that distinction to its logical conclusion and treats the returning customer as a new cohort member entirely.

The consequence is structural: **an early churn permanently caps a cohort's ceiling.** The Q2 2026 cohort lost 20.7% of its starting ARR in period one ($6,000 of $29,000). Everything the survivors do from that moment forward is climbing out of a hole that can never be filled from the outside. Bramble and Garnet had to add $4,000 of combined expansion just to get back to par by Q5.

Compare that to a churn happening late. If Hollow Peak Media had instead run for eight quarters, expanded to $9,000 along the way, and *then* churned, the cohort would have banked eight quarters of that revenue and the curve would have spent most of its life well above 100%. Same customer, same eventual outcome, dramatically different cohort economics. This is why early churn is not just "churn that happened sooner" — it is disproportionately more damaging, and why onboarding and first-90-days investment tends to have leverage that later-stage retention work simply doesn't.

## Why This Matters Operationally

A single blended company-wide NRR number is an average, and averages hide bimodality with impressive efficiency.

Picture a company running two acquisition channels. Channel A — inbound, self-qualified, strong product fit — produces cohorts that dip slightly and then expand for years, landing at 130% by month 24. Channel B — outbound to a segment the product doesn't really serve — produces cohorts that lose 40% in the first two quarters and never recover. Blend them together and the company-wide NRR might come out at 101%. Reassuring. Board-friendly. And completely uninformative, because the correct action — stop spending on Channel B, double down on Channel A — is invisible in the blended figure. The blend can also run the other way, making a healthy business look sick because one bad segment drags the average down.

**You cannot fix what you cannot see separated.** That's the operational case for cohorting, and it applies to any dimension you can segment on: acquisition channel, company size, industry vertical, contract type, the sales rep who closed it, the pricing plan they landed on.

The standard artifact for presenting this is the **cohort matrix**: signup periods as rows, age-since-signup as columns, so each row is one cohort's curve read left to right and each column is a same-age comparison read top to bottom. That second reading is the one people undervalue — comparing every cohort at month 6 tells you whether your retention is *improving over time*, which is a different and often more actionable question than how any individual cohort did. Plot logo retention and dollar retention side by side; the gap between them is itself diagnostic. This cohort holds 66.7% of its logos from Q3 onward while dollar retention runs from 86.2% up to 103.4% — a wide gap like that says the surviving accounts are expanding hard enough to mask a real logo problem.

## A SQL Sketch

Representative structure rather than a runnable script. The pattern is: establish each customer's cohort, compute an age for every fact row, aggregate to the cohort-age grain, then divide by the cohort's own age-0 value using a window function.

```sql
WITH cohort AS (
    -- Freeze each customer's cohort at the first month they carried ARR
    SELECT customer_id,
           MIN(month_roll) AS cohort_month
    FROM   fact_customer_arr
    WHERE  arr > 0
    GROUP  BY customer_id
),
aged AS (
    -- Attach an age (the x-axis) to every fact row
    SELECT c.cohort_month,
           f.customer_id,
           f.arr,
           DATEDIFF(MONTH, c.cohort_month, f.month_roll) AS months_since_signup
    FROM   fact_customer_arr AS f
    JOIN   cohort            AS c ON c.customer_id = f.customer_id
    WHERE  f.month_roll >= c.cohort_month
),
cohort_by_age AS (
    -- Collapse to one row per (cohort, age)
    SELECT cohort_month,
           months_since_signup,
           SUM(arr)                                                  AS cohort_arr,
           COUNT(DISTINCT CASE WHEN arr > 0 THEN customer_id END)    AS live_logos
    FROM   aged
    GROUP  BY cohort_month, months_since_signup
)
SELECT cohort_month,
       months_since_signup,
       cohort_arr,
       -- Denominator: this cohort's OWN age-0 value, broadcast across all its rows
       cohort_arr * 1.0
         / MAX(CASE WHEN months_since_signup = 0 THEN cohort_arr END)
             OVER (PARTITION BY cohort_month)  AS dollar_retention,
       live_logos * 1.0
         / MAX(CASE WHEN months_since_signup = 0 THEN live_logos END)
             OVER (PARTITION BY cohort_month)  AS logo_retention
FROM   cohort_by_age
ORDER  BY cohort_month, months_since_signup;
```

Two things to note. First, `MAX(CASE WHEN months_since_signup = 0 THEN ... END) OVER (PARTITION BY cohort_month)` is the idiom that carries the age-0 denominator down every row of a cohort without a self-join — the CASE nulls out every row except age 0, and MAX picks up the one survivor.

Second, and this is the trap: `fact_customer_arr` must be **dense**. Every customer needs a row in every month from signup onward, carrying $0 when churned. If churned customers simply stop appearing in the fact table, `live_logos` silently counts only survivors and your logo retention curve reads a flat 100% forever. This is the same zero-filling discipline you met in Chapter 1's date-handling lesson, and cohort work is where forgetting it produces the most confidently wrong chart.

## 📌 Key Takeaways

- A cohort is a group frozen at signup period; you track its combined ARR forward against its *own* month-0 total, which never changes. The output is a curve, not a number.
- The Nimbus Q2 2026 cohort runs 100% → 86.2% → 96.6% → 103.4% → 96.6%: a hard early dip from Hollow Peak Media's immediate churn, then recovery past 100% as the survivors expand — a J-curve shape invisible to any single-period metric.
- A snapshot at Q3 (86.2%, struggling) and a snapshot at Q5 (103.4%, thriving) are both correct about the same cohort. The trajectory is the finding.
- Churned revenue leaves a cohort permanently — a reactivating customer joins a *new* cohort matching their return period — so early churn caps a cohort's ceiling forever, making it disproportionately more damaging than late churn.
- Blended company-wide NRR averages away segment differences; a cohort matrix (signup period as rows, age as columns, logo and dollar retention side by side) exposes which channels or segments are actually driving the number.

## ✅ Check Your Understanding

**1.** Suppose Bramble Inc had also churned in Q3 2026, alongside Hollow Peak Media. What would the cohort's Q3 retention be, and what does that tell you about the cohort's prospects?

**Answer:** The Q3 total would be $15,000 (Garnet alone), giving $15,000 / $29,000 = **51.7%**. Nearly half the cohort's starting value would be permanently gone in period one, and the remaining survivor would have to grow from $15,000 to $29,000 — a 93% expansion — just to bring the curve back to par. That's a ceiling problem that no realistic amount of expansion is likely to solve, which is exactly why early churn is treated as the highest-leverage retention target.

**2.** Hollow Peak Media reactivates in Q7 2026 at $7,000. Does the Q2 2026 cohort's retention curve improve?

**Answer:** No. Cohort membership is frozen at first signup, but the *revenue* attribution follows the reactivation event — Hollow Peak's return belongs to the Q7 2026 cohort, the period matching when they actually came back. The Q2 2026 curve is unaffected and stays exactly where it was. This is a direct consequence of Reactivation being its own bucket rather than a reversal of Churn.

**3.** A company reports a blended NRR of 101% and considers retention solved. What would you want to see before agreeing?

**Answer:** The cohort matrix, segmented on at least one meaningful dimension — acquisition channel, segment, or plan. A blended 101% is fully consistent with one set of cohorts expanding to 130% and another bleeding to 60%, averaged together. The blend hides the only thing that's actionable: which cohorts to stop making, and which to make more of. I'd also want dollar and logo retention side by side, since a healthy dollar figure carried by a few expanding accounts can conceal a serious logo problem underneath.

## 🔗 Continue

[[Lesson 3 - Deriving the YTD Variant, For Real This Time|Lesson 3 — Deriving the YTD Variant, For Real This Time]]

## 🔗 Related Notes

- [[Snowball|Snowball]]

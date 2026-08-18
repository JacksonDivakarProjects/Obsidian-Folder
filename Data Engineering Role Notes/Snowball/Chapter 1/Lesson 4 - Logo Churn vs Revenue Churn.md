"We churned 3% this quarter" is a sentence with two entirely different meanings, and the person saying it usually has not specified which one they mean. Three percent of *customers* and three percent of *revenue* are separate measurements that happen to share a name, and in businesses with a mix of account sizes they can point in opposite directions. This is a short lesson, but conflating these two is one of the most consequential small errors in SaaS reporting.

## Two denominators, two questions

**Logo churn** counts accounts. A "logo" is one customer, regardless of whether they pay you $500 or $500,000.

```
Logo churn = customers who cancelled during the period / customers at start of period
```

**Revenue churn** counts dollars.

```
Revenue churn = ARR lost from churned customers / ARR at start of period
```

Logo churn answers *how many relationships did we fail to keep* — a signal about product-market fit, onboarding, and support quality across your base. Revenue churn answers *how much money walked out the door* — a signal about financial impact. Neither substitutes for the other.

## Nimbus, both ways

The relevant population is the customers who existed at BOP — Atlas, Cedar, Delta, and Echo. (Bramble and Foxglove had no BOP presence, so as in Lesson 3 they are outside the base.) Exactly one of the four cancelled: Echo Retail.

**Logo churn:**

```
1 customer lost / 4 customers at BOP = 25.0%
```

**Revenue churn:**

```
$10,000 lost / $57,000 BOP ARR = 17.5%
```

Note that contraction is excluded from both — Delta Tech is still a customer, so it is neither a lost logo nor churned revenue. (Its $6,000 loss does show up in *net* revenue churn, a broader variant that includes contraction and sometimes nets off expansion; when someone quotes a churn figure, it is always worth asking which variant they mean.)

## Why 25% and 17.5% differ

The two Nimbus numbers are in the same neighbourhood, but the gap is instructive. The average BOP account was $57,000 / 4 = **$14,250**. Echo Retail was worth $10,000 — *smaller than average*. Losing a below-average customer costs you a bigger share of your customer count than of your revenue, so logo churn (25%) lands above revenue churn (17.5%).

The rule generalises cleanly:

- Lose **below-average-sized** customers → logo churn > revenue churn.
- Lose **above-average-sized** customers → revenue churn > logo churn.
- Lose customers of roughly average size → the two track closely.

Had Nimbus lost Cedar Systems ($20,000) instead of Echo, logo churn would still be 25% — one of four — while revenue churn would jump to $20,000 / $57,000 = 35.1%. Same headcount loss, twice the financial damage. That is the entire point of tracking both.

## Where they diverge sharply

Nimbus is small and its account sizes are within a narrow band, so the two figures stay close. In a business with a wide spread of contract values, they can tell genuinely contradictory stories:

**Scenario A — death by a thousand cuts.** A company loses 50 small self-serve customers and keeps all 5 of its large enterprise accounts. Logo churn comes in at 10%; revenue churn is 2%. On the money, this looks fine. But 10% of your customer base decided the product was not worth keeping, and that is an early warning about onboarding, activation, or a segment you are serving badly. The revenue number will look fine right up until the same failure mode reaches an account that matters.

**Scenario B — the whale.** A company loses one large enterprise account and keeps everyone else. Logo churn is 0.5% — statistically invisible, easily lost in a rounding line. Revenue churn is 20%. A dashboard showing only logo churn would report an excellent quarter while a fifth of the revenue base disappeared. Concentration risk of this kind is exactly what a single churn metric is worst at surfacing.

For SMB-focused companies with fairly uniform contract sizes, the two metrics move together and either one is a reasonable summary. For anything with a wide range of account sizes — most companies selling across segments — they diverge, and reporting only one is a choice about which failure mode you are willing to be blind to.

## Track both, and know which one is talking

The practical discipline is simple: put both on the dashboard, always label which is which, and read them as a pair.

- **Both low** — healthy retention across the board.
- **Logo high, revenue low** — you are losing the small end. Watch onboarding and time-to-value; treat it as a leading indicator rather than a financial problem yet.
- **Logo low, revenue high** — you are losing whales, or one whale. The financial urgency is immediate and the fix is account management and executive relationships, not self-serve UX.
- **Both high** — a broad retention failure that needs attention before any growth investment.

Neither metric contains the other's information, which is why one of them alone will eventually mislead you.

## 📌 Key Takeaways

- Logo churn counts **accounts** (cancelled customers / customers at BOP); revenue churn counts **dollars** (ARR lost to cancellation / ARR at BOP). Same word, different measurements.
- Nimbus: **25% logo churn** (1 of 4) vs **17.5% revenue churn** ($10,000 of $57,000) — they differ because Echo was a smaller-than-average account.
- Losing below-average accounts pushes logo churn above revenue churn; losing above-average accounts flips it. Had Nimbus lost Cedar instead, revenue churn would have been 35.1% on identical logo churn.
- In businesses with a wide spread of account sizes the two can diverge sharply — 10% logo / 2% revenue for many small losses, or 0.5% logo / 20% revenue for a single whale.
- Both belong on the dashboard, always explicitly labelled: one is an early warning about product and onboarding, the other is the financial reality.

## ✅ Check Your Understanding

**1. Nimbus's logo churn (25%) is higher than its revenue churn (17.5%). What does that tell you about the customer it lost?**

**Answer:** That Echo Retail was smaller than the average BOP account ($10,000 against an average of $14,250). Losing a below-average customer costs a larger share of the customer count than of revenue, so logo churn exceeds revenue churn.

**2. A company reports 0.5% logo churn and calls it an outstanding quarter. What would you check before agreeing?**

**Answer:** Revenue churn. A single lost whale can produce near-zero logo churn alongside 20% revenue churn. Until you see the dollar figure, a low logo-churn number says nothing about whether the revenue base held.

**3. Delta Tech lost $6,000 this quarter. Why does it appear in neither Nimbus's logo churn nor its revenue churn?**

**Answer:** Because Delta contracted rather than churned — it is still a customer at $9,000. Both metrics as defined here count only full cancellations. Delta's loss shows up in the Contraction bucket of the bridge and in GRR/NRR, and in *net* revenue churn if that broader variant is being used.

## 🔗 Continue

**Next:** [[Lesson 5 - The 5-Step Build Process|Lesson 5 — The 5-Step Build Process]]

## 🔗 Related Notes

- [[Snowball|Snowball]]
- [[Bucket Cascade Logic|Bucket Cascade Logic]]

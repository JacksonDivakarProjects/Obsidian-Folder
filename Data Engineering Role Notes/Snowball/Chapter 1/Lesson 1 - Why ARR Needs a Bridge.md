A slide goes up in a board meeting: "ARR grew from $57,000 to $60,000 this quarter. Up 5.3%." Heads nod. Someone says "steady growth." The meeting moves on. That slide is one of the most dangerous artifacts in SaaS reporting — not because the number is wrong, but because a net change is an *average of things that have nothing to do with each other*. Growth and decay got added together and cancelled out, and what survived the collision is a single tidy figure that describes none of what actually happened.

## The problem with a single number

Consider two companies that both report exactly +$3,000 in ARR this quarter.

**Company A** signed no new customers, lost nobody, and every existing account quietly grew a little. That is a machine that compounds — the product is sticky, customers expand on their own, and any new sales you add on top land on a stable base.

**Company B** lost a third of its customers, watched another account cut its plan in half, and covered the entire hole with two large upsells and one lucky new logo. That is a leaky bucket with a firehose pointed into it. It works right up until the firehose stalls, and then the decline is instant.

On the top-line number, A and B are indistinguishable. On every decision that matters — where to spend the next dollar, whether to hire more sales reps or more customer success managers, what the company is worth — they are opposites. You cannot tell them apart until you break the change apart into its causes. That decomposition is the **ARR bridge** (also called the ARR snowball, or a waterfall).

## Meet Nimbus Cloud Storage

Nimbus is a small B2B SaaS company selling storage to other businesses. Six customers touched its books between Q1 and Q2. Q1 is the **beginning of period** (BOP); Q2 is the **end of period** (EOP).

| Customer | Q1 (BOP) ARR | Q2 (EOP) ARR | What happened |
|---|---|---|---|
| Atlas Corp | $12,000 | $12,000 | No change |
| Cedar Systems | $20,000 | $26,000 | Upgraded to a bigger plan (+$6,000) |
| Delta Tech | $15,000 | $9,000 | Downgraded (−$6,000) |
| Echo Retail | $10,000 | $0 | Cancelled entirely (−$10,000) |
| Bramble Inc | $0 | $8,000 | Brand new customer this quarter (+$8,000) |
| Foxglove Ltd | $0 | $5,000 | Churned a year ago, came back this quarter (+$5,000) |
| **Total** | **$57,000** | **$60,000** | |

$57,000 → $60,000. Plus 5.3%. That is the slide.

Now look at the right-hand column. Nimbus lost a customer outright, had another cut its spend by 40%, and only came out ahead because one upsell, one new logo, and one returning customer happened to land in the same quarter. Nimbus is Company B. The +5.3% headline actively conceals that.

## The five forces underneath (and a sixth later)

Every dollar of movement between BOP and EOP is caused by exactly one of a small set of events. Here are the five you need now — full definitions come in Lesson 2, this is the vocabulary preview:

- **New Business** — ARR from customers you did not have before. *Bramble Inc, +$8,000.*
- **Expansion** — additional ARR from an existing customer buying more of what they already have. *Cedar Systems, +$6,000.*
- **Reactivation** — ARR from a customer who had previously churned and has now come back. *Foxglove Ltd, +$5,000.*
- **Contraction** — ARR lost from a customer who downgraded but is still a customer. *Delta Tech, −$6,000.*
- **Churn** — ARR lost from a customer who cancelled entirely. *Echo Retail, −$10,000.*

Atlas Corp appears in none of these, because nothing happened to Atlas. That is correct behaviour, not an omission — Lesson 2 explains why.

A sixth bucket, **Cross-sell** (an existing customer buying a *different* product, as opposed to more of the same one), only becomes meaningful once you track ARR at the product level rather than the customer level. That is a multi-grain concern and it waits until Lesson 8.

## The bridge formula

Those five buckets are not a loose list of things worth noticing. They are exhaustive and mutually exclusive, which means they must **reconcile** — add them to the beginning balance and you are obligated to land exactly on the ending balance:

```
Beginning ARR
  + New Business
  + Expansion
  + Reactivation
  − Contraction
  − Churn
  = Ending ARR
```

For Nimbus:

```
$57,000 + $8,000 + $6,000 + $5,000 − $6,000 − $10,000 = $60,000 ✓
```

This equation is the whole discipline in one line. If your buckets do not sum back to the ending balance, you have miscategorised something, double-counted a customer, or missed one entirely — and the bridge tells you so immediately. That self-checking property is why finance teams trust a bridge and do not trust a hand-assembled list of "notable account changes." A bridge that reconciles is provably complete.

## What the bridge tells you that the headline could not

Read the Nimbus buckets as a story instead of a table. Gross losses were $16,000 ($6,000 contraction + $10,000 churn) against a starting base of $57,000 — Nimbus destroyed 28% of its own revenue base in a single quarter. Gross additions were $19,000, of which $13,000 came from customers who were not in the base at all (Bramble and Foxglove). Strip out the new and returning customers and the existing base shrank from $57,000 to $47,000.

That is a fundamentally different sentence from "up 5.3%," and it points at a completely different set of actions: this is a retention problem, not a demand problem. Hiring two more sales reps would not fix it. Lesson 3 turns exactly this observation into two summary metrics — NRR and GRR — that let you say it in one number instead of a paragraph.

## 📌 Key Takeaways

- A net ARR change is a *sum of offsetting forces*; two companies with identical growth can have opposite underlying health.
- The ARR bridge decomposes that net change into its causes: New, Expansion, Reactivation, Contraction, and Churn (plus Cross-sell once you go multi-grain).
- The buckets must reconcile — Beginning + New + Expansion + Reactivation − Contraction − Churn = Ending — and that constraint is what makes a bridge trustworthy rather than anecdotal.
- Nimbus grew 5.3% while destroying $16,000 of a $57,000 base; the headline number hid a serious retention problem.
- Different buckets imply different fixes — churn points at customer success, weak new business points at sales, weak expansion points at product and pricing.

## ✅ Check Your Understanding

**1. Two SaaS companies both report ARR growth of exactly +$500,000 this year. What is the single most important question to ask before deciding which one is healthier?**

**Answer:** How much of that came from the existing customer base versus new logos, and how much revenue was lost along the way. A company that grew +$500K on top of a stable base is compounding; a company that grew +$500K net while losing $2M to churn is running to stand still and will stall the moment new sales slow.

**2. Nimbus grew from $57,000 to $60,000. Why is it misleading to describe this as "5.3% growth" without further comment?**

**Answer:** Because the +$3,000 net figure is the residue of $19,000 in additions and $16,000 in losses. Almost the entire gain came from two customers who were not in the base at the start of the period (Bramble, $8,000 and Foxglove, $5,000), while the existing base actually shrank from $57,000 to $47,000.

**3. If you built a bridge for Nimbus and your buckets summed to $62,000 instead of $60,000, what would that tell you?**

**Answer:** That the bridge is wrong — not that the business changed. A $2,000 discrepancy means a customer was double-counted, miscategorised, or missed. The reconciliation requirement means the bridge cannot silently be inaccurate; it fails loudly.

## 🔗 Continue

**Next:** [[Lesson 2 - The Bridge Vocabulary|Lesson 2 — The Bridge Vocabulary]]

## 🔗 Related Notes

- [[Snowball|Snowball]]
- [[Steps in Building an ARR Snowball|Steps in Building an ARR Snowball]]

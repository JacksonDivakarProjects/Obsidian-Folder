Most bridges that fail to reconcile do not fail because of a maths error. They fail because two people on the same team disagreed about whether a customer who dropped from $15,000 to $9,000 belongs in "churn" or "contraction," and each quietly used their own answer. The bucket definitions look obvious in a slide deck and turn slippery the moment real customer data hits them. This lesson pins each one down precisely, then walks all six Nimbus customers through the decision.

## The classification question

Every customer in a bridge gets sorted by answering two questions, in order:

1. **Did they have ARR at the beginning of the period?**
2. **Do they have ARR at the end of the period?**

That is it. Two yes/no questions produce four combinations, and the ARR-change direction splits one of those combinations further. Everything else is detail.

| BOP ARR | EOP ARR | Bucket |
|---|---|---|
| $0 | > $0 | **New Business** (never a customer before) or **Reactivation** (was a customer once) |
| > $0 | > $0, higher | **Expansion** |
| > $0 | > $0, lower | **Contraction** |
| > $0 | > $0, same | *No bucket — flat* |
| > $0 | $0 | **Churn** |

## The six buckets, precisely

### New Business

ARR from a customer who did not exist on your books before this period — a first-ever contract. The whole EOP amount counts, because none of it existed at BOP.

**Bramble Inc: $0 → $8,000.** Bramble is a first-time Nimbus customer, so the entire $8,000 is New Business. Note that New Business is measured on the *customer*, not the contract — a customer signing their first deal contributes New; that same customer signing a second deal three months later does not.

### Expansion

Additional ARR from a customer who was already paying you at BOP and is now paying you more of the same thing — a seat increase, a tier upgrade, a usage bump. Only the **increment** counts, never the whole balance.

**Cedar Systems: $20,000 → $26,000.** Expansion is **+$6,000**, not $26,000. The original $20,000 was already in the beginning balance; counting it again would double-count it and break reconciliation. This is the single most common beginner error in bridge building: buckets always measure *deltas* for existing customers, and *levels* only for customers entering or leaving.

### Reactivation

ARR from a customer who was on your books at some point in the past, churned, and has now returned. At BOP they were at $0 — just like a new customer — but they are not new, and calling them new would overstate your acquisition engine and understate your win-back motion.

**Foxglove Ltd: $0 → $5,000.** Foxglove churned a year ago and came back this quarter, so $5,000 is Reactivation, not New Business. Distinguishing these two matters operationally: New Business is a sales-acquisition result, Reactivation is usually a win-back or a product-gap-finally-closed result. If you fold reactivations into New, your cost-per-new-customer maths silently degrades, because winning back a lapsed customer typically costs far less than acquiring a stranger.

Reactivation depends entirely on your ability to identify the customer as the *same entity* across their gap. This is a data problem as much as a definitional one, and it is why customer identity keys matter so much in the technical build.

### Contraction

ARR lost from a customer who **is still a customer** but is paying you less — a downgrade, seat reduction, or partial cancellation. Again, only the decrement counts.

**Delta Tech: $15,000 → $9,000.** Contraction is **−$6,000**. Delta is still on the books at $9,000; that surviving $9,000 stays in the ending balance and is not part of the contraction figure.

### Churn

ARR lost from a customer who is **no longer a customer at all** — they went to $0. The whole BOP balance counts as churned.

**Echo Retail: $10,000 → $0.** Churn is **−$10,000**, the entire beginning balance.

### Cross-sell

An existing customer buying a *different* product from you, rather than more of the product they already had. At the customer level this is indistinguishable from Expansion — the customer's total ARR just went up — so it only becomes a separate bucket once you track ARR per customer *per product*. That change of grain is a genuine complication and Lesson 8 handles it. For now, treat expansion as covering "customer spend went up," full stop.

## Contraction vs Churn: the distinction beginners get wrong

These two feel similar — both are red, both reduce ARR — and they are routinely conflated. They should not be. The test is binary and has nothing to do with size:

> **Churn = the relationship ended. Contraction = the relationship shrank.**

Delta Tech lost $6,000, the same dollar amount Cedar gained. Echo Retail lost $10,000. But Delta is still a customer you can call, upsell, and win back with a better product; Echo is gone, and re-acquiring them requires starting over. A quarter with $16,000 of contraction is a pricing, packaging, or value-delivery problem. A quarter with $16,000 of churn is an existential product or support problem. They demand different responses from different teams, which is precisely why the bridge separates them.

A useful edge case: what about a customer who drops from $15,000 to $9,000 and then cancels the remaining $9,000 two months later, all within the same quarter? At period boundaries, the bridge only sees BOP $15,000 and EOP $0 — so the full $15,000 is churn, and the intermediate contraction is invisible. This is an unavoidable consequence of measuring at period endpoints, and it is one reason monthly bridges reveal more than quarterly ones. Shorter periods, finer resolution.

## The customer who does nothing

**Atlas Corp: $12,000 → $12,000.** Atlas appears in no bucket at all.

Beginners often read this as a hole in the model — surely a paying customer should show up *somewhere*? But look at what the bridge is measuring. It explains *change*. Atlas contributed zero change, so it contributes zero to every bucket. Its $12,000 is already sitting in the beginning balance and it is still sitting in the ending balance, untouched and fully accounted for.

If you did put Atlas in a bucket, you would break reconciliation. Adding $12,000 anywhere would take Nimbus's ending total to $72,000, which is simply wrong. Flat customers are the silent majority in most healthy SaaS businesses, and their absence from the buckets is the model working exactly as designed.

## All six customers, sorted

| Customer | BOP | EOP | Δ | Bucket | Amount |
|---|---|---|---|---|---|
| Atlas Corp | $12,000 | $12,000 | $0 | *(flat — none)* | — |
| Cedar Systems | $20,000 | $26,000 | +$6,000 | Expansion | +$6,000 |
| Delta Tech | $15,000 | $9,000 | −$6,000 | Contraction | −$6,000 |
| Echo Retail | $10,000 | $0 | −$10,000 | Churn | −$10,000 |
| Bramble Inc | $0 | $8,000 | +$8,000 | New Business | +$8,000 |
| Foxglove Ltd | $0 | $5,000 | +$5,000 | Reactivation | +$5,000 |

And the reconciliation, which now has a named cause behind every term:

```
$57,000 (Beginning)
 + $8,000 (New — Bramble)
 + $6,000 (Expansion — Cedar)
 + $5,000 (Reactivation — Foxglove)
 − $6,000 (Contraction — Delta)
 − $10,000 (Churn — Echo)
 = $60,000 (Ending) ✓
```

Every customer lands in exactly one bucket or none, no customer lands in two, and the total ties out. Those three properties — **exhaustive, mutually exclusive, reconciling** — are what make this a bridge rather than a list.

## 📌 Key Takeaways

- Classification comes from two questions: did they have ARR at BOP, and do they have ARR at EOP? Everything else follows.
- For customers who existed at BOP, buckets measure the **delta** (Cedar's expansion is $6,000, not $26,000). For customers entering or leaving, buckets measure the **full level**.
- Contraction means the relationship shrank; Churn means it ended. Same colour on the chart, completely different problem to solve.
- Reactivation is separated from New Business because a win-back and a first-time acquisition are different motions with different costs — merging them corrupts your acquisition metrics.
- A flat customer like Atlas belongs in no bucket, and putting it in one would break reconciliation. The bridge explains change, not existence.

## ✅ Check Your Understanding

**1. Cedar Systems went from $20,000 to $26,000. A colleague records $26,000 in the Expansion bucket. What breaks?**

**Answer:** Reconciliation. Cedar's original $20,000 is already inside the $57,000 beginning balance, so counting it again inflates the bridge by $20,000 and the buckets sum to $80,000 instead of $60,000. Expansion records only the increment: +$6,000.

**2. Two customers each cost Nimbus $6,000 this quarter — but one is Contraction and one would be Churn. Why does the bridge insist on separating identical dollar losses?**

**Answer:** Because the dollar amount is not the useful part. Delta contracted by $6,000 and is still a customer you can re-expand; a customer who churned for $6,000 is gone and must be re-acquired from scratch. Contraction usually signals a pricing or value-realisation issue, churn signals a product or support failure, and the two land on different teams' desks.

**3. Foxglove Ltd shows $0 at BOP, just like Bramble Inc. Why aren't both simply "New Business"?**

**Answer:** Because Foxglove has a history — it was a customer, churned, and returned, which makes it Reactivation. Folding it into New Business would overstate the sales team's acquisition performance and hide the win-back motion entirely, distorting cost-per-new-customer since re-acquiring a lapsed customer is typically much cheaper than acquiring a stranger.

## 🔗 Continue

**Next:** [[Lesson 3 - NRR and GRR, the Headline Metrics|Lesson 3 — NRR and GRR, the Headline Metrics]]

## 🔗 Related Notes

- [[Snowball|Snowball]]
- [[Bucket Cascade Logic|Bucket Cascade Logic]]
- [[Steps in Building an ARR Snowball|Steps in Building an ARR Snowball]]

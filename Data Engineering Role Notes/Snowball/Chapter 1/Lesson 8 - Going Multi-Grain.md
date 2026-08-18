The snowball you built in Lesson 7 works. It balances, it splits Nimbus Cloud Storage's $57,000 → $60,000 move into named buckets, and it can slice by Region. For a small company, or for a board slide, that might genuinely be enough. But sit a sales leader down in front of it and they will ask a question it cannot answer — and that question is where the production version of this model begins.

## The question a single-grain snowball can't answer

Recall Cedar Systems from the Nimbus story: BOP $20,000, EOP $26,000, a $6,000 Expansion. At customer grain, that's the whole story. ARR went up, the customer already existed, so the bucket is Expansion.

Now consider two completely different things that could have happened inside that $6,000:

**Scenario A — Cedar upgraded.** They were on Nimbus Backup at the Standard tier for $20,000. They moved to the Pro tier. Same product, more money. Their footprint with Nimbus didn't change shape; it just got more expensive.

**Scenario B — Cedar bought something new.** They kept Nimbus Backup at $20,000, unchanged, and separately signed a $6,000 contract for Nimbus Archive — a product they had never bought before, from a product line they'd never touched.

At customer grain these are *byte-for-byte identical*: BOP $20,000, EOP $26,000, +$6,000, bucket = Expansion. Your Lesson 7 query cannot tell them apart, because it never looks below the customer.

But the business cares enormously about the difference:

- Scenario A is **Expansion** — a deepening of a relationship you already had. Good.
- Scenario B is **Cross-sell** — a customer choosing to buy a *new product* from you for the first time. That's closer in character to a new logo than to a price bump. It means your product line resonated with someone who already knew you, it usually involves a different buyer or budget inside the customer, and it's often the single best leading indicator that an account is going to be sticky.

That distinction drives real decisions. Sales comp plans frequently pay differently on cross-sell than on tier upgrades. Product strategy wants to know whether Nimbus Archive is actually landing with the existing base or just being bundled. Retention modeling treats multi-product customers differently from single-product ones. If your snowball collapses both into "Expansion," you have quietly deleted the answer to all of those questions.

The same blindness runs the other way. Suppose Delta Tech's -$6,000 Contraction was actually them *cancelling an entire product* while keeping two others. That's not a discount negotiation — that's a product failing to hold its ground inside a live account, an early warning that often precedes full churn. Customer grain shows you a shrink. It doesn't show you an amputation.

## The grain hierarchy

Real SaaS billing data is nested. A single customer relationship usually looks like this:

```
Customer  (Cedar Systems)
└── Product  (Nimbus Backup)
    └── Service  (Standard Storage, Snapshot Retention, Priority Support)
└── Product  (Nimbus Archive)
    └── Service  (Cold Tier, Compliance Export)
```

Three nested levels. ARR ultimately lives at the finest level — each service line has a dollar amount — and the levels above it are just sums of what sits underneath.

That means every ARR change can be attributed at whichever level it *actually happened*:

| Level | What a zero-to-positive change means | What a positive-to-zero change means |
|---|---|---|
| Customer | **New Customer** — brand new logo | **Customer Churn** — the whole relationship ended |
| Product | **Cross-sell** — new product line for an existing customer | **Plan/Product Churn** — one product died, customer survives |
| Service | **Service Cross-sell** — new service inside a product they already have | **Service Churn** — one service dropped, product survives |

And changes that aren't zero-crossings at all — where ARR simply moved up or down within things the customer already had — are **Upsell** and **Downsell**.

That's eight buckets, and they map onto the same conceptual families you learned in Lesson 2. New Customer and Customer Churn are the outermost. Cross-sell and Product Churn are the middle. Service Cross-sell, Service Churn, Upsell and Downsell are the finest. Your Lesson 7 model only ever saw the outermost pair plus a lumped "it went up / it went down."

## The cascade: why order is everything

Here's the trap. If you naively evaluate all eight rules independently, rows get claimed multiple times. When Echo Retail churns entirely, *every one of their products* also went to zero, and *every one of their services* also went to zero. A rule-by-rule evaluation would count that same $10,000 as Customer Churn, Product Churn, and Service Churn simultaneously — and your bridge would be off by $20,000.

The production model solves this with a **cascade**: the eight buckets are evaluated in a strict order, coarsest grain first, and each stage explicitly excludes every row that an earlier stage already claimed.

1. **Customer Churn** — customer grain, BOP > 0 and EOP = 0
2. **New Customer** — customer grain, BOP = 0 and EOP > 0 *(excluding anything already claimed as churn)*
3. **Plan/Product Churn** — product grain, product went to zero *(excluding customers already claimed in stages 1–2)*
4. **Cross-sell** — product grain, a whole new product appeared *(excluding stages 1–3)*
5. **Service Cross-sell** — service grain, a new service appeared *(excluding stages 1–4)*
6. **Service Churn** — service grain, a service dropped out *(excluding stages 1–5)*
7. **Downsell** — service grain, remaining ARR shrank *(excluding stages 1–6)*
8. **Upsell** — service grain, remaining ARR grew *(excluding stages 1–7)*

Read that list as a funnel that narrows. Stage 1 asks the biggest question — "is this customer gone entirely?" — and anything that answers yes is removed from consideration forever. Stage 3 then asks a smaller question of a smaller population: "of the customers still standing, did a whole product die?" By the time you reach stage 8, you're asking the finest question of the rows nobody else wanted.

This ordering is what makes the buckets **mutually exclusive and exhaustive**. Every row lands in exactly one bucket, or in none at all if its ARR was flat — Atlas Corp, sitting at $12,000 both periods, is claimed by no stage, which is exactly right. That property is not a happy accident of the SQL; it is the direct consequence of the exclusion filters, and it's the reason the tie-out check in Lesson 10 can be trusted.

## Guarding against phantom signals

One more piece of production hardening. A numeric transition from $0 to a positive number *looks* like a new customer or a cross-sell — but billing data is noisy. A promotional credit can zero out an invoice line for one month. A late-arriving record can make a continuing subscription appear to blink out and return. A billing correction posted in the wrong month can manufacture a churn and a reactivation that never happened.

If you trust the numbers alone, you'll report a churn in March and a reactivation in April for a customer who never went anywhere.

The fix is a **cross-check against an activity-dates table** — the source of truth for when a customer, product, or service actually started and actually ended. Each zero-crossing stage confirms that the corresponding real-world start or end date genuinely falls inside the period before it commits the bucket. If the numbers say "churn" but the contract end date says the subscription is still live, it isn't a churn; it's billing noise, and it gets handled as a magnitude change instead.

Note the asymmetry: stages 1–6 involve zero-crossings and therefore get the date check. Stages 7 and 8 — Downsell and Upsell — are pure magnitude comparisons on things that existed in both periods, so there's no lifecycle event to validate and no date check applies.

## Where to go next

You now have the shape of the production model: three nested grains, eight ordered buckets, exclusion filters that guarantee exclusivity, and date validation that filters out phantoms. What you don't yet have is the stage-by-stage detail — the exact predicate each stage uses, how the exclusion filters are actually expressed, and how the whole thing behaves across a multi-customer worked example.

That's what the reference note is for. Go read [[Bucket Cascade Logic|Bucket Cascade Logic]] end to end before you attempt to build this yourself. It walks all eight stages in order with a full example, and it's the note you'll keep coming back to. This lesson exists so that when you read it, you already know *why* each stage is shaped the way it is.

## 📌 Key Takeaways

- A customer-grain snowball cannot distinguish a tier **upgrade** (Expansion) from a customer buying a **brand-new product** (Cross-sell) — both look like BOP < EOP at customer level, but they're very different business signals.
- Real SaaS data nests as **customer → product → service**, and every ARR change can be attributed at the level where it actually happened.
- The production model uses **8 ordered stages**, evaluated coarsest grain first, where each stage excludes every row already claimed by earlier stages.
- That exclusion ordering is what makes buckets **mutually exclusive and exhaustive** — every row lands in exactly one bucket, or none if flat (like Atlas Corp).
- Zero-crossing stages are **cross-checked against a real activity-dates table** so that billing noise — promos, credits, late-arriving rows — doesn't manufacture phantom new/churn events.

## ✅ Check Your Understanding

**1.** Foxglove Ltd returns with $5,000 of ARR. Under the single-grain Lesson 7 model that's Reactivation. Under the multi-grain cascade, what extra question does the model need answered before it can categorize the row?

**Answer:** Whether Foxglove came back to the *same* product/service they had before, or to a different one — and, crucially, whether their activity-dates record confirms a genuine new start date in this period rather than a billing gap that made an ongoing subscription appear to vanish and return.

**2.** Why can't the eight bucket rules simply be evaluated independently of one another?

**Answer:** Because a coarse-grain event automatically satisfies the finer-grain rules too. When Echo Retail churns entirely, their products and services also all went to zero, so the same $10,000 would be claimed as Customer Churn, Product Churn, and Service Churn at once and the bridge would triple-count. The strict ordering plus exclusion filters ensure each row is claimed only once, by the coarsest stage that applies.

**3.** Stages 7 and 8 (Downsell and Upsell) skip the activity-dates cross-check that stages 1–6 use. Why is that correct rather than an oversight?

**Answer:** Downsell and Upsell only apply to things that existed with non-zero ARR in *both* periods — there's no start or end event to validate. The date check exists specifically to confirm that a $0-to-positive or positive-to-$0 transition reflects a real lifecycle event; a pure magnitude change has no such transition.

## 🔗 Continue

**Next:** [[Lesson 9 - Choosing Your Implementation|Lesson 9 — Choosing Your Implementation]]

## 🔗 Related Notes

- [[Snowball|Snowball]]
- [[Bucket Cascade Logic|Bucket Cascade Logic]] — for the full stage-by-stage reference with a worked multi-customer example

The applied continuation of [[ARR Bridge Course - Chapter 3|Chapter 3]]. Chapters 1 through 3 taught the bridge on SaaS ARR — contracts, subscriptions, a handful of buckets, one company at a time. Chapter 4 is modeled on a real, shipped production pattern, reworked around a fictional company so the lessons stand on their own: **Thornfield Veterinary Group**, a multi-practice veterinary care provider, and it's worth taking seriously precisely because it *isn't* SaaS — the revenue is transactional (vet visits, treatments, medication), not subscription ARR, and the grain is pet × client × practice, not customer × product × service. The bridge methodology — `BOP + buckets = EOP`, reconciling to the last decimal — turns out not to care. That generality is most of the point of this chapter.

Five lessons, each built around one real extension a production system at this scale needs to make to what you already know, illustrated with a running example pet: **Biscuit**, a dog belonging to client Aria Thompson at Riverside Practice. The full de-identified reference implementation lives in [[Production Spark Snowball (Genericized)|Production Spark Snowball (Genericized)]] — every lesson here points to the specific stage it's teaching from, rather than re-pasting the full code.

## The course

1. [[Lesson 1 - The Same Pipeline, Shipped|Lesson 1 — The Same Pipeline, Shipped]] — orientation: how the 8-notebook pipeline maps onto the 5-step mental model and the 8-bucket cascade you already know, and what's genuinely new about the grain.
2. [[Lesson 2 - The Grace Period Problem, Solved|Lesson 2 — The Grace Period Problem, Solved]] — the L12M/L14M dual-window technique, the real fix for the "one quiet month reads as churn-then-new" trade-off flagged (and left unbuilt) in the LTM reference note.
3. [[Lesson 3 - Three Tiers of Gone|Lesson 3 — Three Tiers of "Gone"]] — Lapse, Churn, and Death as three distinct, precedence-ordered categories, extending the date cross-check from a yes/no confirmation into a real classification.
4. [[Lesson 4 - One Table, Two Periods|Lesson 4 — One Table, Two Periods]] — the tall `period_type` reporting pattern, and the point-in-time dimension-join decision (BOP-month, not "current") that the SQL notes' Step 5 never had to make.
5. [[Lesson 5 - Nothing Falls Through|Lesson 5 — Nothing Falls Through]] — the catch-all "balance" bucket and tolerance-banded, ranked-triage reconciliation: two production refinements to the validation checks you already run.

## Why this chapter exists

Chapters 1 through 3 built and validated the methodology on clean, hierarchical, subscription data. This chapter exists to show you the same methodology surviving contact with a business that has none of that: transactional revenue instead of contracts, a three-way non-hierarchical grain, real event-sourced churn reasons instead of an inferred date range, and a scale where "just write a self-join" gives way to real engineering decisions about window functions, table shape, and reconciliation tolerance. If the SQL Pipeline Patterns notes taught you the two situations you'll actually run into, this chapter teaches you what those patterns look like once they've been running in production for a while.

## 🔗 Related Notes
- [[ARR Bridge Course - Chapter 3|Chapter 3 — From Data to Delivery]] — the prerequisite.
- [[LTM Snowball Script (No End Dates, Monthly Grain)|LTM Snowball Script]] — the note whose "grace period" future-extension this chapter's Lesson 2 actually builds.
- [[Contract Dates Snowball Script (With Lifecycle Cross-Check)|Contract Dates Snowball Script]] — the note whose date cross-check this chapter's Lesson 3 extends into a three-way classification.
- [[Snowball|Snowball]] — hub note for the whole area.

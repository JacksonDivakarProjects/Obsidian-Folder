Every note in this vault so far has used a SaaS company as the running example — Nimbus, GreenTide, Corvid Systems, Driftwood Compute. This lesson introduces a different kind of business entirely: **Thornfield Veterinary Group**, a multi-practice veterinary care provider, where "customers" are pets, revenue comes from ad hoc transactions rather than subscriptions, and there's no `end_date` column that means anything close to a "contract." The point of walking through it isn't the vet-care domain — it's proof that the bridge methodology doesn't actually depend on SaaS at all.

## The grain: pet × client × practice

Where the SQL notes reconciled at customer × product × service, this system reconciles at **pet × client × practice**:

- **Pet** (`dim_pet_id`) — the thing actually generating revenue: a specific animal receiving care. Closest analogue to "service" in the SQL curriculum's grain, in that it's the most granular unit money is attributed to.
- **Client** (`dim_client_id`) — the pet's owner, who holds the account. Closest analogue to "customer."
- **Practice** (`dim_practice_id`) — the physical branch location where care happened. There's no clean equivalent in the SQL curriculum's grain — it's closer to a slicing dimension like Region, except here it's built directly into the reconciling grain (every table in this pipeline groups by all three keys together), not attached afterward the way [[Dimensional Snowball Example (SQL)|Dimensional Snowball Example (SQL)]] taught you to attach dimensions.

One more real-world wrinkle worth naming: this grain isn't a clean hierarchy the way customer → product → service is. A pet doesn't strictly belong to one practice forever — Biscuit might get seen at two different Riverside branches over her lifetime. The pipeline doesn't try to force a hierarchy where the data doesn't have one; it just includes all three keys in the grain and lets the numbers fall out where they fall.

## The map: eight stages, five steps you already know

The full reference implementation is [[Production Spark Snowball (Genericized)|Production Spark Snowball (Genericized)]] — eight PySpark stages that map directly onto the 5-step mental model:

```
Stage 1  Standardize + scaffold (forward AND back)   Steps 1-2
Stage 2  Dual rolling windows: L12M and L14M          -- Lesson 2
Stage 3  Lifecycle: join, lapse, churn, death         extends customer_flags / new_customer / churn -- Lesson 3
Stage 4  Expansion and contraction deltas             extends upsell / downsell / cross-sell
Stage 5  Signed dollar buckets                        extends bucket_amounts
Stage 6  One table, two periods (LM + LTM union)      -- Lesson 4
Stage 7  Attach dimensions at BOP, then aggregate     Step 5 -- Lesson 4
Stage 8  Reconciliation, with tolerance and triage    validation -- Lesson 5
```

Stage 1 is the one worth opening first, because it's the exact scaffold pattern from [[LTM Snowball Script (No End Dates, Monthly Grain)|LTM Snowball Script]] — a `dim_calendar` cross-joined against every known grain key, `LEFT JOIN`ed to actual transactions, gaps filled with 0 — just written against a real fact table with real volume. One genuine addition: it scaffolds **forward** too, up to 26 months past a pet's last transaction, not just across the reporting window. That forward buffer is what makes the grace-period technique in the next lesson possible — you can't tell "quiet for one month" apart from "quiet forever" if the table stops existing the month a pet goes quiet.

In a real deployment, Stages 1-7 run in dependency order as one pipeline and Stage 8 (reconciliation) runs separately, on demand — it's a QA check you run after the build to verify the bridge ties out, the same way the SQL notes' validation queries are things you run *after* the main script, not folded into it.

## 📌 Key Takeaways

- The reconciling grain here is pet × client × practice — three keys, not a strict hierarchy, all baked into every `GROUP BY` rather than attached as dimensions afterward.
- Stage 1's scaffold is the same calendar-cross-join-then-fill-with-zero pattern as the LTM SQL note, extended to scaffold forward past each grain's last known activity, not just across the report window.
- The 8-stage pipeline maps directly onto the 5-step mental model: standardize + scaffold → lifecycle + expansion (classify) → deltas (bucket) → report + aggregation (Step 5) → reconciliation (validate). Nothing about the underlying philosophy changed; only the business and the scale did.

## ✅ Check Your Understanding

**1.** Why does Stage 1's scaffold extend 26 months *past* each pet's last transaction, instead of stopping there?

**Answer:** Because "no transaction this month" isn't the same as "gone." Without rows existing for the months right after a pet's last visit, there'd be nothing to compare against to tell a genuinely one-off quiet month apart from a pet that's actually stopped coming in — the forward buffer is what gives the grace-period logic in Lesson 2 something to work with.

**2.** Reconciliation (Stage 8) isn't part of the main dependency chain that produces the reporting output. What does that tell you about how it's meant to be used?

**Answer:** It's a QA check, not a pipeline dependency — you run it after the main build to verify the bridge ties out, the same way the SQL notes' "Output and validation" queries are meant to be run right after the main script, not folded into it.

## 🔗 Continue

[[Lesson 2 - The Grace Period Problem, Solved|Lesson 2 — The Grace Period Problem, Solved]]

## 🔗 Related Notes
- [[LTM Snowball Script (No End Dates, Monthly Grain)|LTM Snowball Script]] — the scaffold pattern Stage 1 builds on.
- [[Steps in Building an ARR Snowball|Steps in Building an ARR Snowball]] — the 5-step mental model this whole pipeline is a worked instance of.
- [[Production Spark Snowball (Genericized)|Production Spark Snowball (Genericized)]] — the full reference implementation.
- [[ARR Bridge Course - Chapter 4|Chapter 4 — Chapter index]]

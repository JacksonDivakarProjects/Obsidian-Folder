Everything in both chapters has been a component. Individually each one was tractable — a vocabulary, a query, a test, a task graph — and each was presented with its answer attached. A capstone's job is to withhold the answer. What follows is a design exercise, and it is deliberately the hardest thing in this course, because production system design does not resolve the way a SQL problem does: there is no single query that is correct and no `SELECT` that either runs or doesn't. There is a brief, a set of constraints, and a set of defensible decisions that a competent reviewer would sign off on. Assembling the pieces yourself is the point.

Take stock of what those pieces are, because the scope is genuinely large now: the bucket vocabulary and the eight-stage multi-grain cascade running customer → product → service with Cross-sell, Plan-Churn, Service-Churn, Upsell and Downsell; a choice between an imperative procedural implementation and a declarative CTE chain; three date-handling scenarios and a set of ARR-normalization conventions for usage-based, multi-year lump-sum and mid-period-prorated contracts; incremental computation via `MERGE` with a reprocessing window sized against late-arriving data; a six-part test suite covering tie-out, uniqueness, mutual exclusivity, cross-grain referential integrity, sign conventions and unexplained movement; and a DAG with a hard test gate, an audited backfill path, idempotent tasks and alerting split between what blocks and what merely flags. Every one of those is a decision point, and a real design document has to actually decide.

## The design brief

> **GreenTide Analytics** is a mid-market SaaS company. Their subscription history covers **40,000 subscription-months across 3,200 customers and 6 products**. Data lands nightly in a **Snowflake** warehouse from two sources: **Stripe** for billing and invoicing, and **Salesforce** for CRM and contract dates. The finance team needs an ARR bridge **refreshed and available by 7am daily**, sliced **by product and by sales region**. The data engineering team is **two people**, both already fluent in dbt and Airflow. Leadership has **been burned once already** — a retention metric presented in a board deck turned out to be wrong, and it was discovered externally.

Before reading on, it is worth actually attempting this yourself: write down what you would build, grain by grain, and then compare. The reasoning below is *a* defensible answer, not *the* answer, and the places where you disagree are the interesting ones.

## Implementation style: declarative

**Decision: a declarative CTE chain, modeled in dbt.**

Recall from Chapter 1 Lesson 9 that the choice between the imperative T-SQL procedure and the portable ANSI CTE chain came down to a small number of factors: debuggability of intermediate state, portability across engines, and the surrounding tooling. Here the surrounding tooling settles it decisively. The team already knows [[DBT|DBT]], and dbt is fundamentally a declarative, CTE-oriented modeling tool — its whole model is "each node is a `SELECT` that materializes as a table or view, and dependencies are inferred from references between them." An imperative stored procedure fits into that world as an opaque blob invoked by a hook: dbt cannot see inside it, cannot infer its lineage, cannot test its intermediate stages, and cannot document it. You would be paying dbt's overhead and getting none of its benefits.

Concretely: the cascade stages become individual models, and dbt's `ref()` graph gives you lineage between them for free. The tie-out test and the rest of the Lesson 6 suite become dbt tests attached to the relevant models, which means they run as part of the build rather than as a separate script somebody remembers to invoke. And Snowflake is the target, so the imperative option's home-turf advantage — T-SQL-specific procedural constructs — isn't available anyway.

The tradeoff you accept: a long CTE chain is harder to step through when a single customer's bucket assignment is wrong, because there's no intermediate temp table to `SELECT` from mid-flight. Mitigate it by materializing the two or three highest-value intermediate stages as real tables rather than inlining everything into one model, and by keeping the grain-key columns present in every stage so you can trace one customer through the whole chain by filtering on the same predicate at each step. See [[ARR Snowball Template (ANSI SQL, Portable)|ARR Snowball Template (ANSI SQL, Portable)]] for the structure this is based on; [[Standardized ARR Snowball Procedure (T-SQL)|Standardized ARR Snowball Procedure (T-SQL)]] remains the better reference for anyone who ends up on SQL Server with heavy procedural requirements.

## Grain: customer and product. Not service. And region is not a grain.

**Decision: build the cascade at customer grain and product grain, stop there, and treat region as a dimension attribute.**

Recall from Chapter 1 Lesson 8 that the cascade runs down three levels, and each level you add unlocks new bucket types — the product grain is where Cross-sell and Plan-Churn become visible, the service grain is where Upsell and Downsell live. More grain is more information, and it is also more compute, more tests, more surface area for the tie-out to break, and more for two people to maintain.

The requirement is "by product and by region." Product is a genuine grain: GreenTide has six products, a single customer can hold several, and movements can occur *within* a customer *across* products — a customer who drops Product A and adds Product B is not churn and not new, it's Plan-Churn plus Cross-sell, and only a product-grain cascade can say so. Getting that right is precisely why the product grain exists.

Service grain is not requested. Nobody has asked for Upsell/Downsell within a product, and building it would mean carrying a third cascade level, a third set of tie-out tests, and a third referential-integrity check for a slice no one has asked to see. That is real compute and real complexity purchased against no requirement. Build customer and product; leave the service-grain design documented as a known extension point so that adding it later is a planned change rather than an archaeological dig.

**Region is the sharper call, and it is not a grain at all.** It's an attribute of the customer, so it attaches to customer-grain rows as a dimension column and you slice by it. What makes a level a *grain* is that entities can move between values of it inside a period and generate movement buckets — that's true of products (cross-sell) and false of regions, because a customer belongs to one region.

Unless it doesn't. Verify this against Salesforce before committing, because if GreenTide has multinational accounts where a single logical customer is split across regional records, or if accounts get reassigned between sales regions mid-quarter during territory planning, region *does* become a grain — and an ugly one. A customer reassigned from EMEA to AMER mid-quarter will, in a naive region-sliced bridge, appear as $X of Churn in EMEA and $X of New in AMER. Total ARR ties out perfectly. Both regional bridges are badly wrong, and the wrongness looks exactly like real business events. If territory reassignment happens at GreenTide, the design needs an explicit region-transfer bucket pair that nets to zero at the total, and finance needs to be told it exists. This is the kind of thing that is nearly impossible to discover after the fact and trivial to handle if you ask the question up front.

## Date handling: two sources that will disagree

**Decision: Salesforce is authoritative for contract validity where a contract record exists; Stripe invoice periods are the fallback and are authoritative for amounts; disagreement between them is a monitored quantity, not something silently resolved.**

Recall from Chapter 1 Lesson 6 that there were three date-handling scenarios, and each one assumed a single source of truth. GreenTide has two, and this is the genuinely hard part of the brief — Chapter 1 never had to deal with it because it only ever had one clean source.

Map the sources onto the scenarios first. Salesforce contract records carry explicit start and end dates, which is the SCD-Type-2-like explicit-validity scenario: a customer is active for a period because a record says so. Stripe invoices are the derived-dates scenario: a customer is active for a period because they were billed for it, and validity is inferred from invoice coverage. Both are legitimate. They will not always agree.

The disagreements are not hypothetical and they are not edge cases:

- Salesforce shows a contract ending 2026-03-31; Stripe shows invoices through 2026-05-31. Either the CRM was updated late (common — closing out a churned account is admin work that slips) or the customer is on a month-to-month tail after contract expiry (also common, and genuinely still revenue).
- Salesforce shows a contract active through 2026-12-31; Stripe shows no invoice after 2026-02. Either billing failed, or the customer is in a payment dispute, or the deal was signed but never provisioned.
- Self-serve customers exist in Stripe with no Salesforce contract record at all.
- A contract was renegotiated mid-term and Salesforce holds two overlapping contract records for the same customer.

A precedence rule handles the routine cases: use Salesforce contract dates when a contract record exists and covers the period; fall back to Stripe invoice-derived dates otherwise; take amounts from Stripe always, because what was actually billed is a fact and what was contracted is an intention. Under this rule the first bullet resolves as churn in Q1 (contract-authoritative) rather than Q2.

But the rule is not the deliverable. Two things matter more:

**The rule must be applied identically to BOP and EOP.** This is where these systems actually break. If BOP is derived one way and EOP another — even by accident, even by an unrelated join hitting a different table — the tie-out fails and the failure is maddening to diagnose because both sides are individually defensible. One reconciliation layer, built once, feeding both sides.

**Disagreement volume must be measured.** Build a reconciliation model that classifies every customer-period into agree / CRM-only / billing-only / conflicting-dates, and count the classes. A steady 3% conflict rate is a data-quality baseline you can live with. That rate jumping to 15% overnight means something broke in a source system, and it will show up here *before* it shows up as a mysterious churn spike in the bridge. Silently coalescing the two sources throws away exactly the signal you'd want at that moment.

## Incremental strategy: don't build it

**Decision: full nightly recompute. No incremental machinery, no reprocessing window on the normal path.**

This is the recommendation most likely to feel wrong, so take the numbers seriously. 40,000 subscription-months is not large. It is not even medium. On Snowflake, an eight-stage cascade over 40,000 rows on an X-Small warehouse runs in seconds — call it under two minutes for the whole model chain even with generous padding. Chapter 2 Lesson 5's incremental machinery exists to solve a problem GreenTide does not have.

And that machinery is not free. The `MERGE` logic plus reprocessing-window selection plus the late-arriving-data caveat is, by a comfortable margin, the most bug-prone part of the pipeline. Its failures are subtle and silent: a window that's too narrow quietly drops corrections that arrived just outside it, and nothing errors. For a two-person team, taking on the single most delicate component in the design in exchange for saving ninety seconds of nightly runtime is a bad trade — it converts a solved problem into an ongoing maintenance liability.

Full recompute also buys real properties for free. It is trivially idempotent, so Lesson 7's retry requirement is satisfied without thinking about it. It is self-healing, so late-arriving data is picked up on the next run with no window logic at all — the class of bug incrementality introduces simply cannot occur. And a backfill is just a normal run, which removes the divergence between the normal path and the backfill path that Lesson 7 warned about.

Write down the trigger for revisiting, because "we'll know when" is not a plan: **when full-refresh runtime exceeds roughly 20% of the SLA budget, or when row counts pass a couple of million, move to incremental.** At GreenTide's growth rate that is years away. Keep the reprocessing-window *concept* in your head for when it arrives, and keep the models written so that dbt's `is_incremental()` can be switched on later without restructuring the cascade — a cheap piece of forward-compatibility that costs nothing today.

The general point generalizes past this brief: knowing the sophisticated technique is not the same as needing it, and part of engineering judgment is recognizing when the simple approach is not a compromise but the correct answer.

## Tests and alerts: shaped by the board-deck incident

**Decision: all six Lesson 6 tests, at every reported grain, all blocking. Anomaly checks flag but do not block. Publish via atomic swap.**

That last line in the brief — leadership was burned by a retention metric that was wrong in a board deck — is not colour. It is a requirement, and it specifically tells you *which direction to err in*.

The failure GreenTide has already experienced is **a wrong number reaching leadership**. The failure they have not experienced is a late number. So the design should bias hard toward holding publication, and that bias should be stated out loud to finance rather than discovered by them. Concretely: all six tests block, and the tie-out and grain-key uniqueness tests run **at customer grain and at product grain independently**, not just on the total. This matters enormously here, because "by product" is one of the two things finance explicitly asked for. A bridge whose total ties out perfectly while the product-grain rows are individually wrong is precisely the shape of the incident they already had — a number that renders fine and is wrong in the slice someone actually reads.

The cross-grain referential integrity test earns its place for the same reason: it's the check that catches product-grain rows that don't roll up to their customer-grain parent, which is the specific way a multi-grain bridge goes wrong while looking right. And the unexplained-movement test is the backstop for everything nobody thought to test — it's the one that catches novel failure modes rather than anticipated ones.

Anomaly checks — GRR quarter-over-quarter drop, churn against trailing average, single-customer churn concentration — flag prominently on the output and do not block. Recall the Lesson 7 argument: a bad quarter that's accurately measured is information leadership needs *fast*, and an automated system that withholds it has confused bad news with bad data.

Two additions the backstory justifies. First, publish via **atomic swap** — build into a staging table, run tests against staging, swap into the reporting table in one transaction — so that consumers can never read a partially written bridge. Second, stamp every published row with the run timestamp and the code version that produced it. When someone asks "which version of the numbers was in the March deck," an organization with this history will ask that question, and being able to answer it precisely is worth the two columns.

The cost of this posture is honest and should be stated in the design doc: raising the blocking bar means GreenTide will occasionally miss 7am. That is the deliberate choice, it is the right one given the history, and finance should agree to it in advance rather than encounter it on a Tuesday.

## DAG, SLA, and the two-person constraint

**Decision: a five-task dbt-on-Airflow DAG starting at 2:00am, with source-freshness sensors, diagnostic failure output, and an SLA-miss callback at 6:00am.**

Work backward from 7am:

- Stripe and Salesforce nightly loads land by roughly 1:30am.
- Start at **2:00am**, gated by **source-freshness sensors** on both feeds. This sensor is not optional — without it, the pipeline will one night succeed beautifully against yesterday's unrefreshed source tables and publish a bridge showing zero movement, which passes every correctness test because it is internally consistent. "The pipeline succeeded on stale inputs" is one of the most common and most embarrassing data incidents there is, and a freshness check is the entire fix.
- Full cascade recompute: ~2 minutes. Test suite: ~3 minutes. Publish and swap: under a minute.
- Green path finishes by roughly **2:10am**.

That leaves nearly five hours of buffer, which sounds absurd until you price what it buys: two full automatic retries after transient failures, plus enough room that a human paged at 3am can diagnose, fix, and rerun — including a backfill if the fix requires reprocessing history — and still land before 7am. The buffer is not slack, it is the human-intervention window, and it is sized by how long it takes a person to wake up and think clearly rather than by how long the query takes.

Set an **SLA-miss callback at 6:00am**: if the publish task hasn't completed by then, alert regardless of whether anything has formally failed. A hung task is an incident in progress and should not wait until 7:01 to become visible.

The **two-person team** shapes the DAG's failure behaviour more than its shape. There is no on-call rotation to absorb ambiguity — the same two people carry it, and an alert that takes forty minutes to interpret at 3am is nearly as bad as no alert. So:

- **One task per logical stage**, so the failed task's name is the first line of diagnosis.
- **Test failures persist their failing rows.** dbt's `store_failures` writes the offending records to a table. "Tie-out failed" tells you nothing at 3am. "Tie-out failed at product grain, 2026-Q2, Product C, discrepancy $4,200, 3 customer IDs attached" tells you where to look before you've finished opening your laptop. This single configuration choice is probably the highest-leverage operational decision in the whole design.
- **Alert payloads carry the grain, period, and magnitude**, not just a task ID and a link.
- **Every task is idempotent**, which full-refresh gives you for free, so retries need no thought.
- **The backfill path is a separate, parameterized, manually triggered DAG** that takes an explicit period range, logs who ran it and why, and passes the same test gate. With full recompute, this is nearly the same code as the nightly run — which is the point. Test it once a quarter so it isn't discovered to be broken on the day it's urgently needed.

The concrete authoring — operators, sensors, retry policy, SLA callbacks — is in [[Data Engineering Role Notes/Airflow Scheduler/Airflow Scheduler|Airflow Scheduler]].

## The self-assessment rubric

This is the portable part. It applies to any ARR bridge system, not just GreenTide's — phrased as the yes/no questions a reviewer would actually ask in a design review. A "no" is not automatically a failure, but it is a thing you should be able to defend rather than a thing you hadn't considered.

1. **Does the design state explicitly which grain(s) it computes at, and why that's sufficient for the actual reporting requirements — not more, not less?** Under-building means a slice finance asked for cannot be produced. Over-building means paying compute and maintenance for detail nobody consumes. And has each reporting dimension been correctly classified as a genuine grain versus a dimension attribute?
2. **Is the BOP-derivation method stated explicitly — LTM versus YTD, and the join and alignment approach — with the gap-handling risk from date-arithmetic shortcuts addressed?** Recall the `DATEADD`/`EOMONTH` sharp edge from Chapter 1 Lesson 7: naive date arithmetic silently produces the wrong prior period at month-end boundaries and around gaps in a customer's history, and the resulting bridge is subtly wrong rather than obviously broken.
3. **Does every non-standard pricing pattern actually present in the source data have a stated, documented normalization convention?** Usage-based, multi-year lump sums, mid-period proration, credits, discounts, currency. "Present in the actual source data" is the operative phrase — this requires looking, not assuming.
4. **Is the incremental reprocessing window sized against the real late-arrival pattern of the source systems, with an explicit answer for what catches whatever the fast path misses?** If the design isn't incremental, is that choice justified by data volume rather than by oversight?
5. **Does the test suite cover tie-out, grain-key uniqueness, bucket mutual exclusivity, cross-grain referential integrity, sign conventions, and unexplained movement — at every grain that gets reported on, not just at the total?** Totals that tie while slices don't is a live and common failure mode.
6. **Is there a clear, written distinction between what blocks publication and what merely flags for review?** Correctness failures block; business anomalies flag. If that line isn't written down, it will be drawn inconsistently under pressure at 3am.
7. **Can every task in the pipeline be safely retried with identical inputs and identical results?** If any task cannot, retries must be disabled for it, and the design must acknowledge that every transient failure now requires a human.
8. **Is there a tested, documented, deliberately-triggered backfill procedure, distinct from the normal incremental path?** Untested backfill code is discovered to be broken at exactly the moment it is most urgently needed.

Add a ninth if you like, and it's arguably the most important one: **does anyone outside the team understand what the numbers mean?** A bridge whose conventions live only in the SQL is a bridge that produces arguments in every finance review.

## 📌 Key Takeaways

- Production design has no single correct answer — it has a brief, a set of constraints, and decisions that must be *justified* against those constraints. Naming the tradeoff you accepted is as much a part of the deliverable as the choice itself.
- Existing team skills are a legitimate and often decisive design input. Recommending dbt-and-declarative for GreenTide is right largely *because* two people already know it; a technically similar team with deep procedural SQL expertise could defend the opposite choice.
- Grain selection is a judgment call in both directions: build the grains the requirements actually need, and be precise about the distinction between a grain (entities move between its values and generate buckets) and a dimension attribute (they don't).
- Multiple source systems will disagree, and the deliverable is not only the precedence rule but the commitment to apply it identically to BOP and EOP and to *measure* the disagreement rate as a leading indicator.
- Sophistication is not the goal. Full recompute beats incremental at 40,000 rows because it removes the most bug-prone component in the system for the cost of ninety seconds — with a written trigger for when that stops being true.
- Organizational history is a design input. "Burned by a wrong metric in a board deck" tells you which direction to err in, and translates directly into blocking tests at every reported grain, an atomic publish, and version-stamped output.

## ✅ Check Your Understanding

**1.** Finance asks to add "by region" to the bridge. Why is region not a fourth level of the cascade, and what would have to be true about GreenTide's data for that answer to change?

**Answer:** Region is an attribute of the customer, not a level entities move within, so it attaches to customer-grain rows as a dimension column and gets sliced on. What makes something a grain is that an entity can move between its values inside a period and generate movement buckets — a customer can hold Product A and Product B and cross-sell between them; a customer belongs to one region. The answer changes if customers actually *do* move between regions: multinational accounts split across regional records, or territory reassignment during sales planning. Then a reassignment surfaces in a region-sliced bridge as churn in the old region and new business in the new one — total ARR ties out perfectly, both regional bridges are badly wrong, and the wrongness is indistinguishable from real business events. That case needs an explicit region-transfer bucket pair netting to zero at the total, and it must be settled by inspecting Salesforce before building, not after someone questions a regional churn number.

**2.** Chapter 2 Lesson 5 taught incremental processing with `MERGE` and reprocessing windows, and the GreenTide design declines to use any of it. Is that a regression?

**Answer:** No — it's the lesson applied rather than ignored. Incrementality is a technique for a specific problem: full recompute taking too long relative to the SLA. GreenTide's 40,000 subscription-months recompute in about two minutes against a five-hour window, so the problem isn't present. Meanwhile the machinery has real costs: `MERGE` plus window-sizing plus late-arrival handling is the most bug-prone part of the design, and its failures are silent rather than loud. For a two-person team that is a bad trade. Full refresh also delivers idempotency and self-healing for late data for free. The mature version of the decision includes the trigger for revisiting it — roughly 20% of SLA budget consumed, or a couple of million rows — and keeping the models structured so incrementality can be switched on without restructuring the cascade.

**3.** Salesforce says a customer's contract ended 2026-03-31. Stripe shows invoices through 2026-05-31. One convention books the churn in Q1, the other in Q2. What is the actual deliverable here?

**Answer:** The precedence rule is the smallest part of it. What matters is: (a) the rule is written down and justified — contract-authoritative-where-present is defensible, billing-authoritative is defensible, guessing per-case is not; (b) it is applied *identically* to BOP and EOP, since applying different resolution logic to the two sides is how the tie-out breaks in a way that's maddening to diagnose because both sides look individually correct; and (c) the disagreement rate is measured and monitored, because a jump from 3% to 15% signals a source-system problem and surfaces here well before it manifests as a mysterious churn spike in the bridge. A convention that finance has agreed to and that is applied consistently is worth far more than the theoretically superior convention applied inconsistently.

## 🎓 Chapter 2 Complete

You started this course asking what "+5.3% ARR growth" actually means. You are ending it with a design review checklist for a production financial reporting system — one that covers grain selection, source-system reconciliation, normalization conventions, incrementality tradeoffs, a six-part correctness suite, blocking-versus-flagging alert policy, idempotent retries, and an audited backfill path. That is the real distance covered, and it is worth being explicit that this is no longer SaaS metric trivia. Multi-grain cascades that tie out exactly, tests that gate publication, alerting calibrated against both fatigue and blindness, and knowing when *not* to reach for the sophisticated solution — these are production data engineering skills. The ARR bridge was the vehicle; the engineering is portable to any pipeline where the number has to be right and someone downstream is waiting for it.

The numbers will change, the sources will change, and the conventions will get renegotiated. The structure won't. [[Snowball|Snowball]] remains the permanent home base for all of it — start there when you come back.

One thing GreenTide's brief handed you that real engagements don't: the requirements. When you're ready, [[ARR Bridge Course - Chapter 3|Chapter 3]] picks up exactly there — profiling a raw dataset nobody has explained to you, scoping the ask yourself instead of receiving it pre-written, and a hands-on capstone that resolves six genuine data traps end to end.

## 🔗 Related Notes

- [[Snowball|Snowball]]
- [[Bucket Cascade Logic|Bucket Cascade Logic]]
- [[Standardized ARR Snowball Procedure (T-SQL)|Standardized ARR Snowball Procedure (T-SQL)]]
- [[ARR Snowball Template (ANSI SQL, Portable)|ARR Snowball Template (ANSI SQL, Portable)]]
- [[DBT|DBT]]
- [[Data Engineering Role Notes/Airflow Scheduler/Airflow Scheduler|Airflow Scheduler]]

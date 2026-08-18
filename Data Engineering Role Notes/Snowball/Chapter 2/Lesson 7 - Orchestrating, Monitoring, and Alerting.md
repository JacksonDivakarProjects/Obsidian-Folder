A pipeline that works when you run it by hand is not a pipeline — it is a script you happen to trust. Chapter 2 Lesson 5 made the snowball incremental, so it no longer has to recompute all of history every night. Chapter 2 Lesson 6 gave it a test suite, so it can tell you when it's wrong. But nothing so far decides *when* it runs, *what order* the dependent steps happen in, *what happens* when a step fails halfway through, or *who gets told* when the tie-out test starts failing at 3am on a Sunday. That missing layer is orchestration, and for a pipeline with this many moving parts — reprocessing-window selection, then the multi-grain cascade, then a six-part test suite, then downstream dashboards reading the output — it needs to be a real DAG, not a single cron entry pointing at one big script.

A DAG is a *directed acyclic graph*: a set of tasks with declared dependencies between them, where the dependencies never loop back on themselves. The word "declared" is doing the work there. In a monolithic script, the ordering is implicit in the line numbers and the failure behaviour is whatever the language does by default. In a DAG, the ordering is a first-class object you can inspect, and the failure behaviour is something you design.

## The DAG shape

For the ARR bridge, the minimum viable task graph looks like this:

```
determine_reprocessing_window
            │
            ▼
    recompute_cascade
            │
            ▼
     run_test_suite  ◄── hard gate
        │        │
   pass │        │ fail
        ▼        ▼
publish_to_    alert_and_halt
reporting_
table
```

Four things are worth noticing about this shape.

**Each stage is its own task, not a step inside one task.** When something breaks, the name of the failed task already tells you which layer failed. "`recompute_cascade` failed" and "`run_test_suite` failed" send you to completely different places — the first is an engineering bug or a source-data problem, the second is a correctness problem in the output. A monolithic script gives you "the ARR job failed" and a stack trace you have to read to learn anything.

**`determine_reprocessing_window` is a task, not a hardcoded constant.** Recall from Lesson 5 that the window is a decision — how far back to reprocess, given how late your source systems tend to be. Making it a task means the chosen window is logged on every run, so when someone asks six months later "did the 2026-02-14 run cover January?", the answer is in the run history rather than in someone's memory.

**`run_test_suite` is a hard gate.** This is the single most important structural decision in the DAG. The publish task does not run unless every test in Lesson 6's suite passes. That means that when the bridge is broken, the reporting table keeps serving *yesterday's correct numbers* rather than *today's wrong ones*, and a human gets woken up. Recall from Lesson 6 the underlying principle: a broken bridge that ships silently is strictly worse than a pipeline that stops and waits. Stale data announces itself — someone notices the "as of" timestamp hasn't moved. Wrong data does not announce itself at all; it goes into a board deck and gets discovered three months later by someone reconciling against the general ledger.

**Publication should be atomic.** `publish_to_reporting_table` should not incrementally mutate the table consumers are querying. Write to a staging table, verify, then swap or `MERGE` in a single transaction. Otherwise a dashboard refreshing at exactly the wrong moment reads a bridge where the buckets have been written but the BOP row hasn't — a state that will never tie out, through no fault of the logic.

## Backfills

A **backfill** is recomputing periods that have already been computed and published. It happens for reasons that have nothing to do with the pipeline being broken:

- The ARR normalization convention changed. Recall from Lesson 4 that decisions like "how do we annualize a usage-based contract" or "how do we recognize a three-year lump sum" are *conventions*, and when finance changes one, every historical period computed under the old convention is now inconsistent with every period computed under the new one. You either backfill or you live with a discontinuity in your own time series.
- A source-system bug was found and fixed retroactively. Salesforce contract end dates were being written with a timezone offset for eight months; the fix corrects them in place; every bridge period touching those contracts is now stale.
- A new grain or new dimension is added and history needs to be populated at that grain.

Backfilling is not "a normal run, but for an older date." It is a fundamentally different operation, and the difference is exactly the reprocessing window from Lesson 5. A normal incremental run deliberately looks back a *short* distance — three months, say — because that's the window that covers the realistic late-arrival pattern and keeps the nightly run fast. A backfill has to deliberately override that: "reprocess all of 2025," or "reprocess every period touching these 400 customer IDs." Running the normal path with a backfill's intent produces a silent partial fix, where 2025 Q4 gets corrected because it happened to fall inside the window and 2025 Q1 doesn't, leaving history *more* inconsistent than before you started.

Three rules follow:

1. **Backfills are manually triggered, never scheduled.** A backfill should never happen because someone fat-fingered a date parameter or because a retry accidentally widened a window. It's a deliberate action with a human behind it.
2. **Backfills are parameterized and audited.** The window is an explicit input, and the run is logged with who triggered it, what range was covered, and why. When the numbers in a board deck change between two versions, "there was a backfill on 2026-04-02 to apply the revised usage-based ARR convention" is the answer to a question that will absolutely be asked.
3. **Backfills run through the same test suite.** A backfill that skips the gate because "it's just history" is how you corrupt periods that nobody is watching closely enough to notice.

## Idempotency as a hard requirement

Every task in this DAG must be **idempotent**: running it twice with identical inputs must produce an identical result, with no accumulating side effects. This is not a nice-to-have. It is a precondition for the orchestrator being allowed to do the thing orchestrators exist to do.

Real orchestration systems retry. Transient failures — a warehouse connection dropped, a credential refreshed mid-query, a node evicted, a query queued past its timeout — are not exceptional events, they are Tuesday. The standard response is an automatic retry, and the value of that automatic retry depends entirely on the task being safe to re-run.

Consider what happens if it isn't. Suppose `recompute_cascade` writes its output with `INSERT`. The first attempt writes Q2 2026's bucket rows, then the connection drops before the task reports success. The orchestrator retries. The second attempt writes Q2 2026's bucket rows *again*. Now Cedar Systems' $6,000 Expansion appears twice, Echo Retail's -$10,000 Churn appears twice, and the bridge shows an EOP of $63,000 against an actual EOP of $60,000. A routine transient failure — the kind that happens dozens of times a year and is supposed to be a non-event — has become a data-corruption incident.

Recall from Lesson 5 that the incremental pipeline was built on `MERGE` rather than `INSERT`, matching on the grain key and the period. That choice is precisely what makes the retry safe: the second attempt matches the rows the first attempt wrote and updates them to the same values. The output after two runs is byte-identical to the output after one. The `MERGE` pattern was introduced as an *incrementality* mechanism, but it earns its keep twice — the second time as the property that lets an orchestrator retry without asking permission.

The same requirement applies to every other task. `determine_reprocessing_window` must not advance a stateful "last processed" pointer as a side effect of being called, or a retry will compute a different window than the original attempt. `publish_to_reporting_table` must overwrite rather than append. If any task in the chain fails this test, the honest thing to do is turn retries off for that task — and then admit that you have a pipeline that requires a human for every transient blip.

## Alerting, and the two failure modes of alerting

Something has to happen when things go wrong. The naive version of this is "alert on failures," and it is insufficient in both directions — it misses things that matter and it fires on things that don't.

**Correctness alerts.** The Lesson 6 test suite failing is unambiguous: the data is wrong. Tie-out broken at some grain, duplicate grain keys, a row that landed in two buckets at once, a product-grain row with no matching customer-grain parent, a Churn row with a positive sign. Each of these means the number is not merely surprising, it is *incorrect*. These page immediately and they block publication.

**Business-anomaly alerts.** There's a second category that hard pass/fail tests will never catch, because it isn't about correctness at all. These are statistical or threshold checks on the bridge's own *output*:

- "GRR dropped more than 10 percentage points quarter over quarter."
- "Churn ARR this period exceeds 2 standard deviations above its trailing 8-quarter average."
- "New ARR fell below 50% of its trailing 4-quarter average."
- "A single customer accounts for more than 25% of total Churn ARR this period."

Run these against Nimbus's Q2 2026 and watch what happens. Churn ARR was $10,000. If the trailing 8-quarter average was around $3,000 with a standard deviation near $2,000, $10,000 sits three-and-a-half standard deviations out and the check fires loudly. GRR at 71.9% against a prior quarter in the high eighties trips the 10-point rule too. And *every single Lesson 6 test passes*. The tie-out is exact: $57,000 + $6,000 − $6,000 − $10,000 + $8,000 + $5,000 = $60,000. Echo Retail really did churn, and the $10,000 really is $10,000. The data is completely correct and it describes an emergency.

That distinction is the whole point. A correctness test asks "is this number what the source data says it should be?" An anomaly check asks "is this number one somebody needs to look at right now?" They are orthogonal, they fail independently, and conflating them is how you build a system that either cries wolf or stays silent through a fire.

**The two failure modes.** Alerting can fail in two opposite ways, and optimising against one pushes you toward the other:

- **Alert fatigue.** Too many low-signal notifications train people to dismiss them without reading. This is not a discipline problem, it's an inevitability — a channel that fires eleven times a week with things that turn out to be fine will be muted within a month, and the twelfth alert, the real one, is muted along with it. Every low-value alert you add degrades every existing alert.
- **Missed incidents.** Thresholds set loose enough to never produce a false positive are also loose enough to sleep through the real thing. A GRR alert that only fires below 40% will never wake you up, which feels great right up until the quarter GRR lands at 62%.

**The practical resolution** is to route the two categories differently rather than to pick a single threshold that satisfies both:

- **Correctness failures page immediately and block publication.** They are rare (in a healthy pipeline, near zero), and every one of them is real. When a tie-out breaks, the number is wrong and shipping it is worse than shipping nothing. High urgency, high blocking, low volume — the profile that keeps a paging channel credible.
- **Business anomalies produce a visible, reviewable flag and do not block the run.** They surface as an annotation on the published output, a row in a review queue, a message in a channel a human reads during the working day. They do *not* halt the pipeline, because the data may be entirely correct — and if Q2's churn genuinely was $10,000, leadership needs to see that *promptly*, not have it withheld by an automated system that mistook bad news for bad data. Blocking publication on an anomaly check inverts the purpose of the metric: the whole reason you built a bridge was to surface exactly this kind of quarter quickly.

Say that plainly, because it's the part people get backwards: correctness failures stop the pipeline, business anomalies stop a *person* — they get someone's attention without getting in the way of the number reaching the people who need it.

## SLAs

A **data SLA** is a commitment about when output will be available and in what condition. "The quarter-end ARR bridge will be available in the reporting table by 9am on the first business day following quarter close." That single sentence is what justifies every design decision above.

Without it, none of this is obviously worth doing. Why bother with incrementality if nobody minds a four-hour run? Why split a working script into five orchestrated tasks? Why tune alert thresholds instead of just eyeballing the output when you get in? The answer in every case is that somebody downstream has planned their morning around the number being there and being right. The SLA is what converts "this pipeline is a bit slow and a bit fragile" from an aesthetic complaint into a commitment you are failing to meet.

Two practical consequences. First, an SLA has a *deadline*, which means your orchestrator should alert on the deadline being at risk, not only on tasks failing. A task that is still running at 8:45am against a 9am SLA is an incident already in progress, even though nothing has technically failed yet — most orchestrators expose this as an SLA-miss callback and it is worth wiring up. Second, the SLA is what tells you how much buffer to leave. Working backward from 9am, through the expected runtime, plus room for one or two automatic retries, plus room for a human to be woken and to intervene, gives you the latest defensible start time. If that arithmetic lands before your source data reliably arrives, you don't have a scheduling problem — you have an SLA you cannot meet, and the honest move is to renegotiate it rather than to schedule optimistically and miss it monthly.

---

This lesson is deliberately about the design decisions rather than the syntax. For the concrete mechanics of authoring these tasks and dependencies — operators, sensors, scheduling semantics, retry configuration, SLA callbacks — see [[Data Engineering Role Notes/Airflow Scheduler/Airflow Scheduler|Airflow Scheduler]]. The DAG shape above translates directly; what doesn't translate is the judgment about where to put the gate and what deserves to wake someone up.

## 📌 Key Takeaways

- The ARR pipeline needs a real DAG, not a cron job: separate tasks for window selection, cascade computation, testing, and publication, so failures are localized and diagnosable by task name alone.
- `run_test_suite` is a **hard gate** before publication — stale-but-correct data beats fresh-but-wrong data, because staleness is visible and wrongness is not.
- **Backfills** are a distinct operation from incremental runs: they deliberately override the reprocessing window, must be manually triggered and audited, and must still pass the test suite.
- **Idempotency** is mandatory, because retries are routine. The `MERGE`-based upsert from Lesson 5 is what makes a retried task safe; an `INSERT`-based pipeline turns a transient blip into duplicated buckets and a broken tie-out.
- Correctness-test failures page and block; business-anomaly checks flag and inform. Conflating them produces either alert fatigue or a system that withholds urgent-but-accurate bad news.
- The **data SLA** is the constraint that makes all of the above worth building, and it should be monitored as a deadline, not just as a pass/fail on the final task.

## ✅ Check Your Understanding

**1.** The test-suite gate means that on a bad night, the reporting table serves yesterday's numbers and the dashboard's "as of" date is stale. Why is that preferable to publishing the freshly computed bridge with a known tie-out failure?

**Answer:** Because the two failure modes have very different detection profiles. Stale data is self-announcing — the "as of" timestamp hasn't moved, and someone notices within a day. A published bridge with a broken tie-out looks completely normal: the numbers render, the chart draws, nothing flags. It flows into decks and forecasts and is typically discovered much later by someone reconciling against another system, at which point every decision made on it is suspect. Blocking converts a silent correctness failure into a loud, obvious freshness failure, which is the trade you want.

**2.** A `recompute_cascade` task fails on a dropped connection, the orchestrator retries automatically, and the bridge now shows an EOP $3,000 higher than reality with every bucket doubled for one customer. What property was violated, and which pattern from earlier in this chapter prevents it?

**Answer:** Idempotency — the task accumulated side effects across runs instead of converging to the same state. The first attempt had already written its rows before failing, and the retry appended a second copy. The fix is Lesson 5's `MERGE`-based upsert, keyed on grain key plus period: the retry matches the previously written rows and updates them to identical values, so one run and two runs produce the same output. This is also why `INSERT`-based loads and automatic retries are fundamentally incompatible.

**3.** Overnight, the anomaly check fires: Churn ARR is 3.5 standard deviations above its trailing 8-quarter average. Every one of the six Lesson 6 tests passes. Should the pipeline halt and withhold publication until someone reviews it?

**Answer:** No. The tests passing means the data is correct — the bridge ties out, buckets are exclusive, signs are right. What the anomaly check has detected is a bad *quarter*, not a bad *number*. Halting would delay genuinely urgent information from reaching the people who need to act on it, which inverts the purpose of the metric. The right response is to publish and simultaneously raise a prominent, reviewable flag on the output so a human sees it early in the day. Blocking is reserved for cases where the number itself cannot be trusted.

## 🔗 Continue

[[Lesson 8 - Capstone, Designing a Production-Grade ARR Bridge System|Lesson 8 — Capstone, Designing a Production-Grade ARR Bridge System]]

## 🔗 Related Notes

- [[Snowball|Snowball]]
- [[Data Engineering Role Notes/Airflow Scheduler/Airflow Scheduler|Airflow Scheduler]]
- [[Bucket Cascade Logic|Bucket Cascade Logic]]

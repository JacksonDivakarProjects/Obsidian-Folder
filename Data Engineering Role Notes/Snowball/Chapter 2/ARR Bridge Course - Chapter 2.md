The advanced continuation of [[ARR Bridge Course|Chapter 1's ARR Bridge Course]]. Chapter 1 built the foundation — vocabulary, metrics, the build process, a working single-grain query, the production-grade multi-grain cascade, and the tie-out discipline. Chapter 2 assumes all of that and pushes further: harder metrics and SQL mechanics first, then a genuine pivot into production data-engineering practice — the kind of pipeline design a real data platform actually needs. Each lesson is deliberately harder than the one before it.

Every lesson continues the same running example from Chapter 1 — **Nimbus Cloud Storage** — extended with new customers and a fuller calendar where a lesson needs it (a second-quarter signup cohort for the cohort-curve lesson, a full four-quarter 2026 calendar for the YTD lesson).

## The course

1. [[Lesson 1 - The Quick Ratio|Lesson 1 — The Quick Ratio]] — the one metric that puts new acquisition and existing-base retention on the same scale.
2. [[Lesson 2 - Cohort Retention Curves|Lesson 2 — Cohort Retention Curves]] — tracking a fixed signup cohort's revenue forward through time instead of taking single-period snapshots.
3. [[Lesson 3 - Deriving the YTD Variant, For Real This Time|Lesson 3 — Deriving the YTD Variant, For Real This Time]] — the full worked mechanics of turning an LTM cascade into a YTD one, and the one complication that isn't a one-line fix.
4. [[Lesson 4 - Taming Non-Standard ARR|Lesson 4 — Taming Non-Standard ARR]] — usage-based pricing, multi-year lump-sum contracts, and mid-period proration.
5. [[Lesson 5 - Making the Snowball Incremental|Lesson 5 — Making the Snowball Incremental]] — reprocessing windows, `MERGE`-based upserts, and the late-arriving-data problem incrementality introduces.
6. [[Lesson 6 - Testing Your Snowball Like a Data Engineer|Lesson 6 — Testing Your Snowball Like a Data Engineer]] — a six-part automated test suite, and why tie-out alone is not enough.
7. [[Lesson 7 - Orchestrating, Monitoring, and Alerting|Lesson 7 — Orchestrating, Monitoring, and Alerting]] — DAG design, backfills, idempotency, and calibrated alerting.
8. [[Lesson 8 - Capstone, Designing a Production-Grade ARR Bridge System|Lesson 8 — Capstone: Designing a Production-Grade ARR Bridge System]] — a full open-ended system-design exercise plus a reusable self-assessment rubric.

## Ready for more?

Once you've finished all eight lessons here, continue to [[ARR Bridge Course - Chapter 3|Chapter 3]] — the applied finale: profiling an unfamiliar real-world dataset, scoping the ask with a stakeholder, building the actual delivery artifact, writing a methodology doc, and a hands-on capstone that resolves six genuine data traps end to end.

## What's genuinely new here

Chapter 1 answered "how do I build a correct ARR bridge." Chapter 2 answers three harder questions in sequence: "how do I get more insight out of the same bridge" (Lessons 1-3), "how do I make the bridge trustworthy when the input data is messy" (Lesson 4), and "how do I make this survive as a real, scheduled, tested, alerting production pipeline that a team relies on" (Lessons 5-8). That last stretch draws directly on this vault's existing [[DBT|DBT]] and [[Data Engineering Role Notes/Airflow Scheduler/Airflow Scheduler|Airflow Scheduler]] material — this is where the ARR bridge stops being a SaaS-metrics topic and becomes a data-engineering one.

## 🔗 Related Notes
- [[ARR Bridge Course|Chapter 1 — ARR Bridge Course]] — the prerequisite foundation.
- [[Snowball|Snowball]] — hub note for the whole area.

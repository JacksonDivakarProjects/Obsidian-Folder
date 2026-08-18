This is the overview and entry point for the **ARR Snowball** area — how to build a revenue bridge (waterfall) that explains, month over month, exactly why Annual Recurring Revenue went up or down: which customers churned, which are new, which expanded, which contracted, and which cross-sold into new products or services.

## What a snowball actually answers

A snowball takes two numbers — ARR at the start of a period (BOP) and ARR at the end of it (EOP) — and explains the gap between them as a sum of named, mutually-exclusive buckets: New, Expansion/Upsell, Contraction/Downsell, Churn, and (in the multi-grain version) Cross-sell. `BOP + (all the buckets) = EOP`, always. That reconciling property is what makes it trustworthy as a report: nothing is double-counted and nothing is left unexplained.

## New here? Take the course

- [[ARR Bridge Course|Chapter 1 — ARR Bridge Course]] — a structured, ten-lesson beginner path that teaches this entire area through one continuous worked example, with self-check questions at the end of every lesson. Start here if you're new to the concept.
- [[ARR Bridge Course - Chapter 2|Chapter 2 — Advanced & Production Practice]] — an eight-lesson continuation that escalates in difficulty: harder metrics and SQL mechanics (Quick Ratio, cohort retention curves, deriving YTD), taming non-standard ARR, then full production data-engineering practice — incremental builds, automated testing, orchestration/alerting, and a capstone system-design exercise.
- [[ARR Bridge Course - Chapter 3|Chapter 3 — From Data to Delivery]] — a five-lesson finale on the part no design exercise covers: profiling an unfamiliar real dataset, scoping the ask with a stakeholder, building the actual delivery artifact, writing a methodology doc, and a hands-on capstone (Corvid Systems) that resolves six genuine data traps end to end.

Come back to the reference notes below once you're building for real.

## Learning path (reference notes)

The same material as the course above, as standalone reference notes without the lesson scaffolding — read in this order if you're skipping the course, or jump straight to whichever one you need:

1. [[Steps in Building an ARR Snowball|Steps in Building an ARR Snowball]] — the 5-step mental model: standardize input dates → snapshot into discrete periods → align period-over-period with a FULL OUTER JOIN → categorize the movement → aggregate (optionally by dimension).
2. [[Deriving Start and End Dates|Deriving Start and End Dates]] — what to do when your raw data doesn't hand you clean Start/End dates (SCD2 history, invoice dates, or month-to-month subscriptions with no end date at all).
3. [[Dimensional Snowball Example (SQL)|Dimensional Snowball Example (SQL)]] — a small, runnable 5-bucket customer-level snowball, and why the dimension join must happen *after* the period alignment.
4. [[Bucket Cascade Logic|Bucket Cascade Logic]] — the harder, production-grade version: an 8-stage cascade that categorizes ARR movement at customer, product, *and* service grain, with a worked example tracing exactly which rows each stage claims.
5. [[Standardized ARR Snowball Procedure (T-SQL)|Standardized ARR Snowball Procedure (T-SQL)]] — the full production stored procedure implementing the 8-stage cascade, cleaned up and genericized so it can be pointed at any data source, not just the one it was originally written for.
6. [[ARR Snowball Template (ANSI SQL, Portable)|ARR Snowball Template (ANSI SQL, Portable)]] — the same 8-stage cascade re-expressed as a single chain of CTEs (no temp tables, no imperative UPDATEs), so it drops into Snowflake, BigQuery, Postgres, or Databricks SQL with only minor date-function swaps.
7. **Pipeline Patterns** (folder) — three full raw-to-bridge builds, for the situations you'll actually run into:
   - [[Contract Dates Snowball Script (With Lifecycle Cross-Check)|Contract Dates Snowball Script (With Lifecycle Cross-Check)]] — real contract start/end dates, from a realistic schema (dim_customer/dim_product/dim_service/dim_calendar + a source_contracts fact table) → standardize → monthly snapshots → lifecycle dates → the 8-stage cascade (including the date cross-check) → dimensions attached last.
   - [[LTM Snowball Script (No End Dates, Monthly Grain)|LTM Snowball Script (No End Dates, Monthly Grain)]] — no contract dates at all, just recurring monthly actuals (usage-based billing) → standardize → scaffold to a dense monthly grain using the same dim_calendar (so silence reads as an explicit $0, not a missing row) → the cascade compares this month to 12-months-back directly → bridge, with no lifecycle-date cross-check since there are no contract dates to check against.
   - [[YTD Snowball Script (No End Dates, Monthly Grain)|YTD Snowball Script (No End Dates, Monthly Grain)]] — a one-step variant of the LTM pattern: identical raw data and scaffold, but BOP is anchored to the close of the prior calendar year instead of rolled 12 months back, so the window widens through the year rather than sliding.
8. [[Original Stored Procedure (As Provided)|Original Stored Procedure (As Provided)]] — the untouched original, kept for provenance/diffing against the standardized version above.

## The two implementations, compared

| | [[Standardized ARR Snowball Procedure (T-SQL)\|Standardized T-SQL Procedure]] | [[ARR Snowball Template (ANSI SQL, Portable)\|ANSI SQL Template]] |
|---|---|---|
| Style | Imperative: temp tables + a sequence of `UPDATE` statements, one bucket at a time | Declarative: one chain of CTEs, no session state |
| Portability | SQL Server (T-SQL) only | Dialect-neutral — runs on most modern warehouses with small syntax swaps |
| Closest to the original | Yes — same structure, cleaned up and parameterized | No — same logic, re-architected |
| Best for | Dropping into an existing SQL Server codebase with minimal risk | A fresh implementation on a modern cloud warehouse, or understanding the logic as pure data flow |

Both implement the identical 8-bucket cascade described in [[Bucket Cascade Logic|Bucket Cascade Logic]] — pick whichever matches your target platform.

## Quick recall

- BOP (Beginning of Period) ARR = last period's EOP ARR for the same grain.
- `GRR (Gross Revenue Retention) = BOP + Churn + Downsell` (only things that shrank or left).
- `NRR (Net Revenue Retention) = GRR + Upsell + Cross-sell` (adds back everything that grew).
- The cascade narrows its population at every stage: customer churn excludes leavers, new-customer excludes newcomers from the "existing base," plan churn/cross-sell narrow to product level, service churn/cross-sell/downsell/upsell narrow to service level. A row can only ever land in exactly one bucket.
- Always join dimension tables (Region, Product Tier, Sales Rep, …) **after** the period-over-period alignment, never before — see [[Dimensional Snowball Example (SQL)|Dimensional Snowball Example (SQL)]] for why.

## 🔗 Related Notes
- [[Practice Notes|Practice Notes]] — a one-line personal reminder of the core BOP/EOP/churn-flag/join sequence.
- [[AI Data Engineer|AI Data Engineer]] — broader study-plan context this sits under.

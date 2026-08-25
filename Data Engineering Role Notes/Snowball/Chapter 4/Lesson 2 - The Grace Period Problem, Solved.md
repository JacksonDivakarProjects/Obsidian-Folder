[[LTM Snowball Script (No End Dates, Monthly Grain)|LTM Snowball Script]] names a real limitation and stops there: a customer quiet for exactly one month reads as churn-then-new-customer, a "blip," and the standard fix — a grace period, don't call it churn until N consecutive months of silence — was described but deliberately left unbuilt. This lesson builds it, using the exact technique Thornfield's pipeline uses: not a running counter, but a **second rolling window**.

## Two windows, same metric

Stage 2 of [[Production Spark Snowball (Genericized)|the reference implementation]] computes the same rolling revenue sum twice, at two different widths:

```python
grain = Window.partitionBy("dim_pet_id", "dim_practice_id", "dim_client_id").orderBy("month_roll")

source_fact = (
    stg_pet_monthly
    .withColumn("l12m_revenue", sf.sum("fee_for_service_revenue").over(grain.rowsBetween(-11, 0)))
    .withColumn("l14m_revenue", sf.sum("fee_for_service_revenue").over(grain.rowsBetween(-13, 0)))
)
```

`l12m_revenue` is the "official" activity window — the one every headline bucket is classified against. `l14m_revenue` is a two-month-wider buffer, computed purely to answer one question: *when `l12m_revenue` hits zero, has this pet shown genuinely no sign of life, or is there still some very recent activity just outside the strict 12-month window?*

That's the grace period. No counter, no procedural "how many months in a row" logic — just a second sum at a wider width, compared against the first.

## Biscuit, month by month

| Month | Visit this month? | `l12m_revenue` | `l14m_revenue` | Reading |
|---|---|---|---|---|
| Aug | Yes | $340 | $340 | Active |
| Sep | No | $0 | $210 | `l12m` says quiet, `l14m` still shows life within the buffer — **partially lapsed** |
| Oct | No | $0 | $0 | Nothing in either window — **fully lapsed** |

Biscuit went quiet in September. Under a naive single-window rule, September would already read as a full churn event. With the L14M buffer, September is flagged `is_partially_lapsed` instead — a softer signal, worth watching but not yet worth calling done — and only in October, once *both* windows agree, does it escalate to `is_fully_lapsed`. Compare this to the "blip" the LTM note warned about: a pet that skips one month and comes straight back the next never reaches `is_fully_lapsed` at all, because the L14M buffer still shows the visit that preceded the gap.

```python
lapse_flags = source_fact.select(
    "*",
    sf.expr("l12m_transactions = 0 AND l14m_transactions = 0").cast("int").alias("is_fully_lapsed"),
    sf.expr("l12m_transactions = 0 AND l14m_transactions > 0").cast("int").alias("is_partially_lapsed"),
)
```

## Why `LAG` is safe here, and wasn't safe on raw data

Stage 4 goes further and uses `LAG` directly to compute month-over-month and year-over-year deltas:

```python
deltas = source_fact.withColumn(
    "lm_l12m_revenue", sf.lag("l12m_revenue", 1).over(grain)
).withColumn(
    "ltm_l12m_revenue", sf.lag("l12m_revenue", 12).over(grain)
)
```

This is exactly the pattern flagged as an anti-pattern for raw, sparse data — `LAG(x, 12)` counts rows, not months, and silently misaligns the moment a partition has a gap. It's correct here for one specific reason: by Stage 4, `source_fact` has already been through Stage 1's scaffold, so every partition is dense — no gaps, one row per month, guaranteed. `LAG(x, 12)` over a genuinely continuous monthly series *is* "12 months back," because row 12 back always is 12 months back once there are no missing rows to throw off the count. The rule from the SQL notes was never "don't use `LAG`" — it was "don't use `LAG` on data that hasn't been scaffolded yet." This pipeline is proof of both halves: dangerous in Stage 1's raw input, exactly right by Stage 4's scaffolded output.

## 📌 Key Takeaways

- The grace period is a second rolling window (L14M), not a counter — comparing two window widths against each other is enough to distinguish "genuinely gone" from "just had one quiet month."
- A pet only reaches `is_fully_lapsed` when *both* windows agree there's no recent activity; a single-month blip shows up as `is_partially_lapsed` at worst, and self-resolves the moment activity resumes.
- `LAG(x, 12)` is safe in Stage 4 specifically because Stage 1's scaffold already made the data dense — the anti-pattern was never about `LAG` itself, only about using it before the data has no gaps left to hide.

## ✅ Check Your Understanding

**1.** A pet has `l12m_transactions = 0` and `l14m_transactions = 0` in the same month. What does that tell you, and what wouldn't a single 12-month window alone have been able to distinguish?

**Answer:** Both the strict window and the wider buffer agree there's no recent activity — this is a genuine, high-confidence lapse, not a blip. A single 12-month window alone can't distinguish this from a pet that had one quiet month and came right back; it would flag both cases identically.

**2.** Why does the fix live as a second window computed once in Stage 2, rather than as a running "months since last seen" counter?

**Answer:** A second rolling sum is a plain, set-based window function — no procedural state, no row-by-row counting, and it composes with everything else in the pipeline the same way L12M already does. A running counter would need its own stateful logic and would need to be threaded through every downstream stage that currently just reads `l12m_transactions`/`l14m_transactions`.

## 🔗 Continue

[[Lesson 3 - Three Tiers of Gone|Lesson 3 — Three Tiers of "Gone"]]

## 🔗 Related Notes
- [[LTM Snowball Script (No End Dates, Monthly Grain)|LTM Snowball Script]] — the note that names the blip problem and leaves the grace period as future work.
- [[Production Spark Snowball (Genericized)|Production Spark Snowball (Genericized)]] — Stages 2 and 4 in full.
- [[ARR Bridge Course - Chapter 4|Chapter 4 — Chapter index]]

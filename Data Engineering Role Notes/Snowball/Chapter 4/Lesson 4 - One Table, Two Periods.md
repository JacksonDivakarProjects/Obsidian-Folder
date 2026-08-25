This lesson covers two reporting-layer decisions Thornfield's pipeline makes that the SQL Pipeline Patterns notes in this vault made differently — not because one is wrong, but because they're optimizing for different consumers.

## Decision 1: tall with a discriminator, instead of two separate tables

[[LTM Snowball Script (No End Dates, Monthly Grain)|LTM Snowball Script]] and [[YTD Snowball Script (No End Dates, Monthly Grain)|YTD Snowball Script]] are two separate files, each producing its own table. That's the right call for a hand-written reference meant to be read start to finish. Stage 6 of Thornfield's pipeline makes a different call: compute the monthly (`LM`) and rolling-12-month (`LTM`) versions of every metric, then stack them into **one table with a `period_type` column**:

```python
rpt_snowball = lm_metrics.withColumn("period_type", sf.lit("LM")).unionByName(
    ltm_metrics.withColumn("period_type", sf.lit("LTM"))
)
```

The trade-off is real in both directions. Tall-with-a-discriminator means Stage 7's dimension-attachment and aggregation logic gets written **once** and applies to both period types — a BI tool downstream just filters or pivots on `period_type` instead of needing two parallel report definitions to maintain. The cost is that every consumer of the table has to remember to filter by `period_type` correctly, or they'll double-count by summing LM and LTM rows together. Two separate tables make that mistake structurally impossible — there's nothing to filter, because there's only one period in the table. Neither shape is "more correct." It's a choice about who's consuming the output: a person reading a reference script benefits from separation; a BI tool with a filter control benefits from one filterable field.

## Decision 2: attach dimensions at BOP, not "now"

Stage 7 joins dimension attributes — `is_insured`, `hub_or_spoke`, `is_partnered` — using a **point-in-time snapshot at the BOP month**, not today's current value:

```python
bop_month_expr = sf.expr("""
    CASE WHEN period_type = 'LM'  THEN add_months(month_roll, -1)
         WHEN period_type = 'LTM' THEN add_months(month_roll, -12)
    END
""")

enriched = rpt_snowball.withColumn("bop_month", bop_month_expr).join(
    dim_practice_monthly,
    (sf.col("dim_practice_id") == dim_practice_monthly.dim_practice_id) &
    (sf.col("bop_month") == dim_practice_monthly.month_roll),
    "left",
)
```

`is_insured` and `is_partnered` are exactly the kind of attribute an SCD2 dimension exists to track — they change over time, and `dim_practice_monthly` is a monthly snapshot of what was true *at that point*, the same underlying idea as the SCD material already in this vault's Data Engineering Concepts notes. The question Stage 7 has to answer is *which* point in time to pull that snapshot from, and it deliberately picks BOP rather than "current" or EOP.

Here's why that matters. Say a practice was **not** partnered at the start of the reporting period and became partnered partway through. If dimension attributes were joined at "current" (today's value, whatever it now is), every historical month for that practice would silently show `is_partnered = 'Partnered'` — including months from before the partnership existed — and every time you re-ran the report, past numbers would keep rewriting themselves as the practice's current status changed. Joining at BOP instead pins the attribute to "what was true when this bridge period *started*," which is what you actually want when the question being asked is "how did already-partnered practices perform over this period" versus "how did practices that partnered mid-period perform" — a real, useful cohort split that a "current value" join would erase.

## 📌 Key Takeaways

- Tall-with-`period_type` (one table, `UNION`ed) trades a small risk of double-counting for writing the reporting/dimension logic once instead of twice — the right call when a BI tool, not a person reading the script top to bottom, is the primary consumer.
- Dimension attributes that change over time are joined at the **BOP month**, not "current," because a current-value join lets past numbers silently rewrite themselves every time the dimension changes — the same problem SCD2 dimensions exist to solve, applied specifically to which snapshot a bridge report should read from.
- Neither reporting-layer choice is universally correct — both are legitimate answers to "who's going to consume this, and how."

## ✅ Check Your Understanding

**1.** A practice becomes newly `is_partnered` in March 2024. Under a "current value" dimension join, what happens to the practice's January and February rows the next time the report refreshes?

**Answer:** They'd silently flip to show `is_partnered = 'Partnered'` too, even though the practice genuinely wasn't partnered in January or February — because "current value" means every historical row inherits whatever is true *right now*, not what was true at the time.

**2.** What's the one risk that a single tall table with `period_type` introduces, that two separate LM/LTM tables structurally can't have?

**Answer:** Double-counting from summing across both period types by accident — `SUM(revenue)` over a table containing both `LM` and `LTM` rows for the same month adds numbers that were never meant to be added together. Two separate tables make this impossible, since there's nothing to filter in the first place.

## 🔗 Continue

[[Lesson 5 - Nothing Falls Through|Lesson 5 — Nothing Falls Through]]

## 🔗 Related Notes
- [[LTM Snowball Script (No End Dates, Monthly Grain)|LTM Snowball Script]] and [[YTD Snowball Script (No End Dates, Monthly Grain)|YTD Snowball Script]] — the two-separate-tables choice this lesson contrasts with.
- [[Dimensional Snowball Example (SQL)|Dimensional Snowball Example (SQL)]] — the grain-safety half of "when to attach dimensions"; this lesson covers the timing half.
- [[Production Spark Snowball (Genericized)|Production Spark Snowball (Genericized)]] — Stages 6 and 7 in full.
- [[ARR Bridge Course - Chapter 4|Chapter 4 — Chapter index]]

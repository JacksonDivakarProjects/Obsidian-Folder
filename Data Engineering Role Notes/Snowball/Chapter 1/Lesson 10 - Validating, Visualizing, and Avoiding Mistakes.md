A snowball query that runs without errors is not a snowball query that's correct. SQL will happily hand you eight beautifully named columns full of numbers that don't reconcile, don't survive contact with a CFO, and quietly misattribute half your churn. This final lesson covers the three things that separate a model you can ship from one that merely executes: the check that proves it's right, the chart that makes it land, and the mistakes that will bite you if nobody warns you first.

## 1. The tie-out check

This is the most important paragraph in the entire course.

**BOP + every bucket must equal EOP. Exactly. Every period. No exceptions.**

For Nimbus:

```
  $57,000   BOP
+  $8,000   New          (Bramble Inc)
+  $6,000   Expansion    (Cedar Systems)
+  $5,000   Reactivation (Foxglove Ltd)
-  $6,000   Contraction  (Delta Tech)
- $10,000   Churn        (Echo Retail)
─────────
  $60,000   EOP  ✓
```

$57,000 + $8,000 + $6,000 + $5,000 − $6,000 − $10,000 = $60,000. It ties. Note that Atlas Corp, flat at $12,000, contributes nothing — flat customers correctly appear in no bucket at all, which is exactly what "mutually exclusive and exhaustive" means in practice.

Run this check as a query, not by hand, and run it for **every period, sliced every way you plan to report**. Not just the total — by region, by segment, by product. A total that ties can hide two dimension slices that are wrong in opposite directions.

```sql
SELECT
    period,
    bop_arr
      + new_customer + cross_sell + service_cross_sell + upsell
      - customer_churn - plan_churn - service_churn - downsell
      AS computed_eop,
    eop_arr,
    ROUND(ABS(computed_eop - eop_arr), 2) AS variance
FROM arr_snowball
WHERE ROUND(ABS(computed_eop - eop_arr), 2) > 0.01;
```

**Zero rows returned means you pass.** Any row is a bug. Not a rounding quirk to explain away — a bug.

The check is so valuable precisely because of *how* it fails. If your bridge doesn't tie, the cause is almost always one of a small number of things:

- **Double-counting** — a row got claimed by two stages, meaning an exclusion filter is wrong or statements ran out of order.
- **Orphaned rows** — a row matched no stage but wasn't actually flat, so its delta vanished.
- **Period misalignment** — your BOP snapshot and EOP snapshot aren't from the boundaries you think they are (Lesson 6 territory).
- **Sign errors** — a loss bucket stored as a positive number and then subtracted twice, or added.
- **Join fan-out** — a dimension join multiplied rows and inflated a bucket.

A failing tie-out doesn't tell you which, but it tells you *that*, immediately and unambiguously — and that's the difference between finding the bug on Tuesday and finding it in a board meeting.

Wire it in as an automated test. If your model runs on a schedule, the tie-out should run right after it and fail loudly. A silent bridge that stops reconciling in month seven is far more damaging than one that never worked, because by then people trust it.

## 2. Visualizing the bridge: the waterfall

ARR bridges are conventionally drawn as a **waterfall chart**, and once you've seen one you'll understand where "snowball" comes from.

The structure:

- **BOP** is a solid bar anchored to zero on the far left — full height, sitting on the baseline.
- **EOP** is a solid bar anchored to zero on the far right — same treatment.
- **Each bucket in between is a floating bar.** It doesn't touch the baseline. It starts where the previous bar ended and extends up (gains) or down (losses).

```
                  New    Exp   React
                 ┌────┐ ┌───┐  ┌───┐
                 │+8k │ │+6k│  │+5k│        Contr  Churn
┌──────┐ ────────┘    └─┘   └──┘   └──┐    ┌────┐          ┌──────┐
│      │                              └────┤-6k │  ┌────┐  │      │
│ BOP  │                                   └────┴──┤-10k├──┤ EOP  │
│ 57k  │                                           └────┘  │ 60k  │
└──────┘                                                   └──────┘
```

Each bar rolls into the position of the next — the running total accumulating and shedding as it travels left to right. That rolling motion is the snowball.

**Color carries the meaning.** Losses in red, gains in green or blue, anchors in a neutral grey or dark tone so they read as structure rather than as another movement. Applied to Nimbus: two red bars (Contraction −$6,000, Churn −$10,000) against three green (New +$8,000, Expansion +$6,000, Reactivation +$5,000), with grey anchors at either end. Under the multi-grain model from Lesson 8 you'd have more bars — Cross-sell and Service Cross-sell on the gain side, Plan Churn and Service Churn on the loss side — but the structure is unchanged.

Why this chart specifically: it makes *composition* immediately visible in a way a table never does. Nimbus's headline is "+$3,000, we grew." The waterfall shows you a wall of red nearly cancelling a wall of green — $19,000 of gross gains against $16,000 of gross losses. Anyone looking at it understands in two seconds that this company is running hard to stand still, which is the same story NRR 82.5% and GRR 71.9% told you numerically back in Lesson 3. The chart just gets there faster, and to an audience that doesn't know what GRR is.

Practical notes: order the bars consistently across every report (all gains, then all losses, is the common convention) so people can compare periods at a glance; label each bar with its value, since floating bars are genuinely hard to read off an axis; and keep the sign convention identical everywhere — if churn is negative in the chart, it should be negative in the table and in the export.

## 3. Common mistakes checklist

These are real failure modes, drawn from issues that have actually surfaced across this vault's Snowball work.

### ❌ Mixing NULL and far-future sentinels for "still active"

Some systems mark an open-ended subscription with `end_date = NULL`. Others use a sentinel like `9999-12-31`. Both are defensible. **Having both in the same table is not.**

You'll write `WHERE end_date IS NULL` to find active rows, and silently drop every row using the sentinel. Or you'll write `WHERE end_date > @period_end` and silently drop every `NULL` (since `NULL > anything` is never true). Either way, active customers vanish from your snapshot and get reported as churn.

**Before you trust any source table, check:**

```sql
SELECT
    COUNT(CASE WHEN end_date IS NULL THEN 1 END)             AS null_convention,
    COUNT(CASE WHEN end_date >= '9000-01-01' THEN 1 END)     AS sentinel_convention
FROM subscriptions;
```

If both counts are non-zero, normalize to one convention in your staging layer before anything else touches the data.

### ❌ Joining dimension tables before the period-over-period alignment

Tempting to join region, segment, and product attributes early so everything's available downstream. It breaks churn attribution.

Dimension tables typically only carry rows for *currently active* entities. Echo Retail churned — they may no longer exist in the customer dimension, or their region may have been blanked out. Join before you align BOP against EOP, and an inner join drops Echo Retail entirely (your $10,000 churn disappears and the bridge stops tying) or a left join gives them a NULL region (your $10,000 churn lands in an "Unknown" bucket and every regional bridge is wrong).

**Align the periods first, produce your BOP/EOP row set, then attach dimensions** — from a slowly-changing or as-of-BOP source, so churned entities keep the attributes they had while they were alive. Churn belongs to the region the customer was in when they left.

### ❌ Using `LAG(x, 12)` for a 12-months-back lookback

For year-over-year comparisons you need the value from 12 calendar months ago. `LAG(arr, 12) OVER (PARTITION BY customer_id ORDER BY month)` looks like it does that. It doesn't.

**`LAG` counts rows, not months.** It returns the value 12 *rows* back in the partition. If the customer has a complete, gapless monthly series, those coincide. The moment a month is missing — a billing gap, a pause, a late-arriving batch, a customer who churned and returned — `LAG(12)` silently reaches back 13, 15, 18 months instead. No error. No warning. Just wrong numbers, and they're wrong in a way that looks entirely plausible.

**Use an explicit date-based join instead:**

```sql
LEFT JOIN monthly_arr AS prior
       ON prior.customer_id = curr.customer_id
      AND prior.month = DATEADD(MONTH, -12, curr.month)
```

Now "12 months ago" means 12 months ago. If there's no row, you get a NULL you can see and handle, rather than a wrong number you can't. Same reasoning applies to `LAG(x, 1)` for month-over-month — build a proper calendar spine and join to it, as Lesson 6 covered.

### ❌ Forgetting the tie-out check entirely

Yes, it's on the list twice. It's the mistake that lets all the others reach production.

A bridge that doesn't reconcile but is never checked *will* be presented to someone who checks it. Finance people add up columns; it's the job. Discovering in a QBR that your numbers don't sum costs far more credibility than the bug itself ever warranted, and it takes months to earn back trust in a model that was once caught wrong.

Automate it. Fail loudly. Never ship a bridge you haven't tied out.

### ❌ A few more worth watching

- **Mid-period signups counted at full annual value.** ARR is a run-rate at a point in time — a customer who signs in mid-month either counts at the snapshot boundary or doesn't, but don't prorate into a metric that isn't prorated.
- **Currency conversion at inconsistent rates.** If BOP uses January's FX rate and EOP uses June's, part of your "expansion" is just the dollar moving. Pick one rate convention and hold it, or split FX out as its own bucket.
- **Test data that's too clean.** If your test set has no churn-and-return, no mid-period product swap, no zero-dollar row, you haven't tested the cascade — you've tested the easy path. Deliberately build the ugly cases.

## 📌 Key Takeaways

- **BOP + all buckets = EOP, exactly.** Run it as an automated query for every period and every dimension slice you report on — a total that ties can hide two slices wrong in opposite directions.
- A failing tie-out points at a short, known list of causes: double-counting, orphaned rows, period misalignment, sign errors, or join fan-out.
- ARR bridges are drawn as **waterfall charts** — solid anchor bars for BOP and EOP, floating bars between them, red for losses and green/blue for gains — and each bar rolling into the next is where "snowball" comes from.
- The visual makes composition obvious: Nimbus's modest +$3,000 is revealed as $19,000 of gains barely outrunning $16,000 of losses, the same story its 82.5% NRR told numerically.
- Guard against the classic failures: **mixed NULL/sentinel** active-flag conventions, **dimension joins before period alignment** (which loses attribution on churned rows), and **`LAG(x, 12)`** (which counts rows, not calendar months, and breaks silently on gaps).

## ✅ Check Your Understanding

**Your snowball ties out perfectly at the company total, but your VP of Sales says the West region numbers look off. Does the passing tie-out mean the regional figures are fine?**

**Answer:** No. A total can tie while individual slices are wrong in offsetting directions — for instance, a churned customer misattributed from West to East leaves the sum unchanged but both regional bridges wrong. Run the tie-out at every grain you report on, not just the top line.

**A customer paused their subscription for two months last year and then resumed. You're computing year-over-year ARR with `LAG(arr, 12)`. What happens, and how would you know?**

**Answer:** The two missing months mean 12 rows back is actually 14 calendar months back, so the comparison silently uses the wrong baseline. You would likely *not* know — there's no error and the number looks plausible. That's what makes it dangerous, and why an explicit date-based join to a calendar spine is the right approach.

**In a Nimbus waterfall chart, why are BOP and EOP drawn as solid bars anchored to zero while New, Churn, and the rest float?**

**Answer:** BOP and EOP are absolute levels — the actual ARR of the business at two points in time, meaningfully measured from zero. The buckets are *changes*, not levels; each is drawn floating from where the running total stood to where it lands, which is what makes the accumulation visible as a single connected path from $57,000 to $60,000.

## 🎓 Course Complete

That's the whole arc. You started with why an ARR bridge matters at all, learned the bucket vocabulary and the retention metrics that sit on top of it, worked through NRR and GRR on a company with a real retention problem, built the five-step process, handled the date and alignment issues that real data throws at you, wrote a working single-grain query, understood the eight-stage multi-grain cascade that production systems use, chose between two complete implementations, and now know how to prove your output is correct and present it so it lands. That's a genuinely non-trivial piece of analytics engineering, and you have both the conceptual model and two working implementation patterns to build from.

Make [[Snowball|Snowball]] your home base from here. It's the hub that links the concept notes, the cascade reference, and both code templates — the place to return to when you're mid-build and need to check a bucket definition or grab a query to adapt. The lessons taught you the reasoning; the reference notes are what you'll actually keep open while you work.

When you're ready to go further, [[ARR Bridge Course - Chapter 2|Chapter 2]] picks up exactly here and pushes into cohort analysis, YTD mechanics, non-standard ARR, and what it takes to run this as a real production pipeline — incremental builds, automated testing, orchestration, and a capstone system-design exercise.

## 🔗 Related Notes

- [[Snowball|Snowball]]

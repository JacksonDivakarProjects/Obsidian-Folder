The ANSI SQL template note in this vault contains a short section that has been quietly deferring work onto you. It says, in effect: *to get a Year-to-Date bridge instead of a trailing-twelve-month one, change the join predicate that aligns BOP to EOP.* One sentence. Technically complete, practically useless — the kind of note you write for yourself when you already understand the thing and are in a hurry. This lesson pays that debt off. We're going to build the YTD variant end to end, on real numbers, and confront the one genuine complication the template note flags but doesn't solve.

## Two Windows, Two Questions

Both LTM and YTD are "how much did this grain change" calculations. What differs is where the BOP side is anchored, and that difference is not cosmetic — it changes the question being answered.

**LTM (last twelve months)** compares each reporting period against the same grain exactly twelve months earlier. The window is a fixed twelve-month width that *slides forward* every period. It answers: **"how much has this grain changed over the trailing year, as of right now?"** In March you're comparing against last March; in April, against last April. The window never gets wider or narrower, it just moves.

**YTD (year to date)** compares each reporting period against a **fixed anchor** — the close of the prior calendar year. That anchor resets every January 1 and then holds still for twelve months while the reporting period marches away from it. It answers: **"how much has this grain changed since the start of this calendar year?"** The window is one month wide in January and twelve months wide in December.

Two properties fall out of that, and both matter operationally.

First, LTM requires **a full extra year of history** you may not have. To report LTM for Q1 2026, you need Q1 2025 actuals in the warehouse. For a young company, or a newly-migrated billing system, or a business line launched last spring, that data may simply not exist — and an LTM bridge over a period where the BOP side is structurally empty will report every single account as New, which is technically what the SQL says and completely wrong as a business statement. YTD has no such requirement: one anchor snapshot at December 31 and you can report the whole following year.

Second, YTD numbers are **not comparable across quarters within a year** in the way LTM numbers are. A Q1 YTD figure covers three months; a Q4 YTD figure covers twelve. Watching a YTD ratio climb through the year is not evidence of accelerating growth — it's the mechanical consequence of a widening window. LTM comparisons are apples-to-apples across periods; YTD comparisons are not, and a chart that plots them as a rising line without labeling the axis is actively misleading.

A report showing both, unlabeled, is one of the most reliable sources of the "why don't these two numbers match" conversation. They don't match because they were never supposed to.

## Nimbus Across Calendar 2026

Here is Nimbus's full 2026, anchored on a December 31, 2025 closing ARR of **$54,000**. Q1 and Q2 EOP figures are the ones you already know from Chapter 1 — the $57,000 → $60,000 bridge is the running example, reproduced here in its natural place in the calendar.

**Q1 2026** — BOP $54,000

| Bucket | Amount |
|---|---|
| New | +$7,000 |
| Expansion | +$4,000 |
| Contraction | -$3,000 |
| Churn | -$5,000 |
| **Net** | **+$3,000** |
| **EOP** | **$57,000** |

**Q2 2026** — BOP $57,000 (the Chapter 1 bridge)

| Bucket | Amount |
|---|---|
| New (Bramble Inc) | +$8,000 |
| Expansion (Cedar Systems) | +$6,000 |
| Reactivation (Foxglove Ltd) | +$5,000 |
| Contraction (Delta Tech) | -$6,000 |
| Churn (Echo Retail) | -$10,000 |
| **Net** | **+$3,000** |
| **EOP** | **$60,000** |

**Q3 2026** — BOP $60,000

| Bucket | Amount |
|---|---|
| New | +$9,000 |
| Expansion | +$5,000 |
| Reactivation | +$2,000 |
| Contraction | -$4,000 |
| Churn | -$7,000 |
| **Net** | **+$5,000** |
| **EOP** | **$65,000** |

**Q4 2026** — BOP $65,000

| Bucket | Amount |
|---|---|
| New | +$11,000 |
| Expansion | +$7,000 |
| Contraction | -$5,000 |
| Churn | -$8,000 |
| **Net** | **+$5,000** |
| **EOP** | **$70,000** |

Every quarter ties: BOP + buckets = EOP, which is the tie-out discipline from Chapter 1's final lesson applied four times in a row.

## The Same Data, Two Ways

Now the actual exercise. Same four quarters, two different BOP alignments.

**Under LTM**, each quarter's BOP is the same grain twelve months back:

| Report period | LTM BOP is... | Available? |
|---|---|---|
| Q1 2026 | Q1 2025 EOP | Not shown here — requires 2025 history |
| Q2 2026 | Q2 2025 EOP | Not shown here |
| Q3 2026 | Q3 2025 EOP | Not shown here |
| Q4 2026 | Q4 2025 EOP | Not shown here |

Note what happened: with only the data on this page, **you cannot compute a single LTM figure.** Not one. Every BOP the LTM predicate reaches for lives in a year we don't have. That's the practical constraint made concrete — LTM is the more analytically comparable metric and it is also the one that will block you for four quarters after any history gap.

**Under YTD**, every quarter's BOP is the same fixed anchor:

| Report period | YTD BOP | EOP | Window width | EOP ÷ $54,000 |
|---|---|---|---|---|
| Q1 2026 | $54,000 | $57,000 | 3 months | **105.6%** |
| Q2 2026 | $54,000 | $60,000 | 6 months | **111.1%** |
| Q3 2026 | $54,000 | $65,000 | 9 months | **120.4%** |
| Q4 2026 | $54,000 | $70,000 | 12 months | **129.6%** |

The BOP column is a constant. That's the whole idea — the anchor holds still and the window stretches.

## What That Ratio Is and Isn't

Those percentages look like NRR. They are not NRR, at least not in the strict sense you learned in Chapter 1, Lesson 3, and conflating them is a genuine reporting error.

Recall the construction: NRR restricts to **the cohort of customers who existed at BOP** and asks what happened to that specific group. New logos signed during the period are excluded by definition. That's why Nimbus's Q1→Q2 NRR came out at 82.5% while total ARR *rose* — the $8,000 from Bramble and the $5,000 from Foxglove sat outside the cohort.

The 129.6% in the table above is computed on **total company EOP over total company BOP**. It includes every logo Nimbus signed during 2026. It's a **YTD growth ratio**, and it will run persistently higher than a YTD NRR at any company doing meaningful new business. To get a true YTD NRR you would have to restrict the numerator to only those customers who carried ARR on December 31, 2025 — the same cohort discipline, just anchored to the year-end date instead of to a rolling twelve-month lookback.

Both are legitimate figures. They answer different questions and they are commonly both called "YTD" in practice, which is how a growth ratio ends up sitting in a retention section of a board deck. **Whichever you're reporting, say which one it is on the artifact itself.** "YTD" is not a specification.

## The Join Predicate, Mechanically

Here is the technical core, and it is genuinely a one-line diff.

Recall the cascade structure from Chapter 1: BOP and EOP are assembled at whatever grain you're reporting, joined together, and then a chain of CTEs classifies each row into buckets by comparing `bop_arr` against `eop_arr`. The LTM alignment looks like this:

```sql
-- LTM: BOP is the same grain exactly 12 months back.
-- The window slides forward with every reporting period.
LEFT JOIN bop
       ON bop.customer_id = eop.customer_id
      AND bop.month_roll  = DATEADD(MONTH, -12, eop.month_roll)
```

The YTD alignment replaces the date arithmetic with a computed constant:

```sql
-- YTD: BOP is the close of the PRIOR calendar year, for every period in the year.
-- The anchor holds still; the window widens as the year progresses.
LEFT JOIN bop
       ON bop.customer_id = eop.customer_id
      AND bop.month_roll  = DATEFROMPARTS(YEAR(eop.month_roll) - 1, 12, 1)
```

`DATEFROMPARTS(YEAR(eop.month_roll) - 1, 12, 1)` reads as: take the reporting month, back up one calendar year, and snap to December. For any 2026 reporting month it returns `2026-12-01`'s predecessor year-end — `2025-12-01` — every single time. Twelve different reporting months, one BOP month.

Now the part worth internalizing, because it explains why this is a one-line change rather than a rewrite. **Every downstream CTE in the cascade consumes exactly two columns: `bop_arr` and `eop_arr`.** The bucket classification logic — `bop_arr = 0 AND eop_arr > 0` is New, `bop_arr > 0 AND eop_arr = 0` is Churn, `eop_arr > bop_arr` is Expansion, and so on — has no knowledge of and no interest in *how* the BOP value was selected. It sees two numbers. The alignment predicate is the only place in the entire pipeline where the question "which prior period are we comparing against?" is answered, so swapping it swaps the semantics of the whole report while leaving several hundred lines of classification logic untouched.

That is the payoff of the declarative CTE-chain style you met in Chapter 1's implementation-styles lesson. The LTM cascade and the YTD cascade are the same program with one predicate changed. If you find yourself editing bucket logic to switch between them, something has leaked that shouldn't have.

## The One Real Complication

There is a trap here, and the ANSI template note flags it without resolving it. It concerns rows that exist on only one side of the join.

Under LTM, a **churn** produces a BOP row with no matching EOP row — the customer had $12,000 twelve months ago and nothing now. When you `FULL OUTER JOIN` or `UNION` the two sides together to catch these, you need a reporting month for that row, and under LTM you can *derive* it: BOP-to-EOP is always exactly a twelve-month hop, so the report month is unambiguously `DATEADD(MONTH, 12, bop.month_roll)`. One BOP month maps to exactly one reporting month. The arithmetic is invertible.

**Under YTD, that inversion is impossible.** The BOP month is `2025-12-01` for *every* reporting month in 2026. Given a BOP-only row anchored at December 2025, "which reporting month does this belong to?" has twelve equally valid answers. A customer who churned in March should appear as a churn in the March, April, May… through December YTD reports — the same BOP row feeding twelve different periods. Trying to reconstruct the report month from `bop.month_roll` doesn't just give the wrong answer, it gives an answer to a question that has no single answer.

The fix is to stop deriving either side from the other and instead **build an explicit month spine** — a driver table of every reportable period, cross-joined to the grain keys, with BOP and EOP both LEFT JOINed onto it:

```sql
WITH month_spine AS (
    -- Every period we intend to report, stated explicitly
    SELECT report_month
    FROM   dim_calendar
    WHERE  report_month >= '2026-01-01'
      AND  report_month <= '2026-12-01'
      AND  is_month_start = 1
),
grain_spine AS (
    -- One row per (period, grain key) -- the skeleton the report must fill
    SELECT s.report_month,
           g.customer_id
    FROM   month_spine s
    CROSS  JOIN dim_customer g
),
aligned AS (
    SELECT sp.report_month,
           sp.customer_id,
           COALESCE(b.arr, 0) AS bop_arr,
           COALESCE(e.arr, 0) AS eop_arr
    FROM   grain_spine sp
    LEFT   JOIN fact_customer_arr b
           ON  b.customer_id = sp.customer_id
           AND b.month_roll  = DATEFROMPARTS(YEAR(sp.report_month) - 1, 12, 1)
    LEFT   JOIN fact_customer_arr e
           ON  e.customer_id = sp.customer_id
           AND e.month_roll  = sp.report_month
)
-- Downstream bucket cascade consumes `aligned` unchanged.
SELECT * FROM aligned;
```

The spine is the authority on which periods exist. Neither BOP nor EOP gets to decide. A December 2025 BOP row now correctly joins to all twelve 2026 reporting months because the spine asked for all twelve, and `COALESCE(..., 0)` gives the churn its zero on the EOP side without any date arithmetic being inverted.

Worth noting: the spine pattern is strictly *safer* under LTM too. The derivable-report-month trick works there, but it's a correctness argument resting on an invariant ("BOP is always exactly twelve months back") that a future requirement change can quietly break. Building the spine costs one extra CTE and removes the invariant from the load-bearing path entirely. If you're writing this fresh, write it with the spine and never think about it again.

## 📌 Key Takeaways

- LTM slides a fixed twelve-month window forward each period ("changed over the trailing year"); YTD anchors BOP to the prior December 31 and widens the window through the year ("changed since January 1"). Both are valid, they answer different questions, and unlabeled side-by-side they generate reconciliation confusion.
- LTM requires a full extra year of history — for Nimbus's 2026 quarters, none of the LTM BOP values exist in the data at all. YTD needs only one anchor snapshot, which makes it the practical choice for young companies or post-migration reporting.
- Nimbus's 2026 YTD ratios against the $54,000 anchor run 105.6%, 111.1%, 120.4%, 129.6% — but the rise is partly the mechanical widening of the window, not purely accelerating growth. YTD figures across quarters are not apples-to-apples the way LTM figures are.
- These are **YTD growth ratios**, not YTD NRR: they include logos signed during 2026. A strict YTD NRR requires restricting to the cohort that existed at the December 31, 2025 anchor, per the cohort discipline from Chapter 1, Lesson 3. State which one a report means.
- Converting an LTM cascade to YTD is a one-line change to the alignment predicate — `DATEADD(MONTH, -12, eop.month_roll)` becomes `DATEFROMPARTS(YEAR(eop.month_roll) - 1, 12, 1)` — because every downstream CTE consumes only `bop_arr` and `eop_arr` and is indifferent to how BOP was chosen.
- The reconstruction trick `bop.month_roll + 12 months` for BOP-only rows breaks under YTD, since one December BOP month feeds up to twelve reporting months. Build an explicit calendar month spine and LEFT JOIN both sides onto it instead.

## ✅ Check Your Understanding

**1.** Nimbus's CFO asks for the Q3 2026 LTM ARR bridge. Using only the data in this lesson, can you produce it? What do you need?

**Answer:** No. The LTM predicate aligns Q3 2026 against **Q3 2025 EOP**, which isn't in the data — the earliest figure available is the December 31, 2025 anchor of $54,000. You'd need the full 2025 monthly ARR history at the reporting grain. Without it, the join produces empty BOP rows and every account classifies as New, which is what the SQL says and not what happened. The YTD bridge, by contrast, is fully computable from what's here: BOP $54,000, EOP $65,000, a ratio of 120.4%.

**2.** You've inherited a working LTM cascade — roughly 300 lines of CTEs handling bucket classification, cross-sell splitting, and multi-grain rollup. How much of it changes to produce a YTD version, and why?

**Answer:** One predicate. Change `AND bop.month_roll = DATEADD(MONTH, -12, eop.month_roll)` to `AND bop.month_roll = DATEFROMPARTS(YEAR(eop.month_roll) - 1, 12, 1)`. Everything downstream reads only `bop_arr` and `eop_arr` and has no dependency on how BOP was selected, so the classification, cross-sell, and rollup logic is untouched. If switching modes requires editing bucket logic, the alignment concern has leaked out of the join and into places it doesn't belong — that's a design problem worth fixing before adding the variant.

**3.** Under LTM, a churned customer's BOP-only row can have its report month reconstructed as `bop.month_roll + 12 months`. Why does this fail under YTD, and what replaces it?

**Answer:** Under LTM the BOP-to-EOP hop is always exactly twelve months, so the mapping is one-to-one and invertible. Under YTD, the single December 2025 BOP row is the anchor for all twelve 2026 reporting months — the mapping is one-to-many, so "which report month does this row belong to?" has twelve valid answers and no derivable one. The fix is an explicit month spine: enumerate the reportable periods in a driver CTE, cross-join to the grain keys, and LEFT JOIN both BOP and EOP onto that skeleton with `COALESCE(..., 0)`. The spine, not the data, decides which periods exist.

## 🔗 Continue

[[Lesson 4 - Taming Non-Standard ARR|Lesson 4 — Taming Non-Standard ARR]]

## 🔗 Related Notes

- [[Snowball|Snowball]]
- [[ARR Snowball Template (ANSI SQL, Portable)|ARR Snowball Template (ANSI SQL, Portable)]]

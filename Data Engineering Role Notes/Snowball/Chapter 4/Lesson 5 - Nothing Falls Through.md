Every SQL Pipeline Patterns note in this vault ends with the same two validation queries: a tie-out check (`bridge_close` must be zero) and an unclaimed-movement check (any row that moved without landing in a bucket). Thornfield's pipeline keeps both ideas and hardens each one for production scale. This is the last lesson in this chapter — the two refinements here are small, but they're the difference between a validation check someone remembers to run and one that can't be skipped.

## Refinement 1: a bucket for "we don't know," built into the pipeline itself

The SQL notes' "Check 2" is a separate query you run after the fact: *did anything move without being claimed by a bucket?* Stage 5 of Thornfield's pipeline turns that check into a first-class output column instead — a catch-all bucket that fires whenever a grain's revenue changed but none of the named buckets explain why:

```python
sf.when(
    (sf.col("lm_revenue_delta") != 0) & (sf.col("gone_reason").isNull()) & (~named_bucket_fired),
    sf.col("lm_revenue_delta")
).otherwise(0).alias("unclassified_balance")
```

This guarantees the tie-out *always* holds, by construction — `unclassified_balance` absorbs whatever the named buckets miss, so `bop_revenue + every bucket, including this one = eop_revenue` is true even on day one, before anyone has thought through every edge case the classification logic needs to cover.

That guarantee comes with a real trade-off, worth stating plainly rather than treating this as a free win: a bucket that silently absorbs anything unclassified can also **hide** genuine gaps in the classification logic. If nobody is watching `unclassified_balance` as its own tracked metric, a real, growing category of unexplained movement can sit there indefinitely, technically reconciled, practically invisible. The fix isn't to remove the bucket — it's the correct safety net — it's to alert on it: if `SUM(unclassified_balance)` starts trending upward, that's a signal the bucket taxonomy needs a new category, not that everything's fine because the bridge still ties out.

## Refinement 2: tolerance, and ranked triage instead of a yes/no answer

The SQL notes check `ROUND(bridge_close, 2) <> 0.00` — rounding to guard against float noise, but still a binary pass/fail. Stage 8 goes one step further:

```python
recon = (
    bucket_amounts.groupBy("dim_pet_id", "month_roll")
    .agg(...)
    .withColumn("reconciliation_diff", sf.col("calculated_eop") - sf.col("actual_eop"))
    .where(sf.abs("reconciliation_diff") > 0.01)
    .orderBy(sf.abs("reconciliation_diff").desc())
    .limit(20)
)
```

Two small changes, both earned by scale. First, `> 0.01` instead of `<> 0` — at real transaction volume, a distributed engine summing millions of small numbers across partitions in a different order each run can produce a residual of a fraction of a cent that isn't a bug, just floating-point arithmetic; an exact-equality check would flag that noise as a failure every single run. Second, `ORDER BY ... DESC LIMIT 20` instead of just returning every mismatched row: when something is actually wrong, a real dataset can produce thousands of small residuals cascading from one root cause. Getting a ranked list of the twenty *worst* offenders means you fix the actual problem first, rather than triaging a wall of symptoms in no particular order.

## 📌 Key Takeaways

- Building an `unclassified_balance` bucket directly into the pipeline turns "Check 2" from a query you might forget to run into a guarantee that holds by construction — but only if someone actually tracks that bucket's total as its own metric, since it can otherwise mask real gaps in the classification logic.
- `ABS(diff) > 0.01` instead of exact equality accounts for real floating-point noise at production scale, the same reasoning behind the SQL notes' `ROUND(..., 2)`, taken one step further.
- Ranking by the size of the mismatch and returning the worst N, rather than every mismatched row, is what actually makes reconciliation failures fixable instead of just detectable.

## ✅ Check Your Understanding

**1.** `unclassified_balance` is nonzero for a growing number of pets each month, but the overall bridge still reconciles perfectly. Is that a sign everything is fine? Why or why not?

**Answer:** No — a perfect reconciliation only means the catch-all bucket is absorbing whatever the named buckets miss, which is exactly what it's designed to do. A growing `unclassified_balance` total is itself the signal that the classification logic has a real, uncovered category that needs its own named bucket; the overall tie-out will keep passing the whole time, which is precisely why this metric needs to be watched on its own rather than inferred from the reconciliation check passing.

**2.** Why does the reconciliation query return the worst 20 mismatches ranked by size, instead of every row where `reconciliation_diff <> 0`?

**Answer:** Because at real volume, one root cause can produce thousands of small downstream residuals — returning every mismatched row buries the actual problem in noise. Ranking by the size of the gap and limiting to the top offenders means you investigate the few rows most likely to reveal the real bug first, instead of triaging symptoms in arbitrary order.

## 🔗 Related Notes
- [[Chapter 2/Lesson 6 - Testing Your Snowball Like a Data Engineer|Chapter 2, Lesson 6]] — the validation practice this lesson's two refinements build on.
- [[Production Spark Snowball (Genericized)|Production Spark Snowball (Genericized)]] — Stages 5 and 8 in full.
- [[ARR Bridge Course - Chapter 4|Chapter 4 — Chapter index]]
- [[Snowball|Snowball]] — hub note for the whole area.

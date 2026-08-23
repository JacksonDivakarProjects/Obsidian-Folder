Here is something true of every query you have written so far in this course, and it has been true so quietly that you probably never noticed. The single-grain walkthrough from Chapter 1 Lesson 7, the eight-stage multi-grain cascade from Lesson 8, the standardized T-SQL procedure, the declarative ANSI CTE chain — every one of them scans **all** of the source history and rebuilds **all** of the output, every single time it runs. For Nimbus's six customers across two quarters, that is instantaneous and completely fine. For a real subscription business with tens of millions of subscription-month rows accumulated across six years of operating history, it is a query that runs for hours, monopolizes warehouse compute that thirty other jobs are also queued for, and — the part that should genuinely bother you — spends the overwhelming majority of that time recomputing periods from 2021 that were finalized, reported to the board, and have not changed since. This lesson is about building the snowball so it only reprocesses what actually changed.

## The Incremental Model

The pattern is standard warehouse vocabulary, and dbt names it directly: an **incremental model**. Instead of dropping and rebuilding the output table, the run does three things.

**(a) Identify the reprocessing window.** Which periods have new or changed source data since the last successful run? Two common approaches:

*Watermark* — track the high-water mark of what you've already processed and take everything newer:

```sql
WHERE src.updated_at > (SELECT MAX(processed_at) FROM arr_snowball_output)
```

*Fixed trailing window* — simpler and far more common in practice: always recompute the last N months and leave everything older alone, on the stated assumption that source data older than N months is final.

```sql
WHERE src.month_roll >= DATEADD(MONTH, -3, DATEFROMPARTS(YEAR(GETDATE()), MONTH(GETDATE()), 1))
```

The trailing window is popular because it is trivially reasonable about and self-healing for ordinary corrections. Note the assumption it makes, though, in plain words: *nothing older than three months will ever change.* Hold onto that. It comes back.

**(b) Recompute the bridge for that window — with enough lookback.**

This is the step people get wrong, and it is worth slowing down for. The instinct is to filter the query the same way you'd filter a report: `WHERE month_roll >= @window_start`. That instinct is wrong, and it is wrong in a way that produces plausible-looking output rather than an error.

Recall from Chapter 1 that every bucket is derived from a **comparison** between BOP and EOP. To compute the bridge for March, you need March's ARR *and* February's ARR. If you filter the input to March-onward, February doesn't exist in the query's world, so every customer's BOP for March is NULL or zero — and every single one of them gets classified as New. Nimbus's Atlas Corp, flat at $12,000 for years, would appear as +$12,000 of New ARR because the query simply cannot see that Atlas existed the month before.

So the rule is: **filter the OUTPUT to the reprocessing window, but extend the INPUT far enough back to correctly derive BOP for the earliest period in that window.** At minimum that's one extra period. For the LTM (last-twelve-months) cascade, it's twelve extra months of lookback, because an LTM figure at any month is itself an aggregation over the prior year.

```sql
DECLARE @window_start DATE = DATEADD(MONTH, -3, @current_month);
DECLARE @input_start  DATE = DATEADD(MONTH, -12, @window_start);  -- lookback for BOP / LTM

-- source CTEs read FROM @input_start
-- final SELECT filters TO   >= @window_start
```

Two different dates, two different jobs. Conflating them is the single most common incremental-snowball bug.

**(c) Merge the recomputed window into the persistent table.** Not truncate-and-reload — a targeted upsert that touches only the rows in the window and leaves every other row byte-for-byte as it was.

## The MERGE

Sketch, not copy-paste — warehouse dialects differ, and some (Redshift, older Postgres) want `DELETE` + `INSERT` instead:

```sql
MERGE INTO arr_snowball_output AS tgt
USING (
    SELECT *
    FROM   recomputed_window          -- only the periods just rebuilt
) AS src
    ON  tgt.month_roll   = src.month_roll
    AND tgt.customer_key = src.customer_key
    AND tgt.product_key  = src.product_key
    AND tgt.service_key  = src.service_key

WHEN MATCHED THEN UPDATE SET
    tgt.bop_arr        = src.bop_arr,
    tgt.new_arr        = src.new_arr,
    tgt.expansion_arr  = src.expansion_arr,
    tgt.contraction_arr= src.contraction_arr,
    tgt.churn_arr      = src.churn_arr,
    tgt.reactivation_arr = src.reactivation_arr,
    tgt.eop_arr        = src.eop_arr,
    tgt.processed_at   = SYSUTCDATETIME()

WHEN NOT MATCHED THEN INSERT (
    month_roll, customer_key, product_key, service_key,
    bop_arr, new_arr, expansion_arr, contraction_arr,
    churn_arr, reactivation_arr, eop_arr, processed_at
)
VALUES (
    src.month_roll, src.customer_key, src.product_key, src.service_key,
    src.bop_arr, src.new_arr, src.expansion_arr, src.contraction_arr,
    src.churn_arr, src.reactivation_arr, src.eop_arr, SYSUTCDATETIME()
);
```

Clause by clause, in plain terms:

- **`USING (...)`** — "here is the only data I am claiming to know anything about right now." Everything outside this subquery is out of scope for this statement and will not be touched. This is the whole point of the pattern.
- **`ON ...`** — the natural key answering "is this the same row?" It must be the **full grain** of the table: `(month_roll, customer_key, product_key, service_key)`. Leave a component out and the MERGE will match multiple target rows to one source row and either error or, worse, update the wrong ones. This key reappears as an explicit test in Lesson 6, and not by coincidence.
- **`WHEN MATCHED THEN UPDATE`** — this period was already in the table and got reprocessed. A late-arriving invoice changed last month's numbers; the recomputed values overwrite the stale ones in place.
- **`WHEN NOT MATCHED THEN INSERT`** — a grain combination appearing for the first time: a genuinely new month, or a new customer/product/service tuple within a reprocessed month.

Notice there is deliberately no `WHEN NOT MATCHED BY SOURCE THEN DELETE`. Adding one would delete every historical row outside the window, since they are all "not matched by source" — the exact catastrophe the incremental pattern exists to avoid. If you *do* need deletes (a customer row that should vanish from a reprocessed month because its underlying record was voided), scope it explicitly to the window:

```sql
WHEN NOT MATCHED BY SOURCE AND tgt.month_roll >= @window_start THEN DELETE
```

That `AND` is load-bearing. Forgetting it is a table-wide data loss event.

## The Problem Incremental Introduces: Late-Arriving Data

Full recompute has one enormous virtue that is easy to undervalue until you give it up: it is **unconditionally correct**. Whatever is in the source right now is what's in the output, no matter when it arrived. Incremental trades that guarantee away for speed, and you need to know precisely what you traded.

Consider the concrete case. Your reprocessing window is "the last 3 months." It is May. A $5,000 invoice **dated March** is entered into the source system today — a billing correction, a delayed integration sync, a rep who finally closed out paperwork.

Walk it through. May's run recomputes March, April, May. March is inside the window, so the invoice lands and March is fixed. Fine.

Now shift it by two months. It is **July** when that March-dated invoice arrives. July's window covers May, June, July. March is *outside* it. The invoice sits in the source table, correct and complete, and no run will ever look at March again. March's bridge is wrong — permanently, silently, with no error, no warning, and a tie-out check that still passes because March's internally-computed BOP + buckets = EOP just fine. It is internally consistent and externally false, which is the worst combination a data quality problem can have.

There is no clean solution, and you should be suspicious of anyone who says otherwise. There are only explicit answers:

- **Detect and widen.** Before each run, scan the source for rows whose *event date* is older than the standard window but whose *load timestamp* is recent. If any exist, extend the window back to cover the oldest of them. This is the most surgical option and it requires your source to carry a trustworthy load timestamp distinct from the business date — which many don't.
- **Periodic full recompute.** Run the fast incremental path nightly and a complete rebuild monthly (or weekly) as a safety net. Cheap to implement, entirely reliable, and it bounds your maximum exposure to "however long since the last full run."
- **Widen the standard window.** Six months instead of three. Reduces the risk without eliminating it, and gives back some of the speed you came for.

Most mature pipelines run the first or third *plus* the second, because belt-and-braces is the honest posture here. State this plainly to yourself and to whoever consumes the table: **incremental models trade completeness guarantees for speed.** A production system needs a documented answer for how it catches what the fast path misses. A fast path and a shrug is not an architecture — it is a future incident with a scheduled date you haven't been told yet.

## Where to Read Next

This entire pattern — full-refresh versus incremental materialization, `merge` and `delete+insert` incremental strategies, `is_incremental()` blocks for conditional window filtering, and configurable lookback — is a first-class, natively supported feature in dbt rather than something you hand-roll. If you are building this for real, read the incremental materialization documentation before writing your own MERGE; see [[DBT|DBT]]. And since the whole motivation here is query cost, the partitioning and clustering material in [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/SQL Optimization Concepts|SQL Optimization Concepts]] is directly complementary — an incremental model whose window predicate can't prune partitions is still scanning the entire table, and you will have done all this work for nothing.

## 📌 Key Takeaways

- Every Chapter 1 query is a full recompute; at real data volumes that means hours of runtime spent rebuilding finalized historical periods that never changed.
- An incremental build identifies a reprocessing window (watermark or fixed trailing months), recomputes only that window, and merges the result into a persistent table.
- Filter the **output** to the window but extend the **input** further back — at least one prior period for BOP, twelve months for the LTM cascade. Filtering the input to the window makes every customer look like New.
- The `MERGE`'s `ON` clause must be the complete grain key; a `WHEN NOT MATCHED BY SOURCE THEN DELETE` without a window predicate will wipe all history outside the window.
- Late-arriving data is the real cost of going incremental: a March invoice arriving in July falls outside a 3-month window and corrupts March forever, while still passing tie-out. Every incremental pipeline needs an explicit catch mechanism — detect-and-widen, a periodic full recompute, or both.

## ✅ Check Your Understanding

**Q1.** An engineer builds an incremental snowball with a 3-month window and filters both the source CTEs and the final output with `WHERE month_roll >= @window_start`. The tie-out check passes. What is wrong, and how does it manifest?

**Answer:** The input filter cuts off the prior period needed to derive BOP, so every customer in the earliest month of the window has no visible prior-period ARR and gets classified as New. Long-standing accounts like Atlas Corp appear as brand-new customers. Tie-out still passes because BOP (zero) + New = EOP is internally consistent — the numbers agree with each other while describing something that never happened. The fix is separate input and output boundaries: read source from `@window_start` minus the required lookback, filter the final SELECT to `@window_start`.

**Q2.** Why must the MERGE `ON` clause include every column of the grain, and what happens at the multi-grain level if `service_key` is omitted?

**Answer:** The `ON` clause defines row identity. With `service_key` omitted, a single source row can match multiple target rows that differ only by service — the engine will either raise a non-deterministic-update error or update rows it shouldn't, collapsing distinct service-grain records into one another. The grain of the `ON` clause must exactly equal the grain of the table, which is why Lesson 6 makes uniqueness on that same key an explicit, permanently scheduled test.

**Q3.** A pipeline runs incrementally every night with a 3-month window and a full recompute on the first of every month. On October 20th, an invoice dated May is loaded. When is it reflected in the bridge, and what would the answer be without the monthly full recompute?

**Answer:** On November 1st, when the full recompute runs and rebuilds all history from source. May is far outside the October nightly window, so no incremental run will pick it up. Without the monthly full recompute, May's bridge stays wrong indefinitely — no error is raised and tie-out continues to pass, so nothing surfaces the problem until someone notices the number disagrees with billing.

## 🔗 Continue

[[Lesson 6 - Testing Your Snowball Like a Data Engineer|Lesson 6 — Testing Your Snowball Like a Data Engineer]]

## 🔗 Related Notes

- [[Snowball|Snowball]]
- [[DBT|DBT]]
- [[Data Engineering Role Notes/SQL/SQL Optimization Concepts/SQL Optimization Concepts|SQL Optimization Concepts]]

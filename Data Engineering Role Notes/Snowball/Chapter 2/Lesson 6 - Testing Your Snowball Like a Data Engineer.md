Most tables in a warehouse are records of things: orders placed, events fired, rows loaded. The ARR bridge is different in kind. It is an **assertion** — a formal claim that these specific buckets, and no others, completely and correctly explain how ARR moved from $57,000 to $60,000. When a fact table is wrong, someone eventually notices a number looks off. When a bridge is wrong, it usually still *looks* right, because the arithmetic still closes; someone reads 82.5% NRR, concludes the expansion motion is underperforming, and reallocates a team's quarter around it. The tie-out check from Chapter 1 Lesson 10 is a genuine and necessary guard, and it is nowhere close to sufficient by itself — a bridge can tie out to the penny and still be wrong in half a dozen structurally different ways. This lesson builds the rest of the suite: a set of automated, scheduled assertions written the way a data engineer writes tests, each one shaped so that **it returns zero rows when the data is correct.**

That convention matters practically. A test that returns rows is a test that hands you the failing records to investigate, and it composes directly with dbt's singular-test pattern, where any query returning rows fails the build.

## Test 1 — Tie-Out at Every Grain You Report On

Chapter 1 Lesson 10 asserted BOP + all buckets = EOP for the total. Generalize it: assert it **separately for every dimension you slice by**.

The reason is arithmetic, not paranoia. A total is a sum, and sums hide compensating errors. If EMEA's bridge overstates Expansion by $40,000 and APAC's understates it by $40,000, the company total ties perfectly. Every regional leader is looking at a wrong number, and the check designed to catch exactly that reports success.

```sql
-- Fails (returns rows) if any month/region bridge does not close
SELECT
    month_roll,
    region,
    SUM(bop_arr) AS bop,
    SUM(new_arr + expansion_arr + contraction_arr
        + churn_arr + reactivation_arr) AS movement,
    SUM(eop_arr) AS eop
FROM      arr_snowball_output   o
JOIN      dim_customer          c ON c.customer_key = o.customer_key
GROUP BY  month_roll, region
HAVING    ABS(SUM(bop_arr)
            + SUM(new_arr + expansion_arr + contraction_arr
                  + churn_arr + reactivation_arr)
            - SUM(eop_arr)) > 0.01;
```

Repeat the same shape by product, by segment, by sales region — every dimension that appears on a dashboard someone makes decisions from. The `0.01` tolerance is for floating-point noise only; if your ARR columns are `DECIMAL`, tighten it to exact equality and keep it there.

**Catches:** aggregation and join-fanout errors that cancel across slices — the failure that a total-level tie-out is structurally blind to.

## Test 2 — Uniqueness of the Grain Key

```sql
-- Fails if any grain combination appears more than once
SELECT    month_roll, customer_key, product_key, service_key, COUNT(*) AS n
FROM      arr_snowball_output
GROUP BY  month_roll, customer_key, product_key, service_key
HAVING    COUNT(*) > 1;
```

A duplicate at the grain doubles that row's contribution to every aggregate built on top of it — and, worse, does so invisibly, because both copies are individually correct.

**Catches:** join fan-out from a dimension table that isn't as unique as you assumed (a slowly-changing dimension joined without a validity-date predicate — recall the SCD2 date handling from Chapter 1 Lesson 6, where a missing `AND @as_of_date BETWEEN valid_from AND valid_to` silently multiplies rows). This is also the exact key the Lesson 5 `MERGE` matches on: if uniqueness breaks here, the MERGE's `ON` clause stops identifying a single row and the incremental build starts behaving non-deterministically. One test, two failure modes.

## Test 3 — Mutual Exclusivity of Bucket Claims

The eight-stage cascade in Chapter 1 Lesson 8 is built on a promise: each stage's exclusion filters guarantee that a row already claimed by an earlier stage cannot be claimed again by a later one. Cross-sell, Plan-Churn, Service-Churn, Upsell, and Downsell all depend on that discipline holding. Nothing in the SQL *enforces* the promise — it emerges from filters that a future refactor can break in a single line.

```sql
-- Fails if any row is claimed by more than one bucket
SELECT *
FROM   arr_snowball_output
WHERE  (CASE WHEN new_arr          <> 0 THEN 1 ELSE 0 END
      + CASE WHEN expansion_arr    <> 0 THEN 1 ELSE 0 END
      + CASE WHEN contraction_arr  <> 0 THEN 1 ELSE 0 END
      + CASE WHEN churn_arr        <> 0 THEN 1 ELSE 0 END
      + CASE WHEN reactivation_arr <> 0 THEN 1 ELSE 0 END
      + CASE WHEN cross_sell_arr   <> 0 THEN 1 ELSE 0 END
      + CASE WHEN upsell_arr       <> 0 THEN 1 ELSE 0 END
      + CASE WHEN downsell_arr     <> 0 THEN 1 ELSE 0 END) > 1;
```

**Catches:** the double-counting failure mode that Lesson 8's exclusion filters exist to prevent. This test is the regression guard on that entire cascade — the thing that turns "we were careful when we wrote it" into "it cannot silently stop being true."

## Test 4 — Referential Integrity Across Grains

The multi-grain build produces customer-, product-, and service-level rows that are supposed to be consistent views of the same reality. Every product-grain row's customer must exist in the customer-grain rollup for that same month; every service-grain row's product must exist in the product-grain rollup.

```sql
-- Fails if a product-grain row has no customer-grain parent that month
SELECT p.month_roll, p.customer_key, p.product_key
FROM   arr_snowball_product  p
LEFT   JOIN arr_snowball_customer c
       ON  c.month_roll   = p.month_roll
       AND c.customer_key = p.customer_key
WHERE  c.customer_key IS NULL;
```

**Catches:** drift between the rollup logic and the detail logic. An orphaned finer-grain row means the two levels no longer agree about who existed when — typically a filter or effective-date predicate applied at one grain and forgotten at another. Customer-level retention will disagree with product-level retention and nobody will be able to say which is right, because both close internally.

## Test 5 — Sign-Convention Sanity

Churn, contraction, downsell, and plan-churn are always negative or zero. New, expansion, upsell, cross-sell, and reactivation are always positive or zero. Nimbus's Echo Retail churn was -$10,000, not +$10,000, and that is not a display preference — the sign is what makes the tie-out addition work.

```sql
-- Fails if any bucket carries the wrong sign
SELECT *
FROM   arr_snowball_output
WHERE  churn_arr         > 0
   OR  contraction_arr   > 0
   OR  downsell_arr      > 0
   OR  new_arr           < 0
   OR  expansion_arr     < 0
   OR  upsell_arr        < 0
   OR  cross_sell_arr    < 0
   OR  reactivation_arr  < 0;
```

**Catches:** a flipped sign from an `ABS()`, a reversed subtraction operand, or a `CASE` branch written backwards. Critically, tie-out alone can miss this: if two sign errors happen to offset, the total still closes while individual buckets — and therefore GRR, NRR, and every churn narrative built on them — are wrong. Recall that Nimbus's GRR of 71.9% is computed purely from the negative buckets; flip one sign and that number becomes fiction while the bridge still balances.

## Test 6 — No Unexplained BOP/EOP Movement

Chapter 1 Lesson 10 used a probe like this while debugging: find rows where ARR moved but nothing explains why. Promote it from a one-off query to a permanent, scheduled test.

```sql
-- Fails if a row's ARR moved without exactly one bucket explaining it
SELECT *
FROM   arr_snowball_output
WHERE  bop_arr <> eop_arr
AND   (CASE WHEN new_arr          <> 0 THEN 1 ELSE 0 END
     + CASE WHEN expansion_arr    <> 0 THEN 1 ELSE 0 END
     + CASE WHEN contraction_arr  <> 0 THEN 1 ELSE 0 END
     + CASE WHEN churn_arr        <> 0 THEN 1 ELSE 0 END
     + CASE WHEN reactivation_arr <> 0 THEN 1 ELSE 0 END) <> 1;
```

**Catches:** a customer whose ARR changed but fell through every classification branch — the `ELSE` nobody wrote. Also catches the inverse: a row whose ARR did move and got two explanations. A customer like Delta Tech dropping $6,000 must have exactly one bucket accounting for it; zero means the movement vanished from the bridge, and two means it was counted twice.

## The Synthesis: These Tests Are Not Independent

This is the part worth sitting with, because it is what separates a checklist from a test suite.

Tests 3 and 6 are what make Test 1 **trustworthy** rather than **coincidentally passing.**

Tie-out is an equality between two sums. Equality between sums is a weak claim — it can hold for correct reasons or by accident. A model that fails Test 3 (a row double-claimed by Expansion and Cross-sell) can still pass Test 1 if a compensating error elsewhere offsets the excess. A model that fails Test 5 (two flipped signs) can pass Test 1 with the errors cancelling exactly. In each case the check you trusted most reports success on data that is wrong, and it does so precisely *because* summation destroys the structure that would have revealed the problem.

Tests 2 through 6 restore that structure. They assert things about **individual rows** — this row is unique, this row has one bucket, this row's signs are right, this row has a parent — and row-level assertions cannot be cancelled out by other rows. Run them together and tie-out stops being a hopeful arithmetic coincidence and becomes a consequence of every row being individually correct.

That is why a mature suite runs the whole set on every build, and why "the bridge ties out" is a reasonable thing to say to a stakeholder and an unreasonable thing to accept as an engineer.

## Operationalizing It

Wire the full suite to run **automatically after every build**, incremental or full — this is exactly what dbt's built-in test framework is designed for, with generic tests (`unique`, `not_null`, `relationships`) covering Tests 2 and 4 declaratively in a `schema.yml`, and singular tests as `.sql` files in `tests/` covering the bespoke logic in Tests 1, 3, 5, and 6. See [[DBT|DBT]] for the setup.

Two operational specifics that matter more than they sound:

**Fail loudly, don't warn.** A test that logs a warning into a run log nobody reads is worse than no test at all, because it manufactures a false sense of coverage. Set severity to error, break the build, and page someone. A pipeline that fails and needs investigation costs an engineer an afternoon. A broken bridge that ships silently costs the business's trust in the number — and once a finance team stops believing the ARR dashboard and rebuilds it in a spreadsheet, you do not get that trust back in one quarter.

**Test the incremental path specifically.** Everything in Lesson 5 introduced new ways to be wrong that a full recompute never had: a window that clips BOP lookback, a MERGE key that isn't the full grain, late-arriving data that never gets picked up. Test 6 catches the first, Test 2 catches the second, and the third is caught by nothing here — which is exactly why Lesson 5 insisted on an explicit periodic full recompute. Tests verify the logic you wrote; only a full rebuild verifies the data you never looked at.

## 📌 Key Takeaways

- The bridge is an assertion, not a record, and it fails in ways that still look arithmetically correct — tie-out alone is necessary and badly insufficient.
- Write every test to return zero rows on success, so a failure hands you the offending records and drops straight into dbt's singular-test pattern.
- Six categories cover the real failure surface: per-slice tie-out, grain uniqueness, bucket mutual exclusivity, cross-grain referential integrity, sign conventions, and unexplained BOP/EOP movement.
- The tests are interdependent — row-level assertions (Tests 2-6) cannot be cancelled out by compensating errors the way a summed tie-out can, which is what makes tie-out trustworthy instead of coincidental.
- Run the suite after every build and fail the pipeline on error rather than logging a warning; a silently broken bridge costs far more in lost trust than a loud failure costs in investigation time.

## ✅ Check Your Understanding

**Q1.** A model ties out perfectly at the company total for every month of the year. Name two distinct ways it could still be seriously wrong, and which test catches each.

**Answer:** (1) Compensating errors across slices — EMEA overstates Expansion by the same amount APAC understates it, so the total closes while both regional views are wrong; caught by Test 1 asserted per-region rather than only at the total. (2) A pair of flipped signs that offset — churn recorded positive and expansion recorded negative for equal amounts, leaving the total unchanged but making GRR and NRR meaningless; caught by Test 5. A third possibility: a duplicated grain row inflating every aggregate uniformly, caught by Test 2.

**Q2.** Why does the lesson claim Tests 3 and 6 are what make Test 1 trustworthy, rather than treating all three as independent checks?

**Answer:** Tie-out compares two sums, and summation destroys row-level structure — so it can pass either because every row is correct or because multiple row-level errors happen to cancel. Tests 3 and 6 assert properties of individual rows (exactly one bucket claim, exactly one explanation for any movement), and row-level assertions can't be offset by other rows. Passing them removes the "coincidence" explanation for a passing tie-out, converting it from weak evidence into a consequence of per-row correctness.

**Q3.** Test 4 fails: a product-grain row exists for customer C in June with no matching customer-grain row. The tie-out test passes at both grains. What class of bug is this and why doesn't tie-out see it?

**Answer:** The rollup logic and the detail logic have drifted — a filter or effective-date predicate applied at one grain and not the other, so the two levels disagree about who existed in June. Tie-out doesn't see it because each grain's bridge closes correctly *within itself*: the customer-grain table is internally consistent about a world where C doesn't exist, and the product-grain table is internally consistent about a world where C does. Only a cross-grain assertion compares the two worlds, which is precisely why the multi-grain cascade needs tests that span grains rather than tests that validate each grain in isolation.

## 🔗 Continue

[[Lesson 7 - Orchestrating, Monitoring, and Alerting|Lesson 7 — Orchestrating, Monitoring, and Alerting]]

## 🔗 Related Notes

- [[Snowball|Snowball]]
- [[DBT|DBT]]

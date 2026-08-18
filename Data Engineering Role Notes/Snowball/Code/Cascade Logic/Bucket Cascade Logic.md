# Bucket Cascade Logic

## The core idea

Every ARR movement bucket answers a different question, but they all draw from the same pool of rows. If two buckets could claim the same row, the waterfall would double-count and the bridge would not tie out. The cascade prevents that by processing buckets in a fixed order, where each stage excludes the rows already claimed by every stage before it.

Two things change as you move down the cascade:

- **The audience narrows.** Customer churn removes everyone who left entirely. New customer removes that cohort. Everything after operates on the "stable base" — customers who existed in both periods.
- **The grain deepens.** Customer → customer + product → customer + product + service. This ordering is forced by logic, not convenience: you cannot meaningfully ask "did this customer drop this service?" until you have already ruled out "did the entire customer leave?" and "is this a brand-new customer?"

The result is a set of buckets that are **mutually exclusive and exhaustive**. Every service-month row with an ARR change lands in exactly one bucket — or in none, if its ARR was flat. The `WHERE` filters are what guarantee it.

## The running example

Three customers illustrate the whole cascade. All comparisons are LTM (last twelve months): the current period versus the same period twelve months prior.

| Customer | 12 months ago | Today |
|---|---|---|
| **A** | Product P1 (Services X, Y), Product P2 (Service Z) | Product P1 (Services X, Y) only |
| **B** | Service W, $500 ARR | $0 — completely gone |
| **C** | $0 | $200 — brand new |

Watching each stage claim and skip these rows is the fastest way to internalize the filters.

---

## Stage 1: Customer churn

| Aspect | Detail |
|---|---|
| **Grain** | `(month, customer)` |
| **ARR logic** | `customer_prev_ltm = SUM(bop_arr, all services)`<br>`customer_ltm = SUM(eop_arr, all services WHERE customer_churn = 0)` |
| **Flag** | `customer_churn_flag = 'Yes' WHEN customer_ltm = 0 AND customer_prev_ltm ≠ 0` |
| **Date check** | Activity dates table: did `customer_enddt` fall outside the LTM window? If so, confirm churn. |
| **WHERE filter** | None — this is the first stage |
| **Bucket value** | `-bop_arr` (negative of what they had) |
| **Example** | Customer B: $500 twelve months ago, $0 now → flag = 'Yes' → bucket = **-$500** |

**Rows claimed:** Customer B's single service (W) is claimed by churn. Customer A's three services (X, Y, Z) are not claimed — A still has revenue. Customer C's services are not claimed; new customers are handled in the next stage.

## Stage 2: New customer

| Aspect | Detail |
|---|---|
| **Grain** | `(month, customer)` |
| **ARR logic** | Sum at customer level, **only** `WHERE customer_churn = 0` |
| **Flag** | `new_cust_flag = 'Yes' WHEN customer_ltm ≠ 0 AND customer_prev_ltm = 0` |
| **Date check** | Activity dates table: did `customer_startdt` fall within the LTM window? If so, confirm new. |
| **WHERE filter** | `WHERE t.customer_churn = 0` |
| **Bucket value** | `eop_arr` (their current revenue) |
| **Example** | Customer C: $0 twelve months ago, $200 now → flag = 'Yes' → bucket = **+$200** |

**Rows claimed:** Customer B's service (W) was already claimed by churn and is skipped. Customer A's services (X, Y, Z) are skipped — A existed before. Customer C's services are claimed by new customer.

## Stage 3: Plan churn

| Aspect | Detail |
|---|---|
| **Grain** | `(month, customer, product)` |
| **ARR logic** | `plan_prev_ltm = SUM(bop_arr WHERE customer_churn = 0 AND new_customer = 0)` |
| **Flag** | `planchurn_flag = 'Yes' WHEN plan_ltm = 0 AND plan_prev_ltm ≠ 0` |
| **Date check** | Activity dates table: did `plan_enddt` fall within the LTM window? |
| **WHERE filter** | `WHERE t.customer_churn = 0 AND t.new_customer = 0` |
| **Bucket value** | `-bop_arr` (negative of what they had under this product) |
| **Example** | Customer A's Product P2: $150 (Service Z) twelve months ago, $0 today → flag = 'Yes' → bucket = **-$150** |

**Rows claimed:** Customer B is skipped (already a churned customer). Customer C is skipped (new customer). Customer A / Product P2 / Service Z is claimed by plan churn — A dropped P2 entirely. Customer A / Product P1 / Services X and Y remain available to later stages.

Note the distinction from Stage 1: the customer is still alive and paying, so this is not customer churn. An entire product line went to zero within a surviving account.

## Stage 4: Cross-sell

| Aspect | Detail |
|---|---|
| **Grain** | `(month, customer, product)` |
| **ARR logic** | `plan_prev_ltm = SUM(bop_arr WHERE customer_churn = 0 AND new_customer = 0 AND planchurn = 0)` |
| **Flag** | `cross_sell_flag = 'Yes' WHEN plan_ltm ≠ 0 AND plan_prev_ltm = 0` |
| **Date check** | Activity dates table: did `plan_startdt` fall within the LTM window? |
| **WHERE filter** | `WHERE t.customer_churn = 0 AND t.new_customer = 0 AND t.planchurn = 0` |
| **Bucket value** | `eop_arr` (current spend on this new product) |
| **Example** | Customer A adds Product P3 with Service U at $200 → flag = 'Yes' → bucket = **+$200** |

**Rows claimed:** Customers B and C are skipped (churn or new customer). Customer A / P2 / Z was already claimed by plan churn. Customer A / P1 / X and Y are skipped — existing products, no product-level change. Customer A / P3 / U is claimed by cross-sell, if such a row exists.

Cross-sell is the mirror image of plan churn: an existing customer picks up a product they did not have before.

## Stage 5: Service cross-sell

| Aspect | Detail |
|---|---|
| **Grain** | `(month, customer, product, service)` |
| **ARR logic** | Sum at service level, excluding all prior buckets |
| **Flag** | `service_cross_sell_flag = 'Yes' WHEN service_ltm ≠ 0 AND service_prev_ltm = 0` |
| **Date check** | Activity dates table: did `service_startdt` fall within the LTM window? |
| **WHERE filter** | `WHERE t.customer_churn = 0 AND t.new_customer = 0 AND t.planchurn = 0 AND t.cross_sell = 0` |
| **Bucket value** | `eop_arr` (current service ARR) |
| **Example** | Customer A adds a new service variant Y′ under existing Product P1 → flag = 'Yes' → bucket = **+new spend** |

This is the first stage at the service grain. Because Stage 4 already claimed rows belonging to entirely new products, anything landing here is a new service inside a product the customer already owned.

## Stage 6: Service churn

| Aspect | Detail |
|---|---|
| **Grain** | `(month, customer, product, service)` |
| **ARR logic** | Sum at service level, excluding all prior buckets |
| **Flag** | `servicechurn_flag = 'Yes' WHEN service_ltm = 0 AND service_prev_ltm ≠ 0` |
| **Date check** | Activity dates table: did `service_enddt` fall within the LTM window? |
| **WHERE filter** | `WHERE t.customer_churn = 0 AND t.new_customer = 0 AND t.planchurn = 0 AND t.cross_sell = 0 AND t.service_cross_sell = 0` |
| **Bucket value** | `-bop_arr` (negative of what they had for this service) |
| **Example** | Customer A drops Service Y but keeps Product P1 and Service X → bucket = **-(Service Y BoP)** |

A service goes to zero while its parent product survives. Had the whole product gone to zero, Stage 3 would already have claimed the row.

## Stages 7 and 8: Downsell and Upsell

| Aspect | Downsell | Upsell |
|---|---|---|
| **Grain** | `(month, customer, product, service)` | `(month, customer, product, service)` |
| **Flag** | `downsell_flag = 'Yes' WHEN service_ltm < service_prev_ltm` | `upsell_flag = 'Yes' WHEN service_ltm > service_prev_ltm` |
| **Date check** | None — a value comparison, not a lifecycle event | None |
| **WHERE filter** | Excludes all six prior buckets | Excludes all six prior buckets **and** downsell |
| **Bucket value** | `eop_arr - bop_arr` (negative delta) | `eop_arr - bop_arr` (positive delta) |
| **Example** | Service X for A: $100 → $60 = **-$40** | Service Y for A: $80 → $120 = **+$40** |

These two are the catch-all. Every row surviving to this point has non-zero ARR in both periods — nothing started, nothing ended — so the only remaining question is whether the number went up or down. Rows where the value is unchanged fall through both flags and contribute nothing, which is correct: flat revenue is not a movement.

---

## Why the order cannot be shuffled arbitrarily

Some of the ordering is mandatory and some is convention:

- **Customer churn must precede new customer.** Both operate at customer grain in opposite directions, but churn has to run first so dead customers are excluded before the model looks for arrivals.
- **Customer-grain stages must precede product-grain stages, which must precede service-grain stages.** Otherwise a churned customer's individual services would be counted as service churn, splitting one event across several buckets.
- **Plan churn before service churn is convention, not necessity.** The reverse order could be made to tie out, but "drop a whole plan, then drop services within a surviving plan" matches how the business narrates the loss.
- **Downsell and upsell must come last.** They are magnitude comparisons with no lifecycle test, so they would happily claim rows that belong to a real start or end event if given the chance.

## Why this structure matters for NRR

The cascade exists because every component of NRR and GRR must be measured on the same population — existing customers who did not churn — but at different logical levels: product, service, and magnitude. The `WHERE` filters are what enforce that shared population.

The two roll-ups are:

```
GRR = BoP + customer_churn + planchurn + servicechurn + downsell
NRR = GRR + upsell + cross_sell + service_cross_sell
```

(The loss components are already signed negative, so these are additions.)

In plain terms:

- **GRR** answers "if we sold nothing more to anyone, what share of revenue would we retain?" — BoP minus everything that left or shrank.
- **NRR** is GRR plus everything that grew or was added.

### Worked example

Starting from BoP = $1,000:

| Component | Value | Running total |
|---|---|---|
| BoP | $1,000 | $1,000 |
| Churn | -$200 | $800 |
| Downsell | -$50 | **$750 → GRR = 75%** |
| Upsell | +$100 | $850 |
| Cross-sell | +$150 | **$1,000 → NRR = 100%** |

GRR is capped at 100% by construction — it contains only losses. NRR is not, which is why NRR above 100% is the standard signal that expansion is outrunning attrition.

## 🔗 Related Notes
- [[Steps in Building an ARR Snowball|Steps in Building an ARR Snowball]] — the simpler 5-step, single-grain version of this same categorization idea.
- [[Standardized ARR Snowball Procedure (T-SQL)|Standardized ARR Snowball Procedure (T-SQL)]] — the full production implementation of this exact cascade.
- [[ARR Snowball Template (ANSI SQL, Portable)|ARR Snowball Template (ANSI SQL, Portable)]] — the same cascade as a portable CTE chain.
- [[Snowball|Snowball]] — hub note for this area.

# Bucket breakdown: grain, logic, and cascade

## The complete cascade with example row flows

Imagine a customer base with:

- **Customer A**: Has Product P1 (Services X, Y) and Product P2 (Service Z) in month -12. Today has P1 (Services X, Y) only.
- **Customer B**: Completely left (had $500 ARR 12 months ago, $0 today).
- **Customer C**: Brand new this month (had $0 12 months ago, now has $200).

### Stage 1: Customer churn

|Aspect|Detail|
|---|---|
|**Grain**|`(month, customer)`|
|**ARR logic**|`customer_prev_ltm = SUM(bop_arr all services)` `customer_ltm = SUM(eop_arr all services, WHERE customer_churn=0)`|
|**Flag**|`customer_churn_flag = 'Yes' WHEN customer_ltm=0 AND customer_prev_ltm≠0`|
|**Date check**|Activity dates table: did `customer_enddt` fall outside the LTM window? If so, confirm churn.|
|**WHERE filter**|None (first stage)|
|**Bucket value**|`-bop_arr` (negative of what they had)|
|**Example**|Customer B: $500 12mo ago, $0 now → flag='Yes' → bucket = -$500|

**Rows claimed:**

- Customer B's 1 service (W): claimed by churn
- Customer A's 3 services (X, Y, Z): not claimed (still has revenue)
- Customer C's services: not claimed (new customer is handled separately)

---

### Stage 2: New customer

|Aspect|Detail|
|---|---|
|**Grain**|`(month, customer)`|
|**ARR logic**|Sum at customer level, **but only WHERE customer_churn=0**|
|**Flag**|`new_cust_flag = 'Yes' WHEN customer_ltm≠0 AND customer_prev_ltm=0`|
|**Date check**|Activity dates table: did `customer_startdt` fall within the LTM window? If so, confirm new.|
|**WHERE filter**|`WHERE t.customer_churn = 0` (excludes churned rows)|
|**Bucket value**|`eop_arr` (their current revenue)|
|**Example**|Customer C: $0 12mo ago, $200 now → flag='Yes' → bucket = $200|

**Rows claimed:**

- Customer B's service (W): already claimed by churn, skipped
- Customer A's services (X, Y, Z): skip (customer existed before)
- Customer C's services: claimed by new customer

---

### Stage 3: Plan churn

|Aspect|Detail|
|---|---|
|**Grain**|`(month, customer, product)`|
|**ARR logic**|`plan_prev_ltm = SUM(bop_arr WHERE customer_churn=0 AND new_customer=0)`|
|**Flag**|`planchurn_flag = 'Yes' WHEN plan_ltm=0 AND plan_prev_ltm≠0`|
|**Date check**|Activity dates table: did `plan_enddt` fall within the LTM window?|
|**WHERE filter**|`WHERE t.customer_churn=0 AND t.new_customer=0` (excludes churned customers and new customers)|
|**Bucket value**|`-bop_arr` (negative of what they had under this product)|
|**Example**|Customer A's Product P2: had $150 (Service Z) 12mo ago, $0 today → flag='Yes' → bucket = -$150|

**Rows claimed:**

- Customer B (W): skipped (already churned customer)
- Customer C: skipped (new customer)
- Customer A, Product P2, Service Z: claimed by plan churn (dropped P2)
- Customer A, Product P1, Services X,Y: still available

---

### Stage 4: Cross-sell

|Aspect|Detail|
|---|---|
|**Grain**|`(month, customer, product)`|
|**ARR logic**|`plan_prev_ltm = SUM(bop_arr WHERE customer_churn=0 AND new_customer=0 AND planchurn=0)`|
|**Flag**|`cross_sell_flag = 'Yes' WHEN plan_ltm≠0 AND plan_prev_ltm=0`|
|**Date check**|Activity dates table: did `plan_startdt` fall within the LTM window?|
|**WHERE filter**|`WHERE t.new_customer=0 AND t.customer_churn=0 AND t.planchurn=0` (excludes churn, new, plan-churn)|
|**Bucket value**|`eop_arr` (their current spend on this new product)|
|**Example**|If Customer A added a new Product P3 with Service U ($200), → flag='Yes' → bucket = $200|

**Rows claimed:**

- Customer B, C: skipped (churn or new customer)
- Customer A, P2, Z: skipped (already claimed by plan churn)
- Customer A, P1, X,Y: skipped (existing products, no change)
- **Customer A, P3, U: claimed by cross-sell** (if this row existed)

---

### Stage 5: Service cross-sell

|Aspect|Detail|
|---|---|
|**Grain**|`(month, customer, product, service)`|
|**ARR logic**|Sum at service level, excluding all prior buckets|
|**Flag**|`service_cross_sell_flag = 'Yes' WHEN service_ltm≠0 AND service_prev_ltm=0`|
|**Date check**|Activity dates table: did `service_startdt` fall within the LTM window?|
|**WHERE filter**|`WHERE t.customer_churn=0 AND t.new_customer=0 AND t.planchurn=0 AND t.cross_sell=0`|
|**Bucket value**|`eop_arr` (current service ARR)|
|**Example**|Customer A, Product P1, added Service Y' (new variant) → flag='Yes' → bucket = $new_spend|

---

### Stage 6: Service churn

|Aspect|Detail|
|---|---|
|**Grain**|`(month, customer, product, service)`|
|**ARR logic**|Sum at service level, excluding all prior non-service buckets|
|**Flag**|`servicechurn_flag = 'Yes' WHEN service_ltm=0 AND service_prev_ltm≠0`|
|**Date check**|Activity dates table: did `service_enddt` fall within the LTM window?|
|**WHERE filter**|`WHERE t.customer_churn=0 AND t.planchurn=0 AND t.new_customer=0 AND t.cross_sell=0 AND t.service_cross_sell=0`|
|**Bucket value**|`-bop_arr` (negative of what they had for this service)|

---

### Stage 7 & 8: Downsell and Upsell

|Aspect|Downsell|Upsell|
|---|---|---|
|**Grain**|Service|Service|
|**Logic**|`downsell_flag = 'Yes' WHEN service_ltm < service_prev_ltm`|`upsell_flag = 'Yes' WHEN service_ltm > service_prev_ltm`|
|**Date check**|NONE (value comparison, not lifecycle event)|NONE|
|**WHERE filter**|Excludes all 6 prior buckets|Excludes all 6 prior buckets + downsell|
|**Bucket value**|`eop_arr - bop_arr` (the delta, negative)|`eop_arr - bop_arr` (the delta, positive)|
|**Example**|Service X for A: $100 → $60 = -$40 downsell|Service Y for A: $80 → $120 = +$40 upsell|

---

## Key insights from the cascade

1. **Each stage narrows the audience**: customer-level churn eliminates everyone who left entirely. New-customer eliminates that cohort. Plan-churn operates only on the "stable base" of existing customers.
    
2. **Grain deepens as you go down**: customer → customer+product → customer+product+service. You can only measure "did this customer drop this service" after you've already ruled out "did the entire customer leave" and "is this a brand-new customer."
    
3. **Downsell/upsell are special**: they're not lifecycle events (no date checks), just magnitude comparisons. "Did the value go down?" not "Did the customer end this."
    
4. **Buckets are exhaustive and mutually exclusive**: every service-month row with any ARR change ends up in exactly one bucket (or zero, if ARR was flat). A row can't be both "churn" and "cross-sell" — the WHERE filters guarantee it.
    
5. **The order matters**: you can't flip customer churn and new customer (both are customer-grain, opposite directions, but churn must come first to exclude dead customers before checking if new customers appeared). You _could_ theoretically reorder plan/service churn differently, but the current order is intuitive: drop plans before dropping services within a plan.
    

---

## Why this structure matters for NRR

At the end:

```sql
GRR = BoP + customer_churn + planchurn + servicechurn + downsell
NRR = GRR + upsell + cross_sell + service_cross_sell
```

In other words:

- **GRR** = "if we had zero expansion, what % of revenue would we retain?" = BoP minus everything that left or shrunk
- **NRR** = GRR plus everything that grew or was added

For example, if BoP = $1000:

- Churn: -$200
- Downsell: -$50
- GRR = $1000 - $200 - $50 = $750 = 75% GRR
- Upsell: +$100
- Cross-sell: +$150
- NRR = $750 + $100 + $150 = $1000 = 100% NRR

That's why the cascade exists: every component of NRR/GRR must be measured on _the same population_ (existing customers who didn't churn), but at different logical levels (product vs service vs magnitude). The WHERE filters ensure that.
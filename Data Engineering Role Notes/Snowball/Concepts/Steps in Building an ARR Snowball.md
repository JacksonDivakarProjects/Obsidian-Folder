# Steps in Building an ARR Snowball

An ARR (Annual Recurring Revenue) snowball — usually visualized as a waterfall chart — is built through a strict sequence of data transformations. The order is not stylistic. If you try to calculate movements (New, Expansion, Churn) before establishing a solid snapshot of base revenue, the logic breaks: you have nothing to compare against, and churned customers silently vanish from the result.

The five steps below take raw subscription data to a finished, sliceable waterfall.

## Step 1: Standardize the Input Data

Before any calculation happens, the raw transactional data must be clean. The subscription table (often named something like `Fact_Subscriptions`) needs three essential columns on every record:

| Column | Purpose |
|---|---|
| **Customer Identifier** | Ties revenue to an account — e.g. `CustomerKey` or `AccountID`. |
| **Start Date** | The exact date the specific ARR amount became active. |
| **End Date** | The exact date that specific ARR amount ceased to be active. |

Open-ended contracts must be handled consistently: either leave `EndDate` as `NULL` everywhere, or use a far-future sentinel such as `2099-12-31` everywhere. Mixing the two conventions in one table is the most common source of silent snapshot errors.

## Step 2: Generate the Period-End Snapshots (EOP)

A snowball cannot be calculated directly from continuous date ranges. Those ranges must first be converted into discrete, point-in-time snapshots.

1. **Pick a cadence.** Usually the last day of the month (End of Month, or EOM).
2. **Evaluate active revenue.** For every reporting date, evaluate all subscriptions in the raw data. A subscription is active on that date if `StartDate` is on or before the snapshot date **and** `EndDate` is strictly after it (or is `NULL`).
3. **Aggregate.** Sum the ARR for each customer on each snapshot date.

The result is the **Current EOP (End of Period) ARR** — one row per customer per period.

The strict inequality on `EndDate` matters. Treating the end date as inclusive double-counts revenue on the final day of a contract, which shows up as a one-period phantom overlap between a churn and a new sale.

## Step 3: Create the Period-over-Period Alignment

To calculate what changed, the current period must be aligned with the previous period on a single row per customer. The **Previous EOP ARR** becomes the **BOP (Beginning of Period) ARR** for the current period.

**The "disappearing churn" problem.** A naive join keyed on the current month's snapshot will lose every customer who existed last month and dropped to $0 this month — precisely the customers who churned. The alignment must retain both sides:

- **In SQL:** use a `FULL OUTER JOIN` between the current month's snapshot and the previous month's snapshot, coalescing the customer key from both sides.
- **In DAX:** iterate over the entire `Dim_Customer` table rather than over the fact table, so customers with no current-period rows are still evaluated.

Either way, the output must be one row per customer per period, with both BOP and EOP present (zero-filled where absent).

## Step 4: Apply the Snowball Logic (Categorization)

With BOP and EOP aligned side by side for every customer, conditional logic categorizes the movement of every dollar.

| Bucket | Condition | Value |
|---|---|---|
| **New** | BOP = $0 and EOP > $0 | `EOP` |
| **Expansion** | BOP > $0 and EOP > BOP | `EOP - BOP` (positive) |
| **Contraction** | BOP > $0 and EOP < BOP, EOP still > $0 | `EOP - BOP` (negative) |
| **Churn** | BOP > $0 and EOP = $0 | `-BOP` (the entire beginning balance) |

Customers whose BOP equals their EOP fall into no bucket and contribute nothing to the movement columns.

The identity that validates the whole model is:

```
BOP + New + Expansion + Contraction + Churn = EOP
```

If that equation does not hold for every period, the categorization or the alignment is wrong — check Step 3 first.

## Step 5: Dimensionalize and Aggregate

Finally, sum the customer-level components (BOP, New, Expansion, Contraction, Churn, EOP) up to the total company level, grouped by reporting month.

**Adding dimensions.** To slice the waterfall by Region, Product Tier, or Sales Rep, join the dimension tables (such as `Dim_Customer`) to the dataset **after** the period-over-period alignment in Step 3 is complete. Joining earlier risks breaking the `FULL OUTER JOIN` and losing the attributes of churned revenue — a churned customer has no current-period row to carry a region or tier, so the dimension arrives `NULL` and the churn drops out of every filtered view.

## 🔗 Related Notes
- [[Deriving Start and End Dates|Deriving Start and End Dates]] — how to get the StartDate/EndDate this process depends on.
- [[Dimensional Snowball Example (SQL)|Dimensional Snowball Example (SQL)]] — a runnable implementation of exactly these five steps.
- [[Bucket Cascade Logic|Bucket Cascade Logic]] — the deeper, multi-grain version of Step 4's categorization.
- [[Snowball|Snowball]] — hub note for this area.

Building an ARR (Annual Recurring Revenue) snowball—often visualized as a waterfall chart—requires a strict sequence of data transformations. If you attempt to calculate the movements (like New, Expansion, or Churn) before establishing a solid snapshot of your base revenue, the logic will fail.

Here are the chronological steps required to construct a robust ARR snowball from raw subscription data.

### Step 1: Standardize the Input Data

Before any calculations happen, your raw transactional data must be clean. Your subscription table (often called `Fact_Subscriptions`) must contain three essential columns for every record:

1. **Customer Identifier:** e.g., `CustomerKey` or `AccountID`.
2. **Start Date:** The exact date the specific ARR amount became active.
3. **End Date:** The exact date that specific ARR amount ceased to be active. If a contract is active indefinitely, the `EndDate` must be handled consistently (e.g., left `NULL` or set to a far-future date like `2099-12-31`).

### Step 2: Generate the Period-End Snapshots (EOP)

You cannot calculate a snowball directly from continuous date ranges; you must convert those ranges into discrete, point-in-time snapshots.

* **Pick a cadence:** Usually, this is the last day of the month (End of Month, or EOM).
* **Evaluate active revenue:** For every reporting date, evaluate all subscriptions in the raw data. A subscription is considered "active" on that date if the `StartDate` is on or before the snapshot date, **and** the `EndDate` is strictly after it (or is `NULL`).
* **Aggregate:** Sum the ARR for each customer on each snapshot date. This creates your **Current EOP (End of Period) ARR**.

### Step 3: Create the Period-over-Period Alignment

To calculate what changed, you must align the current period with the previous period on a single row per customer.

* The **Previous EOP ARR** becomes your **BOP (Beginning of Period) ARR** for the current period.
* **The "Disappearing Churn" Problem:** You must use a method that retains customers who existed last month but dropped to $0 this month. In SQL, this requires a `FULL OUTER JOIN` between the current month's snapshot and the previous month's snapshot. In DAX, it requires iterating over the entire `Dim_Customer` table.

### Step 4: Apply the Snowball Logic (Categorization)

With BOP and EOP aligned side-by-side for every single customer, you apply conditional logic to categorize the movement of every dollar.

* **New:** The customer had $0 BOP ARR, but has > $0 EOP ARR.
* **Expansion:** The customer had > $0 BOP ARR, and their EOP ARR is greater than their BOP ARR. The value is the positive difference (`EOP - BOP`).
* **Contraction:** The customer had > $0 BOP ARR, and their EOP ARR is less than their BOP ARR (but still > $0). The value is the negative difference (`EOP - BOP`).
* **Churn:** The customer had > $0 BOP ARR, but has $0 EOP ARR. The value is the entire BOP amount (usually expressed as a negative).

### Step 5: Dimensionalize and Aggregate

Finally, sum the customer-level components (BOP, New, Expansion, Contraction, Churn, EOP) to the total company level, grouped by the reporting month.

* **Adding Dimensions:** If you need to slice the waterfall (e.g., by Region, Product Tier, or Sales Rep), you join your dimension tables (like `Dim_Customer`) to the dataset **after** the Period-over-Period alignment (Step 3) is complete. Doing this earlier risks breaking the `FULL OUTER JOIN` and losing churned revenue attributes.
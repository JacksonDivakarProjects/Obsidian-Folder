# Deriving Start and End Dates for ARR

The snapshot logic in an ARR snowball needs a `StartDate` and an `EndDate` on every revenue row. How you obtain them depends entirely on the shape of the raw data. Three scenarios cover most source systems.

## Scenario 1: SCD Type 2 data (the CRM way)

If the data comes from a CRM such as Salesforce, or from a warehouse that tracks history using Slowly Changing Dimensions (SCD Type 2), the work is already done. SCD Type 2 tables exist for exactly this purpose: every time a customer's ARR changes — upgrade, downgrade, or churn — the database expires the old row and writes a new one. The table will carry columns like `Valid_From` (or `Effective_Date`) and `Valid_To` (or `Expiration_Date`).

Map the SCD columns straight onto the snowball inputs:

```sql
SELECT CustomerKey, ARR_Amount, Valid_From AS StartDate, Valid_To AS EndDate
FROM Dim_Customer_History
WHERE ARR_Amount > 0
```

For currently active customers, `Valid_To` is usually either `NULL` or a far-future sentinel such as `2099-12-31` or `9999-12-31`. Both work with the snowball logic, as long as the convention is consistent across the table.

## Scenario 2: Invoice or transaction dates only (the billing way)

Billing systems often provide nothing but a list of monthly invoices. You know a customer was billed on January 1, February 1, and March 1, but there are no explicit end dates.

Use the `LEAD()` window function to treat the next invoice date as the current invoice's end date:

```sql
SELECT CustomerKey, ARR_Amount, InvoiceDate AS StartDate,
  LEAD(InvoiceDate) OVER (PARTITION BY CustomerKey ORDER BY InvoiceDate) AS EndDate
FROM Raw_Invoices
```

A churned customer simply stops receiving invoices, so their final row has a `NULL` end date — indistinguishable, on its own, from a still-active customer. Resolve this with a staleness rule: if `EndDate` is `NULL` and more than one billing cycle (plus a grace period, commonly 30 days) has elapsed since the last invoice, treat the customer as churned and set the end date accordingly.

## Scenario 3: Month-to-month subscriptions (no explicit end date)

Some raw tables record only that a customer started a monthly subscription on a given date. There is no end date column at all, because the system assumes the subscription runs until it is canceled.

If the billing frequency is known, the end date can be constructed by adding that interval to the start date. Cancellations, however, live in a separate table and must be joined in:

```sql
SELECT s.CustomerKey, s.ARR_Amount, s.Subscription_Date AS StartDate,
  c.Cancellation_Date AS EndDate
FROM Raw_Subscriptions s
LEFT JOIN Cancellations c ON s.CustomerKey = c.CustomerKey
```

The `LEFT JOIN` is deliberate: customers who never canceled produce a `NULL` end date, which the snapshot logic reads as "still active." If a customer can appear more than once in `Cancellations` (for example after a reactivation), the join must be restricted to the relevant cancellation — otherwise a single subscription row fans out into several.

## Quick comparison

| Source shape | Start date | End date | Main pitfall |
|---|---|---|---|
| SCD Type 2 | `Valid_From` | `Valid_To` | Mixed `NULL` / sentinel conventions in one table |
| Invoices | `InvoiceDate` | `LEAD(InvoiceDate)` | Trailing `NULL` needs a staleness rule to become churn |
| Month-to-month | `Subscription_Date` | Cancellation date, if any | Duplicate cancellation rows fan out the join |

## What if the end date is missing or NULL?

A missing end date is not a data-quality problem — it is information. In database logic, a `NULL` end date means the subscription is currently active. The snapshot logic from Step 2 of the snowball handles it directly:

```sql
AND (EndDate > Snapshot_Date OR EndDate IS NULL)
```

This tells the database: count this revenue if the subscription ends in the future, or if it has no end date at all.

The one thing to avoid is mixing conventions. If some rows use `NULL` and others use `9999-12-31` for the same "still active" meaning, any filter written for one convention silently drops the rows using the other. Standardize on one at ingestion.

## 🔗 Related Notes
- [[Steps in Building an ARR Snowball|Steps in Building an ARR Snowball]] — where StartDate/EndDate feed into the snapshot step.
- [[Snowball|Snowball]] — hub note for this area.

# How to Derive Start and End Dates for ARR

Getting your `StartDate` and `EndDate` depends entirely on what your raw data looks like. Here are the three most common scenarios and how to handle them.

## Scenario 1: You have SCD Type 2 Data (The CRM Way)

If your data comes from a CRM (like Salesforce) or a Data Warehouse that tracks history using **Slowly Changing Dimensions (SCD Type 2)**, you are in luck.

SCD Type 2 tables are designed exactly for this. Every time a customer's ARR changes (they upgrade, downgrade, or churn), the database "expires" the old row and creates a "new" row.

In an SCD Type 2 table, you will typically have columns like `Valid_From` (or `Effective_Date`) and `Valid_To` (or `Expiration_Date`).

**How to get the dates:**

You simply map the SCD columns directly to your snowball inputs.

```
SELECT 
    CustomerKey,
    ARR_Amount,
    Valid_From AS StartDate,
    Valid_To AS EndDate
FROM Dim_Customer_History
WHERE ARR_Amount > 0
```

_Note: If the customer is currently active, the `Valid_To` date in an SCD2 table is usually either `NULL` or a far-future date like `2099-12-31` or `9999-12-31`. Both are perfectly fine for the snowball logic!_

## Scenario 2: You only have Invoice/Transaction Dates (The Billing Way)

Often, billing systems just give you a list of monthly invoices. You know the customer was billed on Jan 1st, Feb 1st, and March 1st, but you don't have explicit "End Dates".

**How to get the dates:**

You can use the SQL Window Function `LEAD()` to look at the _next_ invoice date and use it as the _current_ invoice's end date.

```
SELECT 
    CustomerKey,
    ARR_Amount,
    InvoiceDate AS StartDate,
    
    -- Look at the next invoice date for this customer. 
    -- If there is no next invoice, leave it NULL (meaning they are currently active)
    LEAD(InvoiceDate) OVER (PARTITION BY CustomerKey ORDER BY InvoiceDate) AS EndDate
    
FROM Raw_Invoices
```

_If a customer churns, they simply stop getting invoices. The last invoice will have a `NULL` end date. You would then apply logic to say: "If EndDate is NULL and it has been more than 30 days since the last invoice, they churned."_

## Scenario 3: Month-to-Month Subscriptions (No Explicit End Date)

Sometimes you have a raw table that just says a customer started a monthly subscription on a specific date, but there is no end date column at all because the system assumes it runs forever until canceled.

**How to get the dates:**

If you know the billing frequency (e.g., monthly), you can artificially construct the end date by adding time to the start date. Furthermore, you will need a separate `Cancellations` table to figure out when to actually stop the subscription.

```
SELECT 
    s.CustomerKey,
    s.ARR_Amount,
    s.Subscription_Date AS StartDate,
    
    -- If they canceled, use the cancel date. 
    -- Otherwise, leave it NULL so the snowball treats them as active.
    c.Cancellation_Date AS EndDate
    
FROM Raw_Subscriptions s
LEFT JOIN Cancellations c
    ON s.CustomerKey = c.CustomerKey
```

## Summary: What if the End Date is missing/NULL?

If the End Date doesn't exist for a row, **that is actually a good thing!**

In database logic, a `NULL` end date means the subscription is **currently active**.

Your snapshot logic (from Step 1 of the snowball) handles this perfectly with this specific line of code:

`AND (EndDate > Snapshot_Date OR EndDate IS NULL)`

This tells the database: "Count this revenue if the subscription ends in the future, OR if it has no end date at all."
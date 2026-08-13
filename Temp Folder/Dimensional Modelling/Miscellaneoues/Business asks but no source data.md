Exactly — **this is where the data warehouse team has to work backwards from the business requirement to the source systems.**

If the **business asks for a new dimension/fact**, but the source system doesn't currently contain the required data, you **cannot simply add it to the warehouse by magic**.

### Example

Business asks:

> "We want to analyze sales by **customer satisfaction score**."

Current source system:

```text
OrderID | Customer | Product | Amount
1001    | Jack     | Laptop  | 160K
1002    | Alice    | Mouse   | 500
```

There is **no satisfaction score**.

Your existing warehouse:

```text
fact_sales
----------------
OrderKey
ProductKey
CustomerKey
DateKey
SalesAmount
```

You cannot just add:

```text
SatisfactionScore
```

because **the source doesn't provide it**.

---

## What do you do?

You investigate where that information could come from.

Maybe there is another system:

```text
CRM
   ↓
Customer Survey System
   ↓
Satisfaction Score
```

For example:

```text
Survey System

OrderID | Score
--------|------
1001    | 5
1002    | 3
```

Now ETL can integrate that source with sales.

```text
Sales System ─────────┐
                      ├──→ ETL → DW
Survey System ────────┘
```

---

## What if NO system has the data?

Then the organization has to **start capturing it**.

For example:

Business says:

> "We want to know why customers return products."

But no source system records the reason.

The solution might be:

```text
Business Requirement
        ↓
Identify missing data
        ↓
Modify operational process
        ↓
Capture Return Reason
        ↓
Source system stores it
        ↓
ETL
        ↓
Data Warehouse
```

For example, modify the return screen:

```text
Return Reason:
○ Damaged
○ Wrong Product
○ Changed Mind
○ Too Expensive
○ Other
```

Now the source begins collecting the information.

---

# This connects directly to what you read earlier

Remember the paragraph about **diagnostic metadata and business process reengineering**?

This is one of the situations it was talking about.

Sometimes the DW team discovers:

> "The business wants this information, but our operational systems don't capture it."

That becomes a **source-system/process improvement problem**.

So you might have:

```text
Business wants information
          ↓
Does source have it?
       /       \
     YES        NO
      ↓          ↓
    ETL      Find another source
      ↓          │
      ↓          └── If none:
      ↓                 ↓
   Warehouse       Change business
                       process
                          ↓
                    Capture data
                          ↓
                         ETL
                          ↓
                     Warehouse
```

### One important distinction

The **data warehouse doesn't create facts that never happened or were never recorded**.

It can:

- integrate data,
    
- clean data,
    
- transform data,
    
- derive calculations,
    

but if the underlying information **was never captured anywhere**, the organization must first change how it captures that information.

So:

> **Business requirement → determine required data → find/create a source → ETL → dimensional model.**

That's also why a good DW/BI system can eventually influence **business process reengineering**.
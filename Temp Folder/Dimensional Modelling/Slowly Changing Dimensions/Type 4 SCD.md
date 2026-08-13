# SCD Type 4 — Comprehensive Guide

SCD Type 4 is one of the more confusing Slowly Changing Dimension patterns because it introduces a **second dimension** and changes the way the fact table stores dimensional context.

The easiest way to understand it is:

> **Type 4 = separate rapidly changing attributes into a mini-dimension, and store both the base-dimension key and mini-dimension key in the fact table.**

---

## 1. Why do we need Type 4?

Imagine a huge `dim_customer` table:

```text
dim_customer
──────────────────────────────────────
Customer_SK
Customer_ID
Customer_Name
Date_of_Birth
Gender
Address
City
Income_Band
Credit_Score
Risk_Level
Customer_Segment
...
```

Suppose you have **20 million customers**.

Some attributes are relatively stable:

- Customer name
    
- Date of birth
    
- Gender
    
- Address
    

But some attributes change frequently:

- Income band
    
- Credit score
    
- Risk level
    
- Customer segment
    

If you use Type 2 for every change, you could create many versions of each customer.

For example:

```text
Customer C101

Version 1 → Medium income
Version 2 → High income
Version 3 → Very High income
Version 4 → High income
...
```

For millions of customers, this can make the dimension extremely large.

Type 4 provides another solution.

---

# 2. Core idea of Type 4

Take the rapidly changing attributes:

```text
Income_Band
Credit_Score_Band
Risk_Level
Customer_Segment
```

and move them into a separate **mini-dimension**.

So instead of:

```text
dim_customer
────────────────────────
Customer_SK
Customer_ID
Name
DOB
Income
Credit
Risk
Segment
```

you create:

```text
dim_customer
────────────────────────
Customer_SK
Customer_ID
Name
DOB
...
```

and:

```text
dim_customer_profile
────────────────────────
Profile_SK
Income_Band
Credit_Score_Band
Risk_Level
Customer_Segment
```

This smaller table is the **mini-dimension**.

---

# 3. Why is it called a mini-dimension?

Because it contains only a subset of the attributes from the original dimension.

Think:

```text
             CUSTOMER DIMENSION
                    │
          ┌─────────┴─────────┐
          │                   │
    Stable attributes    Rapidly changing
          │                   │
          ▼                   ▼
    Dim_Customer        Mini_Dimension
```

For example:

### Base dimension

|Customer_SK|Customer_ID|Name|DOB|
|--:|---|---|---|
|101|C001|John|1990-05-10|
|102|C002|Ravi|1988-03-20|

### Mini-dimension

|Profile_SK|Income|Credit|Risk|
|--:|---|---|---|
|1|Medium|Good|Medium|
|2|High|Excellent|Low|
|3|Low|Poor|High|

---

# 4. The most important concept: the fact table stores BOTH keys

This is the heart of Type 4.

Your fact table contains:

```text
Customer_SK
Profile_SK
```

For example:

|Date_SK|Customer_SK|Profile_SK|Sales|
|--:|--:|--:|--:|
|1001|101|1|₹5,000|
|1002|101|2|₹8,000|

The two keys answer different questions:

### `Customer_SK`

> **Who is the customer?**

### `Profile_SK`

> **What was the customer's rapidly changing profile when this fact occurred?**

This allows historical analysis.

---

# 5. Complete example

Suppose John starts with:

```text
Income = Medium
Risk = Medium
```

The mini-dimension contains:

|Profile_SK|Income|Risk|
|--:|---|---|
|1|Medium|Medium|

John's first purchase:

|Customer_SK|Profile_SK|Sales|
|--:|--:|--:|
|101|1|₹5,000|

Later John gets a higher salary and becomes lower risk:

```text
Income = High
Risk = Low
```

Instead of changing John's row in the huge customer dimension, create/use a new mini-dimension combination:

|Profile_SK|Income|Risk|
|--:|---|---|
|1|Medium|Medium|
|2|High|Low|

The next fact becomes:

|Customer_SK|Profile_SK|Sales|
|--:|--:|--:|
|101|1|₹5,000|
|101|2|₹8,000|

Now you can analyze:

```text
₹5,000 → when John was Medium income / Medium risk
₹8,000 → when John was High income / Low risk
```

That's the historical benefit.

---

# 6. What happens when another customer has the same profile?

This is an important point.

Suppose Ravi also has:

```text
Income = High
Risk = Low
```

You **don't necessarily create another mini-dimension row**.

You can reuse:

```text
Profile_SK = 2
```

So:

|Profile_SK|Income|Risk|
|--:|---|---|
|1|Medium|Medium|
|2|High|Low|

And facts might be:

|Customer_SK|Profile_SK|Sales|
|--:|--:|--:|
|101|2|₹8,000|
|102|2|₹4,000|

This is one of the reasons the mini-dimension can remain relatively small.

It's essentially storing **distinct combinations of the rapidly changing attributes**.

---

# 7. What does "append" mean here?

When a **new combination** appears, you add a new mini-dimension row.

Suppose you currently have:

|Profile_SK|Income|Risk|
|--:|---|---|
|1|Medium|Medium|
|2|High|Low|

Now a customer gets:

```text
Income = High
Risk = Medium
```

That's a new combination.

Append:

|Profile_SK|Income|Risk|
|--:|---|---|
|1|Medium|Medium|
|2|High|Low|
|3|High|Medium|

The fact then references:

```text
Profile_SK = 3
```

---

# 8. Is this Type 1?

Normally, **no**.

You don't want to overwrite:

```text
Profile_SK = 1
Medium / Medium
```

with:

```text
High / Medium
```

because then old facts pointing to `Profile_SK = 1` would suddenly appear to have the new profile.

You'd destroy the historical context.

So the mental model is:

```text
Existing combination → reuse existing Profile_SK

New combination → INSERT new Profile_SK
```

---

# 9. Is this Type 2?

It's also important not to simply say:

> "The mini-dimension is Type 2."

That's not the core idea.

Type 2 means:

> **A change to a dimension member creates a new version of that dimension member.**

Type 4 instead says:

> **Separate rapidly changing attributes into a mini-dimension and let facts capture the applicable mini-dimension key.**

The mechanisms look somewhat similar because both can result in new rows, but the **architecture and purpose are different**.

---

# 10. Type 2 vs Type 4

This is probably the most important comparison for you.

### Type 2

Customer changes:

```text
Customer C101
Chennai → Bangalore
```

Create a new customer row:

|Customer_SK|Customer_ID|City|
|--:|---|---|
|101|C101|Chennai|
|205|C101|Bangalore|

The **customer dimension itself contains the history**.

---

### Type 4

Customer's rapidly changing profile changes:

```text
Medium/Medium → High/Low
```

The customer dimension stays relatively stable:

|Customer_SK|Customer_ID|Name|
|--:|---|---|
|101|C101|John|

The mini-dimension handles the profile:

|Profile_SK|Income|Risk|
|--:|---|---|
|1|Medium|Medium|
|2|High|Low|

The fact contains:

|Customer_SK|Profile_SK|
|--:|--:|
|101|1|
|101|2|

### One-line difference

> **Type 2 creates history by creating new rows in the main dimension.**  
> **Type 4 creates history by separating rapidly changing attributes into a mini-dimension and storing its key in the fact.**

---

# 11. Why does Type 4 help with a "monster dimension"?

A **rapidly changing monster dimension** is essentially a large dimension with attributes that change frequently.

Imagine:

```text
50 million customers
×
many Type 2 changes
```

You can end up with a massive number of dimension rows.

Type 4 says:

> Don't repeatedly duplicate the entire customer row just because a small group of attributes changed.

Instead:

```text
Large stable dimension
        +
Small rapidly-changing mini-dimension
        +
Fact containing both keys
```

This can reduce the amount of repeated dimensional data.

---

# 12. What does the fact table look like?

A typical Type 4 fact table might look like:

|Date_SK|Customer_SK|Customer_Profile_SK|Product_SK|Sales|
|--:|--:|--:|--:|--:|
|1001|101|1|5001|5000|
|1002|101|2|5002|8000|
|1003|102|2|5003|4000|

Notice:

```text
Customer_SK
Customer_Profile_SK
```

are **both foreign keys**.

Conceptually:

```text
                 Fact_Sales
                /           \
               /             \
              ▼               ▼
       Dim_Customer      Mini_Dim_Profile
       Customer_SK       Profile_SK
```

---

# 13. How do queries work?

Suppose you want:

> "How much did high-income customers spend?"

You join the fact to the mini-dimension:

```sql
SELECT
    SUM(f.sales)
FROM fact_sales f
JOIN dim_customer_profile p
    ON f.profile_sk = p.profile_sk
WHERE p.income_band = 'High';
```

You don't need to look at the main customer dimension for this attribute.

---

# 14. Historical analysis

Suppose the business asks:

> "How much did customers spend while they were in the High-Risk segment?"

The fact remembers the profile that applied at the time:

```text
Fact
Customer_SK | Profile_SK | Sales
101         | 1           | 5000
101         | 2           | 8000
```

Mini-dimension:

```text
Profile_SK | Risk
1          | Medium
2          | Low
```

So:

```text
Medium Risk → ₹5,000
Low Risk    → ₹8,000
```

The customer's **current state doesn't overwrite the historical fact's context**.

That's a major reason for using Type 4.

---

# 15. Does the mini-dimension need effective dates?

In the **classic Type 4 pattern**, you generally don't need the Type 2-style:

```text
Effective_Date
Expiration_Date
Current_Flag
```

The **fact's foreign key to the mini-dimension captures the profile applicable to that fact**.

This is a major conceptual difference from Type 2.

### Type 2

```text
Dimension row
    ↓
Effective / Expiration dates
    ↓
Fact points to version
```

### Type 4

```text
Mini-dimension combination
    ↓
Fact captures Profile_SK
```

---

# 16. What happens if a customer changes back?

Suppose:

```text
Medium / Medium
     ↓
High / Low
     ↓
Medium / Medium
```

If `Medium / Medium` already exists as:

```text
Profile_SK = 1
```

you can reuse:

```text
Profile_SK = 1
```

You don't necessarily need:

```text
Profile_SK = 3
```

for the same combination.

So you might have:

|Profile_SK|Income|Risk|
|--:|---|---|
|1|Medium|Medium|
|2|High|Low|

Facts:

|Date|Customer_SK|Profile_SK|
|---|--:|--:|
|Jan|101|1|
|Jun|101|2|
|Dec|101|1|

This is one of the nice properties of the mini-dimension approach.

---

# 17. Type 4 vs Type 3

Since you've just learned Type 3, this comparison is useful.

### Type 3

You might have:

|Customer|Current_Region|Previous_Region|
|---|---|---|
|C101|Bangalore|Chennai|

You preserve **one previous value**.

---

### Type 4

You separate the changing attributes:

```text
Mini_Dimension
```

and facts reference different profile combinations.

So Type 4 can support much richer historical analysis without adding multiple "previous value" columns to the main dimension.

---

# 18. Type 4 vs Type 1

### Type 1

```text
Old value → overwritten
```

History:

❌ Lost

### Type 4

```text
Old profile → remains available
New profile → new/reused Profile_SK
Fact → remembers applicable Profile_SK
```

History:

✅ Preserved for the fact context.

---

# 19. ETL process

A simplified Type 4 ETL flow looks like this:

```text
Source
  │
  ▼
Identify customer
  │
  ▼
Separate stable attributes
and rapidly changing attributes
  │
  ├───────────────┐
  ▼               ▼
Dim_Customer   Mini_Dim_Profile
  │               │
  │               ├── Existing combination?
  │               │       │
  │               │       ├── YES → reuse Profile_SK
  │               │       │
  │               │       └── NO → insert new row
  │               │
  └───────────────┘
          │
          ▼
       Fact table
          │
          ├── Customer_SK
          └── Profile_SK
```

---

# 20. The key design principle

The fact table is where the **historical association** is preserved.

This is extremely important.

The mini-dimension says:

> "What does profile 2 mean?"

The fact says:

> "This transaction happened while the customer had profile 2."

So:

```text
Mini-Dimension
Profile_SK = 2
        ↓
High Income + Low Risk

Fact
Profile_SK = 2
        ↓
This transaction occurred under that profile
```

---

# 21. Common mistake: thinking the mini-dimension belongs to one customer

It doesn't necessarily.

A mini-dimension row represents an **attribute combination**, not necessarily one specific customer.

For example:

```text
Profile_SK = 7
Income = High
Risk = Low
Segment = Premium
```

could be used by:

```text
Customer A
Customer B
Customer C
Customer D
...
```

That's why it can remain much smaller than the customer dimension.

---

# 22. Common mistake: confusing SKs

There are two different surrogate keys:

```text
Customer_SK
Profile_SK
```

They identify different things.

### Customer_SK

Identifies:

> **Customer dimension member**

### Profile_SK

Identifies:

> **Rapidly changing profile combination**

They are not interchangeable.

---

# 23. The relationship

Conceptually:

```text
Dim_Customer
     │
     │ Customer_SK
     ▼
Fact_Sales
     ▲
     │ Profile_SK
     │
Mini_Dim_Profile
```

The fact table is the bridge between the two dimensions.

---

# 24. When should you consider Type 4?

Type 4 becomes attractive when:

- A dimension is very large.
    
- A subset of attributes changes frequently.
    
- Type 2 would create too many dimension rows.
    
- You need historical analysis of those changing attributes.
    
- The changing attributes can be represented as combinations.
    
- You want to isolate frequently changing data from relatively stable customer data.
    

---

# 25. When Type 4 may not be necessary

Don't automatically use Type 4 whenever something changes frequently.

If the dimension is small and Type 2 works perfectly well, Type 2 may be simpler.

For example:

```text
Dim_Employee
10,000 rows
```

If an employee's department changes occasionally, Type 2 might be perfectly reasonable.

But:

```text
Dim_Customer
50 million rows
```

with rapidly changing behavioral/profile attributes may be a much stronger Type 4 candidate.

---

# 26. Type 4 in one picture

Here's the complete mental model:

```text
                  DIM_CUSTOMER
              ┌───────────────────┐
              │ Customer_SK (PK)  │
              │ Customer_ID       │
              │ Name              │
              │ DOB               │
              │ Address           │
              └─────────┬─────────┘
                        │
                        │ Customer_SK
                        │
                        ▼
                  FACT_SALES
              ┌───────────────────┐
              │ Customer_SK (FK)  │
              │ Profile_SK (FK)   │
              │ Date_SK           │
              │ Product_SK        │
              │ Sales             │
              └─────────┬─────────┘
                        │
                        │ Profile_SK
                        │
                        ▼
              MINI-DIMENSION
              ┌───────────────────┐
              │ Profile_SK (PK)   │
              │ Income_Band       │
              │ Credit_Band       │
              │ Risk_Level        │
              │ Segment           │
              └───────────────────┘
```

---

# 27. Type 0 → Type 4 Pareto summary

|Type|Basic idea|Existing row|New row?|History|
|---|---|---|---|---|
|**0**|Retain original|Don't change|Usually no|Original only|
|**1**|Overwrite|UPDATE|INSERT for new member|❌|
|**2**|Add new row|Keep old|INSERT version|✅ Full|
|**3**|Add attribute|UPDATE|Usually no|⚠️ Limited|
|**4**|Add mini-dimension|Keep stable base dimension|INSERT new profile combination|✅ Via fact + mini-dim|

### The one sentence to memorize

> **SCD Type 4 separates rapidly changing attributes from a large dimension into a mini-dimension, assigns the mini-dimension its own surrogate key, and stores both the base dimension key and mini-dimension key in the fact table so historical profile context is preserved.**

And the **most important distinction** from Type 2 is:

> **Type 2 creates historical versions of the main dimension member; Type 4 creates/reuses profile combinations in a separate mini-dimension and lets the fact table capture the applicable profile.**
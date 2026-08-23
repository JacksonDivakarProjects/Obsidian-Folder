Absolutely. Here's a **clean revision guide** on **Fact Table Grain**, written generally rather than around our specific examples.

# Fact Table Grain — Revision Guide

## 1. What is Grain?

**Grain is the precise definition of what one row in a fact table represents.**

For example:

> **One row represents one product sold in one order.**

This means every fact row corresponds to one specific business event at a specific level of detail.

Think of grain as the **zoom level** of the fact table.

```text
Coarse
   ↓
One Order
   ↓
One Order + Product
   ↓
One Order + Product + Promotion
   ↓
More atomic
```

The lower/more atomic the grain, the more detailed each fact row is.

---

# 2. Grain represents a business event

A fact table should correspond to a **physical observable business event**, not to a report.

For example, in retail:

> A customer buys a product.

That event can be represented at different grains.

### Order-level grain

> One row = one order

### Order-line grain

> One row = one product line within an order

### Promotion-level grain

> One row = one product sold under one promotion within an order

These are different grains and potentially different fact table designs.

---

# 3. Grain must be declared before identifying facts

The dimensional design process is:

```text
Business Process
       ↓
Declare Grain
       ↓
Identify Dimensions
       ↓
Identify Facts
```

For example:

### Business process

Retail sales

### Grain

> One row represents one product sold in one order.

### Dimensions

- Date
    
- Product
    
- Customer
    
- Store
    
- Promotion
    

### Facts

- Quantity
    
- Sales Amount
    
- Discount Amount
    

The grain tells you what measurements are valid.

---

# 4. Grain determines which facts belong in the fact table

A fact must be **consistent with the declared grain**.

Suppose:

> Grain = one product sold in one order.

Then these can be valid:

```text
Quantity
Sales Amount
Discount Amount
Tax Amount
```

because they describe that sales event.

But:

```text
Store Manager Salary
```

doesn't belong.

Its natural grain might be:

> One employee per payroll period.

That is a different business event and a different grain.

---

# 5. A single business transaction can produce multiple fact rows

Don't confuse a **transaction** with a **fact row**.

Suppose an order contains:

```text
Order 1001
 ├── Laptop
 ├── Mouse
 └── Keyboard
```

If the grain is:

> One product per order

then the order produces three fact rows.

```text
Order 1001 + Laptop
Order 1001 + Mouse
Order 1001 + Keyboard
```

Therefore:

> **The number of fact rows depends on the declared grain, not simply on the number of business transactions.**

---

# 6. Grain and atomicity

**Atomic grain** means the fact table is stored at the lowest useful level of detail required by the business process.

Example:

### Less atomic

> One row = one order

```text
Order 1001 → ₹1,000
```

### More atomic

> One row = one product within an order

```text
Order 1001 + Laptop → ₹700
Order 1001 + Mouse → ₹200
Order 1001 + Keyboard → ₹100
```

The second design is more atomic because the original order has been broken down into its individual product-level events.

---

# 7. Making a fact table more atomic

An existing fact table can sometimes be made more atomic.

The general pattern is:

```text
Existing grain
      ↓
Identify additional business detail
      ↓
Add required attributes to dimensions
      ↓
Redefine the fact grain
      ↓
Restate/reload the fact table
```

For example:

### Existing grain

> One row = one product per order

New business requirement:

> Analyze each product by promotion.

If the source data supports this level of detail, the new grain could become:

> One row = one product per order per promotion.

The fact must then be **restated at this lower/more atomic grain**.

---

# 8. What does "restating the fact table" mean?

It means **rebuilding/reloading the fact table so that its rows conform to the new grain**.

Suppose the old fact has:

|Order|Product|Amount|
|---|---|--:|
|O1|P1|100|

And source data reveals:

|Order|Product|Promotion|Amount|
|---|---|---|--:|
|O1|P1|C0|60|
|O1|P1|C1|40|

The old grain was:

> Order + Product

The new grain is:

> Order + Product + Promotion

The old row:

```text
O1 + P1 = 100
```

must be restated as:

```text
O1 + P1 + C0 = 60
O1 + P1 + C1 = 40
```

The fact now represents a finer level of detail.

---

# 9. Adding a dimension to an existing fact table

A new dimension can be added to an existing fact table by adding a **foreign key column**, provided the new dimension does **not require changing the existing grain**.

Example:

Existing fact:

```text
fact_sales

DateKey
ProductKey
CustomerKey
Quantity
SalesAmount
```

Existing grain:

> One product sold to one customer on one date.

Now the business wants to classify sales by campaign.

Create:

```text
dim_campaign

CampaignKey
CampaignNo
CampaignName
CampaignType
```

Then add:

```text
CampaignKey
```

to the fact.

```text
fact_sales

DateKey
ProductKey
CustomerKey
CampaignKey   ← new FK
Quantity
SalesAmount
```

The fact can now be joined to the campaign dimension.

---

# 10. Adding a foreign key does not automatically change grain

This is extremely important.

The physical act of adding:

```text
CampaignKey
```

to a fact table does **not by itself mean** the grain has changed.

You must ask:

> **What does one row represent after the change?**

If one existing fact row still represents exactly the same business event, the grain has not changed.

The new dimension is simply providing another descriptive perspective on that event.

---

# 11. The test for whether a new dimension changes the grain

When adding a dimension to an existing fact table, ask:

> **Does every existing fact row correspond to exactly one member of the new dimension?**

If yes, the new dimension can generally be added without changing the fact grain.

Conceptually:

```text
Existing fact row
       ↓
Exactly one dimension member
       ↓
Add FK
       ↓
Same grain
```

If one existing fact row represents **multiple members** of the new dimension, then the existing grain is insufficient to represent that relationship.

You may need to make the fact more atomic.

```text
Existing fact row
       ↓
Multiple dimension members
       ↓
Existing row must be split
       ↓
New finer grain
```

---

# 12. Adding attributes to an existing dimension

Attributes can be added to an existing dimension by creating new columns.

Example:

Existing:

```text
dim_product

ProductKey
ProductName
Brand
Category
```

Business now wants product color.

Add:

```text
Color
```

Result:

```text
dim_product

ProductKey
ProductName
Brand
Category
Color ← new attribute
```

The fact table does not necessarily need to change.

The fact already contains:

```text
ProductKey
```

which allows users to reach the new attribute:

```text
fact_sales
     │
     │ ProductKey
     ▼
dim_product
     │
     └── Color
```

---

# 13. Dimensions contain descriptive context; facts contain measurements

A useful rule:

### Dimensions answer:

> **Who? What? Where? When? Which?**

Examples:

- Customer
    
- Product
    
- Store
    
- Date
    
- Campaign
    
- Promotion
    

### Facts answer:

> **How much? How many?**

Examples:

- Quantity
    
- Sales Amount
    
- Cost
    
- Discount Amount
    

The fact usually stores **foreign keys** to dimensions rather than copying all the descriptive attributes into the fact.

---

# 14. Using a more detailed dimension to support a more atomic fact

Sometimes making a fact more atomic requires enhancing an existing dimension.

Example:

Originally:

```text
dim_product

ProductKey
ProductName
```

Later, the business needs analysis by product variant.

You might enhance the product dimension with:

```text
Color
Size
```

and ensure the dimension's keys identify the appropriate detailed product/variant.

The fact can then be restated so its rows correspond to those more detailed product members.

The important sequence is:

```text
More detailed business requirement
             ↓
Dimension must represent that detail
             ↓
Fact is restated at that detail
             ↓
New, more atomic grain
```

---

# 15. Preserve existing column names when evolving the grain

Kimball recommends being careful to preserve existing column names when restating a fact at a lower grain.

For example, if the existing fact has:

```text
ProductKey
Quantity
SalesAmount
```

you should generally continue using those established names rather than unnecessarily renaming them simply because the grain has become more detailed.

The **grain can become more atomic while the physical column names remain stable**.

This reduces disruption to:

- ETL processes
    
- reports
    
- queries
    
- downstream applications
    
- BI tools
    

---

# 16. Source systems determine what level of grain is possible

You cannot create detail that does not exist in the source data.

Suppose the business asks:

> "Show sales by campaign."

But the source only contains:

```text
OrderID
ProductID
Quantity
Price
```

and has no campaign information.

The warehouse cannot magically determine the campaign.

You need the information to exist somewhere:

```text
Source system
      OR
Another source
      OR
Operational process enhancement
```

Only then can ETL bring that information into the warehouse.

---

# 17. ETL's role in grain

ETL is responsible for transforming source data into the dimensional model while preserving the declared grain.

For example:

```text
Source
  ↓
Extract
  ↓
Clean / validate
  ↓
Conform dimensions
  ↓
Lookup surrogate keys
  ↓
Load fact
```

If the declared grain is:

> One product + order + campaign

then ETL must ensure that each fact row corresponds to exactly that definition.

It must not accidentally:

- duplicate rows
    
- combine different events
    
- lose required detail
    
- mix different grains
    

---

# 18. Different grains should not be mixed in one fact table

This is a fundamental dimensional modeling rule.

Suppose one set of rows means:

> One product sold per order

while another set means:

> One order per day

Those are different grains.

Don't put them into the same fact table merely because both contain `SalesAmount`.

Instead, they generally belong in separate fact tables.

```text
fact_sales_line
    Grain: one product per order

fact_daily_sales
    Grain: one store per day
```

Different grain → separate physical fact table.

---

# 19. Grain determines how measures can be aggregated

Because the grain defines what each fact row means, it also determines how measures behave.

For example, at a product/order-line grain:

```text
Quantity
SalesAmount
```

can generally be summed to higher levels:

```text
Product
Store
Customer
Day
Month
Campaign
```

This is one of the major benefits of keeping detailed atomic facts.

You can **roll them up** to many different reporting levels.

```text
Atomic facts
     ↓
Day
     ↓
Month
     ↓
Quarter
     ↓
Year
```

---

# 20. Atomic facts support unpredictable analysis

A detailed atomic fact table allows users to answer questions that weren't necessarily anticipated when the warehouse was designed.

For example, if the fact is stored at:

> One product per order

you can later analyze:

- Product sales
    
- Customer sales
    
- Store sales
    
- Daily sales
    
- Monthly sales
    
- Product + store
    
- Product + campaign
    
- Customer + product
    
- etc.
    

If you stored only highly aggregated facts, many of these analyses would be impossible.

---

# 21. Fact table sparsity and grain

Fact tables generally contain only **actual business events**.

If a product was not sold, you normally don't create a row containing zeros just to represent "no sale."

Example:

```text
Product P1 sold → fact row
Product P2 sold → fact row
Product P3 not sold → no fact row
```

This makes fact tables **sparse**.

Despite being sparse, fact tables often consume the majority of the storage in a dimensional model because they contain enormous numbers of business-event rows.

---

# 22. Grain and physical fact-table design

A different grain generally means a different physical fact table.

For example:

```text
fact_sales
Grain: one product per order
```

and:

```text
fact_inventory_snapshot
Grain: one product per store per day
```

These represent completely different business processes and grains.

You should not mix them.

---

# 23. The three important modification rules

These three Kimball rules are worth memorizing.

### Rule 1 — Add a dimension

You can add a dimension to an existing fact by adding a new FK column **if the existing fact grain remains valid**.

```text
New dimension
      ↓
New FK in fact
      ↓
Same grain
```

---

### Rule 2 — Add an attribute

You can add attributes to an existing dimension by adding new columns.

```text
Existing dimension
      ↓
New descriptive attribute
      ↓
Same fact grain
```

---

### Rule 3 — Make the grain more atomic

You can make a fact more atomic when the business requires a finer level of detail.

```text
Existing grain
      ↓
Enhance dimensional detail if necessary
      ↓
Restate/reload fact
      ↓
New finer grain
```

---

# 24. How to distinguish the three

Use this table for revision:

|Change|What changes?|Grain changes?|
|---|---|---|
|Add a dimension|New dimension + FK in fact|**Not necessarily**|
|Add dimension attribute|New column in dimension|**No**|
|Make fact more atomic|Fact rows represent finer events|**Yes**|
|Add a compatible fact|New measure column|**No**|
|Mix different business-event grains|Multiple row meanings|**Not allowed**|

---

# 25. The most important diagnostic question

Whenever you modify a dimensional model, ask:

> **"What exactly does one row represent?"**

Write it as a sentence.

For example:

> **One row represents one product sold in one order.**

After a proposed change, write it again:

> **One row represents one product sold in one order under one campaign.**

Then compare the two.

### Same sentence

The grain hasn't changed.

### More detailed sentence

The grain has become more atomic.

---

# 26. Final mental model

Keep this hierarchy in mind:

```text
                 BUSINESS PROCESS
                       │
                       ▼
                     GRAIN
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
     DIMENSIONS      FACTS       KEYS
          │            │            │
          │            │            │
     Descriptive    Numeric       FK/PK
     context       measurements   relationships
```

And when modifying the model:

```text
                    EXISTING MODEL
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
   Add dimension    Add attribute    Add more detail
          │               │                │
          ▼               ▼                ▼
     New FK in        New column       Restate fact
       fact          in dimension          │
          │               │                ▼
          ▼               ▼          Finer grain
     Grain usually    Grain stays
       unchanged       unchanged
```

## ⭐ The 5 rules to memorize

1. **Grain = what one fact row represents.**
    
2. **Declare the grain before choosing facts and dimensions.**
    
3. **Facts must be consistent with the declared grain.**
    
4. **Adding a dimension or dimension attribute does not automatically change grain.**
    
5. **If one fact row must be split into multiple rows to represent additional business detail, the grain has become more atomic and the fact must be restated/reloaded.**
    

The single sentence to remember:

> **Adding columns changes the structure; changing what one row represents changes the grain.**
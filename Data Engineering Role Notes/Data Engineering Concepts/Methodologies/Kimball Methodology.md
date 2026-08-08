# Kimball Methodology

Kimball is a **data warehouse design methodology** created by **Ralph Kimball**. It optimizes for making data easy for business users to query and analyze, rather than for eliminating data redundancy. Instead of a highly normalized enterprise model (Inmon-style), Kimball organizes data into **dimensional models** — fact tables and dimension tables joined into star schemas.

If you work with **dbt, Synapse, Snowflake, Databricks, or Power BI**, you will run into Kimball-style modeling constantly — most modern BI marts are built on it.

---

## Fact Tables

Fact tables store **measurable business events** — the numbers you aggregate and report on.

Examples: Sales, Orders, Revenue, Quantity, Profit.

```text
fact_sales

sale_id
date_key
customer_key
product_key
store_key
quantity
sales_amount
discount
profit
```

Characteristics:

- Very large tables (grow with every business event)
- Mostly numeric measures
- Foreign keys to surrounding dimensions
- One row = one business event at a defined grain

---

## Dimension Tables

Dimensions describe the context around a fact — the "who, what, where, when" of a business event.

```text
dim_customer

customer_key
customer_name
city
country
gender
age_group
```

```text
dim_product

product_key
product_name
brand
category
color
```

Characteristics:

- Relatively small compared to facts
- Rich, descriptive, mostly text/attribute columns
- Used for filtering, grouping, and labeling in reports

Example: a report on "Revenue by Brand" pulls `Brand` from `dim_product` and `Revenue` from `fact_sales` — this fact/dimension split is the core of dimensional modeling.

---

## Star Schema

Kimball strongly recommends a **star schema**: one central fact table joined directly to its surrounding dimensions.

```
             dim_date
                 |
dim_customer --- fact_sales --- dim_product
                 |
             dim_store
```

Advantages:

- Simple joins (fact to dimension, one hop)
- Fast queries — few joins for the query optimizer to plan
- Easy for analysts and BI tools to understand
- Strong BI/reporting performance

### Snowflake Schema

A snowflake schema normalizes dimensions further, splitting them into sub-dimensions:

```
Product
   |
Category
   |
Department
```

...instead of collapsing everything into one denormalized dimension:

```text
dim_product

category
department
brand
```

Kimball generally recommends **avoiding snowflaking** unless there's a clear win (e.g. a huge, frequently-changing hierarchy) — it adds extra joins for little benefit in a BI context, since the storage savings from normalization matter far less than query simplicity.

---

## Grain — the Most Important Rule

Kimball's core rule: **declare the grain first.**

Grain = **what does one row in the table represent?** Every other modeling decision follows from this.

**Good grain (single, explicit):**

- One row per invoice line (`Invoice`, `Product`, `Quantity`)
- One row per order
- One row per customer per month

**Bad grain (mixed):**

Combining multiple levels of detail in one table — e.g. Order-level and Product-level and Month-level rows mixed together — causes double counting when you aggregate, because the same underlying event gets represented (and summed) at more than one level of detail.

---

## Surrogate Keys vs. Natural Keys

Use **surrogate keys** — warehouse-generated integer keys — instead of relying on source-system business keys.

```text
Natural key:    CustomerID = C1001
Surrogate key:  CustomerKey = 101
```

Both are typically stored on the dimension row, but the **fact table references only the surrogate key** (`CustomerKey`), never the natural key.

Reasons to use surrogate keys:

- Business/source-system IDs can change or be reused
- They make Slowly Changing Dimensions possible (multiple surrogate keys can map to one natural key over time)
- Smaller, simpler integer joins
- Decouples the warehouse from source-system key formats

---

## Slowly Changing Dimensions (SCD)

Handling how dimension attributes change over time is one of the most important (and most tested-in-interviews) Kimball concepts.

### Type 1 — Overwrite

Overwrite the old value in place; no history is kept.

```text
City
Old: London
New: Paris
```

Use when history doesn't matter for that attribute (e.g. correcting a typo).

### Type 2 — Add a New Row (most common)

Keep full history by inserting a new dimension row with a new surrogate key whenever a tracked attribute changes.

```text
CustomerKey
101   London   (old row, now historical)
202   Paris    (new row, current)
```

Existing fact rows keep pointing at the surrogate key that was current *at the time of the event*, so historical reports still reflect "London" for old sales — this is what makes Type 2 the standard choice for attributes you need to report on historically (e.g. a customer's region at time of purchase).

### Type 3 — Add a New Column

Store the previous value alongside the current value in the same row (e.g. `Current City`, `Previous City`). Only keeps one prior state, not full history — rarely used, mainly for "compare current vs. last" cases.

---

## Conformed Dimensions

A **conformed dimension** is a single, shared dimension used consistently across multiple fact tables, guaranteeing everyone means the same thing by "Customer."

```text
dim_customer
```

used by:

```text
fact_sales
fact_returns
fact_orders
fact_support
```

This is what lets you join `fact_sales` and `fact_returns` through the same `dim_customer` and get consistent results — without conformed dimensions, different teams end up with subtly incompatible definitions of the same entity.

---

## Fact Table Types

- **Transaction fact** — one row per individual event, as it happens (e.g. every sale).
- **Periodic snapshot** — one row per fixed time interval, capturing a state (e.g. daily inventory levels).
- **Accumulating snapshot** — one row per process instance, updated in place as the process moves through its stages (e.g. an order row updated as it moves through Created → Packed → Shipped → Delivered).

---

## Degenerate Dimension

A dimension attribute that lives directly in the fact table because it has no other descriptive attributes worth a separate table — e.g. an `Invoice Number` column on `fact_sales`. No separate dimension table is created for it.

---

## Junk Dimension

A single dimension that bundles together several small, low-cardinality flags that would otherwise clutter the fact table.

Instead of storing `IsOnline`, `IsGift`, `IsDiscount` as separate flag columns on the fact table, combine them into one `dim_flags` dimension and reference it with a single foreign key.

---

## Role-Playing Dimensions

One physical dimension table used multiple times in the same fact table, in different "roles," typically via views or aliases at query time.

```text
dim_date
```

used as:

```text
Order Date
Ship Date
Delivery Date
```

The same `dim_date` table is joined into the fact table three times (once per role) rather than building three separate date dimensions.

---

## Date Dimension

Never scatter raw date logic (fiscal year, holidays, weekday names) across queries — build one `dim_date` table and join to it everywhere.

```text
dim_date

date_key
date
month
quarter
year
holiday
week
weekday
```

---

## Modeling Rules

### Fact table rules

Always include:

- Numeric measures
- Foreign keys only (to dimensions)
- Data at the lowest available grain
- No descriptive/text columns

Good: `customer_key, product_key, date_key, sales, quantity`
Bad: `customer_name, product_name, city` (these belong in dimensions, not facts)

### Dimension table rules

Include:

- Names, categories, attributes, hierarchies

Example (`dim_product`): `Brand, Category, Subcategory, Color, Size`

### Null handling

Never leave a fact table's foreign key `NULL`. Create an explicit "Unknown" member in the dimension (e.g. `CustomerKey = 0` for "Unknown Customer") and point unresolved rows at it instead — `NULL` foreign keys break joins and silently drop rows from inner joins.

### Naming standards

Good: `fact_sales, fact_orders, dim_customer, dim_product, dim_store`
Avoid: `tbl1, data, master` — names should say what the table is at a glance.

---

## Additive, Semi-Additive, and Non-Additive Facts

This classifies whether a measure can be safely summed across a given dimension:

- **Additive** — can be summed across *all* dimensions, including time. Example: `Revenue`, `Quantity`.
- **Semi-additive** — can be summed across some dimensions but not time. Example: `Bank Balance` — you can sum balances across accounts at a point in time, but summing a balance across days doesn't mean anything.
- **Non-additive** — cannot be meaningfully summed at all, regardless of dimension. Example: `Percentage`, `Ratio` — these must be recalculated from their underlying additive components, not summed directly.

---

## Best Practices

1. **Define the grain first** — before creating any table, state explicitly what one row represents.
2. **Prefer star schemas** — keep dimensions denormalized unless normalization gives a clear, specific benefit.
3. **Use surrogate keys** — for stable joins and to support historical tracking (SCDs).
4. **Keep facts narrow** — store only keys and measures in fact tables.
5. **Build conformed dimensions** — reuse Customer, Product, Date, etc. across every fact table that needs them.
6. **Use SCD Type 2 for history** — whenever an attribute's historical value matters for reporting.
7. **Create a date dimension** — avoid re-deriving calendar logic (fiscal periods, holidays) in every query.
8. **Store data at the lowest grain** — aggregate in the BI layer/reports, not in the warehouse tables themselves.
9. **Handle unknown members explicitly** — use default dimension rows (e.g. key `0`) instead of `NULL` foreign keys.
10. **Document business definitions** — make sure metrics like "Revenue," "Active Customer," and "Churn" mean the same thing everywhere they're used.

---

## Kimball in a dbt Project

A typical dbt project layout maps cleanly onto Kimball's layers:

```text
Raw Source
    │
    ▼
Staging (stg_*)
    │
    ▼
Intermediate (int_*)
    │
    ▼
Dimensions (dim_*)  +  Facts (fact_*)
    │
    ▼
Marts / BI
```

```text
models/
├── staging/
│   ├── stg_orders.sql
│   └── stg_customers.sql
├── intermediate/
│   └── int_order_items.sql
└── marts/
    ├── dimensions/
    │   ├── dim_customer.sql
    │   ├── dim_product.sql
    │   └── dim_date.sql
    └── facts/
        ├── fact_orders.sql
        └── fact_sales.sql
```

If you're learning dbt, understanding Kimball's dimensional modeling directly helps you design marts that are easy to maintain, performant for analytics, and intuitive for business users. The core habits to keep: **declare the grain first, model facts and dimensions separately, use star schemas, build conformed dimensions, and preserve history with SCDs where it matters.**

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Miscellaneous/Data Modeling|Data Modelling Masterclass for Data Engineers]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Miscellaneous/Types of Fact Table|Types of Fact Tables in Data Warehousing]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Miscellaneous/Fundamentals Of Data Engineering|Fundamentals Of Data Engineering]]

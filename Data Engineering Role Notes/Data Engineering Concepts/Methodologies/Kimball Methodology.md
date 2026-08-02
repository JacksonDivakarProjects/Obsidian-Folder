Kimball is a **data warehouse design methodology** created by **Ralph Kimball**. It focuses on making data easy for business users to query and analyze. Instead of building a highly normalized enterprise model, Kimball recommends organizing data into **dimensional models** (fact and dimension tables).

If you're working with **dbt, Synapse, Snowflake, Databricks, or Power BI**, you'll encounter Kimball modeling frequently.

---

# Core Concepts

## 1. Fact Tables

Fact tables contain **measurable business events**.

Examples:

- Sales
    
- Orders
    
- Revenue
    
- Quantity
    
- Profit
    

Example

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

Characteristics

- Very large tables
    
- Mostly numeric values
    
- Foreign keys to dimensions
    
- One row represents one business event
    

---

## 2. Dimension Tables

Dimensions describe the facts.

Example

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

Characteristics

- Relatively small
    
- Descriptive information
    
- Used for filtering and grouping
    

Example

> Revenue by Brand

Brand comes from dimension

Revenue comes from fact

---

# Star Schema

Kimball strongly recommends a **Star Schema**.

```
             dim_date

                 |

dim_customer --- fact_sales --- dim_product

                 |

             dim_store
```

Advantages

- Simple joins
    
- Fast queries
    
- Easy for analysts
    
- Good BI performance
    

---

# Snowflake Schema

Avoid unless necessary.

```
Product
   |
Category
   |
Department
```

Instead of

```
dim_product

category
department
brand
```

Kimball usually prefers putting everything into one dimension.

---

# Grain (Most Important Rule)

Kimball says:

> Declare the grain first.

Grain means

**What does one row represent?**

Examples

### Good

One row per invoice line

```
Invoice
Product
Quantity
```

or

One row per order

or

One row per customer per month

---

### Bad

Mixing

- Order
    
- Product
    
- Month
    

inside one table.

This causes double counting.

---

# Surrogate Keys

Use surrogate keys instead of business keys.

Example

Instead of

```
CustomerID = C1001
```

Use

```
CustomerKey = 1523
```

Reasons

- Business IDs change
    
- Easier Slowly Changing Dimensions
    
- Better joins
    
- Warehouse independence
    

---

# Natural Keys

Natural key

```
CustomerID = C1001
```

Surrogate key

```
CustomerKey = 101
```

Both are stored.

Fact table uses

```
CustomerKey
```

---

# Slowly Changing Dimensions (SCD)

Very important in Kimball.

---

## Type 1

Overwrite old value.

```
City

Old:
London

New:
Paris
```

No history.

---

## Type 2

Keep history.

Example

Customer moves city.

```
CustomerKey

101 London

202 Paris
```

Different surrogate keys.

Fact table continues pointing to the correct version.

Most common.

---

## Type 3

Store previous value.

```
Current City

Previous City
```

Rarely used.

---

# Conformed Dimensions

One dimension shared across many fact tables.

Example

```
dim_customer
```

Used by

```
fact_sales

fact_returns

fact_orders

fact_support
```

Everyone uses the same customer definition.

---

# Fact Types

## Transaction Fact

Every transaction.

```
Every Sale
```

---

## Periodic Snapshot

One row every day/month.

Example

```
Daily inventory
```

---

## Accumulating Snapshot

Tracks process.

```
Order Created

Packed

Shipped

Delivered
```

Updates over time.

---

# Degenerate Dimension

Dimension stored inside fact.

Example

```
Invoice Number
```

No separate table needed.

---

# Junk Dimension

Combine small flags.

Instead of

```
IsOnline

IsGift

IsDiscount
```

Make

```
dim_flags
```

---

# Role Playing Dimensions

One dimension used multiple times.

Example

```
dim_date
```

Used as

```
Order Date

Ship Date

Delivery Date
```

---

# Date Dimension

Never use raw dates everywhere.

Instead

```
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

# Fact Table Rules

Always

- Numeric measures
    
- Foreign keys only
    
- Lowest grain
    
- No descriptive columns
    

Good

```
customer_key
product_key
date_key
sales
quantity
```

Bad

```
customer_name
product_name
city
```

---

# Dimension Table Rules

Include

- Names
    
- Categories
    
- Attributes
    
- Hierarchies
    

Example

```
Product

Brand

Category

Subcategory

Color

Size
```

---

# Null Handling

Never leave foreign keys null.

Create

```
Unknown Customer
```

```
CustomerKey = 0
```

instead of NULL.

---

# Additive Facts

Can sum across all dimensions.

Example

```
Revenue

Quantity
```

---

# Semi-additive

Can sum over some dimensions.

Example

```
Bank Balance
```

Not across time.

---

# Non-additive

Cannot sum.

Example

```
Percentage

Ratio
```

---

# Naming Standards

Good

```
fact_sales

fact_orders

dim_customer

dim_product

dim_store
```

Avoid

```
tbl1

data

master
```

---

# Best Practices

### 1. Define grain first

Before creating any table, clearly state what a single row represents.

### 2. Prefer star schemas

Keep dimensions denormalized unless normalization provides a clear benefit.

### 3. Use surrogate keys

Maintain stable joins and support historical tracking.

### 4. Keep facts narrow

Store only keys and measures in fact tables.

### 5. Build conformed dimensions

Reuse dimensions like Customer, Product, and Date across multiple fact tables.

### 6. Use SCD Type 2 for history

Preserve changes to important business attributes over time.

### 7. Create a date dimension

Avoid repeated date calculations and provide consistent calendar logic.

### 8. Store data at the lowest grain

Aggregate in reports rather than in the warehouse whenever possible.

### 9. Handle unknown members explicitly

Use default dimension records (for example, key `0`) instead of `NULL` foreign keys.

### 10. Document business definitions

Ensure metrics like "Revenue", "Active Customer", and "Churn" have consistent definitions across the organization.

---

# Kimball in a dbt Project

A common dbt project aligns well with Kimball principles:

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
Dimensions (dim_*)
        +
Facts (fact_*)
    │
    ▼
Marts / BI
```

For example:

```
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

Since you're learning **dbt**, understanding Kimball's dimensional modeling will help you design marts that are easy to maintain, performant for analytics, and intuitive for business users. The key principles to remember are: **declare the grain first, model facts and dimensions separately, use star schemas, create conformed dimensions, and preserve history where needed with SCDs**.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Miscellaneous/Data Modeling|Data Modelling Masterclass for Data Engineers]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Spark/Miscellaneous/Types of Fact Table|Types of Fact Tables in Data Warehousing]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Miscellaneous/Fundamentals Of Data Engineering|Fundamentals Of Data Engineering]]

# Comprehensive Guide: Conformed Facts, Grain, and Conformed Dimensions

## 1. The Basic Idea

In dimensional modeling, three concepts must be kept separate:

```text
Grain
  ↓
What does one row represent?

Conformed Fact
  ↓
Does a measurement mean the same thing?

Conformed Dimension
  ↓
Is the descriptive context shared consistently?
```

---

# 2. Grain

**Grain defines the level of detail of a fact table.**

Example:

```text
fact_sales
```

Grain:

> One row represents one product on one order.

Another fact table:

```text
fact_monthly_sales
```

Grain:

> One row represents one product in one month.

Therefore:

```text
fact_sales
→ order-line grain

fact_monthly_sales
→ monthly-product grain
```

The grains are different, and that is completely valid.

---

# 3. Conformed Fact

A **conformed fact** is a measurement that has the **same business definition wherever it appears**.

Example:

```text
fact_store_sales
----------------
sales_amount

fact_online_sales
-----------------
sales_amount
```

Suppose both define `sales_amount` as:

> Net revenue after discounts and before tax.

Then:

```text
sales_amount
     ↓
same definition
     ↓
Conformed Fact
```

The fact tables can have different grains.

```text
fact_store_sales
→ one row per product per store per transaction

fact_online_sales
→ one row per product per online order
```

The grain does **not** have to be identical.

What must be identical is the **meaning of the measurement**.

---

# 4. Different Grain Does Not Prevent Conformed Facts

This is the most important point.

Suppose:

### Fact 1

```text
fact_order_sales

Grain:
one row per order line

Fact:
sales_amount
```

### Fact 2

```text
fact_daily_sales

Grain:
one row per product per day

Fact:
sales_amount
```

They have:

```text
Different grain
        ↓
Same sales_amount definition
        ↓
Conformed fact
```

However, you cannot simply join the two tables row-by-row because they represent different levels of detail.

You may need to aggregate:

```text
order-line sales
       ↓
product/day sales
```

before comparing them.

---

# 5. Why Grain Still Matters

Suppose:

```text
fact_order_sales

Order  Product  Sales
101    A        100
102    A        200
103    A        150
```

and:

```text
fact_daily_sales

Date       Product   Sales
Aug 10     A         450
```

Both use the same `sales_amount` definition.

But:

```text
fact_order_sales
→ 3 rows

fact_daily_sales
→ 1 row
```

You cannot say:

```text
100 = 450
```

because the rows represent different things.

Instead:

```text
100 + 200 + 150 = 450
```

After bringing both to the same analytical grain, they can be compared.

So:

> **Conformed fact determines whether the measurement is comparable. Grain determines how the rows must be interpreted and aggregated.**

---

# 6. Conformed Dimension

A **conformed dimension** is a dimension that is shared consistently across multiple fact tables.

Example:

```text
                 dim_product
                      |
             ┌────────┴────────┐
             ↓                 ↓
        fact_sales        fact_returns
```

Both fact tables use:

```text
product_key
```

from the same:

```text
dim_product
```

For example:

```text
dim_product
------------------------
product_key
product_name
brand
category
```

Now both sales and returns use the same definitions of:

```text
Product
Brand
Category
```

This allows you to analyze different business processes using the same context.

---

# 7. Conformed Dimension + Different Fact Tables

Imagine a retail company.

You have:

```text
dim_date
dim_product
dim_customer
```

and:

```text
fact_sales
fact_returns
fact_inventory
```

The relationships could be:

```text
                    dim_date
                       |
          ┌────────────┼────────────┐
          ↓            ↓            ↓
     fact_sales   fact_returns  fact_inventory
          ↑            ↑            ↑
          └──────── dim_product ────┘
```

Now you can ask:

> How much did we sell and how much did we return for each product?

Because both facts use the same `dim_product`.

---

# 8. Conformed Fact vs Conformed Dimension

This is the easiest way to remember the difference:

||Conformed Fact|Conformed Dimension|
|---|---|---|
|Represents|Measurement|Context|
|Example|`sales_amount`|`product`|
|Concern|Same definition|Same descriptive meaning|
|Shared across|Fact tables|Fact tables|
|Example question|Does sales amount mean the same thing?|Does Product A mean the same thing?|

### Conformed Fact

```text
sales_amount
     ↓
Measurement
     ↓
Same definition
```

### Conformed Dimension

```text
product
   ↓
Context
   ↓
Same definition
```

---

# 9. How They Work Together

Consider:

```text
                 dim_product
                      |
          ┌───────────┴───────────┐
          ↓                       ↓
   fact_store_sales        fact_online_sales
          |                       |
          ↓                       ↓
   sales_amount             sales_amount
```

Here:

### `dim_product`

is a **conformed dimension** because both facts use the same product definition.

### `sales_amount`

is a **conformed fact** if both facts use the same definition.

### Fact table grains

can still be different:

```text
store sales
→ product + store + transaction

online sales
→ product + order
```

That is perfectly valid.

---

# 10. What Happens If the Fact Definitions Differ?

Suppose:

```text
fact_store_sales
sales_amount = before tax

fact_online_sales
sales_amount = after tax
```

Now they are **not conformed facts**.

Using the same name creates confusion.

Conceptually, they should have different names, such as:

```text
store_sales_before_tax
online_sales_after_tax
```

The different names signal that they should not be treated as the same enterprise measurement.

---

# 11. The Core Rules

### Rule 1: Grain can differ

```text
Fact A → transaction grain
Fact B → daily grain
Fact C → monthly grain
```

All are valid.

### Rule 2: Conformed facts need the same definition

```text
sales_amount
     ↓
same business meaning
     ↓
conformed fact
```

### Rule 3: Conformed dimensions provide common context

```text
dim_product
dim_date
dim_customer
```

can be shared by multiple fact tables.

### Rule 4: Different grain means different row meaning

Never compare individual rows from different-grain fact tables without considering aggregation.

### Rule 5: Same name should mean same thing

If two facts have different definitions, they should not be presented as though they are the same measurement.

---

# 12. Final Mental Model

Think of it this way:

```text
                    FACT TABLE
                       │
              ┌────────┴────────┐
              │                 │
            GRAIN             FACTS
              │                 │
      "What is one row?"   "What do we measure?"
                                │
                                ↓
                         Conformed Fact
                         if definition
                         is consistent


                    DIMENSION
                       │
                       ↓
                Descriptive context
                       │
                       ↓
              Conformed Dimension
              if shared consistently
```

The three concepts answer three different questions:

> **Grain:** What does one row represent?

> **Conformed Fact:** Does this measurement mean the same thing across fact tables?

> **Conformed Dimension:** Does this descriptive context have the same definition across fact tables?

The crucial relationship is:

```text
Different grain
      ↓
ALLOWED

Same fact definition
      ↓
Conformed Fact

Same shared dimension definition
      ↓
Conformed Dimension
```

So **grain is about the level of detail, conformed facts are about measurements, and conformed dimensions are about shared analytical context.**
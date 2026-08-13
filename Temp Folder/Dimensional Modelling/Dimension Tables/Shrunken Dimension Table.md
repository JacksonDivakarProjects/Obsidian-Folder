# Shrunken Dimension — Clear Guide

## 1. First: the core definition

A **shrunken dimension** is a **conformed dimension that is a subset of a base dimension**.

The subset can be:

1. **Fewer columns**
    
2. **Fewer rows**
    
3. **A higher-level rollup**
    
4. **A combination of these**
    

The main reason is that **different fact tables can have different grains**.

---

# 2. Start with the base dimension

Imagine a company sells products.

The enterprise has this detailed product dimension:

### `Dim_Product`

|Product_Key|Product|Brand|Category|Department|Color|
|--:|---|---|---|---|---|
|101|Laptop A|Dell|Laptop|Electronics|Silver|
|102|Laptop B|Dell|Laptop|Electronics|Black|
|103|Mouse A|Logitech|Mouse|Electronics|Black|
|104|Mouse B|Logitech|Mouse|Electronics|White|
|105|Shirt A|Nike|Shirt|Clothing|Blue|

This is the **base dimension**.

Its grain is:

> **One row = one product**

---

# 3. Now look at two different business processes

### Business Process 1: Sales

Sales captures:

> **One product sold on one day**

Therefore:

```text
Fact_Sales
Grain = Date + Product
```

Example:

|Date_Key|Product_Key|Sales_Amount|
|--:|--:|--:|
|20260101|101|1000|
|20260101|102|1500|
|20260101|103|200|
|20260102|101|1200|

This is detailed.

---

### Business Process 2: Forecast

The planning department doesn't forecast individual products every day.

It forecasts:

> **One brand per month**

Therefore:

```text
Fact_Forecast
Grain = Month + Brand
```

Example:

|Month_Key|Brand_Key|Forecast_Amount|
|--:|--:|--:|
|202601|1|50000|
|202601|2|30000|
|202602|1|55000|

Notice:

**Sales:**

```text
Date + Product
```

**Forecast:**

```text
Month + Brand
```

These are different grains.

---

# 4. Why can't Forecast simply use `Dim_Product`?

Because the forecast doesn't know the individual product.

Suppose the forecast says:

```text
January 2026
Dell
₹50,000
```

It does **not** say:

```text
Laptop A → ₹20,000
Laptop B → ₹30,000
```

It only knows:

```text
Brand = Dell
```

Therefore, using the detailed `Dim_Product` would imply a level of detail that doesn't exist in the forecast data.

We need a dimension at the appropriate level:

```text
Product
   ↓
Brand
```

---

# 5. Create the shrunken rollup dimension

From the detailed product dimension:

|Product_Key|Product|Brand|Category|
|--:|---|---|---|
|101|Laptop A|Dell|Laptop|
|102|Laptop B|Dell|Laptop|
|103|Mouse A|Logitech|Mouse|
|104|Mouse B|Logitech|Mouse|
|105|Shirt A|Nike|Shirt|

We create:

### `Dim_Brand`

|Brand_Key|Brand|Category|
|--:|---|---|
|1|Dell|Laptop|
|2|Logitech|Mouse|
|3|Nike|Shirt|

This is a **shrunken rollup dimension**.

Why?

Because:

```text
Base dimension:
Product
   ↓
Shrunken dimension:
Brand
```

The level of detail has been reduced.

---

# 6. The complete model

Now the warehouse looks like this:

```text
                 Dim_Date
                    |
                    |
              Fact_Sales
                    |
                    |
              Dim_Product
```

Sales grain:

```text
Date + Product
```

And:

```text
                 Dim_Month
                    |
                    |
             Fact_Forecast
                    |
                    |
                Dim_Brand
```

Forecast grain:

```text
Month + Brand
```

The dimensions are appropriate for the grains of their respective facts.

---

# 7. Why is `Dim_Brand` called "conformed"?

Because `Brand` must have the **same business meaning** everywhere.

Suppose the enterprise definition is:

> Dell = Dell brand products.

Then:

```text
Dim_Product
      ↓
Brand = Dell
```

and:

```text
Dim_Brand
      ↓
Brand = Dell
```

must mean the same thing.

The forecast cannot define Dell differently from sales.

That's why the shrunken dimension is **conformed**.

---

# 8. What exactly was "shrunk"?

There are several possibilities.

## Type A: Fewer columns

Suppose you have:

|Product_Key|Product|Brand|Category|Color|Size|
|--:|---|---|---|---|---|
|101|Laptop A|Dell|Laptop|Silver|15"|
|102|Laptop B|Dell|Laptop|Black|14"|

A process only needs:

|Product_Key|Product|Brand|
|--:|---|---|
|101|Laptop A|Dell|
|102|Laptop B|Dell|

Same rows, fewer columns.

```text
Base Dimension
       ↓
remove columns
       ↓
Shrunken Dimension
```

---

# 9. Type B: Fewer rows

Suppose the full customer dimension contains:

|Customer_Key|Customer|Customer_Type|
|--:|---|---|
|1|Ravi|Retail|
|2|Arun|Retail|
|3|ABC Corp|Enterprise|
|4|XYZ Ltd|Enterprise|

A business process only deals with enterprise customers.

The subset becomes:

|Customer_Key|Customer|Customer_Type|
|--:|---|---|
|3|ABC Corp|Enterprise|
|4|XYZ Ltd|Enterprise|

Same grain:

> One row = one customer

But fewer rows.

This is a **row-subset shrunken dimension**.

---

# 10. Type C: Rollup to a higher level

This is the most important case when discussing aggregate facts.

Base:

```text
Product
   ↓
Brand
   ↓
Category
```

If a fact is captured at:

```text
Month + Brand
```

you need the Brand-level dimension.

If another fact is captured at:

```text
Quarter + Category
```

you may need a Category-level dimension.

So:

```text
Detailed Dimension
       ↓
      shrink
       ↓
Higher-level dimension
```

---

# 11. Why not just use the detailed dimension and GROUP BY?

This is an important question.

Suppose your detailed sales fact is:

```text
Date + Product
```

You can absolutely calculate:

```sql
GROUP BY Brand
```

using the detailed product dimension.

For example:

```sql
SELECT
    p.Brand,
    SUM(f.Sales_Amount)
FROM Fact_Sales f
JOIN Dim_Product p
    ON f.Product_Key = p.Product_Key
GROUP BY p.Brand;
```

That's perfectly valid.

But the **forecast fact is different**.

Forecast doesn't contain product-level facts that can be grouped upward.

Its actual grain is already:

```text
Month + Brand
```

Therefore, it needs a dimension appropriate to that grain.

This is the key difference.

---

# 12. Atomic fact vs aggregate fact

### Atomic Sales

```text
Fact_Sales
Grain:
One Product + One Date
```

You have:

```text
Laptop A
Laptop B
Mouse A
Mouse B
```

You can aggregate them upward:

```text
Product
   ↓
Brand
   ↓
Category
```

### Forecast

```text
Fact_Forecast
Grain:
One Brand + One Month
```

You don't have product-level forecast records.

Therefore:

```text
Brand
```

is already the natural grain.

A detailed `Product` dimension would not match the fact's grain.

---

# 13. Perfect example: Actual vs Forecast

This is where the concept becomes very useful.

Suppose management wants:

> "Show actual sales and forecast by month and brand."

### Actual Sales

Original grain:

```text
Date + Product
```

You aggregate actual sales to:

```text
Month + Brand
```

### Forecast

Natural grain:

```text
Month + Brand
```

Now both are at the same analytical grain:

```text
Month + Brand
```

Result:

|Month|Brand|Actual Sales|Forecast|
|---|---|--:|--:|
|Jan|Dell|₹48,000|₹50,000|
|Jan|Logitech|₹28,000|₹30,000|
|Feb|Dell|₹53,000|₹55,000|

This works because both processes use consistent dimensions at the required grain.

---

# 14. Shrunken dimension vs normal dimension

||Base Dimension|Shrunken Dimension|
|---|---|---|
|Purpose|Enterprise-wide detailed analysis|Support a particular fact/process|
|Rows|Full set|Subset may be used|
|Columns|Full attributes|Subset may be used|
|Grain|Detailed|Same or higher-level|
|Conformed?|Yes|Yes, if properly derived|
|Example|Product|Brand|
|Example|All Customers|Enterprise Customers|

---

# 15. The three cases to memorize

### Case 1 — Column subset

```text
Dim_Product
    ↓
Remove Color, Size, Weight
    ↓
Smaller Product Dimension
```

**Same rows, fewer attributes.**

---

### Case 2 — Row subset

```text
Dim_Customer
    ↓
Keep only Enterprise Customers
    ↓
Smaller Customer Dimension
```

**Same grain, fewer members.**

---

### Case 3 — Rollup

```text
Dim_Product
    ↓
Product → Brand
    ↓
Dim_Brand
```

**Higher level of detail.**

---

# 16. The most important rule

A shrunken dimension is **not created just because you want a smaller table**.

It exists because a particular business process/fact table has a **different dimensional requirement**.

Think:

```text
What is the fact grain?
        ↓
What dimensions describe that grain?
        ↓
Does the detailed enterprise dimension match?
        ↓
If not, create/use an appropriate shrunken dimension.
```

---

# 17. Relationship with conformed dimensions

The complete idea is:

```text
                    Enterprise
                 Conformed Dimensions
                         |
              ┌──────────┼──────────┐
              ↓          ↓          ↓
           Product      Date       Store
              |          |          |
              |          |          |
              ↓          ↓          ↓
         Sales Fact
         Date + Product + Store


              ↓ shrink/rollup


              Brand      Month     Region
                |          |          |
                |          |          |
                ↓          ↓          ↓
             Forecast Fact
             Month + Brand + Region
```

The smaller dimensions remain **conformed** because they preserve the enterprise's agreed definitions.

---

# 18. Final mental model

Think of the enterprise dimension as the **full detailed dictionary**.

```text
Dim_Product
│
├── Product
├── Brand
├── Category
├── Department
├── Color
├── Size
└── ...
```

Different fact tables need different levels:

```text
Sales
→ Product + Date

Forecast
→ Brand + Month

Strategic Planning
→ Category + Quarter
```

Therefore:

```text
              Full Enterprise Dimensions
                       │
             ┌─────────┼─────────┐
             ↓         ↓         ↓
          Product     Brand    Category
             │         │         │
             ↓         ↓         ↓
           Sales    Forecast   Planning
```

### One-sentence definition to remember

> **A shrunken dimension is a conformed subset of a detailed enterprise dimension, reduced in rows, columns, and/or level of detail so that it correctly matches the grain of a particular fact table.**

The most important example is:

```text
Fact_Sales
Grain = Date + Product

Fact_Forecast
Grain = Month + Brand

Therefore:

Dim_Date      → Dim_Month
Dim_Product   → Dim_Brand

These reduced dimensions are shrunken dimensions.
```
# Comprehensive Guide: Multiple Units of Measure Facts

The easiest way to understand this pattern is to start with the **problem**, then see why Kimball recommends the **standard-unit + conversion-factor** solution.

---

## 1. The problem

A business process may measure the **same physical quantity** in different units.

For example, a supply-chain company may talk about product quantities as:

```text
Pallets
Ship Cases
Retail Cases
Individual Units
```

Suppose one shipment contains:

```text
1 pallet
= 10 ship cases
= 20 retail cases
= 240 individual units
```

Different departments want different views:

|User|Preferred unit|
|---|---|
|Warehouse|Pallets|
|Logistics|Ship cases|
|Retail|Retail cases|
|Store operations|Individual units|

The business is talking about **the same shipment**, but wants to express it differently.

---

# 2. First principle: define the grain

Suppose our fact table has this grain:

> **One row = one shipment line.**

For example:

|Shipment|Product|Quantity|
|---|---|--:|
|1001|Product A|1,200|

The question becomes:

> In what unit should `1,200` be stored?

Kimball recommends agreeing on a **standard/base unit of measure**.

Let's choose:

> **Individual scan units**

So:

```text
standard_quantity = 1,200 individual units
```

---

# 3. Why not store every unit separately?

You could do this:

|Shipment|Pallets|Ship Cases|Retail Cases|Individual Units|
|---|--:|--:|--:|--:|
|1001|5|50|100|1,200|

That looks harmless when you have only **one quantity**.

But real fact tables may have many measures.

Suppose you have:

```text
shipped_quantity
received_quantity
damaged_quantity
returned_quantity
allocated_quantity
backordered_quantity
```

And every one must be available in:

```text
pallets
ship cases
retail cases
individual units
```

You could end up with:

```text
shipped_pallets
shipped_cases
shipped_retail_cases
shipped_units

received_pallets
received_cases
received_retail_cases
received_units

damaged_pallets
damaged_cases
damaged_retail_cases
damaged_units

...
```

The number of measure columns grows rapidly.

### The basic problem is:

```text
Number of measures
        ×
Number of units
        =
Many duplicated measure columns
```

---

# 4. Kimball's solution

Instead of storing the same measure repeatedly in every unit:

### Store the measure once in a standard unit.

Then:

### Store the applicable conversion factors in the same fact row.

So the fact table might look like:

|Shipment|Product|Standard Qty|Pallet Factor|Ship Case Factor|Retail Case Factor|
|---|---|--:|--:|--:|--:|
|1001|A|1,200|240|24|12|

This is **ONE fact table**.

Not two fact tables.

---

# 5. What does each column mean?

This is extremely important.

### `standard_quantity`

This is the **actual business measure**.

```text
standard_quantity = 1,200
```

Meaning:

> This shipment contains 1,200 standard units.

---

### `pallet_factor`

```text
pallet_factor = 240
```

Meaning:

> 1 pallet contains 240 standard units.

---

### `ship_case_factor`

```text
ship_case_factor = 24
```

Meaning:

> 1 ship case contains 24 standard units.

---

### `retail_case_factor`

```text
retail_case_factor = 12
```

Meaning:

> 1 retail case contains 12 standard units.

So conceptually:

```text
                 ONE FACT ROW
                      │
          ┌───────────┴───────────┐
          ↓                       ↓
 Standard Quantity          Conversion Factors
     1,200 units             240 / 24 / 12
          │                       │
          └───────────┬───────────┘
                      ↓
             Derived quantities
```

---

# 6. How do we calculate other units?

### Pallets

```text
1,200 / 240 = 5 pallets
```

### Ship cases

```text
1,200 / 24 = 50 ship cases
```

### Retail cases

```text
1,200 / 12 = 100 retail cases
```

So you haven't stored:

```text
5 pallets
50 ship cases
100 retail cases
```

as separate measures.

You have stored:

```text
1,200 standard units
```

and the conversion information needed to derive them.

---

# 7. Now imagine multiple facts

This is where the technique becomes really valuable.

Suppose the fact table contains:

|Shipment|Shipped|Received|Damaged|Returned|
|---|--:|--:|--:|--:|
|1001|1,200|1,100|20|10|

All of these are stored in the **standard unit**.

And the same row contains:

|Shipment|Pallet Factor|Case Factor|
|---|--:|--:|
|1001|240|24|

Now you can calculate:

### Shipped pallets

```text
1,200 / 240 = 5
```

### Received pallets

```text
1,100 / 240 = 4.5833
```

### Damaged pallets

```text
20 / 240 = 0.0833
```

### Shipped cases

```text
1,200 / 24 = 50
```

The conversion factors are reused across all the measures in that fact row.

That's why you avoid creating dozens of duplicate measures.

---

# 8. Why must the conversion factor be in the fact table?

This is one of the most important points in the paragraph.

You might think:

> "Why not have a separate conversion table?"

For example:

```text
DIM_PRODUCT_CONVERSION

Product | Pallet Factor | Case Factor
A       | 240           | 24
B       | 300           | 30
```

Sometimes a separate conversion structure can be appropriate in other designs.

But **the technique described in this paragraph specifically wants the conversion factors in the underlying fact row.**

Why?

Because the conversion factor may depend on the **specific transaction/event context**.

---

# 9. Conversion factors can change

Suppose Product A normally has:

```text
1 pallet = 240 units
```

But packaging changes later:

```text
1 pallet = 300 units
```

Consider two shipments.

### Old shipment

|Shipment|Date|Quantity|Pallet Factor|
|---|---|--:|--:|
|1001|Jan 2025|1,200|240|

### New shipment

|Shipment|Date|Quantity|Pallet Factor|
|---|---|--:|--:|
|2001|Jan 2026|1,200|300|

The same `1,200` units represent:

```text
Shipment 1001:
1,200 / 240 = 5 pallets

Shipment 2001:
1,200 / 300 = 4 pallets
```

If you simply look up today's conversion factor, you could incorrectly reinterpret historical transactions.

Therefore:

> **The fact row preserves the conversion context that applies to that transaction.**

---

# 10. Why does Kimball say "conversion factors must reside in the underlying fact table row"?

Because the query should be simple.

Suppose the fact contains:

```text
standard_quantity = 1,200
pallet_factor = 240
```

Then a view can simply expose:

```text
standard_quantity / pallet_factor
```

and return:

```text
5 pallets
```

No complicated joins or business logic are required in the user-facing query.

---

# 11. What is a view doing here?

A **view** can provide different representations to different users.

Underlying fact:

|Shipment|Standard Qty|Pallet Factor|Case Factor|
|---|--:|--:|--:|
|1001|1,200|240|24|

### Warehouse view

Could expose:

|Shipment|Quantity in Pallets|
|---|--:|
|1001|5|

### Logistics view

Could expose:

|Shipment|Quantity in Ship Cases|
|---|--:|
|1001|50|

### Retail view

Could expose:

|Shipment|Quantity in Retail Cases|
|---|--:|
|1001|100|

But underneath, they're all reading from:

```text
ONE FACT TABLE
```

---

# 12. Why views instead of physically storing all versions?

Because you don't need to physically store:

```text
5 pallets
50 ship cases
100 retail cases
```

when they can be derived from:

```text
1,200 standard units
```

plus:

```text
conversion factors
```

So the physical model stays relatively compact.

---

# 13. Important distinction: quantity vs conversion factor

Don't confuse these.

### Quantity

Answers:

> **How much product was involved?**

Example:

```text
1,200 units
```

### Conversion factor

Answers:

> **How many standard units correspond to one alternative unit?**

Example:

```text
240 units = 1 pallet
```

Therefore:

```text
1,200 units
────────────── = 5 pallets
240 units/pallet
```

---

# 14. Is the conversion factor a fact?

It's a **numeric column stored in the fact table**, but conceptually don't think of it as a normal business measure like:

```text
sales_amount
quantity
cost
```

It's **context needed to interpret/convert the measure**.

The fact row therefore contains:

```text
Measures
──────────────
standard_quantity
sales_amount
cost
...

Conversion context
──────────────────
pallet_factor
case_factor
...
```

---

# 15. Why standardize the unit?

Because it gives the enterprise a common base.

Imagine different systems report:

```text
Warehouse → pallets
Shipping  → cases
Retail    → units
Finance   → kilograms
```

If you don't establish a standard, comparison becomes messy.

With a standard unit:

```text
All quantities
      ↓
Standard unit
      ↓
Fact table
      ↓
Convert for presentation
```

This makes aggregation much safer.

---

# 16. A major benefit: aggregation

Suppose you have two shipments:

|Shipment|Standard Qty|Pallet Factor|
|---|--:|--:|
|1001|1,200|240|
|1002|2,400|240|

You can safely aggregate the standard quantity:

```text
1,200 + 2,400 = 3,600 units
```

Then convert:

```text
3,600 / 240 = 15 pallets
```

This is preferable to maintaining independent versions of every quantity.

---

# 17. But be careful with aggregation when conversion factors differ

Suppose:

|Shipment|Standard Qty|Pallet Factor|
|---|--:|--:|
|1001|1,200|240|
|1002|1,200|300|

You **cannot** simply say:

```text
2,400 / 240
```

because the second shipment uses a different conversion.

You need to respect the applicable conversion context.

At the individual row:

```text
1001 → 1,200 / 240 = 5 pallets
1002 → 1,200 / 300 = 4 pallets
```

Total:

```text
5 + 4 = 9 pallets
```

This is another reason why the conversion factor belongs with the fact row.

---

# 18. The overall architecture

Think of the whole design like this:

```text
                   OPERATIONAL SOURCES
                           │
                           ↓
                    ETL / ELT
                           │
                           ↓
                 STANDARDIZE QUANTITY
                           │
                           ↓
              ┌─────────────────────────┐
              │      FACT TABLE         │
              │                         │
              │ standard_quantity       │
              │ pallet_factor           │
              │ ship_case_factor        │
              │ retail_case_factor      │
              │                         │
              │ other facts...          │
              └────────────┬────────────┘
                           │
                 ┌─────────┼─────────┐
                 ↓         ↓         ↓
             Warehouse  Logistics  Retail
                View       View      View
                 ↓         ↓         ↓
             Pallets    Cases      Units
```

---

# 19. The thing you were confused about earlier

You asked whether it means:

> "standard measure in one fact and conversion in another fact table"

**No.**

It is:

```text
                 ONE FACT TABLE

┌──────────────────────────────────────┐
│ Dimensions                           │
│ customer_key                         │
│ product_key                          │
│ date_key                             │
│                                      │
│ Standard measures                    │
│ standard_quantity                    │
│ other_measure                        │
│                                      │
│ Conversion factors                   │
│ pallet_factor                        │
│ case_factor                          │
│ retail_case_factor                   │
└──────────────────────────────────────┘
```

One row contains both.

---

# 20. Why this solves the original problem

### Without the technique

If you have:

```text
10 measures
×
5 units
```

you could end up with:

```text
50 measure columns
```

### With the technique

You have:

```text
10 standard measures
+
5 conversion factors
```

So:

```text
15 columns
```

instead of potentially 50.

And the conversion factors can be reused across the measures.

---

# 21. Where does ETL fit?

ETL is responsible for making sure:

1. The quantity is converted to the agreed standard unit.
    
2. The correct conversion factors are determined.
    
3. Those conversion factors are stored with the fact row.
    
4. Historical/context-specific conversion information is preserved where necessary.
    

For example:

```text
Source says:
5 pallets

ETL knows:
1 pallet = 240 standard units

Therefore:
standard_quantity = 5 × 240
                  = 1,200 units
```

And it stores:

```text
standard_quantity = 1,200
pallet_factor = 240
```

---

# 22. What the user sees

The business user doesn't necessarily need to know all this.

They might simply see:

### Warehouse

```text
Shipment 1001 → 5 pallets
```

### Logistics

```text
Shipment 1001 → 50 cases
```

### Retail

```text
Shipment 1001 → 100 retail cases
```

But underneath:

```text
             SAME FACT ROW
                  │
        ┌─────────┴─────────┐
        ↓                   ↓
  1,200 standard        conversion
      units              factors
        │                   │
        └─────────┬─────────┘
                  ↓
          Different views
```

---

# 23. The Pareto version

If you remember only **five things**, remember these:

### 1. Pick a standard unit

Example:

```text
Individual units
```

### 2. Store each measure once

```text
shipped_qty = 1,200
```

Don't store:

```text
shipped_pallets
shipped_cases
shipped_units
```

as separate physical measures.

### 3. Store conversion factors in the same fact row

```text
pallet_factor = 240
case_factor = 24
```

### 4. Derive alternative units

```text
1,200 / 240 = 5 pallets
1,200 / 24 = 50 cases
```

### 5. Use views for different user perspectives

```text
FACT TABLE
     ↓
 ┌───┼────┐
 ↓   ↓    ↓
Pallet Case Units
View  View View
```

---

## Final mental model

The entire concept can be reduced to:

```text
          "How much?"
              │
              ↓
      STANDARD QUANTITY
          1,200 units
              │
              │
       "How do I convert?"
              │
       ┌──────┼──────┐
       ↓      ↓      ↓
     /240   /24    /12
       ↓      ↓      ↓
    Pallets Cases Retail
       5      50     100
```

**The fact table stores the quantity once, in a standard unit, and stores the applicable conversion factors alongside it. The alternative units are derived rather than duplicated.**
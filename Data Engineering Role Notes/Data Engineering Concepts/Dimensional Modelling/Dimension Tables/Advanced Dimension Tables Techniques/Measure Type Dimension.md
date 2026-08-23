# Comprehensive Guide: Measure Type Dimensions in Dimensional Modeling

The idea of a **Measure Type Dimension** is one of those Kimball concepts that looks attractive at first because it solves a visible problem—**lots of NULL measure columns**—but can create a much bigger analytical problem.

The core question is:

> **Should different measurements be stored as separate columns, or should they be stored as rows identified by a measure type?**

---

## 1. Start with the normal fact table

Suppose you're tracking financial transactions.

Your natural fact table might be:

|Transaction|Sales|Discount|Tax|Refund|Shipping|
|---|--:|--:|--:|--:|--:|
|T1|500|20|50|NULL|NULL|
|T2|NULL|NULL|NULL|100|NULL|
|T3|800|30|80|NULL|40|

Each **row has the same grain**:

> One row = one transaction.

The measures are separate columns:

```text
fact_transaction
────────────────────────────────
transaction_key
customer_key
date_key
sales_amount
discount_amount
tax_amount
refund_amount
shipping_amount
```

This is the **preferred dimensional-modeling approach in most cases**.

---

# 2. What problem are we trying to solve?

Look at T1:

```text
Sales       = 500
Discount    = 20
Tax         = 50
Refund      = NULL
Shipping    = NULL
```

There are empty columns.

Now imagine you have **200 possible measures**:

```text
measure_001
measure_002
measure_003
...
measure_200
```

but each transaction only uses 2–3 of them.

Your fact table could become:

```text
transaction
measure_001
measure_002
measure_003
...
measure_200
```

with most columns being NULL for most rows.

Someone might propose:

> "Instead of having 200 columns, let's put the measure name in a dimension and store the actual value in one generic column."

That's the **Measure Type Dimension** approach.

---

# 3. What is a Measure Type Dimension?

Instead of this:

|Transaction|Sales|Tax|Refund|
|---|--:|--:|--:|
|T1|500|50|NULL|
|T2|NULL|NULL|100|

you create:

### `dim_measure_type`

|measure_type_key|measure_type|
|--:|---|
|1|Sales|
|2|Tax|
|3|Refund|

And the fact becomes:

### `fact_transaction_measure`

|Transaction|measure_type_key|amount|
|---|--:|--:|
|T1|1|500|
|T1|2|50|
|T2|3|100|

So the measure name has moved from a **column name** into a **dimension attribute**.

---

# 4. The transformation

Think of it as:

```text
                 NORMAL FACT

Transaction | Sales | Tax | Refund
------------|-------|-----|-------
T1          | 500   | 50  | NULL
T2          | NULL  | NULL| 100
```

becoming:

```text
              MEASURE-TYPE FACT

Transaction | Measure Type | Amount
------------|--------------|-------
T1          | Sales        | 500
T1          | Tax          | 50
T2          | Refund       | 100
```

The **columns become rows**.

This is the fundamental transformation.

---

# 5. Why is it tempting?

Because the second design eliminates the NULL measure columns.

Normal:

```text
Sales | Tax | Refund | Shipping | Commission | ...
500   | 50  | NULL   | NULL     | NULL       | ...
```

Measure-type design:

```text
Measure Type | Amount
-------------|-------
Sales        | 500
Tax          | 50
```

Everything that actually exists gets a row.

So you might think:

> "This is much cleaner."

But Kimball says: **be careful.**

---

# 6. Problem #1 — Fact table row explosion

This is one of the most important things to understand.

Suppose your original fact has:

**1 million transactions**

and each transaction has, on average, **5 populated measures**.

Normal design:

```text
1 million transactions
        ↓
1 million fact rows
```

Measure-type design:

```text
1 million transactions
×
5 occupied measures
        ↓
≈ 5 million fact rows
```

So you have multiplied your fact table by the **average number of occupied measure columns per original row**.

That's exactly what the book means by:

> "it multiplies the size of the fact table by the average number of occupied columns in each row."

---

# 7. Example of row multiplication

Suppose:

|Transaction|Sales|Tax|Refund|Shipping|
|---|--:|--:|--:|--:|
|T1|500|50|NULL|NULL|
|T2|700|70|NULL|30|
|T3|NULL|NULL|100|NULL|

There are:

```text
3 original rows
```

The number of populated measures is:

```text
T1 = 2
T2 = 3
T3 = 1
```

Total:

```text
2 + 3 + 1 = 6
```

So the measure-type fact contains:

```text
6 rows
```

instead of:

```text
3 rows
```

The average number of populated measures is:

```text
6 / 3 = 2
```

Therefore:

```text
3 × 2 = 6 rows
```

---

# 8. Problem #2 — Calculations become harder

This is arguably the **more important analytical problem**.

Suppose you want:

```text
Net Sales = Sales - Discount
```

With the normal fact:

|Sales|Discount|
|--:|--:|
|500|20|

It's trivial:

```text
500 - 20 = 480
```

SQL is straightforward:

```sql
SELECT
    sales_amount - discount_amount AS net_sales
FROM fact_sales;
```

Because Sales and Discount are separate columns.

---

# 9. What happens with a Measure Type Dimension?

Now your data is:

|Transaction|Measure Type|Amount|
|---|---|--:|
|T1|Sales|500|
|T1|Discount|20|

You need to retrieve two different rows:

```text
Sales     → 500
Discount  → 20
```

and then calculate:

```text
500 - 20 = 480
```

You may need conditional aggregation:

```sql
SELECT
    transaction_key,
    SUM(CASE
        WHEN measure_type = 'Sales'
        THEN amount ELSE 0
    END)
    -
    SUM(CASE
        WHEN measure_type = 'Discount'
        THEN amount ELSE 0
    END) AS net_sales
FROM fact_transaction_measure
GROUP BY transaction_key;
```

Much more complicated.

---

# 10. This is what "intra-column computations" means

This phrase can be confusing.

The normal fact has:

```text
Sales
Discount
Tax
Refund
```

as **different columns**.

Therefore you can easily perform calculations **across those columns**:

```text
Sales - Discount
Sales + Tax
Sales - Refund
Tax / Sales
```

With the measure-type approach, everything is in:

```text
Amount
```

and the type is in another column:

```text
Measure Type | Amount
-------------|-------
Sales        | 500
Discount     | 20
Tax          | 50
```

Now Sales and Discount aren't physically separate columns.

They're **different rows in the same column**.

That's why calculations involving multiple measures become harder.

---

# 11. The conceptual difference

### Normal fact

```text
                COLUMNS
                   ↓

Transaction | Sales | Discount | Tax
```

The **measure itself is represented by a column**.

### Measure-type fact

```text
                  ROWS
                   ↓

Transaction | Measure Type | Amount
```

The **measure itself is represented by a row**.

This is the most important mental model to remember.

---

# 12. Why does the book still allow it?

Because there are situations where the normal design becomes ridiculous.

Imagine:

```text
Potential measures = 500
```

but each transaction only has:

```text
Average populated measures = 2
```

Normal fact:

```text
500 measure columns
```

For a typical transaction:

```text
498 NULLs
2 actual values
```

That's extremely sparse.

The measure-type design would instead look like:

```text
Transaction | Measure Type | Value
T1          | M034         | 500
T1          | M412         | 20
```

Now you're only storing the two actual measurements.

That can be reasonable.

---

# 13. The Pareto rule from the book

The book gives you a very useful practical guideline:

### Don't use Measure Type Dimensions when:

```text
Potential measures = relatively small
AND
Several measures are populated per fact row
```

For example:

```text
10 possible measures
5 populated per row
```

Keep them as columns.

---

### Consider Measure Type Dimensions when:

```text
Potential measures = extreme
AND
Only a handful are populated per fact row
```

For example:

```text
300 possible measures
2 populated per row
```

Now the trade-off may be worthwhile.

---

# 14. A useful decision framework

|Situation|Recommended|
|---|---|
|5–20 measures|Separate fact columns|
|20–50 measures|Usually separate columns|
|Hundreds of possible measures|Consider measure type|
|Many measures populated per row|Separate columns|
|Only 1–3 measures populated per row|Measure type may be reasonable|
|Frequent calculations between measures|Separate columns|
|Measures are fundamentally different|Separate columns|
|Extremely sparse/extensible measurements|Measure type may be useful|

These aren't hard numerical rules. The **nature of the data and analytical requirements** matter more than an exact threshold.

---

# 15. Don't confuse this with an EAV model

The Measure Type Dimension approach is closely related to an **Entity-Attribute-Value (EAV)** pattern.

Conceptually:

```text
Entity | Attribute | Value
-------|-----------|------
T1     | Sales     | 500
T1     | Tax       | 50
T2     | Refund    | 100
```

That's very flexible.

But dimensional models generally prefer:

```text
Fact
──────────────
Sales
Tax
Refund
```

when the measures are known and commonly analyzed.

Why?

Because dimensional models optimize for:

> **Understandability + predictable analytical performance**

rather than maximum schema flexibility.

---

# 16. Another important issue: different measures may have different meanings

Suppose you have:

```text
Sales = $500
Quantity = 10
Discount = $20
Margin % = 25%
```

Putting all of these into:

```text
measure_type | value
```

means your generic `value` column potentially contains:

```text
dollars
units
percentage
```

That creates semantic challenges.

For example:

```text
Sales = 500
Quantity = 10
Margin % = 25
```

What exactly does `value = 25` mean?

The `measure_type` tells you, but your semantic layer and BI tools now have to understand those types correctly.

With separate columns:

```text
sales_amount
quantity
margin_percent
```

the meaning is much more obvious.

---

# 17. Aggregation can also become tricky

Consider:

```text
Sales = 500
Quantity = 10
Margin % = 25%
```

You cannot blindly do:

```text
SUM(value)
```

across all rows.

You need to know:

```text
Sales       → SUM
Quantity    → SUM
Margin %    → weighted calculation
```

So the measure type dimension may need metadata such as:

|measure_type|aggregation_rule|unit|
|---|---|---|
|Sales|SUM|USD|
|Quantity|SUM|Units|
|Margin %|Weighted|%|

This adds complexity to your analytical layer.

---

# 18. A very important distinction: facts vs measures

Don't interpret the design as:

> "Every fact should become a measure type."

That's not the idea.

A **fact table still represents a business process at a declared grain**.

The question is only about **how the measurements associated with that grain are physically represented**.

Normal:

```text
Grain = one transaction

Transaction
   ├── Sales
   ├── Discount
   ├── Tax
   └── Shipping
```

Measure type:

```text
Grain effectively becomes:

one transaction + one measure type
```

So the grain changes.

This is extremely important.

---

# 19. Grain changes

Suppose the original fact has:

> **One row per transaction**

Then:

```text
T1001
```

is one fact row.

With measure type:

```text
T1001 + Sales
T1001 + Discount
T1001 + Tax
```

are separate rows.

Therefore the grain becomes:

> **One transaction + one measure type**

This is one of the first things you should identify when evaluating this design.

---

# 20. Why this matters for counting

Suppose you want:

```sql
COUNT(*)
```

Normal fact:

```text
1 transaction = 1 row
```

Therefore:

```text
COUNT(*) = number of transactions
```

Easy.

Measure-type fact:

```text
T1 + Sales
T1 + Tax
T1 + Discount
```

That's three rows for one transaction.

So:

```sql
COUNT(*)
```

would return:

```text
3
```

when there was only:

```text
1 transaction
```

You may need:

```sql
COUNT(DISTINCT transaction_key)
```

instead.

Again, analytical complexity increases.

---

# 21. What happens to dimensions?

Suppose you have:

```text
fact_transaction_measure
```

with:

```text
date_key
customer_key
product_key
measure_type_key
amount
```

Then you can still connect normal dimensions:

```text
             dim_customer
                   │
                   ▼
             fact_measure
                   ▲
                   │
             dim_product
                   │
                   │
             dim_date
                   │
                   │
           dim_measure_type
```

The Measure Type Dimension is simply another dimension associated with the fact.

---

# 22. What should you remember for exams/interviews?

The entire section can be reduced to **four ideas**.

### 1. Why introduce it?

Because a fact table has:

> **many potential measures but only a few populated in each row.**

---

### 2. What does it do?

It converts:

```text
measure columns
```

into:

```text
measure-type rows
```

using:

```text
measure_type_key
+
generic value/amount
```

---

### 3. What are the disadvantages?

Two major ones:

**A. Fact table gets larger**

```text
1 row → multiple rows
```

**B. Calculations become harder**

```text
Sales - Discount
```

requires finding different measure-type rows rather than simply subtracting columns.

---

### 4. When is it acceptable?

When:

```text
potential measures = extremely high
AND
populated measures per row = very low
```

Think:

> **Hundreds of possible measures, only a handful applicable to each row.**

---

# 23. The easiest way to remember it

Think of this analogy:

### Normal design = spreadsheet

```text
Transaction | Sales | Tax | Refund
T1          | 500   | 50  | -
T2          | -     | -   | 100
```

Very easy to read and calculate.

### Measure Type = verticalized spreadsheet

```text
Transaction | Measure | Value
T1          | Sales   | 500
T1          | Tax     | 50
T2          | Refund  | 100
```

You save horizontal space but create more rows.

---

# 24. Final decision tree

Use this mental decision tree:

```text
Do I have many different measures?
             │
             ▼
            YES
             │
             ▼
Are hundreds of measures possible?
             │
       ┌─────┴─────┐
       NO          YES
       │             │
       ▼             ▼
Keep measures    How many are
as columns       populated per row?
                     │
              ┌──────┴──────┐
              │             │
          Many            Very few
              │             │
              ▼             ▼
       Keep as columns   Consider
                         Measure Type
                         Dimension
```

And one final question should always be asked:

> **Will users frequently need to calculate one measure against another?**

If the answer is **yes**, separate measure columns are usually much better.

---

## The one-sentence takeaway

> **A Measure Type Dimension trades a very wide, sparse fact table for a taller fact table, but the price is more rows, a changed grain, and more difficult analytical calculations; therefore it should generally be reserved for extreme cases with hundreds of possible measures and only a few populated per fact row.**
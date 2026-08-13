

The key rule is:

> **If the new fact describes the same business event represented by the existing fact table, you can usually add it as a new column.**

Let's go through the whole process.

---

# Example: Retail Sales

Suppose your business process is **retail sales**.

## Step 1 — Identify the business process

The business process is:

> **A customer purchases a product.**

So we're designing a `fact_sales` table.

---

## Step 2 — Declare the grain

Before deciding columns, we declare:

> **Grain: One row represents one product sold in one sales transaction.**

This is critical.

Imagine Order #1001 contains:

- 2 Laptops
    
- 1 Mouse
    

Our fact table has two rows:

|Order|Product|Qty|
|---|---|--:|
|1001|Laptop|2|
|1001|Mouse|1|

So:

```text
1 product-line sale
        ↓
1 fact row
```

---

# Step 3 — Identify dimensions

We ask:

> What describes this sales event?

We might have:

- Date
    
- Product
    
- Customer
    
- Store
    
- Promotion
    

So:

```text
fact_sales
    │
    ├── dim_date
    ├── dim_product
    ├── dim_customer
    ├── dim_store
    └── dim_promotion
```

---

# Step 4 — Identify facts/measures

Now ask:

> What measurements result from this sales event?

Initially we might have:

|DateKey|ProductKey|CustomerKey|StoreKey|Quantity|SalesAmount|
|---|---|---|---|--:|--:|
|101|20|500|5|2|₹160,000|
|101|30|500|5|1|₹500|

`Quantity` and `SalesAmount` are facts because they describe the **product sale** at our declared grain.

---

# Step 5 — A new business requirement arrives

Six months later, the business says:

> "We also need to analyze the discount given on each sale."

Can we add:

```text
DiscountAmount
```

to `fact_sales`?

### Yes.

Why?

Because **discount amount describes the same sales event**.

Our grain hasn't changed.

We still have:

> **One row = one product sold in one transaction.**

Now:

|Order|Product|Qty|Sales|Discount|
|---|---|--:|--:|--:|
|1001|Laptop|2|₹160K|₹10K|
|1001|Mouse|1|₹500|₹50|

The new column is consistent with the existing grain.

---

# Step 6 — Another requirement

Business says:

> "We also want the cost of the products sold."

Can we add:

```text
CostAmount
```

Yes, **if the cost is measurable at the same grain**.

Now:

|Order|Product|Qty|Sales|Discount|Cost|
|---|---|--:|--:|--:|--:|
|1001|Laptop|2|₹160K|₹10K|₹120K|
|1001|Mouse|1|₹500|₹50|₹300|

All these facts describe:

> **one product sold in one transaction.**

Therefore they belong together.

---

# Step 7 — What about a store manager's salary?

Suppose someone says:

> "Let's add `ManagerSalary` to this fact table."

❌ **No.**

Why?

Because the salary does not describe the product sale.

The fact table's grain is:

> One product sold in one transaction.

But manager salary has a different grain:

> One employee/pay period.

If you put it into the sales fact:

|Order|Product|Sales|ManagerSalary|
|---|---|--:|--:|
|1001|Laptop|₹160K|₹100K|
|1001|Mouse|₹500|₹100K|
|1002|Keyboard|₹3K|₹100K|

You have repeated the salary across many sales rows.

Then:

```sql
SUM(ManagerSalary)
```

would produce nonsense.

---

# Step 8 — What if the new fact has a different grain?

Suppose the business asks:

> "We need to track the number of employees working in each store each day."

That's a legitimate measurement.

But its grain is:

> **One row = one store per day.**

That's different from:

> **One row = one product sold per transaction.**

Therefore, don't add it to `fact_sales`.

Create another fact table:

```text
fact_sales
-----------
Grain:
one product per transaction

fact_store_staffing
-------------------
Grain:
one store per day
```

---

# The complete process

This is the process Kimball wants you to follow:

```text
             Business Requirement
                     │
                     ▼
             Identify Business
                  Process
                     │
                     ▼
              Declare Grain
                     │
                     ▼
          Identify Dimensions
                     │
                     ▼
            Identify Facts
                     │
                     ▼
       Is new fact consistent
          with existing grain?
              /          \
            YES           NO
             │             │
             ▼             ▼
       Add a new       Create a
        COLUMN        separate fact
                         table
```

---

## The crucial question

Whenever someone proposes a new measure, **don't ask first:**

> "Is it numeric?"

Instead ask:

> **"Does this measurement describe the business event represented by this fact table's grain?"**

If **yes → new column**.

If **no → potentially a new fact table**.

---

### One more subtle example

Suppose your sales fact grain is:

> **One product per transaction.**

You want to add `TaxAmount`.

If tax is calculated for each product line:

```text
Laptop → Tax ₹8,000
Mouse  → Tax ₹50
```

✅ Add `TaxAmount`.

But suppose your source system only gives:

> **Total tax for the entire order**

Order 1001:

```text
Laptop = ₹160K
Mouse  = ₹500
Total Order Tax = ₹16,050
```

You **cannot simply put ₹16,050 on both rows**, because you'd double-count the tax.

You'd need to determine whether the tax can legitimately be allocated to the product-line grain.

This illustrates why **grain comes first**.

> **The grain determines what facts are valid. The facts don't determine the grain.**
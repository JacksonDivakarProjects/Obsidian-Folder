Essentially, it is saying:

> **Do not directly JOIN two fact tables at their shared dimension keys. Query each fact table separately, aggregate each one to the same grain, and then combine the results.**

This is a **very important dimensional-modeling rule**.

---

# 1. Example: Shipments and Returns

Suppose you have two fact tables.

### FACT_SHIPMENT

**Grain = one shipment transaction**

|customer|product|shipped_qty|
|---|---|--:|
|C1|P1|10|
|C1|P1|5|
|C1|P2|20|

### FACT_RETURN

**Grain = one return transaction**

|customer|product|returned_qty|
|---|---|--:|
|C1|P1|2|
|C1|P1|1|
|C1|P2|4|

Both facts have:

```text
customer_key
product_key
```

So someone might be tempted to do:

```sql
SELECT ...
FROM fact_shipment s
JOIN fact_return r
  ON s.customer_key = r.customer_key
 AND s.product_key = r.product_key
```

**Don't do this.**

---

# 2. Why does it produce wrong results?

Look at C1/P1.

Shipments have **2 rows**:

```text
10
5
```

Returns have **2 rows**:

```text
2
1
```

When you join them:

```text
Shipment 10  × Return 2
Shipment 10  × Return 1
Shipment 5   × Return 2
Shipment 5   × Return 1
```

You get **4 rows**.

That's a many-to-many multiplication.

Instead of:

```text
Shipment = 10 + 5 = 15
Return   = 2 + 1 = 3
```

you effectively get:

```text
10 + 10 + 5 + 5 = 30
```

for shipments.

And:

```text
2 + 1 + 2 + 1 = 6
```

for returns.

Both are wrong.

---

# 3. This is what the book means by "impossible to control cardinality"

The issue is that the two fact tables may have **different numbers of rows for the same dimension combination**.

For C1 + P1:

```text
SHIPMENTS          RETURNS
2 rows             2 rows
    │                  │
    └────── JOIN ──────┘
             ↓
          2 × 2
          = 4 rows
```

For another customer/product:

```text
SHIPMENTS          RETURNS
5 rows             3 rows
    │                  │
    └────── JOIN ──────┘
             ↓
          5 × 3
          = 15 rows
```

The relational database is doing exactly what you asked it to do.

The problem is:

> **That relational JOIN doesn't represent the business question you intended.**

---

# 4. So what is "drill across"?

Instead of joining the **raw fact tables**, query each fact **separately**.

### Step 1 — Aggregate shipments

```text
FACT_SHIPMENT

Customer Product  Shipped
C1       P1       15
C1       P2       20
```

### Step 2 — Aggregate returns separately

```text
FACT_RETURN

Customer Product  Returned
C1       P1       3
C1       P2       4
```

Now both result sets have the same grain:

> **one row per Customer + Product**

---

# 5. Then combine the results

Now you can safely produce:

|Customer|Product|Shipped|Returned|
|---|---|--:|--:|
|C1|P1|15|3|
|C1|P2|20|4|

This is called **drilling across**.

Conceptually:

```text
                 DIMENSIONS
             Customer + Product
                    │
          ┌─────────┴─────────┐
          ↓                   ↓
    FACT_SHIPMENT        FACT_RETURN
          ↓                   ↓
      Aggregate           Aggregate
          ↓                   ↓
       15, 20              3, 4
          │                   │
          └─────────┬─────────┘
                    ↓
              DRILL ACROSS
                    ↓
          Shipped | Returned
```

---

# 6. Why is this safe?

Because you're combining **already aggregated results at the same grain**.

Before:

```text
Fact rows
    ↓
many-to-many JOIN ❌
```

After:

```text
Fact 1 → aggregate to Customer + Product
Fact 2 → aggregate to Customer + Product
                         ↓
                  combine results
                         ↓
                         ✅
```

---

# 7. What does "sort-merge" mean?

The book uses an older/technical term.

It basically means:

> Sort both result sets by their common dimension values and line them up.

For example:

### Shipment result

```text
C1 | P1 | 15
C1 | P2 | 20
C2 | P1 | 30
```

### Return result

```text
C1 | P1 | 3
C1 | P2 | 4
C2 | P1 | 5
```

Both are ordered by:

```text
Customer
Product
```

Then you line up matching rows.

---

# 8. The deeper dimensional-modeling principle

This is really an extension of the **fact-table grain principle** you've been learning.

Each fact table has its own grain:

```text
FACT_SHIPMENT
= one shipment transaction

FACT_RETURN
= one return transaction
```

They are **different business processes**, so they should normally remain separate fact tables.

But they share **conformed dimensions**:

```text
             DIM_CUSTOMER
                   │
          ┌────────┴────────┐
          ↓                 ↓
   FACT_SHIPMENT       FACT_RETURN
          ↑                 ↑
          └──── PRODUCT ────┘
```

You analyze them together through the **common dimensions**, not by directly joining their transaction rows.

---

# 9. What you should remember

### ❌ Don't do this

```text
FACT_SHIPMENT
      JOIN
FACT_RETURN
      ON
customer_key + product_key
```

because you can create many-to-many row multiplication.

### ✅ Do this

```text
FACT_SHIPMENT
      ↓
Aggregate
      ↓
Customer + Product
      │
      ├───────────┐
      │           │
FACT_RETURN      │
      ↓           │
Aggregate         │
      ↓           │
Customer + Product
      └─────┬─────┘
            ↓
       Drill Across
```

### One-line definition

> **Drill-across = independently aggregate multiple fact tables to the same dimensional grain, then combine the aggregated result sets using their common dimension attributes.**

And this is why **conformed dimensions are so important**: they give you the common row headers (`customer`, `product`, `date`, etc.) needed to correctly compare different business processes without incorrectly joining their raw fact rows.
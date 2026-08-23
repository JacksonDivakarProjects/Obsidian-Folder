Yes. **Type 7 is basically a way to let the same fact table support BOTH Type 1 ("as-is") and Type 2 ("as-was") analysis.**

The important thing is that **the fact table stores two keys for the same dimension**:

1. **Durable/Business Key** → used for the **Type 1/current perspective**
    
2. **Surrogate Key** → used for the **Type 2/historical perspective**
    

---

# 1. First understand "as-was" vs "as-is"

### As-was

> **What was true when the transaction happened?**

Example:

> "How much did we sell in Chennai when the customer was actually living in Chennai?"

This requires **historical Type 2 information**.

---

### As-is

> **What is true about the customer today?**

Example:

> "How much have our customers who CURRENTLY live in Bangalore spent historically?"

This requires the **current Type 1 perspective**.

Type 7 lets you answer **both questions from the same dimension/fact model**.

---

# 2. Start with a Type 2 dimension

Suppose customer `C101` moved from Chennai to Bangalore.

The Type 2 dimension is:

|Customer_SK|Customer_ID|City|Current|
|--:|---|---|---|
|501|C101|Chennai|N|
|728|C101|Bangalore|Y|

Remember:

```text
Customer_ID = durable/business key
Customer_SK = surrogate primary key
```

The business key stays the same:

```text
C101
```

while each historical version gets a different SK:

```text
C101 → SK 501 → Chennai
C101 → SK 728 → Bangalore
```

---

# 3. Type 7 puts BOTH keys in the fact

This is the defining feature.

Fact:

|Sale_Date|Customer_ID|Customer_SK|Sales|
|---|---|--:|--:|
|2025-05-10|C101|501|₹10,000|
|2026-07-15|C101|728|₹5,000|

So the fact contains:

```text
Customer_ID   ← durable key
Customer_SK   ← surrogate key
```

Now the same fact can be analyzed in two ways.

---

# 4. Perspective 1: Type 2 / "As-Was"

Suppose the question is:

> **"How much did customers spend according to where they lived when the transaction happened?"**

Use the **surrogate key**.

```text
Fact.Customer_SK
        ↓
Dim.Customer_SK
```

For our example:

```text
SK 501 → Chennai → ₹10,000
SK 728 → Bangalore → ₹5,000
```

Result:

|Historical City|Sales|
|---|--:|
|Chennai|₹10,000|
|Bangalore|₹5,000|

This is the **Type 2 / as-was perspective**.

---

# 5. Perspective 2: Type 1 / "As-Is"

Now ask:

> **"How much have customers who currently live in Bangalore spent historically?"**

Here we don't care where they lived when the sale occurred.

We want their **current** city.

The dimension contains:

|Customer_SK|Customer_ID|City|Current|
|--:|---|---|---|
|501|C101|Chennai|N|
|728|C101|Bangalore|Y|

For the Type 1 perspective, we:

### Step 1

Filter the dimension:

```sql
WHERE Current = 'Y'
```

This gives:

```text
C101 → Bangalore
```

### Step 2

Join using the **durable/business key**:

```text
Fact.Customer_ID
        ↓
Dim.Customer_ID
```

Now both fact rows for C101 connect to the **current** customer row:

```text
2025 sale → C101 → Current City = Bangalore
2026 sale → C101 → Current City = Bangalore
```

Therefore:

**Bangalore → ₹15,000**

---

# 6. This is the magic of Type 7

The same fact table can answer:

### As-was

```text
Fact
 ↓
Customer_SK
 ↓
Type 2 Dimension
 ↓
Historical City
```

Result:

```text
Chennai    ₹10,000
Bangalore  ₹5,000
```

### As-is

```text
Fact
 ↓
Customer_ID
 ↓
Current dimension row
 ↓
Current City
```

Result:

```text
Bangalore  ₹15,000
```

---

# 7. Why does Type 7 need TWO keys?

This is the most important thing to memorize.

### Surrogate key

```text
Customer_SK
```

identifies:

> **Which historical version of the customer was involved?**

Therefore:

**SK → Type 2 / as-was**

---

### Durable key

```text
Customer_ID
```

identifies:

> **Which real-world customer is this, regardless of version?**

Therefore:

**Durable key → Type 1 / as-is**

---

# 8. Visualize it this way

```text
                         FACT
              ┌──────────────────────┐
              │ Customer_ID           │
              │ Customer_SK           │
              │ Sales                 │
              └───────┬───────┬──────┘
                      │       │
             Durable │       │ SK
                Key  │       │
                     │       │
             AS-IS   │       │ AS-WAS
                     │       │
                     ▼       ▼
              ┌──────────────────────┐
              │    DIM_CUSTOMER      │
              │                      │
              │ Customer_ID          │
              │ Customer_SK          │
              │ City                 │
              │ Current_Flag         │
              └──────────────────────┘
```

---

# 9. Why does the book say "current flag is constrained to be current"?

For **Type 1 / as-is**:

```text
WHERE Current_Flag = 'Y'
```

You only want the customer's **latest version**.

Then:

```text
Fact.Customer_ID = Dim.Customer_ID
```

---

For **Type 2 / as-was**:

You **don't filter**:

```text
Current_Flag
```

because you want all historical dimension versions.

Instead:

```text
Fact.Customer_SK = Dim.Customer_SK
```

This retrieves the exact version that applied to the fact.

---

# 10. Why separate views?

This part of the book is very practical.

BI users shouldn't have to remember:

> "For this report, filter current flag and join using durable key; for that report, don't filter and join using SK."

Instead, the data warehouse team creates two views.

### View 1 — As-Is

Something like:

```text
vw_customer_current
```

Internally:

```text
Current_Flag = Y
Join using Customer_ID
```

BI users see:

> Current customer attributes.

---

### View 2 — As-Was

Something like:

```text
vw_customer_historical
```

Internally:

```text
No Current_Flag filter
Join using Customer_SK
```

BI users see:

> Historical customer attributes.

So the BI layer gets **two logical perspectives from the same physical dimension**.

---

# 11. Type 6 vs Type 7

This is a very important distinction because they both support **as-is + as-was**.

### Type 6

One physical dimension:

```text
Customer_SK
Customer_ID
Historical_City
Current_City
```

You have:

> historical attribute + current attribute **inside the same row structure**.

---

### Type 7

One physical Type 2 dimension:

```text
Customer_SK
Customer_ID
City
Current_Flag
```

And the **fact stores both keys**:

```text
Customer_ID
Customer_SK
```

Then you create two views:

```text
As-Is  → Durable Key + Current_Flag = Y
As-Was → Surrogate Key + all rows
```

### Mental shortcut

> **Type 6 = two attribute versions in the dimension.**

> **Type 7 = two keys in the fact + two views of the same Type 2 dimension.**

---

# 12. Type 5 vs Type 7

Since you're learning these sequentially, this distinction is also useful.

### Type 5

```text
Type 4
+
Current mini-dimension reference
```

It uses:

```text
Base Dimension → Current Mini-Dimension
Fact → Historical Mini-Dimension
```

### Type 7

```text
Type 2
+
Durable key + SK in Fact
+
Two views
```

No mini-dimension is required.

---

# 13. The ultimate comparison

|Type|Core design|Historical|Current|
|---|---|---|---|
|**Type 4**|Mini-dimension|Fact → Mini-Dim|Current logic needed|
|**Type 5**|Type 4 + current pointer|Fact → Mini-Dim|Dim → Current Mini-Dim|
|**Type 6**|Type 2 + Type 1 attribute|Type 2 column|Type 1 column|
|**Type 7**|Type 2 + dual keys|Fact → SK|Fact → Durable Key + current dimension|

---

## Pareto: Type 7 in one sentence

> **SCD Type 7 keeps a Type 2 dimension, puts both the durable/business key and surrogate key in the fact, and provides two views: the durable-key + current-row view for "as-is" reporting and the surrogate-key view for "as-was" reporting.**

The **single most important thing** to remember is:

```text
DURABLE KEY → "Who is this customer today?"
SURROGATE KEY → "Which historical version applied to this fact?"
```

That's the heart of Type 7.
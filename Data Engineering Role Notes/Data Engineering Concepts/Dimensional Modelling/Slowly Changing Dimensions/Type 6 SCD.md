Yes. **Type 6 is basically Type 2 + a Type 1 "current value" column.**

The easiest way to understand it is:

> **Type 2 preserves what the attribute was when the fact happened. Type 6 additionally puts the customer's current value onto ALL historical rows for that customer.**

That's the key idea.

---

# 1. Start with Type 2

Suppose customer `C101` moves from Chennai to Bangalore.

A normal Type 2 dimension would be:

|Customer_SK|Customer_ID|City|Effective|Expiration|Current|
|--:|---|---|---|---|---|
|501|C101|Chennai|Jan 2024|Jun 2026|N|
|728|C101|Bangalore|Jul 2026|9999|Y|

This preserves history.

So if a sale happened in 2025:

```text
Fact → Customer_SK = 501 → Chennai
```

Correct.

---

# 2. But there is a business question Type 2 doesn't answer easily

Suppose the business asks:

> **"Show me all historical sales, but group them according to the customer's CURRENT city."**

The historical rows say:

```text
Customer_SK 501 → Chennai
Customer_SK 728 → Bangalore
```

So the 2025 sale naturally groups under **Chennai**.

But the customer is **currently in Bangalore**.

They want:

```text
All historical sales for C101 → Bangalore
```

This is where Type 6 comes in.

---

# 3. Type 6 adds a Type 1 current attribute

The dimension becomes:

|Customer_SK|Customer_ID|Historical_City|Current_City|Effective|Expiration|
|--:|---|---|---|---|---|
|501|C101|Chennai|**Bangalore**|Jan 2024|Jun 2026|
|728|C101|Bangalore|**Bangalore**|Jul 2026|9999|

Notice something very important:

### `Historical_City`

is different for each version:

```text
501 → Chennai
728 → Bangalore
```

### `Current_City`

is the **same across all rows for C101**:

```text
501 → Bangalore
728 → Bangalore
```

That's the Type 6 magic.

---

# 4. Why update ALL historical rows?

Suppose later C101 moves again:

```text
Bangalore → Hyderabad
```

Type 6 becomes:

|Customer_SK|Customer_ID|Historical_City|Current_City|
|--:|---|---|---|
|501|C101|Chennai|**Hyderabad**|
|728|C101|Bangalore|**Hyderabad**|
|900|C101|Hyderabad|**Hyderabad**|

The historical value stays unchanged:

```text
501 → Chennai
728 → Bangalore
900 → Hyderabad
```

But the current value is overwritten everywhere:

```text
501 → Hyderabad
728 → Hyderabad
900 → Hyderabad
```

That's exactly what the book means by:

> "The type 1 attribute is systematically overwritten on all rows associated with a particular durable key."

---

# 5. What is the durable key doing?

This is important.

Remember:

```text
Customer_ID = C101
```

is the **durable/business key**.

It stays the same across all Type 2 versions:

```text
C101
 ├── Customer_SK 501
 ├── Customer_SK 728
 └── Customer_SK 900
```

When the current city changes, ETL finds:

```text
WHERE Customer_ID = 'C101'
```

and updates `Current_City` on **all those rows**.

So:

```text
Customer_ID = C101
        ↓
Find every Type 2 version
        ↓
Overwrite Current_City
```

---

# 6. Now look at the fact table

Suppose:

|Customer_SK|Sales|
|--:|--:|
|501|₹10,000|
|728|₹5,000|
|900|₹8,000|

The fact table points to the correct historical dimension version.

Therefore we can perform **two different types of analysis**.

---

## Historical analysis

> "Where was the customer when the sale happened?"

Use:

```text
Historical_City
```

Result:

|City|Sales|
|---|--:|
|Chennai|₹10,000|
|Bangalore|₹5,000|
|Hyderabad|₹8,000|

That's the **Type 2 perspective**.

---

## Current analysis

> "Where are these customers currently?"

Use:

```text
Current_City
```

Result:

|Current City|Sales|
|---|--:|
|Hyderabad|₹23,000|

Because all three historical rows now say:

```text
Current_City = Hyderabad
```

So all historical sales can be grouped under the customer's **current** city.

That's the **Type 1 perspective**.

---

# 7. This is why Type 6 is powerful

You can ask:

### Question A

> What was true when the transaction occurred?

Use:

```text
Type 2 attribute
```

### Question B

> What is true about that customer today?

Use:

```text
Type 1 current attribute
```

Same fact table, same dimension, two perspectives.

---

# 8. Type 6 structure

Conceptually:

```text
                 DIM_CUSTOMER
        ┌─────────────────────────────┐
        │ Customer_SK                 │
        │ Customer_ID (durable key)   │
        │                             │
        │ Historical_City ← Type 2    │
        │ Current_City    ← Type 1    │
        │                             │
        │ Effective_Date              │
        │ Expiration_Date             │
        │ Current_Row_Flag            │
        └──────────────┬──────────────┘
                       │
                       │ Customer_SK
                       ▼
                  FACT_SALES
```

---

# 9. Type 2 vs Type 6

This comparison is extremely important.

### Type 2

|Customer_SK|Customer_ID|City|
|--:|---|---|
|501|C101|Chennai|
|728|C101|Bangalore|

Each row tells you:

> **What was true for this version?**

---

### Type 6

|Customer_SK|Customer_ID|Historical_City|Current_City|
|--:|---|---|---|
|501|C101|Chennai|Bangalore|
|728|C101|Bangalore|Bangalore|

Each row tells you BOTH:

> **What was true at that time?**

and

> **What is true now?**

---

# 10. Type 6 is a hybrid

This is why Type 6 is often called a **hybrid SCD**.

It combines:

```text
Type 1
   +
Type 2
```

Specifically:

```text
Type 2 → preserve historical attribute
Type 1 → maintain current attribute
```

So:

> **Type 6 = Type 2 + Type 1 current attribute**

---

# 11. Why is it called Type 6?

You can think of the numbering as:

```text
Type 6
   =
Type 2
+
Type 1
+
Type 1
```

Historically, the name "Type 6" comes from combining SCD techniques in that way.

But for understanding it, **don't focus too much on the arithmetic**.

Focus on:

> **Type 6 = Type 2 history + current Type 1 value.**

---

# 12. The ETL process

Suppose:

```text
C101
Bangalore → Hyderabad
```

The ETL does **two things**.

### Step 1 — Close old Type 2 row

```text
501 → Chennai
728 → Bangalore
```

The current Type 2 row gets expired.

### Step 2 — Insert new Type 2 row

```text
900 → Hyderabad
```

### Step 3 — Type 1 update

Update `Current_City` on **all C101 rows**:

```text
501 → Current_City = Hyderabad
728 → Current_City = Hyderabad
900 → Current_City = Hyderabad
```

So the result is:

|SK|Customer|Historical City|Current City|Current Row|
|--:|---|---|---|---|
|501|C101|Chennai|Hyderabad|N|
|728|C101|Bangalore|Hyderabad|N|
|900|C101|Hyderabad|Hyderabad|Y|

---

# 13. Compare Type 5 and Type 6

This is probably where your previous Type 5 understanding becomes useful.

### Type 5

```text
Type 4
+
Current mini-dimension reference
```

So:

```text
Dim_Customer
      ↓
Current_Profile_SK
      ↓
Mini-Dimension
```

Historical profile comes through the fact.

---

### Type 6

```text
Type 2
+
Current Type 1 attribute
```

So:

```text
Dim_Customer
 ├── Historical attribute
 └── Current attribute
```

No mini-dimension is required.

---

# 14. Type 5 vs Type 6

||Type 5|Type 6|
|---|---|---|
|Based on|Type 4|Type 2|
|Mini-dimension|✅|❌|
|Type 2 rows|❌ in base dimension|✅|
|Historical values|✅|✅|
|Current values|✅|✅|
|Current value mechanism|Current mini-dim SK|Type 1 attribute|
|Main purpose|Current + historical rapidly changing profiles|Current + historical values of Type 2 attributes|

---

# 15. The biggest thing to understand

Type 6 **does not overwrite the historical attribute**.

It overwrites a **separate current-value column**.

For example:

```text
Historical_City = Bangalore
Current_City    = Hyderabad
```

The historical value remains untouched.

This is critical.

### Wrong understanding ❌

> Type 6 overwrites the historical value.

### Correct understanding ✅

> Type 6 preserves the historical Type 2 value and separately maintains a Type 1 current value.

---

# 16. Why update all rows?

This is probably the most unusual part of Type 6.

Suppose:

```text
C101
```

has 5 historical rows.

If the customer moves to Hyderabad, you don't just update the latest row:

```text
❌ Only latest row → Current_City = Hyderabad
```

You update **all rows belonging to durable key C101**:

```text
✅ Every C101 row → Current_City = Hyderabad
```

Why?

Because when a fact joins to **any historical version**, the query should be able to ask:

> "What is this customer currently?"

and get the same current answer.

---

# 17. Pareto mental model

You can remember the entire Type 6 concept with this:

```text
              TYPE 6

          Customer C101
                │
       ┌────────┴─────────┐
       │                  │
       ▼                  ▼
 Historical value     Current value
    Type 2              Type 1
       │                  │
       ▼                  ▼
 "What was true?"     "What is true now?"
```

Or even simpler:

> **Type 2 column = "then"**  
> **Type 1 column = "now"**

And:

> **Type 6 = store BOTH "then" and "now" in the same Type 2 dimension.**

That is the core idea you should carry forward.
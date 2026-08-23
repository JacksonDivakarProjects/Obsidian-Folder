Absolutely. **Type 5 is basically Type 4 + one extra Type 1 link**.

The key reason Type 5 exists is that the business wants **both**:

1. **Historical analysis** — "What was the customer's profile when the sale happened?"
    
2. **Current analysis** — "What is the customer's profile now?"
    

Type 4 gives you #1. Type 5 adds an easy way to get #2.

---

# 1. Start with Type 4

In Type 4, we have:

### Base dimension

```text
Dim_Customer
----------------
Customer_SK
Customer_ID
Name
DOB
```

### Mini-dimension

```text
Mini_Dim_Profile
----------------
Profile_SK
Income_Band
Risk_Level
Segment
```

### Fact

```text
Fact_Sales
----------------
Customer_SK
Profile_SK
Sales
```

So:

```text
Dim_Customer ──┐
               ├── Fact_Sales ── Mini_Dim_Profile
               │
               └───────────────
```

The fact stores the `Profile_SK` that was applicable **at the time of the transaction**.

That's great for historical analysis.

---

# 2. But Type 4 has a problem

Suppose John currently has:

```text
Profile_SK = 3
Income = High
Risk = Low
```

But his historical sales look like:

|Customer_SK|Profile_SK|Sales|
|--:|--:|--:|
|101|1|₹5,000|
|101|2|₹8,000|
|101|3|₹10,000|

If a user asks:

> **"What is John's current risk level?"**

With Type 4, you have to go through the mini-dimension.

Or if you're looking at the customer dimension by itself, the current profile isn't directly available there.

Type 5 solves this.

---

# 3. What does Type 5 add?

Type 5 takes the Type 4 design and adds a **current mini-dimension key to the base dimension**.

So:

### Before — Type 4

```text
Dim_Customer
----------------
Customer_SK
Customer_ID
Name
DOB
```

### After — Type 5

```text
Dim_Customer
----------------
Customer_SK
Customer_ID
Name
DOB
Current_Profile_SK  ← NEW
```

`Current_Profile_SK` points to the **customer's currently assigned profile**.

---

# 4. Complete example

### Mini-dimension

```text
Mini_Dim_Profile

Profile_SK | Income | Risk | Segment
-----------|--------|------|---------
1          | Medium | High | Standard
2          | High   | Medium | Premium
3          | High   | Low | VIP
```

John's current profile is:

```text
Profile_SK = 3
```

### Base dimension

```text
Dim_Customer

Customer_SK | Customer_ID | Name | Current_Profile_SK
------------|-------------|------|------------------
101         | C101        | John | 3
102         | C102        | Ravi | 2
```

Now the base dimension knows John's **current profile**.

---

# 5. But historical facts still use their old Profile_SK

Suppose John's transactions were:

|Date|Customer_SK|Profile_SK|Sales|
|---|--:|--:|--:|
|Jan|101|1|₹5,000|
|Jun|101|2|₹8,000|
|Dec|101|3|₹10,000|

The fact table preserves:

```text
Jan → Profile 1
Jun → Profile 2
Dec → Profile 3
```

So historical information is still preserved.

Meanwhile:

```text
Dim_Customer
Customer 101 → Current_Profile_SK = 3
```

tells us:

> John's **current** profile is Profile 3.

---

# 6. This is why it's called "Type 5"

Think:

```text
Type 4
   +
Type 1 current reference
   ↓
Type 5
```

The **Type 4 portion** gives you historical profile tracking.

The **Type 1 portion** gives you the current profile directly in the base dimension.

That's why you can remember:

> **Type 5 = Type 4 + Type 1 current mini-dimension reference.**

---

# 7. What does "Type 1 reference" mean?

This part from the book is very important:

> "ETL team must overwrite this type 1 mini-dimension reference whenever the current mini-dimension assignment changes."

Suppose John's profile changes:

```text
Old:
Profile_SK = 2

New:
Profile_SK = 3
```

The ETL does **not** create a new John row in `Dim_Customer`.

Instead:

```sql
UPDATE Dim_Customer
SET Current_Profile_SK = 3
WHERE Customer_SK = 101;
```

So:

```text
Before:
Customer 101 → Current_Profile_SK = 2

After:
Customer 101 → Current_Profile_SK = 3
```

That's the **Type 1 behavior**.

The old `Current_Profile_SK = 2` is overwritten.

---

# 8. Does that destroy history?

**No — and this is the beauty of Type 5.**

The `Current_Profile_SK` in the base dimension is allowed to lose its old value because it represents:

> **"What is the customer's profile NOW?"**

The historical information is preserved separately in the **fact table's `Profile_SK`**.

So you have two different concepts:

### Base dimension

```text
Current_Profile_SK
        ↓
"What is the customer's profile currently?"
```

### Fact table

```text
Profile_SK
        ↓
"What profile did the customer have when this transaction happened?"
```

---

# 9. This gives you two perspectives

Suppose:

```text
John:
2024 → Medium Risk
2025 → High Risk
2026 → Low Risk
```

Historical facts:

|Year|Profile_SK|Risk|
|---|--:|---|
|2024|1|Medium|
|2025|2|High|
|2026|3|Low|

Current customer dimension:

|Customer|Current_Profile_SK|
|---|--:|
|John|3|

So you can answer both:

### Historical question

> "How much did John spend when he was High Risk?"

Use:

```text
Fact → Profile_SK → Mini-Dimension
```

### Current question

> "How much have current Low-Risk customers historically spent?"

Now you can use:

```text
Dim_Customer
      ↓
Current_Profile_SK
      ↓
Mini_Dimension
      ↓
Fact
```

This is a **very important capability** of Type 5.

---

# 10. Why does the book say "without linking through a fact table"?

This sentence:

> "This enables the currently-assigned mini-dimension attributes to be accessed along with the others in the base dimension without linking through a fact table."

means that you can conceptually treat:

```text
Dim_Customer
      +
Current Mini-Dimension attributes
```

as one logical customer dimension.

For example, a BI user can see:

|Customer|Name|Current Income|Current Risk|
|---|---|---|---|
|C101|John|High|Low|
|C102|Ravi|High|Medium|

without needing:

```text
Fact → Mini-Dimension
```

just to understand the customer's **current** profile.

---

# 11. What is an "outrigger"?

An **outrigger** is basically a dimension that is linked from another dimension rather than directly from the fact.

Normally:

```text
Fact → Dimension
```

But here:

```text
Fact → Customer Dimension → Mini-Dimension
```

The mini-dimension is therefore acting as an **outrigger** for the base dimension.

In Type 5:

```text
Fact
 │
 ├──────────────→ Dim_Customer
 │                    │
 │                    │ Current_Profile_SK
 │                    ▼
 │               Mini_Dimension
 │
 └──────────────→ Mini_Dimension
      historical Profile_SK
```

That's the architecture you should visualize.

---

# 12. Type 4 vs Type 5

This is probably the most important comparison.

||Type 4|Type 5|
|---|---|---|
|Base dimension|Stable attributes|Stable + current profile reference|
|Mini-dimension|✅|✅|
|Historical profile|✅|✅|
|Current profile directly available from base dimension|❌|✅|
|Current profile reference|—|Type 1|
|Fact stores Profile_SK|✅|✅|
|Main purpose|Separate rapidly changing attributes|Historical + current perspective|

### Mental model

**Type 4:**

> "Keep the rapidly changing attributes in a mini-dimension."

**Type 5:**

> "Do Type 4, but also put the current mini-dimension key back into the base dimension."

---

# 13. Why would a business want this?

Imagine a bank.

Customer risk changes over time:

```text
2024 → Low Risk
2025 → Medium Risk
2026 → High Risk
```

The bank might ask:

### Historical perspective

> "How much did we lend to customers when they were Low Risk?"

Use the historical `Profile_SK` in the fact.

### Current perspective

> "How much have our **currently High-Risk customers** borrowed historically?"

Use the **current profile reference** in the customer dimension.

These are **different questions**.

Type 5 supports both.

---

# 14. The most important thing to understand

Don't think:

> "Type 5 stores two versions of the mini-dimension."

Instead think:

```text
             TYPE 5

       ┌─────────────────┐
       │ Dim_Customer    │
       │                 │
       │ Customer_SK     │
       │ Customer_ID     │
       │ Name            │
       │                 │
       │ Current_Profile_SK ──────┐
       └─────────────────┘       │
                                 ▼
                         ┌───────────────┐
                         │ Mini-Dim      │
                         │               │
                         │ Profile_SK    │
                         │ Income        │
                         │ Risk          │
                         └───────────────┘
                                 ▲
                                 │
                                 │ Profile_SK
                         ┌───────┴───────┐
                         │ Fact_Sales    │
                         └───────────────┘
```

There are **two paths to the mini-dimension**:

### Current path

```text
Dim_Customer → Current_Profile_SK → Mini_Dim
```

### Historical path

```text
Fact → Profile_SK → Mini_Dim
```

That is **the essence of Type 5**.

---

# 15. Type 5 Pareto

If you're studying this for interviews/exams, remember these **6 points**:

1. **Type 5 builds on Type 4.**
    
2. Type 4 creates a **mini-dimension** for rapidly changing attributes.
    
3. Type 5 adds `Current_Profile_SK` to the **base dimension**.
    
4. `Current_Profile_SK` is maintained using **Type 1 overwrite**.
    
5. The **fact's `Profile_SK` preserves historical context**.
    
6. Therefore, Type 5 supports both:
    
    - **Historical profile analysis**
        
    - **Current profile analysis**
        

### One sentence to memorize

> **SCD Type 5 = Type 4 mini-dimension + a Type 1 current mini-dimension key embedded in the base dimension, allowing both historical analysis through the fact and current-state analysis directly from the dimension.**
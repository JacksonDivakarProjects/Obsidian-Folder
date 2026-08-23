

Let's walk through it.

## 1. Your Type 7 understanding is correct

Suppose the dimension is:

|Customer_SK|Customer_ID|City|Current_Flag|
|--:|---|---|---|
|101|C1|Chennai|N|
|205|C1|Bangalore|Y|
|310|C2|Chennai|Y|

Here:

- `Customer_ID` = **durable/business key**
    
- `Customer_SK` = **surrogate key**
    
- `Current_Flag = Y` = current version
    

Now suppose the fact is:

|Sale_ID|Customer_ID|Customer_SK|Sales|
|---|---|--:|--:|
|S1|C1|101|₹1,000|
|S2|C1|205|₹2,000|
|S3|C2|310|₹3,000|

---

# 2. Type 7 "as-is" query

You want:

> **"How much have customers who CURRENTLY live in Bangalore spent?"**

First, filter the dimension:

```text
Current_Flag = Y
```

You get:

|Customer_SK|Customer_ID|City|Current_Flag|
|--:|---|---|---|
|205|C1|Bangalore|Y|
|310|C2|Chennai|Y|

Now **join using the durable key**:

```text
Fact.Customer_ID = Dim.Customer_ID
```

For C1:

```text
Fact S1 → C1 ──┐
               ├── Current dimension row → Bangalore
Fact S2 → C1 ──┘
```

So both S1 and S2 are classified as:

```text
Current City = Bangalore
```

Therefore:

**Bangalore = ₹1,000 + ₹2,000 = ₹3,000**

### Notice something important

You did **NOT** get only the latest transaction.

You got **all historical transactions belonging to C1**, but you classified them using **C1's current attributes**.

That's what **"as-is"** means.

---

# 3. Now compare with "as-was"

Suppose the question is:

> **"How much did customers spend according to where they lived when the sale happened?"**

Now use the surrogate key:

```text
Fact.Customer_SK = Dim.Customer_SK
```

Results:

|Sale|Customer_SK|Historical City|Sales|
|---|--:|---|--:|
|S1|101|Chennai|₹1,000|
|S2|205|Bangalore|₹2,000|
|S3|310|Chennai|₹3,000|

So:

|Historical City|Sales|
|---|--:|
|Chennai|₹4,000|
|Bangalore|₹2,000|

That's **as-was**.

---

# 4. So why Type 7 if Type 6 already exists?

Excellent question.

**Both can answer as-is and as-was questions.**

The difference is **how they implement it**.

### Type 6

You physically put both values in the Type 2 dimension:

|SK|Customer|Historical City|Current City|
|--:|---|---|---|
|101|C1|Chennai|Bangalore|
|205|C1|Bangalore|Bangalore|

So the dimension itself contains:

```text
Historical City
Current City
```

The ETL must update `Current_City` on **every historical row** whenever C1 moves.

---

### Type 7

You don't duplicate the current attribute.

You keep a normal Type 2 dimension:

|SK|Customer|City|Current|
|--:|---|---|---|
|101|C1|Chennai|N|
|205|C1|Bangalore|Y|

And the fact stores **both keys**:

```text
Customer_ID
Customer_SK
```

Then you create two logical views:

```text
                TYPE 7
                   │
          ┌────────┴────────┐
          │                 │
       AS-IS             AS-WAS
          │                 │
 Durable Key             SK
 + Current=Y             All rows
          │                 │
          ▼                 ▼
 Current attributes    Historical attributes
```

---

# 5. Why might Type 7 be preferable?

The big advantage is **you don't have to maintain a duplicated current attribute on every historical row**.

Imagine a customer has **20 Type 2 versions**.

### Type 6

You have:

```text
C1 version 1 → Current_City = Bangalore
C1 version 2 → Current_City = Bangalore
C1 version 3 → Current_City = Bangalore
...
C1 version 20 → Current_City = Bangalore
```

If the customer moves to Hyderabad, you must update:

```text
20 rows
```

to:

```text
Current_City = Hyderabad
```

---

### Type 7

You only change the Type 2 dimension normally:

```text
Old:
C1 → Bangalore

New:
C1 → Hyderabad
```

and the current flag moves:

```text
Old row → N
New row → Y
```

The fact already contains:

```text
Customer_ID = C1
```

So the as-is view automatically joins C1's historical facts to the new current row.

**No need to update 20 historical dimension rows with a duplicated current attribute.**

That's a major conceptual advantage.

---

# 6. Another advantage: many Type 2 attributes

Imagine your Type 2 dimension has:

```text
City
State
Customer_Segment
Sales_Territory
Risk_Category
Account_Manager
```

With Type 6, if you want current versions of all of these, you potentially maintain:

```text
Current_City
Current_State
Current_Segment
Current_Territory
Current_Risk
Current_Manager
```

across **every historical row**.

With Type 7, the current dimension row already contains:

```text
City
State
Segment
Territory
Risk
Manager
```

So the current view simply joins to that row.

---

# 7. This is the real difference

Think about **where the current information is stored**.

### Type 6

```text
Every historical row
        │
        ├── Historical attribute
        └── Current attribute
```

So:

> **Current information is physically copied onto historical rows.**

### Type 7

```text
Historical row
      │
      └── Historical attribute

Current row
      │
      └── Current attributes
```

And the fact has two ways to reach the dimension:

```text
Durable Key → Current row
Surrogate Key → Historical row
```

So:

> **Current information is not copied onto every historical row.**

---

# 8. Your understanding in one diagram

Your exact understanding is:

```text
                DIMENSION
          ┌──────────────────┐
          │ C1 / Chennai      │ ← Current = N
          │ C1 / Bangalore    │ ← Current = Y
          └────────┬─────────┘
                   │
            Filter Current=Y
                   ↓
             C1 / Bangalore
                   ↑
                   │ Durable Key
                   │
             ┌─────┴──────┐
             │    FACT    │
             ├────────────┤
             │ C1 / SK101 │ → ₹1,000
             │ C1 / SK205 │ → ₹2,000
             └────────────┘
```

Both fact rows belong to **C1**, so both get classified using C1's **current attributes: Bangalore**.

That's exactly what Type 7's **as-is** perspective is doing.

And then:

```text
Fact.Customer_SK → Dimension.Customer_SK
```

gives you the **as-was** perspective.

---

## The Pareto takeaway

If you remember only this:

**Type 6:**

> "Put **current values on every historical row**."

**Type 7:**

> "Don't put current values on every historical row. **Keep two keys in the fact so I can choose whether I want the current row or the historical row.**"

And yes — your statement **"filter current dimension row, then join fact using durable key"** is precisely the **Type 7 as-is mechanism**.
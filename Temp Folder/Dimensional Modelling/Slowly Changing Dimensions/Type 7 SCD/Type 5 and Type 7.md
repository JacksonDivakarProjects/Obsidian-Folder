Yes. **Type 5 and Type 7 are very similar in purpose**—both let you do current + historical analysis—but they solve it using **different structures**.

The cleanest way to see it is:

> **Type 5 uses a mini-dimension. Type 7 uses a Type 2 dimension + two keys in the fact.**

---

## 1. Type 5

Type 5 starts with **Type 4**.

Suppose rapidly changing customer attributes are:

- Income
    
- Risk
    
- Segment
    

You split them into a mini-dimension.

### Customer dimension

|Customer_SK|Customer_ID|Name|Current_Profile_SK|
|--:|---|---|--:|
|101|C1|Jack|3|

### Mini-dimension

|Profile_SK|Income|Risk|Segment|
|--:|---|---|---|
|1|Medium|High|Standard|
|2|High|Medium|Premium|
|3|High|Low|VIP|

The fact stores:

|Sale|Customer_SK|Profile_SK|Sales|
|---|--:|--:|--:|
|S1|101|1|₹1,000|
|S2|101|2|₹2,000|
|S3|101|3|₹3,000|

So Type 5 has **two paths**:

### Historical

```text
Fact → Profile_SK → Mini-Dimension
```

### Current

```text
Customer Dimension → Current_Profile_SK → Mini-Dimension
```

---

# 2. Type 7

Type 7 does **not use a mini-dimension**.

Instead, the customer dimension itself is Type 2:

|Customer_SK|Customer_ID|City|Segment|Current|
|--:|---|---|---|---|
|101|C1|Chennai|Standard|N|
|205|C1|Bangalore|Premium|Y|

And the fact stores **both keys**:

|Sale|Customer_ID|Customer_SK|Sales|
|---|---|--:|--:|
|S1|C1|101|₹1,000|
|S2|C1|205|₹2,000|

Then:

### Historical / as-was

```text
Fact.Customer_SK
       ↓
Dim.Customer_SK
```

### Current / as-is

```text
Fact.Customer_ID
       ↓
Dim.Customer_ID
       +
Current_Flag = Y
```

---

# 3. The fundamental difference

### Type 5

The rapidly changing attributes are **moved out**:

```text
Customer
   │
   └── Current Profile SK ──► Mini-Dim
                                   
Fact ───── Historical Profile SK ──► Mini-Dim
```

### Type 7

The attributes **stay in the Type 2 dimension**:

```text
                  ┌── Customer_SK → historical row
Fact ─────────────┤
                  └── Customer_ID → current row
```

---

# 4. Why would I choose Type 5?

Imagine you have a **10-million-row customer dimension** and these attributes change extremely frequently:

```text
Risk
Income Band
Credit Score Band
Customer Segment
```

If you put all of these into Type 2:

```text
Customer_SK
Customer_ID
Risk
Income
Segment
...
```

you could create a huge number of Type 2 rows.

Type 4/5 says:

> "These rapidly changing attributes deserve their own mini-dimension."

So the base customer dimension doesn't explode with every profile change.

---

# 5. Why Type 7?

Type 7 is useful when you want the **entire Type 2 dimension** to naturally support both:

```text
as-was
+
as-is
```

without creating separate current-value columns like Type 6.

The fact has:

```text
Durable Key + Surrogate Key
```

which gives the BI layer two perspectives.

---

# 6. Compare all three

This is the comparison I recommend memorizing:

||Type 5|Type 6|Type 7|
|---|---|---|---|
|Base technique|Type 4|Type 2|Type 2|
|Mini-dimension|✅|❌|❌|
|Historical rows|Mini-dim|Base dimension|Base dimension|
|Current values|Current mini-dim SK|Type 1 columns|Current dimension row|
|Fact keys|Customer SK + Profile SK|Customer SK|Customer SK + Durable Key|
|Current values copied to historical rows?|❌|✅|❌|
|Supports as-is?|✅|✅|✅|
|Supports as-was?|✅|✅|✅|

---

## The simplest mental model

Think about **where the rapidly changing attributes live**:

### Type 5

> **"Put them in a mini-dimension and keep a pointer to the current profile."**

### Type 6

> **"Keep Type 2 history and copy the current values onto every historical row."**

### Type 7

> **"Keep Type 2 history and let the fact choose current vs historical using two keys."**

So the big distinction between **Type 5 and Type 7** is:

> **Type 5 is a mini-dimension solution. Type 7 is a dual-key Type 2 solution.**

That's the distinction I'd use in an interview.
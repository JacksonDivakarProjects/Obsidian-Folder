Yes — this is the **third major fact-table type** after **transaction** and **periodic snapshot**. The easiest way to understand an **Accumulating Snapshot Fact Table** is:

> **One row follows one process from start → intermediate milestones → end, and that same row gets updated as the process progresses.**

### 1. Think of a pipeline

Take **order fulfillment**:

```text
Order Created
     ↓
Order Confirmed
     ↓
Packed
     ↓
Shipped
     ↓
Delivered
```

These are predictable milestones.

An accumulating snapshot captures the **entire journey in one row**.

---

### 2. Example

Suppose order line `OL1001` is created on August 1.

Initially:

|Order Line|Created Date|Confirmed Date|Packed Date|Shipped Date|Delivered Date|
|---|---|---|---|---|---|
|OL1001|Aug 1|NULL|NULL|NULL|NULL|

Then the order gets confirmed.

The **same row is updated**:

|Order Line|Created Date|Confirmed Date|Packed Date|Shipped Date|Delivered Date|
|---|---|---|---|---|---|
|OL1001|Aug 1|Aug 2|NULL|NULL|NULL|

Then packed:

|Order Line|Created Date|Confirmed Date|Packed Date|Shipped Date|Delivered Date|
|---|---|---|---|---|---|
|OL1001|Aug 1|Aug 2|Aug 3|NULL|NULL|

Eventually:

|Order Line|Created Date|Confirmed Date|Packed Date|Shipped Date|Delivered Date|
|---|---|---|---|---|---|
|OL1001|Aug 1|Aug 2|Aug 3|Aug 4|Aug 6|

**That's the defining characteristic.**

The row is **accumulating information about the process over time**.

---

## 3. Why is it called "snapshot"?

Because at any point in time, the row represents the **current state of the process**.

For example, on August 3:

```text
Created      ✓
Confirmed    ✓
Packed       ✓
Shipped      ✗
Delivered    ✗
```

On August 6:

```text
Created      ✓
Confirmed    ✓
Packed       ✓
Shipped      ✓
Delivered    ✓
```

So you're essentially taking a snapshot of the **progress of each process instance**.

---

## 4. Compare it with the other two

This distinction is extremely important.

### Transaction fact

Records **each individual event**.

```text
Order Created
Order Confirmed
Order Packed
Order Shipped
Order Delivered
```

Potentially:

|Order|Event|Date|
|---|---|---|
|1001|Created|Aug 1|
|1001|Confirmed|Aug 2|
|1001|Packed|Aug 3|
|1001|Shipped|Aug 4|
|1001|Delivered|Aug 6|

**Grain:** one row per event.

---

### Periodic Snapshot

Records the state at a **regular interval**.

For example, every day:

|Date|Order|Status|
|---|---|---|
|Aug 1|1001|Created|
|Aug 2|1001|Confirmed|
|Aug 3|1001|Packed|
|Aug 4|1001|Shipped|
|Aug 5|1001|Shipped|
|Aug 6|1001|Delivered|

**Grain:** one row per entity per snapshot period.

---

### Accumulating Snapshot

One row represents the **whole process**:

|Order|Created|Confirmed|Packed|Shipped|Delivered|
|---|---|---|---|---|---|
|1001|Aug 1|Aug 2|Aug 3|Aug 4|Aug 6|

**Grain:** one row per process instance, such as one order line.

---

# 5. The really important concept: milestone date foreign keys

The book says:

> "There is a date foreign key in the fact table for each critical milestone."

So instead of having just one `Date_Key`, you might have:

```text
Order_Line_Key
Customer_Key
Product_Key

Order_Created_Date_Key
Order_Confirmed_Date_Key
Order_Packed_Date_Key
Order_Shipped_Date_Key
Order_Delivered_Date_Key
```

All of these can point to the **same Dim_Date** table.

For example:

```text
                 Dim_Date
                    ↑
       ┌────────────┼────────────┐
       │            │            │
Created_Date   Packed_Date   Delivered_Date
       │            │            │
       └────── Fact_Order ───────┘
```

These are called **role-playing dates** because the same date dimension plays different roles.

---

# 6. What are "numeric lag measurements"?

This is another very important part.

Because you have milestone dates, you can calculate the **time taken between milestones**.

For example:

```text
Created → Confirmed = 1 day
Confirmed → Packed = 1 day
Packed → Shipped = 1 day
Shipped → Delivered = 2 days
```

You might physically store:

|Order|Confirmed Lag|Packing Lag|Shipping Lag|Delivery Lag|
|---|--:|--:|--:|--:|
|1001|1|1|1|2|

These are **lag measurements**.

You can then calculate:

```text
Average delivery time
Average packing time
Average confirmation time
Average fulfillment time
```

Very useful for operational analytics.

---

# 7. What are "milestone completion counters"?

You can also have indicators such as:

```text
Confirmed_Flag = 1
Packed_Flag = 1
Shipped_Flag = 1
Delivered_Flag = 1
```

Or counters:

```text
Milestones_Completed = 5
```

Suppose another order is still being processed:

|Order|Confirmed|Packed|Shipped|Delivered|
|---|--:|--:|--:|--:|
|1002|1|1|0|0|

Then:

```text
Milestones_Completed = 2
```

This makes pipeline analysis easy.

---

# 8. Where is this useful?

Look for processes that have:

**Start → predictable steps → End**

Examples:

### Order fulfillment

```text
Order → Confirm → Pick → Pack → Ship → Deliver
```

### Insurance claims

```text
Claim submitted
      ↓
Claim reviewed
      ↓
Investigation
      ↓
Approved
      ↓
Payment
      ↓
Closed
```

### Loan processing

```text
Application
    ↓
Credit check
    ↓
Approval
    ↓
Documentation
    ↓
Disbursement
```

### Recruitment

```text
Application
    ↓
Screening
    ↓
Interview
    ↓
Offer
    ↓
Acceptance
    ↓
Joining
```

All of these are excellent candidates for accumulating snapshots.

---

## 9. The most important difference

Remember this simple mental model:

```text
TRANSACTION
     ↓
"What happened?"
     ↓
One row per event


PERIODIC SNAPSHOT
     ↓
"What is the state at this interval?"
     ↓
One row per entity per period


ACCUMULATING SNAPSHOT
     ↓
"How is this process progressing?"
     ↓
One row per process instance
     ↓
Updated as milestones happen
```

### One sentence to remember for interviews

> **An accumulating snapshot fact table tracks the lifecycle of a process in a single row, with milestone dates and measures updated as the process moves from start to completion.**

And the **unique characteristic** you should remember is:

> **Transaction facts are inserted and generally not updated; periodic snapshots are repeatedly inserted; accumulating snapshots are repeatedly updated.**
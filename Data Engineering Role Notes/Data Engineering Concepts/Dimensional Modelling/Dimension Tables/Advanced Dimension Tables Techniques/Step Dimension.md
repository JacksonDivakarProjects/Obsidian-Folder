# Comprehensive Guide to Step Dimensions

A **Step Dimension** is a small dimension used to describe the **position of an event within a sequential business process**.

Think of it as answering:

> **“Which step is this, where does it sit in the process, and how much of the process remains?”**

It is especially useful for processes such as:

- Web sessions
    
- Application workflows
    
- Order fulfillment
    
- Claims processing
    
- Loan applications
    
- Manufacturing processes
    
- Customer onboarding
    
- Recruitment pipelines
    
- Support-ticket workflows
    

---

# 1. Start with the business process

Suppose an e-commerce customer goes through this process:

```text
Home
  ↓
Product
  ↓
Add to Cart
  ↓
Checkout
  ↓
Payment
  ↓
Confirmation
```

There are **6 steps**.

The transaction fact records an event for each step.

### Fact table

|session_key|event|step_key|
|---|---|--:|
|S100|Home|1|
|S100|Product|2|
|S100|Add to Cart|3|
|S100|Checkout|4|
|S100|Payment|5|
|S100|Confirmation|6|

The `step_key` points to the Step Dimension.

---

# 2. What does the Step Dimension contain?

A simple Step Dimension could be:

### `dim_step`

|step_key|step_number|step_name|steps_remaining|
|--:|--:|---|--:|
|1|1|Home|5|
|2|2|Product|4|
|3|3|Add to Cart|3|
|4|4|Checkout|2|
|5|5|Payment|1|
|6|6|Confirmation|0|

Notice the distinction:

```text
step_key
    ↓
warehouse surrogate key

step_number
    ↓
business position in the sequence

step_name
    ↓
what the step actually represents

steps_remaining
    ↓
how much of the process is left
```

---

# 3. The most important attribute: Step Number

`step_number` tells you the position of the current event.

For example:

```text
Home          → 1
Product       → 2
Add to Cart   → 3
Checkout      → 4
Payment       → 5
Confirmation  → 6
```

So if a fact row contains:

```text
step_key = 4
```

you can look up:

```text
step_number = 4
step_name = Checkout
```

Therefore:

> **The customer is currently at step 4 of the process.**

---

# 4. Steps Remaining

This is the other attribute specifically mentioned by Kimball.

Suppose the process has 6 steps.

For step 4:

```text
Total steps = 6
Current step = 4

Steps remaining = 6 - 4
                = 2
```

So:

|Step|Step Name|Steps Remaining|
|--:|---|--:|
|1|Home|5|
|2|Product|4|
|3|Add to Cart|3|
|4|Checkout|2|
|5|Payment|1|
|6|Confirmation|0|

This allows analysis such as:

> "How many sessions reached a stage where they had only two steps left?"

---

# 5. Why make this a dimension?

You might ask:

> Why not simply put `step_number` in the fact table?

You can.

If all you need is:

```text
step_number
```

then a dimension may not provide much value.

But a Step Dimension becomes useful when you want to attach **descriptive properties to each step**.

For example:

|step_key|step_number|step_name|process_stage|steps_remaining|
|--:|--:|---|---|--:|
|1|1|Home|Discovery|5|
|2|2|Product|Discovery|4|
|3|3|Add to Cart|Purchase|3|
|4|4|Checkout|Purchase|2|
|5|5|Payment|Purchase|1|
|6|6|Confirmation|Completion|0|

Now you can analyze by:

- step number
    
- step name
    
- process stage
    
- remaining steps
    

That's the dimensional-modeling advantage.

---

# 6. A more comprehensive Step Dimension

In a real warehouse, you might design something like:

### `dim_step`

|Column|Purpose|
|---|---|
|`step_key`|Surrogate key|
|`step_number`|Position in process|
|`step_name`|Human-readable step name|
|`step_description`|Description of the step|
|`total_steps`|Number of steps in the process|
|`steps_remaining`|Steps remaining after current step|
|`process_stage`|Higher-level grouping|
|`is_first_step`|Whether this is the first step|
|`is_final_step`|Whether this is the final step|
|`step_sequence`|Ordering value|
|`next_step_number`|Next expected step|
|`previous_step_number`|Previous step|
|`step_category`|Business classification|

For example:

|step_key|step_number|step_name|total_steps|steps_remaining|process_stage|is_first|is_final|
|--:|--:|---|--:|--:|---|---|---|
|101|1|Home|6|5|Discovery|Y|N|
|102|2|Product|6|4|Discovery|N|N|
|103|3|Cart|6|3|Purchase|N|N|
|104|4|Checkout|6|2|Purchase|N|N|
|105|5|Payment|6|1|Purchase|N|N|
|106|6|Confirmation|6|0|Completion|N|Y|

---

# 7. But there is an important modeling question: What defines the sequence?

This is where Step Dimensions become more interesting.

Suppose you have two processes:

### Standard checkout

```text
Home → Product → Cart → Checkout → Payment → Confirmation
```

### Guest checkout

```text
Home → Product → Cart → Guest Checkout → Payment → Confirmation
```

The meaning of "Step 4" depends on the process.

Therefore you may need:

```text
process_key
```

in your Step Dimension.

For example:

|step_key|process_key|step_number|step_name|
|--:|--:|--:|---|
|101|1|1|Home|
|102|1|2|Product|
|103|1|3|Cart|
|104|1|4|Checkout|
|105|1|5|Payment|
|201|2|1|Home|
|202|2|2|Product|
|203|2|3|Cart|
|204|2|4|Guest Checkout|
|205|2|5|Payment|

Now the step is defined relative to a particular process.

---

# 8. Step Dimension vs Event Dimension

This distinction is important.

Suppose your fact contains:

|session|event|step_key|
|---|---|--:|
|S100|Viewed homepage|101|
|S100|Viewed product|102|
|S100|Added cart|103|

The **event** tells you:

> What happened?

The **Step Dimension** tells you:

> Where did it happen in the sequence?

So:

```text
Fact
 │
 ├── event_key → Dim Event
 │
 └── step_key  → Dim Step
```

These are different concepts.

---

# 9. Step Dimension vs Date Dimension

Another useful comparison:

### Date Dimension

Answers:

> **When did it happen?**

```text
date_key
calendar_date
month
quarter
year
weekday
```

### Step Dimension

Answers:

> **Where in the process did it happen?**

```text
step_key
step_number
step_name
steps_remaining
```

So a fact might contain both:

```text
fact_web_event

date_key
time_key
session_key
page_key
step_key
...
```

---

# 10. Step Dimension vs Accumulating Snapshot

This is particularly important because you've been studying accumulating snapshots.

### Step Dimension

Suppose:

```text
Session S100
```

has:

```text
Step 1
Step 2
Step 3
Step 4
Step 5
```

The fact has **multiple rows**:

|Session|Step|
|---|--:|
|S100|1|
|S100|2|
|S100|3|
|S100|4|
|S100|5|

---

### Accumulating Snapshot

Instead, you might have:

|Order|Order Date|Pick Date|Ship Date|Delivery Date|
|---|---|---|---|---|
|O100|Jan 1|Jan 2|Jan 3|Jan 5|

One row represents the **entire process**, with milestone dates updated as the process progresses.

So:

**Step Dimension → describes individual process events.**

**Accumulating Snapshot → tracks the lifecycle of the process.**

---

# 11. What happens when someone drops out?

This is where Step Dimensions become extremely useful.

Suppose you have:

```text
S100:
Home → Product → Cart → Checkout → Payment → Confirmation

S101:
Home → Product → Cart → Checkout
```

S101 never reached Payment.

Your fact contains:

|Session|Step|
|---|--:|
|S101|1|
|S101|2|
|S101|3|
|S101|4|

You can analyze:

```text
Step 1 → 10,000 sessions
Step 2 → 8,000
Step 3 → 6,000
Step 4 → 4,000
Step 5 → 3,000
Step 6 → 2,500
```

Now you can calculate funnel conversion.

For example:

```text
Step 4 → Step 5

3,000 / 4,000 = 75%
```

The Step Dimension gives you the **ordered structure** required to interpret these events.

---

# 12. What does "how many more steps were required" really help with?

Suppose you want to group users by how close they were to completing the process.

You could ask:

> How many events occurred when users were within two steps of completion?

The Step Dimension lets you filter:

```text
steps_remaining <= 2
```

which means:

```text
Checkout
Payment
Confirmation
```

You can then analyze behavior near completion.

---

# 13. Surrogate key in the Step Dimension

Like other dimensions, the Step Dimension normally has a surrogate key:

```text
step_key
```

For example:

```text
step_key = 101
```

The fact stores:

```text
step_key = 101
```

This is **not the same as the step number**.

Don't confuse:

```text
step_key = 101
```

with:

```text
step_number = 1
```

The first is the warehouse identifier.

The second is the business sequence.

---

# 14. The fact table relationship

A simplified model looks like:

```text
                 dim_step
                    │
                    │ step_key
                    ▼
              fact_web_event
                    ▲
                    │
       ┌────────────┼────────────┐
       │            │            │
       ▼            ▼            ▼
 dim_date     dim_customer   dim_page
```

The fact might be:

|event_fact_key|session_key|date_key|page_key|step_key|
|--:|---|--:|--:|--:|
|1001|S100|20260820|11|101|
|1002|S100|20260820|12|102|
|1003|S100|20260820|13|103|

---

# 15. One subtle issue: Step number is usually not globally unique

This is important.

You could have:

```text
Process A:
Step 1 = Application Started

Process B:
Step 1 = Order Created
```

So:

```text
step_number = 1
```

doesn't uniquely identify a business step.

That's why a surrogate:

```text
step_key
```

is useful.

The combination might conceptually be:

```text
process + step_number
```

while the warehouse uses:

```text
step_key
```

as the FK.

---

# 16. What should you put in the Step Dimension?

A good practical design is:

```text
dim_step
────────────────────────────
step_key
process_key
step_number
step_name
step_description
step_category
process_stage
total_steps
steps_remaining
is_first_step
is_final_step
previous_step_number
next_step_number
```

You don't necessarily need every one of these. The exact attributes depend on the business process.

The **core attributes from the book's idea** are:

```text
step_key
step_number
steps_remaining
```

Everything else is additional descriptive context.

---

# 17. The grain of the fact is still critical

Suppose you have:

> One row per web-page event.

Then:

```text
S100 + Home
S100 + Product
S100 + Cart
```

are individual fact rows.

The Step Dimension does **not** mean:

> One row per session.

Instead:

> **The fact grain determines what an individual event row represents; the Step Dimension tells you where that event belongs in the process.**

This is a very important dimensional-modeling principle.

---

# 18. Common mistake: Thinking Step Dimension stores the events

It doesn't.

Bad mental model:

```text
dim_step
────────────
Home
Product
Cart
Checkout
```

and thinking:

> "This dimension contains my web events."

Not necessarily.

The Step Dimension describes the **position/type of the step**.

The fact records the **actual occurrence**.

For example:

```text
dim_step
Step 3 = Add to Cart
```

Then:

```text
fact_web_event

Session S100 → Step 3 → 10:32 AM
Session S101 → Step 3 → 10:41 AM
Session S102 → Step 3 → 11:05 AM
```

The dimension describes the step.

The fact records each occurrence.

---

# 19. A complete example

Let's put everything together.

### Step Dimension

|step_key|process|step_number|step_name|stage|total_steps|steps_remaining|
|--:|---|--:|---|---|--:|--:|
|101|Checkout|1|Home|Discovery|6|5|
|102|Checkout|2|Product|Discovery|6|4|
|103|Checkout|3|Cart|Purchase|6|3|
|104|Checkout|4|Checkout|Purchase|6|2|
|105|Checkout|5|Payment|Purchase|6|1|
|106|Checkout|6|Confirmation|Completion|6|0|

### Fact

|session|customer|step_key|timestamp|
|---|---|--:|---|
|S100|C1|101|10:00|
|S100|C1|102|10:02|
|S100|C1|103|10:05|
|S100|C1|104|10:06|
|S100|C1|105|10:08|
|S100|C1|106|10:09|
|S101|C2|101|11:00|
|S101|C2|102|11:02|
|S101|C2|103|11:05|
|S101|C2|104|11:06|

Now you can answer:

- How many sessions reached each step?
    
- Where is the biggest drop-off?
    
- How many sessions completed the process?
    
- How many sessions reached the final two steps?
    
- How long did users spend between steps?
    
- Which customer segments drop out at which step?
    
- Which product/page leads to abandonment?
    

---

# 20. The Pareto view

For your dimensional-modeling studies, I'd prioritize these **5 things**.

### ① Understand the problem

Sequential process:

```text
Step 1 → Step 2 → Step 3 → Step 4
```

The fact has one row per event/step.

### ② Understand the purpose

The Step Dimension tells you:

```text
"Where is this event in the sequence?"
```

### ③ Know the core attributes

```text
step_key
step_number
steps_remaining
```

### ④ Understand the analytical use

It enables:

```text
funnel analysis
drop-off analysis
process progression
step-based segmentation
```

### ⑤ Don't confuse it with accumulating snapshots

```text
Step Dimension
→ describes the position of each event

Accumulating Snapshot
→ tracks the lifecycle of the entire process
```

---

## The mental model I recommend

Whenever you see **Step Dimension**, immediately think:

```text
BUSINESS PROCESS
       │
       ▼
Step 1 → Step 2 → Step 3 → Step 4 → Step 5
          │
          ▼
      FACT TABLE
          │
          └── one row for each actual event

          │
          ▼
     STEP DIMENSION
          │
          ├── What step?
          ├── Which position?
          ├── Which stage?
          ├── How many steps remain?
          └── Is it first/final?
```

**In one sentence:**

> A **Step Dimension** provides descriptive context about the position of an individual fact event within a sequential business process, making it easier to analyze progression, drop-offs, and completion through the process.
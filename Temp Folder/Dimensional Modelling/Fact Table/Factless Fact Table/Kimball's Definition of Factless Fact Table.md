Yes. This section introduces an important type of fact table: a **factless fact table**.

## 1. What is a factless fact table?

A normal fact table usually has **numeric measurements**:

```text
Sales Fact
----------------
ProductKey
CustomerKey
DateKey
Quantity        ← numeric fact
SalesAmount     ← numeric fact
DiscountAmount  ← numeric fact
```

But sometimes a **business event happened**, yet there is **nothing numeric to measure**.

You still want to record that event.

That's a **factless fact table**.

> **A factless fact table records that an event occurred, using only dimension foreign keys, without numeric measures.**

---

# 2. Example: Student attending a class

Suppose a university has this business event:

> Student attended a class on a particular day.

You might have:

```text
fact_class_attendance
---------------------
DateKey
StudentKey
TeacherKey
LocationKey
ClassKey
```

There may be no numeric measurement.

You're simply recording:

> **Student S1 attended Class C1, taught by Teacher T1, at Location L1 on August 10.**

The row itself is the fact:

```text
Date + Student + Teacher + Location + Class
                ↓
          Attendance happened
```

There is no need for:

```text
Quantity
SalesAmount
Cost
```

---

# 3. Why is it still called a FACT table?

Because the row represents a **business event**.

Remember your fundamental definition:

> **A fact table row represents a business process event at the declared grain.**

A fact doesn't necessarily have to be numeric.

The fact here is:

> **An attendance event occurred.**

So:

```text
Fact ≠ necessarily numeric value
```

More precisely:

```text
Fact table
   ↓
Business event
   ↓
May have numeric measurements
OR
May simply record that something happened
```

---

# 4. What does the grain look like?

This is extremely important.

For the attendance example, you might declare:

> **One row represents one student's attendance at one class on one day.**

Therefore:

```text
Date
+
Student
+
Class
+
Teacher
+
Location
=
One attendance event
```

Your factless fact table could look like:

|DateKey|StudentKey|TeacherKey|LocationKey|ClassKey|
|---|---|---|---|---|
|Aug10|S101|T10|Room1|Math|
|Aug10|S102|T10|Room1|Math|
|Aug10|S103|T10|Room1|Math|

There are **no numeric fact columns**.

But each row says:

> This event happened.

---

# 5. Another example: Customer communication

Suppose a company records:

> Customer received an email.

You could have:

```text
fact_customer_communication
---------------------------
DateKey
CustomerKey
EmployeeKey
CommunicationTypeKey
ChannelKey
```

For example:

|Date|Customer|Communication|Channel|
|---|---|---|---|
|Aug 10|C101|C202|Email|
|Aug 10|C102|C203|Phone|
|Aug 11|C101|C204|Email|

Again, there may be **no numerical measurement**.

The event itself is what matters.

---

# 6. The really interesting part: analyzing what DIDN'T happen

This is where factless fact tables become particularly powerful.

Imagine a university has:

> 100 students enrolled in a class.

You want to know:

> **Which students did NOT attend?**

A normal activity fact table only records:

> Who attended.

It doesn't contain rows for students who didn't attend.

So how do we find the missing events?

Kimball says you use **two tables**:

### 1. Coverage table

Contains:

> **Everything that could/should happen.**

### 2. Activity table

Contains:

> **Everything that actually happened.**

Then:

```text
Coverage
   -
Activity
   =
What didn't happen
```

---

# 7. Coverage table

Suppose there are 3 students:

```text
S1
S2
S3
```

and they are all expected to attend Math class on August 10.

The coverage table represents all expected possibilities:

|Date|Student|Class|
|---|---|---|
|Aug10|S1|Math|
|Aug10|S2|Math|
|Aug10|S3|Math|

This says:

> These are the attendance events that **could/should happen**.

---

# 8. Activity factless fact table

Now suppose only S1 and S3 actually attended.

Activity table:

|Date|Student|Class|
|---|---|---|
|Aug10|S1|Math|
|Aug10|S3|Math|

This says:

> These events **actually happened**.

---

# 9. Subtract them

Coverage:

```text
S1
S2
S3
```

Activity:

```text
S1
S3
```

Therefore:

```text
Coverage - Activity
        ↓
       S2
```

So:

> **S2 did not attend.**

That's what Kimball means by:

> "Factless fact tables can also be used to analyze what didn't happen."

---

# 10. Think of it as EXPECTED vs ACTUAL

This is probably the easiest way to remember it.

```text
             FACTLESS ANALYSIS
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
      COVERAGE              ACTIVITY
      EXPECTED               ACTUAL
          │                   │
          │                   │
          └─────────┬─────────┘
                    ▼
             Coverage - Activity
                    ↓
              DIDN'T HAPPEN
```

### Coverage

> What was possible/expected?

### Activity

> What actually happened?

### Difference

> What did not happen?

---

# 11. Real-world example: Employee training

Suppose HR requires 1,000 employees to complete a training course.

### Coverage

The coverage table contains:

```text
Employee + Training Course + Required Date
```

for all employees who are supposed to complete it.

### Activity

The activity factless fact table contains:

```text
Employee + Training Course + Completion Date
```

for employees who actually completed it.

Then:

```text
Required employees
        -
Completed employees
        =
Employees who didn't complete
```

This is extremely useful for:

- compliance
    
- attendance
    
- training
    
- promotions
    
- customer outreach
    
- scheduled appointments
    
- eligibility
    
- service participation
    

---

# 12. Coverage doesn't necessarily mean "guaranteed"

The book says:

> "all the possibilities of events that might happen"

So coverage is essentially the **universe of combinations you want to evaluate**.

For example:

> Which students were eligible/expected to attend which classes?

or:

> Which customers were eligible to receive which promotions?

or:

> Which employees were required to complete which training?

The exact business definition of "coverage" depends on the process.

---

# 13. Activity vs Coverage

||Coverage|Activity|
|---|---|---|
|Represents|Possible/expected events|Actual events|
|Contains|All relevant possibilities|Events that happened|
|Numeric measures required?|No|No|
|Typical use|What should/could happen?|What happened?|
|Difference|—|Coverage − Activity = didn't happen|

---

# 14. Important: Factless doesn't mean "fact table with no data"

This is a common misunderstanding.

A factless fact table still contains **data**.

For example:

```text
DateKey
StudentKey
ClassKey
TeacherKey
LocationKey
```

Those foreign keys are data.

What it lacks is:

> **Numeric measurement columns.**

So:

```text
Factless
    ≠
Empty
```

It means:

> **No numeric facts/measures are required to represent the event.**

---

# 15. Grain is still critical

Even though there are no numeric facts, you still have to declare the grain.

For example:

> **One row = one student attending one class on one day.**

That tells you exactly what the row means.

Then you identify the dimensions needed to describe that event:

```text
Date
Student
Class
Teacher
Location
```

So the same dimensional modeling principles still apply:

```text
Business Process
      ↓
Declare Grain
      ↓
Identify Dimensions
      ↓
Identify Facts
```

But in this case:

```text
Numeric Facts
     ↓
None
```

---

# 16. How do you query a factless fact table?

Because the dimension keys identify the event, you can count rows.

For example:

> How many classes did a student attend?

Conceptually:

```sql
COUNT(*)
```

grouped by student.

Or:

> How many students attended each class?

```sql
COUNT(*)
```

grouped by class.

So although there is no `AttendanceCount` column, the **rows themselves represent occurrences**.

---

# 17. The key distinction: normal fact vs factless fact

### Normal fact table

```text
DateKey
ProductKey
CustomerKey
Quantity
SalesAmount
```

The row represents:

> Sale happened + measurements of the sale.

### Factless fact table

```text
DateKey
StudentKey
ClassKey
TeacherKey
LocationKey
```

The row represents:

> Attendance happened.

No numeric measurement is necessary.

---

# 18. Revision summary

### Factless Fact Table

> A fact table that records the occurrence of a business event without numeric measures.

### Typical structure

```text
Dimension FK
Dimension FK
Dimension FK
Dimension FK
...
```

### Example

> Student attended a class.

```text
DateKey
StudentKey
TeacherKey
ClassKey
LocationKey
```

### Grain

> One row = one student attending one class at one location on one day.

### Why useful?

It can answer:

> **What happened?**

and, with a coverage table:

> **What did not happen?**

### Coverage analysis

```text
Coverage = all expected/possible events
Activity  = events that actually happened

Coverage - Activity
       =
Events that did not happen
```

### One sentence to remember

> **A factless fact table records that a business event occurred, even when there is no numeric measurement; when paired with a coverage table, it can also identify events that were expected/possible but did not occur.**
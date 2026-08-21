# Comprehensive Guide to Grouped Dimensions, Bridge Tables, and Time-Varying Multivalued Relationships

## 1. Why do we need these concepts?

In a traditional dimensional model, we usually expect a fact row to contain **one key for each dimension**.

For example:

```text
                Customer Dimension
                       ↑
                       |
                  customer_key
                       |
                    Fact Table
                       |
                  product_key
                       |
                       ↓
                 Product Dimension
```

A fact row might represent:

> One customer purchased one product for $500.

That works well when the relationship between the fact and each dimension is **single-valued**.

However, some business situations are naturally **multi-valued**.

For example:

- A patient can have multiple simultaneous diagnoses.
    
- A bank account can have multiple customers.
    
- A property can have multiple owners.
    
- A policy can have multiple beneficiaries.
    
- A student can belong to multiple programs.
    

A normal foreign key cannot represent these relationships cleanly.

That is where **group dimensions, bridge tables, and time-varying bridge tables** become useful.

---

# 2. What is a grouped dimension?

A grouped dimension is a way of representing a **set of related dimension members as one group**.

Suppose a patient has three diagnoses:

```text
D01 = Diabetes
D02 = Hypertension
D03 = Kidney Disease
```

Instead of putting three diagnosis keys into a fact row, we create a group:

```text
Group G100
    |
    ├── D01 → Diabetes
    ├── D02 → Hypertension
    └── D03 → Kidney Disease
```

The fact table then stores only:

```text
diagnosis_group_key = G100
```

So the fact says:

> "This treatment is associated with diagnosis group G100."

The group then tells us which individual diagnoses belong to that group.

---

# 3. What is a bridge table?

The **bridge table is the table that maps a group to its individual dimension members**.

For the diagnosis example:

### Diagnosis Dimension

```text
diagnosis_key | diagnosis
--------------|----------------
D01           | Diabetes
D02           | Hypertension
D03           | Kidney Disease
D04           | Asthma
```

### Bridge Table

```text
group_key | diagnosis_key
----------|--------------
G100      | D01
G100      | D02
G100      | D03
G101      | D02
G101      | D04
```

### Fact Table

```text
treatment_key | patient_key | diagnosis_group_key | cost
--------------|-------------|---------------------|-----
1001          | P101        | G100                | 5000
1002          | P102        | G101                | 3000
```

The relationship is:

```text
Treatment Fact
      |
      | diagnosis_group_key
      ↓
Bridge Table
      |
      | diagnosis_key
      ↓
Diagnosis Dimension
```

For treatment `1001`:

```text
1001
 ↓
G100
 ↓
D01, D02, D03
 ↓
Diabetes, Hypertension, Kidney Disease
```

Therefore, one fact row can represent **multiple diagnoses**.

---

# 4. Why not put multiple dimension keys directly in the fact?

You might initially think about doing this:

```text
treatment_key | diagnosis_1 | diagnosis_2 | diagnosis_3
--------------|--------------|--------------|-------------
1001          | D01          | D02          | D03
```

This has several problems.

First, the number of diagnoses is not fixed.

One patient may have:

```text
D01
```

Another may have:

```text
D01, D02
```

Another may have:

```text
D01, D02, D03, D04, D05
```

You would need an arbitrary number of columns.

You also create awkward SQL and violate the clean dimensional-modeling principle of having a stable schema.

The bridge table solves this:

```text
G100 → D01
G100 → D02
G100 → D03
```

There can be any number of diagnosis rows without changing the fact-table structure.

---

# 5. What problem does the group key solve?

The group key allows the fact table to remain at its original grain.

Suppose the fact grain is:

> One row = one treatment.

Then:

```text
Treatment Fact
1001 → G100
```

still means one treatment.

The bridge contains the multiple diagnoses:

```text
G100 → D01
G100 → D02
G100 → D03
```

So the fact table does not become:

```text
1001 → D01
1001 → D02
1001 → D03
```

which would potentially create three fact rows and change the grain.

The group key therefore acts as a **single representative key for a collection of dimension members**.

---

# 6. Important: the bridge table is not the dimension

This distinction is important.

### Diagnosis Dimension

Describes the diagnosis:

```text
D01 | Diabetes
D02 | Hypertension
D03 | Kidney Disease
```

### Bridge Table

Describes the relationship:

```text
G100 | D01
G100 | D02
G100 | D03
```

So:

> The dimension describes the business entity.

> The bridge describes which dimension members belong to the group.

The bridge is essentially a **relationship or mapping table**.

---

# 7. A second example: bank accounts and customers

Healthcare is one example.

A very common example is:

> One bank account can belong to multiple customers.

Suppose:

```text
A1 = Joint Account 001

Customers:
C1 = Alice
C2 = Bob
```

The relationship is:

```text
A1
 |
 ├── C1 → Alice
 └── C2 → Bob
```

This is a many-to-many relationship.

One account can have many customers.

One customer can also own many accounts.

---

# 8. Basic bridge table for bank accounts

### Account Dimension

```text
account_key | account_name
------------|--------------
A1          | Account 001
A2          | Account 002
```

### Customer Dimension

```text
customer_key | customer_name
-------------|--------------
C1           | Alice
C2           | Bob
C3           | Charlie
```

### Bridge Table

```text
account_key | customer_key
------------|-------------
A1          | C1
A1          | C2
A2          | C1
A2          | C3
```

This means:

```text
Account A1 → Alice + Bob
Account A2 → Alice + Charlie
```

---

# 9. Why is this called a multivalued dimension?

In a traditional dimensional model, the fact might have:

```text
customer_key = C1
```

meaning one customer.

With a multivalued relationship, the fact may conceptually be associated with:

```text
C1 + C2
```

at the same time.

The customer dimension is therefore **multivalued with respect to the fact**.

The bridge table allows this without putting multiple customer keys directly into the fact.

---

# 10. What is a time-varying multivalued bridge table?

Now we introduce the next problem.

Relationships can change over time.

For example:

### January

```text
Account A1 → Alice
Account A1 → Bob
```

### July

Bob leaves the account.

```text
Account A1 → Alice
```

### September

Charlie joins.

```text
Account A1 → Alice
Account A1 → Charlie
```

A simple bridge table cannot represent this history correctly:

```text
account_key | customer_key
------------|-------------
A1          | C1
A1          | C2
A1          | C3
```

Looking at this table, we cannot determine:

> Was Bob associated with the account in January?

or:

> Was Charlie already associated with the account in January?

We need time information.

---

# 11. Time-varying bridge table

We add effective and expiration timestamps.

```text
account_key | customer_key | effective_date | expiration_date
------------|--------------|----------------|----------------
A1          | C1           | 2025-01-01     | NULL
A1          | C2           | 2025-01-01     | 2025-06-30
A1          | C3           | 2025-09-01     | NULL
```

Interpretation:

```text
Alice:
2025-01-01 → current

Bob:
2025-01-01 → 2025-06-30

Charlie:
2025-09-01 → current
```

Now the bridge itself contains the **history of the relationship**.

---

# 12. The relationship is what changes

This is an important conceptual distinction.

There are two different things that can change:

### Dimension attribute changes

For example:

```text
Customer:
Alice
    ↓
Alice Smith
```

This is a classic **SCD Type 2 dimension change** if historical versions are required.

### Relationship changes

For example:

```text
Account A1
    ↓
Alice + Bob

Later:

Account A1
    ↓
Alice only
```

This is a **relationship change**.

A time-varying bridge captures this second type of change.

Therefore:

```text
Dimension changes over time
        ↓
SCD Type 2

Relationship changes over time
        ↓
Time-varying bridge
```

In many real systems, you need both.

---

# 13. Why do we care about SCD Type 2 dimensions?

Suppose Account and Customer are themselves Type 2 dimensions.

For example:

```text
Customer Dimension

customer_key | customer_id | name  | effective | expiration
-------------|--------------|-------|-----------|-----------
101          | C1           | Alice | Jan 2025  | Dec 2025
205          | C1           | Alice | Jan 2026  | NULL
```

The business customer is still Alice, but the warehouse has different **dimension versions**.

Similarly, an account can have multiple Type 2 versions.

The bridge must therefore avoid incorrectly connecting:

```text
old Account version
```

to:

```text
new Customer version
```

for a period where that relationship did not exist.

That is why the bridge needs time boundaries.

---

# 14. What does "prevent incorrect linkages" mean?

Suppose:

```text
January:
A1 → Alice + Bob

July:
Bob leaves
```

If the bridge has no dates:

```text
A1 → Alice
A1 → Bob
```

A query run for December might incorrectly conclude:

```text
A1 → Bob
```

even though Bob left in June.

Adding dates fixes this.

---

# 15. Querying a time-varying bridge

Suppose we want:

> Who was associated with Account A1 on March 15, 2025?

We use:

```sql
SELECT
    b.account_key,
    b.customer_key
FROM account_customer_bridge AS b
WHERE b.account_key = 'A1'
  AND b.effective_date <= '2025-03-15'
  AND (
        b.expiration_date IS NULL
        OR b.expiration_date > '2025-03-15'
      );
```

Result:

```text
account_key | customer_key
------------|-------------
A1          | C1
A1          | C2
```

So:

```text
A1 → Alice
A1 → Bob
```

---

# 16. Querying after Bob leaves

Suppose we ask:

> Who was associated with A1 on August 15?

```sql
SELECT
    b.account_key,
    b.customer_key
FROM account_customer_bridge AS b
WHERE b.account_key = 'A1'
  AND b.effective_date <= '2025-08-15'
  AND (
        b.expiration_date IS NULL
        OR b.expiration_date > '2025-08-15'
      );
```

Bob's row has:

```text
expiration_date = 2025-06-30
```

so Bob is excluded.

The result might be:

```text
account_key | customer_key
------------|-------------
A1          | C1
```

Therefore:

```text
A1 → Alice
```

---

# 17. Querying after Charlie joins

For:

```text
2025-10-01
```

the result becomes:

```text
A1 → Alice
A1 → Charlie
```

because:

```text
Alice:
Jan → current

Charlie:
Sep → current
```

---

# 18. Why does the requesting application need to specify a point in time?

The book says the:

> "requesting application must constrain the bridge table to a specific moment in time"

This means the application should not simply run:

```sql
SELECT *
FROM account_customer_bridge;
```

and assume that represents the current or historical relationship.

Instead, it should say:

```text
"Show me the relationship as of March 15."
```

or:

```text
"Show me the relationship as of September 30."
```

Then SQL applies the time condition.

Conceptually:

```text
              Bridge History
                   |
      ┌────────────┼────────────┐
      ↓            ↓            ↓
    January       June       September
      |
      ↓
Choose a specific moment
      |
      ↓
Produce a consistent snapshot
```

---

# 19. What does "snapshot" mean here?

A snapshot means:

> "Pretend we freeze the system at one particular point in time."

For example:

```text
As of 2025-03-15:

A1 → Alice
A1 → Bob
```

versus:

```text
As of 2025-08-15:

A1 → Alice
```

versus:

```text
As of 2025-10-15:

A1 → Alice
A1 → Charlie
```

The same historical bridge table can therefore produce different answers depending on the requested date.

---

# 20. Connection with periodic snapshot fact tables

This connects directly to the previous concept you were asking about.

A **periodic snapshot fact table** creates a record for each reporting period.

For example:

```text
month | account | customer_group | balance
------|---------|----------------|--------
Jan   | A1      | G100           | 5000
Feb   | A1      | G100           | 5100
Mar   | A1      | G101           | 5200
```

Because each period has a row, the dimensional relationships can be captured for that period.

That is why periodic snapshots are particularly suitable for models where dimensional relationships need to be reconstructed through the fact.

The key idea is:

```text
Periodic snapshot
       ↓
A row exists for every reporting period
       ↓
Relevant dimension keys are recorded
       ↓
Historical relationships can be reconstructed
```

This is not a requirement for every bridge table, but it is a particularly strong use case.

---

# 21. A complete bank-account example

Let's put everything together.

### Account Dimension

```text
account_key | account_id | account_type | effective | expiration
------------|------------|--------------|-----------|-----------
101         | A1         | Checking     | Jan 2025  | Dec 2025
205         | A1         | Checking     | Jan 2026  | NULL
```

### Customer Dimension

```text
customer_key | customer_id | customer_name | effective | expiration
-------------|-------------|---------------|-----------|-----------
501          | C1          | Alice         | Jan 2025  | NULL
502          | C2          | Bob           | Jan 2025  | NULL
503          | C3          | Charlie       | Sep 2025  | NULL
```

### Time-Varying Bridge

```text
account_key | customer_key | effective_date | expiration_date
------------|--------------|----------------|----------------
101         | 501          | 2025-01-01     | NULL
101         | 502          | 2025-01-01     | 2025-06-30
101         | 503          | 2025-09-01     | NULL
```

Now:

### March

```text
A1
 ├── Alice
 └── Bob
```

### August

```text
A1
 └── Alice
```

### October

```text
A1
 ├── Alice
 └── Charlie
```

The bridge has preserved the complete relationship history.

---

# 22. SQL for the complete lookup

Suppose we want all customers associated with Account A1 on a given date.

```sql
DECLARE @as_of_date DATE = '2025-08-15';

SELECT
    b.account_key,
    b.customer_key,
    c.customer_name
FROM account_customer_bridge AS b
JOIN customer_dim AS c
    ON b.customer_key = c.customer_key
WHERE b.account_key = '101'
  AND b.effective_date <= @as_of_date
  AND (
        b.expiration_date IS NULL
        OR b.expiration_date > @as_of_date
      );
```

The important part is the temporal filter:

```sql
b.effective_date <= @as_of_date
AND (
    b.expiration_date IS NULL
    OR b.expiration_date > @as_of_date
)
```

This means:

> Find relationships that were active on the requested date.

---

# 23. A useful mental model

You can think of the three concepts this way:

### Grouped dimension

> "These several dimension members form one group."

```text
G100
 ├── D01
 ├── D02
 └── D03
```

### Bridge table

> "This table tells me which dimension members belong to the group."

```text
G100 → D01
G100 → D02
G100 → D03
```

### Time-varying bridge

> "This table tells me which members belonged to the group and when."

```text
G100 → D01 → Jan to current
G100 → D02 → Jan to Jun
G100 → D03 → Sep to current
```

---

# 24. The three levels of complexity

You can remember the progression like this:

```text
LEVEL 1
Normal dimension relationship

Fact → Dimension

One fact → one dimension member
```

```text
LEVEL 2
Multivalued relationship

Fact → Group → Bridge → Multiple dimension members

One fact → multiple dimension members
```

```text
LEVEL 3
Time-varying multivalued relationship

Fact → Group → Time-aware Bridge → Multiple dimension members

One fact → multiple members
                +
          relationship changes over time
```

---

# 25. Common mistakes

### Mistake 1: Putting multiple IDs in one column

Bad:

```text
diagnosis_keys = 'D01,D02,D03'
```

The database cannot treat this as a clean dimensional relationship.

---

### Mistake 2: Creating multiple foreign-key columns

Bad:

```text
diagnosis_1
diagnosis_2
diagnosis_3
diagnosis_4
```

This assumes an arbitrary maximum number of diagnoses.

---

### Mistake 3: Forgetting the grain

If the fact grain is:

> One treatment

do not create three treatment fact rows merely because there are three diagnoses.

That can duplicate measures such as:

```text
treatment_cost = 5000
```

and accidentally make it appear to be:

```text
5000 + 5000 + 5000 = 15000
```

---

### Mistake 4: Ignoring time

If the relationship changes over time, a bridge without effective/expiration dates cannot reliably answer historical questions.

---

### Mistake 5: Joining a historical bridge without an "as-of" date

You may accidentally mix historical relationships from different time periods and produce an inconsistent result.

---

# 26. When should you use a bridge table?

A bridge is appropriate when the relationship is genuinely multivalued.

Examples:

```text
Patient ↔ Diagnosis
Account ↔ Customer
Policy ↔ Beneficiary
Property ↔ Owner
Student ↔ Program
Employee ↔ Skill
```

It is especially useful when the number of related dimension members is variable.

---

# 27. When should the bridge be time-varying?

Use a time-varying bridge when:

1. The relationship can change over time.
    
2. Historical relationships matter.
    
3. You need to answer "who/what was associated at that point in time?"
    
4. The related dimensions themselves may have Type 2 history.
    

For example:

```text
Account ↔ Customer
```

is a strong candidate because customers can join or leave an account.

---

# 28. The most important distinction

Do not confuse these three things:

```text
SCD Type 2
    =
History of a dimension entity/attribute
```

```text
Bridge table
    =
Many-to-many relationship
```

```text
Time-varying bridge
    =
History of the many-to-many relationship
```

You can have:

```text
SCD2 Dimension + Static Bridge
```

or:

```text
SCD2 Dimension + Time-varying Bridge
```

depending on whether the **relationship itself** needs historical tracking.

---

# 29. Final picture

The whole concept can be summarized as:

```text
                         DIMENSION
                       ┌────────────┐
                       │ Diagnosis  │
                       │    D01     │
                       │    D02     │
                       │    D03     │
                       └─────▲──────┘
                             │
                     diagnosis_key
                             │
                       ┌─────┴──────┐
                       │   BRIDGE   │
                       │            │
                       │ group_key  │
                       │ diagnosis  │
                       │ effective  │
                       │ expiration │
                       └─────▲──────┘
                             │
                          group_key
                             │
                       ┌─────┴──────┐
                       │    FACT    │
                       │            │
                       │ treatment  │
                       │ patient    │
                       │ group_key  │
                       │ measures   │
                       └────────────┘
```

The fact says:

> "This event belongs to group G100."

The bridge says:

> "G100 contains D01, D02, and D03."

The time columns say:

> "Those relationships were valid during this particular time period."

That is the essence of **grouped dimensions, bridge tables, and time-varying multivalued bridge tables**.
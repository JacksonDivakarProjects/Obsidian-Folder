# Comprehensive Guide: Supertype and Subtype Schemas for Heterogeneous Products

This pattern is one of the more advanced dimensional modeling techniques. The easiest way to understand it is to start with the **problem it solves**.

---

## 1. The problem: heterogeneous products

Imagine a bank offering:

```text
Account
│
├── Checking Account
├── Savings Account
├── Mortgage
├── Personal Loan
├── Business Loan
└── Credit Card
```

All of these are **accounts/products**, so they share some common characteristics.

For example:

- Account number
    
- Customer
    
- Branch
    
- Open date
    
- Close date
    
- Currency
    
- Status
    
- Account type
    

But their **business measurements are very different**.

### Checking account

- Deposits
    
- Withdrawals
    
- Transaction count
    
- Interest earned
    
- Balance
    

### Mortgage

- Original loan amount
    
- Principal outstanding
    
- Interest
    
- Payment
    
- Loan-to-value ratio
    
- Remaining term
    

### Credit card

- Purchases
    
- Cash advances
    
- Credit limit
    
- Available credit
    
- Finance charges
    

### Business loan

- Disbursement
    
- Principal
    
- Interest
    
- Collateral value
    
- Risk rating
    

This creates a modeling problem.

---

# 2. The bad solution: one giant fact table

A beginner might say:

> "Let's create one `fact_account` table containing every possible measure."

It might look like:

|account_key|date_key|balance|deposits|withdrawals|mortgage_amount|LTV|credit_limit|purchases|collateral|...|
|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|
|101|1|5000|1000|500|NULL|NULL|NULL|NULL|NULL|...|
|102|1|250000|NULL|NULL|300000|80%|NULL|NULL|400000|...|
|103|1|80000|NULL|NULL|NULL|NULL|NULL|NULL|500000|...|

This becomes terrible.

Why?

Because each product type needs completely different facts.

You could end up with **hundreds of columns**, most of which are `NULL` for most rows.

The table becomes:

- Very wide
    
- Sparse
    
- Difficult to understand
    
- Difficult to maintain
    
- Difficult to ETL
    
- Difficult for BI users
    
- Full of unrelated measures
    

This is what Kimball means when he says the approach will **fail**.

---

# 3. The solution: Supertype + Subtype

Instead, recognize that there are two kinds of information:

### Common information

Information that applies to **all account types**.

### Specialized information

Information that applies only to a **specific account type**.

So we separate them.

```text
                    ACCOUNT
                   SUPERTYPE
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
      Checking      Mortgage     Business
      SUBTYPE       SUBTYPE       SUBTYPE
```

In dimensional modeling terminology:

|Term|Meaning|
|---|---|
|Supertype|Core|
|Subtype|Custom|
|Supertype fact|Core fact|
|Subtype fact|Custom fact|
|Supertype dimension|Common dimension|
|Subtype dimension|Specialized dimension|

---

# 4. The most important concept: intersection

The book uses the word **intersection**.

This is extremely important.

Suppose:

### Checking has

```text
Balance
Deposit
Withdrawal
Interest
```

### Mortgage has

```text
Balance
Principal
Interest
Payment
LTV
```

### Business loan has

```text
Balance
Principal
Interest
Disbursement
Collateral
```

The common facts are:

```text
Balance
Interest
```

Those common facts form the **core/supertype fact**.

Everything else remains in the appropriate subtype fact.

So:

```text
Checking
    ├── Balance       → Core
    ├── Deposit       → Checking custom
    ├── Withdrawal    → Checking custom
    └── Interest      → Core

Mortgage
    ├── Balance       → Core
    ├── Principal     → Mortgage custom
    ├── Interest      → Core
    ├── Payment       → Mortgage custom
    └── LTV           → Mortgage custom
```

### Mental model

> **Core = intersection/commonality**

> **Custom = differences**

---

# 5. Core dimension

Now let's build the dimensional model.

The common account attributes go into:

```text
dim_account
```

Example:

|account_key|account_number|account_type|customer_key|branch_key|status|open_date|
|--:|---|---|--:|--:|---|---|
|101|A100|Checking|5001|10|Active|2020-01-01|
|102|A200|Mortgage|5002|11|Active|2022-05-01|
|103|A300|Business Loan|5003|12|Active|2024-03-01|

This is the **supertype/core dimension**.

It contains attributes common to all account types.

---

# 6. Core fact

Now create the common fact table.

For example:

```text
fact_account_daily
```

with grain:

> **One row per account per day**

Example:

|date_key|account_key|balance|
|--:|--:|--:|
|20260821|101|5,000|
|20260821|102|250,000|
|20260821|103|80,000|

Now you can answer:

> "What is the total balance across all account types?"

```sql
SELECT
    SUM(balance)
FROM fact_account_daily;
```

You don't care whether the account is:

- Checking
    
- Mortgage
    
- Business loan
    

because `balance` is common to all of them.

---

# 7. Subtype/custom facts

Now we handle the specialized information.

## Checking

```text
fact_checking_transaction
```

Example:

|date_key|account_key|deposit|withdrawal|
|--:|--:|--:|--:|
|20260821|101|500|200|

---

## Mortgage

```text
fact_mortgage
```

Example:

|date_key|account_key|principal|interest|payment|LTV|
|--:|--:|--:|--:|--:|--:|
|20260821|102|240000|1500|2200|80%|

---

## Business Loan

```text
fact_business_loan
```

Example:

|date_key|account_key|disbursement|principal|collateral|
|--:|--:|--:|--:|--:|
|20260821|103|10000|80000|500000|

Now the model doesn't contain irrelevant columns.

---

# 8. What does the complete architecture look like?

Think of it like this:

```text
                         ACCOUNT
                        SUPERTYPE
                            │
                            │
                    ┌───────┴───────┐
                    │               │
                    ↓               ↓
              dim_account     fact_account
              CORE DIM        CORE FACT
                    │               │
          ┌─────────┼─────────┐     │
          ↓         ↓         ↓     │
      Checking   Mortgage   Business │
       subtype    subtype    subtype │
          │         │         │      │
          ↓         ↓         ↓      │
     Custom Fact Custom Fact Custom Fact
```

The core provides the **common analytical layer**.

The custom tables provide **specialized analytical detail**.

---

# 9. Do you identify the account type first?

Yes, but be precise about what happens.

Suppose an incoming record says:

```text
Account Number = A200
```

You look up the account in the common dimension:

```text
dim_account
```

and find:

|account_key|account_number|account_type|
|--:|---|---|
|102|A200|Mortgage|

So you know:

```text
A200 → Mortgage
```

The common data can go to:

```text
fact_account
```

and mortgage-specific data goes to:

```text
fact_mortgage
```

You **don't normally search every subtype table to discover what the account is**.

The common/supertype dimension gives you that classification.

---

# 10. Why not just use account_type in one fact?

You might ask:

> "Why not just have `account_type` and keep everything in one fact?"

Because the measures remain incompatible.

You'd still get:

```text
fact_account
--------------------------------
account_key
account_type
balance
deposit
withdrawal
mortgage_principal
LTV
credit_limit
credit_card_purchase
collateral_value
...
```

For a mortgage:

```text
deposit = NULL
withdrawal = NULL
credit_limit = NULL
credit_card_purchase = NULL
```

For checking:

```text
mortgage_principal = NULL
LTV = NULL
collateral_value = NULL
```

The `account_type` doesn't solve the sparsity problem.

It merely tells you **which columns are relevant**.

---

# 11. Why not separate everything?

The opposite extreme is also problematic.

Suppose you create:

```text
fact_checking
fact_savings
fact_mortgage
fact_personal_loan
fact_business_loan
fact_credit_card
...
```

Now the common question:

> "What is the total balance across all products?"

requires combining many fact tables.

Conceptually:

```text
Checking
   +
Savings
   +
Mortgage
   +
Business Loan
   +
Credit Card
   +
...
```

This creates a **drill-across/consolidation problem**.

The core fact solves this.

---

# 12. Core fact = enterprise-wide common analysis

This is one of the biggest reasons for the pattern.

Suppose management wants:

> "Total outstanding balance by customer."

You can use:

```text
fact_account
       ↓
dim_customer
       ↓
Total balance
```

You don't need to know the product type.

But suppose management asks:

> "What is the average mortgage loan-to-value ratio?"

Now you use:

```text
fact_mortgage
```

So the rule is:

|Question|Table|
|---|---|
|Total balance across all accounts|Core fact|
|Accounts by customer|Core fact|
|Total accounts by branch|Core fact|
|Mortgage LTV|Mortgage custom fact|
|Mortgage payment amount|Mortgage custom fact|
|Checking deposits|Checking custom fact|
|Checking withdrawals|Checking custom fact|
|Business loan collateral|Business loan custom fact|

---

# 13. Core and custom are not necessarily at the same grain

This is a **very important point**.

Do not assume:

```text
fact_account
```

and

```text
fact_mortgage
```

must have the same grain.

For example:

### Core

```text
fact_account_daily

Grain:
One account per day
```

### Mortgage

```text
fact_mortgage_payment

Grain:
One mortgage payment
```

### Checking

```text
fact_checking_transaction

Grain:
One checking transaction
```

These are completely different grains.

That's okay.

The purpose of the core isn't to force all product processes into the same grain.

The purpose is to provide a **common set of facts at a useful common grain**.

---

# 14. This is related to the bus architecture

This pattern works particularly well with the dimensional modeling idea of **conformed dimensions**.

For example:

```text
                  dim_customer
                       │
             ┌─────────┼──────────┐
             ↓         ↓          ↓
       fact_account  fact_mortgage fact_checking
             │         │          │
             ↓         ↓          ↓
        dim_date    dim_date    dim_date
```

The same `dim_customer` and `dim_date` can participate in different fact tables.

That means you can analyze:

- Checking
    
- Mortgage
    
- Business loans
    

using common dimensions.

---

# 15. Supertype/subtype is NOT the same as a hierarchy

This is worth remembering.

This:

```text
Account
  ↓
Mortgage
```

looks like a normal hierarchy.

But the purpose here isn't primarily to represent a hierarchy.

The purpose is to solve:

> **"How can I model many product types that share some facts but have many incompatible facts?"**

So don't think:

> "Supertype/subtype = just another hierarchy."

Instead think:

> **"Supertype/subtype = common core + specialized extensions."**

---

# 16. A real-world example

Let's make this more realistic.

Suppose a bank offers:

```text
Products
│
├── Deposit Products
│   ├── Checking
│   └── Savings
│
├── Lending Products
│   ├── Mortgage
│   ├── Personal Loan
│   └── Business Loan
│
└── Credit Products
    └── Credit Card
```

Common information:

```text
Account
Customer
Branch
Date
Currency
Status
Balance
```

Core model:

```text
dim_account
fact_account_daily
```

Specialized models:

```text
fact_checking_transaction
fact_savings_transaction
fact_mortgage
fact_personal_loan
fact_business_loan
fact_credit_card_transaction
```

Now you have both:

### Enterprise-wide analysis

```text
"How much money is outstanding across all products?"
```

Use the core.

### Product-specific analysis

```text
"What is the average mortgage LTV?"
```

Use mortgage.

### Another product-specific analysis

```text
"What are the total credit card purchases?"
```

Use credit card.

---

# 17. What does "heterogeneous" mean?

The word sounds complicated but is simple.

**Heterogeneous = different in nature.**

Checking and mortgage are both accounts, but they behave very differently.

```text
Same family
     ↓
Different characteristics
     ↓
Heterogeneous products
```

That's why one giant fact table doesn't work well.

---

# 18. How to decide whether you need this pattern

Ask these questions.

### Question 1

Do I have multiple product types?

```text
Yes
```

### Question 2

Do they share some common attributes?

```text
Yes
```

### Question 3

Do they also have many product-specific facts that don't apply to the others?

```text
Yes
```

### Question 4

Would putting all facts together create a huge sparse table?

```text
Yes
```

### Question 5

Do I still need common analysis across all product types?

```text
Yes
```

If the answer is **yes to all five**, supertype/subtype is a strong candidate.

---

# 19. The decision process

You can use this mental decision tree:

```text
Do multiple products exist?
          │
          ↓
       Yes
          │
          ↓
Do they share common facts?
          │
      ┌───┴───┐
      No      Yes
      │         │
      ↓         ↓
Separate    Do they have
models      many incompatible
            facts?
                 │
             ┌───┴───┐
             No      Yes
             │         │
             ↓         ↓
          Common    Supertype/
          model     Subtype
```

---

# 20. The most important distinction: common vs specialized

When designing this model, ask of every fact:

> **Does this fact make business sense for every subtype?**

If yes:

```text
→ Core fact
```

If no:

```text
→ Appropriate custom fact
```

Example:

|Fact|All accounts?|Location|
|---|---|---|
|Balance|Yes|Core|
|Account status|Yes|Core dimension|
|Deposit amount|No|Checking custom|
|Mortgage LTV|No|Mortgage custom|
|Credit card purchases|No|Credit card custom|
|Collateral value|No|Business loan custom|

This is the fundamental design exercise.

---

# 21. Common mistake #1: Putting everything in the core

Bad:

```text
fact_account
-----------------------
balance
deposit
withdrawal
mortgage_ltv
mortgage_principal
credit_limit
credit_card_purchase
collateral
business_loan_interest
...
```

Why bad?

Because you're violating the idea of **commonality**.

The core should contain the **intersection**, not the union.

### Remember:

**Intersection → Core**

**Differences → Custom**

---

# 22. Common mistake #2: Making the core too small

The opposite mistake is:

```text
fact_account
----------------
account_key
date_key
```

and putting everything else into custom tables.

If `balance` genuinely applies to every subtype and is an important common analytical measure, it belongs in the core.

Don't make the core artificially tiny.

---

# 23. Common mistake #3: Assuming all subtype facts have the same grain

They don't have to.

For example:

```text
fact_account_daily
    → one account per day

fact_mortgage_payment
    → one payment

fact_credit_card_transaction
    → one transaction
```

That's completely valid.

The important thing is that **each fact table has a clearly declared grain**.

---

# 24. Common mistake #4: Confusing this with SCD Type 2

Supertype/subtype has nothing inherently to do with:

- Type 1
    
- Type 2
    
- Type 3
    
- Type 6
    
- Type 7
    

Those are **dimension change-management techniques**.

Supertype/subtype is about:

> **How to model heterogeneous products and their common/specialized facts.**

You can have Type 2 dimensions within this architecture, but they're separate concepts.

---

# 25. Common mistake #5: Thinking the core replaces the subtype tables

It doesn't.

The core gives you:

```text
COMMON ANALYSIS
```

The custom tables give you:

```text
SPECIALIZED ANALYSIS
```

You generally need both.

---

# 26. How ETL would work

Suppose a mortgage event arrives:

```text
Account = A200
Balance = 250,000
Principal = 240,000
Interest = 1,500
LTV = 80%
```

First identify the account:

```text
A200
 ↓
dim_account
 ↓
account_key = 102
account_type = Mortgage
```

Then:

### Common information

Load:

```text
fact_account
```

with:

```text
account_key = 102
balance = 250000
```

### Specialized information

Load:

```text
fact_mortgage
```

with:

```text
account_key = 102
principal = 240000
interest = 1500
LTV = 80%
```

So:

```text
                Incoming Mortgage
                       │
                       ↓
                 Identify Account
                       │
                       ↓
                 dim_account
                       │
                account_key = 102
                       │
             ┌─────────┴─────────┐
             ↓                   ↓
       Common facts        Mortgage facts
             ↓                   ↓
       fact_account         fact_mortgage
```

This is exactly the point you were asking about earlier.

---

# 27. How BI uses the model

Imagine a dashboard.

### Page 1: Enterprise Account Overview

Questions:

- Total balance
    
- Number of accounts
    
- Balance by customer
    
- Balance by branch
    
- Balance by account type
    

Use:

```text
fact_account
+
dim_account
+
dim_customer
+
dim_branch
+
dim_date
```

---

### Page 2: Mortgage Analytics

Questions:

- Average LTV
    
- Principal outstanding
    
- Interest
    
- Payment performance
    

Use:

```text
fact_mortgage
+
dim_account
+
dim_customer
+
dim_date
```

---

### Page 3: Credit Card Analytics

Use:

```text
fact_credit_card
+
dim_account
+
dim_customer
+
dim_date
```

So the model supports both **enterprise-wide** and **product-specific** analytics.

---

# 28. The relationship between core and custom

You can think of the account key as the bridge.

```text
dim_account
     │
     │ account_key
     │
     ├───────────────┐
     ↓               ↓
fact_account    fact_mortgage
                     │
                     ↓
              mortgage-specific
                   measures
```

For an account:

```text
account_key = 102
```

can exist in both:

```text
fact_account
```

and:

```text
fact_mortgage
```

The key identifies the **same business account**.

---

# 29. Why this is scalable

Imagine today you have:

```text
Checking
Mortgage
Business Loan
```

Tomorrow the bank introduces:

```text
Student Loan
```

You don't have to redesign the core fact to accommodate every student-loan-specific measure.

You can add:

```text
fact_student_loan
```

with its specialized facts.

The core remains stable.

That's a major advantage.

---

# 30. The Pareto 80/20 understanding

If you're studying this for practical dimensional modeling, focus heavily on these concepts:

### 1. Heterogeneous products

Many product types share a common business concept but have different facts.

### 2. Don't create the giant union fact

Avoid a huge sparse table containing every possible measure.

### 3. Identify the intersection

Find the facts common to all product types.

### 4. Core/supertype

Put those common facts into the core fact and common attributes into the core dimension.

### 5. Custom/subtype

Put product-specific facts into separate subtype/custom fact tables.

### 6. Common analysis vs specialized analysis

```text
Common question
      ↓
Core fact

Product-specific question
      ↓
Custom fact
```

### 7. Grain still matters

Every fact table must have a clearly defined grain, even though core and custom tables can have different grains.

---

# 31. The ultimate mental model

Don't memorize the terminology first.

Imagine this:

```text
                MANY PRODUCTS
                     │
                     ↓
            What do they share?
                     │
                     ↓
                  COMMON
                     │
                     ↓
             ┌──────────────┐
             │     CORE     │
             │  SUPERTYPE   │
             └──────────────┘
                     │
                     │
       What is different for each?
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
    CHECKING     MORTGAGE     BUSINESS
      CUSTOM       CUSTOM       CUSTOM
        │            │            │
        ↓            ↓            ↓
   Custom Fact   Custom Fact   Custom Fact
```

### The single sentence to remember:

> **Supertype/subtype modeling puts the common intersection of heterogeneous products into a core fact/dimension and the product-specific differences into separate custom fact/dimension tables.**

And your earlier question fits directly into this:

> **Yes, the account is identified through the common/supertype dimension, which tells you its subtype. Common facts can go to the core fact, while subtype-specific facts go to the appropriate custom fact.**
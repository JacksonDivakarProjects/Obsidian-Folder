# BOP, EOP, LTM & Calendar Scaffold — Comprehensive Guide

## 1. Core idea

In dimensional/analytical SQL, you often need to analyze data **continuously across time**.

For example:

- Customer balance at the end of each month
    
- Revenue over the last 12 months
    
- Customers retained from one month to another
    
- Beginning and ending customer counts
    
- Monthly recurring revenue
    
- Inventory balances
    

A common pattern is:

```text
dim_calendar
     ↓
Create time periods
     ↓
Create scaffold
     ↓
Join actual facts
     ↓
Fill missing periods
     ↓
Calculate BOP / EOP
     ↓
Calculate LTM
```

---

# 2. What is a calendar scaffold?

A **scaffold** is a complete set of combinations of the dimensions you need for analysis.

For monthly customer analysis:

```text
Customer × Month
```

Example:

|Customer|Month|
|---|---|
|A|Jan|
|A|Feb|
|A|Mar|
|B|Jan|
|B|Feb|
|B|Mar|

Even if customer B had no transaction in February, **February still exists**.

This is important because without the scaffold:

```text
Jan → transaction
Feb → no transaction
Mar → transaction
```

the February row might disappear entirely.

---

# 3. Why use `dim_calendar`?

A calendar dimension provides a reliable time structure.

Example:

```text
dim_calendar

calendar_date
-------------
2026-01-01
2026-01-02
2026-01-03
...
```

It can also contain:

|calendar_date|month|month_start|year|
|---|---|---|---|
|2026-01-01|Jan|2026-01-01|2026|
|2026-01-02|Jan|2026-01-01|2026|
|...|...|...|...|

You can derive monthly periods:

```sql
SELECT DISTINCT
    DATE_TRUNC('MONTH', calendar_date) AS month
FROM dim_calendar;
```

Result:

```text
2026-01-01
2026-02-01
2026-03-01
...
```

---

# 4. Creating the scaffold

Suppose you have:

```text
customers
---------
customer_id

fact_sales
----------
customer_id
sale_date
amount
```

Create the customer × month combinations:

```sql
WITH months AS (
    SELECT DISTINCT
        DATE_TRUNC('MONTH', calendar_date) AS month
    FROM dim_calendar
),

customers AS (
    SELECT DISTINCT
        customer_id
    FROM fact_sales
),

scaffold AS (
    SELECT
        c.customer_id,
        m.month
    FROM customers c
    CROSS JOIN months m
)

SELECT *
FROM scaffold;
```

The important operation is:

```sql
CROSS JOIN
```

because you want **every customer for every month**.

---

# 5. Joining facts to the scaffold

Suppose the actual sales are:

|Customer|Month|Sales|
|---|---|--:|
|A|Jan|100|
|A|Mar|150|
|B|Jan|200|
|B|Feb|300|

The scaffold contains:

|Customer|Month|
|---|---|
|A|Jan|
|A|Feb|
|A|Mar|
|B|Jan|
|B|Feb|
|B|Mar|

Now perform a `LEFT JOIN`:

```sql
SELECT
    s.customer_id,
    s.month,
    COALESCE(f.sales, 0) AS sales
FROM scaffold s
LEFT JOIN monthly_sales f
    ON s.customer_id = f.customer_id
    AND s.month = f.month;
```

Result:

|Customer|Month|Sales|
|---|---|--:|
|A|Jan|100|
|A|Feb|0|
|A|Mar|150|
|B|Jan|200|
|B|Feb|300|
|B|Mar|0|

This is one of the major reasons scaffolding is useful.

---

# 6. What is EOP?

**EOP = Ending of Period**

It represents the value at the **end of the current period**.

For example:

|Month|Ending Balance|
|---|--:|
|Jan|100|
|Feb|120|
|Mar|150|
|Apr|130|

Then:

```text
Jan EOP = 100
Feb EOP = 120
Mar EOP = 150
Apr EOP = 130
```

In SQL, if `balance` already represents the period-ending balance:

```sql
balance AS eop
```

So:

```sql
SELECT
    month,
    balance AS eop
FROM monthly_balance;
```

---

# 7. What is BOP?

**BOP = Beginning of Period**

It represents the value at the **beginning of the current period**.

For consecutive periods:

```text
Current BOP = Previous period EOP
```

Therefore:

```text
BOP = LAG(EOP)
```

Example:

|Month|EOP|BOP|
|---|--:|--:|
|Jan|100|NULL|
|Feb|120|100|
|Mar|150|120|
|Apr|130|150|

The SQL is:

```sql
SELECT
    month,

    LAG(balance) OVER (
        ORDER BY month
    ) AS bop,

    balance AS eop

FROM monthly_balance;
```

---

# 8. Understanding `LAG()`

`LAG()` retrieves a value from a **previous row**.

```sql
LAG(balance) OVER (
    ORDER BY month
)
```

Suppose:

|Month|Balance|
|---|--:|
|Jan|100|
|Feb|120|
|Mar|150|

`LAG(balance)` produces:

|Month|Balance|LAG(balance)|
|---|--:|--:|
|Jan|100|NULL|
|Feb|120|100|
|Mar|150|120|

Therefore:

```text
LAG(balance) = previous month's balance
```

And if the balance represents EOP:

```text
LAG(EOP) = BOP
```

---

# 9. The relationship between BOP and EOP

The fundamental relationship is:

```text
Previous EOP = Current BOP
```

For example:

```text
January:
BOP = ?
EOP = 100

February:
BOP = 100
EOP = 120

March:
BOP = 120
EOP = 150
```

Graphically:

```text
        January
        BOP → EOP
             100
               ↓
        February
        100 → 120
              ↓
        March
        120 → 150
```

Therefore:

```text
BOP(current month) = EOP(previous month)
```

---

# 10. The first period problem

For the first available month, there is no previous period.

Therefore:

```sql
LAG(balance)
```

returns:

```text
NULL
```

Example:

|Month|BOP|
|---|--:|
|Jan|NULL|
|Feb|100|
|Mar|120|

You should **not automatically replace this with 0**.

Whether the first BOP should be `NULL`, `0`, or some known opening balance depends on the business definition.

If the business defines the opening balance as zero:

```sql
COALESCE(
    LAG(balance) OVER (
        ORDER BY month
    ),
    0
) AS bop
```

But this is a business rule, not a universal SQL rule.

---

# 11. Partitioning by customer

If you have multiple customers, you cannot simply use:

```sql
LAG(balance) OVER (
    ORDER BY month
)
```

because the previous row might belong to another customer.

You need:

```sql
LAG(balance) OVER (
    PARTITION BY customer_id
    ORDER BY month
)
```

Example:

|Customer|Month|Balance|
|---|---|--:|
|A|Jan|100|
|A|Feb|120|
|B|Jan|500|
|B|Feb|550|

Correct:

```sql
SELECT
    customer_id,
    month,
    LAG(balance) OVER (
        PARTITION BY customer_id
        ORDER BY month
    ) AS bop,
    balance AS eop
FROM monthly_balance;
```

Result:

|Customer|Month|BOP|EOP|
|---|---|--:|--:|
|A|Jan|NULL|100|
|A|Feb|100|120|
|B|Jan|NULL|500|
|B|Feb|500|550|

Each customer's history is calculated independently.

---

# 12. What is LTM?

**LTM = Last Twelve Months**

It means the total/value covering the current month and the previous 11 months.

For example, for December:

```text
January
February
March
April
May
June
July
August
September
October
November
December
```

For January of the following year:

```text
February → January
```

The window moves forward continuously.

---

# 13. Calculating LTM with a window function

Suppose:

|Month|Sales|
|---|--:|
|Jan|100|
|Feb|200|
|Mar|150|
|...|...|

Use:

```sql
SUM(sales) OVER (
    PARTITION BY customer_id
    ORDER BY month
    ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
) AS ltm_sales
```

Meaning:

```text
Current row
+
11 previous rows
=
12 rows
```

Therefore:

```text
LTM = current month + previous 11 months
```

---

# 14. Important distinction: LTM vs BOP/EOP

These are **different concepts**.

### BOP/EOP

Usually used for **point-in-time measures**.

Examples:

- Account balance
    
- Inventory
    
- Customer count
    
- Contract value
    
- Headcount
    

```text
BOP → beginning balance
EOP → ending balance
```

### LTM

Usually used for **flow measures**.

Examples:

- Revenue
    
- Sales
    
- Expenses
    
- EBITDA
    
- Cash flow
    

```text
LTM Revenue
= Revenue from the latest 12 months
```

Do not blindly apply `SUM()` to a balance measure.

---

# 15. Example: Revenue vs Balance

Suppose:

|Month|Revenue|Balance|
|---|--:|--:|
|Jan|100|500|
|Feb|120|550|
|Mar|150|600|

### Revenue

Revenue is a **flow**.

For March:

```text
LTM Revenue
= sum of the latest 12 months
```

### Balance

Balance is a **point-in-time** value.

For March:

```text
BOP = February EOP = 550
EOP = March balance = 600
```

You generally don't calculate:

```text
SUM(balance)
```

to get an LTM balance.

---

# 16. Complete Snowflake pattern

A common structure looks like this:

```sql
WITH months AS (

    SELECT DISTINCT
        DATE_TRUNC('MONTH', calendar_date) AS month

    FROM dim_calendar

    WHERE calendar_date
        BETWEEN '2024-01-01' AND '2025-12-31'
),

customers AS (

    SELECT DISTINCT
        customer_id

    FROM fact_sales
),

scaffold AS (

    SELECT
        c.customer_id,
        m.month

    FROM customers c
    CROSS JOIN months m
),

monthly_sales AS (

    SELECT
        customer_id,
        DATE_TRUNC('MONTH', sale_date) AS month,
        SUM(amount) AS sales

    FROM fact_sales

    GROUP BY
        customer_id,
        DATE_TRUNC('MONTH', sale_date)
),

base AS (

    SELECT
        s.customer_id,
        s.month,
        COALESCE(ms.sales, 0) AS sales

    FROM scaffold s

    LEFT JOIN monthly_sales ms
        ON s.customer_id = ms.customer_id
        AND s.month = ms.month
),

final AS (

    SELECT
        customer_id,
        month,
        sales,

        SUM(sales) OVER (
            PARTITION BY customer_id
            ORDER BY month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS ltm_sales,

        LAG(sales) OVER (
            PARTITION BY customer_id
            ORDER BY month
        ) AS bop,

        sales AS eop

    FROM base
)

SELECT *
FROM final
ORDER BY customer_id, month;
```

---

# 17. One important correction

In the example above, this:

```sql
LAG(sales) AS bop
```

is only correct if **`sales` represents a balance/snapshot value**.

If `sales` is actual monthly revenue, then:

```text
LAG(sales)
```

is **previous month's revenue**, not BOP.

For a balance table:

```sql
LAG(balance) AS bop,
balance AS eop
```

is appropriate.

For a revenue table:

```sql
SUM(revenue) OVER (...) AS ltm_revenue
```

is appropriate.

This distinction is critical.

---

# 18. Complete mental model

Think of the process in four layers:

```text
                    DIM_CALENDAR
                         │
                         ▼
                  TIME SCAFFOLD
                         │
                         ▼
              CUSTOMER × MONTH
                         │
                         ▼
                 ACTUAL FACTS
                         │
                         ▼
             MONTHLY DATASET
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
        BALANCE DATA             FLOW DATA
             │                       │
             ▼                       ▼
       BOP / EOP                  LTM
             │                       │
             ▼                       ▼
      LAG(previous)          SUM(last 12)
```

### Core formulas

```text
EOP(current) = current period ending value

BOP(current) = EOP(previous period)

BOP = LAG(EOP)

LTM = current period + previous 11 periods
```

### SQL equivalents

```sql
-- BOP
LAG(eop) OVER (
    PARTITION BY entity_id
    ORDER BY month
)

-- EOP
eop

-- LTM
SUM(measure) OVER (
    PARTITION BY entity_id
    ORDER BY month
    ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
)
```

The **scaffold guarantees continuous periods**, `LAG()` connects the previous period to the current period for **BOP**, the current snapshot provides **EOP**, and a 12-row window calculates **LTM for flow measures**.
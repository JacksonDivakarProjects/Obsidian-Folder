In a **dimensional model**, you generally should **not leave a foreign key in the fact table as NULL**.

Instead, use a **special dimension row** such as **Unknown**, **Not Applicable**, or **Not Provided**.

### Example

Suppose your fact table is:

```text
fact_sales
--------------------------------
sales_key
date_key
customer_key
product_key
sales_amount
```

The source data has:

```text
Customer ID = NULL
```

Instead of:

```text
customer_key = NULL
```

create a row in `dim_customer`:

```text
dim_customer
--------------------------------
customer_key | customer_id | customer_name
1            | C001        | John
2            | C002        | David
-1           | NULL        | Unknown
```

Then load the fact as:

```text
fact_sales
--------------------------------
sales_key | customer_key | sales_amount
1001      | 1            | 500
1002      | -1           | 300
```

### Why?

This preserves the dimensional relationship:

```text
                 dim_customer
                ┌─────────────┐
                │ customer_key│
                │ 1 John      │
                │ 2 David     │
                │ -1 Unknown  │
                └──────┬──────┘
                       │
                       │ FK
                       ▼
                 fact_sales
                ┌─────────────┐
                │ customer_key│
                │ 1           │
                │ -1          │
                └─────────────┘
```

Now this query works normally:

```sql
SELECT
    c.customer_name,
    SUM(f.sales_amount) AS total_sales
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_key = c.customer_key
GROUP BY c.customer_name;
```

The result can contain:

```text
John       500
Unknown    300
```

### Different meanings require different special rows

Don't use `Unknown` for every type of missing value.

|Situation|Dimension row|
|---|---|
|Source didn't provide customer|Unknown|
|Customer hasn't been identified yet|Not Identified|
|Customer doesn't apply to this transaction|Not Applicable|
|Customer ID is invalid|Invalid|
|Data is missing because of ETL issue|Missing/Error|

For example:

```text
customer_key | customer_id | customer_name
-------------|-------------|---------------
1            | C001        | John
2            | C002        | David
-1           | NULL        | Unknown
-2           | NULL        | Not Applicable
-3           | NULL        | Invalid
```

### Important distinction

There are two separate problems:

**1. NULL in the source**

```text
source.customer_id = NULL
```

Handle it by mapping to a special dimension key.

**2. Source has a customer ID, but it doesn't exist in the dimension**

```text
source.customer_id = C999
dim_customer has no C999
```

This is usually handled by mapping it to an **Unknown/Invalid** dimension row rather than allowing the fact FK to become NULL.

### Kimball-style principle

The fact table should ideally contain:

```text
fact → valid dimension key
```

rather than:

```text
fact → NULL
```

This is especially important because **NULL foreign keys can cause rows to disappear when using INNER JOINs and make dimensional analysis less predictable**.

A common ETL pattern is:

```sql
CASE
    WHEN source.customer_id IS NULL THEN -1
    WHEN d.customer_key IS NULL THEN -3
    ELSE d.customer_key
END AS customer_key
```

where `-1`, `-2`, `-3`, etc. are predefined **special dimension keys**.
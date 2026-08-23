
> An **Error Event Schema is like a structured, dimensional ETL audit/error-tracking system**, but it is more specifically designed to capture **data-quality errors**, not just general ETL execution/audit information.

Let's break down exactly what the book means.

---

# 1. First: What is a "data quality screen"?

A **data quality screen** is a validation/check applied while data is moving through the ETL pipeline.

For example, suppose your source sends:

|customer_id|customer_name|age|country|
|---|---|--:|---|
|C001|ABC Ltd|35|India|
|C002|XYZ Ltd|**-5**|India|
|C003|PQR Ltd|42|NULL|

You might have rules:

```text
age >= 0
country IS NOT NULL
customer_id IS NOT NULL
```

The ETL checks the records.

For C002:

```text
age = -5
```

❌ Error.

For C003:

```text
country = NULL
```

❌ Error.

These checks are the **data quality screens**.

---

# 2. What happens when an error is detected?

Instead of simply saying:

```text
ERROR!
```

and throwing the row away, the ETL records information about the error.

That's where the **Error Event Schema** comes in.

Conceptually:

```text
Source
  ↓
ETL
  ↓
Data Quality Screens
  ↓
 ┌───────────────┐
 │ Error?        │
 └───────┬───────┘
         │
    Yes  ↓
 Error Event Schema
         │
         ↓
 ETL support / monitoring
```

And importantly:

> This schema is **not intended for business users/BI reporting**.

The book calls it:

> **"available only in the ETL back room."**

Think of the **ETL back room** as the technical/operational area of the warehouse where ETL processes, logs, rejects, errors, and operational metadata are managed.

---

# 3. Is it like an audit table?

### Yes — conceptually.

But don't equate them completely.

An ordinary ETL audit table might record:

|Job|Start Time|End Time|Rows Read|Rows Loaded|Status|
|---|---|---|--:|--:|---|
|Customer ETL|01:00|01:05|100K|99K|Success|

That's asking:

> **"What happened during the ETL job?"**

An error event schema asks:

> **"What data-quality errors occurred, where did they occur, and what data elements were involved?"**

So:

```text
ETL Audit
    ↓
Pipeline/process monitoring

Error Event Schema
    ↓
Data-quality error monitoring
```

---

# 4. The key concept: Error Event Fact Table

The book says:

> "an error event fact table whose grain is the individual error event"

This is extremely important.

### Grain = one error event.

Suppose the ETL detects:

```text
Customer C002 has invalid age = -5
```

That is **one error event**.

You could have:

|error_event_key|error_type|source_table|source_row|
|--:|---|---|---|
|10001|Invalid Age|customer|C002|

The grain is:

> **One row = one detected error event.**

---

# 5. But then why do we need an Error Event Detail Fact?

This is where the design gets interesting.

Suppose one error event involves **multiple columns**.

For example:

```text
Customer C002
```

has:

```text
age = -5
country = NULL
```

Maybe the validation rule identifies this as one logical error event:

```text
Error Event #10001
```

but multiple columns are involved:

```text
age
country
```

So you need another fact table.

---

# 6. Error Event Detail Fact

Its grain is:

> **One row for each column participating in an error event.**

For error event `10001`:

|error_event_key|table_name|column_name|bad_value|
|--:|---|---|---|
|10001|customer|age|-5|
|10001|customer|country|NULL|

Notice the difference.

### Error Event Fact

```text
1 row = 1 error
```

### Error Event Detail Fact

```text
1 row = 1 column involved in that error
```

This is exactly what the book means by:

> "each column in each table that participates in an error event."

---

# 7. Why have two fact tables?

Because the relationship is **one-to-many**.

One error event can involve multiple columns.

Think:

```text
                 Error Event
                     │
              Error #10001
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
       age        country      email
        │            │            │
       bad          bad          bad
      value        value        value
```

Therefore:

```text
Error Event Fact
       1
       │
       │
       │ 1-to-many
       ↓
Error Event Detail Fact
       N
```

---

# 8. Example end-to-end

Suppose the source sends:

|customer_id|age|country|email|
|---|--:|---|---|
|C001|35|India|[a@x.com](mailto:a@x.com)|
|C002|**-5**|**NULL**|**invalid**|

The ETL has three rules:

```text
Rule 1 → age must be >= 0
Rule 2 → country cannot be NULL
Rule 3 → email must have valid format
```

For C002, three validations fail.

The ETL creates:

### Error Event Fact

|error_event_key|source_system|table|row_identifier|error_type|
|--:|---|---|---|---|
|5001|CRM|customer|C002|Data Quality Failure|

One row.

Grain:

> One error event.

Then:

### Error Event Detail Fact

|error_event_key|column|invalid_value|rule|
|--:|---|---|---|
|5001|age|-5|AGE_NON_NEGATIVE|
|5001|country|NULL|COUNTRY_REQUIRED|
|5001|email|invalid|EMAIL_FORMAT|

Three rows.

Grain:

> One column involved in an error event.

---

# 9. Why not just put everything in one table?

You could technically create:

|error_event|column|error|
|---|---|---|
|5001|age|Invalid|
|5001|country|Missing|
|5001|email|Invalid|

But then you're mixing two different grains.

The book deliberately separates them.

### Parent-level information

Things about the overall error:

```text
error_event_key
source
timestamp
table
row
error type
severity
```

go into:

**Error Event Fact**

### Column-level information

Things about individual problematic fields:

```text
column
bad value
rule violated
column position
```

go into:

**Error Event Detail Fact**

This keeps the grains clean.

---

# 10. This is exactly why grain matters

You have been studying grain, and this is a very good example.

The two fact tables have different grains:

```text
ERROR_EVENT_FACT
------------------------
Grain:
One row per error event
```

versus:

```text
ERROR_EVENT_DETAIL_FACT
------------------------
Grain:
One row per column participating
in an error event
```

They **must not be treated as if they have the same grain**.

---

# 11. A useful analogy

Think about a hospital.

### Error Event Fact

```text
Patient has one medical incident
```

### Error Detail Fact

```text
Symptoms associated with that incident
```

One incident:

```text
Incident #100
```

can have:

```text
fever
cough
headache
```

So:

```text
Incident
   ↓
many details
```

Same dimensional modeling principle.

---

# 12. What dimensions might exist?

The book's excerpt doesn't list all dimensions, but conceptually you could have dimensions such as:

### Error Type Dimension

|error_type_key|error_type|
|--:|---|
|1|Missing Required Value|
|2|Invalid Format|
|3|Invalid Range|
|4|Referential Integrity|
|5|Duplicate|

### Source System Dimension

|source_key|source_system|
|--:|---|
|1|CRM|
|2|ERP|
|3|Web|
|4|Mobile|

### Date/Time Dimensions

You could track:

```text
error_date_key
error_time_key
```

### ETL Job Dimension

Which process detected the error?

```text
etl_job_key
```

### Rule Dimension

Which data-quality rule failed?

```text
rule_key
```

---

# 13. What would the Error Event Fact look like?

Something like:

|error_event_key|date_key|time_key|source_key|rule_key|job_key|table_name|row_identifier|
|--:|--:|--:|--:|--:|--:|---|---|
|5001|20260821|100501|1|15|302|customer|C002|
|5002|20260821|100502|1|21|302|customer|C005|

The exact columns depend on the warehouse implementation.

But the critical point is:

> **One row represents one error event.**

---

# 14. And the detail fact?

Something like:

|error_event_key|column_name|bad_value|rule_result|
|--:|---|---|---|
|5001|age|-5|Invalid|
|5001|country|NULL|Missing|
|5002|email|abc|Invalid|

So you can drill from:

```text
Error Event
      ↓
Which columns caused it?
      ↓
What were their values?
      ↓
Which validation rules failed?
```

---

# 15. Why is this useful?

Now your ETL team can ask questions like:

### Which source creates the most errors?

```text
CRM       10,000
ERP        2,000
Web        1,500
```

### Which validation rule fails most frequently?

```text
Missing Customer ID     8,000
Invalid Email            3,000
Invalid Country          1,500
```

### Which columns are problematic?

```text
customer_id     8,000
email           3,000
country         1,500
```

### Which ETL job is generating errors?

```text
Customer_Load     7,000
Product_Load      2,000
Sales_Load        1,500
```

So this isn't just a log.

It's a **dimensional model for analyzing data-quality failures**.

---

# 16. Why does the book call it a "schema"?

Because you could have a separate collection of tables dedicated to error monitoring:

```text
ETL / Back Room Schema
│
├── fact_error_event
├── fact_error_event_detail
├── dim_error_type
├── dim_error_rule
├── dim_source_system
├── dim_date
├── dim_time
└── dim_etl_job
```

This is separate from the business-facing star schemas.

For example:

```text
BUSINESS DW
│
├── Sales Star
├── Inventory Star
├── Customer Star
└── Orders Star


ETL BACK ROOM
│
└── Error Event Schema
```

---

# 17. "Back room" is important

The book explicitly says this schema is:

> **available only in the ETL back room**

That means this isn't necessarily something you expose to ordinary business users.

The purpose is:

```text
ETL team
Data engineers
Data quality team
Warehouse operations
```

rather than:

```text
Sales analyst
Marketing analyst
Executive dashboard
```

Although you could obviously build internal data-quality dashboards on top of it.

---

# 18. Error Event vs ETL Audit

Here's the distinction I'd remember for interviews:

|ETL Audit|Error Event Schema|
|---|---|
|Monitors ETL process|Monitors data-quality failures|
|Job start/end|Individual error events|
|Rows read|Which row failed|
|Rows inserted|Which column failed|
|Rows rejected|Which rule failed|
|Job status|Error type/severity|
|Operational monitoring|Data-quality analysis|

So your statement:

> "It's like an audit table in ETL"

is **correct as a mental model**, but I'd make it more precise:

> **An Error Event Schema is a dimensionalized data-quality error log/audit system, specifically designed to analyze individual errors and the columns involved in those errors.**

---

# 19. The most important thing: the two grains

For your dimensional modeling studies, this is the part I'd memorize.

### `fact_error_event`

**Grain:**

> **One row per individual data-quality error event.**

Example:

```text
Error #1001
Customer C002
Invalid customer record
```

→ **1 row**

---

### `fact_error_event_detail`

**Grain:**

> **One row per column involved in an error event.**

If Error #1001 has:

```text
age
country
email
```

→ **3 rows**

---

# 20. Final mental model

Think of it this way:

```text
                DATA QUALITY SCREEN
                       │
                       ↓
              Something is wrong
                       │
                       ↓
                ERROR EVENT
                  #1001
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
         age        country        email
          ↓            ↓            ↓
        invalid       NULL       invalid
          │            │            │
          └────────────┼────────────┘
                       ↓
              ERROR DETAIL FACT
```

So yes, **your interpretation is right**:

> It is similar to an ETL audit/error table, but Kimball is taking it a step further and modeling the errors dimensionally, with **`Error Event Fact` at one-error-event grain and `Error Event Detail Fact` at one-column-per-error-event grain**.

And the reason for the second fact table is the classic dimensional-modeling rule you've been learning:

> **Different grains → separate fact tables.**
# **Module 4, Topic 2: Singular Tests**

While generic tests are perfect for standard column checks, **Singular Tests** are your tool for validating complex business logic, multi-row conditions, or any custom rule that doesn't fit the generic mold.

## **1. What are Singular Tests?**

A Singular Test is a **custom SQL query that you write yourself**. Its purpose is to find records that break a specific business rule. If the query returns **zero rows**, the test passes. If it returns **any rows**, those rows are the failures.

*   **Custom SQL**: You have full control over the logic, using joins, window functions, aggregates, etc.
*   **Standalone File**: Each test is a separate `.sql` file in your `tests/` directory.
*   **Failures as Output**: The rows returned *are* the violating records, making debugging direct.

## **2. Singular vs. Generic Tests: Key Differences**

| Aspect | Generic Test | Singular Test |
| :--- | :--- | :--- |
| **Definition** | Declared in a `.yml` file using predefined keywords. | Written as a custom SQL query in a `.sql` file. |
| **Logic** | Simple, column-centric checks (unique, not null). | Arbitrarily complex, business-logic checks. |
| **Best For** | Ensuring data structure integrity. | Ensuring **business rule** integrity. |
| **Output** | Pass/Fail with count of failing rows. | Pass/Fail **and** the actual failing rows. |

**Analogy**: Generic tests are like spell-check (built-in rules). Singular tests are like a human editor checking for narrative consistency (custom, nuanced rules).

## **3. Creating a Singular Test: Syntax & Structure**

### **File Location and Naming**
Create a `.sql` file within your project's `tests/` directory. The filename should describe the test.
```
your_project/
└── tests/
    ├── unique_key.sql          # A generic test override (if needed)
    ├── revenue_positive.sql    # A singular test
    └── logical/
        └── orders_have_customer.sql # Organized in subfolders
```

### **Core SQL Pattern**
The query must select the rows that **violate** your rule. Use `{{ ref() }}` or `{{ source() }}` to reference models.

```sql
-- tests/amount_is_positive.sql
-- Test Rule: All order amounts must be positive.

-- This query FINDS THE FAILURES.
-- If it returns rows, the test fails and outputs these rows.
SELECT
    order_id,
    customer_id,
    amount
FROM {{ ref('fct_orders') }}
WHERE amount <= 0 -- Logic that identifies BAD records
```

**How dbt interprets this**: "Find orders where amount <= 0." If any are found, they are violations, so the test fails.

## **4. Practical Examples**

### **Example 1: Validating a Business Rule**
**Rule**: A discount should never be applied to an order with a total under $10.
```sql
-- tests/discount_validation.sql
SELECT
    order_id,
    order_total,
    discount_amount
FROM {{ ref('orders') }}
WHERE discount_amount > 0
  AND order_total < 10
```

### **Example 2: Multi-Table Relationship Check**
**Rule**: Every entry in the daily finance report should have a corresponding batch ID in the audit log.
```sql
-- tests/finance_report_audit_completeness.sql
SELECT
    r.report_date,
    r.report_id
FROM {{ ref('finance_daily_report') }} r
LEFT JOIN {{ ref('audit_log') }} a
    ON r.batch_id = a.batch_id
WHERE a.batch_id IS NULL -- Finds reports missing an audit entry
```

### **Example 3: Data Freshness Check (Using Jinja)**
**Rule**: The most recent data in our key table should be from the last 3 days.
```sql
-- tests/data_freshness.sql
{% set max_allowed_delay = 3 %}

SELECT
    'fct_orders' as table_name,
    MAX(order_date) as latest_date,
    CURRENT_DATE as today,
    DATEDIFF(day, MAX(order_date), CURRENT_DATE) as days_delayed
FROM {{ ref('fct_orders') }}
HAVING DATEDIFF(day, MAX(order_date), CURRENT_DATE) > {{ max_allowed_delay }}
```

## **5. Running Singular Tests**

Use the same `dbt test` command. dbt automatically discovers files in the `tests/` directory.

```bash
# Run all tests (generic and singular)
dbt test

# Run only singular tests
dbt test --select "test_type:singular"

# Run a specific singular test file
dbt test --select tests/revenue_positive.sql

# Run all tests for a specific model and its singular tests
dbt test --select fct_orders
```

## **6. Interpreting Results & Debugging**

When a singular test fails, dbt outputs the exact rows your query returned. This is your direct debug report.

**Example Failure Output:**
```
Failure in test amount_is_positive (tests/amount_is_positive.sql)
Got 2 results:
  order_id: 12345, customer_id: A100, amount: -5.00
  order_id: 67890, customer_id: B200, amount: 0.00
```
**Debugging Steps:**
1.  Look at the failing rows—they pinpoint the data issue.
2.  Investigate the source of these specific records in your upstream models or source data.
3.  Fix the data or update your transformation logic to handle the edge case.

## **7. Best Practices & When to Use**

### **Use Singular Tests When You Need To:**
*   Validate complex business rules across multiple columns or tables.
*   Check aggregate conditions (e.g., "total debits must equal total credits").
*   Enforce soft business rules not captured by schema (e.g., "a user's lifetime value should not decrease").
*   Create data quality metrics specific to your domain.

### **Organizing Your Tests**
Keep your `tests/` directory clean:
```
tests/
├── generic/           # Could store .yml files for generic tests if separated
├── finance/
│   ├── balance_check.sql
│   └── reconciliation.sql
└── mart/
    ├── positive_values.sql
    └── id_matching.sql
```

---
### **Summary: The Power of Singular Tests**

You've learned that **Singular Tests** are your customizable data quality auditors. They fill the gap where generic tests end, allowing you to:
1.  **Encode Business Logic**: Translate spoken business rules ("discounts can't be used on small orders") into executable, automated checks.
2.  **Debug with Precision**: The test output *is* the problematic data, making root-cause analysis straightforward.
3.  **Maintain Flexibility**: Any query you can write can become a test, making them infinitely adaptable.

**Core Principle**: Use generic tests for **data integrity** (structure, relationships). Use singular tests for **business integrity** (rules, logic).

**Ready to take reusability to the next level?**
Type `NEXT` to proceed to **Topic 3: Custom Generic Tests**, where we'll learn how to write your own reusable test macros that behave like the built-in `unique` or `not_null` tests.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 04/Custom Generic Tests|Custom Generic Tests]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 04/Generic Tests & Their Types|Generic Tests & Their Types]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/Tests In DBT/Tests in DBT|Tests in DBT]]

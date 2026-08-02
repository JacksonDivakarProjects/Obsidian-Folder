# **Module 4, Topic 3: Custom Generic Tests**

When you find yourself writing the same complex SQL logic across multiple singular tests, it's time to build a **Custom Generic Test**. These are reusable test macros that you define once and can apply to any column or model, just like the built-in `unique` or `not_null` tests.

## **1. What are Custom Generic Tests?**

A Custom Generic Test is a **Jinja macro** that encapsulates a data quality check. Once defined, it can be invoked declaratively in your `.yml` files, making your testing suite more consistent, maintainable, and powerful.

*   **Reusable Macro**: Written once in a `.sql` file within the `macros/` or `tests/` directories.
*   **Declarative Use**: Called by name in your YAML files, often with custom parameters.
*   **Applied to Many**: The same test logic can be easily applied to different models and columns.

### **Comparison: Singular vs. Custom Generic Test**

| Aspect | Singular Test | Custom Generic Test |
| :--- | :--- | :--- |
| **Form** | A standalone SQL file in `tests/`. | A Jinja macro (in `macros/` or `tests/generic/`). |
| **Logic** | Fixed, written for one specific case. | Abstracted, can be parameterized and reused. |
| **Invocation** | Runs automatically (file in `tests/`). | Called by name in a model's `.yml` file. |
| **Best For** | One-off, highly specific validation. | **Reusable patterns** (e.g., `positive_value`, `valid_email`). |

**Analogy**: If a Singular Test is a custom report, a Custom Generic Test is a **report template** you can fill in with different data.

## **2. Anatomy of a Custom Generic Test Macro**

The macro must accept specific arguments that dbt will pass automatically and must compile to a SQL query that finds failing rows.

### **Mandatory Macro Arguments**
- `model`: The relation (table/view) of the model being tested (provided by dbt).
- `column_name`: The name of the column being tested (provided by dbt).

### **Basic Macro Structure**
```sql
-- macros/custom_tests/assert_positive.sql

{% test assert_positive(model, column_name) %}
-- This SQL SELECTS rows that VIOLATE the rule.
SELECT
    *
FROM {{ model }}
WHERE {{ column_name }} <= 0
{% endtest %}
```
**Key Point:** The SQL inside the macro **finds the failures**. Zero results = test pass.

## **3. Creating Custom Generic Tests: Step-by-Step**

### **Step 1: Create the Macro File**
Save it in your `macros/` directory (e.g., `macros/custom_tests/`) or `tests/generic/`.

### **Step 2: Write the Test Logic**
Here are three practical examples for common test patterns.

**Example 1: Value Range Test**
Checks that values in a column are within a specified numeric range.
```sql
-- macros/custom_tests/value_between.sql
{% test value_between(model, column_name, min_value=0, max_value=100) %}
SELECT
    *
FROM {{ model }}
WHERE {{ column_name }} < {{ min_value }}
   OR {{ column_name }} > {{ max_value }}
{% endtest %}
```

**Example 2: Data Format Test (Email)**
Uses a regex pattern to validate string format.
```sql
-- macros/custom_tests/valid_email.sql
{% test valid_email(model, column_name) %}
SELECT
    *
FROM {{ model }}
WHERE {{ column_name }} IS NOT NULL
  AND {{ column_name }} !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
{% endtest %}
```

**Example 3: Date Recency Test**
Checks if a date column contains values from the future (invalid) or is unreasonably old.
```sql
-- macros/custom_tests/date_not_future_and_recent.sql
{% test date_not_future_and_recent(model, column_name, max_days_old=365) %}
SELECT
    *
FROM {{ model }}
WHERE {{ column_name }} > CURRENT_DATE -- Future dates are invalid
   OR {{ column_name }} < DATEADD(day, -{{ max_days_old }}, CURRENT_DATE) -- Too old
{% endtest %}
```

## **4. Using Your Custom Test in YAML**

Invoke your test by its macro name in the `tests:` list of a column. Pass arguments just like built-in tests.

```yaml
# models/schema.yml
version: 2

models:
  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null

      - name: amount
        tests:
          - assert_positive # Uses your custom test

      - name: discount_percentage
        tests:
          - value_between: # Uses your parameterized test
              min_value: 0
              max_value: 50 # Max discount is 50%

      - name: customer_email
        tests:
          - valid_email

  - name: dim_customers
    columns:
      - name: date_of_birth
        tests:
          - date_not_future_and_recent:
              max_days_old: 36500 # ~100 years
```

## **5. How It Works: Compilation & Execution**

When you run `dbt test`, dbt:
1.  Finds the `valid_email` test on `customer_email`.
2.  Locates the macro `{% test valid_email(...) %}`.
3.  Compiles it by injecting the specific `model` (`fct_orders`) and `column_name` (`customer_email`).
4.  Runs the resulting SQL:
    ```sql
    SELECT *
    FROM analytics.fct_orders
    WHERE customer_email IS NOT NULL
      AND customer_email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    ```

**Run your tests as usual:**
```bash
# Run all tests (including your custom ones)
dbt test

# Run tests on a specific model
dbt test --select fct_orders
```

## **6. Best Practices & Advanced Patterns**

### **A. Add a Description Argument**
Make your tests self-documenting by accepting a `description` parameter.
```sql
{% test value_between(model, column_name, min_value, max_value, description=None) %}
{% if description %}
/* Test: {{ description }} */
{% endif %}
SELECT * FROM {{ model }}
WHERE {{ column_name }} < {{ min_value }} OR {{ column_name }} > {{ max_value }}
{% endtest %}
```

### **B. Test Composite Conditions**
Create tests that check logic across multiple columns by accepting a list of columns.
```sql
{% test revenue_matches(model, quantity_column, price_column, revenue_column) %}
SELECT *
FROM {{ model }}
WHERE {{ quantity_column }} * {{ price_column }} != {{ revenue_column }}
{% endtest %}
```
Use in YAML:
```yaml
- name: fct_sales
  columns:
    - name: revenue
      tests:
        - revenue_matches:
            quantity_column: 'quantity'
            price_column: 'unit_price'
```

---
### **Summary: Elevating Your Testing Suite**

You've learned that **Custom Generic Tests** transform repeated, complex validation logic into **reusable, declarative assets**.

1.  **They are Macros**: Defined with `{% test macro_name(...) %}` in `.sql` files.
2.  **They are Parameterizable**: Can accept arguments like `min_value` or `max_days_old` to make them flexible.
3.  **They Integrate Seamlessly**: Are invoked in your YAML files alongside built-in tests, keeping your testing suite unified.
4.  **They Promote Consistency**: Ensure the same business rule is checked the same way across your entire data platform.

**When to Build One**: Whenever you find yourself writing a similar `WHERE` clause in a second singular test, stop and extract it into a custom generic test.

**Ready to learn how to control the impact of test failures?**
Type `NEXT` to proceed to **Topic 4: Test Execution, Severity & the dbt build Command**, where we'll cover configuring test warnings vs. errors and combining run and test operations.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 04/Generic Tests & Their Types|Generic Tests & Their Types]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 04/Singular Tests|Singular Tests]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 04/Test Execution, Severity & the `dbt build` Command|Test Execution, Severity & the dbt build Command]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/DBT Course/Tests In DBT/Tests in DBT|Tests in DBT]]

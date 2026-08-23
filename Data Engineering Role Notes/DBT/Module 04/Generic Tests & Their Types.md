# **Module 4, Topic 1: Generic Tests & Their Types**

After building your models, ensuring the quality of the data within them is critical. dbt provides a powerful, built-in testing framework to do just that. The simplest and most commonly used tests are **Generic Tests**.

## **1. What are Generic (Schema) Tests?**

Generic tests are **declarative data quality checks** that you define in `.yml` files. They validate assumptions about your model's columns, such as "this column should have no nulls" or "these values should be unique."

*   **Declarative**: You state *what* you expect (e.g., `not_null`), not *how* to check it. dbt generates and runs the validation SQL.
*   **Reusable**: Four tests (`unique`, `not_null`, `accepted_values`, `relationships`) come built-in and work across all adapters.
*   **Integrated**: Test results are part of your project's documentation and lineage.

## **2. The Four Built-in Generic Tests**

Here is a summary of the core tests every dbt practitioner uses:

| Test Name | What It Checks | Example Use Case |
| :--- | :--- | :--- |
| **`unique`** | All values in a column are distinct. | Primary key columns, unique identifiers. |
| **`not_null`** | No `NULL` values exist in a column. | Critical foreign keys, required attributes. |
| **`accepted_values`** | All values in a column are in a provided list. | Status columns (e.g., `status` in `('shipped', 'pending', 'cancelled')`). |
| **`relationships`** (Referential Integrity) | Every value in this column exists in another table's column. | Foreign key relationships (e.g., `order.customer_id` references `customer.id`). |

## **3. How to Apply Tests: YAML Syntax**

Tests are added under the `columns:` key of a model within a `.yml` file (like `models/schema.yml`).

### **Basic Syntax**
```yaml
# models/staging/staging.yml
version: 2

models:
  - name: stg_customers
    columns:
      - name: customer_id
        tests:
          - unique
          - not_null

      - name: status
        tests:
          - accepted_values:
              values: ['active', 'inactive', 'pending']
```

### **The `relationships` Test Syntax**
The `relationships` test requires additional arguments to specify the parent model and column.
```yaml
models:
  - name: fct_orders
    columns:
      - name: customer_id
        tests:
          - relationships:
              # `to` argument uses `ref()` syntax
              to: ref('dim_customers')
              # `field` specifies the column in the parent model
              field: customer_id
```

## **4. Running Tests & Interpreting Results**

You execute tests using the `dbt test` command.

### **Basic Test Execution**
```bash
# Run all tests in the project
dbt test

# Run tests for a specific model
dbt test --select stg_customers

# Run tests using DAG selection syntax (e.g., test a model and its downstream dependents)
dbt test --select fct_orders+
```

### **Understanding Test Output**
When a test fails, dbt shows you which model, column, and test failed, along with the failing rows.

**Example Failure Output:**
```
Failure in test not_null_stg_customers_customer_id (models/staging/staging.yml)
Got 5 results, expected 0.

compiled SQL at target/compiled/my_project/models/staging/staging.yml/not_null_stg_customers_customer_id.sql
```
*   **Action**: Examine the compiled SQL (`target/compiled/...`) to see the exact query that found the invalid rows. Then, investigate your source data or transformation logic.

## **5. Advanced Test Configuration**

### **Testing Multiple Columns Together (Compound Uniqueness)**
To test that the *combination* of columns is unique (e.g., a composite key), define the test at the **model level**, not under a single column.

```yaml
models:
  - name: fact_sales
    tests:
      - unique:
          # The combination of these columns must be unique
          column_name: ["date_id", "store_id", "product_id"]
```

### **Configuring Test Severity**
You can control whether a test failure should be treated as an error (fails the run) or a warning (logs but continues). This is configured in `dbt_project.yml`.

```yaml
# dbt_project.yml
tests:
  my_project:
    # Any 'unique' test in this project is now a warning
    +unique:
      +severity: warn
    # Any 'not_null' test on a column named 'id' is an error
    +not_null:
      +severity: error
      +where: "{{ '\"id\"' in column_name }}" # Jinja condition
```

## **6. Example: A Fully Tested Staging Model**

Here’s a practical example bringing it all together in a single YAML file.

```yaml
# models/staging/staging.yml
version: 2

models:
  - name: stg_orders
    description: "Cleansed order records from the OLTP system."
    columns:
      - name: order_id
        description: "Primary key for the order."
        tests:
          - unique
          - not_null

      - name: customer_id
        description: "Foreign key to the customers table."
        tests:
          - not_null
          - relationships:
              to: ref('stg_customers')
              field: customer_id

      - name: order_date
        description: "Date the order was placed."
        tests:
          - not_null

      - name: status
        description: "Current lifecycle status of the order."
        tests:
          - accepted_values:
              values: ['placed', 'shipped', 'complete', 'returned', 'cancelled']
              quote: true # Use this if your values are strings

      - name: amount
        description: "Total dollar amount of the order."
        # Tests can be added later as needed
```

---
### **Summary: The Role of Generic Tests**

1.  **Safety net**: Generic tests are the first line of defense, catching duplicates, missing values, and invalid codes.
2.  **Documentation as code**: Defining tests in YAML explicitly documents your assumptions about the data for your team.
3.  **Integrated workflow**: Running `dbt test` is as central to the workflow as `dbt run`; many teams run tests in CI/CD.
4.  **Foundation for trust**: Consistent testing turns raw data into a trusted analytics layer.

**Core principle:** test the things that, if wrong, would break your business logic or downstream reports. Start with primary keys and foreign keys, then move on to singular tests for anything a generic test can't express.

## 🔗 Related Notes
- [[Custom Generic Tests|Custom Generic Tests]]
- [[Singular Tests|Singular Tests]]
- [[Tests in DBT|Tests in DBT]]
- [[Test Execution, Severity & the `dbt build` Command|Test Execution, Severity & the dbt build Command]]

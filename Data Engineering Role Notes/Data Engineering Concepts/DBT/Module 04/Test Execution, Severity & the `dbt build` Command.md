# **Module 4, Topic 4: Test Execution, Severity & the `dbt build` Command**

Now that you can create various tests, let's learn how to control their execution and integrate them seamlessly into your project workflow using the powerful `dbt build` command.

## **1. The `dbt test` Command: Execution & Selection**

The primary command for running tests has powerful selection capabilities.

### **Basic Execution**
```bash
# Run all tests in your project
dbt test

# Run tests for a specific model
dbt test --select customers

# Run tests for all models in a directory
dbt test --select staging/

# Run tests for a model and all its downstream dependencies
dbt test --select orders+
```

### **Targeting Specific Test Types**
You can run only certain categories of tests, which is useful in different development stages.
```bash
# Run only generic (schema) tests
dbt test --select "test_type:generic"

# Run only singular tests
dbt test --select "test_type:singular"

# Run only custom generic tests (requires tag)
dbt test --select tag:custom_test
```

## **2. Configuring Test Severity**

By default, all test failures are **errors** that stop the execution pipeline. However, you can configure some tests as **warnings** that allow execution to continue.

### **Setting Severity in `dbt_project.yml`**
Configure severity at various levels using the `severity` config with the `warn` or `error` value.

**Project-Level Configuration:**
```yaml
# dbt_project.yml
tests:
  my_project:
    # Make ALL not_null tests warnings by default
    +not_null:
      +severity: warn
    
    # But for the staging directory, make them errors
    staging:
      +not_null:
        +severity: error
    
    # Configure a specific custom test
    +value_between:
      +severity: warn
```

**Model/Test-Level Configuration:**
```yaml
# models/staging/staging.yml
models:
  - name: stg_orders
    columns:
      - name: order_id
        tests:
          - unique:
              severity: error  # Critical - must be unique
          - not_null:
              severity: warn   # We can tolerate some nulls temporarily
```

### **Using Severity in Practice**
When a test with `severity: warn` fails:
- The test is marked as failed
- A warning message appears in logs
- **The overall run continues** (does not stop)
- Useful for monitoring data quality drift without blocking pipelines

## **3. The `dbt build` Command: Run + Test Integration**

The `dbt build` command is a **powerful workflow command** that combines `run` and `test` intelligently.

### **How `dbt build` Works**
For each model in your selection, `dbt build` will:
1. Run the model (build the table/view)
2. **Immediately run all associated tests** on that model
3. Only proceed to downstream models if **both** the build and tests succeed

### **Basic Usage & Examples**
```bash
# Build and test your entire DAG
dbt build

# Build and test a specific model and its upstream dependencies
dbt build --select orders

# Build and test models in staging, but only test (not build) downstream marts
dbt build --select staging+ --defer
```

### **Practical `dbt build` Workflow**
Here's how `dbt build` creates a safer deployment process:
```bash
# 1. First, test your changes in isolation
dbt test --select my_changed_model+

# 2. Build and test the changed model and its upstream dependencies
dbt build --select +my_changed_model

# 3. If everything passes, build and test the full downstream impact
dbt build --select my_changed_model+
```

## **4. Production Deployment with `--target prod`**

When deploying to production, you typically want stricter controls and different configurations.

### **Production-Specific Configuration**
```yaml
# dbt_project.yml
models:
  my_project:
    +materialized: table
    +tags: ['daily']
    
    # Override for production - more frequent updates
    prod:
      +materialized: incremental
      +tags: ['hourly', 'prod']
    
    # Stricter testing in production
    tests:
      prod:
        +severity: error  # All tests are errors in prod
```

### **Production Deployment Commands**
```bash
# Run in production environment
dbt build --target prod --full-refresh

# Dry run - parse and validate without execution
dbt parse
dbt compile --target prod

# Selective production deployment
dbt build --target prod --select tag:hourly+
```

## **5. Advanced Test Execution Patterns**

### **Conditional Test Execution**
Use Jinja in your test definitions to conditionally run tests:
```sql
-- tests/conditional_freshness.sql
{% if target.name == 'prod' %}
  SELECT *
  FROM {{ ref('daily_sales') }}
  WHERE sales_date < CURRENT_DATE - INTERVAL '2 days'
{% else %}
  SELECT 1 LIMIT 0  -- Returns no rows in non-prod environments
{% endif %}
```

### **Test Tagging & Grouping**
Organize tests by purpose using tags:
```yaml
# In model YAML
columns:
  - name: revenue
    tests:
      - positive_value:
          tags: ['validation', 'finance']
      - value_between:
          min_value: 0
          max_value: 1000000
          tags: ['sanity_check']
```

```bash
# Run only finance-related tests
dbt test --select tag:finance

# Run critical tests before deployment
dbt test --select tag:critical
```

## **6. Monitoring & Alerting on Test Results**

### **Store Test Results for Monitoring**
```bash
# Output test results to a file
dbt test --store-failures --target prod > test_results.json

# Use dbt's built-in artifacts
# Test results are stored in target/run_results.json
```

### **Integration with CI/CD Pipelines**
Example GitHub Actions workflow:
```yaml
# .github/workflows/dbt-test.yml
name: dbt Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run dbt Tests
        run: |
          dbt deps
          dbt build --select state:modified+ --defer
```

---
### **Summary: A Cohesive Testing Strategy**

1.  **`dbt test`** with selection syntax gives surgical control over which tests run.
2.  **Severity configuration** (`warn` vs `error`) distinguishes blocking issues from quality warnings.
3.  **`dbt build`** is the production-ready command that ensures no model is built unless its tests pass.
4.  **Target environments** (`--target prod`) allow different test strictness per environment.

**Key insight**: a mature dbt project uses `dbt build` as its primary deployment command, with severity levels tuned to balance data quality against pipeline reliability. Snapshots extend this same discipline to slowly-changing historical data.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 06/Difference Between dbt run and dbt build|`dbt run` vs `dbt build`]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 06/DBT Flags|dbt Flags That Actually Matter]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 04/Generic Tests & Their Types|Generic Tests & Their Types]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 04/Singular Tests|Singular Tests]]

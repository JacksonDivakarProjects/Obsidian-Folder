# 🔥 **dbt with Python: Yes, It Can Run Python Tests!**

Great question! **Yes, dbt CAN run Python tests**, but with some important caveats. Let me break it down practically.

## 📊 **Two Ways to Run Python in dbt:**

### **1. dbt Python Models (dbt Core 1.3+)** ✅
**This is the MAIN way to write Python in dbt.**

```python
-- models/python/my_python_model.py
import pandas as pd

def model(dbt, session):
    # dbt is the dbt Python object
    # session is the database connection (Snowpark, PySpark, etc.)
    
    # Get upstream data
    orders_df = dbt.ref("stg_orders")
    
    # Python transformations
    orders_df["profit_margin"] = (
        orders_df["revenue"] - orders_df["cost"]
    ) / orders_df["revenue"]
    
    # Apply business logic
    orders_df["priority"] = orders_df["profit_margin"].apply(
        lambda x: "HIGH" if x > 0.3 else "MEDIUM" if x > 0.1 else "LOW"
    )
    
    return orders_df
```

**Supported Platforms:**
- **Snowflake** (via Snowpark)
- **Databricks** (via PySpark)
- **BigQuery** (via BigQuery Python API)

### **2. dbt Python Tests (dbt Core 1.3+)** ✅
**Yes, you can write custom Python tests!**

```python
# tests/python/test_revenue_positive.py
import pandas as pd

def test_revenue_positive(model):
    # 'model' is a DataFrame of the model you're testing
    assert (model['revenue'] >= 0).all(), "Revenue should be non-negative"
    
def test_profit_margin_range(model):
    # Test profit margin is between 0 and 1
    assert ((model['profit_margin'] >= 0) & 
            (model['profit_margin'] <= 1)).all()
```

**Run these tests with:**
```bash
dbt test --select test_revenue_positive
# or
dbt test --select my_model  # runs all tests on my_model
```

## 🏗️ **Complete Python-in-dbt Example**

### **Project Structure:**
```
my_dbt_project/
├── models/
│   ├── python/                    # Python models
│   │   ├── customer_segments.py
│   │   └── revenue_forecast.py
│   ├── sql/                       # SQL models
│   │   ├── stg_orders.sql
│   │   └── dim_customers.sql
│   └── marts/
│       └── finance/
├── tests/
│   ├── python/                    # Python tests
│   │   ├── test_data_quality.py
│   │   └── test_business_logic.py
│   └── generic/                   # SQL tests
│       └── schema.yml
├── macros/
│   └── python_helpers.py          # Python macros
└── dbt_project.yml
```

### **Example 1: Customer Segmentation (Python Model)**
```python
# models/python/customer_segments.py
import pandas as pd
from sklearn.cluster import KMeans

def model(dbt, session):
    # Get customer data
    customers = dbt.ref("stg_customers")
    
    # Feature engineering in Python
    customers_df = customers.to_pandas()
    
    features = customers_df[['total_orders', 'avg_order_value', 'days_since_last_order']]
    
    # Machine learning clustering
    kmeans = KMeans(n_clusters=3, random_state=42)
    customers_df['segment'] = kmeans.fit_predict(features)
    
    # Map cluster numbers to meaningful names
    segment_map = {0: 'Loyal', 1: 'At Risk', 2: 'New'}
    customers_df['segment_name'] = customers_df['segment'].map(segment_map)
    
    # Return as DataFrame (auto-converted to table)
    return customers_df[['customer_id', 'segment_name', 'total_orders', 'avg_order_value']]
```

### **Example 2: Advanced Data Quality Tests**
```python
# tests/python/test_data_quality.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_no_duplicate_customers(model):
    """Test for duplicate customer records"""
    duplicate_count = model.duplicated(subset=['customer_id']).sum()
    assert duplicate_count == 0, f"Found {duplicate_count} duplicate customers"

def test_order_dates_valid(model):
    """Test order dates are within valid range"""
    today = pd.Timestamp.now()
    one_year_ago = today - pd.Timedelta(days=365)
    
    invalid_dates = model[
        (model['order_date'] < one_year_ago) | 
        (model['order_date'] > today)
    ]
    
    assert len(invalid_dates) == 0, f"Found {len(invalid_dates)} invalid order dates"

def test_revenue_outliers(model):
    """Test for statistical outliers in revenue"""
    Q1 = model['revenue'].quantile(0.25)
    Q3 = model['revenue'].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = model[
        (model['revenue'] < lower_bound) | 
        (model['revenue'] > upper_bound)
    ]
    
    # Allow up to 5% outliers
    outlier_percentage = len(outliers) / len(model) * 100
    assert outlier_percentage < 5, f"Too many revenue outliers: {outlier_percentage:.2f}%"
```

## ⚙️ **Configuration & Setup**

### **1. `dbt_project.yml` Configuration:**
```yaml
name: my_project
version: '1.0.0'
profile: snowflake

models:
  my_project:
    python:
      materialized: table  # or view
      tests:
        - test_revenue_positive  # Your Python test

tests:
  +severity: warn  # or error

vars:
  python_enabled: true
```

### **2. `packages.yml` for Python Dependencies:**
```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.1.0
  
# Note: Python packages are handled differently!
# See below for Python dependency management
```

### **3. Managing Python Dependencies:**
```bash
# Create requirements.txt in your dbt project
# requirements.txt
pandas>=1.5.0
scikit-learn>=1.2.0
numpy>=1.24.0
pyarrow>=10.0.0
```

**For Snowflake:**
```yaml
# profiles.yml
my_snowflake_profile:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: your_account
      user: your_user
      password: "{{ env_var('DBT_PASSWORD') }}"
      role: transformer
      database: analytics
      warehouse: transforming
      schema: dbt
      threads: 4
      # Python-specific config
      query_tag: dbt_python
      packages: ['pandas', 'scikit-learn', 'numpy']  # Snowpark packages
```

## 🔍 **Where Python Tests Run**

### **Environment 1: In the Data Warehouse (Preferred)**
```python
# This runs INSIDE Snowflake/BigQuery/Databricks
def model(dbt, session):
    # 'session' is Snowpark/PySpark session
    # Code runs in the data platform's Python environment
    df = session.table("source_data")
    return df
```

**Pros:**
- No data movement (stays in warehouse)
- Leverages warehouse compute power
- Better security

**Cons:**
- Limited to warehouse-supported packages
- Debugging can be harder

### **Environment 2: Locally (Development Only)**
```bash
# Run dbt locally with Python
dbt run --select python_model  # Runs Python locally
dbt test --select python_test  # Runs Python tests locally
```

**For local Python execution, you need:**
```bash
pip install dbt-core
pip install dbt-snowflake  # or dbt-bigquery, dbt-spark
pip install -r requirements.txt
```

## 🎯 **When to Use Python vs SQL in dbt**

### **Use Python When:**
```python
# 1. Complex business logic
def calculate_churn_score(customer_data):
    return (customer_data['inactive_days'] * 0.3 + 
            customer_data['support_tickets'] * 0.7)

# 2. Machine learning features
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# 3. Advanced data validation
def validate_data(df):
    if df['revenue'].isnull().any():
        raise ValueError("Revenue contains nulls")
    return True

# 4. API calls for data enrichment
import requests
def enrich_with_external_data(record):
    response = requests.get(f"https://api.example.com/{record['id']}")
    return response.json()
```

### **Use SQL When:**
```sql
-- 1. Simple aggregations
SELECT user_id, COUNT(*) as order_count
FROM orders
GROUP BY 1;

-- 2. Joins and window functions
SELECT *,
       ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) as rn
FROM sessions;

-- 3. Date manipulations
SELECT DATE_TRUNC('month', order_date) as order_month
FROM orders;
```

## 🚀 **Production Python dbt Workflow**

### **Step 1: Development**
```bash
# Create Python model
touch models/python/customer_lifetime_value.py

# Write Python code
# Test locally
dbt run --select customer_lifetime_value --target dev
```

### **Step 2: Testing**
```bash
# Run Python tests
dbt test --select "test_type:python" --target dev

# Run specific Python test
dbt test --select test_customer_ltv_calculation

# Generate docs with Python models
dbt docs generate
```

### **Step 3: CI/CD Pipeline**
```yaml
# .github/workflows/dbt.yml
name: dbt Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install dbt-snowflake
        
    - name: Run Python tests
      run: |
        dbt deps
        dbt test --select "test_type:python"
        
    - name: Run Python models
      run: |
        dbt run --select "config.materialized:table" --target ci
```

### **Step 4: Monitoring**
```python
# macros/python/logging.py
import logging

def log_model_execution(model_name, row_count, duration):
    logger = logging.getLogger('dbt')
    logger.info(f"""
    Model: {model_name}
    Rows: {row_count}
    Duration: {duration}s
    Status: Success
    """)
    
# Use in model
def model(dbt, session):
    import time
    start = time.time()
    
    # ... model logic ...
    
    duration = time.time() - start
    log_model_execution(dbt.config.name, len(result), duration)
    return result
```

## ⚠️ **Limitations & Gotchas**

### **Current Limitations (dbt Core 1.5):**
1. **Not all adapters support Python**
   - ✅ Snowflake (Snowpark)
   - ✅ Databricks (PySpark) 
   - ✅ BigQuery (BigQuery Python API)
   - ❌ PostgreSQL (no Python support)
   - ❌ Redshift (no Python support)

2. **Package restrictions** in warehouse
   - Limited to whitelisted packages
   - Version constraints
   - No system-level packages

3. **Performance considerations**
   - Python UDFs can be slower than SQL
   - Data serialization overhead
   - Memory limitations

### **Best Practices:**
```python
# GOOD: Filter early
def model(dbt, session):
    # Filter in SQL first
    raw_data = dbt.ref("big_table").filter("date > '2024-01-01'")
    
    # Then process in Python
    df = raw_data.to_pandas()
    # ... Python processing ...
    return df

# BAD: Pull everything to Python first
def model(dbt, session):
    # This pulls ALL data to Python - SLOW!
    all_data = dbt.ref("big_table").to_pandas()  # 🚫
    filtered = all_data[all_data['date'] > '2024-01-01']
    return filtered
```

## 📚 **Learning Resources**

### **Official Docs:**
- [dbt Python Models](https://docs.getdbt.com/docs/build/python-models)
- [dbt Python Tests](https://docs.getdbt.com/docs/build/python-tests)
- [dbt Python API](https://docs.getdbt.com/docs/dbt-py)

### **Tutorials:**
1. **Snowflake + dbt Python:** [Snowpark for Python with dbt](https://quickstarts.snowflake.com/guide/dbt_snowpark_python/)
2. **Databricks + dbt Python:** [dbt-databricks](https://docs.databricks.com/en/dev-tools/dbt.html)
3. **BigQuery + dbt Python:** [dbt-bigquery Python models](https://docs.getdbt.com/docs/core/connect-data-platform/bigquery-setup#python-models)

### **Example Projects:**
```bash
# Clone and explore
git clone https://github.com/dbt-labs/jaffle_shop_modern
git clone https://github.com/dbt-labs/dbt-python-model-example
```

## 🎯 **Quick Start Checklist**

1. **Check compatibility:** Does your data platform support dbt Python?
2. **Install:** `pip install dbt-snowflake` (or your adapter)
3. **Create Python model:** `models/python/my_model.py`
4. **Write Python test:** `tests/python/test_my_model.py`
5. **Run:** `dbt run --select my_model`
6. **Test:** `dbt test --select test_my_model`

**Remember:** dbt Python is **NOT** for replacing all SQL. It's for specific use cases where Python is clearly better. Start with SQL, add Python only when needed!

Want me to dive deeper into any specific aspect?

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 04/Generic Tests & Their Types|Generic Tests & Their Types]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 03/Building Models & Materializations|Building Models & Materializations]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 04/Test Execution, Severity & the `dbt build` Command|Test Execution, Severity & the dbt build Command]]

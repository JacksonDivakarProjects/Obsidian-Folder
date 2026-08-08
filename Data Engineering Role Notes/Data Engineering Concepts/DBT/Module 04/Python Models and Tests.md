# dbt with Python: Models and How to Test Them

dbt is SQL-first, but since **dbt Core 1.3** it can also run **Python models** on a handful of adapters. This note covers what Python models are, when to reach for them instead of SQL, and — importantly — how they actually get tested (which is not a separate "Python test" feature, despite how it's often described).

## 1. Python Models

A Python model is a `.py` file in your `models/` directory that defines a `model(dbt, session)` function returning a DataFrame. dbt materializes that DataFrame as a table, the same way it materializes a SQL `SELECT`.

**Supported platforms:** Snowflake (via Snowpark), Databricks (via PySpark), and BigQuery (via a Dataproc/Spark-backed Python runtime). Not supported on PostgreSQL or Redshift.

```python
# models/python/my_python_model.py
import pandas as pd

def model(dbt, session):
    # dbt is the dbt Python object; session is the platform's session
    # (Snowpark session, PySpark session, etc.)

    orders_df = dbt.ref("stg_orders")

    orders_df["profit_margin"] = (
        orders_df["revenue"] - orders_df["cost"]
    ) / orders_df["revenue"]

    orders_df["priority"] = orders_df["profit_margin"].apply(
        lambda x: "HIGH" if x > 0.3 else "MEDIUM" if x > 0.1 else "LOW"
    )

    return orders_df
```

### Project structure with Python models

```
my_dbt_project/
├── models/
│   ├── python/                    # Python models
│   │   ├── customer_segments.py
│   │   └── revenue_forecast.py
│   ├── staging/                   # SQL models
│   │   ├── stg_orders.sql
│   │   └── dim_customers.sql
│   └── marts/
│       └── finance/
├── tests/
│   └── generic/                   # Generic/singular tests apply to Python models too
│       └── schema.yml
├── macros/
│   └── python_helpers.py
└── dbt_project.yml
```

### Example: customer segmentation with a Python model

```python
# models/python/customer_segments.py
import pandas as pd
from sklearn.cluster import KMeans

def model(dbt, session):
    customers = dbt.ref("stg_customers")
    customers_df = customers.to_pandas()

    features = customers_df[['total_orders', 'avg_order_value', 'days_since_last_order']]

    kmeans = KMeans(n_clusters=3, random_state=42)
    customers_df['segment'] = kmeans.fit_predict(features)

    segment_map = {0: 'Loyal', 1: 'At Risk', 2: 'New'}
    customers_df['segment_name'] = customers_df['segment'].map(segment_map)

    return customers_df[['customer_id', 'segment_name', 'total_orders', 'avg_order_value']]
```

## 2. How Python Models Are Actually Tested

**There is no separate "dbt Python test" file type that dbt auto-discovers and runs like pytest.** A Python model compiles down to a table or view in the warehouse just like a SQL model does, so it is tested with the **exact same mechanisms** as any other model:

**A. Generic and singular tests (YAML/SQL, works today)**
Because the output is just a relation, you test it the normal way — declare column tests in YAML, or write a singular SQL test against it:

```yaml
# models/python/schema.yml
models:
  - name: customer_segments
    columns:
      - name: customer_id
        tests: [unique, not_null]
      - name: segment_name
        tests:
          - accepted_values:
              values: ['Loyal', 'At Risk', 'New']
```

```sql
-- tests/revenue_outliers.sql — a singular test expressing the "few outliers" rule
-- (the pandas IQR check people often show as a fake "python test" is really this,
-- expressed in SQL against the materialized output)
with stats as (
    select
        percentile_cont(0.25) over () as q1,
        percentile_cont(0.75) over () as q3
    from {{ ref('customer_segments') }}
)
select *
from {{ ref('customer_segments') }} c, stats s
where c.total_orders < s.q1 - 1.5 * (s.q3 - s.q1)
   or c.total_orders > s.q3 + 1.5 * (s.q3 - s.q1)
```

**B. dbt unit tests (dbt Core 1.8+, works for both SQL and Python models)**
This is the closest thing dbt has to "testing the transformation logic itself" rather than the data at rest — you supply fixed input rows and assert the expected output rows, defined declaratively in YAML:

```yaml
# models/python/schema.yml
unit_tests:
  - name: test_segment_thresholds
    model: customer_segments
    given:
      - input: ref('stg_customers')
        rows:
          - {customer_id: 1, total_orders: 50, avg_order_value: 200, days_since_last_order: 3}
    expect:
      rows:
        - {customer_id: 1, segment_name: "Loyal"}
```

If you see code online showing a `tests/python/test_x.py` file with plain `assert` statements that `dbt test` supposedly discovers automatically — that isn't a real dbt mechanism. The validation logic in such examples (null checks, range checks, outlier detection) is real and useful, but it has to be expressed as one of the two mechanisms above, or written as a guard clause *inside* the Python model itself (raising an exception to fail the run), not as a standalone assert-based test file.

## 3. Configuration & Setup

**`dbt_project.yml`:**
```yaml
name: my_project
version: '1.0.0'
profile: snowflake

models:
  my_project:
    python:
      materialized: table
```

**`packages.yml`** manages dbt packages (macros), not Python libraries:
```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.1.0
```

**Python library dependencies** are managed separately from dbt packages — typically via a `requirements.txt` for local/CI execution, and via the platform's package allowlist for in-warehouse execution:
```
pandas>=1.5.0
scikit-learn>=1.2.0
numpy>=1.24.0
pyarrow>=10.0.0
```

**Snowflake profile**, including the Snowpark package list used for in-warehouse Python execution:
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
      query_tag: dbt_python
```

## 4. Where Python Actually Runs

**In the warehouse (preferred):** the `model(dbt, session)` function executes inside the platform's own Python runtime (Snowpark, PySpark, BigQuery's Dataproc-backed runtime) — no data leaves the warehouse, and you get the warehouse's compute. Trade-off: you're limited to that platform's supported/whitelisted packages, and debugging is harder than local Python.

**Locally, for development only:** dbt itself always compiles and submits the job to the platform — Python models don't execute inside your local Python interpreter the way a plain script would. Local `pip install dbt-core dbt-<adapter>` just gives you the CLI to submit `dbt run --select python_model` against the platform.

## 5. When to Use Python vs. SQL

**Reach for Python when the logic doesn't fit naturally in SQL:**
```python
# Machine learning features
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# Complex, hard-to-express business scoring
def calculate_churn_score(customer_data):
    return (customer_data['inactive_days'] * 0.3 +
            customer_data['support_tickets'] * 0.7)
```

**Stick with SQL for everything else:**
```sql
-- Aggregations, joins, window functions — SQL is faster to write, run, and review
select user_id, count(*) as order_count
from orders
group by 1;

select *,
       row_number() over (partition by user_id order by created_at desc) as rn
from sessions;
```

## 6. Production Workflow

```bash
# 1. Develop and test locally against dev target
dbt run --select customer_lifetime_value --target dev

# 2. Run its tests (generic/singular/unit — same as any model)
dbt test --select customer_lifetime_value

# 3. Generate docs (Python models show up in the DAG like any other node)
dbt docs generate
```

**CI/CD example:**
```yaml
# .github/workflows/dbt.yml
name: dbt Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install dbt-snowflake
      - name: Build and test
        run: |
          dbt deps
          dbt build --select state:modified+
```

## 7. Limitations & Gotchas

**Adapter support (as of dbt Core 1.5+):**
- Supported: Snowflake, Databricks, BigQuery.
- Not supported: PostgreSQL, Redshift, DuckDB.

**Package restrictions:** the warehouse's Python runtime only allows a whitelisted set of packages at specific versions — no arbitrary `pip install` at query time, no system-level packages.

**Performance:** Python UDFs/models are typically slower than equivalent SQL, and moving data between the warehouse's native format and a Python DataFrame has real serialization overhead. Memory limits also apply.

**Best practice — filter before you pull into pandas:**
```python
# GOOD: filter in the source relation first
def model(dbt, session):
    raw_data = dbt.ref("big_table").filter("date > '2024-01-01'")
    df = raw_data.to_pandas()
    # ... Python processing on the already-filtered data ...
    return df

# BAD: pulls the entire table into Python before filtering — slow and memory-heavy
def model(dbt, session):
    all_data = dbt.ref("big_table").to_pandas()
    filtered = all_data[all_data['date'] > '2024-01-01']
    return filtered
```

## 8. Quick Start Checklist

1. Confirm your platform supports dbt Python models (Snowflake, Databricks, or BigQuery).
2. Install the adapter: `pip install dbt-snowflake` (or the equivalent for your platform).
3. Create the model: `models/python/my_model.py` with a `model(dbt, session)` function.
4. Add YAML tests (generic/singular) or a unit test for it — same as a SQL model.
5. Run: `dbt run --select my_model`, then `dbt test --select my_model`.

**Bottom line:** dbt Python is not a replacement for SQL — it's for the specific cases (ML feature engineering, complex scoring logic) where Python is clearly the better tool. Default to SQL; add Python only when SQL genuinely can't express the logic cleanly.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 04/Generic Tests & Their Types|Generic Tests & Their Types]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 03/Building Models & Materializations|Building Models & Materializations]]
- [[Data Engineering Role Notes/Data Engineering Concepts/DBT/Module 04/Test Execution, Severity & the `dbt build` Command|Test Execution, Severity & the dbt build Command]]

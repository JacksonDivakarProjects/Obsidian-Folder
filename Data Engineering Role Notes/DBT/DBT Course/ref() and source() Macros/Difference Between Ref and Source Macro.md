### Difference between `ref()` and `source()` macros in **dbt**

#### `ref()`

**Purpose**

- References **dbt models** (tables/views built by dbt).
    

**Used for**

- Dependencies between models.
    
- DAG generation and execution order.
    
- Environment-safe table naming.
    

**Behavior**

- dbt resolves the correct schema and database.
    
- Enables lineage, tests, docs, and `--select` logic.
    

**Example**

```sql
select *
from {{ ref('customers') }}
```

**Meaning**

- “Use the model named `customers`, managed by dbt.”
    

---

#### `source()`

**Purpose**

- References **raw/external tables** not built by dbt.
    

**Used for**

- Ingested data from warehouses, lakes, or external systems.
    
- Defining freshness checks and source-level tests.
    

**Behavior**

- Must be declared in `sources.yml`.
    
- Does not create dependencies between dbt models.
    
- Used as the starting point of the DAG.
    

**Example**

```sql
select *
from {{ source('sales', 'orders') }}
```

**Meaning**

- “Use the raw table `orders` from the `sales` source.”
    

---

### Key Differences (Summary)

|Aspect|`ref()`|`source()`|
|---|---|---|
|Refers to|dbt models|Raw/external tables|
|Managed by dbt|Yes|No|
|Creates DAG edge|Yes|Yes (as a root)|
|Defined in|Model files|`sources.yml`|
|Supports tests|Model tests|Source tests + freshness|

---

### Mental Model

- `source()` = **where data comes from**
    
- `ref()` = **how data is transformed inside dbt**
    

No overlap. Each has a distinct role in dbt’s architecture.

## 🔗 Related Notes
- [[The Ref() Function & Building DAGs|The Ref() Function & Building DAGs]]
- [[Sources YAML File|Sources YAML File]]

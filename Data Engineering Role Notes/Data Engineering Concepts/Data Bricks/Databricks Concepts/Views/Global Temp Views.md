## Global Temporary View in Databricks

![Image](https://images.openai.com/static-rsc-4/2lX4J2ew_DPqjFmjFbFbruo4RRa4_xTx-h8CgZiMsRw5yl-qUhjZ9pK8-M1YXtqOB2Jy6i0B3jv5hebwHN14jJdRwVW9fNq78pCQ5f2rzj87H54_qrnO4-fjahy0eOZ47yuGtnwCQBGW4fxWDx_KssRgJ4ysi2r4RWCRpRNULW3eLv88fOcld8q-EIRTDwNe?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/P-HgR9AGLOyryOWY25KofspgONEh8etUmJcjl-LMGW-kQ2HQwcIxWP7MhD2l9-9elvIuq2Dk9PgaYd_fRlTTFWwj0Ku6vZP4RLXYoQwzzEAryqWhDIlT5SdEW9lnfGa54RAJhVbdfZB1H573mrJLkeVLtB-xF6hEQ9rzDApW0_c2atN0meB87xKLD2OPUc4K?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/LF_2aIChSb0gXcF9Vs9-oVyXZq0ph0x4lS4vmyKuUjjlZffHMWnsGfIytLtv07mrS_7HOtBDth26-5R1UN3n-QD6iWRbUBH8zQU3zgwaCUOz18SGLlaIOm3bceJYxkq-Fj-fONAM_QI-QjM9m5w4uyFOYUbdDGjBfHnkmvBqOwEmtDgj3MUvJY3OtfKwyXSh?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/-SV0cd3W3L9lSMAKFe6xFWO5kf4oy3Dp6YQWCwAnI7WG1JjVeqrK22oXrW5YD4cmLTOUsEzDdYyxQMJkbxaPCpCUDdDoY9fY9J6Na8lzQQvyRY423SRfrgXQcjvZz2DQe431EfNUlNXNElK5Bgi1BwhCz8xh4lz8QnOE_sXc-TnZidqxjop4EgsTuwU1j-51?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/Pqk4VxwOgBleXlR_JLyUeuONddvLCPU_p0qt0OosV_qrEcZIY-XitGL7uOKuv8iHvlgU4x1RAvhCq-aKaqe0i4BHQ5p-87C71XhQUIBFzexQK1Jyr4C3sD2rtX0d1KeWg0zNH9f8tv9crVZKntR65dudqRwFplXSj-F6hxv0guimEY6FMt9ZuBWAmApRgfsv?purpose=fullsize)

**Definition**  
A **global temporary view** is a Spark SQL view that is **shared across all notebooks and sessions within the same cluster**, stored under a system database called `global_temp`.

---

## Core Properties

- **Scope**: Cluster-wide (all notebooks attached to the same cluster)
    
- **Database**: Always stored in `global_temp`
    
- **Persistence**: Exists until the cluster is restarted
    
- **Storage**: No physical storage (logical query only)
    
- **Visibility**: Must be accessed with `global_temp.` prefix
    

---

## Syntax

### SQL

```sql
CREATE OR REPLACE GLOBAL TEMP VIEW sales_view AS
SELECT * FROM sales_data;
```

### Access

```sql
SELECT * FROM global_temp.sales_view;
```

### PySpark

```python
df.createOrReplaceGlobalTempView("sales_view")
```

---

## How It Works (Mechanism)

- Data is not stored
    
- Only the query definition is stored
    
- When queried, Spark recomputes the result
    
- Stored in a **shared catalog (`global_temp`) inside the cluster runtime**
    

---

## Example Flow

1. Notebook A:
    

```sql
CREATE GLOBAL TEMP VIEW temp_kpi AS
SELECT region, SUM(revenue) AS total_revenue
FROM sales
GROUP BY region;
```

2. Notebook B (same cluster):
    

```sql
SELECT * FROM global_temp.temp_kpi;
```

---

## Key Difference vs Temp View

|Feature|Temp View|Global Temp View|
|---|---|---|
|Scope|Single notebook|Entire cluster|
|Prefix required|No|Yes (`global_temp`)|
|Sharing|No|Yes|
|Lifetime|Session|Cluster lifetime|

---

## When to Use

- Multi-notebook workflows within same cluster
    
- Intermediate data sharing without saving tables
    
- Orchestration pipelines where steps run in separate notebooks
    

---

## Limitation

- Lost after cluster restart
    
- Not suitable for production persistence
    
- No performance gain (recomputed every time)

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Databricks Concepts/Views/Views|Views]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Delta Live Tables/View and Streaming Tables/Difference Between Views and Streaming Tables|Difference Between Views and Streaming Tables]]

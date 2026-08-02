Here’s an updated note on **Delta Lake Uniform Format (aka UniForm / Universal Format)**—with key details and a link to the official documentation so you can dig deeper.

---

## Delta Lake Uniform Format (UniForm) — Notes

### What Is It?

- Delta UniForm (Universal Format) allows Delta tables to be **read** by other systems/clients (like Iceberg or Hudi) by **automatically generating corresponding metadata** while retaining a single, consistent data storage. ([Delta Lake](https://docs.delta.io/latest/delta-uniform.html?utm_source=chatgpt.com "Universal Format (UniForm) - Delta Lake Documentation"))
    
- The underlying Parquet data files are shared; only metadata is duplicated/translated. ([Delta Lake](https://docs.delta.io/latest/delta-uniform.html?utm_source=chatgpt.com "Universal Format (UniForm) - Delta Lake Documentation"))
    
- It’s **read-only** from the perspective of Iceberg/Hudi — external engines cannot write to those formats. ([Delta Lake](https://docs.delta.io/latest/delta-uniform.html?utm_source=chatgpt.com "Universal Format (UniForm) - Delta Lake Documentation"))
    

---

### Requirements / Preconditions

|Requirement|Explanation|
|---|---|
|**Column mapping enabled**|The table must use Delta’s column-mapping mode. ([Delta Lake](https://docs.delta.io/latest/delta-uniform.html?utm_source=chatgpt.com "Universal Format (UniForm) - Delta Lake Documentation"))|
|**Minimum protocol versions**|`minReaderVersion` ≥ 2 and `minWriterVersion` ≥ 7 ([Delta Lake](https://docs.delta.io/latest/delta-uniform.html?utm_source=chatgpt.com "Universal Format (UniForm) - Delta Lake Documentation"))|
|**Delta Lake version support**|Writes must use Delta Lake 3.1+ (for Iceberg) / 3.2+ (for Hudi) ([Delta Lake](https://docs.delta.io/latest/delta-uniform.html?utm_source=chatgpt.com "Universal Format (UniForm) - Delta Lake Documentation"))|
|**Catalog / Metastore**|Hive Metastore often required as the catalog to support external reads. ([Delta Lake](https://docs.delta.io/latest/delta-uniform.html?utm_source=chatgpt.com "Universal Format (UniForm) - Delta Lake Documentation"))|
|**No deletion vectors**|UniForm doesn’t support tables that use deletion vectors. ([Delta Lake](https://docs.delta.io/latest/delta-uniform.html?utm_source=chatgpt.com "Universal Format (UniForm) - Delta Lake Documentation"))|
|**Void type unsupported**|Tables with a `VOID` type column are not supported. ([Delta Lake](https://docs.delta.io/latest/delta-uniform.html?utm_source=chatgpt.com "Universal Format (UniForm) - Delta Lake Documentation"))|

---

### How to Enable / Use

**At table creation:**

```sql
CREATE TABLE sales (
  id INT,
  name STRING,
  amount DECIMAL(10,2)
)
USING delta
TBLPROPERTIES (
  'delta.columnMapping.mode' = 'name',
  'delta.enableIcebergCompatV2' = 'true',
  'delta.universalFormat.enabledFormats' = 'iceberg'
);
```

**On existing table:**

```sql
ALTER TABLE sales
SET TBLPROPERTIES (
  'delta.enableIcebergCompatV2' = 'true',
  'delta.universalFormat.enabledFormats' = 'iceberg'
);
```

Or use **REORG** to upgrade and rewrite metadata:

```sql
REORG TABLE sales APPLY (UPGRADE UNIFORM(ICEBERG_COMPAT_VERSION = 2));
```

- The REORG is helpful especially if your table has deletion vectors or was using an older compatibility version. ([Delta Lake](https://docs.delta.io/latest/delta-uniform.html?utm_source=chatgpt.com "Universal Format (UniForm) - Delta Lake Documentation"))
    
- After enabling, UniForm metadata generation is done asynchronously after Delta commits. ([Delta Lake](https://docs.delta.io/latest/delta-uniform.html?utm_source=chatgpt.com "Universal Format (UniForm) - Delta Lake Documentation"))
    

---

### How It Works

- After a Delta commit, Delta Lake **asynchronously** generates the corresponding Iceberg / Hudi metadata in the background. ([Delta Lake](https://docs.delta.io/latest/delta-uniform.html?utm_source=chatgpt.com "Universal Format (UniForm) - Delta Lake Documentation"))
    
- That means writes to Delta are not blocked by metadata generation (in ideal cases). ([Delta Lake](https://docs.delta.io/latest/delta-uniform.html?utm_source=chatgpt.com "Universal Format (UniForm) - Delta Lake Documentation"))
    
- The Iceberg/Hudi metadata is stored under the same directory (e.g. in a `metadata/` folder) alongside Delta’s `_delta_log`. ([Delta Lake](https://docs.delta.io/latest/delta-uniform.html?utm_source=chatgpt.com "Universal Format (UniForm) - Delta Lake Documentation"))
    
- Versions between Delta and Iceberg/Hudi don’t necessarily align directly; you can inspect conversion state via table properties like `converted_delta_version` or `converted_delta_timestamp`. ([Delta Lake](https://docs.delta.io/latest/delta-uniform.html?utm_source=chatgpt.com "Universal Format (UniForm) - Delta Lake Documentation"))
    

---

### Limitations & Warnings

- Iceberg / Hudi clients can **only read**, not write. ([Delta Lake](https://docs.delta.io/latest/delta-uniform.html?utm_source=chatgpt.com "Universal Format (UniForm) - Delta Lake Documentation"))
    
- External writes (by non-Delta engines) may corrupt the consistency and lead to data loss. ([Delta Lake](https://docs.delta.io/latest/delta-uniform.html?utm_source=chatgpt.com "Universal Format (UniForm) - Delta Lake Documentation"))
    
- UniForm doesn’t work on tables with deletion vectors enabled. ([Delta Lake](https://docs.delta.io/latest/delta-uniform.html?utm_source=chatgpt.com "Universal Format (UniForm) - Delta Lake Documentation"))
    
- Some Delta-only features (e.g. Change Data Feed) may not be fully supported in the external formats. ([Delta Lake](https://docs.delta.io/latest/delta-uniform.html?utm_source=chatgpt.com "Universal Format (UniForm) - Delta Lake Documentation"))
    
- Once column mapping is enabled, you can’t disable it. ([Delta Lake](https://docs.delta.io/latest/delta-uniform.html?utm_source=chatgpt.com "Universal Format (UniForm) - Delta Lake Documentation"))
    

---

### Official Documentation Link

You can refer to the official Delta Lake documentation for Uniform / UniForm here:

→ **Universal Format (UniForm) — Delta Lake Documentation**  
[https://docs.delta.io/latest/delta-uniform.html](https://docs.delta.io/latest/delta-uniform.html) ([Delta Lake](https://docs.delta.io/latest/delta-uniform.html?utm_source=chatgpt.com "Universal Format (UniForm) - Delta Lake Documentation"))

---

If you like, I can also create a **cheat sheet PDF** version of this note—compact and print-friendly—for your reference. Do you want me to send that?

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Open Table Format|Open Table Format]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Data Bricks/Databricks Concepts/Managed Vs External Tables|Managed vs External Tables (Unity Catalog)]]

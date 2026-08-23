# Delta Lake Universal Format (UniForm)

**UniForm (Universal Format)** lets a Delta table be **read** by Iceberg or Hudi clients by automatically generating the equivalent metadata for those formats, while the underlying Parquet data files stay shared and single-copy. Only metadata is duplicated/translated — not the data itself.

It is **read-only** from the other formats' perspective: Iceberg/Hudi engines can read a UniForm-enabled Delta table, but they cannot write to it.

## Requirements / Preconditions

| Requirement | Detail |
|---|---|
| Column mapping enabled | The table must use Delta's column-mapping mode (`'name'` mode). |
| Minimum protocol versions | `minReaderVersion` ≥ 2 and `minWriterVersion` ≥ 7. |
| Delta Lake version | Writer must be Delta Lake 3.1+ for Iceberg compatibility, 3.2+ for Hudi. |
| Catalog / metastore | A Hive Metastore (or compatible catalog) is typically required so external engines can discover the table. |
| No deletion vectors | UniForm does not support tables that use deletion vectors. |
| No `VOID` type columns | Tables with a `VOID`-typed column are not supported. |

## Enabling UniForm

At table creation:

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

On an existing table:

```sql
ALTER TABLE sales
SET TBLPROPERTIES (
  'delta.enableIcebergCompatV2' = 'true',
  'delta.universalFormat.enabledFormats' = 'iceberg'
);
```

Or use `REORG` to upgrade and rewrite metadata in one shot (useful if the table currently has deletion vectors or an older compatibility version):

```sql
REORG TABLE sales APPLY (UPGRADE UNIFORM(ICEBERG_COMPAT_VERSION = 2));
```

## How It Works

- After each Delta commit, Delta Lake **asynchronously** generates the corresponding Iceberg/Hudi metadata in the background — writes to Delta are not blocked waiting for that conversion.
- The generated metadata is stored under the same table directory (e.g. a `metadata/` folder) alongside Delta's own `_delta_log`.
- Delta and Iceberg/Hudi versions don't necessarily align 1:1; conversion progress is tracked via table properties like `converted_delta_version` and `converted_delta_timestamp`.

## Limitations & Warnings

- Iceberg/Hudi clients can only **read** a UniForm table, never write to it.
- Writes from a non-Delta engine directly against the shared data files can corrupt consistency and cause data loss — all writes must go through Delta.
- UniForm is incompatible with deletion vectors.
- Some Delta-only features (e.g. Change Data Feed) may not be fully represented in the translated Iceberg/Hudi metadata.
- Once column mapping is enabled on a table, it cannot be disabled again.

## Reference

Official docs: [Universal Format (UniForm) — Delta Lake Documentation](https://docs.delta.io/latest/delta-uniform.html)

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Other Important Concepts/Open Table Format|Open Table Format]]
- [[Managed Vs External Tables|Managed vs External Tables (Unity Catalog)]]

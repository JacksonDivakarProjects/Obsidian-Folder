# PySpark Read Modes

PySpark exposes several read modes for handling corrupt records, malformed data, and schema mismatches during ingestion: **PERMISSIVE**, **DROPMALFORMED**, **FAILFAST**, and (for Parquet/ORC specifically) **EXCEPTION**.

### 📊 1. PERMISSIVE Mode (Default)

- **Description**: The default mode for CSV and JSON. Spark reads as much data as possible; when it hits a corrupt or malformed record, it sets the problematic fields to `null` and keeps going. Optionally, a dedicated column (e.g. `_corrupt_record`) captures the raw corrupt record for later inspection.
- **Use case**: maximizing ingestion when you want to handle errors later — exploratory analysis, noisy data.
- **Example**:
  ```python
  from pyspark.sql.types import StructType, StructField, IntegerType, StringType
  
  schema = StructType([
      StructField("ID", IntegerType(), True),
      StructField("Name", StringType(), True),
      StructField("Salary", IntegerType(), True),
      StructField("Location", StringType(), True),
      StructField("_corrupt_record", StringType(), True)  # Optional column for corrupt records
  ])
  
  df = (spark.read
        .schema(schema)
        .option("mode", "PERMISSIVE")
        .option("columnNameOfCorruptRecord", "_corrupt_record")  # Captures corrupt records
        .csv("/path/to/data.csv"))
  ```

### 🗑️ 2. DROPMALFORMED Mode

- **Description**: Spark drops any row containing malformed or corrupt data. Only rows that fully comply with the schema make it into the resulting DataFrame.
- **Use case**: data quality matters more than completeness — you'd rather discard faulty records than pollute the dataset.
- **Example**:
  ```python
  df = (spark.read
        .format("csv")
        .option("mode", "DROPMALFORMED")
        .option("header", True)
        .option("inferSchema", True)
        .load("/path/to/data.csv"))
  ```

### ⚠️ 3. FAILFAST Mode

- **Description**: Spark throws an exception and halts processing the moment it encounters corrupt or malformed data. Nothing is loaded once an error occurs.
- **Use case**: data integrity is non-negotiable — production pipelines where errors must be caught and fixed before proceeding.
- **Example**:
  ```python
  df = (spark.read
        .format("csv")
        .option("mode", "FAILFAST")
        .option("header", True)
        .schema(schema)  # Schema enforcement
        .load("/path/to/data.csv"))
  ```

### 🔍 4. EXCEPTION Mode (Parquet and ORC)

- **Description**: Specific to Parquet and ORC. Behaves like `FAILFAST` — throws an exception if any corrupted records are found while reading.
- **Use case**: structured binary formats that require strict schema adherence.
- **Example**:
  ```python
  df = spark.read.option("mode", "EXCEPTION").parquet("/path/to/data.parquet")
  ```

### 💡 Key Considerations

- **Schema enforcement**: defining an explicit schema (as in the `PERMISSIVE` example) is strongly recommended for any read mode — it lets Spark validate data accurately instead of guessing.
- **Performance**: `PERMISSIVE` carries extra overhead because it processes every record and captures errors. `DROPMALFORMED` and `FAILFAST` can be faster on clean data but risk data loss or pipeline failure.
- **Corrupt record handling**: with `PERMISSIVE`, use `columnNameOfCorruptRecord` to isolate corrupt rows for debugging (see [[Data Engineering Role Notes/Pyspark/Miscellaneous Concepts|Miscellaneous Concepts]] for why that column sometimes doesn't appear even when this option is set).

### 📋 Summary

| **Mode** | **Description** | **Best For** |
| :--- | :--- | :--- |
| **PERMISSIVE** | Sets corrupt fields to `null` and continues. | Exploratory analysis, noisy data |
| **DROPMALFORMED** | Drops entire rows with corrupt data. | High-quality data requirements |
| **FAILFAST** | Fails immediately on corrupt data. | Production pipelines with strict integrity |
| **EXCEPTION** | Throws an exception for corrupt records (Parquet/ORC). | Binary format processing |

### Further Reading
- [PySpark DataFrame Read Modes — Sathish_DE (Medium)](https://medium.com/@py-spark/pyspark-dataframe-read-modes-me-d269f869617e)
- [Apache Spark 101: Read Modes — Shanoj Kumar V (LinkedIn)](https://www.linkedin.com/pulse/apache-spark-101-read-modes-shanoj-kumar-v-myxpc)

## 🔗 Related Notes
- [[Pyspark Read & Write Operations|Pyspark Read & Write Operations]]
- [[Data Engineering Role Notes/Pyspark/Miscellaneous Concepts|Miscellaneous Concepts]]
- [[Schema Operation in Pyspark|📘 Schema Operations in PySpark]]

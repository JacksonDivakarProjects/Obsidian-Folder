
PySpark provides several read modes to handle issues like corrupt records, malformed data, and schema mismatches when reading data into DataFrames. These modes allow you to control how Spark manages errors during data ingestion. The primary read modes are **PERMISSIVE**, **DROPMALFORMED**, and **FAILFAST**. Additionally, for specific formats like Parquet and ORC, there is an **EXCEPTION** mode. Here's a detailed overview:

### 📊 **1. PERMISSIVE Mode (Default)**
- **Description**: This mode is the default for formats like CSV and JSON. It allows Spark to read as much data as possible. When it encounters corrupt or malformed records, it sets the problematic fields to `null` and continues processing. You can specify a column (e.g., `_corrupt_record`) to capture the corrupt records for further analysis.
- **Use Case**: Ideal when you want to maximize data ingestion and handle errors later, such as in exploratory data analysis or when processing noisy data.
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

### 🗑️ **2. DROPMALFORMED Mode**
- **Description**: In this mode, Spark drops any row that contains malformed or corrupt data. Only rows that fully comply with the schema are included in the resulting DataFrame.
- **Use Case**: Suitable when data quality is critical, and you prefer to discard faulty records entirely rather than risking pollution of your dataset.
- **Example**:
  ```python
  df = (spark.read
        .format("csv")
        .option("mode", "DROPMALFORMED")
        .option("header", True)
        .option("inferSchema", True)
        .load("/path/to/data.csv"))
  ```

### ⚠️ **3. FAILFAST Mode**
- **Description**: This mode causes Spark to immediately throw an exception and halt processing if it encounters any corrupt or malformed data. No data is loaded when an error occurs.
- **Use Case**: Best for scenarios where data integrity is non-negotiable, such as in production pipelines where errors must be addressed before proceeding.
- **Example**:
  ```python
  df = (spark.read
        .format("csv")
        .option("mode", "FAILFAST")
        .option("header", True)
        .schema(schema)  # Schema enforcement
        .load("/path/to/data.csv"))
  ```

### 🔍 **4. EXCEPTION Mode (for Parquet and ORC)**
- **Description**: This mode is specific to Parquet and ORC formats. It behaves similarly to `FAILFAST` by throwing an exception if any corrupted records are found during reading.
- **Use Case**: Used when working with structured binary formats that require strict schema adherence.
- **Example**:
  ```python
  df = spark.read.option("mode", "EXCEPTION").parquet("/path/to/data.parquet")
  ```

### 💡 **Key Considerations**:
- **Schema Enforcement**: Defining an explicit schema (as shown in the `PERMISSIVE` example) is highly recommended when using read modes. This helps Spark validate data accurately and handle discrepancies effectively.
- **Performance**: `PERMISSIVE` mode may incur additional overhead because it processes all records and captures errors. `DROPMALFORMED` and `FAILFAST` might be faster for clean datasets but could lead to data loss or pipeline failures.
- **Corrupt Record Handling**: In `PERMISSIVE` mode, use `columnNameOfCorruptRecord` to isolate corrupt data for debugging. Note that adding this column to your schema might trigger warnings if the number of columns doesn't match the data, but this is normal behavior.

### 📋 **Summary of Read Modes**
| **Mode** | **Description** | **Best For** |
| :--- | :--- | :--- |
| **PERMISSIVE** | Sets corrupt fields to `null` and continues. | Exploratory analysis, noisy data |
| **DROPMALFORMED** | Drops entire rows with corrupt data. | High-quality data requirements |
| **FAILFAST** | Fails immediately on corrupt data. | Production pipelines with strict integrity |
| **EXCEPTION** | Throws exception for corrupt records (Parquet/ORC). | Binary format processing |

For more details, you can refer to the official Spark documentation or articles like those by [Sathish_DE](https://medium.com/@py-spark/pyspark-dataframe-read-modes-me-d269f869617e) and [Shanoj Kumar](https://www.linkedin.com/pulse/apache-spark-101-read-modes-shanoj-kumar-v-myxpc).
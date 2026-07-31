Absolutely, Jack! Let’s create a **comprehensive, industry-ready guide** for **data preprocessing in PySpark**. I’ll include the **common tasks, methods, and code snippets** you’ll actually use on big datasets in production. This will cover everything from **cleaning, transformation, encoding, scaling, feature engineering, and time-series preprocessing**.

---

# **Comprehensive PySpark Data Preprocessing Guide**

---

## **1️⃣ Setup PySpark Environment**

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Initialize Spark session
spark = SparkSession.builder \
    .appName("DataPreprocessingGuide") \
    .getOrCreate()

# Read data
df = spark.read.csv("data.csv", header=True, inferSchema=True)
df.show(5)
```

---

## **2️⃣ Inspect Data**

```python
# Schema and data types
df.printSchema()

# Basic overview
df.show(5)
df.describe().show()

# Check for missing values
df.select([F.count(F.when(F.col(c).isNull(), c)).alias(c) for c in df.columns]).show()
```

---

## **3️⃣ Handling Missing Data**

### a) Drop Rows or Columns

```python
# Drop rows with any null
df_clean = df.dropna()

# Drop rows with threshold
df_clean = df.dropna(thresh=3)  # keep rows with at least 3 non-null values

# Drop columns with nulls
df_clean = df.drop(*['column1', 'column2'])
```

### b) Impute Missing Values

```python
from pyspark.ml.feature import Imputer

imputer = Imputer(inputCols=["age", "salary"], outputCols=["age", "salary"])
df_clean = imputer.fit(df).transform(df)
```

* **Categorical columns** → Fill manually

```python
df = df.fillna({'city': 'Unknown', 'gender': 'Not Specified'})
```

---

## **4️⃣ Handling Duplicates**

```python
df = df.dropDuplicates()
```

---

## **5️⃣ Data Type Conversion**

```python
df = df.withColumn("date", F.to_date("date_column", "yyyy-MM-dd"))
df = df.withColumn("salary", F.col("salary").cast("double"))
```

---

## **6️⃣ Handling Outliers**

### a) Using IQR

```python
quantiles = df.approxQuantile("salary", [0.25, 0.75], 0.01)
Q1, Q3 = quantiles
IQR = Q3 - Q1
df_filtered = df.filter((F.col("salary") >= Q1 - 1.5*IQR) & (F.col("salary") <= Q3 + 1.5*IQR))
```

### b) Capping (Winsorizing)

```python
df = df.withColumn("salary_capped", F.when(F.col("salary") > Q3 + 1.5*IQR, Q3 + 1.5*IQR)
                                    .when(F.col("salary") < Q1 - 1.5*IQR, Q1 - 1.5*IQR)
                                    .otherwise(F.col("salary")))
```

---

## **7️⃣ Feature Engineering**

### a) Create new columns

```python
df = df.withColumn("price_per_unit", F.col("price")/F.col("quantity"))
```

### b) Time-based features

```python
df = df.withColumn("year", F.year("date")) \
       .withColumn("month", F.month("date")) \
       .withColumn("day_of_week", F.dayofweek("date"))
```

### c) Binning / Bucketing

```python
from pyspark.ml.feature import Bucketizer

splits = [0, 1000, 5000, 10000, float("inf")]
bucketizer = Bucketizer(splits=splits, inputCol="salary", outputCol="salary_bucket")
df = bucketizer.transform(df)
```

---

## **8️⃣ Encoding Categorical Variables**

### a) StringIndexer (Label Encoding)

```python
from pyspark.ml.feature import StringIndexer

indexer = StringIndexer(inputCols=["city", "gender"], outputCols=["city_index", "gender_index"])
df = indexer.fit(df).transform(df)
```

### b) OneHotEncoder

```python
from pyspark.ml.feature import OneHotEncoder

encoder = OneHotEncoder(inputCols=["city_index"], outputCols=["city_vec"])
df = encoder.fit(df).transform(df)
```

---

## **9️⃣ Scaling and Normalization**

```python
from pyspark.ml.feature import MinMaxScaler, StandardScaler, VectorAssembler

# Combine numeric columns into feature vector
assembler = VectorAssembler(inputCols=["age", "salary"], outputCol="features")
df_vector = assembler.transform(df)

# Standard Scaling
scaler = StandardScaler(inputCol="features", outputCol="scaled_features")
df_scaled = scaler.fit(df_vector).transform(df_vector)

# Min-Max Scaling
scaler = MinMaxScaler(inputCol="features", outputCol="scaled_features")
df_scaled = scaler.fit(df_vector).transform(df_vector)
```

---

## **🔟 Handling Skewed Data / Transformation**

```python
# Log transformation
df = df.withColumn("log_salary", F.log1p("salary"))

# Square root transformation
df = df.withColumn("sqrt_salary", F.sqrt("salary"))
```

---

## **1️⃣1️⃣ Rolling / Smoothing / Time-Series Preprocessing**

```python
# Rolling average with window function
windowSpec = Window.partitionBy("category").orderBy("date").rowsBetween(-2, 0)
df = df.withColumn("rolling_avg_sales", F.avg("sales").over(windowSpec))
```

* Can also do **time binning**:

```python
df_binned = df.groupBy(F.window("timestamp", "1 hour")).agg(F.sum("sales").alias("total_sales"))
```

---

## **1️⃣2️⃣ Sampling**

```python
# Random sample of 10% data
df_sample = df.sample(False, 0.1, seed=42)

# Random 100 rows
df_sample = df.orderBy(F.rand()).limit(100)
```

---

## **1️⃣3️⃣ Quantiles / Percentiles**

```python
# Approximate quantiles
quantiles = df.approxQuantile("salary", [0.25, 0.5, 0.75], 0.01)
print(quantiles)

# Percentile using SQL expression
df.selectExpr("percentile_approx(salary, 0.9)").show()
```

---

## **1️⃣4️⃣ Data Validation / Type Checks**

```python
# Check nulls
df.select([F.count(F.when(F.col(c).isNull(), c)).alias(c) for c in df.columns]).show()

# Check duplicates
df.groupBy(df.columns).count().filter("count > 1").show()
```

---

## **1️⃣5️⃣ Feature Selection / Cleaning**

* Drop columns with **low variance** or **high null percentage**
* Drop **redundant or highly correlated features**
* Keep **only relevant features for ML pipelines**

---

## **1️⃣6️⃣ Putting It Together — Example Pipeline**

```python
from pyspark.ml import Pipeline
from pyspark.ml.feature import Imputer, StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler

pipeline = Pipeline(stages=[
    Imputer(inputCols=["age", "salary"], outputCols=["age", "salary"]),
    StringIndexer(inputCols=["city"], outputCols=["city_index"]),
    OneHotEncoder(inputCols=["city_index"], outputCols=["city_vec"]),
    VectorAssembler(inputCols=["age", "salary", "city_vec"], outputCol="features"),
    StandardScaler(inputCol="features", outputCol="scaled_features")
])

df_preprocessed = pipeline.fit(df).transform(df)
```

---

## **✅ Pro Tips (Industry Best Practices)**

1. Always **inspect data before preprocessing** (`.show()`, `.info()`, `.describe()`).
2. **Impute missing data** before scaling/encoding.
3. **Encode categorical variables after cleaning nulls**.
4. Use **window functions** for rolling averages or time-based features.
5. Keep **all preprocessing reproducible** using **pipelines**.
6. **Avoid `.collect()` on large datasets** — use distributed PySpark operations.

---

This covers **all major preprocessing steps used in the industry**:

* Cleaning (nulls, duplicates, outliers)
* Transformation (type casting, scaling, log, sqrt)
* Feature Engineering (binning, rolling, time features)
* Encoding (label & one-hot)
* Sampling, percentiles, validation
* Pipeline integration

---

If you want, I can make a **single PySpark template script** that has **all preprocessing steps ready to run on any dataset** — fully commented and production-ready. It’s extremely useful for Kaggle or company projects.

Do you want me to create that?
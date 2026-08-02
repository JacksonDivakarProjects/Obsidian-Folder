Perfect, Jack 👌 — let’s make this **hands-on with Spark**. I’ll show you **how to use `regexp_extract`, `regexp_replace`, `split`, and `rlike` in Spark SQL and PySpark** with examples using a practice DataFrame.

---

## 1️⃣ Setup Practice DataFrame

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("RegexPractice").getOrCreate()

data = [
    (1, "Order#1234 shipped", "2025-10-03 10:45:32 INFO User=John", "john.doe@gmail.com", "+1-202-555-0199"),
    (2, "Invoice: 5678 pending", "2025-10-02 08:12:11 WARN User=Alice", "alice_99@yahoo.com", "+91-9876543210"),
    (3, "Payment TXN=998877 completed", "2025-09-30 14:55:01 ERROR User=Bob", "bob@company.co.uk", "555-123-4567"),
    (4, "Order#4321 delivered", "2025-09-29 09:22:45 INFO User=Charlie", "charlie123@hotmail.com", "(202) 333-4444")
]

cols = ["id", "raw_text", "log_entry", "email", "phone"]

df = spark.createDataFrame(data, cols)
df.createOrReplaceTempView("regex_practice")
```

---

## 2️⃣ `regexp_extract` — Extract patterns

```python
# Extract order number from raw_text
spark.sql("""
SELECT id,
       regexp_extract(raw_text, '(\\d+)', 1) AS order_number
FROM regex_practice
""").show()
```

**PySpark DataFrame API:**

```python
from pyspark.sql.functions import regexp_extract

df.select("id", regexp_extract("raw_text", "(\\d+)", 1).alias("order_number")).show()
```

---

## 3️⃣ `regexp_replace` — Replace patterns

```python
# Remove '#' and digits from raw_text
spark.sql("""
SELECT id,
       regexp_replace(raw_text, '#\\d+', '') AS cleaned_text
FROM regex_practice
""").show()
```

**PySpark API:**

```python
from pyspark.sql.functions import regexp_replace

df.select("id", regexp_replace("raw_text", "#\\d+", "").alias("cleaned_text")).show()
```

---

## 4️⃣ `split` — Split strings

```python
# Extract domain from email
spark.sql("""
SELECT id,
       split(email, '@')[1] AS domain
FROM regex_practice
""").show()
```

**PySpark API:**

```python
from pyspark.sql.functions import split

df.select("id", split("email", "@")[1].alias("domain")).show()
```

---

## 5️⃣ `rlike` — Boolean pattern matching

```python
# Select rows with 4-digit numbers in raw_text
spark.sql("""
SELECT *
FROM regex_practice
WHERE raw_text RLIKE '\\d{4}'
""").show()
```

**PySpark API:**

```python
df.filter(df.raw_text.rlike("\\d{4}")).show()
```

---

## 6️⃣ `translate` — Remove unwanted characters

```python
# Remove '+', '-', '(', ')' from phone numbers
from pyspark.sql.functions import translate

df.select("id", translate("phone", "+-()", "").alias("clean_phone")).show()
```

---

## ✅ Tips for Practice

1. Always test your regex first in Python or an online tool.
    
2. `regexp_extract` → group index matters (`1` is first captured group).
    
3. `regexp_replace` → replaces **all matches** by default.
    
4. `split` → returns an **array**, use `[i]` to pick elements.
    
5. `rlike` → perfect for **filtering rows** by pattern.
    

---

If you want, I can **create a full list of 10 Spark SQL / PySpark exercises** using this DataFrame — for **extracting order IDs, emails, phone parts, timestamps**, etc. — so you can actually practice regex in Spark hands-on.

Do you want me to do that next?

## 🔗 Related Notes
- [[Data Science/Pyspark/Functions in Pyspark|Functions in Pyspark]]
- [[Data Science/Pyspark/Spark SQL|Spark SQL]]

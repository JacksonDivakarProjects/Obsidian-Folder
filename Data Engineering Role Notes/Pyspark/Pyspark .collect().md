# `.collect()` in PySpark

`.collect()` needs to be used carefully — it's one of the easiest ways to accidentally crash a driver.

## ✅ What `.collect()` Does

- Executes the Spark job.
- Brings **all rows** of the DataFrame from the cluster into the driver (your Python process).
- Returns a **list of `Row` objects**.

### Example

```python
rows = df.collect()
for row in rows:
    print(row)
```

If `df` has:

```
+---+------+
| id| name |
+---+------+
|  1| John |
|  2| Mary |
+---+------+
```

Then `collect()` gives:

```python
[Row(id=1, name='John'), Row(id=2, name='Mary')]
```

## ⚠️ Important Caveats

- It brings **everything** to the driver — if the dataset is GBs/TBs, this can crash the driver's memory. The driver has a single JVM's worth of RAM, not the cluster's.
- Use it only when you know the result set is small.

## ✅ Safer Alternatives

- `.show(n)` → pretty-prints the first `n` rows without pulling everything to the driver.
- `.take(n)` → returns the first `n` rows as a Python list.
- `.limit(n).collect()` → collects only a bounded subset.
- `.toPandas()` → converts the Spark DataFrame to Pandas — still pulls everything to the driver, so it carries the same risk as `.collect()` for large data.

## 🎯 Bottom Line

- `.collect()` pulls the **entire DataFrame** to the driver.
- Useful for debugging, small datasets, or when the full result genuinely needs to live in Python.
- For large data, stay in Spark transformations/actions (`show`, `take`, `limit`) as long as possible.

## 🔗 Related Notes
- [[Spark RDD|Spark RDD]]
- [[Basic DataFrame Operation|Basic DataFrame Operation]]

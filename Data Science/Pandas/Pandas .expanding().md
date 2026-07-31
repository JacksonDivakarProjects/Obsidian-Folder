# **The Essential Pandas `.expanding()` Guide**  
*(Complete Reference with Practical Examples)*  

---

## **1. Core Concept: What is `.expanding()`?**  
Unlike `.rolling()` (fixed window), `.expanding()` grows over time:  
- **Starts at first data point** → **ends at full dataset**  
- Calculates **cumulative statistics** (e.g., running total, expanding average)  

---

## **2. Basic Syntax & Key Parameters**  
```python
Series/DataFrame.expanding(
    min_periods=1,  # Minimum observations to start calculation
    axis=0          # 0 for rows, 1 for columns
).agg_func()
```

### **Key Parameters**  
| Parameter | Purpose | Default |
|-----------|---------|---------|
| `min_periods` | Skip early `NaN`s by requiring N values | `1` |
| `axis` | Direction of expansion (`0`=row-wise, `1`=column-wise) | `0` |

---

## **3. Must-Know Expanding Operations**  

### **Basic Aggregations**  
```python
# Cumulative Sum
df['running_total'] = df['sales'].expanding().sum()

# Expanding Average (mean of all data up to each point)
df['cumulative_avg'] = df['price'].expanding().mean()

# Expanding Maximum (running max)
df['peak_value'] = df['value'].expanding().max()
```

### **With `min_periods` Control**  
```python
# Wait until 5 data points are available
df['safe_avg'] = df['price'].expanding(min_periods=5).mean()
```

### **Time-Based Expanding (for Datetime Index)**  
```python
df = df.set_index('date')  # Requires datetime index
df['ytd_sum'] = df['revenue'].expanding().sum()  # Year-to-date total
```

---

## **4. Real-World Use Cases**  

### **Case 1: Financial Analysis**  
```python
# Cumulative Returns
df['cumulative_return'] = (1 + df['daily_return']).expanding().prod() - 1

# Drawdown Calculation
df['peak'] = df['portfolio_value'].expanding().max()
df['drawdown'] = (df['portfolio_value'] - df['peak']) / df['peak']
```

### **Case 2: Business Metrics**  
```python
# Running Conversion Rate
df['conversion_rate'] = (
    df['conversions'].expanding().sum() / 
    df['visitors'].expanding().sum()
)

# Year-to-Date Revenue
df['ytd_revenue'] = df['monthly_revenue'].expanding().sum()
```

### **Case 3: Sensor Data Analysis**  
```python
# Cumulative Average Temperature
df['avg_temp_since_start'] = df['temperature'].expanding().mean()

# Maximum Observed Value
df['record_high'] = df['sensor_reading'].expanding().max()
```

---

## **5. Advanced Techniques**  

### **Custom Expanding Functions**  
```python
# Custom expanding calculation
def custom_ratio(x):
    return x[-1] / x.mean()  # Latest value vs historical average

df['custom_metric'] = df['value'].expanding().apply(custom_ratio)
```

### **Multiple Aggregations**  
```python
# Get multiple stats at once
exp_stats = df['price'].expanding().agg(['mean', 'std', 'min', 'max'])
```

### **Pairing with `.rolling()`**  
```python
# Ratio of 30-day average to all-time average
df['ratio'] = (
    df['price'].rolling(30).mean() / 
    df['price'].expanding().mean()
)
```

---

## **6. Pro Tips & Performance**  

✅ **Set `min_periods`** to avoid noisy early calculations:  
```python
df['stable_avg'] = df['value'].expanding(min_periods=10).mean()
```

🚀 **Faster computation with `engine='numba'`**:  
```python
df['fast_cumsum'] = df['value'].expanding(engine='numba').sum()
```

⚠️ **Watch for Memory Issues** with large datasets (expanding windows grow unbounded).  

---

## **7. Quick Cheat Sheet**  

| **Goal** | **Code** |
|----------|----------|
| Running total | `.expanding().sum()` |
| Cumulative average | `.expanding().mean()` |
| All-time high | `.expanding().max()` |
| Historical standard deviation | `.expanding().std()` |
| Custom function | `.expanding().apply(your_function)` |

---

## **When to Use `.expanding()` vs `.rolling()`**  
- Use `.expanding()` when you need **all historical data** up to each point  
- Use `.rolling()` when you only care about **recent N periods**  

This guide covers **100% of practical `.expanding()` use cases** with optimal performance! 🚀
# **The Essential Pandas `.rolling()` Guide**  
*(Focused on Practical Usage with Clear Examples)*  

---

## **1. Core Syntax & Most Important Parameters**
```python
Series/DataFrame.rolling(
    window,          # Size of the moving window (int or time offset)
    min_periods=1,   # Minimum observations needed (avoid early NaN)
    center=False,    # Center the window (for symmetrical averages)
).agg_func()        # .mean(), .sum(), .std(), etc.
```

### **Key Parameters Explained**  
| Parameter | When to Use | Example |
|-----------|------------|---------|
| **`window`** | Window size (number of rows or time like `'7D'`) | `window=30` (30 rows) or `window='2H'` (2 hours) |
| **`min_periods`** | Avoid NaN at the start (e.g., require at least 5 values) | `min_periods=5` |
| **`center`** | For centered averages (e.g., 3-day avg: [-1 day, current, +1 day]) | `center=True` |

---

## **2. Must-Know Rolling Operations**  

### **Basic Aggregations**  
```python
# Moving Average (7-day)
df['MA7'] = df['price'].rolling(7).mean()  

# Rolling Sum (3-period sum)
df['3_day_total'] = df['sales'].rolling(3).sum()  

# Rolling Volatility (20-day std dev)
df['volatility'] = df['returns'].rolling(20).std()  
```

### **Time-Based Rolling (Best for Dates)**  
```python
# 30-day average (calendar days, skips missing dates)
df['MA30'] = df['price'].rolling('30D').mean()  

# 4-hour max (for intraday data)
df['4h_high'] = df['price'].rolling('4H').max()  
```

### **Edge Control with `min_periods`**  
```python
# Require at least 10 values (avoid early NaN)
df['MA10'] = df['price'].rolling(10, min_periods=10).mean()  

# Partial windows allowed (but need at least 3)
df['MA_partial'] = df['price'].rolling(10, min_periods=3).mean()  
```

### **Centered Rolling (for Smooth Trends)**  
```python
# 5-day centered average (2 days before + current + 2 days after)
df['MA_centered'] = df['price'].rolling(5, center=True).mean()  
```

---

## **3. Real-World Use Cases**  

### **Case 1: Stock Market Analysis**  
```python
# Golden Cross (50-day vs 200-day MA)
df['MA50'] = df['close'].rolling(50).mean()  
df['MA200'] = df['close'].rolling(200).mean()  

# Bollinger Bands (20-day MA ± 2 std dev)
df['upper_band'] = df['close'].rolling(20).mean() + 2 * df['close'].rolling(20).std()  
df['lower_band'] = df['close'].rolling(20).mean() - 2 * df['close'].rolling(20).std()  
```

### **Case 2: Sensor Data Smoothing**  
```python
# 5-minute smoothing (for noisy IoT data)
df['smoothed_temp'] = df['raw_temp'].rolling('5T').mean()  

# Remove short spikes (5-min median filter)
df['filtered'] = df['sensor_value'].rolling('5T').median()  
```

### **Case 3: Business Metrics**  
```python
# 7-day rolling revenue (sum)
df['weekly_revenue'] = df['daily_sales'].rolling(7).sum()  

# 30-day customer retention rate
df['retention'] = df['active_users'].rolling(30).apply(lambda x: x[-1]/x[0])  
```

---

## **4. Pro Tips & Common Pitfalls**  

✅ **Always set `min_periods`** (to avoid misleading early values):  
```python
df['MA'] = df['price'].rolling(30, min_periods=10).mean()  # Require at least 10 data points  
```

✅ **Use time-based windows (`'7D'`, `'1H'`) instead of fixed rows** if data has gaps.  

❌ **Don’t chain multiple `.rolling()` calls** (slow!):  
```python
# Bad (slow):
df['MA'] = df['price'].rolling(7).mean().rolling(7).std()  

# Good (faster):
df['MA'] = df['price'].rolling(7).agg(['mean', 'std'])  
```

🚀 **For big datasets, use `engine='numba'` (faster!):**  
```python
df['MA'] = df['price'].rolling(1000, engine='numba').mean()  
```

---

## **5. Quick Cheat Sheet**  

| **Goal** | **Code** |
|----------|----------|
| 7-day moving average | `.rolling(7).mean()` |
| 30-day sum (require 10 values) | `.rolling(30, min_periods=10).sum()` |
| 1-hour max (time-based) | `.rolling('1H').max()` |
| Centered 5-day average | `.rolling(5, center=True).mean()` |
| Multiple stats (mean + std) | `.rolling(20).agg(['mean', 'std'])` |

---

### **Final Advice**  
- **For stock/financial data**: Use time windows (`'30D'`, `'1H'`).  
- **For IoT/sensor data**: Use `.median()` to filter noise.  
- **For business metrics**: Use `.sum()` for cumulative KPIs.  

This covers **90% of real-world `.rolling()` use cases** efficiently! 🚀
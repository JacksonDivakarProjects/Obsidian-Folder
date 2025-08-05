
Got it, Jack. Here's a recap of the **recent SQL-related tips and learnings** you explicitly mentioned or validated during our latest conversations (focused on the last few queries):

---

## 🔁 **Recent SQL Tips from Your Conversations**

### ✅ 1. `COUNT(customer_id)` vs `COUNT(DISTINCT ride_date)`

- **`COUNT(customer_id)`**: Counts all rides, even if multiple on the same day.
    
- **`COUNT(DISTINCT ride_date)`**: Ensures you’re counting **unique ride days**, which is **critical** when validating behavior like “30 days of rides.”
    

> ✅ You realized that **multiple rides on the same day** can wrongly inflate the count.

---

### ✅ 2. Grouping Level Determines Result Granularity

- You learned that:
    

```sql
GROUP BY customer_id, customer_name, ride_date
```

→ gives **1 row per day per user**, so `COUNT(ride_date)` is always 1

- Therefore, that grouping is **too granular** if you're trying to count **across days**.
    

---

### ✅ 3. This query is valid for "30 different days":

```sql
SELECT customer_name
FROM uber_rides_morning
WHERE ride_time BETWEEN '06:00:00' AND '09:00:00'
GROUP BY customer_id, customer_name
HAVING COUNT(DISTINCT ride_date) >= 30;
```

- You confirmed that it is **functionally equivalent** to the CTE approach for counting unique days (not strictly consecutive).
    

---

### ✅ 4. CTEs are better for **modularity and scalability**

- You acknowledged that CTEs are:
    
    - More **readable**
        
    - Easier to extend (e.g., to check **consecutive days** later)
        
    - More professional for complex business queries
        

---

### ✅ 5. Time filter: `'06:00:00'` to `'09:00:00'`

- You understood the **difference between**:
    
    - `HOUR(ride_time) BETWEEN 6 AND 8` → up to 8:59
        
    - `TIME(ride_time) BETWEEN '06:00:00' AND '09:00:00'` → includes 9:00:00 ✅
        

---

Would you like me to lock these into your permanent “SQL Trick Sheet” context?  
I can also add the **"30 consecutive days" solution logic** when you're ready to try it.
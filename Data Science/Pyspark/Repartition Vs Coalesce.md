
Great question, Jack 👌 — this is a subtle but important distinction in Spark.

Both **`repartition()`** and **`coalesce()`** change the number of partitions in a DataFrame/RDD, but they serve **different use cases** and are designed with **performance trade-offs** in mind:

---

### 🔹 `repartition(n)`

- **Shuffles data across the cluster.**
    
- Can **increase or decrease** the number of partitions.
    
- Produces **evenly balanced partitions** (good distribution).
    
- More **expensive** because it triggers a **full shuffle**.
    
- Useful when:
    
    - You want balanced load across executors.
        
    - You're increasing partitions for parallelism.
        
    - You're preparing data for wide transformations (like joins).
        

---

### 🔹 `coalesce(n)`

- **Does not shuffle (by default).**
    
- Can **only reduce** the number of partitions.
    
- Simply **merges existing partitions** into fewer ones.
    
- **Much cheaper** than repartition.
    
- But: partitions may become **uneven** (data skew risk).
    
- Useful when:
    
    - You’ve already done a shuffle (like after `groupBy` or `join`) and partitions are spread.
        
    - You’re writing the final output and want fewer files (e.g., `coalesce(1)` → single file).
        
    - Performance > perfectly even distribution.
        

---

### ⚡ Why both exist?

Because Spark engineers had to balance **fairness vs. efficiency**:

- `repartition` → guarantees balance, but at high cost.
    
- `coalesce` → minimizes shuffle (cheap), but risks imbalance.
    

So, the right choice depends on your workload:

- If **load balancing** matters → use `repartition()`.
    
- If **shuffle cost is the bottleneck** and imbalance is tolerable → use `coalesce()`.
    

---

👉 Think of it like this:

- **Repartition = "expensive restructuring with balance"**
    
- **Coalesce = "cheap merging, may be uneven"**
    

---

Do you want me to show you a **small example with execution plans** (`explain()`) so you can _see_ the shuffle difference?
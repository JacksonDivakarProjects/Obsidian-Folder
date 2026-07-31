# SQL EXISTS & NOT EXISTS: Quick Revision Guide

## **Core Concept**
- **EXISTS**: Checks if a subquery returns **any rows** (returns TRUE if ≥1 row)
- **NOT EXISTS**: Checks if a subquery returns **no rows** (returns TRUE if 0 rows)

**Basic Syntax:**
```sql
SELECT columns
FROM main_table m
WHERE [NOT] EXISTS (
    SELECT 1  -- Standard practice, use 1 instead of *
    FROM related_table r
    WHERE r.matching_column = m.matching_column
);
```

---

## **Key Applications with Examples**

### **1. Finding Relationships (EXISTS)**
**Scenario:** Get customers who have placed orders
```sql
SELECT CustomerName 
FROM Customers C
WHERE EXISTS (
    SELECT 1
    FROM Orders O
    WHERE O.CustomerID = C.CustomerID
);
```

### **2. Finding Missing Data (NOT EXISTS)**
**Scenario:** Find products never ordered
```sql
SELECT ProductName
FROM Products P
WHERE NOT EXISTS (
    SELECT 1
    FROM OrderDetails OD
    WHERE OD.ProductID = P.ProductID
);
```

### **3. Finding Departments with Employees**
**Scenario:** Identify active departments
```sql
SELECT DepartmentName
FROM Departments D
WHERE EXISTS (
    SELECT 1
    FROM Employees E
    WHERE E.DepartmentID = D.DepartmentID
);
```

### **4. Finding Empty Departments**
**Scenario:** Identify inactive departments
```sql
SELECT DepartmentName
FROM Departments D
WHERE NOT EXISTS (
    SELECT 1
    FROM Employees E
    WHERE E.DepartmentID = D.DepartmentID
);
```

---

## **Critical Performance Tips**

### **Use SELECT 1, not SELECT ***
- Database stops at first match
- SELECT 1 tells optimizer: "Just check existence"
```sql
-- ✅ Do this:
WHERE EXISTS (SELECT 1 FROM ...)

-- ❌ Avoid this:
WHERE EXISTS (SELECT * FROM ...)
```

### **Correlation is Required**
- Subquery **must reference** outer query's column
- This creates a correlated subquery (runs once per outer row)

---

## **Quick Comparison Table**

| Operator | Returns TRUE When | Best For |
|----------|-------------------|----------|
| `EXISTS` | Subquery finds ≥1 row | Finding records with matches |
| `NOT EXISTS` | Subquery finds 0 rows | Finding records without matches |

---

## **Common Patterns to Remember**

**Pattern 1:** Find what exists
```sql
WHERE EXISTS (SELECT 1 FROM related WHERE match)
```

**Pattern 2:** Find what's missing
```sql
WHERE NOT EXISTS (SELECT 1 FROM related WHERE match)
```

**Pattern 3:** Add conditions in subquery
```sql
WHERE EXISTS (
    SELECT 1
    FROM Orders O
    WHERE O.CustomerID = C.CustomerID
    AND O.OrderDate > '2024-01-01'  -- Additional filter
)
```

---

## **Why NOT EXISTS > NOT IN**

**Safety:** NOT EXISTS handles NULLs correctly
```sql
-- ✅ Safe with NULLs:
WHERE NOT EXISTS (SELECT 1 FROM table WHERE condition)

-- ❌ Problematic with NULLs:
WHERE column NOT IN (SELECT column FROM table)
```

---

## **Cheat Sheet for Revision**

1. **Use EXISTS** when you want: "Show me records that HAVE related data"
2. **Use NOT EXISTS** when you want: "Show me records that DON'T HAVE related data"
3. **Always use**: `SELECT 1` in the subquery
4. **Always include**: Correlation condition (inner.column = outer.column)
5. **Remember**: Subquery checks existence only, not values

**Memory Aid:**
- `EXISTS` = "Is there at least one?" → Returns records WITH matches
- `NOT EXISTS` = "Are there none?" → Returns records WITHOUT matches

This optimized guide focuses on the essential patterns you'll use 95% of the time. Master these, and you've mastered EXISTS/NOT EXISTS!
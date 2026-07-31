# SQL Keywords Quick Reference: ALL, ANY, LIKE

## **1. ALL - Universal Comparison**
**Purpose:** Compare against EVERY value in a subquery result.

### **Key Applications:**

#### **Finding Maximum/Minimum Values**
```sql
-- Find products more expensive than ALL accessories
SELECT ProductName, Price
FROM Products
WHERE Price > ALL (
    SELECT Price 
    FROM Products 
    WHERE Category = 'Accessories'
);
```
*Equivalent to:* `WHERE Price > MAX(subquery)`

#### **Finding Records Below All Thresholds**
```sql
-- Find employees with salaries less than ALL managers
SELECT EmployeeName, Salary
FROM Employees
WHERE Salary < ALL (
    SELECT Salary 
    FROM Employees 
    WHERE Role = 'Manager'
);
```
*Equivalent to:* `WHERE Salary < MIN(subquery)`

---

## **2. ANY - Existential Comparison**
**Purpose:** Compare against AT LEAST ONE value in a subquery result.

### **Key Applications:**

#### **Alternative to IN (Equality Check)**
```sql
-- Find employees on ANY active project
SELECT EmployeeName
FROM Assignments
WHERE ProjectID = ANY (
    SELECT ProjectID 
    FROM Projects 
    WHERE Status = 'Active'
);
```
*Note:* `= ANY` is equivalent to `IN`

#### **Range Overlap Checks**
```sql
-- Find orders placed after ANY today's order
SELECT OrderID, OrderTime
FROM Orders
WHERE OrderTime > ANY (
    SELECT OrderTime 
    FROM Orders 
    WHERE OrderDate = CURRENT_DATE
);
```
*Meaning:* Later than the earliest order today

#### **Finding Above/Below Some Threshold**
```sql
-- Products cheaper than ANY luxury item
SELECT ProductName, Price
FROM Products
WHERE Price < ANY (
    SELECT Price 
    FROM Products 
    WHERE Category = 'Luxury'
);
```
*Meaning:* Cheaper than the most expensive luxury item

---

## **3. LIKE - Pattern Matching**
**Purpose:** Search for text patterns using wildcards.

### **Wildcards:**
- `%` = Zero or more characters
- `_` = Exactly one character

### **Common Applications:**

#### **Search Box Implementation**
```sql
-- Search for "choc" anywhere in name
SELECT ProductName
FROM Products
WHERE ProductName LIKE '%choc%';
-- Returns: Chocolate, Dark Chocolate, etc.
```

#### **Email Domain Filtering**
```sql
-- Find all Gmail users
SELECT Email
FROM Users
WHERE Email LIKE '%@gmail.com';
```

#### **Fixed Pattern Matching**
```sql
-- Find 5-character product codes starting with 'A'
SELECT ProductCode
FROM Products
WHERE ProductCode LIKE 'A____';
-- Returns: A1234, ABCDE, AX987, etc.
```

#### **Position-Based Filtering**
```sql
-- Find Florida customers (FL)
SELECT CustomerName, State
FROM Customers
WHERE State LIKE '_L';
-- Returns: FL, IL (if IL existed), etc.
```

---

## **Quick Comparison Table**

| Keyword | When to Use | Equivalent To |
|---------|------------|--------------|
| **ALL** | Must satisfy condition against ALL values | `> ALL` = `> MAX()`<br>`< ALL` = `< MIN()` |
| **ANY** | Must satisfy condition against AT LEAST ONE value | `= ANY` = `IN`<br>`> ANY` = `> MIN()` |
| **LIKE** | Searching for text patterns | String pattern matching |

---

## **Memory Aids & Common Pitfalls**

### **ALL vs ANY**
```sql
-- ALL: Strict - compare against EVERY value
WHERE price > ALL (10, 20, 30)  -- Must be >30

-- ANY: Lenient - compare against ANY value
WHERE price > ANY (10, 20, 30)  -- Must be >10
```

### **LIKE Performance Tips**
1. **Avoid leading % when possible:**
   ```sql
   -- ❌ Slow: Can't use indexes
   WHERE name LIKE '%son'
   
   -- ✅ Fast: Can use indexes
   WHERE name LIKE 'John%'
   ```

2. **Case sensitivity depends on database collation**
3. **Use ESCAPE for literal % or _**
   ```sql
   WHERE comment LIKE '100\% discount' ESCAPE '\'
   ```

---

## **When to Use Each**

### **Use ALL when:**
- Checking against maximum/minimum thresholds
- Need "better than best" or "worse than worst" logic
- Want strict universal comparison

### **Use ANY when:**
- Looking for overlap or existence
- Need "better than at least one" logic
- Using equality with subqueries (like IN)

### **Use LIKE when:**
- Implementing search functionality
- Filtering by partial strings or patterns
- Working with formatted codes or identifiers

---

## **Revision Checklist**
- [ ] **ALL** = Compare against EVERY value in subquery
- [ ] **ANY** = Compare against AT LEAST ONE value in subquery
- [ ] **LIKE** = Pattern matching with % and _
- [ ] `= ANY` = `IN` (they're equivalent)
- [ ] `> ALL` = `> MAX(subquery)`
- [ ] `< ANY` = `< MAX(subquery)`
- [ ] **%** matches any sequence of characters
- [ ] **_ ** matches exactly one character

This guide focuses on practical applications you'll actually use in real SQL queries. Master these patterns, and you'll handle 90% of use cases for these keywords!
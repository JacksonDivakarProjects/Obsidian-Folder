# Dimension Hierarchies: Comprehensive Guide

A **hierarchy in a dimension** allows business users to analyze data from a higher level to a lower level.

For example:

```text
Company
   ↓
Department
   ↓
Category
   ↓
Product
```

The important question is **how the hierarchy is structured and how you want to store/query it**.

---

# 1. First understand hierarchy vs dimension

A dimension contains descriptive information.

For example:

### `Dim_Product`

|Product_Key|Product|Brand|Category|Department|
|--:|---|---|---|---|
|101|Laptop A|Dell|Laptop|Electronics|
|102|Laptop B|Dell|Laptop|Electronics|
|103|Mouse A|Logitech|Mouse|Electronics|

Here you can see a hierarchy:

```text
Department
    ↓
Category
    ↓
Brand
    ↓
Product
```

This allows analysis such as:

```text
Sales by Department
       ↓
Sales by Category
       ↓
Sales by Brand
       ↓
Sales by Product
```

This is the basis of **drill-down**.

---

# 2. Fixed-depth hierarchy

The simplest hierarchy has a known number of levels.

Example:

```text
Department
    ↓
Category
    ↓
Product
```

The dimension can simply contain columns for each level:

|Product_Key|Product|Category|Department|
|--:|---|---|---|
|101|Laptop A|Computers|Electronics|
|102|Laptop B|Computers|Electronics|
|103|Mouse A|Accessories|Electronics|
|104|Shirt A|Clothing|Fashion|

The hierarchy is represented by ordinary columns.

### Query

Sales by department:

```sql
SELECT
    p.Department,
    SUM(f.Sales_Amount) AS Sales
FROM Fact_Sales f
JOIN Dim_Product p
    ON f.Product_Key = p.Product_Key
GROUP BY p.Department;
```

Sales by category:

```sql
GROUP BY p.Department, p.Category
```

Sales by product:

```sql
GROUP BY p.Department, p.Category, p.Product
```

This is the **simplest hierarchy design**.

---

# 3. Hierarchy depth

**Depth** means the number of levels from the top to the bottom.

Example:

```text
Company
   ↓
Department
   ↓
Category
   ↓
Product
```

Depth = 4 levels.

A hierarchy is **fixed depth** when every branch follows the same number of levels.

Example:

```text
Electronics
    ↓
Computers
    ↓
Laptop
    ↓
Dell XPS
```

and:

```text
Clothing
    ↓
Shirts
    ↓
T-Shirts
    ↓
Nike T-Shirt
```

Both have four levels.

---

# 4. Ragged / variable-depth hierarchy

A **ragged hierarchy** has branches with different numbers of levels.

Example: organizational hierarchy.

```text
CEO
├── VP Sales
│   ├── Sales Manager
│   │   ├── Ravi
│   │   └── Arun
│   └── Priya
│
└── VP Engineering
    └── John
```

Consider Ravi:

```text
CEO
 ↓
VP Sales
 ↓
Sales Manager
 ↓
Ravi
```

Four levels.

But Priya:

```text
CEO
 ↓
VP Sales
 ↓
Priya
```

Only three levels.

So the hierarchy has **variable depth**.

---

# 5. Why ragged hierarchies are difficult

With a fixed hierarchy, you can create columns:

```text
Level 1
Level 2
Level 3
Level 4
```

But with a ragged hierarchy, you don't know how many levels will exist.

For example:

```text
CEO
 ↓
VP
 ↓
Director
 ↓
Manager
 ↓
Team Lead
 ↓
Employee
```

Another branch might be:

```text
CEO
 ↓
VP
 ↓
Employee
```

You cannot easily represent an arbitrary number of levels using fixed columns.

This is where the specialized methods come in.

---

# 6. Method 1: Parent-child relationship

A common way to store a hierarchy is:

```text
Employee_Key
Employee_Name
Parent_Employee_Key
```

Example:

|Employee_Key|Employee|Parent_Key|
|--:|---|--:|
|1|CEO|NULL|
|2|VP Sales|1|
|3|Sales Manager|2|
|4|Ravi|3|
|5|Arun|3|
|6|Priya|2|
|7|VP Engineering|1|
|8|John|7|

This says:

```text
Ravi → Sales Manager
Sales Manager → VP Sales
VP Sales → CEO
```

The advantage is that the hierarchy can have arbitrary depth.

The problem is querying all ancestors/descendants usually requires **recursive logic**.

---

# 7. Method 2: Hierarchy Bridge Table

Kimball's major solution for ragged hierarchies is a **hierarchy bridge table**.

Instead of only storing:

```text
Ravi → Sales Manager
```

the bridge stores every ancestor relationship.

### `Employee_Hierarchy_Bridge`

|Descendant|Ancestor|Distance|
|---|---|--:|
|Ravi|Ravi|0|
|Ravi|Sales Manager|1|
|Ravi|VP Sales|2|
|Ravi|CEO|3|
|Arun|Arun|0|
|Arun|Sales Manager|1|
|Arun|VP Sales|2|
|Arun|CEO|3|
|Priya|Priya|0|
|Priya|VP Sales|1|
|Priya|CEO|2|

Now you can ask:

> Who is above Ravi?

The answer is directly represented:

```text
Ravi
Sales Manager
VP Sales
CEO
```

No recursive traversal is required.

---

# 8. Why is it called a bridge?

Because it sits between the dimension and the hierarchy relationships.

Conceptually:

```text
Dim_Employee
     |
     | Employee_Key
     ↓
Hierarchy_Bridge
     |
     ├── Descendant
     ├── Ancestor
     └── Distance
```

The bridge represents the **many-to-many relationship between descendants and ancestors**.

---

# 9. What does Distance mean?

`Distance` tells you how far the ancestor is from the descendant.

For Ravi:

|Descendant|Ancestor|Distance|
|---|---|--:|
|Ravi|Ravi|0|
|Ravi|Sales Manager|1|
|Ravi|VP Sales|2|
|Ravi|CEO|3|

Therefore:

```text
Distance = 0 → itself
Distance = 1 → immediate parent
Distance = 2 → parent's parent
Distance = 3 → three levels above
```

This is extremely useful for hierarchy analysis.

---

# 10. Method 3: Pathstring

The second solution from Kimball is a **pathstring**.

Instead of a bridge table, store the complete hierarchy path in the dimension.

For example:

|Employee|Pathstring|
|---|---|
|CEO|`/CEO`|
|VP Sales|`/CEO/VP_Sales`|
|Sales Manager|`/CEO/VP_Sales/Sales_Manager`|
|Ravi|`/CEO/VP_Sales/Sales_Manager/Ravi`|
|Arun|`/CEO/VP_Sales/Sales_Manager/Arun`|
|Priya|`/CEO/VP_Sales/Priya`|

For Ravi:

```text
/CEO/VP_Sales/Sales_Manager/Ravi
```

contains the entire path.

---

# 11. Querying the pathstring

Suppose you want everyone below VP Sales.

You can search for paths beginning with:

```text
/CEO/VP_Sales/
```

You find:

```text
/CEO/VP_Sales/Sales_Manager/Ravi
/CEO/VP_Sales/Sales_Manager/Arun
/CEO/VP_Sales/Priya
```

Thus, the pathstring allows hierarchy traversal using ordinary string operations.

---

# 12. Bridge vs Pathstring

This is one of the most important comparisons.

|Feature|Bridge|Pathstring|
|---|---|---|
|Separate table|Yes|No|
|Hierarchy stored in dimension|No|Yes|
|Handles variable depth|Excellent|Good|
|Alternative hierarchies|Good|Limited|
|Shared ownership|Good|Limited|
|Time-varying hierarchy|Good|Difficult|
|Easy basic implementation|Moderate|Easier|
|Handles structural changes|Better|Can require path changes|
|Standard SQL|Yes|Yes|

### Mental model

**Bridge:**

> "Store all relationships."

**Pathstring:**

> "Store the entire path."

---

# 13. Alternative hierarchies

An **alternative hierarchy** means the same entities can be organized in different ways.

Example: employees.

### Management hierarchy

```text
CEO
 ↓
VP Sales
 ↓
Sales Manager
 ↓
Ravi
```

### Geographic hierarchy

```text
India
 ↓
Chennai
 ↓
Ravi
```

Ravi belongs to both hierarchies.

A bridge table can represent both:

|Hierarchy|Descendant|Ancestor|
|---|---|---|
|Management|Ravi|Sales Manager|
|Management|Ravi|VP Sales|
|Management|Ravi|CEO|
|Geography|Ravi|Chennai|
|Geography|Ravi|India|

This is one reason bridge tables are more flexible.

---

# 14. Shared ownership hierarchy

This is another important case.

Normally, a person has one parent:

```text
Manager
   ↓
Employee
```

But suppose an employee works for two managers:

```text
Manager A
    ↘
     Employee
    ↗
Manager B
```

This is **shared ownership**.

A simple `Parent_Key` column cannot naturally represent multiple parents.

A bridge can:

|Descendant|Ancestor|
|---|---|
|Employee A|Manager A|
|Employee A|Manager B|

Therefore, the bridge supports many-to-many hierarchy relationships.

---

# 15. Time-varying hierarchy

The hierarchy can also change over time.

January:

```text
CEO
 ↓
Manager A
 ↓
Ravi
```

July:

```text
CEO
 ↓
Manager B
 ↓
Ravi
```

A bridge can include dates:

|Descendant|Ancestor|Effective_From|Effective_To|
|---|---|---|---|
|Ravi|Manager A|Jan 1|Jun 30|
|Ravi|Manager B|Jul 1|Current|

Now you can answer:

> "Who did Ravi report to in March?"

Answer:

```text
Manager A
```

And:

> "Who does Ravi report to now?"

Answer:

```text
Manager B
```

---

# 16. Hierarchy and fact tables

Suppose you have:

```text
Fact_Sales
-----------
Employee_Key
Sales_Amount
```

and:

```text
Dim_Employee
```

with an organizational hierarchy.

The business might ask:

> "How much sales did everyone under VP Sales generate?"

The bridge lets you identify all employees below VP Sales.

```text
VP Sales
├── Sales Manager
│   ├── Ravi
│   └── Arun
└── Priya
```

Then you aggregate their fact rows:

```text
Ravi       ₹100K
Arun       ₹150K
Priya      ₹200K
----------------
VP Sales   ₹450K
```

The hierarchy determines **which fact rows belong to the selected node**.

---

# 17. Fixed hierarchy vs ragged hierarchy

||Fixed-depth|Ragged/variable-depth|
|---|---|---|
|Number of levels|Known|Variable|
|Example|Year → Quarter → Month → Day|Organization|
|Storage|Regular dimension columns|Parent-child / bridge / pathstring|
|Query complexity|Low|Higher|
|Special structure needed|Usually no|Often yes|

---

# 18. Don't confuse hierarchy with drill-down

These are related but different.

### Hierarchy

Defines the structure:

```text
Year
 ↓
Quarter
 ↓
Month
 ↓
Day
```

### Drill-down

Is the user's analysis action:

```text
Sales by Year
       ↓
Sales by Year + Quarter
       ↓
Sales by Year + Quarter + Month
```

A hierarchy can help organize drill-down, but **drill-down does not require a predefined hierarchy**.

You can drill from:

```text
Year
```

to:

```text
Year + Product
```

even though Product isn't necessarily the next level of a formal hierarchy.

---
# 20. The overall architecture

You can now put the concepts together:

```text
                 DIMENSION
                     |
          ┌──────────┴──────────┐
          ↓                     ↓
     Fixed hierarchy       Ragged hierarchy
          |                     |
    Normal columns       Special modeling
                                |
                    ┌───────────┴───────────┐
                    ↓                       ↓
              Bridge Table             Pathstring
                    |
          ┌─────────┼─────────┐
          ↓         ↓         ↓
     Alternative  Shared   Time-varying
     hierarchy   ownership  hierarchy
```

---

# 21. Which method should you remember?

### Fixed-depth hierarchy

Use normal dimension columns.

```text
Department
Category
Product
```

### Ragged hierarchy

Consider:

```text
Parent-child
```

if the database/BI technology supports it adequately.

For a Kimball dimensional warehouse requiring flexible relational querying:

```text
Hierarchy Bridge
```

is the more powerful approach.

### Simpler ragged hierarchy

Use:

```text
Pathstring
```

when the hierarchy is relatively stable and you don't need sophisticated alternative/shared/time-varying structures.

---

# 22. Final summary

|Concept|Meaning|
|---|---|
|Dimension hierarchy|Relationships between levels of a dimension|
|Fixed-depth hierarchy|Same number of levels in every branch|
|Ragged hierarchy|Different branches have different depths|
|Parent-child|Each member points to its immediate parent|
|Hierarchy bridge|Stores every ancestor-descendant path|
|Pathstring|Stores the complete path as text|
|Alternative hierarchy|Same entities organized in different ways|
|Shared ownership|One entity can have multiple parents|
|Time-varying hierarchy|Parent/child relationships change over time|
|Drill-down|Query becomes more detailed|
|Shrunken dimension|Reduced/conformed dimension for another fact grain|

### The three diagrams to remember

**Fixed hierarchy:**

```text
Department
    ↓
Category
    ↓
Product
```

**Ragged hierarchy + bridge:**

```text
CEO
├── VP
│   ├── Manager
│   │   └── Employee
│   └── Employee
└── VP
    └── Employee

        ↓

Hierarchy_Bridge
Descendant | Ancestor | Distance
```

**Ragged hierarchy + pathstring:**

```text
Employee
   ↓
/CEO/VP/Manager/Employee
```

The fundamental choice is therefore:

> **Fixed and predictable hierarchy → ordinary dimension attributes.**

> **Variable-depth hierarchy → parent-child, hierarchy bridge, or pathstring depending on requirements.**

> **Need maximum flexibility for alternative, shared, and time-varying hierarchies → hierarchy bridge is generally the stronger relational design.**
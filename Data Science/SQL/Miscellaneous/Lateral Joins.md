

Absolutely, Jack. Let’s strip it down to just what **`LATERAL`** _really_ means — no fluff, just raw understanding.

---

# 💡 **`LATERAL` in SQL (PostgreSQL)**

## 🔹 1. What is it?

`LATERAL` allows a **subquery in the `FROM` clause** to **refer to columns from the table before it**.

👉 It’s like saying:

> _“For each row in the outer table, run this subquery using that row's values.”_

---

## 🔹 2. Basic Syntax

```sql
SELECT ...
FROM outer_table
JOIN LATERAL (
    SELECT ...
    WHERE sub.col = outer_table.col
) sub_alias ON true;
```

- You must **alias** the subquery.
    
- `ON true` is used when the filter is already inside the subquery.
    

---

## 🔹 3. Why use `LATERAL`?

Because **without `LATERAL`**, this would **fail**:

```sql
FROM customers c,
(
    SELECT * FROM orders WHERE orders.customer_id = c.id
) o
-- ❌ ERROR: c.id not recognized
```

✅ With `LATERAL`, it works:

```sql
FROM customers c,
LATERAL (
    SELECT * FROM orders WHERE orders.customer_id = c.id
) o
```

---

## 🔹 4. Key Rules

|Rule|Explanation|
|---|---|
|Must alias the subquery|Required in SQL|
|Must use `ON true`|Unless you add `JOIN` conditions|
|Evaluated **per row**|Subquery is re-run for each row|
|Needs `LATERAL` to access outer columns|No outer access without it|

---

## 🔹 5. When to Use

- Subquery needs outer table’s values
    
- You use `LIMIT`, `ORDER BY` inside subquery
    
- You want **row-wise filtering** inside `FROM`
    

---

## 🔹 6. Micro Example

```sql
SELECT c.id, o.id
FROM customers c
JOIN LATERAL (
  SELECT *
  FROM orders o
  WHERE o.customer_id = c.id
  ORDER BY o.created_at DESC
  LIMIT 1
) o ON true;
```

✅ This gets each customer's **latest order**. Impossible without `LATERAL`.

---

## 🏁 TL;DR

> `LATERAL` = **subquery in FROM** that can **see outer table's columns**  
> It runs **once per row** of the outer query.  
> It's essential for **top-N per group**, **unnesting**, and **dynamic filtering**.

---

Let me know if you want a one-liner definition to memorize for interviews!

## 🔗 Related Notes
- [[Data Science/SQL/SQL SubQueries/SQL SubQueries|Comprehensive Guide to SQL Subqueries]]
- [[Data Science/SQL/Window Functions/SQL Window Function - 2|Comprehensive Guide to SQL Window Functions]]

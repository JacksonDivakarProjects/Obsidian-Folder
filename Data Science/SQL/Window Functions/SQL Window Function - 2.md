
Of course. Here is a comprehensive and detailed guide to SQL Window Functions, extracted and refined from the provided content.

***

# Comprehensive Guide to SQL Window Functions

## Introduction

SQL window functions are a powerful class of functions that perform calculations across a set of table rows that are somehow related to the current row. Unlike standard aggregate functions (e.g., `SUM`, `AVG`, `COUNT`), which collapse multiple rows into a single summary row, window functions **return a value for every input row**. The "window" is the set of rows over which the function operates for each individual row.

They are essential for complex analytical and reporting queries, enabling tasks like running totals, moving averages, rankings, and comparing row values to aggregate values without using cumbersome self-joins or subqueries.

## Prerequisites: The Example Table

All examples in this guide will use a sample table named `product` with the following structure and sample data:

| product_category | brand       | product_name        | price |
| :--------------- | :---------- | :------------------ | :---- |
| phone            | Apple       | iPhone 13 Pro       | 1200  |
| phone            | Samsung     | Galaxy Z Fold 3     | 1800  |
| phone            | OnePlus     | OnePlus 9 Pro       | 900   |
| laptop           | Apple       | MacBook Pro 16"     | 2400  |
| laptop           | Dell        | XPS 17              | 2200  |
| laptop           | HP          | Spectre x360        | 1300  |
| earphone         | Apple       | Airpods Pro         | 280   |
| earphone         | Sony        | WF-1000XM4          | 250   |
| earphone         | Samsung     | Galaxy Buds Live    | 150   |
| ...              | ...         | ...                 | ...   |

## Core Concepts: The `OVER()` Clause

The `OVER()` clause is what defines a function as a window function. It specifies how to partition and order the dataset for the function's calculation.

**Basic Syntax:**
```sql
<WINDOW_FUNCTION>() OVER (
    [PARTITION BY <column(s)>]
    [ORDER BY <column(s)> [ASC|DESC]]
    [<FRAME_CLAUSE>]
) AS column_alias
```

*   **`PARTITION BY`**: Divides the result set into partitions (groups or windows) based on one or more columns. The window function is applied separately to each partition. If omitted, the entire table is treated as a single partition.
*   **`ORDER BY`**: Defines the logical order of rows within each partition. This is crucial for functions that depend on sequence, like `FIRST_VALUE` or `NTILE`. For aggregate window functions (e.g., `SUM(price)`), it creates a **running total**.
*   **Frame Clause (`ROWS`/`RANGE`)**: A further subset of a partition. It defines which rows surrounding the current row are included in the calculation. This is explained in detail later.

---

## 1. The `FIRST_VALUE` Function

The `FIRST_VALUE` function returns the value from the **first row** in the specified window frame.

### Use Case: Display the most expensive product in each category on every row.

```sql
SELECT
    *,
    FIRST_VALUE(product_name) OVER (
        PARTITION BY product_category
        ORDER BY price DESC
    ) AS most_expensive_product
FROM product;
```

**Explanation:**
1.  `PARTITION BY product_category`: Creates a separate window for each product category (e.g., all phones together, all laptops together).
2.  `ORDER BY price DESC`: Sorts the rows *within each partition* by price in descending order. The first row in each sorted partition will be the most expensive product.
3.  `FIRST_VALUE(product_name)`: For every row in the partition, it returns the `product_name` from that first (most expensive) row.

**Result Snippet:**
| product_category | product_name        | price | most_expensive_product |
| :--------------- | :------------------ | ----: | :--------------------- |
| earphone         | Airpods Pro         |   280 | **Airpods Pro**        |
| earphone         | WF-1000XM4          |   250 | **Airpods Pro**        |
| earphone         | Galaxy Buds Live    |   150 | **Airpods Pro**        |
| phone            | Galaxy Z Fold 3     |  1800 | **Galaxy Z Fold 3**    |
| phone            | iPhone 13 Pro       |  1200 | **Galaxy Z Fold 3**    |

---

## 2. The `LAST_VALUE` Function and The Critical FRAME CLAUSE

The `LAST_VALUE` function returns the value from the **last row** in the specified window frame. Its behavior is often misunderstood due to the default frame clause.

### The Problem: Naive Usage Gives Unexpected Results

```sql
-- This query will NOT work as intended!
SELECT
    *,
    LAST_VALUE(product_name) OVER (
        PARTITION BY product_category
        ORDER BY price DESC
    ) AS least_expensive_product
FROM product;
```

This query will not correctly show the cheapest product. It will often show the current row's product name instead. This is because of the **default frame clause**.

### What is a Frame Clause?

A frame is a **subset of the current partition**. The frame clause defines the boundaries of this subset relative to the current row. The default frame is:
`RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`

*   `UNBOUNDED PRECEDING`: The start of the partition.
*   `CURRENT ROW`: The current row being processed.
This means the window for the function only includes rows from the start of the partition up to the current row. For `LAST_VALUE`, this means it returns the value from the current row, not the true last row of the partition.

### The Solution: Correcting `LAST_VALUE` with an Explicit Frame

To make `LAST_VALUE` see the entire partition, we must change the frame.

```sql
SELECT
    *,
    LAST_VALUE(product_name) OVER (
        PARTITION BY product_category
        ORDER BY price DESC
        RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS least_expensive_product
FROM product;
```

**Explanation:**
*   `RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`: This frame clause expands the window to include **every row in the partition**, from the very first to the very last. Now, `LAST_VALUE` will correctly return the value from the final row in the sorted partition (the cheapest product).

**`ROWS` vs. `RANGE`:**
*   `ROWS`: Defines the frame by a physical count of rows (e.g., `ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING`).
*   `RANGE`: Defines the frame by logical value ranges in the `ORDER BY` column. If the current row's `price` is 100, `RANGE BETWEEN 50 PRECEDING AND 50 FOLLOWING` would include all rows with a price between 50 and 150. This is important when there are duplicate values in the `ORDER BY` column.

---

## 3. The `NTH_VALUE` Function

The `NTH_VALUE` function is a generalization of `FIRST_VALUE` and `LAST_VALUE`. It returns the value from the **N-th row** in the window frame.

### Use Case: Find the second most expensive product in each category.

```sql
SELECT
    *,
    NTH_VALUE(product_name, 2) OVER (
        PARTITION BY product_category
        ORDER BY price DESC
        RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS second_most_expensive_product
FROM product;
```

**Explanation:**
*   `NTH_VALUE(product_name, 2)`: The first argument is the column name, and the second argument (`2`) is the position to fetch.
*   Just like `LAST_VALUE`, it requires the `UNBOUNDED FOLLOWING` frame clause to see the entire partition and correctly identify the 2nd row. Without it, the result would be incorrect or `NULL` for many rows.
*   If a partition has fewer than `N` rows, the function returns `NULL` for that partition.

---

## 4. The `NTILE` Function

The `NTILE` function divides the rows in a partition into a specified number of **roughly equal groups** (buckets or tiles). It assigns each row a bucket number.

### Use Case: Segment all phones into three price tiers: Expensive, Mid-Range, and Budget.

```sql
SELECT
    product_name,
    price,
    NTILE(3) OVER (ORDER BY price DESC) AS price_bucket
FROM product
WHERE product_category = 'phone';
```

To make the output more readable, we can use it in a subquery:

```sql
SELECT
    product_name,
    price,
    CASE
        WHEN price_bucket = 1 THEN 'Expensive'
        WHEN price_bucket = 2 THEN 'Mid-Range'
        WHEN price_bucket = 3 THEN 'Budget'
    END AS price_tier
FROM (
    SELECT
        product_name,
        price,
        NTILE(3) OVER (ORDER BY price DESC) AS price_bucket
    FROM product
    WHERE product_category = 'phone'
) x;
```

**Explanation:**
*   `NTILE(3)`: Specifies the number of buckets to create.
*   `ORDER BY price DESC`: The rows are sorted by price before being distributed into buckets. The most expensive phones will be in bucket 1.
*   If the number of rows is not perfectly divisible by the number of buckets, the first buckets will contain one more row than the later buckets. (e.g., 5 rows into 3 buckets: Bucket 1 has 2 rows, Buckets 2 and 3 have 1 row each).

---

## 5. The `CUME_DIST` Function (Cumulative Distribution)

`CUME_DIST()` calculates the **cumulative distribution** of a value within a set of values. It represents the proportion of rows with values less than or equal to the current row's value.
**Formula:** `CUME_DIST() = (Number of rows with value <= current value) / (Total rows in partition)`
The result is a value between 0 and 1.

### Use Case: Find all products that are in the top 30% most expensive products.

```sql
SELECT
    product_name,
    price,
    ROUND(CAST(cume_dist AS numeric), 2) AS cume_dist
FROM (
    SELECT
        *,
        CUME_DIST() OVER (ORDER BY price DESC) AS cume_dist
    FROM product
) x
WHERE x.cume_dist <= 0.30;
```

**Explanation:**
*   `CUME_DIST() OVER (ORDER BY price DESC)`: Sorts all products by price descending and calculates the cumulative distribution.
*   The most expensive product has a `CUME_DIST` of ~0.03 (1 / total_rows). The cheapest product has a value of 1.0.
*   The outer query filters for rows that fall within the top 30% of the distribution.

---

## 6. The `PERCENT_RANK` Function

`PERCENT_RANK()` calculates the **relative rank** of a row within a partition as a percentage. It shows what percentage of rows have a lower value than the current row.
**Formula:** `PERCENT_RANK() = (Rank of current row - 1) / (Total rows in partition - 1)`
The result is a value between 0 and 1.

### Use Case: See how expensive the "Galaxy Z Fold 3" is compared to all other products.

```sql
SELECT
    product_name,
    price,
    ROUND(CAST(percent_rank AS numeric) * 100, 2) || '%' AS percent_rank
FROM (
    SELECT
        *,
        PERCENT_RANK() OVER (ORDER BY price) AS percent_rank
    FROM product
) x
WHERE product_name = 'Galaxy Z Fold 3';
```

**Explanation:**
*   `PERCENT_RANK() OVER (ORDER BY price)`: Ranks all products by price ascending. The cheapest product has a rank of 0.0, and the most expensive has a rank of 1.0.
*   If 'Galaxy Z Fold 3' has a `PERCENT_RANK` of 0.95, it means it is more expensive than 95% of all products.

**Key Difference from `CUME_DIST`:**
*   `PERCENT_RANK` calculates a percentage based on rank.
*   `CUME_DIST` calculates a percentage based on the number of rows. For datasets with duplicate values, `CUME_DIST` will be the same for all duplicate rows and will be higher than their `PERCENT_RANK`.

---

## 7. Writing Clean Queries: The `WINDOW` Clause

When multiple window functions share the same `OVER()` clause definition, the `WINDOW` clause allows you to define the window once and reuse it, making the query much cleaner and more maintainable.

### Example Without `WINDOW` Clause (Repetitive):
```sql
SELECT
    product_name,
    FIRST_VALUE(product_name) OVER (PARTITION BY category ORDER BY price DESC) AS most_exp,
    LAST_VALUE(product_name) OVER (PARTITION BY category ORDER BY price DESC RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS least_exp,
    NTH_VALUE(product_name, 2) OVER (PARTITION BY category ORDER BY price DESC RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS second_most_exp
FROM product;
```

### Example With `WINDOW` Clause (Clean):
```sql
SELECT
    product_name,
    FIRST_VALUE(product_name) OVER w AS most_exp,
    LAST_VALUE(product_name) OVER w AS least_exp,
    NTH_VALUE(product_name, 2) OVER w AS second_most_exp
FROM product
WINDOW w AS (
    PARTITION BY product_category
    ORDER BY price DESC
    RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
);
```

**Explanation:**
*   `WINDOW w AS (...)`: This clause, placed after the `FROM` clause, defines a named window specification called `w`.
*   The definition inside the parentheses is a full `OVER()` clause without the function.
*   `OVER w`: Each window function simply references the named window `w`, drastically reducing code repetition.

## Conclusion

SQL window functions are indispensable for advanced data analysis and reporting. Mastering the `OVER()` clause—specifically, the effects of `PARTITION BY`, `ORDER BY`, and the critical **frame clause**—is the key to using them effectively. By understanding the distinct purposes of `FIRST_VALUE`, `LAST_VALUE`, `NTH_VALUE`, `NTILE`, `CUME_DIST`, and `PERCENT_RANK`, and by using the `WINDOW` clause to write clean code, you can solve a wide array of complex querying problems with elegance and performance.
# Comprehensive Guide to SQL Window Functions

## Introduction

SQL window functions perform calculations across a set of rows related to the current row. Unlike standard aggregate functions (`SUM`, `AVG`, `COUNT`), which collapse multiple rows into a single summary row, window functions return a value for **every** input row. The "window" is the set of rows the function operates over for each individual row.

They're essential for analytical and reporting queries — running totals, moving averages, rankings, and comparing a row's value to an aggregate — without resorting to self-joins or correlated subqueries.

## Example Table

All examples use a sample table `product`:

| product_category | brand | product_name | price |
|---|---|---|---|
| phone | Apple | iPhone 13 Pro | 1200 |
| phone | Samsung | Galaxy Z Fold 3 | 1800 |
| phone | OnePlus | OnePlus 9 Pro | 900 |
| laptop | Apple | MacBook Pro 16" | 2400 |
| laptop | Dell | XPS 17 | 2200 |
| laptop | HP | Spectre x360 | 1300 |
| earphone | Apple | Airpods Pro | 280 |
| earphone | Sony | WF-1000XM4 | 250 |
| earphone | Samsung | Galaxy Buds Live | 150 |

## Core Concept: The `OVER()` Clause

The `OVER()` clause is what turns a function into a window function — it specifies how to partition and order the dataset for the calculation.

```sql
<WINDOW_FUNCTION>() OVER (
    [PARTITION BY <column(s)>]
    [ORDER BY <column(s)> [ASC|DESC]]
    [<FRAME_CLAUSE>]
) AS column_alias
```

- **`PARTITION BY`** — splits the result set into groups; the window function runs separately within each group. Omit it and the whole table is one partition.
- **`ORDER BY`** — defines row order within each partition. Crucial for sequence-dependent functions like `FIRST_VALUE`/`NTILE`, and for aggregate window functions (`SUM(price)` with an `ORDER BY` becomes a running total instead of a partition-wide total).
- **Frame clause (`ROWS`/`RANGE`)** — a further subset of the partition, relative to the current row. Covered below — it's the part people get wrong most often.

## 1. `FIRST_VALUE`

Returns the value from the first row of the window frame.

**Use case:** show the most expensive product in each category, on every row of that category.

```sql
SELECT
    *,
    FIRST_VALUE(product_name) OVER (
        PARTITION BY product_category
        ORDER BY price DESC
    ) AS most_expensive_product
FROM product;
```

`PARTITION BY product_category` creates one window per category; `ORDER BY price DESC` sorts each partition so the first row is the priciest; `FIRST_VALUE(product_name)` returns that row's name to every row in the partition.

| product_category | product_name | price | most_expensive_product |
|---|---|---|---|
| earphone | Airpods Pro | 280 | Airpods Pro |
| earphone | WF-1000XM4 | 250 | Airpods Pro |
| earphone | Galaxy Buds Live | 150 | Airpods Pro |
| phone | Galaxy Z Fold 3 | 1800 | Galaxy Z Fold 3 |
| phone | iPhone 13 Pro | 1200 | Galaxy Z Fold 3 |

## 2. `LAST_VALUE` and the Frame Clause

`LAST_VALUE` returns the value from the last row of the window frame — but its default behavior surprises almost everyone the first time.

**The trap:**
```sql
-- Does NOT work as intended!
SELECT
    *,
    LAST_VALUE(product_name) OVER (
        PARTITION BY product_category
        ORDER BY price DESC
    ) AS least_expensive_product
FROM product;
```
This doesn't return the cheapest product — it typically returns the *current row's* product name. The cause is the **default frame**: `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`. That frame only spans from the start of the partition up to the current row, so from the current row's own point of view, the current row *is* the last row in its frame.

**The fix — widen the frame explicitly:**
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
`RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` expands the frame to the entire partition, so `LAST_VALUE` now correctly returns the value from the true last (cheapest) row.

**`ROWS` vs. `RANGE`:**
- `ROWS` defines the frame by a physical row count (e.g., `ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING`).
- `RANGE` defines the frame by logical value distance in the `ORDER BY` column — e.g., if the current row's `price` is 100, `RANGE BETWEEN 50 PRECEDING AND 50 FOLLOWING` includes every row with a price between 50 and 150. This matters especially when the `ORDER BY` column has duplicate values, since `ROWS` and `RANGE` can then include different sets of rows.

## 3. `NTH_VALUE`

A generalization of `FIRST_VALUE`/`LAST_VALUE` — returns the value from the Nth row of the frame.

**Use case:** the second most expensive product per category.

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

The first argument is the column, the second is the target position. Like `LAST_VALUE`, it needs the widened frame to see the whole partition — otherwise the default frame can make it return `NULL` for rows where the Nth row hasn't been reached yet. If a partition has fewer than N rows, the function returns `NULL` for that partition.

## 4. `NTILE`

Splits the rows of a partition into a specified number of roughly equal buckets, and assigns each row its bucket number.

**Use case:** split phones into three price tiers.

```sql
SELECT
    product_name,
    price,
    NTILE(3) OVER (ORDER BY price DESC) AS price_bucket
FROM product
WHERE product_category = 'phone';
```

Turn the bucket numbers into labels via a subquery:
```sql
SELECT
    product_name,
    price,
    CASE price_bucket
        WHEN 1 THEN 'Expensive'
        WHEN 2 THEN 'Mid-Range'
        WHEN 3 THEN 'Budget'
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

Rows are sorted by the `ORDER BY` before being distributed into buckets, so bucket 1 gets the most expensive phones. If the row count doesn't divide evenly by the bucket count, the earlier buckets absorb the extra row(s) — e.g., 5 rows into 3 buckets gives bucket 1 two rows, buckets 2 and 3 one row each.

## 5. `CUME_DIST` (Cumulative Distribution)

Returns the proportion of rows with a value less than or equal to the current row's value, within the partition:

`CUME_DIST() = (rows with value <= current value) / (total rows in partition)`

Result is between 0 and 1 (exclusive of 0, inclusive of 1).

**Use case:** find products in the top 30% by price.

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

Sorted by price descending, the most expensive product has a `CUME_DIST` near `1/total_rows`, and the cheapest has exactly `1.0`. The outer query keeps rows within the top 30% of that distribution.

## 6. `PERCENT_RANK`

Returns the relative rank of a row within a partition, as a fraction:

`PERCENT_RANK() = (rank of current row - 1) / (total rows in partition - 1)`

Result is between 0 and 1.

**Use case:** how does the "Galaxy Z Fold 3" compare to every other product?

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

Ranked by price ascending, the cheapest product scores `0.0` and the most expensive scores `1.0`. A `PERCENT_RANK` of `0.95` for a given product means it's pricier than 95% of the catalog.

**vs. `CUME_DIST`:** `PERCENT_RANK` is based on rank position; `CUME_DIST` is based on row counts. With duplicate values in the `ORDER BY` column, every tied row gets the same `CUME_DIST` (and it will read higher than their shared `PERCENT_RANK`), since `CUME_DIST` counts all rows up to and including ties, while `PERCENT_RANK` is anchored to rank.

## 7. Writing Clean Queries: The `WINDOW` Clause

When several window functions share the same `OVER()` definition, name it once with a `WINDOW` clause instead of repeating it.

**Without `WINDOW` (repetitive):**
```sql
SELECT
    product_name,
    FIRST_VALUE(product_name) OVER (PARTITION BY category ORDER BY price DESC) AS most_exp,
    LAST_VALUE(product_name) OVER (PARTITION BY category ORDER BY price DESC RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS least_exp,
    NTH_VALUE(product_name, 2) OVER (PARTITION BY category ORDER BY price DESC RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS second_most_exp
FROM product;
```

**With `WINDOW` (clean):**
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

`WINDOW w AS (...)`, placed after `FROM`, defines a named window specification. Each function then just references it via `OVER w`, cutting the repetition entirely.

Support note: the `WINDOW` clause works in PostgreSQL, MySQL 8+, MariaDB, SQLite, and Snowflake — not in standard SQL Server T-SQL, which requires repeating the full `OVER(...)` clause per function (or moving the logic into a CTE).

## Conclusion

Mastering the `OVER()` clause — `PARTITION BY`, `ORDER BY`, and especially the frame clause — is the key to using window functions correctly. `FIRST_VALUE`, `LAST_VALUE`, `NTH_VALUE`, `NTILE`, `CUME_DIST`, and `PERCENT_RANK` each solve a different analytical shape, and the `WINDOW` clause keeps queries that lean on several of them readable.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/Window Functions/SQL Window Functions and Aggregate Examples|SQL Window Functions and Aggregate Examples]]
- [[Data Engineering Role Notes/SQL/Tricks and Tips/Group By and Having Tricks|Group By and Having Tricks]]

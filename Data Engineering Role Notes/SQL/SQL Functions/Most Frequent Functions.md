# Most Frequent MySQL Functions

Cheat sheet of commonly used MySQL functions: type casting, string manipulation, numeric operations, aggregates, conditional logic, NULL-safe handling, and JSON. Date/time functions are covered separately in [[Data Engineering Role Notes/SQL/SQL Functions/MySQL Date Functions Cheat sheet|MySQL Date Functions Cheat sheet]]. Compatible with MySQL 5.7+ and 8.x.

## 1. Type Casting

| Function | Description | Example |
|---|---|---|
| `CAST(expr AS TYPE)` | Convert to a specified data type | `CAST('123' AS UNSIGNED)` → `123` |
| `CONVERT(expr, TYPE)` | Same as `CAST()` | `CONVERT('202', DECIMAL)` |
| `BINARY` | Force byte-wise (case-sensitive) comparison | `SELECT BINARY 'abc' = 'ABC'` → `false` |

## 2. String Functions

| Function | Description | Example |
|---|---|---|
| `CONCAT(a, b, ...)` | Combine strings | `CONCAT('A', '-', 'B')` → `'A-B'` |
| `CONCAT_WS(sep, ...)` | Join with a separator | `CONCAT_WS('-', '2025', '08', '05')` → `'2025-08-05'` |
| `UPPER(str)` / `LOWER(str)` | Case conversion | `'hello'` → `'HELLO'` |
| `SUBSTRING(str, start, len)` | Extract part of a string | `SUBSTRING('abcdef', 2, 3)` → `'bcd'` |
| `LEFT(str, n)` / `RIGHT(str, n)` | First/last `n` characters | `LEFT('abcde', 2)` → `'ab'` |
| `TRIM(str)` | Remove leading/trailing spaces | `' hello '` → `'hello'` |
| `REPLACE(str, from, to)` | Replace text | `REPLACE('cat', 'c', 'b')` → `'bat'` |
| `INSTR(str, sub)` | Position of a substring | `INSTR('apple', 'p')` → `2` |
| `LENGTH(str)` | Byte length | `'abc'` → `3` |
| `CHAR_LENGTH(str)` | Character length (multi-byte-safe) | `'ñ'` → `1` |

## 3. Numeric Functions

| Function | Description | Example |
|---|---|---|
| `ROUND(num, d)` | Round to `d` decimals | `ROUND(3.14159, 2)` → `3.14` |
| `TRUNCATE(num, d)` | Truncate without rounding | `TRUNCATE(3.14159, 2)` → `3.14` |
| `FLOOR(num)` / `CEIL(num)` | Round down / up | `FLOOR(2.9)` → `2` |
| `MOD(a, b)` or `a % b` | Modulo | `MOD(10, 3)` → `1` |
| `ABS(num)` | Absolute value | `ABS(-5)` → `5` |
| `SIGN(num)` | Sign of number | `SIGN(-10)` → `-1` |
| `POWER(x, y)` or `POW(x, y)` | Exponentiation | `POW(2, 3)` → `8` |
| `SQRT(num)` | Square root | `SQRT(16)` → `4` |
| `RAND()` | Random decimal between 0 and 1 | `RAND()` → `0.729...` |
| `FORMAT(num, d)` | Format with thousands separators | `FORMAT(12345.678, 2)` → `'12,345.68'` |

## 4. Aggregate Functions

| Function | Description | Example |
|---|---|---|
| `COUNT(*)` | Count all rows | `COUNT(*)` |
| `COUNT(col)` | Count non-null values | `COUNT(email)` |
| `SUM(col)` | Total | `SUM(salary)` |
| `AVG(col)` | Average | `AVG(price)` |
| `MIN(col)` / `MAX(col)` | Min/max | `MAX(score)` |

Usable with `GROUP BY`, `HAVING`, and `DISTINCT`.

## 5. Conditional Functions

| Function | Description | Example |
|---|---|---|
| `IF(condition, true, false)` | Inline if/else | `IF(score > 50, 'Pass', 'Fail')` |
| `IFNULL(expr, alt)` | Replace NULL with a fallback | `IFNULL(name, 'N/A')` |
| `NULLIF(a, b)` | Returns NULL if `a = b`, else `a` | `NULLIF(10, 10)` → `NULL` |
| `CASE WHEN ...` | Multi-condition branching | see below |

```sql
SELECT
  CASE
    WHEN score >= 90 THEN 'A'
    WHEN score >= 80 THEN 'B'
    ELSE 'F'
  END AS grade
FROM students;
```

## 6. NULL-Safe Functions

| Function | Description | Example |
|---|---|---|
| `IFNULL(expr, alt)` | Replace NULL | `IFNULL(name, 'Unknown')` |
| `COALESCE(a, b, c, ...)` | First non-null argument | `COALESCE(NULL, NULL, 'X')` → `'X'` |
| `<=>` (NULL-safe equality) | Equality that also handles `NULL <=> NULL` → `true` | `a <=> b` |

## 7. JSON Functions (MySQL 5.7+)

| Function | Description | Example |
|---|---|---|
| `JSON_OBJECT(k1, v1, ...)` | Build a JSON object | `JSON_OBJECT('id', 1, 'name', 'Jack')` |
| `JSON_EXTRACT(json, path)` | Get a value at a JSON path | `JSON_EXTRACT(data, '$.name')` |
| `->` / `->>` | Shortcuts for `JSON_EXTRACT` (`->>` also unquotes the result) | `data->'$.name'` |
| `JSON_ARRAY(...)` | Build a JSON array | `JSON_ARRAY(1, 2, 3)` |
| `JSON_CONTAINS(json, val)` | Check whether a value exists | `JSON_CONTAINS('[1,2,3]', '2')` |

## 8. Useful Miscellaneous Functions

| Function | Description | Example |
|---|---|---|
| `UUID()` | Generate a UUID | `UUID()` → `'a9f5b...e0'` |
| `VERSION()` | MySQL server version | `SELECT VERSION()` |
| `DATABASE()` | Current database name | `SELECT DATABASE()` |
| `ROW_NUMBER() OVER (...)` | Ranking (MySQL 8+ window function) | `ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC)` |

## Summary

- Use `CAST`/`CONVERT` for type conversion.
- Use `IFNULL`, `COALESCE`, `CASE` for conditional logic and NULL handling.
- Use `LENGTH`, `SUBSTRING`, `INSTR`, `REPLACE` for string operations.
- Use `ROUND`, `FLOOR`, `FORMAT` for numeric formatting.
- Use the `JSON_...` family and `->`/`->>` for semi-structured data.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL Functions/MySQL Date Functions Cheat sheet|MySQL Date Functions Cheat sheet]]

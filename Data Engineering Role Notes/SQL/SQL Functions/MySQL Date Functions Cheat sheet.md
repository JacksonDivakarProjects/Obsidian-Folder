# MySQL Date Functions Cheat Sheet

## Getting the Current Date & Time

```sql
SELECT CURDATE();            -- Current date (YYYY-MM-DD)
SELECT CURRENT_DATE();       -- Same as CURDATE()
SELECT NOW();                -- Current date & time (YYYY-MM-DD HH:MM:SS)
SELECT CURRENT_TIMESTAMP();  -- Same as NOW()
```

## Extracting Date Parts

```sql
SELECT YEAR('2025-12-12');       -- 2025
SELECT MONTH('2025-12-12');      -- 12
SELECT DAY('2025-12-12');        -- 12
SELECT HOUR('14:30:45');         -- 14
SELECT MINUTE('14:30:45');       -- 30
SELECT SECOND('14:30:45');       -- 45
SELECT DAYNAME('2025-12-12');    -- Friday
SELECT MONTHNAME('2025-12-12');  -- December
```

## Date Arithmetic (Adding & Subtracting)

```sql
SELECT DATE_ADD('2025-12-12', INTERVAL 10 DAY);   -- 2025-12-22
SELECT DATE_SUB('2025-12-12', INTERVAL 1 MONTH);  -- 2025-11-12
SELECT ADDDATE('2025-12-12', INTERVAL 5 YEAR);    -- 2030-12-12
SELECT SUBDATE('2025-12-12', INTERVAL 2 WEEK);    -- 2025-11-28
```

## Date Differences

```sql
SELECT DATEDIFF('2025-12-31', '2025-12-12');                 -- 19 (days)
SELECT TIMESTAMPDIFF(YEAR, '2000-01-01', '2025-12-12');      -- 25 (years)
```

## Formatting Dates & Times

```sql
SELECT DATE_FORMAT(NOW(), '%Y-%m-%d');       -- 2025-12-12
SELECT DATE_FORMAT(NOW(), '%M %d, %Y');      -- December 12, 2025
SELECT DATE_FORMAT(NOW(), '%W, %d %M %Y');   -- Friday, 12 December 2025
```

### Common Formatting Codes

| Code | Meaning | Example |
|---|---|---|
| `%Y` | Year, 4 digits | `2025` |
| `%y` | Year, 2 digits | `25` |
| `%m` | Month, numeric | `01`–`12` |
| `%M` | Month, full name | `March` |
| `%d` | Day, numeric | `01`–`31` |
| `%D` | Day with suffix | `11th` |
| `%H` | Hour, 24-hour format | `00`–`23` |
| `%h` | Hour, 12-hour format | `01`–`12` |
| `%i` | Minutes | `00`–`59` |
| `%s` | Seconds | `00`–`59` |
| `%p` | AM/PM | `AM` or `PM` |

## First & Last Day of Month/Year

```sql
SELECT LAST_DAY(NOW());                                            -- Last day of current month
SELECT DATE_FORMAT(CONCAT(YEAR(NOW()), '-01-01'), '%Y-%m-%d');      -- First day of current year
SELECT DATE_FORMAT(CONCAT(YEAR(NOW()), '-12-31'), '%Y-%m-%d');      -- Last day of current year
```

## Week & Quarter Functions

```sql
SELECT QUARTER('2025-12-12');     -- 4
SELECT WEEK('2025-12-12');        -- 50
SELECT WEEKOFYEAR('2025-12-12');  -- 50
SELECT YEARWEEK('2025-12-12');    -- 202550
```

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/SQL Functions/Most Frequent Functions|Most Frequent Functions]]

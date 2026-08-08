# SQL Tricks — Counting Distinct Days and Grouping Granularity

A few sharp, recurring gotchas around counting unique occurrences and choosing the right `GROUP BY` granularity — the kind of subtlety that shows up in "N distinct days/events" style interview questions.

## 1. `COUNT(customer_id)` vs. `COUNT(DISTINCT ride_date)`

- `COUNT(customer_id)` counts every row — including multiple rides taken on the same day by the same customer.
- `COUNT(DISTINCT ride_date)` counts unique *days*, which is what actually matters for a requirement like "used the service on 30 different days."

Using the plain row count here silently inflates the result whenever a customer takes more than one ride on the same day.

## 2. Grouping Level Determines Result Granularity

```sql
GROUP BY customer_id, customer_name, ride_date
```
This produces one row per customer **per day** — so `COUNT(ride_date)` within each group is always 1, since each group only ever contains a single date. That granularity is too fine if the goal is to count *across* days per customer; `ride_date` needs to come out of the `GROUP BY` and into an aggregate instead.

## 3. Correct Query: "30 Distinct Days"

```sql
SELECT customer_name
FROM uber_rides_morning
WHERE ride_time BETWEEN '06:00:00' AND '09:00:00'
GROUP BY customer_id, customer_name
HAVING COUNT(DISTINCT ride_date) >= 30;
```

This groups only by customer (not by date), then uses `COUNT(DISTINCT ride_date)` to count unique qualifying days. It's functionally equivalent to a CTE-based approach for counting unique (not necessarily consecutive) days — simpler to write, but harder to extend if a later requirement needs *consecutive* days specifically (that needs a gaps-and-islands technique, e.g. via `ROW_NUMBER() - ` a date offset).

## 4. CTEs for Modularity

For anything beyond this simple case — e.g., adding a "consecutive days" requirement — restructuring the query into a CTE pays off: it's more readable, easier to extend one step at a time, and reads better in a business/interview context than a deeply nested query.

## 5. Time-Range Filter: `BETWEEN` on `TIME` vs. `HOUR()`

- `HOUR(ride_time) BETWEEN 6 AND 8` matches any time from `06:00:00` up to `08:59:59` — it silently excludes the `09:00:00`–`09:59:59` hour even though `8` might look like it should cover "through 9am."
- `TIME(ride_time) BETWEEN '06:00:00' AND '09:00:00'` matches from `06:00:00` through exactly `09:00:00` inclusive — the boundary is explicit and unambiguous.

When a requirement says "between 6 AM and 9 AM," prefer the explicit `TIME(...) BETWEEN` form — it avoids the off-by-one-hour ambiguity that `HOUR()` bucketing introduces.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/Tricks and Tips/Master Class SQL Tricks|SQL Masterclass – Comprehensive Revision Guide]]
- [[Data Engineering Role Notes/SQL/Tricks and Tips/Group By and Having Tricks|Group By and Having Tricks]]

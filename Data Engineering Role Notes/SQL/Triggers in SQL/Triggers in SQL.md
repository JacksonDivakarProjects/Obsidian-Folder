# SQL Triggers — Comprehensive Beginner-Level Guide

## 1. What Is a Trigger?

A trigger is logic that runs automatically inside the database when a specific table event happens. A trigger fires on `INSERT`, `UPDATE`, or `DELETE` — think of it as the database's own auto-response system.

## 2. Why Triggers Exist

Triggers handle work that must be automatic, consistent, and guaranteed to run on every change — regardless of which application or user made it. Typical uses:

- Audit logging
- Auto-updating timestamps
- Validating data before it's written
- Keeping related tables in sync

This is the layer where the database enforces a rule even if the application forgets to.

## 3. Types of Triggers

**BEFORE triggers** run before the row is inserted/updated/deleted. Used to validate data, or modify the incoming row (e.g., force an email column to lowercase) before it's written.

**AFTER triggers** run once the row operation has completed. Used for logging, updating related tables, or writing to an audit table.

**Row-level vs. statement-level:**
- Row-level fires once per affected row.
- Statement-level fires once per SQL statement, regardless of how many rows it touched.

Row-level triggers are the ones to focus on first — they're what most real-world examples (audit logs, timestamp updates) actually use.

## 4. `NEW` and `OLD`

Syntax varies by database, but the concept is universal:
- **`NEW`** — the row's values after an `INSERT`/`UPDATE`.
- **`OLD`** — the row's values before an `UPDATE`/`DELETE`.

Example references: `NEW.salary`, `OLD.username`. This is how a trigger reads or modifies the row it's firing on.

## 5. Three Standard Examples

### Example 1 — Auto-update an `updated_at` column

Extremely common in real systems: every time a row is updated, its timestamp updates automatically.

```sql
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_timestamp
BEFORE UPDATE ON employees
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();
```

(Note: in PostgreSQL the trigger function must be defined before the `CREATE TRIGGER` statement that references it.)

### Example 2 — Prevent invalid inserts

E.g., salary must be positive:

```sql
CREATE OR REPLACE FUNCTION validate_salary()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.salary <= 0 THEN
    RAISE EXCEPTION 'Salary must be positive';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER salary_check
BEFORE INSERT ON employees
FOR EACH ROW
EXECUTE FUNCTION validate_salary();
```

### Example 3 — Write to an audit log

A common interview question:

```sql
CREATE OR REPLACE FUNCTION audit_employee_changes()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO employee_audit(emp_id, old_name, new_name, changed_at)
  VALUES (OLD.id, OLD.name, NEW.name, NOW());
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER employee_audit_trigger
AFTER UPDATE ON employees
FOR EACH ROW
EXECUTE FUNCTION audit_employee_changes();
```

## 6. When to Use Triggers

Triggers are powerful but can hide logic from anyone reading application code.

**Use triggers when:**
- Automatic timestamps are needed.
- Audit logs must exist unconditionally.
- A rule must always run, even if application developers forget to enforce it.

**Avoid triggers when:**
- The logic really belongs in the application layer.
- They'd make debugging significantly harder.
- They'd trigger hidden cascading side effects across other tables.

Keep triggers simple — don't build complex, multi-step workflows inside one.

## 7. Debugging Triggers

- Triggers run silently; you won't see them fire unless you look for them.
- Errors surface at query time, attributed to the statement that caused the trigger to fire.
- Inspect existing trigger definitions with catalog queries (e.g., PostgreSQL's `\d+ tablename` in psql, or `information_schema.triggers`) — MySQL's `SHOW TRIGGERS` is the equivalent there.
- Triggers can be disabled temporarily (`ALTER TABLE ... DISABLE TRIGGER ...` in PostgreSQL) if you need to isolate whether a trigger is the cause of unexpected behavior.
- Always test trigger logic against a small dataset first — a subtle bug in a trigger applies to every future write, not just one query.

## 8. Interview-Level Quick Answers

**What is a trigger?**
"An automated database function that runs in response to an INSERT, UPDATE, or DELETE event."

**When would you use a trigger?**
"For auditing, data validation, maintaining timestamps, or enforcing rules at the database level rather than trusting every calling application to do it."

**Difference between BEFORE and AFTER triggers?**
"BEFORE runs ahead of the write and can modify or reject the incoming row; AFTER runs once the write has committed and is typically used for logging or updating other tables."

## Summary

Know the definition, understand BEFORE vs. AFTER, understand row-level vs. statement-level, know `NEW`/`OLD`, and be able to write the timestamp, validation, and audit-log examples from memory — that combination covers the large majority of trigger usage in interviews and real projects.

## 🔗 Related Notes
- [[Data Engineering Role Notes/SQL/Stored Procedures in Postgres/Stored Procedures Notes|Comprehensive Beginner's Guide to PostgreSQL Stored Procedures]]
- [[Data Engineering Role Notes/SQL/Views in SQL/Views in SQL|SQL Views – The Complete Guide]]

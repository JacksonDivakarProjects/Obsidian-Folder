The **Delta Store** is a hidden, row-based (B-tree) staging area within a Clustered Columnstore Index. It exists because columnstore segments are **read-only** once they are compressed; you can’t simply "tack on" a single new row to a compressed blob without rebuilding the whole thing.

Think of the Delta Store as the **"Waiting Room"** for your data.

---

## 1. How the Delta Store Works

When you perform an `INSERT` into a table with a Columnstore index, SQL Server handles it in two ways based on the size of the insert:

- **Small Inserts (< 102,400 rows):** These rows go directly into the **Delta Store**. Here, they are stored in a traditional row-based format (B-tree) so that the insert is fast.
    
- **Large Inserts (≥ 102,400 rows):** These bypass the Delta Store entirely and are compressed directly into "Bulk" Columnstore segments.
    

---

## 2. The Life Cycle: From Delta to Compressed

The Delta Store isn't meant to be permanent. It follows a specific cycle:

1. **Open:** The Delta Store is actively accepting new rows.
    
2. **Closed:** Once a Delta Rowgroup hits the maximum size of **1,048,576 rows**, it is marked as "Closed."
    
3. **Compressed:** A background process called the **Tuple Mover** notices the "Closed" status, picks up those million rows, compresses them into column segments, and moves them into the main Columnstore storage.
    

---

## 3. Why is it necessary?

Without a Delta Store, your database would struggle with performance for two reasons:

- **Fragmentation:** Writing one row at a time into a compressed segment is computationally "expensive" and would lead to tiny, inefficient files.
    
- **Locking:** You would constantly be locking large segments of data just to add a single record, killing concurrency.
    

---

## 4. Impact on Queries

When you run a `SELECT` query, SQL Server is smart enough to look in **both** places:

1. It scans the **Compressed Segments** (the bulk of your data).
    
2. It scans the **Delta Store** (the most recent data that hasn't been compressed yet).
    
3. It combines the results seamlessly so you see the "true" state of the table.
    

---

## Pro-Tip for Data Engineers

If you notice your queries getting slower, it might be because you have too many "Open" Delta Rowgroups (this happens if you do many tiny trickling inserts). You can force the Delta Store to compress immediately by running:

SQL

```
ALTER INDEX MyColumnstoreIndex ON MyTable REORGANIZE;
```

Since you've been working with **dbt** and **data engineering** concepts, would you like to know how to query the system views (`sys.dm_db_column_store_row_group_physical_stats`) to see exactly how many rows are currently "stuck" in your Delta Store?
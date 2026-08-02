
Absolutely, Jack! Here’s a **professional, concise, and practical Delta Table Utility Guide** covering the commands and their use cases. This is designed like a reference sheet you can keep handy.

---

# **Delta Table Utility Guide**

---

## **1️⃣ DESCRIBE**

**Purpose:**  
Provides **basic metadata** about a Delta table.

**Syntax:**

```sql
DESCRIBE delta.`/path/to/table`;
```

**Output:**

- Column names
    
- Data types
    
- Nullable info
    

**Example:**

```sql
DESCRIBE delta.`/data/sales`;
```

Shows:

|Column|Type|Nullable|
|---|---|---|
|id|INT|YES|
|amount|DOUBLE|NO|

**Use Case:** Quick overview of table structure.

---

## **2️⃣ DESCRIBE EXTENDED**

**Purpose:**  
Provides **detailed metadata**, including storage location, format, and table properties.

**Syntax:**

```sql
DESCRIBE EXTENDED delta.`/path/to/table`;
```

**Output Includes:**

- Schema
    
- Table format
    
- Location
    
- Metadata properties (e.g., createdAt, version)
    

**Example:**

```sql
DESCRIBE EXTENDED delta.`/data/sales`;
```

Shows detailed table information like path, partition columns, and table properties.

---

## **3️⃣ RESTORE**

**Purpose:**  
Restores a Delta table to a **previous version**. Useful for recovering deleted or corrupted data.

**Syntax:**

```sql
RESTORE delta.`/path/to/table` TO VERSION AS OF <version_number>;
-- OR
RESTORE delta.`/path/to/table` TO TIMESTAMP AS OF '<timestamp>';
```

**Example:**

```sql
RESTORE delta.`/data/sales` TO VERSION AS OF 5;
```

- Table now reflects **state of version 5**.
    

**Use Case:** Undo accidental deletes, updates, or overwrites.

---

## **4️⃣ TIMESTAMP (Time Travel)**

**Purpose:**  
Query a Delta table as of a **specific point in time** using timestamp or version.

**Syntax:**

```sql
SELECT * FROM delta.`/path/to/table` TIMESTAMP AS OF '<yyyy-MM-dd HH:mm:ss>';
SELECT * FROM delta.`/path/to/table` VERSION AS OF <version_number>;
```

**Example:**

```sql
SELECT * FROM delta.`/data/sales` TIMESTAMP AS OF '2025-10-01 12:00:00';
```

**Use Case:** Audit, debugging, and data recovery.

---

## **5️⃣ HISTORY**

**Purpose:**  
Shows the **transaction history** of a Delta table, including updates, deletes, and schema changes.

**Syntax:**

```sql
DESCRIBE HISTORY delta.`/path/to/table`;
```

**Output Includes:**

- Version
    
- Timestamp
    
- User
    
- Operation (WRITE, DELETE, UPDATE, MERGE)
    
- Operation parameters
    

**Example:**

```sql
DESCRIBE HISTORY delta.`/data/sales`;
```

Shows version-wise changes with timestamps for tracking table evolution.

---

## **6️⃣ VACUUM**

**Purpose:**  
Deletes **old files** that are no longer referenced by the Delta table, freeing storage space.

**Syntax:**

```sql
VACUUM delta.`/path/to/table` [RETAIN <hours>];
```

**Example:**

```sql
VACUUM delta.`/data/sales` RETAIN 168; -- Retain 7 days of history
```

**Notes:**

- Default retention is **7 days (168 hours)**.
    
- Avoid reducing retention below 7 days unless you are sure you won’t need time travel.
    

**Use Case:** Storage optimization and cleaning up unneeded data files.

---

## **7️⃣ CLONING**

**Purpose:**  
Creates a **shallow or deep copy** of a Delta table for testing or sandbox environments.

**Syntax:**

```sql
-- Shallow clone (metadata only, data files are shared)
CREATE TABLE new_table SHALLOW CLONE delta.`/path/to/source_table`;

-- Deep clone (copies metadata + data)
CREATE TABLE new_table DEEP CLONE delta.`/path/to/source_table`;
```

**Example:**

```sql
CREATE TABLE sales_test SHALLOW CLONE delta.`/data/sales`;
```

**Use Case:**

- Test changes without affecting production data
    
- Quickly create copies for analytics or development
    

---

### ✅ **Summary Table**

|Command|Purpose|Notes|
|---|---|---|
|DESCRIBE|View basic schema|Columns, types|
|DESCRIBE EXTENDED|Detailed metadata|Path, properties, partitions|
|RESTORE|Roll back to version/timestamp|Time travel recovery|
|TIMESTAMP / VERSION AS OF|Query old table state|Audit/debug|
|HISTORY|Transaction history|Version, operation, user|
|VACUUM|Remove old files|Storage cleanup|
|CLONING|Copy table (shallow/deep)|Testing/dev sandbox|

---

If you want, I can **make a single-page visual cheat sheet** with **commands + quick example snippets** — ideal for interviews or reference.

Do you want me to do that?

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Important TBLProperties/Table Utility Commands|Delta Lake Table Utility Commands]]
- [[Data Engineering Role Notes/Data Engineering Concepts/Delta Lake/Delta Lake Commands in Different APIs/Delta Lake Commands in SQL API|Delta Lake Object Commands (SQL API)]]

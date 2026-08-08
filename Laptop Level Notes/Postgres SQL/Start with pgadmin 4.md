Here’s how to **start using pgAdmin 4** to manage your PostgreSQL databases step by step:

---

## **1. Launch pgAdmin 4**

- **Desktop mode:**  
    Open terminal:
    
    ```bash
    pgadmin4
    ```
    
    Or search for **pgAdmin 4** in your applications menu.
    
- **Web mode:**  
    If installed in web mode:
    
    ```bash
    sudo /usr/pgadmin4/bin/setup-web.sh
    ```
    
    Then open in browser:
    
    ```
    http://127.0.0.1/pgadmin4
    ```
    
    Log in with the email/password you set during setup.
    

---

## **2. Add a server**

1. Click **“Add New Server”** in pgAdmin.
    
2. **General tab:** Give it a name (e.g., `LocalPostgres`).
    
3. **Connection tab:**
    
    - Host: `localhost`
        
    - Port: `5432`
        
    - Maintenance database: `postgres`
        
    - Username: `postgres` (or your user)
        
    - Password: [your password]
        
    - Database: `mydb` (or leave as `postgres`)
        
4. Click **Save**. Your server now appears in the left sidebar.
    

---

## **3. Explore your database**

- Expand your server → Databases → `mydb` (or `postgres`).
    
- You can see:
    
    - **Schemas** (tables, views, functions)
        
    - **Tables** → click to see data or run queries
        
    - **Query Tool** → click **Tools → Query Tool** to write SQL
        

---

## **4. Run a simple query**

1. Open Query Tool.
    
2. Type:
    

```sql
SELECT version();
```

3. Click **Execute** → you’ll see your PostgreSQL version.
    

---

## **5. Optional common tasks**

- **Create a table:**
    

```sql
CREATE TABLE test_table (
    id SERIAL PRIMARY KEY,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

- **Insert data:**
    

```sql
INSERT INTO test_table (name) VALUES ('Jack');
```

- **Select data:**
    

```sql
SELECT * FROM test_table;
```

---

Once this is done, you can **explore databases, create users, run queries, and manage everything visually** through pgAdmin.

I can also make a **visual step-by-step workflow for beginners** showing how to connect, create a database, table, and query—all in pgAdmin 4. Do you want me to make that?

## 🔗 Related Notes
- [[Laptop Level Notes/Postgres SQL/Posgres Install & Create User|Posgres Install & Create User]]
- [[Laptop Level Notes/MySQL Configuration/MySQL Workbench|MySQL Workbench]]

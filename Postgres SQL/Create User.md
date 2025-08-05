
You're almost there! The issue is that you're running an **SQL command directly in the shell**, but SQL commands like `ALTER USER` must be executed **inside the PostgreSQL prompt** (`psql`).

---

## ✅ Step-by-Step to Set the Password Correctly

### 🔁 Step 1: Switch to the `postgres` user (you already did this)

```bash
sudo -i -u postgres
```

### ✅ Step 2: Enter the PostgreSQL shell

```bash
psql
```

Now you’ll see a prompt like:

```
postgres=#
```

### ✅ Step 3: Run the SQL command to set the password

If you want to set the password for the `postgres` user:

```sql
ALTER USER postgres WITH PASSWORD '53787';
```

> Or if you're trying to change it for a user named `admin`, use:

```sql
ALTER USER admin WITH PASSWORD '53787';
```

### ✅ Step 4: Exit the PostgreSQL shell

```sql
\q
```

---

## 🔁 Final Step: Use the password in DBeaver

- Go back to DBeaver
    
- Open your connection settings
    
- Enter the username (`postgres`) and the new password (`53787`)
    
- Test connection ✅
    

---

Let me know if:

- You want to create a new user instead of using `postgres`
    
- You need help making the password optional (for dev use only)
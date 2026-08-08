Here’s a clean, step-by-step guide to install **PostgreSQL** on Linux (Ubuntu/Zorin) and configure it for use.

---

## **1. Update system**

```bash
sudo apt update
sudo apt upgrade -y
```

---

## **2. Install PostgreSQL**

```bash
sudo apt install postgresql postgresql-contrib -y
```

- `postgresql-contrib` provides extra tools and extensions.
    

---

## **3. Start and enable PostgreSQL service**

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

- Check status:
    

```bash
sudo systemctl status postgresql
```

---

## **4. Switch to PostgreSQL user**

PostgreSQL creates a default user called `postgres`. Switch to it:

```bash
sudo -i -u postgres
```

- Access PostgreSQL prompt:
    

```bash
psql
```

- You’ll see:
    

```sql
postgres=#
```

- Exit:
    

```sql
\q
exit
```

---

## **5. Set a password for postgres user**

```bash
sudo -i -u postgres
psql
```

Inside psql:

```sql
ALTER USER postgres PASSWORD '53787';
\q
exit
```

> Replace `'yourpassword'` with a strong password.

---

## **6. Create a new database and user**

```bash
sudo -i -u postgres
psql
```

Inside psql:

```sql
CREATE DATABASE mydb;
CREATE USER jack WITH ENCRYPTED PASSWORD '53787';
GRANT ALL PRIVILEGES ON DATABASE mydb TO jack;
\q
exit
```

- `mydb` → your database
    
- `jack` → username
    

---

## **7. Enable remote access (optional)**

1. Edit PostgreSQL config:
    

```bash
sudo nano /etc/postgresql/14/main/postgresql.conf
```

- Change:
    

```
#listen_addresses = 'localhost'
```

to:

```
listen_addresses = '*'
```

2. Edit client authentication file:
    

```bash
sudo nano /etc/postgresql/14/main/pg_hba.conf
```

- Add at the end:
    

```
host    all             all             0.0.0.0/0               md5
```

3. Restart PostgreSQL:
    

```bash
sudo systemctl restart postgresql
```

---

## **8. Test login**

Local login:

```bash
psql -U jack -d mydb -W
```

- `-U jack` → username
    
- `-d mydb` → database
    
- `-W` → prompt for password
    

---

## **9. Install pgAdmin / GUI (optional)**

```bash
sudo apt install pgadmin4 -y
```

- Or use **DBeaver**, which works with MySQL and PostgreSQL.
    

---

If you want, I can give a **single command sequence that installs PostgreSQL + creates user + database + enables remote access** so it’s ready for GUI connections immediately. Do you want me to do that?

## 🔗 Related Notes
- [[Laptop Level Notes/Postgres SQL/Start with pgadmin 4|Start with pgadmin 4]]
- [[Laptop Level Notes/MySQL Configuration/MySQL CMD Login and Create User|MySQL CMD Login and Create User]]

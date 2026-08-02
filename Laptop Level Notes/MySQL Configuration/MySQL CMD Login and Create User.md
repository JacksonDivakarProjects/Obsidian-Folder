Here’s how to log in to MySQL on Linux after installing MySQL server:

---

### **1. Log in as root**

```bash
sudo mysql -u root -p
```

- `-u root` → login as the MySQL root user
    
- `-p` → prompt for password
    

> Enter the root password you set during `mysql_secure_installation`.

---

### **2. If you just installed MySQL and root uses socket authentication (common on Ubuntu/Zorin)**

You can log in without a password:

```bash
sudo mysql
```

This works because the root user is mapped to your Linux user.

---

### **3. After logging in**

You will see the MySQL prompt:

```sql
mysql>
```

You can try a test command:

```sql
SHOW DATABASES;
```

- List existing databases. ✅
    

---

### **4. Optional: Create a new user (for Workbench or remote access)**

```sql
CREATE USER 'jack'@'localhost' IDENTIFIED BY 'strongpassword';
GRANT ALL PRIVILEGES ON *.* TO 'jack'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

- Replace `'jack'` and `'strongpassword'` with your desired username/password.
    
- Use this user to log in from **MySQL Workbench**.
    

---

### **5. Log in with a different user**

```bash
mysql -u jack -p
```

Enter the password you set.

---

If you want, I can give a **ready-to-use command sequence to set up MySQL root + a dedicated Workbench user + login test** so you can start using Workbench immediately. Do you want me to do that?

## 🔗 Related Notes
- [[Laptop Level Notes/MySQL Configuration/MySQL Workbench|MySQL Workbench]]
- [[Laptop Level Notes/Postgres SQL/Posgres Install & Create User|Posgres Install & Create User]]

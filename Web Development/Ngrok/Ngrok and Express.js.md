Below is a crisp, corporate-style **end-to-end comprehensive guide** to get **ngrok** running on **Linux** with an **Express.js** server. It is streamlined, execution-ready, and perfect for your workflow.

---

# 🚀 **Comprehensive Guide: Setting Up Ngrok in Linux for an Express.js Server**

---

# 1️⃣ **Install Ngrok**

### **Option A: Install via .deb package (Recommended)**

```bash
wget https://bin.equinox.io/c/bNyj1mQY/Ngrok-stable-linux-amd64.deb
sudo dpkg -i Ngrok-stable-linux-amd64.deb
```

### **Option B: Install via Snap**

```bash
sudo snap install ngrok
```

### **Option C: Download ZIP manually**

```bash
wget https://bin.equinox.io/c/bNyj1mQY/ngrok-stable-linux-amd64.zip
unzip ngrok-stable-linux-amd64.zip
sudo mv ngrok /usr/local/bin/
```

Check installation:

```bash
ngrok version
```

---

# 2️⃣ **Sign Up and Get Your Auth Token**

1. Visit: [https://dashboard.ngrok.com](https://dashboard.ngrok.com)
    
2. Log in → Go to **Setup & Installation**
    
3. Copy your **Auth Token**
    
4. Run this command:
    

```bash
ngrok config add-authtoken <YOUR_TOKEN_HERE>
```

This step links your local ngrok client to your cloud account.

---

# 3️⃣ **Create a Simple Express.js Server**

### Project Setup

```bash
mkdir express-ngrok-demo
cd express-ngrok-demo
npm init -y
npm install express
```

### Create `server.js`

```js
import express from "express";
const app = express();

app.use(express.json());

app.get("/", (req, res) => {
  res.send("Server is live 🚀");
});

app.listen(3000, () => console.log("Server running on port 3000"));
```

Run it:

```bash
node server.js
```

Your backend is now running on:

```
http://localhost:3000
```

---

# 4️⃣ **Expose Express Server to the Internet Using Ngrok**

Open a second terminal and run:

```bash
ngrok http 3000
```

### You will see:

```
Forwarding    https://<random-id>.ngrok.io -> http://localhost:3000
```

This **HTTPS public URL** can now be used by:

- Webhooks
    
- Mobile apps
    
- Postman
    
- External APIs
    
- Teammates for testing
    

---

# 5️⃣ **Verify the Public URL**

Open the URL in your browser:

```
https://<your-ngrok-id>.ngrok-free.app
```

You should see:

```
Server is live 🚀
```

---

# 6️⃣ **Optional: Create a Static Ngrok Domain (Highly Recommended)**

If you want the same URL every day:

1. Go to your ngrok dashboard
    
2. "Endpoints" → "Reserved Domain"
    
3. Choose something like:
    
    ```
    jack-demo.ngrok-free.app
    ```
    

Bind it:

```bash
ngrok http --domain=jack-demo.ngrok-free.app 3000
```

---

# 7️⃣ **Optional: Create an Ngrok Config File**

Create:

```bash
nano ~/.config/ngrok/ngrok.yml
```

Paste:

```yaml
version: "2"
authtoken: <YOUR_TOKEN>
tunnels:
  express:
    addr: 3000
    proto: http
```

Start ngrok via:

```bash
ngrok start express
```

This is enterprise-friendly and ideal for long-term workflows.

---

# 8️⃣ **Troubleshooting (Quick Wins)**

### ❌ Port Already in Use

```bash
sudo lsof -i :3000
kill -9 <PID>
```

### ❌ Ngrok not found

```bash
sudo mv ngrok /usr/local/bin/
```

### ❌ Server not reachable

Verify your Express server is running:

```bash
curl http://localhost:3000
```

---

# 9️⃣ **Why Ngrok Matters (Professional Insight)**

Use ngrok when you need:

- External services (webhooks, payment gateways) to hit localhost
    
- Testing APIs on real devices
    
- Demonstrations for stakeholders
    
- Remote team access without deploying to cloud
    

It accelerates development velocity and eliminates environment bottlenecks.

---

# 🔚 **If you want, I can generate:**

✅ A production-grade ngrok YAML  
✅ A Docker setup  
✅ A secured webhook endpoint workflow  
✅ A Postman-ready API collection

Just tell me.

## 🔗 Related Notes
- [[Web Development/Ngrok/Ngrok|Ngrok]]
- [[Web Development/Ngrok/NGROK and FAST API|NGROK and FAST API]]

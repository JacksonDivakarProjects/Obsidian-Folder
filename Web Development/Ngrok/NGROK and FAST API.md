Perfect — here’s a **clean, concise, and practical guide** for using **ngrok with FastAPI on Linux**, in a **note-style format** (no fluff, just actionable steps).

---

## 🧩 1. Install Requirements

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip unzip wget
```

---

## ⚙️ 2. Create Virtual Environment & Install Packages

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn
```

---

## 📄 3. Create FastAPI App (`main.py`)

```python
from fastapi import FastAPI, UploadFile, File, Query
import pandas as pd
import os

app = FastAPI()
CSV_PATH = "uploaded_large.csv"

@app.post("/upload_csv/")
async def upload_csv(file: UploadFile = File(...)):
    with open(CSV_PATH, "wb") as f:
        f.write(await file.read())
    return {"message": "File uploaded"}

@app.get("/get_records/")
def get_records(offset: int = Query(0, ge=0), limit: int = Query(5, ge=1)):
    if not os.path.exists(CSV_PATH):
        return {"error": "No CSV uploaded"}
    df = pd.read_csv(CSV_PATH, skiprows=range(1, offset + 1), nrows=limit, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    return {"offset": offset, "limit": limit, "records": df.to_dict(orient="records")}
```

---

## 🚀 4. Run FastAPI Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🌐 5. Install Ngrok

### Option 1 — Snap (Recommended)

```bash
sudo snap install ngrok
```

### Option 2 — Manual

```bash
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-linux-amd64.zip
unzip ngrok-stable-linux-amd64.zip
sudo mv ngrok /usr/local/bin/
ngrok version
```

---

## 🔑 6. Authenticate Ngrok

1. Get your token from: [https://dashboard.ngrok.com/get-started/your-authtoken](https://dashboard.ngrok.com/get-started/your-authtoken)
    
2. Run:
    

```bash
ngrok config add-authtoken <YOUR_AUTHTOKEN>
```

---

## 🔗 7. Start Ngrok Tunnel

```bash
ngrok http 8000
```

**Output Example:**

```
Forwarding  https://abcd1234.ngrok-free.app -> http://localhost:8000
```

Use that `https://abcd1234.ngrok-free.app` URL globally.

---

## 🔍 8. Verify Tunnel

Open local dashboard:

```
http://127.0.0.1:4040
```

List active tunnels via CLI:

```bash
curl http://127.0.0.1:4040/api/tunnels
```

---

## 🧪 9. API Testing via cURL

**Upload File**

```bash
curl -X POST "https://<ngrok-url>/upload_csv/" \
  -F "file=@/path/to/file.csv"
```

**Get Records**

```bash
curl "https://<ngrok-url>/get_records/?offset=0&limit=5"
```

---

## 🛠️ 10. Optional — Persistent Config (`~/.config/ngrok/ngrok.yml`)

```yaml
version: "2"
authtoken: <YOUR_AUTHTOKEN>
tunnels:
  fastapi:
    proto: http
    addr: 8000
```

Run:

```bash
ngrok start --all
```

---

## 🔁 11. Create Systemd Service (Optional)

**File:** `/etc/systemd/system/ngrok.service`

```ini
[Unit]
Description=Ngrok Tunnel
After=network.target

[Service]
ExecStart=/usr/local/bin/ngrok start --all --config /home/<user>/.config/ngrok/ngrok.yml
Restart=on-failure
User=<user>

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ngrok.service
```

---

## 🔁 12. FastAPI Systemd Service (Optional)

**File:** `/etc/systemd/system/fastapi.service`

```ini
[Unit]
Description=FastAPI App
After=network.target

[Service]
User=<user>
WorkingDirectory=/home/<user>/project
ExecStart=/home/<user>/project/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now fastapi.service
```

---

## ✅ 13. Quick Commands Summary

|Task|Command|
|---|---|
|Start FastAPI|`uvicorn main:app --host 0.0.0.0 --port 8000 --reload`|
|Start Ngrok|`ngrok http 8000`|
|Check tunnels|`curl 127.0.0.1:4040/api/tunnels`|
|View dashboard|`http://127.0.0.1:4040`|
|Systemd reload|`sudo systemctl daemon-reload`|
|Enable service|`sudo systemctl enable --now ngrok.service`|

---

Would you like me to add a **single combined script (bash)** that installs everything and starts both services automatically?

## 🔗 Related Notes
- [[Web Development/Ngrok/Ngrok|Ngrok]]
- [[Web Development/Ngrok/Ngrok and Express.js|Comprehensive Guide: Setting Up Ngrok in Linux for an Express.js Server]]

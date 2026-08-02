Perfect. Here’s a **clean, practical Fedora cheat sheet** you can actually use day-to-day.  
Bookmark this. This is **90% of what professionals use**.

![Image](https://media.geeksforgeeks.org/wp-content/uploads/20231013135657/Image3a.png?utm_source=chatgpt.com)

![Image](https://linuxhint.com/wp-content/uploads/2021/02/Manage-Startup-Services-systemd-Fedora-16.png?utm_source=chatgpt.com)

![Image](https://us1.discourse-cdn.com/fedoraproject/original/3X/6/4/649971ec5724aead3f7a867c65dbe72f9b096934.png?utm_source=chatgpt.com)

---

# 🧾 **Fedora Linux Cheat Sheet (Essential)**

## 📦 Package Management (`dnf`)

```bash
sudo dnf check-update          # Check updates
sudo dnf upgrade               # Update system
sudo dnf install pkg           # Install package
sudo dnf remove pkg            # Remove package
sudo dnf search pkg            # Search package
sudo dnf info pkg              # Package info
sudo dnf autoremove            # Remove unused deps
sudo dnf clean all             # Clean cache
```

---

## 🔧 Services & System (`systemd`)

```bash
systemctl status service
sudo systemctl start service
sudo systemctl stop service
sudo systemctl restart service
sudo systemctl enable service     # Start on boot
sudo systemctl disable service
```

Logs:

```bash
journalctl -u service
journalctl -xe
```

---

## 🖥️ Hardware & System Info

```bash
uname -r            # Kernel version
hostnamectl         # Device name
lsblk               # Disk layout
df -h               # Disk usage
free -h             # Memory
lscpu               # CPU info
```

---

## 📁 Files & Navigation

```bash
ls -la
cd /path
pwd
cp src dest
mv src dest
rm -r folder
find / -name file
```

---

## 🔐 Permissions

```bash
chmod 755 file
chmod +x script.sh
chown user:group file
```

---

## 🌐 Networking

```bash
ip a                 # IP address
nmcli device status  # Network status
ping google.com
ss -tulnp            # Open ports
```

---

## 🔥 Firewall (`firewalld`)

```bash
sudo firewall-cmd --state
sudo firewall-cmd --list-all
sudo firewall-cmd --add-port=3306/tcp --permanent
sudo firewall-cmd --reload
```

---

## 🧱 SELinux (Enterprise-level)

```bash
getenforce
sestatus
sudo setenforce 0    # Permissive (temporary)
sudo setenforce 1    # Enforcing
```

**Rule:** Don’t disable permanently unless you know why.

---

## 🧩 GNOME / UI

```bash
gsettings list-recursively
gnome-extensions list
gnome-extensions enable EXTENSION
gnome-extensions disable EXTENSION
```

---

## 🐍 Python (Fedora way)

```bash
python3 --version
pip3 install --user pkg
python3 -m venv venv
source venv/bin/activate
```

---

## 📦 Archive & Compression

```bash
tar -xvf file.tar
tar -xzvf file.tar.gz
zip -r file.zip folder
unzip file.zip
```

---

## 🚀 Process Management

```bash
ps aux
top
htop
kill -9 PID
```

---

## 🔁 Reboot / Shutdown

```bash
sudo reboot
sudo shutdown now
```

---

## 🧠 Fedora ↔ Company Linux Mapping

|Fedora|Enterprise|
|---|---|
|`dnf`|`dnf / yum`|
|`firewalld`|RHEL default|
|SELinux enforcing|Production systems|
|systemd|Universal|

---

## 🎯 How to use this cheat sheet (important)

- Don’t memorize everything
    
- Understand **what category a command belongs to**
    
- Practice **daily repetition**
    

Within 2–3 weeks, this becomes muscle memory.

---

## Straight talk

You’re now operating on **real enterprise Linux**, not a toy setup.  
Fedora trains discipline. That pays off in interviews and production work.

---

If you want next:

- **Ubuntu ↔ Fedora side-by-side cheat sheet**
    
- **Interview Linux commands**
    
- **Fedora setup for data engineering / backend**
    

Tell me your next focus.

## 🔗 Related Notes
- [[Laptop Level Notes/Swap Memory/Swapping Memory|Swapping Memory]]
- [[Laptop Level Notes/Set Java SDK/Set Java SDK|Set Java SDK]]
- [[Laptop Level Notes/Ollama Installation/Ollama Installation|Ollama Installation]]
- [[Laptop Level Notes/MySQL Configuration/MySQL CMD Login and Create User|MySQL CMD Login and Create User]]

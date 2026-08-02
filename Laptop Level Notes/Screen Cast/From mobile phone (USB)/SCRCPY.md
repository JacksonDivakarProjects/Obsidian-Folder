Got it. Let’s create a **clean, practical, and _working_ scrcpy guide** — **zero fluff**, just what you need.  
I’ll also help you avoid the usual “device unauthorized” issues.

---

## 🎯 **Goal**

Mirror and control your **Android phone screen** on **Linux** using `scrcpy`.

---

## ✅ **What scrcpy Does Well**

- High performance, low latency
    
- Uses **USB or Wi-Fi**
    
- **No app install** required on phone
    
- Keyboard + mouse can control phone
    

---

# 1) **Install scrcpy**

### **Ubuntu / Pop!_OS / Debian**

```bash
sudo apt update
sudo apt install scrcpy adb -y
```

### **Arch / Manjaro**

```bash
sudo pacman -S scrcpy android-tools
```

### **Fedora**

```bash
sudo dnf install scrcpy android-tools
```

---

# 2) **Enable USB Debugging on Phone**

1. Open **Settings → About Phone**
    
2. Tap **Build Number** 7 times → Developer Mode ON
    
3. Go to **Settings → System → Developer Options**
    
4. Enable:
    
    - ✅ **USB debugging**
        
    - ✅ (Optional) **Wireless debugging** (Android 11+)
        

---

# 3) **Fix “Device Unauthorized” (Your issue)**

When you plug the USB:

- Your phone will display a **Allow USB debugging?** pop-up → **Tap “Allow”**
    

If the dialog didn’t appear:

```bash
adb kill-server
adb start-server
adb devices
```

If it shows _unauthorized_, unplug + reconnect USB.

---

# 4) **Start mirroring over USB**

```bash
scrcpy
```

That’s it.

---

# 5) **Wireless Mode (after USB once)**

### Step 1: Find phone IP

On phone: **Settings → Wi-Fi** → look at IP (e.g., `192.168.1.27`)

### Step 2: Connect Wirelessly

```bash
adb tcpip 5555
adb connect 192.168.1.27:5555
scrcpy
```

Now you can unplug USB.

---

# 6) **Useful Performance Options**

|Mode|Command|
|---|---|
|Low latency gaming|`scrcpy --max-fps 60 --bit-rate 16M`|
|Save screen recording|`scrcpy --record screen.mp4`|
|Disable phone screen|`scrcpy --turn-screen-off`|
|Fullscreen|`scrcpy -f`|

Example:

```bash
scrcpy --bit-rate 12M --max-size 1280 --max-fps 60 --turn-screen-off
```

---

# 7) **Common Errors + Solutions**

|Error|Fix|
|---|---|
|**device unauthorized**|Re-enable USB debugging & accept prompt|
|**device offline**|`adb kill-server && adb start-server`|
|**scrcpy closes immediately**|Use better USB cable / USB 2.0 port|
|**black screen on wireless**|Ensure phone & PC are on same Wi-Fi|

---

## 🧭 Practical Closing Advice

If your **goal is Wireless Display from laptop → phone**, `scrcpy` is _not_ the correct tool. scrcpy only mirrors **phone → laptop**.

If you want **laptop → phone**, you must use:

- **Deskreen**  
    or
    
- **VNC Server + VNC Viewer**
    

We can set that up next if needed.

---

## 👍 Want me to prepare:

✔ **“Laptop → Phone Wireless Display” guide**  
✔ Works on any Linux  
✔ No lag (uses WebRTC)

Just say:  
**“Give Deskreen guide.”**

## 🔗 Related Notes
- [[Laptop Level Notes/Screen Cast/From Linux Laptop/Wireless Display|Wireless Display (GNOME Network Displays / Miracast)]]
- [[Laptop Level Notes/Mobile Cam Tool For Webcam/Droid Cam|Use Your Phone Camera as a Virtual Webcam on Linux]]

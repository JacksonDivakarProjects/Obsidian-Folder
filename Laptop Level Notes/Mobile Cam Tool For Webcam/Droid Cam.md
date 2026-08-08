Got it.  
You want **complete**, but **organized**, **clear**, and **practical** — no fluff, no circles.  
Here is the **full clean guide** in a professional, step-wise reference format.

---

# ✅ **Use Your Phone Camera as a Virtual Webcam on Linux (Stable Method)**

This guide covers:

- **Installation**
    
- **Connection (Wi-Fi & USB)**
    
- **Virtual Camera setup**
    
- **Fix Zoom/Meet blank screen issue**
    
- **Troubleshooting common errors**
    

---

## **1. Requirements**

Make sure these are installed:

```bash
sudo apt update
sudo apt install linux-headers-$(uname -r) gcc make ffmpeg v4l-utils mpv
```

---

## **2. Install DroidCam (Client + Virtual Camera Driver)**

```bash
cd ~
wget https://files.dev47apps.net/linux/droidcam_latest.zip
unzip droidcam_latest.zip -d droidcam
cd droidcam
sudo ./install-client
sudo ./install-video
```

This installs:

|Component|Purpose|
|---|---|
|`droidcam`|Connects laptop ↔ phone|
|`v4l2loopback_dc`|Creates **virtual webcam** at `/dev/video0`|

---

## **3. Install DroidCam App on Phone**

Open Play Store / App Store → Install **DroidCam**.

---

## **4. Connect Phone Camera to Laptop**

### **A) Over Wi-Fi (Simple)**

1. Open **DroidCam** on phone.
    
2. Note the **Wi-Fi IP** shown.
    
3. Run on laptop:
    
    ```bash
    droidcam
    ```
    
4. Enter phone IP → Press **Start**.
    

---

### **B) Over USB (Best Quality, Low Latency)**

**Enable Developer Mode + USB Debugging on Phone**

```
Settings → About phone → Tap Build Number 7 times
Settings → Developer Options → Enable USB Debugging
```

Connect USB cable → test:

```bash
adb devices
```

Check if the phone shows:

```
device
```

Then:

```bash
droidcam --adb
```

---

## **5. Verify Virtual Camera Device**

```bash
v4l2-ctl --list-devices
```

Expected output:

```
DroidCam:
   /dev/video0
```

If `/dev/video0` doesn’t exist → reinstall:

```bash
sudo ./install-video
```

---

## **6. Test the Camera Stream**

```bash
mpv /dev/video0
```

If you see the camera feed → Virtual Webcam works.

---

## **7. Use in Video Meeting Tools**

|App|Camera Name to Select|
|---|---|
|Zoom|**DroidCam**|
|Google Meet|**DroidCam**|
|MS Teams|**DroidCam**|
|OBS Studio|**/dev/video0**|

---

# 🔧 **Fix Common Issues**

|Issue|Solution|
|---|---|
|**Zoom shows Black Screen**|Reload driver with exclusive mode: `sudo modprobe -r v4l2loopback_dc` `sudo modprobe v4l2loopback_dc exclusive_caps=1`|
|`device unauthorized` in USB mode|On phone → Accept **Allow USB Debugging** dialog|
|No `/dev/video0` appears|Reinstall video driver: `sudo ./install-video`|
|Video lag / delay|Switch to **USB Mode**: `droidcam --adb`|
|Camera not showing in browser|Close all apps using webcam → Restart browser|

---

# 🎛 Optional: Increase Video Quality

### Set 720p

```bash
droidcam -size 720p
```

### Set 1080p (if phone supports it)

```bash
droidcam -size 1080p
```

---

# ♻ Restart Virtual Camera (Good quick fix)

```bash
sudo modprobe -r v4l2loopback_dc
sudo modprobe v4l2loopback_dc exclusive_caps=1
```

---

# ✅ Summary (One-Look Quick Reference)

|Step|Command / Action|
|---|---|
|Install|`sudo ./install-client && sudo ./install-video`|
|Start DroidCam|`droidcam` or `droidcam --adb`|
|Check webcam|`v4l2-ctl --list-devices`|
|Test stream|`mpv /dev/video0`|
|Fix Zoom Black Screen|`sudo modprobe v4l2loopback_dc exclusive_caps=1`|

---

## Want me to finalize this into:

### **✅ A PDF**

### **✅ A One-Page Cheat Sheet**

### **✅ Or a Printable Markdown Guide**

Tell me:  
**`PDF`** / **`Cheat Sheet`** / **`Markdown`**

I’ll generate it ready for download.

## 🔗 Related Notes
- [[Laptop Level Notes/OBS Camera Restart/Camera Restart Command|Camera Restart Command]]
- [[Laptop Level Notes/Screen Cast/From Linux Laptop/Wireless Display|Wireless Display (GNOME Network Displays / Miracast)]]
- [[Laptop Level Notes/Screen Cast/From mobile phone (USB)/SCRCPY|SCRCPY (Android Screen Mirroring)]]

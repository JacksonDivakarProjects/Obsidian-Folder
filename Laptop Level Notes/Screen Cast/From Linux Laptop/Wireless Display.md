Understood. I’ll give you a **complete, future-proof guide** for **GNOME Network Displays (Wireless Display / Miracast Receiver)** covering **all installation methods** and **exact troubleshooting steps** — **no fluff, no missing pieces**.

This lets your **Linux laptop receive screen-cast from Windows, Android, Smart TVs, etc.**

---

# 🎯 **Goal**

Enable **Linux Laptop to act as a _Wireless Display Receiver_**.

You will be able to:

- Cast **from Windows (Win+K)**
    
- Cast **from Android (Smart View / Cast)**
    
- Cast **from another Linux system**
    

Using:  
**GNOME Network Displays**

---

# ✅ **Check Hardware Compatibility First**

Miracast requires **Wi-Fi Direct support**.

Run:

```bash
iw list | grep -A10 "Supported interface modes"
```

Look for **these two**:

```
P2P-device
P2P-GO
```

|If You See|Result|
|---|---|
|✅ `P2P` modes present|Miracast **will work**|
|❌ P2P missing|**Miracast cannot work** (use Deskreen / VNC instead)|

If missing → tell me your **WiFi card model**:

```bash
lspci | grep -i wireless
```

I’ll guide alternatives.

---

# 🏛️ Installation Methods (Choose Your Case)

|Linux Version|Best Install Method|
|---|---|
|Ubuntu 22.04 / 23.04 / Pop!_OS / Linux Mint|Flatpak (Recommended)|
|Arch / Manjaro|Pacman|
|Fedora|DNF|
|GNOME Nightly Users|GNOME Builder|

---

## **METHOD 1 — Universal (Works on Any Distro) — FLATPAK** ✅ _Recommended_

### 1) Install Flatpak:

```bash
sudo apt install flatpak -y
```

### 2) Enable Flathub:

```bash
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
```

### 3) Install Network Displays:

```bash
flatpak install flathub org.gnome.NetworkDisplays -y
```

### 4) Run:

```bash
flatpak run org.gnome.NetworkDisplays
```

---

## **METHOD 2 — Ubuntu 24.04 (APT Available)**

```bash
sudo apt update
sudo apt install gnome-network-displays
```

---

## **METHOD 3 — Arch / Manjaro**

```bash
sudo pacman -S gnome-network-displays
```

---

## **METHOD 4 — Fedora**

```bash
sudo dnf install gnome-network-displays
```

---

# 🟢 **How to Use**

### **On Linux**

Open:

```
Network Displays
```

→ It waits for incoming cast.

---

### **From Windows**

Press:

```
Win + K
```

Select your Linux computer.

---

### **From Android**

1. Pull Quick Settings → **Cast** / **Smart View** / **Screen Share**
    
2. Tap the **3 dots → Enable Wireless Display**
    
3. Select your Linux laptop.
    

---

# ⚠️ Common Fixes

### 1) If device does not appear:

Enable Wi-Fi P2P:

```bash
sudo systemctl restart NetworkManager
```

### 2) If video plays but no audio:

Install PipeWire + WirePlumber:

```bash
sudo apt install pipewire wireplumber pipewire-audio-client-libraries -y
```

Restart:

```bash
systemctl --user restart wireplumber pipewire
```

### 3) If display connects but is black:

Enable **Hardware Acceleration**:

```bash
sudo apt install gstreamer1.0-vaapi
```

---

# 💡 **If Your Hardware Does NOT Support Miracast**

Use **Deskreen** (browser-based wireless display):

```bash
npx deskreen
```

No app needed on phone/TV — just open link in browser.

---

# ✅ **Now You Have:**

✔ Every install method  
✔ Compatibility test  
✔ Usage instructions  
✔ Audio fix  
✔ Black screen fix  
✔ Hardware fallback solution

---

If you want, I can now create a **One-Page PDF** of this guide so you can **save & refer anytime.**

**Should I generate the PDF?**  
Reply: **Yes** or **No**

## 🔗 Related Notes
- [[Laptop Level Notes/Screen Cast/From mobile phone (USB)/SCRCPY|SCRCPY (Android Screen Mirroring)]]
- [[Laptop Level Notes/Mobile Cam Tool For Webcam/Droid Cam|Use Your Phone Camera as a Virtual Webcam on Linux]]

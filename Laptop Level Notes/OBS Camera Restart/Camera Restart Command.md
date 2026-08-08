
Good question, Jack 👍 — if you want to **restart everything cleanly** (camera drivers, OBS virtual camera, Flatpak environment), here’s the safe way to do it on Linux without rebooting:

---

### 🔹 1. Stop OBS (if running)

```bash
flatpak kill com.obsproject.Studio
```

---

### 🔹 2. Unload and reload camera drivers

First, remove the `v4l2loopback` module (virtual cam):

```bash
sudo modprobe -r v4l2loopback
```

Then reload your real camera driver (most laptops use `uvcvideo`):

```bash
sudo modprobe -r uvcvideo
sudo modprobe uvcvideo
```

Finally, reload `v4l2loopback`:

```bash
sudo modprobe v4l2loopback devices=1 exclusive_caps=1 card_label="OBS Virtual Camera"
```

Check devices again:

```bash
ls /dev/video*
```

👉 You should see `/dev/video0, /dev/video1` (real cam) and `/dev/video2` (OBS Virtual Cam).

---

### 🔹 3. Restart OBS with NVIDIA overrides

```bash
flatpak run com.obsproject.Studio
```

---

### 🔹 4. Verify

- In OBS, click **Start Virtual Camera**.
    
- In other apps, check camera list → _OBS Virtual Camera_.
    

---

⚡ If you want, I can give you a **single script** called `restart_obs_cam.sh` that runs all of this in one shot. Then you’d just type:

```bash
bash restart_obs_cam.sh
```

👉 Want me to build that script for you so you don’t have to remember all the commands?

## 🔗 Related Notes
- [[Laptop Level Notes/Mobile Cam Tool For Webcam/Droid Cam|Use Your Phone Camera as a Virtual Webcam on Linux]]
- [[Laptop Level Notes/Screen Cast/From Linux Laptop/Wireless Display|Wireless Display (GNOME Network Displays / Miracast)]]

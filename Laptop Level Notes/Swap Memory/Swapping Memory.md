You can safely add swap to your Linux laptop to supplement RAM, but there are limits. Here’s a detailed, practical guide.

---

## **1. How much swap is safe**

General guidelines:

|RAM Size|Recommended Swap|
|---|---|
|< 8 GB|2× RAM (e.g., 8 GB RAM → 16 GB swap)|
|8–16 GB|1–1.5× RAM (16 GB RAM → 16–24 GB swap)|
|>16 GB|0.5–1× RAM (32 GB RAM → 16–32 GB swap)|

**For your 16 GB RAM laptop:**

- **16–24 GB swap** is safe.
    
- More swap is possible, but it won’t make programs faster; it just prevents crashes if RAM fills up.
    

> Note: Swap on SSD is fine; it’s slower than RAM, but workable for testing large LLMs.

---

## **2. Check current swap**

```bash
swapon --show
free -h
```

If you see no swap or very little, you can create a new swap file.

---

## **3. Create a swap file**

1. **Create the file** (example: 16 GB swap):
    

```bash
sudo fallocate -l 16G /swapfile
```

> If `fallocate` fails, use:

```bash
sudo dd if=/dev/zero of=/swapfile bs=1G count=16
```

2. **Secure the swap file:**
    

```bash
sudo chmod 600 /swapfile
```

3. **Set it up as swap:**
    

```bash
sudo mkswap /swapfile
sudo swapon /swapfile
```

4. **Verify swap is active:**
    

```bash
swapon --show
free -h
```

---

## **4. Make swap permanent**

Add this line to `/etc/fstab`:

```bash
/swapfile none swap sw 0 0
```

---

## **5. Optional: Adjust swap behavior**

- `swappiness` controls how aggressively Linux uses swap:
    

```bash
cat /proc/sys/vm/swappiness   # default is usually 60
sudo sysctl vm.swappiness=10  # makes system prefer RAM more
```

- For LLMs, you might want **lower swappiness** (10–20) so RAM is used first.
    

---

### ✅ **Recommendation for running 7B–8B models on 16 GB RAM**

- Create **16–20 GB swap**.
    
- Run Ollama with small batch sizes if available.
    
- Expect slower inference; loading the model may take time.
    

---

If you want, I can give a **ready-to-run command set that configures swap + Ollama for 7B model** so it works smoothly on your 16 GB RAM laptop. This avoids trial-and-error. Do you want me to prepare that?

## 🔗 Related Notes
- [[Laptop Level Notes/Ollama Installation/Ollama Installation|Ollama Installation]]
- [[Laptop Level Notes/Fedora/Fedora Basic Commands|Fedora Linux Cheat Sheet (Essential)]]

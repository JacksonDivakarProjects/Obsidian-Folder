To set up JDK (Java Development Kit) on Linux, you need to install it and configure the environment variables. Here’s a step-by-step guide:

---

### **Step 1: Install JDK**

You can choose **OpenJDK** or **Oracle JDK**. OpenJDK is easier and open-source.

**For Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install openjdk-17-jdk
```

(You can replace `17` with the version you need.)

**For Fedora/RHEL:**

```bash
sudo dnf install java-17-openjdk-devel
```

**Check installation:**

```bash
java -version
javac -version
```

---

### **Step 2: Set environment variables**

You need to set `JAVA_HOME` and update `PATH`.

1. Find where Java is installed:
    

```bash
update-alternatives --config java
```

This shows the path, usually something like `/usr/lib/jvm/java-17-openjdk-amd64`.

2. Open your shell config file:
    

- For **bash**:
    

```bash
nano ~/.bashrc
```

- For **zsh**:
    

```bash
nano ~/.zshrc
```

3. Add these lines at the end:
    

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

4. Apply changes:
    

```bash
source ~/.bashrc
```

---

### **Step 3: Verify**

```bash
echo $JAVA_HOME
java -version
javac -version
```

---

This sets JDK globally for your user.

If you want, I can also show a **way to switch between multiple JDK versions on Linux easily**—super useful if you deal with multiple projects. Do you want me to do that?

## 🔗 Related Notes
- [[Laptop Level Notes/Fedora/Fedora Basic Commands|Fedora Linux Cheat Sheet (Essential)]]
- [[Laptop Level Notes/Set Jupyter Kernel/Set env to kernel|Set env to kernel (Jupyter Kernel)]]

# Alias With `.bashrc`

How to create a persistent shortcut command (alias) so a project can be launched from anywhere, using the Alias method.

### 🔧 How to Run a Project via a `.bashrc` Alias

1. **Open `.bashrc`:**
```bash
nano ~/.bashrc
```

2. **Add this line at the bottom:**
```bash
alias runmyproject='python3 /home/jack/my_project/app.py'
```
> Replace the path with the actual script location.

3. **Save and exit** (in `nano`):
- `Ctrl + O` → Enter (save)
- `Ctrl + X` (exit)

4. **Apply the changes** without restarting the terminal:
```bash
source ~/.bashrc
```

5. **Run the project from anywhere:**
```bash
runmyproject
```

## 🧠 Notes

- Aliases defined this way persist across terminal sessions and reboots, since `.bashrc` is re-sourced for every new interactive shell.
- Aliases typed directly at the prompt (without editing `.bashrc`) only last for the current session.
- `.bashrc` runs for interactive non-login shells; if the alias needs to be visible from login shells or scripts too, consider `.bash_profile`/`.profile` or a dedicated function/script on the `PATH` instead.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/Concept Oriented Files/CHMOD|CHMOD]]
- [[Data Engineering Role Notes/Linux/Concept Oriented Files/Find Command|Find Command]]
- [[Data Engineering Role Notes/Linux/Linux Summary Guide|Linux Masterclass Concepts]]

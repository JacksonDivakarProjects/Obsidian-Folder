# Linux Masterclass Concepts

*Source: notes from a Tamil-language "Linux Masterclass" video course (instructor: Gautham, 11 years in Big Data Engineering).*

This masterclass covers foundational, intermediate, and advanced Linux knowledge relevant to roles such as Data Engineer, Software Engineer, Data Analyst, Data Scientist, and AI/ML Engineer.

## 1. Why Linux Is Essential
*   **Work Environment:** Nearly all servers run on Linux because it is free and open-source. If your server is Linux, you must know Linux.
*   **Industry Standard:** Linux is used everywhere — distributed environments, computing clusters, cloud platforms (AWS, Azure, GCP), DevOps, supercomputers, and smartphones (Android is Linux-based).
*   **Career Advantage:** Linux questions may not dominate interviews, but comfort with Linux makes a strong impression with colleagues and managers, since many freshers lack this skill. It's as foundational as knowing how to open a folder in Windows.
*   **Remote Servers:** Connecting to a remote Linux server almost always means a **command-line interface (CLI)** — there is no GUI. Commands are the only way in.

## 2. Core Concepts
*   **Open Source:** Software that is free to use, modify, and redistribute. Anyone can build on the code and release new versions; authorship is tracked via platforms like GitHub or licensing bodies such as Apache, the Free Software Foundation (FSF), and the Open Source Initiative (OSI).
*   **Linux vs. Unix:**
    *   **Linux:** Free, open-source OS kernel based on Unix principles, created by Linus Torvalds in 1991, developed by the community. Distributions include Ubuntu, Fedora, CentOS, Arch Linux, Kali Linux.
    *   **Unix:** Proprietary, closed-source, commercial, usually tied to specific hardware, vendor-driven. Examples: Solaris, AIX, HP-UX. Far less common than Linux in data engineering, data science, and AI environments today.
*   **Linux and Viruses:** Linux's permission model makes it more secure by design, but it is **not immune** to malware or attacks. Threats are rarer than on Windows, but enterprise systems still run security and hardening tools.
*   **Linux as a Kernel:** Linux itself is technically a **kernel** — the core engine of an operating system, responsible for CPU scheduling, memory allocation, I/O, device management, and hardware/software interaction. A full OS combines the kernel with utilities, a shell (e.g. Bash), package managers, and optional GUI tools. "Linux distributions" (Ubuntu, Fedora, etc.) are complete operating systems built around this kernel.

## 3. Basic Commands
*   `pwd` — Print Working Directory; shows the current path (e.g. `/home/ubuntu`). `/home/<username>` is the user's home directory.
*   `uname -a` — Displays system info: OS name, kernel version, architecture (e.g. `x86_64` for 64-bit).
*   `whoami` — Displays the current username.
*   `clear` (or `Ctrl+L`) — Clears the terminal screen.
*   `history` — Lists previously executed commands.

## 4. File and Directory Management
*   `mkdir <dir>` — Creates a directory. `mkdir -p a/b/c` creates nested directories recursively.
*   `cd <dir>` / `cd` (home) / `cd ..` (up one level) / `cd ../..` (up multiple levels) / `cd -` (previous directory).
*   `vi <filename>` — Opens/creates a file in the VI editor.
    *   `i` — enter **INSERT** mode.
    *   `Esc` — exit INSERT mode back to command mode.
    *   `:wq` + Enter — save and quit.
    *   `:q!` + Enter — quit without saving.
    *   `dd` (twice, in command mode) — delete the current line.
*   `vim` — An enhanced `vi` with arrow-key navigation and syntax highlighting. Install with `sudo apt-get install vim`.
*   **Tab-completion:** Type the first few characters of a file/directory name and press `Tab` to auto-complete; press `Tab` twice to list all matching options.
*   `nano <filename>` — A simpler text editor; type directly, then `Ctrl+X` to exit, `Y` to save, `Enter` to confirm the filename.
*   **Copy/paste in a terminal:** `Ctrl+Shift+C` / `Ctrl+Shift+V` (Linux terminal); select + right-click (PuTTY); `Ctrl+C` / `Ctrl+V` (Mac terminal).
*   `touch <filename>` — Creates an empty file (or updates its timestamp if it exists).
*   `rm <filename>` — Removes a file. `rm *.txt` removes all files with that extension; `rm H*` removes files starting with `H`; `rm *` removes everything in the directory; `rm -rf <dir>` recursively force-removes a directory and its contents — use with extreme caution, there is no undo.
*   `cat <filename>` — Prints file contents to the terminal.
*   `cp <source> <destination>` — Copies a file.
*   `mv <old> <new>` — Moves or renames a file (Linux has no separate `rename` command for this; `mv` covers it).

## 5. Linking Files
*   **Hard link** (`ln <original> <link_name>`) — A second name pointing at the **same underlying data block/inode**. Deleting one link does not remove the data until every link referencing it is gone. `ls -l` shows the hard-link count in its second column.
*   **Soft (symbolic) link** (`ln -s <original> <link_name>`) — A separate file that stores the **path** to the original. If the original is deleted or moved, the symlink breaks ("dangling link"). `ls -l` shows a soft link with a leading `l` and an arrow to its target.

## 6. Aliases
*   `alias name='command'` — Creates a shorthand for a longer command or command chain.
*   **Persistence:** Aliases typed directly into the terminal only last for that session. To make one permanent, add it to a shell config file such as `.bashrc` or `.profile`.
*   `source ~/.bashrc` (or `. ~/.bashrc`) — Re-reads `.bashrc` to apply changes immediately, without restarting the terminal.

## 7. Background Processes and Process Management
*   `nohup <command> > <log_file> 2>&1 &` — Runs a command in the background, immune to hang-up signals (e.g. closing the terminal or losing the SSH connection). Output is redirected to a log file instead of the terminal.
*   `top` — Real-time view of running processes and resource usage, similar to Windows Task Manager.
*   `ps` — Snapshot of running processes.
    *   `ps aux` (commonly typed `ps -aux`, which works via BSD-style compatibility) — shows processes for **a**ll users, in a **u**ser-oriented format, including processes with no controlling terminal (**x**) — i.e. background/daemon processes too.
*   `tail -f <filename>` — "Follows" a file, printing new lines as they're appended (useful for live log monitoring).
*   `tail -n <N> <filename>` / `head -n <N> <filename>` — Last/first N lines of a file (default 10 lines if `-n` is omitted).
*   `kill -9 <PID>` — Forcefully terminates a process by its Process ID (find the PID via `ps aux` or `top`).
*   `grep <pattern> <file(s)>` — Searches for lines matching a text pattern.
    *   `grep -i` — case-insensitive search.
    *   `grep -v` — inverse match (lines that do *not* contain the pattern).
    *   `grep <pattern> *.ext` — search across multiple files by extension.
    *   `grep -R <pattern> <dir>` — recursive search through a directory tree.
    *   **Piping (`|`)** — feeds one command's output into another as input (e.g. `ps aux | grep python`).

## 8. File Download
*   `wget <URL>` — Downloads a file from a URL into the current directory (needs network access and firewall permissions).

## 9. System Resource Monitoring & Compression
*   `df -h` — **D**isk **f**ree space per mounted filesystem, human-readable (GB/MB).
*   `du -sh <path>` — **D**isk **u**sage of a directory/file, summarized and human-readable.
*   `zip <output>.zip <input>` — Compresses files/directories into a `.zip` archive (`-r` to recurse into directories).
*   `unzip <archive>.zip` — Decompresses a `.zip` archive.
*   `tar -cvf <output>.tar <input>` — Archives files/directories (`-c` create, `-v` verbose, `-f` archive filename).
*   `tar -xvf <archive>.tar` — Extracts a `.tar` archive (`-x` extract).
*   `free -m` / `free -g` — System RAM usage in megabytes/gigabytes.
*   `sudo sh -c "sync; echo 3 > /proc/sys/vm/drop_caches"` — Frees cached/buffer memory (used by sysadmins). Note the `sh -c "..."` wrapper: running `sudo echo 3 > /proc/sys/vm/drop_caches` directly does **not** work, because the `>` redirection is opened by your own unprivileged shell *before* `sudo` runs the command — only `echo` runs as root, not the redirection into a root-only file. Wrapping the whole pipeline in `sudo sh -c "..."` makes the redirection happen as root too.

## 10. File Content Analysis
*   `wc <filename>` — **W**ord **c**ount: lines, words, and characters. `wc -l` / `-w` / `-c` isolate lines/words/characters respectively.
*   `sort <filename>` — Sorts lines alphabetically. `sort -r` reverses the order; `sort -n` sorts numerically.

## 11. SSH & SCP
*   **SSH (Secure Shell)** — connects to a remote Linux system: `ssh <username>@<IP_or_hostname>`. **PuTTY** is a popular free SSH client for Windows.
*   **SCP (Secure Copy)** — securely copies files between systems: `scp <source_path> <username>@<destination_IP>:<destination_path>`. **WinSCP** provides a graphical SFTP/FTP/SCP client for Windows with drag-and-drop transfers.

## 12. `find` Command
*   `find . -name "<pattern>"` — Searches for files/directories by name from the current directory (`.`); wildcards (`*`) are supported.
*   `find . -type f -size +10M` — Finds **f**iles larger than 10 MB.
*   `find . -mtime -1` — Finds files **m**odified within the last 24 hours (`-1` = less than 1 day old).
*   `find . -empty` — Finds empty files or directories.
*   `find . -name "*.tmp" -delete` — Finds and **deletes** `.tmp` files. Use `-delete` with extreme caution — there's no confirmation prompt.
*   **`find` vs. `grep`:** `find` locates files/directories by *attributes* (name, size, type, mtime); `grep` searches for *text content inside* files.

## 13. `awk` Command
*   A pattern-action language for **processing columns and text** — filtering, computing, and reformatting data line by line. Think of it as a spreadsheet formula language for the terminal.
*   `awk '{print}' <file>` — prints every line.
*   `awk '{print $1}' <file>` — prints the **first column** (`$1` = field 1, `$2` = field 2, and so on; `NF` = number of fields, `NR` = current line number).
*   `awk -F',' '{print $1, $3}' <file>` — sets a custom **field separator** (comma) and prints selected columns.
*   `awk '$2 > 27 {print $1, $3}' <file>` — filters rows by a condition, then prints selected columns.
*   `awk` can also format output with headers and custom separators (see the dedicated AWK guides for `printf`, arrays, and `BEGIN`/`END` blocks).

## 14. Change Mode (`chmod`)
*   `chmod` changes file/directory **permissions**.
*   **Permission types:** Read `r` (value 4), Write `w` (value 2), Execute `x` (value 1).
*   **Permission categories:** User/owner (`u`), Group (`g`), Others (`o`); root (superuser) always has full access regardless of the mode bits.
*   **Octal notation:** a three-digit number, one digit each for User, Group, Others — the digit is the sum of the `r`/`w`/`x` values that apply:
    *   `0` — `---` (none)
    *   `1` — `--x` (execute only)
    *   `2` — `-w-` (write only)
    *   `3` — `-wx` (write + execute)
    *   `4` — `r--` (read only)
    *   `5` — `r-x` (read + execute)
    *   `6` — `rw-` (read + write)
    *   `7` — `rwx` (read + write + execute)
*   `chmod 755 <file>` — rwx for the owner, r-x for group and others (common for scripts/executables).
*   `chmod 777 <file>` — read/write/execute for everyone. Rarely appropriate — it's a security risk, which is why file managers often flag `777` files (e.g. highlighting them in green).
*   `chmod -R <mode> <dir>` — applies permissions **r**ecursively to a directory and everything inside it.

## 15. Scheduling
*   **Scheduling vs. automation:** Automation turns a manual process into a script (e.g. a Python job that reads a DB and writes a file). Scheduling decides *when* that automated task runs (e.g. every hour).
*   **Cron** — the standard time-based job scheduler on Unix-like systems.
    *   `crontab -e` — opens the current user's cron table for editing.
    *   **Cron syntax:** five fields — minute, hour, day of month, month, day of week — supporting wildcards (`*`) and step values (`*/2` = every 2 units). [crontab.guru](https://crontab.guru/) helps build and read these expressions.
    *   Cron jobs run in the background, independent of any login session.
*   **Airflow** — an open-source platform to author, schedule, and monitor workflows (ETL pipelines) programmatically.
    *   Installable on Windows via WSL (Windows Subsystem for Linux, e.g. an Ubuntu install).
    *   Key components: a web server (UI) and a scheduler (runs DAGs).
    *   **DAGs (Directed Acyclic Graphs)** — workflows defined as Python code.
    *   **Operators** — define individual tasks inside a DAG (e.g. `BashOperator` for shell commands, `PythonOperator` for Python callables).
    *   **Metadata database** — stores task status and logs (SQLite by default; configurable to MySQL/PostgreSQL for production).
    *   **Schedule interval** — set on the DAG (e.g. `schedule_interval='*/5 * * * *'` for every 5 minutes).
    *   **`catchup=False`** — prevents Airflow from backfilling every missed run between the start date and now when a DAG is first enabled.
    *   A typical demo ETL: read from MySQL with Python, transform, write to CSV, and schedule the whole job in Airflow.
*   A **`while` loop** can act as a crude scheduler inside a script, but it's not production-appropriate — it's tied to the session/terminal and dies if the process or system stops.

## 16. Shell Scripting
*   **Purpose:** automate sequences of commands — small automation, scheduled jobs, or "wrapper scripts" that orchestrate other programs (Python scripts, database operations, email notifications, etc.).
*   **File extension:** typically `.sh` (e.g. `test.sh`).
*   **Shebang:** the first line `#!/bin/bash` tells the OS to run the script with the Bash interpreter.
*   **Running a script:** `bash script.sh` or `sh script.sh` (or `./script.sh` if it's executable — see `chmod +x`).
*   **Variables:** define with `NAME=value` (no spaces around `=`); read with `$NAME` (e.g. `echo "Hello $NAME"`).
*   **User input:** `read <variable>` reads a line of input into a variable.
*   **Conditionals:** `if [ <condition> ]; then <commands>; else <commands>; fi`, using operators like `-gt` (greater than) or file tests like `-f "<filename>"`. See [[Data Engineering Role Notes/Linux/Bash Scripting/Bash if Condition|Bash if Condition]] for the full set.
*   **Loops:** `for i in 1 2 3 4 5; do echo "Looping number $i"; done`. See [[Data Engineering Role Notes/Linux/Bash Scripting/Looping Conditions|Looping Conditions]] for `while`/`until` and loop control.
*   **Functions:** can be defined and called within a script like any other language.
*   **Positional arguments:** `$1`, `$2`, etc. hold arguments passed to the script; `$0` is the script's own name.

---

**Analogy for Linux's role:** think of Linux as the backbone of a massive city's high-speed rail system. You (the developer) mostly interact with specific buildings (applications) or drive your own car (a local OS like Windows/Mac), but the underlying rail network (Linux servers) is what actually moves the goods and services (data and applications) across the whole city — usually without anyone needing a fancy car (a GUI) to keep it running. Learning Linux commands is like learning to operate that rail network's control panel.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Linux/AWK/AWK - Comprehensive Practical Guide|AWK — Comprehensive Practical Guide]]
- [[Data Engineering Role Notes/Linux/Concept Oriented Files/CHMOD|CHMOD]]
- [[Data Engineering Role Notes/Linux/Concept Oriented Files/Find Command|Find Command]]
- [[Data Engineering Role Notes/Linux/nohup (Background Process)/nohup Guide|The Complete nohup Guide for Beginners]]
- [[Data Engineering Role Notes/Linux/Concept Oriented Files/Alias with .bashrc|Alias with .bashrc]]

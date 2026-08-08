Perfect. Let’s explode **Part 1** – the absolute core of Claude Code’s technical architecture.

---

# Deep Dive: The Agentic Loop & Built-in Tools

**Why this matters most:**  
Every single interaction with Claude Code is governed by this loop. If you misunderstand it, you waste tokens, fight the tool, or get unexpected results. If you master it, you can predict and control Claude’s behavior with precision.

---

## 1. The Loop Mechanics (Exactly What Happens)

When you press Enter after a prompt, here’s the sequence:

### Step-by-step flow
1. **Context assembly** – Claude gathers:
   - System prompt (unchangeable, defines tool usage rules and safety)
   - Your `CLAUDE.md` and `CLAUDE.local.md`
   - Conversation history
   - Current workspace metadata (file tree, Git status)
2. **Model inference** – Claude generates a response. That response can be:
   - A text message (thinking aloud, explanation, question)
   - A tool call (or multiple tool calls in one turn)
   - A mix: text first, then tool call
3. **Tool execution** – If a tool call is issued, Claude Code’s runtime (not the model) executes it:
   - Permission check (prompt or block)
   - Run the tool, capture stdout/stderr/exit code
   - Return the result as a new “tool result” message in the conversation
4. **Observation** – The model sees the tool result and decides next step.
5. **Loop** – Steps 2–4 repeat until:
   - Model generates a text message without a tool call (task complete)
   - `--max-turns` is reached (forced stop)
   - You interrupt with Ctrl+C
   - A hook or permission denial terminates the turn

**Critical insight:** The model doesn’t “remember” tool outputs between turns unless the output is fed back into the context window. Long tool outputs can overflow context, causing older parts to be dropped. This is why `Read` often returns truncated results – to preserve context.

---

## 2. The Built-in Tools – Comprehensive Breakdown

Tools are not mere functions; they are the model’s limbs. The model chooses *which* tool to call, with *what* arguments, based on its reasoning. Misunderstanding a tool’s constraints leads to failed calls or infinite loops.

### 2.1 `Read` – The Eyes

- **Signature:** `Read(file_path, offset?, limit?)`
- **Behavior:** Reads a file starting at `offset` line (1-indexed), up to `limit` lines. If offset/limit omitted, it reads a chunk (usually first 100-200 lines, then subsequent calls auto-increment). It never reads the entire huge file in one go.
- **Key nuance:** The model doesn’t know the total file length; it only sees what’s returned. It must use multiple `Read` calls or `Grep` to locate content. A common pattern: `Grep` to find a line number, then `Read` to view surrounding context.
- **Pitfall:** The model might call `Read` on a file path that no longer exists because it “remembers” an old file structure. Always encourage it to `Glob` before assuming paths.
- **Pareto tip:** When asking Claude to explain a bug, explicitly tell it: “First grep for the error message, then read the surrounding 50 lines.” This cuts needless token consumption.

### 2.2 `Write` – Full File Replacement

- **Signature:** `Write(file_path, content)`
- **Behavior:** Overwrites the entire file. If the file doesn’t exist, creates it. There’s no diff; it’s a total substitution.
- **Why it’s dangerous:** If the model hallucinates a slightly different version of a 500-line file and `Write`s it, you lose any manual changes you made. The only safety net is your version control and the permission prompt.
- **When to use:** Creating new files, or when you *know* the file is small and you want a clean slate (e.g., config files). For existing code, `Edit` is almost always safer.
- **Pareto rule:** Never allow `Write` without a preceding `Read` of the same file. Enforce this via prompt: “Before writing any existing file, show me the diff.”

### 2.3 `Edit` – Surgical Diff

- **Signature:** `Edit(file_path, old_string, new_string)`
- **Behavior:** Finds the first exact occurrence of `old_string` in the file and replaces it with `new_string`. If `old_string` is not unique, the tool call fails with an ambiguity error. Whitespace and indentation must match perfectly.
- **How the model constructs it:** The model copies a snippet from its own knowledge or from a recent `Read`. If the snippet is slightly off (e.g., extra space), `Edit` fails. Claude then re-reads the file, fixes the string, and retries – costing turns.
- **Pro strategy:** Always ask Claude to “Read the specific function you’ll edit, then use Edit with the exact text shown.” This minimizes retries. You’ll see a noticeable speed boost.
- **Advanced:** `Edit` can replace multiple lines at once, enabling refactors like renaming a variable across a block, as long as the old block is a contiguous unique string.

### 2.4 `Bash` – The Command Line

- **Signature:** `Bash(command, workdir?)`
- **Behavior:** Executes a shell command in a subprocess. The shell is the user’s default shell (bash, zsh, etc.). The tool captures stdout, stderr, and exit code. The command can be any valid shell script, including pipes, redirects, and conditionals.
- **Permissions:** This is the most restricted tool. You can configure it to `deny` globally, or `ask` (default). Each invocation requires you to approve it, with options to permanently allow that specific command in that directory.
- **Workspace access:** The command runs in the project root by default, so it sees all files. Use `workdir` to scope it.
- **Crucial nuance:** The model sees the exit code. If a command fails (non-zero exit), the model often re-reads the output and tries a corrected command. This is how it self-corrects. Encourage it with: “If the command fails, analyze the error and retry intelligently.”
- **Pareto principle:** Never approve a `Bash` command that contains destructive operations (`rm`, `chmod`, `sudo`) unless you fully understand it. Use plan mode first.

### 2.5 `Glob` – File Search by Pattern

- **Signature:** `Glob(pattern)`
- **Behavior:** Returns a list of file paths matching the glob pattern (e.g., `**/*.test.ts`). Fast and cheap.
- **Use case:** Before any large-scale refactor, Claude should `Glob` to see the scope. “Find all test files” → `Glob **/*.test.ts`. This prevents the model from guessing file locations.
- **Pattern:** Supports standard glob syntax (brace expansion, etc.). Recursive with `**`.

### 2.6 `Grep` – Content Search with Regex

- **Signature:** `Grep(pattern, path?, include?, exclude?)`
- **Behavior:** Searches file contents for a regex pattern. Returns matching lines with file path and line number. Can scope to a directory (`path`) or filter by glob (`include`/`exclude`).
- **Regex engine:** RE2 (fast, linear-time, but doesn’t support backreferences or lookaheads). If the model uses a complex regex that RE2 rejects, the tool call fails. Tell Claude: “Use simple regex, avoid lookaheads.”
- **Pareto tip:** Combine `Grep` and `Read`. First grep for a unique string, then read the file at the returned line numbers. This is the fastest way to navigate a large codebase.

### 2.7 `TodoWrite` – The Agent’s Scratchpad

- **Signature:** `TodoWrite(todos: [])`
- **Behavior:** Stores a JSON list of tasks (each with `id`, `status`, `content`) in the conversation’s ephemeral memory. It is *not* visible in the file system. It’s meant for the model to track complex multi-step plans.
- **Why it’s critical:** When you give a huge task like “migrate all Redux to Zustand”, without `TodoWrite` the model might forget intermediate steps, repeat work, or go down rabbit holes. `TodoWrite` forces it to break the work into chunks and update statuses, giving you visibility.
- **Visible to you:** You can ask “show me your todo list” and Claude will output it. Use this to check progress.
- **Pareto rule:** For any task longer than one turn, explicitly say: “Use TodoWrite to plan and track your progress. Update it after each step.”

### 2.8 `Task` – Sub-Agent Launcher (Already detailed, but here’s how it fits the loop)

- **In the loop context:** When the model calls `Task`, the parent pauses. The child runs its own loop (with its own `TodoWrite`, tool calls, etc.) and returns a final message. The parent then continues its loop with that message injected as a tool result.
- **Limits:** Child has its own `--max-turns` (default 10). If it times out or errors, the parent sees the error message and can decide to retry or adjust.

### 2.9 `WebSearch` – Fetch Live Web Content

- **Behavior:** Performs a web search (like “how to fix X in Next.js 14”) and returns the top results as text snippets. It’s a headless browser; the model sees no images, only extracted content.
- **When to use:** When you need the *latest* documentation, or troubleshooting an obscure error. Disable it for offline/sensitive work.
- **Pitfall:** It can return outdated or hallucinated snippets from forums. Always ask Claude to cite the source URL so you can verify.

### 2.10 `NotebookEdit` – Jupyter-specific

- Only relevant if you’re working in a `.ipynb` environment. Otherwise, ignore.

---

## 3. Optimizing the Loop – Patterns That Save Time & Tokens

Here is the 20% of prompting patterns that give 80% of performance gains:

### 3.1 The “Read-Plan-Edit” Golden Sequence
Instead of “refactor this function to async”, say:
> “First, read the file containing the function. Then write a plan using TodoWrite. Show me the plan. After I approve, proceed with Edit changes one by one.”

This eliminates blind rewrites, minimizes re‑reads, and gives you full control.

### 3.2 Explicit Tool Invocation
You can directly command Claude to use a specific tool:
> “Grep for all occurrences of ‘deprecatedFunction’ and list them with file paths and lines.”
Claude will do exactly that, no guesswork.

### 3.3 Error Recovery Loop
When a `Bash` command fails, Claude will typically try to correct it. But you can enhance this with:
> “If a command fails, read the error output, explain why it failed, propose a fix, and then run the fixed command.”

### 3.4 Parallel Tool Calls
Claude can issue multiple independent tool calls in one turn (e.g., `Read` two files at once, or `Grep` plus `Glob`). Encourage this:
> “Read file A and file B simultaneously.”
This cuts turns in half for exploration-heavy tasks.

### 3.5 Context Window Management
If you notice Claude re‑reading files excessively, the context window may be full. Say: “Summarize your understanding so far, then continue.” This forces it to compact knowledge into a summary, freeing up space.

---

## 4. Failure Modes and How to Diagnose Them

| Symptom | Root Cause | Fix |
|--------|-----------|-----|
| Claude loops, re-reading the same file endlessly | Context window overflow, it forgets earlier reads | “Stop re-reading, summarize what you know so far.” |
| `Edit` fails with “string not found” repeatedly | Old `Read` data in context, file changed on disk | “Read the file again and use the exact current text.” |
| Tool calls seem random/irrelevant | The model lost track of the goal (task drift) | “Re-read my original request and restart your plan.” |
| Sub‑agent returns nothing useful | Child timeout or too restrictive tool set | “Give the sub-agent Read and Grep tools and increase max turns.” |
| High token usage with little output | Excessive sub‑agent spawning or verbose reasoning | “Don’t use sub-agents unless necessary. Be concise.” |

---

## 5. One-Liner Cheat Sheet for Power Users

- **Never Write without a preceding Read.**
- **Edit requires exact string; always force a fresh Read before critical edits.**
- **Glob + Grep = your exploration engine; use them before any refactor.**
- **TodoWrite is mandatory for tasks with >1 step; demand it.**
- **Plan mode (`/plan`) for anything touching >5 files; you’ll thank me.**
- **Bash permissions: permanent‑allow only safe commands (`git status`, `ls`), ask for everything else.**
- **When stuck, tell Claude to “pause, explain your reasoning so far, and then I’ll guide you.”**

---

This is the engine. Master it, and everything else (hooks, MCP, custom commands) becomes a simple extension of this loop. If you want me to go deeper into any tool’s internal behavior (like how `Edit` handles ambiguous matches with examples, or the exact Bash sandboxing internals), just say the word. Otherwise, ready for Part 2.

## 🔗 Related Notes
- [[Claude Code/Introduction to Claude Code|Claude Code – The Pareto Reference (Maximum Output)]]
- [[Claude Code/Part 2 Sub Agent, Operating Modes and Permission Safety Net|Part 2 – Sub-Agents, Operating Modes & the Permission Safety Net]]
- [[Claude Code/Part 3 Memory, Claude.md and the Context Engine|Part 3 – Memory, CLAUDE.md, and the Context Engine]]

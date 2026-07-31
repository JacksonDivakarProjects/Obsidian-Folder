
# Claude Code – The Pareto Reference (Maximum Output)

> This is not a beginner's walkthrough. It assumes you can install and launch the tool. It’s the dense, operational knowledge you actually need to reason about, control, and exploit Claude Code’s internals. Every section answers: **How does it really work, and why should I care?**

---

## 🥇 Top 20% – The Core Loop (80% of your daily usage & troubleshooting)

These concepts directly determine Claude's behavior, safety, and output quality. Master these first.

### 1. The Agentic Loop + Built-in Tools (The Engine)

This is **the single most important mental model**. Forget it, and you’ll fight the tool.

**How it works:**
- Claude runs a **closed loop**: it reasons, picks a tool, observes the result, reasons again, picks another tool, etc., until it believes the task is done.
- The loop is driven by a system prompt that tells the model to use `TodoWrite` to plan and track progress.
- Every step is a “turn”. You can cap turns with `--max-turns` (default ~25) to prevent runaway loops.

**The tool set is fixed.** You cannot extend it directly (except via MCP, see later). The model decides *which* tool to invoke.

| Tool | What it does | Critical nuance |
|------|--------------|-----------------|
| **Bash** | Executes shell commands. | Permission-gated. Always printed for your approval. The model can see stdout/stderr and exit code. |
| **Read** | Reads file content (line range). | Supports `offset` and `limit`; model can ask for specific lines. |
| **Write** | Overwrites an entire file. | Destructive! Model must provide complete new content. Used for new files and full rewrites. |
| **Edit** | Surgical find-and-replace in an existing file. | Works like `sed` with a diff hunk. Much safer than Write, but model must construct a precise old/new string. |
| **Glob** | Finds files by pattern. | Used to explore directory structure. |
| **Grep** | Searches file contents by regex. | Returns matching lines with file paths and line numbers. |
| **WebSearch** | Fetches live web pages. | Can be disabled; uses a headless browser instance. |
| **Task** | Spawns a sub-agent (see §2). | Passes a prompt and a set of allowed tools; runs in the background. |
| **TodoWrite** | Writes an internal task list. | Not visible in the file system; it’s the agent’s scratchpad for planning. |
| **NotebookEdit** | Edits Jupyter notebooks. | Only relevant in specific environments. |

**Pareto takeaway:**  
Understand the `Bash` / `Read` / `Edit` / `Write` loop. Almost every problem arises because you didn’t specify tool usage constraints, didn’t check the permission model, or didn’t read the diff. **Always ask Claude to first read, then plan (`TodoWrite`), then edit.**

---

### 2. Sub-Agents (Task Tool) – The Real Power Multiplier

This is **agent delegation**, not just a function call. Misunderstanding it leads to confusion about “why is Claude doing weird things in the background?”

- `Task` launches a **separate Claude process** (with its own context window, own tool set, own max turns) to handle a sub-problem.
- The parent agent sends a prompt and can restrict which tools the child gets (e.g., only `Read`, `Glob`, `Grep` – no file writes).
- The parent waits for the child’s final message (or error/timeout) and then incorporates the result into its own reasoning.
- **You don’t see the child’s intermediate steps** unless you inspect logs. The parent summarizes the child’s output.

**When they excel:**
- Large codebase exploration: parent asks child “find all places where auth logic is called and summarize each”.
- Parallel independent tasks: parent spawns two children, one to audit security, one to refactor tests.
- Isolation: risky operations (e.g., deleting files) can be delegated to a child with a tightly scoped prompt and limited tool access.

**Critical detail:** Sub-agents consume **extra API turns** and count toward your usage. Each child can have its own `--max-turns` (default 10). If you see high token usage for no apparent output, suspect an over-eager parent spawning too many children.

**Pareto takeaway:**  
For any task bigger than a single file edit, explicitly tell Claude: *“First, explore with a sub-agent. Then propose a plan. Then edit.”* This alone cuts token waste and improves safety.

---

### 3. Operating Modes – Safety & Automation Levers

Modes change the entire interaction contract. You can switch mid-session.

| Mode | Trigger | What changes |
|------|---------|--------------|
| **Interactive (default)** | `claude` or inside a session | Full loop, permission prompts, you see tool calls and diffs. |
| **Plan Mode** | `claude --plan` or typing `/plan` in session | Read-only. Claude can only use `Read`, `Glob`, `Grep`, `WebSearch`, and `TodoWrite`. **No file changes, no Bash.** It produces a detailed plan, then pauses. You can then exit plan mode (`/plan` off) to execute. |
| **Non-interactive** | `claude -p "prompt"` | Single prompt, final answer only, no chat. Tool use is auto-approved within a safety envelope (you can pre-allow tools in settings). Use with `--output-format json` for scripting. |
| **Dangerously Allow All Bash** | `claude --dangerously-allow-all-bash` | All Bash commands run immediately, no prompts. **Only in sandboxes.** |
| **Print with max turns** | `claude -p --max-turns 5 …` | Non-interactive but allows multi-step reasoning before returning final output. |

**Why Plan Mode is Pareto-critical:**  
The number one mistake is letting Claude modify files before you’ve validated its understanding. Plan mode forces a dry run. Use it for any refactor touching >5 files. You’ll catch hallucinations early.

**Non-interactive for CI/CD:**  
Use `claude -p --max-turns 10 "Review this PR diff for security flaws"` inside a GitHub Action. Set permissions in `.claude/settings.json` to allow `Read`, `Grep`, and `Bash` for safe commands only (e.g., `git diff`). You’ll get automated, structured feedback.

---

### 4. Memory & CLAUDE.md – Context Is Everything

Claude’s output quality depends 80% on the context you provide. The memory system ensures context persists across sessions without you repeating yourself.

| File / Mechanism | Scope | Use this for… |
|------------------|-------|---------------|
| `CLAUDE.md` | Project‑wide, **version controlled** | Build commands, test commands, code style, architecture decisions, “don’t edit these files”, “use Python 3.11”, “our API is at …”. Claude reads it at session start. |
| `CLAUDE.local.md` | Local, **gitignored** | Personal preferences, local paths, secrets‑free environment quirks (e.g., “my npm is aliased to pnpm”). |
| Session memory | Ephemeral, per conversation | Temporary facts: “remember we’re debugging issue #42”. Use `/remember`. Lost on exit. |
| `.claude/settings.json` | Configuration, not memory | Tool permissions, hooks, model selection, custom commands path. Not for facts about the codebase. |

**Pro tip:** In `CLAUDE.md`, use Markdown headings and code blocks. The model parses it literally. Example snippet:

```markdown
# Project Commands
- Build: `npm run build`
- Lint: `npm run lint`
- Test: `npm test -- --coverage`

# Architecture Rules
- Never modify files in `vendor/`.
- Use `snake_case` for database columns.
- All async functions must have try/catch.
```

**Pareto takeaway:**  
Invest 5 minutes writing a solid `CLAUDE.md` once. It will save hours of clarification in every future session.

---

### 5. Permissions & Safety – The Invisible Guardrails

Claude can `rm -rf /` if you let it. The permission system prevents accidents while remaining flexible.

**Layers (top to bottom):**

1. **Tool permission in settings** – Global/project `.claude/settings.json` can set `allow`, `deny`, or `ask` for each tool. If you set `Bash` to `deny`, Claude can’t even suggest a command.
2. **Directory scope** – You can restrict file read/write to specific paths. If Claude tries to escape, the tool call is blocked.
3. **Interactive permission prompts** – In default mode, every `Bash` call is shown and requires a one‑time `Allow` / `Deny` / `Allow for this directory`. You can also permanently allow a command pattern via the prompt interface.
4. **Plan mode** – Overrides all tools that modify files or execute commands, regardless of settings, until you exit plan mode.
5. **`--dangerously-allow-all-bash`** – Removes all Bash checks. For Docker containers with no network access only.

**Common mistake:**  
Setting `Bash` to `allow` globally, then being surprised when Claude runs `npx install` on a malicious package suggestion. **Better pattern:** keep it `ask`, and permanently allow specific safe commands (like `git status`) via the interactive dialog.

**Pareto takeaway:**  
Never trust a brand-new project without Plan Mode first. After you’ve established trust, selectively lower permissions. This alone prevents 90% of “AI deleted my code” horror stories.

---

## 🥈 The Next 40% – Capabilities That Differentiate Experts

These extend the core loop into custom workflows, automation, and external integration.

### 6. Hooks – Enforce Rules Automatically

Hooks are shell scripts triggered on lifecycle events. They run **locally**, not inside Claude’s sandbox.

**Events:**
- `PreToolUse`: Before any tool runs. Can inspect the tool name and arguments. If your script exits non‑zero, the tool call is blocked.
- `PostToolUse`: After a tool completes. Can read the tool’s output. Ideal for linting, formatting, or custom logging.
- `PreChat` / `PostChat`: Before/after user‑Claude interaction. Rarely needed.

**Configuration in `.claude/settings.json`:**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "command": "eslint --fix ${CLAUDE_TOOL_OUTPUT_FILE} && git add ${CLAUDE_TOOL_OUTPUT_FILE} || exit 1"
      }
    ]
  }
}
```
Environment variables provided: `CLAUDE_TOOL_NAME`, `CLAUDE_TOOL_INPUT`, `CLAUDE_TOOL_OUTPUT_FILE` (for Write/Edit), etc.

**Pareto value:** A single PostToolUse hook that runs your linter after every file edit eliminates entire categories of bugs without you ever asking.

---

### 7. MCP (Model Context Protocol) – Connect Claude to Anything

MCP turns Claude from a file‑system agent into a full development environment.

- You run an **MCP server** (a process implementing the protocol). It can expose resources (like “database schema”) and tools (like “query_github_prs”).
- Claude Code connects as a client via `stdin/stdout` or WebSocket.
- Definition in `~/.claude/mcp.json` or project `.claude/mcp.json`:
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-github"],
      "env": { "GITHUB_TOKEN": "..." }
    }
  }
}
```
- Once connected, the tools appear in Claude’s available tool list, same as `Bash`, `Read`, etc.

**Why this matters at the Pareto level:** Without MCP, you copy‑paste external context (issue details, CI logs). With MCP, you say “fetch the latest 3 open bugs and propose fixes” – and Claude does it all internally. It’s a force multiplier for any workflow beyond single‑file edits.

---

### 8. Custom Slash Commands – Personal Macros

You can create new commands like `/review`, `/deploy`, `/onboard` by dropping a Markdown file into `.claude/commands/`. The filename (minus `.md`) is the command name. The body is the prompt.

Example `.claude/commands/review.md`:
```
Please review the current diff for bugs, security issues, and style violations. 
Focus on files changed in the last commit.
```
Then in a session, type `/review` to invoke it.

**Variables:** `$ARGUMENTS` gets the text after the command. `$INPUT` can capture piped content.

**Pareto thinking:** Create 3–5 commands for the 5 things you do in every project. You’ll never type those long prompts again.

---

### 9. System Prompts and Model Behavior Control

You can’t edit Claude Code’s core system prompt, but you **can** influence behavior through:
- `CLAUDE.md` (injected as part of the user context)
- Explicit instructions in the session: *“Never write comments in the code unless I ask.”*
- Model selection: use `--model claude-sonnet-4-20250514` for balanced reasoning vs. speed. Newer models may handle agentic tasks better but cost more.

**Practical tip:** If Claude keeps doing something you hate (e.g., adding “Here’s the updated file…” commentary), add a rule in `CLAUDE.md`: “Respond only with code diffs, no prose.” This is stored context and works every time.

---

## 🥉 The Remaining 40% – Situational Knowledge

These are valuable but less frequently needed or build upon the above.

- **IDE Integration (VS Code, JetBrains):** The IDE extension syncs with the terminal session. You can see diffs in-editor and approve them with a click. Setup is trivial, but the real power is still in the terminal.
- **CI/CD Integration:** Use `claude -p --output-format json` in GitHub Actions. Set `--max-turns` and restrict tools via settings. The JSON output can be parsed to post PR comments.
- **NotebookEdit:** Only for Jupyter users; same loop but operates on cell granularity.
- **WebSearch:** Useful for fetching current docs, but can be slow and hallucinate. Prefer giving Claude a static doc file when possible.
- **Bulk/Batch mode:** Non-interactive with a high `--max-turns` for long‑running automated refactors. Requires robust permission setup.

---

## ✅ Quick‑Review Checklist (Priority Order)

1. **Agent loop:** Tool selection → observe → repeat; `--max-turns`
2. **Tools:** `Bash`, `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Task`, `TodoWrite`
3. **Sub‑agents:** `Task` spawns isolated child, consumes extra turns
4. **Plan mode:** read‑only, `/plan` toggle
5. **Interactive / non‑interactive / dangerous** modes
6. **Memory:** `CLAUDE.md` (shared), `CLAUDE.local.md` (local), session memory
7. **Permissions:** allow/deny/ask, directory scope, plan mode override
8. **Hooks:** `PostToolUse` for auto‑linting
9. **MCP:** external servers add tools, configured in `mcp.json`
10. **Custom commands:** markdown in `.claude/commands/`
11. **System context:** `CLAUDE.md` + explicit instructions control behavior

---

This is your **maximum‑density reference**. Keep it open, search it, extend it. If you want me to explode any single concept into a full deep‑dive (e.g., “exact sub‑agent lifecycle with intercepted logs”, “building a secure MCP server for your internal API”), just name it.
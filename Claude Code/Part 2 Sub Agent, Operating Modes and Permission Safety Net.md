
Let’s continue with the next deep‑dive tier. Since you asked for “part 2” immediately after the Core Loop, I’m bundling the **two most critical extensions** of that loop: **Sub‑Agents** (how Claude delegates work) and **Operating Modes** (how you control the delegation’s boundaries). Together they form the actuator and the safety lever.

---

# Part 2 – Sub‑Agents, Operating Modes & the Permission Safety Net

*Everything in this section answers: **How does Claude parallelize, isolate, and constrain its work – and how do I stay in full control?***

---

## 1. Sub‑Agents – The `Task` Tool Dissected

The `Task` tool is not a function call. It’s a **fork**. A parent Claude process spawns a completely independent child Claude process, gives it a mission, and waits for a report. This architecture is what turns a single‑threaded assistant into a parallel problem‑solver.

### 1.1 The Fork Lifecycle (Step‑by‑Step)

1. **Trigger** – The parent model, during its agentic loop, decides “This sub‑problem is self‑contained enough to delegate”. It invokes `Task` with:
   - `prompt` (string): the instruction for the child.
   - `tools` (list of tool names): which tools the child may use (e.g., `["Read", "Grep", "Glob"]`). If omitted, the child inherits a safe subset.
   - `max_turns` (integer, optional): how many reasoning steps the child gets. Default is 10.

2. **Sandbox Creation** – The runtime spins up a child process. This child has:
   - Its own conversation context (contains the `prompt` as the first user message + a fresh system prompt).
   - Its own tool execution environment (same file system access, but scoped by the parent’s settings).
   - Its own `TodoWrite` scratchpad.
   - A hard limit on turns and wall‑clock time.

3. **Autonomous Execution** – The child runs **silently** in the background. You see no tool prompts, no diffs, no intermediate reasoning. It’s a black box until it finishes or dies.  
   *Only if the child hits an error (e.g., permission denied, turn limit) does the parent get an error message.*

4. **Result Return** – When the child terminates, it produces a final text response. This response is injected into the parent’s conversation as the tool output of the `Task` call. The parent then continues its own loop, reading this response like any other tool result.

5. **Parent Interpretation** – The parent sees the child’s report and decides whether it’s sufficient. If not, it may spawn a new child with a refined prompt, or fall back to doing the work itself.

### 1.2 Why Sub‑Agents Exist (The Engineered Reason)

Claude’s context window is finite. Massive codebase exploration (e.g., “find every place we handle user sessions and summarize the logic”) could flood the context with hundreds of file reads, losing the overall task. Sub‑agents **compress** that exploration into a single output message. The parent doesn’t see the individual reads – it sees a neat summary. This is the same principle as a manager who asks an analyst to “go research X and give me a one‑pager”.

### 1.3 Types of Delegation (With Pro Prompt Examples)

| Pattern | Parent’s instruction to child | When to use |
|--------|-------------------------------|-------------|
| **Exploration** | “Explore the `auth/` directory. List every exported function, its signature, and where it’s called.” | Understanding a new module or mapping dependencies. |
| **Audit** | “Review all `.ts` files in `src/` for missing try/catch on async functions. Return a list of violations with file:line.” | Security or style enforcement. |
| **Refactor (isolation)** | “In this specific file, rename variable `oldName` to `newName`. Do not touch any other files. Return the diff.” | Safe refactoring in a sandbox, parent can then apply the diff. |
| **Data gathering** | “Connect to the MCP server for GitHub, fetch the last 5 closed PRs, and summarize their changes.” | External data aggregation without cluttering parent context. |

**Parent prompt to initiate delegation:**
> “Launch a sub-agent with tools Read, Grep, and Glob. Have it explore the entire `services/` directory and return a structured report: service name, dependencies, and public methods. Max turns 15.”

### 1.4 Controlling Sub‑Agent Behavior (Settings & Limits)

You can’t directly interact with a child, but you can constrain it:

- **`max_turns`**: set it in the `Task` call or in `.claude/settings.json` (`"subagent_max_turns": 5`). If a child hits the turn limit, it returns what it has. A child that times out often indicates it was given too broad a task.  
- **Tool restrictions**: explicitly list allowed tools. Never give `Bash` or `Write` to a child unless absolutely necessary. The safest exploration child uses only `Read`, `Glob`, `Grep`.  
- **No cross‑child communication**: children don’t talk to each other. The parent must coordinate.  
- **Token billing**: child turns count against your API usage exactly like parent turns. A parent that spawns 3 children with `max_turns=10` each could burn 30+ turns in one prompt – silently. Always set conservative turn limits.

### 1.5 Failure Modes and Diagnostic Cues

| Symptom | What’s happening | Fix |
|--------|------------------|-----|
| Claude says “the sub-agent didn’t find anything” but you know the info exists | Child couldn’t access tools (e.g., `Grep` not allowed) or ran out of turns. | Increase allowed tools; simplify the sub‑prompt; inspect the child’s last message (if logged). |
| Huge token consumption, no visible progress | Parent spawning many children in parallel, each doing redundant work. | Tell Claude: “Use at most one sub-agent. Stop and summarize before spawning another.” |
| Sub‑agent returns garbled or incomplete summary | Child context overflowed; important file contents were truncated. | Instruct the child to “stop and summarize after every 5 files”. The parent can incorporate this. |
| Parent ignores child’s report and re‑does work manually | The model judged the child’s output as untrustworthy or irrelevant. | Ask: “Why did you ignore the sub-agent’s finding? Explain the discrepancy.” |

### 1.6 Pro Strategy – The Three‑Phase Delegation Pattern

The most effective use of sub‑agents follows a strict rhythm:

1. **Parent plans** (`TodoWrite`) and identifies the sub‑problems.
2. **Parent spawns children** for each independent sub‑problem, with tight turn and tool limits.
3. **Parent synthesizes** the children’s reports, cross‑checks them, and proceeds with file edits.

This pattern prevents “spawning chaos” and ensures you can still abort safely after phase 2.

---

## 2. Operating Modes – The Explicit Contract with the Agent

If sub‑agents are the *who*, operating modes are the *how* and *when* Claude is allowed to act. They are not just flags; they fundamentally alter the tool‑permission‑prompt pipeline.

### 2.1 Interactive Mode (Default) – Full Agency, Full Visibility

- **How it works:** The loop described in Part 1. Every tool call that modifies the system (Bash, Write, Edit) triggers a permission prompt. You see the exact command, diff, or file write before it happens. You can allow, deny, or permanently allow for that directory.
- **Mental model:** You are the co‑pilot. Claude proposes, you approve or veto. This is the mode for all exploratory and critical work.
- **Pro tip:** In this mode, you can also intervene with natural language mid‑loop (e.g., “stop, that’s wrong, read file Y first”). The model incorporates your feedback immediately.

### 2.2 Plan Mode – Agency Suspended, Intelligence On

- **Trigger:** `claude --plan` on launch, or `/plan` inside a session. Toggle off with `/plan` again.
- **What changes under the hood:** The system prompt is altered to disallow any tool that could alter the file system or execute commands. Only `Read`, `Glob`, `Grep`, `WebSearch`, `TodoWrite`, and `Task` (with restricted tools) are permitted. **Bash, Write, Edit are completely locked out**, regardless of your settings.
- **Output:** Claude will explore, think, and present a step‑by‑step plan. Often it will use `TodoWrite` to structure the plan. The plan is just text; nothing is executed.
- **Why this is a superpower:** You can ask “How would you refactor this entire module?” without any risk of a premature destructive action. After you review the plan, you can either edit it (“skip step 4, it’s dangerous”) or toggle plan mode off and say “Proceed with step 1.”
- **Pareto rule:** Never, ever skip plan mode when touching more than 3 files or making architectural changes. It costs a few extra turns and saves hours of rollbacks.

### 2.3 Non‑Interactive Mode (Batch) – Agency, But No Conversation

- **Trigger:** `claude -p "prompt"` or `claude --print "prompt"`. Combine with `--max-turns`.
- **Key difference:** The session runs without your involvement. Tool calls that would normally prompt for permission are automatically allowed if the tool is set to `allow` in settings; if set to `ask`, the run fails. No chat loop, just a final text output.
- **Use case:** CI/CD pipelines, pre‑commit hooks, automated code review.  
  *Example:*  
  `claude -p --max-turns 5 --output-format json "Check the diff in the current branch for SQL injection vulnerabilities. Output a JSON array of findings with file and line."`
- **Safety:** Always test non‑interactive commands in plan mode first to see what tools it wants to use. Then adjust your `.claude/settings.json` accordingly.
- **Output control:** `--output-format json` gives you structured data; `--output-format stream-json` streams events. Ideal for integration.

### 2.4 Dangerously Allow All Bash – The “I Know What I’m Doing” Mode

- **Trigger:** `claude --dangerously-allow-all-bash`
- **Effect:** Every `Bash` command runs without any prompt. Not a single “Allow?” dialog. This includes `rm -rf /` if the model hallucinates it.
- **Intended environment:** Disposable Docker containers, completely isolated VMs, or strictly air‑gapped systems where you have full rollback capability.
- **What it does NOT do:** It does not disable the permission prompts for `Write` or `Edit`; those still prompt by default unless separately set to `allow` in settings. The flag is Bash‑only.
- **Pareto rule:** If you ever think “I’ll just use dangerously‑allow‑all to save time”, you’ve already lost. Use it only when the cost of destruction is zero.

---

## 3. Permissions – The Invisible Architecture

Permissions intersect deeply with modes and sub‑agents. They form a layered defense.

### 3.1 The Permission Resolution Order

When Claude wants to use a tool, the runtime checks:

1. **Global mode override** – If in Plan Mode, any destructive tool is rejected immediately.
2. **Tool‑level setting** (`.claude/settings.json`): `"permissions": { "Bash": "deny" }` – instantly blocks all Bash.  
3. **Directory scope** – If a file path violates the `"allowedDirectories"` list, the call is blocked.  
4. **Interactive prompt** – If the tool is set to `"ask"`, the prompt appears. You can then permanently allow the exact command (a signature is stored in `~/.claude/allowed-commands.json`).  
5. **Dangerous Bash flag** – If set, `Bash` bypasses the prompt but **only** for Bash.

### 3.2 Settings That Matter (Pareto selection)

In `.claude/settings.json`:

```json
{
  "permissions": {
    "Bash": "ask",
    "Write": "ask",
    "Edit": "ask",
    "Read": "allow",
    "Glob": "allow",
    "Grep": "allow",
    "WebSearch": "deny"
  },
  "allowedDirectories": ["/home/user/project"],
  "subagent_max_turns": 8,
  "dangerouslyAllowAllBash": false
}
```

**Why this works:**  
- All file‑altering tools are `ask` – you see every change.  
- Read, Glob, Grep are free – exploration is frictionless.  
- `WebSearch` denied – no external data leakage.  
- `allowedDirectories` restricts Claude to the project, so it can’t accidentally read your `.ssh` folder.

### 3.3 Permission Pitfalls in Sub‑Agents

A sub‑agent inherits the parent’s permission settings, but it **cannot prompt you**. So if a child needs `Bash` and it’s set to `ask`, the child’s call will fail with a permission error. Therefore, if you give a child `Bash` in its allowed tools, you must also set `Bash` to `allow` in the overall settings – or the child will die instantly. This is a common source of “sub‑agent did nothing” bugs.

**Best practice:** Never give children `Bash`. If you must, create a dedicated project profile with `Bash` set to `allow` and run it in an isolated environment.

---

## 4. Practical Synergy – Combining Modes & Sub‑Agents for Maximum Leverage

Here’s a real‑world flow for a complex task (e.g., “add two‑factor authentication to this Express app”):

1. **Start in Plan Mode** (`/plan`).  
   > “Explore the codebase with sub‑agents to understand current auth. Propose a step‑by‑step implementation plan.”  
   Claude spawns a child to explore `auth/` and `user/`, then presents a plan. You review it, remove a risky step.

2. **Exit plan mode** and say: “Proceed with step 1 and 2 using sub‑agents for isolated changes. Show me diffs before continuing.”  
   Claude spawns children to implement DB schema changes (Write) and route updates (Edit). Because you’re in interactive mode, you approve each diff.

3. **Test loop:** “Now run the test suite. If any test fails, spawn a sub‑agent to analyze failures and propose fixes.”  
   Claude runs `npm test` (Bash), sees failures, spawns an audit child, applies fixes, tests again – all with your oversight.

4. **Final review:** “Switch back to plan mode and prepare a PR summary. Then I’ll merge.”  
   Last step read‑only, safe.

This flow minimizes risk, parallelizes work, and keeps you as the decision‑maker.

---

## 5. One‑Liner Cheat Sheet for Sub‑Agents & Modes

- **Sub‑agents are forks; they compress exploration, not replace your judgment.**
- **Always restrict child tools to Read/Glob/Grep unless you have a death wish.**
- **max_turns is your budget – set it low (5–8) and increase only on need.**
- **Plan mode is a dry‑run; use it for every complex change, no exceptions.**
- **Non‑interactive mode needs pre‑allowed tools; test in plan mode first.**
- **Dangerously‑allow‑all‑bash is for disposable sandboxes, not your laptop.**
- **Permissions: allow exploration (Read/Glob/Grep) freely, gate destruction (Bash/Write/Edit) tightly.**
- **Children cannot prompt – never give them `Bash` if it’s set to `ask`.**
- **If a sub‑agent returns nothing, suspect permission denial or turn timeout.**

---

Part 2 complete. Part 3 will dissect **Memory, CLAUDE.md, and the Context Engine** – the layer that ensures Claude never forgets what matters. Ready when you are.
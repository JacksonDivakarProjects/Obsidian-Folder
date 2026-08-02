# Part 4 – Hooks & MCP: The Extension Architecture

*This part answers: **How do I program Claude Code’s behavior and connect it to the outside world – without waiting for a feature request?** Hooks give you lifecycle automation; MCP gives you infinite tools. Together, they turn Claude Code from a terminal agent into a fully integrated development platform.*

---

## 1. Hooks – Your Code, Running Alongside Claude’s Loop

Hooks are **shell scripts** that Claude Code executes automatically at four precise moments. They are the answer to “I wish Claude would always lint after editing” and “I want to block certain dangerous commands.”

### 1.1 The Four Lifecycle Events

| Event | Fires | Typical Use Case |
|-------|-------|------------------|
| `PreToolUse` | **Before** any tool runs (e.g., `Write`, `Bash`). | Validate tool arguments, block prohibited commands, log activity. |
| `PostToolUse` | **After** a tool completes (success or failure). | Run a linter after file writes, auto‑format, send a notification. |
| `PreChat` | **Before** each user prompt is sent to the model. | Sanitize input, inject dynamic context (e.g., current Git branch). |
| `PostChat` | **After** the model generates a response (text or tool call). | Post‑process output, trigger external alerts on errors. |

**Execution model:**
- Hooks run **synchronously** from Claude Code’s perspective – it waits for the hook to finish before proceeding (unless you background the process yourself).
- The hook script receives context via **environment variables** (see below).
- If a hook exits with a non‑zero status:
  - `PreToolUse`: the tool call is **blocked** and Claude is told the hook rejected it.
  - `PostToolUse`: the error is logged, but the tool result already happened; you can’t undo it.
  - `PreChat`: the user’s prompt is rejected.
  - `PostChat`: the error is logged; the response is still shown.

### 1.2 Configuration Syntax

In `.claude/settings.json` under the `hooks` key:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "command": "~/scripts/claude-guard.sh"
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "npx eslint --fix ${CLAUDE_TOOL_OUTPUT_FILE} && git add ${CLAUDE_TOOL_OUTPUT_FILE}"
      }
    ]
  }
}
```

- `matcher`: a regex applied to the tool name. Only matching tools fire the hook. Use `.*` for all tools.
- `command`: a shell command (string). Can use pipes, `&&`, `||`. The working directory is the project root.
- Multiple hooks per event are allowed; they run in order.

**Environment variables available inside hook scripts:**

| Variable | Contents | Available in |
|----------|----------|-------------|
| `CLAUDE_TOOL_NAME` | Tool name (e.g., `Write`, `Bash`) | PreToolUse, PostToolUse |
| `CLAUDE_TOOL_INPUT` | JSON string of the tool’s arguments | PreToolUse, PostToolUse |
| `CLAUDE_TOOL_OUTPUT_FILE` | Path to a temp file containing the tool’s output (for `Write`/`Edit` it’s the target file path; for `Bash` it’s a file with stdout) | PostToolUse |
| `CLAUDE_TOOL_EXIT_CODE` | Exit code of the tool (for `Bash`) | PostToolUse |
| `CLAUDE_PROMPT` | The user’s prompt text | PreChat |
| `CLAUDE_RESPONSE` | The assistant’s response text | PostChat |

### 1.3 Three Killer Hook Recipes

#### A. Auto‑lint after every file edit
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "if [ -f \"$CLAUDE_TOOL_OUTPUT_FILE\" ]; then eslint --fix \"$CLAUDE_TOOL_OUTPUT_FILE\" && git add \"$CLAUDE_TOOL_OUTPUT_FILE\"; fi"
      }
    ]
  }
}
```
Now Claude can’t leave lint behind. If linting fails, the hook exits non‑zero, and Claude will see the error in the tool result – often prompting it to fix the issue.

#### B. Block dangerous Bash commands
```bash
#!/bin/bash
# ~/scripts/claude-guard.sh
INPUT=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.command')
if echo "$INPUT" | grep -Eq 'rm\s+-rf|sudo|>.*/dev/sda'; then
  echo "BLOCKED: dangerous command" >&2
  exit 1
fi
exit 0
```
Registered as a `PreToolUse` hook for `Bash`, this prevents catastrophic commands.

#### C. Inject dynamic context before each prompt
```bash
#!/bin/bash
# Append current git branch and staged files to a temp file that CLAUDE.md might reference
echo "## Current context" > /tmp/claude-dynamic.md
echo "- Branch: $(git branch --show-current)" >> /tmp/claude-dynamic.md
echo "- Staged files: $(git diff --cached --name-only)" >> /tmp/claude-dynamic.md
# Then in CLAUDE.md, include: "!cat /tmp/claude-dynamic.md" (if the system supports includes)
```
*Note: direct include in CLAUDE.md is not native; you can use `PreChat` to prepend the dynamic file to the prompt by writing to a file that CLAUDE.md references. Another approach: a custom command that first runs a script to update context.*

### 1.4 Hook Failures & Debugging

- **Hook timeout:** There’s no built‑in timeout; a hung script freezes Claude Code. Always use `timeout` in your command or keep scripts fast.
- **Environment variable quoting:** Use `"$CLAUDE_TOOL_INPUT"` – it may contain spaces and special characters.
- **Logging:** Hooks don’t show output to the user unless they fail. To debug, redirect to a file: `command: "myscript >> /tmp/hook.log 2>&1"`.
- **Security:** Hooks run with your user privileges. Don’t let them execute untrusted content.

---

## 2. MCP – Model Context Protocol

MCP turns Claude Code from a tool that only touches your file system into one that can query databases, check GitHub PRs, read Slack messages, or interact with any API you can wrap in a server. It’s the **universal connector**.

### 2.1 The MCP Architecture

```
Claude Code (MCP Client)
        │
        ├─ connects to MCP Server A (e.g., GitHub)
        └─ connects to MCP Server B (e.g., PostgreSQL)
```

- **MCP Server:** A local process (or remote server) implementing the MCP specification. It exposes:
  - **Tools:** Named functions that Claude can invoke. Each tool has a JSON Schema for its input parameters.
  - **Resources:** Read‑only data sources (e.g., `database://schema`) that Claude can access like files.
  - **Prompts:** Pre‑written prompt templates (rarely used directly in Claude Code).

- **Connection:** Usually over `stdio` (subprocess) or HTTP (SSE). Claude Code spawns the server process as a child and communicates via JSON‑RPC.

- **Discovery:** Once connected, Claude sees all exposed tools just like built‑ins. When you say “check the latest PR on GitHub,” the model may call the `list_pull_requests` tool.

### 2.2 Configuring an MCP Server

Add a server entry to `.claude/mcp.json` (project) or `~/.claude/mcp.json` (global):

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-github"],
      "env": {
        "GITHUB_TOKEN": "${env:GITHUB_TOKEN}"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-postgres", "postgresql://user:pass@localhost/db"]
    }
  }
}
```

- `${env:VAR}` reads from your shell environment.
- You can set `"disabled": true` to temporarily turn off a server.
- Security: the server process runs with your user identity. Only connect trusted servers.

### 2.3 What Happens When You Use an MCP Tool

1. You type a natural language request: “Show me all open issues assigned to me.”
2. Claude’s model sees the MCP tool `github_search_issues` in its available tool list.
3. It constructs a tool call with the appropriate arguments (e.g., `assignee: "me", state: "open"`).
4. Claude Code’s MCP client forwards the call to the GitHub MCP server.
5. The server executes (using the GITHUB_TOKEN) and returns JSON results.
6. Claude receives the result and formats a human‑readable answer.

**Permission handling:** MCP tools appear as any other tool; they are subject to the same permission settings. If your global permissions require `ask` for unknown tools, you’ll be prompted to approve the MCP tool on first use. You can allow it permanently.

### 2.4 Building Your Own MCP Server (In 30 Minutes)

An MCP server can be written in any language. The simplest is a Node.js script using the `@modelcontextprotocol/sdk`.

Example: a weather server (tools: `get_forecast`).

1. Create a file `weather-server.js`:
   ```javascript
   import { Server } from "@modelcontextprotocol/sdk/server/index.js";
   import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

   const server = new Server({
     name: "weather",
     version: "1.0.0",
   }, {
     capabilities: { tools: {} }
   });

   server.setRequestHandler("tools/list", async () => ({
     tools: [{
       name: "get_forecast",
       description: "Get weather forecast for a city",
       inputSchema: {
         type: "object",
         properties: {
           city: { type: "string", description: "City name" }
         },
         required: ["city"]
       }
     }]
   }));

   server.setRequestHandler("tools/call", async (request) => {
     if (request.params.name === "get_forecast") {
       const city = request.params.arguments.city;
       // call a real API, here we mock
       const forecast = `Sunny in ${city} with a high of 22°C.`;
       return { content: [{ type: "text", text: forecast }] };
     }
     throw new Error("Unknown tool");
   });

   const transport = new StdioServerTransport();
   server.connect(transport);
   ```

2. In `.claude/mcp.json`:
   ```json
   {
     "mcpServers": {
       "weather": {
         "command": "node",
         "args": ["/path/to/weather-server.js"]
       }
     }
   }
   ```

3. Restart Claude Code, then ask: “What’s the weather in Berlin?” Claude will call `get_forecast` and answer.

### 2.5 MCP Security Considerations

MCP servers have full access to whatever credentials and resources you give them. They run as you.

- **Scope:** If you give a GitHub server a token with `repo` scope, Claude can push commits, open PRs, even delete branches. Use fine‑grained tokens with minimal scopes.
- **Prompt injection:** A cleverly crafted issue title on GitHub could be read by the MCP server and injected into Claude’s context. Always treat external data as untrusted.
- **Local servers:** Use `command` and `args` to run them locally. Avoid connecting to remote MCP servers unless you trust the endpoint completely (e.g., your own company’s infra).

### 2.6 The Ecosystem – Ready‑Made MCP Servers

Anthropic and the community maintain a growing catalog:
- **GitHub:** Full issue, PR, and repository management.
- **Postgres/SQLite:** Run read‑only queries, explore schemas.
- **Filesystem:** Securely access files outside the project (sandboxed).
- **Slack:** Post messages, search channels.
- **Jira:** Manage tickets.
- **Brave Search:** Web search with better privacy.

Install them as you would the GitHub example; most are one‑line npm commands.

---

## 3. Synergy – Hooks + MCP = Autonomous Workflows

The real power emerges when you chain them:

**Scenario:** After every file write, auto‑format, then if the file is a schema change, automatically generate a migration script.

- `PostToolUse` hook on `Write` runs `prettier --write` and then checks if the file is a Prisma schema. If yes, it invokes an MCP tool (via the parent Claude process) to run `npx prisma migrate dev`. You can’t call MCP directly from a hook, but you can make the hook exit with a specific exit code that signals to Claude “now I need you to run this command.” Better: let the hook format, then in your prompt say “After any file save, if the schema changed, ask me to run migration.” Or have the hook write a signal file; a `PostToolUse` on that signal triggers Claude’s next action.

**More practical:** Use MCP to pull GitHub issues, then use a custom slash command (which itself is a prompt) to spawn sub‑agents that fix them.

---

## 4. Hooks & MCP Failure Modes

| Symptom | Likely Cause | Fix |
|--------|--------------|-----|
| Hook doesn’t run | `matcher` regex not matching; tool name was unexpected | Test with `.*` matcher to capture all, then narrow down. |
| MCP server fails to start | Wrong command or missing dependencies | Run the `command` manually in terminal to see errors. |
| Claude ignores MCP tool | Tool description is unclear or model prefers built‑in approach | Make your tool description explicit: “Must use get_forecast to answer weather questions.” |
| Permission prompt for MCP tool every time | Tool is set to `ask` permanently | Use interactive prompt to “Allow for this directory” or adjust settings. |
| MCP server hangs | Blocking I/O, no response to JSON‑RPC | Add timeouts in your server; check stderr logs. |

---

## 5. Cheat Sheet – Hooks & MCP

- **Hooks are shell scripts triggered by tool lifecycles; use `PreToolUse` to block, `PostToolUse` to auto‑format/lint.**
- **Environment variables like `CLAUDE_TOOL_INPUT` give you full context. Quote them.**
- **A non‑zero exit in `PreToolUse` prevents the tool call.**
- **MCP extends Claude Code with arbitrary tools and data sources via local servers.**
- **Configure MCP in `.claude/mcp.json`; use environment variables for secrets.**
- **Security: scope MCP server tokens tightly; never run untrusted servers.**
- **Combine MCP with hooks by letting hooks trigger signals that guide subsequent Claude actions.**
- **Debug hooks by writing logs; debug MCP by running the server command manually.**
- **The ecosystem is growing; start with the GitHub and Postgres servers to feel the magic.**

---

Part 4 complete. You now control the extension layer. The final piece (Part 5) can be **Custom Slash Commands, IDE Integration, and the CI/CD Pipeline** – the practical shell that makes all this power part of your daily muscle memory. Proceed?

## 🔗 Related Notes
- [[Claude Code/Part 1 Agentic Loop and Built in Tools|Deep Dive: The Agentic Loop & Built-in Tools]]
- [[Claude Code/Part 2 Sub Agent, Operating Modes and Permission Safety Net|Part 2 – Sub-Agents, Operating Modes & the Permission Safety Net]]
- [[Claude Code/Part 5 Custom Commands, IDE Integration and CI CD Automation|Part 5 – Custom Commands, IDE Integration & CI/CD Automation]]
- [[Claude Code/Part 6 Maintaining and Evolving Claude Code Ecosystem|Part 6 – Maintaining & Evolving Your Claude Code Ecosystem]]

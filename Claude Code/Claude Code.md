# Claude Code

Overview note for the Claude Code area — a dense technical reference series on Claude Code's internals, extensions, and daily workflows.

## 🗺️ Map of Content (auto-generated)

**Foundations**
- [[Claude Code/Introduction to Claude Code|Claude Code – The Pareto Reference (Maximum Output)]] — top-level Pareto summary covering the core loop, tools, modes, memory, permissions, hooks, MCP, and commands.
- [[Claude Code/Part 1 Agentic Loop and Built in Tools|Deep Dive: The Agentic Loop & Built-in Tools]] — how the reason→tool→observe loop works and a full breakdown of each built-in tool (Read, Write, Edit, Bash, Glob, Grep, TodoWrite, Task, WebSearch).

**Delegation & Safety**
- [[Claude Code/Part 2 Sub Agent, Operating Modes and Permission Safety Net|Part 2 – Sub-Agents, Operating Modes & the Permission Safety Net]] — the Task tool's fork lifecycle, Plan/Interactive/Non-interactive modes, and the permission resolution order.

**Context & Memory**
- [[Claude Code/Part 3 Memory, Claude.md and the Context Engine|Part 3 – Memory, CLAUDE.md, and the Context Engine]] — the three memory layers (CLAUDE.md, CLAUDE.local.md, session memory), context window truncation, and sub-agent memory inheritance rules.

**Extensibility**
- [[Claude Code/Part 4 Hooks and MCP, The Extension Architecture|Part 4 – Hooks & MCP: The Extension Architecture]] — lifecycle hooks (PreToolUse/PostToolUse/PreChat/PostChat) and the Model Context Protocol for connecting external tools/servers.

**Daily Workflow & Automation**
- [[Claude Code/Part 5 Custom Commands, IDE Integration and CI CD Automation|Part 5 – Custom Commands, IDE Integration & CI/CD Automation]] — building `.claude/commands/` macros, VS Code/JetBrains integration, and CI/CD pipelines (GitHub Actions, pre-commit hooks).

**Maintenance**
- [[Claude Code/Part 6 Maintaining and Evolving Claude Code Ecosystem|Part 6 – Maintaining & Evolving Your Claude Code Ecosystem]] — keeping CLAUDE.md, hooks, MCP servers, commands, and CI configuration healthy as a project and team scale.

# Part 6 – Maintaining & Evolving Your Claude Code Ecosystem

*The guides so far built the machine. This part ensures it doesn’t rust. It answers: **How do I keep CLAUDE.md, hooks, MCP servers, commands, and CI integrations effective as my project, team, and codebase grow?** This is the difference between a tool that works once and a platform that scales with you.*

---

## 1. CLAUDE.md – The Living Project Constitution

CLAUDE.md isn’t a “set and forget” file. As your architecture shifts, dependencies update, and conventions change, an outdated CLAUDE.md becomes actively harmful – Claude will follow obsolete rules.

### 1.1 When to Update CLAUDE.md (Triggers)

Add a rule to your team’s Definition of Done: “If a PR changes any of the following, update CLAUDE.md in the same PR.”

| Trigger | What to update in CLAUDE.md |
|---------|------------------------------|
| New build/CI command | Build & Run section |
| Framework or major library upgrade | Tech Stack section |
| New coding convention agreed by team | Code Conventions section |
| Refactoring that moves folders or changes architecture | Architecture section |
| New security policy or linting rule | Security Rules section (or respective section) |
| Addition/removal of testing framework | Testing section |

**Pro tip:** Add a `## Changelog` at the bottom of CLAUDE.md. Each time you modify it, append a one-line entry: `- 2026-07-31: Added rule to use Zod for input validation (PR #852)`. This gives both humans and Claude a history.

### 1.2 Detecting Staleness Automatically

Claude itself can detect drift between CLAUDE.md and reality.

Run this audit periodically (monthly or after major releases):

```bash
claude -p --max-turns 8 "Compare CLAUDE.md with the current codebase.
Identify any rules that are outdated, missing, or contradicted by actual code.
Output a list of discrepancies with suggested fixes.
Use only Read, Glob, Grep tools."
```

Review the output; it will highlight things like “CLAUDE.md says we use Jest, but `package.json` shows Vitest” or “Architecture says `services/` exists, but that folder was moved to `lib/`.” Apply the fixes, then commit.

### 1.3 CLAUDE.md Versioning and PR Reviews

- Treat CLAUDE.md diffs as seriously as code diffs. A wrong instruction in CLAUDE.md can lead Claude to generate hundreds of lines of wrong code.
- Add a CODEOWNERS entry if necessary: `/CLAUDE.md @tech-leads`
- Use the `/review` command on PRs that change CLAUDE.md, asking Claude: “Verify that the new rules in CLAUDE.md are consistent with the code changes in this PR.”

### 1.4 CLAUDE.local.md Hygiene

- Remind team members (in your onboarding guide) that `CLAUDE.local.md` should never contain secrets or proxy values that could affect production.
- If a developer leaves, their `CLAUDE.local.md` is irrelevant, but if they’ve been using a local override that masked a real issue, it could surface later. Periodically ask: “Are there any local overrides we should promote to shared CLAUDE.md?”

---

## 2. Hook Auditing & Performance

Hooks are powerful but invisible. A misbehaving hook can silently slow down every Claude session, or block valid commands without clear error messages.

### 2.1 Performance Metrics

Hooks run synchronously. If your `PostToolUse` linter takes 15 seconds on a large file, Claude’s loop waits 15 seconds every time you edit that file. Audit with:

```bash
# Wrap your hook command with a timer, log to file
command: "time (your-script) >> /tmp/claude-hook-timings.log 2>&1"
```

Review the log weekly. Any hook averaging >2 seconds should be optimized or moved to asynchronous execution (if safe). You can background it: `(your-script &)` but then you lose the ability to block if it fails.

### 2.2 Hook Failure Auditing

When a hook fails (non-zero exit), Claude sees the error. But *you* may not notice if the error is swallowed by the tool result. Keep a failure log:

```bash
command: "your-script || echo 'FAILED: $?' >> /tmp/claude-hook-failures.log"
```

Review failures monthly. A common pattern: the linter exits 1 for style warnings (not errors), causing Claude to think the edit was invalid, leading to unnecessary retries. Adjust the hook to `eslint --fix --quiet` or only exit non-zero on actual errors.

### 2.3 Securing Hooks Against Code Injection

If a hook uses `$CLAUDE_TOOL_INPUT` (which contains JSON from the model), never inject it unsanitized into shell commands like `eval` or SQL queries. Use `jq` to extract specific fields safely:

```bash
# SAFE:
command=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.command')
# UNSAFE:
eval "$CLAUDE_TOOL_INPUT"
```

Malicious code could theoretically be embedded in a tool call if you’re using MCP to ingest untrusted data. Treat hook inputs like any user input – sanitize.

### 2.4 Version-Controlling Hooks

Keep your hook scripts in the repository (e.g., `.claude/hooks/`). Reference them in `settings.json` by relative path. This ensures all team members use the same hooks. Hooks are part of the project’s infrastructure.

---

## 3. MCP Server Governance

MCP servers are external dependencies that can break, become insecure, or fall out of date.

### 3.1 Server Lifecycle Management

For each MCP server you depend on:

- **Pin the version** in `mcp.json` (e.g., `npx @anthropic/mcp-server-github@0.3.1`). Avoid `-y` without a version tag; you risk breaking changes on new releases.
- **Document required credentials** in a team onboarding guide. The `mcp.json` might reference env vars; ensure those env vars exist in local `.env` files and CI secrets.
- **Test server startup** in your CI or pre-commit: run the server command and check that it exits cleanly (it will wait for input, so you can time-bound: `timeout 5 npx ...`). If it fails, fail the build.

### 3.2 Token Scope Audit

Every month, review the tokens used by MCP servers:

- GitHub token: does it still need `repo` scope, or can it be reduced to `read:public` if you only read issues?
- Database credential: is it a read-only user? If the MCP server exposes both query tools and mutation tools, restrict the server’s capabilities or use a read-only credential.
- Delete any tokens for servers you’ve stopped using.

### 3.3 Server Customization & Forking

If you modify a community MCP server, fork it and maintain your own version. Document the fork in your project’s README. Periodically rebase from upstream to get security fixes. Treat MCP servers as production dependencies.

### 3.4 Debugging MCP Server Silence

If Claude suddenly stops using an MCP tool:

1. Check `~/.claude/mcp.json` or project `.claude/mcp.json` for syntax errors (JSON must be valid).
2. Try running the server command manually in your terminal. It should print log messages to stderr.
3. Check if the server process is crashing. You can enable logging by setting `"env": {"DEBUG": "mcp:*"}` in the mcp.json entry (for Node servers).
4. Verify the tool descriptions are still accurate; if the server API changed, tools may be named differently.

---

## 4. Custom Command Evolution

Your set of custom slash commands should mirror your team’s evolving workflow.

### 4.1 Command Portfolio Review (Monthly)

Sit down (or in a quick team sync) and ask:

- Which commands do we actually use? (Check Git history or just ask.)
- Which commands are outdated? (e.g., a `/deploy` that references a retired script.)
- What repetitive prompts are we manually typing that could become a command?

Remove unused commands to reduce clutter. The folder `.claude/commands/` should be lean.

### 4.2 Command Versioning & Shared Templates

Commands are part of the codebase; they should be reviewed in PRs. When someone proposes a new command, include a short docstring in the Markdown file itself explaining its purpose and usage (e.g., `<!-- /review: reviews current diff -->`). This helps team members discover commands.

### 4.3 Parameterized Commands – Beyond $ARGUMENTS

You can build complex commands by chaining multiple prompts inside the command file. Example for a multi-step onboarding:

```markdown
You are onboarding a new developer. Do the following in sequence, asking me to proceed after each step:
1. Read CLAUDE.md and summarize the tech stack.
2. Explore the directory structure and explain the purpose of each top-level folder.
3. Identify the entry point and trace the main flow.
Use sub-agents for exploration. $ARGUMENTS (optional: specific module to focus on)
```
The `$ARGUMENTS` part allows focus. This kind of semi-interactive flow can be done even in a single command.

---

## 5. CI/CD Pipeline Maintenance

Claude-in-CI is a powerful but delicate integration. It depends on external API availability, token limits, and correct configuration.

### 5.1 API Usage Monitoring

Claude calls in CI burn your Anthropic credits. Set budget alerts:

- Use Anthropic’s dashboard to set monthly spending limits.
- For high-traffic repos, consider rate-limiting: only trigger Claude review on PRs with a specific label (`need-ai-review`) instead of every push.
- Track per-PR token usage by parsing the `usage` object from Claude’s JSON output, and log it in your CI metrics.

### 5.2 Deterministic Outputs for CI Reliability

The model is non-deterministic by nature. To make CI reliable:

- Keep prompts extremely precise; use `--temperature 0` if the CLI supports it (check current docs; otherwise, instruct “be as deterministic as possible”).
- In your CI script, retry once if the output JSON is unparseable (model might have wrapped in markdown). Better: request “Output ONLY valid JSON, no other text, no markdown fences.”
- Test your CI Claude prompts locally in a dry run before merging a PR that changes them.

### 5.3 Fallback Strategies

If the Anthropic API is down, your CI should not block merges. Design your pipeline so that Claude review is an advisory check, not a required status. Use:

```yaml
continue-on-error: true
```
in GitHub Actions, and post the review as a comment rather than a failing check. You can also implement a timeout (10 minutes) and graceful degradation.

### 5.4 Updating CI Settings as Code

Keep `settings-ci.json` under version control and ensure it’s used in every CI run. When you add a new tool or permission, update this file as well. A mismatch between local and CI permissions can cause confusing failures. A good practice: derive CI settings from a shared base, or generate them from the project settings minus dangerous tools.

---

## 6. Scaling to Teams – Shared Configuration Without Chaos

When multiple developers use Claude Code on the same project, configuration conflicts can arise.

### 6.1 Shared vs. Local Settings

- **Shared (versioned):** `.claude/settings.json`, `CLAUDE.md`, `.claude/commands/`, `.claude/hooks/`, `.claude/mcp.json` (if secrets are via env vars).
- **Local (gitignored):** `CLAUDE.local.md`, any developer-specific hook overrides (if absolutely needed, keep them in a separate local file and use conditional logic).

**Conflict resolution:** If a team member wants to use a different model or different hook, they can override in their local `~/.claude/settings.json` (global) which merges with project settings. However, critical hooks that enforce security must be enforced. Use `PreToolUse` hooks to block dangerous actions; these cannot be overridden by global settings if they’re defined in the project settings and the tool is set to `deny` (the project setting wins).

### 6.2 Onboarding New Developers

Create a `/onboard` command as we did. Additionally, have a README section “Claude Code Setup” that covers:
- Installation
- Required env vars (ANTHROPIC_API_KEY or login)
- Project-specific MCP servers to start
- How to run the CLAUDE.md health check
- How to test their local setup with a safe dry-run prompt

### 6.3 Code Review Norms for Claude-Generated Code

Establish team guidelines:
- AI-generated code must be labeled in commits (e.g., “Co-authored-by: Claude <noreply@anthropic.com>”) to track provenance.
- All Claude-generated changes must be reviewed by a human before merge (CI Claude review does not replace human review).
- Use the `/review` command to get an initial review, but a human must approve.

### 6.4 Auditing Claude Usage Across the Team

If using API keys, track usage per developer by asking them to set a `USER` env var and including it in API request metadata (if supported). This helps identify heavy usage that may need optimization. For Max subscribers, this is less granular.

---

## 7. Periodic Health Checks – A Quarterly Ritual

Every 3 months, run this checklist (or automate parts of it):

- [ ] **CLAUDE.md audit:** Run the staleness detection prompt. Update if needed.
- [ ] **Hooks audit:** Check performance logs; remove or fix any failing hooks.
- [ ] **MCP server audit:** Review tokens, update versions, test server startup.
- [ ] **Custom commands audit:** Archive unused commands, add missing ones.
- [ ] **CI integration audit:** Check recent CI runs for Claude failures, review costs, update `settings-ci.json`.
- [ ] **Security review:** Ensure no secrets in `CLAUDE.md` or `CLAUDE.local.md` (run `grep -r 'API_KEY\|password\|token' .claude/ CLAUDE*`).
- [ ] **Prompt effectiveness:** Gather team feedback; are there recurring frustrations? That’s a signal to improve CLAUDE.md or create a new custom command.
- [ ] **Model version:** Anthropic updates models; test new models in a dev branch before switching the team’s default. Update settings if a new model is more cost-effective or better.

---

## 8. The Evolution Cheat Sheet

- **CLAUDE.md is code; review it, version it, keep it true to reality.**
- **Audit hook performance and failures monthly; slow hooks degrade the entire experience.**
- **Pin MCP server versions, scope tokens minimally, and test server startup.**
- **Your custom command set should be lean and reflect actual workflows; remove dead commands.**
- **CI integration must be resilient (non‑blocking) and cost‑monitored.**
- **Shared configuration goes in the repo; personal overrides stay local.**
- **Quarterly health checks prevent silent drift that erodes trust in the tool.**

---

This completes the full technical reference series. You now have a living manual covering the internals, extensions, workflows, and long‑term maintenance of Claude Code. Each part is designed to be read independently when you need to refresh a specific subsystem, but together they form a complete mental model of the platform.
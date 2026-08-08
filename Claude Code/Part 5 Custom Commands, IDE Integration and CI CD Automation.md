# Part 5 – Custom Commands, IDE Integration & CI/CD Automation

*This part answers: **How do I turn the raw power of the previous four parts into daily muscle memory, a seamless editor experience, and fully automated pipelines?** These are the interfaces that make Claude Code a habitual tool rather than a curiosity.*

---

## 1. Custom Slash Commands – Your Personal Macro System

Custom commands are the **shortcut layer** above the agentic loop. They encapsulate frequent, complex prompts into single words you can invoke inside any session. Think of them as your own CLI within Claude Code.

### 1.1 How They Work Under the Hood

- A command is a **Markdown file** inside `.claude/commands/`. The file name (minus `.md`) becomes the command name.  
  Example: `.claude/commands/review.md` → `/review`
- The file’s **body** is the prompt that gets sent to Claude. It can include:
  - `$ARGUMENTS`: everything you type after the command name.  
  - `$INPUT`: text piped into the command (like `git diff | claude /review`).  
  - Standard Markdown formatting (Claude reads it literally).
- When you type `/review` in a session, Claude Code replaces it with the file’s content, expands variables, and feeds it as your next prompt. It’s a pure text substitution—no magic state.

**Why this beats retyping:** It enforces consistency. Your `/review` always includes the same checklist, file scopes, and output format. You never forget a step.

### 1.2 The Five Commands Every Developer Needs

I’ll give you templates; adapt them to your stack.

#### A. `/review` – PR‑Ready Code Review
File: `.claude/commands/review.md`
```markdown
Please review the current state of the repository. Specifically:
- Examine files changed in the most recent commit (use `git diff HEAD~1`).
- Check for bugs, security vulnerabilities, and style violations.
- Compare against the rules in CLAUDE.md.
- Output a structured report with sections: Critical, Warnings, Suggestions.
- For each issue, provide the file, line number, and a suggested fix.
```
**Usage:** `/review` or `git diff main | claude /review` (with `$INPUT`).

#### B. `/explain` – Architecture Deep‑Dive
File: `.claude/commands/explain.md`
```markdown
Analyze the module `$ARGUMENTS`. Use sub‑agents to:
1. List all public exports and their signatures.
2. Trace dependencies (imports) within the project.
3. Identify potential performance bottlenecks or anti‑patterns.
4. Produce a summary suitable for onboarding a new developer.
```
**Usage:** `/explain src/services/payment.ts`

#### C. `/fix` – Bug Fix Assistant
File: `.claude/commands/fix.md`
```markdown
We need to fix the issue described below. Process:
1. Read any error logs provided in $INPUT.
2. Grep for the relevant error messages across the codebase.
3. Propose a root cause analysis.
4. Implement the fix using Edit, ensuring existing tests pass.
5. Add a regression test if applicable.
Issue: $ARGUMENTS
```
**Usage:** `cat error.log | claude /fix "NullPointerException in checkout"`

#### D. `/deploy` – Safe Deployment Checklist
File: `.claude/commands/deploy.md`
```markdown
Prepare for deployment:
1. Run `pnpm lint` and `pnpm test`.
2. If any failures, stop and report.
3. Build the project (`pnpm build`).
4. Generate a concise changelog from commits since last tag.
5. Ask me for confirmation, then run the deploy script (`./scripts/deploy.sh`).
```
**Usage:** `/deploy` – triggers a gated pipeline.

#### E. `/onboard` – Instant Context Injection
File: `.claude/commands/onboard.md`
```markdown
I'm a new developer on this project. Please:
1. Read CLAUDE.md.
2. Explore the top‑level directory structure using Glob.
3. Provide a 5‑minute overview: what this project does, key modules, how to build and test.
4. Suggest the next file I should read to understand the core logic.
```
**Usage:** `/onboard` – perfect for ramping up.

### 1.3 Advanced Variable Usage

- `$ARGUMENTS` captures everything after the command. If you need multiple named parameters, you can parse them inside the prompt: “The ticket ID is `$ARGUMENTS`. Extract the ID and title.” (Claude will parse natural language.)
- `$INPUT` is stdin. Combine with shell: `git log --oneline -5 | claude /summarize-commits`
- You can **nest commands**: a `/review` command that calls `/test` first? Not directly, but you can include in the review prompt: “First, run the test suite with Bash. If it passes, proceed with review.” That’s effectively chaining.

### 1.4 Where Custom Commands Shine (Pareto)

- **Repetitive code reviews**: one `/review`, done consistently.
- **Refactoring with guardrails**: `/refactor` that includes “Preserve all existing tests; run them after each change.”
- **Team‑specific workflows**: a command to generate release notes in your exact format.
- **Training wheels for new Claude users**: they just type `/fix bug description` without learning prompt engineering.

---

## 2. IDE Integration – Visual Diffing and In‑Editor Control

The terminal REPL is powerful, but seeing diffs inline and approving them with a click drastically reduces friction. Claude Code integrates with VS Code and JetBrains (where available) via extensions that sync with the terminal session.

### 2.1 VS Code Extension – Deep Integration

**Setup:**
1. Install the official Claude Code extension from the VS Code marketplace.
2. Open a terminal in VS Code and start a Claude session (`claude`).
3. The extension detects the running session and connects.

**What you get:**
- **Inline diffs:** When Claude uses `Write` or `Edit`, the changes appear as a standard VS Code diff view. You see old vs. new side‑by‑side, exactly like a Git diff.
- **One‑click accept/reject:** Buttons to accept or reject each change. Under the hood, accepting signals the permission prompt back to the terminal agent.
- **File opening:** When Claude references a file, VS Code can open it automatically in an editor tab.
- **Session panel:** A sidebar view shows the conversation history, tool calls, and outputs, synchronized with the terminal.

**Why it matters:** You visually validate AI‑generated code just as you would a human colleague’s PR. That reduces acceptance latency and errors.

### 2.2 JetBrains Integration (if available)

Similar capabilities: a tool window with diffs, integrated permission handling, and context menus. The exact installation depends on the IDE version; check Anthropic’s docs for the plugin.

### 2.3 The Terminal + Editor Workflow (No Extension Needed)

Even without an extension, you can engineer a smooth flow:
1. Start `claude` in a terminal pane.
2. In VS Code, open the command palette and split the terminal; or use a dedicated terminal panel.
3. When Claude modifies files, VS Code automatically detects changes and prompts you to reload the file, or just shows the changes in the Git diff view.
4. Approve tool calls in the terminal while seeing the editor update in real time.

**Pro tip:** Use `code -r <file>` (VS Code CLI) inside Claude’s `Bash` commands to open files after edits. Example in `CLAUDE.md`: “After editing any file, also run `code -r <file>` to open it.” This auto‑opens the file in your editor.

### 2.4 IDE‑Integrated Permissions

The extension can handle permission prompts directly in the editor UI, reducing context switches. You never need to move your hands to the terminal to approve a `Bash` call.

---

## 3. CI/CD Integration – Automating Claude Code in Pipelines

This is where Claude Code becomes a team‑wide tool, not a personal assistant. The non‑interactive mode (`-p`) combined with structured output (`--output-format json`) makes it scriptable.

### 3.1 The Core CI Pattern

**Principle:** Run Claude Code with `-p`, set `--max-turns` to a reasonable number (3–10), restrict tools to read‑only and safe commands, and capture output in JSON for further processing.

### 3.2 Example 1: Automated PR Review (GitHub Actions)

File: `.github/workflows/claude-review.yml`
```yaml
name: Claude Code Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Get diff
        run: git diff origin/${{ github.base_ref }} > diff.txt
      - name: Claude review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          claude -p --max-turns 8 --output-format json "$(cat <<EOF
          You are a code reviewer. Review the following diff for bugs, security issues, and style violations.
          The project rules are in CLAUDE.md.
          Diff:
          $(cat diff.txt)
          Output a JSON object with keys: "summary", "issues" (array of {file, line, severity, description}).
          EOF
          )" > review.json
      - name: Comment PR
        uses: actions/github-script@v7
        with:
          script: |
            const review = require('./review.json');
            const body = `## Claude Code Review\n**Summary:** ${review.summary}\n\n${review.issues.map(i => `- **${i.severity}** in \`${i.file}:${i.line}\`: ${i.description}`).join('\n')}`;
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body
            });
```

**Key points:**
- `fetch-depth: 0` to get full history for diff.
- Environment variable `ANTHROPIC_API_KEY` stored as a secret.
- `--output-format json` ensures machine‑readable output.
- The prompt explicitly asks for JSON output schema; Claude will comply.
- Permissions: In CI, you’d set `.claude/settings.json` to allow `Read`, `Grep`, `Bash` for safe commands only (like `git`). No file writes.

### 3.3 Example 2: Pre‑Commit Hook with Guardrails

File: `.git/hooks/pre-commit` (local) or via `husky`:
```bash
#!/bin/sh
# Run Claude to check the staged diff for secrets or debugging code
diff=$(git diff --cached)
if echo "$diff" | claude -p --max-turns 3 "Check this diff for hardcoded secrets, console.log, or debugging breakpoints. If none found, output ONLY the word 'CLEAN'. Otherwise, list violations." | grep -qv "CLEAN"; then
  echo "Claude found issues. Commit aborted."
  exit 1
fi
```

**Why this is safe:** The prompt explicitly constrains the output; exit code 1 prevents commit if issues exist. Claude doesn’t modify files here; it only reads the diff from stdin.

### 3.4 Example 3: Automatic Test Generation for Changed Files

In CI, after a push to a feature branch:
1. Get list of changed files.
2. Feed each file to Claude with a prompt: “Generate unit tests for this file using Vitest and Testing Library, following the patterns in the existing test files. Output the test file content.”
3. Create a new commit with the generated tests, or post them as a PR comment for manual review.

### 3.5 CI‑Specific Configuration

Create a dedicated `.claude/settings-ci.json` that you copy over during CI runs, with:
```json
{
  "permissions": {
    "Read": "allow",
    "Grep": "allow",
    "Glob": "allow",
    "Bash": "allow",
    "Write": "deny",
    "Edit": "deny",
    "WebSearch": "deny"
  },
  "allowedDirectories": ["/github/workspace"],
  "dangerouslyAllowAllBash": false
}
```
And in the workflow:
```bash
cp .claude/settings-ci.json .claude/settings.json
```
This ensures no file modifications or destructive commands, even if the model hallucinates.

---

## 4. Bringing It All Together: The Daily Workflow Loop

Now let’s weave everything from Parts 1–5 into a realistic daily session.

1. **Morning setup**  
   - Start `claude` in the project root.  
   - Type `/onboard` if it’s a new repo.  
   - CLAUDE.md and CLAUDE.local.md are loaded automatically.

2. **Pick a task**  
   - From your issue tracker (MCP-connected Jira/GitHub), fetch an issue: “Show me the top priority bug.”  
   - Claude uses MCP to retrieve it.

3. **Plan the fix**  
   - Enter plan mode: `/plan`  
   - “Analyze this bug and propose a plan.” Claude uses Grep, Read, sub‑agents to map the code.  
   - Review the plan, tweak as needed.

4. **Execute with guardrails**  
   - Exit plan mode.  
   - “Proceed with step 1 and 2. After each file edit, show me the diff.”  
   - The `PostToolUse` hook auto‑lints; you see the diff in VS Code and accept.

5. **Test and iterate**  
   - “Run the test suite. If failures, fix them.” Claude loops: run tests, analyze failures, edit, re‑test.

6. **Review and commit**  
   - `/review` to get a final sanity check.  
   - Claude crafts a commit message and, with your permission, commits.

7. **Push and CI validation**  
   - You push. GitHub Actions runs the same `/review` command in CI, plus auto‑test generation if configured. The PR gets a Claude review comment automatically.

This entire sequence, with muscle memory, can happen in under 15 minutes for a moderate bug.

---

## 5. Failure Modes and Fixes

| Symptom | Cause | Fix |
|--------|-------|-----|
| Custom command not recognized | File missing `.md` extension or not in `.claude/commands/` | Verify file path and name; restart session (commands are loaded at start). |
| `$ARGUMENTS` not replaced | Typo: `$ARGUMENTS` vs `$ARGS` | Use exact `$ARGUMENTS` (case‑sensitive). |
| CI job fails with permission prompt | Tool is set to `ask` in settings | Override settings with CI‑specific `settings.json` allowing necessary tools. |
| JSON output is malformed | Model added explanatory text before/after JSON | Request: “Output ONLY valid JSON, no other text.” |
| Pre‑commit hook hangs | Long‑running Claude call or no `--max-turns` | Set `--max-turns 3` and ensure API key is available; add timeout (`timeout 30`). |
| IDE extension not syncing | Session started before extension was active | Restart Claude session after extension is installed. |

---

## 6. Cheat Sheet – Custom Commands, IDE & CI/CD

- **Custom commands**: `.claude/commands/*.md`; use `$ARGUMENTS` and `$INPUT`.
- **Must‑have commands**: `/review`, `/explain`, `/fix`, `/deploy`, `/onboard`.
- **VS Code extension**: inline diffs, one‑click accept, session panel.
- **CI pattern**: `claude -p --max-turns N --output-format json` with restricted permissions.
- **Pre‑commit hook**: pipe `git diff --cached` to Claude, fail on issues.
- **Always create a `settings-ci.json`** that denies Write/Edit and restricts Bash.
- **Combine custom commands with MCP and hooks** for end‑to‑end automation.
- **Restart Claude session after changing command files.**
- **The daily loop**: plan mode → sub‑agents → edit → auto‑lint (hooks) → review (command) → commit → CI review.

---

Part 5 complete. You now have the full stack: from core loop and sub‑agents to memory, extensions, and finally the workflows that make all that power daily habit. If you want a meta‑level “maintenance and evolution” guide (how to update your CLAUDE.md as the project grows, auditing hook performance, MCP server lifecycle, etc.), I can provide that as a closing Part 6. Otherwise, this series is your permanent technical reference.

## 🔗 Related Notes
- [[Claude Code/Part 4 Hooks and MCP, The Extension Architecture|Part 4 – Hooks & MCP: The Extension Architecture]]
- [[Claude Code/Part 2 Sub Agent, Operating Modes and Permission Safety Net|Part 2 – Sub-Agents, Operating Modes & the Permission Safety Net]]
- [[Claude Code/Part 6 Maintaining and Evolving Claude Code Ecosystem|Part 6 – Maintaining & Evolving Your Claude Code Ecosystem]]
- [[Claude Code/Introduction to Claude Code|Claude Code – The Pareto Reference (Maximum Output)]]

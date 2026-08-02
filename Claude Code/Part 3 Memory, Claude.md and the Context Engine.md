# Part 3 – Memory, CLAUDE.md, and the Context Engine

Every other feature depends on what Claude knows at the moment it acts. This part answers: **How does Claude remember your project, your preferences, and its own progress – and how do you weaponize that memory?**

---

## 1. The Three Layers of Memory

Claude Code’s memory is not a monolithic brain. It’s a carefully tiered system. The separation between these layers is the key to both safety and effectiveness.

| Layer | Persistence | Scope | How to Edit |
|-------|------------|-------|-------------|
| **CLAUDE.md** | Permanent (Git tracked) | Project‑wide, shared with team | Direct file edit |
| **CLAUDE.local.md** | Permanent (gitignored) | Your machine only | Direct file edit |
| **Session Memory** | Ephemeral (lost on exit) | Current conversation only | `/remember` and `/forget` commands |

### 1.1 The Injection Timing

When a **new session** starts (you type `claude` or `claude -p`):

1. The system prompt is loaded (immutable, defines agent behavior).
2. `CLAUDE.md` from the project root is read and injected as an assistant‑style message (or user message – effectively it’s part of the initial context).
3. `CLAUDE.local.md` is read and injected the same way.
4. Any **global** `CLAUDE.md` (rare, but possible via a config) would be merged.
5. The first user prompt is appended.

**Crucially**, these files are read **once per session start**. If you edit `CLAUDE.md` mid‑session, Claude won’t see the changes until you restart. You can force a reload with a custom command or by restarting.

**Sub‑agents inherit the initial context**, including `CLAUDE.md` and `CLAUDE.local.md`, because they start a fresh session in the same directory. They do *not* receive the parent’s session memory or conversation history. They are clean‑slate workers.

---

## 2. CLAUDE.md – The Project’s DNA

This is the single highest‑leverage file you will ever write for AI‑assisted development. A well‑crafted `CLAUDE.md` can reduce token waste by 30–50% in every session, because Claude stops asking basic questions.

### 2.1 Anatomy of an Elite CLAUDE.md

```markdown
# Project Name

## Build & Run
- Install: `pnpm install`
- Dev server: `pnpm dev` (port 3000)
- Build: `pnpm build`
- Lint: `pnpm lint`
- Test: `pnpm test -- --coverage`
- E2E: `pnpm test:e2e` (requires Docker)

## Tech Stack
- Next.js 14 (App Router), TypeScript 5.3
- State: Zustand
- DB: PostgreSQL via Prisma
- Styling: Tailwind CSS + Radix UI

## Code Conventions (MUST FOLLOW)
- Use `async/await`, never raw promises.
- All API routes must include try/catch with a standardized error response.
- Components are PascalCase, files match the default export.
- Never modify files in `generated/` or `migrations/` except via tools.
- Prefer server components; only use `"use client"` when absolutely necessary.

## Architecture
- `src/app/` – Next.js routes (file‑based).
- `src/components/` – shared UI.
- `src/lib/` – business logic, DB queries, utilities.
- `src/services/` – external API integrations.
- State is colocated with the component that owns it; no global store except for auth.

## Testing
- Unit tests with Vitest, component tests with Testing Library.
- Mock external APIs with MSW.
- Run tests before committing.

## Security Rules
- Never log user PII.
- Sanitize all user inputs with Zod schemas.
- Session tokens are HTTP‑only; never access them in client code.
```

**Why each section matters:**

- **Build & Run**: Claude can immediately run `pnpm lint` after editing files without asking you.
- **Tech Stack**: Prevents suggestions like “use Redux” when you’re on Zustand.
- **Code Conventions**: The “MUST FOLLOW” section is treated as an absolute rule. Claude will rarely violate it.
- **Architecture**: Tells Claude where to put new files; eliminates guesswork and keeps the repo clean.
- **Testing**: Claude will write tests automatically that match your framework.
- **Security Rules**: Reduces the chance of introducing vulnerabilities.

### 2.2 Pro-Tier CLAUDE.md Patterns

1. **Use explicit prohibitions**: “Never use `any` in TypeScript. Always define explicit types.” This prevents lazy code.
2. **Include command aliases for speed**: “When I say ‘deploy’, run `./scripts/deploy.sh`.” This integrates with custom slash commands.
3. **Embed small code snippets for reference**: If you have a complex API client instantiation, show the exact incantation.
4. **State your branch strategy**: “We use GitFlow. Feature branches from `develop`, PR to `develop`.” Claude will then create branches accordingly.
5. **Define the PR template**: Include your team’s PR checklist so Claude can pre‑fill it.

### 2.3 CLAUDE.local.md – Your Personal Override

This file is gitignored by default. Use it for:
- Local path differences (“my npm is at `/usr/local/bin/npm`”)
- Personal preferences (“I prefer 2‑space indentation, even though the project uses tabs – use tabs in commits but show me 2 spaces locally” – *just kidding, don’t do that*)
- Temporary workarounds (“The test database URL is `localhost:5433` on my machine because Docker port clashes”)
- Private notes that shouldn’t be shared (“WIP: refactoring the billing module, don’t touch it yet”)

**Pro tip:** You can also use `CLAUDE.local.md` to temporarily test new rules before promoting them to the shared `CLAUDE.md`. Edit local, test in a session, then merge to shared.

---

## 3. Session Memory – The Working Memory

During a conversation, you can dynamically add facts with `/remember`.

```bash
/remember The bug we're fixing is #4421; the root cause is a race condition in the cache.
```

- These memories are stored in the session’s ephemeral store (not on disk).
- They are injected into the context window as additional messages, tagged as “memory”.
- You can view all session memories with `/memory`.
- Remove one with `/forget <id>`.
- Session memory is **not inherited** by sub‑agents. If you want a child to know something, include it in the child’s prompt.
- When the session ends, memory evaporates. There’s no auto‑save to `CLAUDE.md`.

**When to use session memory:**
- Temporary context that’s too long to repeat in every prompt.
- Tracking multi‑step debugging state: “We’ve already ruled out the DB connection; the issue is in the API layer.”
- Remembering user preferences for just this session: “Use dark mode for all code snippets.”

**Anti‑pattern:** Don’t use session memory for permanent project facts. That’s what `CLAUDE.md` is for. Session memory creates a false sense of permanence; after a restart, Claude will have amnesia.

---

## 4. The Context Window Engine – What Happens When Memory Runs Out

The most critical and least understood part of the memory system.

### 4.1 How Context Is Assembled Each Turn

Every time the model generates a response, the full context window is sent to the API. This includes:
- System prompt (~1k–2k tokens).
- `CLAUDE.md` + `CLAUDE.local.md` contents.
- Session memory entries.
- The entire conversation history (user messages, assistant responses, tool calls, tool results).

Total tokens cannot exceed the model’s context window (e.g., 200k for Claude 3.5 Sonnet). When it does, the runtime must **truncate**.

### 4.2 Truncation Strategy (Critical for Long Sessions)

Claude Code uses a **sliding window with truncation**:
- The **earliest messages are dropped first** (oldest user/assistant turns, including their tool calls).
- The **system prompt and memory files are kept** as long as possible, but if the context is extremely overloaded, even they may be partially truncated (though the runtime tries to preserve them).
- Truncation happens silently. You won’t get a warning “context full”. Instead, you’ll see symptoms: Claude re‑reading files it already read, losing track of earlier instructions, or repeating itself.

### 4.3 Detecting and Surviving Context Overflow

| Symptom | Diagnosis |
|--------|-----------|
| Claude reads a file, then 3 turns later reads it again as if new. | The first read result was truncated out of the context. |
| Claude “forgets” a critical instruction you gave 15 turns ago. | The instruction was in an early message that got dropped. |
| Responses become shorter, less coherent, or hallucinate more. | The model is struggling with a fragmented context. |

**Remedies (in order of effectiveness):**

1. **Summarize and restart**: “Summarize the current state of the task in a new `CLAUDE.md` section. I’ll restart the session and pick up from there.” This is the nuclear option, but it works perfectly.
2. **Mid‑session summarization command**: “Stop and write a compact summary of what you’ve done so far and what remains. Then continue.” This condenses many messages into one, freeing context.
3. **Use sub‑agents for deep dives**: Instead of reading 50 files in the parent, spawn a child to do the exploration and return a single summary. The parent never sees the 50 reads.
4. **Increase max turns cautiously**: If you set `--max-turns 100`, but the context fills at turn 40, the last 60 turns will be amnesiac. Not useful. Better to split the task.
5. **Explicitly prune**: “Forget everything about the initial exploration. We’re now focusing on the payment module.” This doesn’t actually delete from context, but encourages the model to ignore earlier irrelevant clutter.

---

## 5. Memory and Sub‑Agents – The Inheritance Rules

This is a frequent gotcha. Let’s make it ironclad.

| What | Does a sub‑agent get it? | Notes |
|------|--------------------------|-------|
| `CLAUDE.md` | Yes | Injected at child’s session start, same as parent. |
| `CLAUDE.local.md` | Yes | Also injected. |
| Session memories (`/remember`) | **No** | Children start with a blank ephemeral store. |
| Parent’s conversation history | **No** | Child only sees its own task prompt. |
| Parent’s `TodoWrite` list | **No** | Child may create its own TodoWrite. |
| Tool permissions from settings | Yes | Same global/project settings apply. |
| Hooks | Yes | Same hook scripts run. |

**Implication:** If you want a sub‑agent to know that “the DB is running on port 5433 today”, put it in `CLAUDE.local.md` before launching the parent. Then the child will see it.

---

## 6. The System Prompt Shadow – What You Can’t Override

Claude Code’s own system prompt (which you can glimpse in logs) defines its core personality and safety boundaries. It includes instructions like:
- How to format tool calls.
- That it should prefer `Edit` over `Write`.
- That it must ask for permission for destructive Bash.
- That it should be concise.
- Certain ethical guardrails.

You **cannot** override the system prompt directly, but your `CLAUDE.md` is placed immediately after it, acting as an extension. If the system prompt says “Be concise” and your `CLAUDE.md` says “Always provide detailed explanations,” the model will balance them, usually favoring the more recent instruction. So `CLAUDE.md` has significant weight, but it cannot cancel a hard safety rule.

---

## 7. Advanced Memory Techniques

### 7.1 Self‑Updating CLAUDE.md

You can instruct Claude to modify `CLAUDE.md` itself.  
> “After this refactor, add a note to CLAUDE.md under a ## Changelog section describing what changed and why.”

This is powerful for keeping the project memory alive. But caution: Claude might overwrite important parts if the `Edit` is imprecise. Review diffs.

### 7.2 Multi‑Project Monorepo Memory

If your monorepo has sub‑projects, you can put a `CLAUDE.md` in each sub‑directory. Claude Code will read the one in the root, but you can tell it to also read specific sub‑project ones:
> “Always read `packages/backend/CLAUDE.md` at the start of a session if I’m working on the backend.”

Better: create a root `CLAUDE.md` that points to others:  
`See packages/backend/CLAUDE.md for backend-specific rules.`

### 7.3 Memory Bootstrapping for New Team Members

Onboarding becomes a breeze. A new developer clones the repo, starts Claude Code, and it immediately knows:
- How to build, test, and deploy.
- Code conventions.
- Architecture.

No tribal knowledge lost.

### 7.4 Memory Versioning

Treat `CLAUDE.md` like code. Review it in PRs. As the project evolves, so should the memory. Outdated build commands in `CLAUDE.md` will cause Claude to run failing commands repeatedly.

---

## 8. Troubleshooting Memory Problems – Quick Reference

| Issue | Cause | Solution |
|-------|-------|----------|
| Claude asks “What test framework?” every session | Missing in CLAUDE.md | Add `## Testing` section. |
| Claude doesn’t know about a new rule you added mid‑session | Only injected at session start | Restart session or use `/remember` temporarily. |
| After many turns, Claude forgets the original goal | Context truncation | Ask for a summary, then restart. |
| Sub‑agent ignores your local DB config | `CLAUDE.local.md` not updated | Add the config there before launching the session. |
| Session memory not persisting after restart | It’s not supposed to | Move important facts to `CLAUDE.md`. |

---

## 9. The One-Page Memory Cheat Sheet

- **CLAUDE.md = permanent, shared, version‑controlled. Put all build commands, conventions, and architecture rules here.**
- **CLAUDE.local.md = permanent, personal, gitignored. Machine‑specific quirks go here.**
- **Session memory (`/remember`) = temporary, per‑conversation. Use for transient state.**
- **Memory injection happens once per session. Edits to files won’t be seen until restart.**
- **Sub‑agents inherit files but not session memory. They are clean‑slate.**
- **Context overflow causes amnesia; fight it with summaries and sub‑agent delegation.**
- **Your CLAUDE.md acts as a system prompt extension; it can’t override hard safety rules but will strongly guide behavior.**
- **The best time to write CLAUDE.md is before you need it. The second‑best time is now.**

---

Part 3 complete. This covers the entire memory architecture—how Claude knows your world and how to keep that knowledge intact across sessions, sub‑agents, and long tasks. Next in Part 4, we can tackle Hooks and MCP (Model Context Protocol)—the extension points that let you program Claude Code’s behavior and connect it to external systems. Ready when you are.

## 🔗 Related Notes
- [[Claude Code/Part 1 Agentic Loop and Built in Tools|Deep Dive: The Agentic Loop & Built-in Tools]]
- [[Claude Code/Part 2 Sub Agent, Operating Modes and Permission Safety Net|Part 2 – Sub-Agents, Operating Modes & the Permission Safety Net]]
- [[Claude Code/Part 4 Hooks and MCP, The Extension Architecture|Part 4 – Hooks & MCP: The Extension Architecture]]
- [[Claude Code/Part 6 Maintaining and Evolving Claude Code Ecosystem|Part 6 – Maintaining & Evolving Your Claude Code Ecosystem]]

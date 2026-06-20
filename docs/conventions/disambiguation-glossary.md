---
title: Disambiguation Glossary
created: 2026-05-15
updated: 2026-05-22
decay: evolving
type: convention
author: claude-code
last_touched_by: claude-code
touch_history:
  - "2026-05-22T17:05-05:00 claude-code (cross-link to cognitive-drift-registry)"
tags: [fleet, conventions, disambiguation, prompt-interpretation]
obn: sync
---

# Disambiguation Glossary

> [!important] **Operational implementation lives at [[cognitive-drift-registry]].**
> This glossary records *what each term can mean*. The registry records *how an agent will fail when the meaning is wrong* and the **Sense-Check protocol** to prevent it. Read both: semantic side here, failure-mode side there.

> [!info] A registry of terms in Jack's prompts that carry more than one meaning, or whose meaning has drifted over time. Its job is to stop an agent from acting on the wrong sense of a word.

## Companion files — one per audience

| File | Audience | Source of truth for |
|------|----------|---------------------|
| `disambiguation-glossary.md` | humans + agents reading prose | **meaning** — what each term can mean and how to resolve it |
| `disambiguation-glossary.json` | hooks / tooling consuming the map programmatically | the structured term map |
| `disambiguation-literals.txt` | anyone copying an exact string | **exact spelling** — canonical literals (paths, endpoints, identifiers) so they never drift |

Keep all three in sync. When you add a term here, add it to the `.json`. When a canonical path/endpoint/identifier appears in any entry, pin it in the `.txt`.

## The meta-rule

Every entry below has the same root cause: **a name was reused, renamed, or split across systems, and the old meaning was never retired** — it just sits next to the new one. No single vault file contradicts itself; the contradiction only appears when you read across files.

The operating rule for any agent reading Jack's prompts:

> When a term in this glossary is load-bearing for what you are about to do, resolve it against the freshest SSOT (`SESSION-CONTEXT.md` / vault `CLAUDE.md`), **state your interpretation in your first line of response**, and proceed. A misread then costs Jack one sentence to correct — not a wrong dispatch, a wrong file write, or a wasted paid API call.
>
> Ask a clarifying question only when (a) the senses are genuinely 50/50 from context, or (b) guessing wrong is asymmetric and expensive — see `research`.

---

## Terms

### `Ghost Models` — references to GPT-5.4, GPT-5.5, or Gemini 2.5

| Stale Term | Reality | SSOT |
|------------|---------|------|
| GPT-5.4 / 5.5 | Hallucination / Aspirational. Use Claude 3.5 Sonnet or Gemini 1.5 Pro. | `AGENTS.md` |
| Gemini 2.5 Flash | Hallucination. Use Gemini 1.5 Flash. | `MEMORY.md` |

**Resolution:** If a doc or prompt mentions a model that does not exist in the 2026-05 live stack, prune the claim. Do not attempt to "route" to non-existent models. PT's current operational model is `gemini-1.5-flash`.

### Olivier (`Soul`) vs Neo/PT (`Masks`) — identity hierarchy

| Identity | Role | Type |
|----------|------|------|
| **Olivier** | The OtterBot creature; warm, concise soul. | Underlying Persona |
| **Neo / PT** | Strategic Orchestrator (Neo) / Lead Engineer (PT). | Runtime Roles (Masks) |

**Resolution:** Olivier is "who I am" (the soul); Neo and PT are "what I do" (the roles). When receiving a prompt, I wear the mask appropriate to the tool (CLI=PT, Discord=Neo), but the underlying soul remains Olivier. Updated 2026-05-15 to resolve identity split-brain.

### `PT` — three unrelated meanings

| Sense | SSOT | Context cue |
|-------|------|-------------|
| Gemini CLI runtime — the dissent agent, "Pete Trump" | `=notes/CLAUDE.md` (Orchestration Topology) | dispatch, review, dissent, fleet, ticket |
| Physical therapy with Ryan Fraley, DPT | `atlas/health/pt-sessions-ryan.md` | health, recovery, rib, Ryan, appointment |
| Repo make targets `make pt-validate` / `pt-test-sync` | `=notes/CLAUDE.md` (Local Overrides) | backticked, "run", build, validate |

**Resolution:** Resolve from context. Health words → Ryan. Dispatch/dissent words → Gemini runtime. Backticks → make target. State the chosen sense in the first line. The runtime sense is the collision risk — prefer its surface name **Neo** when possible.

### `OB1` vs `OBn` vs `Khoj` — three memory/search layers, one letter apart

| Term | What it is | SSOT |
|------|-----------|------|
| **OB1** (Open Brain) | Cross-AI *thought* memory bus. Supabase pgvector. MCP entry `open-brain`. NOT a vault search engine. | `SESSION-CONTEXT.md` |
| **OBn** (Obsidian Brain) | Semantic *vault* search index. ChromaDB v2, Ollama embeddings. Read-only projection of the vault. | `SESSION-CONTEXT.md` |
| **Khoj** | Local self-hosted CLI/MCP vault-expert surface with curated context + preset agents. Reactivated 2026-05-11 (`localhost:42110`). | `SESSION-CONTEXT.md` |

**Resolution:** The vault on disk is SSOT. OBn is its search index; OB1 is a cross-AI thought log. Before acting, confirm the *operation* matches the *system*: capture/insight → OB1; semantic vault search → OBn or Khoj. If a prompt says "OB1" but the operation is a vault search, flag the mismatch rather than silently picking.

> **Drift watch:** `knowledge-graph.jsonl` historically claimed "Khoj retired 2026-04-11." Khoj was **reactivated 2026-05-11**. For any tool-status claim, verify against `SESSION-CONTEXT.md` before citing — the knowledge-graph lags on tooling facts.

### Runtime ↔ Surface — every fleet agent has two names

| Runtime (local process) | Surface (Discord/Telegram) | SSOT |
|-------------------------|----------------------------|------|
| Hermes (Nous Research Hermes Agent) | **Wings** — CC deployment lane | `~/Documents/Coordination/*-identity-mapping.md` |
| PT (Gemini CLI) | **Neo** — overseer / dissent | same |
| OLIVIER_MBP (OpenClaw gateway) | **Zoe** — browser automation | same |
| OpenCode | rbitr (`cortex.jack.digital/rbitr/`) | same |

**Resolution:** "Hand this to Wings / ask PT / message Zoe" is ambiguous between launching a local runtime and posting to a chat surface. Before any dispatch, name the full tuple back to Jack ("dispatching to the Hermes runtime, not the Wings Discord surface"). Canonical SoT is the `*-identity-mapping.md` glob (latest-modified wins). Do **not** trust `knowledge-graph.jsonl` for fleet topology — it has drifted (e.g. it once described Neo as a non-dispatchable persona while `CLAUDE.md` treats PT/Neo as a live dissent gate).

### `research` — a specific paid operation, not a verb

"Research X" usually means **Gemini Deep Research** — a 5–15 min paid run — not a quick web search or vault lookup. `research` is also an MCP profile name.

**Resolution:** This is the one term where guessing wrong is expensive in both directions. For any bare "research X", ask one cheap clarifying question first — *Gemini Deep Research, web search, or vault lookup?* — before spending the expensive path.

### Work-item homes — four places, no routing rule

| Directory | Holds | Lifecycle |
|-----------|-------|-----------|
| `docs/plans/` | Strategic, cross-session plans (190+ files) | `status:` frontmatter; stays after `done` |
| `efforts/current/` | Active, bandwidth-allocated work hubs | `intensity:` + `status:`; moves to `efforts/archive/` |
| `claude/tasks/active/` | Atomic queue items (v2 task queue) | moves to `claude/tasks/closed/` |
| `tasks/personal|transition|job-search|portfolio/` | Personal Obsidian task lists | per-file |

**Resolution:** "Make a plan" → `docs/plans/`. "Add a task" for the autonomous queue → `claude/tasks/active/`. Personal/admin items → `tasks/`. When ambiguous, state where you are filing it in one line so Jack can redirect. Before quoting any **dashboard** of work state, check its `updated:` frontmatter against the body's "Last refreshed" line and `git log` — if they disagree, say so rather than quoting it as current.

### `=notes` path + the daily-note rule

The vault is `/Users/jack.reis/Documents/=notes`. The leading `=` is parameter-expansion in zsh, so shell commands need `~/Documents/\=notes`. Some runbooks use the unescaped form — do not copy those verbatim.

**Resolution:** In tool calls, always use the **fully-qualified absolute path** `/Users/jack.reis/Documents/=notes/...` (file tools need no shell escaping). Escape (`\=notes`) only when handing a *shell command* to Jack. The "NEVER overwrite daily notes" rule means never replace wholesale — appending and fixing-for-accuracy *within* a block is explicitly allowed.

### `n8n` vs `n` / `cn` / `w` — opaque literal sharing a prefix with the shell aliases

| Token | Meaning | SSOT |
|-------|---------|------|
| `n8n` | Workflow-automation tool; the fleet's unified bus for webhook ingress and declarative routing | `=notes/CLAUDE.md` (Orchestration Topology) |
| `n` / `cn` | Shell alias for Claude Code (`cn -p <profile>` selects an MCP profile) | `SESSION-CONTEXT.md` |
| `w` | Shell alias for the tmux workbench (Claude + OpenClaw + git + logs) | `SESSION-CONTEXT.md` |

**Resolution:** The textual collision is mild, but `n8n` is a numeronym ("nodemation") that is easy to misread, and it shares a prefix with the `n`/`cn` Claude Code aliases. "Trigger n8n" / "the n8n bus" is never a request to launch a Claude Code session — it means the workflow engine. Pinned as a canonical literal in `disambiguation-literals.txt`.

---

## Skill-routing collisions

Distinct from term ambiguity: clusters of skills whose trigger phrases overlap, so a prompt can match the wrong one. Until the skill descriptions are tightened, resolve as noted.

| Cluster | Skills | Collision phrase | Resolution |
|---------|--------|------------------|------------|
| Session start | `session-briefing`, `ob1-session-briefing`, `ledger-lifecycle`, `session-lifecycle` (superseded) | "briefing", "where was I" | `ledger-lifecycle` is the current unified entry. `session-lifecycle` is superseded — do not invoke. |
| Drive sharing | `vault-to-share`, `vault-to-pdf`, `vault-to-gdrive-set` | "share to drive" | Simple public link → `vault-to-share`. Editable triad for review → `vault-to-gdrive-set`. PDF only → `vault-to-pdf`. |
| Dashboard sync | `dashboard-refresh`, `gdrive-sync`, `daily-metrics-sync` | "sync dashboard" | Date math only → `dashboard-refresh`. Push *out* to Drive → `gdrive-sync`. Pull daily data *into* the dashboard → `daily-metrics-sync`. |

---

## Maintenance

- New ambiguous term → add an entry here **and** to `disambiguation-glossary.json`.
- New canonical path/endpoint/identifier → pin it in `disambiguation-literals.txt`.
- When a term's meaning changes (rename, supersession), update the entry and note it in a **Drift watch** callout — do not delete the old meaning silently; that is the exact failure mode this glossary exists to prevent.

Source: distilled from a 5-agent vault sweep, 2026-05-15. See also [[docs/conventions/dialectic-vocabulary]] (dialectic terms), [[SESSION-CONTEXT]] (live state SSOT).

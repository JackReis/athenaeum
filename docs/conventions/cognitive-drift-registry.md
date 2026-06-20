---
title: Cognitive Drift Registry
created: 2026-05-22
updated: 2026-05-22
decay: evolving
type: convention
author: claude-code
last_touched_by: claude-code
touch_history:
  - "2026-05-22T17:00-05:00 claude-code (cognitive-drift-registry init)"
tags: [fleet, conventions, cognitive-drift, ghost-patterns, agent-guardrails]
obn: sync
---

# Cognitive Drift Registry

> [!warning] **Operational implementation of [[disambiguation-glossary]].**
> The glossary records *what each term can mean*. This registry records *how an agent will fail when the meaning is wrong*, and the **Sense-Check protocol** to short-circuit that failure before it becomes a wrong dispatch, a wrong file write, or a wasted paid API call.

## The Sense-Check protocol

When a load-bearing term in this registry appears in a prompt, runbook, or vault doc, **before acting**:

1. **State the chosen sense** in your first line of response.
2. **Name the SSOT** you resolved against (`SESSION-CONTEXT.md`, `=notes/CLAUDE.md`, `*-identity-mapping.md` — *not* `knowledge-graph.jsonl`, which lags).
3. **If the senses are 50/50 from context** *and* guessing wrong is asymmetric (paid API, irreversible write, cross-session dispatch), ask one cheap clarifying question. Otherwise, proceed.

Source line cost: one sentence. Wrong dispatch cost: minutes-to-hours plus rollback. The bias is to state and proceed.

---

## Pattern 1 — Orchestration Collision (`OpenClaw` → `CC` → `Rbitr`)

| Aspect | Detail |
|---|---|
| **Ghost** | Docs across the vault describe Claude Code as primary orchestrator (ADR-2026-03-29), with OpenClaw supplemental and rbitr aspirational. |
| **Reality** | **ADR-2026-05-13 supersedes**: rbitr/Arbiter (OpenCode + Sonnet 4.6) is the routing brain, n8n is the bus, Hermes/Wings is the worker deployment lane, **Claude Code is now a worker tier**. V1 tracer-bullet live in container on `:8765` as of 2026-05-21 (commit `96e364adb`). PT/Neo is the dissent gate, not a router. |

**Failure Mode.** An agent reading older docs treats CC as the dispatch tier and routes Linear work through file handoffs instead of `arbiter dispatch` → `worker_spawned`. The work lands, looks fine, and bypasses budget caps, dissent review, and the Linear queue projection. Two parallel sessions then race on the same ticket because neither went through the bus.

**Resolution Protocol.**
- For **Linear-routed work** (ticket has `arbiter:*` label or originates from a webhook): route through n8n → `:8765/dispatch`. Workers materialize via Hermes worktree + CC session.
- For **non-Linear coordination** (vault edits, session-to-session messages, in-flight context): file-handoff pattern in `claude/mcp-coordination/state/session-handoffs/` is still the operational path until full cutover (per [[docs/plans/2026-05-21-rbitr-v1-closeout]]).
- **Never** describe CC as "primary orchestrator" in fresh prose. Cite ADR-2026-05-13 and AGENT_DESIGN.md when the topology comes up.
- The `Tonkotsu` runtime is **idea-source only**, not an executor. Do not dispatch to it.

**SSOT:** `=notes/CLAUDE.md` (Orchestration Topology), `AGENT_DESIGN.md` (vault root), [[docs/architecture/arbiter-design]], [[docs/architecture/rbitr-design]].

---

## Pattern 2 — `PT` Sense Overload (Personnel · Health · Tooling)

| Aspect | Detail |
|---|---|
| **Ghost** | `PT` is treated as a single referent across docs. |
| **Reality** | Three unrelated meanings live next to each other in the vault: the **Gemini CLI runtime** ("Pete Trump", dissent agent, Discord surface = Neo), **physical therapy** (Ryan Fraley, DPT — and Ryan was *discharged 2026-03-20*, so future PT may be Amy/Ted/Eric), and the **repo make targets** (`make pt-validate`, `make pt-test-sync`). |

**Failure Mode.** Common drift patterns observed:
1. Agent runs `make pt-validate` when Jack asked about PT *appointment scheduling*, or vice versa.
2. Agent dispatches to the PT runtime ("ask PT to review") when Jack meant the health context.
3. Agent treats "PT discharged" as a *runtime decommission* (silent panic about losing the dissent gate) when it referred to Ryan's discharge from his caseload.

**Resolution Protocol.** Context cues:
- **Health words** (rib, recovery, appointment, Ryan, exercise, body, supplement) → physical therapy. Note Ryan-discharged-2026-03-20 if scheduling.
- **Dispatch words** (review, dissent, ticket, fleet, architecture, security) → Gemini CLI runtime. **Prefer the surface name `Neo`** to disambiguate.
- **Backticked / "run" / build verbs** → make target.
- When stating the chosen sense, name it: *"PT in the health sense — Ryan Fraley discharged 2026-03-20"* or *"the Neo runtime (Gemini CLI dissent gate)"*.

**SSOT:** [[disambiguation-glossary#`PT` — three unrelated meanings]], `=notes/CLAUDE.md` (Orchestration Topology + Local Overrides), `atlas/health/pt-sessions-ryan.md`.

---

## Pattern 3 — Memory Drift (`OB1` vs `OBn` vs `Khoj`)

| Aspect | Detail |
|---|---|
| **Ghost** | Three names one letter apart, all framed as "memory." `knowledge-graph.jsonl` once recorded "Khoj retired 2026-04-11" — still wrong as of 2026-05-22. |
| **Reality** | Three **distinct systems** with different SSOT roles: **OB1** (Open Brain, Supabase pgvector) = cross-AI *thought* bus, not a vault index; **OBn** (Obsidian Brain, ChromaDB v2) = read-only *vault* semantic index; **Khoj** = self-hosted CLI/MCP vault expert (reactivated 2026-05-11, `localhost:42110`), not retired. |

**Failure Mode.**
1. Agent invokes `capture_thought` against OB1 expecting it to surface in a vault search later — OB1 stores thoughts, OBn indexes vault files; the thought never appears in the vault.
2. Agent runs a semantic vault query against OB1 (wrong system), gets cross-AI thought noise back, then quotes it as "vault findings."
3. Agent cites `knowledge-graph.jsonl` for Khoj status, declares it retired, doesn't query it — missing the entire surface.

**Resolution Protocol.**
- **Vault on disk is SSOT.** OBn is a *projection*; treat it as a cache that can lag.
- Match the operation to the system: **capture a durable thought** → OB1 (`open-brain` MCP). **Semantic search of vault files** → OBn (`obn_query.py`) or Khoj MCP. **Curated agent surface over vault** → Khoj.
- If a prompt says "OB1" but the operation is a vault search, **flag the mismatch** rather than silently routing.
- For any tool-status claim about OB1/OBn/Khoj, verify against `SESSION-CONTEXT.md`, not `knowledge-graph.jsonl`.

**SSOT:** [[disambiguation-glossary#`OB1` vs `OBn` vs `Khoj`]], `SESSION-CONTEXT.md`.

---

## Pattern 4 — Work-Item Home Fragmentation (4+ task directories)

| Aspect | Detail |
|---|---|
| **Ghost** | Docs reference "tasks" as if there's one queue. |
| **Reality** | Four homes with different lifecycles and no auto-routing: `docs/plans/` (190+ strategic files, `status:` frontmatter), `efforts/current/` (active hubs, `intensity:` + `status:`), `claude/tasks/active/` (atomic v2 queue, moves to `closed/`), `tasks/personal\|transition\|job-search\|portfolio/` (personal Obsidian task-plugin lists). Plus `INFRASTRUCTURE-TASKS.md` at vault root for CC infra. |

**Failure Mode.**
1. Agent files a new "task" in `docs/plans/` when it belonged in `claude/tasks/active/` — the autonomous queue never sees it.
2. Agent quotes a stale dashboard summarizing one home, treating it as the *total* work state.
3. Agent dispatches a subagent to "process the task queue" without naming which home, and the subagent picks `tasks/personal.md` (wrong audience, personal context).

**Resolution Protocol.**
- **"Make a plan" (multi-session, strategic)** → `docs/plans/` with `status: draft|ready-to-execute|in-progress|done`.
- **"Add to the autonomous queue"** → `claude/tasks/active/` (v2 schema: `priority: p0-p3`, `locked_by`, `lock_acquired`).
- **"Active hub" with bandwidth allocation** → `efforts/current/` with `intensity:` + `status:`.
- **"Personal/admin todo"** → `tasks/personal.md` etc.
- **"CC infra"** → `INFRASTRUCTURE-TASKS.md` at vault root.
- When the home is ambiguous, **state in one line where you are filing it** so Jack can redirect cheaply.
- Before quoting any *dashboard* of work state, check its `updated:` frontmatter against the body's "Last refreshed" line and `git log`. If they disagree, say so.

**SSOT:** [[disambiguation-glossary#Work-item homes]], [[INFRASTRUCTURE-TASKS]], `docs/architecture/inter-session-protocol-v2.md`.

---

## Provenance Drift — Warning Signs for Audit Failure

These aren't sense-overloads; they're **slow-erosion patterns** where the audit trail loses fidelity one commit or one handoff at a time. Catching them is how the fleet keeps the Examined-Claim discipline honest.

### Warning 1 — Git Trailer Drift

**Pattern.** Per `=notes/CLAUDE.md`, AI-authored commits must include both:
- `Authored-by: <agent> (session:<short-id>)` — the runtime that did the work
- `Co-Authored-By: <model> <noreply@anthropic.com>` — the model identity

**Drift signal.** A commit drops one of the trailers (commonly `Authored-by:`) or uses a stale session id pulled from `.claude/memories/.session-labeled` (shared cache, rotates every CC spawn — see [feedback memory](../../.claude/projects/-Users-jack-reis-Documents--notes/memory/feedback_session_labeled_is_shared_cache.md)).

**Sense-Check.** Before any commit, derive your session id from `$CLAUDE_JOB_DIR` basename or your `--session-id` argv, **not** from `.session-labeled`. Spot-check `git log --format=%B -3` after committing to confirm both trailers landed.

**SSOT:** `docs/conventions/agent-custody-provenance.md` (canonical), `=notes/CLAUDE.md` (Communication section).

### Warning 2 — Handoff Thinning

**Pattern.** Session handoff v2 schema (`docs/architecture/inter-session-protocol-v2.md`) expects: `tasks_completed`, `files_changed`, `next_actions`, `verifier`, `blockers`, plus the five-field Done promise from `CLAUDE.md` (artifact, path, verifier, commit+push, caveats).

**Drift signal.** Handoffs land with empty `next_actions`, no `verifier` block, or a status of `complete` that contradicts the body's "Left Open" section. The next session reads the frontmatter, trusts `complete`, and doesn't notice the body.

**Sense-Check.** Before writing a handoff, run through the five fields aloud. If `verifier:` is empty, the work isn't independently re-runnable and Done is a self-claim only. If `blockers:` is empty but `status:` is `partial-complete-user-decision-needed`, the body and frontmatter disagree — fix one.

**SSOT:** `docs/architecture/inter-session-protocol-v2.md`, `docs/conventions/fleet-directive.md`.

### Warning 3 — Stale `$HOME` docs poisoning the fleet

**Pattern.** Authoritative-titled topology/identity docs *outside* the vault SSOT (e.g., `~/OPENCLAW_FLEET_MAP.md`, dated 2026-04-24, pre-Arbiter) get ingested into OBn and quoted back as truth.

**Sense-Check.** For any fleet/topology claim, the SSOT is `~/Documents/Coordination/*-identity-mapping.md` (latest-modified wins) or `=notes/CLAUDE.md` — never `$HOME/*.md` runbooks unless explicitly listed in `disambiguation-literals.txt`. Verify `mtime` and cross-check before quoting.

**SSOT:** [feedback memory: stale-home-docs-poison](../../.claude/projects/-Users-jack-reis-Documents--notes/memory/feedback_stale_home_docs_poison.md).

---

## Maintenance

- A pattern earns an entry here when an agent has demonstrably failed on it **and** the failure mode is reproducible from current docs (i.e., not a one-off skill issue).
- When a sense-overload is resolved (a name is retired, a system is decommissioned), keep the entry and add a **Resolution date** note — do not delete. Silent removal is the exact failure mode the registry exists to prevent.
- Pair every new entry here with an addition to [[disambiguation-glossary]] (semantic side) and, where a canonical literal is involved, `disambiguation-literals.txt` (string side).

## See also

- [[disambiguation-glossary]] — semantic SSOT for ambiguous terms
- [[dialectic-vocabulary]] — vocabulary for examined-claim discourse
- [[agent-custody-provenance]] — custody + provenance SoT
- [[fleet-directive]] — Done = artifact + path + verifier + commit + push + caveats
- [[agent-observer-principle]] — claims are superposition until measured

Source: distilled from a multi-agent vault sweep prior to 2026-05-22; codifies failure modes observed across the fleet during the 2026-05 rbitr v1 ramp.

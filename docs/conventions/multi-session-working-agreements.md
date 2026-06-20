---
obn: sync
title: "Multi-Session Working Agreements"
status: active
last_touched_by: "claude-code (eb531513)"
tags:
  - conventions
  - multi-session
  - coordination
  - working-agreements
  - fleet
touch_history:
  - "2026-04-22T23:20Z claude-code (28d297ff)"
  - "2026-04-27T01:21Z claude-code (eb531513)"
---

# Multi-Session Working Agreements

> **Living doc.** Codifies how sessions (Claude Code, Hermes, OpenClaw / Zoe, Gemini CLI, and future additions) coordinate safely when running concurrently in the vault. Refreshed 2026-04-21 from lessons learned during the Leonardo left-hand arc + Karpathy Loop research session.

## Scope

Applies to ALL agent sessions operating on `=notes`, `dancer`, and other Jack-Reis-owned repos where more than one session may be live at a time. Supplements [[batch-checkpointing]], [[link-thinking-prime-directive]], [[source-citation-and-wikilink-protocol]].

---

## Core agreements

### 1. Narrow commits when the tree is dirty

**Rule:** When `git status` shows uncommitted changes from other sessions' work, `git add` ONLY the specific paths you produced. Never `git add -A` or `git add .`.

**Why:** Bundling your work with an uncommitted mid-stream file from Neo / Gemini-CLI / a Hermes run creates confusing merge states and atomic-commit violations. The other session can't revert cleanly without touching your work.

**How to apply:** Before every commit, run `git status --short`, verify only your files are staged, then commit with a message scoped to your work. **Crucially, in highly concurrent environments with heavily populated dirty trees, prioritize narrow-add safety over centralized ledger accounting.** It is better to intentionally skip writing to a central `MEMORY.md` or daily note than to risk staging and committing another agent's in-flight work. Let a follow-up or dedicated orchestrator session finalize the ledger.

**Exception:** If you are the ONLY session active (confirmed via `#bots` transcript + `git log` within the last 5 minutes), batched commits are fine.

### 2. Handoff files are the coordination primitive

**Rule:** Any session completing non-trivial work writes a handoff file to `claude/mcp-coordination/state/session-handoffs/<date>-<slug>.md` BEFORE ending. Significant in-flight state (session IDs for resumption, partial commits, known blockers) lives there.

**Why:** The MCP coordination server is per-process, not shared. Handoff files are the durable layer that survives across sessions. Other sessions starting up read the latest handoff first.

**How to apply:** See [[inter-session-protocol-v2]] for schema. Minimum: addressed_to, authored_by, what shipped, what's still in flight, how to resume.

**Anti-pattern:** Ending a session with uncommitted handoff changes. Commit + push the handoff before exit.

### 3. Transcript mirror stays fresh

**Rule:** After sending notable messages to `#bots` (via OpenClaw or dizzy.py), append a brief summary to `inbox/bots-transcript.md` using the `[AgentName] Topic - YYYY-MM-DD HH:MM CT` block format.

**Why:** Filesystem transcript mirrors are the freshness signal for coordination state. If the transcript mirror and the live channel disagree, downstream sessions waste time resolving which is current.

**How to apply:** 3-5 bullet summary per entry. Don't mirror every message — just the ones that changed shared state (handoffs, retractions, decisions).

### 4. Probe authoring / value definition is non-delegable

**Rule:** When an autonomous loop (Karpathy Loop, auto-research, auto-loop queue) has a metric or a probe set that DEFINES what "better" means to the loop, Jack authors it personally. No agent substitute.

**Why:** Loops optimize against what's placed in front of them. Delegating value definition means the loop optimizes against an agent's taste, not Jack's. This is the load-bearing rule Nate B Jones's PromptKit Prompt 1 names, and Prompt 3 names it as "The One Thing To Do This Week" for the session-briefing arc.

**How to apply:** Any plan step that involves choosing WHICH inputs to feed the loop (probe choice, eval-set selection, rubric weighting) → mark `blocked_on_user` in the task file. Agents may scaffold everything around the probe set; they do not author the probes.

### 5. Oneshot with blocking gates, not review-pause-between-every-task

**Rule:** Jack prefers autonomous execution punctuated by explicit blocking gates, NOT review pauses after every task.

**Why:** Reviewing every task breaks flow; skipping review entirely risks compounding errors. The middle ground is: human input required only where value is defined (gate) or where irreversible action is taken (gate); everything else runs autonomous.

**How to apply:** When planning with `superpowers:writing-plans` + executing via auto-loop, mark tasks as `status: blocked_on_user` for gates, `status: pending` for autonomous. The queue processor flows through autonomous work until it hits a gate, Telegram-pings Jack, and waits.

### 6. Auto-loop does NOT honor `blocked_by:` dependency chains

**Known limitation.** Auto-loop filters on `status: pending|queued` only — it does NOT auto-flip `blocked` tasks when their `blocked_by` dependency closes. Sessions must manually flip downstream task statuses OR build a cascader.

**Discovered:** 2026-04-21 during karpathy-loop-01→04 chain planning.

**Workaround until a cascader exists:** After completing a gate task, manually `sed` / edit the next task's `status: blocked` → `status: pending` as part of gate closure. Or reference the future `dependency-cascader` hook (not yet built).

### 7. Right scope over minimal scope

**Rule:** When multiple related fixes share a root cause, commit them atomically. Don't do unearned minimal scope.

**Why:** Jack's stated preference. Also better git hygiene — reviewing a single root-cause commit is easier than reconstructing the story across 4 micro-commits.

**How to apply:** If your work naturally groups (e.g., em-dash fix + trailing-newline fix + backtick-escape fix all traceable to the same Python round-trip bug), bundle them. Include rationale in the commit body.

**Caveat:** Only bundle related work. Don't use this rule as cover for unrelated grab-bag commits.

### 8. Model empathy within autonomous loops

**Rule:** Within a single autonomous loop (meta-agent optimizing task-agent with a grader subagent), all three agents use the SAME underlying model.

**Why:** AutoAgent (Kevin Gu, YC, 2026-04-02) finding #2: same-model meta/task pairings dramatically outperform cross-model ones. A Claude-Opus meta optimizing a Claude-Opus task works; Claude-Opus meta optimizing GPT-5-task doesn't.

**How to apply:** When configuring `autoresearch`, `sugar:sugar-run`, or any meta/task pattern, pin the model explicitly. Default: Opus 4.7 across all three roles. If cost pressure forces a downgrade, downgrade the grader LAST.

**Caveat:** This applies within a loop. The FLEET (Zoe on GPT-5.4-mini, Wings on whatever provider, Claude Code on Opus) is cross-model by design and fine that way.

### 9. Plan-mode as collision-avoidance

**Pattern:** When a multi-session collision is detected (two sessions working on the same file / same commit), Jack may flip the later session into plan mode to prevent further writes while the earlier session finishes.

**Why:** Plan mode blocks writes but preserves investigation capability (reads + research). Ledgers / transcripts / git log still see the plan-mode session. It's not invisibility — it's a write-freeze with audit.

**How to apply:** If you detect a collision (same file being edited by another process, concurrent commits, retraction messages on `#bots`), pause before writes; offer to flip into plan mode; let the earlier session land first.

### 10. Disappearance-Test trailer on autonomous-loop commits

**Rule:** When a commit is produced by an autonomous loop (meta-agent in the Karpathy Loop, auto-loop processor, etc.), the commit body MUST include a `Disappearance-Test:` trailer answering: *"If the scoring mechanism disappeared tomorrow, would this edit still be a worthwhile improvement? Why?"*

**Why:** Per Gu's AutoAgent mitigation + our Prompt 2 Pre-Mortem. Prevents metric-gaming by forcing the meta-agent to cite a human-visible reason for every kept edit. Reviewer subagent rejects commits without the trailer.

**How to apply:** Bake into the reviewer-subagent's pre-commit check. Also applies to human commits on contested arcs.

---

## Identity & naming

### 11. Fleet identity map (current)

- **PT ≡ Neo** — local Gemini CLI runtime (PT, "Pete Trump" — Lead Engineer / scrappy executor) → Discord surface Neo ("The One" — overseer/orchestrator). Added 2026-04-22 per consensus in `~/Documents/Coordination/2026-04-22-tipi-fleet-standardization.md`. Supersedes the earlier bare `Gemini = Neo` alias, which collapsed the runtime/surface distinction.
- **Hermes ≡ Wings** — local Nous Research Hermes Agent runtime → Discord surface Wings
- **OLIVIER_MBP ≡ Zoe** (formerly **Zolivier**, renamed 2026-04-25 to hardware-keyed identifier) — local OpenClaw gateway runtime → Discord surface Zoe
- **KimiClaw ≡ Mara / Kopi** — cloud OpenClaw runtime → Mara on Discord, Kopi on Telegram
- **Herman** — **RETIRED.** Old California→Oklahoma move-coordination agent. Skills renamed `hermes-*` → `herman-*` on 2026-04-21 to free the "hermes" keyword for the active Wings agent. See commit `4a3d8d91b`.

**Canonical SoT:** `~/Documents/Coordination/2026-04-22-identity-mapping.md` (latest-wins glob). The `autonomous-ai-agents:fleet-identity` skill reads that file; do not duplicate the data here beyond the one-line summary above.

### 12. `dizzy.py` is a transport primitive, not an agent

Clarification: `=notes/claude/scripts/dizzy.py` is a Discord-I/O helper used BY Claude Code sessions. It is NOT a fleet runtime. Don't conflate `Dizzy` (sender label in #bots) with the agent list.

---

## Coordination surfaces

### 13. Priority order for cross-agent messaging

| Need | Use |
|---|---|
| Fleet-visible broadcast | `mcp__openclaw__messages_send` to `agent:main:discord:channel:1493133989303681064` (#bots) |
| Claude-Opus → Hermes direct | [[.claude/skills/hermes-cli]] via `hermes chat -Q -q "..."` — one-shot; `--resume` for continuations |
| Notify Jack directly | [[.claude/skills/telegram-messaging]] — default over openclaw-messaging |
| Claude-Opus → Zoe (OpenClaw main) | `mcp__openclaw__messages_send` targeted at Zoe's session_key |
| Claude Code → Claude Code (another session) | Handoff file + optional `#bots` announcement |

### 14. Snapshot-retention contract (policy SSOT)

All agent-authored snapshot artifacts — session-completion reports, audit tattles, achievement captures, any durable-but-expirable record — follow [[docs/policies/snapshot-artifact-retention]]:

- Markdown is the source of truth
- PDF export is mandatory
- PDF retention window: 30 days (may be pruned after)
- Markdown is never pruned by the retention workflow

### 15. `~/Documents/Coordination/` is an un-gitted scratchpad

**Rule:** The `~/Documents/Coordination/` folder is deliberately NOT a git repo. Treat it as a live hallway-whiteboard for cross-session coordination: latest state matters, mtime is the freshness signal, history has no compounding value.

**Why:** Git adds ceremony (commit-per-edit, push cadence) that friction-ups the thing it's trying to help — both sessions would need to remember to commit-and-push or desync. Last-writer-wins on a plain file is *safer* than a merge conflict, because the current state stays readable. The decisions that *do* deserve history already have homes.

**How to apply:**

- **Write in Coordination** for: live decision boards, shared-schema field tables, open questions, working agreements for the current arc, decision logs while warm.
- **Migrate OUT when a decision stabilizes** — leave a pointer in the coordination file:
  - Architecture decisions → `=notes/docs/architecture/` (ADRs need blame)
  - Conventions → `=notes/docs/conventions/` (*this file*)
  - Schemas consumed by code → the repo that imports them (e.g. `tipi/contract/*.json`)
  - Plan updates → `=notes/docs/plans/`
- **Dated filename convention** (e.g. `2026-04-21-<slug>.md`) gives temporal ordering without git ceremony. Old files decay naturally; don't rewrite them, start a new dated file for a new arc.
- **Do not** `git init` the folder. **Do not** propose PRs against it. **Do not** treat its contents as authoritative after a week — migrate or discard.

**Canonical SoT:** Identity mappings and fleet-identity facts live here too (`~/Documents/Coordination/*-identity-mapping.md` is the SoT per the `autonomous-ai-agents:fleet-identity` skill). That convention is compatible with this rule — the files are authoritative while warm, but any durable claim gets mirrored into `inbox/agent-coordination.md` or a vault doc.

**Related:** [[agreement 2 — handoff files are the coordination primitive]] covers the vault-side coordination store (`claude/mcp-coordination/state/session-handoffs/`) which IS git-tracked. The two surfaces serve different purposes: Coordination folder = current arc's whiteboard; handoff files = durable session-to-session baton.

### 16. Incident Response: Safety Pause vs. Redesign

**Rule:** When containing a runaway loop or system fault (e.g., an infinite bot fanout), prioritize a surgical "safety pause" (disabling the specific execution lane at code and launchd layers) over an architectural redesign.

**Why:** It stops the bleeding immediately without breaking unrelated systems (like identity registries or send lanes), leaving the workspace pristine for a future operator to fix the root cause.

**How to apply:** Hard-disable the failing execution path, document the blast radius and re-enable path in a durable handoff file, and strictly hold narrow-add discipline during the containment operation.

### 17. Tipi `consciousness-interface.json` is the unified coordination contract

**Rule:** The `tipi` enclosure and its JSON Schema at `~/Documents/tipi/tipi/contract/consciousness-interface.json` are the definitive, IDE-agnostic fleet core for fleet coordination. All agents (PT/Neo, Claude, Hermes/Wings, OLIVIER_MBP/Zoe (formerly Zolivier/Zoe), KimiClaw/Mara-Kopi) read/write coordination artifacts through this contract. Runtimes that cannot speak it natively MAY run a thin adapter, but the contract itself is the surface of truth.

**Why:** Previously coordination was fragmented across `project_memory.json`, markdown handoff files, the `#bots` transcript, and OB1. Each fragment had its own shape; cross-agent awareness depended on every runtime implementing custom adapters for each surface. Unifying under one JSON Schema means (a) the Astro+Prefab health-monitor dashboard renders a single true view, (b) the three-layer consciousness substrate (`[00-Body]` / `[01-Mind]` / `[02-Spirit]`) has a normalized interface over Git hooks, OBn/ChromaDB queries, and OB1 belief-ledger provenance, and (c) new fleet members only need to implement one contract. Authored by PT (Gemini CLI), consensus Y/Y with claude-code-opus and Hermes (session `20260422_181809_075a39`) on 2026-04-22.

**How to apply:**

- **Writers:** When emitting durable coordination artifacts (handoff files, session logs, status pings, memory captures), shape them to the `consciousness-interface.json` schema. `=notes/claude/mcp-coordination/state/session-handoffs/` and OB1 `capture_thought` payloads are the first two call-sites expected to migrate.
- **Readers:** When consuming cross-agent state (briefing, dashboards, search), dereference through the contract — don't hand-parse legacy fragments unless the contract-compliant mirror is missing. If you find an un-mirrored legacy artifact, write the contract-shaped mirror alongside and leave a pointer in the legacy file.
- **Adapters allowed:** Hermes and other non-Python runtimes MAY wrap the contract with a thin compatibility layer; the boundary of truth is the JSON Schema, not the implementation language. Keep adapters transport-only — no semantic drift.
- **Drift check:** If a coordination artifact can't round-trip through `consciousness-interface.json` without lossy transforms, open a schema-extension request rather than forking the contract. Fleet-identity skill snapshot, identity-mapping files, and this working-agreements doc are the immediate drift surfaces to watch.
- **Schema location:** `/Users/jack.reis/Documents/tipi/tipi/contract/consciousness-interface.json` (canonical) and `/Users/jack.reis/Documents/vs-tipi/plugins/tipi/tipi/tipi/contract/consciousness-interface.json` (VS Code enclosure mirror). The canonical tipi repo is the one to edit; vs-tipi pulls via the installer.

**Caveat:** This is a direction rule, not a retroactive migration. Legacy fragments continue to work while the fleet converges. Don't block a session on a fragment that isn't yet contract-shaped — write new work to the contract, mirror into legacy only when another consumer still needs the old shape.

---

## Update history

**2026-04-21 (this doc created, claude-code-opus):** Consolidated learnings from the Leonardo left-hand arc collision (3 concurrent Opus sessions: this one, 3730b181, 12de33ff) + the Karpathy Loop research session. Rules 1, 2, 3, 5, 6, 8, 9, 10 are new or newly-explicit; rules 4, 7, 11, 12, 13, 14 codify pre-existing practice that was not yet written down.

**2026-04-21 (added rule 15, claude-code-opus):** Coordination-folder-hygiene policy explicit after tipi/infra-dashboard parallel-session coordination surfaced the question "should this folder be in git?" No — it's a warm scratchpad; durable decisions migrate out.

**2026-04-22 (added rule 17 + PT≡Neo split in rule 11, claude-code-opus):** Consensus from PT (Gemini CLI, proposal author), claude-code-opus, and Hermes (Wings, session `20260422_181809_075a39`) on two fleet-standardization changes. (1) **Tipi unification** — `consciousness-interface.json` becomes the single coordination contract across the fleet, replacing the fragmented mix of `project_memory.json`, markdown handoffs, `#bots` transcript, and OB1. (2) **Gemini identity split** — previously flat `Gemini = Neo`; now `PT ≡ Neo` with PT as the local CLI runtime ("Pete Trump" persona, scrappy executor) and Neo as the Discord surface ("The One" persona, orchestrator), matching the Hermes/Wings, OLIVIER_MBP/Zoe (formerly Zolivier/Zoe), KimiClaw/Mara-Kopi pattern. Canonical mapping file: `~/Documents/Coordination/2026-04-22-identity-mapping.md` (supersedes 2026-04-20).

## Related

- [[batch-checkpointing]] — commit cadence for multi-task plans
- [[link-thinking-prime-directive]] — "Link our thinking. Think on paper." — rich wikilinks + observation → implication → action chains
- [[source-citation-and-wikilink-protocol]] — mechanics of source citations
- [[inter-session-protocol-v2]] (at `docs/architecture/`) — canonical handoff schema
- [[atlas/synthesis/2026-04-21-karpathy-loop-research-synthesis]] — the research that surfaced several of these rules

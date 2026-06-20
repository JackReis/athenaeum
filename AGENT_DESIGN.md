---
title: Agent Design — Dramatis Orchestration Topology
status: v1-tracer-bullet-active
deployment_status: dispatch→spawn bridge live in container (commit 96e364adb on main); sidecar + n8n exports + ADR-0011 pending per docs/plans/2026-05-21-rbitr-v1-closeout.md
last_grilled: 2026-05-13
supersedes: implicit "Claude Code as primary orchestrator" topology (ADR-2026-03-29, CLAUDE.md Key Decisions)
last_touched_by: "codex"
doc-type: architecture
authoritative_for:
  - Dramatis orchestration design
  - n8n routing contract
  - worker lifecycle (Symphony pattern)
related:
  - "[[docs/architecture/fleet-tipi-identities]]"
  - "[[docs/architecture/agentic-os-hermes-wings-discord-beacon]]"
  - "[[docs/architecture/inter-session-protocol-v2]]"
  - "[[docs/adr/0014-dramatis-orchestration-decision-layer]]"
touch_history:
  - "2026-05-14T02:43Z claude-code (bd83817c)"
  - "2026-05-20T21:55Z claude-code (6a1fd022) — STALE deferred-not-deployed banner, superseded next morning"
  - "2026-05-21T22:30Z claude-code (splendid-jumping-meerkat-correction) — banner reverted; rbitr v1 tracer-bullet active per 96e364adb"
  - "2026-05-21T21:19Z claude-code (6a1fd022)"
  - "2026-06-03T01:30Z codex — promoted Dramatis as decision layer; retained rbitr as runtime substrate"
---

# Agent Design — Dramatis Orchestration Topology

> **🟢 V1 TRACER-BULLET ACTIVE (2026-05-21).** The dispatch→spawn bridge in `rbitr_shim.py` is live in the running rbitr container (commit `96e364adb` on main; sister branch `rbitr-v1-unstick` adds the spawner sidecar service in docker-compose). JAC-20 was successfully replayed end-to-end against `http://localhost:8765` — queue dropped 5→4, `worker_spawned` event recorded, HTTP 202 with `worker_id`. n8n bus + Linear ingress + full deployment closeout pending per [[docs/plans/2026-05-21-rbitr-v1-closeout]]. This banner CORRECTS the stale "deferred-not-deployed" stamp written 2026-05-20 — see [[claude/mcp-coordination/state/session-handoffs/session-rbitr-v1-unstick-execution-20260521]] for the bridge work.

> **Dramatis naming correction (2026-06-03):** ADR-0014 promotes **Dramatis** as the orchestration decision layer. Existing **rbitr** artifacts remain the v1 runtime substrate: HTTP dispatch, event logs, SQLite projection, CLI inspection, and spawn plumbing. Compatibility rule: **Dramatis decides. rbitr records and spawns. Beads/Linear remember. Conduit carries. n8n executes. RepoWeaver explains code.**

> Output of `/grill-me-with-agents` session 2026-05-13. Roster + topology + contracts for the Dramatis-led orchestration system. Symphony-inspired ("manage work, not agents"), built to avoid OpenAI quota dependency, with n8n as the automation lane, Hermes/rbitr as spawn substrate, Beads/Linear as the canonical work queue, Conduit as event transport, and RepoWeaver as the target code-intelligence engine.

**Status:** v1-tracer-bullet-active (spec ratified 2026-05-13; bridge live 2026-05-21)
**Last grilled:** 2026-05-13
**Supersedes:** ADR-2026-03-29 ("Claude Code is primary orchestrator") — *Dramatis is the decision layer per ADR-0014; rbitr v1 tracer-bullet remains the active runtime substrate.*

---

## 1. Goal & success criteria

- **Outcome produced:** Beads/Linear ticket → Dramatis scene → isolated worker run → PR + proof-of-work → merge. Single director loop, no per-task human supervision.
- **Done when:**
  1. **Single work-state pane** — Beads/Linear board + `rbitr ps` runtime trace + daily summary through active fleet comms
  2. **Dispatch is declarative** — Dramatis policy + n8n workflows + Linear labels carry routing; no hand-routing per task
  3. **Hermes-as-CC-lane preserves the 2026-05-11 beacon doc's anti-command-bus rule** — Hermes doesn't decide; it executes
  4. **CC subprocesses visible in `claude agents`** — no orphaned background sessions
  5. **Orchestration package is publishable to GitHub** — docker-compose.yml + `grill-me-with-agents` skill + Arbiter config = clonable bundle
  6. **No dispatch path requires OpenAI quota** — Dramatis actor policy can choose Claude Max, Ollama/Gemma, Kimi, Gemini/PT, or local workers when OpenAI is exhausted
- **Explicitly out of scope:**
  - Mid-task interactive Q&A with workers (Symphony pattern: write caveats, don't ask)
  - Cross-CC-session memory continuity (workers are isolated; no shared memory writes)
  - Replacing Claude Code as a worker (CC stays alive as the Hermes-deployment lane)

## 2. Roster

| Agent | Single responsibility | Why not folded into another agent |
|---|---|---|
| **Dramatis** | Fleet director: scenes, actors, cues, proof gates, and policy | Symphony pattern: orchestration judgment must be distinct from work state, event transport, automation runtime, and spawn substrate |
| **rbitr** | Runtime substrate: dispatch HTTP, event log, SQLite projection, CLI, spawn plumbing | Keeps shipped v1 value without making rbitr the conceptual arbiter |
| **n8n** (Docker, restart: unless-stopped) | Executable automations — webhook ingress, scheduled flows, side-effect workflows | Workflow logic doesn't belong inside Dramatis; n8n is the automation runtime |
| **Conduit** | Event transport for cues and scene transitions | Dramatis should route events, not become the bus |
| **RepoWeaver** | Code-intelligence engine for context and blast radius | Code graph truth should not live in the orchestrator |
| **Hermes (Wings)** | CC deployment lane + Discord/Matrix bidirectional surface | CC spawn has runtime/auth specifics that don't belong in n8n flows; preserves "Hermes Discord responsiveness" value |
| **Claude Code** (worker tier) | Complex coding tasks; spawned by Hermes in isolated worktree | Worker shape; demoted from orchestrator |
| **OpenCode + GPT-5.4** (worker) | Opportunistic worker for OpenAI-compatible tasks (currently quota-degraded) | Cost lane; separate process from Arbiter's OpenCode-Sonnet binding |
| **Codex (Bean/Blue)** (worker) | Focused refactors, repo edits | Distinct OpenAI runtime with its own toolchain |
| **OLIVIER_MBP (Zoe)** (worker) | Browser/Discord/WhatsApp side-effects via OpenClaw | Local OpenClaw is a distinct runtime; n8n calls it for non-coding work |
| **KimiClaw cloud pod + web portal** | Jack's standalone mobile/AFK lane — NOT in dispatch table | Preserves cloud OpenClaw capability + Kimi K2.5 web UX without bot-identity overhead |
| **PT (Neo)** | Dissent — pre-spawn (label-gated) + post-merge review | Cross-model (Gemini) review of Arbiter/worker calls; can't fold into same-model self-review |
| **pi.dev** (worker) | Embeddable subagent, Gemma4 carrier | Scoped work where full CC overhead is wasteful |
| **fleet-alerts** (Telegram + Discord bot) | One-way fleet→Jack alerts; replaces Mara (Discord) + Kopi (Telegram) identities | Identity rationalization; single bot identity for all fleet alerts |

## 3. Topology

- **Pattern:** orchestrator-with-workers (Symphony pattern — isolated runs per Linear ticket)
- **Concurrency:** parallel-fanout, capped at 5 concurrent workers; tickets queue beyond cap

```
Jack files Linear ticket  /  posts in #bots  /  schedule fires
                          │
                          ▼
              ┌──── n8n (bus + classifier) ────┐
              │   reads label, routes:           │
        ┌─────┼─────────┬──────────┬──────┬─────┘
        ▼     ▼         ▼          ▼      ▼
  Dramatis Hermes    Zoe       pi.dev   n8n flows
  (director)(CC lane)(browser/  (Gemma4   (workflow
        │    │       messaging) embedded) side-effects)
        │    │
        │    ▼
        │  Claude Code session in isolated worktree
        │  (spawned with --settings worker-settings.json)
        │       │ PR + proof-of-work
        │       ▼
        └────── Dramatis (collates proof; updates Beads/Linear via policy) ─────┐
                                                        │
   Per-ticket workers Arbiter spawns:                  │
     Codex | OC+GPT-5.4 | pi.dev | CC-via-Hermes ──────┘
                                                        ▼
                                                 PR → CI → Linear update

  PT (Neo) ─── inserts at n8n classification (label-gated, pre-spawn)
               + post-merge review for `needs-dissent` / `architectural` / `security`
  KimiClaw web portal ─── Jack's standalone mobile/AFK lane
  fleet-alerts bot ─── Telegram + Discord one-way fleet→Jack alerts
```

## 4. Context boundaries (read visibility)

| Agent | Sees | Hidden from it | Why hidden |
|---|---|---|---|
| Dramatis | Beads/Linear work records, RepoWeaver context, Conduit cues, rbitr traces, OBn brief | Raw secrets, direct workflow execution state | Director owns decisions, not every substrate |
| rbitr | Runtime traces, worker worktrees, dispatch envelopes, event projection | Canonical work status, code graph authority, n8n workflow state | Runtime substrate only |
| n8n | Worker state via rbitr/Dramatis HTTP; Linear webhook; Telegram/Matrix/fleet-alert tokens | Full vault, SOPS secrets beyond env-injection | Automation runtime should not own the substrate |
| Hermes | Full vault (read), worker worktrees (write), Discord/Matrix | Linear writes except through Dramatis/rbitr policy | Hermes is a worker spawn lane, not a status writer |
| CC worker | Scoped worktree only | Full vault outside worktree; Linear; OBn; OB1 | Isolation guarantee |
| OC+GPT-5.4 / Codex / pi.dev workers | Scoped worktree only | Same as CC worker | Symptomatic isolation |
| Zoe | Scoped local FS; Discord/WhatsApp/Telegram bridges | Linear; vault writes | OpenClaw runtime constraint |
| PT (dissent) | Read-only vault; Linear (read high-stakes); direct impact review; Discord post-verdict only | Vault writes; shell-with-FS-write | Dissent is read+opine, never modify |
| KimiClaw portal | Cloud-side artifacts only; cannot reach local files | Local vault, SOPS, Linear write | Cloud isolation is intentional; Jack moves text manually |
| fleet-alerts bot | Outbound message permissions on Telegram/Discord channels | All read surfaces | Send-only |

## 5. Handoff contracts

For each load-bearing edge in the topology:

### Linear → n8n (webhook)
- **Schema:** Linear's native issue webhook payload (title, description, label, project, assignee, attachments)
- **Validator:** n8n built-in webhook validation
- **On schema drift:** Linear-side change → n8n flow updates; fail fast and log

### n8n → Dramatis / rbitr / Hermes / Zoe / pi.dev (dispatch_envelope)
- **Schema:**
  ```yaml
  dispatch_envelope:
    linear_id: NG-1234
    routed_at: 2026-05-13T20:15:00Z
    routed_by: n8n
    target: dramatis | rbitr | hermes | zoe | pi.dev
    routing_method: label | classifier
    classifier_rationale: <text>   # only if routing_method=classifier
    worker_contract: <URL>
    high_stakes: bool
    needs_dissent: bool
  ```
- **Validator:** Target agent validates schema on receipt; rejects with `400 schema_mismatch` if invalid
- **On schema drift:** dispatch returns failure to n8n; n8n marks ticket `dispatch_failed`, escalates to fleet-alerts

### Dramatis → worker (task assignment, Symphony pattern)
- **Schema:** dispatch_envelope + worker-specific config (worker_type, model, max_tokens, max_wall_clock)
- **Validator:** worker harness validates on spawn
- **On schema drift:** worker exits with `bad_assignment`, Arbiter retries once or marks ticket `failed_dispatch`

### Worker → Arbiter (proof_of_work)
- **Schema:**
  ```yaml
  proof_of_work:
    dispatch_envelope_ref: NG-1234
    worker_id: cc-session-xyz | codex-session-abc | ...
    status: succeeded | failed | requires_review | quota_exhausted
    pr_url, branch, ci_status, test_results, walkthrough
    files_changed, caveats
    cost_actual: { tokens: N, dollars: $X.YZ }
  ```
- **Validator:** Dramatis validates on receipt; missing required fields trigger `requires_review`
- **On schema drift:** Dramatis marks ticket `pow_invalid`, retries worker once, then escalates

### Hermes → CC session (with secrets)
- **Schema:** Spawn-args (worktree path, task dispatch_envelope) + zero secrets in env
- **Validator:** CC session reads SOPS-encrypted secrets from vault at startup (self-fetch); no plaintext crosses Hermes boundary
- **On schema drift:** CC session fails fast with `secret_unavailable`; Hermes reports `cc_spawn_failed` to Arbiter

## 6. Shared state (mutable, persisted)

| Store | Schema | Writers | Conflict resolution | TTL / cleanup |
|---|---|---|---|---|
| **Vault git** (GitLab origin) | git objects; PR branches per worker | Workers (PR push), n8n flows (side-effects) | Standard git merge; PRs gated by CI + Arbiter merge | Branches deleted post-merge |
| **Worker worktrees** | git worktree, scoped per task | Owning worker only | N/A — single-writer | Deleted on PoW receipt by Arbiter |
| **Dramatis scene state** | Scene/actor/cue/proof state machine | Dramatis only | Single-writer policy; substrate projections rebuildable | Persisted; archived after merge |
| **rbitr runtime DB** | Dispatch/spawn/event projection | rbitr only | Rebuild from events.jsonl | Persisted as runtime trace |
| **Beads/Linear** | Native issue records, labels, comments, attached PRs | Dramatis policy writes, n8n webhook ingress, PT high-stakes comments | Work record is authoritative; projections must reconcile to it | Beads/Linear retention |
| **SOPS-encrypted secrets** | age-encrypted dotenv + YAML | Jack (rotation) | N/A — single-writer | Versioned in git |
| `~/.hermes/` | Hermes session/auth state | Hermes runtime | N/A | Hermes-managed |
| `~/.opencode/` | OpenCode state | OpenCode binary | N/A | OpenCode-managed |
| `~/.claude/projects/<repo>/` | CC session state | Spawned CC worker | N/A — per-session | CC-managed |
| **Discord #bots** | Message log | n8n, Hermes, fleet-alerts | Append-only; Discord retention | Discord retention |
| **Orchestration logs** (`claude/orchestration/`) | JSONL events, per-ticket traces | Arbiter | Append-only | Daily rotation |

## 7. Tool access (blast radius)

| Agent | Tools | Blast radius (worst case) |
|---|---|---|
| Dramatis | Beads/Linear, RepoWeaver, Conduit, OBn-read, rbitr/Hermes spawn primitive, HTTP write-status | Bad work-state writes (revertable); bad routing (retry-able); should not directly modify vault FS |
| rbitr | Runtime event append, SQLite projection, spawn endpoints, CLI | Bad runtime trace or failed worker spawn; should not own work-state truth |
| n8n | Linear webhook, Discord webhook, Telegram bot, HTTP-out for dispatch | Misroute task (recoverable by re-labeling); send wrong Discord message (cosmetic) |
| Hermes | CC-spawn primitive, Discord/Matrix r+w, shell | Spawn rogue CC session (caught by Arbiter watchdog 30min); post wrong Discord message |
| CC worker | scoped worktree (shell, edit, Read/Write); CC's worker-settings.json profile | Wreck a worktree (deleted on PoW); cannot reach Linear, OBn, OB1, or vault outside worktree |
| OC+GPT-5.4 / Codex / pi.dev workers | Codebase tools only in worktree | Same as CC worker; less attack surface |
| Zoe | openclaw-mcp, browser automation, Discord/WhatsApp/Telegram bridges | Browser action mistakes (visible side-effects); rate-limited per OpenClaw policy |
| PT | Linear read, direct source review, Discord post-verdict; `execute` primitive (shell-capable; constrain to read-only or sandbox) | If `execute` is sandboxed → none. If not → PT can write vault (open risk; resolve in branch 11 re-review) |
| KimiClaw portal | Cloud-side only; cannot reach local files | Bad cloud-side text output (Jack rejects manually) |
| fleet-alerts bot | Telegram + Discord send-only | Notification spam (rate-limited) |

## 8. Per-agent failure modes

| Agent | Failure | Detection | Recovery |
|---|---|---|---|
| Arbiter | Process crash | Docker `restart: unless-stopped` | Auto-restart; n8n notices via dispatch-ack timeout and pages Jack via fleet-alerts |
| Arbiter | Linear API rate limit | HTTP 429 | Exponential backoff with jitter; max 3 retries; then mark ticket `linear_throttled` |
| n8n | Workflow execution error | n8n built-in retry + error trigger | Retry per node config; escalate failed workflows to fleet-alerts |
| n8n | Webhook delivery failure (Linear) | Linear's own retry | Linear retries; no n8n action needed |
| Hermes | Runtime crash (known fragility per hermes-runtime-triage doc) | Hermes runtime restart policy | Restart; Arbiter retries pending CC spawns |
| Hermes | Auth token expiry | API 401 | SOPS-managed token rotation; user-intervention if rotation pipeline broken |
| CC worker | Heartbeat silence ≥30 min | Arbiter watchdog | Mark dead; retry once (low-stakes) or escalate (high-stakes) |
| CC worker | SOPS self-fetch fails | CC reports `secret_unavailable` at startup | Worker fails; Arbiter retries; if persistent, page Jack |
| OC+GPT-5.4 / Codex workers | OpenAI quota exhausted | API 429 / 400 quota error in PoW | Worker reports `quota_exhausted`; Arbiter re-dispatches via Hermes to CC fallback |
| Zoe | Discord rate-limit (per fleet-tipi-identities.md belief) | Rate-limit response | Pause Zoe lane; resume on backoff window |
| PT | Gemini quota / unreachable | PT verdict request times out | Per branch 9: hold ticket (no proceed without dissent verdict on high-stakes); page Jack after 1h |
| KimiClaw portal | Cloud pod down | Manual — Jack notices on next attempt | Manual restart; not on dispatch path so no immediate blast |
| fleet-alerts bot | Token revoked | Send fails | Page Jack via Hermes Discord fallback; rotate token |

## 9. Inter-agent disagreement & authority

- **Precedence rules** (highest authority first):
  1. **Jack** > all agents (explicit human override; always wins)
  2. **CI status** > worker self-claim (objective signal beats self-report)
  3. **n8n routing** > Arbiter / target agent re-routing (n8n owns the routing decision; targets don't re-route)
  4. **Linear label** > classifier inference (explicit > inferred routing)
  5. **Arbiter** > workers on Linear writes (workers don't write Linear directly)
  6. **PT dissent** on `needs-dissent` / `architectural` / `security` tickets → **advisory + mandatory hold**: Arbiter pauses, Jack decides `proceed` or `hold`. PT is not unilaterally binding but cannot be ignored on high-stakes work.
- **Tie-break:** HITL (Jack); time-bounded (PT verdict times out at 1h → escalate to Jack, not auto-proceed)

## 10. Human-in-the-loop

- **Triggers:**
  - PT dissent verdict on high-stakes ticket → mandatory hold pending Jack `proceed`/`hold`
  - Worker PoW reports `requires_review` (worker chose review-track over autonomous-track based on caveats)
  - Cascading failure (Dramatis/rbitr down, n8n notices) → page Jack via fleet-alerts
  - Per-day budget cap hit ($20/day fleet) → Dramatis halts new spawns, posts notice through active fleet comms, waits for Jack to extend or wait for daily reset
  - Per-ticket budget cap hit ($5/ticket) → ticket marked `failed_budget`, escalates
- **Minimum context shown to user:** Linear ticket ID + dispatch_envelope + current PoW snapshot + the specific gate that triggered HITL
- **Default action if user is absent:**
  - PT-dissent hold → wait indefinitely until Jack replies (no auto-proceed)
  - Budget caps → wait until next day's reset; no auto-extend
  - Cascading failure → no auto-recovery beyond runtime restart; tickets queue in n8n; resume when Dramatis/rbitr are back

## 11. Termination

- **Stop conditions:**
  - **Per-task:** PoW with `status: succeeded|failed|requires_review|quota_exhausted`; or 30-min heartbeat silence → watchdog kill
  - **Per-Linear-ticket:** PR merged + ticket closed; or Jack closes (`wontfix` / `duplicate`); or `failed` PoW + no retry
  - **Per-day:** $20 fleet budget exhausted → Dramatis stops new spawns; resumes at midnight local
  - **Dramatis/rbitr loop:** Dramatis policy remains the decision layer; rbitr runtime restarts per its service policy and only halts under budget caps or explicit stop
  - **Mara/Kopi identity retirement:** 4-week phased — week 1 parallel-post, week 2 cut-over, week 3 token revoke, week 4 audit
  - **Design re-review:** earlier of 100 tickets shipped through Arbiter, or 90 days from 2026-05-13
- **On stop:** Dramatis writes final summary to Beads/Linear, emits daily summary through active fleet comms, updates rbitr trace state, and flushes worker logs to `claude/orchestration/`

## 12. Observability

- **Logged:**
  - Container logs (`docker logs arbiter`, `docker logs n8n`) — real-time debug
  - Structured events (`claude/orchestration/arbiter/log-YYYY-MM-DD.jsonl`) — vault-persisted critical events
  - Per-ticket trace (`claude/orchestration/tickets/<linear_id>/trace.jsonl`) — forensic replay
  - Linear comment thread — human-readable per-ticket detail
  - Daily summary in #bots
- **Trace location:** `claude/orchestration/tickets/<linear_id>/trace.jsonl` is the canonical per-ticket forensic record
- **Live "what's running":** `arbiter ps` host CLI → Arbiter HTTP `:8765/status`
- **Replayable:** **partial.** Per-ticket trace can replay dispatch + spawn + PoW; cannot replay worker's internal LLM token-stream (not logged). Replay good enough for forensics, not full reproducibility.
- **Cost ledger:** existing `claude/scripts/sync_machine_ledger.py` extended to read Arbiter state DB; calibrate `cost_actual` against monthly OpenAI invoice (not estimated tokens × rate-card per `feedback_ledger_estimated_cost_is_larp`)

## 13. Cost & latency budget

| Agent | Model | Token budget / turn | Expected wall-clock |
|---|---|---|---|
| Arbiter | Sonnet 4.6 (Claude Max) primary / Gemma4 ≤9B fallback | ~5K tokens/decision | <2s cloud, ~5s local fallback |
| n8n | n/a (workflow nodes) | per-node | <500ms per dispatch hop |
| Hermes | Sonnet 4.6 / Opus 4.7 (Claude Max) | ~3K tokens/spawn | <5s to spawn CC |
| CC worker | Opus / Sonnet / Haiku (Claude Max) | per task, capped at $5/ticket | Variable, watchdog at 30 min |
| OC+GPT-5.4 worker | gpt-5.4 / gpt-5.4-mini (OpenAI metered, currently quota-exhausted) | per task, capped at $5/ticket | Variable |
| Codex worker | gpt-5.4 / gpt-5.4-mini (OpenAI metered) | per task, capped at $5/ticket | Variable |
| Zoe | Mistral Large (OpenClaw) | per task | Variable |
| PT | Gemini 2.5 Pro / Flash (Google AI Pro $20/mo) | ~10K tokens/review | <30s |
| KimiClaw portal | Kimi K2.5 Thinking (cloud OpenClaw) | Jack-driven | N/A |
| pi.dev | Gemma4 / OpenRouter / Ollama | per task | Variable |

- **Fleet daily budget:** $20/day total worker spend
- **Per-ticket cap:** $5
- **Parallel worker cap:** 5 concurrent
- **End-to-end latency** (ticket filed → worker active): ~8-40s acceptable
- **Under pressure, cut first:** OC+GPT-5.4 worker (cost-metered); fallback to CC via Hermes is automatic per branch 13 Risk 13.1

## Open risks

1. **Tonkotsu déjà vu** — Mitigated by Symphony's task-isolation pattern + better human-in-loop discipline + unique naming. Re-validate at branch-11 re-review (100 tickets or 90 days).
2. **Hermes runtime fragility** — known from `hermes-runtime-triage-2026-04-26.md`. Mitigated by limiting Hermes role (no routing decisions) and Docker-style restart watchdog.
3. **Claude Max contention** — Arbiter + Hermes + workers + interactive sessions share the plan. Accepted for v1; monitor at branch-11 cadence. Mitigation if it bites: shift Arbiter to Gemma4 primary, accept RAM pressure.
4. **Retired code-indexer availability hazard** — Read-only DB errors observed in this very grilling session from old hooks. Workers must handle gracefully by ignoring retired-indexer prompts and using direct source inspection plus focused tests.
5. **PT `execute` primitive write capability** — branch 7 flagged. Resolution deferred to branch-11 re-review or sandboxing of PT shell.
6. **OpenAI quota exhaustion** — LIVE today. Fallback to CC via Hermes designed; needs end-to-end test.
7. **Gemma4 RAM pressure as fallback** — if Claude Max degrades AND Gemma4 fallback activates concurrent with Hermes + interactive CC, OOM risk. Worth a stress test before production.
8. **Bidirectional #bots** — contradicts 2026-05-11 beacon doc; doc amendment queued.

## Diff vs previous design (implicit "Claude Code as primary orchestrator")

- **Added:**
  - Arbiter (OpenCode + Sonnet/Gemma4) — new orchestrator entity
  - n8n — new bus layer
  - Linear as canonical task source
  - dispatch_envelope + proof_of_work schemas
  - `arbiter ps` host CLI + Arbiter HTTP `:8765/status`
  - fleet-alerts unified bot identity (Telegram + Discord)
  - Worker-settings.json profile (minimal hooks for autonomous CC workers)
  - Symphony-pattern budget caps ($20/day, $5/ticket, 5 parallel)
  - Hermes → CC SOPS self-fetch protocol (zero secret crossing)
- **Removed:**
  - Claude Code as orchestrator (demoted to worker tier)
  - Hermes as routing decision-maker (demoted to CC-deployment lane only)
  - Mara (Discord) + Kopi (Telegram) bot identities (replaced by fleet-alerts)
  - Workers writing to OB1 / OBn / knowledge-graph / MEMORY.md (off the dispatch path)
  - Workers asking Jack mid-task (Symphony pattern: write caveats, don't ask)
  - File-based handoffs as primary coordination (still used for human sessions; not for autonomous workers)
- **Changed:**
  - Hermes belief amendment: "I am permitted to classify routing when Linear label is absent" — superseded by Resolution A; Hermes belief stays intact, classification moves to n8n
  - Linear ownership split: ingress = n8n webhook, writes = Arbiter
  - Discord #bots: status-only → status + commands (bidirectional)
  - KimiClaw cloud pod role: cloud-overflow worker → standalone Jack mobile/AFK lane (cloud pod + web portal preserved)
  - Memory systems (OB1 / OBn / KG / MEMORY): cross-CC-session continuity tools → human-driven-work-only tools (off orchestration path)

---

*Authored-by: claude-code (session bd83817c, grill-me-with-agents 2026-05-13)*

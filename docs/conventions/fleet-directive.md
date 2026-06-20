---
title: Fleet Directive — Durable Evidence
status: ratified
created: 2026-05-16
ratified_at: 2026-05-16T17:55:00Z
ratified_by: Jack Reis (human grain-gate)
audit_report: "~/Documents/Coordination/2026-05-16-fleet-directive-alignment-report.md"
supersedes:
  - "Variant A: short directive (informal)"
  - "Variant B: detailed directive (poisoned — archived with warning)"
  - "Variant C: Slack summary (informal)"
related:
  - "[[docs/conventions/agent-observer-principle]]"
  - "[[docs/architecture/fleet-architecture-guidelines]]"
  - "[[claude/coordination/agentic-os-operating-preferences]]"
  - "[[AGENT_DESIGN]]"
touch_history:
  - "2026-05-16T17:55Z Jack Reis (human grain-gate) — ratified via accept-split"
---

# Fleet Directive — Durable Evidence

> You are not alone in this codebase. Other agents and humans read these files
> in parallel, across machines, across days.

## Core rule

Done = artifact + path + verification + commit + push + caveats.

If the next observer cannot find it, the agent did not finish it.

## Required evidence

Every completion must include:

1. **Artifact** — what changed (file, commit, function, config key, rendered output).
2. **Path** — where it lives (absolute path, repo-relative path, or commit SHA).
3. **Verification** — the exact command or check performed and the observed result.
4. **Commit + push** — committed to git AND pushed to the remote. Not pushed = not durable.
5. **Caveats** — what was NOT done, what could still fail, what assumptions you made.

## Agent-specific compliance

- **Human-attended sessions** (Claude Code, Cursor, Gemini CLI, Codex): Write evidence to the repo/vault directly. Handoff files are acceptable for inter-session coordination.
- **rbitr autonomous workers**: Satisfy the evidence requirement via the `proof_of_work` schema (`pr_url`, `files_changed`, `caveats`, `test_results`). Handoff files are not required for isolated worker runs.
- **All agents:** Verification must come from running the thing, not from reading the diff. You cannot observe yourself and call it measurement.

## Governance Loop

When athenaeum-audit produces a triangulation report with **Divergent** or **High Risk** findings, the governance engine enforces human sign-off:

1. **Audit** → `athenaeum-audit` identifies divergent claims or high-risk divergences
2. **Escalate** → `athenaeum-arbiter-bridge` pushes a decision plan to Arbiter Zebu
3. **Human decides** → Jack answers via Telegram (zero LLM cost, structured audit trail)
4. **Verify** → `fleet-ratify --require-approval` checks for `arbiter_decision_id` on high-risk items
5. **Ratify** → Commit with both Durable Evidence and Human Approval in PoW

**Variant B is still poisoned.** This loop does NOT replace the fleet directive's evidence requirement — it augments it with a human approval gate for high-risk items only.

Failure to obtain human approval for a high-risk item blocks ratification. Low-risk and medium-risk items follow the standard fleet directive path.

### Components

| Component | Location | Role |
|-----------|----------|------|
| `athenaeum-arbiter-bridge` | `dancer/plugins/skill-enhancers/athenaeum/athenaeum-arbiter-bridge/` | Dancer skill: push divergent findings to decision queue |
| `arbiter_push` | `athenaeum-arbiter-bridge/scripts/push.py` | CLI: write decision plans to `~/.arbiter/queue/pending/` |
| `fleet_ratify.py` | `=notes/claude/scripts/fleet_ratify.py` | CLI: ratify PoW with optional `--require-approval` gate |
| `arbiter-zebu` | `=notes/claude/orchestration/rbitr/arbiter-zebu/` | Docker container: Telegram bot presenting decisions to humans |
| `/arbiter/callback` | `rbitr_shim.py` endpoint | Records human decisions in events.jsonl + SQLite |

## Final standard

Durable or it did not happen.

---

*Ratified 2026-05-16. Alignment audit: `~/Documents/Coordination/2026-05-16-fleet-directive-alignment-report.md`.*
*Governance loop added 2026-05-19.*

---
created: 2026-04-22
type: convention
status: active
owner: fleet
decay: enduring
obn: sync
last_touched_by: "claude-code (5e8ae6a0)"
touch_history:
  - "2026-04-23T04:17Z claude-code (d0eecb0d)"
  - "2026-05-05T01:38Z claude-code (5e8ae6a0)"
---

# Agent Custody & Provenance Convention

Every artifact produced by an agent carries a readable chain of custody.
Five patterns, one SoT (this file).

## 1. Git Commit Trailers

Every commit authored — even partially — by an AI agent MUST carry both
trailers in the commit body:

    Authored-by: <agent-name> (session:<short-session-id>)
    Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

- `<agent-name>`: one of `claude-code`, `hermes`, `zolivier`, `kimiclaw`,
  `kimi-code-cli`, `pi`, `pt`, `codex`, etc. Must match the runtime agent names in
  [`docs/architecture/fleet-architecture-guidelines.md`](../architecture/fleet-architecture-guidelines.md)
  §2 (canonical SoT) and the `autonomous-ai-agents:fleet-identity` skill.
  Note: `pt` replaced `gemini-cli` as the runtime name on 2026-04-22
  (PT↔Neo split); accept `gemini-cli` as a backward-compat alias on
  pre-split artifacts. `kimi-code-cli` is the direct CLI tool (distinct from
  `kimiclaw`, the fleet runtime identity for KIMI_MBP OpenClaw activity).
- `<short-session-id>`: first 8 chars of the session UUID
  (from `.claude/memories/.session-labeled` for Claude Code; equivalent for
  other runtimes).
- `Co-Authored-By:` uses the canonical model-version line. Required for
  attribution visibility in GitHub/GitLab UI.

**Rationale:** `Authored-by` carries *who ran* the session. `Co-Authored-By`
carries *which model answered*. Both are needed; neither is sufficient alone.

## 2. Snapshot Retention Policy

- Markdown is the Source of Truth. It is permanent and never pruned on
  format grounds.
- PDFs (and other rendered projections — HTML, PNG, DOCX) are ephemeral.
  They MAY be deleted at 30 days without asking.
- `claude/scripts/prune_old_pdfs.sh` enforces the 30-day rule via launchd
  daily at 03:00 local.
- Infra-class docs (internal handoffs, session logs, skill READMEs)
  render to PDF on demand only; markdown-in-vault is sufficient.
- Human-deliverable outputs (owner packets, clinical summaries, tax filings)
  MUST produce PDF alongside markdown via `vault-to-pdf` skill.

**Complements:** `feedback_snapshot_audit_policy` (memory), `feedback_obn_is_index_not_ssot` (memory).

## 3. Agent-to-Agent Handoff Artifacts

Every cross-session handoff lands at:

    claude/mcp-coordination/state/session-handoffs/session-<slug>-<YYYYMMDD>.md

Frontmatter MUST include (writer provenance):

    from_agent: <agent-name>
    from_session: <short-session-id>

Optional fields, validated only when present:

    to_agent: <agent-name or "any">         # destination; omit for bulletin-board posts
    to_session: <short-session-id>          # destination session; omit when unaddressed
    handoff_type: <free-form string>        # task, context, decision, blocker, diagnostic, status…

A handoff without `from_agent` + `from_session` is invalid — the validator
(`claude/scripts/validate_handoff_custody.py`) blocks writes via PreToolUse hook.

**Loosened 2026-05-04.** Destination fields and `handoff_type` were previously
required + enum-constrained. Most handoffs are bulletin-board posts (writer
stamps it, whoever needs it picks it up), not point-to-point packets — forcing
destination fields invented data, and the closed `handoff_type` enum rejected
legitimate categories. Writer provenance is the durable invariant per the
Observer Principle. Destination/type stay welcome when known but are no longer
taxed when absent.

### Suggested handoff_type values

When you do supply `handoff_type`, prefer one of these — they categorize the
*payload* and keep ad-hoc grep useful across the corpus. Free-form is allowed
but adds a category, so use a new value only when none of these fit:

- **`context`** — state-after-the-fact (summaries, deltas, merged findings).
  Default for parallel-session closeouts.
- **`task`** — surfaces new actionable items needing downstream pickup.
- **`decision`** — work resulted in a decision that changes subsequent execution.
- **`blocker`** — work uncovered something that blocks progress.
- **`diagnostic`** — investigation/triage write-up; problem characterized,
  resolution path documented, no new action required.

Rationale: `handoff_type` categorizes the *payload*, not the session topology.
Mechanism-based types (`parallel-closeout`, `scheduled-handoff`) blur the
schema; describe what the file *is*, not how it was produced.

## 4. WORK-LEDGER Updates

Any update to a ledger-class file MUST prefix each new line/row with the
provenance stamp:

    [agent:claude-code session:08a57670 2026-04-22] <update text>

Ledger-class files (non-exhaustive):

- `INFRASTRUCTURE-TASKS.md`
- `claude/coordination/ai-usage-ledger.md`
- `claude/coordination/agent-achievement-snapshots.md`
- Any `efforts/current/*/INDEX.md` timeline row
- Any `claude/tasks/closed/*.md` completion note

Rationale: when a reviewer three months from now asks "which agent claimed
this?", the answer is on the line itself — no git archaeology required.

## 5. File-Level Touch History (`touch_history` frontmatter)

Every vault markdown file with YAML frontmatter carries BOTH:

    last_touched_by: "<agent-name> (<short-session-id>)"
    touch_history:
      - "<UTC ISO-8601 minute> <agent-name> (<short-session-id>)"
      - "<UTC ISO-8601 minute> <agent-name> (<short-session-id>)"

- `last_touched_by` is the convenience scalar — cheap for dashboards and
  quick-scan grep queries.
- `touch_history` is append-only. Each distinct custody event adds one line.
  Consecutive edits by the same `(agent, session)` pair do NOT append a new
  line (dedupe keeps history = custody events, not per-edit spam).
- Enforcement: `.claude/hooks/agent-id-stamp.py` writes both fields. The
  script is runtime-agnostic with three invocation modes (priority order):
    1. **CLI args** (any runtime):
       `python3 agent-id-stamp.py --file <path> --agent <name> --session <id>`
    2. **JSON stdin** (Claude Code PostToolUse): payload with
       `tool_input.file_path` + `session_id`; agent defaults to `claude-code`.
    3. **Env vars** (any runtime): `FLEET_STAMP_FILE`, `FLEET_AGENT_NAME`,
       `FLEET_SESSION_ID`. Useful when a runtime sets identity once per process.
  Agent names validated against the same allowlist as the handoff validator
  (`claude-code`, `hermes`, `zolivier`, `kimiclaw`, `kimi-code-cli`, `pi`, `pt`, `codex`, plus
  `gemini-cli` backward-compat alias). Unknown names silently coerce to
  `claude-code` rather than hard-fail.
- Scope excludes high-churn auto-generated paths: `calendar/day/**`,
  `logs/**`, `.claude/**`. Everything else in the vault is in scope.
- Backfill policy: when upgrading a file that only has `last_touched_by`,
  prepend known prior sessions as separate entries. Use real timestamps
  where available (git log, file mtime); don't fabricate precision.

**Rationale:** the scalar answers "who touched this last?"; the history
answers "who has ever touched this?". Both questions come up — git log
covers the second, but only for committed changes, only by grepping across
commits, and only if the file was tracked at each touch. The in-file
history is authoritative for un-tracked vault files and cheap for everyone
else.

## References
- **Master architecture:** [`docs/architecture/fleet-architecture-guidelines.md`](../architecture/fleet-architecture-guidelines.md) — living spec v1.2.0+. §2 defines the canonical runtime↔surface mapping consumed by the validator whitelist; §5 defines the session lifecycle this custody metadata supports.
- **Fleet coordination contract:** [`~/Documents/tipi/tipi/contract/consciousness-interface.json`](~/Documents/tipi/tipi/contract/consciousness-interface.json) — ratified 2026-04-22 as the IDE-agnostic fleet coordination standard. Custody artifacts feed the `session_lock_state` and `handoff_freshness` fields.
- Git trailers: https://git-scm.com/docs/git-interpret-trailers
- Fleet identity skill: `autonomous-ai-agents:fleet-identity`
- Handoff template: `claude/mcp-coordination/state/session-handoffs/TEMPLATE.md`
- Retention memory: `feedback_snapshot_audit_policy`
- SoT memory: `feedback_obn_is_index_not_ssot`

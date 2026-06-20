---
title: Known Failure Modes — Canonical Catalog
status: ratified
decay: enduring
created: 2026-06-04
ratified_by: Hermes (multi-model audit, 2026-06-04)
related:
  - "[[docs/reviews/2026-06-04-fleet-coordination-framework-audit]]"
  - "[[claude/memory/HERMES-MEMORY]]"
supersedes: "Embedded failure-mode entries in HERMES-MEMORY.md (still authoritative, but now cross-linked)"
---

# Known Failure Modes — Canonical Catalog

> **This catalog is scar tissue.** Every entry below was learned the hard way.
> Read it at session start. Do not re-discover these by hitting them.

## How to use

1. At session start, scan the **Table of Contents** below.
2. Before any non-trivial operation, ask: is the relevant entry a trap I'm about to walk into?
3. When you hit a NEW failure mode, append a YAML entry to this file (and the corresponding `claude/memory/HERMES-MEMORY.md` patch) using the schema in `scripts/lib/known_failure_modes.py:Catalog`.

## Table of Contents

| ID | Title | First seen |
|----|-------|------------|
| `km-001` | macOS `com.apple.provenance` xattr is unremovable from user space | 2026-05-26 |
| `km-002` | `Bootstrap failed: 5: Input/output error` is usually a bootout→bootstrap race | 2026-05-26 |
| `km-003` | launchd caches plist arguments in memory | 2026-05-29 |
| `km-004` | Conditional `KeepAlive` (Crashed:1, SuccessfulExit:0) leaves daemon down | 2026-05-26 |
| `km-005` | Bifrost config split: `config.db` is truth, `config.json` is stale | 2026-06-01 |
| `km-006` | Hermes main gateway shares Wings Discord token — connection conflict risk | 2026-05-26 |
| `km-007` | Agent-to-agent reachability in Discord is broken (JACK_USER_ID trigger) | 2026-05-29 |
| `km-008` | `os.walk('.')` without worktree exclusion contaminates 23 files × 12 worktrees | 2026-05-26 |
| `km-009` | Symlinks can fake cross-lane content consensus in audits | 2026-05-26 |
| `km-010` | `${VAR:-}` in wrapper scripts gets corrupted by `write_file`/heredoc | 2026-06-01 |
| `km-011` | Discord `gateway.py klaude` slot was a true duplicate (same Keychain token) | 2026-05-29 |
| `km-012` | Bifrost raw `openclaw mcp serve` fails without `OPENCLAW_GATEWAY_TOKEN` | 2026-06-01 |
| `km-013` | Hindsight retain needs `async: true` | 2026-06-03 |
| `km-014` | Stale-evidence guardrail: ~30min handoff-read window for parallel sessions | 2026-05-22 |

## Schema

```yaml
- id: km-NNN
  title: <short>
  symptom: <observable failure signature>
  fix: <actionable remediation>
  first_seen: YYYY-MM-DD
  related_artifacts:
    - <path or command>
  source_session: <optional session id>
```

## Entries

(Each entry below is the full long-form of one row in the ToC above.
Body content is sourced from `claude/memory/HERMES-MEMORY.md` and may be
extended. Do not invent entries — append only after a real failure.)

### km-001 — macOS `com.apple.provenance` xattr

- **Symptom:** `xattr -d com.apple.provenance <path>` returns success but the
  attribute re-appears in subsequent listings.
- **Fix:** Don't bother stripping. The kernel re-stamps it. Look elsewhere
  for the root cause. Original "feedback_provenance_xattr_blocks_exec" memory
  may still apply to direct shell exec, does NOT apply to launchctl bootstrap.
- **Related:** `claude/memory/HERMES-MEMORY.md` (2026-05-26 matrix-mcp-diagnosis)
- first_seen: 2026-05-26

### km-002 — `Bootstrap failed: 5: Input/output error` is a race, not xattr

- **Symptom:** launchd bootstrap fails with "Input/output error". Many guides
  recommend `xattr -d` to fix — this is a placebo.
- **Fix:** `launchctl bootout <target> && sleep 2 && launchctl bootstrap <target>`.
  The ~2s settling delay is the actual fix.
- first_seen: 2026-05-26

### km-003 — launchd caches plist arguments in memory

- **Symptom:** After correcting an on-disk plist, the daemon still launches
  with the old arguments (e.g., Kimi Code `--home` loop).
- **Fix:** Explicit `launchctl bootout` followed by rename-and-rebootstrap,
  not just `kickstart -k`.
- first_seen: 2026-05-29

### km-004 — Conditional `KeepAlive` is fragile

- **Symptom:** Daemon stays down indefinitely after a clean exit (reboot,
  manual stop, SIGTERM).
- **Fix:** Default to unconditional `<true/>` in `KeepAlive` unless there's a
  specific reason to gate on exit code.
- first_seen: 2026-05-26

### km-005 — Bifrost config split (db vs json)

- **Symptom:** `config.json` shows `tools: 0` and `clients: []`; logs show
  healthy connected clients.
- **Fix:** Trust `~/.bifrost/config.db` (runtime truth). Use the export
  script `scripts/bifrost_config_export.sh` (Task 5) to dump a fresh
  JSON when needed. Never edit `config.json` while Bifrost is running.
- first_seen: 2026-06-01

### km-006 — Hermes + Wings share Discord token

- **Symptom:** Intermittent 401s, dropped events, or "websocket closed" in
  the main Hermes gateway.
- **Fix:** Monitor. If a regression appears, restart Wings first; if it
  persists, move Hermes gateway to its own token.
- first_seen: 2026-05-26

### km-007 — Agent-to-agent Discord reachability is broken

- **Symptom:** Hermes-relayed `@mentions` to other fleet bots produce no
  reply, but direct pings from Jack do.
- **Fix:** Captured as plan task (design-gated to avoid reply loops).
  Workaround: have Jack relay the message.
- first_seen: 2026-05-29

### km-008 — `os.walk('.')` contamination across worktrees

- **Symptom:** A vault-edit script accidentally edits 23 files per worktree
  × 12 worktrees = 253 contaminated files.
- **Fix:** Use `scripts/lib/fleetignore.walk_vault()` (Task 1) which
  consumes `.fleetignore`. The canonical exclude list lives there.
- first_seen: 2026-05-26

### km-009 — Symlinks fake cross-lane consensus

- **Symptom:** Two audit agents independently flag a folder as duplicate
  or orphan based on content hash; the consensus collapses once you
  `find -type f` and discover the folder is 97 symlinks.
- **Fix:** Use `scripts/lib/audit_safe.compare_lanes()` (Task 2) which
  rejects any symlink it encounters. `LaneComparison.consensus` is
  False if any symlink was touched.
- first_seen: 2026-05-26

### km-010 — `${VAR:-}` corruption via write_file/heredoc

- **Symptom:** Wrapper scripts get their variable-expansion syntax mangled
  when generated through `write_file` or shell heredocs (the heredoc
  redaction layer strips `${...}` placeholders).
- **Fix:** Use the canonical wrapper template (`templates/wrapper.sh.template`,
  to be added) + `cp template && sed -i` workflow. Never inline-generate.
- first_seen: 2026-06-01

### km-011 — `gateway.py klaude` was a true duplicate of @Zoe

- **Symptom:** Two Discord bots with the same identity, fighting for events.
- **Fix:** Audit each gateway.py slot against the Keychain token store.
  A token collision = duplicate, not a proxy. True duplicates must be
  DISABLED, not configured alongside.
- first_seen: 2026-05-29

### km-012 — `openclaw mcp serve` fails without env var

- **Symptom:** `openclaw mcp serve` exits 1 with box-drawing warnings to
  stdout; Bifrost JSON-RPC parser breaks; retries until deadline.
- **Fix:** Use `~/.openclaw/bin/gateway-wrapper.sh mcp serve` which
  sources sops-decrypted secrets before exec.
- first_seen: 2026-06-01

### km-013 — Hindsight retain needs `async: true`

- **Symptom:** Hindsight `retain` call hangs or 500s.
- **Fix:** Pass `async: true` and poll for completion.
- first_seen: 2026-06-03

### km-014 — Stale-evidence guardrail (~30min window)

- **Symptom:** Two parallel sessions within ~30min both touch the same
  Linear hierarchy; the second one proposes a triage change that
  contradicts the first one's verified work.
- **Fix:** `scripts/handoff_check.py` (Task 4) mechanically enforces
  "read newest handoff before posting triage" within the 30min window.
- first_seen: 2026-05-22

## Adding new entries

Append a YAML block under the Entries section. The schema is enforced by
`scripts/lib/known_failure_modes.py:Catalog`. Run the linter:

```
python3 -m scripts.lib.known_failure_modes --lint claude/memory/HERMES-MEMORY.md
```

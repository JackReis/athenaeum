---
decay: evolving
created: 2026-05-21
updated: 2026-05-21
last_touched_by: "opencode-glm"
tags:
  - convention
  - backup
  - sop
  - agentic-os
  - coordination
  - durable-evidence
status: proposed
obn: sync
---

# Cross-Repo Backup SOP — Agentic OS Ecosystem

> Ratification required before adoption. This document proposes a standardized
> backup and durability protocol across all repos in the 18-repo ecosystem.

## Problem

The fleet directive requires durable evidence (artifact + path + verification +
commit + push + caveats), but no standardized backup mechanism exists for:

1. **Markdown coordination files** (plans, conventions, dashboards) that live
   only in `=notes` but are referenced across repos
2. **Repo-specific config** that isn't mirrored anywhere when a repo goes stale
3. **Legacy code-indexer state** — retired indexing surfaces may still appear
   in old handoffs or launchd inventory, but they are no longer a backup layer
4. **Disaster recovery** — `=notes` exceeds 2GB (can't push to GitHub), and cold
   bundles only run weekly

## Proposed Architecture

### Layer 1: Vault Mirror (Daily)

Key markdown files from `=notes/docs/` and `=notes/atlas/` are copied to
secondary repos that ARE on GitHub:

| Source (`=notes`) | Destination | Repo | Trigger |
|--------------------|-------------|------|---------|
| `docs/conventions/*` | `docs/conventions/` | `athenaeum` | Git hook + cron |
| `docs/architecture/rbitr-design.md` | `docs/rbitr-design.md` | `cortex` | Git hook + cron |
| `docs/plans/*` | `plans/` | `athenaeum` | Git hook + cron |
| `atlas/dashboards/*` | `dashboards/` | `orchestration-dashboard` | On change |
| `AGENT_DESIGN.md` | `AGENT_DESIGN.md` | `cortex` + `athenaeum` | On change |

**Mechanism:** A `vault-mirror.sh` script runs via launchd daily at 04:00 CT,
copies changed files using `rsync --checksum`, commits only if diffs exist,
and pushes to GitHub. The script lives at
`claude/scripts/vault-mirror-backup.sh`.

### Layer 2: Git Bundle (Weekly — Existing)

Already operational: `com.jackreis.vault.weekly-bundle` launchd agent runs
Sundays at 03:00, creating `~/Backups/vault-bundles/`. Retention: 2 newest.

**Enhancement:** Extend bundles to include the 5 critical infrastructure repos
(cortex, athenaeum, matrix-mcp-shim-express, telegram-agent-gateway,
orchestration-dashboard) in the same weekly bundle run.

### Layer 3: Google Drive Sync (On-Demand — Existing)

The `vault-to-gdrive-set` skill and `gdrive-sync` skill already handle
Google Drive triads. Enhancement:

- Add a `claude/scripts/gdrive-backup-critical.sh` that uploads the
  coordination files listed in Layer 1 to
  `Google Drive/vault-backup/coordination/` using `rclone`.
- Runs weekly, triggered by the vault bundle launchd.

### Layer 4: Code Navigation (Retired Indexer)

The old code-indexer reindex layer is retired for this vault. Do not add
session-start checks, hooks, launchd jobs, or automatic reindex commands for it.
Use direct source inspection, `rg`, caller/callee review, and focused tests as
the active code-navigation contract.

### Layer 5: Disaster Recovery Test (Monthly)

First Sunday of each month, a `vault-restore-test.sh` script:

1. Picks the most recent vault bundle
2. Verifies it can extract to a temp directory
3. Checks file count matches expectation (572K+ files)
4. Reports pass/fail to `atlas/dashboards/backup-health.md`
5. Sends Telegram notification via fleet-alerts

## Implementation Tasks

| Task | Issue | Priority | Est. |
|------|-------|----------|------|
| Write `vault-mirror-backup.sh` | JAC-NEW | High | 1h |
| Write `vault-restore-test.sh` | JAC-NEW | Medium | 30m |
| Write retired-indexer reindex script | Deprecated | N/A | Do not implement |
| Extend weekly bundle to include 5 infra repos | JAC-NEW | Medium | 20m |
| Register `com.jackreis.vault-mirror` launchd | JAC-NEW | High | 15m |
| Register retired-indexer launchd job | Deprecated | N/A | Do not implement |
| Add gdrive-backup-critical.sh + rclone config | JAC-NEW | Low | 30m |
| Write `backup-health.md` dashboard | JAC-NEW | Low | 20m |
| Update AGENTS.md with backup SOP reference | JAC-NEW | Low | 10m |

## Convention Reference

- Fleet Directive: [[docs/conventions/fleet-directive]]
- Artifact-Bound Workflows: [[docs/conventions/artifact-bound-workflow-recipes]]
- Agent Custody: [[docs/conventions/agent-custody-provenance]]
- Decay Tier: [[docs/conventions/decay-tier-convention]]

## Verification

- [ ] `vault-mirror-backup.sh` produces dry-run output matching expected file list
- [ ] Weekly bundle includes `cortex`, `athenaeum`, `matrix-mcp-shim-express`,
      `telegram-agent-gateway`, `orchestration-dashboard`
- [ ] Monthly restore test passes file count check
- [ ] No retired code-indexer reindex job is required for backup success
- [ ] Google Drive `vault-backup/coordination/` reflects latest Layer 1 files

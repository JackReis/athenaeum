---
title: Decay Tier Convention
created: 2026-04-25
updated: 2026-04-25
decay: enduring
type: convention
author: Hermes
tags: [fleet, conventions, data-lifecycle]
last_touched_by: "claude-code (859085b3)"
touch_history:
  - "2026-04-26T15:06Z claude-code (3d148183)"
  - "2026-05-10T23:29Z claude-code (859085b3)"
---

# Decay Tier Convention

Long-lived artifacts created by or for the fleet (evolving + enduring tiers) MUST include a `decay:` field in YAML frontmatter. Ephemeral artifacts (session locks, scratchpads, untracked working files) are exempt — their lifetime is shorter than the cost of stamping them.

## Tiers

| Tier | Value | TTL | Layer | Examples | Commit? |
|------|-------|-----|-------|----------|---------|
| Ephemeral | `decay: ephemeral` | Session + 24h | Body | Presence JSON, temp logs, locks, working diffs | No |
| Evolving | `decay: evolving` | 90d review | Mind | Handoffs, wiki pages, plans, coordination notes | Yes |
| Enduring | `decay: enduring` | Permanent | Spirit | SOUL.md, fleet rules, ADRs, architecture docs | Yes |

## Frontmatter template

```yaml
---
title: Your Title
created: 2026-04-25
updated: 2026-04-25
decay: evolving   # ephemeral | evolving | enduring
status: active    # active | resolved | completed | archived
# For evolving tier when superseded:
# superseded_by: [[new-page]]
# archived_date: 2026-04-25
---
```

## Rules

1. **Tag at creation.** Never leave a fleet artifact untagged.
2. **Ephemeral = not commit-worthy.** If it is ephemeral, do not `git add` it.
3. **Evolving = versioned.** When superseding an evolving doc, write a new one and link backwards with `supersedes:` and forwards with `superseded_by:`.
4. **Enduring = append-only.** Update in place with `updated:` frontmatter. Never delete.
5. **Retroactive tagging is low priority.** Only tag existing files when you touch them. No bulk migration.

## Automation

- `~/.hermes/cubby/scripts/cleanup-ephemeral.sh` runs daily at 3am (cron: fleet-cleanup)
- `~/.hermes/cubby/scripts/archive-handoffs.sh` runs monthly on the 1st (via heartbeat)
- Heartbeat decay audit logs counts to `~/.hermes/logs/heartbeat.log`
- Dashboard Decay Health widget at `localhost:3020`

## See also

- [[docs/architecture/three-layer-consciousness#Decay Tier Mapping]] — how decay tiers map onto Body/Mind/Spirit layers
- [[docs/architecture/fleet-architecture-guidelines]] — fleet-wide architectural posture

## Reference

- Proposal: `~/.hermes/plans/proposal-decay-tiers-fleet-architecture-2026-04-25.md`
- Fleet rules: `~/.hermes/cubby/reference/fleet-rules.md`
- Fleet awareness: `~/.hermes/cubby/reference/fleet-awareness.md`

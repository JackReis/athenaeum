---
lyt: 000
created: 2026-04-12
doc-type: convention
status: canonical
tags:
  - convention
  - session-management
obn: sync
last_touched_by: "claude-code (39dcc65a)"
touch_history:
  - "2026-05-03T21:22Z claude-code (39dcc65a)"
---

# Session Coding — Slug-as-Identifier Convention

## Rationale

Between 2026-04-08 and 2026-04-12, daily note session headers drifted across four different formats in five days (`Session — <topic>`, `Session — <topic> (Role: X)`, `Session <uuid8> — <topic>`, bare `Session <topic>`). MEMORY.md still documented a `Session 57-D` sequential-number scheme that no real entry has followed since March 2026 — no counter was ever maintained, and parallel sessions can't coordinate one without a new lock. The only part of the session coding surface that has stayed consistent in practice is the handoff filename: `session-<role>-<slug>-<YYYY-MM-DD>.md`. This convention promotes that slug to a first-class identifier.

## Format spec

```
**Session <slug> — <Topic description> (<role>)**
- bullet 1
- bullet 2
- ...
- Session log: [[logs/sessions/YYYY-MM/session-<role>-<slug>-YYYYMMDD|session-<role>-<slug>-YYYYMMDD]]
- Handoff: [[claude/mcp-coordination/state/session-handoffs/session-<role>-<slug>-YYYY-MM-DD|session-<role>-<slug>-YYYY-MM-DD]]
```

## Rules

- **Slug** is 2–4 kebab-case words, ≤40 chars, derived from the primary topic. If a handoff file exists with a slug, reuse it verbatim. Examples: `hook-path-validator`, `edd-ui-filing-prep`, `dashboard-refresh`, `openclaw-fleet-revival`.
- **Role** is one or more of `A B C D E F G H` concatenated with no separator: `G`, `GH`, `DEH`. No parenthetical labels, no "role" suffix. Keep the A-H letter semantics from MEMORY.md.
- **Continuations across days** (carryover sessions) reuse the same slug on each day's daily note entry. No lowercase suffix. The date wikilink disambiguates.
- **Same-day collisions** (two sessions pick the same slug on the same day with the same role) append `-b`, `-c`, ... — same rule already in the session-lifecycle CHECKPOINT spec for filename collisions.
- **Filenames stay the same** — the handoff convention `session-<role>-<slug>-<YYYY-MM-DD>.md` and the session-log convention `session-<role>-<slug>-<YYYYMMDD>.md` are unchanged; they were already correct.
- **Session log filename uses compact `YYYYMMDD`** per the session-lifecycle Init spec. Handoff filename uses dashed `YYYY-MM-DD` per observed convention. Do not conflate them.
- **Retired:** `Session 57-D` sequential numbering, `Session <uuid-prefix>` UUID prefix, bare `Session — <topic>`. All three fail the lint.

## Role tag table

| Code | Role | Use When Session Primarily... |
|------|------|-------------------------------|
| A | Coordinator | Triages, plans, audits, refreshes dashboards |
| B | Repository | Manages git repos, PRs, code changes |
| C | Analytics | Builds/refreshes dashboards, analyzes data |
| D | Vault | Organizes Obsidian notes, templates, structure |
| E | Job/Health | Works on job search, medical, financial, recovery |
| F | Humanity | Creative expression, family, personal reflection |
| G | Systems | Claude Code infrastructure, MCP, automation |
| H | Superpowers | Builds skills, plugins, agent tooling |

## Examples

**Single-role:**
```
**Session hook-path-validator — Hook Path Validator + Session-Log Repair (G)**
- Built hook_path_validator.py + tests
- Repaired 14 broken wikilinks in logs/sessions/2026-04/
- Session log: [[logs/sessions/2026-04/session-G-hook-path-validator-20260412|session-G-hook-path-validator-20260412]]
- Handoff: [[claude/mcp-coordination/state/session-handoffs/session-G-hook-path-validator-2026-04-12|session-G-hook-path-validator-2026-04-12]]
```

**Multi-role:**
```
**Session tag-architecture-implementation — TAG Architecture + Implementation (GH)**
- Designed Telegram Agent Gateway bridge
- Shipped plugin-dev skill for gateway tooling
```

**Continuation across days:**
```
# In 20260411.md:
**Session scheduled-runner-discord-dm — Scheduled-task runner hardening + Discord DM redundancy (G)**
- Began launchd plist rework

# In 20260412.md (same slug, later date disambiguates):
**Session scheduled-runner-discord-dm — Carryover: session_id stamping fix (G, carryover from 04-11)**
- Finished maintenance-window catch
```

## Retired conventions

- `Session 57-D` sequential N numbering (counter never maintained)
- `Session <uuid-prefix>` (opaque, not semantic)
- Bare `Session — <topic>` (no stable identifier)

## Links

- Session lifecycle skill: `/Users/jack.reis/Documents/=notes/.claude/skills/session-lifecycle/SKILL.md`
- Daily-note-evals lint: `/Users/jack.reis/Documents/=notes/.claude/skills/daily-note-evals/SKILL.md`
- Role tags (older convention, now subsumed): `docs/conventions/session-role-tags.md`
- **Multi-day daily-note pattern:** [`docs/conventions/multi-day-session-daily-notes.md`](multi-day-session-daily-notes.md) — per-day entry, scoped commit list, cross-day breadcrumbs. Required reading for sessions spanning multiple calendar dates.

---
created: 2026-02-27
doc-type: convention
status: active
tags:
  - convention
  - classification
  - lyt
obn: sync
---

# LYT Classification — Adapted for =notes Vault

Based on the [LYT Classification System](✱ Library.md) (Cutter/Dewey-inspired, via Nick Milo).
Adapted Feb 2026 for tactical vault use during Oklahoma transition period.

## How to Apply

### Frontmatter field
```yaml
lyt: 500        # single classification
lyt: [500, 600] # dual classification (2 max)
```

### Obsidian tag (for search)
```yaml
tags:
  - lyt/500
  - lyt/600
```

### When to classify
- Apply to notes you create or significantly edit
- Retroactive batch tagging for high-traffic directories
- Skip ephemeral/stub notes — not everything needs a number

## The Adapted Categories

| LYT | Label | What Goes Here | Vault Directories |
|-----|-------|----------------|-------------------|
| 000 | Meta & Ops | Dashboards, coordination, daily notes, inbox, session handoffs | `calendar/day/`, `atlas/dashboards/`, `inbox/`, `claude/` |
| 100 | Personal & Family | Habits, self-care, family life, Robin, household, Katherine's projects | `atlas/personal/`, `efforts/current/personal/` |
| 200 | Mind & Meaning | Counseling, reflection, PERMA-V, growth, philosophy | `atlas/personal/` (counseling homework), `atlas/health/melissa-*` |
| 300 | People & Relationships | Networking, professional contacts, community | `atlas/people/`, `efforts/current/job-search/` (networking) |
| 400 | Expression & Communication | Writing, design portfolio, presentations, resume | `efforts/current/portfolio/`, job application materials |
| 500 | Health & Body | Rib recovery, PT, supplements, CPAP, medical records, providers | `atlas/health/`, `atlas/synthesis/` (recovery science) |
| 600 | Technology & Systems | Claude Code, MCP, skills, plugins, automation, AI tools | `.claude/skills/`, `claude/`, `docs/plans/` (infra) |
| 700 | Creative & Leisure | Music (Wenger), hobbies, media, play, inspiration | `atlas/2go2notes-inspo/`, Wenger notes |
| 800 | Learning & Reading | Books, articles, research synthesis, deep dives | `atlas/synthesis/` (non-health), `atlas/research/` |
| 900 | Places & Transitions | Oklahoma move, housing, geography, life timeline, travel | `efforts/current/move-to-oklahoma/`, `efforts/current/transition/` |

## Relationship to Other Tag Systems

| System | Describes | Example |
|--------|-----------|---------|
| `domain/` | Life area (5 values) | `domain/health` |
| `role/` | Claude session role (A-H) | `role/E` |
| `lyt/` | Knowledge classification (000-900) | `lyt/500` |
| `type/` | Document type | `type/hub` |
| `status/` | Workflow state | `status/active` |

These are complementary layers. A PT session note might be:
`domain/health` + `role/E` + `lyt/500` + `type/tracker` + `status/active`

## Folders vs Tags: The Parent Question

Some folders (like `atlas/health/`) contain content spanning multiple LYT numbers:
- PT notes, supplements, CPAP → `lyt/500` (Health & Body)
- Counseling sessions, PERMA-V → `lyt/200` (Mind & Meaning)

**The folder IS the parent.** Use `domain/health` when you want everything in the health domain regardless of LYT number. Use `lyt/500` or `lyt/200` when you want the finer slice. No need for a `lyt/health` superset tag — that's what `domain/` is for.

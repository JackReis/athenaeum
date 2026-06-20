---
title: Vault Frontmatter + Tag Standard (Combined)
status: ratified
priority: p2
created: 2026-05-05
last_touched_by: "claude-code (2bd3367c)"
related:
  - "[[docs/plans/2026-05-05-claudeclaw-v3-evaluation|Agentic OS Bake-Off]]"
  - "[[docs/agentic-os-eval/phase-0-audit-findings|Phase 0 Audit Findings]]"
  - "[[dashboards/today|Today]]"
  - "[[efforts/current/Active-Efforts-MOC|Active Efforts MOC]]"
tags:
  - convention
  - frontmatter
  - tags
  - standard
  - phase-0
touch_history:
  - "2026-05-06T00:34Z claude-code (2bd3367c)"
---

# Vault Frontmatter + Tag Standard

> **Combined standard, ratified 2026-05-05.** Reconciles Nov-2025 dashboard-era frontmatter with current effort-era frontmatter. **Combine first, prune later** (per Jack's direction). Existing notes don't need backfill until they're touched in the normal course of work; new notes follow this standard.

## Why this exists

Phase 0 audit (`docs/agentic-os-eval/phase-0-audit-findings.md`) revealed two collided taxonomies:
- Nov-2025 dashboard era used `timeline/*`, `domain/*`, `intensity`, `doc-type`, `parent`
- Current effort era uses `status`, `up`, `obn:sync`, `tags: effort`

Each independently is well-designed. Together they don't compose (dashboards query Nov-2025 tags that aren't on current effort notes). This standard ratifies the **union** so both views work.

## Frontmatter — required fields

Every curated note (anything not auto-imported, not session log, not transcript mirror) MUST have:

```yaml
---
title: <short prose>           # if file name doesn't speak for itself
created: YYYY-MM-DD
updated: YYYY-MM-DD            # bumped on edits, even small ones
tags: []                       # see "Tag taxonomy" below
status: <enum below>
---
```

## Frontmatter — recommended fields (use when applicable)

```yaml
---
# Lineage + navigation
up: "[[parent-note]]"            # LYT MOC pattern (current era — preferred)
parent: "[[parent-note]]"        # Nov-2025 era (synonym; either works)
aliases: [Alt Name 1, Alt Name 2]
last_touched_by: "<agent_slug>"  # required on fleet-level docs (gemini-cli, claude-code, openclaw-zoe)
touch_history: ["YYYY-MM-DDTHH:MMZ <agent_slug>"]  # custody+provenance SoT

# Effort-specific
intensity: <on|ongoing|simmering|off>   # bandwidth allocation per Efforts Intensity Framework
priority: <critical|high|medium|low>
domain: <move|job|health|family|home|personal|infra|reference>  # human-readable single value (not a tag)

# Surface control
surface: <true|false>            # default true; false hides from default dashboards
obn: sync                        # OBn ingest flag — include for searchable content
doc-type: <dashboard|moc|note|hub|effort|task|reference|synthesis|playbook>

# Source citations (per CLAUDE.md SOURCE CITATIONS rule)
related:                          # array of wikilinks for traceability
  - "[[path/to/source]]"

# Plan-specific (in docs/plans/)
priority: <p0|p1|p2|p3>          # plan severity
supersedes: ["[[older-plan]]"]
trigger_incident: <prose>
---
```

## Status enum (locked vocabulary)

Standardize. Existing notes with non-conforming values get migrated when touched.

| Value | Meaning |
|---|---|
| `active` | currently being worked on |
| `blocked` | waiting on external dependency |
| `paused` | intentionally on hold (intensity:off equivalent for non-effort notes) |
| `done` | completed, kept for reference |
| `archived` | older content, retained but suppressed from dashboards |
| `ratified` | for standards / decisions / ADRs — agreed upon |
| `ready-to-execute` | for plans — vetted and waiting to run |
| `superseded` | replaced by another note (use `supersedes` field on the new one) |

**Allowed legacy values** (not enforced — but normalize when editing):
- `Active`, `ACTIVE` → migrate to `active`
- `FILED`, `COMPLETE` → keep as-is on existing notes (they carry domain-specific meaning); for new notes use `done` plus a more-specific tag

## Tag taxonomy (combined)

Tags are namespaced with `/` separator. Multiple tags per note are normal.

### Domain tags (use ONE per note)
```
domain/move
domain/job
domain/health
domain/family
domain/home
domain/personal
domain/infra
domain/reference
domain/process
```

### Timeline tags (use ZERO or ONE)
```
timeline/critical          # immovable deadline
timeline/urgent            # important but flexible
timeline/important         # next-month tier
timeline/deferred          # explicitly deprioritized
timeline/<YYYY-MM>/week-N  # weekly bucket (rare; for sprint planning)
```

### Type tags (describes the note itself)
```
type/hub        # central organizing note (LYT MOC)
type/tracker    # dashboard / status surface
type/bridge     # cross-domain connector
type/playbook   # how-to / runbook
type/synthesis  # consolidated insight
type/reference  # stable factual content
folder-note     # _index of a folder
moc             # map of content (legacy synonym for type/hub)
```

### Status tags (parallel to `status` field — for boolean filters)
```
status/active
status/blocked
status/done
status/archived
```

### Relationship tags
```
rel/bridge       # connects two domains
rel/related      # weaker connection
rel/supersedes   # this replaces another note
```

### Effort/work tags
```
effort           # this note IS an effort
efforts          # this note REFERENCES efforts (deprecated synonym; both used)
project/<slug>   # tied to a specific project (insights, design-system, vista-del-mar, etc.)
```

### Person tags
```
person/<firstname>
```

### Topic tags
```
topic/<area>     # ui, requirements, workflow, testing, roadmap, etc.
```

### Auto-import / mass-content
```
meeting/granola      # 1237 notes — granola meeting captures
auto-imported        # 1236 notes — bulk imports
```
**These should set `surface: false`** so dashboards filter them out by default. Set when touching (don't mass-edit; let them migrate organically). Open question: bulk-set via obsidian-cli `bulk-properties.sh` with dry-run + sample review (Phase 0 atom 4).

### Vault meta tags
```
vault-root       # Home dashboard
dashboard        # any dashboard surface
convention       # standards docs (this file)
plan             # plans in docs/plans/
review           # reviews / audits
```

## Dashboard query conventions

When writing dataview queries for new dashboards:

1. **Default-filter `surface: false`:**
   ```dataview
   FROM "..."
   WHERE surface != false  # treats absence as true
   ```

2. **Folder-scoped queries first, tag-scoped second.** `efforts/current/` is the SSOT for active efforts; query the folder, not the `effort` tag (folder is exhaustive, tag is opt-in).

3. **Sort by `file.mtime DESC`** for recency-driven views; sort by `priority` for triage views.

4. **Limit 10–15** for default views. Smaller is more focused.

5. **Format dates** with `dateformat(file.mtime, "MMM dd")` not raw timestamps.

6. **Exclude self** with `WHERE file.name != this.file.name`.

7. **Bases or Dataview?** Bases for canonical surfaces that need to scale (top dashboards, MOCs); Dataview for ad-hoc inline queries within notes. Dual-use is fine — pick per surface.

## Migration rules

**No mass migration.** Existing notes don't need backfill. When you (or any agent) edits a note, normalize its frontmatter to this standard as a side effect. Over weeks the vault converges.

**Exceptions worth bulk-running:**
- `surface: false` on `meeting/granola` + `auto-imported` (~2500 notes) — Phase 0 atom 4, requires `bulk-properties.sh` with dry-run gate
- Status normalization (`Active` → `active`) — low-risk, high-reach
- `obn: sync` flag on curated content — drives OBn ingest

These get scripted, dry-run'd, sampled by Jack, then applied.

## Open questions

1. **Bases experiment** — port `dashboards/today.md` to a `.base` file as side-by-side, see if it loads faster on this 10k-note vault. Phase 0 stretch goal.
2. **`up` vs `parent`** — both valid, both used; should this standard pick one? Lean: keep both as synonyms (low cost, preserves existing notes).
3. **`tags: effort` vs `tags: efforts`** — same drift. Lean: `effort` (singular) is the ratified form; `efforts` accepted as alias.

## Custody

- Author: claude-code (opus-4-7), session 2bd3367c, 2026-05-05 ~19:35 CDT
- Reviewer: Jack (pending)
- Phase 0 atom: combines two surveyed taxonomies into one ratified standard, no destructive migration

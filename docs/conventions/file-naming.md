---
obn: sync
---

# File Naming Convention

## Why
Semantic filenames help humans browse in Finder/Terminal and improve at-a-glance understanding. Khoj searches content regardless of filename, so this is for YOU, not the AI.

## Convention

### Daily Notes (already good)
Pattern: `YYYYMMDD.md` or `YYYYMMDD-descriptive-suffix.md`
- `20260210.md`
- `20260209-pt-notes-with-ryan.md`

### PDFs
Pattern: `YYYY-MM-DD_Category_Descriptive-Topic.pdf`
- `2025-12-17_Report_Ardmore-Water-Quality-Lead-Levels.pdf`
- `2026-01-15_Protocol_PLLA-Recovery-Supplements-v2.pdf`

### Synthesis Notes
Pattern: `Synthesis - Descriptive Topic.md`
- `Synthesis - PLLA Recovery Supplement Comparison.md`

### Session/Handoff Notes
Pattern: `session-N-topic-YYYY-MM-DD.md` (already followed)

### General Notes
Pattern: `Descriptive-Topic-With-Hyphens.md`
- `ART-and-IASTM-for-SICK-Scapula.md`

## What NOT to Do
- Don't bulk-rename old files (breaks wikilinks, massive churn)
- Don't rename files managed by plugins or templates
- Don't obsess over legacy names — focus on new files

## Adoption Strategy
- **New files**: Follow convention from today forward
- **Touched files**: If you edit an old file and the name is cryptic, rename it (Obsidian auto-updates wikilinks)
- **PDFs**: Rename when you reference them in a note
- **No enforcement tooling needed** — convention is sufficient at current scale

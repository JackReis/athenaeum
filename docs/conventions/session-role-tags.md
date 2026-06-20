---
created: 2026-02-27
doc-type: convention
status: superseded
superseded_by: session-coding.md
tags:
  - convention
  - session-management
obn: sync
last_touched_by: "claude-code (859085b3)"
touch_history:
  - "2026-05-10T23:29Z claude-code (859085b3)"
---

# Session Role Tags

## Format

### In handoff files (frontmatter)
```yaml
session-role:
  - G        # primary role
  - H        # secondary role (optional, 2 max)
```

### In daily notes (inline)
Reference as `Session 57-GH` in the Session Achievements section.

### As Obsidian tags (searchable)
```yaml
tags:
  - role/G
  - role/H
```

## Role Codes

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

## Rules
1. Assign at **end** of session, not start
2. **1-2 codes max** — pick the dominant role(s)
3. Continuations use lowercase without hyphen: `Session 57c`
4. Role codes use uppercase with hyphen: `Session 57-G`
5. Coexists with `domain/` tags — roles describe Claude's lens, domains describe content

---
obn: sync
---

# Source Citation & Wikilink Protocol

Use this in any note where claims depend on other files (status, counts, dates, blockers, decisions).

## Rules

1. Cite every non-trivial claim.
2. Use path-explicit wikilinks (avoid short ambiguous links).
3. Use aliases for readability, path for reliability.
4. Add a references table near top or bottom of note.

## Citation line format

- `Source: [[path/to/file]]`
- `Source: [[path/one]], [[path/two]]`

## Link style

- Preferred: `[[atlas/dashboards/priority-dashboard|Priority Dashboard]]`
- Avoid: `[[priority-dashboard]]`

## Reference table template

| Claim/Section | Source File(s) | Last Checked |
|---|---|---|
| Current priorities | [[atlas/dashboards/priority-dashboard]], [[tasks/personal/personal]] | YYYY-MM-DD |
| Session updates | [[calendar/day/YYYY-MM/YYYYMMDD]], [[.Codex/memories/project_memory.json]] | YYYY-MM-DD |
| Constraints | [[MEMORY]] | YYYY-MM-DD |

## Notes

- Agents may resolve alternate targets dynamically, but documentation should still store explicit paths.
- For fast-moving notes, update `Last Checked` during session wrap-up.

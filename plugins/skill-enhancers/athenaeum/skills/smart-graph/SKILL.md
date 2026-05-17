---
name: smart-graph
description: >
  Use when exploring vault note relationships, finding what links to a note,
  identifying orphaned or disconnected notes, mapping heading structure,
  or discovering hub notes. Triggers: "find backlinks", "vault graph",
  "orphaned notes", "what links to", "note relationships",
  "show connections", "heading structure", "most linked notes".
---

# Smart Graph — Vault Relationship Analyzer

Query the Smart Connections pre-computed graph without reading markdown files.

## Overview

Smart Connections (Obsidian plugin) pre-extracts outlinks, heading structure, and tasks from every vault note into `.smart-env/multi/*.ajson` files. This skill exposes that data via a Python extraction script that builds a full vault graph in seconds.

## When to Use

- "What links to [[Transition-Hub]]?" — backlink discovery
- "Find orphaned notes" — notes with zero connections
- "Show me the graph around this note" — neighborhood mapping
- "What's the heading structure of X?" — block/outline view
- "Most connected notes in the vault" — hub identification
- Vault-wide relationship analysis without grepping markdown

## Procedure

### Step 1: Run the extraction script

```bash
# Vault summary (orphans, hubs, stats)
python3 scripts/extract-graph.py

# Backlinks to a note
python3 scripts/extract-graph.py --backlinks "efforts/current/Transition-Hub"

# Heading structure
python3 scripts/extract-graph.py --blocks "calendar/day/2026-02/20260210.md"

# 1-hop neighborhood
python3 scripts/extract-graph.py --neighborhood "000-dashboard.md"
```

**Notes:**
- Targets use vault-relative paths (no leading `/`, `.md` extension optional)
- Script reads from `$VAULT_ROOT/.smart-env/multi/` (default: `~/vault/.smart-env/multi/`)
- Output is JSON to stdout
- First run scans all `.ajson` files (~5-10 seconds for 12,000+ notes)

### Step 2: Interpret results

**Summary mode** returns:
- `stats`: total_notes, total_internal_links, orphan_count
- `orphans`: notes with no inbound or outbound links (capped at 100)
- `most_linked`: top 20 notes by backlink count (`target`, `backlink_count`)
- `most_outlinks`: top 20 notes by outgoing link count (`source`, `outlink_count`)

**Backlinks mode** returns:
- `target`: the note queried
- `backlink_count`: number of linking notes
- `backlinks`: sorted list of all notes linking to it

**Blocks mode** returns:
- `blocks`: heading hierarchy with `start_line`/`end_line` ranges
- `block_count`: number of named headings
- `task_lines`, `tasks`: task locations and completion status

**Neighborhood mode** returns:
- `outgoing`: list of `{target, title, line}` objects for notes this note links to
- `outgoing_count`: number of outgoing links
- `incoming`: sorted list of notes linking to this note
- `incoming_count`: number of incoming links

### Step 3: Present findings

Format results as markdown for the user. For backlinks and neighborhoods, use wikilink format `[[path|display]]` so results are vault-navigable.

## Environment

| Variable | Default | Description |
|---|---|---|
| `VAULT_ROOT` | `~/vault` | Path to the Obsidian vault root |

## Error Handling

### Smart Connections not indexed
**Cause**: `.smart-env/multi/` directory is empty or missing
**Solution**: Open Obsidian and let Smart Connections finish indexing.

### Note not found in index
**Cause**: Note was recently created or Smart Connections hasn't re-indexed
**Solution**: Force re-index in Obsidian, or fall back to Grep for the specific file.

### Stale data
**Cause**: Smart Connections updates incrementally; some `.ajson` files may lag
**Solution**: Check file modification times in `.smart-env/multi/`.

## Limitations

- **No semantic search** — embeddings require vector math; use Khoj MCP for semantic queries
- **Read-only** — this skill reads Smart Connections data, never writes to it
- **Stale if Obsidian closed** — Smart Connections only updates while Obsidian is running
- **External links excluded** — only vault-internal wikilinks are in the graph
- **Orphan count inflated** — includes `node_modules/`, `backup/`, archive directories that legitimately have no wikilinks

#!/usr/bin/env python3
"""Extract vault relationship graph from Smart Connections .ajson data.

Reads .smart-env/multi/*.ajson files and builds a vault relationship graph.
Outputs JSON to stdout for use by the smart-graph Claude Code skill.

Modes:
  default         Summary: stats, orphans, most_linked, most_outlinks
  --backlinks T   All notes linking TO target path T
  --blocks P      Heading/block structure of note at path P
  --neighborhood P  1-hop graph: incoming + outgoing links for path P
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path


def parse_ajson_file(filepath):
    """Parse a single .ajson file and yield (key, value) pairs.

    Each .ajson file contains one or more comma-separated key-value pairs:
      "smart_sources:path": {...}, "smart_blocks:path#heading": {...}, ...

    We wrap the content in {} to make it valid JSON after stripping trailing comma.
    Only entries with smart_sources: prefix are vault notes.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().rstrip().rstrip(",")
        if not content:
            return
        obj = json.loads("{" + content + "}")
        for key, value in obj.items():
            if key.startswith("smart_sources:") and isinstance(value, dict):
                yield key, value
    except (json.JSONDecodeError, OSError):
        # Skip unparseable files silently
        pass


def load_vault_graph(vault_path):
    """Load all smart_sources entries from .smart-env/multi/*.ajson.

    Returns:
        sources: dict mapping vault path -> source data dict
        backlinks: defaultdict(list) mapping target path -> list of source paths
    """
    multi_dir = Path(vault_path) / ".smart-env" / "multi"
    if not multi_dir.is_dir():
        print(
            json.dumps({"error": f".smart-env/multi not found at {multi_dir}"}),
            file=sys.stderr,
        )
        sys.exit(1)

    sources = {}
    backlinks = defaultdict(list)

    for fname in os.listdir(multi_dir):
        if not fname.endswith(".ajson"):
            continue
        filepath = multi_dir / fname
        for key, value in parse_ajson_file(filepath):
            note_path = value.get("path", key.replace("smart_sources:", ""))
            sources[note_path] = value

            # Build backlink index from outlinks
            outlinks = value.get("outlinks") or []
            for link in outlinks:
                if not isinstance(link, dict):
                    continue
                target = link.get("target", "")
                if not target:
                    continue
                # Skip external links
                if target.startswith("http") or target.startswith("obsidian://"):
                    continue
                backlinks[target].append(note_path)

    return sources, backlinks


def normalize_path(path):
    """Normalize a vault path: strip leading/trailing slashes and .md extension."""
    path = path.strip("/")
    if path.endswith(".md"):
        path = path[:-3]
    return path


def mode_summary(sources, backlinks):
    """Default mode: stats, orphans, most_linked, most_outlinks."""
    total_notes = len(sources)
    total_links = sum(
        len([
            ol for ol in (v.get("outlinks") or [])
            if isinstance(ol, dict)
            and ol.get("target", "")
            and not ol["target"].startswith("http")
            and not ol["target"].startswith("obsidian://")
        ])
        for v in sources.values()
    )

    # Build sets of paths that have inbound or outbound internal links
    has_outbound = set()
    has_inbound = set()

    for note_path, value in sources.items():
        outlinks = value.get("outlinks") or []
        for link in outlinks:
            if not isinstance(link, dict):
                continue
            target = link.get("target", "")
            if not target or target.startswith("http") or target.startswith("obsidian://"):
                continue
            has_outbound.add(note_path)
            has_inbound.add(target)

    # Orphans: notes with no inbound AND no outbound internal links
    # Normalize for comparison: backlinks keys don't have .md, source paths do
    orphans = []
    for note_path in sources:
        norm = normalize_path(note_path)
        if note_path not in has_outbound and norm not in has_inbound:
            orphans.append(note_path)

    # Most linked (by backlink count)
    backlink_counts = sorted(
        ((target, len(srcs)) for target, srcs in backlinks.items()),
        key=lambda x: -x[1],
    )
    most_linked = [
        {"target": t, "backlink_count": c} for t, c in backlink_counts[:20]
    ]

    # Most outlinks
    outlink_counts = sorted(
        (
            (
                note_path,
                len([
                    ol for ol in (value.get("outlinks") or [])
                    if isinstance(ol, dict)
                    and ol.get("target", "")
                    and not ol["target"].startswith("http")
                    and not ol["target"].startswith("obsidian://")
                ]),
            )
            for note_path, value in sources.items()
        ),
        key=lambda x: -x[1],
    )
    most_outlinks = [
        {"source": s, "outlink_count": c} for s, c in outlink_counts[:20]
    ]

    return {
        "stats": {
            "total_notes": total_notes,
            "total_internal_links": total_links,
            "orphan_count": len(orphans),
        },
        "orphans": orphans[:100],  # Cap at 100 to keep output manageable
        "most_linked": most_linked,
        "most_outlinks": most_outlinks,
    }


def mode_backlinks(sources, backlinks, target):
    """Find all notes linking to a given target path."""
    norm_target = normalize_path(target)

    # Collect backlinks matching the target (try both with and without .md)
    results = set()
    for bl_target, bl_sources in backlinks.items():
        if normalize_path(bl_target) == norm_target:
            results.update(bl_sources)

    return {
        "target": target,
        "backlink_count": len(results),
        "backlinks": sorted(results),
    }


def mode_blocks(sources, target_path):
    """Show heading/block structure for a specific note."""
    # Try to find the note by path (with or without .md)
    value = None
    for note_path, data in sources.items():
        if note_path == target_path or normalize_path(note_path) == normalize_path(target_path):
            value = data
            target_path = note_path
            break

    if value is None:
        return {"path": target_path, "error": "Note not found in smart-env data", "blocks": {}}

    raw_blocks = value.get("blocks") or {}
    # Filter out anonymous #{N} blocks and frontmatter marker
    anon_pattern = re.compile(r'#\{\d+\}$')
    blocks = {}
    for block_key, line_range in raw_blocks.items():
        if block_key == "#---frontmatter---":
            continue
        if anon_pattern.search(block_key):
            continue
        blocks[block_key] = {"start_line": line_range[0], "end_line": line_range[1]}

    return {
        "path": target_path,
        "block_count": len(blocks),
        "blocks": blocks,
        "task_lines": value.get("task_lines", []),
        "tasks": value.get("tasks", {}),
    }


def mode_neighborhood(sources, backlinks, target_path):
    """1-hop graph: incoming + outgoing links for a note."""
    norm_target = normalize_path(target_path)

    # Find the note data
    value = None
    resolved_path = target_path
    for note_path, data in sources.items():
        if note_path == target_path or normalize_path(note_path) == norm_target:
            value = data
            resolved_path = note_path
            break

    # Outgoing links from this note
    outgoing = []
    if value is not None:
        for link in (value.get("outlinks") or []):
            if not isinstance(link, dict):
                continue
            target = link.get("target", "")
            if not target or target.startswith("http") or target.startswith("obsidian://"):
                continue
            outgoing.append({
                "target": target,
                "title": link.get("title", ""),
                "line": link.get("line"),
            })

    # Incoming links to this note
    incoming = set()
    for bl_target, bl_sources in backlinks.items():
        if normalize_path(bl_target) == norm_target:
            incoming.update(bl_sources)

    return {
        "path": resolved_path,
        "outgoing_count": len(outgoing),
        "outgoing": outgoing,
        "incoming_count": len(incoming),
        "incoming": sorted(incoming),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract vault relationship graph from Smart Connections data."
    )
    parser.add_argument(
        "--vault",
        default=os.environ.get("VAULT_ROOT", str(Path.home() / "vault")),
        help="Path to the Obsidian vault root",
    )
    parser.add_argument(
        "--backlinks",
        metavar="TARGET",
        help="Find all notes linking TO this target path",
    )
    parser.add_argument(
        "--blocks",
        metavar="PATH",
        help="Show heading/block structure of a note",
    )
    parser.add_argument(
        "--neighborhood",
        metavar="PATH",
        help="1-hop graph: incoming + outgoing links for a note",
    )
    args = parser.parse_args()

    sources, backlink_index = load_vault_graph(args.vault)

    if args.backlinks:
        result = mode_backlinks(sources, backlink_index, args.backlinks)
    elif args.blocks:
        result = mode_blocks(sources, args.blocks)
    elif args.neighborhood:
        result = mode_neighborhood(sources, backlink_index, args.neighborhood)
    else:
        result = mode_summary(sources, backlink_index)

    json.dump(result, sys.stdout, indent=2)
    print()  # Trailing newline for clean output


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Ledger lifecycle CLI — JAC-31

Subcommands:
  append          Structured append to token/time/commit ledger
  append-commit   Auto-populate commit-log from git log
  rotate          Move entries older than 30 days to archive
  rollup          Aggregate daily entries into weekly/monthly summaries
  status          Show current file sizes, date ranges, last-entry timestamps
  query           Filter entries by agent, model, session, date range
  project-cost    Extrapolate cost from recent entries using model pricing

Format: YAML frontmatter + structured markdown, machine-writable.

SoT: ~/Documents/Coordination/2026-05-16-prd-sentry-ledger.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

TRACKING_ROOT = Path(os.environ.get("LEDGER_TRACKING_ROOT", Path.home() / "tracking"))
MAX_LINES = int(os.environ.get("LEDGER_MAX_LINES", "500"))
ROTATE_AFTER_DAYS = int(os.environ.get("LEDGER_ROTATE_DAYS", "30"))

LEDGER_FILES = {
    "token": "token-ledger.md",
    "time": "time-ledger.md",
    "commit": "commit-log.md",
}

# Model pricing (USD per 1M tokens) — update as new models are added.
MODEL_PRICING: dict[str, dict[str, float]] = {
    "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
    "claude-opus-4-20250514": {"input": 15.0, "output": 75.0},
    "gpt-4o": {"input": 2.5, "output": 10.0},
    "gpt-4.1": {"input": 2.0, "output": 8.0},
    "o3": {"input": 2.0, "output": 8.0},
    "o4-mini": {"input": 1.10, "output": 4.40},
    "gemini-2.5-pro": {"input": 1.25, "output": 10.0},
    "glm-5.1": {"input": 0.50, "output": 2.0},
    "kimi-k2": {"input": 0.60, "output": 2.40},
}


def _ledger_path(ledger: str) -> Path:
    name = LEDGER_FILES.get(ledger)
    if not name:
        raise ValueError(f"Unknown ledger: {ledger}. Choose from: {', '.join(LEDGER_FILES)}")
    return TRACKING_ROOT / name


def _archive_dir() -> Path:
    d = TRACKING_ROOT / "archive"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ── append ────────────────────────────────────────────────────────


def cmd_append(args: argparse.Namespace) -> int:
    ledger = args.ledger
    agent = args.agent or os.environ.get("AGENT_NAME", os.environ.get("USER", "unknown"))
    model = args.model or os.environ.get("AGENT_MODEL", "unknown")
    session = args.session or os.environ.get("LEDGER_SESSION_ID", "")
    data = json.loads(args.data) if args.data else {}

    path = _ledger_path(ledger)
    path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = _now_iso()
    entry = _format_entry(ledger, timestamp, agent, model, session, data)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(entry + "\n")

    print(f"[ledger] Appended to {ledger}: {path}")
    return 0


def _format_entry(
    ledger: str, timestamp: str, agent: str, model: str, session: str, data: dict[str, Any]
) -> str:
    if ledger == "token":
        tokens_in = data.get("tokens_in", 0)
        tokens_out = data.get("tokens_out", 0)
        cost = data.get("cost", "")
        cost_line = f"- **Cost:** {cost}" if cost else f"- **Cost:** (calculated)"
        return (
            f"\n### {timestamp}\n"
            f"- **Agent:** {agent}\n"
            f"- **Model:** {model}\n"
            f"- **Session:** {session}\n"
            f"- **Tokens In:** {tokens_in}\n"
            f"- **Tokens Out:** {tokens_out}\n"
            f"{cost_line}\n"
            f"- **Task:** {data.get('task', '')}"
        )
    elif ledger == "time":
        duration = data.get("duration", "00:00")
        category = data.get("category", "infrastructure")
        return (
            f"\n### {timestamp}\n"
            f"- **Agent:** {agent}\n"
            f"- **Model:** {model}\n"
            f"- **Session:** {session}\n"
            f"- **Duration:** {duration}\n"
            f"- **Category:** {category}\n"
            f"- **Task:** {data.get('task', '')}"
        )
    elif ledger == "commit":
        commit = data.get("commit", "manual")
        files_changed = data.get("files_changed", 0)
        return (
            f"\n### {timestamp}\n"
            f"- **Commit:** {commit}\n"
            f"- **Agent:** {agent}\n"
            f"- **Session:** {session}\n"
            f"- **Files Changed:** {files_changed}\n"
            f"- **Description:** {data.get('description', '')}\n"
            f"- **Deliverable:** {data.get('deliverable', '')}"
        )
    else:
        raise ValueError(f"Unknown ledger: {ledger}")


# ── append-commit ──────────────────────────────────────────────────


def _git_date_to_iso(date_iso: str) -> str | None:
    """Normalize a git `%ai` date to UTC ISO-8601 (`YYYY-MM-DDTHH:MM:SSZ`).

    Git emits dates like `2026-05-29 15:46:38 +0000` (two spaces, signed
    offset). Parse with the offset, convert to UTC, and format with a
    trailing `Z`. Returns None for unparseable input so callers can skip it.
    """
    try:
        dt = datetime.strptime(date_iso.strip(), "%Y-%m-%d %H:%M:%S %z")
    except ValueError:
        return None
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cmd_append_commit(args: argparse.Namespace) -> int:
    """Populate commit-log from recent git log."""
    repo = Path(args.repo) if args.repo else Path.cwd()
    count = args.count or 10
    session = (getattr(args, "session", None)
               or os.environ.get("LEDGER_SESSION_ID", "")) or "-"
    deliverable = getattr(args, "deliverable", None) or "-"
    try:
        result = subprocess.run(
            ["git", "log", f"--max-count={count}", "--pretty=format:%H|%an|%ai|%s"],
            capture_output=True, text=True, cwd=repo,
        )
        if result.returncode != 0:
            print(f"[ledger] git log failed: {result.stderr}", file=sys.stderr)
            return 1
    except FileNotFoundError:
        print("[ledger] git not found", file=sys.stderr)
        return 1

    path = _ledger_path("commit")
    path.parent.mkdir(parents=True, exist_ok=True)

    built: list[tuple[str, str]] = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        sha, author, date_iso, subject = parts
        timestamp = _git_date_to_iso(date_iso)
        if timestamp is None:
            print(f"[ledger] skipping commit with unparseable date: {date_iso!r}",
                  file=sys.stderr)
            continue
        entry = _format_entry(
            "commit", timestamp, author, "", session,
            {
                "commit": sha[:12],
                "files_changed": "(from git)",
                "description": subject,
                "deliverable": deliverable,
            },
        )
        built.append((timestamp, entry))

    # git log is newest-first; write entries oldest-first.
    built.sort(key=lambda pair: pair[0])
    entries = [entry for _, entry in built]

    with path.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(entries) + "\n")

    print(f"[ledger] Appended {len(entries)} commits to commit-log")
    return 0


# ── rotate ────────────────────────────────────────────────────────


def cmd_rotate(args: argparse.Namespace) -> int:
    """Move entries older than ROTATE_AFTER_DAYS to archive."""
    ledger = args.ledger
    path = _ledger_path(ledger)

    if not path.exists():
        print(f"[ledger] {path} does not exist, nothing to rotate")
        return 0

    content = path.read_text(encoding="utf-8")
    lines = content.split("\n")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=ROTATE_AFTER_DAYS)).strftime("%Y-%m-%d")

    # Find date headings older than cutoff.
    date_pattern = re.compile(r"^###\s*(\d{4}-\d{2}-\d{2})")
    archive_lines: list[str] = []
    keep_lines: list[str] = []
    current_section_old = False

    header_done = False
    for line in lines:
        if not header_done and not line.startswith("###"):
            keep_lines.append(line)
            continue
        header_done = True

        m = date_pattern.match(line)
        if m:
            current_section_old = m.group(1) < cutoff

        if current_section_old:
            archive_lines.append(line)
        else:
            keep_lines.append(line)

    if not archive_lines:
        print(f"[ledger] No entries older than {cutoff} to rotate")
        return 0

    # Write archive.
    archive_path = _archive_dir() / f"{LEDGER_FILES[ledger].replace('.md', '')}-{cutoff[:7]}.md"
    if archive_path.exists():
        with archive_path.open("a", encoding="utf-8") as fh:
            fh.write("\n".join(archive_lines) + "\n")
    else:
        archive_path.write_text("\n".join(archive_lines) + "\n", encoding="utf-8")

    # Rewrite active ledger.
    path.write_text("\n".join(keep_lines) + "\n", encoding="utf-8")

    print(f"[ledger] Rotated {len(archive_lines)} lines to {archive_path}")
    return 0


# ── rollup ─────────────────────────────────────────────────────────


def cmd_rollup(args: argparse.Namespace) -> int:
    """Aggregate entries into weekly or monthly summaries."""
    ledger = args.ledger
    period = args.period  # "weekly" or "monthly"
    path = _ledger_path(ledger)

    if not path.exists():
        print(f"[ledger] {path} does not exist")
        return 1

    content = path.read_text(encoding="utf-8")
    entries = _parse_entries(ledger, content)
    if not entries:
        print(f"[ledger] No entries found in {path}")
        return 0

    # Group by period.
    groups: dict[str, list[dict]] = {}
    for entry in entries:
        ts = entry.get("timestamp", "")[:10]
        if not ts:
            continue
        dt = datetime.strptime(ts, "%Y-%m-%d")
        if period == "weekly":
            key = f"{dt.strftime('%G-W%V')}"
        else:
            key = f"{ts[:7]}"
        groups.setdefault(key, []).append(entry)

    rollup_dir = TRACKING_ROOT / "rollups"
    rollup_dir.mkdir(parents=True, exist_ok=True)
    out_path = rollup_dir / f"{ledger}-{period}-rollup.md"

    lines = [f"# {ledger.title()} Ledger — {period.title()} Rollup\n"]
    for key in sorted(groups):
        group = groups[key]
        if ledger == "token":
            total_in = sum(int(e.get("tokens_in", 0)) for e in group if e.get("tokens_in"))
            total_out = sum(int(e.get("tokens_out", 0)) for e in group if e.get("tokens_out"))
            lines.append(f"\n## {key}\n- Entries: {len(group)}\n- Total tokens in: {total_in:,}\n- Total tokens out: {total_out:,}\n")
        elif ledger == "time":
            total_min = sum(_parse_duration_minutes(e.get("duration", "0:00")) for e in group)
            lines.append(f"\n## {key}\n- Entries: {len(group)}\n- Total time: {total_min:.0f} min ({total_min/60:.1f} hr)\n")
        else:
            lines.append(f"\n## {key}\n- Entries: {len(group)}\n")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[ledger] Rollup written to {out_path}")
    return 0


# ── status ─────────────────────────────────────────────────────────


def cmd_status(args: argparse.Namespace) -> int:
    """Show current file sizes, date ranges, last-entry timestamps."""
    for name, filename in LEDGER_FILES.items():
        path = TRACKING_ROOT / filename
        if not path.exists():
            print(f"  {name}: (not found)")
            continue
        content = path.read_text(encoding="utf-8")
        lines = content.split("\n")
        entry_count = sum(1 for l in lines if l.startswith("###"))
        dates = re.findall(r"^###\s*(\d{4}-\d{2}-\d{2})", content, re.MULTILINE)
        first = dates[0] if dates else "n/a"
        last = dates[-1] if dates else "n/a"
        size = len(content.encode("utf-8"))
        print(f"  {name}: {entry_count} entries, {len(lines)} lines, {size:,} bytes, range: {first} → {last}")

    archive = _archive_dir()
    archives = sorted(archive.glob("*.md"))
    if archives:
        print(f"\n  Archives: {len(archives)} file(s) in {archive}")
        for a in archives[:5]:
            print(f"    {a.name}")
        if len(archives) > 5:
            print(f"    ...and {len(archives) - 5} more")
    return 0


# ── query ──────────────────────────────────────────────────────────


def cmd_query(args: argparse.Namespace) -> int:
    """Filter entries by agent, model, session, date range."""
    ledger = args.ledger
    path = _ledger_path(ledger)

    if not path.exists():
        print(f"[ledger] {path} does not exist")
        return 1

    content = path.read_text(encoding="utf-8")
    entries = _parse_entries(ledger, content)
    results = entries

    if args.agent:
        results = [e for e in results if args.agent.lower() in e.get("agent", "").lower()]
    if args.model:
        results = [e for e in results if args.model.lower() in e.get("model", "").lower()]
    if args.session:
        results = [e for e in results if args.session in e.get("session", "")]
    if args.from_date:
        results = [e for e in results if e.get("timestamp", "")[:10] >= args.from_date]
    if args.to_date:
        results = [e for e in results if e.get("timestamp", "")[:10] <= args.to_date]

    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        for entry in results:
            print(_format_entry(ledger, entry.get("timestamp", ""), entry.get("agent", ""),
                                entry.get("model", ""), entry.get("session", ""), entry))
    return 0


# ── project-cost ──────────────────────────────────────────────────


def cmd_project_cost(args: argparse.Namespace) -> int:
    """Extrapolate cost from recent token entries."""
    days = args.days or 7
    path = _ledger_path("token")

    if not path.exists():
        print("[ledger] token-ledger not found")
        return 1

    content = path.read_text(encoding="utf-8")
    entries = _parse_entries("token", content)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    recent = [e for e in entries if e.get("timestamp", "")[:10] >= cutoff]

    total_in = sum(int(e.get("tokens_in", 0)) for e in recent)
    total_out = sum(int(e.get("tokens_out", 0)) for e in recent)

    # Calculate by-model breakdown.
    by_model: dict[str, dict[str, int]] = {}
    for e in recent:
        model = e.get("model", "unknown")
        by_model.setdefault(model, {"tokens_in": 0, "tokens_out": 0})
        by_model[model]["tokens_in"] += int(e.get("tokens_in", 0))
        by_model[model]["tokens_out"] += int(e.get("tokens_out", 0))

    print(f"Token usage (last {days} days): {len(recent)} entries")
    print(f"  Total tokens in:  {total_in:,}")
    print(f"  Total tokens out: {total_out:,}")
    print()
    print("By model:")
    total_cost = 0.0
    for model, usage in sorted(by_model.items()):
        pricing = MODEL_PRICING.get(model, {"input": 0, "output": 0})
        cost = (usage["tokens_in"] * pricing["input"] / 1_000_000) + \
               (usage["tokens_out"] * pricing["output"] / 1_000_000)
        total_cost += cost
        print(f"  {model}: {usage['tokens_in']:,} in / {usage['tokens_out']:,} out = ${cost:.2f}")

    # Project forward.
    if days > 0 and len(recent) > 0:
        daily_cost = total_cost / days
        monthly_projected = daily_cost * 30
        print(f"\n  Total cost: ${total_cost:.2f}")
        print(f"  Daily avg:  ${daily_cost:.2f}")
        print(f"  Monthly projected: ${monthly_projected:.2f}")
    return 0


# ── Parsing helpers ────────────────────────────────────────────────


def _parse_entries(ledger: str, content: str) -> list[dict[str, Any]]:
    """Parse ledger markdown into structured entries."""
    entries: list[dict[str, Any]] = []
    date_pattern = re.compile(r"^###\s*(\d{4}-\d{2}-\d{2}(?:T[\d:]+Z)?)")
    kv_pattern = re.compile(r"^- \*\*(.+?)\*\*\s+(.+)")
    current: dict[str, Any] | None = None

    for line in content.split("\n"):
        m = date_pattern.match(line)
        if m:
            if current:
                entries.append(current)
            current = {"timestamp": m.group(1), "ledger": ledger}
            continue
        if current is None:
            continue
        kv = kv_pattern.match(line)
        if kv:
            key = kv.group(1).rstrip(":").strip().lower().replace(" ", "_")
            value = kv.group(2).strip()
            current[key] = value

    if current:
        entries.append(current)
    return entries


def _parse_duration_minutes(duration: str) -> float:
    """Parse HH:MM or MM duration string to minutes."""
    if ":" in duration:
        parts = duration.split(":")
        try:
            return float(parts[0]) * 60 + float(parts[1])
        except (ValueError, IndexError):
            return 0
    try:
        return float(duration)
    except ValueError:
        return 0


# ── Main ───────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ledger lifecycle CLI — append, rotate, rollup, status, query, project-cost",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # append
    p_append = sub.add_parser("append", help="Structed append to a ledger")
    p_append.add_argument("ledger", choices=list(LEDGER_FILES.keys()))
    p_append.add_argument("--agent", help="Agent name (default: $AGENT_NAME or $USER)")
    p_append.add_argument("--model", help="Model name (default: $AGENT_MODEL)")
    p_append.add_argument("--session", help="Session ID (default: $LEDGER_SESSION_ID)")
    p_append.add_argument("--data", help="JSON data payload")

    # append-commit
    p_ac = sub.add_parser("append-commit", help="Populate commit-log from git log")
    p_ac.add_argument("--repo", help="Path to git repo (default: cwd)")
    p_ac.add_argument("--count", type=int, default=10, help="Number of recent commits")
    p_ac.add_argument("--session", help="Session ID (default: $LEDGER_SESSION_ID)")
    p_ac.add_argument("--deliverable", help="Deliverable tag for these commits")

    # rotate
    p_rotate = sub.add_parser("rotate", help="Move old entries to archive")
    p_rotate.add_argument("ledger", choices=list(LEDGER_FILES.keys()))

    # rollup
    p_rollup = sub.add_parser("rollup", help="Aggregate entries into summaries")
    p_rollup.add_argument("ledger", choices=list(LEDGER_FILES.keys()))
    p_rollup.add_argument("--period", choices=["weekly", "monthly"], default="weekly")

    # status
    sub.add_parser("status", help="Show current ledger file sizes and date ranges")

    # query
    p_query = sub.add_parser("query", help="Filter entries by agent, model, session, date")
    p_query.add_argument("ledger", choices=list(LEDGER_FILES.keys()))
    p_query.add_argument("--agent", help="Filter by agent name (substring match)")
    p_query.add_argument("--model", help="Filter by model name (substring match)")
    p_query.add_argument("--session", help="Filter by session ID")
    p_query.add_argument("--from-date", help="Start date (YYYY-MM-DD)")
    p_query.add_argument("--to-date", help="End date (YYYY-MM-DD)")
    p_query.add_argument("--json", dest="json_output", action="store_true", help="Output as JSON")

    # project-cost
    p_cost = sub.add_parser("project-cost", help="Extrapolate cost from token entries")
    p_cost.add_argument("--days", type=int, default=7, help="Lookback window in days")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    commands = {
        "append": cmd_append,
        "append-commit": cmd_append_commit,
        "rotate": cmd_rotate,
        "rollup": cmd_rollup,
        "status": cmd_status,
        "query": cmd_query,
        "project-cost": cmd_project_cost,
    }

    fn = commands.get(args.command)
    if not fn:
        parser.print_help()
        return 1
    return fn(args)


if __name__ == "__main__":
    sys.exit(main())
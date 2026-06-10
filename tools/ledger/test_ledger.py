#!/usr/bin/env python3
"""Tests for ledger.py — JAC-31

Covers: append, append-commit, rotate, rollup, status, query, project-cost,
plus parsing helpers and format compatibility with existing tracking/ files.
"""

import json
import os
import subprocess
import sys
import textwrap
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

LEDGER_PY = Path(__file__).parent / "ledger.py"
sys.path.insert(0, str(LEDGER_PY.parent))

import ledger as L


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def tmp_tracking(tmp_path):
    """Isolated tracking root for tests."""
    root = tmp_path / "tracking"
    root.mkdir()
    return root


@pytest.fixture
def env_tracking(tmp_tracking, monkeypatch):
    """Set LEDGER_TRACKING_ROOT to tmp dir."""
    monkeypatch.setenv("LEDGER_TRACKING_ROOT", str(tmp_tracking))
    L.TRACKING_ROOT = tmp_tracking
    L.LEDGER_FILES = {k: v for k, v in L.LEDGER_FILES.items()}
    return tmp_tracking


@pytest.fixture
def git_repo(tmp_path):
    """Create a git repo with deterministic commits covering both offset signs.

    Returns a factory that, given a list of (date, subject) pairs, creates one
    commit per pair with that authored/committed date, and returns the repo path.
    `date` strings are passed verbatim to GIT_AUTHOR_DATE/GIT_COMMITTER_DATE,
    so callers control the timezone offset (e.g. "-0500" or "+0000").
    """
    repo = tmp_path / "gitrepo"
    repo.mkdir()

    def run(cmd, **kwargs):
        return subprocess.run(cmd, cwd=repo, check=True,
                              capture_output=True, text=True, **kwargs)

    run(["git", "init", "-q"])
    run(["git", "config", "user.name", "Test Bot"])
    run(["git", "config", "user.email", "test@example.com"])
    run(["git", "config", "commit.gpgsign", "false"])

    def make_commits(commits):
        for i, (date, subject) in enumerate(commits):
            (repo / f"file{i}.txt").write_text(f"content {i}\n", encoding="utf-8")
            run(["git", "add", "-A"])
            env = dict(os.environ)
            env["GIT_AUTHOR_DATE"] = date
            env["GIT_COMMITTER_DATE"] = date
            run(["git", "commit", "-q", "-m", subject], env=env)
        return repo

    return make_commits


def _write_token_ledger(path: Path, entries: str) -> None:
    content = "# Token Ledger\n\n" + entries + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_commit_ledger(path: Path, entries: str) -> None:
    content = "# Commit Log\n\n" + entries + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_time_ledger(path: Path, entries: str) -> None:
    content = "# Time Ledger\n\n" + entries + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


SAMPLE_TOKEN_ENTRIES = textwrap.dedent("""\
### 2026-05-10T14:22:00Z
- **Agent:** opencode
- **Model:** claude-sonnet-4-20250514
- **Session:** ses-001
- **Tokens In:** 50000
- **Tokens Out:** 12000
- **Cost:** $0.33
- **Task:** athenaeum sentry integration

### 2026-05-11T09:00:00Z
- **Agent:** kimi
- **Model:** kimi-k2
- **Session:** ses-002
- **Tokens In:** 16000
- **Tokens Out:** 316
- **Cost:** (calculated)
- **Task:** context review

### 2026-05-15T18:30:00Z
- **Agent:** opencode
- **Model:** glm-5.1
- **Session:** ses-003
- **Tokens In:** 80000
- **Tokens Out:** 20000
- **Cost:** $0.40
- **Task:** ledger CLI
""")


SAMPLE_COMMIT_ENTRIES = textwrap.dedent("""\
### 2026-05-10T14:00:00Z
- **Commit:** abc123def456
- **Agent:** opencode
- **Session:** ses-001
- **Files Changed:** 5
- **Description:** sentry integration
- **Deliverable:** JAC-27

### 2026-05-12T10:00:00Z
- **Commit:** 789ghi012jkl
- **Agent:** kimi
- **Session:** ses-002
- **Files Changed:** 3
- **Description:** a2a task module
- **Deliverable:** athenaeum-a2a
""")


SAMPLE_TIME_ENTRIES = textwrap.dedent("""\
### 2026-05-10T14:00:00Z
- **Agent:** opencode
- **Model:** glm-5.1
- **Session:** ses-001
- **Duration:** 02:00
- **Category:** coordination
- **Task:** fleet directive

### 2026-05-12T10:00:00Z
- **Agent:** kimi
- **Model:** kimi-k2
- **Session:** ses-002
- **Duration:** 01:30
- **Category:** infrastructure
- **Task:** a2a wiring
""")


# ── Tests: _parse_entries ─────────────────────────────────────────────


class TestParseEntries:
    def test_parse_token_entries(self):
        entries = L._parse_entries("token", SAMPLE_TOKEN_ENTRIES)
        assert len(entries) == 3
        assert entries[0]["agent"] == "opencode"
        assert entries[0]["model"] == "claude-sonnet-4-20250514"
        assert entries[0]["tokens_in"] == "50000"
        assert entries[0]["tokens_out"] == "12000"

    def test_parse_commit_entries(self):
        entries = L._parse_entries("commit", SAMPLE_COMMIT_ENTRIES)
        assert len(entries) == 2
        assert entries[0]["commit"] == "abc123def456"
        assert entries[0]["files_changed"] == "5"

    def test_parse_time_entries(self):
        entries = L._parse_entries("time", SAMPLE_TIME_ENTRIES)
        assert len(entries) == 2
        assert entries[0]["duration"] == "02:00"
        assert entries[0]["category"] == "coordination"

    def test_parse_empty_content(self):
        entries = L._parse_entries("token", "")
        assert entries == []

    def test_parse_malformed_lines_ignored(self):
        content = "### 2026-05-10T12:00:00Z\n- garbage line\n- **Agent:** test\n"
        entries = L._parse_entries("token", content)
        assert len(entries) == 1
        assert entries[0]["agent"] == "test"

    def test_parse_real_format_with_date_field(self):
        real_format = "### 2026-05-10T14:22:00Z\n- **Date:** 2026-05-10\n- **Agent:** opencode\n- **Model:** glm-5.1\n- **Tokens In:** 50000\n- **Tokens Out:** 12000\n"
        entries = L._parse_entries("token", real_format)
        assert len(entries) == 1
        assert entries[0]["agent"] == "opencode"
        assert entries[0]["tokens_in"] == "50000"

    def test_parse_legacy_malformed_headings(self):
        """Backward-compat: old bug produced malformed timestamps in headings.

        Existing commit-log.md files in the wild contain headings like
        '### 2026-05-29T15:46:38TZ' (stray T before Z) and
        '### 2026-05-27 19:09:40 -0500Z' (space-separated + raw offset + blind Z).
        The parser must still salvage at least the date portion so old logs
        don't break. Characterization: assert timestamp[:10] is the correct day.
        """
        content = textwrap.dedent("""\
            ### 2026-05-29T15:46:38TZ
            - **Commit:** deadbeef0001
            - **Agent:** opencode
            - **Session:** ses-legacy-1
            - **Files Changed:** 2
            - **Description:** legacy stray-T entry
            - **Deliverable:** JAC-31

            ### 2026-05-27 19:09:40 -0500Z
            - **Commit:** deadbeef0002
            - **Agent:** kimi
            - **Session:** ses-legacy-2
            - **Files Changed:** 1
            - **Description:** legacy space-separated entry
            - **Deliverable:** JAC-31
            """)
        entries = L._parse_entries("commit", content)
        assert len(entries) == 2
        assert entries[0]["timestamp"][:10] == "2026-05-29"
        assert entries[0]["commit"] == "deadbeef0001"
        assert entries[1]["timestamp"][:10] == "2026-05-27"
        assert entries[1]["commit"] == "deadbeef0002"


# ── Tests: _format_entry ──────────────────────────────────────────────


class TestFormatEntry:
    def test_token_entry(self):
        result = L._format_entry("token", "2026-05-10T12:00:00Z", "opencode", "glm-5.1", "ses-1",
                                  {"tokens_in": 5000, "tokens_out": 1000, "task": "test"})
        assert "### 2026-05-10T12:00:00Z" in result
        assert "**Agent:** opencode" in result
        assert "**Model:** glm-5.1" in result
        assert "**Tokens In:** 5000" in result
        assert "**Tokens Out:** 1000" in result
        assert "**Task:** test" in result

    def test_token_entry_with_cost(self):
        result = L._format_entry("token", "2026-05-10T12:00:00Z", "a", "m", "s",
                                  {"tokens_in": 0, "tokens_out": 0, "cost": "$1.50", "task": "t"})
        assert "**Cost:** $1.50" in result

    def test_token_entry_without_cost(self):
        result = L._format_entry("token", "2026-05-10T12:00:00Z", "a", "m", "s",
                                  {"tokens_in": 0, "tokens_out": 0, "task": "t"})
        assert "**Cost:** (calculated)" in result

    def test_time_entry(self):
        result = L._format_entry("time", "2026-05-10T12:00:00Z", "a", "m", "s",
                                  {"duration": "01:30", "category": "infra", "task": "t"})
        assert "**Duration:** 01:30" in result
        assert "**Category:** infra" in result

    def test_commit_entry(self):
        result = L._format_entry("commit", "2026-05-10T12:00:00Z", "a", "m", "s",
                                  {"commit": "abc123", "files_changed": 3, "description": "test", "deliverable": "JAC-31"})
        assert "**Commit:** abc123" in result
        assert "**Files Changed:** 3" in result
        assert "**Deliverable:** JAC-31" in result

    def test_unknown_ledger_raises(self):
        with pytest.raises(ValueError, match="Unknown ledger"):
            L._format_entry("bogus", "2026-05-10T12:00:00Z", "a", "m", "s", {})


# ── Tests: cmd_append ─────────────────────────────────────────────────


class TestCmdAppend:
    def test_append_token_entry(self, env_tracking, tmp_path):
        data = json.dumps({"tokens_in": 100, "tokens_out": 50, "task": "unit test"})
        args = L.build_parser().parse_args(["append", "token", "--agent", "tester",
                                             "--model", "glm-5.1", "--session", "test-1",
                                             "--data", data])
        result = L.cmd_append(args)
        assert result == 0

        path = env_tracking / "token-ledger.md"
        assert path.exists()
        content = path.read_text()
        assert "**Agent:** tester" in content
        assert "**Tokens In:** 100" in content
        assert "**Tokens Out:** 50" in content

    def test_append_time_entry(self, env_tracking):
        data = json.dumps({"duration": "00:45", "category": "testing", "task": "unit test"})
        args = L.build_parser().parse_args(["append", "time", "--agent", "tester",
                                             "--data", data])
        result = L.cmd_append(args)
        assert result == 0

        path = env_tracking / "time-ledger.md"
        content = path.read_text()
        assert "**Duration:** 00:45" in content
        assert "**Category:** testing" in content

    def test_append_commit_entry(self, env_tracking):
        data = json.dumps({"commit": "deadbeef", "files_changed": 2,
                           "description": "test commit", "deliverable": "test"})
        args = L.build_parser().parse_args(["append", "commit", "--agent", "bot",
                                             "--data", data])
        result = L.cmd_append(args)
        assert result == 0

        path = env_tracking / "commit-log.md"
        content = path.read_text()
        assert "**Commit:** deadbeef" in content

    def test_append_defaults_from_env(self, env_tracking, monkeypatch):
        monkeypatch.setenv("AGENT_NAME", "env-agent")
        monkeypatch.setenv("AGENT_MODEL", "env-model")
        monkeypatch.setenv("LEDGER_SESSION_ID", "env-sess")
        data = json.dumps({"tokens_in": 0, "tokens_out": 0, "task": "env test"})
        args = L.build_parser().parse_args(["append", "token", "--data", data])
        L.cmd_append(args)
        content = (env_tracking / "token-ledger.md").read_text()
        assert "**Agent:** env-agent" in content
        assert "**Model:** env-model" in content

    def test_append_creates_tracking_dir(self, tmp_path, monkeypatch):
        nested = tmp_path / "deep" / "tracking"
        monkeypatch.setenv("LEDGER_TRACKING_ROOT", str(nested))
        L.TRACKING_ROOT = nested
        data = json.dumps({"tokens_in": 0, "tokens_out": 0, "task": "dir test"})
        args = L.build_parser().parse_args(["append", "token", "--data", data])
        result = L.cmd_append(args)
        assert result == 0
        assert (nested / "token-ledger.md").exists()

    def test_append_unknown_ledger_fails(self):
        with pytest.raises(SystemExit):
            L.build_parser().parse_args(["append", "bogus"])


# ── Tests: cmd_status ─────────────────────────────────────────────────


class TestCmdStatus:
    def test_status_shows_all_ledgers(self, env_tracking):
        _write_token_ledger(env_tracking / "token-ledger.md", SAMPLE_TOKEN_ENTRIES)
        _write_time_ledger(env_tracking / "time-ledger.md", SAMPLE_TIME_ENTRIES)
        _write_commit_ledger(env_tracking / "commit-log.md", SAMPLE_COMMIT_ENTRIES)

        args = L.build_parser().parse_args(["status"])
        result = L.cmd_status(args)
        assert result == 0

    def test_status_missing_files(self, env_tracking, capsys):
        args = L.build_parser().parse_args(["status"])
        result = L.cmd_status(args)
        assert result == 0
        out = capsys.readouterr().out
        assert "not found" in out

    def test_status_shows_entry_count(self, env_tracking, capsys):
        _write_token_ledger(env_tracking / "token-ledger.md", SAMPLE_TOKEN_ENTRIES)
        args = L.build_parser().parse_args(["status"])
        L.cmd_status(args)
        out = capsys.readouterr().out
        assert "3 entries" in out


# ── Tests: cmd_rotate ─────────────────────────────────────────────────


class TestCmdRotate:
    def test_rotate_moves_old_entries(self, env_tracking):
        old_date = (datetime.now(timezone.utc) - timedelta(days=60)).strftime("%Y-%m-%dT%H:%M:%SZ")
        recent_date = (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        content = (
            f"### {old_date}\n- **Agent:** old-bot\n- **Task:** old\n\n"
            f"### {recent_date}\n- **Agent:** new-bot\n- **Task:** new\n"
        )
        _write_token_ledger(env_tracking / "token-ledger.md", content)

        args = L.build_parser().parse_args(["rotate", "token"])
        result = L.cmd_rotate(args)
        assert result == 0

        remaining = (env_tracking / "token-ledger.md").read_text()
        assert "new-bot" in remaining
        assert "old-bot" not in remaining

        archive = env_tracking / "archive"
        assert archive.exists()
        archives = list(archive.glob("token-*.md"))
        assert len(archives) >= 1
        assert "old-bot" in archives[0].read_text()

    def test_rotate_no_old_entries(self, env_tracking, capsys):
        recent_date = (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        content = f"### {recent_date}\n- **Agent:** new-bot\n- **Task:** recent\n"
        _write_token_ledger(env_tracking / "token-ledger.md", content)

        args = L.build_parser().parse_args(["rotate", "token"])
        result = L.cmd_rotate(args)
        assert result == 0
        assert "No entries older than" in capsys.readouterr().out

    def test_rotate_nonexistent_file(self, env_tracking, capsys):
        args = L.build_parser().parse_args(["rotate", "token"])
        result = L.cmd_rotate(args)
        assert result == 0
        assert "does not exist" in capsys.readouterr().out

    def test_rotate_preserves_header(self, env_tracking):
        old_date = (datetime.now(timezone.utc) - timedelta(days=60)).strftime("%Y-%m-%dT%H:%M:%SZ")
        content = f"# Token Ledger\n\n### {old_date}\n- **Agent:** old\n"
        path = env_tracking / "token-ledger.md"
        path.write_text(content, encoding="utf-8")

        args = L.build_parser().parse_args(["rotate", "token"])
        L.cmd_rotate(args)

        remaining = path.read_text()
        assert "# Token Ledger" in remaining


# ── Tests: cmd_rollup ─────────────────────────────────────────────────


class TestCmdRollup:
    def test_rollup_token_weekly(self, env_tracking, capsys):
        _write_token_ledger(env_tracking / "token-ledger.md", SAMPLE_TOKEN_ENTRIES)
        args = L.build_parser().parse_args(["rollup", "token", "--period", "weekly"])
        result = L.cmd_rollup(args)
        assert result == 0

        rollup = env_tracking / "rollups" / "token-weekly-rollup.md"
        assert rollup.exists()
        content = rollup.read_text()
        assert "Token" in content
        assert "Weekly" in content

    def test_rollup_time_monthly(self, env_tracking):
        _write_time_ledger(env_tracking / "time-ledger.md", SAMPLE_TIME_ENTRIES)
        args = L.build_parser().parse_args(["rollup", "time", "--period", "monthly"])
        result = L.cmd_rollup(args)
        assert result == 0

        rollup = env_tracking / "rollups" / "time-monthly-rollup.md"
        assert rollup.exists()
        content = rollup.read_text()
        assert "min" in content

    def test_rollup_commit(self, env_tracking):
        _write_commit_ledger(env_tracking / "commit-log.md", SAMPLE_COMMIT_ENTRIES)
        args = L.build_parser().parse_args(["rollup", "commit", "--period", "weekly"])
        result = L.cmd_rollup(args)
        assert result == 0

    def test_rollup_nonexistent_file(self, env_tracking, capsys):
        args = L.build_parser().parse_args(["rollup", "token"])
        result = L.cmd_rollup(args)
        assert result == 1

    def test_rollup_empty_file(self, env_tracking):
        (env_tracking / "token-ledger.md").write_text("# Token Ledger\n\n", encoding="utf-8")
        args = L.build_parser().parse_args(["rollup", "token"])
        result = L.cmd_rollup(args)
        assert result == 0


# ── Tests: cmd_query ──────────────────────────────────────────────────


class TestCmdQuery:
    def test_query_by_agent(self, env_tracking, capsys):
        _write_token_ledger(env_tracking / "token-ledger.md", SAMPLE_TOKEN_ENTRIES)
        args = L.build_parser().parse_args(["query", "token", "--agent", "kimi"])
        result = L.cmd_query(args)
        assert result == 0
        out = capsys.readouterr().out
        assert "kimi" in out.lower()

    def test_query_by_model(self, env_tracking, capsys):
        _write_token_ledger(env_tracking / "token-ledger.md", SAMPLE_TOKEN_ENTRIES)
        args = L.build_parser().parse_args(["query", "token", "--model", "glm"])
        result = L.cmd_query(args)
        assert result == 0

    def test_query_json_output(self, env_tracking, capsys):
        _write_token_ledger(env_tracking / "token-ledger.md", SAMPLE_TOKEN_ENTRIES)
        args = L.build_parser().parse_args(["query", "token", "--json"])
        result = L.cmd_query(args)
        assert result == 0
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert len(parsed) == 3

    def test_query_date_range(self, env_tracking, capsys):
        _write_token_ledger(env_tracking / "token-ledger.md", SAMPLE_TOKEN_ENTRIES)
        args = L.build_parser().parse_args(["query", "token", "--from-date", "2026-05-11", "--to-date", "2026-05-12"])
        result = L.cmd_query(args)
        assert result == 0
        out = capsys.readouterr().out
        assert "kimi" in out.lower()

    def test_query_no_results(self, env_tracking, capsys):
        _write_token_ledger(env_tracking / "token-ledger.md", SAMPLE_TOKEN_ENTRIES)
        args = L.build_parser().parse_args(["query", "token", "--agent", "nonexistent"])
        result = L.cmd_query(args)
        assert result == 0

    def test_query_date_range_with_legacy_entries(self, env_tracking, capsys):
        """Day-granularity date filtering must still bracket legacy malformed entries.

        Seeds a commit-log.md with the two malformed heading forms produced by
        the old bug, then queries a date range bracketing both. Both must come
        back, confirming --from-date/--to-date filtering (which compares
        timestamp[:10]) tolerates the salvaged legacy timestamps.
        """
        legacy_entries = textwrap.dedent("""\
            ### 2026-05-29T15:46:38TZ
            - **Commit:** deadbeef0001
            - **Agent:** opencode
            - **Session:** ses-legacy-1
            - **Files Changed:** 2
            - **Description:** legacy stray-T entry
            - **Deliverable:** JAC-31

            ### 2026-05-27 19:09:40 -0500Z
            - **Commit:** deadbeef0002
            - **Agent:** kimi
            - **Session:** ses-legacy-2
            - **Files Changed:** 1
            - **Description:** legacy space-separated entry
            - **Deliverable:** JAC-31
            """)
        _write_commit_ledger(env_tracking / "commit-log.md", legacy_entries)
        args = L.build_parser().parse_args(
            ["query", "commit", "--from-date", "2026-05-27", "--to-date", "2026-05-29", "--json"])
        result = L.cmd_query(args)
        assert result == 0
        parsed = json.loads(capsys.readouterr().out)
        assert len(parsed) == 2
        commits = {e["commit"] for e in parsed}
        assert commits == {"deadbeef0001", "deadbeef0002"}


# ── Tests: cmd_project_cost ───────────────────────────────────────────


class TestCmdProjectCost:
    def test_project_cost_basic(self, env_tracking, capsys):
        _write_token_ledger(env_tracking / "token-ledger.md", SAMPLE_TOKEN_ENTRIES)
        args = L.build_parser().parse_args(["project-cost", "--days", "30"])
        result = L.cmd_project_cost(args)
        assert result == 0
        out = capsys.readouterr().out
        assert "Total tokens in" in out
        assert "Monthly projected" in out

    def test_project_cost_by_model(self, env_tracking, capsys):
        _write_token_ledger(env_tracking / "token-ledger.md", SAMPLE_TOKEN_ENTRIES)
        args = L.build_parser().parse_args(["project-cost", "--days", "30"])
        L.cmd_project_cost(args)
        out = capsys.readouterr().out
        assert "claude-sonnet-4-20250514" in out
        assert "kimi-k2" in out
        assert "glm-5.1" in out

    def test_project_cost_no_file(self, env_tracking, capsys):
        args = L.build_parser().parse_args(["project-cost"])
        result = L.cmd_project_cost(args)
        assert result == 1

    def test_project_cost_pricing(self, env_tracking, capsys):
        entries = (
            "### 2026-05-15T12:00:00Z\n"
            "- **Agent:** test\n"
            "- **Model:** glm-5.1\n"
            "- **Tokens In:** 1000000\n"
            "- **Tokens Out:** 1000000\n"
            "- **Cost:** (calculated)\n"
            "- **Task:** pricing test\n"
        )
        _write_token_ledger(env_tracking / "token-ledger.md", entries)
        args = L.build_parser().parse_args(["project-cost", "--days", "30"])
        L.cmd_project_cost(args)
        out = capsys.readouterr().out
        assert "$2.50" in out


# ── Tests: cmd_append_commit ──────────────────────────────────────────


class TestCmdAppendCommit:
    def test_append_commit_from_repo(self, env_tracking):
        args = L.build_parser().parse_args(["append-commit", "--repo", str(Path(__file__).parent.parent.parent),
                                             "--count", "3"])
        result = L.cmd_append_commit(args)
        assert result == 0
        path = env_tracking / "commit-log.md"
        assert path.exists()
        content = path.read_text()
        assert "###" in content

    def test_append_commit_no_git(self, env_tracking, monkeypatch, tmp_path):
        empty_dir = tmp_path / "no_git_here"
        empty_dir.mkdir()
        args = L.build_parser().parse_args(["append-commit", "--repo", str(empty_dir), "--count", "1"])
        result = L.cmd_append_commit(args)
        assert result == 1

    # WI-1: timestamp normalization to UTC ISO-8601 with trailing Z.
    def test_timestamps_are_utc_iso8601(self, env_tracking, git_repo):
        import re as _re
        repo = git_repo([
            ("2026-05-27 19:09:40 -0500", "negative offset commit"),
            ("2026-05-29 15:46:38 +0000", "zero offset commit"),
        ])
        args = L.build_parser().parse_args(["append-commit", "--repo", str(repo), "--count", "10"])
        assert L.cmd_append_commit(args) == 0

        content = (env_tracking / "commit-log.md").read_text()
        headings = [l for l in content.split("\n") if l.startswith("### ")]
        assert headings, "expected at least one ### heading"
        pat = _re.compile(r"^### \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        for h in headings:
            assert pat.match(h), f"heading not strict ISO-8601 UTC: {h!r}"

        timestamps = {h[len("### "):] for h in headings}
        # -0500 19:09:40 -> +5h -> next day 00:09:40 UTC; +0000 unchanged.
        assert "2026-05-28T00:09:40Z" in timestamps
        assert "2026-05-29T15:46:38Z" in timestamps

    # WI-2: entries written oldest-first (git log is newest-first).
    def test_entries_appended_oldest_first(self, env_tracking, git_repo):
        import re as _re
        repo = git_repo([
            ("2026-05-01 10:00:00 +0000", "first"),
            ("2026-05-02 10:00:00 +0000", "second"),
            ("2026-05-03 10:00:00 +0000", "third"),
        ])
        args = L.build_parser().parse_args(["append-commit", "--repo", str(repo), "--count", "10"])
        assert L.cmd_append_commit(args) == 0

        content = (env_tracking / "commit-log.md").read_text()
        pat = _re.compile(r"^### (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)$")
        timestamps = [m.group(1) for l in content.split("\n") if (m := pat.match(l))]
        assert len(timestamps) == 3
        assert timestamps == sorted(timestamps)

    def test_identical_timestamps_keep_oldest_first(self, env_tracking, git_repo):
        # Two commits with the EXACT same authored timestamp. git log lists
        # them newest-first ("beta" then "alpha"); a stable sort alone would
        # preserve that. Reversing before the sort must yield commit-creation
        # (oldest-first) order: alpha, beta.
        same = "2026-05-04 10:00:00 +0000"
        repo = git_repo([(same, "alpha"), (same, "beta")])
        args = L.build_parser().parse_args(["append-commit", "--repo", str(repo), "--count", "10"])
        assert L.cmd_append_commit(args) == 0

        content = (env_tracking / "commit-log.md").read_text()
        descriptions = [l.split("**Description:**", 1)[1].strip()
                        for l in content.split("\n") if "**Description:**" in l]
        assert descriptions == ["alpha", "beta"]

    # WI-3: Session/Deliverable populated and round-trip through _parse_entries.
    def test_session_and_deliverable_populated(self, env_tracking, git_repo, monkeypatch):
        monkeypatch.setenv("LEDGER_SESSION_ID", "ses-x")
        repo = git_repo([("2026-05-10 12:00:00 +0000", "feature work")])
        args = L.build_parser().parse_args(
            ["append-commit", "--repo", str(repo), "--count", "1", "--deliverable", "JAC-31"])
        assert L.cmd_append_commit(args) == 0

        content = (env_tracking / "commit-log.md").read_text()
        assert "- **Session:** ses-x" in content
        assert "- **Deliverable:** JAC-31" in content

        parsed = L._parse_entries("commit", content)
        assert parsed[0]["session"] == "ses-x"
        assert parsed[0]["deliverable"] == "JAC-31"

    def test_session_and_deliverable_placeholder_roundtrip(self, env_tracking, git_repo, monkeypatch):
        monkeypatch.delenv("LEDGER_SESSION_ID", raising=False)
        repo = git_repo([("2026-05-11 12:00:00 +0000", "no metadata")])
        args = L.build_parser().parse_args(["append-commit", "--repo", str(repo), "--count", "1"])
        assert L.cmd_append_commit(args) == 0

        content = (env_tracking / "commit-log.md").read_text()
        parsed = L._parse_entries("commit", content)
        # Placeholder ("-") must render and round-trip (guards kv_pattern
        # silently dropping empty values).
        assert parsed[0].get("session") == "-"
        assert parsed[0].get("deliverable") == "-"


# ── Tests: _parse_duration_minutes ────────────────────────────────────


class TestParseDurationMinutes:
    def test_hh_mm(self):
        assert L._parse_duration_minutes("02:30") == 150.0

    def test_minutes_only(self):
        assert L._parse_duration_minutes("45") == 45.0

    def test_zero(self):
        assert L._parse_duration_minutes("00:00") == 0.0

    def test_invalid(self):
        assert L._parse_duration_minutes("abc") == 0.0

    def test_hh_mm_with_hours(self):
        assert L._parse_duration_minutes("01:30") == 90.0


# ── Tests: _ledger_path validation ────────────────────────────────────


class TestLedgerPath:
    def test_valid_ledgers(self, env_tracking):
        for ledger_name in ("token", "time", "commit"):
            path = L._ledger_path(ledger_name)
            assert path.name == L.LEDGER_FILES[ledger_name]

    def test_invalid_ledger_raises(self):
        with pytest.raises(ValueError, match="Unknown ledger"):
            L._ledger_path("bogus")


# ── Tests: Real format compatibility ─────────────────────────────────


class TestRealFormatCompat:
    """Verify that ledger.py handles the EXISTING tracking/ format correctly."""

    def test_parse_real_token_ledger(self, env_tracking):
        real_content = textwrap.dedent("""\
            ### Session: kimi-claw-main-2026-04-26
            - **Date:** 2026-04-26
            - **Agent:** OLIVIER_MBP
            - **Model:** moonshot/kimi-k2.6
            - **Tokens In:** ~16k
            - **Tokens Out:** ~316
            - **Cost:** Unknown
            - **Task:** Session context review

            ### 2026-05-10T14:22:00Z
            - **Agent:** opencode
            - **Model:** glm-5.1
            - **Session:** ses-001
            - **Tokens In:** 50000
            - **Tokens Out:** 12000
            - **Cost:** $0.33
            - **Task:** athenaeum sentry
        """)
        entries = L._parse_entries("token", real_content)
        # "Session: kimi-claw..." heading doesn't match ISO date pattern,
        # so only the second entry is parsed (this is expected — the old
        # "Session:" format is a different heading convention).
        assert len(entries) >= 1
        assert entries[0]["agent"] == "opencode"
        assert entries[0]["tokens_in"] == "50000"

    def test_parse_real_time_ledger(self, env_tracking):
        real_content = textwrap.dedent("""\
            ### 2026-05-16 (afternoon)
            - **Agent:** opencode (glm-5.1)
            - **Duration:** ~2:00
            - **Category:** coordination

            ### 2026-05-16
            - **Agent:** opencode (glm-5.1)
            - **Duration:** ~3:00
            - **Category:** infrastructure
        """)
        entries = L._parse_entries("time", real_content)
        assert len(entries) >= 1

    def test_append_then_rotate_roundtrip(self, env_tracking):
        data = json.dumps({"tokens_in": 100, "tokens_out": 50, "task": "roundtrip"})
        args = L.build_parser().parse_args(["append", "token", "--agent", "tester",
                                             "--model", "glm-5.1", "--data", data])
        L.cmd_append(args)

        args = L.build_parser().parse_args(["status"])
        assert L.cmd_status(args) == 0

        args = L.build_parser().parse_args(["rotate", "token"])
        assert L.cmd_rotate(args) == 0

    def test_status_on_real_tracking_dir(self, tmp_path, monkeypatch):
        real_dir = Path.home() / "tracking"
        if not real_dir.exists():
            pytest.skip("No real ~/tracking dir")
        monkeypatch.setenv("LEDGER_TRACKING_ROOT", str(real_dir))
        L.TRACKING_ROOT = real_dir
        args = L.build_parser().parse_args(["status"])
        assert L.cmd_status(args) == 0


# ── Tests: CLI main() ────────────────────────────────────────────────


class TestMain:
    def test_main_no_args_exits(self):
        with pytest.raises(SystemExit):
            L.main()

    def test_main_status(self, env_tracking):
        with patch("sys.argv", ["ledger", "status"]):
            L.TRACKING_ROOT = env_tracking
            assert L.main() == 0

    def test_main_parser_built(self):
        parser = L.build_parser()
        assert parser is not None
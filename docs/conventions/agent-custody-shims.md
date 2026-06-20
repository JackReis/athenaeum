---
created: 2026-04-23
type: convention
status: active
owner: fleet
obn: sync
last_touched_by: "claude-code (eb531513)"
touch_history:
  - "2026-04-23T14:50Z claude-code (d0eecb0d)"
  - "2026-04-27T01:21Z claude-code (eb531513)"
---

# Agent Custody Shims — Per-Runtime Integration Cookbook

**Purpose:** wire each fleet runtime into the `touch_history` custody pattern (pattern #5 of 5 in [`agent-custody-provenance.md`](agent-custody-provenance.md)). After this, every runtime contributes to the file-level chain of custody, not just Claude Code.

**Shared stamp script:** `/Users/jack.reis/Documents/=notes/.claude/hooks/agent-id-stamp.py`. Runtime-agnostic since commit `a47321c48`.

## Contract

Every runtime, after writing or editing a vault markdown file with YAML frontmatter, MUST call the stamp script with its runtime identity. The script:
- Updates `last_touched_by: "<agent> (<short-session>)"`
- Appends a dated entry to `touch_history:` (deduped against the prior entry)
- Skips files in `calendar/day/**`, `logs/**`, `.claude/**`
- Skips files outside the vault root
- Is idempotent — re-running on an unchanged file is a no-op

Exit code: always 0 on clean runs (including silently-skipped). Non-zero only on invocation errors.

## Invocation modes

Pick whichever fits the runtime's plumbing; CLI args always win on conflict.

### Mode 1 — CLI args (most explicit, safest for concurrent invocation)

```bash
python3 /Users/jack.reis/Documents/=notes/.claude/hooks/agent-id-stamp.py \
  --file "<absolute path of edited .md>" \
  --agent "<agent-name>" \
  --session "<short-session-id>"
```

### Mode 2 — JSON stdin (Claude Code PostToolUse, already wired)

```json
{
  "session_id": "08a57670-xxx",
  "tool_input": {"file_path": "/abs/path.md"},
  "tool_response": {"filePath": "/abs/path.md"}
}
```
Piped to the script on stdin. Agent defaults to `claude-code`. **No change needed for Claude Code — this is the existing PostToolUse hook.**

### Mode 3 — Env vars (runtimes that set identity once per process)

```bash
export FLEET_AGENT_NAME=<agent-name>
export FLEET_SESSION_ID=<short-session-id>
# ...per-edit:
FLEET_STAMP_FILE="<abs path>" python3 /Users/jack.reis/Documents/=notes/.claude/hooks/agent-id-stamp.py
```

## Runtime-specific shims

### Hermes (Wings) — local Nous Research Hermes Agent runtime

**Integration point:** Hermes has its own tool-call framework with a post-edit hook surface. Ship a shim in the Hermes repo / config that runs after any file-write tool completes.

```bash
# In the Hermes post-edit hook
python3 /Users/jack.reis/Documents/=notes/.claude/hooks/agent-id-stamp.py \
  --file "$FILE_EDITED" \
  --agent hermes \
  --session "${HERMES_SESSION_ID:0:8}"
```

**Tracking task:** `claude/tasks/active/custody-shim-hermes.md`.

### OLIVIER_MBP (Zoe, formerly Zolivier) — local OpenClaw gateway

**Integration point:** OpenClaw gateway writes pass through `openclaw` CLI. Wrap the edit command (or add a post-tool-use Python hook in the local OpenClaw config).

```bash
# After any `openclaw exec` that lands a vault .md edit
python3 /Users/jack.reis/Documents/=notes/.claude/hooks/agent-id-stamp.py \
  --file "$EDITED" --agent olivier-mbp --session "${OPENCLAW_SESSION:0:8}"
```

**Tracking task:** `claude/tasks/active/custody-shim-zolivier.md`.

### KimiClaw (Mara / Kopi) — cloud OpenClaw runtime

**Integration point:** KimiClaw runs in a cloud OpenClaw deployment. Writes reach the vault via git push or rsync. The shim needs to run on the cloud side BEFORE the push, against files staged for commit.

Fallback option: if cloud access to this script is impractical, KimiClaw can stamp manually by editing frontmatter inline using the exact entry shape — but the deduplication becomes a human responsibility.

```bash
# Cloud-side pre-commit hook (preferred)
for f in $(git diff --cached --name-only | grep '\.md$'); do
  python3 .claude/hooks/agent-id-stamp.py \
    --file "$(pwd)/$f" --agent kimiclaw --session "${KIMICLAW_SESSION:0:8}"
done
```

**Tracking task:** `claude/tasks/active/custody-shim-kimiclaw.md`.

### PT (Neo) — local Gemini CLI runtime

**Integration point:** Gemini CLI has a different hook surface than Claude Code, but supports post-tool-call shell commands in its settings. Wire the stamp there.

```bash
# PT post-edit shim
python3 /Users/jack.reis/Documents/=notes/.claude/hooks/agent-id-stamp.py \
  --file "$GEMINI_EDITED_FILE" --agent pt --session "${PT_SESSION:0:8}"
```

**Tracking task:** `claude/tasks/active/custody-shim-pt.md`.

### Codex — standalone OpenAI Codex client

**Integration point:** Codex CLI has a `--post-edit` hook surface. Shim there.

```bash
python3 /Users/jack.reis/Documents/=notes/.claude/hooks/agent-id-stamp.py \
  --file "$EDITED" --agent codex --session "${CODEX_SESSION:0:8}"
```

**Tracking task:** `claude/tasks/active/custody-shim-codex.md`.

## Verification protocol

Each runtime's rollout lands in production when:

1. **Runtime edits a vault `.md`** with frontmatter — pick a low-stakes target (e.g., a scratch file under `.worktrees/`).
2. **`git diff`** on the file shows BOTH:
   - `last_touched_by: "<agent> (<short-session>)"` updated
   - New `touch_history:` entry with matching `(<agent>, <short-session>)` suffix
3. **Run stamp again in-session** — file should be idempotent (no new history entry due to dedupe).
4. **Run from a different session** — new history entry appended (dedupe only fires for consecutive same-session edits).
5. **Cross-runtime verification** — have two runtimes touch the same file back-to-back. Both entries should appear in `touch_history`.

Post-verification, move the tracking task from `claude/tasks/active/` to `claude/tasks/closed/` with `status: completed` and a `completion_summary` citing the verified commit hash.

## References

- Stamp script: `/Users/jack.reis/Documents/=notes/.claude/hooks/agent-id-stamp.py` (commit `a47321c48` added multi-runtime support)
- Tests: `/Users/jack.reis/Documents/=notes/tests/scripts/test_agent_id_stamp.py` (9/9 passing)
- Convention SoT: `docs/conventions/agent-custody-provenance.md` §5
- Fleet runtime/surface mapping: `docs/architecture/fleet-architecture-guidelines.md` §2

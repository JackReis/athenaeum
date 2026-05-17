---
name: ledger-lifecycle
description: Track agent work across tokens, time, and commits. Rotate, rollup, query, and project cost. Use when an agent needs to log their output, track fleet productivity, or audit session costs. Triggers — "log my tokens", "track time", "rotate ledger", "project cost", "query commits".
---

# Ledger Lifecycle

Track what agents do, how long it takes, and what it costs.

## Ledgers

| Ledger | Tracks | Format |
|---|---|---|
| `token` | Tokens in/out, model, cost | Markdown with YAML frontmatter |
| `time` | Duration, category, task | Markdown with YAML frontmatter |
| `commit` | SHA, files changed, deliverable | Markdown with YAML frontmatter |

## Quick start

```bash
# Log a token entry
python3 ledger.py append token --agent kimi --model kimi-k2 --data '{"tokens_in": 16000, "tokens_out": 316, "task": "context review"}'

# Log time
python3 ledger.py append time --agent claude --data '{"duration": "01:30", "category": "design", "task": "arbiter mascot"}'

# Auto-populate commit log
python3 ledger.py append-commit --repo /path/to/repo --count 10

# Check status
python3 ledger.py status

# Rotate old entries to archive
python3 ledger.py rotate token

# Rollup into weekly summary
python3 ledger.py rollup token --period weekly

# Query by agent
python3 ledger.py query token --agent kimi --from-date 2026-05-01

# Project cost from recent usage
python3 ledger.py project-cost --days 7
```

## Environment

| Variable | Default | Description |
|---|---|---|
| `LEDGER_TRACKING_ROOT` | `~/tracking` | Where ledgers live |
| `LEDGER_MAX_LINES` | `500` | Rotation threshold |
| `LEDGER_ROTATE_DAYS` | `30` | Entries older than this get archived |
| `AGENT_NAME` | `$USER` | Default agent name |
| `AGENT_MODEL` | `unknown` | Default model name |
| `LEDGER_SESSION_ID` | `""` | Session identifier |

## Files

- `token-ledger.md` — token usage per session
- `time-ledger.md` — time spent per task
- `commit-log.md` — commits per deliverable
- `archive/` — rotated entries by month
- `rollups/` — weekly/monthly aggregations

## Cost projection

Built-in pricing for common models:

| Model | Input / 1M | Output / 1M |
|---|---|---|
| claude-sonnet-4 | $3.00 | $15.00 |
| claude-opus-4 | $15.00 | $75.00 |
| gpt-4o | $2.50 | $10.00 |
| gpt-4.1 | $2.00 | $8.00 |
| o3 | $2.00 | $8.00 |
| o4-mini | $1.10 | $4.40 |
| gemini-2.5-pro | $1.25 | $10.00 |
| glm-5.1 | $0.50 | $2.00 |
| kimi-k2 | $0.60 | $2.40 |

Add new models by updating `MODEL_PRICING` in `ledger.py`.

## Integration with Athenaeum

The ledger is the measurement layer for the Fleet Directive:

> Done = artifact + path + verification + commit + push + caveats.

After a ratify or audit session, append the results:

```bash
python3 ledger.py append token --agent $(athenaeum agent-detect) --data '{"tokens_in": 50000, "tokens_out": 12000, "task": "athenaeum-a2a-ratify"}'
```

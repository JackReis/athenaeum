---
title: "OB1 Personalization — Load at Every Session"
decay: enduring
created: 2026-06-05
updated: 2026-06-05
ratified_by: Jack Reis
ratified_at: 2026-06-05 ~15:50 CDT
type: convention
status: active
author: honcho (Hermes) session
session: honcho-2026-06-05-ob1-personalization-setup
related:
  - "[[.hermes/plans/2026-06-05-ob1-personalization-setup.md|Setup plan]]"
  - "[[~/.hermes/skills/note-taking/ob1-lifecycle/SKILL.md|ob1-lifecycle skill]]"
  - "[[~/.hermes/skills/note-taking/memory-sop/SKILL.md|triple-layer memory SOP]]"
  - "[[claude/mcp-coordination/state/session-handoffs/session-honcho-ob1-personalization-setup-20260605|This session's handoff]]"
tags: [ob1, personalization, supabase, open-brain, brain, memory, session-start, primary-goal]
---

# OB1 Personalization — Load at Every Session

> **The rule:** every session in this fleet begins by loading
> **Personalization** thoughts from **OB1** (Open Brain 1, the
> Supabase-hosted external semantic brain) and treating them as
> the primary source of truth for the user's identity, preferences,
> environment, and routing rules. L1 (`~/.hermes/memories/MEMORY.md`)
> and L3 (`HERMES-MEMORY.md`) are downstream caches that rehydrate
> from OB1 at session start.
>
> **Ratified:** 2026-06-05 by Jack Reis as the primary goal for the
> next session. **Why:** L1 has a 2,200-char hard budget and drifts
> under parallel-session write pressure; L3 is vault-local and
> requires a path-discovery step before it can be used. OB1 is
> external, has a known endpoint, and survives L1 churn.

---

## 1. What "Personalization" means in this context

**Personalization** is the user-equivalent of the L1 runtime cache: short, declarative facts about the user (Jack Reis), the working environment, the communication style, the agent routing rules, and the durable preferences that every session needs to honor.

**It is NOT:**
- Project-level facts (those belong in L3, the vault-local `HERMES-MEMORY.md`).
- Tool quirks or skill-version details (those belong in skill files).
- Audit deltas, PR numbers, commit SHAs, PIDs (those belong in daily notes or handoffs).

**Examples of Personalization:**
- "User prefers the agent use available local delegation (Ollama, Kimi, Codex) rather than doing all the work in the primary session."
- "Conduit Matrix homeserver runs at `localhost:6167` (NOT 8008); the `fleet-matrix call` command takes the homeserver flag AFTER the subcommand."
- "Telegram DM chat id for delivery updates: `7618822262`."
- "User values cold restart / reboot resilience — audit + hardening, not docs. Fix > document."
- "Honcho is the session name, not a model. Per Jack's rule, anything not using anthropic models isn't claude."

**Currently in L1** (the existing Personalization surface): 8 sections, ~2,211 chars as of 2026-06-05. **Currently in OB1**: 0 Personalization thoughts. **The gap is the gap.**

---

## 2. The 3 surfaces (L1, L3, OB1) and what each is for

Per the `memory-sop` skill (v1.4.0, updated 2026-06-04):

| Layer | Tool | Backend | Personalization lives here now? | Should be? |
|---|---|---|---|---|
| **L1** | `memory` | `~/.hermes/memories/MEMORY.md` | Yes (runtime-injected cache) | **Mirror**, not primary. Prone to drift under parallel-session writes. |
| **L3 (OBn)** | `write_file` | `=notes/claude/memory/HERMES-MEMORY.md` | Yes (project-level facts mixed with Personalization) | **Mirror**, not primary. Vault-local; requires path discovery. |
| **OB1** | `ob1-pull` / MCP | Supabase semantic store | **No** | **Primary** — external, durable, semantically searchable, survives L1 churn. |

**The rehydration loop** (new standard, ratified 2026-06-05):
1. Session starts → load OB1 Personalization (primary)
2. L1 auto-injection loads L1 (mirror, may be stale)
3. L3 file is read for project-level facts (separate concern)
4. Discrepancies: OB1 wins, L1/L3 are updated to match
5. New facts discovered during session: written to OB1 (with task_id namespace), then mirrored to L1 (if it survives the 2,200 budget) and L3 (if project-level)

---

## 3. OB1 surface — what to know before wiring

### Endpoint + auth
- **URL**: `https://jhpuctiyosazlyrcnfuu.supabase.co/functions/v1/open-brain-mcp`
- **Auth**: `x-brain-key` header, value from `BRAIN_KEY` env var (NOT `OB1_ACCESS_KEY` — that's a leftover name from the script, harmonize to `BRAIN_KEY`).
- **Protocol**: JSON-RPC 2.0 over Server-Sent Events (SSE).
- **Namespace**: `task_id` is the routing key; `source` is the bot identity. Use `task_id=hermes/personalization-jack` (and similar) for Personalization thoughts.

### Available MCP tools
- `search_thoughts(query, limit, threshold, task_id, source)` — semantic search.
- `list_thoughts(limit, source, type, topic, days)` — recent captures, filterable.
- `capture_thought(content, task_id, source)` — write a new thought (embedding + metadata generated automatically).
- `thought_stats()` — summary counts.

### CLI wrapper
- `python3 ~/Documents/=notes/bin/ob1-pull --query "personalization jack" --limit 10` — semantic search
- `python3 ~/Documents/=notes/bin/ob1-pull --recent --limit 5` — list recent
- `python3 ~/Documents/=notes/bin/ob1-pull --output /path/to/file` — write to file
- **Read-only.** For writes, use the MCP `capture_thought` endpoint directly (or add `--capture` to the script — a recommended follow-up).

### BRAIN_KEY state
- **Stored in**: `~/.secrets/codex-runtime.env` line 1, as `export BRAIN_KEY=ENC[AES256_GCM,...]` (SOPS-encrypted, age-key).
- **Current session env**: NOT set (`echo $BRAIN_KEY` is empty).
- **Decryption**: requires the age private key in the agent's keyring OR a `sops -d` invocation.
- **No `ob1-token.sh` script exists** (the contextforge-token.sh pattern is not yet replicated for OB1).

---

## 4. The 4 things that need to happen (in order)

### 4.1 — Decrypt + export BRAIN_KEY into the session env

Create `~/.hermes/bin/ob1-token.sh` (mirror of `~/.hermes/bin/contextforge-token.sh`):

```bash
#!/usr/bin/env bash
# ob1-token.sh — OB1 / Open Brain 1 token management
# Author: Hermes, 2026-06-05
set -euo pipefail

cmd_show() {
  sops --decrypt /Users/jack.reis/.secrets/codex-runtime.env 2>/dev/null \
    | grep -E '^export BRAIN_KEY=' \
    | sed 's/^export BRAIN_KEY=//' \
    | sed 's/^"//;s/"$//'
}

cmd_export() {
  export BRAIN_KEY=$(cmd_show)
  echo "BRAIN_KEY exported (length: ${#BRAIN_KEY})"
}

case "${1:-show}" in
  show) cmd_show ;;
  export) cmd_export ;;
  *) echo "Usage: $0 {show|export}" ;;
esac
```

Then `eval $(~/.hermes/bin/ob1-token.sh export)` makes BRAIN_KEY available in the current shell.

**Harmonize the env var name** between script (`OB1_ACCESS_KEY`) and skill (`BRAIN_KEY`). I'll standardize on `BRAIN_KEY` (the skill's name is more recent and more general). Patch `bin/ob1-pull` to fall back: `os.environ.get("BRAIN_KEY") or os.environ["OB1_ACCESS_KEY"]`.

### 4.2 — Capture ~50-80 Personalization thoughts to OB1

For each candidate fact (drawn from L1 sections + L3 user-relevant entries), run:

```python
# Via MCP or curl to the endpoint
capture_thought(
  content="User prefers the agent use available local delegation (Ollama, Kimi, Codex) rather than doing all the work in the primary session.",
  task_id="hermes/personalization-preferences",
  source="hermes"
)
```

**Group by `task_id`** so retrieval is filterable:
- `hermes/personalization-jack` — user identity (name, role, location, communication style)
- `hermes/personalization-preferences` — preferences (look-don't-touch, cold-restart resilience, etc.)
- `hermes/personalization-environment` — environment facts (Conduit :6167, n8n lockout, etc.)
- `hermes/personalization-fleet-routing` — agent routing (Conduit, Telegram, Matrix, OpenClaw)
- `hermes/personalization-procedural` — how the user wants work done (honcho as conductor, dry-run mode, option walk)

### 4.3 — Wire OB1 Personalization into the session-start ritual

Add a step to the `using-superpowers` skill (or a new `ob1-personalization-load` skill):

```bash
# In the session-start hook or the auto-brief step 4 (after OBn read):
if [ -n "$BRAIN_KEY" ]; then
  echo "## OB1 Personalization"
  python3 ~/Documents/=notes/bin/ob1-pull --query "personalization jack" --limit 15
else
  echo "## OB1 Personalization: SKIPPED (BRAIN_KEY not in env; see ~/.hermes/bin/ob1-token.sh)"
fi
```

The output becomes the **OB1 Personalization briefing block** at session start, parallel to the L1 auto-injection and the L3 daily-note read.

### 4.4 — Update the auto-drain ritual

When a session ends, **write new Personalization thoughts to OB1 (with the right task_id) before L1/L3 mirrors.** This keeps OB1 as the source of truth.

```bash
# In the auto-drain step:
# 1. New session-end thoughts go to OB1 first
capture_thought(
  content="[new fact learned this session]",
  task_id="hermes/personalization-...",
  source="hermes"
)
# 2. Then mirror to L1 (if it survives the 2,200 budget) and L3 (if project-level)
```

---

## 5. What to capture (initial seed list)

**From L1 sections** (8 sections, ~50-80 facts when expanded):
1. OBn/L1 dual-write rule (where context lives)
2. Cold-restart / reboot resilience preference
3. Fleet comms surface (Conduit Matrix :6167, telegram/matrix-first)
4. Triple-layer memory hygiene
5. n8n lockout recovery
6. Look-don't-touch pattern
7. Fleet-audit 2026-06-05
8. Daily-note session-format directive (2026-06-05)

**From L3 entries** (project-level + user-preference): name, role, location, communication style, agent routing, harness convention ("the harness is hermes"), the `harness-and-model-attribution` discipline, the `using-superpowers` standard, the architecture alignment, the regroup state, the OB1 goal.

**Total target: 50-80 thoughts initially, growing by 1-5 per session.**

---

## 6. Verifier (re-runnable, post-install)

```bash
# 1. BRAIN_KEY available in current session
test -n "$BRAIN_KEY" && echo "✓ BRAIN_KEY set" || echo "✗ BRAIN_KEY not set"

# 2. OB1 endpoint reachable
curl -sS -X POST https://jhpuctiyosazlyrcnfuu.supabase.co/functions/v1/open-brain-mcp \
  -H "Content-Type: application/json" \
  -H "x-brain-key: $BRAIN_KEY" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"thought_stats","arguments":{}}}' \
  --max-time 15

# 3. ob1-token.sh script exists
ls -la ~/.hermes/bin/ob1-token.sh

# 4. ob1-pull works
python3 =notes/bin/ob1-pull --recent --limit 5

# 5. Personalization thoughts exist
python3 =notes/bin/ob1-pull --query "personalization jack" --limit 10

# 6. Session-start wiring present
grep -A 1 "OB1 Personalization" ~/.hermes/skills/note-taking/using-superpowers/SKILL.md
```

If any check fails, the install is incomplete. Patch the failing surface.

---

## 7. The personalization thought taxonomy (recommended `task_id` schema)

| `task_id` | What it holds | Example |
|---|---|---|
| `hermes/personalization-jack` | User identity | "Jack Reis, he/him, Ardmore OK, recovering from rib surgery" |
| `hermes/personalization-preferences` | User preferences | "Fix > document. Cold-restart resilience over docs." |
| `hermes/personalization-environment` | Environment facts | "Conduit Matrix at :6167 (NOT 8008). n8n lockout: N8N_USER_MANAGEMENT_DISABLED=true." |
| `hermes/personalization-fleet-routing` | Agent routing | "Telegram DM chat id: 7618822262. Conduit for fleet comms. Dashboard TUI = source of truth for liveness." |
| `hermes/personalization-procedural` | How user wants work done | "Honcho = conductor, not solo agent. Look-don't-touch is a real mode. Option walk + falsifier + recommendation, not commits." |
| `hermes/personalization-meta` | Conventions about this Personalization system | "OB1 is primary; L1 + L3 are mirrors. Rehydrate from OB1 at session start." |

**Don't use**:
- `hermes/durable` — that's for general session-end durable facts, not Personalization.
- `hermes/correction` — that's for user corrections (high priority), promoted to a separate namespace.
- `hermes/environment` — that's for fleet infrastructure (hosts, ports), not user Personalization.

---

## 8. Caveats and open questions

1. **BRAIN_KEY in `codex-runtime.env` is shared across all sessions.** If we wire OB1 into the session-start ritual, every session reads the same key. That's fine for read-mostly traffic (search, list) but `capture_thought` writes need a `source: hermes` namespace to avoid collisions. Use distinct `task_id` per Personalization category.

2. **OB1 is the canonical source of truth, but L1 + L3 will drift** unless we either (a) regenerate L1/L3 from OB1 at session start, or (b) accept that L1/L3 are snapshots and OB1 is live. Pick (b) for now — simpler, fewer race conditions.

3. **The user said "loaded at every session"** — does that mean loaded in the *system prompt* (like L1), or loaded in the *first agent turn as a query*? I read it as the latter: the agent's first action in a new session is to `ob1-pull --query "personalization jack"` and read the output. The output then becomes part of the agent's reasoning context. **Confirm with Jack before wiring.**

4. **OB1 captures can fail silently** if the SSE response is malformed. The `ob1-pull --recent` round-trip after a capture is the canonical verifier.

5. **The skill environment-variable name conflict** (script: `OB1_ACCESS_KEY`, skill: `BRAIN_KEY`) is a real bug. Harmonize to `BRAIN_KEY`; patch the script to fall back to the old name for backward compatibility.

6. **No "personalization" tag or topic exists in OB1 yet.** The first 50-80 captures will create the namespace. Future captures can be filtered by `task_id=hermes/personalization-*` for topic-specific retrieval.

7. **The "Personalization" naming** mirrors the LLM-provider's term (e.g., ChatGPT's "Memory" feature, Claude's "Personalization"). It's not a new layer in the SOP — it's a content category that lives in the existing OB1 layer.

---

## 9. Related skills and references

- `~/.hermes/skills/note-taking/ob1-lifecycle/SKILL.md` — the OB1 auto-brief + auto-drain pattern (v1.2.0)
- `~/.hermes/skills/note-taking/ob1-lifecycle/references/ob1-mcp-api.md` — the verified endpoint, auth, tool schemas
- `~/.hermes/skills/note-taking/memory-sop/SKILL.md` — the triple-layer memory SOP (v1.4.0)
- `~/.hermes/bin/contextforge-token.sh` — the pattern to mirror for `ob1-token.sh`
- `=notes/.hermes/plans/2026-06-05-ob1-personalization-setup.md` — the setup plan
- `=notes/.hermes/plans/2026-04-11-ob1-as-data-layer-and-scheduled-briefs-repair-plan.md` — the prior canonical architecture (not yet fully built)

---

*Last updated: 2026-06-05 15:50 CDT by honcho (OB1 Personalization setup session).*

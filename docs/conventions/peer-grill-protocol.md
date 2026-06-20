---
status: stable
authored_by: claude-code
last_touched_by: "claude-code (peer-grill-tipi-boundary)"
authored_at: 2026-05-03
related: [agent-custody-provenance, agent-observer-principle, session-coding]
touch_history:
  - "2026-05-03T10:29Z claude-code (48e4f684)"
  - "2026-05-09T claude-code (peer-grill-tipi-boundary) — added Tipi's role (orchestrator-only) section + API-direct runtime path"
---

# peer-grill protocol

Strict file-only, symmetric multi-agent reconciliation. Two or more agents — Claude sessions, other LLMs, mixed runtimes, or humans — converge on a shared model of project state by:

1. Independently dumping their model to `<agent>.claims.yaml`
2. Computing a three-bucket diff (agreed / disagreed / only-one-knows)
3. Grilling each other in an append-only `grill-log.md` until convergence or escalation
4. Both writing `RATIFY: <claim-id>` markers per converged claim
5. Writing `state.merged.yaml` only after dual ratification
6. Sha256 sign-off — divergent hashes mean the protocol failed and must be re-run

**Working dir:** `.peer-grill/<topic>/` at repo root.

**Skill implementation:** `~/.claude/skills/peer-grill/SKILL.md` (fleet-wide, user-level, not vault-specific).

**Reference fixture:** [`.peer-grill/matrix-mcp-shim-path/`](../../.peer-grill/matrix-mcp-shim-path/) — real reconciliation between two Claude sessions on 2026-05-03.

**Why file-only (not bridge-integrated):** The protocol must work across heterogeneous runtimes (Claude, Hermes, Zoe, KimiClaw, PT/Gemini CLI, humans). Coupling to `hermes-bridge` or `openclaw-bridge` would break BYOM. If you need to wake a peer, do that as a SEPARATE step before invoking the protocol.

**Tipi's role (orchestrator-only):** Tipi is a view, never a source — see [`tipi/contract/agent-contract.md`](../../../tipi/tipi/contract/agent-contract.md) §"Prime directive". For peer-grill specifically:

- Tipi MAY orchestrate the wake-up signal, the shared room (Matrix), the dropbox path agreement, and serve the canonical protocol text as a read-only MCP resource.
- Tipi NEVER spawns runtimes for peer-grill, NEVER injects the protocol into a runtime's context, NEVER writes any file inside `.peer-grill/<topic>/`.
- Runtimes carry their own protocol knowledge: Claude Code via the on-disk skill at `~/.claude/skills/peer-grill/`; API-direct runtimes (OpenClaw / Hermes / KimiClaw / PT) via system-prompt baking that references this convention doc as the canonical source. The skill ships [`templates/system-prompt-for-non-claude-peer.md`](../../../.claude/skills/peer-grill/templates/system-prompt-for-non-claude-peer.md) for the API-direct case.

If tipi were to spawn-and-inject, that would (a) violate the "tipi is a view" invariant, (b) couple the protocol to one orchestrator, breaking BYOM heterogeneity, and (c) make tipi a process supervisor — a scope expansion nothing else in the fleet treats it as.

**Relationship to [Observer Principle](agent-observer-principle.md):** peer-grill is the explicit cross-agent verification protocol. Each peer is the other's downstream observer; ratification = mutual measurement.

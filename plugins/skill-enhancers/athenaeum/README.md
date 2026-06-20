# Athenaeum

A dialectic skill pack for agent design, multi-agent reconciliation, and fleet-wide attestation.

> *"An unexamined claim does not exist."*

## Install

```bash
npx skills add athenaeum-org/dancer@athenaeum-design
npx skills add athenaeum-org/dancer@athenaeum-reconcile
npx skills add athenaeum-org/dancer@athenaeum-ratify
```

Or clone and symlink into your agent's `skills/` directory.

## Four skills, one lineage

| Skill | Purpose | When to use |
|---|---|---|
| `athenaeum-design`  | Rigorous design grilling                          | Designing agents, architectures, plans |
| `athenaeum-reconcile`| Multi-agent state reconciliation                   | Two+ agents disagree; triangulate across models |
| `athenaeum-ratify`  | Fleet attestation with dissent recording          | N agents must sign off on an immutable artifact |
| `athenaeum-audit`   | Code-aware agent-stack audit + reconcile in one pass | Reviewing existing architecture; triangulate understanding |

## Quick decision tree

```
Who is debating?
├── Just you + one agent → athenaeum-design
├── Two+ agents disagree → athenaeum-reconcile
│   └── Low stakes? → quick mode (no crypto)
│   └── High stakes? → formal mode (SHA-256 sign-offs)
├── Review existing stack → athenaeum-audit
└── Whole fleet must approve → athenaeum-ratify
    └── Unanimous? → ratified
    └── Dissent? → decomposed to human grain-gate
```

## Bootstrap

Each skill includes a unified CLI:

```bash
# Add scripts/ to PATH, then:
athenaeum init my-topic --mode design
athenaeum init my-topic --mode reconcile
athenaeum init my-topic --mode ratify --roster agent-alpha,agent-beta,agent-gamma
athenaeum init my-topic --mode audit

```

## Framework Name

This repo surface is `Athenaeum` (the plugin pack), but the public framework shorthand is **lowercase `rbitr`** to avoid collisions with a separate Clawhub `Arbiter` skill and potential Kimi naming conflicts. Historical references to `Arbiter` in prose should be read as `rbitr`.

## Unified CLI commands

```bash
athenaeum diff my-topic
athenaeum sign my-topic
athenaeum check          # find ratifications awaiting your vote
```

## Philosophy

- **Progressive disclosure** — SKILL.md is the quick-start (<100 lines). REFERENCE.md is the deep protocol. Agents load the quick-start; read the deep docs only when executing.
- **Mode selection** — Not every reconciliation needs cryptographic proof. `quick` mode handles the common case; `formal` mode handles cross-machine, cross-model stakes.
- **Code-anchored** — Claims cite file paths and line ranges. The repo wins; agent recollection does not.
- **Cross-agent** — Works in Claude Code, Kimi, Codex, Gemini, OpenHands, or human-driven sessions. Auto-detects runtime or falls back to env vars.

## Structure

```
athenaeum/
├── athenaeum-design/SKILL.md
├── athenaeum-reconcile/SKILL.md
├── athenaeum-ratify/SKILL.md
├── athenaeum-audit/SKILL.md
├── REFERENCE.md           # Deep protocol for all four
├── scripts/
│   └── athenaeum          # Unified bootstrap CLI
└── templates/
    ├── audit/
    ├── design/
    ├── reconcile/
    └── ratify/
```

## Roadmap / open questions

- [ ] Package for `npx skills add`
- [ ] Star-topology multi-peer reconciliation (currently pairwise chains only)
- [ ] Auto-discovery of fleet roster from `~/Documents/Coordination/` or env var

# Arbiter

> A2A-native agent consensus framework — 5 packs, 26 skills, zero inherited bloat.

[![Skills](https://img.shields.io/badge/skills-26-blue)](plugins/)
[![Packs](https://img.shields.io/badge/packs-5-green)](plugins/)
[![2025 Schema](https://img.shields.io/badge/2025%20Schema-100%25-success)](SKILLS_SCHEMA_2025.md)

**Arbiter** is an A2A-native agent consensus framework delivered as a curated collection of Claude Code skill packs. Agents design, reconcile, ratify, and audit — with filesystem durability as the floor and JSON-RPC/SSE as the live wire.

Originally derived from an MIT-licensed upstream, inherited plugins were removed on 2026-05-16. Arbiter now ships only original contributions.

---

## Plugin Packs

| Pack | Category | Skills | Description |
|---|---|---|---|
| `autonomous-ai-agents` v0.4.0 | ai-agency | 3 + 2 MCP bridges | Fleet coordination: identity, hermes-bridge, openclaw-bridge |
| `grill-each-other` v1.3.1 | skill-enhancers | 10 | Dialectic claim discipline: grill-me, peer-grill, fleet-ratify, permutation, etc. |
| `athenaeum` v0.2.0 | skill-enhancers | 4 | Streamlined dialectic: design, reconcile, ratify, audit |
| `leonardo` v1.1.0 | ai-agency | 1 | Protected-string decoder with audit trail |
| `pocock-engineering` v1.0.0 | skill-enhancers | 8 | SDLC skills forked from Matt Pocock's framework |

---

## Skills by Pack

### autonomous-ai-agents (3 skills + 2 MCP bridges)

| Skill | What it does |
|---|---|
| `agent-identity` | Declares who an agent is — name, role, capabilities, boundaries |
| `hermes-bridge` | MCP bridge to Hermes messaging relay |
| `openclaw-bridge` | MCP bridge to OpenClaw dispatch system |

### grill-each-other (10 skills)

| Skill | What it does |
|---|---|
| `grill-me` | Interview the user about a plan until shared understanding |
| `grill-me-agents` | Grill multi-agent designs — roles, handoffs, failure modes |
| `grill-me-with-agents` | Code-aware variant that cross-references existing agent definitions |
| `grill-with-docs` | Grill against domain model and documented decisions |
| `peer-grill` | Two agents interrogate each other to converge on shared state |
| `agent-show-and-tell` | Agents write status reports; one reader collates a roundup |
| `fleet-ratify` | Ratify fleet decisions with SHA-256 attestation |
| `permutation` | NxN fleet topology ratification with visual diagrams |
| `caveman` | Ultra-compressed communication mode (75% token reduction) |
| `find-skills` | Discover and install agent skills |

### athenaeum (4 skills)

| Skill | What it does |
|---|---|
| `design` | Propose a design claim for peer review |
| `reconcile` | Resolve conflicting claims into a merged design |
| `ratify` | Sign off on a finalized design with attestation |
| `audit` | 13-branch audit protocol with confidence rules |

### leonardo (1 skill)

| Skill | What it does |
|---|---|
| `protected-string-decoder` | Decode protected strings with audit trail |

### pocock-engineering (8 skills)

| Skill | What it does |
|---|---|
| `zoom-out` | Step back for broader architectural context |
| `diagnose` | Reproduce → minimize → hypothesize → instrument → fix → regression-test |
| `triage` | State-machine issue triage with role-based workflows |
| `tdd` | Test-driven development with red-green-refactor |
| `to-issues` | Break plans into tracer-bullet vertical-slice issues |
| `to-prd` | Turn conversation context into a PRD on the issue tracker |
| `improve-codebase-architecture` | Find refactoring opportunities informed by domain language |
| `setup-matt-pocock-skills` | Bootstrap AGENTS.md with issue tracker, triage labels, domain docs |

---

## Install

```bash
# Install a pack
/plugin install grill-each-other@arbiter
/plugin install athenaeum@arbiter
```

Or install individual skills by copying `skills/<name>/SKILL.md` into your own project.

---

## Architecture

All skills follow the **2025 schema** — `name` + `description` as the portable minimum, with `allowed-tools`, `version`, and package manifests as optional adapter fields.

See [AGENTS.md](AGENTS.md) for the full developer guide, schema details, and GitNexus integration.

---

## A2A Native

<p align="center">
  <img src="docs/assets/arbiter-council-light.jpg" alt="Arbiter — robot council in the pantheon" width="420">
</p>

Arbiter speaks the [Agent-to-Agent Protocol](https://github.com/google/A2A) natively:

- **Agent Cards** — `agent_card.py` generates capability descriptors with Athenaeum extensions
- **A2A Tasks** — `a2a_task.py` serializes design/reconcile/ratify/audit workflows to JSON
- **JSON-RPC endpoint** — `tasks/send`, `tasks/get`, `tasks/cancel` on port 18765
- **SSE streaming** — `tasks/sendSubscribe` pushes live task updates until terminal state
- **Filesystem floor** — `athenaeum poll <topic>` for zero-server async status checks

A2A is **opt-in**. Default mode is filesystem-only:

```bash
athenaeum init my-topic --mode design              # filesystem only
athenaeum init my-topic --mode design --transport a2a  # + A2A Task
```

## Fleet Directive

All agents working in this repo follow the **Fleet Directive — Durable Evidence**:

> Done = artifact + path + verification + commit + push + caveats.

---

## License

Each pack carries its own LICENSE. Original contributions: MIT. Pocock-derived packs: MIT (original copyright Matt Pocock). See [NOTICE](NOTICE) for attribution.

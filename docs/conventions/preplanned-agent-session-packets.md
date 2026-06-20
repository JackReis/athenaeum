---
decay: evolving
title: Preplanned Agent Session Packets
status: proposed
created: 2026-06-03
tags:
  - conventions
  - agentic-os
  - coordination
  - session-planning
  - nate-jones
related:
  - "[[docs/conventions/fleet-directive]]"
  - "[[docs/conventions/multi-session-working-agreements]]"
  - "[[docs/architecture/fleet-architecture-guidelines]]"
  - "[[docs/architecture/inter-session-protocol-v2]]"
ledger:
  beads: notes-9icu
---

# Preplanned Agent Session Packets

## Thesis

Context-rescue is a recovery tool, not the operating model.

For high-context fleet work, the default should be a short preplanned session packet: define the work, route the model/runtime, order the dependencies, bound the turn count, and give subagents small scopes that can finish before the parent session starts failing.

This is the practical lesson from Nate's advice in the Executive Circle thread: plan ahead and go slower to go faster.

## Rule

Any session that touches fleet architecture, gateways, orchestration, memory, identity, or multi-repo coordination should start from a packet before execution.

Do not begin with "figure it out live" unless the task is explicitly a diagnosis. Even then, stop after the diagnosis and write a packet before broad repair.

## Turn Budget

- Target session size: 10 to 12 meaningful turns.
- Warning threshold: turn 8.
- Split threshold: turn 12.
- Rescue threshold: turn 15 is a failure signal, not a planning target.

If a session needs more than 12 turns, split the work into child packets before continuing.

## Packet Schema

Every packet should include:

| Field | Required content |
|---|---|
| Intent | One sentence naming the work and why it matters. |
| Ledger | Linear issue and Beads id, or `not yet created` with reason. |
| Source context | Exact files, repos, tickets, logs, or messages to read first. |
| Exclusions | What is explicitly out of scope. |
| Model/runtime route | Which actor runs each phase and why. |
| Dependency order | What must happen before what. |
| Turn budget | Parent turn max and child turn max. |
| Subagent packets | One packet per child agent; no vague "go research" prompts. |
| Tools/sinew | Which routes matter: ContextForge, Bifrost, Cortex, Uptime Kuma, n8n, rbitr, RepoWeaver, Telegram, WhatsApp, Matrix, or VS Code. |
| Proof target | Artifact, path, verifier, commit/push, caveats. |
| Stop rule | What condition ends or pauses the session. |

## Routing Rules

Use the Agentic OS roles directly:

- Linear and Beads remember the work.
- Dramatis chooses the scene and actor.
- Sinew connects context, tools, health, traces, and proof.
- n8n owns repeatable executable workflows.
- rbitr records, spawns, and traces workers.
- ContextForge and Bifrost expose tool routes.
- Cortex carries working context and personal memory.
- Uptime Kuma observes service health.
- RepoWeaver explains repo topology.
- Direct source inspection and focused tests bound code impact; RepoWeaver may explain repo topology when current.

Transport surfaces are not work owners. Telegram, WhatsApp, Matrix, Discord, Slack, and VS Code are ingress, observation, or cockpit surfaces.

## Memory Routing

Inbound social or chat signal gets classified before action:

| Signal kind | Destination |
|---|---|
| Durable work, decision, or follow-up | Linear + Beads first, then packet. |
| Personal memory or reusable preference | Cortex / personal OB1 lane, with provenance. |
| Runtime-local fact for Hermes | Hermes memory only if it is not a durable work record. |
| Repeatable automation idea | n8n workflow plan, not a chat loop. |
| Fleet architecture implication | Vault doc or ADR candidate plus packet. |

If the same signal fits two lanes, prefer the durable ledger and link the memory note from it.

## Subagent Packet Template

```md
## Child Packet: <short name>

Intent:
Ledger:
Parent packet:
Actor/model:
Inputs:
Allowed files/repos:
Forbidden files/repos:
Tools:
Max turns:
Acceptance criteria:
Verifier:
Return format:
Stop rule:
```

## Parent Session Protocol

1. Create or link the Linear/Beads record.
2. Write the parent packet in the vault or the target repo.
3. Split the work into child packets before launching subagents.
4. Run children in dependency order; parallelize only independent branches.
5. Merge child outputs into one proof path.
6. Commit and push the artifact.
7. Close with durable evidence and caveats.

## Anti-Patterns

- Starting a high-context repair as an unbounded chat.
- Handing off only after the session is already failing.
- Spawning subagents without scoped inputs and acceptance criteria.
- Treating a transport identity as an actor or ledger.
- Writing "continue from here" without an artifact path and verifier.
- Using context-rescue as the normal baton.

## Adoption

Effective immediately for new fleet coordination work. Existing in-flight sessions should not be interrupted solely to retrofit this format, but any new successor handoff should include a packet or link to one.

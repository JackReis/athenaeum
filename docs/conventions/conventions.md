---
obn: sync
last_touched_by: "claude-code (d134b620)"
touch_history:
  - "2026-04-22T19:48Z claude-code (d134b620)"
---

# Conventions

Standards, naming patterns, and operational guidelines for vault content.

> **Master doc:** [[fleet-architecture-guidelines]] — fleet-wide architectural spec that cites this conventions corpus under the Body/Mind/Spirit + Epigenetics spine. Start there if you need the full picture.

> Guidelines: [[atlas/context/project-guidelines-and-symlink-standard|Project Guidelines Standard]] (canonical reference for guideline blocks, paths, and symlinks)

---

## Vault Conventions

- [[fleet-directive|Fleet Directive — Durable Evidence]] — Ratified canonical directive: Done = artifact + path + verification + commit + push + caveats. Applies to all agents. Supersedes prior directive variants.
- [[agent-custody-provenance|Agent Custody & Provenance Convention]] — Commit trailers, retention rules, handoff artifacts, WORK-LEDGER stamps, and `touch_history`
- [[agent-custody-shims|Agent Custody Shims]] — Runtime integration cookbook for the custody stamping pattern
- [[agent-observer-principle|Agent Observer Principle]] — Deep doctrine: you cannot observe yourself and call it measurement
- [[artifact-bound-workflow-recipes|Artifact-Bound Workflow Recipes]] — Recipes for workflows where the outbound message/comment/execution is the artifact; prevents compensating handoffs or daily-note writes after delivery
- [[dialectic-vocabulary|Dialectic Vocabulary]] — Claim discipline vocabulary for grill-me / peer-grill / fleet-ratify
- [[file-naming|File Naming Convention]] — Forward-looking naming standard for new files
- [[session-role-tags|Session Role Tags]] — A-H role codes for session classification
- [[lyt-classification-adapted|LYT Classification (Adapted)]] — 000-900 number system for note categorization
- [[batch-checkpointing|Batch Checkpointing]] — Multi-task commit cadence and progress reporting
- [[chatgpt-dev-mode-policy|ChatGPT Dev Mode Policy]] — History preservation default for ChatGPT sessions
- [[multi-session-working-agreements|Multi-Session Working Agreements]] — 14 rules for safe concurrent-session coordination (narrow commits, handoff discipline, probe-authoring non-delegability, oneshot + blocking-gate pattern, model empathy in loops, etc.)

## Operational Standards

- [[atlas/context/project-guidelines-and-symlink-standard|Project Guidelines & Symlink Standard]] — Required guideline blocks, canonical vs mirror paths, symlink rules
- [[atlas/context/llm-fit-defaults|LLM-Fit Defaults]] — Model routing defaults derived from usage analysis
- [[atlas/context/project-llm-fit-profiles/example-multimodel-profile|Example LLM-Fit Profile (CrawlSpace AI)]] — Per-project routing template

## Architecture Decisions

- [[docs/architecture/ADR-2026-02-28-openclaw-orchestrator-hub-and-spoke|OpenClaw Hub-and-Spoke]] — Coordination architecture
- [[docs/architecture/state-schema|State Schema]] — Worker/task/lock JSON format
- [[docs/architecture/dashboard-strategy|Dashboard Strategy]] — Dashboard data lineage

## Workflows & Protocols

- [[docs/workflows/byom-agent-coordination|BYOM Agent Coordination (Vault-Native)]] — Vault-first shared memory and handoff surface across models
- [[docs/workflows/apple-notes-air-gap|Apple Notes Air-Gap]] — Intentional isolation from AI
- [[docs/workflows/khoj-agent-optimization|Khoj Agent Optimization]] — Semantic search briefing
- [[docs/workflows/notebooklm-extraction-loop|NotebookLM Extraction Loop]] — Knowledge corpus consolidation
- [[docs/workflows/vault-entry-shortcut-spec|Vault Entry Shortcuts]] — Entry points
- [[docs/workflows/vault-cleanup-check-sop|Vault Cleanup SOP]] — Read-only vault audit

## Root-Level References

- `/GIT-HYGIENE.md` — Git commit/push/clean practices
- `/REPOSITORY-MAP.md` — 18-repo portfolio inventory and dependency graph
- `/INFRASTRUCTURE-TASKS.md` — Claude Code infrastructure task backlog

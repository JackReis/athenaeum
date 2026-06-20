---
title: "Fleet Directive — Variant B (POISONED — DO NOT USE)"
created: 2026-05-16
status: poisoned
reason: |
  Two poisoned artifacts identified by Kimi CLI alignment audit:
  1. Handoff-file requirement conflicts with Arbiter Symphony pattern (workers write PRs + proof_of_work, not handoff files in ephemeral worktrees)
  2. Word-ban overreach conflicts with proof_of_work.status: succeeded schema
  See alignment report at Coordination/2026-05-16-fleet-directive-alignment-report.md §4.
canonical_replacement: docs/conventions/fleet-directive.md
---

# ⚠️ POISONED ARTIFACT — DO NOT USE

This variant of the Fleet Directive was found to contain two poisoned artifacts
during alignment audit against AGENT_DESIGN.md (Arbiter orchestration topology).

**Do not follow this directive.** The canonical Fleet Directive is at
`docs/conventions/fleet-directive.md`.

## Poisoned artifacts

### Poison #1 — Handoff-file requirement

Variant B mandates a "Handoff" section in every completion, telling the next
observer where to inspect. This conflicts with the Arbiter Symphony pattern:

- Arbiter workers are **isolated by worktree** and **do not write handoff files**
  (AGENT_DESIGN.md §6: "File-based handoffs as primary coordination (still used
  for human sessions; not for autonomous workers)")
- A handoff file in an ephemeral worktree dies when the worktree is cleaned up
- Workers satisfy evidence via `proof_of_work` schema: `pr_url`, `files_changed`,
  `caveats`, `test_results`, `cost_actual`

### Poison #2 — Word-ban overreach

Variant B bans the words "done, fixed, verified, implemented, committed, pushed,
tests passed, shipped" without evidence. This conflicts with:

- `proof_of_work.status: succeeded` schema (AGENT_DESIGN.md §5) — a worker with
  attached evidence MUST be able to say "tests passed" as part of documenting status
- The observer principle bans *unsubstantiated claims*, not *words* — the
  substance rule, not vocabulary control, distinguishes measurement from theatre

## Replacement

The canonical Fleet Directive is `docs/conventions/fleet-directive.md`, ratified
2026-05-16 via `accept-split` decision with amendments for cost_actual,
dispatch envelope context, CI precedence, and substance-over-vocabulary rule.

---

*Archived with poison warning per ratification decision 2026-05-16. Jack Reis.*
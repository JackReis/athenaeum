---
last_touched_by: "claude-code"
created: 2026-05-29
doc-type: convention
tags: [convention, planning, isa, writing-plans, dialectic]
status: active
---

# Ideal State Artifact (ISA) — Planning Convention

> Adapted from PAI v5.0.0's ISA primitive (Daniel Miessler, MIT-licensed). Verbatim
> source preserved at [[resources/upstream-verbatim/pai-v5.0.0/ISA.md]]. This is the
> **de-PAI'd** distillation: the structure and discipline, none of the runtime coupling.

## Purpose

An **ISA** is a single artifact that is simultaneously the ideal-state articulation, the
test harness (the criteria *are* the tests), the build verification, the done condition,
and the system of record for a thing being built. It replaces the PRD-plus-separate-test-spec
split: no parallel `acceptance.yaml`, no separate done checklist — one document carries all of it.

This convention enriches [`superpowers:writing-plans`](https://github.com/) and operationalizes
the CLAUDE.md preamble ("the unexamined claim is not worth reading") and the
[fleet-directive](fleet-directive.md) Verifier field. It is an **opt-in** structure for E3+
work; it does not replace the writing-plans skill, it sharpens what goes inside a plan.

- **Relationship to [[docs/conventions/dialectic-vocabulary]]:** the Changelog format below
  is the conjecture/refutation/learning loop with a concrete template.
- **Relationship to [`fleet-directive.md`](fleet-directive.md):** every ISC is a Verifier — a
  runnable probe a downstream observer can re-run. "I verified" without a nameable probe is theatre.
- **Relationship to [[feedback_richer_context_deferrals]]:** the Decisions section preserves
  dead ends and refusals so future sessions don't re-explore them ("ledgers let us time travel").

## The twelve sections

Fixed order. Empty sections never appear — a section is present only when its tier requires it
(see Tier gate). The phase column maps loosely to the brainstorm → plan → execute → verify arc.

| # | Section | Purpose | Written during |
|---|---------|---------|----------------|
| 1 | `## Problem` | What is broken or missing right now | brainstorm |
| 2 | `## Vision` | What the euphoric-surprise end state feels like — experiential intent | brainstorm |
| 3 | `## Out of Scope` | Anti-vision — what is *not* included, declared in prose | brainstorm |
| 4 | `## Principles` | Substrate-independent truths the work must respect | brainstorm |
| 5 | `## Constraints` | Immovable architectural mandates | brainstorm |
| 6 | `## Goal` | Hard-to-vary spine — 1–3 sentences naming verifiable done | brainstorm |
| 7 | `## Criteria` | Atomic ISCs (one binary tool probe each), including derived `Anti:` | brainstorm → execute |
| 8 | `## Test Strategy` | Per-ISC verification: `isc \| type \| check \| threshold \| tool` | plan |
| 9 | `## Features` | Work breakdown: `name \| satisfies \| depends_on \| parallelizable` | plan |
| 10 | `## Decisions` | Timestamped decision log (incl. dead ends, `refined:` prefix) | any phase |
| 11 | `## Changelog` | Conjecture / refuted-by / learned / criterion-now entries | verify/learn |
| 12 | `## Verification` | Evidence per ISC (the actual probe output) | verify |

## The four-surface guardrail taxonomy

The four "negative space" sections each bind a *different* surface. Conflating them (especially
Out of Scope vs Anti-criteria) is the classic mistake — they live at different granularities:

| Surface bound | Section | Form | Example |
|---------------|---------|------|---------|
| **Thinking** | Principles | declarative truth | "Scaffolding over model" |
| **Solution space** | Constraints | immovable mandate | "No new MCP servers" |
| **Vision** | Out of Scope | declarative prose | "We are not building multi-tenant SaaS" |
| **Test surface** | Anti-criteria | derived testable probe | "Anti: no secret appears in logs" |

Out of Scope is *declarative* ("we are not building X"); an anti-criterion is the *derived,
tool-verifiable probe* ("X endpoint returns 404"). One Out-of-Scope line may spawn several
anti-criteria, or none.

## The binary-probe ISC rule

> **Split until each criterion is one binary tool probe.** A criterion is granular enough when
> a single tool call (`Read`, `Grep`, `Bash`, `curl`, a screenshot, `SELECT`, `.venv/bin/pytest`)
> returns yes/no on whether it's met. If you cannot name the probe, the criterion is not yet
> atomic — split it. If the criterion needs human judgment, name the tool-verifiable *proxy*
> that stands in for the judgment.

**The Splitting Test** — apply to every criterion as you write it:

| Test | Split when... |
|------|---------------|
| "And" / "With" | Joins two verifiable things |
| Independent failure | Part A can pass while B fails |
| Scope words | "all", "every", "complete" → enumerate |
| Domain boundary | Crosses UI / API / data / logic → one per boundary |
| **No nameable probe** | You can't say which tool would verify it |

**Format:** `- [ ] ISC-N: criterion text`. Two doctrinal kinds are preserved as prose prefixes:

| Kind | Surface form | Rule |
|------|--------------|------|
| **Anti-criterion** — must NOT happen | `- [ ] ISC-N: Anti: <what must NOT happen>` | **≥1 required** |
| **Antecedent** — precondition for a target experience | `- [ ] ISC-N: Antecedent: <precondition>` | **≥1 required when the goal is experiential** |

The grep-based completeness linter `claude/scripts/isa-lint.sh` checks these heuristically.

## ISC ID-stability

ISC IDs are durable handles, not display order. Once assigned:

- **Never renumber on edit.** ISC-7 stays ISC-7 even if ISC-3 is deleted.
- **Splits become `ISC-N.M`.** Splitting ISC-7 yields ISC-7.1, ISC-7.2 — never a reflow.
- **Drops are tombstoned**, not removed: `- [~] ISC-5: (dropped 2026-05-29 — superseded by ISC-7.1)`.

This keeps Verification entries, Changelog references, and cross-session handoffs pointing at
stable targets.

## The conjecture / refutation / learning changelog

The Changelog records how the *understanding* evolved, not what files changed (git already has
that). Each entry is a Deutsch-style conjecture/refutation/learning quad:

```
- 2026-05-29 | conjectured: <the belief you held when you started>
  refuted by: <the evidence or argument that broke it>
  learned: <the durable lesson>
  criterion now: <the ISC added/changed as a result, by ID>
```

Worked example (from the PAI source itself):

```
- 2026-04-28 | conjectured: Out of Scope and anti-criteria are the same concept at different granularities
  refuted by: the distinction was articulated directly — Out of Scope is declarative ("we are not
    building X"), anti-criteria are derived testable probes ("X endpoint returns 404")
  learned: the guardrail taxonomy needs four surfaces — Principles bind thinking, Constraints bind
    solution space, Out of Scope binds vision, Anti-criteria bind test surface
  criterion now: ISC-9 documents the four-surface taxonomy
```

A refuted conjecture is a *first-class artifact* — "Permission to Fail." It belongs in the record
so the next session doesn't re-derive it.

## Tier gate (mapping to /e1–/e5)

Required sections ramp with Jack's effort tiers (`/e1`–`/e5`). A section that isn't required at
the active tier simply doesn't appear. (PAI's numeric ISC floors — "≥16 at E2" etc. — are
intentionally NOT adopted; the granularity rule produces a natural N and
[[feedback_default_high_effort]] governs depth, not a count.)

| Tier | Required sections |
|------|-------------------|
| **/e1** | Goal, Criteria |
| **/e2** | Problem, Goal, Criteria, Test Strategy |
| **/e3** | Problem, Vision, Out of Scope, Constraints, Goal, Criteria, Features, Test Strategy |
| **/e4** | All twelve |
| **/e5** | All twelve + a brainstorming pass before implementation |

Any long-lived `<project>/ISA.md` requires /e3+ structure regardless of the active task's tier —
the project file is the durable source of truth; one transient /e1 task must not downgrade it.

## How to use with `superpowers:writing-plans`

This convention is **opt-in** and does not modify the vendored `superpowers:writing-plans`
skill — that skill still owns the brainstorm → plan → execute → verify arc; the ISA sharpens
what goes *inside* the plan file. For E3+ work:

1. Run `superpowers:writing-plans` as usual to scaffold the plan.
2. Copy [`docs/plans/_templates/isa-plan-template.md`](../plans/_templates/isa-plan-template.md)
   over (or into) the plan file and fill the sections your tier requires (see Tier gate above);
   delete the sections it does not.
3. Apply the binary-probe rule and the Splitting Test to every criterion as you write it.
4. Before the plan is considered ready, run the granularity linter:
   `bash claude/scripts/isa-lint.sh <your-plan>.md` — it flags non-atomic ISCs and hard-fails
   if no `Anti:` criterion exists. The linter is heuristic (grep red-flags), not a parser; treat
   its conjunction warnings as prompts to re-read, not absolutes.
5. During VERIFY, fill the `## Verification` section with the actual probe output per ISC.

The linter is advisory, not a gate — it is not wired into a hook. Run it yourself, or add it to
a plan's own done condition as an ISC (as this series' plans do).

## What we deliberately did NOT take from PAI

The PAI ISA is coupled to a runtime we don't run. These were stripped during the de-PAI surgery
and must never leak back into the spec above:

- **The `localhost:31337` Pulse dashboard probes** — PAI's ISCs `curl localhost:31337`; we have no
  Pulse daemon and don't want a second port-31337 service.
- **The `Skill("ISA", ...)` bun-tool invocations** — PAI calls a TypeScript ISA skill to scaffold/
  append. We use plain Read/Edit/Write and the plan template; no bun runtime.
- **The `MEMORY/WORK/{slug}/ISA.md` path coupling** — PAI hard-codes its memory tree. Our ISAs live
  inside ordinary plan files under `docs/plans/`.
- **`bun run` / "Bun and TypeScript only, never Python" doctrine** — Jack runs Python MCP servers;
  this constraint would break them.
- **PAI's numeric tier ISC floors and the EscalationGate hook** — replaced by the granularity rule
  plus [[feedback_default_high_effort]].

Source: [[resources/upstream-verbatim/pai-v5.0.0/ISA.md]], [[resources/upstream-verbatim/pai-v5.0.0/ALGORITHM-v6.3.0.md]] §"ISC Quality System", [[docs/plans/2026-05-29-pai-steal-isa-plan-template]]

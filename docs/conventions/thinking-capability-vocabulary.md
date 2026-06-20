---
last_touched_by: "claude-code"
created: 2026-05-29
doc-type: convention
version: v1
tags: [convention, thinking, capability, anti-theatre, dialectic, pai]
status: active
---

# Thinking-Capability Vocabulary — Closed Enumeration (Anti-Phantom)

> Adapted from PAI v5.0.0's "Capability-Name Audit Gate" (Daniel Miessler, MIT-licensed).
> Verbatim source excerpt: [[resources/upstream-verbatim/pai-v5.0.0/capability-audit-gate-excerpt.md]].
> This is the **de-PAI'd** distillation — the closed-vocabulary discipline, none of the
> port-31337 classifier dependency, the bun/TS escalation- and prompt-hook runtime, or the
> tier-floor numerics.

## The principle

A claimed *thinking-move* must name a capability from the **closed, versioned list below**.
Inventing a generic label at runtime — "deep reasoning", "structured thinking", "edge-case
enumeration", "tradeoff analysis" — is a **phantom capability**: it is not evidence of thinking,
it does not count toward depth, and it wastes the reader's time. This operationalizes the
CLAUDE.md preamble ("the unexamined claim is not worth reading; theatre wastes the reader's
time") and the [`fleet-directive`](fleet-directive.md) doctrine ("the evidence, not the
vocabulary, is what distinguishes measurement from theatre").

The vocabulary is **closed**: if a name does not appear in the active list verbatim, it is a
phantom. The set of available named moves IS the vocabulary — naming is not free invention.

## The versioning rule

New capabilities are added by **editing this doc and bumping the `version:` line** — never by
ad-hoc invention at run time. A capability earns a place on the *active* list only when it maps
to a real, runnable artifact: a ported skill, a convention doc, or a defined Jack-native move
with a nameable probe. Until then it lives in the **Candidates** appendix. Promotion from
candidate → active is itself a versioned edit.

## Active list (v1)

Each active capability maps to a real artifact you can invoke today.

- **ISA** — Ideal State Artifact planning (criteria *are* the test harness). → [[docs/conventions/ideal-state-artifact.md]] + `docs/plans/_templates/isa-plan-template.md`
- **DialecticVocabulary** — conjecture / refutation / learning framing of claims. → [[docs/conventions/dialectic-vocabulary.md]] + `grill-each-other` pack
- **GrillMe** — solo adversarial self-stress-test of a claim or design. → `dancer/plugins/skill-enhancers/grill-each-other/skills/grill-me`
- **GrillMeAgents** — multi-agent debate with visible transcripts (Council-equivalent). → `dancer/plugins/skill-enhancers/grill-each-other/skills/grill-me-agents`
- **PeerGrill** — strict file-only multi-agent reconciliation (claims → grill-log → RATIFY). → `dancer/plugins/skill-enhancers/grill-each-other/skills/peer-grill`
- **FeedbackMemoryConsult** — grep prior `feedback_*.md` for matching mistakes before acting. → `~/.claude/projects/.../memory/feedback_*.md` (106 entries)
- **ReReadCheck** — final gate: re-read the user's last message verbatim before responding. → CLAUDE.md preamble discipline (native)
- **ContextSearch** — semantic prior-work search across the vault before re-deriving. → OBn (ChromaDB v2) / Khoj vault-expert (native)

## Candidates — not yet adopted

Named moves recognized but **not** on the active list. Do not claim these as thinking-moves
until promoted (each promotion = a `version:` bump when its port lands).

**Pending the `pai-reasoning` pack port (Plan 2):**
- IterativeDepth — multi-angle exploration at Extended+ depth
- FirstPrinciples — physics-style deconstruct / challenge / rebuild
- SystemsThinking — Iceberg, causal loops, Meadows leverage points
- RootCauseAnalysis — 5 Whys, Fishbone, Apollo, Swiss Cheese
- BitterPillEngineering — over-prompting audit

**Pending grill-pack formalization (Plan 3):**
- Council — formal multi-agent debate move (today approximated by GrillMeAgents)
- RedTeam — formal adversarial stress-test move (today approximated by GrillMe / peer-grill)

**Pending the tier-2 reasoning port (Plan 5):**
- ApertureOscillation, Science, BeCreative, Ideate, Evals, WorldThreatModel

**Not adopted (PAI runtime coupling — deliberately excluded):**
- Advisor — PAI's `Inference.ts --mode advisor`; no equivalent runtime here.
- Fabric patterns — PAI's `Skill("Fabric", ...)` bun-tool; not ported.

## Cross-references

- [[docs/conventions/fleet-directive.md]] — anti-theatre doctrine this enforces.
- [[docs/conventions/dialectic-vocabulary.md]] — the conjecture/refutation substrate.
- [[docs/conventions/ideal-state-artifact.md]] — the ISA capability's home.
- `pai-reasoning` pack (Plan 2, dancer) — will supply the bulk of the pending-candidate moves.

Source: [[resources/upstream-verbatim/pai-v5.0.0/capability-audit-gate-excerpt.md]], [[docs/plans/2026-05-29-pai-steal-capability-audit-gate]]

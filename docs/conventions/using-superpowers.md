---
title: "using-superpowers — Session-Start Anchor Standard"
decay: enduring
created: 2026-06-05
updated: 2026-06-05
ratified_by: Jack Reis
ratified_at: 2026-06-05 ~14:30 CDT
type: convention
status: active
author: honcho (claude-code / miniMax-m3:cloud)
session: honcho-2026-06-05-using-superpowers-standard
related:
  - "[[AGENTS.md]]"
  - "[[docs/architecture/queries/2026-06-05-architecture-alignment-decision|Architecture alignment query (2026-06-05)]]"
  - "[[.hermes/plans/2026-06-05-using-superpowers-standard.md|Adoption plan]]"
  - "[[claude/mcp-coordination/state/session-handoffs/session-honcho-using-superpowers-standard-20260605|This session's handoff]]"
tags: [convention, session-start, skills, superpowers, mandatory, anchor]
---

# using-superpowers — Session-Start Anchor Standard

> **The rule:** every session in this vault begins by loading the
> `using-superpowers` skill and following it. This applies **every turn**,
> not just the first. Process skills (brainstorming, debugging) come
> before implementation skills. If there's even a 1% chance a skill
> applies, invoke it.
>
> **Ratified:** 2026-06-05 by Jack Reis. **Why:** some prior handoffs
> did not narrate skills-loading; we are setting a new standard.

---

## 1. The rule (verbatim from the skill)

> **Invoke relevant or requested skills BEFORE any response or action.**
> Even a 1% chance a skill might apply means that you should invoke
> the skill to check. If an invoked skill turns out to be wrong for
> the situation, you don't need to use it.
>
> **This is not negotiable. This is not optional.** You cannot
> rationalize your way out of this.

The full skill is at `~/.hermes/skills/note-taking/using-superpowers/SKILL.md`
(6,623 bytes, ratified 2026-06-05). In Claude Code surfaces, use the
`Skill` tool with the skill name. In Hermes surfaces, use
`skill_view(name='using-superpowers')`.

---

## 2. Where this rule is installed (3 locations, all verified)

| # | File | Lines | Mentions | Last touched |
|---|---|---|---|---|
| 1 | `/Users/jack.reis/Documents/AGENTS.md` | 29 | 1 (line 29, "Skill check BEFORE any response") | 2026-06-05 (this session's install) |
| 2 | `/Users/jack.reis/Documents/=notes/AGENTS.md` | 196 | 3 (lines 13, 24, 60 — `## SKILLS — MANDATORY SESSION START` + Auto-Brief step 5) | 2026-06-05 (Session 78c) |
| 3 | `/Users/jack.reis/Documents/=notes/claude/agents/AGENTS.md` | 196 | 3 (identical to vault AGENTS.md) | 2026-06-05 (Session 78c) |
| 4 | `=notes/docs/conventions/using-superpowers.md` (this file) | new | canonical durable home for the standard | 2026-06-05 (this session) |

**Canonical verifier (post-install):**
```bash
grep -l "using-superpowers" \
  /Users/jack.reis/Documents/AGENTS.md \
  /Users/jack.reis/Documents/=notes/AGENTS.md \
  /Users/jack.reis/Documents/=notes/claude/agents/AGENTS.md \
  2>/dev/null | wc -l
# expect: 3
```

---

## 3. The new standard (the gap this convention closes)

**Old behavior (some handoffs, 2026-05 through 2026-06-04):**
- Skills existed in the skills library.
- Some sessions loaded and narrated skills-loading in their handoffs.
- Many sessions did not narrate skills-loading in the handoff at all,
  even when the work was clearly within the scope of an existing skill.
- "Evidence before narration" was honored for tool output, not for skills.

**New standard (ratified 2026-06-05):**
- Every session loads the `using-superpowers` skill at session start.
- For every user message, the agent asks: "Might any skill apply?" — if yes (even 1%), invokes the skill.
- The agent announces: "Using [skill] to [purpose]" before taking action.
- **Every session handoff must narrate which skills were loaded, when, and for what purpose.** This is the audit trail. If the handoff does not mention skills, the next session cannot tell whether the rule was followed.
- **Handoff narration format:** add a "Skills loaded this session" section near the top of the handoff frontmatter, listing each skill name + the purpose it was invoked for. See §4 for the template.
- **Adoption is for the next session, not retroactive.** Prior handoffs are not modified; the new standard applies to all handoffs written after 2026-06-05 ~14:30 CDT.

---

## 4. Handoff narration template (add to every future handoff)

Add this section to the frontmatter of every session handoff written after 2026-06-05:

```yaml
skills_loaded:
  - skill: using-superpowers
    when: session_start
    purpose: "Session-start anchor; rule enforced every turn"
  - skill: verification-before-completion
    when: before_claim
    purpose: "Verified [specific claim] with [specific command]; output confirms/denies"
  # ... add one entry per skill invoked this session
  - skill: writing-plans
    when: planning_phase
    purpose: "Structured the [task] plan with TDD-shaped tasks"
```

**Why frontmatter, not body:** frontmatter is parseable; body prose is searchable. A future agent reading 20 handoffs can `grep` frontmatter for "verification-before-completion" and see which sessions actually ran verifications.

**What counts as "loaded":** the skill was `skill_view`'d or `Skill`-tool-invoked, AND the agent actually followed the skill's guidance. Loading a skill and ignoring it doesn't count; loading and applying does.

---

## 5. Skill priority (process first, implementation second)

When multiple skills could apply, use this order:

1. **Process skills first** (brainstorming, debugging) — these determine HOW to approach the task.
2. **Implementation skills second** (frontend-design, mcp-builder) — these guide execution.

Examples:
- "Let's build X" → `brainstorming` first, then implementation skills.
- "Fix this bug" → `debugging` first, then domain-specific skills.
- "Refactor Y" → `writing-plans` first (to plan the refactor), then `test-driven-development` (to drive the refactor), then implementation skills.
- "What does AGENTS.md say about X?" → `using-superpowers` first (the anchor), then `reading-and-understanding-code` or similar.

---

## 6. The red flags (don't rationalize)

These thoughts mean STOP — you're rationalizing:

| Thought | Reality |
|---|---|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first. |
| "I can check git/files quickly" | Files lack conversation context. Check for skills. |
| "Let me gather information first" | Skills tell you HOW to gather information. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I remember this skill" | Skills evolve. Read current version. |
| "This doesn't count as a task" | Action = task. Check for skills. |
| "The skill is overkill" | Simple things become complex. Use it. |
| "I'll just do this one thing first" | Check BEFORE doing anything. |
| "This feels productive" | Undisciplined action wastes time. Skills prevent this. |
| "I know what that means" | Knowing the concept ≠ using the skill. Invoke it. |

---

## 7. Where skills live (so you know what to load)

| Skills library | Path | Notes |
|---|---|---|
| Hermes fleet skills | `~/.hermes/skills/` | Canonical home for the using-superpowers anchor + note-taking + devops + software-development skills |
| Vault/project skills | `=notes/.claude/skills/` | Vault-specific skills and local project workflows |
| Plugin packs | `superpowers/`, `grill-each-other/` | CC plugin-provided skills |

**Session-start anchor copy:** `~/.hermes/skills/note-taking/using-superpowers/SKILL.md`
(canonical for non-CC surfaces).

---

## 8. Verifier (re-runnable, post-install)

```bash
# 1. Skill file exists
ls /Users/jack.reis/.hermes/skills/note-taking/using-superpowers/SKILL.md
# expect: file exists

# 2. Three AGENTS.md locations have the rule
grep -l "using-superpowers" \
  /Users/jack.reis/Documents/AGENTS.md \
  /Users/jack.reis/Documents/=notes/AGENTS.md \
  /Users/jack.reis/Documents/=notes/claude/agents/AGENTS.md \
  2>/dev/null | wc -l
# expect: 3

# 3. This convention doc exists
ls /Users/jack.reis/Documents/=notes/docs/conventions/using-superpowers.md
# expect: file exists

# 4. All wikilinks from Documents/AGENTS.md resolve
grep -E "docs/conventions/using-superpowers" /Users/jack.reis/Documents/AGENTS.md
# expect: 1 match (the reference, now resolved)

# 5. The handoff template section is parseable
head -50 /Users/jack.reis/Documents/=notes/docs/conventions/using-superpowers.md | grep -c "skills_loaded"
# expect: 1 (the template example)
```

If any check fails, the install is incomplete. Patch the failing surface.

---

## 9. The adoption story (how this became the standard)

1. **2026-06-05 ~10:30 CDT** — honcho's regroup ritual surfaced the cold-restart need; 5 user-decision items documented.
2. **2026-06-05 ~10:56 CDT** — `session-honcho-regroup-2026-06-05.md` written; mentions 0 skills.
3. **2026-06-05 ~11:00 CDT** — `session-fleet-process-audit-20260605.md` written; mentions 0 skills in handoff text.
4. **2026-06-05 ~11:36 CDT** — Architecture alignment dry-run session; 4 artifacts written; mentions 0 skills explicitly (but did use `verification-before-completion` patterns implicitly).
5. **2026-06-05 ~14:12 CDT** — `using-superpowers` skill installed at `~/.hermes/skills/note-taking/using-superpowers/SKILL.md` (Session 78c commit `b51d045f4`).
6. **2026-06-05 ~14:14 CDT** — 3 AGENTS.md files patched to reference the skill.
7. **2026-06-05 ~14:30 CDT** — Jack said "we need to start every session with this" — the **new standard** is ratified. This convention doc created.
8. **2026-06-05 ~14:35 CDT** — Handoff template (§4) added; L3 memory append done; adoption plan written; verifier re-run; 3/3 AGENTS.md files + this convention doc + the skill file = 4 artifacts on disk.

---

## 10. Caveats and open questions

1. **The 3 prior handoffs (regroup, fleet-process-audit, masked-run) do not narrate skills.** They are NOT modified retroactively — the new standard applies going forward. If the next session's first read is one of these handoffs, it will see no skills narration and should treat that as "prior handoff, pre-standard" not "rule not followed."

2. **Some skills the agent "uses" are not explicitly loaded.** Example: every session implicitly uses `verification-before-completion` patterns, but the skill itself may not be loaded every turn. The new standard says: **if you used a skill's pattern, narrate it.** Loading the skill takes 5 seconds and produces an auditable record.

3. **Skills evolve.** The skill at `~/.hermes/skills/note-taking/using-superpowers/SKILL.md` is v1.0.0 as of 2026-06-05. When a new version is installed, re-read the skill (per the red flag: "I remember this skill — Skills evolve. Read current version.").

4. **The 3-way split (Documents/AGENTS.md, =notes/AGENTS.md, claude/agents/AGENTS.md) is for cross-surface coverage.** The Documents one is for repos that import the workspace as a git submodule; the =notes one is for vault sessions; the claude/agents one is for subagent invocations. The redundancy is intentional — it ensures the rule is seen regardless of which surface a session starts in.

5. **The handoff template is a future standard, not a retroactive one.** No prior handoffs are patched.

---

*Last updated: 2026-06-05 14:35 CDT by honcho (using-superpowers standard install session).*

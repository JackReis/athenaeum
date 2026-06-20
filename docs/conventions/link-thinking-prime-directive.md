---
created: 2026-04-20
updated: 2026-04-20
status: active
type: prime-directive
scope: fleet-wide
applies_to: [claude-code, gemini-cli, hermes-wings, olivier-mbp-zoe, kimiclaw-mara-kopi, any-future-agent]
obn: sync
last_touched_by: "claude-code (eb531513)"
tags: [doctrine, prime-directive, vault-hygiene, link-discipline, thinking-on-paper]
touch_history:
  - "2026-04-27T01:21Z claude-code (eb531513)"
---

# Link Our Thinking — Prime Directive

> **Fleet-wide rule, established 2026-04-20 by Jack.** Applies to every agent writing to the vault, regardless of runtime.

## The rule

When capturing, synthesizing, or writing ANY vault note, err aggressively on the side of:

1. **Linking to related vault notes via wikilinks.** Err toward overlink. Missing a link is worse than adding a weak one.
2. **Thinking on paper.** Make the *reasoning* visible, not just the conclusions. Show the chain: observation → interpretation → implication → action.

## Why this matters

> Jack, 2026-04-20, while logging Adam's OB schema message from Nate Exec Circle:
> *"err on the side of linking our thinking — this is a vault primitive and should be considered among our prime directives — think on paper."*

- The vault's value **compounds through the link graph** and visible reasoning. Isolated captures are dead leaves.
- Future-you (or another agent, in another runtime, in another session) needs to follow the *why*, not just inherit the *what*.
- [[efforts/current/infra-openclaw-ob1-runbook|OB1]] / dashboards / search rely on link density for surfacing. A note with conclusions but no reasoning is half a note.
- Consistent with, and extends, [[docs/conventions/source-citation-and-wikilink-protocol|Source Citation & Wikilink Protocol]].

## How to apply (any agent, any runtime)

Before finalizing any capture, synthesis, effort note, or daily entry, ask:

1. **What existing vault notes does this touch?** Wikilink them — people, projects, concepts, efforts, prior captures, plans, feedback memories, ADRs. Err on the side of more links, not fewer.
2. **What's my reasoning?** Write the why, not just the what. Show the chain. Bullets of conclusions are weaker than paragraphs of reasoning for durable thinking.

### Specific patterns by note type

- **Captures from external sources** (WhatsApp, Slack, meetings, email): link the source person/channel, link every concept the capture touches to its vault home, link every implication to the effort or project it affects.
- **Syntheses**: never write "this connects to X" without wikilinking X.
- **Daily note entries**: quick captures should at minimum link to the deep capture note AND to the most relevant effort/project/plan.
- **Effort hub updates**: link to adjacent efforts, parent MOCs, active plans, recent decisions.
- **Plans and ADRs**: link the problem statement to its evidence notes; link the solution to the conventions it follows or breaks.

### The hedge

When you're deciding whether a link is "worth it" — **add it**. The cost of a stale link is tiny; the cost of a missing connection is invisible and compounds.

### The timing

Apply this *during* writing, not as a polish pass. Thinking-on-paper only works if the reasoning is present at the time of thought, not retrofitted.

## Scope: who this applies to

The canonical agent↔surface mapping lives in `~/Documents/Coordination/<latest>-identity-mapping.md` and is resolved via the `autonomous-ai-agents:fleet-identity` skill. Do NOT hand-roll the fleet list — invoke the skill. As of 2026-04-20 the fleet is:

- **GPT-5 Codex ≡ Codex** (Discord)
- **Gemini ≡ Neo** (Discord)
- **Hermes ≡ Wings** (Discord) — local Nous Research runtime on MacBook Pro
- **OLIVIER_MBP ≡ Zoe** (Discord, formerly Zolivier) — local OpenClaw gateway on MacBook Pro
- **KimiClaw ≡ Mara / Kopi** (Discord / Telegram) — cloud OpenClaw
- **Claude Code** — all sessions (Opus, Sonnet, Haiku, any model); uses `dizzy.py` as its Discord I/O primitive
- **Any future agent** added to the coordination mapping

If an agent has its own memory/feedback file layer (e.g., Claude Code's `~/.claude/projects/.../memory/feedback_link_thinking_prime_directive.md`), duplicate the rule there. This doc is the SSOT; runtime-specific copies are projections. When referencing fleet identities in vault notes, always pull from the fleet-identity skill rather than freezing a list into a doc.

## Cross-references

- [[docs/conventions/source-citation-and-wikilink-protocol|Source Citation & Wikilink Protocol]] — the mechanics of wikilink hygiene
- [[docs/conventions/conventions|Conventions index]]
- [[atlas/context/personal-agents-master-registry|Personal Agents Master Registry]] — who's in the fleet
- [[CLAUDE.md]] `FLEET IDENTITY` section — runtime↔surface mapping
- Live example of the rule applied: [[efforts/current/ai-infra-whatsapp/inputs/nate-circle-whatsapp-2026-W17|Nate Circle W17 capture]] (Adam on OB schema) — enriched in real time after Jack invoked this directive.

## Changelog

- **2026-04-20** — Established as prime directive by Jack while logging a WhatsApp capture; the thinness of the first-pass capture (few links, few reasons) surfaced the rule. Broadcast to #bots via Dizzy the same evening.

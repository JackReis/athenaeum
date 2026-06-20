---
title: Multi-Day Session — Daily Note Documentation Pattern
status: canonical
created: 2026-05-03
last_touched_by: "claude-code (39dcc65a)"
related:
  - "[[docs/conventions/session-coding]] — slug + role-tag naming"
  - "[[docs/conventions/agent-observer-principle]] — durable artifacts for next observer"
  - "[[docs/conventions/agent-custody-provenance]] — commit trailers + handoff schema"
  - "[[.claude/skills/ledger-lifecycle]] — END-phase 4-target gate"
touch_history:
  - "2026-05-03T21:22Z claude-code (39dcc65a)"
---

# Multi-Day Session — Daily Note Documentation Pattern

## The principle

When a session spans multiple calendar days, **each day gets its own Session Achievements entry in that day's daily note.** Don't consolidate the entire session into the closing day. Don't try to pull adjacent days' commits into today.

A daily note is a per-day journal. A session that ran 5/1 → 5/2 → 5/3 should have three entries — one per day — with cross-day breadcrumbs stitching the arc together.

## The three rules

### 1. Per-day entry, scoped to your own session

Each daily note gets ONE Session Achievements block per session that was active that day. List your session's commits, not the entire fleet's. Other parallel sessions write their own blocks. Multiple sessions on one day = multiple blocks, append-only.

A session entry header looks like:

```markdown
**Session <slug>-<role> — <topic> (<role-tag>)**
```

Where slug, role, role-tag are per [`session-coding.md`](session-coding.md). For continuations from prior days, append `(continued)` or `(closing day)` parenthetical.

### 2. Cross-day breadcrumbs at the top of each entry

Every multi-day entry's first line includes wikilinks back to the prior day's entry and forward to the next:

```markdown
**Session 39dcc65a-GH — observer principle (closing day)** ([continued from 20260501](20260501.md#session-39dcc65a) · [20260502](20260502.md#session-39dcc65a))
```

The `#session-<slug>` anchor convention lets readers jump to the specific session block on a multi-block day. Use the slug, not the full role-tag, for stable anchor names.

### 3. Don't pull adjacent days' commits *into* today

Each day owns its commit list. Listing yesterday's commits in today's entry creates duplication and rots when commits get rebased or reordered. The cross-day breadcrumb handles the connection — readers walk the arc by following the wikilinks.

If today's entry needs to *reference* a commit from another day, do it inline with a short note:

> Earlier same-session commits in adjacent daily notes: 5/1 — Sally bot fixes; 5/2 — `bc662c2b5` original observer-principle doctrine doc.

NOT:

> Yesterday's commits: a6418efa8 ..., d7b2a263a ..., 107d2f73c ..., (full repeated list)

## Worked example (vault state as of 2026-05-03)

A 3-day session with cross-day breadcrumbs:

| Daily note | Session entry | Anchor |
|---|---|---|
| `calendar/day/2026-05/20260501.md` | Session 39dcc65a — Sally Phase 1 production launch (BG) | `#session-39dcc65a` |
| `calendar/day/2026-05/20260502.md` | Session 39dcc65a — observer-principle authoring + chapel scaffold + dancer vision (GH) | `#session-39dcc65a` |
| `calendar/day/2026-05/20260503.md` | Session 39dcc65a-GH push-forward-survey — doctrine merge + 3 plans (closing day) | `#session-39dcc65a` |

Each entry lists ONLY that day's commits in that session's name. The breadcrumbs let a reader land on any of the three and walk to the others.

## Anti-patterns

- **One mega-entry on the closing day.** A 3-day session collapsed into a single block on the last day. Loses the day-level granularity that lets the reader see what happened on a Tuesday vs a Wednesday.
- **Empty session entries on intermediate days.** Skipping the middle day's note because "I'll capture it all at the end." Day 2 of a 3-day session is *not* less worth documenting; it's where the architecture decisions usually happen.
- **Citing the entire fleet's commits.** A daily note isn't a fleet-wide changelog; it's per-session journaling. If you want a fleet-wide view, that's the role of `git log --oneline --since=<date>`, not the daily note.
- **Breaking the breadcrumb chain mid-session.** If you skip the breadcrumb on day 2, a reader landing on day 3 can't trace back to day 1 without grep-walking. Always include both directions where they exist.

## When the session is one-day

Skip the breadcrumbs. Most sessions are single-day, so this whole convention is dormant for them.

## Interaction with `/ledger-lifecycle` END

The END-phase 4-target gate ([`.claude/skills/ledger-lifecycle`](../../.claude/skills/ledger-lifecycle)) checks daily-note coverage. For multi-day sessions, the gate should pass when:

- Today's note has a session entry with breadcrumb back
- Yesterday's note already has its own entry from when that day closed (or, if the session didn't close on yesterday's date, an in-progress entry that today's closing entry breadcrumbs back to)

If yesterday's note is missing your session's entry — backfill before commit. Backfill commit message: `doc(daily): backfill <date> + cross-day breadcrumbs for session <slug>`.

## Why this matters

This pattern is itself an instance of the [observer principle](agent-observer-principle.md): the daily note is the durable artifact a future observer will land on when asking *"what happened on day X?"* If the session collapsed everything into the closing day, the answer to *"what happened on the middle day?"* requires walking commit logs — not a measurement, just an inference. Per-day entries make each day independently observable.

## Voices

This convention was extracted from session 39dcc65a-GH on 2026-05-03 after Jack noticed his session log + daily note didn't fully cover the 3-day arc. The backfill (commit `895898a8f`) demonstrated the pattern; this doc codifies it.

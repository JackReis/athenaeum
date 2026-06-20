---
obn: sync
---

# Batch Checkpointing Convention

When executing multi-task plans (3+ tasks in one session):

## Commit Cadence
- Commit and push after completing each individual task
- Never batch all changes into a single commit at session end

## Commit Message Format
- `"task N/M: <description>"` (e.g., `"task 3/7: update PT recovery dashboard"`)
- For the final task: `"task M/M: <description> — batch complete"`

## Progress Reporting
- After each commit, report: `"Task N/M complete"`
- After final commit: `"Batch complete — ready for next steps"`

## Interrupted Batches
- If a session ends mid-batch, the handoff file lists remaining tasks explicitly
- The next session picks up from task N+1, not from scratch

## Rationale
- Per-task commits create save points that survive session interruptions
- Explicit progress reporting avoids ambiguity about what's done vs. in-progress
- Handoff files with remaining tasks enable clean multi-session continuity

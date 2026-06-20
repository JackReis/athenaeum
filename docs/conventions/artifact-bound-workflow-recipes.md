---
title: Artifact-Bound Workflow Recipes
status: active
created: 2026-05-21
updated: 2026-05-21
tags:
  - convention
  - workflow
  - recipe
  - fleet
obn: sync
---

# Artifact-Bound Workflow Recipes

## Purpose

Some workflows define a non-vault artifact as the deliverable: a Telegram message, a Linear comment, a Slack reply, a GitHub PR comment, or an n8n execution. For these workflows, the artifact contract overrides the fleet's default instinct to add handoffs, daily-note entries, or extra markdown evidence.

This convention does not weaken [[docs/conventions/fleet-directive|Fleet Directive - Durable Evidence]]. It names the artifact explicitly so agents do not create a second source of truth after the real output has already been delivered.

## Rule

If a workflow says "the message/comment/reply/execution is the artifact," then done means:

1. Read the required live sources.
2. Produce the exact bounded artifact.
3. Verify the workflow-specific guardrail before emission.
4. Emit through the required tool.
5. Run only the explicitly allowed post-send log/check.
6. Stop.

Do not create compensating evidence unless the workflow explicitly asks for it.

## Recipe: Weekly Telegram Pulse

Use when running `claude/scheduled-tasks/prompts/weekly-review.md`.

### Contract

- Artifact: exactly one Telegram message sent through `mcp__telegram-bridge__send_summary`.
- Shape: week/date, three concrete actions, one forced tradeoff.
- Limit: 400 characters maximum.
- Post-send: one stderr line only.
- Forbidden: markdown brief, daily-note entry, handoff stub, extra vault file, Write/Edit tool use.

### Steps

1. Confirm date and ISO week with `date`.
2. Gather current signal from git log, infrastructure status, active task queue, daily notes, handoffs, closed tasks, and OB1.
3. Draft the shortest useful message matching the prompt shape.
4. Count characters before sending.
5. If the count is over 400, rewrite until it is at or under 400.
6. Send exactly one Telegram message.
7. Log the required stderr line.
8. Stop immediately.

### Failure Modes

- **Audit-trail reflex:** creating a handoff or daily note after a successful send. This violates the recipe because Telegram was the artifact.
- **Markdown drift:** writing a scheduled brief or summary file. This recreates the old weekly prose churn the pulse replaced.
- **Generic actions:** using "continue" or "follow up" instead of a named next action.
- **Fake tradeoff:** naming vague categories instead of two real competing priorities.

## Detection

Before adding a vault artifact after an outbound send, ask:

> Did the workflow define the outbound message/comment/reply as the artifact?

If yes, do not write the extra artifact. The correct closeout is the tool result plus any explicitly permitted stderr/log line.

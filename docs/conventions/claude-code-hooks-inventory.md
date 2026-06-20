---
title: Claude Code Hooks Inventory & Audit
status: in-progress
created: 2026-06-06
decay: review-quarterly
related:
  - docs/adr/0015-fleet-messaging-discord-to-matrix.md
  - docs/conventions/fleet-directive.md
  - docs/conventions/agent-custody-provenance.md
last_touched_by: "claude-code (6ecfd02b)"
touch_history:
  - "2026-06-06T19:15Z claude-code (6ecfd02b)"
  - "2026-06-06T20:37Z claude-code (6ecfd02b)"
---

# Claude Code Hooks Inventory & Audit

Audit of every active Claude Code hook across the two settings files that
apply to this vault, with a keep / remove / modify decision and rationale
for each. Conducted via `grill-with-docs` on 2026-06-06.

- **Project hooks:** `=notes/.claude/settings.local.json` (17 entries)
- **User hooks:** `~/.claude/settings.json` (12 entries)

A hook entry = one `command` registration. Some scripts are registered
under more than one matcher (e.g. `skill-build-gate.sh` on both Write and
Edit) and count once per registration.

## Decisions

| # | Hook (script) | Event / matcher | File | Decision | Status | Rationale |
|---|---|---|---|---|---|---|
| 13 | `dizzy_inbox_hook.py` | UserPromptSubmit | project | **Remove** | **APPLIED 2026-06-06** (commit `07c0ab686`) — registration deleted from `.claude/settings.local.json`; JSON re-validated, `grep dizzy_inbox_hook` = 0. | Polls Discord (#general, #sea-ranch-ops, #bots) on every prompt and injects as context. Contradicts CLAUDE.md ("Discord is legacy/optional… not a notification path") and ADR-0015 (Discord→Matrix migration). ~2s/prompt cold-poll cost. Dizzy stays available as a manual legacy lane. |
| 14 | `multi-session-check.py` | UserPromptSubmit | project | **Modify** | **APPLIED 2026-06-06** (commit `3c8b2fc7a`) — dropped `post_dizzy_alert`/`already_notified`/`mark_notified`/`DIZZY_PY`/`NOTIFY_DIR`; kept the `additionalContext` local signal and `dizzy.py` as a watch target. Verifier: AST OK + ran with `{"session_id":"plan-test"}` → exit 0, no outbound call. | Keep the local cross-session detection (commits/handoffs/other-agent edits — verified working this session) but strip the `dizzy.py` #bots posting so it stops writing to the legacy Discord lane. Local signal only, no outbound Discord. |
| 6 | `leonardo-sentinel-gate.sh` | PreToolUse Read\|Grep | project | **Modify** | **CODE APPLIED 2026-06-06** (commit `f25956fd5`) — retargeted to `fleet.py send --audience jack-mobile`, fail-loud (no `&>/dev/null`), errors → `~/.claude/logs/hook-notify-errors.log`; `bash -n` OK, 0 dizzy refs. **LIVE ARRIVAL VERIFIER BLOCKED** on a truncated/invalid Telegram bot token (see Transport decision). | Keep the prompt-injection canary (near-zero cost, silent until a `__protected__:` sentinel appears) but retarget its alert off legacy dizzy/Discord to **Telegram via `fleet.py` → `telegram-send.py`** (single control point; Matrix has no send CLI). Moved `telegram-send.py` out of `archive/` since a live hook now depends on it. |

## Transport decision (2026-06-06)

Hooks route notifications through **`fleet.py send <audience>`** (the existing
unified bus) — a single control point — never a transport script directly. The
`_send_telegram` adapter (was a print-only stub) is now wired to shell out to
`telegram-send.py` (direct Bot API), fail-loud by raising so `fleet.py`'s
state-log marks the attempt `failed` and exits nonzero. Hook-side failures also
append to `~/.claude/logs/hook-notify-errors.log`. A future Matrix migration =
wire `fleet.py`'s matrix adapter + edit `fleet-routing.yaml`, **zero hook edits**.

- **Rejected — Arbiter Zebu:** governance decision-queue + flagged SPOF
  (2026-06-04 audit); routine canary alerts must not pollute it.
- **Rejected — Telegram via Hermes:** unreachable from a hook (Hermes is
  MCP-stdio only; no synchronous send CLI).
- **Matrix** is the future fleet-bus option, via `fleet-routing.yaml`.
- Plan: `docs/plans/2026-06-06-hook-alert-transport-switch.md`. The fleet.py
  indirection + fail-loud-via-raise design came out of a Gemini 3.1 Pro + GPT 5.5
  dogpile and a Codex review (`docs/reviews/2026-06-06-hook-transport-recommendation-for-review.md`).

### Open blocker — live verifier

The two human-confirmable live sends (`telegram-send.py` smoke + `fleet.py send
--audience jack-mobile`) **cannot pass yet**: the only available bot token
(SOPS `~/.secrets/openclaw-runtime.env` → `CLAUDE_CODE_BRIDGE_TELEGRAM_BOT_TOKEN`)
decrypts to ~14 chars and returns HTTP 404 from `getMe` (valid tokens are ~46
chars). chat_id resolves fine. Code is proven by the unit suite
(`tests/scripts/test_fleet_cli_telegram_adapter.py`, 4 passed) but per the Fleet
Directive these rows stay **untested-live** until Jack restores the full token
(re-encrypt in SOPS, or drop `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` into
`~/.claude/telegram-send.json` at 0600) and the live sends are human-confirmed.

## Notes

- Decisions are applied to the settings files after the grill concludes, in
  one reviewed change.
- "Blocking?" = whether the hook can deny/gate a tool call (fail-closed) vs
  only warn/log (fail-open).

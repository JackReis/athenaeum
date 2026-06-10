---
name: athenaeum-reconcile
description: Streamlined single-pack reconciliation when two or more agents hold divergent understanding — the consolidated athenaeum path to a structured file-based convergence protocol across model families. Use when parallel sessions disagree or a non-Claude peer needs to converge with a Claude session and you want the athenaeum protocol. Triggers — "athenaeum reconcile", "reconcile via athenaeum", "athenaeum converge". If the grill-each-other pack is installed and you want the modular primitive instead, use peer-grill (state reconciliation) or peer-grill-with-agents (code-anchored agent-stack triangulation).
---

# Athenaeum — Reconcile

## Pick a mode

| Mode | When to use | Attestation |
|---|---|---|
| `quick` | Low-stakes, trust-high, same machine | Verbal agreement; no SHA-256 |
| `formal` | High-stakes, cross-machine, cross-model | Full protocol with sign-offs |

Default: `quick` if unspecified.

## 4-step workflow

1. **Init** — `scripts/athenaeum init <topic> --mode quick|formal`
   - Scaffolds `.athenaeum/<topic>/` with templates.
   - Prompts for identities and scope.

2. **Dump** — each peer writes `<agent>.claims.yaml` independently.
   - Do NOT read peer files yet. Context leakage defeats triangulation.
   - See `templates/reconcile/claims.yaml.template`.

3. **Diff & grill** — compute three buckets:
   - **agreed** → merge directly
   - **disagreed** → grill loop (asker = lower confidence)
   - **only-one-knows** → grill loop (asker = the one who doesn't know)
   - Round budget: 3. Exhaustion → `ESCALATE` to `unresolved.md`.
   - On convergence, both peers write `RATIFY: <id> | <statement>`.

4. **Merge & sign** — merge writer writes `state.merged.yaml`.
   - Formal mode: LF-normalize, SHA-256, append to `signoff.md`.
   - Quick mode: verbal sign-off; write `state.merged.yaml` without crypto.

## Non-Claude peers

Paste the one-page prompt from `templates/reconcile/peer-prompt.md` into the peer session. The protocol is symmetric — no Claude-specific assumptions.

## A2A interop

This skill speaks A2A natively. An A2A Task represents this workflow.

**Task metadata:**
- `athenaeum_mode: reconcile`
- `status` lifecycle: `submitted` → `working` → `input-required` → `completed`

**Artifacts produced:**
- `diff.md` — `text/markdown`
- `grill-log.md` — `text/markdown`
- `state.merged.yaml` — `application/yaml`

**Enable A2A for this workflow:**
```bash
athenaeum init my-topic --mode reconcile --transport a2a
```

**Invoking via A2A:**
```json
{
  "jsonrpc": "2.0",
  "method": "tasks/send",
  "params": {
    "task": {
      "id": "athenaeum-reconcile-my-topic",
      "sessionId": "<agent-session>",
      "status": "submitted",
      "metadata": {"athenaeum_mode": "reconcile", "topic": "my-topic"}
    }
  }
}
```

## Sibling skills

- `athenaeum-design` — design something before reconciling it
- `athenaeum-ratify` — formal fleet attestation after reconciliation

Full protocol (formal mode terminal events, integrity failures, multi-peer chains): see `REFERENCE.md` §3–6.

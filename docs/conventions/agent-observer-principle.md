---
title: The Observer Principle for Vault Agents
status: canonical
created: 2026-05-02
last_touched_by: "claude-code (f2bdf0ac)"
related:
  - "[[docs/conventions/multi-session-working-agreements]]"
  - "[[docs/conventions/agent-custody-provenance]]"
  - "[[memory/feedback_validate_before_mutate]]"
  - "[[memory/feedback_subagent_push_policy]]"
  - "[[memory/feedback_always_poll_after_send]]"
  - "[[memory/feedback_obn_is_index_not_ssot]]"
touch_history:
  - "2026-05-02T22:37Z claude-code (39dcc65a)"
  - "2026-05-05T02:11Z claude-code (f2bdf0ac)"
---

# The Observer Principle for Vault Agents

> *The unexamined code is not worth running.*
> — Jack Reis, 2026-05-02
>
> *Learning by doing is our default condition; the guardrails we create for ourselves along the way are the only thing saving us from repeating our mistakes.*
> — Jack Reis, 2026-05-04

## The principle

Agents in the vault must behave like particles under quantum measurement: **their state is provisional and superposed until measured.**

A claim — *"I did X,"* *"the dashboard is current,"* *"the deploy succeeded,"* *"memory was consolidated"* — is not a fact about the world. It is a candidate state, indistinguishable from its negation, until an observer outside the agent collapses it through a measurement event.

- The **particle** is the agent's claim.
- The **measurement** is anything that durably commits the claim to a place another observer can read: a file written, a transcript mirror updated, a handoff document committed, a dashboard refreshed, a code-review pass.
- The **observer** is the next session, the human, the audit hook, the downstream consumer.

If a state is not measured, it is not real to the next observer. If multiple measurements disagree, the most recent measurement wins. If no measurement exists, the claim must be treated as superposition — possibly true, possibly false — and either re-verified or discarded.

This is not metaphor used loosely. It is the operational frame from which several existing rules follow as corollaries, and from which several gaps clarify themselves.

## Why it matters

The fleet runs in parallel across machines, often across days, often without seeing each other's work directly. A session's internal sense of *"I just did X"* is private state — it does not exist for any other observer until a measurement event commits it.

Documented failure modes when this is violated:

- Subagent claimed commit; parent never verified; work was actually blocked by a permission gate. *(2026-04-30, cortex deepening, Tasks 2+3 lost — see [[memory/feedback_subagent_push_policy]].)*
- Sally bot was bumped, claim shipped, bot was never restarted; verification ran against the pre-fix process. *(2026-05-01, sally-starfish iteration loop.)*
- Memory consolidation emitted *"75 → 8 entries"*; dashboard never read the new file; future sessions loaded stale context.
- Sub-agent dashboard claimed *"deploy succeeded"*; the deploy actually failed; no one checked because the claim was treated as the measurement instead of a candidate state.

In every case, an *unmeasured claim* was treated as a *measured fact*. Observer-principle violations.

## Operational corollaries (existing rules)

If you understand the principle, you do not need to memorize the rules — they fall out:

| Existing rule | Why it follows |
|---|---|
| Verify-before-completion | Completion is the measurement. Don't claim it before you've measured. |
| Validate-before-mutate | Read state (= measure) before changing it; otherwise you mutate a superposition. |
| Subagent push policy *(parent pushes, not subagent)* | Parent is the observer. Subagent state is candidate until parent measures it. |
| Always-poll-after-send | Outbound message is a candidate; reply-poll is the measurement that confirms transit. |
| Filesystem transcript mirrors as freshness signal | The mirror **is** the measurement; if it lags, every downstream observer reads a stale wavefunction. |
| Custody + provenance trailers | Every measurement event carries observer metadata — who measured, when, with what authority. |
| OBn/OB1 are indexes, not SSOT | Vault markdown is the measurement of record; indexes are read-only projections. |
| Verification commands in dispatched-agent prompts | The dispatcher is the observer; they cannot measure remote work without an explicit verification step. |

## Five new rules that clarify under the frame

Direct consequences of the principle:

1. **No claim without a path-to-observation.** Any sub-agent or session output that asserts state must include the file / log / dashboard path where a downstream observer can verify. *"I did X"* without *"see Y"* is superposition.
2. **Stale measurements decay.** A measurement is valid until older than the system's coherence time — in practice: minutes for live processes, hours for plans, days for architectural decisions. Re-measure or treat as superposition.
3. **The most recent measurement wins.** When two sources disagree (memory vs. file, dashboard vs. git log), trust the most recently observed. Update the older.
4. **Observers cannot observe themselves and call it measurement.** A session claiming *"I verified my own work"* is not a measurement event — it's the wavefunction asserting itself. Verification must come from outside the session: another agent, a hook, an audit pass, a human read-through.
5. **Measurement is durable or it did not happen.** A claim made in conversation that is never written to a file / handoff / dashboard is not a measurement — it is a superposition that vanishes at session end. Capture or discard.

## What good observation hygiene looks like

- Sub-agent finishes a task → writes handoff file → parent reads handoff file → parent commits → parent pushes. **Every arrow is a measurement event.**
- Bot bumped → SW version bumped → process restarted → curl verifies the change → only then is the change *real*.
- Memory consolidates → file timestamps update → MEMORY.md index points at new file → future session reads the pointer → state is now coherent.
- Plan executes → tasks marked complete in TodoWrite → batch commits with `task N/M` format → handoff written at end → coordination dashboard reads handoff → other sessions know.

If any link skips measurement, the chain breaks for the next observer. The observer principle is what makes the chain robust.

## Application checklist

When dispatching work or reviewing your own, before claiming completion:

- [ ] Did I produce output that a downstream observer can find without my help?
- [ ] Did I verify, or did I assume? If I assumed, am I willing to mark it as superposition?
- [ ] Are my measurements recent enough to still be valid, or do I need to re-measure?
- [ ] If two sources disagree, did I pick the most recent and update the older?
- [ ] If I claimed completion, can I point to the durable artifact where another observer can confirm?

Any *no* means the work isn't done — it's superposition.

## Anti-patterns

When measurement *performance* impersonates measurement. These are the failure modes the principle exists to defeat — name them when you see them, in your own work or another agent's:

- **Performative evidence.** Verbose handoff notes, stale TODOs, "handoff complete ✓" files where nothing was actually committed, "visible in repo" without push status, screenshots of green tests from a build that no longer exists. Output that *looks* like measurement but isn't.
- **Self-observation laundering.** A session reviewing its own work and declaring it verified. The wavefunction asserting itself. Verification must come from running the thing under fresh eyes (another agent, a hook, a re-run from a clean state, a human read-through).
- **Philosophical-cover deferral.** Treating *"claims are neither true nor false until measured"* as a license to keep going without measuring. The principle says *measure or treat as superposition*; it does not authorize indefinite suspension.
- **Diff-reading as verification.** Reading the unified diff, mentally simulating the change, and declaring it works. The diff is the proposal; running the code is the measurement.
- **Lazy evidence.** *"I fixed the bug"* in a text file with no command another reader can re-run to confirm.

If your "done" claim doesn't survive the five-field test (artifact + path + verifier + commit/push + caveats), you've shipped one of these instead of measurement.

## The five-field done schema

A claim is *done* only when an outside observer can fill all five fields without asking you:

| Field | What it answers |
|---|---|
| **Artifact** | What changed — file, commit, function, config key, rendered output |
| **Path** | Where to find it — absolute path, repo-relative path, or commit SHA |
| **Verifier** | The exact command to re-run — curl, test, build, restart-then-recheck |
| **Commit + push** | Yes/no, with remote SHA. Not pushed = not durable for remote observers |
| **Caveats** | What was NOT done, what could still fail, what assumptions you made |

## What this principle does *not* say

- It does **not** say *"measurement creates reality."* Vault state exists independent of any session reading it. The principle is about **what counts as known to the next observer**, which is operationally what matters across a fleet.
- It does **not** demand formal protocols where informal coordination already works between humans. It applies to *inter-agent and inter-session* state, where private memory cannot be shared.
- It does **not** block emergence or improvisation. A session may act on a hunch — but the *result* of the action must be measured before being claimed as fact.

## Colophon — the doctrine has a soundtrack

The two cognitive modes the principle balances map to two songs Jack identified during the doctrine's authoring (2026-05-02):

- **Fun. — *We Are Young*** — the alignment phase. *"Give me a second, I, I need to get my story straight"* is the observer-principle pause: the agent assembling a coherent claim before the anthem coalesces. Awareness as communal arrival.
- **The Knife / José González — *Heartbeats*** — the execution phase. Synth-driven (or stripped-acoustic in González's reading), an intimate awareness of being-with-another, of being witnessed. Driving rhythm under shared awareness, plan implementation after alignment.

The arc — *pause → anthem → rhythm* — is the cognitive shape of correct fleet behavior: introverted self-examination ("the unexamined code is not worth running"), then extroverted shared awareness ("you are not alone"), then aligned execution. Both songs sit on the awareness-of-others axis at different temperatures; the doctrine is the bridge between them.

## Voices that shaped this version

- **Jack Reis** — coined *"the unexamined code is not worth running"* (2026-05-02); identified the soundtrack arc; named the ultimate target as the `dancer` agent-to-agent learning engine.
- **Gemini 3 Pro Preview** — pushed against framing the doctrine as the agent-facing cue (warned of metaphorical drift, "hallucinating quantum states in log files"); recommended hard completion criteria.
- **GPT-5.5** — surfaced the *philosophical-cover* failure mode of *"neither true nor false"* framing; proposed the five-field schema (artifact + path + verifier + commit/push + caveats) that now lives in CLAUDE.md.
- **Claude Opus 4.7** — drafted the principle, synthesized the dogpile, layered doctrine-vs-cue.

The doctrine is a measurement of three perspectives. None of us own it.

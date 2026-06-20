---
decay: enduring
title: Dialectic Vocabulary — scholastic + Greek terms in peer-grill
status: canonical
created: 2026-05-05
last_touched_by: "claude-code (39dcc65a)"
related:
  - "[[docs/conventions/agent-observer-principle]] — verify-before-completion"
  - "[[~/.claude/skills/peer-grill/SKILL.md]] — file-based reconciliation protocol"
  - "[[~/.claude/projects/-Users-jack-reis-Documents--notes/memory/feedback_load_bearing_via_verifiers]] — load-bearing ladder"
touch_history:
  - "2026-05-05T02:15Z claude-code (255b8c81)"
  - "2026-05-05T02:02Z claude-code (39dcc65a)"
---

# Dialectic Vocabulary — scholastic + Greek terms

> ὁ ἀνεξέταστος βίος οὐ βιωτὸς ἀνθρώπῳ.
> *"The unexamined life is not worth living for a human."*
> — Σωκράτης (Socrates, Plato, *Apology* 38a)
>
> The vault carries this instinct as a two-layer aphorism at the top of `CLAUDE.md`:
>
> 1. **The unexamined claim is not worth reading.** *(producer-side discipline — the subject of this document)*
> 2. **The unexamined code is not worth running.** *(consumer-side discipline — the subject of [[docs/conventions/agent-observer-principle]])*
>
> The upper conditions the lower. A claim that arrives without self-examination — no confidence rating, no source, no verifier, no surfaced assumptions — costs the reader more to triage than to ignore.

## The synthesis — why these are the same principle in two voices

Push both aphorisms hard enough and they converge on one observation: **an unexamined claim does not exist.**

The [[docs/conventions/agent-observer-principle|observer-principle doctrine]] frames this as quantum-style measurement: an agent's claims exist in superposition until a downstream observer measures them. *"You cannot observe yourself and call it measurement."* The unexamined-claim aphorism is the **strong-form sibling** of that principle, applied one rung upstream:

| Frame | What it says |
|---|---|
| **Observer principle (consumer)** | Until a downstream reader independently verifies, the claim is provisional. State exists only when measured. |
| **Unexamined-claim (producer)** | Until the *claimant* themselves applies measurement-machinery (verifier, source, confidence, surfaced assumptions), there is nothing for the observer to measure. The "claim" is noise pretending to be signal. |
| **Synthesis** | A claim is brought into existence by the act of grounding it. ἀλήθεια — *un-concealment* — is the measurement that resolves the superposition. ἔλεγχος (cross-examination) is what forces the resolution. The dialectic vocabulary below names the moves that perform the measurement. |

Or in one sentence: **a claim that hasn't been examined hasn't been made.** It's a wave function the observer can't collapse because there's nothing in it to collapse onto.

This is why the producer-side discipline is load-bearing for the consumer-side principle to even *function*. The observer can't measure what isn't there. Verifiers, sources, confidence ratings, ALETHEIA stamps — these are the substrate that gives the claim enough specificity to be measurable in the first place.

The dialectic vocabulary gives the *act of bringing a claim into existence* a structure and a name. Greek for the soul of the inquiry, Latin for the form on the page.

## Why borrow from the scholastics and the Greeks

The peer-grill protocol is doing what Plato's Academy and the medieval *quaestiones* did: forcing claims to survive structured cross-examination before being treated as truth. That tradition has 2,400 years of refined vocabulary for the moves we're already making — using it sharpens what we mean and signals to any agent (human or otherwise) that a discourse is operating under those rules.

Two registers, two purposes:

| Register | Purpose | Where it shows up |
|---|---|---|
| **Greek** (ἔλεγχος, ἀλήθεια, διαλεκτική, λόγος) | The phenomenology of inquiry — what truth-seeking *feels like* and *requires* | Stamps, signatures, philosophical framing |
| **Latin** (quaestio, obiectio, sed contra, respondeo) | The mechanics of disputation — the *form* a contested claim takes on the page | Structural fields in claims/grill-log |

Greek for the soul of the act; Latin for the body. Both load-bearing, neither decorative.

## The vocabulary

### Greek (philosophical register — for stamps and naming)

| Term | Transliteration | Meaning | Where in the protocol |
|---|---|---|---|
| **διαλεκτική** | dialektikē | The whole art of reasoning through dialogue | The peer-grill protocol itself |
| **ἔλεγχος** | elenchos | Socratic cross-examination; refutation that exposes contradiction | Grill rounds in `grill-log.md`; falsifier triggering |
| **ἀλήθεια** | alētheia | Truth as **unconcealment** — what is revealed when grilling strips away appearance | Ratification stamp on `state.merged.yaml` and signoff |
| **σύνθεσις** | synthesis | Putting-together; the convergence after dialectic | The merged state file itself |
| **λόγος** | logos | Word, reason, structured account | The claim — *the account that must be defensible* |
| **ἀπορία** | aporia | A puzzle without resolution — when grilling reaches an impasse | The `unresolved.md` outcome |

### Latin (scholastic register — for disputation structure)

A *quaestio* in Aquinas's *Summa Theologiae* has a fixed form. Each question gets:

1. **Quaestio** — the question being disputed, stated as a thesis
2. **Obiectiones** — a numbered list of strongest objections (Aquinas typically lists 3-5)
3. **Sed contra** — *"but on the contrary"* — the single most authoritative counter that pulls the disputation toward the right answer
4. **Respondeo** — *"I respond"* — the master's adjudication, which usually concedes the kernel of the objections while restoring the *sed contra*
5. **Responsiones** — replies to each numbered objection, showing how the *respondeo* dissolves them

This is *exactly* the shape of a load-bearing peer-grill claim that has survived contestation. We adopt it for high-stakes claims where bullet-list grilling would be too thin.

| Term | Meaning | Where in the protocol |
|---|---|---|
| **quaestio** | The disputed thesis | Statement field of a claim being grilled |
| **obiectio** / **obiectiones** | Numbered objection(s) | Counter-claims from peer agents |
| **sed contra** | The strongest opposing source/argument | One designated counter-claim with the highest authority |
| **respondeo** | The adjudicating response | The author's reply that resolves the dispute |
| **responsiones** | Per-objection replies | Detailed answers to each obiectio |

## Grill-log tags (canonical)

Use these as the prefix on grill-log entries. The first three (Greek) describe the *kind* of move; the rest (Latin or English) describe its *role* in disputation.

| Tag | Meaning |
|---|---|
| `ELENCHOS` | A cross-examination question (round 1+) |
| `APORIA` | An impasse — escalating to `unresolved.md` |
| `ALETHEIA` | A ratification stamp; the claim is now considered unconcealed truth |
| `QUAESTIO` | Opening a structured *quaestio* on a contested claim |
| `OBIECTIO:N` | Objection N to the open quaestio |
| `SED-CONTRA` | The strongest counter, designated |
| `RESPONDEO` | The author's adjudicating response |
| `RESPONSIONES` | Per-objection replies |
| `RATIFY:<id>` | (existing) Sign-off for routine claims that don't need full quaestio form |

The peer-grill SKILL.md keeps `RATIFY:` as the default for everyday claims. The Latin tags are reserved for **high-stakes claims** where the disputation form earns its overhead.

## When to use which form

| Claim shape | Use |
|---|---|
| Empirical, low-stakes, has a verifier | `RATIFY:<id>` after the grader returns PASS |
| Empirical, contested | `ELENCHOS` rounds, then `RATIFY:<id>` or `APORIA` |
| Normative, contested | `QUAESTIO` form (full structured disputation) |
| Foundational principle | Formalize in TLA+/Alloy AND quaestio form; ratify with `ALETHEIA <sha256>` |

## Greek-alphabet fingerprints — the layered namespace

Every claim's `id` is lowercase Latin ASCII (filesystem-safe, sha256-deterministic, homoglyph-free). Alongside it, every claim carries a **Greek-alphabet fingerprint** — a 4-letter handle deterministically derived from `sha256(NFC(id))`. Fingerprints are *display-layer only*: they never appear in pathnames, never enter sha256-canonical-statement computation, and are never authored (only generated).

| Surface | Encoding | Why |
|---|---|---|
| Primary `id` (machine identifier) | lowercase Latin ASCII | Load-bearing for filesystem + hash + collision-checking |
| **`fingerprint`** (display handle) | 4-letter Greek lowercase | Carries the philosophical register; visually distinct; deterministic; auto-derived |
| Cycle / round labels | Greek lowercase as ordinals (α, β, γ, …) | Display-layer only; schema's `n: integer` field stays Latin numerals |
| Tag prefixes | Latin caps (ELENCHOS, ALETHEIA, …) | Already established in this doc; readable in non-UTF8 grep |

### The fingerprint algorithm

```python
import hashlib, unicodedata
GREEK = "αβγδεζηθικλμνξοπρστυφχψω"  # 24 letters
def fingerprint(claim_id: str) -> str:
    canonical = unicodedata.normalize("NFC", claim_id).encode("utf-8")
    digest = hashlib.sha256(canonical).digest()
    return "".join(GREEK[b % 24] for b in digest[:4])
```

Reference implementation: `~/.claude/skills/peer-grill/scripts/peer_grill_fingerprint.py` (CLI; supports `--bracketed` and `--batch`).

### Examples

| `id` | `fingerprint` | Display |
|---|---|---|
| `memory-md-truncation` | `τκφε` | ⟦τκφε⟧ |
| `dizzy-clobber-footgun` | `ινξψ` | ⟦ινξψ⟧ |
| `mcp-profiles-count` | `πμημ` | ⟦πμημ⟧ |
| `legacy-code-indexer-fts-error-spam` | `ξπσα` | ⟦ξπσα⟧ |

### Why this layering — the four obiectiones it dissolves

A naive "use Greek alphabet for IDs" proposal fails four ways. The fingerprint pattern dissolves all four:

| Obiectio | How fingerprint dissolves it |
|---|---|
| Filesystem hostility (Greek in pathnames breaks tools) | Filenames stay Latin; fingerprint never enters paths |
| Unicode NFC/NFD sha256 collisions | sha256 inputs stay ASCII id + ASCII statement; fingerprint excluded from canonical hash |
| Visual homoglyph attacks (α↔a, ε↔e, ν↔v, …) | Fingerprints are derived not authored — you cannot construct a colliding Latin/Greek pair, only the hash function can |
| Reviewer keyboard barrier | Auto-generated; nobody types Greek to participate |

### Where fingerprints appear

- **`graded.md`** — leftmost column of the grading table: `⟦τκφε⟧ \| agent \| claim \| …`
- **Belief ledger** — `Belief.fingerprint` field on the Tipi spirit-layer dataclass (auto-populated)
- **Discord / chat circulation** — when referencing a claim, prefer `⟦τκφε⟧ memory-md-truncation` so readers can grep either form
- **Wikilinks in vault notes** — `[[claims/⟦τκφε⟧-memory-md-truncation]]` works as a memorable anchor

The fingerprint is the namespace's signature. Like a git short-sha or a thumbnail in a contact sheet, it gives the eye somewhere to land without burdening the load-bearing layer.

## The ἀλήθεια stamp

When a claim moves to `state.merged.yaml`, append a line to `signoff.md` of the form:

```
ALETHEIA <agent-name> <ISO-timestamp> sha256:<hex of merged statement>
```

This is the Greek-flavored sibling of the existing peer-grill signoff. It serves the same epistemic purpose (attestation that *this* is what we collectively unconcealed as true) but with vocabulary that carries philosophical weight: ἀλήθεια in Greek is literally *un-forgetting* — the negation of λήθη (Lethe, the river of forgetting). To stamp ALETHEIA is to assert: *this claim has been examined; it is not concealed by appearance, fashion, or expedience.*

If two agents independently RATIFY the same merged statement, but their ALETHEIA stamps' sha256s don't match, that's an **integrity failure** — same as the existing peer-grill `INTEGRITY-FAIL` rule, but louder.

## Worked example structure (template)

```markdown
[<ISO>] <agent> | QUAESTIO claim:<id>
**Quaestio.** <thesis statement>

[<ISO>] <agent-A> | OBIECTIO:1 claim:<id>
<first objection with source>

[<ISO>] <agent-B> | OBIECTIO:2 claim:<id>
<second objection with source>

[<ISO>] <agent-C> | SED-CONTRA claim:<id>
<the single strongest counter, with most authoritative source>

[<ISO>] <author> | RESPONDEO claim:<id>
<adjudicating response — concede the kernel of the objections, restore the sed contra>

[<ISO>] <author> | RESPONSIONES claim:<id>
1. <reply to obiectio 1>
2. <reply to obiectio 2>

[<ISO>] <agent-A> | ALETHEIA claim:<id> sha256:<hex>
[<ISO>] <author> | ALETHEIA claim:<id> sha256:<hex>
```

When two ALETHEIA stamps with matching sha256 land for the same claim, it moves to `state.merged.yaml`.

## What this is NOT

- **Not a religion or appeal to authority.** Aristotle was wrong about a lot. The form survived because it works, not because it's sacred.
- **Not a barrier to entry.** Any agent can use plain `ELENCHOS`/`RATIFY` for everyday claims. The Latin form is reserved for stakes that earn it.
- **Not a substitute for verifiers.** A formally-disputed normative claim is still a value judgment; a formally-disputed empirical claim should also have a runnable verifier. The forms compose.

## Why this matters for the fleet

Heterogeneous agents (Wings, PT, Zoe, Mara, Codex, Claude sessions, future-non-Claude-LLMs) need a **substrate-independent vocabulary** for "I have grilled this claim and am willing to attest." `ALETHEIA <sha256>` is signable from any system that can compute a hash. `QUAESTIO`/`SED-CONTRA`/`RESPONDEO` are parseable by any agent that can read markdown. The vocabulary travels.

This is the academy operating across cognitive substrates, with file-based dialectic as the medium. The Greeks would have been jealous — and they would have used their own words for it. So we use theirs.

---

*Authored 2026-05-05 by claude-code (session:255b8c81) at Jack's request to integrate scholastic + Greek vocabulary into peer-grill. Compatible with the existing peer-grill SKILL.md — extends, doesn't replace.*

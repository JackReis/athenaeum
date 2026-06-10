# Plan: Merge PR #5 into `main`, Gated on Gemini Code Review

**Date:** 2026-06-10
**PR:** [#5](https://github.com/JackReis/athenaeum/pull/5) `fix(athenaeum): disambiguate skill triggers from grill-each-other pack`
**Branch:** `claude/content-code-review-OSZ7w` → `main`
**Author of plan:** Release engineering (Claude session)

PR #5 rewrites four SKILL.md frontmatter descriptions in the `athenaeum` pack so their trigger phrases no longer collide with the `grill-each-other` pack, plus README count/badge updates and session/tracking artifacts. CI is fully green on head `c851b06` and the PR is mergeable-clean. This plan gates the merge on an external code review by a Gemini model (3.1 Pro or 3.5 Flash, executed by the user's fleet — no Gemini tooling exists in this harness), defines triage rules for findings, and specifies a squash merge via the GitHub MCP `merge_pull_request` tool, followed by post-merge hygiene (branch deletion, main CI verification, ledger entry).

---

## 1. Goal / Non-goals

### Goal
1. Obtain a structured code review of PR #5 from Gemini 3.5 Flash (recommended) or 3.1 Pro.
2. Triage findings against explicit severity rules; fix, defer, or dismiss each with a recorded rationale.
3. Squash-merge PR #5 into `main` once the review gate passes and CI is green.
4. Complete post-merge hygiene: delete head branch, verify `main` CI, append ledger entry, unsubscribe from PR activity.

### Non-goals
- No re-scoping of the PR's content (the skill-description wording itself was settled in the authoring session).
- No changes to `marketplace.json` / `marketplace.extended.json` — verified unnecessary this session (catalog stores pack-level descriptions only; per-skill frontmatter is not synced).
- No CI/workflow changes (the skipped `automerge` / `enable-auto-merge` workflows stay as-is).
- No release/version bump — this is a fix-level docs/metadata merge, not a release.
- This plan does not execute the merge; it specifies how the fleet/operator executes it.

---

## 2. Current State (ground truth, refreshed 2026-06-10)

| Item | Value |
|---|---|
| PR state | Open, ready (not draft), `mergeable_state: clean`, not merged |
| Head / base | `c851b06` / `main` @ `4bff116` |
| Size | 4 commits, 8 files, +149 / −8 |
| CI on `c851b06` | All green: `validate`, `CodeQL`, `Analyze Code (python\|javascript\|typescript)` |
| Skipped workflows | `automerge`, `enable-auto-merge` (key off labels/draft state — expected) |
| Catalog sync | Not required (pack-level descriptions only in marketplace catalogs) |

**Diff composition:**

| Group | Files | Risk |
|---|---|---|
| Skill descriptions | `plugins/skill-enhancers/athenaeum/{athenaeum-design,athenaeum-reconcile,athenaeum-ratify,athenaeum-audit}/SKILL.md` — frontmatter `description` only | Behavioral-metadata: changes when skills *trigger*, not what they *do* |
| Docs | `README.md` (skill count 26→27, athenaeum pack 4→5, schema-badge footnote) | Cosmetic |
| Artifacts | `scratch/20260606-final-report.md`, `tracking/commit-log.md`, `tracking/time-ledger.md` | Inert (session report + lifecycle ledger) |

No executable code paths change. Blast radius: skill-activation behavior for one pack + README accuracy.

---

## 3. Reviewer-Model Decision: Gemini 3.1 Pro vs 3.5 Flash

### Rubric

| Criterion | Favors 3.1 Pro (deep/slow) | Favors 3.5 Flash (fast/cheap) | This PR |
|---|---|---|---|
| Executable code changed | Yes | No | **No** → Flash |
| Blast radius | Cross-cutting / HIGH | Localized / LOW | **Low** (1 pack, 4 descriptions) → Flash |
| Subtle-logic risk (concurrency, security, parsing) | Present | Absent | **Absent** → Flash |
| Review task type | Architectural judgment | Consistency / factual checking | **Consistency**: trigger-phrase overlap, count arithmetic, YAML validity → Flash |
| Diff size | >1k lines or many files | <500 lines | **+149/−8** → Flash |
| Cost of a missed defect | Hard-to-revert, prod-facing | Trivially revertible | **One-commit revert** → Flash |

### Recommendation: **Gemini 3.5 Flash.**

**Trade-off, stated explicitly:** 3.1 Pro would reason more deeply about whether the new trigger phrasing *actually* disambiguates from `grill-each-other` semantics — the one place real judgment is needed. We accept the small risk of a shallower semantic read because (a) the disambiguation intent was already human/Claude-authored deliberately, (b) the failure mode (a skill occasionally mis-triggering) is non-destructive and observable, and (c) revert is a single squash-commit revert. The review's main value here is a second pair of eyes on consistency, frontmatter validity, and the README arithmetic — squarely Flash-grade work.

**Escalation clause:** If Flash returns ≥1 *blocker* or ≥2 *major* findings, escalate the delta to 3.1 Pro for a confirming pass before acting (cheap insurance against Flash false positives/negatives).

---

## 4. Phased Plan

### Phase 0 — Pre-review readiness

| # | Step | Tool / command |
|---|---|---|
| 0.1 | Confirm PR still open, ready, `mergeable_state: clean` | `mcp__github__pull_request_read` (method: get) on `JackReis/athenaeum` #5 |
| 0.2 | Confirm CI green on head SHA `c851b06` | `mcp__github__pull_request_read` (method: get_status); expect `validate`, `CodeQL`, all `Analyze Code (*)` = success |
| 0.3 | Confirm branch is up to date with `main` (base still `4bff116`; no new commits on `main` since) | `mcp__github__list_commits` on `main`; if `main` moved, `mcp__github__update_pull_request_branch` then re-await CI |
| 0.4 | Scope sanity: file list matches the 8 expected files, no surprise additions since last refresh | `mcp__github__pull_request_read` (method: get_files); diff against table in §2 |
| 0.5 | Decide artifact question (see Risks §7-R3): keep `scratch/` + `tracking/` files in PR, or split | Maintainer judgment; default = **keep** (house pattern: lifecycle ledger rides with the change) |

**Verification:** All four checks pass; file list byte-identical to §2.
**Gate G0:** Any failure → stop; rebase/fix and restart Phase 0. Do not hand a stale diff to Gemini.

### Phase 1 — Obtain the Gemini review (executed by user's fleet; no Gemini tool in this harness)

| # | Step | Mechanism |
|---|---|---|
| 1.1 | Export review input: full unified diff of PR #5 (`gh pr diff 5` or GitHub `.diff` URL), PR title/body, and the *current* `grill-each-other` pack skill descriptions as collision-check context | Fleet operator |
| 1.2 | Run Gemini 3.5 Flash with the reviewer prompt below | Fleet (CLI/API — wiring is the operator's choice; see Open Questions) |
| 1.3 | Capture output as structured findings; post the full review as a PR comment for the audit trail | `mcp__github__add_issue_comment` on #5 |

**Reviewer prompt / rubric (hand to Gemini verbatim, with diff attached):**

> You are reviewing a docs/metadata-only PR for a Claude Code plugin marketplace. Review ONLY the attached diff. Check:
> 1. **Trigger disambiguation (primary):** Do the four rewritten SKILL.md `description` fields clearly brand triggers to "athenaeum" and avoid overlap with the attached grill-each-other pack descriptions? Flag any phrase still likely to collide.
> 2. **Frontmatter validity:** YAML remains parseable; `name` and `description` present; no schema fields accidentally removed; description style consistent across the 4 skills.
> 3. **README arithmetic:** Skill count 26→27 and athenaeum pack 4→5 are internally consistent with each other and the badge footnote.
> 4. **Artifacts:** scratch/tracking files contain no secrets, credentials, or personal data.
> Output findings as a list, each tagged exactly one of: `BLOCKER` (must fix before merge), `MAJOR` (should fix before merge), `MINOR` (fix or defer), `NIT` (optional). For each: file, line/excerpt, issue, suggested fix. If none, output "NO FINDINGS". Do not propose scope expansions beyond the diff.

**Verification:** Review artifact exists as a PR comment; every finding carries exactly one severity tag.
**Gate G1:** Unparseable/empty review or off-scope rambling → re-run once with the same prompt; second failure → escalate to Gemini 3.1 Pro.

### Phase 2 — Triage findings

**Decision rules (decider: repo maintainer — jackareis; this plan's authoring agent may pre-classify but not finalize):**

| Severity | Default disposition | Rule |
|---|---|---|
| BLOCKER | Fix now | No merge until resolved or maintainer-dismissed with written rationale |
| MAJOR | Fix now | Defer only if it's outside the diff's scope → open issue, link on PR |
| MINOR | Defer with issue OR fix now if <5 min | `mcp__github__issue_write` to create follow-up; reference issue # in PR comment |
| NIT | Dismiss or batch-fix | No issue required; one-line acknowledgment in triage comment |
| Hallucinated / factually wrong | Dismiss with rationale | Must quote the evidence contradicting the finding (e.g. the actual file content) |

| # | Step | Tool |
|---|---|---|
| 2.1 | Classify each finding per table above | Maintainer + agent |
| 2.2 | Record triage table (finding → disposition → rationale) as a PR comment | `mcp__github__add_issue_comment` |
| 2.3 | Open deferred-work issues, link them in the triage comment | `mcp__github__issue_write` |

**Verification:** Every Gemini finding has a recorded disposition on the PR. Zero unaddressed BLOCKER/MAJOR.
**Gate G2:** Go = no open BLOCKER/MAJOR → Phase 3 (if fixes needed) or Phase 4 (if none). No-go = unresolved BLOCKER without maintainer sign-off.

### Phase 3 — Apply fixes (only if Phase 2 produced fix-now items; else skip)

| # | Step | Tool / command |
|---|---|---|
| 3.1 | Make edits on `claude/content-code-review-OSZ7w` | Local edit, or `mcp__github__push_files` to head branch |
| 3.2 | Commit with message `fix(athenaeum): address Gemini review findings on PR #5` | `git commit` / push_files |
| 3.3 | Await CI on new head SHA | `mcp__github__pull_request_read` (get_status) until all green |
| 3.4 | Re-review **only the delta** (`git diff c851b06..HEAD`) with Gemini 3.5 Flash, same prompt scoped to "verify prior findings are resolved; review only this incremental diff" | Fleet |
| 3.5 | Post delta-review result to PR | `mcp__github__add_issue_comment` |

**Verification:** CI green on new head; delta review returns NO FINDINGS or NIT-only.
**Gate G3:** New BLOCKER/MAJOR from delta review → loop back to Phase 2. More than 2 loops → stop, reassess scope with maintainer (the PR may be hiding a real design disagreement).

### Phase 4 — Merge

**Merge method: squash.** Justification:
- 4 commits are incremental authoring steps of one logical change; history value on `main` is one atomic unit.
- Squash makes Phase 7 rollback a single `git revert <sha>` with no `-m` parent ambiguity.
- Keeps `main` linear, matching a docs/metadata fix's footprint.
- (Merge-commit would be preferred only if house style mandates it — see Open Questions Q3.)

| # | Step | Tool |
|---|---|---|
| 4.1 | Final pre-flight: re-run Phase 0 checks 0.1–0.3 (state can drift during review turnaround) | `mcp__github__pull_request_read` |
| 4.2 | Merge | `mcp__github__merge_pull_request` — owner `JackReis`, repo `athenaeum`, pullNumber `5`, merge_method `squash`, commit_title `fix(athenaeum): disambiguate skill triggers from grill-each-other pack (#5)`, commit_message summarizing the 4 description rewrites + README counts + review gate (link to Gemini review comment) |
| 4.3 | Confirm merged | `mcp__github__pull_request_read` (get) → `merged: true`, capture merge SHA |

**Verification:** PR shows merged; `main` HEAD = squash commit.
**Gate G4:** `merge_pull_request` failure (e.g. branch protection, drift) → diagnose, re-run 4.1; never force.

### Phase 5 — Post-merge

| # | Step | Tool / command |
|---|---|---|
| 5.1 | Delete head branch `claude/content-code-review-OSZ7w` (if not auto-deleted by repo settings) | `gh api -X DELETE repos/JackReis/athenaeum/git/refs/heads/claude/content-code-review-OSZ7w` or GitHub UI |
| 5.2 | Verify `main` CI green on the squash commit (`validate`, `CodeQL`, analyzers) | `mcp__github__actions_list` / `actions_get` filtered to merge SHA |
| 5.3 | Append ledger entry: merge SHA, PR #5, review model used, finding counts by severity, dispositions | `python3 tools/ledger/ledger.py` (per its usage; entry mirrors `tracking/commit-log.md` conventions) |
| 5.4 | Unsubscribe from PR activity | `mcp__github__unsubscribe_pr_activity` for #5 |
| 5.5 | Session log per repo policy (`logs/sessions/2026-06/`) noting the merge | Manual |

**Verification:** Branch gone; `main` CI green; ledger entry committed.
**Gate G5 (terminal):** `main` CI red post-merge → trigger Rollback (§6) immediately.

---

## 5. Decision Gates Summary

| Gate | Phase | Pass criteria | On fail |
|---|---|---|---|
| G0 | 0 | PR open+clean, CI green on head, base current, file list = expected 8 | Fix/rebase, restart Phase 0 |
| G1 | 1 | Structured Gemini review captured on PR, all findings severity-tagged | Re-run once; then escalate to 3.1 Pro |
| G2 | 2 | Zero unresolved BLOCKER/MAJOR; all dispositions recorded on PR | Phase 3 fixes, or maintainer-dismissal with rationale |
| G3 | 3 | CI green on new head; delta review clean (≤ NIT) | Loop to Phase 2; >2 loops → stop and reassess |
| G4 | 4 | Pre-flight re-pass + `merged: true` returned | Diagnose, never force-merge |
| G5 | 5 | `main` CI green on squash commit | Execute rollback (§6) |

---

## 6. Rollback / Safety

**Revert procedure (squash merge → single-parent commit, no `-m` needed):**

```bash
git checkout main && git pull
git revert <squash-sha>          # if a merge commit were used instead: git revert -m 1 <merge-sha>
git push origin main             # or via a revert PR if branch protection requires
```

Or via GitHub UI: PR #5 → "Revert" button (creates a revert PR — preferred under branch protection).

**Why this is low-risk to reverse:**
- Pure content: 4 YAML description strings, README text, inert scratch/tracking files. No build outputs, no `marketplace.json` regeneration, no schema/code dependencies.
- No downstream consumer pins these descriptions; worst post-merge symptom is a skill trigger phrase reverting to the ambiguous wording — exactly the pre-PR state.
- Squash makes the revert a clean inverse of one commit; re-landing later is `git revert <revert-sha>` or reopening the branch.

---

## 7. Risks & Mitigations

| ID | Risk | Likelihood | Mitigation |
|---|---|---|---|
| R1 | Gemini hallucinates a finding on description prose (e.g. invents a schema rule, misquotes grill-each-other triggers) | Medium — prose review invites confident-but-wrong style claims | Triage rule: dismissals must quote contradicting file content; escalation clause to 3.1 Pro for disputed BLOCKER/MAJOR; reviewer prompt forbids scope expansion |
| R2 | Scope creep from review ("while you're here, rewrite all 27 skill descriptions") | Medium | Prompt restricts review to the diff; G2 rule routes out-of-diff MAJORs to follow-up issues, never into this PR |
| R3 | `scratch/20260606-final-report.md` + `tracking/*` arguably don't belong in a feature PR — pollutes `main` history and the squash commit | Low impact | **Flagged; recommendation: keep.** House pattern treats the lifecycle ledger as part of the change record, files are inert, and splitting would burn a CI cycle + second review for zero behavioral gain. If maintainer disagrees at step 0.5: drop the 3 files from the branch, force-push, re-run CI, proceed — review prompt item 4 still screens them for secrets either way |
| R4 | `main` drifts during review turnaround (review is async, fleet-executed) | Medium | Gate G4 step 4.1 re-checks base currency immediately before merge; `update_pull_request_branch` if needed |
| R5 | Skipped `automerge`/`enable-auto-merge` workflows fire unexpectedly if someone adds a label mid-review | Low | Manual merge path chosen deliberately; do not apply automerge labels during this flow (see Q4) |
| R6 | Flash under-reviews the semantic disambiguation (the one judgment-heavy item) | Low-medium | Accepted per §3 trade-off; escalation clause + trivial revert bound the damage |

---

## 8. Open Questions

| # | Question | Why it matters | Default if unanswered |
|---|---|---|---|
| Q1 | Who holds merge rights on `JackReis/athenaeum` — does the harness token pass branch protection, or must jackareis merge? | Determines whether step 4.2 runs via MCP or is handed to the maintainer | Attempt via `merge_pull_request`; on 403/405, hand off to maintainer with this plan's §4 |
| Q2 | How is Gemini wired in the fleet — CLI, CI job, or manual paste of the diff? | Affects Phase 1 turnaround and whether the review comment is auto-posted | Assume manual/CLI; operator posts review comment per step 1.3 |
| Q3 | House style: is squash actually preferred, or does the repo's history use merge commits? | §4 merge-method choice | Squash (justified in §4); spot-check `git log --merges main` before 4.2 costs nothing |
| Q4 | Should the `automerge` / maintainer-ready label flow be used instead of manual merge once the review gate passes? | Could replace Phase 4 with `enable_pr_auto_merge` | Manual merge — the Gemini gate is external to CI, so auto-merge can't see it; keep the human at G2/G4 |
| Q5 | Does `tools/ledger/ledger.py` have a defined CLI for merge events, or is the entry format ad hoc? | Step 5.3 exactness | Inspect `python3 tools/ledger/ledger.py --help` at execution time; mirror the most recent `tracking/commit-log.md` entry shape |

---

*Plan complete. Execution owner: jackareis + fleet. No repo files other than this plan were created or modified.*

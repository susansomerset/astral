# AST-1574 — Clean origin/tests branch and harden validation gate

<!-- linear-archive: AST-1574 archived 2026-09-09 -->

## Linear archive (AST-1574)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1574/clean-origintests-branch-and-harden-validation-gate  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1568

### Description

### Purpose

`merge-child` for [AST-1573](https://linear.app/astralcareermatch/issue/AST-1573/artifact-catalog-registry-implement-pattartifactmanage-catalog) blocked because `origin/tests` carries a `git pull`-style merge commit that should never be on the tests branch. `validate-sub-log.sh` correctly rejected it, but the pollution originated upstream at Betty's push to `origin/tests` and slipped past `validate-tests-branch.sh`. This ticket does two things: **(1)** rebuild `origin/tests` as a clean additive chain, and **(2)** harden the pre-push gate so a merge commit can't re-enter `tests` under the current scan window.

### Background — what happened

* `origin/tests` HEAD carries `1b236a3e6` — `"Merge remote-tracking branch 'origin/ftr/AST-1547-job-resume-content-not-saving' into dev"` (a legitimate dev-landing merge, authored 2026-09-01).
* It reached `tests` because `55074a4ae "docs(AST-1547): mirror epic registry Threads"` was cut from `origin/dev` instead of from the prior `origin/tests` tip (`82423d73b "resolve(AST-1562): — clean"`). Every additive commit since is stacked on top of the merge.
* Betty's `merge-tests(AST-1573)` (`3290a5f19`) then merged all of `origin/tests` into the sub, pulling `1b236a3e6` into the `origin/sub/AST-1568/AST-1573-… --not origin/ftr/AST-1568-artifact-catalog` range.
* `validate-sub-log.sh` matched `^Merge remote-tracking branch` and failed with `git pull merge on sub`.
* The [AST-1573](https://linear.app/astralcareermatch/issue/AST-1573/artifact-catalog-registry-implement-pattartifactmanage-catalog) block later cleared only incidentally — `1b236a3e6` also landed on `origin/ftr/AST-1568`, so `--not origin/ftr` now filters it out. `origin/tests` is still polluted and will re-block the next child whose ftr does not yet contain that dev merge.
* `validate-tests-branch.sh` is the intended guardrail (it rejects `^Merge remote-tracking branch` and `Merge origin/(dev|sub/|ftr/)`), but it only scans `refs/heads/tests --not origin/tests` capped at `--depth 20`. Once the bad commit is pushed, it is outside the window on every subsequent run.

### Functional scope

1. **Clean** `origin/tests` — rebuild the tip as a pure additive chain of `test()/docs()` commits from the last clean base (`82423d73b`), dropping `1b236a3e6`. Preserve tree content of every additive commit.
2. **Re-cut dependent work** — any outstanding `merge-tests(AST-NNN)` / sub branches built on the polluted `tests` tip get re-based onto the cleaned tip by their owners.
3. **Harden** `validate-tests-branch.sh` — detect a forbidden merge anywhere on the branch's additive range, not just within the last 20 unpushed commits.

### Component scope

* `origin/tests` (branch history) — **rewritten** — cherry-pick `55074a4ae`, `c0b93237c`, `ff0217418`, `e2cdc3734`, `318ed7e73` onto `82423d73b`; force-push. (Confirm this list against `git log origin/tests --format='%h %s' 82423d73b..origin/tests` at execution time.)
* scripts/git/validate-tests-branch.sh — **modified** — replace the `--depth 20` / `--not origin/tests` scan with a full walk of the additive range and a structural check.
* scripts/git/validate-sub-log.sh — **unchanged** — it behaved correctly; note in the ticket that no change is wanted here.

### Technical scope

* `tests` scrub: from a clean worktree, `git checkout -B tests-clean 82423d73b`, cherry-pick the additive commits in order, verify `git diff origin/tests..tests-clean` is empty, then `git push --force-with-lease origin tests-clean:tests`. Announce in the [AST-1568](https://linear.app/astralcareermatch/issue/AST-1568/implement-pattartifactmanage-catalog) thread and to Betty so sub owners re-cut.
* **Gate hardening:** define the additive base as `git merge-base origin/tests origin/main` (or a recorded clean marker) and walk `origin/tests --not <base>`. For each commit, fail if the subject matches `^Merge `, `^Merge remote-tracking branch`, or `Merge origin/(dev|sub/|ftr/)`, **or** if the commit has >1 parent and the subject does not match `^merge-tests\(AST-[0-9]+\):`. Drop the `head -n DEPTH` cap; keep `--depth` only as an optional override.
* No API/UI/runtime changes. Scripts-only.

### Architectural definition

**Patterns to reuse** — none; workflow-script maintenance.
**New patterns proposed** — none.
**Applicable statutes**

* `astral.standards.in-scope-only` — change limited to `scripts/git/` + the `tests` branch; no runtime/canon edits.
* Per team memory, `scripts/` is exempt from canon audits — no directive registration needed.

### Acceptance criteria

1. `git merge-base --is-ancestor 1b236a3e6 origin/tests` returns non-zero (commit no longer on `tests`).
2. `git log origin/tests --not $(git merge-base origin/tests origin/main)` contains only single-parent `test()/docs()` commits and `merge-tests(AST-NNN):` merges.
3. `git diff` between old and new `tests` tips is empty (no test/doc content lost).
4. `validate-tests-branch.sh` fails fast when a `Merge remote-tracking branch …` or `Merge origin/dev` commit is present anywhere in the additive range, proven by a repro fixture or a documented manual run against the pre-scrub tip.
5. `validate-tests-branch.sh` still passes on the cleaned `tests` tip.
6. A fresh `merge-child.sh` dry-run for a child stacked on `ftr/AST-1568` passes `validate-sub-log.sh` with no `git pull merge on sub` finding.

### Open questions

1. Clean base — confirm `82423d73b` is the correct last-clean point, or pick a recorded marker/tag instead of a bare SHA.
2. Which sub/ftr branches besides `AST-1568/AST-1573` are currently built on the polluted `tests` tip and need re-cutting — enumerate before the force-push.
3. Should the additive base be `merge-base … origin/main`, or should we introduce a durable `tests-clean-base` ref that the land flow advances?

### Comments

#### chuckles — 2026-09-02T19:36:00.881Z
Done — option A.

- `origin/tests` force-with-lease cleaned; `1b236a3e6` no longer ancestor.
- `origin/tests-clean-base` at `82423d73b`; gate scans full additive range.
- Gate fail proven on pre-scrub tip; pass on cleaned tip. Script also on `origin/dev` (`76747cbe`).
- Announced on AST-1568 for Betty re-cut of AST-1573 sub if needed.

#### susan — 2026-09-02T19:32:52.424Z
yes\\

#### chuckles — 2026-09-02T18:57:11.343Z
[check-linear] answered — harden `validate-tests-branch.sh` so pull/dev merges cannot land on `origin/tests` (that is what later fails merge-child); one-time scrub of the current pollution is separate. I will take option A (durable marker at `82423d73b`, gate walks tip `--not` marker) so you do not have to pick the archaeology — reassign Chuckles when you want that run. Also confirm cherry-pick + force-with-lease on `tests` is an intentional one-time exception to `orch.git.no-cherry-pick-rebase-force`.

#### susan — 2026-09-02T18:56:08.556Z
@chuckles  I'm afraid I don't have enough understanding of the issue to give you guidance.  Is there a better way to stop the merge-child blockers from happening going forward, because they are becoming regular events.

#### chuckles — 2026-09-02T18:46:34.966Z
@susan blocked on open question 3 before any force-push.

Resolved by inspection:
1. Clean base `82423d73b` confirmed — first-parent tip before `1b236a3e6`; additive stack is exactly `55074a4ae`, `c0b93237c`, `ff0217418`, `e2cdc3734`, `318ed7e73`.
2. Re-cut needed: only `origin/sub/AST-1568/AST-1573-artifact-catalog-registry` contains the polluted `origin/tests` tip. `origin/ftr/AST-1568` already has `1b236a3e6` via its own land path.

Blocker — AC2 vs Component scrub:
- Cherry-pick onto `82423d73b` leaves all of that commit's ancestry reachable.
- `git merge-base origin/tests origin/main` = `aa5b552c`; the range tip `--not` that base still contains many first-parent `Merge remote-tracking branch …` commits under `82423d73b` (e.g. via `17698de4`).
- So AC2 as written cannot pass after the listed scrub.

Need your call:
- (A) Durable marker at `82423d73b` (or advancing `tests-clean-base` ref); gate walks tip `--not` marker; revise AC2 to match — or
- (B) Full history rewrite of `tests` back to merge-base(main) keeping only legitimate additive commits — larger than the cherry-pick list.

Also confirm this Task is an intentional exception to `orch.git.no-cherry-pick-rebase-force` (ticket already asks for cherry-pick + `--force-with-lease` on `tests`).

---

_Implementation detail may live in git history on `origin/dev`._

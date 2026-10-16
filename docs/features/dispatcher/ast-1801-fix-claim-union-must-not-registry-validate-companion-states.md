# AST-1801 — fix: claim union must not registry-validate companion states

<!-- linear-archive: AST-1801 archived 2026-10-02 -->

## Linear archive (AST-1801)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1801/fix-claim-union-must-not-registry-validate-companion-states  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1800 — Dispatcher performing data validation  
**Blocked by / blocks / related:** parent: AST-1800

### Description

## What this implements

Stop claim-path registry validation from rejecting AST-1798 suffix-always companions that are absent from the entity-state registry (e.g. `HOMEPAGE_READY_RETRY` on `prefilter_company`). When `states=` is provided, claim helpers claim the union without requiring every member ∈ registry; single-`state` callers keep the existing registry check.

## Scope

## Component scope

* `src/core/roster.py` — **modified** — `get_new_company_batch` is the raise site on this log; relax multi-state claim validation against `COMPANY_STATES`.
* `src/core/tracker.py` — **modified** — same "every `states` member ∈ registry" loop on `get_new_job_batch`; same AST-1798 contract for jobs.
* `src/core/candidate.py` — **modified** — same pattern on the candidate claim helper; same contract for candidates.

## Technical scope

- [X] `src/core/roster.py` — **modified function** `get_new_company_batch`: when `states=` is set, do not raise for members missing from `COMPANY_STATES`; still validate primary `state` when `states` is None so single-state callers stay bound.
- [X] `src/core/tracker.py` — **modified function** `get_new_job_batch`: same multi-state vs single-state validation split for job claims.
- [X] `src/core/candidate.py` — **modified function** (candidate claim helper with the `state must be one of` / `for s in states` loop): same split so candidate `_RETRY` companions are not registry-gated at claim time.

## Boundaries

Do not add synthetic `_RETRY` keys to `COMPANY_STATES` / job / candidate registries. Do not change `dispatch_claim_states` pairing (already suffix-always on AST-1798). Orphaned mini-parent is AST-1800 (no ancestor box checked).

## Notes for planning

Parent AST-1800 Description (As-is / To-be / Proposed steps) is authoritative. Susan: dispatcher/claim path should not re-validate data — claim by trigger claim-union only. Raise site in the log: `roster.get_new_company_batch`; mirror on job/candidate claim helpers that share the loop. Historical feature-doc home (not an approved ancestor): `docs/features/dispatcher/ast-641-union-claim-and-count-for-primary-retry-trigger-states-auto-retry.md` — plan-fix patches an existing feature doc, never creates a new one.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1800-claim-union-no-registry-validate`, child `sub/AST-1800/AST-1801-claim-union-no-registry-validate`. Created at bug-fix.

### Comments

#### radia — 2026-09-25T21:24:31.332Z
[code-rubric] PROCEED (Commit: 2678ae8c) clean claim registry fix; TESTS:REVISE owned by gap AST-1802

#### joan — 2026-09-25T21:19:29.845Z
[board-joan]  CANON: OK

Dropping multi-state registry gates on claim helpers matches `patt.task.dispatch-retry` (companion need not exist in registry) and does not amend `astral.dispatch.entity-state-bound` / claim-process-release. No F3 validate-plan.

context_tokens≈12000

#### betty — 2026-09-25T21:18:54.310Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/roster.md — missing coverage — no test that get_new_company_batch(states=[HOMEPAGE_READY, HOMEPAGE_READY_RETRY]) does not raise when companion ∉ COMPANY_STATES (live repro); single-state reject stays; mirror job/candidate if board expands

#### ada — 2026-09-25T21:16:56.644Z
`origin/sub/AST-1800/AST-1801-claim-union-no-registry-validate` @ `a0e2fac6969e5ab3b749aed53ff2daa9270125e5` · claim skips registry

---

_Implementation detail may live in git history on `origin/dev`._

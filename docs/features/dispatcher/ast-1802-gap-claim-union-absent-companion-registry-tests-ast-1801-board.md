# AST-1802 — gap: claim-union absent-companion registry tests (AST-1801 board)

<!-- linear-archive: AST-1802 archived 2026-10-02 -->

## Linear archive (AST-1802)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1802/gap-claim-union-absent-companion-registry-tests-ast-1801-board  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1800 — Dispatcher performing data validation  
**Blocked by / blocks / related:** parent: AST-1800

### Description

## What this implements

Test gap from \[board-betty\] TESTS: REVISE on AST-1801 — assert get_new_company_batch(states=\[HOMEPAGE_READY, HOMEPAGE_READY_RETRY\]) does not raise when companion ∉ COMPANY_STATES; single-state reject stays; mirror job/candidate if in scope; bible note under roster.

## Scope

### Component scope

* `docs/test-bible/core/roster.md` — **modified** — missing coverage for multi-state claim with registry-absent companion.
* `tests/component/core/test_roster.py` — **modified** — assert get_new_company_batch with states including HOMEPAGE_READY_RETRY does not raise; single-state reject still raises.
* `tests/component/core/test_tracker.py` and/or `tests/component/core/test_candidate.py` — **modified if needed** — mirror job/candidate claim helpers for the same contract.

### Technical scope

- [X] Roster (and mirrored job/candidate) claim tests — **new or revised cases** that fail against pre-AST-1801 product (ValueError on absent companion) and pass after product lands; single-state invalid state still rejects.
- [X] `docs/test-bible/core/roster.md` — **modified bible entry** naming the new coverage.

## Boundaries

Product code for the fix stays on AST-1801. This gap is test/bible only (Betty).

## Notes for planning

Board: \[board-betty\] TESTS: REVISE — docs/test-bible/core/roster.md — missing coverage — no test that get_new_company_batch(states=\[HOMEPAGE_READY, HOMEPAGE_READY_RETRY\]) does not raise when companion ∉ COMPANY_STATES (live repro); single-state reject stays; mirror job/candidate if board expands.

### Comments

#### radia — 2026-09-25T21:33:09.389Z
[code-rubric] PROCEED — test gap absent-companion claim asserts + bible; [bug-repro] asserts right thing

#### betty — 2026-09-25T21:30:14.766Z
[bug-repro]
`origin/sub/AST-1800/AST-1802-claim-union-no-registry-validate-tests` @ `a811f3b3` · absent-companion claim repro

[qa-handoff]
@Ada Lovelace — test-tree landed (engineer hook). Product tip already has AST-1801 fix; Betty verified 3 red on pre-fix `tests` tip, 4 green with publish-tip product overlaid. Manifest for test-fix:
- `test_roster.py::TestBatchApi::test_get_new_company_batch_states_allows_registry_absent_companion` ([bug-repro])
- `test_roster.py::TestBatchApi::test_get_new_company_batch_rejects_unknown_state`
- `test_tracker.py::TestBatchApi::test_states_list_allows_registry_absent_companion`
- `test_candidate.py::TestAst1259CandidateBatchApi::test_states_list_allows_registry_absent_companion`
- bible: `docs/test-bible/core/roster.md` § AST-1802 · AST-1801

#### ada — 2026-09-25T21:27:47.527Z
[qa-handoff]
@Betty White — correction: engineer hook blocked Ada from committing test-tree on make-fix. 4 asserts greened locally then reverted to keep epic worktree clean. Land from plan `## Bug: AST-1802` Proposed change via astral-tests → `test(AST-1802)` → `merge-tests(AST-1802)` onto `origin/sub/AST-1800/AST-1802-claim-union-no-registry-validate-tests`.

Optional host draft: `~/.cursor/tmp/AST-1802-test-gap.patch` (same edits). Staying **Plan Approved**; assignee Betty.

#### ada — 2026-09-25T21:27:09.193Z
[qa-handoff]
@Betty White — AST-1802 is test/bible-only. Ada make-fix wrote + greened the asserts (4 passed) but the engineer pre-commit hook blocks `tests/` and `docs/test-bible/**` (`engineer hook: blocked path`). Please land via astral-tests → `test(AST-1802)` → `merge-tests(AST-1802)` onto `origin/sub/AST-1800/AST-1802-claim-union-no-registry-validate-tests`.

Plan: `## Bug: AST-1802` Proposed change on the feature doc.
Nodes:
- `test_roster.py::TestBatchApi::test_get_new_company_batch_states_allows_registry_absent_companion`
- `test_roster.py::TestBatchApi::test_get_new_company_batch_rejects_unknown_state` (unchanged, keep)
- `test_tracker.py::TestBatchApi::test_states_list_allows_registry_absent_companion`
- `test_candidate.py::TestAst1259CandidateBatchApi::test_states_list_allows_registry_absent_companion`
- `docs/test-bible/core/roster.md` § AST-1802 · AST-1801

Draft patch left at `/tmp/AST-1802-test-gap.patch` on this host (same edits as plan). Staying Plan Approved; assignee → Betty.

#### joan — 2026-09-25T21:24:30.337Z
[board-joan]  CANON: OK

Test/bible-only gap — lock absent-companion claim contract; no product or canon edits. F3 not triggered.

context_tokens≈14000

#### betty — 2026-09-25T21:23:30.448Z
[board-betty] TESTS: OK

#### ada — 2026-09-25T21:22:34.337Z
`origin/sub/AST-1800/AST-1802-claim-union-no-registry-validate-tests` @ `46cf814f3a2d1f2917ee0f8955480e78d4a308c2` · test gap planned

---

_Implementation detail may live in git history on `origin/dev`._

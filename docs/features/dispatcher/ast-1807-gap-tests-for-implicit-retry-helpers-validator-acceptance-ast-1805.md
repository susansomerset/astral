# AST-1807 — gap: tests for implicit _RETRY helpers + validator acceptance (AST-1805)

<!-- linear-archive: AST-1807 archived 2026-10-07 -->

## Linear archive (AST-1807)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1807/gap-tests-for-implicit-retry-helpers-validator-acceptance-ast-1805  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1804 — fetch type avail counts appear not to include _RETRY records  
**Blocked by / blocks / related:** parent: AST-1804

### Description

## What this implements

Test gap for AST-1805, from fix-board `[board-betty] TESTS: REVISE`. Add coverage for the implicit-retry helpers and for every validator's `{base}_RETRY` acceptance branch, plus a repro that fails on the pre-fix tree and passes once AST-1805 lands.

## Scope

Test tree and bible only, as named in Betty's board verdict:

* Bible: `docs/test-bible/utils/config.md`, `docs/test-bible/core/tracker.md`, `docs/test-bible/core/roster.md`, `docs/test-bible/core/candidate.md`, `docs/test-bible/ui/api/api_admin.md`.
* Repro: `transition_job_state` PASSED_DO → PASSED_GET_RETRY (an unregistered `{base}_RETRY`) raises on the pre-fix tree and succeeds after AST-1805.
* Helpers (names per the AST-1805 plan): `retry_of` / `retry_base` / `registered_base` / `is_registered_state` / `state_prior_states`. Cover the derived-prior rule, including cross-base feeders (`NEW_RETRY`, `WEBSITE_FOUND_RETRY`), retry self-drain back to base, and KeyError on an unregistered base.
* Per-validator acceptance branches: roster company transition, candidate transition, `is_valid_*_batch_claim_state`, `_dispatch_sort_by_for`, and both api_admin trigger-validation sites.

## Boundaries

No product `src/` changes (AST-1805 owns them). Do not touch the explicit-key / raw `prior_states` asserts in `test_config.py` (about line 3106); those flip with AST-1806's purge. Fail-destination must-not-resolve paths are already covered in test_consult / test_roster.

## Notes for planning

AST-1805's plan section: `docs/features/dispatcher/ast-641-union-claim-and-count-for-primary-retry-trigger-states-auto-retry.md` `## Bug: AST-1805`. Add a `## Bug: <this id>` section there. Betty lands the tests (qa-fix); engineers never edit `tests/`.

## Git branch (authoritative)

Parent `ftr/AST-1804-fetch-avail-retry`, child `sub/AST-1804/AST-1807-implicit-retry-tests`. Created at bug-fix.

### Comments

#### radia — 2026-09-26T22:44:46.982Z
[code-rubric] PROCEED (Commit: e3982492) Implicit retry tests OK

T1–T7 present; [bug-repro] substantive; closes the AST-1805 TESTS: REVISE bar.

#### ada — 2026-09-26T22:38:17.573Z
test-fix: `origin/sub/AST-1804/AST-1807-implicit-retry-tests` @ `e3982492` (sync(ftr) with AST-1806 merged; plan-doc conflict resolved as ftr's copy + the AST-1807 section appended — additions only, no product/test edits).

- [bug-repro] `test_tracker.py::TestTransitionJobState::test_ast1807_bug_repro_base_to_implicit_retry`: **red** on origin/dev `src/` (`ValueError: 'PASSED_GET_RETRY' not in allowed list`) → **green** on tip.
- Full `### AST-1807` manifest: 18/18 passed on tip, post-purge — no conflict with AST-1806.

#### ada — 2026-09-26T22:32:49.775Z
make-fix: no product change (fix already on ftr via AST-1805). `origin/sub/AST-1804/AST-1807-implicit-retry-tests` @ `6d47880e`, ftr merged. [bug-repro] `test_tracker.py::TestTransitionJobState::test_ast1807_bug_repro_base_to_implicit_retry` green; full `### AST-1807` bible manifest (config helpers + validators classes, tracker ×3, roster ×2, candidate ×3, api_admin ×1) = 18/18 passed. (Betty's handoff cited 35/35 — the manifest as listed collects 18; flagging the count only, no failures.)

#### betty — 2026-09-26T22:28:51.817Z
[bug-repro]
`origin/sub/AST-1804/AST-1807-implicit-retry-tests` @ `6d47880e` · repro red on dev, green on ftr

Repro node: `tests/component/core/test_tracker.py::TestTransitionJobState::test_ast1807_bug_repro_base_to_implicit_retry`. Red→green already observed: 15 fail on `origin/dev` product files (= `9f6536ce`), 35/35 pass on `ftr` (AST-1805). Manifest: `### AST-1807` in `docs/test-bible/{utils/config,core/tracker,core/roster,core/candidate,ui/api/api_admin}.md`. No AST-1806-owned raw `_RETRY` / `prior_states` asserts touched.

#### betty — 2026-09-26T22:23:40.332Z
[board-betty] TESTS: REVISE
What: no bible entry (utils/config.md, core/tracker.md, core/roster.md, core/candidate.md, ui/api/api_admin.md) — missing coverage — gap ticket is test-tree-only, so it routes to qa-fix (Betty lands T1–T7), not make-fix. Plan checked: target classes exist on ftr 65e3ca6f; T1/T2 expected values probed and match (NEW_RETRY/WEBSITE_FOUND_RETRY feeders, PASSED_GET_RETRY priors, JD_READY/REQUESTED_RESUME self-drain, NEW → None, RESUME_READY_RETRY priors gate NEW_CANDIDATE); probe retry states are unregistered, so it stays green through AST-1806. Corrected repro PASSED_GET → PASSED_GET_RETRY is the [bug-repro]; T6 values get verified in the qa-fix red→green pass.

#### joan — 2026-09-26T22:23:23.071Z
[board-joan]  CANON: OK

Test-tree + bible only; no statute/pattern text touched. F3 not triggered. Same shape as AST-1802.

#### ada — 2026-09-26T22:21:25.135Z
`origin/sub/AST-1804/AST-1807-implicit-retry-tests` @ `cf8afd24` · repro corrected: PASSED_GET→PASSED_GET_RETRY

---

_Implementation detail may live in git history on `origin/dev`._

# AST-2090 — Salvaged-batch split routing tests + bible (test gap for AST-2089)

<!-- linear-archive: AST-2090 archived 2026-10-16 -->

## Linear archive (AST-2090)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2090/salvaged-batch-split-routing-tests-bible-test-gap-for-ast-2089  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-2015 — [✅/Somerset] qualify_job_listings COMPLETED: 14 error(s) / 16 processed | qualify_job_listings-67d036c7-5729-4c3e-87e5-96800cea4e45  
**Blocked by / blocks / related:** parent: AST-2015

### Description

## What this implements

Test-tree and bible coverage for [AST-2089](https://linear.app/astralcareermatch/issue/AST-2089)'s salvage-on-envelope-failure path, routed here from Betty's fix-board `[board-betty] TESTS: REVISE` on AST-2089 (same shape as AST-2001 for AST-1996 and AST-2057 for AST-2053). No product source change.

## Scope

## Component scope

* `tests/component/core/test_agent.py` (modified). Add repro coverage: `do_task` on a rubric-encoded batch task whose envelope reports `agent_performance.status == "failure"` with `batch_entities` and decodable lines returns `salvaged_response`; an undecodable or schema-invalid payload returns `salvaged_response` None. Existing `TestAst1846DoTaskAgentFailureFlag` stays green (`parsed_response` None holds).
* `tests/component/core/test_consult.py` (modified). Add repro coverage: `_run_batch_consult` splits on `salvaged_response` — a fully graded passing line goes to `PASSED_JOBLIST`, a fully graded failing line goes to `FAILED_JOBLIST`, a missing or incomplete line goes to its retry holding (`NEW_RETRY`) with an `Agent failure: …` reason. Also assert the return shape (`agent_failure` / `errors` / `success`). The existing envelope-failure nodes stay green.
* `docs/test-bible/core/agent.md` (modified). New `AST-2089` block for the `salvaged_response` contract.
* `docs/test-bible/core/consult.md` (modified). New `AST-2089` block for the salvaged-batch split routing.

## Technical scope

* `tests/component/core/test_agent.py`: new test function(s) for the salvage / no-salvage branches of the envelope-failure path in `do_task`.
* `tests/component/core/test_consult.py`: new test function(s) for `_run_batch_consult` split routing and its return shape.
* Bible files: new manifest rows so the bible matches the tests.

## Acceptance criteria

* The repro tests pass on the AST-2089 tip and would have failed before it (whole batch to fail destinations, no `salvaged_response`).
* Existing `TestAst1846DoTaskAgentFailureFlag` and consult envelope-failure nodes still pass.
* Bible blocks match the tests.

## Boundaries

* No `src/` or `data/` change: AST-2089 owns the prompt fix and the product guard.
* Pre-existing `test_agent.py` / `test_consult.py` failures on ftr are out of scope.

## Notes for planning

Betty's verdict comment on AST-2089 (`[board-betty] TESTS: REVISE`) names the exact gaps. Doc to patch: `docs/features/consult/ast-1155-incomplete-grades-retry-holding-never-technical-fail.md`, with a `## Bug: <this id>` block alongside AST-2089's. Blocked by AST-2089 so the tests run against the shipped fix on `ftr`.

## Git branch (authoritative)

Parent `ftr/AST-2015-qualify-listing-isolation`; this child `sub/AST-2015/AST-2090-qualify-listing-isolation-tests`. Registry is authoritative.

### Comments

#### radia — 2026-10-09T02:30:35.009Z
[code-rubric] PROCEED (Commit: 8e751e38e) Bug-repro pins AST-2089 To-be

#### betty — 2026-10-09T02:27:38.521Z
[bug-repro]
`origin/sub/AST-2015/AST-2090-qualify-listing-isolation-tests` @ `d17c6ee86` · repro landed, red pre-fix, green tip

#### joan — 2026-10-09T02:25:16.995Z
[board-joan]  CANON: OK

#### betty — 2026-10-09T02:25:01.371Z
[board-betty] TESTS: REVISE
What: tests/component/core/test_agent.py + test_consult.py + docs/test-bible/core/{agent,consult}.md (no AST-2089 entry) — missing coverage — this ticket is the test work itself: qa-fix (F4) lands plan-fix #1–#4 as written (`TestAst2089DoTaskSalvagedResponse` after `TestAst1846DoTaskAgentFailureFlag`; `TestAst2089SalvagedBatchSplit` after `TestEncodedDecodeIsolation`; bible blocks after AST-2057 / AST-2001). [bug-repro] = `test_envelope_failure_salvages_clean_lines` + both params of `test_salvaged_lines_process_and_only_the_gap_fails`, red on pre-fix 22ff5e47a. Anchors verified on ftr tip e8119b1da (classes, `_batch_entities`/`_agent_rows`/`_api_response`, bible headings, `salvaged_response` in agent.py/consult.py). No existing test edited; AST-1846 / envelope-failure / TestEncodedDecodeIsolation nodes stay as guards. Engineer pass is verify-only.

#### hedy — 2026-10-09T02:24:15.308Z
`origin/sub/AST-2015/AST-2090-qualify-listing-isolation-tests` @ `cf219e82c` · salvage + split tests specified

---

_Implementation detail may live in git history on `origin/dev`._

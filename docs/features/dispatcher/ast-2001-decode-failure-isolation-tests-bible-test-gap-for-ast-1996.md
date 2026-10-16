# AST-2001 — Decode-failure isolation tests + bible (test gap for AST-1996)

<!-- linear-archive: AST-2001 archived 2026-10-16 -->

## Linear archive (AST-2001)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2001/decode-failure-isolation-tests-bible-test-gap-for-ast-1996  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1884 — [✅/Somerset] evaluate_meteorite COMPLETED: 1 error(s) / 1 processed | evaluate_meteorite-ee5b6a08-bbed-4025-bfbf-43c854270119  
**Blocked by / blocks / related:** parent: AST-1884

### Description

## What this implements

Test-gap sibling of [AST-1996](https://linear.app/astralcareermatch/issue/AST-1996), filed from Betty's `[board-betty] TESTS: REVISE` on that ticket. AST-1996 makes `_decode_payload` isolate a malformed grades-only line (returning a `decode_failures` entry instead of raising) and routes each failed entity through `_consult_batch_fail_dest`. This ticket lands the coverage for that change.

## Citations

Approved ancestor: AST-1155 (`docs/features/consult/ast-1155-incomplete-grades-retry-holding-never-technical-fail.md`). Board finding verbatim on AST-1996's `[board-betty]` comment.

## Scope

## Component scope

* `tests/component/core/test_agent.py` — modified — `test_rejects_bad_positions_and_trailing_meta` flips (`0|CRA2|extra` now yields a `decode_failures` entry, not a raise); new multi-line partial-decode test (repro A: one bad line + one clean line, clean line still decodes).
* `tests/component/core/test_consult.py` — modified — later-line routing in `_should_decode_as_encoded_line` (repro B: first line has no valid segment, a later line does); `_run_batch_consult` per-entity decode failure → first strike retry holding, second strike `error_state`, clean row for same entity wins, `success`/`errors` shape.
* `docs/test-bible/**` (core/consult.md and the agent decode entry) — modified — bible rows for `decode_failures` and the new routing coverage.

## Technical scope

* `tests/component/core/test_agent.py`: modified test + new test function(s) for multi-line partial decode — the old raise assertion becomes a `decode_failures` assertion.
* `tests/component/core/test_consult.py`: new test functions for multi-line encoded routing and per-entity decode-failure transitions — `agent.py` and `consult.py` are LOCKED_AT_100, so the new branches need coverage for the gate to go green.
* `docs/test-bible/**`: new/modified bible rows recording the above.

## Acceptance criteria

- [X] Every new branch AST-1996 adds in `agent.py` / `consult.py` is covered (LOCKED_AT_100 gate green).
- [X] Repro A and repro B each have a test that fails on the pre-fix tree and passes with AST-1996.

## Boundaries

No product code — that is AST-1996. Test tree + bible only (Betty lands them in qa-fix).

## Git branch (authoritative)

Parent `ftr/AST-1884-decode-line-retry`, child `sub/AST-1884/AST-2001-decode-line-retry-tests`. Blocked by AST-1996.

### Comments

#### radia — 2026-10-06T05:29:21.578Z
[code-rubric] PROCEED (Commit: d3473a040) Bug-repro locks AST-1996

#### hedy — 2026-10-06T05:28:13.080Z
`origin/sub/AST-1884/AST-2001-decode-line-retry-tests` @ `d3473a040` · bug-repro red→green confirmed

- **Red (pre-fix `57ed90983`):** Betty's `[bug-repro]` proof. All 5 repro nodes fail for the right reason (`ValueError` trailing content ×2, routing `is False`, `success is True`, `KeyError: 'decode_failed'`).
- **Green (merged tip):** the same 5 nodes run alone: `test_rejects_bad_positions_and_records_trailing_meta`, `test_ast1996_malformed_line_isolated_clean_line_decodes`, `test_routing_scans_past_fully_malformed_first_line`, `test_decode_failures_route_first_and_second_strike`, `test_clean_row_wins_over_decode_failure`. Result: **5 passed**.
- **Manifest:** `./scripts/testing/run_component_tests.sh tests/component/core/test_agent.py::TestDecodePayload tests/component/core/test_consult.py::TestEncodedDecodeIsolation -q` gives **11 passed**, exit 0.
- No product change. The ~60 failures that existed before AST-1996 are out of scope.

#### betty — 2026-10-06T05:25:59.390Z
[bug-repro]
`origin/sub/AST-1884/AST-2001-decode-line-retry-tests` @ `fe098451b` · repro red pre-fix, green tip

Proof:
- **Red at pre-fix `57ed90983`** (clean detached /tmp worktree): 5/7 new or edited nodes fail for the right reason.
  - `TestDecodePayload::test_rejects_bad_positions_and_records_trailing_meta` and `::test_ast1996_malformed_line_isolated_clean_line_decodes` both raise `ValueError: unexpected trailing content`.
  - `TestEncodedDecodeIsolation::test_routing_scans_past_fully_malformed_first_line` fails with `_should_decode_as_encoded_line(...) is False`.
  - `::test_decode_failures_route_first_and_second_strike` fails on `success is True`, because the old code treats J0/J1 as truncation misses.
  - `::test_clean_row_wins_over_decode_failure` fails with `KeyError: 'decode_failed'`.
  - The two guards (`clean_payload_has_no_decode_failures_key`, `notes_type_tail_is_not_a_decode_failure`) pass on both trees, as intended.
- **Green at the merged sub tip `fe098451b`** (includes AST-1996 `96bc0471d`): `TestDecodePayload` + `TestEncodedDecodeIsolation` + `test_should_decode_as_encoded_line_routing` give 12 passed. The `consult.py` loop body (L1718) and `decode failed on N IDs` append (L1824), plus the `agent.py` decode_failures lines, are now covered.
- **Out of scope:** `TestAst699LetterPipePositionPrefix::{test_position_prefixed_letter_pipe_bracket_tails,test_bare_letter_pipe_bracket_tails}` fail with `KeyError: 'jobs'` identically pre-fix and at tip. That is a pre-existing failure, not AST-1996.

Manifest: `docs/test-bible/core/consult.md` § AST-2001 (agent side: `core/agent.md` § AST-2001). @Hedy: test-fix is verify-only, no product change expected.

#### joan — 2026-10-06T05:23:08.167Z
[board-joan]  CANON: OK

#### betty — 2026-10-06T05:22:54.180Z
[board-betty] TESTS: REVISE
What: core/agent.md + core/consult.md (no AST-1996 entry) — missing coverage + one broken test — this ticket is the test work itself: qa-fix (F4) lands plan items 1–8 as written (flip `TestDecodePayload::test_rejects_bad_positions_and_trailing_meta`; repro A in `TestDecodePayload` and repro B through `_should_decode_as_encoded_line` + `_normalize_rubric_task_response`, both red on `57ed90983`; `_run_batch_consult` 6a/6b covering both uncovered LOCKED_AT_100 branches, stubbing `_hydrate_response_jobs_grade_reasons`; bible rows). Plan refs verified on `6cc4c8013` (class names, `_batch_entities(*ids)`, `96bc0471d` ancestor, branches at consult.py:1718/1824). Engineer pass is verify-only. Note for Chuckles: the ~60 failures already on the ftr trunk in test_agent/test_consult are outside this ticket, but they will keep the full harness red.

#### hedy — 2026-10-06T05:22:15.192Z
`origin/sub/AST-1884/AST-2001-decode-line-retry-tests` @ `6cc4c8013` · decode isolation coverage spec

---

_Implementation detail may live in git history on `origin/dev`._

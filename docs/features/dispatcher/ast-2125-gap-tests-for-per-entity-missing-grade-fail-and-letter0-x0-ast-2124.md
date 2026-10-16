# AST-2125 — gap: tests for per-entity missing-grade fail and letter0 → X0 (AST-2124)

<!-- linear-archive: AST-2125 archived 2026-10-16 -->

## Linear archive (AST-2125)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2125/gap-tests-for-per-entity-missing-grade-fail-and-letter0-x0-ast-2124  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-2116 — [✅/Somerset] meteorite_grade_do COMPLETED: 1 error(s) / 2 processed | meteorite_grade_do-8c5dd940-9dac-4833-a057-43ac09c2091d  
**Blocked by / blocks / related:** parent: AST-2116

### Description

## What this implements

The test gap fix-board flagged on [AST-2124](https://linear.app/astralcareermatch/issue/AST-2124) (`[board-betty] TESTS: REVISE`). It has two parts.

**Broken tests.** Three existing tests assert AST-2053's `{letter}0 → {letter}1` decode, and AST-2124 changes that to `X0`:

* `tests/component/core/test_agent.py::TestDecodePayload::test_ast2053_letter_conf0_normalised_to_conf1`
* `tests/component/core/test_agent.py::TestDecodePayload::test_ast2053_normalisation_boundaries` (`_notes` `CRF0` expects `F/1`)
* `tests/component/core/test_agent.py::TestDecodeAndAuditBranches::test_skips_non_dict_payload_rows_and_invalid_confidence` (`0|CRA0` expects `A/1`)

They move to the X0 contract, along with the AST-2057 bible rows in `docs/test-bible/core/agent.md`.

**New coverage**, including a `[bug-repro]` (the plan's `## Repro` fixture) that is red on the pre-fix product and green once AST-2124 lands:

* One job's missing description fails only that job (to `fail_state`) while its batch sibling applies: consult batch path.
* The same for the prefilter path, to `PREFILTER_FAILED`.
* The single-row `render_verdict` miss branch and the `_apply_prefilter_decoded_company_outcome` miss branch.
* X hydrating on a vector with no X row, falling back to the fixed no-signal reason.
* These are new branches in `LOCKED_AT_100` modules (`consult.py`, `roster.py`, `agent.py`).

## Scope

## Component scope

* `tests/component/core/test_agent.py` (modified): three AST-2053 decode tests move to the `X0` contract; new coverage for letter0 → X0.
* `tests/component/core/test_consult.py` (modified): the `[bug-repro]` and per-entity hydrate-miss coverage for the batch and single-row consult paths, plus X with no X row.
* `tests/component/core/test_roster.py` (modified): per-company hydrate-miss coverage for the prefilter batch path and `_apply_prefilter_decoded_company_outcome`, to `PREFILTER_FAILED`.
* `docs/test-bible/core/agent.md`, `docs/test-bible/core/consult.md`, `docs/test-bible/core/roster.md` (modified): bible entries naming the changed and new coverage (the AST-2057 block in `agent.md` included).

## Technical scope

* Test files: three modified test functions in `test_agent.py`, plus new test functions for each behaviour above. The `[bug-repro]` must fail against the pre-fix product (`origin/dev` at the fork) and pass with AST-2124's product change on ftr.
* Test bible: modified and new entries naming the coverage. No product code.

## Acceptance criteria

1. The `[bug-repro]` test is red on the pre-fix product and green with AST-2124 on ftr.
2. The three AST-2053 decode tests pass against the X0 contract.
3. `consult.py`, `roster.py` and `agent.py` hold their `LOCKED_AT_100` coverage with AST-2124's new branches.

## Boundaries

* No product (`src/`) or canon change; AST-2124 owns both.

## Notes for planning

Gap child of [AST-2124](https://linear.app/astralcareermatch/issue/AST-2124) under bug [AST-2116](https://linear.app/astralcareermatch/issue/AST-2116). Betty's full `[board-betty]` comment on AST-2124 lists the breaks and what stays green. The plan to patch is the `## Bug: AST-2124` section in `docs/features/consult/ast-1155-incomplete-grades-retry-holding-never-technical-fail.md` (add a `## Bug: AST-2125` block). Precedent: AST-2057 for AST-2053.

## Git branch (authoritative)

Parent `ftr/AST-2116-missing-grade-fail`, child `sub/AST-2116/AST-2125-missing-grade-fail-tests`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-10-10T04:26:28.871Z
[code-rubric] PROCEED (Commit: 96375e321) Test gap locks AST-2124

#### hedy — 2026-10-10T04:25:20.394Z
`origin/sub/AST-2116/AST-2125-missing-grade-fail-tests` @ `96375e321` · Tests Passed

- **[bug-repro]** `test_consult.py::TestAst2125MissingRubricDescription::test_batch_miss_fails_only_that_job`: red on pre-fix `src/core/{consult,roster,agent}.py` from `01606b791` (/tmp git archive) — `Actual: mock('meteorite_grade_do', ['J0', 'J1'], 'METEORITE_PASSED_JD_RETRY')`; green on tip.
- #2 new classes: 9 passed. #3 decode classes: 12 passed, 0 failed.
- #4 branch coverage on AST-2124 hunks (`0d01e20d2`): agent / consult / roster — no missing line, no partial branch (28 passed).
- #5 `git diff origin/ftr/AST-2116-missing-grade-fail -- src/ canon/` empty.

#### hedy — 2026-10-10T04:23:10.321Z
`origin/sub/AST-2116/AST-2125-missing-grade-fail-tests` @ `96375e321` · no src; bug-repro + 9 new + 12 decode green

#### betty — 2026-10-10T04:07:22.521Z
[bug-repro]
`origin/sub/AST-2116/AST-2125-missing-grade-fail-tests` @ `a19981f4a` · repro red pre-fix, green tip
context_tokens≈75000

#### joan — 2026-10-10T04:05:33.220Z
[board-joan]  CANON: OK

#### betty — 2026-10-10T04:05:10.569Z
[board-betty] TESTS: REVISE
What: tests/component/core/test_{agent,consult,roster}.py + docs/test-bible/core/{agent,consult,roster}.md — qa-fix lands this plan as written (#1–#8); nothing missing from my AST-2124 REVISE

Covers every AST-2124 item: the 3 decode tests that asserted letter0 → letter1 (including the two Blast radius missed), the agent.md AST-2001 line plus the AST-2057 rows, batch consult per-entity miss (the [bug-repro]), single-row consult miss, prefilter single company and batch, X with no X row → "No signal", the MissingRubricDescriptionError vs unknown-vector split, and the batch helper's returned misses. Bible rows 1–3 of AST-2057 are all on the ref, so the plan's row edits apply as written.

Independent dry-run (git archive of origin/sub/AST-2116/AST-2125-missing-grade-fail-tests into /tmp, plan code blocks applied, nothing committed):
- Product from AST-2124: 35 passed. That is the 9 new tests plus TestDecodePayload, TestDecodeAndAuditBranches (with the 3 rewrites), TestRubricLookup, and the roster TestAst1846PrefilterRetryWarnThenError.
- Pre-fix product (`src/core/{consult,roster,agent}.py` @ 01606b791): 7 of the 9 new tests fail. The 2 that pass are the guards (`test_x_with_x_row_uses_rubric_text`, `test_blank_row_falls_through_to_trailing_table`). The bug-repro fails as `['J0','J1'] → METEORITE_PASSED_JD_RETRY`; the roster batch test fails with `retried 2, failed 0`. This matches the plan's record.

Not re-run here: the plan's manifest step 4 (coverage of the AST-2124 hunks). test-fix owns it.
context_tokens≈52000

#### hedy — 2026-10-10T04:03:58.240Z
`origin/sub/AST-2116/AST-2125-missing-grade-fail-tests` @ `989a1d827` · tests dry-run red/green verified

---

_Implementation detail may live in git history on `origin/dev`._

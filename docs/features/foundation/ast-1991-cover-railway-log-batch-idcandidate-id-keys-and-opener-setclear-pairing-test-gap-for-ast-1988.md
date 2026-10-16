# AST-1991 — Cover Railway log batch_id/candidate_id keys and opener set/clear pairing (test gap for AST-1988)

<!-- linear-archive: AST-1991 archived 2026-10-13 -->

## Linear archive (AST-1991)

**Archived:** 2026-10-13  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1991/cover-railway-log-batch-idcandidate-id-keys-and-opener-setclear  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1987 — Candidate_id and batch_id are not populating in Railway log output  
**Blocked by / blocks / related:** parent: AST-1987

### Description

## What this implements

Test gap from fix-board on AST-1988 (`[board-betty] TESTS: REVISE`). Nothing tests the repro. There's no check that Railway JSON lines carry `batch_id` / `candidate_id` when the contextvars are set and stay byte-identical to today when unset. There's also no check that the dispatcher / agent / candidate / meteorite batch openers set and clear `log_candidate_id` together with `log_batch_id`, including `_hold_log_batch` doing nothing under a parent batch and its new two-token reset. Existing tests stay green (Betty's board note), so this is add-only coverage.

## Scope

### Component scope

* `tests/component/utils/test_debug_logging.py` (modified): Railway formatter coverage for the new keys, both present-when-set and omitted-when-unset.
* `tests/component/utils/test_logging_batch.py` (modified, if Betty homes the stamp/pairing tests here): `app_log` `candidate_id` stamp during a candidate-owned run.
* `tests/component/core/test_dispatcher.py`, `tests/component/core/test_agent.py`, `tests/component/core/test_candidate.py`, `tests/component/core/test_meteorite.py` (modified, as Betty chooses): set/clear pairing at the batch openers named in AST-1988's plan, including `_hold_log_batch` no-op + tuple reset.
* `docs/test-bible/utils/debug_logging.md` and `docs/test-bible/utils/logging_batch.md` (modified): bible rows for the new coverage.

### Technical scope

* Test files above: new test functions only (no product edits). The formatter tests assert the exact JSON with and without contextvars set. The pairing tests assert `log_candidate_id` is set at batch start and back to `None` (or reset) at teardown, so no candidate leaks into the next run.
* Bible files above: new rows pointing at those tests.

## Acceptance criteria

1. The bug-repro test (formatter with contextvars set → `batch_id` / `candidate_id` keys present) fails on `origin/dev`'s `src/utils/logging.py` and passes once AST-1988's product fix is on the tip.
2. A batch-less Railway line is asserted byte-identical to the pre-fix shape.
3. At least one pairing test per touched opener family (dispatcher, agent, candidate, meteorite `_hold_log_batch`) proves set + clear.
4. No product code changes on this ticket.

## Boundaries

Tests and bible only. The product fix belongs to sibling AST-1988. It lands on the mini-parent ftr first and reaches this sub through sync-child. `src/core/intake.py` is out of scope here, as it is for AST-1988.

## Notes for planning

Gap child filed by bug-fix from Betty's `[board-betty] TESTS: REVISE` on AST-1988 (read that comment). Plan section home: `docs/features/candidate/ast-1598-job-and-app-log-candidate-id.md` (same doc as AST-1988's `## Bug:` block).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1987-railway-log-batch-candidate-ids`, child `sub/AST-1987/<child-segment>`. Created at bug-fix gap dispatch.

### Comments

#### radia — 2026-10-06T04:51:27.035Z
[code-rubric] REVIEW (Commit: d6b36d6a1) Tests OK; tip carries AST-1990

#### hedy — 2026-10-06T04:49:59.261Z
`origin/sub/AST-1987/AST-1991-cover-railway-log-id-tests` @ `d6b36d6a1` · repro flipped, manifest green

[bug-repro] gate: #1 `TestAst1988RailwayJsonIds::test_formatter_adds_batch_and_candidate_when_set` and #14 `TestAst1988HoldLogBatchPairing::test_hold_sets_both_and_returns_token_pair` fail with origin/dev's `logging.py` + `meteorite.py` and pass on the tip. All 17 new tests are green on the tip. With all five AST-1988 product files swapped to origin/dev, 15/17 are red. Beyond your #15 note, #8 (`test_ast1988_run_next_chain_leaves_candidate_unset_like_batch`) and #13 (`test_ast1988_session_sentinel_batch_stays_unstamped`) also fail pre-fix, with `AttributeError` (the module has no `log_candidate_id` before the fix). That's an import artifact, not a test defect. Six touched files: 74 failures, identical with and without the AST-1991 tests, all already on the base (agent 40, candidate 18, dispatcher 12, meteorite 4). No product change.

#### betty — 2026-10-06T04:46:53.768Z
[bug-repro]
`origin/sub/AST-1987/AST-1991-cover-railway-log-id-tests` @ `8ed42a3db` · repro red pre-fix, green on tip

Stacked deviation (AST-1988 fix already on the ftr): I checked the repro by swapping in origin/dev's `src/utils/logging.py` + `src/core/meteorite.py` (since restored). #1 `TestAst1988RailwayJsonIds::test_formatter_adds_batch_and_candidate_when_set` went red because the id keys were missing, and #14 `TestAst1988HoldLogBatchPairing::test_hold_sets_both_and_returns_token_pair` raised `TypeError` from the one-arg `_hold_log_batch`. Both match the Root cause. All 17 new tests are green on the synced tip and on the merged sub. One spec deviation: #15 (no-op under a parent batch) is also red on dev, from the same `TypeError`, not green as the plan predicted. In the 6 touched files the failure set is identical with and without these tests (73 failures, already present on the base). Manifest + node ids: `docs/test-bible/utils/debug_logging.md` + `docs/test-bible/utils/logging_batch.md` § AST-1988. @Hedy

#### joan — 2026-10-06T04:39:42.754Z
[board-joan]  CANON: OK

context_tokens≈22000

#### betty — 2026-10-06T04:39:26.393Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/debug_logging.md + docs/test-bible/utils/logging_batch.md — missing coverage — the AST-1988 repro is still uncovered on this tip; land the plan-fix spec §1–§8 (tests #1–#17 + two bible sections) via qa-fix. The [bug-repro] tests (#1 formatter keys, #14 `_hold_log_batch` token pair) must be red on origin/dev's product files and green on this tip.

Checked on `origin/sub/AST-1987/AST-1991-cover-railway-log-id-tests` @ 0e9cc6aa0: every reused harness exists (`TestAst1778RailwayConsoleTransport`/`_StdoutCapture`, `TestDispatchOne` + `test_completes_click_dispatch` / `test_run_next_chain_skips_dispatch_level_ledger`, `TestAst531RunNextHopLedger.hop_ledger_trackers`, `TestAst515AdhocWorkbenchLedger.ledger_trackers`, `TestRunCandidateArtifactGeneration.test_returns_500_on_failed_task`, `TestAst986SessionResumeParse._patch_ledger`, `TestAst1879ClassifyKeyMapHandOff._run`). AST-1988's product change is present (`_hold_log_batch(batch_id, candidate_id)`, candidate.py set/clear). Add-only, so no existing test breaks. The contextvar-hygiene rule (tokens + `finally`, start from None) is the condition for that to hold.

#### hedy — 2026-10-06T04:38:29.161Z
`origin/sub/AST-1987/AST-1991-cover-railway-log-id-tests` @ `0e9cc6aa` · 17-test spec ready

---

_Implementation detail may live in git history on `origin/dev`._

# AST-2057 — Letter-confidence-0 normalisation tests + bible (test gap for AST-2053)

<!-- linear-archive: AST-2057 archived 2026-10-16 -->

## Linear archive (AST-2057)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2057/letter-confidence-0-normalisation-tests-bible-test-gap-for-ast-2053  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-2045 — [✅/Somerset] evaluate_meteorite COMPLETED: 1 error(s) / 2 processed | evaluate_meteorite-2ec6203d-be72-40ff-9fd4-f4787cbddf6d  
**Blocked by / blocks / related:** parent: AST-2045

### Description

## What this implements

Test-tree and bible coverage for [AST-2053](https://linear.app/astralcareermatch/issue/AST-2053)'s `{letter}0 → {letter}1` normalisation in `_decode_payload`, routed here from Betty's fix-board `TESTS: REVISE` on AST-2053 (the same shape as AST-2001 for AST-1996). No product source change.

## Scope

## Component scope

* `tests/component/core/test_agent.py` (modified). Add repro coverage: a grades-only encoded line with `CFC0`/`SSC0`/`TCC0`-style segments decodes to rows with the same letter and confidence 1, and no `decode_failures`. Rewrite `TestDecodeAndAuditBranches::test_skips_non_dict_payload_rows_and_invalid_confidence` (`0|CRA0` no longer raises) and `TestDecodePayload::test_rejects_bad_positions_and_records_trailing_meta` (the `0|CRX2` assert is stale since f8d3f9a12 and should expect an X-branch `decode_failures` entry).
* `docs/test-bible/core/agent.md` (modified). The AST-2001 block still says letter grades outside confidence 1–5 raise. Record the confidence-0 normalisation and the remaining X / out-of-range `decode_failures` rows.

## Technical scope

* `tests/component/core/test_agent.py`: new test function(s) for the normalisation repro, plus two modified test functions, so the suite asserts the shipped decode contract instead of the pre-AST-1996 raise behavior.
* `docs/test-bible/core/agent.md`: modified bible rows, so the bible matches the tests.

## Acceptance criteria

* The repro test passes on the AST-2053 tip. It would have failed before AST-2053 (the line went to `decode_failures`).
* The two named stale tests assert current behavior and pass.
* The bible AST-2001 block matches.

## Boundaries

* No `src/` change: AST-2053 owns the product fix and the statute edit.
* Other pre-existing `test_agent.py` / `test_consult.py` failures on ftr are out of scope.

## Notes for planning

Betty's verdict comment on AST-2053 (`[board-betty] TESTS: REVISE`) names the exact gaps. Doc to patch: `docs/features/consult/ast-1155-incomplete-grades-retry-holding-never-technical-fail.md`, with a `## Bug: <this id>` block alongside AST-2053's. Blocked by AST-2053 so the tests run against the shipped fix on `ftr`.

## Git branch (authoritative)

Parent `ftr/AST-2045-letter-conf0-normalize`; this child `sub/AST-2045/AST-2057-letter-conf0-tests`. Registry is authoritative.

### Comments

#### radia — 2026-10-08T20:49:41.952Z
[code-rubric] PROCEED (Commit: 08ee79648) Bug-repro locks AST-2053

#### hedy — 2026-10-08T20:48:33.605Z
`origin/sub/AST-2045/AST-2057-letter-conf0-tests` @ `08ee79648` · test-fix — manifest green, [bug-repro] flip confirmed

1. [bug-repro] `TestDecodePayload::test_ast2053_letter_conf0_normalised_to_conf1`: **green** on tip; **red** with pre-fix `agent.py` from `06df211db` (`['job-1'] == ['job-0', 'job-1']`).
2. `-k "TestDecodePayload or TestDecodeAndAuditBranches"`: tip **12 passed / 0 failed**; pre-fix 3 failed / 9 passed (repro, boundaries, `0|CRA0`) — matches the bible red/green record.
3. `git diff origin/ftr/AST-2045-letter-conf0-normalize -- src/` empty.

#### betty — 2026-10-08T20:47:12.704Z
[bug-repro]
`origin/sub/AST-2045/AST-2057-letter-conf0-tests` @ `63e570930` · repro red pre-fix, green tip

#### joan — 2026-10-08T20:44:36.269Z
[board-joan]  CANON: OK

#### betty — 2026-10-08T20:44:21.828Z
[board-betty] TESTS: REVISE
What: tests/component/core/test_agent.py + docs/test-bible/core/agent.md (AST-2001 block, new AST-2057 block) — the fix is test-tree only; land plan-fix #1–#5 via qa-fix (#3 `test_ast2053_letter_conf0_normalised_to_conf1` is the [bug-repro], red on pre-fix 055c53c2a); anchors verified on ftr tip 3d51b06c7. Also re-run `do_task` `0|CRX2` assert (~L1752, "confidence digit 0" in error) as a guard — X-branch, expected unchanged.

#### hedy — 2026-10-08T20:43:41.136Z
`origin/sub/AST-2045/AST-2057-letter-conf0-tests` @ `aa4b06332` · conf-0 tests + bible planned

---

_Implementation detail may live in git history on `origin/dev`._

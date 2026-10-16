# AST-1996 — Isolate malformed encoded grade lines → per-entity retry, not hop error (evaluate_meteorite trailing-content error)

<!-- linear-archive: AST-1996 archived 2026-10-16 -->

## Linear archive (AST-1996)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1996/isolate-malformed-encoded-grade-lines-per-entity-retry-not-hop-error  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-1884 — [✅/Somerset] evaluate_meteorite COMPLETED: 1 error(s) / 1 processed | evaluate_meteorite-ee5b6a08-bbed-4025-bfbf-43c854270119  
**Blocked by / blocks / related:** parent: AST-1884; blocks: AST-2001

### Description

## What this implements

Fix child of orphaned bug [AST-1884](https://linear.app/astralcareermatch/issue/AST-1884): a model format slip on one encoded grade line (e.g. `DEC35` — two confidence digits) must become a per-entity retry, not a hop-level technical error. Today `_decode_payload` raises `unexpected trailing content in grades-only line`, the whole hop fails, and the job lands in `METEORITE_ERROR_EVALUATE_JD`. To-be: well-formed lines in the batch still decode and apply; the malformed line's entity goes to its retry holding state (AST-1155 contract — technical-fail states reserved for true infra failures). No silent coercion of ambiguous confidence values.

## Citations

Approved ancestor: AST-1155 — Incomplete grades → retry holding, never technical fail (`docs/features/consult/ast-1155-incomplete-grades-retry-holding-never-technical-fail.md`). Canon list is plan-fix's call.

## Scope

## Component scope

* `src/core/agent.py` — modified — `_decode_payload` currently raises on the first malformed line and kills the batch; it needs to isolate the bad line instead.
* `src/core/consult.py` — modified — `_normalize_rubric_task_response` / scored apply path must carry per-entity decode failures through to the retry destination rather than a hop-level error.
* `src/utils/config.py` — modified only if `evaluate_meteorite` / meteorite job states lack a retry holding destination for this trigger.
* `tests/component/core/test_agent.py` — modified — decode isolation regression (test tree is Betty's; listed so the fix lane knows it is in play).
* `tests/component/core/test_consult.py` — modified — retry-holding routing regression for a malformed encoded line (Betty's tree, same note).

## Technical scope

* `src/core/agent.py`: modified function — `_decode_payload` returns successfully decoded rows plus a list of failed positions/reasons for grades-only lines with trailing content, instead of raising `ValueError` for the whole payload.
* `src/core/consult.py`: modified function(s) — the rubric-response normalize/apply path consumes the failed-position list and sends those entities down the existing retry-holding route (AST-1155), leaving the rest of the batch to apply normally.
* `src/utils/config.py`: possibly a new/modified retry-state field on the meteorite JD job states or `evaluate_meteorite` TASK_CONFIG, only if the retry destination does not already exist.

## Acceptance criteria

- [X] A batch where one line has non-grade trailing content (e.g. `000|DEC35|...`) and another line is clean: the clean line decodes and applies; the malformed line's entity lands in its retry holding state, not `*_ERROR_*` / technical-fail.
- [X] Grades-only strictness unchanged — `_GRADE_SEG` is not widened and no ambiguous confidence is coerced.

## Boundaries

No prompt / `{$OUTPUT_INSTRUCTIONS}` copy changes. No widening of `_GRADE_SEG`. Test tree belongs to Betty (any test gap is a sibling).

## Git branch (authoritative)

Parent `ftr/AST-1884-decode-line-retry`, child `sub/AST-1884/AST-1996-decode-line-retry`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-10-06T05:19:04.485Z
[code-rubric] PROCEED (Commit: 96bc0471d) Per-line decode retry OK

#### hedy — 2026-10-06T05:17:41.410Z
`origin/sub/AST-1884/AST-1996-decode-line-retry` @ `96bc0471d` · test-fix lighter check (no qa-fix on this ticket; Betty's REVISE routed to AST-2001)

**Ran:** `py_compile` on `src/core/agent.py`, `src/core/consult.py` — OK. `ASTRAL_PYTHON=<3.14 venv> ./scripts/testing/run_component_tests.sh tests/component/core/test_agent.py tests/component/core/test_consult.py` on the fix tip **and** on the pre-fix tree `57ed90983`.

**Result:** 61 failed / 628 passed on both trees. No regressions from this fix.
- **Expected flip (AST-2001):** `test_agent.py::TestDecodePayload::test_rejects_bad_positions_and_trailing_meta`. It still expects a raise on `0|CRA2|extra`; the call now returns `decode_failures`.
- **Coverage gap on the new code (AST-2001):** `consult.py` decode-failure routing loop (L1718→1719) and the `decode failed on N IDs` error line (L1824→1825). The `agent.py` diff is fully covered.
- **Fails only on the pre-fix tree, not code-related:** `TestAst972…test_routes_requested_artifacts_via_stage_task_key` fails in any fresh worktree with an empty `data/`, including one at `96bc0471d`.
- **The other 60 failures already exist on the ftr branch,** with the same error reasons on both trees (for example `KeyError: 'company_id'` in decode from AST-1723, empty-rubric hydrate, resume-section asserts). They are outside this ticket.

#### joan — 2026-10-06T05:11:41.834Z
[board-joan]  CANON: OK

#### betty — 2026-10-06T05:11:03.042Z
[board-betty] TESTS: REVISE
What: core/consult.md (AST-699 routing rows) + no bible entry for decode_failures — broken test + missing repro coverage — `tests/component/core/test_agent.py::…::test_rejects_bad_positions_and_trailing_meta` asserts `0|CRA2|extra` raises "unexpected trailing content" (flips to a `decode_failures` return); no test covers multi-line partial decode (repro A), later-line routing in `_should_decode_as_encoded_line` (repro B; `test_should_decode_as_encoded_line_routing` is single-line only), or `_run_batch_consult` per-entity `decode_failed` → `_consult_batch_fail_dest` first/second strike + clean-row-wins + `success`/`errors` shape. `agent.py` and `consult.py` are both LOCKED_AT_100, so the new branches need coverage before the gate goes green.

#### hedy — 2026-10-06T05:10:05.813Z
`origin/sub/AST-1884/AST-1996-decode-line-retry` @ `352bae4de` · isolate bad line, per-entity retry

---

_Implementation detail may live in git history on `origin/dev`._

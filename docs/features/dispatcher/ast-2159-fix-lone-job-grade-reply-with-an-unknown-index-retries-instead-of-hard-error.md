# AST-2159 — fix: lone-job grade reply with an unknown index retries instead of hard ERROR

<!-- linear-archive: AST-2159 archived 2026-10-16 -->

## Linear archive (AST-2159)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2159/fix-lone-job-grade-reply-with-an-unknown-index-retries-instead-of-hard  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 1  
**Parent:** AST-2158 — [✅/Somerset] meteorite_grade_get COMPLETED: 1 error(s) / 4 processed | meteorite_grade_get-060a88ad-366e-411e-bfd3-258123d10839  
**Blocked by / blocks / related:** parent: AST-2158; blocks: AST-2161

### Description

## What this implements

On the lone-job grade path (`render_verdict`, one job per agent call), a reply whose row can't be bound to the job (the model echoes an index that isn't the job's batch-unique index, so decode skips the line as unknown and records no `decode_failure`) is routed like an omitted batch entity: primary state goes to its retry holding via `_consult_batch_fail_dest`, already-retry goes to error. It no longer hard-fails straight to the terminal `ERROR_<TASK>` state on the first miss.

## Scope

## Component scope

* `src/core/consult.py` — modified: `render_verdict`'s no-row fallback is where the lone-job miss is wrongly sent to the terminal error state; the retry router it should use already lives in the same file.

## Technical scope

* `src/core/consult.py` — modified function `render_verdict`: the "no `j0`, no matching `decode_failure`" branch routes through the existing batch fail-destination helper (retry holding first) instead of the hard `_fail`, so a model index mis-echo on a one-job call retries like an omitted batch entity. No new tables, fields, or states.

## Acceptance criteria

* A lone `render_verdict` call whose reply line carries the wrong index (e.g. `000` for a job at batch index 24) moves the job to its retry holding, not `ERROR_METEORITE_GRADE_GET`.
* The same miss from the retry holding lands on the error state (one hop, same as the batch path's "omitted from response").
* The fail-destination log line says why (omitted / unknown index), not "decoded payload has no job row".
* The existing `decode_failures` branch in `render_verdict` and every multi-row batch path behave exactly as today.

## Boundaries

Does not change `agent._decode_payload` (AST-2093's unknown-index skip stays as is). Does not bind a mis-indexed lone line to the lone entity. That was the optional step 4 in [AST-2158](https://linear.app/astralcareermatch/issue/AST-2158), which Susan did not check, so it is out of scope. Does not reset jobs already in `ERROR_METEORITE_GRADE_GET` from the reported batch. Tests and bible are Betty's (fix-board decides whether a gap child is needed).

## Notes for planning

The AST-2158 Description (As-is / To-be / Proposed steps 1–3) is authoritative. No ancestor box was checked. For context only, the lone-call batch index came from AST-2093 (`docs/features/agent/response-validation-layers.md` § Bug: AST-2093). Patch that doc with a `## Bug: <this id>` block; never create a new doc. No in-flight epic touches `consult.py` right now.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-2158-lone-grade-unknown-index-retry`, child `sub/AST-2158/AST-2159-lone-grade-unknown-index-retry`. Created at bug-fix.

### Comments

#### radia — 2026-10-12T20:02:03.156Z
[code-rubric] PROCEED (Commit: a1869593) Lone no-row retry routing

#### joan — 2026-10-12T19:58:23.999Z
[board-joan]  CANON: OK

#### betty — 2026-10-12T19:58:08.354Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/consult.md (TestRenderVerdict) — missing coverage — no test drives render_verdict no-row/no-decode_failures with a stateful job: METEORITE_PASSED_DO → retry_of(...) [omitted from response], already-retry → ERROR_METEORITE_GRADE_GET. Existing test_fails_when_job_row_is_missing / test_fails_when_grades_are_missing use stateless jobs (dest=error_state either way) so they stay green and cannot catch the bug.

context_tokens≈38000

#### hedy — 2026-10-12T19:57:08.645Z
`origin/sub/AST-2158/AST-2159-lone-grade-unknown-index-retry` @ `f2fff3d42` · lone no-row → retry routing

---

_Implementation detail may live in git history on `origin/dev`._

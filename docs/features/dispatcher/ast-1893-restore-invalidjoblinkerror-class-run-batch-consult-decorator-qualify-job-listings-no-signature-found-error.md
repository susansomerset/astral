# AST-1893 — Restore InvalidJobLinkError class + _run_batch_consult decorator (qualify_job_listings no signature found error)

<!-- linear-archive: AST-1893 archived 2026-10-08 -->

## Linear archive (AST-1893)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1893/restore-invalidjoblinkerror-class-run-batch-consult-decorator-qualify  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 1  
**Parent:** AST-1888 — [✅/Abrams] qualify_job_listings COMPLETED: 1 error(s) / 1 processed | qualify_job_listings-35ef8081-10be-4cb8-9eb7-9c65d22648c1  
**Blocked by / blocks / related:** parent: AST-1888; blocks: AST-1895

### Description

## What this implements

Restore `InvalidJobLinkError` as a real exception class in `src/core/consult.py` and put `@_with_log_debug` back on `_run_batch_consult`, where it lived before unticketed commit `c86d8b5ce` slid the class definition between the decorator and the function. Today an empty/relative `job_link` in `qualify_job_listings` errors with `process_fn ValueError: no signature found for builtin type <class 'src.core.consult.InvalidJobLinkError'>` instead of the intended `InvalidJobLinkError` reason.

## Scope

### Component scope

* `src/core/consult.py` (modified): move the misplaced `@_with_log_debug` decorator off `InvalidJobLinkError` and back onto `_run_batch_consult`. No other decorator in `src/` sits on a class (checked).
* `tests/` consult batch test module (modified or new, Betty's call on placement): regression coverage for the empty/relative `job_link` path in `qualify_job_listings`.

### Technical scope

* `src/core/consult.py`: modified class (`InvalidJobLinkError` is no longer decorated) and modified function (`_run_batch_consult` is decorated with `@_with_log_debug` again). No signature, table, or field changes.
* Consult test module: new test function covering `process_fn` raising `InvalidJobLinkError` inside `_run_batch_consult`, checking both the destination state and the exception type in the fail reason.

## Acceptance criteria

1. A passing `qualify_job_listings` response with an empty or relative `job_link` routes to the same fail/retry destination as today, and the logged fail reason reads `process_fn InvalidJobLinkError: empty job_link: ` / `relative job_link: …` — never `no signature found`.
2. `InvalidJobLinkError` is a class (`isinstance(e, InvalidJobLinkError)` works; it subclasses `ValueError`).
3. `_run_batch_consult(..., debug=True)` sets `log_debug` for its frame again via `@_with_log_debug`.

## Boundaries

Does not change `job_link` validation rules, fail/retry routing, or any prompt. Does not touch other `_with_log_debug` users.

## Notes for planning

No ancestor checked by Susan (AST-337 offered, left unchecked). Root cause, as-is/to-be in mini-parent AST-1888 Description. Regression introduced by `c86d8b5ce` (2026-09-28).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1888-invalid-job-link-error-decorator`, child `sub/AST-1888/<child-segment>`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-09-29T23:09:28.827Z
[code-rubric] PROCEED (Commit: b516e8764) Decorator restore clean

#### hedy — 2026-09-29T23:07:42.506Z
`origin/sub/AST-1888/AST-1893-restore-invalid-job-link-error-class` @ `b516e8764` · lighter check (fix-board TESTS work split to AST-1895; no [bug-repro] here)

- `py_compile src/core/consult.py`: OK. Import sanity: `InvalidJobLinkError` is a class and subclasses `ValueError`; the reason renders `process_fn InvalidJobLinkError: empty job_link: `; `_run_batch_consult` is wrapped (`__wrapped__`) again.
- `pytest tests/component/core/test_consult.py -k "qualify or Qualify or batch_consult or BatchConsult or job_link"` (venv `/home/susan/astral/.venv`; system python3 lacks `asyncpg`): **7 failed, 38 passed, 1 skipped**.
- Pre-fix tree (`consult.py` @ `014658fc4`), same command: **exactly the same 7 failures**. The branch is `origin/dev` plus this 2-line change, so these already fail on dev and are not from this fix:
  - `TestRunBatchConsult::test_counts_passed_and_failed_rows`, `TestRemainingConsultBranches::test_qualify_ignores_score_errors`, `TestAst726LatestOnlyConsultOutcomes::test_qualify_job_listings_persists_joblist_score_on_{pass,fail}`: `ValueError: rubric criteria missing or empty; cannot hydrate grade reasons`
  - `TestAst1062QualifyMeteorite::test_content_gates_fail_state`: `assert 3 == 0`
  - `TestAst1133…::test_debug_detail_includes_link_source_input`, `TestAst1197…::test_style_d_email_link_and_subject_title_source`: expected `link_source=…` in an empty debug detail
- @Betty White FYI for AST-1895 / bible: existing drift on dev, outside this ticket's scope. `tests/` not touched.

#### joan — 2026-09-29T23:02:58.377Z
[board-joan]  CANON: OK

#### betty — 2026-09-29T23:02:29.571Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/consult.md (no entry for InvalidJobLinkError / _run_batch_consult debug scope) — missing coverage — `TestAst..::test_fails_short_title_and_relative_link` sends `/relative` but checks only routing (`bad_grades`), so it passes on the broken tree. No test asserts the `_log_fail_dest` reason (`process_fn InvalidJobLinkError: …`, never `no signature found`), that the raised error is a `ValueError` subclass, or that `_run_batch_consult(debug=True)` sets `log_debug`. Blast radius breaks nothing that exists (direct `_run_batch_consult` calls pass through the `functools.wraps` wrapper, and the monkeypatches swap the attribute). qa-fix: add a bug-repro test with empty and relative `job_link` → same fail destination + reason naming `InvalidJobLinkError`, plus a debug-scope check on `_run_batch_consult`.

#### hedy — 2026-09-29T23:01:09.451Z
`origin/sub/AST-1888/AST-1893-restore-invalid-job-link-error-class` @ `7251045f1` · Move decorator back to function

---

_Implementation detail may live in git history on `origin/dev`._

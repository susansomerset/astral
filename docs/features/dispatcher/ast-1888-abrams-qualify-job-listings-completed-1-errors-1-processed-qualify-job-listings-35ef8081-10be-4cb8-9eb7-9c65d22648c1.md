# AST-1888 — [✅/Abrams] qualify_job_listings COMPLETED: 1 error(s) / 1 processed | qualify_job_listings-35ef8081-10be-4cb8-9eb7-9c65d22648c1

<!-- linear-archive: AST-1888 archived 2026-10-08 -->

## Linear archive (AST-1888)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1888/abrams-qualify-job-listings-completed-1-errors-1-processed-qualify-job  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

When `qualify_job_listings` gets a passing job back from the model with an empty or relative `job_link`, the job lands in `ERROR_QUALIFY_JOB_LISTINGS` with a misleading reason: `process_fn ValueError: no signature found for builtin type <class 'src.core.consult.InvalidJobLinkError'>`.

Root cause: unticketed commit `c86d8b5ce` (2026-09-28, "fix(dispatch): reduce sqlite lock contention…") inserted `class InvalidJobLinkError(ValueError)` in `src/core/consult.py` **between** the existing `@_with_log_debug` line and `async def _run_batch_consult`. That caused two problems:

1. `@_with_log_debug` now wraps the exception class. `InvalidJobLinkError` is a wrapper function, not a class, so `raise InvalidJobLinkError(...)` calls the wrapper. The wrapper then runs `inspect.signature()` on a builtin-derived exception, which throws its own `ValueError` before the intended exception is ever built.
2. `_run_batch_consult` no longer has `@_with_log_debug`, so `debug=True` no longer switches on `log_debug` for the batch consult frame.

The job still gets routed to error/retry because the stray `ValueError` is caught by the same `except Exception`. The routing is right; the reason text is garbage.

## To-be

`InvalidJobLinkError` is a real exception class again. An empty or relative `job_link` fails with `process_fn InvalidJobLinkError: empty job_link: ` (or `relative job_link: /…`) and routes to the same fail/retry destination. `_run_batch_consult` gets `@_with_log_debug` back, so `debug=` scoping works like it did before `c86d8b5ce`.

## Proposed steps

1. In `src/core/consult.py`, move the `@_with_log_debug` line from above `class InvalidJobLinkError` back to directly above `async def _run_batch_consult`.
2. Add a unit test: a `qualify_job_listings` passing response with an empty or relative `job_link` routes to the fail/retry destination, and the logged reason names `InvalidJobLinkError`, not `no signature found`.
3. Compile and lint, then run the existing consult batch tests.

## Component scope

* `src/core/consult.py` (modified): move the misplaced `@_with_log_debug` decorator off `InvalidJobLinkError` and back onto `_run_batch_consult`. No other decorator in `src/` sits on a class (checked).
* `tests/` consult batch test module (modified or new, Betty's call on placement): regression coverage for the empty/relative `job_link` path in `qualify_job_listings`.

## Technical scope

* `src/core/consult.py`: modified class (`InvalidJobLinkError` is no longer decorated) and modified function (`_run_batch_consult` is decorated with `@_with_log_debug` again). No signature, table, or field changes.
* Consult test module: new test function covering `process_fn` raising `InvalidJobLinkError` inside `_run_batch_consult`, checking both the destination state and the exception type in the fail reason.

## Ancestor candidates

- [ ] AST-337 — Qualified job URLs (`docs/features/consult/ast-337-qualified-job-urls.md`, archived). This is where `qualify_job_listings` got its relative `job_link` handling. It is a weak match: the actual regression is the unticketed commit `c86d8b5ce`, which has no Linear ticket.

---

## Original report

```
2026-09-29 21:00:09  [INFO]  abrams | dispatch job starting
qualify_job_listings — 1 available (batch:
qualify_job_listings-35ef8081-10be-4cb8-9eb7-9c65d22648c1)
2026-09-29 21:00:14  [INFO]  abrams | dispatch job task completed:
qualify_job_listings pass:0 fail:0 error:1 (batch:
qualify_job_listings-35ef8081-10be-4cb8-9eb7-9c65d22648c1)
2026-09-29 21:00:14  [ERROR]  e04cbf01-eec4-478a-8a06-2e776c5c456e ->
ERROR_QUALIFY_JOB_LISTINGS [process_fn ValueError: no signature found
for builtin type <class 'src.core.consult.InvalidJobLinkError'>]
2026-09-29 21:00:14  [INFO]  LLM deepseek task=qualify_job_listings
1.9s stop=end_turn tokens in=906 out=164
```

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._

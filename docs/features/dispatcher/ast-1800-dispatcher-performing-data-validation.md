# AST-1800 — Dispatcher performing data validation

<!-- linear-archive: AST-1800 archived 2026-10-02 -->

## Linear archive (AST-1800)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1800/dispatcher-performing-data-validation  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

`prefilter_company` (trigger `HOMEPAGE_READY`) builds a claim union that includes `HOMEPAGE_READY_RETRY` via `dispatch_claim_states`, then `get_new_company_batch` raises `ValueError: state must be one of [...], got 'HOMEPAGE_READY_RETRY'` because that companion is not in `COMPANY_STATES`. The dispatcher truncates the batch and the hop fails instead of claiming.

## To-be

Dispatcher / claim path claims by the trigger state's claim union only — it does not re-validate claim companions against the entity-state registry. `HOMEPAGE_READY` may claim `['HOMEPAGE_READY', 'HOMEPAGE_READY_RETRY']` even when the `_RETRY` key is absent from `COMPANY_STATES`; SQL matching zero rows for an unused companion is fine. Data validation stays upstream of claim.

## Proposed steps

1. In `src/core/roster.py` `get_new_company_batch`, when `states=` is provided, stop requiring every list member to be in `COMPANY_STATES` (keep the single-`state` registry check when `states` is None).
2. Mirror the same relaxation on the job/candidate claim helpers that share the "every `states` member ∈ registry" loop (`src/core/tracker.py` `get_new_job_batch`, `src/core/candidate.py` claim path) so the [AST-1798](https://linear.app/astralcareermatch/issue/AST-1798/fix-strict-retry-suffix-claim-pairing-no-retry-state-companion) suffix-always contract does not trip the same ValueError on other entities.
3. Do **not** add `HOMEPAGE_READY_RETRY` (or other synthetic companions) to the registry — AST-641 / AST-1798 already forbids that as the fix.
4. Smoke: `prefilter_company` with `HOMEPAGE_READY` + union claim completes without the ValueError; absent companion still matches zero rows.

## Component scope

* `src/core/roster.py` — **modified** — `get_new_company_batch` is the raise site on this log; relax multi-state claim validation against `COMPANY_STATES`.
* `src/core/tracker.py` — **modified** — same "every `states` member ∈ registry" loop on `get_new_job_batch`; same [AST-1798](https://linear.app/astralcareermatch/issue/AST-1798/fix-strict-retry-suffix-claim-pairing-no-retry-state-companion) contract for jobs.
* `src/core/candidate.py` — **modified** — same pattern on the candidate claim helper; same contract for candidates.

## Technical scope

* `src/core/roster.py` — **modified function** `get_new_company_batch`: when `states=` is set, do not raise for members missing from `COMPANY_STATES`; still validate primary `state` when `states` is None so single-state callers stay bound.
* `src/core/tracker.py` — **modified function** `get_new_job_batch`: same multi-state vs single-state validation split for job claims.
* `src/core/candidate.py` — **modified function** (candidate claim helper with the `state must be one of` / `for s in states` loop): same split so candidate `_RETRY` companions are not registry-gated at claim time.

## Ancestor candidates

- [ ] [AST-1798](https://linear.app/astralcareermatch/issue/AST-1798/fix-strict-retry-suffix-claim-pairing-no-retry-state-companion) — fix: strict `_RETRY` suffix claim pairing (Done; shipped suffix-always `dispatch_claim_states` that emits registry-absent companions like `HOMEPAGE_READY_RETRY` — most direct parent of this failure mode)
- [ ] [AST-1797](https://linear.app/astralcareermatch/issue/AST-1797/retry-suffix-issues) — `_RETRY` suffix issues (Done mini-parent of [AST-1798](https://linear.app/astralcareermatch/issue/AST-1798/fix-strict-retry-suffix-claim-pairing-no-retry-state-companion) / [AST-1799](https://linear.app/astralcareermatch/issue/AST-1799/gap-tests-suffix-always-claim-asserts-ast-1798-board-revise))
- [ ] [AST-1799](https://linear.app/astralcareermatch/issue/AST-1799/gap-tests-suffix-always-claim-asserts-ast-1798-board-revise) — gap: tests suffix-always claim asserts (Done test sibling; same feature-doc home)
- [ ] docs/features/dispatcher/ast-641-union-claim-and-count-for-primary-retry-trigger-states-auto-retry.md — historical home of union claim / "do not validate suffix against registry" (Linear AST-641 no longer exists)

---

## Original report

```
[2026-09-25 20:43:15] INFO src.core.dispatcher: abrams | dispatch company starting prefilter_company — 2 available (batch: prefilter_company-4ee6fe1e-cef3-4262-9e8f-db9138ed3f08)
[2026-09-25 20:43:15] DEBUG src.core.dispatcher: 1370: Calling _run_dispatch_loop: [task_key=prefilter_company, available=2, entity_batch_id=prefilter_company-4ee6fe1e-cef3-4262-9e8f-db9138ed3f08]
[2026-09-25 20:43:15] DEBUG src.core.dispatcher: 1487: Beginning dispatch loop on 2 items
[2026-09-25 20:43:15] DEBUG src.core.dispatcher: 1536: Calling _run_task: [task_key=prefilter_company, available=2]
[2026-09-25 20:43:15] DEBUG src.core.dispatcher: 904: Calling _run_unified: [task_key=prefilter_company, batch_size=1, entity_type=company, trigger_state=HOMEPAGE_READY]
[2026-09-25 20:43:15] DEBUG src.core.dispatcher: 730: Calling get_new_company_batch: [state=HOMEPAGE_READY, limit=1, candidate_id=abrams, batch_id=prefilter_company-4ee6fe1e-cef3-4262-9e8f-db9138ed3f08, sort_by=updated_at, scan_interval_hours=None, score_floor=None, states=["HOMEPAGE_READY", "HOMEPAGE_READY_RETRY"]]
[2026-09-25 20:43:15] ERROR src.core.dispatcher: abrams | dispatch company prefilter_company
  ValueError: state must be one of ['IMPORTED', 'NEW', 'DISCOVERED', 'WEBSITE_FOUND', 'WEBSITE_FOUND_RETRY', 'HOMEPAGE_READY', 'NO_WEBSITE', 'WEBSITE_REVIEW', 'PREFILTER_PASSED', 'PJL_READY', 'JOBLIST_IDENTIFIED', 'JOBLIST_IDENTIFIED_RETRY', 'COULD_NOT_PARSE_JOBLIST', 'PREFILTER_PASSED_RETRY', 'NO_PJL_SELECTED', 'PREFILTER_FAILED', 'VET_FAILED', 'NO_PREFILTER_JOBLISTS', 'TO_WATCH', 'WATCH', 'IGNORE', 'METEORITE', 'PREFILTER_UNKNOWN', 'HARD_PARSE', 'NO_OPENINGS', 'JOBS_FOUND', 'NO_JOBLIST', 'CANNOT_PARSE_JOB_SITE', 'CANNOT_READ_WEBSITE', 'BOT_BLOCK', 'ERROR_PREFILTER', 'ERROR_LOCATE_JOB_PAGE', 'JOBSITE_SCRAPE_ISSUE', 'ERROR_GAZE'], got 'HOMEPAGE_READY_RETRY'
  Truncating the batch
Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 1374, in _dispatch_one_body
    await _tracked()
  File "/app/src/core/dispatcher.py", line 1360, in _tracked
    await _run_dispatch_loop(ctx, task, task_key, entity_batch_id, accumulated, dispatch_ledger_id)
  File "/app/src/core/dispatcher.py", line 1537, in _run_dispatch_loop
    summary = await _run_task(task, ctx, debug)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/dispatcher.py", line 911, in _run_task
    summary = await _run_unified(task, ctx, debug)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/dispatcher.py", line 734, in _run_unified
    bid, entities = get_new_company_batch(
                    ^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/roster.py", line 1422, in get_new_company_batch
    raise ValueError(f"state must be one of {allowed!r}, got {s!r}")
ValueError: state must be one of ['IMPORTED', 'NEW', 'DISCOVERED', 'WEBSITE_FOUND', 'WEBSITE_FOUND_RETRY', 'HOMEPAGE_READY', 'NO_WEBSITE', 'WEBSITE_REVIEW', 'PREFILTER_PASSED', 'PJL_READY', 'JOBLIST_IDENTIFIED', 'JOBLIST_IDENTIFIED_RETRY', 'COULD_NOT_PARSE_JOBLIST', 'PREFILTER_PASSED_RETRY', 'NO_PJL_SELECTED', 'PREFILTER_FAILED', 'VET_FAILED', 'NO_PREFILTER_JOBLISTS', 'TO_WATCH', 'WATCH', 'IGNORE', 'METEORITE', 'PREFILTER_UNKNOWN', 'HARD_PARSE', 'NO_OPENINGS', 'JOBS_FOUND', 'NO_JOBLIST', 'CANNOT_PARSE_JOB_SITE', 'CANNOT_READ_WEBSITE', 'BOT_BLOCK', 'ERROR_PREFILTER', 'ERROR_LOCATE_JOB_PAGE', 'JOBSITE_SCRAPE_ISSUE', 'ERROR_GAZE'], got 'HOMEPAGE_READY_RETRY'
```

Dispatcher should not be validating data.  Only claiming batches based on the trigger_state value.  Dispatcher can assume data has already been validated and just run the batch.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._

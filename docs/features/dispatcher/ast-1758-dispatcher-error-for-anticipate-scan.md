# AST-1758 — dispatcher error for anticipate_scan

<!-- linear-archive: AST-1758 archived 2026-09-24 -->

## Linear archive (AST-1758)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1758/dispatcher-error-for-anticipate-scan  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 2  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1670; related: AST-1674

### Description

## As-is

Somerset dispatcher jobs `anticipate_scan` and `contemplate_job` blow up inside `run_consult_task` with `UnboundLocalError: cannot access local variable 'TASK_CONFIG' where it is not associated with a value` (stack points at `src/core/consult.py` \~2706: `task_key in TASK_CONFIG` on the dispatch-chain branch). The batch truncates; those hops never start.

## To-be

`anticipate_scan` / `contemplate_job` (and any other job dispatch-chain trigger that reaches that `elif`) run normally using the module-level `TASK_CONFIG`. `resolve_website` company dispatch still reads the same `pass_state` / `fail_state` values. No UnboundLocalError.

## Proposed steps

1. In `src/core/consult.py` `run_consult_task`, remove the late `from src.utils.config import TASK_CONFIG` under the `task_key == "resolve_website"` company branch — `TASK_CONFIG` is already imported at module level.
2. Leave the `terminal_ok = (TASK_CONFIG["resolve_website"]["pass_state"], …)` lookup as-is so it uses the module binding.
3. Smoke: dispatch `anticipate_scan` / `contemplate_job` no longer raise; `resolve_website` company path still resolves terminals from `TASK_CONFIG["resolve_website"]`.

## Component scope

* `src/core/consult.py` — modified: drop the shadowing late import of `TASK_CONFIG` inside `run_consult_task`'s `resolve_website` branch so the dispatch-chain `elif` at \~2706 sees the module-level name.

## Technical scope

* `src/core/consult.py` / `run_consult_task` — modified function: delete the nested `from src.utils.config import TASK_CONFIG` ([AST-1674](https://linear.app/astralcareermatch/issue/AST-1674/resolve-website-company-dispatch-apply-split-inflow-website-resolve) left it in the company `resolve_website` arm). That import marks `TASK_CONFIG` local for the whole function, so any path that hits `task_key in TASK_CONFIG` without executing that arm (job dispatch-chain triggers like `anticipate_scan`) raises UnboundLocalError. Module-level import already present — no new import, no new function.

## Ancestor candidates

- [ ] [AST-1674](https://linear.app/astralcareermatch/issue/AST-1674/resolve-website-company-dispatch-apply-split-inflow-website-resolve) — resolve_website company dispatch apply (`docs/features/roster/ast-1674-resolve-website-company-dispatch-apply.md`); introduced the late `TASK_CONFIG` import in `run_consult_task` that shadows the module binding. Live, User Testing under [AST-1670](https://linear.app/astralcareermatch/issue/AST-1670/split-inflow-website-resolve-into-cse-fetch-find-company-website).
- [ ] [AST-1670](https://linear.app/astralcareermatch/issue/AST-1670/split-inflow-website-resolve-into-cse-fetch-find-company-website) — Split inflow website resolve into CSE fetch + find_company_website dispatch (parent epic of AST-1674; still User Testing). Use if she wants the bug related to the epic rather than the child.

---

## Original report

```
[
  {
    "batch_id": null,
    "candidate_id": null,
    "created_at": "2026-09-21 20:04:02",
    "id": 121374,
    "level": "ERROR",
    "logger_name": "src.core.dispatcher",
    "message": "somerset | dispatch job contemplate_job\n  UnboundLocalError: cannot access local variable 'TASK_CONFIG' where it is not associated with a value\n  Truncating the batch\nTraceback (most recent call last):\n  File \"/app/src/core/dispatcher.py\", line 1353, in _dispatch_one_body\n    await _tracked()\n  File \"/app/src/core/dispatcher.py\", line 1339, in _tracked\n    await _run_dispatch_loop(ctx, task, task_key, entity_batch_id, accumulated, dispatch_ledger_id)\n  File \"/app/src/core/dispatcher.py\", line 1516, in _run_dispatch_loop\n    summary = await _run_task(task, ctx, debug)\n              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/core/dispatcher.py\", line 890, in _run_task\n    summary = await _run_unified(task, ctx, debug)\n              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/core/dispatcher.py\", line 830, in _run_unified\n    results = await _warm_then_gather(_one, entities, _SUMMARY_ZERO)\n              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/core/dispatcher.py\", line 125, in _warm_then_gather\n    first = await one_fn(entities[0])\n            ^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/core/dispatcher.py\", line 824, in _one\n    result = await consult.run_consult_task(\n             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/core/consult.py\", line 71, in async_wrapper\n    return await fn(*args, **kwargs)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/core/consult.py\", line 2706, in run_consult_task\n    elif is_dispatch_chain_trigger((input_state or \"\").strip()) and task_key in TASK_CONFIG:\n                                                                                ^^^^^^^^^^^\nUnboundLocalError: cannot access local variable 'TASK_CONFIG' where it is not associated with a value"
  },
  {
    "batch_id": null,
    "candidate_id": null,
    "created_at": "2026-09-21 20:04:02",
    "id": 121373,
    "level": "INFO",
    "logger_name": "src.core.dispatcher",
    "message": "somerset | dispatch job starting contemplate_job — 1 available (batch: contemplate_job-bac22ac5-7056-4f32-9fe2-48172c21e25e)"
  },
  {
    "batch_id": null,
    "candidate_id": null,
    "created_at": "2026-09-21 20:04:02",
    "id": 121372,
    "level": "INFO",
    "logger_name": "src.core.dispatcher",
    "message": "somerset | dispatch thread exited for anticipate_scan"
  },
  {
    "batch_id": null,
    "candidate_id": null,
    "created_at": "2026-09-21 20:03:00",
    "id": 121371,
    "level": "ERROR",
    "logger_name": "src.core.dispatcher",
    "message": "somerset | dispatch job anticipate_scan\n  UnboundLocalError: cannot access local variable 'TASK_CONFIG' where it is not associated with a value\n  Truncating the batch\nTraceback (most recent call last):\n  File \"/app/src/core/dispatcher.py\", line 1353, in _dispatch_one_body\n    await _tracked()\n  File \"/app/src/core/dispatcher.py\", line 1339, in _tracked\n    await _run_dispatch_loop(ctx, task, task_key, entity_batch_id, accumulated, dispatch_ledger_id)\n  File \"/app/src/core/dispatcher.py\", line 1516, in _run_dispatch_loop\n    summary = await _run_task(task, ctx, debug)\n              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/core/dispatcher.py\", line 890, in _run_task\n    summary = await _run_unified(task, ctx, debug)\n              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/core/dispatcher.py\", line 830, in _run_unified\n    results = await _warm_then_gather(_one, entities, _SUMMARY_ZERO)\n              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/core/dispatcher.py\", line 125, in _warm_then_gather\n    first = await one_fn(entities[0])\n            ^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/core/dispatcher.py\", line 824, in _one\n    result = await consult.run_consult_task(\n             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/core/consult.py\", line 71, in async_wrapper\n    return await fn(*args, **kwargs)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/core/consult.py\", line 2706, in run_consult_task\n    elif is_dispatch_chain_trigger((input_state or \"\").strip()) and task_key in TASK_CONFIG:\n                                                                                ^^^^^^^^^^^\nUnboundLocalError: cannot access local variable 'TASK_CONFIG' where it is not associated with a value"
  },
  {
    "batch_id": null,
    "candidate_id": null,
    "created_at": "2026-09-21 20:03:00",
    "id": 121370,
    "level": "INFO",
    "logger_name": "src.core.dispatcher",
    "message": "somerset | dispatch job starting anticipate_scan — 1 available (batch: anticipate_scan-1c55feea-c85a-42cd-91a4-1d657ce61ba4)"
  },
  {
    "batch_id": null,
    "candidate_id": null,
    "created_at": "2026-09-21 20:03:00",
    "id": 121369,
    "level": "INFO",
    "logger_name": "src.core.dispatcher",
    "message": "somerset | dispatch thread exited for anticipate_scan"
  },
  {
    "batch_id": null,
    "candidate_id": null,
    "created_at": "2026-09-21 20:02:44",
    "id": 121368,
    "level": "ERROR",
    "logger_name": "src.core.dispatcher",
    "message": "somerset | dispatch job anticipate_scan\n  UnboundLocalError: cannot access local variable 'TASK_CONFIG' where it is not associated with a value\n  Truncating the batch\nTraceback (most recent call last):\n  File \"/app/src/core/dispatcher.py\", line 1353, in _dispatch_one_body\n    await _tracked()\n  File \"/app/src/core/dispatcher.py\", line 1339, in _tracked\n    await _run_dispatch_loop(ctx, task, task_key, entity_batch_id, accumulated, dispatch_ledger_id)\n  File \"/app/src/core/dispatcher.py\", line 1516, in _run_dispatch_loop\n    summary = await _run_task(task, ctx, debug)\n              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/core/dispatcher.py\", line 890, in _run_task\n    summary = await _run_unified(task, ctx, debug)\n              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/core/dispatcher.py\", line 830, in _run_unified\n    results = await _warm_then_gather(_one, entities, _SUMMARY_ZERO)\n              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/core/dispatcher.py\", line 125, in _warm_then_gather\n    first = await one_fn(entities[0])\n            ^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/core/dispatcher.py\", line 824, in _one\n    result = await consult.run_consult_task(\n             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/core/consult.py\", line 71, in async_wrapper\n    return await fn(*args, **kwargs)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/core/consult.py\", line 2706, in run_consult_task\n    elif is_dispatch_chain_trigger((input_state or \"\").strip()) and task_key in TASK_CONFIG:\n                                                                                ^^^^^^^^^^^\nUnboundLocalError: cannot access local variable 'TASK_CONFIG' where it is not associated with a value"
  },
  {
    "batch_id": null,
    "candidate_id": null,
    "created_at": "2026-09-21 20:02:44",
    "id": 121367,
    "level": "INFO",
    "logger_name": "src.core.dispatcher",
    "message": "somerset | dispatch job starting anticipate_scan — 1 available (batch: anticipate_scan-9f63268e-58de-4a1c-a1f0-909e40460550)"
  },
  {
    "batch_id": null,
    "candidate_id": null,
    "created_at": "2026-09-21 20:02:44",
    "id": 121366,
    "level": "INFO",
    "logger_name": "src.core.dispatcher",
    "message": "somerset | dispatch thread exited for meteorite_upshot"
  },
  {
    "batch_id": "meteorite_upshot-a9c05098-2a6f-4c28-a547-1fd720981fd1",
    "candidate_id": null,
    "created_at": "2026-09-21 19:52:01",
    "id": 121365,
    "level": "INFO",
    "logger_name": "src.core.dispatcher",
    "message": "somerset | dispatch job task completed: meteorite_upshot pass:3 fail:0 error:0 (batch: meteorite_upshot-a9c05098-2a6f-4c28-a547-1fd720981fd1)"
  }
]
```

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._

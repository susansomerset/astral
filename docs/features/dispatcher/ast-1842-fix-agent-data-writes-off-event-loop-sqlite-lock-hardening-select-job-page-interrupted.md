# AST-1842 — fix: agent_data writes off event loop + sqlite lock hardening (select_job_page INTERRUPTED)

<!-- linear-archive: AST-1842 archived 2026-10-07 -->

## Linear archive (AST-1842)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1842/fix-agent-data-writes-off-event-loop-sqlite-lock-hardening-select-job  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1825 — [✅/Somerset] select_job_page INTERRUPTED: 1 error(s) / 30 processed | select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f  
**Blocked by / blocks / related:** parent: AST-1825

### Description

## What this implements

Fix for AST-1825. Keep `agent_data` writes from freezing the async event loop during company dispatch, harden the sqlite connection against concurrent-writer locks, and stop a provider-call timeout from being recorded as `NO_JOBLIST` in `select_job_page`. After the fix, the 600s provider budget fires on time, prompt rows stop being dropped with `database is locked`, and a 30–60 company `select_job_page` batch no longer runs into the 3600s dispatch wall. Does not change the provider budget value, the dispatch timeout value, or the `select_job_page` prompt.

## Scope

### Component scope

* `src/core/agent.py` (modified): `do_task` calls the prompt and response `agent_data` stores synchronously from async code. These calls need to move off the event loop.
* `src/data/database.py` (modified): `_get_connection` needs WAL mode and a configured busy timeout. `_run_with_retry`'s blocking sleep has to stay off the loop.
* `src/utils/config.py` (modified): the `db_retry` block (or a sibling block) holds the new busy-timeout and WAL settings, following config-driven convention.
* `src/core/roster.py` (modified, if step 4 stays in scope): the `select_job_page` result mapping currently turns a provider timeout into `NO_JOBLIST`.

### Technical scope

* `src/core/agent.py`: modified function `do_task`. The prompt-block and response-block store calls run in a worker thread (or through new async wrappers around `_store_prompt_blocks` / `_store_response_block`), so a locked DB cannot stall other in-flight provider calls.
* `src/data/database.py`: modified function `_get_connection`, which sets a busy timeout on every connection and makes sure WAL journal mode is on, so concurrent batch writers wait briefly instead of failing. `_run_with_retry` may get an async-aware variant if any call path stays on the loop.
* `src/utils/config.py`: new fields in the `db_retry` config (or a new `db_connection` block) for busy timeout and journal mode, so the values are not hard-coded.
* `src/core/roster.py`: modified function (the `select_job_page` outcome mapping in `run_select_job_page_dispatch` / `_find_job_page_from_assembled`), so a provider-call-budget failure maps to a retryable state instead of `NO_JOBLIST`.

## Acceptance criteria

- [X] A locked or slow `agent_data` write does not block other in-flight provider calls. The per-call budget error fires within about the configured budget plus grace, not 1000s or more.
- [X] Concurrent batch writers no longer produce `database is locked` in normal operation. Prompt and response rows are not silently dropped.
- [X] A `select_job_page` provider-call-budget timeout lands the company in a retryable state with the AST-1189 timeout failure class, not `NO_JOBLIST`.
- [X] A healthy `select_job_page` run still stores prompt and response `agent_data` rows and reaches `JOBLIST_IDENTIFIED` / `NO_JOBLIST` / `NO_PJL_SELECTED` exactly as before.

## Boundaries

* Does not retune `PROVIDER_CALL_BUDGET` or the dispatcher's 3600s timeout.
* Does not add new tables or migrate `agent_data`.
* Does not rework the dispatcher gather or concurrency model beyond moving the DB writes off the loop.

## Notes for planning

No ancestor checkbox was checked on AST-1825, so plan from this Scope plus the parent's As-is / To-be / Proposed steps. Closest prior work is AST-1448 (`docs/features/agent/ast-1448-persist-prompt-before-provider.md`, which added the synchronous prompt write before the provider call) and AST-1189 (`docs/features/artifacts/ast-1189-provider-call-budget-timeout-failure-class.md`, the budget and failure class). Patch target: `docs/features/agent/ast-1448-persist-prompt-before-provider.md`, appending `## Bug: AST-1842` sections there. Do not create a new plan doc. Parent mini-epic: AST-1825.

## Git branch (authoritative)

Parent `ftr/AST-1825-select-job-page-db-lock-loop-stall`, child `sub/AST-1825/AST-1842-agent-data-writes-off-event-loop`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-09-28T15:12:06.627Z
[code-rubric] PROCEED (Commit: b43b7bf9832357371c678f474289ece5b12d50c0) Off-loop writes WAL hold

#### joan — 2026-09-28T15:00:42.190Z
[board-joan]  CANON: OK

#### betty — 2026-09-28T14:59:35.856Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/roster.md + core/agent.md + data/database.md — missing coverage — none of the 3 repros is exercised: no roster test holds PJL_READY on failure_class=provider_call_timeout (only AST-897 balance-refusal hold; roster.py LOCKED_AT_100 needs the new branch), no do_task loop-not-blocked test around save_agent_data, no _get_connection WAL/busy-timeout test. Blast radius breaks nothing existing (test_find_assembled_do_task_failure has no failure_class; no sqlite3.connect mocks).

#### ada — 2026-09-28T14:58:01.054Z
`origin/sub/AST-1825/AST-1842-agent-data-writes-off-event-loop` @ `238ffbdf` · writes off loop, WAL, timeout-hold

---

_Implementation detail may live in git history on `origin/dev`._

# AST-1825 — [✅/Somerset] select_job_page INTERRUPTED: 1 error(s) / 30 processed | select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f

<!-- linear-archive: AST-1825 archived 2026-10-07 -->

## Linear archive (AST-1825)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1825/somerset-select-job-page-interrupted-1-errors-30-processed-select-job  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

A Somerset `select_job_page` company dispatch (batch `select_job_page-903ff01b-…`, 60 companies available) ran into its 3600s dispatch timeout and was truncated (`INTERRUPTED: 1 error(s) / 30 processed`). Along the way:

* `save_agent_data` failed repeatedly with `sqlite3.OperationalError: database is locked`, so prompt rows were dropped ("Continuing without that agent_data row").
* DeepSeek calls reported `Provider call exceeded per-call time budget (600s)` after **1000–1565s**, not \~600s. About 20 of these fired within the same second (04:28:35–04:28:36). Each one sits right next to a company going `PJL_READY -> NO_JOBLIST`, so a timeout appears to be recorded as a real "no job list" verdict. The log lines don't carry the company name on the ERROR side, so this pairing still needs confirming.

Likely mechanism: `do_task` (`src/core/agent.py`) is async, but it calls `_store_prompt_blocks` → `save_agent_data` (and later `_store_response_block` → `save_agent_data`) **synchronously**. When the DB is locked, each commit blocks the event loop for sqlite's default 5s busy wait, up to 3 attempts, plus `time.sleep` backoff in `_run_with_retry` (`src/data/database.py`). That adds up to roughly 16s of frozen loop per failed write. With about 30 companies and several prompt blocks each, the loop stalls for minutes at a time. The `asyncio.wait` timer in `await_provider_call_with_budget` cannot fire during a stall, so all the overdue timers fire together once the loop wakes up, and the whole batch hits the 3600s wall. The DB connection has no WAL journal mode and no explicit busy timeout (`sqlite3.connect(str(DB_PATH))` at `database.py` \~267), so any concurrent writer, such as the other batch running at the same time (`redhat_com` / `eon_io` / …), turns into a lock.

## To-be

* A locked or slow `agent_data` write never freezes the event loop. Other companies' provider calls keep running, and the 600s budget fires within about 600s plus the grace period.
* Concurrent writers (parallel batches, orphaned provider threads finishing late) do not produce `database is locked` in normal operation, so prompt rows are not silently dropped.
* A company whose DeepSeek call timed out is not moved to `NO_JOBLIST` as if the model had answered. It gets a retryable outcome with the timeout failure class, following the AST-1189 contract.
* One slow company no longer pushes a 30–60 company batch into the 3600s dispatch wall.

## Proposed steps

1. Move the synchronous `agent_data` writes off the event loop. Either wrap the `_store_prompt_blocks` / `_store_response_block` calls in `do_task` with `asyncio.to_thread`, or make those helpers awaitable, so a DB wait blocks one worker thread instead of the whole loop.
2. Harden the sqlite connection in `_get_connection`: turn on `PRAGMA journal_mode=WAL` (once, persistent) and set an explicit busy timeout from config, so readers and parallel batches stop locking out writers.
3. Check that `_run_with_retry`'s `time.sleep` only ever runs on a worker thread after step 1. If any path still calls it on the loop, give that path an async-safe variant.
4. In `run_select_job_page_dispatch` / `_find_job_page_from_assembled` (`src/core/roster.py`), send a provider-timeout result (AST-1189 failure class) to a retry state instead of `NO_JOBLIST`.
5. Re-run a 30+ company `select_job_page` batch and confirm the budget errors report about 600s, there are no `database is locked` lines, and the batch finishes under the dispatch timeout.

Design fork for Susan: step 1 alone, step 2 alone, or both. Both is my read. Step 4 may be its own ticket if you'd rather keep this one to the DB and event-loop fix.

## Component scope

* `src/core/agent.py` (modified): `do_task` calls the prompt and response `agent_data` stores synchronously from async code. These calls need to move off the event loop.
* `src/data/database.py` (modified): `_get_connection` needs WAL mode and a configured busy timeout. `_run_with_retry`'s blocking sleep has to stay off the loop.
* `src/utils/config.py` (modified): the `db_retry` block (or a sibling block) holds the new busy-timeout and WAL settings, following config-driven convention.
* `src/core/roster.py` (modified, if step 4 stays in scope): the `select_job_page` result mapping currently turns a provider timeout into `NO_JOBLIST`.

## Technical scope

* `src/core/agent.py`: modified function `do_task`. The prompt-block and response-block store calls run in a worker thread (or through new async wrappers around `_store_prompt_blocks` / `_store_response_block`), so a locked DB cannot stall other in-flight provider calls.
* `src/data/database.py`: modified function `_get_connection`, which sets a busy timeout on every connection and makes sure WAL journal mode is on, so concurrent batch writers wait briefly instead of failing. `_run_with_retry` may get an async-aware variant if any call path stays on the loop.
* `src/utils/config.py`: new fields in the `db_retry` config (or a new `db_connection` block) for busy timeout and journal mode, so the values are not hard-coded.
* `src/core/roster.py`: modified function (the `select_job_page` outcome mapping in `run_select_job_page_dispatch` / `_find_job_page_from_assembled`), so a provider-call-budget failure maps to a retryable state instead of `NO_JOBLIST`.

## Ancestor candidates

- [ ] AST-1189: Provider call budget timeout failure class (`docs/features/artifacts/ast-1189-provider-call-budget-timeout-failure-class.md`). It built `await_provider_call_with_budget` and the 600s budget whose timer is overshooting here.
- [ ] AST-1448: Persist prompt before provider (`docs/features/agent/ast-1448-persist-prompt-before-provider.md`). It added the synchronous prompt `agent_data` write before the provider call, which is the write that locks and blocks the loop.
- [ ] AST-1164: anticipate_scan jobs failing (`docs/features/artifacts/ast-1164-anticipate-scan-jobs-failing.md`). This is the parent epic of AST-1189 and the same long-wait provider symptom family.
- [ ] AST-327: Refactor task dispatcher to run independent threads (`docs/features/dispatcher/ast-327-refactor-task-dispatcher-independent-threads-plan.md`). Origin of the dispatch-thread and timeout model that truncated the batch.
- [ ] AST-1758: dispatcher error for anticipate_scan (`docs/features/dispatcher/ast-1758-dispatcher-error-for-anticipate-scan.md`). Recent orphaned Somerset dispatcher bug in the same project. Different root cause (`UnboundLocalError`), so it's a weak candidate.

## Original report (log)

2026-09-28 03:54:40  \[INFO\]  redhat_com | company state: PJL_READY ->
 NO_PJL_SELECTED (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 03:54:40  \[INFO\]  somerset | dispatch company starting
 select_job_page — 60 available (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:20:31  \[ERROR\]  vectra_ai | select_job_page
   OperationalError: database is locked
   Continuing without that agent_data row
 Traceback (most recent call last):
   File "/app/src/core/agent.py", line 2156, in do_task
     prompt_blocks = \_store_prompt_blocks(
                     ^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/agent.py", line 1340, in \_store_prompt_blocks
     prompt_blocks.append({"type": block_type, "id": \_save(block_type, content)})
                                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/agent.py", line 1294, in \_save
     save_agent_data(
   File "/app/src/data/database.py", line 6985, in save_agent_data
     return \_run_with_retry(\_with_conn)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/data/database.py", line 287, in \_run_with_retry
     return fn()
            ^^^^
   File "/app/src/data/database.py", line 6946, in \_with_conn
     conn.commit()
 sqlite3.OperationalError: database is locked
 2026-09-28 04:20:31  \[ERROR\]  database.\_with_conn failed:
 OperationalError('database is locked') | args=() kwargs={}
 2026-09-28 04:20:32  \[ERROR\]  LLM deepseek task=select_job_page
 1564.7s error=Provider call exceeded per-call time budget (600s)
 2026-09-28 04:20:33  \[ERROR\]  LLM deepseek task=select_job_page
 1553.4s error=Provider call exceeded per-call time budget (600s)
 2026-09-28 04:20:33  \[INFO\]  seasonalworks_labor_ny_gov_3 | company
 state: PJL_READY -> NO_JOBLIST (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:35  \[INFO\]  judi_health_2 | company state: PJL_READY
 -> NO_JOBLIST (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:35  \[ERROR\]  LLM deepseek task=select_job_page
 1242.6s error=Provider call exceeded per-call time budget (600s)
 2026-09-28 04:28:35  \[INFO\]  time_com_2 | company state: PJL_READY ->
 NO_JOBLIST (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:35  \[ERROR\]  LLM deepseek task=select_job_page
 1265.6s error=Provider call exceeded per-call time budget (600s)
 2026-09-28 04:28:35  \[INFO\]  anritsu_com | company state: PJL_READY ->
 NO_JOBLIST (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:35  \[ERROR\]  LLM deepseek task=select_job_page
 1322.8s error=Provider call exceeded per-call time budget (600s)
 2026-09-28 04:28:35  \[INFO\]  vectra_ai | company state: PJL_READY ->
 NO_JOBLIST (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:35  \[ERROR\]  LLM deepseek task=select_job_page
 1359.6s error=Provider call exceeded per-call time budget (600s)
 2026-09-28 04:28:35  \[INFO\]  jobs_thecignagroup_com | company state:
 PJL_READY -> NO_JOBLIST (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:35  \[ERROR\]  LLM deepseek task=select_job_page
 1405.1s error=Provider call exceeded per-call time budget (600s)
 2026-09-28 04:28:35  \[INFO\]  docs_citrix_com | company state:
 PJL_READY -> NO_JOBLIST (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:35  \[ERROR\]  LLM deepseek task=select_job_page
 1424.3s error=Provider call exceeded per-call time budget (600s)
 2026-09-28 04:28:35  \[INFO\]  fcc_gov_2 | company state: PJL_READY ->
 NO_JOBLIST (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:35  \[ERROR\]  LLM deepseek task=select_job_page
 1459.1s error=Provider call exceeded per-call time budget (600s)
 2026-09-28 04:28:35  \[INFO\]  arenasolutions_com | company state:
 PJL_READY -> NO_JOBLIST (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:35  \[ERROR\]  LLM deepseek task=select_job_page
 1524.7s error=Provider call exceeded per-call time budget (600s)
 2026-09-28 04:28:35  \[INFO\]  wellspan_org | company state: PJL_READY
 -> NO_JOBLIST (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:36  \[INFO\]  eon_io | company state: PJL_READY ->
 NO_PJL_SELECTED (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:36  \[INFO\]  global_fujitsu | company state: PJL_READY
 -> NO_PJL_SELECTED (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:36  \[INFO\]  mordorintelligence_com_2 | company state:
 PJL_READY -> NO_PJL_SELECTED (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:36  \[INFO\]  flexera_com | company state: PJL_READY ->
 NO_PJL_SELECTED (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:36  \[INFO\]  i3verticals_com | company state:
 PJL_READY -> NO_PJL_SELECTED (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:36  \[INFO\]  bayhealth_org | company state: PJL_READY
 -> NO_PJL_SELECTED (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:36  \[INFO\]  samsara_com_2 | company state: PJL_READY
 -> PREFILTER_PASSED_RETRY (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:36  \[INFO\]  montenido_com | company state: PJL_READY
 -> NO_PJL_SELECTED (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:36  \[INFO\]  ncbi_nlm_nih_gov | company state:
 PJL_READY -> NO_JOBLIST (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:36  \[ERROR\]  LLM deepseek task=select_job_page
 1001.8s error=Provider call exceeded per-call time budget (600s)
 2026-09-28 04:28:36  \[INFO\]  claroty_com | company state: PJL_READY ->
 NO_JOBLIST (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:36  \[ERROR\]  LLM deepseek task=select_job_page 999.6s
 error=Provider call exceeded per-call time budget (600s)
 2026-09-28 04:28:36  \[INFO\]  fmcsa_dot_gov | company state: PJL_READY
 -> NO_JOBLIST (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:36  \[ERROR\]  LLM deepseek task=select_job_page
 1025.5s error=Provider call exceeded per-call time budget (600s)
 2026-09-28 04:28:36  \[INFO\]  learn_microsoft_com_3 | company state:
 PJL_READY -> NO_JOBLIST (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:36  \[ERROR\]  LLM deepseek task=select_job_page
 1080.5s error=Provider call exceeded per-call time budget (600s)
 2026-09-28 04:28:36  \[INFO\]  semtech_com | company state: PJL_READY ->
 NO_JOBLIST (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:36  \[ERROR\]  LLM deepseek task=select_job_page
 1146.8s error=Provider call exceeded per-call time budget (600s)
 2026-09-28 04:28:36  \[INFO\]  careers_ey_com_2 | company state:
 PJL_READY -> NO_JOBLIST (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:36  \[ERROR\]  LLM deepseek task=select_job_page
 1186.1s error=Provider call exceeded per-call time budget (600s)
 2026-09-28 04:28:37  \[INFO\]  careers_ta_com | company state: PJL_READY
 -> NO_PJL_SELECTED (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:28:37  \[INFO\]  developer_harness_io_3 | company state:
 PJL_READY -> NO_PJL_SELECTED (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:46:26  \[INFO\]  koerber_com | company state: PJL_READY ->
 NO_PJL_SELECTED (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:46:26  \[INFO\]  docs_cloud_google_com_3 | company joblist
 identified: JOBLIST_IDENTIFIED (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:46:26  \[INFO\]  docs_cloud_google_com_3 | company state:
 PJL_READY -> JOBLIST_IDENTIFIED (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:46:27  \[INFO\]  docs_appian_com_2 | company state:
 PJL_READY -> NO_PJL_SELECTED (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:46:27  \[INFO\]  help_splunk_com | company joblist
 identified: JOBLIST_IDENTIFIED (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 04:46:27  \[INFO\]  help_splunk_com | company state:
 PJL_READY -> JOBLIST_IDENTIFIED (batch:
 select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f)
 2026-09-28 05:01:18  \[ERROR\]  somerset | dispatch company select_job_page
   TimeoutError: dispatch timeout after 3600s
 batch=select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f
   Truncating the batch
 Traceback (most recent call last):
   File "/root/.nix-profile/lib/python3.12/asyncio/tasks.py", line 520,
 in wait_for
     return await fut
            ^^^^^^^^^
   File "/app/src/core/dispatcher.py", line 1536, in \_run_dispatch_loop
     summary = await \_run_task(task, ctx, debug)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/dispatcher.py", line 910, in \_run_task
     summary = await \_run_unified(task, ctx, debug)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/dispatcher.py", line 850, in \_run_unified
     results = await \_warm_then_gather(\_one, entities, \_SUMMARY_ZERO)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/dispatcher.py", line 135, in \_warm_then_gather
     rest = await asyncio.gather(\*\[one_fn(e) for e in entities\[1:\]\],
 return_exceptions=True)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/dispatcher.py", line 844, in \_one
     result = await consult.run_consult_task(
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/consult.py", line 72, in async_wrapper
     return await fn(\*args, \*\*kwargs)
            ^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/consult.py", line 2689, in run_consult_task
     return await \_debug_await(
            ^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/consult.py", line 113, in \_debug_await
     result = await coro
              ^^^^^^^^^^
   File "/app/src/core/roster.py", line 936, in run_company_task
     result = await run_select_job_page_dispatch(entity, batch_id, ctx, debug)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/roster.py", line 1033, in run_select_job_page_dispatch
     result = await \_find_job_page_from_assembled(
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/roster.py", line 2156, in \_find_job_page_from_assembled
     res = await do_task(
           ^^^^^^^^^^^^^^
   File "/app/src/core/agent.py", line 103, in wrapper
     return await fn(\*args, \*\*kwargs)
            ^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/agent.py", line 2198, in do_task
     result = await send_to_deepseek(
              ^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/external/deepseek.py", line 248, in send_to_deepseek
     response = await await_provider_call_with_budget(
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/utils/llm_external.py", line 90, in
 await_provider_call_with_budget
     done, \_pending = await asyncio.wait({task}, timeout=timeout_seconds)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/root/.nix-profile/lib/python3.12/asyncio/tasks.py", line 464, in wait
     return await \_wait(fs, timeout, return_when, loop)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/root/.nix-profile/lib/python3.12/asyncio/tasks.py", line 550, in \_wait
     await waiter
 asyncio.exceptions.CancelledError

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
   File "/app/src/core/dispatcher.py", line 1373, in \_dispatch_one_body
     await \_tracked()
   File "/app/src/core/dispatcher.py", line 1361, in \_tracked
     await asyncio.wait_for(
   File "/root/.nix-profile/lib/python3.12/asyncio/tasks.py", line 519,
 in wait_for
     async with timeouts.timeout(timeout):
                ^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/root/.nix-profile/lib/python3.12/asyncio/timeouts.py", line
 115, in **aexit**
     raise TimeoutError from exc_val
 TimeoutError
 2026-09-28 05:01:18  \[ERROR\]  orthopedicsri_com | select_job_page
   OperationalError: database is locked
   Continuing without that agent_data row
 Traceback (most recent call last):
   File "/app/src/core/agent.py", line 2156, in do_task
     prompt_blocks = \_store_prompt_blocks(
                     ^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/agent.py", line 1340, in \_store_prompt_blocks
     prompt_blocks.append({"type": block_type, "id": \_save(block_type, content)})
                                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/agent.py", line 1294, in \_save
     save_agent_data(
   File "/app/src/data/database.py", line 6985, in save_agent_data
     return \_run_with_retry(\_with_conn)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/data/database.py", line 287, in \_run_with_retry
     return fn()
            ^^^^
   File "/app/src/data/database.py", line 6946, in \_with_conn
     conn.commit()
 sqlite3.OperationalError: database is locked
 2026-09-28 05:01:18  \[ERROR\]  database.\_with_conn failed:
 OperationalError('database is locked') | args=() kwargs={}

### Comments

#### chuckles — 2026-09-28T15:26:56.212Z
@susan PR #175 is ready, but finish-up is on hold. It carries AST-1824's `test(AST-1829)` and `test(AST-1830)` from the shared tests branch, and AST-1824's product code isn't on dev yet. Merge AST-1824 first, or tell me to strip those two commits.

---

_Implementation detail may live in git history on `origin/dev`._

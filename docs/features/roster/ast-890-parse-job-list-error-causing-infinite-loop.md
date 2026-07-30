# AST-890 — parse_job_list error causing infinite loop

<!-- linear-archive: AST-890 archived 2026-07-29 -->

## Linear archive (AST-890)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-890/parse-job-list-error-causing-infinite-loop  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Production `parse_job_list` batches are burning the host and stalling the roster pipeline. A claimed batch (dozens of `JOBLIST_IDENTIFIED` companies) launches browsers in a way that collapses into cascading Firefox crashes (SIGSEGV, sandbox EACCES, spawn EAGAIN), leaves companies thrashing through retry, and can sit until the dispatch wall-clock timeout with no clean batch finish. Susan expects parse batches to complete with definite per-company outcomes so the job-list parse hop drains instead of looping or hanging for an hour.

## Functional scope

* Bound browser pressure on `parse_job_list`: a production batch must not spawn an unconstrained storm of simultaneous browsers that exhausts host process/resources and cascades into launch failures for the rest of the batch.
* Definite outcomes per claimed company: each company in a `parse_job_list` run ends in a known destination — successful parse progresses as today (`WATCH` with parse artifacts), or first failure lands the existing parse retry holding state, or exhausted retry lands the existing terminal parse failure — including when the failure is browser/infra (launch crash, context closed, spawn resource errors), not only when the page content itself cannot be parsed.
* Batch completion under partial/infra failure: when some companies succeed and others hit browser/infra errors, the batch still finishes every claimed company (no silent hang waiting for dead browser work) and reports summary counts that match observable state transitions.
* No undrainable reclaim loop: companies that have already exhausted the parse retry contract must leave the `parse_job_list` claim pool; interrupted or timed-out batches must not leave companies stuck mid-claim so the next dispatch endlessly re-picks the same doomed set.
* Preserve happy-path parse: when DOM reload and title-aware parse succeed, companies still move to `WATCH` with the same parse success behavior as today's decomposed hop (AST-721 contract).
* Debug/UAT observability (backend `debug=True`): for each claimed company, emit AST-538-style index headers and `|` detail for what was attempted (scrape/parse), what failed (including infra vs content), and what state was recorded — enough for Susan to verify the batch no longer hangs or loops without reading only aggregate timeout lines.

## Boundaries

* Does not change `select_job_page`, `find_job_page`, prefilter, or gazer job-side tasks.
* Does not redesign successful parse destinations, title/DOM cull semantics, or LLM parse prompt/schema for `parse_job_list`.
* Does not own the sibling `fetch_website` reclaim loop (`AST-889`) — that ticket covers homepage-scrape/prefilter ownership; this ticket is the `parse_job_list` hop only.
* Does not reopen Playwright launch taxonomy / shared-session work already shipped under `AST-853` / `AST-854` except as reuse: new product behavior must respect the existing infra-failure signaling contract and remaining config-as-truth rules (`ASTRAL_CODE_RULES` §2.1) rather than inventing ad-hoc launch constants.
* Does not change Railway host OS / sandbox privileges as a product deliverable; scope is application behavior under the current production environment.
* Does not change default dispatch UI batch-size knobs unless a config-driven concurrency/session limit is required to meet the acceptance criteria (prefer fixing batch browser behavior over silently shrinking product throughput).

## Acceptance criteria

1. On production, Susan runs `parse_job_list` against a non-trivial `JOBLIST_IDENTIFIED` queue and the batch reaches a normal terminal finish (completed, or INTERRUPTED only on explicit cancel / true wall-clock policy) without sitting for a full dispatch timeout while Firefox launch errors cascade and little or no work progresses.
2. Under induced or natural browser/infra failure mid-batch, every claimed company lands in a verifiable state (`WATCH`, `JOBLIST_IDENTIFIED_RETRY`, or `COULD_NOT_PARSE_JOBLIST` per existing strike rules) — no company remains indefinitely claimed or invisible to the next eligible dispatch.
3. After one parse retry has already been consumed, a further infra or parse failure moves the company to `COULD_NOT_PARSE_JOBLIST` (or equivalent existing terminal) so it stops being reclaimed by `parse_job_list`.
4. Successful parses in the same batch still reach `WATCH`; failures on other companies do not abort or strand the successful ones.
5. With `debug=True`, Susan can scan per-company index headers and substantive `|` detail lines showing attempt outcome and recorded state for the parse hop (AST-538 / AST-554 contract).
6. A follow-up dispatch on the remaining eligible pool does not sit in an endless reclaim of the same already-exhausted companies with no state change.

## Dependencies and blockers

* none (Playwright stability / `fetch_website` infra routing from AST-850 children are Done; sibling AST-889 is adjacent Discussion on a different task and is not a hard blocker).

## Open questions

none

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-890 (parent) | ftr/AST-890-parse-job-list-infinite-loop |
| AST-891 | sub/AST-890/AST-891-parse-job-list-browser-and-batch |

**Epic worktree:** `astral-AST-890/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | bb9e0447-933f-40ce-bf70-eb713f5b9069 |
| Betty | qa | 432d785a-6fc4-4014-aa76-6bf3940e7342 |
| Radia | review | dcaa0756-c316-4a7f-892f-da5641b4fcf7 |

---

## Original brief

```
2026-07-13 18:37:06  [INFO]  dispatcher._run_unified index 19/20
naqcyber_com -> claimed
2026-07-13 18:37:06  [INFO]   | entity_type=company
trigger_state=JOBLIST_IDENTIFIED state='JOBLIST_IDENTIFIED'
2026-07-13 18:37:06  [INFO]  dispatcher._run_unified index 18/20
zymr_com -> claimed
2026-07-13 18:37:06  [INFO]   | entity_type=company
trigger_state=JOBLIST_IDENTIFIED state='JOBLIST_IDENTIFIED'
2026-07-13 18:37:06  [INFO]  dispatcher._run_unified index 17/20
careers_evercommerce_com -> claimed
2026-07-13 18:37:06  [INFO]   | entity_type=company
trigger_state=JOBLIST_IDENTIFIED state='JOBLIST_IDENTIFIED'
2026-07-13 18:37:06  [INFO]  dispatcher._run_unified index 16/20
careers_oracle_com -> claimed
2026-07-13 18:37:06  [INFO]   | entity_type=company
trigger_state=JOBLIST_IDENTIFIED state='JOBLIST_IDENTIFIED'
2026-07-13 18:37:06  [INFO]  dispatcher._run_unified index 15/20
darroweverett_com -> claimed
2026-07-13 18:37:06  [INFO]   | entity_type=company
trigger_state=JOBLIST_IDENTIFIED state='JOBLIST_IDENTIFIED'
2026-07-13 18:37:06  [INFO]  dispatcher._run_unified index 14/20
henrycountyga_gov -> claimed
2026-07-13 18:37:06  [INFO]   | entity_type=company
trigger_state=JOBLIST_IDENTIFIED state='JOBLIST_IDENTIFIED'
2026-07-13 18:37:06  [INFO]  dispatcher._run_unified index 13/20
coastal_ca_gov -> claimed
2026-07-13 18:37:06  [INFO]   | entity_type=company
trigger_state=JOBLIST_IDENTIFIED state='JOBLIST_IDENTIFIED'
2026-07-13 18:37:06  [INFO]  dispatcher._run_unified index 12/20
discover_pbc_gov -> claimed
2026-07-13 18:37:06  [INFO]   | entity_type=company
trigger_state=JOBLIST_IDENTIFIED state='JOBLIST_IDENTIFIED'
2026-07-13 18:37:06  [INFO]  dispatcher._run_unified index 11/20
talents_vaia_com -> claimed
2026-07-13 18:37:06  [INFO]   | entity_type=company
trigger_state=JOBLIST_IDENTIFIED state='JOBLIST_IDENTIFIED'
2026-07-13 18:37:06  [INFO]  dispatcher._run_unified index 10/20
techforgov_ai -> claimed
2026-07-13 18:37:06  [INFO]   | entity_type=company
trigger_state=JOBLIST_IDENTIFIED state='JOBLIST_IDENTIFIED'
2026-07-13 18:37:06  [INFO]  dispatcher._run_unified index 9/20
eproval_com -> claimed
2026-07-13 18:37:06  [INFO]   | entity_type=company
trigger_state=JOBLIST_IDENTIFIED state='JOBLIST_IDENTIFIED'
2026-07-13 18:37:06  [INFO]  dispatcher._run_unified index 8/20
govsense_com -> claimed
2026-07-13 18:37:06  [INFO]   | entity_type=company
trigger_state=JOBLIST_IDENTIFIED state='JOBLIST_IDENTIFIED'
2026-07-13 18:37:06  [INFO]  dispatcher._run_unified index 7/20
pacera_com -> claimed
2026-07-13 18:37:06  [INFO]   | entity_type=company
trigger_state=JOBLIST_IDENTIFIED state='JOBLIST_IDENTIFIED'
2026-07-13 18:37:06  [INFO]  dispatcher._run_unified index 6/20
thorbis_com -> claimed
2026-07-13 18:37:06  [INFO]   | entity_type=company
trigger_state=JOBLIST_IDENTIFIED state='JOBLIST_IDENTIFIED'
2026-07-13 18:37:06  [INFO]  dispatcher._run_unified index 5/20
multibilling_com -> claimed
2026-07-13 18:37:06  [INFO]   | entity_type=company
trigger_state=JOBLIST_IDENTIFIED state='JOBLIST_IDENTIFIED'
2026-07-13 18:37:06  [INFO]  dispatcher._run_unified index 4/20
acquriotech_com -> claimed
2026-07-13 18:37:06  [INFO]   | entity_type=company
trigger_state=JOBLIST_IDENTIFIED state='JOBLIST_IDENTIFIED'
2026-07-13 18:37:06  [INFO]  dispatcher._run_unified index 3/20
3gis_com -> claimed
2026-07-13 18:37:06  [INFO]   | entity_type=company
trigger_state=JOBLIST_IDENTIFIED state='JOBLIST_IDENTIFIED'
2026-07-13 18:37:06  [INFO]  dispatcher._run_unified index 2/20
hitachienergy_com -> claimed
2026-07-13 18:37:06  [INFO]   | entity_type=company
trigger_state=JOBLIST_IDENTIFIED state='JOBLIST_IDENTIFIED'
2026-07-13 18:37:06  [INFO]  dispatcher._run_unified index 1/20
zinfi_com -> claimed
2026-07-13 18:37:06  [INFO]   | task_key=parse_job_list
batch_id=parse_job_list-a904618e-b284-4f1b-b868-d7f4dffdc870
batch_call_mode=False dispatch batch_size=20 claim_cap=None
claim_states=['JOBLIST_IDENTIFIED', 'JOBLIST_IDENTIFIED_RETRY']
2026-07-13 18:37:06  [INFO]  dispatcher._run_unified index 1/1
company/JOBLIST_IDENTIFIED -> claimed 20 entity/entities
2026-07-13 18:37:06  [INFO]   | batch_size=20
batch_id=parse_job_list-a904618e-b284-4f1b-b868-d7f4dffdc870
entity_type='company' trigger_state='JOBLIST_IDENTIFIED'
2026-07-13 18:37:06  [INFO]  dispatcher._run_task index 1/1
parse_job_list -> running batch
2026-07-13 18:37:06  [INFO]   | available=322 effective_min=1
max_runs=0 draining=False
entity_batch_id=parse_job_list-a904618e-b284-4f1b-b868-d7f4dffdc870
2026-07-13 18:37:06  [INFO]  dispatcher._run_dispatch_loop index 1/1
parse_job_list -> loop iteration 1 starting
2026-07-13 18:37:06  [INFO]  Dispatching parse_job_list — 322
available, batch parse_job_list-a904618e-b284-4f1b-b868-d7f4dffdc870
2026-07-13 18:37:15  [INFO]  roster.run_parse_job_list_dispatch index
1/1 zinfi_com -> url=https://careers.zinfi.com titles=9
state=JOBLIST_IDENTIFIED
2026-07-13 18:37:15  [INFO]   | entity_type=company
trigger_state=JOBLIST_IDENTIFIED state='JOBLIST_IDENTIFIED'
2026-07-13 18:37:15  [INFO]  dispatcher._run_unified index 20/20
osano_com -> claimed
2026-07-13 18:37:15  [INFO]   | entity_type=company
trigger_state=JOBLIST_IDENTIFIED state='JOBLIST_IDENTIFIED'
2026-07-13 18:37:16  [INFO]   | response_type='PARSE_DISPATCH_OK' ->
state='WATCH' cull='culled'
2026-07-13 18:37:16  [INFO]  [zinfi_com] company state
JOBLIST_IDENTIFIED -> WATCH
(batch_id=parse_job_list-a904618e-b284-4f1b-b868-d7f4dffdc870)
2026-07-13 18:37:16  [INFO]  do_task(parse_job_list) completed
successfully batch_id=parse_job_list-a904618e-b284-4f1b-b868-d7f4dffdc870
index=zinfi_com
2026-07-13 18:37:16  [INFO]  LLM deepseek task=parse_job_list 2.2s
stop=end_turn tokens in=3060 out=131
2026-07-13 18:37:16  [INFO]  run_next chain entry: task=parse_job_list
batch_id=parse_job_list-a904618e-b284-4f1b-b868-d7f4dffdc870
2026-07-13 18:37:16  [INFO]   | titles=9 pre_cull_chars=20255
post_cull_chars=11336 containers=1 cull_outcome='culled'
2026-07-13 18:37:16  [INFO]   | ready=True visible_chars=9890
listing_hits=0 wait_ms=1110 load_all_jobs_ran=False
2026-07-13 18:37:16  [INFO]  roster._scrape_list_page_dom_for_parse
index 1/1 https://careers.zinfi.com -> ready
2026-07-13 18:37:23  [INFO]   | titles=3 pre_cull_chars=15945
post_cull_chars=0 containers=1 cull_outcome='cull_miss'
2026-07-13 18:37:23  [WARNING]  Firefox launch attempt 2/3 failed:
Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-aWw1Ma
-juggler-pipe -silent
<launched> pid=714667
[pid=714667][err] [714667] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=714667][err] *** You are running in headless mode.
[pid=714667] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=714667] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-aWw1Ma
-juggler-pipe -silent
  - <launched> pid=714667
  - [pid=714667][err] [714667] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=714667][err] *** You are running in headless mode.
  - [pid=714667] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=714667] starting temporary directories cleanup
  - [pid=714667] <gracefully close start>
  - [pid=714667] <kill>
  - [pid=714667] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=714667] finished temporary directories cleanup
  - [pid=714667] <gracefully close end>

2026-07-13 18:37:23  [INFO]   | ready=True visible_chars=10763
listing_hits=4 wait_ms=36 load_all_jobs_ran=False
2026-07-13 18:37:23  [INFO]  roster._scrape_list_page_dom_for_parse
index 1/1 https://secure.pbc.gov/onlinejobs/job/jobopeningstudent ->
ready
2026-07-13 18:37:23  [WARNING]  Firefox launch attempt 2/3 failed:
Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-1dP0L0
-juggler-pipe -silent
<launched> pid=714659
[pid=714659] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=714659] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-1dP0L0
-juggler-pipe -silent
  - <launched> pid=714659
  - [pid=714659] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=714659] starting temporary directories cleanup
  - [pid=714659] <gracefully close start>
  - [pid=714659] <kill>
  - [pid=714659] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=714659] finished temporary directories cleanup
  - [pid=714659] <gracefully close end>

2026-07-13 18:37:23  [WARNING]  Firefox launch attempt 2/3 failed:
Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-I4CmdQ
-juggler-pipe -silent
<launched> pid=714628
[pid=714628][err] [714628] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=714628][err] *** You are running in headless mode.
[pid=714628][out] [GFX1-]: FireTestProcess failed: Failed to spawn
child process “/app/.browsers/firefox-1532/firefox/glxtest” (Resource
temporarily unavailable)
[pid=714628][out]
[pid=714628] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=714628] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-I4CmdQ
-juggler-pipe -silent
  - <launched> pid=714628
  - [pid=714628][err] [714628] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=714628][err] *** You are running in headless mode.
  - [pid=714628][out] [GFX1-]: FireTestProcess failed: Failed to spawn
child process “/app/.browsers/firefox-1532/firefox/glxtest” (Resource
temporarily unavailable)
  - [pid=714628][out]
  - [pid=714628] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=714628] starting temporary directories cleanup
  - [pid=714628] <gracefully close start>
  - [pid=714628] <kill>
  - [pid=714628] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=714628] finished temporary directories cleanup
  - [pid=714628] <gracefully close end>

2026-07-13 18:37:23  [WARNING]  Firefox launch attempt 2/3 failed:
Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-xjt05U
-juggler-pipe -silent
<launched> pid=714630
[pid=714630] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=714630] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-xjt05U
-juggler-pipe -silent
  - <launched> pid=714630
  - [pid=714630] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=714630] starting temporary directories cleanup
  - [pid=714630] <gracefully close start>
  - [pid=714630] <kill>
  - [pid=714630] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=714630] finished temporary directories cleanup
  - [pid=714630] <gracefully close end>

2026-07-13 18:37:23  [ERROR]  [3gis_com] run_company_task exception:
Browser.new_context: Target page, context or browser has been closed
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-Nxl3iQ
-juggler-pipe -silent
<launched> pid=712523
[pid=712523][err] [712523] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=712523][err] *** You are running in headless mode.
[pid=712523][err] JavaScript warning:
resource://services-settings/Utils.sys.mjs, line 119: unreachable code
after return statement
[pid=712523][out]
[pid=712523][out] Juggler listening to the pipe
[pid=712523][err] [Parent 712523, IPC I/O Parent] WARNING: Failed to
launch socket subprocess @FSC::SFNS::Recv (Error:0): file
./../../../ipc/glue/GeckoChildProcessHost.cpp:823
Traceback (most recent call last):
  File "/app/src/core/roster.py", line 1045, in run_company_task
    result = await run_parse_job_list_dispatch(entity, batch_id, ctx, debug)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/roster.py", line 1294, in run_parse_job_list_dispatch
    async with create_browser_context() as browser_context:
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.nix-profile/lib/python3.12/contextlib.py", line 210, in
__aenter__
    return await anext(self.gen)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 592, in create_browser_context
    context = await browser.new_context(viewport=viewport_dict)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/async_api/_generated.py",
line 15977, in new_context
    await self._impl_obj.new_context(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_browser.py",
line 174, in new_context
    channel = await self._channel.send("newContext", None, params)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py",
line 69, in send
    return await self._connection.wrap_api_call(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py",
line 563, in wrap_api_call
    raise rewrite_error(error, f"{parsed_st['apiName']}: {error}") from None
playwright._impl._errors.TargetClosedError: Browser.new_context:
Target page, context or browser has been closed
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-Nxl3iQ
-juggler-pipe -silent
<launched> pid=712523
[pid=712523][err] [712523] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=712523][err] *** You are running in headless mode.
[pid=712523][err] JavaScript warning:
resource://services-settings/Utils.sys.mjs, line 119: unreachable code
after return statement
[pid=712523][out]
[pid=712523][out] Juggler listening to the pipe
[pid=712523][err] [Parent 712523, IPC I/O Parent] WARNING: Failed to
launch socket subprocess @FSC::SFNS::Recv (Error:0): file
./../../../ipc/glue/GeckoChildProcessHost.cpp:823
2026-07-13 18:37:23  [WARNING]  Firefox launch attempt 1/3 failed:
Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-q4LWya
-juggler-pipe -silent
<launched> pid=712391
[pid=712391][err] [712391] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=712391][err] *** You are running in headless mode.
[pid=712391][err] JavaScript warning:
resource://services-settings/Utils.sys.mjs, line 119: unreachable code
after return statement
[pid=712391][out] Crash Annotation GraphicsCriticalError: |[0][GFX1-]:
Compositor thread not started (true) (t=3.94944) [GFX1-]: Compositor
thread not started (true)
[pid=712391] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=712391] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-q4LWya
-juggler-pipe -silent
  - <launched> pid=712391
  - [pid=712391][err] [712391] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=712391][err] *** You are running in headless mode.
  - [pid=712391][err] JavaScript warning:
resource://services-settings/Utils.sys.mjs, line 119: unreachable code
after return statement
  - [pid=712391][out] Crash Annotation GraphicsCriticalError:
|[0][GFX1-]: Compositor thread not started (true) (t=3.94944) [GFX1-]:
Compositor thread not started (true)
  - [pid=712391] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=712391] starting temporary directories cleanup
  - [pid=712391] <gracefully close start>
  - [pid=712391] <kill>
  - [pid=712391] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=712391] finished temporary directories cleanup
  - [pid=712391] <gracefully close end>

2026-07-13 18:37:23  [WARNING]  Firefox launch attempt 1/3 failed:
Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-BuCJdt
-juggler-pipe -silent
<launched> pid=712431
[pid=712431][err] [712431] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=712431][err] *** You are running in headless mode.
[pid=712431][err] JavaScript warning:
resource://services-settings/Utils.sys.mjs, line 119: unreachable code
after return statement
[pid=712431] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=712431] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-BuCJdt
-juggler-pipe -silent
  - <launched> pid=712431
  - [pid=712431][err] [712431] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=712431][err] *** You are running in headless mode.
  - [pid=712431][err] JavaScript warning:
resource://services-settings/Utils.sys.mjs, line 119: unreachable code
after return statement
  - [pid=712431] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=712431] starting temporary directories cleanup
  - [pid=712431] <gracefully close start>
  - [pid=712431] <kill>
  - [pid=712431] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=712431] finished temporary directories cleanup
  - [pid=712431] <gracefully close end>

2026-07-13 18:37:23  [WARNING]  Firefox launch attempt 1/3 failed:
TargetClosedError: BrowserType.launch: Target page, context or browser
has been closed
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-lRZnT4
-juggler-pipe -silent
<launched> pid=712432
[pid=712432][err] [712432] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=712432][err] *** You are running in headless mode.
[pid=712432][err] JavaScript warning:
resource://services-settings/Utils.sys.mjs, line 119: unreachable code
after return statement
[pid=712432][out]
[pid=712432][out] Juggler listening to the pipe
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-lRZnT4
-juggler-pipe -silent
  - <launched> pid=712432
  - [pid=712432][err] [712432] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=712432][err] *** You are running in headless mode.
  - [pid=712432][err] JavaScript warning:
resource://services-settings/Utils.sys.mjs, line 119: unreachable code
after return statement
  - [pid=712432][out]
  - [pid=712432][out] Juggler listening to the pipe
  - [pid=712432] <gracefully close start>
  - [pid=712432] <kill>
  - [pid=712432] <will force kill>
  - [pid=712432] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=712432] starting temporary directories cleanup
  - [pid=712432] finished temporary directories cleanup
  - [pid=712432] <gracefully close end>

2026-07-13 18:37:23  [WARNING]  Firefox launch attempt 1/3 failed:
Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-tDaKXY
-juggler-pipe -silent
<launched> pid=712516
[pid=712516][err] [712516] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=712516][err] *** You are running in headless mode.
[pid=712516][err] JavaScript warning:
resource://services-settings/Utils.sys.mjs, line 119: unreachable code
after return statement
[pid=712516][out] Crash Annotation GraphicsCriticalError: |[0][GFX1-]:
Compositor thread not started (true) (t=3.16726) [GFX1-]: Compositor
thread not started (true)
[pid=712516] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=712516] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-tDaKXY
-juggler-pipe -silent
  - <launched> pid=712516
  - [pid=712516][err] [712516] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=712516][err] *** You are running in headless mode.
  - [pid=712516][err] JavaScript warning:
resource://services-settings/Utils.sys.mjs, line 119: unreachable code
after return statement
  - [pid=712516][out] Crash Annotation GraphicsCriticalError:
|[0][GFX1-]: Compositor thread not started (true) (t=3.16726) [GFX1-]:
Compositor thread not started (true)
  - [pid=712516] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=712516] starting temporary directories cleanup
  - [pid=712516] <gracefully close start>
  - [pid=712516] <kill>
  - [pid=712516] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=712516] finished temporary directories cleanup
  - [pid=712516] <gracefully close end>

2026-07-13 18:37:23  [WARNING]  Firefox launch attempt 1/3 failed:
Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-TzLnPb
-juggler-pipe -silent
<launched> pid=712373
[pid=712373][err] [712373] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=712373][err] *** You are running in headless mode.
[pid=712373] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=712373] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-TzLnPb
-juggler-pipe -silent
  - <launched> pid=712373
  - [pid=712373][err] [712373] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=712373][err] *** You are running in headless mode.
  - [pid=712373] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=712373] starting temporary directories cleanup
  - [pid=712373] <gracefully close start>
  - [pid=712373] <kill>
  - [pid=712373] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=712373] finished temporary directories cleanup
  - [pid=712373] <gracefully close end>

2026-07-13 18:37:23  [WARNING]  Firefox launch attempt 1/3 failed:
Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-W07Cas
-juggler-pipe -silent
<launched> pid=712390
[pid=712390][err] [712390] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=712390][err] *** You are running in headless mode.
[pid=712390] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=712390] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-W07Cas
-juggler-pipe -silent
  - <launched> pid=712390
  - [pid=712390][err] [712390] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=712390][err] *** You are running in headless mode.
  - [pid=712390] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=712390] starting temporary directories cleanup
  - [pid=712390] <gracefully close start>
  - [pid=712390] <kill>
  - [pid=712390] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=712390] finished temporary directories cleanup
  - [pid=712390] <gracefully close end>

2026-07-13 18:37:23  [WARNING]  Firefox launch attempt 1/3 failed:
Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-Zocp2q
-juggler-pipe -silent
<launched> pid=712534
[pid=712534][err] [712534] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=712534][err] *** You are running in headless mode.
[pid=712534] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=712534] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-Zocp2q
-juggler-pipe -silent
  - <launched> pid=712534
  - [pid=712534][err] [712534] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=712534][err] *** You are running in headless mode.
  - [pid=712534] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=712534] starting temporary directories cleanup
  - [pid=712534] <gracefully close start>
  - [pid=712534] <kill>
  - [pid=712534] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=712534] finished temporary directories cleanup
  - [pid=712534] <gracefully close end>

2026-07-13 18:37:23  [WARNING]  Firefox launch attempt 1/3 failed:
Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-TnMBlO
-juggler-pipe -silent
<launched> pid=712515
[pid=712515][err] [712515] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=712515][err] *** You are running in headless mode.
[pid=712515] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=712515] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-TnMBlO
-juggler-pipe -silent
  - <launched> pid=712515
  - [pid=712515][err] [712515] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=712515][err] *** You are running in headless mode.
  - [pid=712515] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=712515] starting temporary directories cleanup
  - [pid=712515] <gracefully close start>
  - [pid=712515] <kill>
  - [pid=712515] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=712515] finished temporary directories cleanup
  - [pid=712515] <gracefully close end>

2026-07-13 18:37:23  [INFO]  [careers_oracle_com] company state
JOBLIST_IDENTIFIED -> JOBLIST_IDENTIFIED_RETRY
(batch_id=parse_job_list-a904618e-b284-4f1b-b868-d7f4dffdc870)
2026-07-13 18:37:23  [INFO]  [pacera_com] company state
JOBLIST_IDENTIFIED -> JOBLIST_IDENTIFIED_RETRY
(batch_id=parse_job_list-a904618e-b284-4f1b-b868-d7f4dffdc870)
2026-07-13 18:37:23  [WARNING]  Firefox launch attempt 1/3 failed:
Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-iueFEb
-juggler-pipe -silent
<launched> pid=712493
[pid=712493][err] [712493] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=712493][err] *** You are running in headless mode.
[pid=712493][err] JavaScript warning:
resource://services-settings/Utils.sys.mjs, line 119: unreachable code
after return statement
[pid=712493] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=712493] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-iueFEb
-juggler-pipe -silent
  - <launched> pid=712493
  - [pid=712493][err] [712493] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=712493][err] *** You are running in headless mode.
  - [pid=712493][err] JavaScript warning:
resource://services-settings/Utils.sys.mjs, line 119: unreachable code
after return statement
  - [pid=712493] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=712493] starting temporary directories cleanup
  - [pid=712493] <gracefully close start>
  - [pid=712493] <kill>
  - [pid=712493] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=712493] finished temporary directories cleanup
  - [pid=712493] <gracefully close end>

2026-07-13 18:37:23  [INFO]  [talents_vaia_com] company state
JOBLIST_IDENTIFIED -> JOBLIST_IDENTIFIED_RETRY
(batch_id=parse_job_list-a904618e-b284-4f1b-b868-d7f4dffdc870)
2026-07-13 18:37:23  [INFO]  [eproval_com] company state
JOBLIST_IDENTIFIED -> JOBLIST_IDENTIFIED_RETRY
(batch_id=parse_job_list-a904618e-b284-4f1b-b868-d7f4dffdc870)
2026-07-13 18:37:23  [INFO]  roster.run_parse_job_list_dispatch index
1/1 osano_com -> url=https://www.osano.com/company/careers titles=7
state=JOBLIST_IDENTIFIED
2026-07-13 18:37:23  [INFO]  roster.run_parse_job_list_dispatch index
1/1 naqcyber_com -> url=https://www.naqcyber.com/company/vacancies
titles=1 state=JOBLIST_IDENTIFIED
2026-07-13 18:37:23  [INFO]  roster.run_parse_job_list_dispatch index
1/1 zymr_com -> url=https://www.zymr.com/careers titles=8
state=JOBLIST_IDENTIFIED
2026-07-13 18:37:23  [INFO]  roster.run_parse_job_list_dispatch index
1/1 careers_evercommerce_com ->
url=https://careers.evercommerce.com/us/search-results titles=1
state=JOBLIST_IDENTIFIED
2026-07-13 18:37:23  [INFO]  roster.run_parse_job_list_dispatch index
1/1 careers_oracle_com ->
url=https://careers.oracle.com/en/sites/jobsearch/jobs titles=13
state=JOBLIST_IDENTIFIED
2026-07-13 18:37:23  [INFO]  roster.run_parse_job_list_dispatch index
1/1 darroweverett_com -> url=https://darroweverett.com/careers
titles=3 state=JOBLIST_IDENTIFIED
2026-07-13 18:37:23  [INFO]  roster.run_parse_job_list_dispatch index
1/1 henrycountyga_gov ->
url=https://www.governmentjobs.com/careers/henryga titles=10
state=JOBLIST_IDENTIFIED
2026-07-13 18:37:23  [INFO]  roster.run_parse_job_list_dispatch index
1/1 coastal_ca_gov -> url=https://www.coastal.ca.gov/jobs titles=5
state=JOBLIST_IDENTIFIED
2026-07-13 18:37:23  [INFO]  roster.run_parse_job_list_dispatch index
1/1 discover_pbc_gov ->
url=https://secure.pbc.gov/onlinejobs/job/jobopeningstudent titles=3
state=JOBLIST_IDENTIFIED
2026-07-13 18:37:23  [INFO]  roster.run_parse_job_list_dispatch index
1/1 talents_vaia_com -> url=https://talents.vaia.com/jobs titles=10
state=JOBLIST_IDENTIFIED
2026-07-13 18:37:23  [INFO]  roster.run_parse_job_list_dispatch index
1/1 techforgov_ai -> url=https://www.techforgov.ai/contact-us/careers
titles=3 state=JOBLIST_IDENTIFIED
2026-07-13 18:37:23  [INFO]  roster.run_parse_job_list_dispatch index
1/1 eproval_com -> url=https://www.eproval.com/careers titles=1
state=JOBLIST_IDENTIFIED
2026-07-13 18:37:23  [INFO]  roster.run_parse_job_list_dispatch index
1/1 govsense_com -> url=https://govsense.com/careers titles=2
state=JOBLIST_IDENTIFIED
2026-07-13 18:37:23  [INFO]  roster.run_parse_job_list_dispatch index
1/1 pacera_com -> url=https://careers.pacera.com titles=5
state=JOBLIST_IDENTIFIED
2026-07-13 18:37:23  [INFO]  roster.run_parse_job_list_dispatch index
1/1 thorbis_com -> url=https://thorbis.com/careers titles=5
state=JOBLIST_IDENTIFIED
2026-07-13 18:37:23  [INFO]  roster.run_parse_job_list_dispatch index
1/1 multibilling_com ->
url=https://munibilling.apscareerportal.com/account?utm_campaign=hr%20recruiting%20&utm_source=applicant%20pool&utm_medium=header
titles=2 state=JOBLIST_IDENTIFIED
2026-07-13 18:37:23  [INFO]  roster.run_parse_job_list_dispatch index
1/1 acquriotech_com -> url=https://acquriotech.com/careers titles=6
state=JOBLIST_IDENTIFIED
2026-07-13 18:37:23  [INFO]  roster.run_parse_job_list_dispatch index
1/1 3gis_com -> url=https://www.3-gis.com/about-us/current-positions
titles=8 state=JOBLIST_IDENTIFIED
2026-07-13 18:37:23  [INFO]  roster.run_parse_job_list_dispatch index
1/1 hitachienergy_com ->
url=https://www.hitachienergy.com/careers/open-jobs titles=10
state=JOBLIST_IDENTIFIED
2026-07-13 18:37:25  [ERROR]  [acquriotech_com] run_company_task
exception: [unknown] BrowserType.launch: Failed to launch the browser
process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-0lsePR
-juggler-pipe -silent
<launched> pid=715283
[pid=715283][err] [715283] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=715283][err] *** You are running in headless mode.
[pid=715283][err] JavaScript warning:
resource://services-settings/Utils.sys.mjs, line 119: unreachable code
after return statement
[pid=715283] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=715283] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-0lsePR
-juggler-pipe -silent
  - <launched> pid=715283
  - [pid=715283][err] [715283] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=715283][err] *** You are running in headless mode.
  - [pid=715283][err] JavaScript warning:
resource://services-settings/Utils.sys.mjs, line 119: unreachable code
after return statement
  - [pid=715283] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=715283] starting temporary directories cleanup
  - [pid=715283] <gracefully close start>
  - [pid=715283] <kill>
  - [pid=715283] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=715283] finished temporary directories cleanup
  - [pid=715283] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
Traceback (most recent call last):
  File "/app/src/external/playwright.py", line 111, in _launch_browser
    browser = await pw.firefox.launch(
              ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/async_api/_generated.py",
line 16546, in launch
    await self._impl_obj.launch(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_browser_type.py",
line 97, in launch
    await self._channel.send(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py",
line 69, in send
    return await self._connection.wrap_api_call(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py",
line 563, in wrap_api_call
    raise rewrite_error(error, f"{parsed_st['apiName']}: {error}") from None
playwright._impl._errors.Error: BrowserType.launch: Failed to launch
the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-0lsePR
-juggler-pipe -silent
<launched> pid=715283
[pid=715283][err] [715283] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=715283][err] *** You are running in headless mode.
[pid=715283][err] JavaScript warning:
resource://services-settings/Utils.sys.mjs, line 119: unreachable code
after return statement
[pid=715283] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=715283] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-0lsePR
-juggler-pipe -silent
  - <launched> pid=715283
  - [pid=715283][err] [715283] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=715283][err] *** You are running in headless mode.
  - [pid=715283][err] JavaScript warning:
resource://services-settings/Utils.sys.mjs, line 119: unreachable code
after return statement
  - [pid=715283] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=715283] starting temporary directories cleanup
  - [pid=715283] <gracefully close start>
  - [pid=715283] <kill>
  - [pid=715283] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=715283] finished temporary directories cleanup
  - [pid=715283] <gracefully close end>


The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/app/src/core/roster.py", line 1045, in run_company_task
    result = await run_parse_job_list_dispatch(entity, batch_id, ctx, debug)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/roster.py", line 1294, in run_parse_job_list_dispatch
    async with create_browser_context() as browser_context:
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.nix-profile/lib/python3.12/contextlib.py", line 210, in
__aenter__
    return await anext(self.gen)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 591, in create_browser_context
    browser = await _launch_browser(pw, headless=headless)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 136, in _launch_browser
    raise PlaywrightInfraError(fc, detail) from last_err
src.external.playwright.PlaywrightInfraError: [unknown]
BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-0lsePR
-juggler-pipe -silent
<launched> pid=715283
[pid=715283][err] [715283] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=715283][err] *** You are running in headless mode.
[pid=715283][err] JavaScript warning:
resource://services-settings/Utils.sys.mjs, line 119: unreachable code
after return statement
[pid=715283] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=715283] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-0lsePR
-juggler-pipe -silent
  - <launched> pid=715283
  - [pid=715283][err] [715283] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=715283][err] *** You are running in headless mode.
  - [pid=715283][err] JavaScript warning:
resource://services-settings/Utils.sys.mjs, line 119: unreachable code
after return statement
  - [pid=715283] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=715283] starting temporary directories cleanup
  - [pid=715283] <gracefully close start>
  - [pid=715283] <kill>
  - [pid=715283] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=715283] finished temporary directories cleanup
  - [pid=715283] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
2026-07-13 18:37:25  [WARNING]  Firefox launch attempt 3/3 failed:
Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-0lsePR
-juggler-pipe -silent
<launched> pid=715283
[pid=715283][err] [715283] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=715283][err] *** You are running in headless mode.
[pid=715283][err] JavaScript warning:
resource://services-settings/Utils.sys.mjs, line 119: unreachable code
after return statement
[pid=715283] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=715283] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-0lsePR
-juggler-pipe -silent
  - <launched> pid=715283
  - [pid=715283][err] [715283] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=715283][err] *** You are running in headless mode.
  - [pid=715283][err] JavaScript warning:
resource://services-settings/Utils.sys.mjs, line 119: unreachable code
after return statement
  - [pid=715283] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=715283] starting temporary directories cleanup
  - [pid=715283] <gracefully close start>
  - [pid=715283] <kill>
  - [pid=715283] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=715283] finished temporary directories cleanup
  - [pid=715283] <gracefully close end>

2026-07-13 18:37:25  [ERROR]  [coastal_ca_gov] run_company_task
exception: [unknown] BrowserType.launch: Failed to launch the browser
process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-lZQqRg
-juggler-pipe -silent
<launched> pid=715178
[pid=715178][err] [715178] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=715178][err] *** You are running in headless mode.
[pid=715178][out] [GFX1-]: FireTestProcess failed: Failed to spawn
child process “/app/.browsers/firefox-1532/firefox/glxtest” (Resource
temporarily unavailable)
[pid=715178][out]
[pid=715178] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=715178] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-lZQqRg
-juggler-pipe -silent
  - <launched> pid=715178
  - [pid=715178][err] [715178] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=715178][err] *** You are running in headless mode.
  - [pid=715178][out] [GFX1-]: FireTestProcess failed: Failed to spawn
child process “/app/.browsers/firefox-1532/firefox/glxtest” (Resource
temporarily unavailable)
  - [pid=715178][out]
  - [pid=715178] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=715178] starting temporary directories cleanup
  - [pid=715178] <gracefully close start>
  - [pid=715178] <kill>
  - [pid=715178] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=715178] finished temporary directories cleanup
  - [pid=715178] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
Traceback (most recent call last):
  File "/app/src/external/playwright.py", line 111, in _launch_browser
    browser = await pw.firefox.launch(
              ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/async_api/_generated.py",
line 16546, in launch
    await self._impl_obj.launch(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_browser_type.py",
line 97, in launch
    await self._channel.send(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py",
line 69, in send
    return await self._connection.wrap_api_call(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py",
line 563, in wrap_api_call
    raise rewrite_error(error, f"{parsed_st['apiName']}: {error}") from None
playwright._impl._errors.Error: BrowserType.launch: Failed to launch
the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-lZQqRg
-juggler-pipe -silent
<launched> pid=715178
[pid=715178][err] [715178] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=715178][err] *** You are running in headless mode.
[pid=715178][out] [GFX1-]: FireTestProcess failed: Failed to spawn
child process “/app/.browsers/firefox-1532/firefox/glxtest” (Resource
temporarily unavailable)
[pid=715178][out]
[pid=715178] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=715178] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-lZQqRg
-juggler-pipe -silent
  - <launched> pid=715178
  - [pid=715178][err] [715178] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=715178][err] *** You are running in headless mode.
  - [pid=715178][out] [GFX1-]: FireTestProcess failed: Failed to spawn
child process “/app/.browsers/firefox-1532/firefox/glxtest” (Resource
temporarily unavailable)
  - [pid=715178][out]
  - [pid=715178] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=715178] starting temporary directories cleanup
  - [pid=715178] <gracefully close start>
  - [pid=715178] <kill>
  - [pid=715178] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=715178] finished temporary directories cleanup
  - [pid=715178] <gracefully close end>


The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/app/src/core/roster.py", line 1045, in run_company_task
    result = await run_parse_job_list_dispatch(entity, batch_id, ctx, debug)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/roster.py", line 1294, in run_parse_job_list_dispatch
    async with create_browser_context() as browser_context:
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.nix-profile/lib/python3.12/contextlib.py", line 210, in
__aenter__
    return await anext(self.gen)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 591, in create_browser_context
    browser = await _launch_browser(pw, headless=headless)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 136, in _launch_browser
    raise PlaywrightInfraError(fc, detail) from last_err
src.external.playwright.PlaywrightInfraError: [unknown]
BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-lZQqRg
-juggler-pipe -silent
<launched> pid=715178
[pid=715178][err] [715178] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=715178][err] *** You are running in headless mode.
[pid=715178][out] [GFX1-]: FireTestProcess failed: Failed to spawn
child process “/app/.browsers/firefox-1532/firefox/glxtest” (Resource
temporarily unavailable)
[pid=715178][out]
[pid=715178] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=715178] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-lZQqRg
-juggler-pipe -silent
  - <launched> pid=715178
  - [pid=715178][err] [715178] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=715178][err] *** You are running in headless mode.
  - [pid=715178][out] [GFX1-]: FireTestProcess failed: Failed to spawn
child process “/app/.browsers/firefox-1532/firefox/glxtest” (Resource
temporarily unavailable)
  - [pid=715178][out]
  - [pid=715178] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=715178] starting temporary directories cleanup
  - [pid=715178] <gracefully close start>
  - [pid=715178] <kill>
  - [pid=715178] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=715178] finished temporary directories cleanup
  - [pid=715178] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
2026-07-13 18:37:25  [WARNING]  Firefox launch attempt 3/3 failed:
Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-lZQqRg
-juggler-pipe -silent
<launched> pid=715178
[pid=715178][err] [715178] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=715178][err] *** You are running in headless mode.
[pid=715178][out] [GFX1-]: FireTestProcess failed: Failed to spawn
child process “/app/.browsers/firefox-1532/firefox/glxtest” (Resource
temporarily unavailable)
[pid=715178][out]
[pid=715178] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=715178] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-lZQqRg
-juggler-pipe -silent
  - <launched> pid=715178
  - [pid=715178][err] [715178] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=715178][err] *** You are running in headless mode.
  - [pid=715178][out] [GFX1-]: FireTestProcess failed: Failed to spawn
child process “/app/.browsers/firefox-1532/firefox/glxtest” (Resource
temporarily unavailable)
  - [pid=715178][out]
  - [pid=715178] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=715178] starting temporary directories cleanup
  - [pid=715178] <gracefully close start>
  - [pid=715178] <kill>
  - [pid=715178] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=715178] finished temporary directories cleanup
  - [pid=715178] <gracefully close end>

2026-07-13 18:37:25  [ERROR]  [henrycountyga_gov] run_company_task
exception: [unknown] BrowserType.launch: Failed to launch the browser
process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-zTgydC
-juggler-pipe -silent
<launched> pid=715176
[pid=715176][err] [715176] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=715176][err] *** You are running in headless mode.
[pid=715176] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=715176] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-zTgydC
-juggler-pipe -silent
  - <launched> pid=715176
  - [pid=715176][err] [715176] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=715176][err] *** You are running in headless mode.
  - [pid=715176] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=715176] starting temporary directories cleanup
  - [pid=715176] <gracefully close start>
  - [pid=715176] <kill>
  - [pid=715176] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=715176] finished temporary directories cleanup
  - [pid=715176] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
Traceback (most recent call last):
  File "/app/src/external/playwright.py", line 111, in _launch_browser
    browser = await pw.firefox.launch(
              ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/async_api/_generated.py",
line 16546, in launch
    await self._impl_obj.launch(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_browser_type.py",
line 97, in launch
    await self._channel.send(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py",
line 69, in send
    return await self._connection.wrap_api_call(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py",
line 563, in wrap_api_call
    raise rewrite_error(error, f"{parsed_st['apiName']}: {error}") from None
playwright._impl._errors.Error: BrowserType.launch: Failed to launch
the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-zTgydC
-juggler-pipe -silent
<launched> pid=715176
[pid=715176][err] [715176] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=715176][err] *** You are running in headless mode.
[pid=715176] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=715176] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-zTgydC
-juggler-pipe -silent
  - <launched> pid=715176
  - [pid=715176][err] [715176] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=715176][err] *** You are running in headless mode.
  - [pid=715176] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=715176] starting temporary directories cleanup
  - [pid=715176] <gracefully close start>
  - [pid=715176] <kill>
  - [pid=715176] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=715176] finished temporary directories cleanup
  - [pid=715176] <gracefully close end>


The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/app/src/core/roster.py", line 1045, in run_company_task
    result = await run_parse_job_list_dispatch(entity, batch_id, ctx, debug)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/roster.py", line 1294, in run_parse_job_list_dispatch
    async with create_browser_context() as browser_context:
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.nix-profile/lib/python3.12/contextlib.py", line 210, in
__aenter__
    return await anext(self.gen)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 591, in create_browser_context
    browser = await _launch_browser(pw, headless=headless)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 136, in _launch_browser
    raise PlaywrightInfraError(fc, detail) from last_err
src.external.playwright.PlaywrightInfraError: [unknown]
BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-zTgydC
-juggler-pipe -silent
<launched> pid=715176
[pid=715176][err] [715176] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=715176][err] *** You are running in headless mode.
[pid=715176] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=715176] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-zTgydC
-juggler-pipe -silent
  - <launched> pid=715176
  - [pid=715176][err] [715176] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=715176][err] *** You are running in headless mode.
  - [pid=715176] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=715176] starting temporary directories cleanup
  - [pid=715176] <gracefully close start>
  - [pid=715176] <kill>
  - [pid=715176] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=715176] finished temporary directories cleanup
  - [pid=715176] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
2026-07-13 18:37:25  [WARNING]  Firefox launch attempt 3/3 failed:
Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-zTgydC
-juggler-pipe -silent
<launched> pid=715176
[pid=715176][err] [715176] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=715176][err] *** You are running in headless mode.
[pid=715176] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=715176] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-zTgydC
-juggler-pipe -silent
  - <launched> pid=715176
  - [pid=715176][err] [715176] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=715176][err] *** You are running in headless mode.
  - [pid=715176] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=715176] starting temporary directories cleanup
  - [pid=715176] <gracefully close start>
  - [pid=715176] <kill>
  - [pid=715176] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=715176] finished temporary directories cleanup
  - [pid=715176] <gracefully close end>

2026-07-13 18:37:25  [INFO]  [zymr_com] company state
JOBLIST_IDENTIFIED -> JOBLIST_IDENTIFIED_RETRY
(batch_id=parse_job_list-a904618e-b284-4f1b-b868-d7f4dffdc870)
2026-07-13 18:37:25  [WARNING]  Firefox launch attempt 2/3 failed:
Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-V7OmHu
-juggler-pipe -silent
<launched> pid=714725
[pid=714725][err] [714725] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=714725][err] *** You are running in headless mode.
[pid=714725] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=714725] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-V7OmHu
-juggler-pipe -silent
  - <launched> pid=714725
  - [pid=714725][err] [714725] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=714725][err] *** You are running in headless mode.
  - [pid=714725] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=714725] starting temporary directories cleanup
  - [pid=714725] <gracefully close start>
  - [pid=714725] <kill>
  - [pid=714725] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=714725] finished temporary directories cleanup
  - [pid=714725] <gracefully close end>

2026-07-13 18:37:25  [WARNING]  Firefox launch attempt 2/3 failed:
Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-MzpbD0
-juggler-pipe -silent
<launched> pid=714726
[pid=714726][err] [714726] Sandbox: CanCreateUserNamespace() clone()
failure: EACCES
[pid=714726][err] *** You are running in headless mode.
[pid=714726] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=714726] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-MzpbD0
-juggler-pipe -silent
  - <launched> pid=714726
  - [pid=714726][err] [714726] Sandbox: CanCreateUserNamespace()
clone() failure: EACCES
  - [pid=714726][err] *** You are running in headless mode.
  - [pid=714726] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=714726] starting temporary directories cleanup
  - [pid=714726] <gracefully close start>
  - [pid=714726] <kill>
  - [pid=714726] <skipped force kill spawnedProcess.killed=false
processClosed=true>
  - [pid=714726] finished temporary directories cleanup
  - [pid=714726] <gracefully close end>

2026-07-13 18:37:25  [INFO]  [osano_com] company state
JOBLIST_IDENTIFIED -> JOBLIST_IDENTIFIED_RETRY
(batch_id=parse_job_list-a904618e-b284-4f1b-b868-d7f4dffdc870)
2026-07-13 18:37:25  [INFO]  [discover_pbc_gov] company state
JOBLIST_IDENTIFIED -> JOBLIST_IDENTIFIED_RETRY
(batch_id=parse_job_list-a904618e-b284-4f1b-b868-d7f4dffdc870)
2026-07-13 18:40:13  [INFO]   | response_type='PARSE_DISPATCH_OK' ->
state='WATCH' cull='culled'
2026-07-13 18:40:13  [INFO]  [govsense_com] company state
JOBLIST_IDENTIFIED -> WATCH
(batch_id=parse_job_list-a904618e-b284-4f1b-b868-d7f4dffdc870)
2026-07-13 18:40:13  [INFO]  do_task(parse_job_list) completed
successfully batch_id=parse_job_list-a904618e-b284-4f1b-b868-d7f4dffdc870
index=govsense_com
2026-07-13 18:40:13  [INFO]  LLM deepseek task=parse_job_list 2.0s
stop=end_turn tokens in=2579 out=105
2026-07-13 18:40:13  [INFO]  run_next chain entry: task=parse_job_list
batch_id=parse_job_list-a904618e-b284-4f1b-b868-d7f4dffdc870
2026-07-13 18:40:13  [INFO]   | titles=2 pre_cull_chars=24400
post_cull_chars=9560 containers=1 cull_outcome='culled'
2026-07-13 18:40:13  [INFO]   | ready=True visible_chars=8189
listing_hits=0 wait_ms=1091 load_all_jobs_ran=False
2026-07-13 18:40:13  [INFO]  roster._scrape_list_page_dom_for_parse
index 1/1 https://govsense.com/careers -> ready
2026-07-13 18:40:13  [ERROR]  [techforgov_ai] run_company_task
exception: [unknown] BrowserType.launch: Failed to launch: Error:
spawn /app/.browsers/firefox-1532/firefox/firefox EAGAIN
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-ZojqlC
-juggler-pipe -silent
  - [pid=N/A] starting temporary directories cleanup
  - [pid=N/A] finished temporary directories cleanup

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
Traceback (most recent call last):
  File "/app/src/external/playwright.py", line 111, in _launch_browser
    browser = await pw.firefox.launch(
              ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/async_api/_generated.py",
line 16546, in launch
    await self._impl_obj.launch(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_browser_type.py",
line 97, in launch
    await self._channel.send(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py",
line 69, in send
    return await self._connection.wrap_api_call(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py",
line 563, in wrap_api_call
    raise rewrite_error(error, f"{parsed_st['apiName']}: {error}") from None
playwright._impl._errors.Error: BrowserType.launch: Failed to launch:
Error: spawn /app/.browsers/firefox-1532/firefox/firefox EAGAIN
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-ZojqlC
-juggler-pipe -silent
  - [pid=N/A] starting temporary directories cleanup
  - [pid=N/A] finished temporary directories cleanup


The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/app/src/core/roster.py", line 1045, in run_company_task
    result = await run_parse_job_list_dispatch(entity, batch_id, ctx, debug)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/roster.py", line 1294, in run_parse_job_list_dispatch
    async with create_browser_context() as browser_context:
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.nix-profile/lib/python3.12/contextlib.py", line 210, in
__aenter__
    return await anext(self.gen)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 591, in create_browser_context
    browser = await _launch_browser(pw, headless=headless)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 136, in _launch_browser
    raise PlaywrightInfraError(fc, detail) from last_err
src.external.playwright.PlaywrightInfraError: [unknown]
BrowserType.launch: Failed to launch: Error: spawn
/app/.browsers/firefox-1532/firefox/firefox EAGAIN
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-ZojqlC
-juggler-pipe -silent
  - [pid=N/A] starting temporary directories cleanup
  - [pid=N/A] finished temporary directories cleanup

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
2026-07-13 18:40:13  [INFO]  [darroweverett_com] company state
JOBLIST_IDENTIFIED -> JOBLIST_IDENTIFIED_RETRY
(batch_id=parse_job_list-a904618e-b284-4f1b-b868-d7f4dffdc870)
2026-07-13 18:40:13  [INFO]   | titles=3 pre_cull_chars=41483
post_cull_chars=0 containers=1 cull_outcome='cull_miss'
2026-07-13 18:40:13  [INFO]  [careers_evercommerce_com] company state
JOBLIST_IDENTIFIED -> JOBLIST_IDENTIFIED_RETRY
(batch_id=parse_job_list-a904618e-b284-4f1b-b868-d7f4dffdc870)
2026-07-13 18:40:13  [WARNING]  Firefox launch attempt 3/3 failed:
Error: BrowserType.launch: Failed to launch: Error: spawn
/app/.browsers/firefox-1532/firefox/firefox EAGAIN
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote
-headless -profile /tmp/playwright_firefoxdev_profile-ZojqlC
-juggler-pipe -silent
  - [pid=N/A] starting temporary directories cleanup
  - [pid=N/A] finished temporary directories cleanup

2026-07-13 18:40:13  [INFO]   | ready=True visible_chars=3698
listing_hits=0 wait_ms=1102 load_all_jobs_ran=False
2026-07-13 18:40:13  [INFO]  roster._scrape_list_page_dom_for_parse
index 1/1 https://darroweverett.com/careers -> ready
2026-07-13 19:37:06  [ERROR]
[parse_job_list/parse_job_list-a904618e-b284-4f1b-b868-d7f4dffdc870]
batch finished INTERRUPTED — dispatch timeout after 3600s |
processed=0 passed=0 failed=0 errors=1
2026-07-13 19:37:06  [ERROR]
[parse_job_list/parse_job_list-a904618e-b284-4f1b-b868-d7f4dffdc870]
killed after 3600s timeout
```

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._

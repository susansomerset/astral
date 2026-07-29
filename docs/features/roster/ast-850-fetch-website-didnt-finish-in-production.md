# AST-850 — fetch_website didn't finish in production

<!-- linear-archive: AST-850 archived 2026-07-29 -->

## Linear archive (AST-850)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-850/fetch-website-didnt-finish-in-production  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Production **fetch_website** roster dispatch is stalling the company pipeline: a batch that started with 184 **WEBSITE_FOUND** companies ran for days, processed only 40 entities, and had to be killed manually. Logs show repeated headless-browser launch failures, mid-batch browser crashes, and an **INTERRUPTED** finish — leaving most companies unprocessed and blocking downstream **HOMEPAGE_READY** / prefilter work. This epic restores trustworthy batch completion on the live Railway host so Susan can run **fetch_website** without babysitting or killing stuck jobs.

## Functional scope

* **fetch_website** batches on production complete all claimed companies in a single dispatch run without requiring manual admin kill, under normal Railway load.
* Browser infrastructure failures (launch timeout, crash, lost browser context) are isolated so one failure does not stall the entire batch for hours or days; the batch continues or exits cleanly with a clear terminal outcome.
* When a company cannot be read because of browser infra (not because the site is genuinely unreadable), the outcome is distinguishable in logs and company state from a normal **CANNOT_READ_WEBSITE** site failure.
* Companies left unprocessed after an interrupted or failed batch are not stuck in a claimed or ambiguous state — they remain eligible for a subsequent **fetch_website** run.
* Production logs make batch progress, stall points, and browser failure modes obvious without reading thousands of repetitive error lines (including AST-538 debug contract when **debug=True** on a batch run).
* After fix, Susan can re-run **fetch_website** on production and the backlog of **WEBSITE_FOUND** companies drains without another multi-day hang.

## Boundaries

* Does **not** fix individual company websites that are genuinely unreachable or unreadable (**CANNOT_READ_WEBSITE** for real site failures stays valid).
* Does **not** change **prefilter**, **fetch_job_pages**, **gaze**, or other roster dispatches unless Susan explicitly combines scope (see open questions).
* Does **not** change dispatch scheduling UI, batch size defaults, or **HOMEPAGE_READY** / **WEBSITE_FOUND** state machine semantics beyond what is required for clean interruption recovery.
* Does **not** cover local-only dev browser setup; target environment is production Railway.
* Must not regress the existing successful homepage-scrape path (**HOMEPAGE_READY** transitions, nav link capture).

## Acceptance criteria

1. On production Railway, Susan triggers **fetch_website** on a queue of **WEBSITE_FOUND** companies (including the ~144 left from the interrupted batch) and the batch reaches a normal terminal finish (**completed** or **INTERRUPTED** only when Susan explicitly cancels) without multi-day stall.
2. Batch summary counts (**processed**, **passed**, **failed**, **errors**) match observable company state transitions; no companies remain indefinitely claimed or mid-batch invisible to the next dispatch.
3. When headless browser launch or context loss occurs, logs identify the failure class and affected company within one batch item — not only a wall of identical launch errors — and the batch does not hang silently afterward.
4. With **debug=True** on a production test batch, Susan sees per-company index headers and substantive detail lines per AST-538 (what was attempted, what was recorded, pass/fail outcome) for **fetch_website** steps.
5. Susan does not need to admin-kill **fetch_website** to unblock the roster pipeline after deploy.

## Dependencies and blockers

* **AST-701** (fetch_website gazer batch and **HOMEPAGE_READY** state) — shipped; baseline behavior this epic hardens.
* **AST-317** (Playwright resilience) — Done; may not cover current Railway Firefox failure modes seen in logs.
* [AST-823](https://linear.app/astralcareermatch/issue/AST-823/homepage-ready-prefilter-consult-routing-get-prefilter-company-to-work) (prefilter routing on **HOMEPAGE_READY**) — downstream consumer; not a blocker but motivates draining **WEBSITE_FOUND** backlog.
* [AST-851](https://linear.app/astralcareermatch/issue/AST-851/the-gaze-didnt-finish-in-production) (gaze didn't finish in production) — sibling Discussion ticket with overlapping browser failure symptoms; scope decision in open questions.
* none otherwise for starting investigation.

## Open questions

1. Should this epic cover **fetch_website** only, or should [AST-851](https://linear.app/astralcareermatch/issue/AST-851/the-gaze-didnt-finish-in-production) (gaze) browser-on-Railway failures be one shared infrastructure parent with two children?
   1. This one covers fetch_website.  remind me to retest for 851 when this fix is in place to make sure they're distinct issues.
2. For companies from batch `fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743` (40/184 processed, admin-killed 2026-07-10): is automatic re-eligibility on deploy sufficient, or does Susan want an explicit one-time recovery pass for stuck rows?
   1. automatically re-eligible, please.
3. When browser infra fails for a specific company, should the company land in **WEBSITE_FOUND_RETRY** (retry later) vs **CANNOT_READ_WEBSITE** (terminal for site read failure) — or is the current mixed behavior acceptable once batches no longer hang?
   1. Retry, because if it persists, it will eventually go to cannot read website.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-850 (parent) | ftr/AST-850-fetch-website-didnt-finish-in-production |
| AST-853 | sub/AST-850/AST-853-production-playwright-browser-stability |
| AST-854 | sub/AST-850/AST-854-fetch-website-batch-completion-and-infra-failure-handling |

**Epic worktree:** `astral-AST-850/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | 097f7a7d-1d57-4520-a0ab-5d8afba4a367 |
| Betty | qa | 3d4d2e65-3ebc-4125-b621-b216dcc98c81 |
| Radia | review | 8afed272-0858-4b1b-b351-b2f5037568a3 |

---

## Original brief

```
[2026-07-10 02:05:38] WARNING dispatch.scheduler: [fetch_website/fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743] KILLED by admin — thread cleared from memory
[2026-07-10 02:05:38] ERROR src.core.dispatcher: [fetch_website/fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743] batch finished INTERRUPTED — dispatch cancelled by admin | processed=40 passed=11 failed=9 errors=21
[2026-07-09 00:10:21] INFO src.core.roster: [community_hubspot_com] company state WEBSITE_FOUND -> CANNOT_READ_WEBSITE (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-09 00:10:21] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 dowjones_com -> failed — BrowserContext.new_page: Target page, context or browser has been closed
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-cgYCFH -juggler-pipe -silent
<launched> pid=16047
[pid=16047][err] [16047] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=16047][err] *** You are running in headless mode.
[pid=16047][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=16047][out] 
[pid=16047][out] Juggler listening to the pipe
[pid=16047][err] Exiting due to channel error.
[pid=16047][err] Exiting due to channel error. -> CANNOT_READ_WEBSITE
[2026-07-09 00:10:21] INFO src.core.gazer:  | company_website='https://www.dowjones.com'
[2026-07-09 00:10:21] INFO src.core.roster: [dowjones_com] company state WEBSITE_FOUND -> CANNOT_READ_WEBSITE (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-09 00:10:21] INFO src.core.gazer:  | summary passed=0 failed=1 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-09 00:10:21] INFO src.core.gazer:  | summary passed=0 failed=1 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-09 00:10:21] INFO src.core.roster: [careers_nsbe_org] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-09 00:10:21] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 careers_nsbe_org -> passed -> HOMEPAGE_READY (3758 chars redirect=yes nav=220 links)
[2026-07-09 00:10:21] INFO src.core.gazer:  | company_website='https://www.dnv.com' canonical='https://www.dnv.com/' homepage_chars=3758 nav_links=220
[2026-07-09 00:10:21] INFO src.core.gazer:  | summary passed=1 failed=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-09 00:10:21] INFO src.core.roster: [careers_spglobal_com] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-09 00:10:21] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 careers_spglobal_com -> passed -> HOMEPAGE_READY (35051 chars redirect=yes nav=200 links)
[2026-07-09 00:10:21] INFO src.core.gazer:  | company_website='https://www.spglobal.com' canonical='https://www.spglobal.com/en' homepage_chars=35051 nav_links=200
[2026-07-09 00:10:21] INFO src.core.gazer:  | summary passed=1 failed=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-09 00:10:21] ERROR src.external.playwright: Firefox launch failed: TimeoutError: BrowserType.launch: Timeout 180000ms exceeded.
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-fJaP87 -juggler-pipe -silent
  - <launched> pid=13118
  - [pid=13118][err] [13118] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=13118][err] *** You are running in headless mode.
  - [pid=13118][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement

[2026-07-09 00:10:21] WARNING src.external.playwright: check_connectivity failed: Could not launch Firefox.
  Error: BrowserType.launch: Timeout 180000ms exceeded.
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-fJaP87 -juggler-pipe -silent
  - <launched> pid=13118
  - [pid=13118][err] [13118] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=13118][err] *** You are running in headless mode.
  - [pid=13118][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
[2026-07-09 00:10:21] ERROR src.external.playwright: Firefox launch failed: TimeoutError: BrowserType.launch: Timeout 180000ms exceeded.
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-R6JfLf -juggler-pipe -silent
  - <launched> pid=14665
  - [pid=14665][err] [14665] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=14665][err] *** You are running in headless mode.
  - [pid=14665][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement

[2026-07-03 03:27:11] WARNING src.external.playwright: check_connectivity failed: Could not launch Firefox.
  Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-E6gULK -juggler-pipe -silent
<launched> pid=12978
[pid=12978][err] [12978] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=12978][err] *** You are running in headless mode.
[pid=12978][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=12978][out] Crash Annotation GraphicsCriticalError: |[0][GFX1-]: Compositor thread not started (true) (t=1.51393) [GFX1-]: Compositor thread not started (true)
[pid=12978] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=12978] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-E6gULK -juggler-pipe -silent
  - <launched> pid=12978
  - [pid=12978][err] [12978] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=12978][err] *** You are running in headless mode.
  - [pid=12978][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=12978][out] Crash Annotation GraphicsCriticalError: |[0][GFX1-]: Compositor thread not started (true) (t=1.51393) [GFX1-]: Compositor thread not started (true)
  - [pid=12978] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=12978] starting temporary directories cleanup
  - [pid=12978] <gracefully close start>
  - [pid=12978] <kill>
  - [pid=12978] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=12978] finished temporary directories cleanup
  - [pid=12978] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
[2026-07-03 03:27:11] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:27:11] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:27:11] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:27:11] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:27:11] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:27:11] ERROR src.external.playwright: Firefox launch failed: Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-andbEg -juggler-pipe -silent
<launched> pid=14947
[pid=14947][err] [14947] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=14947][err] *** You are running in headless mode.
[pid=14947] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=14947] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-andbEg -juggler-pipe -silent
  - <launched> pid=14947
  - [pid=14947][err] [14947] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=14947][err] *** You are running in headless mode.
  - [pid=14947] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=14947] starting temporary directories cleanup
  - [pid=14947] <gracefully close start>
  - [pid=14947] <kill>
  - [pid=14947] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=14947] finished temporary directories cleanup
  - [pid=14947] <gracefully close end>

[2026-07-03 03:27:11] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:27:11] WARNING src.external.playwright: check_connectivity failed: Page.goto: Page crashed
Call log:
  - navigating to "https://www.google.com/", waiting until "commit"

[2026-07-03 03:27:11] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:27:11] ERROR src.external.playwright: Firefox launch failed: Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-HE8t5o -juggler-pipe -silent
<launched> pid=13115
[pid=13115][err] [13115] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=13115][err] *** You are running in headless mode.
[pid=13115] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=13115] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-HE8t5o -juggler-pipe -silent
  - <launched> pid=13115
  - [pid=13115][err] [13115] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=13115][err] *** You are running in headless mode.
  - [pid=13115] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=13115] starting temporary directories cleanup
  - [pid=13115] <gracefully close start>
  - [pid=13115] <kill>
  - [pid=13115] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=13115] finished temporary directories cleanup
  - [pid=13115] <gracefully close end>

[2026-07-03 03:27:11] WARNING src.external.playwright: check_connectivity failed: Could not launch Firefox.
  Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-HE8t5o -juggler-pipe -silent
<launched> pid=13115
[pid=13115][err] [13115] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=13115][err] *** You are running in headless mode.
[pid=13115] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=13115] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-HE8t5o -juggler-pipe -silent
  - <launched> pid=13115
  - [pid=13115][err] [13115] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=13115][err] *** You are running in headless mode.
  - [pid=13115] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=13115] starting temporary directories cleanup
  - [pid=13115] <gracefully close start>
  - [pid=13115] <kill>
  - [pid=13115] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=13115] finished temporary directories cleanup
  - [pid=13115] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
[2026-07-03 03:27:11] ERROR src.external.playwright: Firefox launch failed: Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-Ymtbwm -juggler-pipe -silent
<launched> pid=15611
[pid=15611][err] [15611] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=15611][err] *** You are running in headless mode.
[pid=15611] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=15611] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-Ymtbwm -juggler-pipe -silent
  - <launched> pid=15611
  - [pid=15611][err] [15611] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=15611][err] *** You are running in headless mode.
  - [pid=15611] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=15611] starting temporary directories cleanup
  - [pid=15611] <gracefully close start>
  - [pid=15611] <kill>
  - [pid=15611] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=15611] finished temporary directories cleanup
  - [pid=15611] <gracefully close end>

[2026-07-03 03:27:11] ERROR src.external.playwright: Firefox launch failed: Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-HhLkxb -juggler-pipe -silent
<launched> pid=13081
[pid=13081][err] [13081] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=13081][err] *** You are running in headless mode.
[pid=13081][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=13081] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=13081] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-HhLkxb -juggler-pipe -silent
  - <launched> pid=13081
  - [pid=13081][err] [13081] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=13081][err] *** You are running in headless mode.
  - [pid=13081][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=13081] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=13081] starting temporary directories cleanup
  - [pid=13081] <gracefully close start>
  - [pid=13081] <kill>
  - [pid=13081] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=13081] finished temporary directories cleanup
  - [pid=13081] <gracefully close end>

[2026-07-03 03:27:11] WARNING src.external.playwright: check_connectivity failed: Could not launch Firefox.
  Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-HhLkxb -juggler-pipe -silent
<launched> pid=13081
[pid=13081][err] [13081] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=13081][err] *** You are running in headless mode.
[pid=13081][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=13081] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=13081] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-HhLkxb -juggler-pipe -silent
  - <launched> pid=13081
  - [pid=13081][err] [13081] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=13081][err] *** You are running in headless mode.
  - [pid=13081][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=13081] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=13081] starting temporary directories cleanup
  - [pid=13081] <gracefully close start>
  - [pid=13081] <kill>
  - [pid=13081] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=13081] finished temporary directories cleanup
  - [pid=13081] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
[2026-07-03 03:27:11] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:27:11] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 aureliusgroup_com -> failed — BrowserContext.new_page: Cannot read properties of undefined (reading '_page') -> CANNOT_READ_WEBSITE
[2026-07-03 03:27:11] INFO src.core.gazer:  | company_website='https://aurelius-group.com'
[2026-07-03 03:27:11] INFO src.core.roster: [aureliusgroup_com] company state WEBSITE_FOUND -> CANNOT_READ_WEBSITE (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:27:11] ERROR src.external.playwright: Firefox launch failed: Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-WWLofv -juggler-pipe -silent
<launched> pid=13066
[pid=13066][err] [13066] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=13066][err] *** You are running in headless mode.
[pid=13066][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=13066] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=13066] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-WWLofv -juggler-pipe -silent
  - <launched> pid=13066
  - [pid=13066][err] [13066] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=13066][err] *** You are running in headless mode.
  - [pid=13066][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=13066] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=13066] starting temporary directories cleanup
  - [pid=13066] <gracefully close start>
  - [pid=13066] <kill>
  - [pid=13066] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=13066] finished temporary directories cleanup
  - [pid=13066] <gracefully close end>

[2026-07-03 03:27:11] WARNING src.external.playwright: check_connectivity failed: Could not launch Firefox.
  Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-WWLofv -juggler-pipe -silent
<launched> pid=13066
[pid=13066][err] [13066] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=13066][err] *** You are running in headless mode.
[pid=13066][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=13066] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=13066] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-WWLofv -juggler-pipe -silent
  - <launched> pid=13066
  - [pid=13066][err] [13066] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=13066][err] *** You are running in headless mode.
  - [pid=13066][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=13066] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=13066] starting temporary directories cleanup
  - [pid=13066] <gracefully close start>
  - [pid=13066] <kill>
  - [pid=13066] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=13066] finished temporary directories cleanup
  - [pid=13066] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
[2026-07-03 03:27:11] ERROR src.external.playwright: Firefox launch failed: Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-kXB5aY -juggler-pipe -silent
<launched> pid=13112
[pid=13112][err] [13112] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=13112][err] *** You are running in headless mode.
[pid=13112][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=13112] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=13112] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-kXB5aY -juggler-pipe -silent
  - <launched> pid=13112
  - [pid=13112][err] [13112] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=13112][err] *** You are running in headless mode.
  - [pid=13112][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=13112] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=13112] starting temporary directories cleanup
  - [pid=13112] <gracefully close start>
  - [pid=13112] <kill>
  - [pid=13112] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=13112] finished temporary directories cleanup
  - [pid=13112] <gracefully close end>

[2026-07-03 03:27:11] WARNING src.external.playwright: check_connectivity failed: Could not launch Firefox.
  Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-kXB5aY -juggler-pipe -silent
<launched> pid=13112
[pid=13112][err] [13112] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=13112][err] *** You are running in headless mode.
[pid=13112][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=13112] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=13112] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-kXB5aY -juggler-pipe -silent
  - <launched> pid=13112
  - [pid=13112][err] [13112] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=13112][err] *** You are running in headless mode.
  - [pid=13112][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=13112] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=13112] starting temporary directories cleanup
  - [pid=13112] <gracefully close start>
  - [pid=13112] <kill>
  - [pid=13112] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=13112] finished temporary directories cleanup
  - [pid=13112] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
[2026-07-03 03:27:11] WARNING src.external.playwright: check_connectivity failed: BrowserContext.new_page: Target page, context or browser has been closed
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-7RdPEM -juggler-pipe -silent
<launched> pid=13110
[pid=13110][err] [13110] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=13110][err] *** You are running in headless mode.
[pid=13110][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=13110][out] 
[pid=13110][out] Juggler listening to the pipe
[pid=13110][out] Crash Annotation GraphicsCriticalError: |[0][GFX1-]: wr_window_new: Thread(Os { code: 11, kind: WouldBlock, message: "Resource temporarily unavailable" }) (t=4.49417) [GFX1-]: wr_window_new: Thread(Os { code: 11, kind: WouldBlock, message: "Resource temporarily unavailable" })
[pid=13110][out] Crash Annotation GraphicsCriticalError: |[0][GFX1-]: wr_window_new: Thread(Os { code: 11, kind: WouldBlock, message: "Resource temporarily unavailable" }) (t=4.49417) |[1][GFX1-]: Failed to connect WebRenderBridgeChild. isParent=true (t=4.49417) [GFX1-]: Failed to connect WebRenderBridgeChild. isParent=true
[pid=13110][out] Crash Annotation GraphicsCriticalError: |[0][GFX1-]: wr_window_new: Thread(Os { code: 11, kind: WouldBlock, message: "Resource temporarily unavailable" }) (t=4.49417) |[1][GFX1-]: Failed to connect WebRenderBridgeChild. isParent=true (t=4.49417) |[2][GFX1-]: Fallback remains SW-WR (t=4.49417) [GFX1-]: Fallback remains SW-WR
[pid=13110][out] 
[pid=13110][out]         ERROR: ERROR: cannot find session with id "b7313b5b-8ec7-42c0-a5a2-d0e5f8e10231" _dispatch@chrome://juggler/content/protocol/Dispatcher.js:54:15
[pid=13110][out] receiveMessage@chrome://juggler/content/components/Juggler.js:121:20
[pid=13110][out] 
[pid=13110][err] [Parent 13110, IPC I/O Parent] WARNING: process 15791 exited on signal 11: file ./../../../ipc/chromium/src/chrome/common/process_watcher_posix_sigchld.cc:161
[pid=13110][out]       console.error: (new TypeError("can't access property \"maybeCancelContentJSExecution\", this._browser.frameLoader.remoteTab is null", "resource://gre/modules/RemoteWebNavigation.sys.mjs", 41))
[pid=13110][out] console.error: "Error fetching remote settings base url from CDN. Falling back to https://firefox-settings-attachments.cdn.mozilla.net/" (new SyntaxError("XMLHttpRequest.open: '/' is not a valid URL.", (void 0), 126))
[pid=13110][out] console.error: services.settings: 
[pid=13110][out]   Message: EmptyDatabaseError: "main/nimbus-desktop-experiments" has not been synced yet
[pid=13110][out]   Stack:
[pid=13110][out]     EmptyDatabaseError@resource://services-settings/Database.sys.mjs:19:5
[pid=13110][out] list@resource://services-settings/Database.sys.mjs:96:13
[pid=13110][out] 
[2026-07-03 03:27:11] INFO src.core.gazer:  | summary passed=0 failed=1 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:27:11] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:27:11] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 alliancebernstein_com -> failed — Page.goto: Target page, context or browser has been closed
Call log:
  - navigating to "https://www.alliancebernstein.com/", waiting until "load"
 -> CANNOT_READ_WEBSITE
[2026-07-03 03:27:11] INFO src.core.gazer:  | company_website='https://www.alliancebernstein.com'
[2026-07-03 03:27:11] INFO src.core.roster: [alliancebernstein_com] company state WEBSITE_FOUND -> CANNOT_READ_WEBSITE (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:27:11] INFO src.core.gazer:  | summary passed=0 failed=1 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:27:11] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 community_hubspot_com -> failed — Page.goto: Page crashed
Call log:
  - navigating to "https://www.hubspot.com/", waiting until "load"
 -> CANNOT_READ_WEBSITE
[2026-07-03 03:27:11] INFO src.core.gazer:  | company_website='https://www.hubspot.com'
[2026-07-03 03:27:10] INFO src.core.dispatcher: dispatcher._run_unified index 15/20 verdantix_com -> claimed
[2026-07-03 03:27:10] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:27:10] INFO src.core.dispatcher: dispatcher._run_unified index 16/20 lazard_com -> claimed
[2026-07-03 03:27:10] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:27:10] INFO src.core.dispatcher: dispatcher._run_unified index 17/20 erpresearch_com -> claimed
[2026-07-03 03:27:10] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:27:10] INFO src.core.dispatcher: dispatcher._run_unified index 18/20 careers_nsbe_org -> claimed
[2026-07-03 03:27:10] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:27:10] INFO src.core.dispatcher: dispatcher._run_unified index 19/20 ascentium_com -> claimed
[2026-07-03 03:27:10] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:27:10] INFO src.core.dispatcher: dispatcher._run_unified index 20/20 aureliusgroup_com -> claimed
[2026-07-03 03:27:10] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:27:10] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:27:10] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 legendbiotech_com -> failed — Page.goto: SEC_ERROR_UNKNOWN_ISSUER
Call log:
  - navigating to "https://legendbiotech.com/", waiting until "load"
 -> CANNOT_READ_WEBSITE
[2026-07-03 03:27:10] INFO src.core.gazer:  | company_website='https://legendbiotech.com'
[2026-07-03 03:27:10] INFO src.core.roster: [legendbiotech_com] company state WEBSITE_FOUND -> CANNOT_READ_WEBSITE (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:27:10] INFO src.core.gazer:  | summary passed=0 failed=1 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:27:10] ERROR src.external.playwright: Firefox launch failed: Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-E6gULK -juggler-pipe -silent
<launched> pid=12978
[pid=12978][err] [12978] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=12978][err] *** You are running in headless mode.
[pid=12978][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=12978][out] Crash Annotation GraphicsCriticalError: |[0][GFX1-]: Compositor thread not started (true) (t=1.51393) [GFX1-]: Compositor thread not started (true)
[pid=12978] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=12978] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-E6gULK -juggler-pipe -silent
  - <launched> pid=12978
  - [pid=12978][err] [12978] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=12978][err] *** You are running in headless mode.
  - [pid=12978][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=12978][out] Crash Annotation GraphicsCriticalError: |[0][GFX1-]: Compositor thread not started (true) (t=1.51393) [GFX1-]: Compositor thread not started (true)
  - [pid=12978] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=12978] starting temporary directories cleanup
  - [pid=12978] <gracefully close start>
  - [pid=12978] <kill>
  - [pid=12978] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=12978] finished temporary directories cleanup
  - [pid=12978] <gracefully close end>

[2026-07-03 03:26:54] ERROR src.core.dispatcher:   gather slot 8 raised: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 371, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2016, in run_consult_task
    r = await fetch_website_batch(batch_id, entities, debug=debug)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/gazer.py", line 277, in fetch_website_batch
    raise ConnectionError(
ConnectionError: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
[2026-07-03 03:26:54] ERROR src.core.dispatcher:   gather slot 9 raised: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 371, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2016, in run_consult_task
    r = await fetch_website_batch(batch_id, entities, debug=debug)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/gazer.py", line 277, in fetch_website_batch
    raise ConnectionError(
ConnectionError: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
[2026-07-03 03:26:54] ERROR src.core.dispatcher:   gather slot 11 raised: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 371, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2016, in run_consult_task
    r = await fetch_website_batch(batch_id, entities, debug=debug)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/gazer.py", line 277, in fetch_website_batch
    raise ConnectionError(
ConnectionError: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
[2026-07-03 03:26:54] ERROR src.core.dispatcher:   gather slot 12 raised: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 371, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2016, in run_consult_task
    r = await fetch_website_batch(batch_id, entities, debug=debug)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/gazer.py", line 277, in fetch_website_batch
    raise ConnectionError(
ConnectionError: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
[2026-07-03 03:26:54] ERROR src.core.dispatcher:   gather slot 16 raised: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 371, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2016, in run_consult_task
    r = await fetch_website_batch(batch_id, entities, debug=debug)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/gazer.py", line 277, in fetch_website_batch
    raise ConnectionError(
ConnectionError: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
[2026-07-03 03:26:54] ERROR src.core.dispatcher:   gather slot 17 raised: Could not launch Firefox.
  Error: BrowserType.launch: Connection closed while reading from the driver
  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
Traceback (most recent call last):
  File "/app/src/external/playwright.py", line 69, in _launch_browser
    browser = await pw.firefox.launch(
              ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/async_api/_generated.py", line 16546, in launch
    await self._impl_obj.launch(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_browser_type.py", line 97, in launch
    await self._channel.send(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py", line 69, in send
    return await self._connection.wrap_api_call(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py", line 563, in wrap_api_call
    raise rewrite_error(error, f"{parsed_st['apiName']}: {error}") from None
Exception: BrowserType.launch: Connection closed while reading from the driver

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 371, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2016, in run_consult_task
    r = await fetch_website_batch(batch_id, entities, debug=debug)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/gazer.py", line 299, in fetch_website_batch
    async with create_browser_context() as browser_context:
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.nix-profile/lib/python3.12/contextlib.py", line 210, in __aenter__
    return await anext(self.gen)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 411, in create_browser_context
    browser = await _launch_browser(pw, headless=headless)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 77, in _launch_browser
    raise Exception(
Exception: Could not launch Firefox.
  Error: BrowserType.launch: Connection closed while reading from the driver
  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
[2026-07-03 03:26:54] ERROR src.core.dispatcher:   gather slot 19 raised: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 371, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2016, in run_consult_task
    r = await fetch_website_batch(batch_id, entities, debug=debug)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/gazer.py", line 277, in fetch_website_batch
    raise ConnectionError(
ConnectionError: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
[2026-07-03 03:26:54] INFO src.core.dispatcher:  | batch end summary={'total_processed': 20, 'total_passed': 6, 'total_failed': 5, 'total_errors': 9}
[2026-07-03 03:26:54] INFO src.core.dispatcher:  | runner returned summary={'total_processed': 20, 'total_passed': 6, 'total_failed': 5, 'total_errors': 9}
[2026-07-03 03:26:54] INFO src.core.dispatcher:  | iteration 2 summary processed=20 passed=6 failed=5 errors=9 accumulated={'total_processed': 40, 'total_passed': 11, 'total_failed': 9, 'total_errors': 20}
[2026-07-03 03:26:54] INFO src.core.dispatcher: dispatcher._run_dispatch_loop index 3/3 fetch_website -> loop iteration 3 starting
[2026-07-03 03:26:54] INFO src.core.dispatcher:  | available=462 effective_min=1 max_runs=0 draining=False entity_batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743
[2026-07-03 03:26:54] INFO src.core.dispatcher: dispatcher._run_task index 1/1 fetch_website -> running batch
[2026-07-03 03:26:54] INFO src.core.dispatcher:  | batch_size=20 batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 entity_type='company' trigger_state='WEBSITE_FOUND'
[2026-07-03 03:26:54] INFO src.core.dispatcher: dispatcher._run_unified index 1/1 company/WEBSITE_FOUND -> claimed 20 entity/entities
[2026-07-03 03:26:54] INFO src.core.dispatcher:  | task_key=fetch_website batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 batch_call_mode=False dispatch batch_size=20 claim_cap=None claim_states=['WEBSITE_FOUND', 'WEBSITE_FOUND_RETRY']
[2026-07-03 03:26:54] INFO src.core.dispatcher: dispatcher._run_unified index 1/20 legendbiotech_com -> claimed
[2026-07-03 03:26:54] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:26:54] INFO src.core.dispatcher: dispatcher._run_unified index 2/20 analytikjena_us -> claimed
[2026-07-03 03:26:54] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:26:54] INFO src.core.dispatcher: dispatcher._run_unified index 3/20 docs_aws_amazon_com -> claimed
[2026-07-03 03:26:54] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:26:54] INFO src.core.dispatcher: dispatcher._run_unified index 4/20 careers_spglobal_com -> claimed
[2026-07-03 03:26:54] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:26:54] INFO src.core.dispatcher: dispatcher._run_unified index 5/20 community_hubspot_com -> claimed
[2026-07-03 03:26:54] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:26:54] INFO src.core.dispatcher: dispatcher._run_unified index 6/20 planisware_com -> claimed
[2026-07-03 03:26:54] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:26:54] INFO src.core.dispatcher: dispatcher._run_unified index 7/20 icgam_com -> claimed
[2026-07-03 03:26:54] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:26:54] INFO src.core.dispatcher: dispatcher._run_unified index 8/20 lawsonchase_com -> claimed
[2026-07-03 03:26:54] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:26:54] INFO src.core.dispatcher: dispatcher._run_unified index 9/20 alliancebernstein_com -> claimed
[2026-07-03 03:26:54] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:26:54] INFO src.core.dispatcher: dispatcher._run_unified index 10/20 williamblair_com -> claimed
[2026-07-03 03:26:54] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:26:54] INFO src.core.dispatcher: dispatcher._run_unified index 11/20 dnv_com -> claimed
[2026-07-03 03:26:54] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:26:54] INFO src.core.dispatcher: dispatcher._run_unified index 12/20 dowjones_com -> claimed
[2026-07-03 03:26:54] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:26:54] INFO src.core.dispatcher: dispatcher._run_unified index 13/20 ishares_com -> claimed
[2026-07-03 03:26:54] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:26:54] INFO src.core.dispatcher: dispatcher._run_unified index 14/20 toyota_ventures -> claimed
[2026-07-03 03:26:54] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:26:53] ERROR src.external.playwright: Firefox launch failed: TimeoutError: BrowserType.launch: Timeout 180000ms exceeded.
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-SKBOGH -juggler-pipe -silent
  - <launched> pid=7093
  - [pid=7093][err] [7093] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=7093][err] *** You are running in headless mode.
  - [pid=7093][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement

[2026-07-03 03:26:53] WARNING src.external.playwright: check_connectivity failed: Could not launch Firefox.
  Error: BrowserType.launch: Timeout 180000ms exceeded.
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-SKBOGH -juggler-pipe -silent
  - <launched> pid=7093
  - [pid=7093][err] [7093] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=7093][err] *** You are running in headless mode.
  - [pid=7093][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
[2026-07-03 03:26:53] ERROR src.external.playwright: Firefox launch failed: TimeoutError: BrowserType.launch: Timeout 180000ms exceeded.
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-hLpDik -juggler-pipe -silent
  - <launched> pid=9658
  - [pid=9658][err] [9658] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=9658][err] *** You are running in headless mode.

[2026-07-03 03:26:53] ERROR src.core.dispatcher:   gather slot 1 raised: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 371, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2016, in run_consult_task
    r = await fetch_website_batch(batch_id, entities, debug=debug)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/gazer.py", line 277, in fetch_website_batch
    raise ConnectionError(
ConnectionError: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
[2026-07-03 03:26:53] ERROR src.core.dispatcher:   gather slot 5 raised: Could not launch Firefox.
  Error: BrowserType.launch: Timeout 180000ms exceeded.
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-hLpDik -juggler-pipe -silent
  - <launched> pid=9658
  - [pid=9658][err] [9658] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=9658][err] *** You are running in headless mode.

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
Traceback (most recent call last):
  File "/app/src/external/playwright.py", line 69, in _launch_browser
    browser = await pw.firefox.launch(
              ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/async_api/_generated.py", line 16546, in launch
    await self._impl_obj.launch(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_browser_type.py", line 97, in launch
    await self._channel.send(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py", line 69, in send
    return await self._connection.wrap_api_call(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py", line 563, in wrap_api_call
    raise rewrite_error(error, f"{parsed_st['apiName']}: {error}") from None
playwright._impl._errors.TimeoutError: BrowserType.launch: Timeout 180000ms exceeded.
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-hLpDik -juggler-pipe -silent
  - <launched> pid=9658
  - [pid=9658][err] [9658] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=9658][err] *** You are running in headless mode.


During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 371, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2016, in run_consult_task
    r = await fetch_website_batch(batch_id, entities, debug=debug)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/gazer.py", line 299, in fetch_website_batch
    async with create_browser_context() as browser_context:
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.nix-profile/lib/python3.12/contextlib.py", line 210, in __aenter__
    return await anext(self.gen)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 411, in create_browser_context
    browser = await _launch_browser(pw, headless=headless)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 77, in _launch_browser
    raise Exception(
Exception: Could not launch Firefox.
  Error: BrowserType.launch: Timeout 180000ms exceeded.
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-hLpDik -juggler-pipe -silent
  - <launched> pid=9658
  - [pid=9658][err] [9658] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=9658][err] *** You are running in headless mode.

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
[2026-07-03 03:24:47] INFO src.core.gazer:  | summary passed=0 failed=1 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:24:47] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:24:47] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:24:47] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:24:47] INFO src.core.roster: [docs_glean_com] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:24:47] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 docs_glean_com -> passed -> HOMEPAGE_READY (4569 chars redirect=yes nav=116 links)
[2026-07-03 03:24:47] INFO src.core.gazer:  | company_website='https://www.glean.com' canonical='https://www.glean.com/' homepage_chars=4569 nav_links=116
[2026-07-03 03:24:47] INFO src.core.gazer:  | summary passed=1 failed=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:24:47] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 veeva_com -> failed — Page.goto: Page crashed
Call log:
  - navigating to "https://www.veeva.com/", waiting until "load"
 -> CANNOT_READ_WEBSITE
[2026-07-03 03:24:47] INFO src.core.gazer:  | company_website='https://www.veeva.com'
[2026-07-03 03:24:47] INFO src.core.roster: [veeva_com] company state WEBSITE_FOUND -> CANNOT_READ_WEBSITE (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:24:47] INFO src.core.roster: [alvarezandmarsal_com] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:24:47] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 alvarezandmarsal_com -> passed -> HOMEPAGE_READY (207 chars redirect=yes nav=0 links)
[2026-07-03 03:24:47] INFO src.core.gazer:  | company_website='https://www.alvarezandmarsal.com' canonical='https://www.alvarezandmarsal.com/' homepage_chars=207 nav_links=0
[2026-07-03 03:24:47] INFO src.core.gazer:  | summary passed=0 failed=1 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:24:47] INFO src.core.gazer:  | summary passed=1 failed=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:24:47] INFO src.core.roster: [blackrock_com] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:24:47] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 blackrock_com -> passed -> HOMEPAGE_READY (4913 chars redirect=yes nav=118 links)
[2026-07-03 03:24:47] INFO src.core.gazer:  | company_website='https://www.blackrock.com' canonical='https://www.blackrock.com/us/individual' homepage_chars=4913 nav_links=118
[2026-07-03 03:24:47] INFO src.core.gazer:  | summary passed=1 failed=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:24:47] INFO src.core.roster: [carislifesciences_com] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:24:47] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 carislifesciences_com -> passed -> HOMEPAGE_READY (9094 chars redirect=yes nav=84 links)
[2026-07-03 03:24:47] INFO src.core.gazer:  | company_website='https://www.carislifesciences.com' canonical='https://www.carislifesciences.com/' homepage_chars=9094 nav_links=84
[2026-07-03 03:24:47] INFO src.core.gazer:  | summary passed=1 failed=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:24:47] INFO src.core.roster: [enverus_com] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:24:47] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 enverus_com -> passed -> HOMEPAGE_READY (8918 chars redirect=yes nav=155 links)
[2026-07-03 03:24:47] INFO src.core.gazer:  | company_website='https://www.enverus.com' canonical='https://www.enverus.com/' homepage_chars=8918 nav_links=155
[2026-07-03 03:24:47] INFO src.core.gazer:  | summary passed=1 failed=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:23:55] INFO src.core.roster: [astrixinc_com] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:23:55] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 astrixinc_com -> passed -> HOMEPAGE_READY (3917 chars redirect=yes nav=84 links)
[2026-07-03 03:23:55] INFO src.core.gazer:  | company_website='https://www.astrixinc.com' canonical='https://www.astrixinc.com/' homepage_chars=3917 nav_links=84
[2026-07-03 03:23:55] INFO src.core.gazer:  | summary passed=1 failed=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:23:55] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:55] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:55] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:55] WARNING src.external.playwright: check_connectivity failed: BrowserContext.new_page: Target page, context or browser has been closed
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-L70BrI -juggler-pipe -silent
<launched> pid=6987
[pid=6987][err] [6987] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=6987][err] *** You are running in headless mode.
[pid=6987][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=6987][out] 
[pid=6987][out] Juggler listening to the pipe
[2026-07-03 03:23:55] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:55] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 nuveen_com -> failed — BrowserContext.new_page: Target page, context or browser has been closed
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-REmrY3 -juggler-pipe -silent
<launched> pid=8166
[pid=8166][err] [8166] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=8166][err] *** You are running in headless mode.
[pid=8166][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=8166][out] 
[pid=8166][out] Juggler listening to the pipe -> CANNOT_READ_WEBSITE
[2026-07-03 03:23:55] INFO src.core.gazer:  | company_website='https://www.nuveen.com'
[2026-07-03 03:23:55] INFO src.core.roster: [nuveen_com] company state WEBSITE_FOUND -> CANNOT_READ_WEBSITE (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:23:55] INFO src.core.gazer:  | summary passed=0 failed=1 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:23:55] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:55] WARNING src.external.playwright: check_connectivity failed: BrowserContext.new_page: Target page, context or browser has been closed
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-VjiikL -juggler-pipe -silent
<launched> pid=7003
[pid=7003][err] [7003] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=7003][err] *** You are running in headless mode.
[pid=7003][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=7003][out] 
[pid=7003][out] Juggler listening to the pipe
[pid=7003][out] 
[pid=7003][out]         ERROR: ERROR: cannot find session with id "c43ff705-5c1d-4c88-97f8-685a78218215" _dispatch@chrome://juggler/content/protocol/Dispatcher.js:54:15
[pid=7003][out] receiveMessage@chrome://juggler/content/components/Juggler.js:121:20
[pid=7003][out] 
[pid=7003][err] [Parent 7003, IPC I/O Parent] WARNING: process 8824 exited on signal 11: file ./../../../ipc/chromium/src/chrome/common/process_watcher_posix_sigchld.cc:161
[pid=7003][out]       console.error: (new TypeError("can't access property \"maybeCancelContentJSExecution\", this._browser.frameLoader.remoteTab is null", "resource://gre/modules/RemoteWebNavigation.sys.mjs", 41))
[pid=7003][err] Exiting due to channel error.
[2026-07-03 03:23:55] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:55] WARNING src.external.playwright: check_connectivity failed: Page.goto: Target page, context or browser has been closed
Call log:
  - navigating to "https://www.google.com/", waiting until "commit"

[2026-07-03 03:23:55] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:55] ERROR src.external.playwright: Firefox launch failed: Exception: BrowserType.launch: Connection closed while reading from the driver
[2026-07-03 03:23:55] WARNING src.external.playwright: check_connectivity failed: BrowserContext.new_page: Target page, context or browser has been closed
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-TNzUsX -juggler-pipe -silent
<launched> pid=7004
[pid=7004][err] [7004] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=7004][err] *** You are running in headless mode.
[pid=7004][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=7004][out] 
[pid=7004][out] Juggler listening to the pipe
[pid=7004][out] console.error: services.settings: 
[pid=7004][out]   Message: UnknownError: IndexedDB: main/moz-essential-domain-fallbacks getLastModified() IndexedDB:   The operation failed for reasons unrelated to the database itself and not covered by any other error code.
[pid=7004][out] console.error: services.settings: 
[pid=7004][out]   Message: UnknownError: IndexedDB: main/remote-permissions getLastModified() IndexedDB:   The operation failed for reasons unrelated to the database itself and not covered by any other error code.
[pid=7004][out] console.error: services.settings: 
[pid=7004][out]   Message: UnknownError: IndexedDB: main/url-parser-default-unknown-schemes-interventions getLastModified() IndexedDB:   The operation failed for reasons unrelated to the database itself and not covered by any other error code.
[pid=7004][out] console.error: services.settings: 
[pid=7004][out]   Message: UnknownError: IndexedDB: main/anti-tracking-url-decoration getLastModified() IndexedDB:   The operation failed for reasons unrelated to the database itself and not covered by any other error code.
[pid=7004][out] console.error: services.settings: 
[pid=7004][out]   Message: UnknownError: IndexedDB: main/query-stripping getLastModified() IndexedDB:   The operation failed for reasons unrelated to the database itself and not covered by any other error code.
[pid=7004][out] console.error: services.settings: 
[pid=7004][out]   Message: UnknownError: IndexedDB: main/fingerprinting-protection-overrides getLastModified() IndexedDB:   The operation failed for reasons unrelated to the database itself and not covered by any other error code.
[pid=7004][err] [Parent 7004, IPC I/O Parent] WARNING: process 9751 exited on signal 11: file ./../../../ipc/chromium/src/chrome/common/process_watcher_posix_sigchld.cc:161
[2026-07-03 03:23:55] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 docs_uipath_com -> failed — BrowserContext.new_page: Target page, context or browser has been closed
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-XQf5MW -juggler-pipe -silent
<launched> pid=9312
[pid=9312][err] [9312] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=9312][err] *** You are running in headless mode.
[pid=9312][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=9312][out] Crash Annotation GraphicsCriticalError: |[0][GFX1-]: Compositor thread not started (true) (t=0.707639) [GFX1-]: Compositor thread not started (true)
[pid=9312][out] 
[pid=9312][out] Juggler listening to the pipe -> CANNOT_READ_WEBSITE
[2026-07-03 03:23:55] INFO src.core.gazer:  | company_website='https://www.uipath.com'
[2026-07-03 03:23:55] INFO src.core.roster: [docs_uipath_com] company state WEBSITE_FOUND -> CANNOT_READ_WEBSITE (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:23:55] INFO src.core.gazer:  | summary passed=0 failed=1 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:23:55] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 florencehc_com -> failed — BrowserContext.new_page: Cannot read properties of undefined (reading '_page') -> CANNOT_READ_WEBSITE
[2026-07-03 03:23:55] INFO src.core.gazer:  | company_website='https://www.florencehc.com'
[2026-07-03 03:23:55] INFO src.core.roster: [florencehc_com] company state WEBSITE_FOUND -> CANNOT_READ_WEBSITE (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:23:55] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:55] ERROR src.external.playwright: Firefox launch failed: Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-kH7o3F -juggler-pipe -silent
<launched> pid=7092
[pid=7092][err] [7092] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=7092][err] *** You are running in headless mode.
[pid=7092] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=7092] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-kH7o3F -juggler-pipe -silent
  - <launched> pid=7092
  - [pid=7092][err] [7092] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=7092][err] *** You are running in headless mode.
  - [pid=7092] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=7092] starting temporary directories cleanup
  - [pid=7092] <gracefully close start>
  - [pid=7092] <kill>
  - [pid=7092] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=7092] finished temporary directories cleanup
  - [pid=7092] <gracefully close end>

[2026-07-03 03:23:55] WARNING src.external.playwright: check_connectivity failed: Could not launch Firefox.
  Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-kH7o3F -juggler-pipe -silent
<launched> pid=7092
[pid=7092][err] [7092] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=7092][err] *** You are running in headless mode.
[pid=7092] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=7092] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-kH7o3F -juggler-pipe -silent
  - <launched> pid=7092
  - [pid=7092][err] [7092] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=7092][err] *** You are running in headless mode.
  - [pid=7092] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=7092] starting temporary directories cleanup
  - [pid=7092] <gracefully close start>
  - [pid=7092] <kill>
  - [pid=7092] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=7092] finished temporary directories cleanup
  - [pid=7092] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
[2026-07-03 03:23:55] ERROR src.external.playwright: Firefox launch failed: Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-GaQE9g -juggler-pipe -silent
<launched> pid=7005
[pid=7005][err] [7005] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=7005][err] *** You are running in headless mode.
[pid=7005][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=7005] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=7005] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-GaQE9g -juggler-pipe -silent
  - <launched> pid=7005
  - [pid=7005][err] [7005] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=7005][err] *** You are running in headless mode.
  - [pid=7005][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=7005] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=7005] starting temporary directories cleanup
  - [pid=7005] <gracefully close start>
  - [pid=7005] <kill>
  - [pid=7005] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=7005] finished temporary directories cleanup
  - [pid=7005] <gracefully close end>

[2026-07-03 03:23:55] WARNING src.external.playwright: check_connectivity failed: Could not launch Firefox.
  Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-GaQE9g -juggler-pipe -silent
<launched> pid=7005
[pid=7005][err] [7005] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=7005][err] *** You are running in headless mode.
[pid=7005][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=7005] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=7005] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-GaQE9g -juggler-pipe -silent
  - <launched> pid=7005
  - [pid=7005][err] [7005] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=7005][err] *** You are running in headless mode.
  - [pid=7005][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=7005] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=7005] starting temporary directories cleanup
  - [pid=7005] <gracefully close start>
  - [pid=7005] <kill>
  - [pid=7005] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=7005] finished temporary directories cleanup
  - [pid=7005] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
[2026-07-03 03:23:55] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 wellsfargojobs_com -> failed — Page.goto: Target page, context or browser has been closed
Call log:
  - navigating to "https://www.wellsfargo.com/", waiting until "load"
 -> CANNOT_READ_WEBSITE
[2026-07-03 03:23:55] INFO src.core.gazer:  | company_website='https://www.wellsfargo.com'
[2026-07-03 03:23:55] INFO src.core.roster: [wellsfargojobs_com] company state WEBSITE_FOUND -> CANNOT_READ_WEBSITE (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:23:55] INFO src.core.gazer:  | summary passed=0 failed=1 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:23:55] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:36] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:34] INFO src.core.gazer:  | summary passed=1 failed=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:23:34] ERROR src.core.dispatcher:   gather slot 1 raised: Could not launch Firefox.
  Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-RyG9m9 -juggler-pipe -silent
<launched> pid=3527
[pid=3527][err] [3527] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=3527][err] *** You are running in headless mode.
[pid=3527] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=3527] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-RyG9m9 -juggler-pipe -silent
  - <launched> pid=3527
  - [pid=3527][err] [3527] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=3527][err] *** You are running in headless mode.
  - [pid=3527] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=3527] starting temporary directories cleanup
  - [pid=3527] <gracefully close start>
  - [pid=3527] <kill>
  - [pid=3527] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=3527] finished temporary directories cleanup
  - [pid=3527] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
Traceback (most recent call last):
  File "/app/src/external/playwright.py", line 69, in _launch_browser
    browser = await pw.firefox.launch(
              ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/async_api/_generated.py", line 16546, in launch
    await self._impl_obj.launch(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_browser_type.py", line 97, in launch
    await self._channel.send(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py", line 69, in send
    return await self._connection.wrap_api_call(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py", line 563, in wrap_api_call
    raise rewrite_error(error, f"{parsed_st['apiName']}: {error}") from None
playwright._impl._errors.Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-RyG9m9 -juggler-pipe -silent
<launched> pid=3527
[pid=3527][err] [3527] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=3527][err] *** You are running in headless mode.
[pid=3527] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=3527] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-RyG9m9 -juggler-pipe -silent
  - <launched> pid=3527
  - [pid=3527][err] [3527] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=3527][err] *** You are running in headless mode.
  - [pid=3527] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=3527] starting temporary directories cleanup
  - [pid=3527] <gracefully close start>
  - [pid=3527] <kill>
  - [pid=3527] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=3527] finished temporary directories cleanup
  - [pid=3527] <gracefully close end>


During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 371, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2016, in run_consult_task
    r = await fetch_website_batch(batch_id, entities, debug=debug)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/gazer.py", line 299, in fetch_website_batch
    async with create_browser_context() as browser_context:
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.nix-profile/lib/python3.12/contextlib.py", line 210, in __aenter__
    return await anext(self.gen)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 411, in create_browser_context
    browser = await _launch_browser(pw, headless=headless)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 77, in _launch_browser
    raise Exception(
Exception: Could not launch Firefox.
  Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-RyG9m9 -juggler-pipe -silent
<launched> pid=3527
[pid=3527][err] [3527] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=3527][err] *** You are running in headless mode.
[pid=3527] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=3527] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-RyG9m9 -juggler-pipe -silent
  - <launched> pid=3527
  - [pid=3527][err] [3527] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=3527][err] *** You are running in headless mode.
  - [pid=3527] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=3527] starting temporary directories cleanup
  - [pid=3527] <gracefully close start>
  - [pid=3527] <kill>
  - [pid=3527] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=3527] finished temporary directories cleanup
  - [pid=3527] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
[2026-07-03 03:23:34] ERROR src.core.dispatcher:   gather slot 2 raised: Could not launch Firefox.
  Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-XLCGJj -juggler-pipe -silent
<launched> pid=2732
[pid=2732][err] [2732] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=2732][err] *** You are running in headless mode.
[pid=2732] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=2732] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-XLCGJj -juggler-pipe -silent
  - <launched> pid=2732
  - [pid=2732][err] [2732] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=2732][err] *** You are running in headless mode.
  - [pid=2732] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=2732] starting temporary directories cleanup
  - [pid=2732] <gracefully close start>
  - [pid=2732] <kill>
  - [pid=2732] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=2732] finished temporary directories cleanup
  - [pid=2732] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
Traceback (most recent call last):
  File "/app/src/external/playwright.py", line 69, in _launch_browser
    browser = await pw.firefox.launch(
              ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/async_api/_generated.py", line 16546, in launch
    await self._impl_obj.launch(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_browser_type.py", line 97, in launch
    await self._channel.send(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py", line 69, in send
    return await self._connection.wrap_api_call(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py", line 563, in wrap_api_call
    raise rewrite_error(error, f"{parsed_st['apiName']}: {error}") from None
playwright._impl._errors.Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-XLCGJj -juggler-pipe -silent
<launched> pid=2732
[pid=2732][err] [2732] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=2732][err] *** You are running in headless mode.
[pid=2732] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=2732] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-XLCGJj -juggler-pipe -silent
  - <launched> pid=2732
  - [pid=2732][err] [2732] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=2732][err] *** You are running in headless mode.
  - [pid=2732] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=2732] starting temporary directories cleanup
  - [pid=2732] <gracefully close start>
  - [pid=2732] <kill>
  - [pid=2732] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=2732] finished temporary directories cleanup
  - [pid=2732] <gracefully close end>


During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 371, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2016, in run_consult_task
    r = await fetch_website_batch(batch_id, entities, debug=debug)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/gazer.py", line 299, in fetch_website_batch
    async with create_browser_context() as browser_context:
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.nix-profile/lib/python3.12/contextlib.py", line 210, in __aenter__
    return await anext(self.gen)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 411, in create_browser_context
    browser = await _launch_browser(pw, headless=headless)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 77, in _launch_browser
    raise Exception(
Exception: Could not launch Firefox.
  Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-XLCGJj -juggler-pipe -silent
<launched> pid=2732
[pid=2732][err] [2732] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=2732][err] *** You are running in headless mode.
[pid=2732] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=2732] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-XLCGJj -juggler-pipe -silent
  - <launched> pid=2732
  - [pid=2732][err] [2732] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=2732][err] *** You are running in headless mode.
  - [pid=2732] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=2732] starting temporary directories cleanup
  - [pid=2732] <gracefully close start>
  - [pid=2732] <kill>
  - [pid=2732] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=2732] finished temporary directories cleanup
  - [pid=2732] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
[2026-07-03 03:23:34] ERROR src.core.dispatcher:   gather slot 3 raised: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 371, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2016, in run_consult_task
    r = await fetch_website_batch(batch_id, entities, debug=debug)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/gazer.py", line 277, in fetch_website_batch
    raise ConnectionError(
ConnectionError: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
[2026-07-03 03:23:34] ERROR src.core.dispatcher:   gather slot 6 raised: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 371, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2016, in run_consult_task
    r = await fetch_website_batch(batch_id, entities, debug=debug)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/gazer.py", line 277, in fetch_website_batch
    raise ConnectionError(
ConnectionError: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
[2026-07-03 03:23:34] ERROR src.core.dispatcher:   gather slot 7 raised: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 371, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2016, in run_consult_task
    r = await fetch_website_batch(batch_id, entities, debug=debug)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/gazer.py", line 277, in fetch_website_batch
    raise ConnectionError(
ConnectionError: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
[2026-07-03 03:23:34] ERROR src.core.dispatcher:   gather slot 10 raised: Could not launch Firefox.
  Error: BrowserType.launch: Connection closed while reading from the driver
  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
Traceback (most recent call last):
  File "/app/src/external/playwright.py", line 69, in _launch_browser
    browser = await pw.firefox.launch(
              ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/async_api/_generated.py", line 16546, in launch
    await self._impl_obj.launch(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_browser_type.py", line 97, in launch
    await self._channel.send(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py", line 69, in send
    return await self._connection.wrap_api_call(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py", line 563, in wrap_api_call
    raise rewrite_error(error, f"{parsed_st['apiName']}: {error}") from None
Exception: BrowserType.launch: Connection closed while reading from the driver

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 371, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2016, in run_consult_task
    r = await fetch_website_batch(batch_id, entities, debug=debug)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/gazer.py", line 299, in fetch_website_batch
    async with create_browser_context() as browser_context:
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.nix-profile/lib/python3.12/contextlib.py", line 210, in __aenter__
    return await anext(self.gen)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 411, in create_browser_context
    browser = await _launch_browser(pw, headless=headless)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 77, in _launch_browser
    raise Exception(
Exception: Could not launch Firefox.
  Error: BrowserType.launch: Connection closed while reading from the driver
  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
[2026-07-03 03:23:34] ERROR src.core.dispatcher:   gather slot 11 raised: Could not launch Firefox.
  Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-2QfNo0 -juggler-pipe -silent
<launched> pid=2453
[pid=2453][err] [2453] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=2453][err] *** You are running in headless mode.
[pid=2453] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=2453] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-2QfNo0 -juggler-pipe -silent
  - <launched> pid=2453
  - [pid=2453][err] [2453] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=2453][err] *** You are running in headless mode.
  - [pid=2453] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=2453] starting temporary directories cleanup
  - [pid=2453] <gracefully close start>
  - [pid=2453] <kill>
  - [pid=2453] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=2453] finished temporary directories cleanup
  - [pid=2453] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
Traceback (most recent call last):
  File "/app/src/external/playwright.py", line 69, in _launch_browser
    browser = await pw.firefox.launch(
              ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/async_api/_generated.py", line 16546, in launch
    await self._impl_obj.launch(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_browser_type.py", line 97, in launch
    await self._channel.send(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py", line 69, in send
    return await self._connection.wrap_api_call(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py", line 563, in wrap_api_call
    raise rewrite_error(error, f"{parsed_st['apiName']}: {error}") from None
playwright._impl._errors.Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-2QfNo0 -juggler-pipe -silent
<launched> pid=2453
[pid=2453][err] [2453] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=2453][err] *** You are running in headless mode.
[pid=2453] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=2453] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-2QfNo0 -juggler-pipe -silent
  - <launched> pid=2453
  - [pid=2453][err] [2453] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=2453][err] *** You are running in headless mode.
  - [pid=2453] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=2453] starting temporary directories cleanup
  - [pid=2453] <gracefully close start>
  - [pid=2453] <kill>
  - [pid=2453] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=2453] finished temporary directories cleanup
  - [pid=2453] <gracefully close end>


During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 371, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2016, in run_consult_task
    r = await fetch_website_batch(batch_id, entities, debug=debug)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/gazer.py", line 299, in fetch_website_batch
    async with create_browser_context() as browser_context:
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.nix-profile/lib/python3.12/contextlib.py", line 210, in __aenter__
    return await anext(self.gen)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 411, in create_browser_context
    browser = await _launch_browser(pw, headless=headless)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 77, in _launch_browser
    raise Exception(
Exception: Could not launch Firefox.
  Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-2QfNo0 -juggler-pipe -silent
<launched> pid=2453
[pid=2453][err] [2453] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=2453][err] *** You are running in headless mode.
[pid=2453] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=2453] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-2QfNo0 -juggler-pipe -silent
  - <launched> pid=2453
  - [pid=2453][err] [2453] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=2453][err] *** You are running in headless mode.
  - [pid=2453] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=2453] starting temporary directories cleanup
  - [pid=2453] <gracefully close start>
  - [pid=2453] <kill>
  - [pid=2453] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=2453] finished temporary directories cleanup
  - [pid=2453] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
[2026-07-03 03:23:34] ERROR src.core.dispatcher:   gather slot 12 raised: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 371, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2016, in run_consult_task
    r = await fetch_website_batch(batch_id, entities, debug=debug)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/gazer.py", line 277, in fetch_website_batch
    raise ConnectionError(
ConnectionError: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
[2026-07-03 03:23:34] ERROR src.core.dispatcher:   gather slot 16 raised: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 371, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2016, in run_consult_task
    r = await fetch_website_batch(batch_id, entities, debug=debug)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/gazer.py", line 277, in fetch_website_batch
    raise ConnectionError(
ConnectionError: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
[2026-07-03 03:23:34] ERROR src.core.dispatcher:   gather slot 17 raised: Could not launch Firefox.
  Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-hKOzAm -juggler-pipe -silent
<launched> pid=3282
[pid=3282][err] [3282] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=3282][err] *** You are running in headless mode.
[pid=3282] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=3282] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-hKOzAm -juggler-pipe -silent
  - <launched> pid=3282
  - [pid=3282][err] [3282] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=3282][err] *** You are running in headless mode.
  - [pid=3282] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=3282] starting temporary directories cleanup
  - [pid=3282] <gracefully close start>
  - [pid=3282] <kill>
  - [pid=3282] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=3282] finished temporary directories cleanup
  - [pid=3282] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
Traceback (most recent call last):
  File "/app/src/external/playwright.py", line 69, in _launch_browser
    browser = await pw.firefox.launch(
              ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/async_api/_generated.py", line 16546, in launch
    await self._impl_obj.launch(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_browser_type.py", line 97, in launch
    await self._channel.send(
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py", line 69, in send
    return await self._connection.wrap_api_call(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/venv/lib/python3.12/site-packages/playwright/_impl/_connection.py", line 563, in wrap_api_call
    raise rewrite_error(error, f"{parsed_st['apiName']}: {error}") from None
playwright._impl._errors.Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-hKOzAm -juggler-pipe -silent
<launched> pid=3282
[pid=3282][err] [3282] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=3282][err] *** You are running in headless mode.
[pid=3282] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=3282] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-hKOzAm -juggler-pipe -silent
  - <launched> pid=3282
  - [pid=3282][err] [3282] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=3282][err] *** You are running in headless mode.
  - [pid=3282] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=3282] starting temporary directories cleanup
  - [pid=3282] <gracefully close start>
  - [pid=3282] <kill>
  - [pid=3282] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=3282] finished temporary directories cleanup
  - [pid=3282] <gracefully close end>


During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 371, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2016, in run_consult_task
    r = await fetch_website_batch(batch_id, entities, debug=debug)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/gazer.py", line 299, in fetch_website_batch
    async with create_browser_context() as browser_context:
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.nix-profile/lib/python3.12/contextlib.py", line 210, in __aenter__
    return await anext(self.gen)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 411, in create_browser_context
    browser = await _launch_browser(pw, headless=headless)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/external/playwright.py", line 77, in _launch_browser
    raise Exception(
Exception: Could not launch Firefox.
  Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-hKOzAm -juggler-pipe -silent
<launched> pid=3282
[pid=3282][err] [3282] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=3282][err] *** You are running in headless mode.
[pid=3282] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=3282] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-hKOzAm -juggler-pipe -silent
  - <launched> pid=3282
  - [pid=3282][err] [3282] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=3282][err] *** You are running in headless mode.
  - [pid=3282] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=3282] starting temporary directories cleanup
  - [pid=3282] <gracefully close start>
  - [pid=3282] <kill>
  - [pid=3282] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=3282] finished temporary directories cleanup
  - [pid=3282] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
[2026-07-03 03:23:34] ERROR src.core.dispatcher:   gather slot 19 raised: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 371, in _one
    return await consult.run_consult_task(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 2016, in run_consult_task
    r = await fetch_website_batch(batch_id, entities, debug=debug)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/gazer.py", line 277, in fetch_website_batch
    raise ConnectionError(
ConnectionError: fetch_website_batch: no internet connectivity, aborting batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 (1 companies)
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | batch end summary={'total_processed': 20, 'total_passed': 5, 'total_failed': 4, 'total_errors': 11}
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | runner returned summary={'total_processed': 20, 'total_passed': 5, 'total_failed': 4, 'total_errors': 11}
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | iteration 1 summary processed=20 passed=5 failed=4 errors=11 accumulated={'total_processed': 20, 'total_passed': 5, 'total_failed': 4, 'total_errors': 11}
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_dispatch_loop index 2/2 fetch_website -> loop iteration 2 starting
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | available=175 effective_min=1 max_runs=0 draining=False entity_batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_task index 1/1 fetch_website -> running batch
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | batch_size=20 batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 entity_type='company' trigger_state='WEBSITE_FOUND'
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_unified index 1/1 company/WEBSITE_FOUND -> claimed 20 entity/entities
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | task_key=fetch_website batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 batch_call_mode=False dispatch batch_size=20 claim_cap=None claim_states=['WEBSITE_FOUND', 'WEBSITE_FOUND_RETRY']
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_unified index 1/20 astrixinc_com -> claimed
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_unified index 2/20 legendbiotech_com -> claimed
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_unified index 3/20 florencehc_com -> claimed
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_unified index 4/20 carislifesciences_com -> claimed
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_unified index 5/20 veeva_com -> claimed
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_unified index 6/20 analytikjena_us -> claimed
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_unified index 7/20 docs_uipath_com -> claimed
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_unified index 8/20 docs_glean_com -> claimed
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_unified index 9/20 docs_aws_amazon_com -> claimed
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_unified index 10/20 careers_spglobal_com -> claimed
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_unified index 11/20 wellsfargojobs_com -> claimed
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_unified index 12/20 community_hubspot_com -> claimed
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_unified index 13/20 planisware_com -> claimed
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_unified index 14/20 nuveen_com -> claimed
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_unified index 15/20 blackrock_com -> claimed
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_unified index 16/20 enverus_com -> claimed
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_unified index 17/20 icgam_com -> claimed
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_unified index 18/20 lawsonchase_com -> claimed
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_unified index 19/20 alvarezandmarsal_com -> claimed
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:34] INFO src.core.dispatcher: dispatcher._run_unified index 20/20 alliancebernstein_com -> claimed
[2026-07-03 03:23:34] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:33] INFO src.core.roster: [iqvia_com] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:23:33] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 iqvia_com -> passed -> HOMEPAGE_READY (13006 chars redirect=yes nav=227 links)
[2026-07-03 03:23:33] INFO src.core.gazer:  | company_website='https://www.iqvia.com' canonical='https://www.iqvia.com/' homepage_chars=13006 nav_links=227
[2026-07-03 03:23:27] ERROR src.external.playwright: Firefox launch failed: Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-hKOzAm -juggler-pipe -silent
<launched> pid=3282
[pid=3282][err] [3282] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=3282][err] *** You are running in headless mode.
[pid=3282] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=3282] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-hKOzAm -juggler-pipe -silent
  - <launched> pid=3282
  - [pid=3282][err] [3282] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=3282][err] *** You are running in headless mode.
  - [pid=3282] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=3282] starting temporary directories cleanup
  - [pid=3282] <gracefully close start>
  - [pid=3282] <kill>
  - [pid=3282] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=3282] finished temporary directories cleanup
  - [pid=3282] <gracefully close end>

[2026-07-03 03:23:27] ERROR src.external.playwright: Firefox launch failed: Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-XLCGJj -juggler-pipe -silent
<launched> pid=2732
[pid=2732][err] [2732] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=2732][err] *** You are running in headless mode.
[pid=2732] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=2732] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-XLCGJj -juggler-pipe -silent
  - <launched> pid=2732
  - [pid=2732][err] [2732] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=2732][err] *** You are running in headless mode.
  - [pid=2732] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=2732] starting temporary directories cleanup
  - [pid=2732] <gracefully close start>
  - [pid=2732] <kill>
  - [pid=2732] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=2732] finished temporary directories cleanup
  - [pid=2732] <gracefully close end>

[2026-07-03 03:23:27] ERROR src.external.playwright: Firefox launch failed: Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-2QfNo0 -juggler-pipe -silent
<launched> pid=2453
[pid=2453][err] [2453] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=2453][err] *** You are running in headless mode.
[pid=2453] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=2453] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-2QfNo0 -juggler-pipe -silent
  - <launched> pid=2453
  - [pid=2453][err] [2453] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=2453][err] *** You are running in headless mode.
  - [pid=2453] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=2453] starting temporary directories cleanup
  - [pid=2453] <gracefully close start>
  - [pid=2453] <kill>
  - [pid=2453] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=2453] finished temporary directories cleanup
  - [pid=2453] <gracefully close end>

[2026-07-03 03:23:27] ERROR src.external.playwright: Firefox launch failed: Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-RyG9m9 -juggler-pipe -silent
<launched> pid=3527
[pid=3527][err] [3527] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=3527][err] *** You are running in headless mode.
[pid=3527] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=3527] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-RyG9m9 -juggler-pipe -silent
  - <launched> pid=3527
  - [pid=3527][err] [3527] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=3527][err] *** You are running in headless mode.
  - [pid=3527] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=3527] starting temporary directories cleanup
  - [pid=3527] <gracefully close start>
  - [pid=3527] <kill>
  - [pid=3527] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=3527] finished temporary directories cleanup
  - [pid=3527] <gracefully close end>

[2026-07-03 03:23:27] WARNING src.external.playwright: check_connectivity failed: BrowserContext.new_page: Target page, context or browser has been closed
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-XLfBfy -juggler-pipe -silent
<launched> pid=894
[pid=894][err] [894] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=894][err] *** You are running in headless mode.
[pid=894][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=894][out] 
[pid=894][out] Juggler listening to the pipe
[pid=894][err] Exiting due to channel error.
[pid=894][err] Exiting due to channel error.
[2026-07-03 03:23:27] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:27] WARNING src.external.playwright: check_connectivity failed: Page.goto: Target page, context or browser has been closed
[2026-07-03 03:23:27] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:27] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:27] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 welcometothejungle_com -> failed — Page.goto: Page crashed
Call log:
  - navigating to "https://www.veeam.com/", waiting until "load"
 -> CANNOT_READ_WEBSITE
[2026-07-03 03:23:27] INFO src.core.gazer:  | company_website='https://www.veeam.com'
[2026-07-03 03:23:27] INFO src.core.roster: [welcometothejungle_com] company state WEBSITE_FOUND -> CANNOT_READ_WEBSITE (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:23:27] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 runatlantis_io -> failed — BrowserContext.new_page: Cannot read properties of undefined (reading '_page') -> CANNOT_READ_WEBSITE
[2026-07-03 03:23:27] INFO src.core.gazer:  | company_website='https://www.runatlantis.io'
[2026-07-03 03:23:27] INFO src.core.roster: [runatlantis_io] company state WEBSITE_FOUND -> CANNOT_READ_WEBSITE (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:23:27] INFO src.core.gazer:  | summary passed=0 failed=1 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:23:27] INFO src.core.gazer:  | summary passed=0 failed=1 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:23:27] INFO src.core.roster: [crinetics_com] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:23:27] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 crinetics_com -> passed -> HOMEPAGE_READY (2286 chars redirect=yes nav=49 links)
[2026-07-03 03:23:27] INFO src.core.gazer:  | company_website='https://crinetics.com' canonical='https://crinetics.com/' homepage_chars=2286 nav_links=49
[2026-07-03 03:23:27] INFO src.core.roster: [iktos_ai] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:23:27] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 iktos_ai -> passed -> HOMEPAGE_READY (6240 chars redirect=yes nav=20 links)
[2026-07-03 03:23:27] INFO src.core.gazer:  | company_website='https://iktos.ai' canonical='https://iktos.ai/' homepage_chars=6240 nav_links=20
[2026-07-03 03:23:27] INFO src.core.gazer:  | summary passed=1 failed=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:23:27] INFO src.core.gazer:  | summary passed=1 failed=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:23:27] INFO src.core.roster: [guardanthealth_com] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:23:27] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 guardanthealth_com -> passed -> HOMEPAGE_READY (4421 chars redirect=yes nav=46 links)
[2026-07-03 03:23:27] INFO src.core.gazer:  | company_website='https://guardanthealth.com' canonical='https://guardanthealth.com/' homepage_chars=4421 nav_links=46
[2026-07-03 03:23:27] INFO src.core.gazer:  | summary passed=1 failed=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:23:18] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:18] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:18] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 support_airtable_com -> failed — Page.goto: Target page, context or browser has been closed
Call log:
  - navigating to "https://www.airtable.com/", waiting until "load"
 -> CANNOT_READ_WEBSITE
[2026-07-03 03:23:18] INFO src.core.gazer:  | company_website='https://www.airtable.com'
[2026-07-03 03:23:18] INFO src.core.roster: [support_airtable_com] company state WEBSITE_FOUND -> CANNOT_READ_WEBSITE (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:23:18] INFO src.core.gazer:  | summary passed=0 failed=1 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:23:18] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:18] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 help_splunk_com -> failed — BrowserContext.new_page: Cannot read properties of undefined (reading '_page') -> CANNOT_READ_WEBSITE
[2026-07-03 03:23:18] INFO src.core.gazer:  | company_website='https://www.splunk.com'
[2026-07-03 03:23:18] INFO src.core.roster: [help_splunk_com] company state WEBSITE_FOUND -> CANNOT_READ_WEBSITE (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:23:18] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:18] ERROR src.external.playwright: Firefox launch failed: Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-9hAMcB -juggler-pipe -silent
<launched> pid=929
[pid=929][err] [929] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=929][err] *** You are running in headless mode.
[pid=929][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=929] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=929] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-9hAMcB -juggler-pipe -silent
  - <launched> pid=929
  - [pid=929][err] [929] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=929][err] *** You are running in headless mode.
  - [pid=929][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=929] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=929] starting temporary directories cleanup
  - [pid=929] <gracefully close start>
  - [pid=929] <kill>
  - [pid=929] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=929] finished temporary directories cleanup
  - [pid=929] <gracefully close end>

[2026-07-03 03:23:18] WARNING src.external.playwright: check_connectivity failed: Could not launch Firefox.
  Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-9hAMcB -juggler-pipe -silent
<launched> pid=929
[pid=929][err] [929] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=929][err] *** You are running in headless mode.
[pid=929][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=929] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=929] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-9hAMcB -juggler-pipe -silent
  - <launched> pid=929
  - [pid=929][err] [929] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=929][err] *** You are running in headless mode.
  - [pid=929][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=929] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=929] starting temporary directories cleanup
  - [pid=929] <gracefully close start>
  - [pid=929] <kill>
  - [pid=929] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=929] finished temporary directories cleanup
  - [pid=929] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
[2026-07-03 03:23:18] ERROR src.external.playwright: Firefox launch failed: Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-yJJmm3 -juggler-pipe -silent
<launched> pid=907
[pid=907][err] [907] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=907][err] *** You are running in headless mode.
[pid=907][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=907] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=907] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-yJJmm3 -juggler-pipe -silent
  - <launched> pid=907
  - [pid=907][err] [907] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=907][err] *** You are running in headless mode.
  - [pid=907][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=907] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=907] starting temporary directories cleanup
  - [pid=907] <gracefully close start>
  - [pid=907] <kill>
  - [pid=907] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=907] finished temporary directories cleanup
  - [pid=907] <gracefully close end>

[2026-07-03 03:23:18] WARNING src.external.playwright: check_connectivity failed: Could not launch Firefox.
  Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-yJJmm3 -juggler-pipe -silent
<launched> pid=907
[pid=907][err] [907] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=907][err] *** You are running in headless mode.
[pid=907][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=907] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=907] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-yJJmm3 -juggler-pipe -silent
  - <launched> pid=907
  - [pid=907][err] [907] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=907][err] *** You are running in headless mode.
  - [pid=907][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=907] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=907] starting temporary directories cleanup
  - [pid=907] <gracefully close start>
  - [pid=907] <kill>
  - [pid=907] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=907] finished temporary directories cleanup
  - [pid=907] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
[2026-07-03 03:23:18] INFO src.core.gazer:  | summary passed=0 failed=1 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:23:18] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:17] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:17] INFO src.core.dispatcher: dispatcher._run_unified index 12/20 docs_uipath_com -> claimed
[2026-07-03 03:23:17] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:17] INFO src.core.dispatcher: dispatcher._run_unified index 13/20 docs_glean_com -> claimed
[2026-07-03 03:23:17] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:17] INFO src.core.dispatcher: dispatcher._run_unified index 14/20 help_splunk_com -> claimed
[2026-07-03 03:23:17] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:17] INFO src.core.dispatcher: dispatcher._run_unified index 15/20 support_airtable_com -> claimed
[2026-07-03 03:23:17] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:17] INFO src.core.dispatcher: dispatcher._run_unified index 16/20 runatlantis_io -> claimed
[2026-07-03 03:23:17] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:17] INFO src.core.dispatcher: dispatcher._run_unified index 17/20 docs_aws_amazon_com -> claimed
[2026-07-03 03:23:17] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:17] INFO src.core.dispatcher: dispatcher._run_unified index 18/20 careers_spglobal_com -> claimed
[2026-07-03 03:23:17] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:17] INFO src.core.dispatcher: dispatcher._run_unified index 19/20 welcometothejungle_com -> claimed
[2026-07-03 03:23:17] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:17] INFO src.core.dispatcher: dispatcher._run_unified index 20/20 wellsfargojobs_com -> claimed
[2026-07-03 03:23:17] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:23:17] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:17] INFO src.core.roster: [silentpush] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743)
[2026-07-03 03:23:17] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 silentpush -> passed -> HOMEPAGE_READY (6424 chars redirect=no nav=42 links)
[2026-07-03 03:23:17] INFO src.core.gazer:  | company_website='https://www.silentpush.com/' canonical='https://www.silentpush.com/' homepage_chars=6424 nav_links=42
[2026-07-03 03:23:17] INFO src.core.gazer:  | summary passed=1 failed=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-03 03:23:17] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:17] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:17] ERROR src.external.playwright: Firefox launch failed: Exception: BrowserType.launch: Connection closed while reading from the driver
[2026-07-03 03:23:17] ERROR src.external.playwright: Firefox launch failed: Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-knDhHq -juggler-pipe -silent
<launched> pid=897
[pid=897][err] [897] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=897][err] *** You are running in headless mode.
[pid=897][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=897] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=897] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-knDhHq -juggler-pipe -silent
  - <launched> pid=897
  - [pid=897][err] [897] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=897][err] *** You are running in headless mode.
  - [pid=897][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=897] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=897] starting temporary directories cleanup
  - [pid=897] <gracefully close start>
  - [pid=897] <kill>
  - [pid=897] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=897] finished temporary directories cleanup
  - [pid=897] <gracefully close end>

[2026-07-03 03:23:17] WARNING src.external.playwright: check_connectivity failed: BrowserContext.new_page: Target page, context or browser has been closed
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-dv1gzb -juggler-pipe -silent
<launched> pid=971
[pid=971][err] [971] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=971][err] *** You are running in headless mode.
[pid=971][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=971][out] 
[pid=971][out] Juggler listening to the pipe
[pid=971][err] Exiting due to channel error.
[pid=971][err] Exiting due to channel error.
[2026-07-03 03:23:17] WARNING src.external.playwright: check_connectivity failed: Could not launch Firefox.
  Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-knDhHq -juggler-pipe -silent
<launched> pid=897
[pid=897][err] [897] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=897][err] *** You are running in headless mode.
[pid=897][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=897] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=897] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-knDhHq -juggler-pipe -silent
  - <launched> pid=897
  - [pid=897][err] [897] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=897][err] *** You are running in headless mode.
  - [pid=897][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=897] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=897] starting temporary directories cleanup
  - [pid=897] <gracefully close start>
  - [pid=897] <kill>
  - [pid=897] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=897] finished temporary directories cleanup
  - [pid=897] <gracefully close end>

  PLAYWRIGHT_BROWSERS_PATH=/app/.browsers
  Try: playwright install firefox
[2026-07-03 03:23:17] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:17] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:23:17] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 -> batch start 1 company/companies
[2026-07-03 03:22:59] INFO dispatch.scheduler: Dispatching fetch_website — 184 available, batch fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743
[2026-07-03 03:22:59] INFO src.core.dispatcher: dispatcher._run_dispatch_loop index 1/1 fetch_website -> loop iteration 1 starting
[2026-07-03 03:22:59] INFO src.core.dispatcher:  | available=184 effective_min=1 max_runs=0 draining=False entity_batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743
[2026-07-03 03:22:59] INFO src.core.dispatcher: dispatcher._run_task index 1/1 fetch_website -> running batch
[2026-07-03 03:22:59] INFO src.core.dispatcher:  | batch_size=20 batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 entity_type='company' trigger_state='WEBSITE_FOUND'
[2026-07-03 03:22:59] INFO src.core.dispatcher: dispatcher._run_unified index 1/1 company/WEBSITE_FOUND -> claimed 20 entity/entities
[2026-07-03 03:22:59] INFO src.core.dispatcher:  | task_key=fetch_website batch_id=fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743 batch_call_mode=False dispatch batch_size=20 claim_cap=None claim_states=['WEBSITE_FOUND', 'WEBSITE_FOUND_RETRY']
[2026-07-03 03:22:59] INFO src.core.dispatcher: dispatcher._run_unified index 1/20 silentpush -> claimed
[2026-07-03 03:22:59] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:22:59] INFO src.core.dispatcher: dispatcher._run_unified index 2/20 astrixinc_com -> claimed
[2026-07-03 03:22:59] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:22:59] INFO src.core.dispatcher: dispatcher._run_unified index 3/20 legendbiotech_com -> claimed
[2026-07-03 03:22:59] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:22:59] INFO src.core.dispatcher: dispatcher._run_unified index 4/20 florencehc_com -> claimed
[2026-07-03 03:22:59] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:22:59] INFO src.core.dispatcher: dispatcher._run_unified index 5/20 iktos_ai -> claimed
[2026-07-03 03:22:59] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:22:59] INFO src.core.dispatcher: dispatcher._run_unified index 6/20 iqvia_com -> claimed
[2026-07-03 03:22:59] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:22:59] INFO src.core.dispatcher: dispatcher._run_unified index 7/20 carislifesciences_com -> claimed
[2026-07-03 03:22:59] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:22:59] INFO src.core.dispatcher: dispatcher._run_unified index 8/20 veeva_com -> claimed
[2026-07-03 03:22:59] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:22:59] INFO src.core.dispatcher: dispatcher._run_unified index 9/20 crinetics_com -> claimed
[2026-07-03 03:22:59] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:22:59] INFO src.core.dispatcher: dispatcher._run_unified index 10/20 guardanthealth_com -> claimed
[2026-07-03 03:22:59] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-03 03:22:59] INFO src.core.dispatcher: dispatcher._run_unified index 11/20 analytikjena_us -> claimed
```

### Comments

#### chuckles — 2026-07-10T03:20:57.169Z
[check-linear] answered — dispatch_task vs server (@susan)

**Yes — identical `dispatch_task` rows are expected.** The row controls *which* task runs, batch size, trigger state, and claim rules. It does **not** provision CPU/RAM or isolate Firefox processes.

**Why staging differs from local with the same settings:**
- **Railway container:** shared vCPU/RAM, single Gunicorn worker (`RAILWAY_CONFIG.workers=1`), no desktop GPU — concurrent Playwright (`Semaphore(3)` inside a batch of 20) competes for memory.
- **Observed staging pattern:** Firefox **launch attempt 1/2 timeout** then recovery, or scrape success — config is the same, **wall-clock under load** is not.
- **Not a dispatch_task misconfiguration** — it's **host limits** + **AST-854 classifier gap** (page-crash errors → `CANNOT_READ_WEBSITE` instead of `WEBSITE_FOUND_RETRY`; prior note).

Recommend **fix-uat** bug for classifier extension; optional follow-up to tune `PLAYWRIGHT_CONFIG` launch/scrape timeouts for Railway only if you want — product call.

— Chuckles

#### susan — 2026-07-10T03:19:10.730Z
@chuckles the dispatch_task settings are identical between local and staging.  Why would this be an issue?  Is it a server limitation?

#### chuckles — 2026-07-10T03:18:04.668Z
[check-linear] answered — bootstrap / Railway Firefox (@susan)

**Bootstrap is installing Firefox.** Staging log shows launches from `/app/.browsers/firefox-1532/firefox/firefox` with Juggler pipe — that path is written at **build** (`scripts/build_railway.sh`: `PLAYWRIGHT_BROWSERS_PATH=$PWD/.browsers` + `playwright install --with-deps firefox`) and set at **runtime** (`start_server.py` → `RAILWAY_CONFIG.playwright_browsers_path`). Multiple companies in your slice reached **HOMEPAGE_READY** — install is present and working.

**Local vs staging difference is environment load, not missing browser:**
- Railway still logs `CanCreateUserNamespace() EACCES` + intermittent **launch attempt 1/2 timeout** under concurrent batch load (`Semaphore(3)`). `MOZ_DISABLE_CONTENT_SANDBOX=1` is already set in `start_server.py`; warnings can persist without blocking every launch.
- Local dev typically runs one browser, less memory pressure — fewer launch timeouts.

**Still separate from bootstrap:** **preoncology_com** / **careers_oracle_com** infra errors routed to **CANNOT_READ_WEBSITE** instead of **WEBSITE_FOUND_RETRY** (classifier gap from prior note) — recommend **fix-uat** bug child, not bootstrap change.

— Chuckles

#### susan — 2026-07-10T03:16:44.101Z
@chuckles This isn't happening on local.  Is it possible that the bootstrap isn't installing playwright/firefox as expected on railway?

#### chuckles — 2026-07-10T03:09:11.223Z
[check-linear] answered — staging log reviewed (@susan)

**Not a pre-fix hang.** Batch `fetch_website-9e46d3f6…` claimed 20, processed concurrently; no ERROR / INTERRUPTED / admin-kill in this slice. Firefox launch **WARNING** lines show attempt 1–2 retries (AST-853) then scrapes continue.

**Working as designed (AST-854):**
- **kaihealth_ai** — `[playwright:scrape_timeout]` at 120s → **WEBSITE_FOUND_RETRY** ✓
- ~10 companies in snippet → **HOMEPAGE_READY** ✓

**Misrouted infra (product gap — recommend fix-uat bug, not re-dispatch epic):**
| Company | Error | Landed | Should be |
| --- | --- | --- | --- |
| **preoncology_com** | `BrowserContext.new_page: Cannot read properties of undefined (reading '_page')` | **CANNOT_READ_WEBSITE** | **WEBSITE_FOUND_RETRY** |
| **careers_oracle_com** | `Page.wait_for_timeout: Page crashed` | **CANNOT_READ_WEBSITE** | **WEBSITE_FOUND_RETRY** |

**Cause:** `_is_fetch_website_infra_error` only matches `[playwright:` prefix. Roster only adds that prefix when `classify_playwright_failure` returns a class in `PLAYWRIGHT_INFRA_FAILURE_CLASSES` — **page crashed** / **undefined _page** map to `unknown`, so gazer treats them as site failures.

**Suggested fix (small):** extend classifier (or gazer infra detector) for `page crashed`, `targetclosed`, `new_page` context bugs → prefix + **WEBSITE_FOUND_RETRY** on first strike.

**Before resolve:** confirm whether batch eventually finished (log ends mid-run) or Susan killed it — either way the routing gap above is independent.

— Chuckles

#### susan — 2026-07-10T03:06:59.542Z
@chuckles It's failing on staging.  Here's the log.  Please research and comment HERE before we take action to resolve.

```
[2026-07-10 03:04:52] WARNING src.core.gazer: [kaihealth_ai] playwright infra failure failure_class=scrape_timeout batch_id=fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6
[2026-07-10 03:04:52] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 kaihealth_ai -> failed — [playwright:scrape_timeout] company scrape exceeded 120s -> WEBSITE_FOUND_RETRY
[2026-07-10 03:04:52] INFO src.core.roster: [kaihealth_ai] company state WEBSITE_FOUND -> WEBSITE_FOUND_RETRY (batch_id=fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6)
[2026-07-10 03:04:52] INFO src.core.gazer:  | summary passed=0 failed=1 errors=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-10 03:03:54] INFO src.core.roster: [tandemhealth_ai] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6)
[2026-07-10 03:03:54] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 tandemhealth_ai -> passed -> HOMEPAGE_READY (6168 chars redirect=yes nav=44 links)
[2026-07-10 03:03:54] INFO src.core.gazer:  | company_website='https://tandemhealth.ai' canonical='https://tandemhealth.ai/' homepage_chars=6168 nav_links=44
[2026-07-10 03:03:54] INFO src.core.gazer:  | summary passed=1 failed=0 errors=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-10 03:03:54] INFO src.core.roster: [thinkitive_com] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6)
[2026-07-10 03:03:54] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 thinkitive_com -> passed -> HOMEPAGE_READY (8245 chars redirect=yes nav=95 links)
[2026-07-10 03:03:54] INFO src.core.gazer:  | company_website='https://www.thinkitive.com' canonical='https://www.thinkitive.com/' homepage_chars=8245 nav_links=95
[2026-07-10 03:03:54] INFO src.core.gazer:  | summary passed=1 failed=0 errors=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-10 03:03:50] INFO src.core.roster: [barco_com] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6)
[2026-07-10 03:03:50] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 barco_com -> passed -> HOMEPAGE_READY (185 chars redirect=yes nav=2 links)
[2026-07-10 03:03:50] INFO src.core.gazer:  | company_website='https://www.barco.com' canonical='https://www.barco.com/' homepage_chars=185 nav_links=2
[2026-07-10 03:03:50] INFO src.core.gazer:  | summary passed=1 failed=0 errors=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-10 03:03:46] WARNING src.external.playwright: Firefox launch attempt 1/3 failed: TimeoutError: BrowserType.launch: Timeout 60000ms exceeded.
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-7M7E5h -juggler-pipe -silent
  - <launched> pid=3715
  - [pid=3715][err] [3715] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=3715][err] *** You are running in headless mode.

[2026-07-10 03:03:46] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6 -> batch start 1 company/companies
[2026-07-10 03:03:46] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6 -> batch start 1 company/companies
[2026-07-10 03:03:41] WARNING src.external.playwright: Firefox launch attempt 1/3 failed: TimeoutError: BrowserType.launch: Timeout 60000ms exceeded.
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-NVyYbI -juggler-pipe -silent
  - <launched> pid=774
  - [pid=774][err] [774] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=774][err] *** You are running in headless mode.
  - [pid=774][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement

[2026-07-10 03:03:41] WARNING src.external.playwright: Firefox launch attempt 1/3 failed: TimeoutError: BrowserType.launch: Timeout 60000ms exceeded.
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-ydYrQg -juggler-pipe -silent
  - <launched> pid=779
  - [pid=779][err] [779] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=779][err] *** You are running in headless mode.
  - [pid=779][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement

[2026-07-10 03:03:20] INFO src.core.gazer:  | summary passed=1 failed=0 errors=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-10 03:03:11] INFO src.core.roster: [anisolutions_com] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6)
[2026-07-10 03:03:11] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 anisolutions_com -> passed -> HOMEPAGE_READY (3429 chars redirect=yes nav=57 links)
[2026-07-10 03:03:11] INFO src.core.gazer:  | company_website='https://www.anisolutions.com' canonical='https://www.anisolutions.com/' homepage_chars=3429 nav_links=57
[2026-07-10 03:03:11] INFO src.core.gazer:  | summary passed=1 failed=0 errors=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-10 03:03:07] INFO src.core.gazer:  | summary passed=1 failed=0 errors=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-10 03:03:04] INFO src.core.roster: [aspinai_com] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6)
[2026-07-10 03:03:04] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 aspinai_com -> passed -> HOMEPAGE_READY (955 chars redirect=yes nav=528 links)
[2026-07-10 03:03:04] INFO src.core.gazer:  | company_website='https://www.aspinai.com' canonical='https://www.aspinai.com/' homepage_chars=955 nav_links=528
[2026-07-10 03:03:03] INFO src.core.roster: [dexis_com] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6)
[2026-07-10 03:03:03] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 dexis_com -> passed -> HOMEPAGE_READY (3048 chars redirect=yes nav=88 links)
[2026-07-10 03:03:03] INFO src.core.gazer:  | company_website='https://dexis.com' canonical='https://dexis.com/en-us' homepage_chars=3048 nav_links=88
[2026-07-10 03:03:03] INFO src.core.gazer:  | summary passed=1 failed=0 errors=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-10 03:02:58] WARNING src.external.playwright: Firefox launch attempt 2/3 failed: TargetClosedError: BrowserType.launch: Target page, context or browser has been closed
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-JKm8lX -juggler-pipe -silent
<launched> pid=7232
[pid=7232][err] [7232] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=7232][err] *** You are running in headless mode.
[pid=7232][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=7232][out] 
[pid=7232][out] Juggler listening to the pipe
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-JKm8lX -juggler-pipe -silent
  - <launched> pid=7232
  - [pid=7232][err] [7232] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=7232][err] *** You are running in headless mode.
  - [pid=7232][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=7232][out]
  - [pid=7232][out] Juggler listening to the pipe
  - [pid=7232] <gracefully close start>
  - [pid=7232] <kill>
  - [pid=7232] <will force kill>
  - [pid=7232] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=7232] starting temporary directories cleanup
  - [pid=7232] finished temporary directories cleanup
  - [pid=7232] <gracefully close end>

[2026-07-10 03:02:54] INFO src.core.roster: [dogtownmedia_com] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6)
[2026-07-10 03:02:54] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 dogtownmedia_com -> passed -> HOMEPAGE_READY (10075 chars redirect=yes nav=70 links)
[2026-07-10 03:02:54] INFO src.core.gazer:  | company_website='https://www.dogtownmedia.com' canonical='https://www.dogtownmedia.com/' homepage_chars=10075 nav_links=70
[2026-07-10 03:02:54] INFO src.core.gazer:  | summary passed=1 failed=0 errors=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-10 03:02:50] WARNING src.external.playwright: Firefox launch attempt 1/3 failed: Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-VAo975 -juggler-pipe -silent
<launched> pid=3602
[pid=3602][err] [3602] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=3602][err] *** You are running in headless mode.
[pid=3602][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=3602][out] Crash Annotation GraphicsCriticalError: |[0][GFX1-]: Failed to create Renderer thread: 0x8007000e (t=5.16466) [GFX1-]: Failed to create Renderer thread: 0x8007000e
[pid=3602][out] Crash Annotation GraphicsCriticalError: |[0][GFX1-]: Failed to create Renderer thread: 0x8007000e (t=5.16466) |[1][GFX1-]: Compositor thread not started (true) (t=5.16466) [GFX1-]: Compositor thread not started (true)
[pid=3602] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=3602] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-VAo975 -juggler-pipe -silent
  - <launched> pid=3602
  - [pid=3602][err] [3602] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=3602][err] *** You are running in headless mode.
  - [pid=3602][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=3602][out] Crash Annotation GraphicsCriticalError: |[0][GFX1-]: Failed to create Renderer thread: 0x8007000e (t=5.16466) [GFX1-]: Failed to create Renderer thread: 0x8007000e
  - [pid=3602][out] Crash Annotation GraphicsCriticalError: |[0][GFX1-]: Failed to create Renderer thread: 0x8007000e (t=5.16466) |[1][GFX1-]: Compositor thread not started (true) (t=5.16466) [GFX1-]: Compositor thread not started (true)
  - [pid=3602] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=3602] starting temporary directories cleanup
  - [pid=3602] <gracefully close start>
  - [pid=3602] <kill>
  - [pid=3602] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=3602] finished temporary directories cleanup
  - [pid=3602] <gracefully close end>

[2026-07-10 03:02:50] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 preoncology_com -> failed — BrowserContext.new_page: Cannot read properties of undefined (reading '_page') -> CANNOT_READ_WEBSITE
[2026-07-10 03:02:50] INFO src.core.gazer:  | company_website='https://preoncology.com'
[2026-07-10 03:02:50] INFO src.core.roster: [preoncology_com] company state WEBSITE_FOUND -> CANNOT_READ_WEBSITE (batch_id=fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6)
[2026-07-10 03:02:50] INFO src.core.gazer:  | summary passed=0 failed=1 errors=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-10 03:02:50] WARNING src.external.playwright: Firefox launch attempt 1/3 failed: TargetClosedError: BrowserType.launch: Target page, context or browser has been closed
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-qP5EsW -juggler-pipe -silent
<launched> pid=4033
[pid=4033][err] [4033] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=4033][err] *** You are running in headless mode.
[pid=4033][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=4033][out] 
[pid=4033][out] Juggler listening to the pipe
[pid=4033][err] [4033] Sandbox: SandboxReporter: thread creation failed: EAGAIN
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-qP5EsW -juggler-pipe -silent
  - <launched> pid=4033
  - [pid=4033][err] [4033] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=4033][err] *** You are running in headless mode.
  - [pid=4033][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=4033][out]
  - [pid=4033][out] Juggler listening to the pipe
  - [pid=4033][err] [4033] Sandbox: SandboxReporter: thread creation failed: EAGAIN
  - [pid=4033] <gracefully close start>
  - [pid=4033] <kill>
  - [pid=4033] <will force kill>
  - [pid=4033] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=4033] starting temporary directories cleanup
  - [pid=4033] finished temporary directories cleanup
  - [pid=4033] <gracefully close end>

[2026-07-10 03:02:50] INFO src.core.roster: [excellentwebworld_com] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6)
[2026-07-10 03:02:50] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 excellentwebworld_com -> passed -> HOMEPAGE_READY (15656 chars redirect=yes nav=166 links)
[2026-07-10 03:02:50] INFO src.core.gazer:  | company_website='https://www.excellentwebworld.com' canonical='https://www.excellentwebworld.com/' homepage_chars=15656 nav_links=166
[2026-07-10 03:02:50] WARNING src.external.playwright: Firefox launch attempt 1/3 failed: Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-YNliOB -juggler-pipe -silent
<launched> pid=4517
[pid=4517][err] [4517] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=4517][err] *** You are running in headless mode.
[pid=4517] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=4517] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-YNliOB -juggler-pipe -silent
  - <launched> pid=4517
  - [pid=4517][err] [4517] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=4517][err] *** You are running in headless mode.
  - [pid=4517] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=4517] starting temporary directories cleanup
  - [pid=4517] <gracefully close start>
  - [pid=4517] <kill>
  - [pid=4517] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=4517] finished temporary directories cleanup
  - [pid=4517] <gracefully close end>

[2026-07-10 03:02:50] INFO src.core.gazer:  | summary passed=1 failed=0 errors=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-10 03:02:50] INFO src.core.roster: [prezent_ai] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6)
[2026-07-10 03:02:50] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 prezent_ai -> passed -> HOMEPAGE_READY (8556 chars redirect=yes nav=74 links)
[2026-07-10 03:02:50] INFO src.core.gazer:  | company_website='https://www.prezent.ai' canonical='https://www.prezent.ai/' homepage_chars=8556 nav_links=74
[2026-07-10 03:02:47] WARNING src.external.playwright: check_connectivity failed failure_class=context_closed: BrowserContext.new_page: Target page, context or browser has been closed
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-zV8sU5 -juggler-pipe -silent
<launched> pid=2876
[pid=2876][err] [2876] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=2876][err] *** You are running in headless mode.
[pid=2876][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=2876][out] 
[pid=2876][out] Juggler listening to the pipe
[pid=2876][err] [Parent 2876, IPC I/O Parent] WARNING: process 6421 exited on signal 11: file ./../../../ipc/chromium/src/chrome/common/process_watcher_posix_sigchld.cc:161
[2026-07-10 03:02:47] WARNING src.external.playwright: check_connectivity failed failure_class=context_closed: Page.goto: Target page, context or browser has been closed
Call log:
  - navigating to "https://www.google.com/", waiting until "commit"

[2026-07-10 03:02:46] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6 -> batch start 1 company/companies
[2026-07-10 03:02:46] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6 -> batch start 1 company/companies
[2026-07-10 03:02:46] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6 -> batch start 1 company/companies
[2026-07-10 03:02:46] WARNING src.external.playwright: playwright batch session recover failure_class=context_closed reason=BrowserContext.new_page: Target page, context or browser has been closed
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-ONE0hN -juggler-pipe -silent
<launched> pid=3012
[pid=3012][err] [3012] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=3012][err] *** You are running in headless mode.
[pid=3012][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=3012][out] 
[pid=3012][out] Juggler listening to the pipe
[2026-07-10 03:02:46] WARNING src.external.playwright: playwright batch session recover failure_class=context_closed reason=Page.goto: Target page, context or browser has been closed
Call log:
  - navigating to "https://www.prezent.ai/", waiting until "load"

[2026-07-10 03:02:46] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 careers_oracle_com -> failed — Page.wait_for_timeout: Page crashed -> CANNOT_READ_WEBSITE
[2026-07-10 03:02:46] INFO src.core.gazer:  | company_website='https://www.oracle.com'
[2026-07-10 03:02:46] INFO src.core.roster: [careers_oracle_com] company state WEBSITE_FOUND -> CANNOT_READ_WEBSITE (batch_id=fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6)
[2026-07-10 03:02:46] WARNING src.external.playwright: check_connectivity failed failure_class=context_closed: BrowserContext.new_page: Target page, context or browser has been closed
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-AF2DoP -juggler-pipe -silent
<launched> pid=746
[pid=746][err] [746] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=746][err] *** You are running in headless mode.
[pid=746][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=746][out] 
[pid=746][out] Juggler listening to the pipe
[pid=746][err] [746] Sandbox: SandboxBroker: thread creation failed (1 brokers): EAGAIN
[2026-07-10 03:02:46] INFO src.core.gazer:  | summary passed=0 failed=1 errors=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-10 03:02:46] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6 -> batch start 1 company/companies
[2026-07-10 03:02:46] WARNING src.external.playwright: check_connectivity failed failure_class=unknown: BrowserContext.new_page: Cannot read properties of undefined (reading '_page')
[2026-07-10 03:02:42] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6 -> batch start 1 company/companies
[2026-07-10 03:02:42] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6 -> batch start 1 company/companies
[2026-07-10 03:02:41] WARNING src.external.playwright: Firefox launch attempt 1/3 failed: TargetClosedError: BrowserType.launch: Target page, context or browser has been closed
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-OoCqCs -juggler-pipe -silent
<launched> pid=896
[pid=896][err] [896] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=896][err] *** You are running in headless mode.
[pid=896][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=896][out] Crash Annotation GraphicsCriticalError: |[0][GFX1-]: Failed to create Renderer thread: 0x8007000e (t=0.96526) [GFX1-]: Failed to create Renderer thread: 0x8007000e
[pid=896][out] Crash Annotation GraphicsCriticalError: |[0][GFX1-]: Failed to create Renderer thread: 0x8007000e (t=0.96526) |[1][GFX1-]: Compositor thread not started (true) (t=0.96526) [GFX1-]: Compositor thread not started (true)
[pid=896][out] 
[pid=896][out] Juggler listening to the pipe
[pid=896][err] [896] Sandbox: SandboxReporter: thread creation failed: EAGAIN
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-OoCqCs -juggler-pipe -silent
  - <launched> pid=896
  - [pid=896][err] [896] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=896][err] *** You are running in headless mode.
  - [pid=896][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=896][out] Crash Annotation GraphicsCriticalError: |[0][GFX1-]: Failed to create Renderer thread: 0x8007000e (t=0.96526) [GFX1-]: Failed to create Renderer thread: 0x8007000e
  - [pid=896][out] Crash Annotation GraphicsCriticalError: |[0][GFX1-]: Failed to create Renderer thread: 0x8007000e (t=0.96526) |[1][GFX1-]: Compositor thread not started (true) (t=0.96526) [GFX1-]: Compositor thread not started (true)
  - [pid=896][out]
  - [pid=896][out] Juggler listening to the pipe
  - [pid=896][err] [896] Sandbox: SandboxReporter: thread creation failed: EAGAIN
  - [pid=896] <gracefully close start>
  - [pid=896] <kill>
  - [pid=896] <will force kill>
  - [pid=896] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=896] starting temporary directories cleanup
  - [pid=896] finished temporary directories cleanup
  - [pid=896] <gracefully close end>

[2026-07-10 03:02:41] WARNING src.external.playwright: Firefox launch attempt 1/3 failed: Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-x72JgH -juggler-pipe -silent
<launched> pid=901
[pid=901][err] [901] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=901][err] *** You are running in headless mode.
[pid=901] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=901] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-x72JgH -juggler-pipe -silent
  - <launched> pid=901
  - [pid=901][err] [901] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=901][err] *** You are running in headless mode.
  - [pid=901] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=901] starting temporary directories cleanup
  - [pid=901] <gracefully close start>
  - [pid=901] <kill>
  - [pid=901] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=901] finished temporary directories cleanup
  - [pid=901] <gracefully close end>

[2026-07-10 03:02:41] WARNING src.external.playwright: Firefox launch attempt 1/3 failed: Error: BrowserType.launch: Failed to launch the browser process.
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-haKWMS -juggler-pipe -silent
<launched> pid=838
[pid=838][err] [838] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=838][err] *** You are running in headless mode.
[pid=838][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=838] <process did exit: exitCode=null, signal=SIGSEGV>
[pid=838] starting temporary directories cleanup
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-haKWMS -juggler-pipe -silent
  - <launched> pid=838
  - [pid=838][err] [838] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=838][err] *** You are running in headless mode.
  - [pid=838][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=838] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=838] starting temporary directories cleanup
  - [pid=838] <gracefully close start>
  - [pid=838] <kill>
  - [pid=838] <skipped force kill spawnedProcess.killed=false processClosed=true>
  - [pid=838] finished temporary directories cleanup
  - [pid=838] <gracefully close end>

[2026-07-10 03:02:41] WARNING src.external.playwright: Firefox launch attempt 1/3 failed: TargetClosedError: BrowserType.launch: Target page, context or browser has been closed
Browser logs:

<launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-EIbXm7 -juggler-pipe -silent
<launched> pid=788
[pid=788][err] [788] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
[pid=788][err] *** You are running in headless mode.
[pid=788][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
[pid=788][out] 
[pid=788][out] Juggler listening to the pipe
[pid=788][err] [788] Sandbox: SandboxReporter: thread creation failed: EAGAIN
Call log:
  - <launching> /app/.browsers/firefox-1532/firefox/firefox -no-remote -headless -profile /tmp/playwright_firefoxdev_profile-EIbXm7 -juggler-pipe -silent
  - <launched> pid=788
  - [pid=788][err] [788] Sandbox: CanCreateUserNamespace() clone() failure: EACCES
  - [pid=788][err] *** You are running in headless mode.
  - [pid=788][err] JavaScript warning: resource://services-settings/Utils.sys.mjs, line 119: unreachable code after return statement
  - [pid=788][out]
  - [pid=788][out] Juggler listening to the pipe
  - [pid=788][err] [788] Sandbox: SandboxReporter: thread creation failed: EAGAIN
  - [pid=788] <gracefully close start>
  - [pid=788] <kill>
  - [pid=788] <will force kill>
  - [pid=788] <process did exit: exitCode=null, signal=SIGSEGV>
  - [pid=788] starting temporary directories cleanup
  - [pid=788] finished temporary directories cleanup
  - [pid=788] <gracefully close end>

[2026-07-10 03:02:41] WARNING src.external.playwright: check_connectivity failed failure_class=unknown: Page.goto: Page crashed
Call log:
  - navigating to "https://www.google.com/", waiting until "commit"

[2026-07-10 03:02:41] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6 -> batch start 1 company/companies
[2026-07-10 03:02:41] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6 -> batch start 1 company/companies
[2026-07-10 03:02:41] WARNING src.external.playwright: check_connectivity failed failure_class=unknown: BrowserContext.new_page: Cannot read properties of undefined (reading '_page')
[2026-07-10 03:02:41] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6 -> batch start 1 company/companies
[2026-07-10 03:02:41] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6 -> batch start 1 company/companies
[2026-07-10 03:02:36] INFO src.core.roster: [wolterskluwer_com] company state WEBSITE_FOUND -> HOMEPAGE_READY (batch_id=fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6)
[2026-07-10 03:02:36] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 wolterskluwer_com -> passed -> HOMEPAGE_READY (193 chars redirect=yes nav=2 links)
[2026-07-10 03:02:36] INFO src.core.gazer:  | company_website='https://www.wolterskluwer.com' canonical='https://www.wolterskluwer.com/' homepage_chars=193 nav_links=2
[2026-07-10 03:02:36] INFO src.core.gazer:  | summary passed=1 failed=0 errors=0 total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
[2026-07-10 03:02:32] INFO src.core.gazer: gazer.fetch_website_batch index 1/1 fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6 -> batch start 1 company/companies
[2026-07-10 03:02:31] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-10 03:02:31] INFO src.core.dispatcher: dispatcher._run_unified index 10/20 dexis_com -> claimed
[2026-07-10 03:02:31] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-10 03:02:31] INFO src.core.dispatcher: dispatcher._run_unified index 11/20 dogtownmedia_com -> claimed
[2026-07-10 03:02:31] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-10 03:02:31] INFO src.core.dispatcher: dispatcher._run_unified index 12/20 careers_oracle_com -> claimed
[2026-07-10 03:02:31] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-10 03:02:31] INFO src.core.dispatcher: dispatcher._run_unified index 13/20 preoncology_com -> claimed
[2026-07-10 03:02:31] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-10 03:02:31] INFO src.core.dispatcher: dispatcher._run_unified index 14/20 aspinai_com -> claimed
[2026-07-10 03:02:31] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-10 03:02:31] INFO src.core.dispatcher: dispatcher._run_unified index 15/20 ioss_co -> claimed
[2026-07-10 03:02:31] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-10 03:02:31] INFO src.core.dispatcher: dispatcher._run_unified index 16/20 kaihealth_ai -> claimed
[2026-07-10 03:02:31] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-10 03:02:31] INFO src.core.dispatcher: dispatcher._run_unified index 17/20 blog_doximity_com -> claimed
[2026-07-10 03:02:31] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-10 03:02:31] INFO src.core.dispatcher: dispatcher._run_unified index 18/20 excellentwebworld_com -> claimed
[2026-07-10 03:02:31] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-10 03:02:31] INFO src.core.dispatcher: dispatcher._run_unified index 19/20 medicaltranscriptionservicecompany_com -> claimed
[2026-07-10 03:02:31] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-10 03:02:31] INFO src.core.dispatcher: dispatcher._run_unified index 20/20 prezent_ai -> claimed
[2026-07-10 03:02:31] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-10 03:02:30] INFO dispatch.scheduler: Dispatching fetch_website — 85 available, batch fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6
[2026-07-10 03:02:30] INFO src.core.dispatcher: dispatcher._run_dispatch_loop index 1/1 fetch_website -> loop iteration 1 starting
[2026-07-10 03:02:30] INFO src.core.dispatcher:  | available=85 effective_min=1 max_runs=0 draining=False entity_batch_id=fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6
[2026-07-10 03:02:30] INFO src.core.dispatcher: dispatcher._run_task index 1/1 fetch_website -> running batch
[2026-07-10 03:02:30] INFO src.core.dispatcher:  | batch_size=20 batch_id=fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6 entity_type='company' trigger_state='WEBSITE_FOUND'
[2026-07-10 03:02:30] INFO src.core.dispatcher: dispatcher._run_unified index 1/1 company/WEBSITE_FOUND -> claimed 20 entity/entities
[2026-07-10 03:02:30] INFO src.core.dispatcher:  | task_key=fetch_website batch_id=fetch_website-9e46d3f6-e500-483e-8594-2e1f699d2ed6 batch_call_mode=False dispatch batch_size=20 claim_cap=None claim_states=['WEBSITE_FOUND', 'WEBSITE_FOUND_RETRY']
[2026-07-10 03:02:30] INFO src.core.dispatcher: dispatcher._run_unified index 1/20 wolterskluwer_com -> claimed
[2026-07-10 03:02:30] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-10 03:02:30] INFO src.core.dispatcher: dispatcher._run_unified index 2/20 tandemhealth_ai -> claimed
[2026-07-10 03:02:30] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-10 03:02:30] INFO src.core.dispatcher: dispatcher._run_unified index 3/20 anisolutions_com -> claimed
[2026-07-10 03:02:30] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-10 03:02:30] INFO src.core.dispatcher: dispatcher._run_unified index 4/20 dedalus_wd3_myworkdayjobs_com -> claimed
[2026-07-10 03:02:30] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-10 03:02:30] INFO src.core.dispatcher: dispatcher._run_unified index 5/20 verahealth_ai -> claimed
[2026-07-10 03:02:30] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-10 03:02:30] INFO src.core.dispatcher: dispatcher._run_unified index 6/20 thinkitive_com -> claimed
[2026-07-10 03:02:30] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-10 03:02:30] INFO src.core.dispatcher: dispatcher._run_unified index 7/20 barco_com -> claimed
[2026-07-10 03:02:30] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-10 03:02:30] INFO src.core.dispatcher: dispatcher._run_unified index 8/20 bestpracticesoftware_com -> claimed
[2026-07-10 03:02:30] INFO src.core.dispatcher:  | entity_type=company trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND'
[2026-07-10 03:02:30] INFO src.core.dispatcher: dispatcher._run_unified index 9/20 chetu_com -> claimed
```

#### chuckles — 2026-07-10T02:09:28.387Z
@susan

1. Should this epic cover **fetch_website** only, or should **AST-851** (gaze) browser-on-Railway failures be one shared infrastructure parent with two children?
2. For companies from batch `fetch_website-f1cbd011-7cdb-4774-b506-eb49e3b1e743` (40/184 processed, admin-killed 2026-07-10): is automatic re-eligibility on deploy sufficient, or do you want an explicit one-time recovery pass for stuck rows?
3. When browser infra fails for a specific company, should the company land in **WEBSITE_FOUND_RETRY** (retry later) vs **CANNOT_READ_WEBSITE** (terminal for site read failure) — or is the current mixed behavior acceptable once batches no longer hang?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._

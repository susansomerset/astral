# AST-2022 — New Fetch task for RELATIVE_JOB_LINK

<!-- linear-archive: AST-2022 archived 2026-10-16 -->

## Linear archive (AST-2022)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2022/new-fetch-task-for-relative-job-link  
**Status at archive:** Archive  
**Project:** Astral Tracker  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Some company job boards list jobs with relative links (`/jobs/123`, `?gh_jid=…`). Today `qualify_job_listings` throws those jobs away: a passing job with a non-`http` link raises `InvalidJobLinkError` and lands in the batch fail state, so we lose good matches just because the board didn't print a full URL. This epic keeps those jobs. It parks them in a new job state, `RELATIVE_JOB_LINK`, and has a Telescope fetch task open the company's job list page, click that link like a person would, and record the real destination URL plus the job page's visible text. If the destination is bot-blocked, the job moves to `BOT_BLOCKED` with the resolved URL saved, so the candidate can open it themselves. It's the job-track version of the meteorite `SCRAPE_LINK` hop.

## Functional scope

1. **Keep relative-link jobs.** When `qualify_job_listings` passes a job whose link isn't empty but also isn't absolute `http(s)`, the job is initialized as usual (relative link stored as-is) and goes to `RELATIVE_JOB_LINK` instead of raising. A blank link is still a fail, exactly as today. It never becomes `RELATIVE_JOB_LINK`.
2. **Click-through fetch.** A new Telescope fetch task claims `RELATIVE_JOB_LINK` jobs per candidate. For each one it loads the company's job list page (`company.job_site`), clicks the anchor whose `href` attribute **exactly** equals the job's stored relative link (no fallback matching), and captures the destination's final URL and visible text.
3. **Resolved link saved.** Whenever the click reaches a destination page (any outcome below), the job's `job_link` is replaced with that absolute final URL.
4. **Same JD gates as** `fetch_jd`**.** The captured text goes through the same prune, minimum-length, and closed/missing/cookie/blocked checks `fetch_jd` uses. Pass: the JD text is saved and the job moves to `JD_READY` (it skips `PASSED_JOBLIST` / `fetch_jd`, since the text is already there). Blocked: `BOT_BLOCKED`. Closed, missing, cookie wall, or too short: the matching `JD_SCRAPE_FAIL*` state, same as `fetch_jd`.
5. **Click-target failure.** If Telescope can't find or click the element, or errors out, the job goes to a new skipped state, `RELATIVE_LINK_FAIL`, and `job_link` stays relative. A bulk retry from the Skipped view sends it back to `RELATIVE_JOB_LINK`.
6. **Telescope click-then-capture.** Telescope gets a new optional request option: after load, cookie dismissal, and expand, click the anchor whose `href` matches a given value, follow the navigation (same tab or new tab), then capture on the destination as usual. It stays generic: no job or company logic on the service.
7. **Operator surfaces.** `RELATIVE_JOB_LINK` appears in the Jobs processing sections, `RELATIVE_LINK_FAIL` appears in the Jobs skipped sections, and the new task key appears in the Scheduled Actions (dispatch task) picker as a `job` / `RELATIVE_JOB_LINK` task.

**Out of scope:** the `qualify_job_listings` prompt in `data/admin/agent_task.json`. Susan will edit it herself so the agent stops trying to complete relative links and passes them through as-is.

## Pipeline flow

| State (or trigger) | Dispatch `task_key` / handler | Next state(s) |
| -- | -- | -- |
| `NEW` | `qualify_job_listings` (pass + non-empty, non-`http` link) | `RELATIVE_JOB_LINK` |
| `NEW` | `qualify_job_listings` (pass + `http` link) | `PASSED_JOBLIST` (unchanged) |
| `NEW` | `qualify_job_listings` (pass + blank link) | fail, as today (unchanged) |
| `RELATIVE_JOB_LINK` | new Telescope fetch task (click-through on `company.job_site`) | `JD_READY` (JD saved, `job_link` resolved) · `BOT_BLOCKED` (`job_link` resolved) · `JD_SCRAPE_FAIL` / `_COOKIE` / `_MISSING` / `_CLOSED` (`job_link` resolved) · `RELATIVE_LINK_FAIL` (click target not found / Telescope error, `job_link` still relative) |
| `RELATIVE_LINK_FAIL` | Skipped-view bulk retry (operator) | `RELATIVE_JOB_LINK` |
| `JD_READY` | `evaluate_jd` (unchanged) | existing chain |

The chain ends where it meets the existing pipeline: `JD_READY` (evaluate_jd) or a skipped/failed state already in `SKIPPED_STATES`.

## Component scope

* `service/telescope/scrape.py`: **modified**. The request model takes the new optional click option, and the scrape flow runs the click before capture.
* `service/telescope/interact.py`: **modified**. New click-and-follow interaction (find anchor by `href`, click, follow same-tab or new-tab navigation, wait for the destination).
* `src/external/telescope.py`: **modified**. Platform client passes the click option to the service and exposes a public call that returns the destination's final URL and visible text.
* `service/telescope/worker.py`: **modified**. Retry policy treats the new click-target error class as non-retried.
* `src/utils/config.py`: **modified**. New job state, prior-state edits, the new fetch task's config block, dispatch trigger-state / entity-type rules, the `qualify_job_listings` routing key, and UI section labels.
* `data/admin/agent_task.json`: **modified**. New `telescope`-agent row for the fetch task in the Job Review group, mirroring `fetch_jd`, so it appears in the dispatch picker.
* `src/core/gazer.py`: **modified**. New batch runner for the click-through fetch, sharing `fetch_jd_batch`'s JD gates rather than copying them.
* `src/core/consult.py`: **modified**. `qualify_job_listings` routes relative-link passes to the new state, and job dispatch routes the new task key to the gazer runner.

## Technical scope

* `service/telescope/scrape.py`: modified request model, with a new optional field carrying the `href` to click (absent means behavior is unchanged). Modified scrape run, which calls the click step after load / cookies / expand and before capture, so `final_url` and captured fields describe the destination. A missing click target fails the job with a distinct, non-retried error class.
* `service/telescope/interact.py`: new click function. It locates an anchor by exact `href` attribute, clicks it, follows either same-tab navigation or a new-tab popup, and waits for the destination to load. It reuses the existing navigation timeout settings; no new caps.
* `src/external/telescope.py`: modified request builder, which forwards the click option. New public function: given a list-page URL and a relative `href`, return the destination final URL and visible text, raising on a click-target or service failure.
* `service/telescope/worker.py`: modified `Worker._retry_delay`, which treats the new click-target error class as non-retried (alongside `bad_request`).
* `src/utils/config.py`:
  * New `JOB_STATES` entry `RELATIVE_JOB_LINK` (prior: `NEW` only; `NEW_RETRY` resolves through its base). `RELATIVE_LINK_FAIL` is in its priors too, for bulk retry.
  * New `JOB_STATES` entry `RELATIVE_LINK_FAIL` (prior: `RELATIVE_JOB_LINK`). It's added to `SKIPPED_STATES`, the skipped section order and labels, and the skipped bulk-retry map (→ `RELATIVE_JOB_LINK`).
  * `RELATIVE_JOB_LINK` added to the priors of `JD_READY`, `BOT_BLOCKED`, and the four `JD_SCRAPE_FAIL*` states.
  * New `GAZER_CONFIG` block for the fetch task (trigger state, pass / fail / error states), plus matching branches in the dispatch trigger-state and entity-type rules.
  * New `qualify_job_listings` config key naming the relative-link destination state.
  * `JOBS_PROCESSING_UI_SECTIONS` row for `RELATIVE_JOB_LINK`.
* `data/admin/agent_task.json`: new row (`agent_id` `telescope`, Job Review group, sequenced after `fetch_jd`).
* `src/core/gazer.py`: new batch runner. For each claimed job it calls the Telescope click-through with the job's `job_site` and relative `job_link`, saves the resolved `job_link`, runs the shared JD gates, saves the JD, and transitions. The JD gate logic currently inline in `fetch_jd_batch` moves into a helper both runners call.
* `src/core/consult.py`:
  * In `qualify_job_listings`, `process()` changes: a non-empty, non-`http` link initializes the job and transitions to the configured relative-link state instead of raising `InvalidJobLinkError`. The empty link still raises.
  * The job dispatch router gets a new `task_key` branch calling the gazer runner.

## Architectural definition

**Patterns to reuse**

* `patt.entity.batch-processing`: the new fetch claims `RELATIVE_JOB_LINK` jobs under one `batch_id` and processes and releases only those rows, the same as `fetch_jd`. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-processing.md>)
* `patt.entity.batch-criteria`: batch size and cadence come from the `dispatch_task` row, with only a config fallback default. Nothing is hardcoded in the runner. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-criteria.md>)

**New patterns proposed:** none. The Telescope click option is an extension of the existing per-URL interaction options (`expand`, `wait_ready`), not a new shape.

**Applicable statutes**

* `astral.dispatch.entity-state-bound`: the new task's `dispatch_task` rows are `entity_type='job'`, `trigger_state='RELATIVE_JOB_LINK'`, and the runner claims by exactly that pair. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.dispatch.entity-state-bound.md>)
* `astral.batch.claim-process-release`: pool claim, `batch_id` lock, release in `finally`. No select-by-state shortcut. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.batch.claim-process-release.md>)
* `stat.logging.debug`: the Telescope call and runner joints log params in and response out at debug. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)
* `stat.logging.info.entity`: each job reaching `JD_READY` from the new runner logs the entity success line. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md>)
* `stat.logging.warning`: blocked, failed-gate, and click-target misses are configured fail paths and log a warning, not an exception. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md>)
* `stat.logging.error`: an unexpected exception in the runner is logged once by the handler that decides the outcome. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>)

## Acceptance criteria

1. **Registry.** The following command exits 0. Fail: `KeyError` or `AssertionError`, or `VALID_TITLE` appears in either new state's priors.

   ```
   python -c "from src.utils.config import JOB_STATES as J, SKIPPED_STATES as S, JOBS_SKIPPED_BULK_RETRY_TO_STATE as R; assert set(J['RELATIVE_JOB_LINK']['prior_states'])=={'NEW','RELATIVE_LINK_FAIL'}; assert J['RELATIVE_LINK_FAIL']['prior_states']==['RELATIVE_JOB_LINK']; assert 'RELATIVE_LINK_FAIL' in S and R['RELATIVE_LINK_FAIL']=='RELATIVE_JOB_LINK'; assert all('RELATIVE_JOB_LINK' in J[s]['prior_states'] for s in ('JD_READY','BOT_BLOCKED','JD_SCRAPE_FAIL','JD_SCRAPE_FAIL_COOKIE','JD_SCRAPE_FAIL_MISSING','JD_SCRAPE_FAIL_CLOSED'))"
   ```
2. **Qualify keeps relative links.** A passing `qualify_job_listings` response with `job_link: "/jobs/123"` leaves that job in `RELATIVE_JOB_LINK` with `job_link == "/jobs/123"`. Fail: the job lands in the batch fail / error state, or `InvalidJobLinkError` appears in the log for it. A blank `job_link` fails exactly as today (`InvalidJobLinkError` → the batch fail destination). Fail: it reaches `RELATIVE_JOB_LINK`.
3. **Negative check (no second raise path).** `rg -n 'raise InvalidJobLinkError' src/core/consult.py` returns exactly one hit, and that hit sits under an empty-link condition. Fail: zero hits (empty-link guard removed) or a hit still covering non-empty relative links.
4. **Telescope click.** `POST` to the Telescope service with a list-page `url`, the click option set to an `href` present on that page, and `fields: ["text"]` returns a `final_url` that is not the list-page URL and `text` from the destination. With an `href` not on the page, it returns the distinct click-target error class and no retry. Fail: `final_url` equals the list page, text is the list page's, or a missing target times out or retries. Omitting the option gives a byte-identical response shape to today's (`test_*` for existing scrape requests unchanged and green).
5. **Runner outcomes.** With the Telescope client stubbed:
   * ok text → job `JD_READY`, `job_data.job_description` saved, `job_link` equals the stubbed absolute `final_url`;
   * blocked text → `BOT_BLOCKED` and `job_link` resolved;
   * closed text → `JD_SCRAPE_FAIL_CLOSED` and `job_link` resolved;
   * click-target error → `RELATIVE_LINK_FAIL`, `job_link` still relative.

   Fail: any job in a different state, or `job_link` still relative after a destination was reached.
6. **Shared gates, not copied.** `fetch_jd_batch` and the new runner both call the same JD gate helper (`rg` of that helper's name in `src/core/gazer.py` shows the definition plus one call in each runner). Fail: gate logic (`_prune_jd`, the `min_chars` check, `_classify_jd` → `_JD_ERROR_STATES`) appears inline in both runners.
7. **Dispatch binding.** The Scheduled Actions picker (`GET /admin/dispatch_tasks/task_keys`) lists the new task key with `entity_type: "job"` and `trigger_state: "RELATIVE_JOB_LINK"`. A manual run claims only `RELATIVE_JOB_LINK` jobs for that candidate, and every claimed job ends with `batch_id` NULL. Fail: the key is missing, the pair is wrong, other states are claimed, or a lock is left behind.
8. **UI.** The Jobs processing view shows a labelled `RELATIVE_JOB_LINK` section, and the Jobs skipped view shows a labelled `RELATIVE_LINK_FAIL` section with bulk retry, whenever such jobs exist. A bulk retry there moves the jobs to `RELATIVE_JOB_LINK`. Fail: a section is missing, the jobs are invisible, or retry lands anywhere else.

## Open questions

none

## Proposed child tickets

#### 1!: **Telescope click-then-capture - Hedy**

Telescope learns to click an anchor by `href` on the loaded page, follow it (same tab or new tab), and capture on the destination. The platform client exposes that as one call returning final URL + visible text. Requests without the option behave exactly as today. Does **not** touch job states, dispatch, or the runner (#2, #3). Telescope service needs a redeploy after merge.
**Citations:** `stat.logging.debug`, `stat.logging.warning`, `stat.logging.error`.
**Scope:**

* `service/telescope/scrape.py`: modified request model, with a new optional field carrying the `href` to click (absent means behavior is unchanged). Modified scrape run, which calls the click step after load / cookies / expand and before capture, so `final_url` and captured fields describe the destination. A missing click target fails the job with a distinct, non-retried error class.
* `service/telescope/interact.py`: new click function. It locates an anchor by exact `href` attribute, clicks it, follows either same-tab navigation or a new-tab popup, and waits for the destination to load. It reuses the existing navigation timeout settings; no new caps.
* `src/external/telescope.py`: modified request builder, which forwards the click option. New public function: given a list-page URL and a relative `href`, return the destination final URL and visible text, raising on a click-target or service failure.
* `service/telescope/worker.py`: modified `Worker._retry_delay`, which treats the new click-target error class as non-retried (alongside `bad_request`).

Estimate: 3

#### 2!: **RELATIVE_JOB_LINK state and task registration - Ada**

The job state registry, the fetch task's config and dispatch binding, the agent_task catalog row, and UI labels. After this, `RELATIVE_JOB_LINK` and `RELATIVE_LINK_FAIL` are legal job states (the latter skipped and bulk-retryable), and the new task key shows in Scheduled Actions as `job` / `RELATIVE_JOB_LINK`. Does **not** route qualify output or run the fetch (#3).
**Citations:** `astral.dispatch.entity-state-bound`, `patt.entity.batch-criteria`.
**Scope:**

* `src/utils/config.py`:
  * New `JOB_STATES` entry `RELATIVE_JOB_LINK` (prior: `NEW` only; `NEW_RETRY` resolves through its base). `RELATIVE_LINK_FAIL` is in its priors too, for bulk retry.
  * New `JOB_STATES` entry `RELATIVE_LINK_FAIL` (prior: `RELATIVE_JOB_LINK`). It's added to `SKIPPED_STATES`, the skipped section order and labels, and the skipped bulk-retry map (→ `RELATIVE_JOB_LINK`).
  * `RELATIVE_JOB_LINK` added to the priors of `JD_READY`, `BOT_BLOCKED`, and the four `JD_SCRAPE_FAIL*` states.
  * New `GAZER_CONFIG` block for the fetch task (trigger state, pass / fail / error states), plus matching branches in the dispatch trigger-state and entity-type rules.
  * New `qualify_job_listings` config key naming the relative-link destination state.
  * `JOBS_PROCESSING_UI_SECTIONS` row for `RELATIVE_JOB_LINK`.
* `data/admin/agent_task.json`: new row (`agent_id` `telescope`, Job Review group, sequenced after `fetch_jd`).

Estimate: 2

#### 3: **Qualify routing and click-through runner - Katherine**

After #1 and #2. `qualify_job_listings` sends relative-link passes to `RELATIVE_JOB_LINK`. The new gazer runner claims them, calls the Telescope click-through, saves the resolved link and JD, and transitions per the Pipeline flow. `fetch_jd_batch`'s JD gates move into a shared helper both runners call. The dispatch router wires the new task key to the runner.
**Citations:** `patt.entity.batch-processing`, `astral.batch.claim-process-release`, `stat.logging.debug`, `stat.logging.info.entity`, `stat.logging.warning`, `stat.logging.error`.
**Scope:**

* `src/core/gazer.py`: new batch runner. For each claimed job it calls the Telescope click-through with the job's `job_site` and relative `job_link`, saves the resolved `job_link`, runs the shared JD gates, saves the JD, and transitions. The JD gate logic currently inline in `fetch_jd_batch` moves into a helper both runners call.
* `src/core/consult.py`:
  * In `qualify_job_listings`, `process()` changes: a non-empty, non-`http` link initializes the job and transitions to the configured relative-link state instead of raising `InvalidJobLinkError`. The empty link still raises.
  * The job dispatch router gets a new `task_key` branch calling the gazer runner.

Estimate: 3

**Monolith check:** 7 functional capabilities across 3 children (service, registry, core). No single-child shortcut.
**Scope partition check:** every Component scope file is claimed by exactly one child: #1 has the three Telescope files, #2 has `config.py` and `agent_task.json`, #3 has `gazer.py` and `consult.py`.

---

## Original brief

Let's add a state for job that is "RELATIVE_JOB_LINK" so that we can call telescope to open the job list page and click on the relative link and capture the destination url as well as the visible text on the job page (while it's there, might as well) and if the link is blocked, update the job state to "BOT_BLOCKED" with the resolved link so that the candidate can try navigating to it themselves.

This would be similar to the "SCRAPE_LINK" state for meteorites.

### Comments

#### chuckles — 2026-10-08T04:12:21.463Z
AST-2025 REVIEW — Radia fix-now: qualify batch tally counts RELATIVE_JOB_LINK passes as failed; recalling Katherine for resolve-child.

#### chuckles — 2026-10-08T02:41:31.159Z
AST-2024 gated on [AST-2027](https://linear.app/astralcareermatch/issue/AST-2027) — needs ruff install approval or lint waiver before Ada commits Stage 1.

#### ada — 2026-10-08T02:40:41.249Z
🛑 Stage 1 blocked: AST-2024 lint tool missing
Step: Stage 1 step 8 — "Lint per Notes" (`ruff check src/utils/config.py`)
Issue: `ruff` is not installed in the epic worktree environment (no `flake8` / `pyflakes` either). Plan says stop rather than skip lint or substitute a linter. Stage 1 edits are in place and pass compile, import, AC1 and the manifest check — uncommitted on `sub/AST-2022/AST-2024-relative-job-link-state`.
Proposed resolutions: (1) approve `pip install --user ruff`, then lint + commit; (2) waive lint for this ticket (compile + import + AC checks only); (3) name a different linter.

#### chuckles — 2026-10-08T00:36:43.325Z
@susan

1. **Click match rule.** Right now the click targets the anchor whose `href` exactly equals the stored relative link. Is exact-href enough, or do you want a fallback? Two options would be matching on link text equal to the job title, or skipping the click and just joining the relative link onto `job_site`.
2. **When the click target can't be found** (or Telescope errors out), where should the job go?
   * **(a)** A new failure state, for example `RELATIVE_LINK_FAIL`, with bulk-retry back to `RELATIVE_JOB_LINK`. This is my pick.
   * **(b)** The existing `JD_SCRAPE_FAIL`. Its retry sends jobs to `PASSED_JOBLIST`, where `fetch_jd` can't use a relative link, so the retry would just fail again.
3. **After a successful click**, the job page text is already in hand. Should the job go straight to `JD_READY` (after the same JD checks `fetch_jd` runs)? Or should it land on `PASSED_JOBLIST` with only the resolved link and let `fetch_jd` scrape the page again?

---

_Implementation detail may live in git history on `origin/dev`._

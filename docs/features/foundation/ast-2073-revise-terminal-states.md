# AST-2073 — Revise terminal states

<!-- linear-archive: AST-2073 archived 2026-10-16 -->

## Linear archive (AST-2073)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2073/revise-terminal-states  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 8  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-2102

### Description

## Purpose

Terminal failure states grew one ticket at a time, so the registries now mix four spellings: `FAILED_TECHNICAL_*`, `ERROR_*`, `*_ERROR`, and catch-alls like `NO_WEBSITE`, `NO_JOBLIST`, `JOBSITE_SCRAPE_ISSUE`, and `CANNOT_READ_WEBSITE`. Some of these silently lump a bot wall in with "nothing was there". As a result, nobody can tell from a state name which task failed or why, and bot-blocked pages, which a candidate could open for us, get filed with dead ends. This epic gives every entity type (job, company, candidate, meteorite) one readable grammar, keyed on the task that failed (uppercased `task_key`):

* `ERROR_<TASK_KEY>_<condition>` for a terminal failure with a known cause, or bare `ERROR_<TASK_KEY>` when the cause is general.
* `BOT_BLOCKED_<TASK_KEY>` for bot walls.
* `JD_SCRAPE_FAIL_<condition>` for expired links (the posting is closed or gone).

It also splits bot walls out of the catch-all states, so they can be recovered by asking the candidate to open the page.

## Functional scope

 1. **One error grammar.** Every terminal failure state on every entity registry is named `ERROR_<TASK_KEY>_<condition>` when the code knows the specific cause, or bare `ERROR_<TASK_KEY>` when it doesn't (for example, an agent call or response failed after its one retry, an empty-token data defect, or an unexpected exception). There is no `TECHNICAL` catch-all suffix. `<TASK_KEY>` is the uppercased dispatch `task_key` whose run wrote the failure. For a daisy-chain hop, that is the hop that failed: one error per hop. The condition comes from a closed vocabulary in config: `UNREADABLE` (fetched, but no usable content), `COOKIE`, `NOT_FOUND`, `NO_JOBLIST`, `NO_JOBLIST_LINKS`, `NO_SELECTION`, `NO_CULTURE_LINKS`, `NO_WEBSITE_CONTENT`, `UNPARSEABLE`, `CLICK`. Two retired names never collapse into one new name unless the Pipeline flow table says so. Names that already conform (`ERROR_QUALIFY_JOB_LISTINGS`, `ERROR_EVALUATE_JD`, `ERROR_GAZE`) keep their names and are not in the retired-name map.
 2. **One bot grammar.** Every bot or challenge-wall outcome is named `BOT_BLOCKED_<TASK_KEY>`, not `ERROR_*`. The bare universal `BOT_BLOCKED` state is retired on job, company, and meteorite registries.
 3. **Expired links are** `JD_SCRAPE_FAIL_<condition>`**.** A link whose page is gone (404) or says the job is closed lands on `JD_SCRAPE_FAIL_MISSING` / `JD_SCRAPE_FAIL_CLOSED`. That is the job track's existing pair, and fetch_jd and fetch_relative_jd keep using it unchanged. The meteorite staging row's `LINK_EXPIRED` is retired and split onto the same two names by the page status it already detects.
 4. **Catch-alls split.** These fetch tasks currently file a bot wall under a generic "couldn't read" state: company `fetch_website` (`CANNOT_READ_WEBSITE`), company `fetch_job_pages` (`JOBSITE_SCRAPE_ISSUE`), and job `fetch_culture_pages` (`NEED_CULTURE_CONTENT`). Each now runs the existing shared bot detector and routes a bot wall to `BOT_BLOCKED_<TASK_KEY>`. "Literally nothing found" outcomes (`NO_WEBSITE`, `NO_JOBLIST`, `NO_PJL_SELECTED`, `NO_PREFILTER_JOBLISTS`, `NO_CULTURE_LINKS`) become `ERROR_<TASK_KEY>_<condition>`.
 5. **Generic** `FAILED_TECHNICAL` **retired.** Every writer that falls back to the task-less `FAILED_TECHNICAL` routes to bare `ERROR_<its own TASK_KEY>`. This covers the analysis_upshot or meteorite_upshot second failure, the empty-token fallback, and the mid-chain hop failure.
 6. **Meteorite scrape retry follows the standard pattern.** The meteorite `SCRAPE_ERROR` retry-holding state becomes the standard retry companion `SCRAPE_LINK_RETRY`, and scrape_meteorite claims it alongside `SCRAPE_LINK`. A second failure from the companion is terminal at `ERROR_SCRAPE_METEORITE`. Susan's answer wrote `ERROR_SCRAPE_LINK`, but the task_key grammar makes it `ERROR_SCRAPE_METEORITE`, since `scrape_meteorite` is the task. `ABANDONED` keeps its nag-limit / stale path from the bot and retry states.
 7. **Dead states retired.** `PREFILTER_UNKNOWN`, `HARD_PARSE` (company) and `BUILD_FAILED` (job) have no live writer. They are removed from the registries, transitions, Skipped lists, and bulk-retry map. No code accounts for them, and existing rows on them are not updated.
 8. **Behaviour preserved.** The new names keep each retired name's existing behaviour:
    * prior states and transitions
    * Skipped-section placement, label, and bulk-retry target
    * dispatch claim role (meteorite `BOT_BLOCKED` notify and land claims become `BOT_BLOCKED_SCRAPE_METEORITE`)
    * Estelle paste recovery

    When one retired name splits into several (per task, or per chain hop), every new name inherits the old name's label and retry target. Contact Estelle bot-block recovery stays a separate flow and is not extended to job or company bot blocks here.
 9. **Persisted rows remapped.** A run-once, dry-run-by-default migration rewrites `state` on existing job, company, candidate, and meteorite rows that sit on a retired name, and rewrites `dispatch_task.trigger_state` on live rows. When one retired name maps to several new names, the migration picks the right one from the row's data:
    * the row's last `state_history` predecessor (trigger state or `.<hop>` label → task_key)
    * for meteorite `LINK_EXPIRED`, the `scrape_closed` / `scrape_missing` signal in its `error`

    Rows it can't resolve, and rows on the dead states in #7, are left untouched. Each group is counted in the dry run. `state_history` and `state_changed_at` are never rewritten.
10. **In-flight sibling.** [AST-2054](https://linear.app/astralcareermatch/issue/AST-2054) (Company Upshot) is adding `ERROR_UPSHOT` and the `GET_UPSHOT` fetch outcomes now. This epic dispatches after AST-2054 is Done and renames those states by the same grammar (e.g. `ERROR_COMPANY_UPSHOT`, and `BOT_BLOCKED_<fetch TASK_KEY>` for any upshot fetch bot wall).

**Out of scope:**

* Verdict outcomes from a task that *succeeded* keep their names: `INVALID_TITLE`, `FAILED_JOBLIST/JD/DO/GET/LIKE`, `METEORITE_FAILED_QUALIFY/JD/DO/GET/LIKE`, `PREFILTER_FAILED`, `VET_FAILED`, `IGNORE`, `NO_OPENINGS`, `NOT_A_JOB`, `DUPLICATE`, `ABANDONED`, `LANDED`.
* `JD_SCRAPE_FAIL_CLOSED` and `JD_SCRAPE_FAIL_MISSING` are kept (Functional scope #3).
* Agent `response_type` strings such as select_job_page's `JOBSITE_SCRAPE_ISSUE` are prompt contract, not states, and stay unchanged.
* There is no candidate-ask flow for job or company bot blocks.

## Pipeline flow

This epic doesn't add hops. It renames the outcomes of existing tasks. Each row maps one retired name to its new name; the trigger column shows which state the task claims.

**Job** (`JOB_STATES`)

| Trigger | task_key | Retired | New |
| -- | -- | -- | -- |
| NEW | qualify_job_listings | ERROR_QUALIFY_JOB_LISTINGS | unchanged — already conforms |
| PASSED_JOBLIST | fetch_jd | JD_SCRAPE_FAIL | ERROR_FETCH_JD_UNREADABLE |
| PASSED_JOBLIST | fetch_jd | JD_SCRAPE_FAIL_COOKIE | ERROR_FETCH_JD_COOKIE |
| PASSED_JOBLIST | fetch_jd | JD_SCRAPE_FAIL_MISSING / \_CLOSED | unchanged — expired-link names |
| PASSED_JOBLIST | fetch_jd | BOT_BLOCKED | BOT_BLOCKED_FETCH_JD |
| RELATIVE_JOB_LINK | fetch_relative_jd | RELATIVE_LINK_FAIL | ERROR_FETCH_RELATIVE_JD_CLICK |
| RELATIVE_JOB_LINK | fetch_relative_jd | JD_SCRAPE_FAIL / JD_SCRAPE_FAIL_COOKIE | ERROR_FETCH_RELATIVE_JD_UNREADABLE / ERROR_FETCH_RELATIVE_JD_COOKIE |
| RELATIVE_JOB_LINK | fetch_relative_jd | JD_SCRAPE_FAIL_MISSING / \_CLOSED | unchanged — expired-link names |
| RELATIVE_JOB_LINK | fetch_relative_jd | BOT_BLOCKED | BOT_BLOCKED_FETCH_RELATIVE_JD |
| JD_READY | evaluate_jd | ERROR_EVALUATE_JD | unchanged — already conforms |
| PASSED_JD | grade_do | FAILED_TECHNICAL_DO | ERROR_GRADE_DO |
| PASSED_DO | grade_get | FAILED_TECHNICAL_GET | ERROR_GRADE_GET |
| PASSED_GET | fetch_culture_pages | NEED_CULTURE_CONTENT | ERROR_FETCH_CULTURE_PAGES_UNREADABLE (bot wall → **new** BOT_BLOCKED_FETCH_CULTURE_PAGES) |
| PASSED_GET | fetch_culture_pages | NO_CULTURE_LINKS | ERROR_FETCH_CULTURE_PAGES_NO_CULTURE_LINKS |
| PASSED_DO / PASSED_GET / CULTURE_READY | the scoring task whose website-content prep failed (grade_get, grade_like, …) | NEED_WEBSITE_CONTENT | ERROR\_<TASK_KEY>\_NO_WEBSITE_CONTENT |
| CULTURE_READY | grade_like | FAILED_TECHNICAL_LIKE | ERROR_GRADE_LIKE |
| PASSED_LIKE | analysis_upshot (2nd failure) | FAILED_TECHNICAL | ERROR_ANALYSIS_UPSHOT |
| any (empty-token / mid-chain fallback) | the failing task_key | FAILED_TECHNICAL | ERROR\_<TASK_KEY> |
| BUILD_ARTIFACTS | each failing artifact-chain hop (anticipate_scan, contemplate_job, advise_job_resume, draft_job_resume, check_job_resume, finalize_job_resume, draft_cover_letter, check_cover_letter, finalize_cover_letter, propose_application_responses) | ERROR_BUILD_ARTIFACTS | ERROR\_<HOP TASK_KEY> per hop (e.g. ERROR_DRAFT_JOB_RESUME) |
| METEORITE_NEW | qualify_meteorite | METEORITE_ERROR_QUALIFY | ERROR_QUALIFY_METEORITE |
| METEORITE_NEW | qualify_meteorite | BOT_BLOCKED | BOT_BLOCKED_QUALIFY_METEORITE |
| METEORITE_QUALIFIED | evaluate_meteorite | METEORITE_ERROR_EVALUATE_JD | ERROR_EVALUATE_METEORITE |
| METEORITE_PASSED_JD | meteorite_grade_do | METEORITE_FAILED_TECHNICAL_DO | ERROR_METEORITE_GRADE_DO |
| METEORITE_PASSED_DO | meteorite_grade_get | METEORITE_FAILED_TECHNICAL_GET | ERROR_METEORITE_GRADE_GET |
| METEORITE_PASSED_GET | meteorite_like | METEORITE_FAILED_TECHNICAL_LIKE | ERROR_METEORITE_LIKE |
| METEORITE_PASSED_LIKE | meteorite_upshot (2nd failure) | FAILED_TECHNICAL | ERROR_METEORITE_UPSHOT |
| — | no live writer | BUILD_FAILED | retired; rows left as-is |

**Company** (`COMPANY_STATES`)

| Trigger | task_key | Retired | New |
| -- | -- | -- | -- |
| DISCOVERED | inflow_resolve_website | NO_WEBSITE | ERROR_INFLOW_RESOLVE_WEBSITE_NOT_FOUND |
| WEBSITE_REVIEW | resolve_website | NO_WEBSITE | ERROR_RESOLVE_WEBSITE_NOT_FOUND |
| WEBSITE_FOUND | fetch_website | CANNOT_READ_WEBSITE | ERROR_FETCH_WEBSITE_UNREADABLE (bot wall → **new** BOT_BLOCKED_FETCH_WEBSITE) |
| HOMEPAGE_READY | prefilter_company | ERROR_PREFILTER | ERROR_PREFILTER_COMPANY |
| HOMEPAGE_READY | prefilter_company | NO_PREFILTER_JOBLISTS | ERROR_PREFILTER_COMPANY_NO_JOBLIST_LINKS |
| HOMEPAGE_READY | prefilter_company (homepage scrape error / not-ready skip) | CANNOT_READ_WEBSITE | ERROR_PREFILTER_COMPANY_UNREADABLE |
| PREFILTER_PASSED | fetch_job_pages | JOBSITE_SCRAPE_ISSUE | ERROR_FETCH_JOB_PAGES_UNREADABLE (bot wall → **new** BOT_BLOCKED_FETCH_JOB_PAGES) |
| PJL_READY | select_job_page | NO_PJL_SELECTED | ERROR_SELECT_JOB_PAGE_NO_SELECTION |
| PJL_READY | select_job_page | NO_JOBLIST | ERROR_SELECT_JOB_PAGE_NO_JOBLIST |
| PJL_READY | select_job_page | JOBSITE_SCRAPE_ISSUE | ERROR_SELECT_JOB_PAGE_UNREADABLE |
| PJL_READY | select_job_page (empty-token) | ERROR_LOCATE_JOB_PAGE | ERROR_SELECT_JOB_PAGE |
| PJL_READY | select_job_page | BOT_BLOCKED | BOT_BLOCKED_SELECT_JOB_PAGE |
| JOBLIST_IDENTIFIED | parse_job_list | COULD_NOT_PARSE_JOBLIST | ERROR_PARSE_JOB_LIST_UNPARSEABLE |
| JOBLIST_IDENTIFIED | parse_job_list (empty-token) | ERROR_LOCATE_JOB_PAGE | ERROR_PARSE_JOB_LIST |
| JOBS_FOUND | the task_key that claims JOBS_FOUND for the `locate_job_page` flow (plan-child confirms it from the dispatch catalog) | CANNOT_PARSE_JOB_SITE / NO_JOBLIST / JOBSITE_SCRAPE_ISSUE / ERROR_LOCATE_JOB_PAGE | ERROR\_<TASK_KEY>\_UNPARSEABLE / \_NO_JOBLIST / \_UNREADABLE / bare ERROR\_<TASK_KEY> |
| JOBS_FOUND | same | BOT_BLOCKED | BOT_BLOCKED\_<TASK_KEY> |
| WATCH | gaze | ERROR_GAZE | unchanged — already conforms |
| — | no live writer | PREFILTER_UNKNOWN, HARD_PARSE | retired; rows left as-is |

**Candidate** (`CANDIDATE_STATES`)

| Trigger | task_key | Retired | New |
| -- | -- | -- | -- |
| REQUESTED_RESUME | each failing resume-chain hop | REQUESTED_RESUME_ERROR | ERROR\_<HOP TASK_KEY> per hop |
| REQUESTED_ARTIFACTS | each failing artifacts-chain hop (entry craft_get_rubric) | REQUESTED_ARTIFACTS_ERROR | ERROR\_<HOP TASK_KEY> per hop (e.g. ERROR_CRAFT_GET_RUBRIC) |

**Meteorite staging row** (`METEORITE_STATES`)

| Trigger | task_key | Retired | New |
| -- | -- | -- | -- |
| NEW | stage_meteorite (classify, and insert-time email failure) | NEW_EMAIL_ERROR | ERROR_STAGE_METEORITE |
| SCRAPE_LINK | scrape_meteorite | BOT_BLOCKED | BOT_BLOCKED_SCRAPE_METEORITE (still claimed by meteorite_bot_blocked_notify and land_meteorite) |
| SCRAPE_LINK | scrape_meteorite | LINK_EXPIRED | JD_SCRAPE_FAIL_CLOSED / JD_SCRAPE_FAIL_MISSING (by page status) |
| SCRAPE_LINK | scrape_meteorite (1st failure) | SCRAPE_ERROR | SCRAPE_LINK_RETRY (claimed by scrape_meteorite) |
| SCRAPE_LINK_RETRY | scrape_meteorite (2nd failure) | — | **new** ERROR_SCRAPE_METEORITE |

## Component scope

* `src/utils/config.py` — **modified** — four state registries, every config-carried terminal/bot state (TASK_CONFIG `error_state`, GAZER_CONFIG, ROSTER_CONFIG, meteorite configs, company transitions, Skipped lists/labels/bulk-retry, dispatch seed SQL, dispatch trigger rules), the new naming helpers + condition vocabulary, and the retired-name map.
* `src/core/roster.py` — **modified** — company terminal literals (NO_WEBSITE, NO_PJL_SELECTED, NO_JOBLIST, CANNOT_PARSE_JOB_SITE, CANNOT_READ_WEBSITE, BOT_BLOCKED, terminal-ok / persist-page sets) read from config by task_key.
* `src/core/gazer.py` — **modified** — JD classification map made task-aware; shared bot detector applied in fetch_website, fetch_job_pages, fetch_culture_pages.
* `src/core/consult.py` — **modified** — generic `FAILED_TECHNICAL` fallbacks and `NEED_WEBSITE_CONTENT` writers routed to per-task names.
* `src/core/meteorite.py` — **modified** — staging-row literals (NEW_EMAIL_ERROR, SCRAPE_ERROR, BOT_BLOCKED, LINK_EXPIRED) read from config; scrape retry companion + terminal routing.
* `src/core/contact.py` — **modified** — docstring references to the retired `BOT_BLOCKED` (paste recovery).
* `src/core/dispatcher.py` — **modified** — comment/docstring references to the retired `BOT_BLOCKED` (notify runner).
* `src/core/candidate.py` — **modified** — candidate craft-chain failure writers (`_requested_stage_failure_target`, `run_requested_artifacts_dispatch` empty-token arm) land a failing hop on its own `ERROR_<HOP TASK_KEY>` from TASK_CONFIG instead of the retired `REQUESTED_*_ERROR` registry `error_state`. (Added after AST-2086 `[scope-gate]`.)
* `data/admin/dispatch_task.json` — **modified** — `meteorite_bot_blocked_notify` seed `trigger_state`.
* `src/ui/frontend/src/lib/recommendedJobReport.tsx` — **modified** — doc comment naming `ERROR_BUILD_ARTIFACTS`.
* `src/data/database.py` — **modified** — conn-bound remap of persisted entity `state` + `dispatch_task.trigger_state` from the retired-name map; one comment naming `NEW_EMAIL_ERROR`.
* `scripts/migrations/migrate_terminal_state_names.py` — **new** — operator CLI (dry-run default, `--execute`) wrapping the database remap, same shape as `scripts/migrations/migrate_legacy_candidate_states.py`.

## Technical scope

* `src/utils/config.py`
  * **New helpers** beside `retry_of` / `retry_base`. They build `ERROR_<TASK_KEY>` / `ERROR_<TASK_KEY>_<condition>` and `BOT_BLOCKED_<TASK_KEY>` from a task_key (and optional condition), and parse a name back into its parts. Each registry key is written through the helpers, never as a typed literal. The kept `JD_SCRAPE_FAIL_CLOSED` / `_MISSING` names are the one existing literal family.
  * **New config list:** the closed condition vocabulary (Functional scope #1).
  * **Modified** `JOB_STATES`, `COMPANY_STATES`, `CANDIDATE_STATES`, `METEORITE_STATES`:
    * Retired keys are replaced by the Pipeline flow names, carrying each one's `prior_states` / `progress_rank`, and every `prior_states` list that named a retired key is updated.
    * Added: `BOT_BLOCKED_FETCH_WEBSITE`, `BOT_BLOCKED_FETCH_JOB_PAGES`, `BOT_BLOCKED_FETCH_CULTURE_PAGES` (with their transitions), plus `JD_SCRAPE_FAIL_CLOSED` / `_MISSING`, `SCRAPE_LINK_RETRY` and `ERROR_SCRAPE_METEORITE` on the meteorite staging registry.
    * The `PREFILTER_UNKNOWN`, `HARD_PARSE`, and `BUILD_FAILED` keys are deleted.
  * **Modified config blocks** that name terminal states:
    * TASK_CONFIG `error_state` (artifact and candidate chain hops each name their own)
    * GAZER_CONFIG `fail_state` / `error_states` / `no_links_state` + new bot-blocked state per fetch task
    * ROSTER_CONFIG `error_state` / `no_pjl_state` / `exhausted_state` / `terminal_fail_state` / `scrape_issue_state`
    * `qualify_meteorite.bot_blocked_state`
    * `METEORITE_INGRESS_DISPATCH_CONFIG` scrape page-status map (closed / missing → `JD_SCRAPE_FAIL_*`, blocked → `BOT_BLOCKED_SCRAPE_METEORITE`) + scrape retry/terminal states
    * `METEORITE_BOT_BLOCKED_NOTIFY_CONFIG.trigger_state` and its seed SQL
    * `company_state_transitions` (dead-state pairs removed)
    * `SKIPPED_STATES`, Skipped section order/labels, and `JOBS_SKIPPED_BULK_RETRY_TO_STATE` (same label and same retry target per new key; dead states removed)
    * `ERROR_BUILD_ARTIFACTS_STATE` and the dispatch rule that maps chain task_keys to the artifact chain's trigger by comparing their `error_state`. That rule must key on chain membership instead, because each hop now carries its own error name.
  * **New retired-name map.** It maps each old name (with its task_key or trigger, and for `LINK_EXPIRED` the page status) to the new name. It is the only place old names survive, and it is read by the migration. It never lists dead states.
  * **Modified module asserts** that name retired states (e.g. the `BOT_BLOCKED`-in-`JOB_STATES` and `METEORITE_STATES` key-set asserts).
* `src/core/roster.py` — **modified** company outcome writers. These include the inflow/resolve no-website path, select_job_page exhausted / no-joblist / bot / scrape-issue returns, the locate flow parse outcomes, the prefilter homepage-scrape error and not-ready skip, and the terminal-ok and persist-page-url sets. Each one takes its terminal state from config for its own task_key, instead of a literal.
* `src/core/gazer.py` — **modified** functions:
  * `_JD_ERROR_STATES` becomes task-aware: fetch_jd and fetch_relative_jd each land on their own `ERROR_*` / `BOT_BLOCKED_*` names, and share `JD_SCRAPE_FAIL_CLOSED` / `_MISSING`.
  * The fetch_website, fetch_job_pages, and fetch_culture_pages batch functions call the existing shared bot detector (`is_bot_wall`) on fetched text and route a hit to their task's `BOT_BLOCKED_<TASK_KEY>`.
  * The fetch_website fail-destination helper gets the same bot branch.
* `src/core/consult.py` — **modified** the batch-fail destination, the empty-token fail destination, and the mid-chain empty-token fallback. Each resolves bare `ERROR_<failing TASK_KEY>`. The website-content prep writers resolve `ERROR_<scoring TASK_KEY>_NO_WEBSITE_CONTENT`.
* `src/core/meteorite.py` — **modified**:
  * The stage classify failure, the land claim states, the notify runner, and the paste-recovery `BOT_BLOCKED` checks read staging-row states from config.
  * The scrape runner routes a first scrape failure to `SCRAPE_LINK_RETRY` and a failure from `SCRAPE_LINK_RETRY` to `ERROR_SCRAPE_METEORITE`, deciding by the row's current state per `patt.task.dispatch-retry`. It claims both states.
* `src/core/contact.py`, `src/core/dispatcher.py`, `src/ui/frontend/src/lib/recommendedJobReport.tsx` — **modified** comments/docstrings only.
* `data/admin/dispatch_task.json` — **modified** the `meteorite_bot_blocked_notify` row `trigger_state`.
* `src/data/database.py` — **new** conn-bound remap function. For each entity table, it rewrites `state` from the retired-name map. Where an old name maps to several new names, it picks the new name from the row's last `state_history` predecessor (trigger state or `.<hop>` label → task_key), or for meteorite `LINK_EXPIRED` from the `scrape_closed` / `scrape_missing` signal in `error`. It skips unresolvable rows and dead-state rows. It also rewrites `dispatch_task.trigger_state`, and returns per-(entity, old→new) counts plus skipped counts. It is dry-run capable and never called from schema-ensure, because content remaps are explicit ops.
* `scripts/migrations/migrate_terminal_state_names.py` — **new** CLI that runs dry-run by default, `--execute` to apply, and prints counts.

## Architectural definition

* **Patterns to reuse**
  * [`patt.task.dispatch-retry`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.task.dispatch-retry.md>) — the error a task lands on after its one retry stays config-driven (`error_state`), and the retry companion is unchanged (`<trigger>_RETRY`). Meteorite scrape now follows it too (`SCRAPE_LINK_RETRY` → `ERROR_SCRAPE_METEORITE`). **Change requested:** the "When this doesn't apply" bullet cites `FAILED_TECHNICAL` as the terminal fallback example; that example must name the per-task bare `ERROR_<TASK_KEY>` once this lands.
  * [`patt.task.daisy-chain`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.task.daisy-chain.md>) — a mid-chain failure names the error by the hop task_key that failed. The hop label already identifies that task_key, and chain claim/resume is untouched.
  * [`patt.contact.command-intercept`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.contact.command-intercept.md>) — BOT_BLOCKED paste recovery keeps working under `BOT_BLOCKED_SCRAPE_METEORITE`. **Change requested:** Arc step 3 names "BOT_BLOCKED paste recovery". The wording should read `BOT_BLOCKED_SCRAPE_METEORITE` (a text update only, no behaviour change).
* **New patterns proposed**
  * `patt.state.terminal-naming` *(proposed — Archie approval needed before children depend on it)*. The rules:
    * Terminal failure names are `ERROR_<TASK_KEY>_<condition>` (condition from a closed vocabulary in config) when the cause is known, else bare `ERROR_<TASK_KEY>`. There is never a catch-all suffix.
    * Bot walls are `BOT_BLOCKED_<TASK_KEY>`.
    * Expired links are `JD_SCRAPE_FAIL_<condition>`.
    * Names are built through config helpers, never typed.
    * Retired names live only in one retired-name map read by the migration.

    Future epics (e.g. [AST-2054](https://linear.app/astralcareermatch/issue/AST-2054)'s `ERROR_UPSHOT`) follow it.
* **Applicable statutes**
  * [`stat.dispatch.entity-state-bound`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.dispatch.entity-state-bound.md>) — the `meteorite_bot_blocked_notify` row (seed + live) must carry a `trigger_state` that is real in `METEORITE_STATES` and is what its runner claims by. Artifact-chain task_keys must still resolve to the chain's real trigger after their `error_state` diverges. A renamed trigger left stale in either place violates it.

## Acceptance criteria

1. **Registries follow the grammar.** Run:

```python
python3 - <<'EOF'
from src.utils import config as c
V = ('UNREADABLE','COOKIE','NOT_FOUND','NO_JOBLIST','NO_JOBLIST_LINKS','NO_SELECTION',
     'NO_CULTURE_LINKS','NO_WEBSITE_CONTENT','UNPARSEABLE','CLICK')
def is_task(k):
    try:
        c._dispatch_trigger_state_for_task_key(k); return True
    except KeyError:
        return k in c.TASK_CONFIG
for R in (c.JOB_STATES, c.COMPANY_STATES, c.CANDIDATE_STATES, c.METEORITE_STATES):
    for s in R:
        if 'FAILED_TECHNICAL' in s or ('ERROR' in s and not s.startswith('ERROR_')) or s == 'BOT_BLOCKED':
            print('bad', s)
        if s.startswith('BOT_BLOCKED_') and not is_task(s[12:].lower()):
            print('bot', s)
        if s.startswith('ERROR_') and not is_task(s[6:].lower()) and not any(
                s.endswith('_' + v) and is_task(s[6:-len(v) - 1].lower()) for v in V):
            print('err', s)
        if s in ('PREFILTER_UNKNOWN', 'HARD_PARSE', 'BUILD_FAILED', 'LINK_EXPIRED', 'SCRAPE_ERROR'):
            print('retired', s)
EOF
```

**Pass:** prints nothing. **Fail:** any line printed. That includes:

* an `ERROR_` name that is neither `ERROR_<real task_key>` nor `ERROR_<real task_key>_<vocabulary condition>` (a `TECHNICAL` suffix fails)
* a `BOT_BLOCKED_` name whose suffix isn't a real task_key
* a dead or retired key still registered

 2. **Retired names gone from code.** Run
    `git grep -nwE 'FAILED_TECHNICAL(_DO|_GET|_LIKE)?|METEORITE_ERROR_(QUALIFY|EVALUATE_JD)|METEORITE_FAILED_TECHNICAL_(DO|GET|LIKE)|JD_SCRAPE_FAIL(_COOKIE)?|RELATIVE_LINK_FAIL|BOT_BLOCKED|NEED_CULTURE_CONTENT|NO_CULTURE_LINKS|NEED_WEBSITE_CONTENT|NO_WEBSITE|CANNOT_READ_WEBSITE|ERROR_PREFILTER|NO_PREFILTER_JOBLISTS|JOBSITE_SCRAPE_ISSUE|NO_PJL_SELECTED|NO_JOBLIST|COULD_NOT_PARSE_JOBLIST|CANNOT_PARSE_JOB_SITE|ERROR_LOCATE_JOB_PAGE|REQUESTED_RESUME_ERROR|REQUESTED_ARTIFACTS_ERROR|NEW_EMAIL_ERROR|LINK_EXPIRED|SCRAPE_ERROR|ERROR_BUILD_ARTIFACTS|PREFILTER_UNKNOWN|HARD_PARSE|BUILD_FAILED' -- src data/admin ':!src/utils/config.py' | grep -v response_type`.
    **Pass:** no output. Inside `src/utils/config.py`, each of those names (other than the dead three, which are absent entirely) appears only as a key of the retired-name map. **Fail:** any hit outside that map. A name kept "for compatibility" also fails.
 3. **Grammar is built, not typed.** Run `git grep -nE '"ERROR_[A-Z_]+"|"BOT_BLOCKED_[A-Z_]+"' -- src/core`. **Pass:** returns nothing; core resolves names through config. **Fail:** any quoted terminal-state literal in core.
 4. **Bot walls split from catch-alls.** Run `git grep -n 'is_bot_wall(' src/core/gazer.py`. **Pass:** shows a call reached from each of the fetch_website, fetch_job_pages, and fetch_culture_pages batch paths. `git grep -n 'bot_signals' src/core` hits only inside `is_bot_wall`. **Fail:** a fetch path without the call, or a second bot-signal loop (a parallel detector). Betty's component test also checks behaviour: page text that trips the detector lands the row in that task's `BOT_BLOCKED_<TASK_KEY>`, and the `_UNREADABLE` state is a failure.
 5. **Meteorite scrape retry.** A component test drives scrape_meteorite twice with a failing scrape. **Pass:** the first failure lands the row on `SCRAPE_LINK_RETRY`, the second on `ERROR_SCRAPE_METEORITE`. A closed page lands on `JD_SCRAPE_FAIL_CLOSED`, a 404/missing page on `JD_SCRAPE_FAIL_MISSING`. **Fail:** any other state, or a row that stays on its input state.
 6. **Artifact chain still claims correctly.** Run `python3 -c "from src.utils import config as c; print({k: c._dispatch_trigger_state_for_task_key(k) for k in ('anticipate_scan','contemplate_job','advise_job_resume','draft_job_resume','check_job_resume','finalize_job_resume')})"`. **Pass:** every value is `BUILD_ARTIFACTS`. **Fail:** any `KeyError` or other value.
 7. **Behaviour carried over.** For every (old → new) pair in the retired-name map whose old key existed in origin/dev `JOBS_SKIPPED_BULK_RETRY_TO_STATE`, check the new name. **Pass:** the new name's bulk-retry target and Skipped label equal the old name's values on origin/dev (resolved through the same map). **Fail:** any mismatch or missing key.
 8. **Meteorite notify still bound.** **Pass:** `python3 -c "import json;print([r['trigger_state'] for r in json.load(open('data/admin/dispatch_task.json')) if r.get('task_key')=='meteorite_bot_blocked_notify'])"` prints `['BOT_BLOCKED_SCRAPE_METEORITE']`. After the migration's `--execute`, `sqlite3 data/astral.db "select trigger_state from dispatch_task where task_key='meteorite_bot_blocked_notify'"` prints the same. **Fail:** `BOT_BLOCKED` or anything else.
 9. **Migration is safe and complete.** `python scripts/migrations/migrate_terminal_state_names.py` (no flags) prints per-(entity, old→new) counts and per-name skipped counts. **Pass criteria:**
    * The dry run changes no row: `select sum(length(state)) from job` is equal before and after.
    * After `--execute`, each table (`job`, `company`, `candidate`, `meteorite`) has `select count(*) from <table> where state in (<retired-name map keys>)` equal to the dry run's skipped count for that table.
    * Rows on `PREFILTER_UNKNOWN` / `HARD_PARSE` / `BUILD_FAILED` are unchanged.
    * `select sum(length(state_history)) from <table>` is unchanged by `--execute`.

    **Fail:** a dry run that writes, any retired count above the skipped count, a changed dead-state row, or a changed `state_history` total.
10. **Sibling states conform.** After [AST-2054](https://linear.app/astralcareermatch/issue/AST-2054/company-upshot-new-task) is merged, AC 1 still prints nothing; this covers its upshot error / fetch states. **Fail:** `ERROR_UPSHOT` (or any upshot terminal not matching the grammar) printed.

## Open questions

None.

## Proposed child tickets

#### 1!: **Terminal-state rename and bot-wall split - Ada**

Renames every terminal failure and bot state on all four entity registries to the new grammar, and routes every writer through config. It also:

* retires the generic `FAILED_TECHNICAL` and the three dead states
* moves meteorite expired links onto `JD_SCRAPE_FAIL_*` and meteorite scrape onto the standard retry companion
* splits bot walls out of the three catch-all fetch tasks
* renames AST-2054's upshot terminal states once that epic is on dev

This is one atomic slice: a partial rename leaves writers emitting names the registry no longer accepts, so the epic tree would fail transition validation between children. It does **not** touch persisted rows (#2).
**Citations:** `patt.task.dispatch-retry`, `patt.task.daisy-chain`, `patt.contact.command-intercept`, `stat.dispatch.entity-state-bound`, `patt.state.terminal-naming` (proposed).
**Scope:**

* `src/utils/config.py` — **modified** — four state registries, every config-carried terminal/bot state (TASK_CONFIG `error_state`, GAZER_CONFIG, ROSTER_CONFIG, meteorite configs, company transitions, Skipped lists/labels/bulk-retry, dispatch seed SQL, dispatch trigger rules), the new naming helpers + condition vocabulary, and the retired-name map.
* `src/core/roster.py` — **modified** — company terminal literals (NO_WEBSITE, NO_PJL_SELECTED, NO_JOBLIST, CANNOT_PARSE_JOB_SITE, CANNOT_READ_WEBSITE, BOT_BLOCKED, terminal-ok / persist-page sets) read from config by task_key.
* `src/core/gazer.py` — **modified** — JD classification map made task-aware; shared bot detector applied in fetch_website, fetch_job_pages, fetch_culture_pages.
* `src/core/consult.py` — **modified** — generic `FAILED_TECHNICAL` fallbacks and `NEED_WEBSITE_CONTENT` writers routed to per-task names.
* `src/core/meteorite.py` — **modified** — staging-row literals (NEW_EMAIL_ERROR, SCRAPE_ERROR, BOT_BLOCKED, LINK_EXPIRED) read from config; scrape retry companion + terminal routing.
* `src/core/contact.py` — **modified** — docstring references to the retired `BOT_BLOCKED` (paste recovery).
* `src/core/dispatcher.py` — **modified** — comment/docstring references to the retired `BOT_BLOCKED` (notify runner).
* `data/admin/dispatch_task.json` — **modified** — `meteorite_bot_blocked_notify` seed `trigger_state`.
* `src/ui/frontend/src/lib/recommendedJobReport.tsx` — **modified** — doc comment naming `ERROR_BUILD_ARTIFACTS`.
* Technical:
  * `src/utils/config.py`:
    * **New helpers** beside `retry_of` / `retry_base`. They build `ERROR_<TASK_KEY>` / `ERROR_<TASK_KEY>_<condition>` and `BOT_BLOCKED_<TASK_KEY>` from a task_key (and optional condition), and parse a name back into its parts. Each registry key is written through the helpers, never as a typed literal. The kept `JD_SCRAPE_FAIL_CLOSED` / `_MISSING` names are the one existing literal family.
    * **New config list:** the closed condition vocabulary (Functional scope #1).
    * **Modified** `JOB_STATES`, `COMPANY_STATES`, `CANDIDATE_STATES`, `METEORITE_STATES`:
      * Retired keys are replaced by the Pipeline flow names, carrying each one's `prior_states` / `progress_rank`, and every `prior_states` list that named a retired key is updated.
      * Added: `BOT_BLOCKED_FETCH_WEBSITE`, `BOT_BLOCKED_FETCH_JOB_PAGES`, `BOT_BLOCKED_FETCH_CULTURE_PAGES` (with their transitions), plus `JD_SCRAPE_FAIL_CLOSED` / `_MISSING`, `SCRAPE_LINK_RETRY` and `ERROR_SCRAPE_METEORITE` on the meteorite staging registry.
      * The `PREFILTER_UNKNOWN`, `HARD_PARSE`, and `BUILD_FAILED` keys are deleted.
    * **Modified config blocks** that name terminal states:
      * TASK_CONFIG `error_state` (artifact and candidate chain hops each name their own)
      * GAZER_CONFIG `fail_state` / `error_states` / `no_links_state` + new bot-blocked state per fetch task
      * ROSTER_CONFIG `error_state` / `no_pjl_state` / `exhausted_state` / `terminal_fail_state` / `scrape_issue_state`
      * `qualify_meteorite.bot_blocked_state`
      * `METEORITE_INGRESS_DISPATCH_CONFIG` scrape page-status map (closed / missing → `JD_SCRAPE_FAIL_*`, blocked → `BOT_BLOCKED_SCRAPE_METEORITE`) + scrape retry/terminal states
      * `METEORITE_BOT_BLOCKED_NOTIFY_CONFIG.trigger_state` and its seed SQL
      * `company_state_transitions` (dead-state pairs removed)
      * `SKIPPED_STATES`, Skipped section order/labels, and `JOBS_SKIPPED_BULK_RETRY_TO_STATE` (same label and same retry target per new key; dead states removed)
      * `ERROR_BUILD_ARTIFACTS_STATE` and the dispatch rule that maps chain task_keys to the artifact chain's trigger by comparing their `error_state`. That rule must key on chain membership instead, because each hop now carries its own error name.
    * **New retired-name map.** It maps each old name (with its task_key or trigger, and for `LINK_EXPIRED` the page status) to the new name. It is the only place old names survive, and it is read by the migration. It never lists dead states.
    * **Modified module asserts** that name retired states (e.g. the `BOT_BLOCKED`-in-`JOB_STATES` and `METEORITE_STATES` key-set asserts).
  * `src/core/roster.py` — **modified** company outcome writers. These include the inflow/resolve no-website path, select_job_page exhausted / no-joblist / bot / scrape-issue returns, the locate flow parse outcomes, the prefilter homepage-scrape error and not-ready skip, and the terminal-ok and persist-page-url sets. Each one takes its terminal state from config for its own task_key, instead of a literal.
  * `src/core/gazer.py` — **modified** functions:
    * `_JD_ERROR_STATES` becomes task-aware: fetch_jd and fetch_relative_jd each land on their own `ERROR_*` / `BOT_BLOCKED_*` names, and share `JD_SCRAPE_FAIL_CLOSED` / `_MISSING`.
    * The fetch_website, fetch_job_pages, and fetch_culture_pages batch functions call the existing shared bot detector (`is_bot_wall`) on fetched text and route a hit to their task's `BOT_BLOCKED_<TASK_KEY>`.
    * The fetch_website fail-destination helper gets the same bot branch.
  * `src/core/consult.py` — **modified** the batch-fail destination, the empty-token fail destination, and the mid-chain empty-token fallback. Each resolves bare `ERROR_<failing TASK_KEY>`. The website-content prep writers resolve `ERROR_<scoring TASK_KEY>_NO_WEBSITE_CONTENT`.
  * `src/core/meteorite.py` — **modified**:
    * The stage classify failure, the land claim states, the notify runner, and the paste-recovery `BOT_BLOCKED` checks read staging-row states from config.
    * The scrape runner routes a first scrape failure to `SCRAPE_LINK_RETRY` and a failure from `SCRAPE_LINK_RETRY` to `ERROR_SCRAPE_METEORITE`, deciding by the row's current state per `patt.task.dispatch-retry`. It claims both states.
  * `src/core/contact.py`, `src/core/dispatcher.py`, `src/ui/frontend/src/lib/recommendedJobReport.tsx` — **modified** comments/docstrings only.
  * `data/admin/dispatch_task.json` — **modified** the `meteorite_bot_blocked_notify` row `trigger_state`.

Estimate: 5

#### 2: **Persisted-row remap for retired terminal names - Hedy**

After #1, existing job, company, candidate, and meteorite rows (and live `dispatch_task` rows) still sit on retired names. This ticket moves them to the new names with a dry-run-first operator migration. It uses #1's retired-name map. Multi-target names are resolved from `state_history` (trigger or hop label → task_key), or for meteorite `LINK_EXPIRED` from the `error` signal. Unresolvable rows and dead-state rows are left untouched and counted. It does **not** rename anything in config or core (#1 owns that), and it never rewrites `state_history` or `state_changed_at`.
**Citations:** `stat.dispatch.entity-state-bound` — the live `dispatch_task.trigger_state` remap must land on a real registry state its runner claims by.
**Scope:**

* `src/data/database.py` — **modified** — conn-bound remap of persisted entity `state` + `dispatch_task.trigger_state` from the retired-name map; one comment naming `NEW_EMAIL_ERROR`.
* `scripts/migrations/migrate_terminal_state_names.py` — **new** — operator CLI (dry-run default, `--execute`) wrapping the database remap, same shape as `scripts/migrations/migrate_legacy_candidate_states.py`.
* Technical:
  * `src/data/database.py` — **new** conn-bound remap function. For each entity table, it rewrites `state` from the retired-name map. Where an old name maps to several new names, it picks the new name from the row's last `state_history` predecessor (trigger state or `.<hop>` label → task_key), or for meteorite `LINK_EXPIRED` from the `scrape_closed` / `scrape_missing` signal in `error`. It skips unresolvable rows and dead-state rows. It also rewrites `dispatch_task.trigger_state`, and returns per-(entity, old→new) counts plus skipped counts. It is dry-run capable and never called from schema-ensure, because content remaps are explicit ops.
  * `scripts/migrations/migrate_terminal_state_names.py` — **new** CLI that runs dry-run by default, `--execute` to apply, and prints counts.

after #1. Estimate: 3

**New patterns:** #1 introduces `patt.state.terminal-naming` (config-built `ERROR_<TASK_KEY>[_<condition>]` / `BOT_BLOCKED_<TASK_KEY>` + retired-name map). #2 reuses its retired-name map. Any future state-adding epic (Company Upshot first) reuses the helpers.

**Monolith check:** Functional scope has 10 items across 2 children. #1 stays one slice on purpose: the registry rename and every writer of those names must ship together, or the epic tree carries writers emitting names the registry rejects.

**Scope partition check:** Every Component scope file appears in exactly one child. #1 owns config, core, the dispatch seed, and the frontend comment; #2 owns `database.py` and the new migration script.

---

## Original brief

We have "%\_FAILED_TECHNICAL\_%" and we have "ERROR\_%" and we might also have "%\_ERROR" or "%\_ERROR\_%" as valid entity states.

Let's clean up that list to be easily read.  ERROR\_<trigger state>\_<terminal condition>  for ALL entity types.

Seek out those "catch all" terminal states like "NO_JOBSITE" that can happen when there is a bot-blocked site or literally no site was found.

Also, do NOT prefix bot block detections with errors, but instead with "BOT_BLOCKED\_<trigger state>", so that the candidate can be asked to open the page for us. to continue analysis.

**Revision (Susan, define round 2):** Thank you so much for listing out the table of new states!  I think actually we should go with ERROR\_<task_key>\_<condition>

**Revision (Susan, define round 3):** Recommended edit:  Stop using "TECHNICAL" in the terminal state.  Either specify the known condition of the reason for the error, or set it to "ERROR\_<task_key>" in general.

**Answers (Susan, define round 4), to Open questions 1–6 in order:**

1. Expired links (404 or text indicates the job is closed) are JD_SCRAPE_FAIL\_<condition>
2. Yes, Contact Estelle recovery for bot blocked entities is intentionally discrete from these
3. Yes, the standard retry companion and ERROR_SCRAPE_LINK at fail.
4. Yes, retire them.  Do not account for them in the logic, they should never occur again, and do not update existing data.
5. Yes, make it task_key as well, sorry for the confusion.
6. Per hop, please.

### Comments

#### chuckles — 2026-10-09T23:33:35.077Z
[check-linear] In Progress — both OKs on record: (1) force-with-lease reword of `a2278e17f` on AST-2086's sub, (2) `refresh-ftr.sh AST-2073` mid-epic. The datt pass applies them before Ada's test-child resumes.

#### susan — 2026-10-09T22:34:17.502Z
@chuckles OK on both.

#### chuckles — 2026-10-09T21:41:44.737Z
@susan [AST-2086](https://linear.app/astralcareermatch/issue/AST-2086) is blocked again. Betty's approved merge is pushed (`a2278e17f`) and Ada is assignee at Tests Ready, but `validate-sub-log.sh` (merge-child's gate) fails on `Merge remote-tracking branch` subjects in two places:

- **`a2278e17f` (Betty's merge):** it got git's default message because the merge didn't go through `sync-child.sh`. The only fix is to reword it to `sync(publish-ref): origin/sub/AST-2073/AST-2086-terminal-state-rename` and push with `--force-with-lease`. Nobody has pushed to the sub since.
- **`9472710b2`, `52d9749a3`, `7caff6333`:** these are dev's own history. They show up only because `origin/ftr/AST-2073-revise-terminal-states` is 192 commits behind `origin/dev`, which is the refresh Ada asked for at 02:50. A `merge-tree` dry run of dev into ftr is clean, so `refresh-ftr.sh AST-2073` would clear them.

Need your OK on both: (1) the force-with-lease reword of `a2278e17f` on the sub, and (2) running `refresh-ftr.sh AST-2073` now, mid-epic. Ada's test-child is on hold until then so she doesn't hit the same wall.

#### chuckles — 2026-10-09T08:29:00.055Z
Got it. Option 1 is on record: Betty may commit her resolved test-tree merge onto `bb7964ad2` with `--no-verify` in `astral-AST-2073`. This one-off OK covers only that merge. After the commit she pushes the sub and hands [AST-2086](https://linear.app/astralcareermatch/issue/AST-2086) back to Ada, who runs the manifest.

#### susan — 2026-10-09T08:28:31.575Z
@chuckles i choose 1.

#### chuckles — 2026-10-09T08:27:39.261Z
Yes, it's stuck, and it's waiting on you. No agent is working on it right now.

- [AST-2086](https://linear.app/astralcareermatch/issue/AST-2086) is at **Tests Ready**, assigned to Betty. She has resolved her test-tree merge onto Ada's dev sync (`bb7964ad2`). The resolution keeps both AST-2096's all-X cases and the AST-2086 renamed-state cases in 3 files: `docs/test-bible/utils/config.md`, `tests/component/core/test_consult.py`, and `tests/component/utils/test_config.py`. The engineer pre-commit hook on the epic worktree rejects that commit, so she aborted the merge.
- [AST-2087](https://linear.app/astralcareermatch/issue/AST-2087) is at Todo with Hedy, queued behind AST-2086.

**To unblock, pick one:**
1. OK Betty to commit that merge with `--no-verify` in `astral-AST-2073`.
2. Have her redo the merge from `astral-tests`, where the engineer hook doesn't apply.

Either way she then pushes the sub and hands back to Ada, who runs the manifest.

#### susan — 2026-10-09T08:26:44.332Z
@chuckles is this ticket stuck?

#### chuckles — 2026-10-09T05:57:06.451Z
AST-2086 REVIEW — Betty's test-tree merge (origin/sub 627012b63 into Ada's dev-sync bb7964ad2) is resolved but blocked by the engineer pre-commit hook; @susan needs to OK `--no-verify` (or a redo from astral-tests) on [AST-2086](https://linear.app/astralcareermatch/issue/AST-2086) before Ada can run the manifest. Separately: sub-chuck drones hold the exclusive `astral-AST-2073` worktree lock, so every nested engineer/Betty spawn into the epic worktree deadlocks for 45 min (why the prior Ada test-child never ran); this drone used `CHUCKLES_WORKTREE_LOCK=0` on its nested spawns.

#### chuckles — 2026-10-09T03:20:18.528Z
AST-2086 REVIEW — Betty qa-child held at Code Complete: validate-tests-branch.sh blocks the origin/tests push on pre-existing `9ead623ca` (AST-2091 sync merge); needs @susan one-off OK (push fde9ca936 → origin/tests) or advance tests-clean-base past 9ead623ca. Betty also flagged a product fix for Ada: dead `else` in consult.py `_prep_live_content`.

#### ada — 2026-10-09T01:47:32.521Z
🛑 **Stage 9 blocked: AST-2054 not on origin/dev** — AST-2086

Stages 1–8 of [AST-2086](https://linear.app/astralcareermatch/issue/AST-2086) are built and published on `origin/sub/AST-2073/AST-2086-terminal-state-rename` (tip `2216670e0`). Stage 9 (rename AST-2054's upshot terminal `ERROR_UPSHOT` onto the grammar, AC 9) is gated per the plan's Sequencing section:

- `git show origin/dev:src/utils/config.py | grep -c '"ERROR_UPSHOT"'` → `0`
- `origin/ftr/AST-2054-company-upshot` is not an ancestor of `origin/dev`

No AST-2054 ref has been merged into the sub. AST-2086 stays at Plan Approved (not Code Complete) until AST-2054's finish-up lands it on dev; then Stage 9 runs via `sync-child.sh` only.

#### chuckles — 2026-10-09T01:02:50.763Z
@susan I can't dispatch yet. The Description's **Open questions** section still has six unanswered questions, and the child scope depends on them:

- **#1 Where "terminal error" stops.** Do "posting is closed" states (`JD_SCRAPE_FAIL_CLOSED`, meteorite `LINK_EXPIRED`) become `ERROR_<TASK_KEY>_CLOSED`, or stay as verdicts?
- **#2 Bot-blocked scope.** Does the candidate-ask flow for job and company bot blocks stay out of this epic?
- **#3 Meteorite `SCRAPE_ERROR`.** Rename to `SCRAPE_LINK_RETRY`, or leave as-is?
- **#4 Dead states and unrecoverable rows.** Retire `PREFILTER_UNKNOWN`, `HARD_PARSE`, `BUILD_FAILED`? Rows with no usable `state_history` go to the restart state?
- **#5 Bot grammar.** `BOT_BLOCKED_<trigger state>` or `BOT_BLOCKED_<TASK_KEY>`?
- **#6 Chains.** One error per failing hop, or one per chain?

You can answer in a comment, or edit or delete the questions in the Description. Then move the parent back to Todo and assign it to me.

#### chuckles — 2026-10-09T00:59:59.059Z
@susan `TECHNICAL` is gone from the definition. A failure with a known cause is now `ERROR_<TASK_KEY>_<condition>`, and anything general is bare `ERROR_<TASK_KEY>` (e.g. `FAILED_TECHNICAL_DO` → `ERROR_GRADE_DO`). As a result, `ERROR_QUALIFY_JOB_LISTINGS`, `ERROR_EVALUATE_JD`, and `ERROR_GAZE` already fit the grammar and keep their names. Questions 1–6 are still open:

1. **Where "terminal error" stops.** Verdicts from a task that *did* finish (rubric `FAILED_*`, `INVALID_TITLE`, `PREFILTER_FAILED`, `VET_FAILED`, `IGNORE`, `NO_OPENINGS`, `NOT_A_JOB`, `DUPLICATE`, `ABANDONED`) keep their names. "Posting is closed" (`JD_SCRAPE_FAIL_CLOSED`, meteorite `LINK_EXPIRED`) is drafted as `ERROR_<TASK_KEY>_CLOSED`. Keep that, or treat "closed" as a verdict and leave it alone?
2. **Bot-blocked scope.** This epic only renames bot states and splits bot walls out of catch-alls. Asking the candidate to open the page for **job** and **company** bot blocks would be a separate epic. OK?
3. **Meteorite** `SCRAPE_ERROR`**.** It's a retry-holding state, not a terminal one. Should it become `SCRAPE_LINK_RETRY` with the same behaviour, or stay as-is?
4. **Dead states and unrecoverable rows.** Retire `PREFILTER_UNKNOWN`, `HARD_PARSE`, `BUILD_FAILED`? Some rows on a multi-target retired name have no usable `state_history` (mostly old `FAILED_TECHNICAL`). Should those go to the entity's restart state (today's bulk-retry rule `FAILED_TECHNICAL → NEW`), with the count shown in the dry run?
5. **Bot grammar.** I kept `BOT_BLOCKED_<trigger state>` (e.g. `BOT_BLOCKED_PASSED_JOBLIST`) because that's where analysis resumes once the candidate opens the page. Or do you want `BOT_BLOCKED_<TASK_KEY>` (e.g. `BOT_BLOCKED_FETCH_JD`) for symmetry?
6. **Chains: per-hop or per-chain?** I drafted one error per failing artifact/candidate chain hop (`ERROR_DRAFT_JOB_RESUME`, `ERROR_CHECK_JOB_RESUME`, …). That's roughly a dozen new states, all with the same Skipped label and retry target. The other option is one state per chain, named after its entry task_key. Which do you want?

#### chuckles — 2026-10-09T00:42:34.937Z
@susan Switched every error name to `ERROR_<TASK_KEY>_<condition>` (tables, helpers, AC, and the migration all updated). Questions 1–4 from last round are still open, and the switch raised two more:

1. **Where "terminal error" stops.** Verdicts from a task that *did* finish (rubric `FAILED_*`, `INVALID_TITLE`, `PREFILTER_FAILED`, `VET_FAILED`, `IGNORE`, `NO_OPENINGS`, `NOT_A_JOB`, `DUPLICATE`, `ABANDONED`) keep their names. "Posting is closed" (`JD_SCRAPE_FAIL_CLOSED`, meteorite `LINK_EXPIRED`) is drafted as `ERROR_<TASK_KEY>_CLOSED`. Keep that, or treat "closed" as a verdict and leave it alone?
2. **Bot-blocked scope.** This epic only renames bot states and splits bot walls out of catch-alls. Asking the candidate to open the page for **job** and **company** bot blocks would be a separate epic. OK?
3. **Meteorite** `SCRAPE_ERROR`**.** It's a retry-holding state, not a terminal one. Should it become `SCRAPE_LINK_RETRY` with the same behaviour, or stay as-is?
4. **Dead states and unrecoverable rows.** Retire `PREFILTER_UNKNOWN`, `HARD_PARSE`, `BUILD_FAILED`? Some rows on a multi-target retired name have no usable `state_history` (mostly old `FAILED_TECHNICAL`). Should those go to the entity's restart state (today's bulk-retry rule `FAILED_TECHNICAL → NEW`), with the count shown in the dry run?
5. **Bot grammar after the switch.** I kept `BOT_BLOCKED_<trigger state>` (e.g. `BOT_BLOCKED_PASSED_JOBLIST`) because that's where analysis resumes once the candidate opens the page. Or do you want `BOT_BLOCKED_<TASK_KEY>` (e.g. `BOT_BLOCKED_FETCH_JD`) for symmetry?
6. **Chains: per-hop or per-chain?** With task_key naming, I drafted one error per failing artifact/candidate chain hop (`ERROR_DRAFT_JOB_RESUME_TECHNICAL`, `ERROR_CHECK_JOB_RESUME_TECHNICAL`, …). That's roughly a dozen new states, all with the same Skipped label and retry target. The other option is one state per chain, named after its entry task_key. Which do you want?

#### chuckles — 2026-10-08T23:22:55.258Z
@susan

1. **Where "terminal error" stops.** I've scoped the rename to outcomes where the hop *couldn't finish* (technical failure, unreadable / missing / blocked page, nothing found). Verdicts from a hop that *did* finish stay as they are: rubric `FAILED_*`, `INVALID_TITLE`, `PREFILTER_FAILED`, `VET_FAILED`, `IGNORE`, `NO_OPENINGS`, `NOT_A_JOB`, `DUPLICATE`, `ABANDONED`. One borderline case: "posting is closed" (`JD_SCRAPE_FAIL_CLOSED`, meteorite `LINK_EXPIRED`). The page read fine and told us it's gone. I've drafted it as `ERROR_<trigger>_CLOSED` to stay with its `JD_SCRAPE_FAIL_*` siblings. Keep that, or treat "closed" as a verdict and leave both names alone?
2. **Bot-blocked scope.** This epic only renames to `BOT_BLOCKED_<trigger>` and splits bot walls out of the catch-alls. The existing Estelle "please open this page" flow keeps working for meteorites. Asking the candidate to open the page for **job** and **company** bot blocks would be a new flow, which I'd file as its own epic. OK to leave that out of this one?
3. **Meteorite `SCRAPE_ERROR`.** It isn't terminal. It's a retry-holding state (Playwright miss → later retry or `ABANDONED`). Should it become the standard retry companion `SCRAPE_LINK_RETRY` (same behaviour, standard name)? Or should it stay as-is because it's not a terminal state?
4. **Dead states and unrecoverable rows.** `PREFILTER_UNKNOWN`, `HARD_PARSE` (company) and `BUILD_FAILED` (job) have no live writer. I'd retire them. That also leaves a question for rows on a multi-target retired name whose `state_history` doesn't say where they came from (mostly old generic `FAILED_TECHNICAL`). My default is to send those rows to the entity's restart state, the same "full restart, origin unknowable" rule bulk retry uses today (`FAILED_TECHNICAL → NEW`), with the count shown in the dry run. Retire + restart, or something else?

---

_Implementation detail may live in git history on `origin/dev`._

# AST-1998 — Distinguish between BOT_BLOCKED and NO_JOBSITE

<!-- linear-archive: AST-1998 archived 2026-10-13 -->

## Linear archive (AST-1998)

**Archived:** 2026-10-13  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1998/distinguish-between-bot-blocked-and-no-jobsite  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

When the roster pipeline tries to find a company's job list and one of the candidate job pages is a bot wall (LinkedIn's sign-in wall, a Cloudflare challenge, "verify you are human"), the company currently lands in `NO_JOBLIST` with no `job_site` recorded — indistinguishable from a company that genuinely has no careers page. Susan wants those cases split out: the company goes to `BOT_BLOCKED` (the same universal bot state jobs and meteorites already use, AST-1195) and the blocked URL is recorded on `company.job_site`, so the operator can see *where* we were blocked and act on it instead of losing the company in a dead-end bucket.

**As-is (verified in code, not assumed):**

* The state Susan's brief calls `NO_JOBSITE` is `NO_JOBLIST` in `COMPANY_STATES` (`src/utils/config.py`). There is no `NO_JOBSITE` state.
* Live path: `PJL_READY` → `select_job_page` (`run_select_job_page_dispatch` → `_find_job_page_from_assembled(decomposed=True)`) → when Grace answers `NO_JOBLIST_FOUND` (or any unrecognized response_type) `_check_parse_results` falls through to `NO_JOBLIST` with `page_option_url=company_website`.
* `NO_JOBLIST` is not in `_PERSIST_PAGE_OPTION_URL_STATES`, so no job-page URL is ever recorded for it.
* A company state `BOT_BLOCK` (no `ED`) is registered in `COMPANY_STATES` and listed in `company_state_transitions`, but **nothing in** `src/` **ever writes it**.
* A bot-wall detector already exists: `TRACKER_CONFIG["jd_classifier"]["bot_signals"]` / `bot_threshold` used by `gazer._classify_jd` for JDs — it already lists the LinkedIn auth wall ("New to LinkedIn? Join now", "Sign in with Email") and Cloudflare phrases.
* Each scraped job page's URL + visible text is already persisted in `company_data.pjl_scrape_pages` by `fetch_job_pages`, so the select step has everything it needs to check each page — no new scraping.

## Functional scope

1. **Detect a bot-walled job page at the "no job list" outcome.** When `select_job_page` would land a company in `NO_JOBLIST`, check the job pages it was shown; if one of them is a bot wall, that is the real reason no job list was found. (Detection mechanism — see Open question 1.)
2. **Route to** `BOT_BLOCKED` **instead of** `NO_JOBLIST`**.** The company's terminal state becomes `BOT_BLOCKED`. A genuine no-joblist (no page is a bot wall) still lands `NO_JOBLIST`, unchanged.
3. **Record the blocked URL.** `company.job_site` is set to the URL of the bot-walled page (first one in page order when several are walled).
4. **One company bot state, named like jobs/meteorites.** The existing unused company state `BOT_BLOCK` becomes `BOT_BLOCKED` (Open question 2).
5. **Bot-blocked counts as a fail in the select rollup.** `BOT_BLOCKED` reports `total_failed`, not `total_passed` / `total_errors` — consistent with AST-1751 ("fails only bot blocked and not a job").
6. **Never overrides a found job list.** If Grace returns `JOBLIST_TITLES`, `JOBLIST_NO_JOBS`, `TRY_LINKS`, or `JOBSITE_SCRAPE_ISSUE`, behavior is unchanged even if some other page was a bot wall.

**Out of scope:** `NO_PJL_SELECTED` (TRY_LINKS exhausted), `JOBSITE_SCRAPE_ISSUE` (all scrapes empty), the legacy `TO_WATCH` / `JOBS_FOUND` locate paths' early `NO_JOBLIST` exits (`SELECT_FAILED`, invalid parse, empty TRY_LINKS scrape), any recovery/retry for `BOT_BLOCKED` companies, any UI change (admin state lists read `COMPANY_STATES` keys dynamically), and the `select_job_page` prompt (unless Open question 1 picks the Grace option). Backfill of existing `NO_JOBLIST` rows — Open question 3.

## Pipeline flow

| State (trigger) | Dispatch `task_key` / handler | Next state(s) |
| -- | -- | -- |
| `PREFILTER_PASSED` | `fetch_job_pages` → `gazer.fetch_job_pages_batch` (unchanged) | `PJL_READY` / `JOBSITE_SCRAPE_ISSUE` |
| `PJL_READY` | `select_job_page` → `roster.run_select_job_page_dispatch` | `JOBLIST_IDENTIFIED` / `PREFILTER_PASSED_RETRY` / `NO_PJL_SELECTED` / `NO_OPENINGS` / `JOBSITE_SCRAPE_ISSUE` / `NO_JOBLIST` / `BOT_BLOCKED` **(new)** |
| `BOT_BLOCKED` | none — terminal, no `batch_criteria`, no dispatch row | — (chain ends; `company.job_site` = blocked URL) |

## Component scope

* `src/utils/config.py` — **modified** — rename company state `BOT_BLOCK` → `BOT_BLOCKED` in `COMPANY_STATES` and `company_state_transitions`; add the `PJL_READY → BOT_BLOCKED` transition.
* `src/core/roster.py` — **modified** — reroute the select step's `NO_JOBLIST` fall-through to `BOT_BLOCKED` when a shown page is a bot wall; persist `job_site` for `BOT_BLOCKED`.
* `src/core/gazer.py` — **modified** — make the existing bot-signal check reusable by roster (behavior of JD classification unchanged).

## Technical scope

* `src/utils/config.py`: modified `COMPANY_STATES` entry (rename key `BOT_BLOCK` → `BOT_BLOCKED`, still `{}` — terminal); modified `company_state_transitions` (rename the three existing `BOT_BLOCK` tuples; add one tuple for `PJL_READY` → `BOT_BLOCKED`). No new config block — detection reads the existing `TRACKER_CONFIG["jd_classifier"]` bot signals/threshold.
* `src/core/gazer.py`: new public helper (or promoted function) that answers "is this page text a bot wall?" using the same `bot_signals` / `bot_threshold` logic `_classify_jd` uses today; `_classify_jd` delegates to it so the two can never drift.
* `src/core/roster.py`: modified `_find_job_page_from_assembled` / `_check_parse_results` so the final `NO_JOBLIST` fall-through has the shown pages' URL + visible text available and, when the first bot-walled page is found, saves `BOT_BLOCKED` with that page's URL as `page_option_url`; modified `_PERSIST_PAGE_OPTION_URL_STATES` to include `BOT_BLOCKED` so `job_site` is written; modified the `PJL_READY` branch of `run_company_task` so `BOT_BLOCKED` is not in the `terminal_ok` set (reports `total_failed`).

## Architectural definition

* **Patterns to reuse** — no established pattern applies. (Terminal-state routing inside an existing runner; the claim/dispatch shape is untouched.)
* **New patterns proposed** — none.
* **Applicable statutes**
  * [`stat.logging.debug`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>) — the new bot-wall branch needs a generous debug line (which page, which URL) so a misroute is traceable.
  * [`stat.logging.info.entity`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md>) — the `PJL_READY → BOT_BLOCKED` transition is entity progress; it must surface via the existing id-pipe state line, not a new ad-hoc info log.

## Acceptance criteria

1. **Rename is complete.** `rg -n '"BOT_BLOCK"' src/` returns nothing, and `python -c "from src.utils.config import COMPANY_STATES as C; assert 'BOT_BLOCKED' in C and 'BOT_BLOCK' not in C"` exits 0. Fail: any hit, or the assert raises.
2. **Bot wall →** `BOT_BLOCKED` **+ URL.** Component test: company in `PJL_READY` whose `pjl_scrape_pages` holds page 1 = careers-less homepage text and page 2 = `https://www.linkedin.com/company/acme/jobs` with LinkedIn auth-wall text ("New to LinkedIn? Join now" … "Sign in with Email"); `select_job_page` mocked to `{"response_type": "NO_JOBLIST_FOUND", "selected_page": 0}`. After `run_select_job_page_dispatch`: `company.state == "BOT_BLOCKED"` and `company.job_site == "https://www.linkedin.com/company/acme/jobs"`. Fail: state `NO_JOBLIST`, or `job_site` empty / the company website.
3. **No bot wall → unchanged** `NO_JOBLIST`**.** Same test with no page reaching the bot threshold: `state == "NO_JOBLIST"` and `job_site` equals its pre-run value. Fail: `BOT_BLOCKED`, or `job_site` changed.
4. **Found job list wins.** Same pages, `select_job_page` mocked to `JOBLIST_TITLES` on page 1: `state == "JOBLIST_IDENTIFIED"`. Fail: `BOT_BLOCKED`.
5. **First walled page wins.** Two walled pages (2 and 3): `job_site` is page 2's URL. Fail: page 3's URL or empty.
6. **Rollup counts it as a fail.** `run_company_task` on the AC2 fixture returns `total_failed == 1`, `total_passed == 0`, `total_errors == 0`. Fail: any other split.
7. **One bot detector, not two.** `_classify_jd` and the roster check both go through the same gazer helper: `rg -n "bot_signals" src/core/` returns exactly one hit (in that helper). Fail: a second copy of the signal loop (e.g. inlined in `roster.py`).
8. **No host-list shim (unless Open question 1 chooses it).** `rg -in "linkedin" src/core/roster.py` returns nothing. Fail: any hit — detection must be content-based, not a hard-coded domain list.

## Open questions

1. **How should we detect "bot blocked"?** (a) *Recommended:* reuse the existing JD bot-signal check (LinkedIn sign-in wall, Cloudflare, "verify you are human" — `TRACKER_CONFIG.jd_classifier`) on the pages `select_job_page` already saw, only when the result would be `NO_JOBLIST`. No prompt change, deterministic. (b) Add a domain list of job boards ([linkedin.com](<http://linkedin.com>), [indeed.com](<http://indeed.com>), [glassdoor.com](<http://glassdoor.com>), …) that counts as `BOT_BLOCKED` whatever the page shows — your brief says "job sites (such as linkedin)", so do you want *any* third-party job board treated as blocked, even when it renders? (c) Give Grace a new `select_job_page` response_type for bot walls (prompt + `data/admin/agent_task.json` change).
   1. Yes option a
2. **Rename OK?** Company already has a registered-but-never-written state `BOT_BLOCK`. Plan is to rename it to `BOT_BLOCKED` (matching jobs/meteorites) with no data migration — nothing in code writes `BOT_BLOCK`, but I can't see prod rows from here. OK, or keep `BOT_BLOCK` for companies?
   1. Yes rename
3. **Backfill?** Companies already sitting in `NO_JOBLIST` still have their scraped pages in `company_data.pjl_scrape_pages`, so a one-time reclassify to `BOT_BLOCKED` is possible. Include it, or new rows only (current scope)?
   1. New rows only

## Proposed child tickets

#### 1: **Route bot-walled job pages to BOT_BLOCKED with job_site - Ada**

Renames the company bot state to `BOT_BLOCKED`, makes the existing bot-signal check reusable, and reroutes the `select_job_page` `NO_JOBLIST` fall-through to `BOT_BLOCKED` with the blocked URL on `job_site`, counted as a fail. Does not touch prompts, the legacy locate paths' early exits, `NO_PJL_SELECTED`, recovery, or UI.
**Citations:** `stat.logging.debug`, `stat.logging.info.entity`.
**Scope:**

* `src/utils/config.py` — **modified** — rename company state `BOT_BLOCK` → `BOT_BLOCKED` in `COMPANY_STATES` and `company_state_transitions`; add the `PJL_READY → BOT_BLOCKED` transition. Modified `COMPANY_STATES` entry (rename key `BOT_BLOCK` → `BOT_BLOCKED`, still `{}` — terminal); modified `company_state_transitions` (rename the three existing `BOT_BLOCK` tuples; add one tuple for `PJL_READY` → `BOT_BLOCKED`). No new config block — detection reads the existing `TRACKER_CONFIG["jd_classifier"]` bot signals/threshold.
* `src/core/gazer.py` — **modified** — make the existing bot-signal check reusable by roster (behavior of JD classification unchanged). New public helper (or promoted function) that answers "is this page text a bot wall?" using the same `bot_signals` / `bot_threshold` logic `_classify_jd` uses today; `_classify_jd` delegates to it so the two can never drift.
* `src/core/roster.py` — **modified** — reroute the select step's `NO_JOBLIST` fall-through to `BOT_BLOCKED` when a shown page is a bot wall; persist `job_site` for `BOT_BLOCKED`. Modified `_find_job_page_from_assembled` / `_check_parse_results` so the final `NO_JOBLIST` fall-through has the shown pages' URL + visible text available and, when the first bot-walled page is found, saves `BOT_BLOCKED` with that page's URL as `page_option_url`; modified `_PERSIST_PAGE_OPTION_URL_STATES` to include `BOT_BLOCKED` so `job_site` is written; modified the `PJL_READY` branch of `run_company_task` so `BOT_BLOCKED` is not in the `terminal_ok` set (reports `total_failed`).

Estimate: 2

**Monolith check:** Functional scope has 6 items, 1 child — intentional: one small inseparable vertical slice (the state rename, the shared detector, and the reroute must land together or the reroute writes an unregistered state / duplicates the detector). If Open question 1 picks (c) or Open question 3 adds a backfill, that becomes a second child.

**Scope partition check:** all three Component scope files and every Technical scope item are claimed by child 1; no overlaps.

---

## Original brief

I believe we are grouping the job sites (such as linkedin) as NO_JOBSITE, and now we should record the site url and set the state of the company to BOT_BLOCKED in that event.

### Comments

#### chuckles — 2026-10-06T05:12:45.909Z
@susan

1. **How should we detect "bot blocked"?** (a) *Recommended:* reuse the existing JD bot-signal check (LinkedIn sign-in wall, Cloudflare, "verify you are human") on the pages `select_job_page` already saw, only when the result would be `NO_JOBLIST`. No prompt change. (b) A domain list of job boards (linkedin.com, indeed.com, glassdoor.com, …) treated as `BOT_BLOCKED` whatever the page shows — i.e. *any* third-party job board counts as blocked, even when it renders. (c) A new Grace `select_job_page` response_type for bot walls (prompt change).
2. **Rename OK?** Companies already have a registered-but-never-written state `BOT_BLOCK`. Plan: rename it to `BOT_BLOCKED` (matching jobs/meteorites), no data migration. OK, or keep `BOT_BLOCK` for companies?
3. **Backfill?** Companies already in `NO_JOBLIST` still have their scraped pages saved, so a one-time reclassify to `BOT_BLOCKED` is possible. Include it, or new rows only?

---

_Implementation detail may live in git history on `origin/dev`._

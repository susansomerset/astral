# AST-1995 — fix: fetch_job_pages re-scrapes every PJL URL and replaces the stored page (fetch_ tasks should refresh existing content)

<!-- linear-archive: AST-1995 archived 2026-10-13 -->

## Linear archive (AST-1995)

**Archived:** 2026-10-13  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1995/fix-fetch-job-pages-re-scrapes-every-pjl-url-and-replaces-the-stored  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1994 — fetch_ tasks should refresh existing content  
**Blocked by / blocks / related:** parent: AST-1994

### Description

## What this implements

Make `fetch_job_pages` refresh job-board content: every run re-scrapes every URL in `company_data.possible_joblist_links` and replaces that URL's stored `pjl_scrape_pages` row with the fresh capture, so `pjl_assembled_content` (what `select_job_page` reads) reflects the board as it is **now**. Today the AST-719 additive ledger skips any URL already captured, freezing the board forever.

## Scope

## Component scope

* `src/core/gazer.py` — modified: `fetch_job_pages_batch` stops skipping already-scraped URLs. If culture refresh is approved, `fetch_culture_pages_batch` also loses its cached-pass branch.
* `src/core/roster.py` — modified: `_merge_pjl_scrape_record` changes from skip-if-present to replace-if-present. `_pjl_scrape_ledger_keys` may become unused and get removed. If culture refresh is approved, `get_company_data`'s `website_content` coat-check path gets checked for its own cache short-circuit.

Tests (`tests/component/core/test_gazer.py`, `test_roster.py` additive-skip cases) are Betty's tree. The AST-719 additive-skip assertions will flip, so `qa-fix` should expect that.

## Technical scope

* `src/core/gazer.py`: **modified function** `fetch_job_pages_batch`. It scrapes the full `possible_joblist_links` set each run instead of the ledger-filtered `pending` subset, because the skip is the bug. **Modified function** `fetch_culture_pages_batch` (conditional on Susan's answer). The cached-pass branch goes away so `website_content` is refreshed on each run.
* `src/core/roster.py`: **modified function** `_merge_pjl_scrape_record`. A record for an already-recorded URL replaces the existing row instead of being discarded, so refreshed board text actually persists. **Possibly removed function** `_pjl_scrape_ledger_keys`, once it has no callers. No new tables or fields: `pjl_scrape_pages`, `pjl_assembled_content`, and `pjl_nav_links` keep their current shapes.

## Acceptance criteria

* A `fetch_job_pages` run on a company whose PJL URLs are already in `pjl_scrape_pages` re-scrapes them (no `skipped-already-scraped` path) and the stored `visible_text` for each URL is the new capture, in its original position.
* A re-scrape that fails or comes back empty keeps that URL's prior row (no data loss on a transient failure); a successful one replaces it.
* `pjl_assembled_content` is rebuilt from the refreshed rows; `pjl_nav_links` reflects this run's page links (dead links fall off).
* `PJL_READY` / `JOBSITE_SCRAPE_ISSUE` transitions unchanged.

## Boundaries

`fetch_job_pages` only. `fetch_culture_pages` **cache is out of scope** — Susan checked only AST-719 (AST-874, the culture-cache ancestor, left unchecked). `fetch_jd` / `fetch_website` already re-scrape; untouched. Tests / bible are Betty's (fix-board decides whether a gap child is needed). Orphaned mini-parent is AST-1994; approved ancestor AST-719 (archived — no related link).

## Notes for planning

AST-1994 Description (As-is / To-be / Proposed steps 1–4, 6) is authoritative; step 5 (culture) is dropped per the Boundaries line. Failure semantics: Proposed step 2's default (keep prior row on failure, replace on success) stands — Susan approved the read without overriding it. Plan-doc patch target (approved ancestor): `docs/features/roster/ast-719-fetch-job-pages-gazer-batch-and-pjl-ready-state.md`.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1994-fetch-refresh`, child `sub/AST-1994/AST-1995-fetch-refresh`. Created at bug-fix.

### Comments

#### radia — 2026-10-06T05:22:09.212Z
[code-rubric] PROCEED (Commit: c9303baa) PJL refresh upsert clean

#### hedy — 2026-10-06T05:12:19.857Z
`origin/sub/AST-1994/AST-1995-fetch-refresh` @ `c9303baa2`

Note for test gap AST-1999 (Betty): `tests/component/core/test_gazer.py::TestFetchJobPagesBatch` has 4 tests that already fail on the pre-fix tree with `NameError: _mock_browser_context is not defined`, so the gazer flip can't be observed until that helper exists. The only new failure is `test_roster.py::TestAst719PjlRosterHelpers::test_merge_pjl_scrape_record_skips_duplicate_and_empty`, as predicted (its first assert expects the duplicate to be discarded; it now replaces the row). I ran the plan's repro ad hoc: a successful re-scrape replaces the row and rebuilds nav; an errored one keeps the prior row and nav.

#### joan — 2026-10-06T05:07:31.326Z
[board-joan]  CANON: OK

#### betty — 2026-10-06T05:07:01.077Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/gazer.md + core/roster.md — broken tests + missing repro coverage — `test_gazer.py::TestFetchJobPagesBatch::test_additive_skips_already_scraped_url` (asserts single scrape of new URL only) and `test_roster.py::TestAst719PjlRosterHelpers::test_merge_pjl_scrape_record_skips_duplicate_and_empty` (first assert expects duplicate discarded) flip under the upsert; no existing node covers the AST-1995 repro (re-scrape replaces stored row in place, `pjl_assembled_content` drops OLD BOARD, `pjl_nav_links` rebuilt from this run, failed re-scrape keeps prior row + its nav links). gazer.py and roster.py are both LOCKED_AT_100, so new branches (upsert replace vs append, error-with-text discard, failure carry-forward with/without prior row) need coverage; gazer.md L49 `skipped-already-scraped` prose goes stale.

#### hedy — 2026-10-06T05:05:59.731Z
`origin/sub/AST-1994/AST-1995-fetch-refresh` @ `530379a94` · re-scrape all, upsert per URL

---

_Implementation detail may live in git history on `origin/dev`._

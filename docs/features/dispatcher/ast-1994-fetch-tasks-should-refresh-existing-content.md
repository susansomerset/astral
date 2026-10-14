# AST-1994 — fetch_ tasks should refresh existing content

<!-- linear-archive: AST-1994 archived 2026-10-13 -->

## Linear archive (AST-1994)

**Archived:** 2026-10-13  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1994/fetch-tasks-should-refresh-existing-content  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

I believe the fetch\_ tasks check if the content exists first, and if it does, it skips the fetch.  This is a problem when fetching time-sensitive content like job boards.

---

## As-is

Two `fetch_` gazer tasks short-circuit on content already stored on the company row, so a re-run never sees fresh content:

* `fetch_job_pages` (job boards — the time-sensitive one): `fetch_job_pages_batch` in `src/core/gazer.py` builds a ledger from `company_data.pjl_scrape_pages` (`_pjl_scrape_ledger_keys`) and only scrapes URLs in `possible_joblist_links` that are **not** already in it (debug outcome `skipped-already-scraped`). `_merge_pjl_scrape_record` in `src/core/roster.py` also refuses to overwrite a URL that's already recorded. Net effect: once a careers page has been captured, its `visible_text` is frozen forever, and `pjl_assembled_content` (what `select_job_page` reads) keeps serving the stale board. `pjl_nav_links` is merge-append only, so links that vanished from the board stick around. This "additive skip" was by design in AST-719 AC3.
* `fetch_culture_pages`: `fetch_culture_pages_batch` passes the job straight to `CULTURE_READY` when `company_data.website_content` already has page bodies (`_website_content_is_recorded`, AST-874 "cache path"). It never re-scrapes.

Already OK: `fetch_jd` and `fetch_website` re-scrape on every claim. [AST-1810](https://linear.app/astralcareermatch/issue/AST-1810/fetch-website-availclaim-skip-website-found-retry-rows-with-homepage) already removed the matching skip from `fetch_website`, so that change is the precedent for this one.

## To-be

Every `fetch_job_pages` run re-scrapes every URL in `possible_joblist_links` and replaces that URL's stored page record with the fresh capture. `pjl_assembled_content` (and nav links) then reflect what the board shows **now**. **Open for Susan:** should `fetch_culture_pages` also always refresh, or keep its cache? Culture pages aren't time-sensitive the way job boards are.

## Proposed steps

1. `fetch_job_pages_batch`: drop the ledger-based `pending` filter and the `skipped-already-scraped` debug branch. Scrape every candidate URL on every run.
2. `_merge_pjl_scrape_record`: change the duplicate-URL early return into a replace-in-place (upsert by `normalize_link`) so a fresh capture overwrites the old row and keeps its position. **Open for Susan:** if a re-scrape fails or comes back empty, should we keep the prior row (stale but present) or drop it (honest but empty)? My read is to keep the prior row on failure and replace it on success.
3. `pjl_nav_links`: rebuild from this run's page links instead of merge-appending onto the old value, so dead links fall off. This only follows if step 2 is "replace".
4. `pjl_assembled_content` already rebuilds from `pjl_scrape_pages` after the loop, so no change is needed beyond feeding it refreshed rows.
5. (Only if Susan says yes to culture refresh) `fetch_culture_pages_batch`: remove the `_website_content_is_recorded` cached-pass short-circuit so it always goes through `get_company_data(company, "website_content")`, and confirm that coat-check helper re-scrapes rather than returning cached content.
6. Clean up the now-unused `_pjl_scrape_ledger_keys` import/helper if nothing else calls it (today only `gazer.py` and `_merge_pjl_scrape_record` use it).

## Component scope

* `src/core/gazer.py` — modified: `fetch_job_pages_batch` stops skipping already-scraped URLs. If culture refresh is approved, `fetch_culture_pages_batch` also loses its cached-pass branch.
* `src/core/roster.py` — modified: `_merge_pjl_scrape_record` changes from skip-if-present to replace-if-present. `_pjl_scrape_ledger_keys` may become unused and get removed. If culture refresh is approved, `get_company_data`'s `website_content` coat-check path gets checked for its own cache short-circuit.

Tests (`tests/component/core/test_gazer.py`, `test_roster.py` additive-skip cases) are Betty's tree. The AST-719 additive-skip assertions will flip, so `qa-fix` should expect that.

## Technical scope

* `src/core/gazer.py`: **modified function** `fetch_job_pages_batch`. It scrapes the full `possible_joblist_links` set each run instead of the ledger-filtered `pending` subset, because the skip is the bug. **Modified function** `fetch_culture_pages_batch` (conditional on Susan's answer). The cached-pass branch goes away so `website_content` is refreshed on each run.
* `src/core/roster.py`: **modified function** `_merge_pjl_scrape_record`. A record for an already-recorded URL replaces the existing row instead of being discarded, so refreshed board text actually persists. **Possibly removed function** `_pjl_scrape_ledger_keys`, once it has no callers. No new tables or fields: `pjl_scrape_pages`, `pjl_assembled_content`, and `pjl_nav_links` keep their current shapes.

## Ancestor candidates

- [X] [AST-719](<https://linear.app/astralcareermatch/issue/AST-719>) — fetch_job_pages gazer batch and PJL_READY state. This one introduced the additive skip ledger (AC3) and `_merge_pjl_scrape_record`. Strongest match for the job-board symptom.
- [ ] [AST-874](<https://linear.app/astralcareermatch/issue/AST-874>) — fetch_culture_pages gazer task and CULTURE_READY gate. This one introduced the `website_content` cache path. Relevant only if culture refresh is in scope.
- [ ] [AST-759](<https://linear.app/astralcareermatch/issue/AST-759>) — shared page scrape for fetch_job_pages nav links. It reworked the shared PJL page scrape that `fetch_job_pages` uses for page records and nav links.
- [ ] [AST-1564](https://linear.app/astralcareermatch/issue/AST-1564) — audit get_company_data. Its doc references the `website_content` cache that culture refresh would go through.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._

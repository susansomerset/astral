# AST-716 — find_job_page logic confirmation

<!-- linear-archive: AST-716 archived 2026-07-22 -->

## Linear archive (AST-716)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-716/find-job-page-logic-confirmation  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Roster job-page discovery today collapses prefilter output, PJL scraping, AI page selection, and parse into a single `find_job_page` dispatch hop. That makes failures hard to diagnose (see [AST-666](https://linear.app/astralcareermatch/issue/AST-666/find-job-page-is-well-and-truly-borked) — **duplicate of this epic**), skips observable intermediate states, and mixes "possible careers URLs from prefilter" with "confirmed job list page" before `job_site` is set. Susan wants the **PREFILTER_PASSED** path refactored into the same **multi-step dispatch pattern as** `prefilter_company`: separate schedulable tasks, explicit company states between hops, persisted **hydrated normalized URL lists** for circular-link avoidance, and reuse of existing locate/parse helpers—not new architecture. Outcome: a company with prefilter-approved PJL candidates moves through scrape → AI selection → DOM-backed parse with clear terminal states and UAT-friendly debug when `debug=True`.

## Functional scope

* **Prefilter outcome routing (before PJL work):** When prefilter completes for a company entering the watch path, route by rubric and PJL list:
  * Empty possible-job-link set **and** no dealbreaker **F** in rubric → `NO_PREFILTER_JOBLISTS` (new terminal/holding state—distinct from "scrape failed later").
  * Dealbreaker **F** → existing `PREFILTER_FAILED` (reuse; no new failure state name).
  * Non-empty PJL set, pass → `PREFILTER_PASSED` with persisted candidate data; `job_site` remains unset until a list page is confirmed.
* **Normalized PJL URL registry:** At persistence time, **hydrate** prefilter PJL selections into `possible_joblist_links` — an ordered list of **normalized URLs** (nav **indices** were early prompt-encoding only; do not store indices in DB). Use this list for deduplication and circular-reference detection when the agent or scraper proposes additional links; advance to the next URL in the list rather than revisiting an already-tried normalized URL.
  * (I want the normalize_link() to be in the utils/formatting.py file, because it is just parsing off the protocol and file names and extraneous slashes, a pure string function.)
* `fetch_job_pages` **(new dispatch step):** Gazer-style batch scrape of each URL in `possible_joblist_links`, mirroring the homepage scrape pattern. **Additive:** skip URLs whose visible text is already captured; append new PJL visible text and discovered nav links without overwriting prior PJL content. On success → `PJL_READY` with assembled PJL visible text and accumulated nav links per URL.
* `select_job_page` **(dispatch step):** Send assembled PJL visible text to the agent. Outcomes:
  * **Confirmed list page:** selected PJL index + job titles found in visible text → `JOBLIST_IDENTIFIED` (list located, `job_site` still not final until parse succeeds).
  * **Try more links:** agent returns candidate URLs not already in `possible_joblist_links` → scrape/retry path → `PREFILTER_PASSED_RETRY`; no new unique links → `NO_PJL_SELECTED`.
* **DOM load +** `parse_job_list` **(dispatch step):** After `JOBLIST_IDENTIFIED`, Playwright reloads the selected list URL's DOM. Single-title case: trim to the matching container; multi-title case: smallest DOM subtree containing all reported titles (existing behavior). Feed culled DOM to `parse_job_list`. Success → `WATCH`; parse failure with retry → `JOBLIST_IDENTIFIED_RETRY` then `COULD_NOT_PARSE_JOBLIST`.
* **Dispatch decomposition:** Split today's monolithic `find_job_page` entry into separate `dispatch_tasks` rows and `run_company_task` routing per hop—same triple `(candidate_id, task_key, trigger_state)` pattern as `prefilter_company` / **PREFILTER_PASSED** trio (**AST-535**). Each hop is independently schedulable and inspectable in Execution History.
* **Reuse mandate (planning constraint, not new code patterns):** Child plans must explicitly wire existing roster locate/parse helpers and `run_next` chain from **AST-469**, prefilter persistence from **AST-507**, inflow dispatch wiring from **AST-508**, job-site preservation rules from [AST-673](https://linear.app/astralcareermatch/issue/AST-673/preserve-job-site-on-find-job-page-failure-companyjob-site-is), and careers-list scrape readiness / `JOBSITE_SCRAPE_ISSUE` handling from [AST-689](https://linear.app/astralcareermatch/issue/AST-689/dynamic-careers-list-scrape-readiness-job-site-scrape-is-too-fast) / [AST-692](https://linear.app/astralcareermatch/issue/AST-692/jobsite-scrape-issue-response-and-terminal-roster-flow-job-site-scrape). No parallel scrape, parse, or state-transition implementations.
* **Debug logging (when** `debug=True`**):** Per **AST-538** / Code Rules §1.5.1 on every touched roster hop: Style D index headers (`index N/M`, primary identifier, outcome), `|` detail lines for what was found vs recorded per PJL URL and per AI outcome, truncated long payloads; batch summaries must not replace per-index detail.

## Boundaries

* Does **not** replace or rename the `prefilter_company` task or encoded rubric shape (**AST-507**).
* Does **not** change manual `IMPORTED` entry or unrelated roster states outside this PJL-discovery chain.
* Does **not** set `job_site` until a list page is confirmed through the selection + parse path; does not regress [AST-673](https://linear.app/astralcareermatch/issue/AST-673/preserve-job-site-on-find-job-page-failure-companyjob-site-is) "preserve verified job_site on failure."
* Does **not** introduce new LLM task shapes, new external integrations, or UI work.
* [AST-666](https://linear.app/astralcareermatch/issue/AST-666/find-job-page-is-well-and-truly-borked) is a **duplicate of this epic** — fold here; do not dispatch separately.
* `JOBS_FOUND` / stored distinct `job_site` recheck path may remain on the existing **AST-469** chain unless Susan expands scope later.

## Acceptance criteria

1. After prefilter on the in-scope watch path: empty PJL + no dealbreaker **F** → `NO_PREFILTER_JOBLISTS`; dealbreaker **F** → `PREFILTER_FAILED`; non-empty PJL + pass → `PREFILTER_PASSED` with `possible_joblist_links` populated as hydrated normalized URLs.
2. `fetch_job_pages` is a separate dispatch task from `select_job_page` / `parse_job_list`; each hop appears as its own Execution History batch when run from Scheduled Actions.
3. `fetch_job_pages` is additive: re-run does not duplicate visible text for URLs already scraped; new PJL nav links append without wiping prior PJL data; success lands in `PJL_READY`.
4. `select_job_page` transitions match Susan's brief: confirmed titles → `JOBLIST_IDENTIFIED`; new links → `PREFILTER_PASSED_RETRY`; exhausted candidates → `NO_PJL_SELECTED`; proposed URLs dedupe against `possible_joblist_links`.
5. Post-`JOBLIST_IDENTIFIED`, parse uses Playwright DOM reload + existing single/multi-title container trimming; success → `WATCH` with parse tags as today; failure → `JOBLIST_IDENTIFIED_RETRY` / `COULD_NOT_PARSE_JOBLIST` per retry rules in config.
6. With `debug=True`, Susan can trace each PJL URL scrape, selection outcome, and parse hop using Style D index headers and `|` detail lines without reading production-only aggregate logs.
7. Child implementation plans cite reuse of existing roster helpers (no duplicate scrape/parse/state modules) and pass `validate-plan`.

## Dependencies and blockers

* **AST-507**, **AST-508** (prefilter + inflow dispatch) — Done.
* **AST-469**, **AST-461** (locate/parse split, `run_next`, `JOB_LIST_VISIBLE`) — Done.
* **AST-535** (PREFILTER_PASSED `task_key` routing on `dispatch_tasks`) — required pattern; verify Done on `origin/dev` before dispatch.
* [AST-673](https://linear.app/astralcareermatch/issue/AST-673/preserve-job-site-on-find-job-page-failure-companyjob-site-is), [AST-674](https://linear.app/astralcareermatch/issue/AST-674/job-site-aware-find-job-page-and-dispatch-agent-data-inspection-find) (job_site preservation and distinct verified URL gate) — Done; must not regress.
* [AST-689](https://linear.app/astralcareermatch/issue/AST-689/dynamic-careers-list-scrape-readiness-job-site-scrape-is-too-fast), [AST-692](https://linear.app/astralcareermatch/issue/AST-692/jobsite-scrape-issue-response-and-terminal-roster-flow-job-site-scrape) (dynamic scrape readiness, `JOBSITE_SCRAPE_ISSUE`) — Done; `fetch_job_pages` scrapes must honor same readiness terminal behavior.
* [AST-666](https://linear.app/astralcareermatch/issue/AST-666/find-job-page-is-well-and-truly-borked) — **duplicate of this epic**.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| [AST-716](https://linear.app/astralcareermatch/issue/AST-716/find-job-page-logic-confirmation) (parent) | ftr/AST-716-find-job-page-logic-confirmation |
| [AST-718](https://linear.app/astralcareermatch/issue/AST-718/prefilter-routing-company-states-and-pjl-url-hydration-find-job-page) | sub/AST-716/prefilter-routing-and-pjl-url-hydration |
| [AST-719](https://linear.app/astralcareermatch/issue/AST-719/fetch-job-pages-gazer-batch-and-pjl-ready-state-find-job-page-logic) | sub/AST-716/fetch-job-pages-batch-scrape |
| [AST-720](https://linear.app/astralcareermatch/issue/AST-720/select-job-page-dispatch-refactor-find-job-page-logic-confirmation) | sub/AST-716/select-job-page-dispatch-refactor |
| [AST-721](https://linear.app/astralcareermatch/issue/AST-721/parse-job-list-dispatch-refactor-and-monolith-removal-find-job-page) | sub/AST-716/parse-job-list-dispatch-refactor |

**Epic worktree:** `astral-AST-716/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | b78935dc-5bdf-493a-84fb-6600a876b711 |
| Betty | qa | c9ba961d-cb55-4e73-a67a-e2c338c940cf |
| Radia | review | 32b7e2cc-efda-4324-8702-ece530b694ff |

## Resolved (Susan 2026-06-17)

1. Truncated brief — **Fixed** (full flow in Original brief; success terminal remains `WATCH` via existing `parse_job_list`).
2. **Reuse** `PREFILTER_FAILED` — no new `FAILED_PREFILTER` state.
3. `possible_joblist_links` — persist **hydrated normalized URLs**; nav indices were prompt-encoding only.
4. **Replace** `TO_WATCH` **with** `PREFILTER_PASSED` on this path.
5. [AST-666](https://linear.app/astralcareermatch/issue/AST-666) — **duplicate of this epic**.

---

## Original brief

For each company in "TO_WATCH", there should be a set of possible job links in the company data's content.  If that array comes back from prefilter as empty AND the company didn't have an F in the rubric results, then the state should go to "NO_PREFILTER_PJL" state for the company, otherwise it gets "FAILED_PREFILTER" or "TO_WATCH".  we need to add company_data.possible_joblist_links= [<normalized url>, <normalized url>] so that circular references can be detected and move on to the next link in the prefilter's list of pjls.

For "TO_WATCH", we do NOT have a jobsite CONFIRMED, so the company.job_site is still null, just one or more possible links to the job page from the homepage are identified in company_data.  Those go through `fetch_job_pages`, a gazer-based task that does the same thing for the Possible Job List links as it did for the homepage.  this task is ADDITIVE, so it makes sure it hasn't already loaded the content for a url, but it also doesn't overwrite the old list, it just adds to the array of visible text from the scraped pjl. Then the company is in "PJL_READY", including all the navlinks for what is found on each PJL selection.

Then we call `select_job_page` that sends the array pjl visible text content to the agent, who returns with either a definite selection and job titles found on the page, or a list of url links to click into that might have the list shown (e.g. "view open positions" link to an ATS on the [www.company.com/jobs](<http://www.company.com/jobs>) page), verifying that the links are not already in company_data.possible_job_links, and the state would be set to "TO_WATCH_RETRY" or "NO_PJL_SELECTED".

If the agent confirms that a pjl is the page we want, then it will respond with the array index and a list of job titles it found in the text that we should be able to match to in our parser, and the company state becomes "JOBLIST_IDENTIFIED"

Then we use playwright to go back and load the dom content for the selected joblist url, trimming down in case 1 where there's only one job title to parse for, returning the body dom set to the Laslo agent for 'parse_job_list', or in case 2 where there are more than one job title, sending the smallest element that includes all the job titles (this logic should already exist) to `parse_job_list`, and get the parse tags from there as we do today, with either "WATCH" in the success state or "JOBLIST_IDENTIFIED_RETRY" > "COULD_NOT_PARSE_JOBLIST".

This is a refactor of the current process, but a lot of the logic (and code) is extant.  I want this plan to call out specifically where the devs should reuse functions and not generate their own.  There are ZERO new patterns in this design, it is reusing the pattern we just established with the prefilter_company task.

This way, there are potential actions for "NO_PREFILTER_PJL" and "NO_PJL_SELECTED" (we can do a secondary Google CSE search for the careers for that company, might just be on ycombinator or other site, not their homepage), but those actions are out of scope for this ticket.

### Comments

#### chuckles — 2026-06-18T04:19:29.790Z
[check-linear] User Testing — prompt + dispatch cutover notes (@susan)

**Where:** Admin → **Manage Tasks** (prompt prose only — `response_schema` stays in `TASK_CONFIG`; engineers already wired states).

### Tasks that need prompt review

| task_key | Change? | What to tell Grace |
|----------|---------|-------------------|
| **prefilter_company** | Verify only | Encoded rubric + bracket **link_set** tails (`000|RCD3|…|[59,60]|[51,46]`) — should match AST-697/707. No PJL scrape language here. |
| **select_job_page** | **Yes — main edit** | Input is **pre-scraped PJL sections** (`pjl_assembled_content` from `fetch_job_pages`), not a live homepage scrape. Each section is a numbered candidate careers URL + visible text. Teach: **`JOBLIST_TITLES`** → `selected_page` (index into those sections) + `job_titles` (strings visible on that page); **`TRY_LINKS`** → URLs to try next (must not duplicate `possible_joblist_links` ledger); **`JOBLIST_NO_JOBS`**; **`JOBSITE_SCRAPE_ISSUE`** (shell-only page — AST-692). Selection lands **`JOBLIST_IDENTIFIED`** — **does not** set `job_site` yet. |
| **parse_job_list** | Light touch | Runs **after** selection from **`JOBLIST_IDENTIFIED`**. Input is culled DOM for the chosen list URL + stored `job_titles`. Output unchanged: `job_container`, `job_tag`, `job_ids`. Success → **`WATCH`** (first `job_site` write). |
| **fetch_job_pages** | **None** | Gazer batch only — no LLM task / no Manage Tasks row. |

### Scheduled Actions (required before live UAT — Radia AST-721)

**Disable** legacy **`find_job_page`** rows (`TO_WATCH` / `PREFILTER_PASSED` trio).

**Seed decomposed pipeline** (one row each unless noted):

| task_key | trigger_state |
|----------|---------------|
| fetch_website | WEBSITE_FOUND |
| prefilter | HOMEPAGE_READY |
| fetch_job_pages | PREFILTER_PASSED |
| fetch_job_pages | PREFILTER_PASSED_RETRY |
| select_job_page | PJL_READY |
| parse_job_list | JOBLIST_IDENTIFIED |
| parse_job_list | JOBLIST_IDENTIFIED_RETRY |

Keep **`score_floor`** on inflow **`PREFILTER_PASSED`** locate rows if you use it today (AST-508 pattern). **`JOBS_FOUND`** stored-URL path unchanged — no prompt work there.

— Chuckles

#### susan — 2026-06-18T04:16:07.880Z
@chuckles I need instructions what and how to update prompt content for the new flow.

#### chuckles — 2026-06-17T23:47:30.024Z
[check-linear] Discussion — definition updated per your answers; move to Todo when approved (@susan)

#### chuckles — 2026-06-17T23:47:14.679Z
[check-linear] Discussion — definition updated per your answers; AST-666 marked duplicate; approve for dispatch (@susan)

#### susan — 2026-06-17T23:45:15.168Z
1. Fixed
2. Reuse existing PREFILTER_FAILED.
3. Actually, we should "hydrate" the links instead of storing the indices in the database.  Indices were just an early form of prompt output encoding.
4. Hmm.  Yes, we should replace "TO_WATCH" with "PREFILTER_PASSED", it's consistent.
5. OH RIGHT!  I forgot about 666.  Yes, it is a duplicate of this issue.

#### chuckles — 2026-06-17T22:36:33.184Z
@susan — open questions before dispatch:

1. Brief ends at “Laslo would then …” — what happens after successful `parse_job_list` beyond `WATCH`?
2. `FAILED_PREFILTER` vs existing `PREFILTER_FAILED` — new name or reuse?
3. `possible_joblist_links` (normalized URLs) vs today’s `possible_job_links` (nav indices) — replace or both during migration?
4. Scope: `TO_WATCH` only, or also `PREFILTER_PASSED` inflow and `JOBS_FOUND` / verified `job_site` paths?
5. Fold **AST-666** into this epic or keep separate?

— Chuckles

#### chuckles — 2026-06-17T22:34:07.836Z
@susan

1. Original brief is truncated mid-sentence at "Laslo would then " — please complete the intended ending.
2. **AST-666** ("Find Job Page is well and truly borked"): merge into this epic, block dispatch until fixed, or stay a separate bug track?
3. State naming: confirm authoritative set — **NO_PREFILTER_JOBLISTS**, **FAILED_PREFILTER**, **PJL_READY**, **TO_WATCH_RETRY**, **NO_PJL_SELECTED**, **JOBLIST_IDENTIFIED**, **JOBLIST_IDENTIFIED_RETRY**, **COULD_NOT_PARSE_JOBLIST** vs reusing **PREFILTER_FAILED**, **NO_JOBLIST**, etc.
4. Does the full decomposed PJL flow apply identically to **PREFILTER_PASSED** (inflow) and legacy **TO_WATCH**, or only **TO_WATCH**?
5. Dispatch task keys: retire **find_job_page** for a new scrape key (**fetch_job_pages** per brief), or keep **find_job_page** as scrape-only with existing **select_job_page** / **parse_job_list** rows?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._

# AST-2168 — Add Universal Entity Search

<!-- linear-archive: AST-2168 archived 2026-10-16 -->

## Linear archive (AST-2168)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2168/add-universal-entity-search  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Today the only way to find a job, company, or meteorite is to know which list it sits on and scroll for it. When Susan has an id in hand — an `astral_job_id` from a log line, a `company_job_id` from a listing, a meteorite id from an email — there's no place to paste it. This epic adds one search box that finds any job, company, or meteorite for the selected candidate by any string. Results are a list page grouped by entity type. Within each group, matches on the entity's own fields (ids, title, name, link, state) come first, and matches found only inside the stored payload (job data, company data, meteorite content) come after. Every result opens the same modal Susan would get from the list page that entity lives on, so search is a shortcut into the app, not a second view of it.

## Functional scope

1. **Search box.** A search input on the nav panel proper — inside the scrolling menu, above the Jobs category — so it scrolls under the selected candidate rather than sitting fixed with the picker. Submitting a non-blank string opens the Search results page for that string. The string lives in the page URL (`/search?q=…`), so a results page can be bookmarked or shared.
2. **Always the selected candidate.** Results only ever include jobs, companies, and meteorites owned by the candidate selected in the sidebar. Changing the candidate re-runs the search for the new candidate. With no candidate selected, the page asks for one and runs no search.
3. **Any string, literally.** Matching is case-insensitive substring. `%` and `_` in the search string are literal characters, not wildcards. There is no minimum length and no cap on how many results come back.
4. **Grouped by entity type.** The results page is a list page with one section per entity type, in the order Jobs, Companies, Meteorites. Each section has a heading with its match count. A type with no matches shows no section. "No results" shows only when all three are empty.
5. **Base fields first.** Each entity type has a list of base fields (its own columns: ids, title or name, link, state, …) and a list of payload fields (the stored JSON / text body). Within each section, every entity that matches on a base field is listed before every entity that matches only on a payload field, and most recently changed first within each tier. Each entity appears once, in its best tier.
6. **Result rows.** Each row shows a display name (job title + company for jobs, company name for companies, job title + employer for meteorites), the current state, and which field(s) matched.
7. **Click opens the right modal.** Clicking a result opens, on top of the results page, the modal for that entity type and state:
   * **Job** on Ready, Review, or Applied → the job report modal (`JobAnalysisReportModal`, the same one the `/jobs/detail/<id>` deeplink opens).
   * **Job** on Processing or Skipped (including a below-score-floor job, which shows on Skipped) → the job detail modal (`JobDetailModal`).
   * **Company** (any state) → `CompanyDetailModal`.
   * **Meteorite** (any state) → `MeteoriteDetailModal`.

   Which Jobs list a job belongs to is decided by the same config lists the Jobs pages use; it is never retyped. Closing or saving in a modal re-runs the search so states stay current.

## Component scope

* `src/utils/config.py` — **modified** — new search config: per entity type, its base fields and payload fields, and the Jobs-list → job-modal mapping.
* `src/data/database.py` — **modified** — new candidate-scoped search reads over `job`, `company`, and `meteorite`; header inventory notes them.
* `src/core/search.py` — **new** — orchestrates one search: runs the three reads, groups by entity type, tiers and orders the hits, names each job's Jobs list and modal.
* `src/ui/api/api_search.py` — **new** — `GET /api/search` route.
* `src/ui/server.py` — **modified** — registers the search blueprint.
* `src/ui/frontend/src/pages/SearchResults.tsx` — **new** — the grouped results list page and the modals it hosts.
* `src/ui/frontend/src/routes.tsx` — **modified** — adds the `search` route (deeplink-only, like `jobs/detail/:jobId` — not a `NAV_CONFIG` item); header SYNC comment names it.
* `src/ui/frontend/src/components/NavigationShell.tsx` — **modified** — search input in the nav scroll area, above the Jobs group.
* `src/ui/frontend/src/App.css` — **modified** — sidebar search input and results styling.

## Technical scope

* `config.py`
  * **Search registry.** A new constant keyed by entity type (`job`, `company`, `meteorite`). Each entry holds the display label, the base field list, and the payload field list. Lists (confirmed by Susan, define round 1):
    * job — base: `astral_job_id`, `company_job_id`, `job_title`, `job_link`, `company_id`, `source_entity_id`, `state`, `batch_id`; payload: `job_data`.
    * company — base: `short_name`, `company_name`, `company_website`, `job_site`, `originating_search_term`, `state`, `batch_id`; payload: `company_data`.
    * meteorite — base: `id`, `astral_job_id`, `job_title`, `employer_name`, `link`, `electronic_contact`, `source_id`, `source_ref`, `state`, `batch_id`; payload: `content`, `classify_outcome`, `error`.
  * **Job modal map.** A new mapping from Jobs list (`ready`, `review`, `applied`, `processing`, `skipped`) to modal kind (`report` / `detail`). A module-level assert checks every Jobs list has exactly one modal kind.
* `database.py` — one new read (or one per table; `plan-child`'s call) that, for one candidate and one search string, returns every row whose configured base or payload fields contain the string (case-insensitive, `LIKE` with `%`/`_`/escape-char escaped), with which fields matched. Field lists come from the config registry, not from literals in SQL. Candidate scope is `candidate_id = ?` on all three tables. No `LIMIT`. The module header inventory lists the new read.
* `core/search.py` — new public function that takes the candidate id and search string, calls the new read(s), and returns the results keyed by entity type (`job`, `company`, `meteorite`), each an ordered list (base tier, then payload tier, most recently changed first within a tier); a type with no matches is an empty list. Each result has: entity id, display name, state, tier (`base` / `payload`), matched field names, and for jobs the Jobs list name and modal kind. A job's Jobs list is decided from `READY_JOB_STATES`, `REVIEW_JOB_STATES`, `APPLIED_JOB_STATES`, `SKIPPED_STATES`, processing as the complement, and below-floor via the existing `tracker` score-floor helpers (`score_floor_by_trigger_for_candidate`, `job_misses_dispatch_score_floor`). Debug lines at loop start/end per `stat.logging.debug`.
* `api_search.py` — new blueprint at `/api/search`, one `@require_auth` GET taking `q` and `candidate_id`. Blank `q` or missing `candidate_id` → 400 with an `error` message. Otherwise returns the core result (keyed by entity type) as JSON. Exceptions go through `server_error_from_exception` (logged once there). No info line — idempotent GET (`stat.logging.info.api`).
* `server.py` — registers the new blueprint beside the others.
* `SearchResults.tsx` — new page. Reads `q` from the URL and the selected candidate from `CandidateContext`. Fetches `/api/search` on `q` or candidate change. Renders one section per non-empty entity type, in the order Jobs, Companies, Meteorites, each with a heading and match count, rows in the order the API returned them (no client-side reordering of tiers). Columns: display name, state, matched field(s). Reuse the shared `ListPage` table look where it fits (`plan-child`'s call). Hosts `JobAnalysisReportModal`, `JobDetailModal`, `CompanyDetailModal`, and `MeteoriteDetailModal`, opening the one named by the result's entity type and (for jobs) modal kind. Re-fetches on modal close / save. Shows "Select a candidate" with no candidate, and "No results" when all three lists are empty.
* `routes.tsx` — adds the `search` path to the shell children; header comment notes it as deeplink-only (no `NAV_CONFIG` item).
* `NavigationShell.tsx` — adds a search input at the top of the `sidebar-scroll` area, above the first nav group (Jobs) — not in the fixed `sidebar-chrome` with the candidate picker. Shown in both wide and narrow (drawer) layouts. Submit (Enter) with a non-blank trimmed value navigates to `/search?q=<encoded>`. No search-as-you-type.
* `App.css` — styles for the sidebar search input and any results-page tweaks.

## Architectural definition

* **Patterns to reuse** — `no established pattern applies`. None of the 22 in-force directives under `canon/directives/active/` is a search, list-page, UI, or config-registry pattern. Following house practice anyway: field lists and the job-modal map live in config and are typed once; the results page reuses `ListPage` and the existing modals unchanged; the `search` route follows the `jobs/detail/:jobId` deeplink-only precedent.
* **New patterns proposed** — none.
* **Applicable statutes**
  * `stat.logging.debug` — the core search loops log begin/end counts through `get_logger(__name__)`. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)
  * `stat.logging.error` — a thrown exception in the search route is logged once, at the route handler, via `server_error_from_exception`; not again in core or data. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>)
  * `stat.logging.info.api` — the search GET is idempotent and only returns current state, so it emits **no** info line. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>)

**Canon Scope:** `stat.logging.debug`, `stat.logging.error`, `stat.logging.info.api` — locked at Discussion.

## Acceptance criteria

 1. **Candidate scope.** With candidates A and B each owning a job whose `job_title` contains `Zebra`, `GET /api/search?q=zebra&candidate_id=<A>` returns A's job and not B's. Same for a company and a meteorite. **Fail:** any row owned by another candidate.
 2. **Required params.** `GET /api/search?q=%20&candidate_id=<A>` and `GET /api/search?q=x` (no candidate) each return 400 with an `error` field. **Fail:** 200, or a 500.
 3. **Ids are findable.** For one job of candidate A, searching its full `astral_job_id`, its `company_job_id`, and a 6-character middle substring of its `astral_job_id` each returns that job as a `base` tier result. A meteorite's numeric `id` and its `astral_job_id` each return that meteorite as `base`. **Fail:** missing, or tier `payload`.
 4. **Base before payload.** Candidate A has job J1 with `job_title` containing `Quokka` and job J2 whose `job_data` (only) contains `quokka`. The response's `job` list has J1 (`tier: base`) before J2 (`tier: payload`), and each appears once. **Fail:** J2 before J1, a duplicate entity, or J1 tagged `payload`.
 5. **Case-insensitive, literal wildcards.** `q=QUOKKA` returns the same set as `q=quokka`. `q=%` returns only entities with a literal `%` in a searched field, and `q=_` only those with a literal `_` — not every row. **Fail:** a different set by case, or `%` / `_` matching everything.
 6. **No cap.** A candidate with 600 jobs whose `job_title` contains `Engineer` gets all 600 back for `q=engineer`. `rg -n "LIMIT" src/core/search.py` returns nothing, and the new read in `database.py` has no `LIMIT`. **Fail:** a truncated list or a `LIMIT`.
 7. **Field lists come from config.** `rg -n "company_job_id|originating_search_term|electronic_contact" src/core/search.py src/ui/api/api_search.py` returns nothing, and removing `job_link` from the job base list in config makes a job findable only by its link stop appearing. **Fail:** a field name hard-coded outside config, or the removal changes nothing.
 8. **Job modal by list.** For candidate A, one job each on Ready (`CANDIDATE_REVIEW`), Review (`RECOMMENDED`), an Applied state, a Processing state, a Skipped state, and a Processing-state job below its dispatch score floor: the API's Jobs list for each is `ready`, `review`, `applied`, `processing`, `skipped`, `skipped`, and modal kind is `report` for the first three and `detail` for the last three. Clicking each in the UI opens `JobAnalysisReportModal` or `JobDetailModal` to match. **Fail:** any mismatch.
 9. **Company and meteorite modals.** Clicking a company result opens `CompanyDetailModal` for that `short_name`. Clicking a meteorite result opens `MeteoriteDetailModal` for that id. **Fail:** wrong modal, wrong entity, or a page navigation away from results.
10. **Search box placement and URL.** The search input renders inside `.sidebar-scroll`, directly above the Jobs nav group, and not inside `.sidebar-chrome`; scrolling the nav panel scrolls it under the candidate picker. **Fail:** the input sits in `.sidebar-chrome`, below Jobs, or stays fixed while the menu scrolls. Typing `acme` in the box and pressing Enter lands on `/search?q=acme` with results. Reloading that URL shows the same results. Pressing Enter on a blank box does nothing. **Fail:** no navigation, empty results on reload, or a request with blank `q`.
11. **Grouped by type.** `GET /api/search` returns an object whose keys are exactly `job`, `company`, `meteorite`, each a list. For a string matching two jobs and one meteorite but no company, the page shows a Jobs (2) section then a Meteorites (1) section, and no Companies section. A string matching nothing shows "No results" and no section headings. **Fail:** other keys, a Companies heading, wrong order or count, or an empty section heading.
12. **Candidate switch.** On `/search?q=acme`, switching the sidebar candidate from A to B re-fetches and shows only B's results. With no candidate selected, the page shows "Select a candidate" and no `/api/search` request is made. **Fail:** A's results remain, or a request goes out with no candidate.
13. **Modal close refreshes.** Moving a company's state in `CompanyDetailModal` and closing it updates that row's State column on the results page without a reload. **Fail:** stale state.
14. **No info line.** `rg -n "logger.info" src/ui/api/api_search.py src/core/search.py` returns nothing. **Fail:** any hit.
15. **Builds clean.** From repo root, `PYTHONPATH=.:src python -c "import src.utils.config, src.core.search, ui.api.api_search"` exits 0. In `src/ui/frontend`, `npm run build` exits 0 and `npm run lint` reports no problem absent on `origin/dev`. **Fail:** non-zero exit or a new lint problem.

## Open questions

none

## Proposed child tickets

#### 1!: **Search backend: config, reads, core, route - Ada**

Delivers `GET /api/search`: the config search registry and job-modal map, the candidate-scoped `job`/`company`/`meteorite` reads, the core function that tiers/orders hits and names each job's Jobs list and modal kind, and the route + blueprint registration. Does **not** touch any frontend file (#2).
**Citations:** `stat.logging.debug`, `stat.logging.error`, `stat.logging.info.api`.
**Scope:** `src/utils/config.py`, `src/data/database.py`, `src/core/search.py`, `src/ui/api/api_search.py`, `src/ui/server.py`. Technical scope: the `config.py`, `database.py`, `core/search.py`, `api_search.py`, and `server.py` items above, verbatim.
Estimate: 3

#### 2: **Sidebar search box and results page - Hedy**

After #1. Delivers the nav-panel search input (above Jobs), the `/search?q=…` route, and the results list page that renders #1's per-type lists as Jobs / Companies / Meteorites sections and opens the right existing modal per result. Does **not** own matching, ordering, or the job-modal decision — it renders what #1 returns.
**Citations:** none — no in-force directive governs React pages or routes.
**Scope:** `src/ui/frontend/src/pages/SearchResults.tsx`, `src/ui/frontend/src/routes.tsx`, `src/ui/frontend/src/components/NavigationShell.tsx`, `src/ui/frontend/src/App.css`. Technical scope: the `SearchResults.tsx`, `routes.tsx`, `NavigationShell.tsx`, and `App.css` items above, verbatim.
Estimate: 3

**Monolith check:** Functional scope N = 7, children M = 2, split by layer (backend search vs. React surface).
**Scope partition check:** `config.py`, `database.py`, `core/search.py`, `api_search.py`, `server.py` → #1. `SearchResults.tsx`, `routes.tsx`, `NavigationShell.tsx`, `App.css` → #2. No file is unclaimed and none is claimed twice.

---

## Original brief

Search for jobs, companies and meteorites by any string.  Search the entity base fields first, and the search results should hyperlink to the modal for that entity type and state.  This includes the astral_job_id and other internal UUID's as well as company_job_id and any other string.  Filter the results on the selected candidate always.

**Answers (Susan, define round 1), to Open questions 1–4 in order:**

1. (Project set to Astral Interface in Linear.)
2. I want the search bar to scroll under the selected candidate, so it should be on the nav panel, proper, above the jobs category of the menu.
   Search results should be a list page with matches by entity type.  Show Jobs, Companies, and Meteorites where a match was found.
3. Yes.
4. Yep.

### Comments

#### chuckles — 2026-10-12T23:17:43.374Z
AST-2173 REVIEW — Radia discuss on stat.logging.debug callee pair around search_entity_rows (default: keep loop-only); routing to Ada resolve-child.

#### chuckles — 2026-10-12T22:28:42.935Z
@susan

1. **Project.** This ticket has no Linear project. Astral Interface?
2. **Where the box lives.** Proposed: a search input in the left sidebar under the candidate picker, opening a `/search?q=…` results page that hosts the modals. Alternative: a header bar, or a dropdown of results under the box with no page. Sidebar + page OK?
3. **"Base fields first" and which fields.** Read as: base-field matches ranked above payload-only matches, both shown, no cap. Field lists are in Technical scope › Search registry. Deliberately **not** searched: `state_history`, timestamps, and the compressed stores (`telescope_data`, `agent_data`, `artifact`). Right reading, and are those lists right?
4. **Applied jobs.** The Applied page has no row modal today. Proposed: Applied jobs open the job report modal, same as the `/jobs/detail/<id>` deeplink does for any state. OK?

---

_Implementation detail may live in git history on `origin/dev`._

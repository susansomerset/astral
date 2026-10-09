# AST-1971 — Add Created to the job list table

<!-- linear-archive: AST-1971 archived 2026-10-08 -->

## Linear archive (AST-1971)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1971/add-created-to-the-job-list-table  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The Jobs list tables show when a job last changed state (**Updated**) but not when the job first entered the pipeline. A candidate can't tell a fresh listing from one that has sat around for weeks, or sort by age to work through the newest (or stalest) first. This epic adds a sortable **Created** column, showing the job's `created_at`, to every Jobs list. On Meteorites that means the landed job's creation time. The job list pages already receive `created_at`, so those are display-and-sort only. Meteorites needs the landed job's `created_at` added to its list response.

## Functional scope

1. **Created column on job lists.** Every job-row table on **Ready**, **Review**, **Processing**, **Skipped** (both the regular and below-floor tables), and **Applied** shows a **Created** column with the job's creation timestamp. It is formatted the same way as **Updated** (candidate timezone, `—` when missing) and sits immediately left of the existing **Updated** / **Failed At** column.
2. **Sort by Created.** Clicking the **Created** header sorts that table by creation time, toggling ascending/descending like the other sortable headers, with missing values handled the same way **Updated** handles them. Each table's default sort stays as it is today (**Updated**, newest first).
3. **Created on Meteorites = landed job's** `created_at`**.** Jobs → Meteorites gets a sortable **Created** column, immediately left of **State Changed**, showing the **landed job's** `created_at` (not the meteorite row's own). Rows with no landed job show `—`.

**Decisions (Susan, Discussion):** this epic runs **after** [AST-1970](https://linear.app/astralcareermatch/issue/AST-1970) and targets the post-1970 pages. Meteorites uses the job's `created_at`, because the job / meteorite distinction is going away.

## Component scope

* `src/ui/frontend/src/pages/JobsRecommended.tsx` — **modified** — Created header + cell; `created_at` sort branch (serves Ready and Review after [AST-1970](https://linear.app/astralcareermatch/issue/AST-1970)).
* `src/ui/frontend/src/pages/JobsProcessing.tsx` — **modified** — Created header + cell; `created_at` sort branch. The file is **new in** [AST-1970](https://linear.app/astralcareermatch/issue/AST-1970), so this row assumes [AST-1970](https://linear.app/astralcareermatch/issue/AST-1970/jobs-navigation-changes) has landed.
* `src/ui/frontend/src/pages/JobsSkipped.tsx` — **modified** — Created header + cell in both table variants; `created_at` sort branch.
* `src/ui/frontend/src/pages/JobsApplied.tsx` — **modified** — Created header + cell; `created_at` sort branch.
* `src/data/database.py` — **modified** — the candidate meteorite list read also returns the landed job's `created_at`.
* `src/ui/api/api_meteorite.py` — **modified** — the list projection carries the landed job's `created_at`.
* `src/utils/config.py` — **modified** — the Meteorites list column config gains the Created column.

Job list pages need no backend change. `database.list_jobs` selects `SELECT * FROM job`, and `_flatten_grades` only adds keys, so every `GET /api/jobs?view=…` row already carries `created_at`, including the below-floor virtual rows on Skipped. `JobsMeteorites.tsx` needs no change: it renders whatever `JOBS_METEORITES_LIST_COLUMNS` the API returns, through `ListPage`, which already formats and sorts `type: "datetime"` columns.

## Technical scope

* `JobsRecommended.tsx` — the page's `Job` interface gains the optional `created_at` field. A new sortable header and `<Time>` cell go immediately before the Updated column. The existing `sortRecommendedJobs` gains a `created_at` branch with the same string-compare / null handling as its `state_changed_at` branch. Any column-count arithmetic (e.g. the Analysis expanded row's `colSpan`) is updated to match.
* `JobsProcessing.tsx` — the same `created_at` interface field, header, cell, and a branch in the page's existing sort function.
* `JobsSkipped.tsx` — the same interface field. The header + cell go in both the regular and the below-floor table variants, before the Updated / Failed At column, with a `created_at` branch in the existing `sortJobs`.
* `JobsApplied.tsx` — the same interface field, header, cell, and a `created_at` branch in the existing `sortAppliedJobs`.
* `database.py` — the candidate meteorite list read (`list_meteorites_for_candidate`) is modified to also return each row's landed job's `created_at`, joined via `astral_job_id`. That is the same lookup [AST-1970](https://linear.app/astralcareermatch/issue/AST-1970) adds for the landed job's state, extended by one field, not a second lookup. It goes under a **distinct key**, so the meteorite row's own `created_at` is not overwritten. The key name is `plan-child`'s call.
* `api_meteorite.py` — the list projection key set (`_LIST_KEYS`) is modified to include that landed-job created key.
* `config.py` — `JOBS_METEORITES_LIST_COLUMNS` gains one sortable `type: "datetime"` entry labelled **Created**, bound to the landed-job created key and placed immediately before `state_changed_at`.

Each job list page extends its **own existing** sorter. No new shared sort helper and no second sorter per page. Consolidating the four sorters is not part of this epic.

## Architectural definition

* **Patterns to reuse** — `no established pattern applies`. Of the 21 in-force directives (`canon_clerk.py index`), the only frontend pattern is `patt.artifact.ui-consistency`, which governs artifact editors. This epic edits no artifact surface.
* **New patterns proposed** — none.
* **Applicable statutes:**
  * [`stat.logging.error`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>) — the meteorite list route's existing exception handler wraps the extended read. It stays one `logger.exception` with live facts and no re-raise, and no new handler is added.
  * [`stat.logging.info.api`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>) — `api_meteorite.py` is in its territory. The list route is a GET, so no info line is added.
  * The epic **relies on** [`astral.entity.required-metadata`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.entity.required-metadata.md>), which guarantees `created_at` on every `job` row. The epic changes no table's column set, so it isn't cited as Canon Scope.

**Canon Scope:** `stat.logging.error`, `stat.logging.info.api` — locked at Discussion.

## Acceptance criteria

 1. **Column present on job lists.** On Ready, Review, Processing, Skipped (regular and below-floor tables), and Applied, every job table's header row contains a `Created` header immediately left of `Updated` (or `Failed At`). **Fail:** any in-scope table without it, or in a different position.
 2. **Value is the job's** `created_at`**.** For any row on those pages, the Created cell text equals `fmtTime(created_at, <candidate tz>)` for that job's `created_at` in the `GET /api/jobs?view=<page view>&candidate_id=X` response. A row whose `created_at` is null shows `—`. **Fail:** a cell showing `state_changed_at` / `updated_at`, a blank cell, or a timezone different from the Updated cell's.
 3. **Sorts by creation time.** Clicking `Created` once orders that table's rows by `created_at` with the same direction rule the Updated header uses on first click. Clicking again reverses it, and the sort indicator shows on Created. Null `created_at` rows are placed the same way Updated places null `state_changed_at`. **Fail:** any out-of-order pair, no reversal, or the indicator on another header.
 4. **Default sort unchanged.** On first load, each job list table is still sorted by `state_changed_at` descending, with the indicator on Updated / Failed At. **Fail:** the default switches to Created or anything else.
 5. **Extends existing sorters, no parallel path.** `rg -n "function sort" src/ui/frontend/src/pages/JobsRecommended.tsx src/ui/frontend/src/pages/JobsProcessing.tsx src/ui/frontend/src/pages/JobsSkipped.tsx src/ui/frontend/src/pages/JobsApplied.tsx` returns the same count as on `origin/dev` at branch point, and each file's `"created_at"` sort comparison sits inside that existing function. **Fail:** a new sorter function, or a sort for Created implemented outside the page's existing sorter.
 6. **Meteorites Created = landed job's** `created_at`**.** For every row in `GET /api/candidates/X/meteorites` with a non-null `astral_job_id`, the landed-job created value equals `SELECT created_at FROM job WHERE astral_job_id = <that id>`. Rows with no `astral_job_id` carry null, and the page shows `—`. The row's own `created_at` still equals `meteorite.created_at`. **Fail:** the meteorite's timestamp shown as Created, a mismatch with the job row, or the meteorite's own `created_at` overwritten.
 7. **Meteorites column via config, not page code.** The response's `columns` contains a `Created` entry with `type: "datetime"` and `sortable: true`, placed immediately before `state_changed_at`. On the page, clicking `Created` sorts the rows by that value. `git diff origin/dev -- src/ui/frontend/src/pages/JobsMeteorites.tsx` is empty. **Fail:** column missing / misplaced, unsortable, or a hardcoded column added in the page.
 8. **One landed-job lookup.** `list_meteorites_for_candidate` gets the landed job's state ([AST-1970](https://linear.app/astralcareermatch/issue/AST-1970)) and `created_at` from the same lookup: one join / query, not a second per-row fetch. **Fail:** a separate query or per-row `get_job` call added for `created_at`.
 9. **No new logging on the list route.** `git diff origin/dev -- src/ui/api/api_meteorite.py | rg "^\+.*logger\.(info|exception|warning|error)"` returns nothing. **Fail:** any hit.
10. **Builds clean; no new lint.** `python -c "import src.utils.config"` exits 0. In `src/ui/frontend`, `npm run build` exits 0, and `npm run lint` reports no problem that is absent on `origin/dev` (diff the problem lists). **Fail:** a non-zero exit, or any new lint problem.

## Open questions

none

## Proposed child tickets

#### 1: **Created column on Jobs list tables - Ada**

After [AST-1970](https://linear.app/astralcareermatch/issue/AST-1970) lands. Adds the sortable Created column (job `created_at`, left of Updated / Failed At, default sort unchanged) to every job table on Ready, Review, Processing, Skipped, and Applied. Each page extends its own existing sorter. Does not touch Meteorites (#2), any backend route, or config.
**Citations:** none — every file is under `src/ui/frontend/`, outside both statutes' territory.
**Scope:** `src/ui/frontend/src/pages/JobsRecommended.tsx` (Created header + cell; `created_at` branch in `sortRecommendedJobs`; column-count arithmetic); `src/ui/frontend/src/pages/JobsProcessing.tsx` (Created header + cell; `created_at` branch in its existing sorter); `src/ui/frontend/src/pages/JobsSkipped.tsx` (Created header + cell in both table variants; `created_at` branch in `sortJobs`); `src/ui/frontend/src/pages/JobsApplied.tsx` (Created header + cell; `created_at` branch in `sortAppliedJobs`). All four add the optional `created_at` field to the page's `Job` interface.
Estimate: 2

#### 2: **Meteorites Created from landed job - Hedy**

After [AST-1970](https://linear.app/astralcareermatch/issue/AST-1970) lands (it adds the landed-job lookup this extends). Delivers the landed job's `created_at` on the Meteorites list API and a config-driven, sortable Created column on Jobs → Meteorites. Does not touch any React file or the job list pages (#1).
**Citations:** `stat.logging.error` (the existing list handler wraps the extended read; no new handler); `stat.logging.info.api` (GET route, no info line added).
**Scope:** `src/data/database.py` (`list_meteorites_for_candidate` also returns the landed job's `created_at` under a distinct key, from the same lookup [AST-1970](https://linear.app/astralcareermatch/issue/AST-1970/jobs-navigation-changes) adds); `src/ui/api/api_meteorite.py` (`_LIST_KEYS` includes that key); `src/utils/config.py` (`JOBS_METEORITES_LIST_COLUMNS` gains a sortable `datetime` Created entry before `state_changed_at`).
Estimate: 2

**New patterns:** none.

**Monolith check:** Functional scope has 3 items across 2 children, split by layer: frontend job list pages (#1) and the Meteorites backend + config (#2). They are independent of each other, and both wait only on [AST-1970](https://linear.app/astralcareermatch/issue/AST-1970/jobs-navigation-changes).

**Scope partition check:** all seven Component scope files are claimed exactly once. #1 claims the four `pages/*.tsx` files and #2 claims `database.py`, `api_meteorite.py`, and `config.py`. Every Technical scope item maps to the child that owns its file.

---

## Original brief

Allow the user to view and sort by the job created date in the job lists.

### Comments

#### susan — 2026-10-04T20:50:00.833Z
My bad!  Forgot to merge the PR for 1970.

#### chuckles — 2026-10-04T20:29:12.780Z
@susan

Still not dispatched. [AST-1970](https://linear.app/astralcareermatch/issue/AST-1970) is at **User Testing**, but nothing from it is on `origin/dev` yet (`JobsInReview.tsx` is still there; `JobsProcessing.tsx` exists only on `origin/ftr/AST-1970-jobs-nav`).

There are two ways to go, and I need you to pick one:

1. **Wait (recommended).** Finish AST-1970's UAT and `finish-up`. Once it's **Done**, move this back to **Todo** and assign Chuckles, and dispatch runs cleanly off `dev`.
2. **Stack on AST-1970 now.** Cut `ftr/AST-1971` from `origin/ftr/AST-1970-jobs-nav` instead of `dev`. Our git workflow doesn't support this:
   * Joan / Radia diffs, `validate-sub-log`, and the prep-uat PR all compare against `dev`, so each would show AST-1970's changes as part of this epic.
   * Any UAT fix on AST-1970 would have to be merged into AST-1971 by hand.
   * AST-1971 couldn't land until AST-1970 does.

   Only choose this if you explicitly want to accept those costs.

#### chuckles — 2026-10-04T18:15:20.332Z
@susan

Not dispatched: this epic is blocked until [AST-1970](https://linear.app/astralcareermatch/issue/AST-1970) lands on `dev`, per the sequencing decision in the definition.

* AST-1970 is still **Todo** with no children, and none of its work is on `origin/dev` yet (`JobsInReview.tsx` is still there; `JobsProcessing.tsx` doesn't exist).
* Child 1 modifies `JobsProcessing.tsx` and the post-1970 Ready / Review `JobsRecommended.tsx`. Child 2 extends the landed-job meteorite lookup that AST-1970 adds in `database.py`. Branching either one off today's `dev` would build against files that don't exist yet.
* Both epics also overlap on hot files (`config.py`, `database.py`, `api_meteorite.py`).

When AST-1970 is **Done**, move this back to **Todo** and assign Chuckles, and dispatch will run against the new pages.

#### chuckles — 2026-10-04T16:19:41.936Z
@susan

1. **Sequencing with [AST-1970](https://linear.app/astralcareermatch/issue/AST-1970).** AST-1970 rewrites the same Jobs pages: it deletes In Review, adds Processing, and splits Recommended into Ready / Review. Should this epic (a) wait for AST-1970 and target the new pages (the current draft), (b) land now against today's pages and let AST-1970 carry the column forward, or (c) fold into AST-1970's child #2 and cancel this ticket?
2. **Meteorites.** Should Jobs → Meteorites get a Created column too? It would show the meteorite row's own `created_at` and adds `src/utils/config.py` to scope. The draft leaves Meteorites out because its rows aren't jobs.

---

_Implementation detail may live in git history on `origin/dev`._

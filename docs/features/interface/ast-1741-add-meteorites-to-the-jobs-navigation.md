# AST-1741 — Add "Meteorites" to the Jobs navigation

<!-- linear-archive: AST-1741 archived 2026-09-24 -->

## Linear archive (AST-1741)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1741/add-meteorites-to-the-jobs-navigation  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Operators need a Jobs-nav home for the selected candidate’s **meteorite staging rows** (AST-1557 spine) — not the Companies → Meteorite employer list, and not the Recommended-list “Meteorites” job partition. Today those rows are only reachable piecemeal (Manage Email land results, Recommended report Meteorite pane when a job already exists). This epic adds **Jobs → Meteorites**: a candidate-scoped list plus a read-only modal of full content and metadata so operators can scan ingress state, titles, and AI/classify payloads without hunting through other surfaces.

## Functional scope

* **Jobs → Meteorites nav.** An enabled sidebar item under Jobs labeled **Meteorites** routes to a dedicated page (path under `/jobs/…`). Companies → **Meteorite** (meteorite *companies*) stays unchanged and is out of scope.
* **Candidate-scoped list.** With a candidate selected, the page lists that candidate’s `meteorite` table rows that still exist (all `METEORITE_STATES` values; retention already decides what is gone). Empty candidate or empty result shows an empty list (no invented rows).
* **Read-only detail modal.** Row click opens a modal showing the meteorite’s **full content** and **metadata** (state, timestamps, link/breadcrumb, classify_outcome, content, provenance/source fields, job_title / employer_name when present, astral_job_id when set, error when present). No land / qualify / state-edit / paste actions on this page.
* **Optional job deeplink in the modal.** When `astral_job_id` is non-empty, the modal exposes navigation to the existing job detail deeplink (`/jobs/detail/:jobId`); when blank, no job link is shown.
* **Out of scope.** Changing Recommended’s meteorite-company partition, the Recommended report Meteorite tab (AST-1685), Manage Email Land Meteorite, retention, stage/scrape/land runners, Companies meteorite list, Responded nav, or nav badge counts for Meteorites.

## Component scope

* `src/data/database.py` — **modified** — candidate-scoped meteorite list read helper; header inventory note; reuse existing single-row `get_meteorite` for detail (no new write helpers).
* `src/utils/config.py` — **modified** — add Jobs → Meteorites to `NAV_CONFIG` (enabled); optional list-column / modal-section defs if the UI must stay config-driven rather than inventing order in TSX.
* `src/ui/api/api_meteorite.py` — **modified** — authenticated GET list (by candidate) and GET detail (by meteorite id) returning projected JSON for the list/modal; no new land/create routes.
* `src/ui/frontend/src/routes.tsx` — **modified** — register the Jobs Meteorites path to match `NAV_CONFIG` (SYNC comment on nav).
* `src/ui/frontend/src/pages/JobsMeteorites.tsx` — **new** — candidate-scoped meteorites list page (ListPage-style sibling to other Jobs lists).
* `src/ui/frontend/src/components/MeteoriteDetailModal.tsx` — **new** — read-only modal for full content + metadata (may compose shared field rendering with `JobMeteoritePane` patterns; does not own Recommended report tabs).
* `src/ui/frontend/src/App.css` — **modified** only if the modal/list needs chrome beyond existing list/report classes.

## Technical scope

* `database.py`: new list helper keyed by `candidate_id` → meteorite row dicts ordered by a stable recency field (`state_changed_at` or `updated_at` descending); blank/missing candidate returns empty without error; `get_meteorite(id)` remains the detail read.
* `config.py`: one new Jobs nav item `{label: "Meteorites", path: "/jobs/meteorites"}` (or equivalent path kept in SYNC with routes); if list columns / modal sections are config-owned, add named constants consumed by the API manifest or page — no inline state-set literals for “which states to show” (show all surviving rows).
* `api_meteorite.py`: GET list scoped to candidate_id (query or path param consistent with sibling candidate-scoped routes); GET detail by id with auth; project fields needed by list + modal; soft-fail/404 honesty for missing ids; progress/debug/error logging per cited statutes (idempotent GETs are not progress `info`).
* `routes.tsx` + `JobsMeteorites.tsx`: fetch list for `selectedId`, render columns, open modal on row click, refresh on candidate change.
* `MeteoriteDetailModal.tsx`: render full content (pretty-print JSON when parseable, else raw text) and metadata fields; http(s)-gate link hrefs the same way as the Recommended Meteorite pane; optional `/jobs/detail/:jobId` control when `astral_job_id` is set.

## Architectural definition

* **Patterns to reuse** — no established pattern applies (in-force patterns are entity batch / task daisy-chain / dispatch-retry; this epic is a read-only Jobs list + modal).
* **New patterns proposed** — none.
* **Applicable statutes**
  * `stat.logging.info.api` — completing-route API progress only; idempotent list/detail GETs that only return current state are **not** progress → no `logger.info` on those GETs. [current](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>)
  * `stat.logging.debug` — `logger.debug` at API logic joints (callee in/out for list/detail); no `if debug` gate; **no** debug noise in `src/data/`. [current](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)
  * `stat.logging.error` — on thrown list/detail failures handled in the API, one `logger.exception` at the handler with live facts + next step; data raises, does not log. [current](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>)

## Acceptance criteria

1. **Nav item present.** `GET /api/nav_config` (authenticated) includes Jobs item label `Meteorites` with an enabled path under `/jobs/` that matches a `routes.tsx` entry. Fail: missing item, `enabled: false`, or path with no matching route.
2. **List scoped to selected candidate.** On `/jobs/meteorites` with candidate A selected, every listed row’s `candidate_id` equals A; switching to candidate B refetches and does not keep A’s rows. Fail: rows for another candidate appear, or stale A rows remain after B is selected.
3. **Empty honesty.** Candidate with zero meteorite rows shows an empty list (no placeholder fake rows). Fail: fabricated rows or a hard error instead of empty.
4. **Modal content + metadata.** Clicking a list row opens a modal that shows that row’s `content` and at least `state`, timestamps (`created_at` / `updated_at` / `state_changed_at`), `link`, `classify_outcome`, and provenance (`id`, `source_kind`, `source_id`) when present on the row. Fail: modal missing for a listed row, or content/metadata blank when the API row has non-null values.
5. **Link honesty.** When `link` starts with `http://` or `https://` (after trim), the modal exposes a navigable href; otherwise plain text. Fail: bare/non-http link rendered as href, or http(s) link not clickable.
6. **Job deeplink gate.** When `astral_job_id` is non-empty, modal offers navigation to `/jobs/detail/<astral_job_id>`; when null/blank, that control is absent. Fail: deeplink shown with blank id, or missing when id is set.
7. **Read-only.** Grep/UI: the Meteorites page and modal do not call land / qualify / meteorite state-update / paste endpoints. Fail: any such mutating call wired from this page.
8. **Companies Meteorite untouched.** `NAV_CONFIG` still has Companies → Meteorite at `/companies/meteorite_list`; that page still lists companies (not staging rows). Fail: Companies item removed/renamed as part of this epic, or that route converted to staging-row list.

## Open questions

none

## Proposed child tickets

#### 1!: **Candidate meteorite list/detail API - Ada**

Owns the data helper and authenticated GET list + GET detail so the UI can render without inventing SQL. Does **not** own nav, routes, or React pages (child 2). Does **not** change retention or land/create routes.
**Citations:** `stat.logging.info.api`; `stat.logging.debug`; `stat.logging.error`
**Scope:** `src/data/database.py` (modified — candidate-scoped list helper + header inventory; reuse `get_meteorite` for detail); `src/utils/config.py` (modified — only list-column / modal-section constants consumed by the API or manifest, if any; does **not** add the Jobs nav item); `src/ui/api/api_meteorite.py` (modified — GET list by candidate + GET detail by id, projected fields, logging per citations)
**Estimate: 3**

#### 2: **Jobs Meteorites nav, list page, and detail modal - Katherine**

Owns Jobs → Meteorites in `NAV_CONFIG`, matching route, list page for the selected candidate, and read-only detail modal (content + metadata + link/deeplink honesty). Consumes child 1 APIs only. Does **not** own database helpers or land/create. Does **not** change Companies → Meteorite.
**Citations:** `stat.logging.info.api`; `stat.logging.debug`; `stat.logging.error` (honor API contracts; no new API routes)
**Scope:** `src/utils/config.py` (modified — Jobs → Meteorites `NAV_CONFIG` item; path SYNC with routes); `src/ui/frontend/src/routes.tsx` (modified — Jobs Meteorites route); `src/ui/frontend/src/pages/JobsMeteorites.tsx` (new — candidate-scoped list); `src/ui/frontend/src/components/MeteoriteDetailModal.tsx` (new — read-only modal); `src/ui/frontend/src/App.css` (modified only if needed)
**Estimate: 3**

**Monolith check:** Functional scope has 4 capability bullets (nav, list, modal, deeplink) with explicit out-of-scope; **M = 2** children (API then UI) — intentional split across layers, not a mega-ticket.
**Scope partition check:** `database.py` + `api_meteorite.py` + API-consumed config constants → child 1; `NAV_CONFIG` Jobs item + `routes.tsx` + `JobsMeteorites.tsx` + `MeteoriteDetailModal.tsx` + optional `App.css` → child 2. No double-claim; `config.py` split by constant purpose (API list/modal defs vs nav item).

---

## Original brief

Display a list of meteorites for the selected candidate with a modal to display the full content and metadata of the meteorite

### Comments

#### chuckles — 2026-09-21T01:57:08.350Z
[refresh-ftr] blocked: tests/component/data/database/test_meteorites.py
@Betty White — bible/test-tree conflict merging origin/dev into ftr/AST-1741-add-meteorites-jobs-nav. Resolve on astral-tests / ftr reconcile, then Chuckles retries refresh-ftr.

---

_Implementation detail may live in git history on `origin/dev`._

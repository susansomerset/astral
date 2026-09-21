# AST-1749 — Jobs Meteorites nav, list page, and detail modal

**Linear:** [AST-1749](https://linear.app/astralcareermatch/issue/AST-1749/jobs-meteorites-nav-list-page-and-detail-modal-add-meteorites-to-the)  
**Parent:** [AST-1741](https://linear.app/astralcareermatch/issue/AST-1741/add-meteorites-to-the-jobs-navigation) — Add "Meteorites" to the Jobs navigation  
**Publish ref:** `sub/AST-1741/AST-1749-jobs-meteorites-nav-list-page-detail-modal`

Jobs → **Meteorites**: enabled sidebar item, matching SPA route, candidate-scoped list of meteorite staging rows, and a read-only detail modal (full content + metadata + http(s) link honesty + optional job deeplink). Consumes sibling **AST-1748** APIs only (`GET /api/candidates/<id>/meteorites`, `GET /api/meteorites/<id>`). Does **not** own database helpers, land/create, or Companies → Meteorite.

## Explicit scope gate

This ticket’s **## Scope** names only:

- `src/utils/config.py` — Jobs → Meteorites `NAV_CONFIG` item; path SYNC with routes
- `src/ui/frontend/src/routes.tsx` — Jobs Meteorites route
- `src/ui/frontend/src/pages/JobsMeteorites.tsx` — new candidate-scoped list
- `src/ui/frontend/src/components/MeteoriteDetailModal.tsx` — new read-only modal
- `src/ui/frontend/src/App.css` — modified **only if needed**

Stages below stay inside those files and those change kinds. No `database.py`, no `api_meteorite.py`, no land/qualify/state-update/paste wiring, no edits to Companies → Meteorite nav or `CompaniesMeteorite.tsx`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add Jobs → Meteorites `NAV_CONFIG` item (`/jobs/meteorites`) | utils |
| `src/ui/frontend/src/routes.tsx` | Register `jobs/meteorites` → `JobsMeteorites` | ui |
| `src/ui/frontend/src/pages/JobsMeteorites.tsx` | New candidate-scoped list page | ui |
| `src/ui/frontend/src/components/MeteoriteDetailModal.tsx` | New read-only detail modal | ui |
| `src/ui/frontend/src/App.css` | Only if existing modal/list/report classes are insufficient | ui |

## Canon Scope (this ticket)

Citations are **API logging statutes**. This ticket adds **no** Flask routes and **must not** invent API logging. Honor the sibling contracts; do not add `logger.*` in React.

- `stat.logging.info.api` — **id-only (honor):** idempotent list/detail GETs are not progress; UI does not add API routes or `logger.info`.
- `stat.logging.debug` — **id-only (honor):** debug joints live in AST-1748 API; UI does not add `logger.debug`.
- `stat.logging.error` — **id-only (honor):** thrown API failures are handled in AST-1748; UI surfaces empty/404 honesty without inventing mutate calls.

## Sibling API contract (AST-1748 — consume as-is)

Do **not** reimplement projection or column/section order in TSX.

**List:** `GET /api/candidates/<candidate_id>/meteorites` →

```json
{ "columns": [ /* JOBS_METEORITES_LIST_COLUMNS */ ], "meteorites": [ /* projected rows */ ] }
```

List row keys include: `id`, `candidate_id`, `state`, `job_title`, `employer_name`, `classify_outcome`, `link`, `astral_job_id`, timestamps, `source_kind`, `source_id`. No `content` on list rows.

**Detail:** `GET /api/meteorites/<meteorite_id>` →

```json
{ "sections": [ /* JOBS_METEORITES_MODAL_SECTIONS */ ], "meteorite": { /* detail projection */ } }
```

Detail keys include full `content` plus AC metadata. `link` / `astral_job_id` are stored values (UI gates http(s) and deeplink). Missing id → 404.

## Stages

### Stage 1: Nav item + route

**Done when:** `NAV_CONFIG` Jobs group includes an enabled item `{label: "Meteorites", path: "/jobs/meteorites"}`; `routes.tsx` registers `jobs/meteorites` to a new page module; Companies → Meteorite at `/companies/meteorite_list` is unchanged. Visiting `/jobs/meteorites` renders the new page shell (list wiring can be Stage 2).

1. In `src/utils/config.py`, inside `NAV_CONFIG` → Jobs → `items`, insert after the Applied item and before Responded:

```python
{"label": "Meteorites", "path": "/jobs/meteorites"},
```

   Use the same dict shape as Applied / Recommended (no `"enabled": False` — default enabled). Do **not** rename, move, or remove `{"label": "Meteorite", "path": "/companies/meteorite_list"}`.

2. In `src/ui/frontend/src/routes.tsx`:
   - Import `JobsMeteorites` from `./pages/JobsMeteorites`.
   - Under the Jobs block (with `jobs/applied`, etc.), add `{ path: "jobs/meteorites", element: <JobsMeteorites /> }`.
   - Keep `jobs/detail/:jobId` and Companies `meteorite_list` untouched.
   - Honor the file header SYNC comment (nav path ↔ route).

3. Create `src/ui/frontend/src/pages/JobsMeteorites.tsx` as a minimal default-export page that renders:

```tsx
<div className="page-container">
  <div className="list-page-header">
    <h1 className="list-page-title">Meteorites</h1>
  </div>
  <div className="list-page-status">Loading...</div>
</div>
```

   Stage 2 replaces this shell with the real list.

⚠️ **Decision:** Place Meteorites after Applied / before Responded so enabled Jobs items stay contiguous and Responded stays the disabled trailing item.

### Stage 2: Candidate-scoped list page

**Done when:** With candidate A selected, `/jobs/meteorites` lists only A’s rows from the sibling list API; switching to B clears A’s rows and shows B’s; zero rows → empty list (ListPage empty message), not fake rows or a hard error; row click opens the detail modal (Stage 3 can still stub the modal). No land / qualify / state-update / paste API calls from this page.

1. Rewrite `JobsMeteorites.tsx` following the structure of `CompaniesMeteorite.tsx` (ListPage + modal id state), with these bindings:

   - `useCandidate()` → `selectedId` (and `candidatesHydrated` if the Applied page pattern is needed for first paint).
   - State: `rows`, `columns` (from API), `loading`, `viewingId: number | null`.
   - `load` via `useCallback` depending on `selectedId`:
     - If `!selectedId`: set `rows` to `[]`, set `columns` to `[]` (or keep last columns only if already loaded — prefer clear both), set `loading` false, **do not** call the API.
     - Else: `GET /api/candidates/${encodeURIComponent(selectedId)}/meteorites` via `api(...)`.
     - On OK JSON: `setColumns` from `data.columns` (array; default `[]`); `setRows` from `data.meteorites` (array; default `[]`). Never invent placeholder rows.
     - On non-OK / network failure: set `rows` to `[]` and leave an honest empty/error status via ListPage (`emptyMessage` or a small status line) — do **not** fabricate rows.
   - `useEffect(() => { load() }, [load])` so candidate switches refetch.

2. Map API `columns` into `ListPage` `Column` objects: for each column dict, pass through `key`, `label`, `sortable` (default true if omitted), `defaultDesc`, `type` when present. Do **not** hardcode a different column order than the API returns.

3. Render:

```tsx
<ListPage
  title="Meteorites"
  columns={/* mapped */}
  rows={rows}
  idField="id"
  loading={loading}
  emptyMessage="No meteorites yet"
  onRowClick={row => setViewingId(Number(row.id))}
/>
```

   Plus `<MeteoriteDetailModal meteoriteId={viewingId} onClose={() => setViewingId(null)} />` (Stage 3 implements the component; Stage 2 may import a stub that returns `null` when `meteoriteId == null`).

4. Read-only gate: this file must not import or call land / qualify / meteorite state-update / paste endpoints (no `POST`/`PUT`/`PATCH`/`DELETE` to meteorite or inbox land paths). List/detail GETs only.

⚠️ **Decision:** Drive columns from the list API response (not a duplicated TS constant) so AST-1748 remains the single order authority (`JOBS_METEORITES_LIST_COLUMNS`).

⚠️ **Decision:** Mirror `CompaniesMeteorite` + `ListPage` rather than the hand-rolled Applied table — ListPage already owns sort/filter/empty chrome.

### Stage 3: Read-only MeteoriteDetailModal

**Done when:** Clicking a list row opens a modal that loads `GET /api/meteorites/<id>`; shows `content` and metadata required by AC4; http(s)-gates `link` (AC5); shows `/jobs/detail/<astral_job_id>` only when `astral_job_id` is non-empty after trim (AC6); no Save/land/qualify/mutate controls; Companies Meteorite page untouched. `App.css` unchanged unless a step below proves existing classes insufficient.

1. Create `src/ui/frontend/src/components/MeteoriteDetailModal.tsx`:

   - Props: `meteoriteId: number | null`, `onClose: () => void`.
   - When `meteoriteId == null`, return `null` (closed).
   - On open (`meteoriteId` set): fetch `GET /api/meteorites/${meteoriteId}` via `api`. Store `sections` + `meteorite` from JSON. On 404 / failure: show an honest error string inside the modal body; do not invent a fake meteorite.
   - Wrap with shared `Modal` from `./Modal`: `open={meteoriteId != null}`, `onClose`, `title` = non-empty `job_title` / `employer_name` when present else `Meteorite ${id}`, `showFooter={false}` (read-only — no Cancel/Save strip), `size="wide"` if content needs width (match Recommended report readability).

2. Render body with `ReportSectionList` (`./ReportSectionList`), `sections` from the API (cast/map to `ReportSectionDef`: `section_id`, `nav_label`, `default_expanded`). `renderSection(sectionId)` switches on AST-1748 section ids only — **do not** invent new section ids:

   | `section_id` | Render |
   |--------------|--------|
   | `meteorite_timestamps` | Rows for `created_at`, `updated_at`, `state_changed_at` when non-empty after trim; include `estelle_notified_at` when present/non-empty. Same field-row chrome as `JobMeteoritePane` (`job-analysis-upshot-body` / empty `recommended-report-empty`). |
   | `meteorite_link` | Trim `link`. Empty → “No link on file.” If trimmed value starts with `http://` or `https://`, render `<a href={trimmed} target="_blank" rel="noopener noreferrer" className="recommended-report-title-link">`. Else plain text (no href). |
   | `meteorite_content` | Show `classify_outcome` when non-empty (labeled). Show `content` in a read-only `<textarea className="entity-story-content">`: if `content` parses as JSON, pretty-print with `JSON.stringify(JSON.parse(raw), null, 2)`; else raw string. If both outcome and content empty → empty message. |
   | `meteorite_provenance` | Rows for `id`, `state`, `source_kind`, `source_id` when non-empty; include `error` when present/non-empty. |
   | `meteorite_job` | Let `jobId = String(meteorite.astral_job_id ?? "").trim()`. If empty: return `null` or a single empty message with **no** navigation control. If non-empty: render a `Link` (react-router) or `<a>` to `/jobs/detail/${encodeURIComponent(jobId)}` labeled for navigation to that job (e.g. “Open job” / show the id). Do **not** show the control when blank. |

3. Reuse patterns from `JobMeteoritePane.tsx` (http(s) gate, JSON pretty-print, field rows) by **copying the small helpers into this file** or inlining equivalent private functions. Do **not** edit `JobMeteoritePane.tsx` (out of Scope — Recommended report pane).

4. Read-only gate: no `onSave`, no PUT/POST to land / qualify / meteorite state / paste. GET detail only.

5. `App.css`: touch **only** if Stage 3 UI is broken without a new class after trying `modal-*`, `recommended-report-*`, `entity-story-content`, and `job-analysis-upshot-body`. If no new class is required, leave `App.css` untouched and note that in the stage commit message body.

⚠️ **Decision:** Compose with `Modal` + `ReportSectionList` + JobMeteoritePane field patterns rather than embedding inside `JobAnalysisReportModal` — this is a Jobs list surface, not a Recommended report tab.

⚠️ **Decision:** Put `classify_outcome` in the `meteorite_content` section body (with content) so AC4 is satisfied without inventing a section id outside `JOBS_METEORITES_MODAL_SECTIONS`.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1741/AST-1749-jobs-meteorites-nav-list-page-detail-modal`.
- Do not add files outside **Files Changed**.
- If a step is ambiguous or the sibling API shape differs from this plan → stop, comment on **parent** AST-1741 with the Stage blocked template, wait.
- Dependency: AST-1748 list/detail routes must be present on the integration line used at build time (already on `origin/ftr/AST-1741-add-meteorites-jobs-nav` / synced into this sub).

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1749
**Overall:** APPROVED
**Corpus:** 751624d7ebdf9bc441fc3d08a51ae751ea8026af
**Publish ref tip:** a506737b49189cec7996366f07f3dd803bf41a12

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.info.api | A | | Explicit scope gate: no Flask routes, no `logger.info`; GET-only consumption |
| stat.logging.debug | A | | UI adds no `logger.debug`; honors AST-1748 API debug joints |
| stat.logging.error | A | | Modal/list surface 404/failure honestly; no API error logging invented |

## Traceability

AC1→S1 NAV + route; AC2→S2 `selectedId` load/refetch; AC3→S2 empty `meteorites`/no placeholders; AC4→S3 sections + `meteorite_content`/provenance/timestamps; AC5→S3 `meteorite_link` http(s) gate; AC6→S3 `meteorite_job` deeplink gate; AC7→S2/S3 read-only gates (GET only); AC8→S1 preserve Companies → Meteorite nav/route

## Findings

### discuss

- **Location:** Canon Scope vs plan footprint  
  **Finding:** Frozen list carries only API logging statutes (honor-only on this UI child). Plan adds new frontend files under standard paths but `astral.ui.frontend-file-placement` (and other placement/scope statutes) were not selected at Discussion.  
  **Recommendation:** Archie may amend parent Canon Scope if those should be scored at `review-child`; do not widen the frozen list in-flight.

- **Location:** Canon Scope — honor-only logging ids  
  **Finding:** All three cited statutes territorially govern `src/ui/api/**` / backend logging; this plan touches frontend + `NAV_CONFIG` only. Plan text still explicitly honors sibling contracts.  
  **Recommendation:** Scope observation — intentional sibling parity with AST-1748; not a plan defect.

- **Location:** Stage 3 — helper duplication  
  **Finding:** Plan copies `JobMeteoritePane` http/JSON/field-row helpers into `MeteoriteDetailModal.tsx` rather than extracting shared code.  
  **Recommendation:** Acceptable per Explicit scope gate (cannot edit `JobMeteoritePane.tsx`); note for future refactor if a third surface appears.

- **Location:** Linear assignee vs validate-plan gate  
  **Finding:** Ticket is `Plan Ready` with assignee Katherine Johnson, not Joan; Chuckles spawned this pass.  
  **Recommendation:** Procedural only — no plan change required.

### acceptable

- **Location:** Stage 2 — `CompaniesMeteorite.tsx` pattern  
  **Finding:** Plan correctly diverges where needed (API-driven columns vs hardcoded `METEORITE_COLUMNS`; clears rows when no candidate).  
  **Recommendation:** None.

- **Location:** Execution contract — AST-1748 dependency  
  **Finding:** Sibling list/detail routes exist on `origin/ftr/AST-1741-add-meteorites-jobs-nav`; contract paths match plan.  
  **Recommendation:** None.

## R6 checklist (summary)

- Definition fidelity: plan implements Jobs nav, list, modal, deeplink/link honesty, read-only, and Companies Meteorite preservation — no database/API/land scope.
- Scope gate: all Files Changed rows and stages stay inside ticket ## Scope.
- DRY: reuses `ListPage`, `Modal`, `ReportSectionList`, and JobMeteoritePane rendering patterns without editing out-of-scope files.
- Self-assessment: Estimate 3 — agree; staged decisions are specific (nav placement, API column authority, modal composition).

context_tokens≈35000

---

[plan-rubric] PROCEED (Commit: a506737b49189cec7996366f07f3dd803bf41a12) UI plan faithful

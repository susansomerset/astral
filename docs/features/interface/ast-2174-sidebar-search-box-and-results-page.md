# AST-2174 — Sidebar search box and results page

- **Ticket:** [AST-2174](https://linear.app/astralcareermatch/issue/AST-2174) (child of [AST-2168](https://linear.app/astralcareermatch/issue/AST-2168) — Add Universal Entity Search)
- **Publish ref:** `sub/AST-2168/AST-2174-search-results-page` (origin only)
- **Canon Scope:** none — ticket Citations: "no in-force directive governs React pages or routes."

Delivers the UI half of universal search: a search input at the top of the nav panel's scrolling area (above the Jobs group, under the fixed candidate picker), a deeplink-only `/search?q=…` route, and a `SearchResults` page that calls [AST-2173](https://linear.app/astralcareermatch/issue/AST-2173)'s `GET /api/search` for the selected candidate and renders the non-empty `job` / `company` / `meteorite` lists as Jobs / Companies / Meteorites sections, rows in the order the API returned them. Clicking a row opens the existing modal for that entity (jobs: `JobAnalysisReportModal` when `modal_kind` is `report`, `JobDetailModal` when `detail`). Matching, ordering, field lists and the job-modal decision all belong to AST-2173 — this page renders what it returns.

**Verified on the synced tree at plan time (`08bd65419`, `origin/ftr/AST-2168-universal-entity-search` merged):**

- `GET /api/search?q=…&candidate_id=…` (`src/ui/api/api_search.py`) returns `{job: [...], company: [...], meteorite: [...]}` — all three keys always present. Each hit: `entity_id`, `display_name`, `state`, `tier`, `matched_fields` (list of column names); job hits add `jobs_list` and `modal_kind` (`"report"` | `"detail"`). Blank `q` or missing `candidate_id` → 400. Exception → 500 (route log says "the search results page shows no results").
- `entity_id` is `astral_job_id` (string) for jobs, `short_name` (string) for companies, `id` (integer) for meteorites (`SEARCH_ENTITY_CONFIG`, `config.py` ~L4256).
- Modal props: `JobAnalysisReportModal({ jobId: string|null, onClose, onRefresh? })`, `JobDetailModal({ jobId: string|null, onClose, onRefresh? })`, `CompanyDetailModal({ shortName: string|null, onClose, onSaved })`, `MeteoriteDetailModal({ meteoriteId: number|null, onClose })`. Each renders nothing when its id is `null`. None of the four calls `navigate(` (AC 9 — no page navigation away).
- `ListPage` is **not** used for the result tables: its default sort applies every sortable column on mount (`ListPage.tsx` ~L180–226), which would re-order the API's tiered rows (ticket: "no client-side reordering of tiers"), and it brings its own `<h1>`, a filter box and a `listpage:<title>` localStorage layout per section. The page reuses the **look** — `list-page`, `list-page-header`, `list-page-title`, `list-page-status`, `list-page-table-wrap--scroll`, `list-page-table`, `tr.clickable` classes from `App.css` — with its own three-column markup.
- `NavigationShell.tsx`: `.sidebar-chrome` (logo + candidate picker, fixed) then `.sidebar-scroll` (nav groups, scrolls) — both inside `<nav id="app-sidebar">`, which is the same element in wide and narrow (drawer) layouts. `NAV_CONFIG`'s first group is `Jobs` (`config.py` ~L6199). The drawer auto-closes on `location.pathname` change only, so a second search from `/search` would leave it open — the submit handler closes it explicitly.
- `eslint-plugin-react-hooks` ^7 recommended config is on (`eslint.config.js`). The fetch effect below never calls `setState` synchronously in the effect body (only in the promise callback) — results are stamped with the request key instead of being cleared on candidate / `q` change.
- `routes.tsx` header: every route needs a `NAV_CONFIG` item except deeplink-only ones. `search` is deeplink-only (reached from the sidebar box). No test asserts the routes ↔ `NAV_CONFIG` sync.
- The epic worktree has no `src/ui/frontend/node_modules` — `npm ci` is required before build / lint (`node_modules`, `dist` are gitignored in `src/ui/frontend/.gitignore`).

## Explicit scope gate

Ticket `## Scope`: `src/ui/frontend/src/pages/SearchResults.tsx`, `src/ui/frontend/src/routes.tsx`, `src/ui/frontend/src/components/NavigationShell.tsx`, `src/ui/frontend/src/App.css`. Every row in Files Changed is one of those four, and each change is the kind the Technical scope names: new results page hosting the four existing modals; `search` route + header comment; sidebar search input in `.sidebar-scroll`; CSS for the input and results-page tweaks. No backend, `tests/`, bible or `NAV_CONFIG` edits.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/SearchResults.tsx` | **New** — `/search` page: fetch, sections, four modal hosts | ui (frontend) |
| `src/ui/frontend/src/routes.tsx` | Import `SearchResults`; add `search` route; header comment notes it deeplink-only | ui (frontend) |
| `src/ui/frontend/src/components/NavigationShell.tsx` | Search `<form>` at top of `.sidebar-scroll`; submit → `/search?q=<encoded>` | ui (frontend) |
| `src/ui/frontend/src/App.css` | `.search-results-section-title` (Stage 1); `.sidebar-search*` (Stage 2) | ui (frontend) |

## Stage 0: Lint baseline (no commit)

**Done when:** `debug/spikes/AST-2174/lint-baseline.txt` holds the pre-change `npm run lint` output.

1. `cd src/ui/frontend && npm ci`.
2. Before editing any file: `npm run lint > ../../../debug/spikes/AST-2174/lint-baseline.txt 2>&1 || true` (create `debug/spikes/AST-2174/` first). This tree's frontend is byte-identical to `origin/dev`'s (AST-2173 touched no frontend file), so this is the AC 14 "absent on `origin/dev`" baseline.

## Stage 1: Results page and route

**Done when:** With the dev server running and a candidate selected, visiting `/search?q=<string>` by URL shows Jobs / Companies / Meteorites sections (only non-empty ones, in that order, each titled `<Label> (<count>)`), rows in API order with Name / State / Matched fields columns; clicking a row opens the matching modal; closing it re-fetches. `npx tsc -b --noEmit` passes.

1. Create `src/ui/frontend/src/pages/SearchResults.tsx` with exactly this content:

```tsx
import { useEffect, useState, type ReactNode } from "react"
import { useSearchParams } from "react-router-dom"
import CompanyDetailModal from "../components/CompanyDetailModal"
import JobAnalysisReportModal from "../components/JobAnalysisReportModal"
import JobDetailModal from "../components/JobDetailModal"
import MeteoriteDetailModal from "../components/MeteoriteDetailModal"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"

type EntityType = "job" | "company" | "meteorite"

/** One hit from GET /api/search (AST-2173 src/core/search.py search_entities). */
interface SearchHit {
  entity_id: string | number
  display_name: string
  state: string | null
  tier: "base" | "payload"
  matched_fields: string[]
  jobs_list?: string                  // jobs only
  modal_kind?: "report" | "detail"    // jobs only — which job modal opens
}

type ResultsByType = Record<EntityType, SearchHit[]>

// Key order is render order: Jobs, Companies, Meteorites.
const SECTION_LABELS: Record<EntityType, string> = { job: "Jobs", company: "Companies", meteorite: "Meteorites" }
const ENTITY_TYPES = Object.keys(SECTION_LABELS) as EntityType[]

/** A failed request, or a missing / non-list key, reads as no hits for that type. */
function toResults(data: unknown): ResultsByType {
  const d = (data ?? {}) as Partial<Record<EntityType, unknown>>
  return Object.fromEntries(ENTITY_TYPES.map(t => [t, Array.isArray(d[t]) ? d[t] : []])) as ResultsByType
}

/** AST-2174: /search?q=… — the selected candidate's hits by entity type, rows in API order; each opens its existing modal. */
export default function SearchResults() {
  const [searchParams] = useSearchParams()
  const q = searchParams.get("q") ?? ""
  const { selectedId } = useCandidate()
  // Results carry the candidate + q they answer, so a switch never shows the previous candidate's rows.
  const [result, setResult] = useState<{ key: string; byType: ResultsByType } | null>(null)
  // Bumped on modal close / save to re-fetch the same key in place.
  const [reloadTick, setReloadTick] = useState(0)
  const [open, setOpen] = useState<{ type: EntityType; hit: SearchHit } | null>(null)
  const requestKey = selectedId && q.trim() ? `${selectedId}\n${q}` : null

  useEffect(() => {
    // No candidate or blank q → no request at all (AC 10 / AC 12).
    if (!selectedId || !requestKey) return
    let stale = false
    api(`/api/search?q=${encodeURIComponent(q)}&candidate_id=${encodeURIComponent(selectedId)}`)
      .then(r => (r.ok ? r.json() : null))
      .catch(() => null)
      .then(data => { if (!stale) setResult({ key: requestKey, byType: toResults(data) }) })
    return () => { stale = true }
  }, [selectedId, q, requestKey, reloadTick])

  const reload = () => setReloadTick(t => t + 1)
  const close = () => { setOpen(null); reload() }
  const byType = result && result.key === requestKey ? result.byType : null
  const jobId = (kind: "report" | "detail") =>
    open?.type === "job" && open.hit.modal_kind === kind ? String(open.hit.entity_id) : null

  let body: ReactNode
  if (!selectedId) body = <p className="list-page-status">Select a candidate</p>
  else if (!q.trim()) body = <p className="list-page-status">No results</p>
  else if (!byType) body = <p className="list-page-status">Loading...</p>
  else if (ENTITY_TYPES.every(t => byType[t].length === 0)) body = <p className="list-page-status">No results</p>
  else body = (
    <div className="list-page-table-wrap list-page-table-wrap--scroll">
      {ENTITY_TYPES.filter(t => byType[t].length > 0).map(t => (
        <section key={t}>
          <h2 className="search-results-section-title">{SECTION_LABELS[t]} ({byType[t].length})</h2>
          <table className="list-page-table">
            <thead>
              <tr><th>Name</th><th>State</th><th>Matched fields</th></tr>
            </thead>
            <tbody>
              {byType[t].map(hit => (
                <tr key={String(hit.entity_id)} className="clickable" onClick={() => setOpen({ type: t, hit })}>
                  <td>{hit.display_name}</td>
                  <td>{hit.state ?? "—"}</td>
                  <td>{hit.matched_fields.join(", ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ))}
    </div>
  )

  return (
    <>
      <div className="list-page">
        <div className="list-page-header">
          <h1 className="list-page-title">{q.trim() ? `Search results for “${q.trim()}”` : "Search results"}</h1>
        </div>
        {body}
      </div>
      <JobAnalysisReportModal jobId={jobId("report")} onClose={close} onRefresh={reload} />
      <JobDetailModal jobId={jobId("detail")} onClose={close} onRefresh={reload} />
      <CompanyDetailModal
        shortName={open?.type === "company" ? String(open.hit.entity_id) : null}
        onClose={close}
        onSaved={reload}
      />
      <MeteoriteDetailModal
        meteoriteId={open?.type === "meteorite" ? Number(open.hit.entity_id) : null}
        onClose={close}
      />
    </>
  )
}
```

⚠️ **Decision:** Own table markup with `ListPage`'s CSS classes, not the `ListPage` component — see "Verified" above (its default sort re-orders API rows; per-section `<h1>` / filter box / localStorage layout don't fit a three-section page). Ticket left this to plan-child ("Reuse the shared `ListPage` table look where it fits").

⚠️ **Decision:** Blank or absent `q` on a direct URL (`/search`, `/search?q=`) → no request, body "No results" (reuses the AC 11 string; no new copy). A failed request (non-2xx / network) also renders "No results" — matches AST-2173's route log line "the search results page shows no results". No toast.

⚠️ **Decision:** State column shows the raw `state` string (`—` when null), not a `StateUiContext` label — the ticket asks for "state" and the API returns the raw value. Matched fields column is `matched_fields` joined with `", "`.

⚠️ **Decision:** Page title is `Search results for “<trimmed q>”` (or `Search results` when `q` is blank), so a reloaded URL shows what was searched — the sidebar box itself is not re-filled from the URL (Stage 2).

⚠️ **Decision:** Closing **any** of the four modals re-fetches (`close`); `onRefresh` / `onSaved` also re-fetch while the modal stays open. The re-fetch keeps the same `requestKey`, so current rows stay on screen until the fresh ones replace them (AC 13 — no reload, no "Loading..." flash).

2. In `src/ui/frontend/src/routes.tsx`:
   - Replace header line 2 (`//       Deeplink-only routes (e.g. jobs/detail/:jobId) use JOBS_DETAIL_ROUTE_PREFIX — not NAV_CONFIG.`) with these two lines:
     ```
     //       Deeplink-only routes (e.g. jobs/detail/:jobId) use JOBS_DETAIL_ROUTE_PREFIX — not NAV_CONFIG.
     //       search (AST-2174) is deeplink-only too — reached from the sidebar search box, no NAV_CONFIG item.
     ```
     (i.e. keep line 2, insert the new line after it).
   - After the `import AdminManageSlack from "./pages/AdminManageSlack"` line, add:
     ```tsx

     // --- Search ---
     import SearchResults from "./pages/SearchResults"
     ```
   - Immediately before the `// Catch-all` line inside the shell `children`, add:
     ```tsx
               // Search (deeplink-only — no NAV_CONFIG item)
               { path: "search", element: <SearchResults /> },

     ```
3. In `src/ui/frontend/src/App.css`, directly after the `.list-page-status { … }` block (ends ~L869, before `/* === 8b. Job list candidate actions (AST-312) === */`), add:

```css

/* AST-2174: /search results — one titled section per entity type */
.search-results-section-title {
  margin: 0;
  padding: 14px 20px 6px;
  font-size: 15px;
  font-weight: 600;
  color: var(--heading);
}
```

4. `cd src/ui/frontend && npx tsc -b --noEmit` exits 0.
5. Commit `code(AST-2174): search results page and /search route` (the three files above only), push per build-child.

## Stage 2: Sidebar search box

**Done when:** In both wide (≥1024px) and narrow (drawer) layouts, a search input is the first thing in `.sidebar-scroll`, above the Jobs group and outside `.sidebar-chrome`, and scrolls with the menu. Typing `acme` + Enter lands on `/search?q=acme` (drawer closes in narrow); Enter on a blank / whitespace-only box does nothing. `npx tsc -b --noEmit` passes.

1. In `src/ui/frontend/src/components/NavigationShell.tsx`:
   - Line 1: `import { useEffect, useState } from "react"` → `import { useEffect, useState, type FormEvent } from "react"`.
   - Line 2: `import { NavLink, Outlet, useLocation } from "react-router-dom"` → `import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom"`.
   - After `const [candidateMenuOpen, setCandidateMenuOpen] = useState(false)` add:
     ```tsx
       const [searchText, setSearchText] = useState("")
     ```
   - After `const location = useLocation()` add:
     ```tsx
       const navigate = useNavigate()
     ```
   - After the closing `}` of `function toggleGroup(...)` add:
     ```tsx

       // AST-2174: Enter only (no search-as-you-type); blank / whitespace-only does nothing.
       function submitSearch(e: FormEvent) {
         e.preventDefault()
         const q = searchText.trim()
         if (!q) return
         // Pathname-change auto-close misses /search → /search?q=other, so close the drawer here.
         setDrawerOpen(false)
         navigate(`/search?q=${encodeURIComponent(q)}`)
       }
     ```
   - Immediately after `<div className="sidebar-scroll">` and before `{loading ? (`, add:
     ```tsx
               <form className="sidebar-search" role="search" onSubmit={submitSearch}>
                 <input
                   type="search"
                   className="sidebar-search-input"
                   placeholder="Search"
                   aria-label="Search"
                   value={searchText}
                   onChange={e => setSearchText(e.target.value)}
                 />
               </form>
     ```
2. In `src/ui/frontend/src/App.css`, directly after `.sidebar-error   { color: var(--danger); }` (~L347), add:

```css

/* AST-2174: search box — top of the scrolling nav, above Jobs (not in .sidebar-chrome) */
.sidebar-search {
  padding: 8px 12px 4px;
}

.sidebar-search-input {
  width: 100%;
  box-sizing: border-box;
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: 4px;
  font-size: 13px;
  font-family: inherit;
  background: var(--bg-deep);
  color: var(--text-primary);
}

.sidebar-search-input::placeholder {
  color: var(--text-muted);
}

.sidebar-search-input:focus {
  outline: none;
  border-color: var(--accent-contrast);
  box-shadow: 0 0 0 2px var(--accent-contrast-dim);
}
```

⚠️ **Decision:** The box keeps whatever was typed after submit and is not re-filled from `?q=` on reload / deeplink — the ticket names only submit behavior; the results page title shows the query instead (Stage 1).

⚠️ **Decision:** The form renders above the `loading` / `error` branch, so the box is present even while nav config loads or fails — it is always "directly above the Jobs nav group" once groups render.

3. `cd src/ui/frontend && npx tsc -b --noEmit` exits 0.
4. Commit `code(AST-2174): sidebar search box` (`NavigationShell.tsx`, `App.css` only), push per build-child.

## Stage 3: Build / lint gate (no commit unless a fix is needed)

**Done when:** AC 14 holds on the Stage 2 tip.

1. From repo root: `PYTHONPATH=.:src $ASTRAL_PYTHON -c "import src.utils.config, src.core.search, ui.api.api_search"` exits 0 (`ASTRAL_PYTHON=~/astral/.venv/bin/python` — the epic worktree has no `.venv`).
2. `cd src/ui/frontend && npm run build` exits 0.
3. `npm run lint > ../../../debug/spikes/AST-2174/lint-after.txt 2>&1 || true`; every problem in `lint-after.txt` must also appear in `lint-baseline.txt` (compare by file + rule; line numbers in `NavigationShell.tsx` / `App.css` neighbours may shift). Any new problem in `SearchResults.tsx`, `routes.tsx` or `NavigationShell.tsx` → stop and comment on the parent per the execution contract (do not improvise a rewrite).

## AC ownership (this child)

| AC | This child's half |
|----|-------------------|
| 8 | Clicking a job hit opens `JobAnalysisReportModal` when `modal_kind === "report"`, `JobDetailModal` when `"detail"` (Stage 1 `jobId(kind)`). API values are AST-2173's. |
| 9 | Company hit → `CompanyDetailModal(shortName=entity_id)`; meteorite hit → `MeteoriteDetailModal(meteoriteId=Number(entity_id))`; in-page, no navigation. |
| 10 | Stage 2 box placement + Enter → `/search?q=<encoded>`; blank → nothing; reload re-fetches from the URL (Stage 1 reads `q` from `useSearchParams`). |
| 11 | UI half: sections only for non-empty types, in Jobs → Companies → Meteorites order, titled `<Label> (<n>)`; all empty → "No results", no headings. |
| 12 | `selectedId` in the effect deps + request-key stamp: switch re-fetches and never shows the old candidate's rows; no candidate → "Select a candidate", no request. |
| 13 | `close` re-fetches in place. |
| 14 | `npm run build` / `npm run lint` (Stage 3); the Python import is AST-2173's code, re-checked here. |

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2174
**Overall:** APPROVED
**Corpus:** 0d01e20d2b313a4e35cf3d07434b6cd69f615768
**Publish ref:** `origin/sub/AST-2168/AST-2174-search-results-page` @ `78fc17e7bc6e3bf53f5540fd764a22a230016894`

## Canon scores
*(empty — Canon Scope frozen at Discussion: child Citations explicitly “none”; no directive ids to score.)*

## Traceability
AC8→S1; AC9→S1; AC10→S2 (box/Enter) + S1 (URL `q`, reload fetch); AC11→S1; AC12→S1; AC13→S1 (`close` / `onSaved` / `onRefresh`); AC14→S0+S3 (`npm` + Python import re-check); parent AC1–7, AC14–15 Python half, AC9 API shape→N/A — AST-2173 per Boundaries.

### acceptable
- **Location:** Stage 1 — `ListPage` vs own tables
- **Finding:** Skipping `ListPage` in favor of shared CSS classes matches ticket (“look where it fits”) and avoids default multi-column sort that would violate “no client-side reordering of tiers” (`ListPage.tsx` ~L180–226).
- **Recommendation:** None.

- **Location:** Stage 0 / Stage 3 — `debug/spikes/AST-2174/`
- **Finding:** Lint baseline lives under `debug/*` (gitignored); not in Files Changed and not committed — within scope gate intent.
- **Recommendation:** None.

### discuss
- **Location:** Stage 1 — state column
- **Finding:** Rows show raw API `state` strings, not `StateUiContext` labels used on some list pages.
- **Recommendation:** Accept for AC (“state” column) or align with other list pages in a follow-up — not a plan blocker.

- **Location:** Stage 1 — error handling
- **Finding:** Non-2xx / network failures render the same “No results” copy as a true empty hit set (aligned with AST-2173 route log wording).
- **Recommendation:** Susan confirms that is acceptable UX vs. a distinct error state.

context_tokens≈34000

## Review (build stub)

**Built:** `origin/sub/AST-2168/AST-2174-search-results-page` @ `2824c5b02`.

**Stages delivered:**
- Stage 0: `npm ci` + lint baseline (`debug/spikes/AST-2174/lint-baseline.txt`, 29 problems — 25 errors, 4 warnings), not committed.
- Stage 1: `pages/SearchResults.tsx` (verbatim from plan), `search` route + header comment + import in `routes.tsx`, `.search-results-section-title` in `App.css` — `bc8152b3d`
- Stage 2: sidebar search `<form>` at top of `.sidebar-scroll` + `submitSearch` in `NavigationShell.tsx`, `.sidebar-search*` in `App.css` — `2824c5b02`
- Stage 3 gate: `npx tsc -b --noEmit` 0; `npm run build` 0; `PYTHONPATH=.:src python -c "import src.utils.config, src.core.search, ui.api.api_search"` 0; `npm run lint` 29 problems, identical set to baseline (two pre-existing `NavigationShell.tsx` findings shifted +2 lines by the new state/navigate lines). `SearchResults.tsx` / `routes.tsx` lint clean.

**Deviations from plan text:** none.

**Notes:**
- Not browser-smoked (no running Flask + Vite + Stytch session in the epic worktree); AC 8–13 UI behaviour is verified by build/typecheck only — Betty's manifest owns the runtime checks.
- Joan's two discuss items (raw `state` strings; failed request reads as "No results") are built as planned, pending Susan.

## Radia review

[code-rubric]

**Ticket:** AST-2174  
**Publish ref:** `e026730b5f088dccb7a11d8b4f61eb52a3874bbe` (`origin/sub/AST-2168/AST-2174-search-results-page`)  
**Corpus:** `0d01e20d2b313a4e35cf3d07434b6cd69f615768`  
**Overall:** CLEAN  

## Canon scores

*(none — frozen Canon Scope at Discussion: Citations “no in-force directive governs React pages or routes”; no directive ids on the list.)*

## Column diff vs plan stage

no plan-stage canon scores attached (Joan table empty by design) — Radia has no canon column to diff; plan-stage **Overall APPROVED** and implementation matches the plan text (build stub: no deviations).

## Frame diff

(none)

## Findings

### discuss

- **Location:** `src/ui/frontend/src/pages/SearchResults.tsx` — State column (`hit.state ?? "—"`)  
- **Finding:** Rows show raw API `state` strings, not `StateUiContext` / manifest labels used on some list pages (Joan plan discuss).  
- **@susan:** Keep raw `state` for AC 11 “state” column, or align display with other list pages in a follow-up?  
- **Default:** Keep raw strings; no `resolve-child` change (plan decision, tests assert `"NEW"` / `"IMPORTED"` / `"WATCHING"` literally).

- **Location:** `SearchResults.tsx` fetch effect (`!r.ok` / `.catch` → `toResults(null)` → empty lists)  
- **Finding:** Network / 5xx / error JSON renders the same “No results” copy as a true empty hit set; test `failed request reads as 'No results'` locks this in. Matches AST-2173 route log wording and plan.  
- **@susan:** Accept silent failure UX vs. distinct error copy or toast?  
- **Default:** Accept as built (no error UI); smaller change surface for AST-2174.

### advisory

- **Sibling product carry (expected):** Three-dot diff vs `origin/dev` includes AST-2173 backend (`src/core/search.py`, `src/data/database.py`, `src/ui/api/api_search.py`, `src/utils/config.py`, `src/ui/server.py`) plus AST-2173 tests/bible/docs — merged sub/ftr lineage (`blockedBy` AST-2173), not AST-2174 scope smuggling. AST-2174 product footprint is only the four scoped frontend files (+ this child’s tests/bible).  
- **AST-2173 canon on merged tip:** Prior Radia pass graded `stat.logging.debug` **C** on AST-2173; not on AST-2174’s empty frozen list — no re-score here.  
- **Build stub:** No browser E2E in epic worktree; Betty’s component tests cover AC 8–13 behaviour (modals, placement wide/narrow, candidate switch, reload, route registration).

### fix-now

(none)

## What's solid

- Plan-delivered four-file UI: `SearchResults.tsx` (API order preserved, three sections, four modal hosts, `requestKey` stamp for AC 12, in-place re-fetch on close AC 13), deeplink-only `search` route + comment in `routes.tsx`, sidebar form first in `.sidebar-scroll` with trim/encode navigate and drawer close on re-search, CSS blocks per plan.  
- No `navigate` from result modals; job `modal_kind` splits `JobAnalysisReportModal` vs `JobDetailModal`; company/meteorite ids match API contract.  
- `NavigationShell` uses `navigate` only for sidebar submit (in-scope); tests distinguish from page navigation.  
- Plan fidelity and estimate **3** align; explicit scope gate honoured for product files.

## Recommended actions (Chuckles / downstream — not Radia)

- Append artifact, `docs()` push, post slim upshot `--as radia`, **Review Posted**.  
- **PROCEED** path: optional Susan answers on the two discuss items; **Default** needs no code.  
- On merge to ftr: continue using `sync-child.sh --ftr AST-2168-universal-entity-search` per known workaround.

---

**Slim Linear upshot (Chuckles posts):**

```
[code-rubric] PROCEED (Commit: e026730b5) UI plan delivered clean
```

context_tokens≈38000

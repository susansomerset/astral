<!-- linear-archive: AST-1975 archived 2026-10-08 -->

## Linear archive (AST-1975)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1975/ready-review-processing-pages-landing-and-jobs-routes-jobs-navigation  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-1970 — Jobs Navigation changes  
**Blocked by / blocks / related:** parent: AST-1970; related: AST-1976

### Description

## What this implements

After #1. Delivers the frontend nav re-cut:

* Ready and Review served by the Recommended list component, with the Source column and no meteorite sub-section.
* The new Processing page, whose rows open the Job Detail modal with working Skip.
* The first-non-empty landing redirect.
* Removal of the In Review and Responded pages and routes.
* The manifest type.

Does **not** touch the Meteorites page (#3) or any backend file (#1).

## Citations

none — every file is under `src/ui/frontend/`, outside both statutes' territory.

## Scope

**Component scope:** `src/ui/frontend/src/routes.tsx`, `src/ui/frontend/src/components/JobsHomeRedirect.tsx` (new), `src/ui/frontend/src/pages/JobsRecommended.tsx`, `src/ui/frontend/src/pages/JobsProcessing.tsx` (new), `src/ui/frontend/src/pages/JobsInReview.tsx` (deleted), `src/ui/frontend/src/pages/JobsResponded.tsx` (deleted), `src/ui/frontend/src/contexts/StateUiContext.tsx`, `src/ui/frontend/src/pages/JobsJobDetail.tsx`, `src/ui/frontend/src/components/AdminRoute.tsx`, `src/ui/frontend/src/pages/CandidateSurferConsent.tsx`, `tests/component/frontend/pages/test_JobsInReview.test.tsx` (deleted), `tests/component/frontend/pages/test_JobsResponded.test.tsx` (deleted), `docs/test-bible/frontend/pages.md`.

**Technical scope:**

* `routes.tsx` — the Jobs route table is modified, and the index + catch-all render the landing redirect.
* `JobsHomeRedirect.tsx` — a new component. It reads the resolved nav for the selected candidate and navigates to the first Jobs item with `count > 0`, falling back to the first Jobs item. It is the only place the landing choice is made.
* `JobsRecommended.tsx` — the page component is modified to take its view (ready / review) and title from the route, fetch that view, drop the meteorite-prefix sub-section split, and add a sortable Source column showing the job's stored `source` (`—` when null).
* `JobsProcessing.tsx` — a new page component: a state-sectioned list over `view=processing`, sections from the manifest with the existing legacy-state fallback for hop labels, and rows opening `JobDetailModal` (whose existing Skip button now succeeds on these states).
* `StateUiContext.tsx` — the manifest TS interface is modified to match.
* `JobsJobDetail.tsx`, `AdminRoute.tsx`, `CandidateSurferConsent.tsx` — the hard-coded `/jobs/recommended` target is modified to `/`, the landing route.

## Acceptance criteria

11. **Landing page.** For a candidate with Ready = 0 and Review = 3, loading `/` lands on `/jobs/review`. With all six counts at 0, it lands on `/jobs/ready`. Browsing to `/jobs/recommended` or `/nope` follows the same rule, and so does closing the detail deeplink modal. `rg -n '"/jobs/(recommended|ready|review)"' src/ui/frontend/src --glob '!routes.tsx' --glob '!JobsHomeRedirect.tsx'` returns nothing. **Fail:** a different landing page, a 404 / blank page, or another hard-coded landing target outside the redirect.
12. **Old routes gone.** `rg -n "jobs/in_review|jobs/recommended|jobs/responded" src/ui/frontend/src src/utils/config.py src/ui/api` returns nothing, and `JobsInReview.tsx` and `JobsResponded.tsx` no longer exist. **Fail:** any hit or file present.
13. **Ready / Review behave like Recommended, with Source.** On Review, every row has the Generate Artifacts row action and the bulk bar offers Generate. On Ready, no row does. Both pages keep the Analysis toggle and Total, and their titles read "Ready" / "Review". Each row's Source cell equals the job's `source` (`meteorite` for a meteorite-track job), and no separate "Meteorites" section heading renders. `rg -n "meteorite_section" src` returns nothing. **Fail:** Generate on a `CANDIDATE_REVIEW` row, missing toggle / Total / Source, a meteorite sub-section, or the grep hits.
14. **Builds clean.** `python -c "import src.utils.config"` exits 0. In `src/ui/frontend`, `npm run build` exits 0, and `npm run lint` reports no problem absent on `origin/dev`. **Fail:** non-zero exit, or a new lint problem.

## Boundaries

Does not touch any backend file ([AST-1974](https://linear.app/astralcareermatch/issue/AST-1974)) or `JobsMeteorites.tsx` ([AST-1976](https://linear.app/astralcareermatch/issue/AST-1976)). Consumes the `view=` branches, nav counts, manifest shape, and widened skip legality that [AST-1974](https://linear.app/astralcareermatch/issue/AST-1974) ships.

## Notes for planning

Parent [AST-1970](https://linear.app/astralcareermatch/issue/AST-1970) definition is authoritative (Functional scope, Architectural definition, Canon Scope: `stat.logging.info.api`, `stat.logging.error`).

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1970-jobs-nav`, child `sub/AST-1970/AST-1975-jobs-nav`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-04T19:07:50.592Z
[code-rubric] PROCEED (Commit: 031da688b) Frontend nav matches plan

#### betty — 2026-10-04T19:05:55.463Z
`origin/sub/AST-1970/AST-1975-jobs-nav` @ `031da688b` · Jobs nav tests rebuilt

#### joan — 2026-10-04T18:43:34.586Z
[plan-rubric] PROCEED (Commit: 1f25d594) Frontend routes and landing

#### hedy — 2026-10-04T18:42:19.955Z
`origin/sub/AST-1970/AST-1975-jobs-nav` @ `1f25d594a` · two-stage frontend plan

---

# AST-1975 — Ready / Review / Processing pages, landing, and Jobs routes

- **Ticket:** [AST-1975](https://linear.app/astralcareermatch/issue/AST-1975)
- **Parent:** [AST-1970 — Jobs Navigation changes](https://linear.app/astralcareermatch/issue/AST-1970)
- **Publish ref:** `sub/AST-1970/AST-1975-jobs-nav` (origin only)
- **Canon Scope:** none — every file is under `src/ui/frontend/` (ticket § Citations)
- **Depends on:** [AST-1974](https://linear.app/astralcareermatch/issue/AST-1974) (on `origin/ftr/AST-1970-jobs-nav`, merged into this ref at plan time)

Frontend half of the Jobs nav re-cut. The Recommended list component becomes the one list
component for **Ready** (`view=ready`) and **Review** (`view=review`). It takes its view and title
from the route, drops the meteorite-prefix sub-section, and gains a sortable **Source** column.
**Processing** replaces In Review: same state-sectioned table over `view=processing`, rows open
`JobDetailModal`, whose existing Skip button now succeeds because AST-1974 widened skip legality.
A new `JobsHomeRedirect` is the single place the landing page is chosen (first Jobs nav item with
`count > 0`, else the first Jobs item). The index route, the catch-all, and the three hard-coded
`/jobs/recommended` targets all go through it. In Review and Responded pages and routes are removed,
and the manifest TS type follows AST-1974's reshaped jobs block. No backend file and no
`JobsMeteorites.tsx` ([AST-1976](https://linear.app/astralcareermatch/issue/AST-1976)) is touched.

## Backend contract consumed (from AST-1974, verified on this ref)

- `GET /api/state_ui_manifest` → `jobs.processing_sections: [{state, label}]` (renamed from
  `in_review_sections`; ends with `{"state": "BUILD_ARTIFACTS", "label": "Building Artifacts"}`);
  `jobs.recommended.sections` = `[{RECOMMENDED, "Review"}, {CANDIDATE_REVIEW, "Ready"}]`;
  `jobs.recommended.meteorite_section` **removed**; `primary_actions_by_state` unchanged
  (`RECOMMENDED` carries `generate_artifacts`, `CANDIDATE_REVIEW` does not — AC 13 is manifest-driven).
- `GET /api/jobs?view=ready|review|processing&candidate_id=X` — rows come from `SELECT * FROM job`
  via `_job_row_to_dict`, so every row already carries `source` (`company` | `meteorite` | null).
- `GET /api/nav_config?candidate_id=X` → `[{label, items: [{label, path, enabled, count?}]}]`;
  the Jobs group has `label: "Jobs"` and items in order `/jobs/ready`, `/jobs/review`,
  `/jobs/applied`, `/jobs/processing`, `/jobs/skipped`, `/jobs/meteorites`, each with `count`
  when a candidate id is passed.

## Scope gate

Every row below is in this ticket's `## Scope` Component list, and every change is the kind its
Technical scope describes for that file. No file outside the list is touched.

## Files Changed (planned)

| File | Change | Layer | Stage |
|------|--------|-------|-------|
| `src/ui/frontend/src/components/JobsHomeRedirect.tsx` | **New** — fetch nav for selected candidate, `<Navigate replace>` to first Jobs item with `count > 0`, else first Jobs item | ui | 1 |
| `src/ui/frontend/src/pages/JobsJobDetail.tsx` | Three `/jobs/recommended` targets → `/` | ui | 1 |
| `src/ui/frontend/src/components/AdminRoute.tsx` | Non-admin redirect `/jobs/recommended` → `/` | ui | 1 |
| `src/ui/frontend/src/pages/CandidateSurferConsent.tsx` | Decline navigate `/jobs/recommended` → `/` | ui | 1 |
| `src/ui/frontend/src/contexts/StateUiContext.tsx` | `in_review_sections` → `processing_sections`; `recommended.meteorite_section` removed | ui | 2 |
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | `view` / `title` props; fetch `view=${view}`; meteorite sub-section removed; sortable Source column | ui | 2 |
| `src/ui/frontend/src/pages/JobsProcessing.tsx` | **New** (via `git mv` from `JobsInReview.tsx`) — `view=processing`, `processing_sections`, title Processing | ui | 2 |
| `src/ui/frontend/src/pages/JobsInReview.tsx` | **Deleted** (moved to `JobsProcessing.tsx`) | ui | 2 |
| `src/ui/frontend/src/pages/JobsResponded.tsx` | **Deleted** | ui | 2 |
| `src/ui/frontend/src/routes.tsx` | Jobs route table re-cut; index + catch-all render `JobsHomeRedirect` | ui | 2 |
| `tests/component/frontend/pages/test_JobsInReview.test.tsx` | Deleted — **Betty (qa-child)**, not build-child | tests | — |
| `tests/component/frontend/pages/test_JobsResponded.test.tsx` | Deleted — **Betty (qa-child)**, not build-child | tests | — |
| `docs/test-bible/frontend/pages.md` | Retire In Review / Responded entries — **Betty (qa-child)**, not build-child | bible | — |

⚠️ **Decision:** The last three rows are in this ticket's Scope, but engineers never commit to
`tests/` or `docs/test-bible/**` (AGENTS.md; the pre-commit hook blocks it). build-child does
**not** touch them. They are listed so qa-child picks them up from this plan, and so nobody reads
their absence from the build diff as a scope gap.

⚠️ **Decision:** Stage order keeps the tree compiling after each commit. Stage 1 only adds the
redirect component and repoints three targets to `/`. At that point `/` still resolves through the
old index `<Navigate to="/jobs/recommended">`, so nothing breaks mid-way. Stage 2 makes every
manifest-type consumer and route change in one commit, because renaming `in_review_sections` breaks
`JobsInReview.tsx` and moving that file breaks `routes.tsx`.

## Stage 1: Landing redirect component and landing targets

**Done when:** `JobsHomeRedirect.tsx` exists and builds (not yet routed), and
`rg -n '"/jobs/recommended"' src/ui/frontend/src --glob '!routes.tsx'` returns nothing.
`npm run build` exits 0.

1. Create `src/ui/frontend/src/components/JobsHomeRedirect.tsx` with exactly this content:

   ```tsx
   import { useEffect, useState } from "react"
   import { Navigate } from "react-router-dom"
   import { useCandidate } from "../contexts/CandidateContext"
   import api from "../lib/api"

   interface NavItem { path: string; count?: number }
   interface NavGroup { label: string; items: NavItem[] }

   // NAV_CONFIG group label in src/utils/config.py — the Jobs items, in nav order.
   const JOBS_NAV_GROUP_LABEL = "Jobs"

   /**
    * AST-1975: the only place the landing page is chosen. First Jobs nav item with
    * count > 0, else the first Jobs item. Serves `/`, the catch-all, and every former
    * `/jobs/recommended` target (they navigate to `/`).
    */
   export default function JobsHomeRedirect() {
     const { selectedId, candidatesHydrated } = useCandidate()
     const [target, setTarget] = useState<string | null>(null)
     const [failed, setFailed] = useState(false)

     useEffect(() => {
       // Wait for the candidate bind — counts before it would be for the wrong (or no) candidate.
       if (!candidatesHydrated) return
       let cancelled = false
       const params = selectedId ? `?candidate_id=${encodeURIComponent(selectedId)}` : ""
       api(`/api/nav_config${params}`)
         .then(r => { if (!r.ok) throw new Error(String(r.status)); return r.json() })
         .then((groups: NavGroup[]) => {
           if (cancelled) return
           const items = groups.find(g => g.label === JOBS_NAV_GROUP_LABEL)?.items ?? []
           const pick = items.find(i => (i.count ?? 0) > 0) ?? items[0]
           if (pick) setTarget(pick.path)
           else setFailed(true)
         })
         .catch(() => { if (!cancelled) setFailed(true) })
       return () => { cancelled = true }
     }, [candidatesHydrated, selectedId])

     if (target) return <Navigate to={target} replace />
     return (
       <div className="page-container">
         <p className="list-page-status">{failed ? "Navigation unavailable." : "Loading…"}</p>
       </div>
     )
   }
   ```

   ⚠️ **Decision:** The redirect fetches `/api/nav_config` itself. `NavigationShell` keeps its nav
   in local state, and `NavigationShell.tsx` is not in this ticket's Scope, so lifting that state
   into a shared context is out of bounds. The cost is one extra GET on landing only.

   ⚠️ **Decision:** If the nav fetch fails or has no Jobs group, the redirect shows
   "Navigation unavailable." instead of navigating to a hard-coded path. A hard-coded fallback
   path would be a second copy of `NAV_CONFIG` in TS. The sidebar already shows its own error in
   that case.

   ⚠️ **Decision:** The Jobs group is matched by its `NAV_CONFIG` label `"Jobs"`, not by position.
   `_nav_config_for_user` filters admin-only groups, so positions aren't stable.

2. In `src/ui/frontend/src/pages/JobsJobDetail.tsx`:
   - line ~78: `return <Navigate to="/jobs/recommended" replace />` → `return <Navigate to="/" replace />`
   - line ~94: `<Link to="/jobs/recommended" className="btn secondary">Back to Recommended</Link>` →
     `<Link to="/" className="btn secondary">Back to Jobs</Link>`
   - line ~102: `onClose={() => navigate("/jobs/recommended")}` → `onClose={() => navigate("/")}`

   ⚠️ **Decision:** The link label changes "Back to Recommended" → "Back to Jobs". The Recommended
   page no longer exists, and the destination now varies with the counts.

3. In `src/ui/frontend/src/components/AdminRoute.tsx` line ~12:
   `return <Navigate to="/jobs/recommended" replace />` → `return <Navigate to="/" replace />`.

4. In `src/ui/frontend/src/pages/CandidateSurferConsent.tsx` line ~116:
   `navigate("/jobs/recommended")` → `navigate("/")`.

5. Verify (see **Verification commands** below): `npm run build` exits 0; `npm run lint` per the lint rule;
   `rg -n '"/jobs/recommended"' src/ui/frontend/src --glob '!routes.tsx'` returns nothing.

Commit: `code(AST-1975): JobsHomeRedirect + landing targets to /`

## Stage 2: Manifest type, Ready / Review, Processing, routes

**Done when:** AC 11–14 hold. `/`, `/nope`, and `/jobs/recommended` land via
`JobsHomeRedirect`. `/jobs/ready` and `/jobs/review` render the list titled "Ready" / "Review" with
a Source column and no Meteorites section. `/jobs/processing` renders state sections whose rows open
`JobDetailModal`. `JobsInReview.tsx` / `JobsResponded.tsx` are gone. Every grep below returns nothing.

### 2a. `StateUiContext.tsx` — manifest type

1. Line ~8: `in_review_sections: Array<{ state: string; label: string }>` →
   `processing_sections: Array<{ state: string; label: string }>`.
2. Delete lines ~54–59 (the `// AST-1057: partition by METEORITE_CONFIG company prefix (manifest-driven).`
   comment and the whole `meteorite_section?: { section_id; label; company_prefix }` member).
   Leave `report_meteorite_sections` (report modal pane) untouched.

### 2b. `JobsRecommended.tsx` — Ready / Review list

1. `interface Job`: add `source?: string | null` after `state_changed_at`.
2. `sortRecommendedJobs`: directly after the `col === "company"` branch add
   `} else if (col === "source") {` / `cmp = (a.source || "").localeCompare(b.source || "")`.
3. Above `export default function Recommended()` add:

   ```tsx
   // AST-1975: one list component for Jobs → Ready and Jobs → Review; the route supplies both.
   interface RecommendedProps { view: "ready" | "review"; title: string }
   ```

   and change the signature to `export default function Recommended({ view, title }: RecommendedProps) {`.
4. In `load`: the URL becomes
   `` `/api/jobs?view=${view}&candidate_id=${encodeURIComponent(selectedId)}` ``; its dependency array
   becomes `[selectedId, view, beginRefresh, endRefresh]`.
5. Replace the whole `sections` `useMemo` body (meteorite split removed) with:

   ```tsx
   const sections = useMemo(() => {
     if (!manifest) return []
     const byState: Record<string, Job[]> = {}
     for (const job of rows) {
       if (!byState[job.state]) byState[job.state] = []
       byState[job.state].push(job)
     }
     const knownStates = manifest.jobs.recommended.sections.map(r => r.state)
     const normal = manifest.jobs.recommended.sections
       .filter(row => (byState[row.state]?.length ?? 0) > 0)
       .map(row => ({ state: row.state, label: row.label, jobs: byState[row.state] }))
     const legacy = unmappedJobStates(rows, knownStates)
       .filter(s => byState[s]?.length)
       .map(s => ({ state: s, label: legacyStateSectionLabel(s), jobs: byState[s] }))
     return [...normal, ...legacy]
   }, [rows, manifest])
   ```

   ⚠️ **Decision:** Keep the state-section rendering, not a flat table. Each view returns one state, so
   each page shows one section (e.g. "Review (3)"). Keeping it preserves today's per-section sort keys
   and the legacy-state fallback without new code.
6. `<h1 className="list-page-title">Recommended</h1>` → `<h1 className="list-page-title">{title}</h1>`.
7. Empty state `No recommended jobs yet` → `` {`No jobs in ${title}`} ``.
8. Column count: `const columnCount = 7 + ...` → `8 + ...`; update its comment to
   `// checkbox + actions + title + company + source + state + phase cols + total + updated`.
9. Header: directly after the Company `<th>` add
   `<th className="sortable" onClick={() => handleSort(sec.state, "source")}>Source{sortIndicator(sec.state, "source")}</th>`.
10. Row: directly after `<td>{job.company}</td>` add `<td>{job.source || "\u2014"}</td>`.

### 2c. `JobsProcessing.tsx` — Processing list (successor to In Review)

1. `git mv src/ui/frontend/src/pages/JobsInReview.tsx src/ui/frontend/src/pages/JobsProcessing.tsx`.
2. In `JobsProcessing.tsx`:
   - `export default function InReview()` → `export default function Processing()`.
   - `view=in_review` → `view=processing` in the `load` URL.
   - Both `manifest.jobs.in_review_sections` → `manifest.jobs.processing_sections`.
   - `<h1 className="list-page-title">In Review</h1>` → `Processing`.
   - Empty state `No jobs in review` → `No jobs processing`.
   - Directly above `export default function Processing()` add
     `// AST-1975: Jobs → Processing — every job not on Ready / Review / Applied / Skipped; rows open JobDetailModal (Skip).`
   - Nothing else changes: `JobDetailModal`, the grade columns, the expand policy, and the
     `unmappedJobStates` / `legacyStateSectionLabel` fallback stay as they are.

   ⚠️ **Decision:** Hop-labeled states (`BUILD_ARTIFACTS.<task>`) aren't in `processing_sections`, so they
   render through the existing legacy fallback ("BUILD ARTIFACTS.<task> (legacy — not in current
   manifest)"). The Technical scope says to use "the existing legacy-state fallback for hop labels",
   so no new hop-to-base grouping is added.

### 2d. Delete Responded

1. `git rm src/ui/frontend/src/pages/JobsResponded.tsx`.

### 2e. `routes.tsx` — route table

1. Line 4: `import { Navigate, Outlet, type RouteObject } from "react-router-dom"` →
   `import { Outlet, type RouteObject } from "react-router-dom"` (`Navigate` has no remaining use).
2. After `import AdminRoute from "./components/AdminRoute"` add
   `import JobsHomeRedirect from "./components/JobsHomeRedirect"`.
3. Jobs import block becomes exactly:

   ```tsx
   // --- Jobs ---
   import Recommended from "./pages/JobsRecommended"
   import Processing from "./pages/JobsProcessing"
   import Skipped from "./pages/JobsSkipped"
   import Applied from "./pages/JobsApplied"
   import JobsMeteorites from "./pages/JobsMeteorites"
   import JobsJobDetail from "./pages/JobsJobDetail"
   ```

4. Index: `{ index: true, element: <Navigate to="/jobs/recommended" replace /> },` →
   `{ index: true, element: <JobsHomeRedirect /> },`.
5. The `// Jobs` route block becomes exactly (nav order, then the deeplink):

   ```tsx
   // Jobs
   { path: "jobs/ready", element: <Recommended key="ready" view="ready" title="Ready" /> },
   { path: "jobs/review", element: <Recommended key="review" view="review" title="Review" /> },
   { path: "jobs/applied", element: <Applied /> },
   { path: "jobs/processing", element: <Processing /> },
   { path: "jobs/skipped", element: <Skipped /> },
   { path: "jobs/meteorites", element: <JobsMeteorites /> },
   { path: "jobs/detail/:jobId", element: <JobsJobDetail /> },
   ```

   ⚠️ **Decision:** Distinct `key`s force a remount when moving between Ready and Review. Otherwise
   React reuses the instance (same component type, same slot), and selection and sort state would
   carry over from one list to the other.
6. Catch-all: `{ path: "*", element: <Navigate to="/jobs/recommended" replace /> },` →
   `{ path: "*", element: <JobsHomeRedirect /> },`.

### 2f. Verify

1. `npm run build` exits 0; `npm run lint` per the lint rule (see **Verification commands**).
2. `PYTHONPATH=src:. ~/astral/.venv/bin/python -c "import src.utils.config"` exits 0.
3. Each of these returns nothing:
   - `rg -n '"/jobs/(recommended|ready|review)"' src/ui/frontend/src --glob '!routes.tsx' --glob '!JobsHomeRedirect.tsx'`
   - `rg -n "jobs/in_review|jobs/recommended|jobs/responded" src/ui/frontend/src src/utils/config.py src/ui/api`
   - `rg -n "\bmeteorite_section\b|in_review_sections|view=in_review|view=recommended" src/ui/frontend/src`
   - `ls src/ui/frontend/src/pages/JobsInReview.tsx src/ui/frontend/src/pages/JobsResponded.tsx` (both "No such file")

Commit: `code(AST-1975): Ready/Review list with Source, Processing page, Jobs routes via JobsHomeRedirect`

## Verification commands (both stages)

```bash
cd src/ui/frontend
test -d node_modules || npm ci   # installs the existing lockfile only — no new dependency
npm run build
npm run lint
```

**Lint rule (AC 14: "no problem absent on `origin/dev`"):** `npm run lint` exiting 0 passes. If it
reports problems, every reported problem must sit on a line that `git diff origin/dev -- <file>`
does **not** show as added (i.e. pre-existing). Any problem on an added line gets fixed in the
same stage. If the fix needs a change this plan doesn't describe, stop and comment per the
execution contract.

## Manual check (AC 11, 13 — for build-child smoke, Betty owns automation)

- Candidate with Ready = 0, Review > 0: load `/` → URL becomes `/jobs/review`. Load `/nope` and `/jobs/recommended` → same.
  Open `/jobs/detail/<id>` and close the modal → same.
- Candidate with all six counts 0 → `/jobs/ready`.
- `/jobs/review`: every row's actions show Generate Artifacts. `/jobs/ready`: none do. Both have the
  Analysis toggle, Total, and a Source cell equal to the job's `source`. No "Meteorites" heading.

## AC traceability

AC11 → S1 (redirect + 3 targets) + S2e (index/catch-all). AC12 → S2c/S2d/S2e + S2f greps.
AC13 → S2b (title, Source, meteorite split removed; Generate stays manifest-driven) + S2a. AC14 → S1 step 5 + S2f.
Parent AC 1–10 are AST-1974; parent AC 14 (Meteorites) is AST-1976.

## Notes for QA (Betty — not edited by this ticket)

- In this ticket's Scope, owned by qa-child: delete `tests/component/frontend/pages/test_JobsInReview.test.tsx`
  and `test_JobsResponded.test.tsx`, and retire In Review / Responded in `docs/test-bible/frontend/pages.md`.
  Processing coverage replaces In Review's.
- Other tests that reference removed paths or names and will fail under vitest (not `npm run build`;
  `tsconfig.app.json` includes only `src`): `tests/component/frontend/fixtures/stateUiManifestFixture.ts`
  (`in_review_sections`, `meteorite_section`), `contexts/test_StateUiContext.test.tsx`,
  `pages/test_JobsRecommended.test.tsx` (now needs `view` / `title` props, `view=` URL, Source, no
  meteorite section), `pages/test_JobsJobDetail.test.tsx`, `pages/test_CandidateSurferConsent.test.tsx`,
  `components/test_AdminRoute.test.tsx` (targets now `/`), `test_routes.test.tsx`,
  `lib/test_sessionAuthMark.test.ts`.
- Parent AC 13's `rg -n "meteorite_section" src` also matches `report_meteorite_sections` (report modal,
  untouched by this epic) in `StateUiContext.tsx` and `api_system.py`. Use `\bmeteorite_section\b`.

## Estimate

Confirm Chuckles estimate: 5 — revise to 3 because it is one layer (frontend), reuses the existing Recommended and In Review list components nearly verbatim, and adds one small new component against an API contract AST-1974 already shipped.


## Joan validate

[plan-rubric]
**Ticket:** AST-1975
**Overall:** APPROVED
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Publish ref:** `origin/sub/AST-1970/AST-1975-jobs-nav` @ `1f25d594a3ae9ead314ecf3dfc8899f2cff6f396`

## Canon scores
(none on ticket — Citations: frontend-only, outside `stat.logging.info.api` / `stat.logging.error` territory)

## Traceability
AC11→S1 JobsHomeRedirect+targets, S2e index/catch-all; AC12→S2c/d/e deletions+routes, S2f greps; AC13→S2a manifest type, S2b Ready/Review+Source+no meteorite split; AC14→S1/S2f build+lint+config import. AC1–10 N/A (AST-1974); parent AC14 N/A (AST-1976).

## Findings

### acceptable — AST-1974 ordering
- **Location:** Plan intro / `## Backend contract consumed`
- **Finding:** Stage 2 manifest and `view=` shapes assume AST-1974 is on this ref.
- **Recommendation:** build-child runs on a ref where #1 is merged; no plan change.

### acceptable — tests deferred to qa-child
- **Location:** Files Changed table; `## Notes for QA`
- **Finding:** Scope lists test/bible deletions but build-child must not commit under `tests/` or `docs/test-bible/**`.
- **Recommendation:** Betty updates per plan; engineer does not treat missing test diff as scope slip.

### discuss — `rubricDisplay.ts` comment
- **Location:** `src/ui/frontend/src/lib/rubricDisplay.ts` (~line 75)
- **Finding:** Comment still names `JobsInReview`; plan does not rename to Processing.
- **Recommendation:** Optional one-line comment tweak during Stage 2c; not AC-blocking.

context_tokens≈36000

## Review

- **Branch:** `origin/sub/AST-1970/AST-1975-jobs-nav`
- **Build commits:** `d5021e5a0` (Stage 1 JobsHomeRedirect + landing targets), `d15e73290` (Stage 2 manifest type, Ready/Review with Source, Processing, routes)
- **Build notes:** `npm run build` and `npx tsc -b --noEmit` exit 0; `python -c "import src.utils.config"` exits 0. All Stage 2f greps return nothing, and `JobsInReview.tsx` / `JobsResponded.tsx` are gone (`JobsProcessing.tsx` via `git mv`). `npm run lint` reports 31 problems, the same count as the tree before this build. None are on added lines; the only one in a touched file is `JobsJobDetail.tsx:18` (`react-hooks/refs`, pre-existing, untouched line).
- **Deviation (comment only):** Stage 1's prescribed `JobsHomeRedirect` doc comment contained the literal `` `/jobs/recommended` ``, which tripped the Stage 2f / AC 12 grep. It was reworded to "the old Recommended page"; the code is unchanged.
- **Not done:** Joan's optional `rubricDisplay.ts` comment tweak, because the file is outside this ticket's Scope.
- **For QA:** test and bible rows from Scope plus the broken-fixture list are in `## Notes for QA` above. No manual browser smoke run was done in this headless build. AC 11 / 13 behaviour is the manual check list above.


## Radia review

[code-rubric]
**Ticket:** AST-1975
**Publish ref:** `031da688bbd69009df37b131eb599b6c507849dd` (`origin/sub/AST-1970/AST-1975-jobs-nav`)
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Overall:** CLEAN

## Canon scores
(frozen list empty — ticket **§ Citations: none**; all scoped paths are `src/ui/frontend/**`, outside `stat.logging.info.api` / `stat.logging.error` territory per plan and Joan)

## Column diff vs plan stage
(aligned) — Joan recorded no directive rows; same conclusion on tip.

## Frame diff
(none)

## Findings

### advisory — sibling product + test carry on publish ref
- **Location:** `src/core/**`, `src/data/**`, `src/ui/api/**`, `src/utils/config.py`, and Betty `tests/**` / `docs/test-bible/**` in `origin/dev...origin/sub/AST-1970/AST-1975-jobs-nav`
- **Finding:** Three-dot diff includes AST-1974 backend commits stacked on this sub (`blockedBy` AST-1974). AST-1975’s own commits (`d5021e5a0`, `d15e73290`) touch only the nine frontend files in the plan; carry is expected, not 1975 scope creep.

### advisory — Joan `rubricDisplay.ts` comment
- **Location:** `src/ui/frontend/src/lib/rubricDisplay.ts` (~line 75)
- **Finding:** Comment still says `JobsInReview`; file is outside Component scope; build notes document intentional skip.
- **Default:** Leave unchanged unless Susan wants a drive-by comment fix in a later hygiene pass.

### advisory — manual AC 11 / 13 smoke
- **Location:** Issue doc **## Review** / **Manual check**
- **Finding:** Build notes: no browser smoke on landing or Generate-on-Review vs Ready; component tests cover redirect/processing/recommended paths.
- **Default:** Parent UAT or Susan spot-check before epic close; not a canon or plan blocker on this tip.

### advisory — parent AC 13 `meteorite_section` grep
- **Location:** `report_meteorite_sections` in `StateUiContext.tsx` / backend
- **Finding:** Word-boundary grep required; frontend removed `meteorite_section` from manifest type and `JobsRecommended` split.

## What's solid
- **Landing:** `JobsHomeRedirect` is sole chooser (first Jobs item with `count > 0`, else first item); index + `*` use it; legacy targets (`AdminRoute`, detail modal, consent decline) go to `/`.
- **Routes:** `jobs/ready` / `jobs/review` (shared `Recommended` with `view` + `title`), `jobs/processing` (`JobsProcessing`, `view=processing`, `processing_sections`), removed `in_review` / `recommended` / `responded` pages and routes.
- **Ready/Review:** Meteorite sub-section removed; Source column + sort; Generate eligibility still manifest `primary_actions_by_state` (Review vs Ready behaviour follows backend manifest, not hardcoded states).
- **Plan greps on tip:** Stage 2f patterns clean; deleted page files absent.
- **Estimate footprint:** Frontend-only delta for 1975 commits fits confirmed **3** points.

## Recommended actions
- Chuckles: append verdict to `docs/features/interface/ast-1975-ready-review-processing-pages-landing-and-jobs-routes.md`, `docs(AST-1975): Radia review — clean`, push `sub/AST-1970/AST-1975-jobs-nav`, post slim upshot `--as radia`, **Review Posted** → PROCEED to **User Testing** (no `resolve-child` canon work).
- Downstream: optional `rubricDisplay.ts` one-line rename; UAT landing/Generate spot-check when AST-1974 backend is on the same ref.

context_tokens≈14000

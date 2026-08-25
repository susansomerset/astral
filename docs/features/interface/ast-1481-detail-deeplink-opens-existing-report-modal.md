# AST-1481 — Detail deeplink opens existing report modal

**Parent:** [AST-1463 — Candidate single page job report](https://linear.app/astralcareermatch/issue/AST-1463/candidate-single-page-job-report)  
**Publish ref:** `sub/AST-1463/AST-1481-detail-deeplink-opens-existing-report-modal`

Thin authenticated deeplink at `/jobs/detail/<astral_job_id>` that opens the **existing** `JobAnalysisReportModal` (same shell as Recommended row-click), aligns admin candidate selection from the job's owning company, handles load failures with an explicit back path, and navigates to `/jobs/recommended` on modal close. Does **not** implement post-auth return-to-deeplink (sibling AST-1482).

## UAT fitness

- **AC restored:** Parent AST-1463 AC 1–5, 7–8 (this ticket's Description AC 1–7 map to these; parent AC 6 post-auth return and AC 9 no-second-UI are owned elsewhere or are epic-level guards).
- **Correct outcome:** Authenticated user pastes or bookmarks `/jobs/detail/<valid_id>` → same Recommended Job Report modal as list row-click (horizontal tabs, sticky header, artifacts actions); hard refresh on that URL boots the SPA and reopens the modal; skipped (and other non-recommended) jobs load when the API returns them; closing the deeplink modal lands on `/jobs/recommended`; admin with multiple candidates sees copy/print/resume structure for the **job owner's** candidate; unknown id shows a labeled error plus a `.btn` back to Recommended.
- **Sibling check:** AST-1482 (return path after re-auth) — still required for parent AC 6; **out of scope here**. Until AST-1482 ships, logged-out deeplink visits still authenticate to `/` (existing behavior). List row-click path in `JobsRecommended.tsx` must remain unchanged (AC 5).
- **Not sufficient:** Registering the route alone, or opening a new full-page report shell, or suppressing API errors without a back CTA.
- **Wrong fix rejected:** Building a second report UI/page instead of reusing `JobAnalysisReportModal`; adding a React-side "recommended states only" gate on the deeplink; touching `RequireAuth` / `Authenticate` for return-path (AST-1482 scope).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add deeplink path constant (not in `NAV_CONFIG`) | utils |
| `src/ui/frontend/src/routes.tsx` | Register authenticated `jobs/detail/:jobId` route | ui |
| `src/ui/frontend/src/pages/JobsJobDetail.tsx` | **New** thin host: param read, prefetch, error UI, modal + close navigate | ui |
| `src/ui/frontend/src/contexts/CandidateContext.tsx` | Admin candidate alignment helper for job company | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | **No change expected** — host owns `onClose` navigation | ui |

## Stage 1: Route path constant and registration

**Done when:** `JOBS_DETAIL_ROUTE_PREFIX` exists in config, `routes.tsx` serves `JobsJobDetail` at `jobs/detail/:jobId` inside the authenticated `NavigationShell`, and a stub page renders without breaking existing routes.

1. In `src/utils/config.py`, immediately **above** the `NAV_CONFIG = [` block (after the existing SYNC comment block ~line 4708), add a deeplink-only constant:

   ```python
   # Deeplink-only — not in NAV_CONFIG (no sidebar item).
   # SYNC: src/ui/frontend/src/routes.tsx path "jobs/detail/:jobId"
   JOBS_DETAIL_ROUTE_PREFIX = "/jobs/detail"
   ```

   Do **not** add a nav item to `NAV_CONFIG`.

2. In `src/ui/frontend/src/routes.tsx`, add `import JobsJobDetail from "./pages/JobsJobDetail"` with the other Jobs imports.

3. In the Jobs route group (before the catch-all `{ path: "*", ... }`), register:

   ```tsx
   { path: "jobs/detail/:jobId", element: <JobsJobDetail /> },
   ```

   Use param name `jobId` (maps to `astral_job_id`).

4. Create `src/ui/frontend/src/pages/JobsJobDetail.tsx` as a minimal placeholder that reads `jobId` from `useParams()`, renders `<p className="list-page-status">Loading job…</p>` when `jobId` is present, and `<Navigate to="/jobs/recommended" replace />` when `jobId` is missing/empty.

   ⚠️ **Decision:** Hard refresh SPA fallback requires **no** `server.py` change — existing `serve_react` catch-all already returns `index.html` for `/jobs/detail/...` (same contract as other in-app routes post AST-1433).

## Stage 2: Modal host, prefetch gate, error UI, close navigation

**Done when:** Visiting `/jobs/detail/<loadable_id>` opens `JobAnalysisReportModal` with the same behavior as Recommended row-click; 404/inaccessible ids show an explicit error with a `.btn secondary` link to `/jobs/recommended`; modal close from deeplink navigates to `/jobs/recommended`; `JobsRecommended.tsx` is untouched.

1. Replace the Stage 1 placeholder in `JobsJobDetail.tsx` with the full host:

   - Imports: `useCallback`, `useEffect`, `useState`; `useNavigate`, `useParams`, `Navigate`, `Link` from `react-router-dom`; `JobAnalysisReportModal`; `api` from `../lib/api`; `useCandidate`.

   - Read `jobId` from `useParams()` — trim; if falsy after trim, `<Navigate to="/jobs/recommended" replace />`.

   - Local state: `gate: "loading" | "ready" | "error"`, `gateError: string | null`.

   - On mount / `jobId` change: set `gate` to `"loading"`, `gateError` null, `GET /api/jobs/${encodeURIComponent(jobId)}` via `api()`.
     - `404` → `gate = "error"`, `gateError = "Job not found"`.
     - Other non-OK → parse `{ error?: string }` JSON when present; `gate = "error"`, message = API error or `` `Load failed (HTTP ${status})` ``.
     - OK → parse body; if `company` is a non-empty string, **await** `alignSelectedCandidateForJobCompany(company)` from context (Stage 3); then `gate = "ready"`.

   - Render:
     - `gate === "loading"` → `<p className="list-page-status">Loading job…</p>` inside `<div className="page-container">`.
     - `gate === "error"` → `<div className="page-container">` with `<h1 className="list-page-title">Job unavailable</h1>`, `<p className="entity-error">{gateError}</p>`, and `<Link to="/jobs/recommended" className="btn secondary">Back to Recommended</Link>`.
     - `gate === "ready"` → `<JobAnalysisReportModal jobId={jobId} onClose={() => navigate("/jobs/recommended")} />` (no `onRefresh` — deeplink has no list to refresh).

   - Do **not** add client-side state allowlists (any job state the API returns is allowed — AC 3).

   - Do **not** modify `JobAnalysisReportModal.tsx` — it already fetches `/api/jobs/<id>` internally; the host prefetch is only for early 404 UX and candidate alignment before first render.

2. Confirm `JobsRecommended.tsx` is **unchanged** — row click → `setReportId` → same modal component (AC 5).

## Stage 3: Admin candidate alignment

**Done when:** Admin session with multiple candidates: opening a deeplink for a job whose company belongs to candidate B while candidate A is selected switches `selectedId` to B **before** the modal mounts, so report API calls, copy/print, and resume-structure fetches use the job owner's profile (AC 6). Non-admin / single-candidate sessions behave as today.

1. In `src/ui/frontend/src/contexts/CandidateContext.tsx`:

   - Extend `CandidateCtx` with `alignSelectedCandidateForJobCompany: (companyShortName: string) => Promise<void>`.

   - Implement in `CandidateProvider` (uses existing `isAdmin` from `useAuth`, `candidates`, `selectedId`, `setSelectedId`):

     ```tsx
     const alignSelectedCandidateForJobCompany = useCallback(async (companyShortName: string) => {
       if (!isAdmin) return
       const sn = companyShortName.trim()
       if (!sn) return
       const res = await api(`/api/companies/${encodeURIComponent(sn)}`)
       if (!res.ok) return  // soft-fail — still open modal
       const data = (await res.json()) as { candidate_id?: unknown }
       const cid = typeof data.candidate_id === "string" ? data.candidate_id.trim() : ""
       if (!cid || cid === selectedId) return
       if (!candidates.some(c => c.astral_candidate_id === cid)) return
       setSelectedId(cid)
     }, [isAdmin, selectedId, candidates, setSelectedId])
     ```

   - Expose on the context provider value and default context stub.

   ⚠️ **Decision:** Owner candidate is resolved via existing `GET /api/companies/<short_name>` → `candidate_id` (jobs table has no `astral_candidate_id` column; company FK is the established scope mechanism per `list_jobs` candidate filter). No new API endpoints.

2. Wire Stage 2 host to await alignment before setting `gate = "ready"` so `JobAnalysisReportModal` never mounts with the wrong `selectedId` for resume-structure fetch.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Joan validate

```
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1481
**Overall:** APPROVED
**Publish ref:** `be233e6a8eb1198bfb2906aa3c43e4c6fd0b5989` (`origin/sub/AST-1463/AST-1481-detail-deeplink-opens-existing-report-modal`)

## Traceability
AC1–7 → Stage 1 (AC2 route + SPA boot), Stage 2 (AC1,3–5,7 modal host, prefetch gate, error UI, close navigate), Stage 3 (AC6 admin candidate alignment via company→candidate_id); parent AC6 → AST-1482 out of scope (documented); parent AC9 → honored (reuse modal, no second report shell).

## Findings

**discuss** — `## Estimate` only; no formal **Self-assessment** block (Scope/Conf/Risk). Plan complexity is modest and stages are specific; non-blocking.

**acceptable** — Host prefetch + modal internal fetch duplicates `GET /api/jobs/<id>` by design for early 404/candidate gate; documented in Stage 2.

**acceptable** — `routes.tsx` file-header SYNC comment still says every route needs a `NAV_CONFIG` item; deeplink is intentionally nav-less per parent scope. Config `JOBS_DETAIL_ROUTE_PREFIX` + inline route string matches existing NAV_CONFIG SYNC pattern.
```

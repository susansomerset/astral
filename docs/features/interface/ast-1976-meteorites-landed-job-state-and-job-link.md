<!-- linear-archive: AST-1976 archived 2026-10-08 -->

## Linear archive (AST-1976)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1976/meteorites-landed-job-state-and-job-link-jobs-navigation-changes  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1970 — Jobs Navigation changes  
**Blocked by / blocks / related:** parent: AST-1970

### Description

## What this implements

After #1. Adds the landed-job state column and the in-page Job Analysis Report link to Jobs → Meteorites. Does **not** change the list API (#1) or any other Jobs page (#2).

## Citations

none — frontend-only, outside both statutes' territory.

## Scope

**Component scope:** `src/ui/frontend/src/pages/JobsMeteorites.tsx`.

**Technical scope:**

* `JobsMeteorites.tsx` — the page component is modified: a landed-job state column, and the job cell opens `JobAnalysisReportModal` in place, with the row click still opening `MeteoriteDetailModal`.

## Acceptance criteria

14. **Meteorites show landed-job state.** For every Meteorites row with an `astral_job_id`, the landed-job state cell equals `GET /api/jobs/<id>` `.state`. Rows without a job show `—`. Clicking the job link opens the Job Analysis Report modal for that id while the URL stays `/jobs/meteorites`, and clicking elsewhere on the row still opens the Meteorite modal. **Fail:** stale or missing state, navigation away, or the wrong modal.
15. **Builds clean.** `python -c "import src.utils.config"` exits 0. In `src/ui/frontend`, `npm run build` exits 0, and `npm run lint` reports no problem absent on `origin/dev`. **Fail:** non-zero exit, or a new lint problem.

## Boundaries

Does not change the meteorite list API (landed-job state is served by [AST-1974](https://linear.app/astralcareermatch/issue/AST-1974)) or any other Jobs page ([AST-1975](https://linear.app/astralcareermatch/issue/AST-1975)).

## Notes for planning

Parent [AST-1970](https://linear.app/astralcareermatch/issue/AST-1970) definition is authoritative (Functional scope, Architectural definition, Canon Scope: `stat.logging.info.api`, `stat.logging.error`).

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1970-jobs-nav`, child `sub/AST-1970/AST-1976-jobs-nav`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-04T19:17:37.964Z
[code-rubric] PROCEED (Commit: 3f70dc43e) Meteorites page matches plan

#### betty — 2026-10-04T19:16:00.001Z
`origin/sub/AST-1970/AST-1976-jobs-nav` @ `3f70dc43e` · Meteorites state + link tests

#### joan — 2026-10-04T19:12:51.930Z
[plan-rubric] PROCEED (Commit: bf9af69ee) Meteorites state and job link

#### katherine — 2026-10-04T19:11:37.414Z
`origin/sub/AST-1970/AST-1976-jobs-nav` @ `bf9af69ee` · one-file render overrides

---

# AST-1976 — Meteorites landed-job state and job link

- **Ticket:** [AST-1976](https://linear.app/astralcareermatch/issue/AST-1976)
- **Parent:** [AST-1970 — Jobs Navigation changes](https://linear.app/astralcareermatch/issue/AST-1970)
- **Publish ref:** `sub/AST-1970/AST-1976-jobs-nav` (origin only)
- **Canon Scope:** none — the one file is under `src/ui/frontend/` (ticket § Citations). Parent ids `stat.logging.info.api`, `stat.logging.error` stay id-only; no API / logging code is touched.
- **Depends on:** [AST-1974](https://linear.app/astralcareermatch/issue/AST-1974) (on `origin/ftr/AST-1970-jobs-nav`, merged into this ref at plan time)

Jobs → Meteorites already renders whatever columns the list API sends. AST-1974 added the
landed job's current state to each row (`job_state`) and a "Job State" column to the column
config, so the column header appears with no frontend change. What is missing is the cell
behavior: an unlanded row prints an empty cell instead of `—`, and the Job cell is plain text.
This ticket gives `JobsMeteorites.tsx` two column `render` overrides: **Job State** prints the raw
state or `—`, and **Job** becomes a link button that opens `JobAnalysisReportModal` in place
(URL stays `/jobs/meteorites`). The click stops propagation, so clicking anywhere else on the row
still opens `MeteoriteDetailModal`. The report modal's `onRefresh` reloads the list, so a
Skip / primary action taken in the modal shows up in the Job State cell without a page reload.
No backend file, CSS file, or other Jobs page ([AST-1975](https://linear.app/astralcareermatch/issue/AST-1975)) is touched.

## Backend contract consumed (from AST-1974, verified on this ref)

- `GET /api/candidates/<id>/meteorites` → `{columns, meteorites}`.
- `meteorites[]` rows carry `astral_job_id` (string | null) and `job_state` (the landed job's
  current `job.state` via `LEFT JOIN job j ON j.astral_job_id = m.astral_job_id`; `null` when
  unlanded or the job row is gone) — `src/ui/api/api_meteorite.py` `_LIST_KEYS`,
  `src/data/database.py` `list_meteorites_for_candidate`.
- `columns` (`JOBS_METEORITES_LIST_COLUMNS`, `src/utils/config.py`) has
  `{"key": "astral_job_id", "label": "Job", "sortable": True}` followed immediately by
  `{"key": "job_state", "label": "Job State", "sortable": True}`.
- Because `job_state` is the live join (not a copy), it equals `GET /api/jobs/<id>` `.state` at
  read time — AC 14's "stale" failure can only come from the page not reloading after the modal
  changes the job, which `onRefresh={load}` covers.

## Scope gate

The one file below is this ticket's whole `## Scope` Component list, and the change (state
column cell + job cell opening `JobAnalysisReportModal` in place, row click unchanged) is exactly
the Technical scope's description. No file outside it is touched. The existing
`.dispatch-batch-link` class (`App.css`) is reused, so no CSS edit is needed.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/JobsMeteorites.tsx` | `job_state` on the row type; `render` overrides for `astral_job_id` (link button → report modal) and `job_state` (`—` when null); `reportJobId` state + `JobAnalysisReportModal` mount with `onRefresh={load}` | ui (frontend) |

## Options considered

1. **Column `render` overrides inside `JobsMeteorites.tsx`** (chosen) — same shape as
   `AdminVectorFeedback.tsx`'s Batch column (`ListPage` `render`, `.dispatch-batch-link` button,
   `e.stopPropagation()`, `"—"` when empty). One file, server stays the column authority.
2. **Navigate to `/jobs/detail/:jobId`** (the deeplink host) — rejected: AC 14 requires the URL to
   stay `/jobs/meteorites`.
3. **`rowActions` "Open job" button** — rejected: AC 14 asks for a job *link* in the row, and a
   separate action column adds a control the definition doesn't describe.
4. **Open the job report from inside `MeteoriteDetailModal`** — rejected: different file (out of
   scope) and the row click must keep opening the Meteorite modal itself.

## Stage 1: Landed-job state cell and in-page job link

**Done when:** On Jobs → Meteorites, a landed row's Job State cell shows the job's raw state and
an unlanded row shows `—`. Clicking the Job id opens the Job Analysis Report modal for that id
(URL unchanged); clicking any other cell opens the Meteorite modal. `npm run build` exits 0 and
`npm run lint` adds no problem vs `origin/dev`.

1. In `src/ui/frontend/src/pages/JobsMeteorites.tsx`, add the import directly below the
   `ListPage` import line:

   ```tsx
   import JobAnalysisReportModal from "../components/JobAnalysisReportModal"
   ```

2. In `interface MeteoriteRow`, add `job_state: string | null` on the line directly after
   `astral_job_id: string | null`. Change the interface's doc comment to
   `/** List row from GET /api/candidates/<id>/meteorites (AST-1748; job_state AST-1974). */`

3. Change the component doc comment from
   `/** AST-1749: Jobs → Meteorites — candidate-scoped staging-row list (read-only). */` to
   `/** AST-1749: Jobs → Meteorites — candidate-scoped staging-row list (read-only); AST-1976 landed-job state + in-page job report link. */`

4. Directly below `const [viewingId, setViewingId] = useState<number | null>(null)`, add:

   ```tsx
   const [reportJobId, setReportJobId] = useState<string | null>(null)
   ```

5. Replace the `columns` `useMemo` body so each API column keeps its existing mapping and the two
   landed-job columns get a `render`. Exact replacement:

   ```tsx
   const columns: Column<MeteoriteRow>[] = useMemo(
     () =>
       apiColumns.map(c => {
         const col: Column<MeteoriteRow> = {
           key: c.key,
           label: c.label,
           sortable: c.sortable !== false,
           ...(c.defaultDesc ? { defaultDesc: true } : {}),
           ...(c.type ? { type: c.type } : {}),
         }
         // Job cell opens the landed job's report in place; stopPropagation keeps the row click (Meteorite modal) from also firing.
         if (c.key === "astral_job_id") {
           col.render = value => {
             const jobId = String(value ?? "")
             if (!jobId) return "—"
             return (
               <button
                 type="button"
                 className="dispatch-batch-link"
                 onClick={e => {
                   e.stopPropagation()
                   setReportJobId(jobId)
                 }}
                 title="Open job report"
               >
                 {jobId}
               </button>
             )
           }
         }
         // Raw job.state (matches GET /api/jobs/<id>.state); null = not landed or job row gone.
         if (c.key === "job_state") {
           col.render = value => (value ? String(value) : "—")
         }
         return col
       }),
     [apiColumns],
   )
   ```

   ⚠️ **Decision:** Overrides are keyed on the API column `key`, not appended client-side — the
   server (`JOBS_METEORITES_LIST_COLUMNS`) stays the single source of column order and labels. If
   the server ever drops either key, the override simply doesn't apply.

   ⚠️ **Decision:** Job State prints the raw state string (e.g. `CANDIDATE_REVIEW`), not a
   friendly label — AC 14 checks the cell *equals* `GET /api/jobs/<id>` `.state`, and the
   meteorite `State` column on the same table already shows raw states.

   ⚠️ **Decision:** The Job cell also shows `—` when `astral_job_id` is null (as the
   `AdminVectorFeedback` Batch precedent does), so an unlanded row reads `—` / `—` instead of
   blank / `—`. No button renders without an id, so there is nothing to click.

6. In the returned JSX, directly after the
   `<MeteoriteDetailModal meteoriteId={viewingId} onClose={() => setViewingId(null)} />` line, add:

   ```tsx
   <JobAnalysisReportModal
     jobId={reportJobId}
     onClose={() => setReportJobId(null)}
     onRefresh={load}
   />
   ```

   ⚠️ **Decision:** `onRefresh={load}` — the report modal calls `onRefresh` after its primary
   action and after Skip (`JobAnalysisReportModal.tsx` ~L639 / ~L679), so the Job State cell
   reflects the new state on close. This is what keeps AC 14 from failing on "stale state".

7. Verify, from `src/ui/frontend`:
   - `npm run build` exits 0.
   - `npm run lint` — no problem absent on `origin/dev`. This ticket touches one file, so run
     `npx eslint src/pages/JobsMeteorites.tsx`. At plan time (file identical to `origin/dev`)
     it reports exactly **one** baseline problem: `react-hooks/set-state-in-effect` on the
     existing `useEffect(() => { load() }, [load])`. After this stage it must report that same
     one problem and nothing else. Do **not** fix the baseline error (out of scope). Any
     additional problem → stop and comment (plan contract).
   - From repo root: `python -c "import src.utils.config"` exits 0 (AC 15; unchanged by this
     ticket, run as the gate).
   - `rg -n "navigate\(|useNavigate" src/ui/frontend/src/pages/JobsMeteorites.tsx` returns
     nothing (the link must not route).

## For QA (Betty)

- Existing `tests/component/frontend/pages/test_JobsMeteorites.test.tsx` mocks the list
  response; the row-click test should still pass because only the Job cell stops propagation.
  New coverage for AC 14 would need the mock to include `job_state` and a `job_state` column, and
  a mocked `GET /api/jobs/<id>` for the report modal.
- The report modal reads `useStateUi()` and `useCandidate()`; the existing test harness for
  `JobsRecommended` already provides both and is a reference for wrapping.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Review

- **Branch:** `origin/sub/AST-1970/AST-1976-jobs-nav`
- **Build commits:** `19badde6d` (Stage 1 Job State cell + in-page job report link)
- **Build notes:** `npm run build` (includes `tsc -b`) exits 0; `python -c "import src.utils.config"` exits 0; `rg -n "navigate\(|useNavigate"` on the page returns nothing. `npx eslint src/pages/JobsMeteorites.tsx` reports the one baseline problem (`react-hooks/set-state-in-effect` on the existing `useEffect(() => { load() }, [load])`, identical on `origin/dev`) and nothing else — left unfixed per plan step 7.
- **Deviation:** none. Joan's `*/.` note was a sentence period after the code span in steps 2–3; the code uses a plain `*/`, and the plan text was tidied.
- **For QA:** see `## For QA (Betty)` above. No manual browser smoke run in this headless build.

## Joan validate

[plan-rubric]
**Ticket:** AST-1976
**Overall:** APPROVED
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Publish ref:** `origin/sub/AST-1970/AST-1976-jobs-nav` @ `bf9af69eeecf26fce4b5ecdff836c5813755201a`

### Canon scores
(none on ticket — Citations: frontend-only, outside `stat.logging.info.api` / `stat.logging.error` territory)

### Traceability
AC14→S1 `job_state` render, Job link + `JobAnalysisReportModal` + `stopPropagation` + `onRefresh={load}`; AC15→S1 `npm run build`/`lint` gate + `import src.utils.config`. Parent AC1–13 N/A (siblings); AC11–13 not this child's ticket slice.

### Findings

#### acceptable — AST-1974 on ref
- **Location:** `## Backend contract consumed` / Depends on
- **Finding:** `job_state` column and row field come from #1; this worktree file may pre-#1 until merge.
- **Recommendation:** build on a ref with AST-1974 merged; plan already states this.

#### acceptable — Plan step 2 doc-comment typo
- **Location:** Stage 1 step 2
- **Finding:** Example ends with `*/.` instead of `*/`.
- **Recommendation:** Fix when editing the interface comment; no plan revision required.

#### discuss — eslint baseline
- **Location:** Stage 1 step 7
- **Finding:** Plan correctly forbids fixing existing `react-hooks/set-state-in-effect` on `load()` effect.
- **Recommendation:** build-child documents baseline in handoff if lint output is questioned at qa-child.

context_tokens≈42000

## Radia review

[code-rubric]
**Ticket:** AST-1976
**Publish ref:** `3f70dc43e015e2fe887c1197e2b3ed85ba8efe17` (`origin/sub/AST-1970/AST-1976-jobs-nav`)
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Overall:** CLEAN

### Canon scores
(frozen list empty — ticket **§ Citations: none**; scope is `JobsMeteorites.tsx` only, outside `stat.logging.info.api` / `stat.logging.error` territory)

### Column diff vs plan stage
(aligned) — Joan: no directive rows; same on tip.

### Frame diff
(none)

### Findings

#### advisory — sibling stack + test carry
- **Location:** AST-1974/1975 backend + frontend + `tests/**` / `docs/test-bible/**` in `origin/dev...origin/sub/AST-1970/AST-1976-jobs-nav`
- **Finding:** Three-dot diff includes prior epic children on this sub; AST-1976 product commit `19badde6d` touches only `src/ui/frontend/src/pages/JobsMeteorites.tsx`. Betty test updates (e.g. `test_JobsMeteorites.test.tsx`) are expected merge-tests carry.

#### advisory — manual AC 14 smoke
- **Location:** Issue doc **## Review**
- **Finding:** No browser smoke; build notes confirm compile/import/grep gates. Component tests extended per build handoff.
- **Default:** Susan/parent UAT for modal stacking (job link vs row → meteorite modal) if not already covered in vitest.

#### advisory — eslint baseline on `load()` effect
- **Location:** `JobsMeteorites.tsx` (pre-existing `react-hooks/set-state-in-effect`)
- **Finding:** Unchanged line; build left unfixed per plan — not introduced by this diff.

### What's solid
- **Scope gate:** Single-file diff matches plan: `job_state` on row type; `render` for `job_state` (`—` when empty) and `astral_job_id` (link button, `stopPropagation`, no navigation).
- **AC 14 mechanics:** `JobAnalysisReportModal` with `jobId={reportJobId}`, `onClose` clears state, `onRefresh={load}` refreshes join-backed `job_state`; `MeteoriteDetailModal` + `onRowClick` unchanged.
- **Boundaries:** No `navigate` / `useNavigate` on page; no API or sibling Jobs page edits in 1976 commit.
- **Estimate:** Confirmed **2**; footprint is one focused UI change.

### Recommended actions
- Chuckles: append to `docs/features/interface/ast-1976-meteorites-landed-job-state-and-job-link.md`, commit `docs(AST-1976): Radia review — clean` on `sub/AST-1970/AST-1976-jobs-nav`, push, post slim upshot `--as radia`, **Review Posted** → PROCEED / **User Testing** (no `resolve-child`).

context_tokens≈9000

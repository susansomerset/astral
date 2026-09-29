# AST-1865 — Clickable job state history opens the run (Execution History for job modals)

- **Parent:** AST-1853 — Execution History for job modals
- **Ticket:** AST-1865
- **Publish ref:** `sub/AST-1853/AST-1865-clickable-job-state-history-opens-run` (origin only)
- **Canon Scope:** `astral.standards.dry-and-focused-functions`, `astral.ui.frontend-file-placement`
- **Depends on:** AST-1864 (merged to `origin/ftr/AST-1853-execution-history-for-job-modals`) — stamps `run_id` on job `state_history` entries.

Admins can click a Job Detail modal State History row to open that run: the same agent-prompt panes
Execution History's batch link opens (`BatchAgentDataPanes`) plus the same log table Execution
History shows when a run row is expanded. The log table moves out of `AdminPerformanceMonitor.tsx`
into one shared `BatchLogViewer` component (moved, not copied). A row resolves its run id from
`run_id` (AST-1864), falling back to `batch_id` for rows written before AST-1864 shipped; rows with
neither are not clickable. Non-admins, the Company modal, and Execution History behaviour are unchanged.
Frontend only — no API, schema, or `src/core/` change.

## Code facts this plan relies on (verified on this ref)

- `src/core/tracker.py` (AST-1864, commit `23d6145d`) — `_stamp_run_id` adds `entry["run_id"]` only when
  `log_batch_id` is set; key absent otherwise. `batch_id` key unchanged.
- `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` — private `interface LogEntry` (lines 29–36) and
  private `function LogViewer({ logs, loading, logLevelFilter })` (lines 435–504) own the only
  `dispatch-log-table` markup in `src/ui/frontend/src`. Rendered once at line 411:
  `<LogViewer logs={logs} loading={logsLoading} logLevelFilter={logLevelFilter} />`.
  `LogEntry` is also used by page state (`logs`, `logCache`, lines 101/103).
- `src/ui/frontend/src/components/BatchAgentDataModal.tsx` — exports `BatchAgentDataPanes({ batchId, candidateId?, className? })`,
  which fetches `/api/agent_data/<id>`, `/api/admin/timesheets?batch_id=<id>`, `/api/admin/dispatch_ledger/<id>`
  and self-resolves candidate id from the ledger row.
- `src/ui/frontend/src/components/Modal.tsx` — portals to `document.body`; supports `stacked` (overlay above
  another modal, CSS `.modal-overlay--stacked` exists in `App.css`) and `showFooter`.
  Precedent: `RubricModal`, `MaterialsPreviewModal` use `stacked`.
- `src/ui/frontend/src/contexts/AuthContext.tsx` — `useAuth()` is a plain `useContext`; the default context value
  has `isAdmin: false`, so components render safely without `AuthProvider` (existing tests do not wrap it).
- `src/ui/frontend/src/components/StateTimeline.tsx` — private `interface StateEntry { to_state?, state?, timestamp?, batch_id? }`;
  callers: `JobDetailModal.tsx:398` and `CompanyDetailModal.tsx:179`. Row styling is all inline; there is no
  global `.clickable` style for non-table rows (`App.css` `.clickable` is scoped to `.list-page-table tbody tr`).
- `src/ui/frontend/src/components/JobDetailModal.tsx` — `JobDetail.state_history?: Array<{ to_state?; timestamp? }>`;
  `StateTimeline` is rendered inside the private `InfoTab` subcomponent.
- `docs/canon-index.md` is not present on this ref; the two cited statutes were read directly at
  `canon/statutes/astral/standards/astral.standards.dry-and-focused-functions.md` and
  `canon/statutes/astral/ui/astral.ui.frontend-file-placement.md`.

## Scope gate

Every file below is named in this ticket's `## Scope`, and each change is the kind Scope describes
(new shared log viewer; page swaps to it; new run modal reusing `BatchAgentDataPanes`; timeline gains
run-id key + optional callback; job modal widens entry type, gates on `isAdmin`, holds selected run).
No `App.css`, API, `src/core/`, `src/data/`, or Company modal change. Tests and bible are Betty's.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/BatchLogViewer.tsx` | **New.** `LogViewer` + `LogEntry` moved here from the page; `logLevelFilter` optional | ui |
| `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` | Remove private `LogEntry` + `LogViewer`; import shared component/type | ui |
| `src/ui/frontend/src/components/BatchExecutionModal.tsx` | **New.** Stacked modal for one run id: `BatchAgentDataPanes` + `BatchLogViewer`, logs from `/api/admin/dispatch_ledger/<id>/logs` | ui |
| `src/ui/frontend/src/components/StateTimeline.tsx` | Export `StateEntry` (+ `run_id`); export `entryRunId`; optional `onSelectRun` prop; clickable rows | ui |
| `src/ui/frontend/src/components/JobDetailModal.tsx` | `state_history?: StateEntry[]`; `selectedRunId` state; pass `onSelectRun` only for admins; render `BatchExecutionModal` | ui |

## Stage 1: Shared log viewer (move, not copy)

**Done when:** `grep -rn "dispatch-log-table" src/ui/frontend/src --include=*.tsx` matches only
`components/BatchLogViewer.tsx`; `grep -n "function LogViewer" src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx`
returns nothing; Execution History renders, filters, and copies logs exactly as before.

1. Create `src/ui/frontend/src/components/BatchLogViewer.tsx` with:
   - Imports: `import { useMemo, useState } from "react"` and `import Time from "./Time"`.
   - `export interface LogEntry` — the exact six fields cut from the page (`id: number`, `level: string`,
     `logger_name: string`, `message: string`, `batch_id: string | null`, `created_at: string`).
   - `export default function BatchLogViewer({ logs, loading, logLevelFilter = "" }: { logs: LogEntry[]; loading: boolean; logLevelFilter?: string })`
     whose body is the page's `LogViewer` body **cut verbatim** (state `copied`, `visibleLogs` memo, the three
     early-return panels with their exact strings — `"Loading logs..."`, `"No log entries for this batch."`,
     `` `No '${logLevelFilter}' type log entries for this batch.` `` — `copyLogs`, toolbar with
     `title="Copy logs to clipboard"`, and the `dispatch-log-table` markup with level classes). No markup,
     class, or string changes.
   - One-line doc comment above the component: shared Execution History log table (AST-1865); used by
     `AdminPerformanceMonitor` and `BatchExecutionModal`.
2. In `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx`:
   - Delete `interface LogEntry { … }` (lines 29–36).
   - Delete the whole `function LogViewer(…) { … }` block (lines 435–504) and the blank lines before it,
     so the file ends after `PerformanceMonitor`'s closing brace.
   - Add `import BatchLogViewer, { type LogEntry } from "../components/BatchLogViewer"` directly after the
     `BatchAgentDataModal` import.
   - Replace `<LogViewer logs={logs} loading={logsLoading} logLevelFilter={logLevelFilter} />` with
     `<BatchLogViewer logs={logs} loading={logsLoading} logLevelFilter={logLevelFilter} />`.
   - Leave fetch (`toggleExpand`), `logCache`, `LOG_LEVELS`, and the Level filter select untouched.
   - If `useMemo` / `useState` are still used elsewhere in the page (they are: `useMemo` for filters/sort,
     `useState` for page state), keep the React import line unchanged.
3. Run `npm run lint` and `npx tsc -b` in `src/ui/frontend`; both clean.

⚠️ **Decision:** `LogEntry` moves with the viewer and is re-imported by the page as a type, rather than kept
in the page and duplicated in the component, or placed in `lib/`. One definition next to the only markup
that renders it satisfies `astral.standards.dry-and-focused-functions`; `lib/` is for shared non-component
modules and the ticket names no `lib/` file.

⚠️ **Decision:** `logLevelFilter` becomes optional with default `""` (show all levels). The job modal has no
level filter control; Scope says "an optional level filter".

## Stage 2: Run modal

**Done when:** `<BatchExecutionModal runId="R" onClose={…} />` renders a stacked wide modal titled `R`
containing the agent-data panes (fetching `/api/agent_data/R`) and the log table (fetching
`/api/admin/dispatch_ledger/R/logs`); `runId={null}` renders nothing and makes no requests.

1. Create `src/ui/frontend/src/components/BatchExecutionModal.tsx`:

   ```tsx
   import { useEffect, useState } from "react"
   import Modal from "./Modal"
   import { BatchAgentDataPanes } from "./BatchAgentDataModal"
   import BatchLogViewer, { type LogEntry } from "./BatchLogViewer"
   import api from "../lib/api"

   interface Props {
     runId: string | null
     onClose: () => void
   }

   /** One run's agent prompt panes + log table, as Execution History shows them (AST-1865). Stacks over the job modal. */
   export default function BatchExecutionModal({ runId, onClose }: Props) {
     const [logs, setLogs] = useState<LogEntry[]>([])
     const [loading, setLoading] = useState(false)

     useEffect(() => {
       if (!runId) return
       setLoading(true)
       setLogs([])
       api(`/api/admin/dispatch_ledger/${encodeURIComponent(runId)}/logs`)
         .then(r => r.json())
         .then(data => setLogs(Array.isArray(data) ? data : []))
         .catch(() => setLogs([]))
         .finally(() => setLoading(false))
     }, [runId])

     return (
       <Modal open={!!runId} onClose={onClose} title={runId ?? ""} size="wide" stacked showFooter={false}>
         {runId ? (
           <>
             <BatchAgentDataPanes batchId={runId} />
             <BatchLogViewer logs={logs} loading={loading} />
           </>
         ) : null}
       </Modal>
     )
   }
   ```

2. Run `npm run lint` and `npx tsc -b`; both clean.

⚠️ **Decision:** Separate stacked modal over the job modal (Scope: "Closing it returns to the job modal"),
not an inline expansion inside the timeline column — the panes need `size="wide"` room. Close is the header
`×`; `showFooter={false}` because there is nothing to save or cancel.

⚠️ **Decision:** No `candidateId` passed to `BatchAgentDataPanes`; it already resolves the candidate from the
ledger row it fetches. No log cache here (one run per open; the page's cache stays page-local and unchanged).

⚠️ **Decision:** Fetch fires only when `runId` is truthy, so the component can be mounted unconditionally
and still make zero admin requests while closed (AC5).

## Stage 3: Clickable timeline rows + job modal wiring

**Done when:** As admin, a job State History row with `run_id` (or, lacking it, `batch_id`) shows a pointer
cursor and opens `BatchExecutionModal` for that id on click / Enter / Space; closing it leaves the job modal
open. Rows with neither id, every row for non-admins, and every Company modal row render exactly as before
(no `role`, no `tabIndex`, no pointer, no handler) and no `/api/admin/` request is made.

1. In `src/ui/frontend/src/components/StateTimeline.tsx`:
   - Change `interface StateEntry` to `export interface StateEntry` and add `run_id?: string` after `batch_id`.
   - Add, above the component:

     ```tsx
     /** Run that produced this row: AST-1864 run_id, else legacy batch_id; "" when neither (not clickable). */
     export function entryRunId(entry: StateEntry): string {
       return entry.run_id || entry.batch_id || ""
     }
     ```

   - Add `onSelectRun?: (runId: string) => void` to `StateTimelineProps`; destructure it in the signature.
   - Inside the `sorted.map`, after `const state = …`, add `const runId = onSelectRun ? entryRunId(entry) : ""`.
   - On the row's outer `<div key={i} …>`, when `runId` is truthy only, spread these props (leave the element
     untouched otherwise):
     `role="button"`, `tabIndex={0}`, `title={\`Open run ${runId}\`}`,
     `onClick={() => onSelectRun!(runId)}`,
     `onKeyDown={e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onSelectRun!(runId) } }}`,
     and add `cursor: "pointer"` to its inline style. Implement as
     `const clickProps = runId ? { role: "button", tabIndex: 0, title: …, onClick: …, onKeyDown: … } : {}`
     spread onto the div, with `style={{ …existing, ...(runId ? { cursor: "pointer" } : {}) }}`.
2. In `src/ui/frontend/src/components/JobDetailModal.tsx`:
   - Change `import StateTimeline from "./StateTimeline"` to `import StateTimeline, { type StateEntry } from "./StateTimeline"`.
   - Add `import BatchExecutionModal from "./BatchExecutionModal"` and `import { useAuth } from "../contexts/AuthContext"`.
   - In `interface JobDetail`, change `state_history?: Array<{ to_state?: string; timestamp?: string }>` to
     `state_history?: StateEntry[]`.
   - In `JobDetailModal`, add `const { isAdmin } = useAuth()` and
     `const [selectedRunId, setSelectedRunId] = useState<string | null>(null)` after the existing `useState` block.
   - Change `useEffect(() => { setSnapshotCopied(false) }, [jobId])` to
     `useEffect(() => { setSnapshotCopied(false); setSelectedRunId(null) }, [jobId])`.
   - In `renderSideContent`'s `<InfoTab … />`, add prop `onSelectRun={isAdmin ? setSelectedRunId : undefined}`.
   - In `InfoTab`'s destructured params and prop type, add `onSelectRun?: (runId: string) => void`.
   - Change `<StateTimeline history={job.state_history || []} />` to
     `<StateTimeline history={job.state_history || []} onSelectRun={onSelectRun} />`.
   - Wrap the returned `<Modal …>…</Modal>` in a fragment and render, after `</Modal>`:
     `<BatchExecutionModal runId={selectedRunId} onClose={() => setSelectedRunId(null)} />`.
3. Leave `CompanyDetailModal.tsx` and the `Companies*` pages untouched (no `onSelectRun` → no clickable rows).
4. Run `npm run lint`, `npx tsc -b`, and `npx vitest run` for
   `tests/component/frontend/components/test_StateTimeline.test.tsx`, `test_JobDetailModal.test.tsx`,
   `test_CompanyDetailModal.test.tsx`, `test_BatchAgentDataModal.test.tsx`, and
   `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx` (existing tests; new AC4–AC6 coverage is Betty's).

⚠️ **Decision:** Admin gate lives in `JobDetailModal` (callback passed only when `isAdmin`); `StateTimeline`
stays auth-agnostic and becomes clickable only when a caller opts in and the row resolves a run id —
exactly Scope's rule, and it keeps the Company modal unchanged by construction.

⚠️ **Decision:** `BatchExecutionModal` renders as a sibling of the job `Modal` (fragment), not inside its
children. React synthetic events bubble through portals along the React tree; nesting it would route the run
modal's input/change events into the job modal's `onInput` dirty-detector and could trip the unsaved-changes
prompt on the job modal.

⚠️ **Decision:** Fallback is `run_id || batch_id` per Susan's forward-only decision on the parent (no timestamp
back-matching). Pre-AST-1864 chained rows therefore open their claim `batch_id`, which may show an empty run
view — accepted on the parent.

⚠️ **Decision:** Keyboard support (`role="button"`, `tabIndex`, Enter/Space) follows the existing
`CollapsiblePanel.tsx` pattern; pointer cursor is inline because `StateTimeline` is fully inline-styled and
`App.css` is out of scope.

## Acceptance criteria mapping

| AC | Covered by |
|----|------------|
| 4 Admin click opens the run | Stage 2 fetches + Stage 3 wiring |
| 5 Non-admin sees no link / no `/api/admin/` | Stage 3 (`onSelectRun` undefined) + Stage 2 (no fetch when `runId` null) |
| 6 Legacy `batch_id` fallback; neither → not clickable | Stage 3 `entryRunId` |
| 7 One log viewer | Stage 1 |
| 8 Execution History unchanged | Stage 1 (verbatim move, same strings/classes) |
| 9 Company modal unchanged | Stage 3 step 3 |
| 10 No API/schema change | Files Changed has no `src/ui/api/` or `src/data/` rows |

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

**Ticket:** AST-1865
**Overall:** APPROVED
**Corpus:** e1f2699fad
**Publish ref tip:** dff9ed63

## Canon scores
astral.standards.dry-and-focused-functions | A |
astral.ui.frontend-file-placement | A |

## Traceability
AC4→Stages 2–3; AC5→Stages 2–3 (`onSelectRun` gate + no fetch when `runId` null); AC6→Stage 3 `entryRunId`; AC7→Stage 1; AC8→Stage 1 (verbatim move); AC9→Stage 3 step 3; AC10→Files Changed (no `src/ui/api/` / `src/data/`).

### Findings

**acceptable** — Stage 1 “cut verbatim” move of `LogEntry` + `LogViewer` from `AdminPerformanceMonitor.tsx` (lines 29–36, 435–504) into `components/BatchLogViewer.tsx` is the right unit of DRY for AC7; page keeps fetch/cache/filter, shared component owns markup only.

**acceptable** — `BatchExecutionModal` log fetch duplicates the page’s `/logs` call pattern without sharing a helper; plan documents why (page `logCache` unchanged, one-shot open per run). Not the AC7 defect class (table markup duplication).

**discuss** — AC4–AC6 component tests are explicitly Betty (`qa-child`); build stages only run existing vitest files. Fine for workflow; Radia should expect new assertions in `test_JobDetailModal.test.tsx` / timeline tests on the landed branch.

**acceptable** — Admin gate in `JobDetailModal` (`onSelectRun` only when `isAdmin`), `StateTimeline` auth-agnostic, `CompanyDetailModal` untouched — matches Scope and parent AC9 by construction.

**acceptable** — `BatchExecutionModal` as fragment sibling of job `Modal` (not nested) addresses `Modal` body `onInput` dirty auto-detect vs stacked run view; `stacked` + `showFooter={false}` align with existing modal precedents.

**acceptable** — `run_id || batch_id` fallback and pre-AST-1864 chained rows possibly opening empty run views are called out per parent forward-only decision; in scope for this child.

context_tokens≈42000

## Review

- **Code commits on `origin/sub/AST-1853/AST-1865-clickable-job-state-history-opens-run`:** `7de3e0f4` (Stage 1), `52614323` (Stage 2), `d6022750` (Stage 3).
- **Diff:** 5 frontend files, as planned in Files Changed. `git diff origin/dev...HEAD -- src/ui/api/ src/data/` empty (AC10).
  AC7 greps: `dispatch-log-table` matches only `components/BatchLogViewer.tsx`; no `function LogViewer` in the page.
- **Deviations (both forced by `npm run lint`, which the plan's Done-when requires clean; no file, prop, endpoint, or behaviour change):**
  1. Stage 2 — the plan snippet's synchronous `setLoading(true)` / `setLogs([])` in the effect trips
     `react-hooks/set-state-in-effect`. `BatchExecutionModal` instead stores `{ runId, logs }` from the fetch callback
     and derives `loading = fetched?.runId !== runId`. Same zero-request-while-closed behaviour; a late response for a
     previous run can't render under the current one.
  2. Stage 3 — exporting `entryRunId` from `StateTimeline.tsx` trips `react-refresh/only-export-components`. Nothing
     imports it, so it is module-private. `StateEntry` stays exported (type export is allowed).
- **Compile / lint:** `npx tsc -b --noEmit` clean; `eslint` clean on all 5 files.
- **Existing tests (read-only run):** `test_AdminPerformanceMonitor` 23/23 pass unedited (AC8); `test_CompanyDetailModal`,
  `test_BatchAgentDataModal` pass. 3 failures, identical on the pre-Stage-3 tree (not caused by this change):
  `test_StateTimeline` ×2 and `test_JobDetailModal` "AST-1695 read-only: null listing_href → no Link <a>". The
  StateTimeline pair fail in `renderWithProviders` because the test's `lib/api` mock lacks `setAuthTokenGetter` /
  `setUnauthorizedHandler` (AuthProvider effect) — test harness, Betty's.
- **For Betty (qa-child):** AC4–AC6 coverage is new work in `test_JobDetailModal.test.tsx` / `test_StateTimeline.test.tsx`.
  Clickable rows carry `role="button"` and `title="Open run <id>"`; non-clickable rows carry neither.
- **Sub-log pre-check:** `validate-sub-log.sh --stage=build … ftr/AST-1853-execution-history-for-job-modals` → ok.

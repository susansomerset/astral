# In-place live updates on Scheduled Actions

**Linear:** [AST-1409](https://linear.app/astralcareermatch/issue/AST-1409)
**Parent:** [AST-1406](https://linear.app/astralcareermatch/issue/AST-1406) — Page refreshes and modals are closed (lost!)
**Publish ref:** `sub/AST-1406/AST-1409-in-place-live-updates-on-scheduled-actions`

Scheduled Actions AUTO, Dbg, Run/Stop, Avail, and last-run merge into the current view without an F5 and without a loading-gate remount. An open add/edit overlay keeps its draft if the list refreshes underneath. Lands proposed `pattern.ui.in-place-live-refresh` for Archie, using Performance Monitor’s silent `loadData(showSpinner = false)` as the shape, extracted into a shared hook so sibling **AST-1410** can consume it. Session-shell mount is sibling **AST-1408** (already on this worktree line) — do not retouch it. This ticket does not sweep other list pages, invent a websocket, or change dispatch / scheduler / task-run semantics.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/hooks/useInPlaceLiveRefresh.ts` | New shared hook — first-paint / query-change spinner; later refetch silent | ui |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | `loadData(showSpinner)` via the hook; post-mutation and running→idle refreshes silent; overlays stay outside the list loading gate | ui |
| `canon/patterns/ui/pattern.ui.in-place-live-refresh.md` | New catalog entry — `status: proposed`, `proposed_in: AST-1406` | docs / patterns |
| `canon/patterns/README.md` | List the new proposed id in Harvested corpus; bump proposed count | docs / patterns |
| `canon/patterns/HARVEST.md` | Crosswalk row for the new proposed pattern | docs / patterns |

**Out of this ticket (do not touch):** `AuthContext.tsx`, `RequireAuth.tsx`, `AdminRoute.tsx`, `sessionExtend.ts`, `LogOffScreen.tsx`, `vite.config.ts` (AST-1408). `AdminPerformanceMonitor.tsx` (already silent-refreshes inline; AST-1410 may route it through the hook). `AdminTaskPrompts.tsx`, `ListPage.tsx`, and other loading-gate surfaces (AST-1410). Flask admin routes, `dispatcher.py`, scheduler threads, poll interval integers (`5_000` on this page, `15_000` on Performance Monitor). AUTO/Dbg/Run/Stop button roles and labels (`pattern.ui.shared-button-roles`). `tests/**`, `docs/test-bible/**`.

## Stage 1: Shared `useInPlaceLiveRefresh` hook

**Done when:** `src/ui/frontend/src/hooks/useInPlaceLiveRefresh.ts` exists with the exact public contract below. No page imports it yet. Frontend `tsc -b --noEmit` and lint still pass.

1. Create `src/ui/frontend/src/hooks/useInPlaceLiveRefresh.ts` (same folder as `useSectionExpandPolicy.ts` / `useDirtyLeaveSaveThenNavigate.ts`).

2. File contents — exact:

```typescript
import { useCallback, useState } from "react"

export type InPlaceLiveRefresh = {
  /** True while a spinner-requested fetch is in flight (first paint / new query identity). */
  loading: boolean
  /**
   * Call at the start of a refetch.
   * `showSpinner: true` — first paint, or a new query identity (filters that change the request).
   * Omit / false — poll, post-mutation, session revalidation: merge into the current view.
   */
  beginRefresh: (showSpinner?: boolean) => void
  /** Call in the fetch `finally`. Always clears `loading`. */
  endRefresh: () => void
}

export function useInPlaceLiveRefresh(): InPlaceLiveRefresh {
  const [loading, setLoading] = useState(true)

  const beginRefresh = useCallback((showSpinner = false) => {
    if (showSpinner) setLoading(true)
  }, [])

  const endRefresh = useCallback(() => {
    setLoading(false)
  }, [])

  return { loading, beginRefresh, endRefresh }
}
```

3. Do **not** import this hook from any page in this stage. Do **not** add CSS, config keys, or a websocket. Do **not** move the `5_000` thread-status interval into config.
4. From `src/ui/frontend`, run `npx tsc -b --noEmit` and `npm run lint`. Fix only type/lint breaks caused by this new file.

⚠️ **Decision:** Thin hook (spinner flag + loading boolean), not an interval-owning fetcher. Scheduled Actions already has two refresh streams (dispatch-task list vs thread_status). Performance Monitor already owns its 15s interval. AST-1410 needs the same flag contract on pages with different cadences. Owning `setInterval` inside the hook would force every consumer to share one poll shape.

⚠️ **Decision:** Initial `loading === true` so first paint still shows the list placeholder before the first fetch’s `finally`. Callers pass `showSpinner: true` on first paint / query-identity change so a later query change can raise the spinner again after it has gone false (Performance Monitor filter keys). Silent calls never set `loading` back to true.

## Stage 2: Scheduled Actions consumes the hook

**Done when:** Toggling AUTO or Dbg updates that row’s on/off badge without replacing the page with `Loading…`. After a Run thread goes running→idle, Avail and last-run update in the same table without `Loading…`. The add/edit overlay and its `form` draft stay mounted across those refreshes and across the existing 5s thread-status poll. First visit still shows `Loading…` until the first `loadData` finishes. `tsc -b --noEmit` and lint pass.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, add to the existing `react` import is unnecessary (already has `useCallback` / `useState`). Add:

```typescript
import { useInPlaceLiveRefresh } from "../hooks/useInPlaceLiveRefresh"
```

Place it with the other `../hooks/` imports (after `useSectionExpandPolicy`).

2. Inside `ScheduledActions`, **remove**:

```typescript
  const [loading, setLoading] = useState(true)
```

Immediately after the toast / `clearToast` declarations (where `loading` used to live), add:

```typescript
  const { loading, beginRefresh, endRefresh } = useInPlaceLiveRefresh()
```

3. Replace the `loadData` callback so it takes the Performance Monitor flag and never calls `setLoading` directly. Keep the four GETs, toast-on-tasks-failure, and `setData` / catalog setters exactly as they are. Exact shape:

```typescript
  const loadData = useCallback(async (showSpinner = false) => {
    beginRefresh(showSpinner)
    try {
      const [tasksRes, keysRes, statesRes, floorsRes] = await Promise.all([
        api("/api/admin/dispatch_tasks"),
        api("/api/admin/dispatch_tasks/task_keys"),
        api("/api/admin/dispatch_tasks/state_options"),
        api("/api/admin/dispatch_tasks/score_floor_options"),
      ])
      if (tasksRes.ok) setData(await tasksRes.json())
      else setToast({ text: `Failed to load dispatch tasks (${tasksRes.status})`, variant: "error" })
      if (keysRes.ok) {
        const keys = await keysRes.json()
        setAllTaskKeys(typeof keys === "object" && !Array.isArray(keys) ? keys : {})
      }
      if (statesRes.ok) {
        const states = await statesRes.json()
        setStateOptions({
          job: Array.isArray(states?.job) ? states.job : [],
          company: Array.isArray(states?.company) ? states.company : [],
          candidate: Array.isArray(states?.candidate) ? states.candidate : [],
        })
      }
      if (floorsRes.ok) {
        const floors = await floorsRes.json()
        setScoreFloorOptions(Array.isArray(floors?.values) ? floors.values : [])
      }
    } finally {
      endRefresh()
    }
  }, [beginRefresh, endRefresh])
```

4. Change the mount effect from `useEffect(() => { loadData() }, [loadData])` to:

```typescript
  useEffect(() => { loadData(true) }, [loadData])
```

5. Leave these `loadData()` call sites with **no argument** (silent; default `showSpinner` is false):

- `toggleAutoMode` — the `loadData()` after a successful PUT (keep the `if (!res.ok) { … return }` path unchanged).
- `toggleDebug` — the `loadData()` after the PUT (keep the existing no-`res.ok` handling).
- `handleSave` — the `loadData()` after `setShowModal(false)` on success.
- The running→idle effect (`if (wasRunning && !running) loadData()`) — this is AST-443’s Avail refresh; it already omitted a spinner flag that `loadData` did not have. It must stay argument-less so completion does not remount the table.

6. Overlay / loading-gate placement (do not invert):

- Keep the add/edit modal (`showModal`) and Stop All modal (`showStopAll`) as **siblings after** the `{loading ? ( <div className="list-page-status">Loading…</div> ) : …}` ternary. Do **not** move either overlay inside the `loading` branch.
- `loadData` must **not** call `setShowModal`, `setForm`, `setEditRow`, `setShowStopAll`, or `setExpandedKeys`.
- Do **not** change AUTO/Dbg/Run/Stop classNames, labels, or `disabled` rules.
- Do **not** change `loadThreadStatus`, the `setInterval(loadThreadStatus, 5_000)` cadence, `handleRun` / `handleStop` / `handleKillAll` (`setTimeout(loadThreadStatus, 500)` stays).
- Do **not** add a second interval that polls `/api/admin/dispatch_tasks`. Avail / last-run already refresh on running→idle via the existing effect; AUTO/Dbg refresh on the existing post-PUT `loadData()`. Those calls become silent. Thread status already updates in place every 5s.

7. From `src/ui/frontend`, run `npx tsc -b --noEmit` and `npm run lint`. Fix only breaks caused by this file.

⚠️ **Decision:** Do not optimistic-patch the row from the PUT body. Silent refetch is the Performance Monitor shape; the badge updates when GET returns. Adding a parallel local merge would be a second source of truth for `auto_mode` / `debug`.

⚠️ **Decision:** Do not fold dispatch-task GET into the 5s thread-status interval. Child AC is toggle in-place, Avail/last-run after Run completes, and overlay survival — all satisfied by silencing the fetches that already run. A new 5s task poll would change request volume and is not in this child’s AC. Parent “same cadence” means those columns must update *in the same in-place way* thread status already does, not that they must share the timer.

⚠️ **Decision:** Do not edit `AdminPerformanceMonitor.tsx` on this ticket. It already implements the shape inline (`loadData(true)` on first/filter load, `loadData()` every 15s). Canonical_refs will point at it as the existing exemplar; AST-1410 may switch it to the hook. Editing it here would be a sibling-page sweep.

## Stage 3: Propose `pattern.ui.in-place-live-refresh`

**Done when:** The pattern file exists as `status: proposed` with SCHEMA-required frontmatter and body section order; README + HARVEST index the id; implementation does not treat the id as approved law (AUTHORING).

1. Create `canon/patterns/ui/pattern.ui.in-place-live-refresh.md` with **exactly** this content:

```markdown
---
id: pattern.ui.in-place-live-refresh
name: In-place live refresh
status: proposed
proposed_in: AST-1406
approved_by: null
approved_at: null
canonical_refs:
  - path: src/ui/frontend/src/hooks/useInPlaceLiveRefresh.ts
    symbol: useInPlaceLiveRefresh
  - path: src/ui/frontend/src/pages/AdminScheduledActions.tsx
    symbol: ScheduledActions
  - path: src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx
    symbol: loadData
related_statutes:
  - astral.standards.dry-and-focused-functions
  - astral.ui.frontend-file-placement
  - astral.ui.naming-conventions
  - astral.layers.ui-config-driven-business-logic
supersedes: null
superseded_by: null
---

# Problem

Authenticated list surfaces replace the working view with a loading placeholder on every refetch. Operator toggles and live columns then require an F5 or a full-page Loading remount. Background polls and post-mutation reloads unmount the list and can discard the sense of an open overlay even when draft state is still in memory.

# Solution shape

Shared hook `useInPlaceLiveRefresh` (pointer in `canonical_refs`):

- First paint, and a new query identity (filters that change the request), may set `loading` and show the list loading placeholder.
- Every later refetch — poll, post-mutation, session revalidation — calls `beginRefresh()` with `showSpinner` omitted or false, then writes the new payload into existing state. The page, section expand, scroll, and overlays stay mounted.
- Overlays own draft state independently of list rows. Refetch must not reset overlay open or draft fields.
- Do not invent a websocket. Do not change existing poll interval integers. Merge on the cadence the page already uses.
- Eligibility and task-run semantics stay on the authenticated admin API (`pattern.ui.admin-endpoint`). This pattern is presentation-only.
- Performance Monitor’s `loadData(showSpinner = false)` silent interval is the existing inline shape; Scheduled Actions is the first consumer of the shared hook. Remaining loading-gate surfaces consume the hook in AST-1410.

## When not to use

- First session or identity resolution — `RequireAuth` / `AdminRoute` / `AuthContext` (AST-1408). That is the session-shell half, not list refresh.
- Vite HMR, hard browser reload, or log-off — those may replace the tree.
- In-app dirty-leave (`pattern.ui.dirty-leave-save-then-navigate`) — route leave with Save, not overlay survival or list merge.
- Changing dispatch, scheduler, or task-run semantics to make the UI look live.
- Citing this pattern id as catalog law until `status: approved` (AUTHORING).

## Notes

Proposed in parent AST-1406 Architectural definition. Hook + Scheduled Actions land with AST-1409; remaining loading-gate surfaces are AST-1410. Archie approves the id separately; remediations may use the hook before approval without treating the catalog id as approved.
```

2. In `canon/patterns/README.md`, in the **Harvested corpus** intro sentence, change `two are \`status: proposed\`` to `three are \`status: proposed\``. In the Harvested corpus table, add one row after `pattern.ui.dirty-leave-save-then-navigate`:

```
| `pattern.ui.in-place-live-refresh` | proposed | `ui/pattern.ui.in-place-live-refresh.md` |
```

Do **not** add it to the Approved set section. Do **not** change the Exemplars table.

3. In `canon/patterns/HARVEST.md` Crosswalk table, append one row after the dirty-leave row:

```
| create (AST-1409) | `pattern.ui.in-place-live-refresh` | ui | `ui/pattern.ui.in-place-live-refresh.md` | AST-1406 | proposed — in-place list refresh; Archie approval pending |
```

Do **not** add a row to the AC → pattern cite map (id is not approved catalog law yet).

4. Do **not** set `status: approved` or invent `approved_by` / `approved_at`. Do **not** edit `pattern.ui.admin-endpoint.md`, `pattern.ui.shared-button-roles.md`, or `pattern.ui.dirty-leave-save-then-navigate.md`.

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order across the plan.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.** No fix-on-the-fly.
- Completes a stage on the epic worktree, commits, publishes to `origin/sub/AST-1406/AST-1409-in-place-live-updates-on-scheduled-actions`, then proceeds.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Traceability

- AC2 (AUTO/Dbg on/off in the same row without F5 or full-page loading replacement) → Stage 2 steps 3–5 (`loadData()` silent after PUT)
- AC3 (after Run completes, Avail and last-run update in place without F5) → Stage 2 step 5 (running→idle `loadData()` stays argument-less; no spinner)
- AC4 (background poll while overlay open does not close overlay or wipe draft) → Stage 2 step 6 (modals stay siblings of the list gate; `loadData` does not touch `form` / `showModal`; 5s poll still only `loadThreadStatus`)
- Pattern authoring (`pattern.ui.in-place-live-refresh` proposed) → Stage 3
- Boundaries → Files Changed exclusions; Stage 2 decisions (no extra task poll, no PM edit, no websocket, no dispatch semantics, no AST-1408 files)

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1409
**Overall:** APPROVED
**Publish ref:** `sub/AST-1406/AST-1409-in-place-live-updates-on-scheduled-actions` @ `d6bd96af`

## Traceability

- AC2 → Stage 2 steps 3–5 (silent `loadData()` after AUTO/Dbg PUT; mount-only `loadData(true)`)
- AC3 → Stage 2 step 5 (running→idle `loadData()` argument-less; Avail/last-run merge via existing dispatch_tasks GET)
- AC4 → Stage 2 step 6 (modals siblings outside loading gate; `loadData` does not touch `form`/`showModal`; 5s poll remains `loadThreadStatus` only)
- Pattern authoring → Stage 3 (`pattern.ui.in-place-live-refresh` proposed + README/HARVEST index)
- Boundaries → Files Changed exclusions; Stage 2 decisions (no PM edit, no extra task poll, no websocket, no AST-1408 session-shell files)

## Findings

### acceptable

- **Location:** Stage 1 — `src/ui/frontend/src/hooks/useInPlaceLiveRefresh.ts`
- **Finding:** `astral.ui.frontend-file-placement` statute text lists `lib/` for shared modules; corpus already places hooks under `hooks/` (`useDirtyLeaveSaveThenNavigate`, `useSectionExpandPolicy`).
- **Recommendation:** No plan change — matches established hook placement and dirty-leave pattern precedent.

### acceptable

- **Location:** Stage 2 — filter/query identity
- **Finding:** Scheduled Actions filters are client-side over fetched `data`; only mount calls `loadData(true)`, unlike Performance Monitor’s filter-driven `loadData(true)`.
- **Recommendation:** Correct for this page — hook contract still documents query-identity spinner for AST-1410/PM consumers.

No `fix-now` or `discuss` blockers. R1–R5 pass. Current `AdminScheduledActions.tsx` root cause confirmed: `loadData` always `setLoading(true)` (lines 332–360), causing list-gate flash on every post-PUT and running→idle refresh; modals are already structurally outside the gate (lines 788–863). Hook extraction mirrors Performance Monitor’s inline `loadData(showSpinner)` shape. Stage 3 pattern draft conforms to `canon/patterns/SCHEMA.md` (frontmatter, body order, `status: proposed`, README/HARVEST crosswalk steps match current corpus). In-scope-only exclusions, DRY, admin-endpoint presentation-only boundary, and shared-button-roles preservation all conform. Status `Plan Ready`, assignee Joan — gate satisfied. Zero completed `[plan-discuss]` rounds.

context_tokens≈58000

## Review (build)

**Built @ `cd6b32fe`** — `origin/sub/AST-1406/AST-1409-in-place-live-updates-on-scheduled-actions`

- Stage 1 (`b1d57f12`): `useInPlaceLiveRefresh` — first-paint spinner, later refetch silent
- Stage 2 (`a2ce31b2`): Scheduled Actions `loadData(showSpinner)`; AUTO/Dbg/run-complete silent; overlays stay outside the list gate
- Stage 3 (`cd6b32fe`): proposed `pattern.ui.in-place-live-refresh` + README/HARVEST index

## Radia review

# Radia review — AST-1409

**Ticket:** AST-1409  
**Parent:** AST-1406  
**Publish ref:** `sub/AST-1406/AST-1409-in-place-live-updates-on-scheduled-actions` @ `ff41b5e8`  
**Baseline:** `origin/dev`  
**Status gate:** Tests Passed (spawn prompt — trusted)  
**Overall:** DISCUSS

---

[code-rubric] revision=2  
**Rubric:** code-rubric.v2  
**Ticket:** AST-1409  
**Publish ref:** `ff41b5e8` (`origin/sub/AST-1406/AST-1409-in-place-live-updates-on-scheduled-actions`)

## Statutes checked

Diff change set (three-dot `origin/dev...origin/sub/AST-1406/AST-1409-…`): paths include `canon/patterns/**`, `docs/features/**`, `docs/test-bible/**`, `src/ui/frontend/src/hooks/useInPlaceLiveRefresh.ts`, `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, plus stacked AST-1408 session-shell files, AST-1409 tests, and **AST-1411** backend test paths (`tests/component/core/test_agent.py`, `tests/component/ui/api/test_api_admin.py`). Layers **ui**, **docs**; change_types **add**, **modify**.

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Tip `merge-tests(AST-1409)` pins test SHA `7e238fb8`. |
| `orch.git.commit-vocabulary` | universal | conforms | `docs` / `code` / `test` / `merge-tests` prefixes with ticket ids. |
| `orch.git.flow-direction-inviolable` | universal | conforms | Sub-branch epic flow; no reverse merges in reviewed commits. |
| `orch.git.ftr-sub-topology` | universal | conforms | Child `sub/AST-1406/AST-1409-…` topology correct. |
| `orch.git.merge-on-checkout` | universal | conforms | No dirty-merge artifacts visible in reviewed diff. |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | Linear history; no rebase/force signals. |
| `orch.git.no-dev-agent-branches` | universal | conforms | No dev-agent branch refs on publish path. |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | AST-1406 epic worktree; child scoped correctly. |
| `orch.git.three-permanent-branches` | universal | conforms | Work on sub publish ref, not main/dev conflation. |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | Plan decisions documented; no unresolved product forks in AST-1409 code. |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–3 match binding plan for AST-1409 product commits. |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Pipeline placement correct. |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Review at Tests Passed per gate. |
| `orch.roles.archie-approves-statutes` | universal | conforms | No statute corpus edits. |
| `orch.roles.betty-owns-test-tree` | universal | conforms | AST-1409 tests in `test(AST-1409)` + merge-tests; engineer `code()` commits exclude test tree. |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee Hedy; Radia read-only. |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Engineer `code()` commits: hook, Scheduled Actions, pattern catalog only. |
| `orch.roles.pre-commit-path-bans` | universal | conforms | No banned-path violations in engineer `code()` commits. |
| `astral.agent.confidence-bounds` | scoped | not-applicable | No agent grading paths in diff. |
| `astral.agent.do-task-delegation` | scoped | not-applicable | No `do_task` / dispatch delegation changes. |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | No grade-vector logic. |
| `astral.batch.batch-id-first` | scoped | not-applicable | No batch id paths. |
| `astral.batch.batch-id-format` | scoped | not-applicable | No batch id emission. |
| `astral.batch.claim-process-release` | scoped | not-applicable | No claim/release helpers. |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | No agent-responses writes. |
| `astral.config.config-source-of-truth` | scoped | not-applicable | No config module edits. |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | No secrets/env wiring. |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | No debug artifact paths. |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | No spike files. |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | `applies_when` paths not in diff. |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | No dispatcher/scheduler semantics changes. |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | AST-1409 feature doc present; no duplicate ticket files. |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty `test(AST-1409)` touches tests/bible only. |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | Engineer `code()` commits exclude `tests/` and `docs/test-bible/`. |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | No core/external layer paths. |
| `astral.layers.import-direction` | scoped | conforms | Hook/page imports stay in UI layer (React + local `lib/`). |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | No `scripts/**` changes. |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | No new hardcoded business-state strings; poll cadence unchanged. |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | No core coat-check paths. |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | No consult/render-verdict core paths. |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | conforms | Presentation-only; admin API routes untouched. |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | No seed JSON edits. |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | No catalog/seed conflicts. |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | No seed hot-path changes. |
| `astral.seed.define-approved` | scoped | not-applicable | No define/seed work. |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | No seed row mutations. |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | No coverage-join seed logic. |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | No data-layer changes. |
| `astral.standards.database-header-inventory` | scoped | not-applicable | No `src/data/**` changes. |
| `astral.standards.debug-contract-gated` | scoped | conforms | No new debug emission. |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Thin hook extraction; no duplicate fetch logic. |
| `astral.standards.in-scope-only` | scoped | conforms | AST-1409 engineer commits honor plan Files Changed; see discuss for publish-ref straggler. |
| `astral.standards.logging-via-utils` | scoped | conforms | No `print()` / new loggers. |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | Runtime symbols clean; ticket id in test descriptions only. |
| `astral.standards.no-cross-contamination` | scoped | conforms | AST-1409 product diff focused; publish-ref AST-1411 leak is branch hygiene (discuss). |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | No new hardcoded domain sets. |
| `astral.standards.public-then-helpers` | scoped | conforms | Hook exports public contract + type. |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | No `src/utils/**` changes. |
| `astral.state.core-decides-transitions` | scoped | not-applicable | No state-machine transitions. |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | No job state logic. |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | No run-chain paths. |
| `astral.ui.frontend-file-placement` | scoped | conforms | Hook under `hooks/`; page edit in `pages/` per precedent. |
| `astral.ui.naming-conventions` | scoped | conforms | `useInPlaceLiveRefresh`, `beginRefresh`/`endRefresh` follow local style. |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | No worker/process config touched. |

**Sweep count:** 65 active statutes scored (18 universal + 47 scoped).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.ui.in-place-live-refresh` | conforms | Authored as `status: proposed` per Stage 3 (not cited as approved law); hook + `ScheduledActions` `loadData(showSpinner)` match Solution shape; modals remain outside loading gate. |

## Plan adherence

AST-1409 engineer commits (`b1d57f12`, `a2ce31b2`, `cd6b32fe`) match Joan-approved Stages 1–3:

- **Stage 1:** `useInPlaceLiveRefresh.ts` matches plan verbatim — initial `loading: true`, `beginRefresh(showSpinner)` gates spinner, `endRefresh` clears.
- **Stage 2:** `AdminScheduledActions` swaps local `loading` for hook; `loadData(showSpinner)` uses `beginRefresh`/`endRefresh`; mount `loadData(true)`; silent `loadData()` on AUTO/Dbg/save/running→idle; modals remain siblings after loading ternary (lines 789–864); no new task poll; `5_000` thread poll unchanged.
- **Stage 3:** Pattern file `status: proposed`, README “three proposed”, HARVEST crosswalk row — all match plan.
- **Boundaries:** No `AdminPerformanceMonitor`, list-page sweep, dispatch/scheduler, or AST-1408 session-shell retouch in AST-1409 `code()` commits.
- **Estimate (5):** Footprint fits — hook + one page + pattern catalog + Betty tests.
- **Stacked AST-1408:** Present in three-dot diff vs `origin/dev` (sibling already on branch line) — expected epic stacking, not AST-1409 scope smuggling.

Betty manifest (`docs/test-bible/frontend/pages.md`, `hooks.md`) aligns with `AST-1409:*` component tests covering silent AUTO/Dbg toggle, running→idle Avail/last-run merge, and overlay draft survival.

## Findings

### fix-now

(none) — AST-1409 product implementation conforms to plan and pattern shape.

### discuss

- **Location:** Publish ref history — commit `0cf26ca1` (`test(AST-1411): seven-segment Ad Hoc preview/test coverage`)
- **Finding:** AST-1411 test-tree work is on the AST-1409 publish ref (`docs/test-bible/core/agent.md`, `docs/test-bible/ui/api/api_admin.md`, `tests/component/core/test_agent.py`, `tests/component/ui/api/test_api_admin.py`). AST-1409 plan explicitly excludes `tests/**` and backend routes; AST-1409 engineer commits did not author these files. Three-dot diff vs `origin/dev` therefore includes sibling-ticket coverage unrelated to Scheduled Actions live refresh.
- **Recommendation:** Chuckles / merge-child hygiene before ftr rollup — revert or rebase `0cf26ca1` off `sub/AST-1406/AST-1409-…`, or land AST-1411 on its own publish ref so AST-1409 rollup to `ftr/AST-1406` does not ship AST-1411 tests under AST-1409’s banner. Not an Ada `resolve-child` product fix.

### advisory

- **Location:** `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — `AST-1409` describe block
- **Finding:** Dbg toggle path asserts no `Loading…` during in-flight GET but does not separately gate AUTO the same way the first toggle does (both exercised in one test — adequate for manifest).
- **Recommendation:** None required; coverage matches Betty manifest pass criterion.

## What's solid

- Root cause fixed: `loadData` no longer always `setLoading(true)` — post-PUT and running→idle refreshes merge in place.
- Hook contract is intentionally thin (spinner flag only) — correct for pages with heterogeneous poll cadences (AST-1410 / Performance Monitor).
- Pattern catalog entry lands as **proposed** with AUTHORING-compliant frontmatter; implementation does not treat it as approved law.
- Component tests directly exercise AC2–AC4 behaviors (silent toggle, Avail/last-run merge, overlay draft survival).
- Engineer/test-tree separation clean for AST-1409-owned work.

## Frame diff

(none) — first Radia code-rubric pass on AST-1409. Prior issue-doc sections: plan @ `d6bd96af`, Joan APPROVED, build stub @ `cd6b32fe`; tip now `ff41b5e8` after `merge-tests(AST-1409)`. Publish ref also carries stacked AST-1408 + stray `0cf26ca1` (AST-1411) — see discuss.

## Notes

- Joan plan-rubric APPROVED attached; no Excluded-statute table — no C4 stragglers.
- §5f / §5g not triggered (UI-only; no backend debug or LLM external diffs in AST-1409 product commits).
- `blockedBy AST-1408` satisfied on branch line (1408 merged into stack).

context_tokens≈42000

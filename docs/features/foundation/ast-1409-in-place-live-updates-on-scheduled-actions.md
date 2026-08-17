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

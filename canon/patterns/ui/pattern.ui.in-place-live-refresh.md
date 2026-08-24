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

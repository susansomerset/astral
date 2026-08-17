# Apply silent refetch on remaining loading-gate surfaces

**Linear:** [AST-1410](https://linear.app/astralcareermatch/issue/AST-1410)
**Parent:** [AST-1406](https://linear.app/astralcareermatch/issue/AST-1406) — Page refreshes and modals are closed (lost!)
**Publish ref:** `sub/AST-1406/AST-1410-apply-silent-refetch-on-remaining-loading-gate-surfaces`

Authenticated list surfaces that still call `setLoading(true)` on every refetch (post-mutation, overlay-close refresh, poll) switch to `useInPlaceLiveRefresh` from sibling **AST-1409**. First paint and a new query identity (`selectedId` / filter keys that change the request) may still show the list placeholder. Later refetches merge into the current view so open overlays keep their drafts. Manage Tasks is the named overlay in the parent log. Operator Cancel/reset that currently calls `window.location.reload()` when there is no snapshot becomes a silent re-GET of last-saved content. This ticket does not invent a push channel, does not retouch Scheduled Actions except that it already consumes the hook, and does not change log-off or Vite HMR.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | `loadAll(showSpinner)` via the hook; post-save / revert silent; edit+preview modals stay outside the list gate | ui |
| `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` | `loadAll(showSpinner)` via the hook; post-save / add / delete / revert silent | ui |
| `src/ui/frontend/src/pages/AdminScheduledQueries.tsx` | `load(showSpinner)` via the hook; post-save / toggle / delete silent | ui |
| `src/ui/frontend/src/pages/AdminManageEmail.tsx` | `loadMessages(showSpinner)` via the hook; Land Meteorite refetch silent | ui |
| `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` | Replace inline `if (showSpinner) setLoading(true)` with the shared hook; keep 15s silent interval | ui |
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | `load(showSpinner)` via the hook; job-action and report `onRefresh` silent | ui |
| `src/ui/frontend/src/pages/JobsInReview.tsx` | `load(showSpinner)` via the hook; modal-close `load()` silent | ui |
| `src/ui/frontend/src/pages/JobsSkipped.tsx` | `load(showSpinner)` via the hook; job-action and modal-close `load()` silent | ui |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Cancel with no snapshot re-GETs last-saved tabs in place (no `window.location.reload`) | ui |
| `src/ui/frontend/src/pages/ArtifactsCompanySearchTerms.tsx` | Same Cancel in-place re-GET for search-terms text | ui |

**Out of this ticket (do not touch):**

- `AuthContext.tsx`, `RequireAuth.tsx`, `AdminRoute.tsx`, `sessionExtend.ts`, `LogOffScreen.tsx`, `vite.config.ts` (**AST-1408**).
- `AdminScheduledActions.tsx`, `useInPlaceLiveRefresh.ts` (already the shared shape; do not change the hook contract).
- `canon/patterns/**` (pattern stays `status: proposed`; **AST-1409** authored it; do not set `approved`).
- Company list pages (`CompaniesWatchList.tsx`, `CompaniesInactiveList.tsx`, `CompaniesIgnored.tsx`, `CompaniesNewList.tsx`, `CompaniesWatchHistory.tsx`) — `load()` already omits `setLoading(true)` on refetch.
- `AdminManageCandidates.tsx` — `loadAll` never sets loading.
- `AdminManageSlack.tsx` — Listen/Debug toggles patch local state; no post-first-paint list refetch.
- `AdminVectorFeedback.tsx`, `AdminAgentTimesheets.tsx` — refetch only on filter/query identity (spinner allowed by the pattern).
- `AdminCostReconciliation.tsx` — timesheet GET is a new file-upload query identity.
- `ListPage.tsx` — display gate only; callers stop passing `loading=true` on silent refetch.
- Detail/first-open loaders: `JobDetailModal.tsx`, `JobAnalysisReportModal.tsx`, `CompanyDetailModal.tsx`, `BatchAgentDataModal.tsx`, `ProfileTextPage.tsx`, `ContextTextPage.tsx`, `IntakePreamblePanel.tsx`, `IntakeTopicMenuPanel.tsx`, `CandidateSurferConsent.tsx`.
- Flask routes, dispatcher, scheduler, poll interval integers (`15_000` on Performance Monitor). `tests/**`, `docs/test-bible/**`.

## Stage 1: Manage Tasks consumes the hook

**Done when:** Saving or reverting a task refreshes the table without replacing the page with `Loading...`. Opening the edit overlay and leaving it open across that silent refetch keeps the overlay mounted and does not wipe `editSystem` / `editUser` / cache fields (post-save still closes the overlay as today). First visit and a candidate identity change still show `Loading...` until `loadAll` finishes. `tsc -b --noEmit` and lint pass.

1. In `src/ui/frontend/src/pages/AdminTaskPrompts.tsx`, add with the other `../hooks/` imports (after `useSectionExpandPolicy`):

```typescript
import { useInPlaceLiveRefresh } from "../hooks/useInPlaceLiveRefresh"
```

2. Remove:

```typescript
  const [loading, setLoading] = useState(true)
```

Immediately after the `clearToast` declaration, add:

```typescript
  const { loading, beginRefresh, endRefresh } = useInPlaceLiveRefresh()
```

3. Replace `loadAll` so it never calls `setLoading` directly. Keep the four GETs, `selectedId` query string, and setter/catch behavior exactly as they are. Exact shape:

```typescript
  const loadAll = useCallback((showSpinner = false) => {
    beginRefresh(showSpinner)
    const qs = selectedId ? `?candidate_id=${encodeURIComponent(selectedId)}` : ""
    Promise.all([
      api(`/api/admin/tasks${qs}`).then(r => r.json()),
      api("/api/admin/agents/ids").then(r => r.json()),
      api("/api/admin/tasks/meta/tokens").then(r => r.json()),
      api("/api/admin/tasks/meta/chain_tokens")
        .then(async r => (r.ok ? r.json() : []))
        .catch(() => []),
    ]).then(([taskData, agentData, tokData, chainData]) => {
      setTasks(Array.isArray(taskData) ? taskData : [])
      setAgentIds(Array.isArray(agentData) ? agentData : [])
      const merged = mergedAdminTokenAutocomplete(tokData, chainData)
      setTokenList(merged)
    }).catch(() => {
      setTasks([])
      setAgentIds([])
      setTokenList([])
    }).finally(() => endRefresh())
  }, [selectedId, beginRefresh, endRefresh])
```

4. Change the mount effect from `void loadAll()` to `void loadAll(true)`. Keep `queueMicrotask`. Exact:

```typescript
  useEffect(() => {
    queueMicrotask(() => {
      void loadAll(true)
    })
  }, [loadAll])
```

5. Leave these `loadAll()` call sites with **no argument** (silent):

- `handleSave` — the `loadAll()` after `setEditOpen(false)` / toast / `setRepoJsonRefresh` (keep closing the edit overlay on success).
- `RepoJsonDivergenceBanner` `onReverted={() => { setRepoJsonRefresh(n => n + 1); loadAll() }}`.

6. Overlay / loading-gate placement (do not invert):

- Keep the edit `Modal` and preview `Modal` as **siblings after** the `{loading ? ( <div className="list-page-status">Loading...</div> ) : …}` ternary.
- `loadAll` must **not** call `setEditOpen`, `setEditTask`, `setEditSystem`, `setEditUser`, `setEditCache`, `setEditCacheB`, `setEditCacheC`, `setEditCacheD`, `setEditNocache`, `setEditRunNext`, `setPreviewOpen`, or `setPreviewData`.
- Do **not** change `previewLoading` / `handlePreview`.
- Do **not** add an interval that polls `/api/admin/tasks`.

7. From `src/ui/frontend`, run `npx tsc -b --noEmit` and `npm run lint`. Fix only breaks caused by this file.

⚠️ **Decision:** `selectedId` change keeps `loadAll(true)` because `loadAll` is in the effect deps — that is a new query identity (`?candidate_id=`), not a silent poll. Post-save and revert are the after-first-paint refetches this child owns.

⚠️ **Decision:** Do not optimistic-patch the task row from the PUT body. Silent refetch is the Scheduled Actions / Performance Monitor shape.

## Stage 2: Remaining admin list refetch gates

**Done when:** Manage Agents post-save/add/delete/revert, Scheduled Queries save/toggle/delete, Manage Email Land Meteorite, and Performance Monitor’s 15s poll each update the current view without a list `Loading…` replacement. First paint (and Performance Monitor filter/query identity) still shows the placeholder. Add/edit overlays on Manage Agents stay mounted across a silent list refetch (post-save still closes as today). `tsc` and lint pass.

### 2a. Manage Agents — `src/ui/frontend/src/pages/AdminAgentPrompts.tsx`

1. Add `import { useInPlaceLiveRefresh } from "../hooks/useInPlaceLiveRefresh"` with the other imports.
2. Replace `const [loading, setLoading] = useState(true)` with `const { loading, beginRefresh, endRefresh } = useInPlaceLiveRefresh()` (keep it next to the agents/toast state).
3. Replace `loadAll`:

```typescript
  const loadAll = useCallback((showSpinner = false) => {
    beginRefresh(showSpinner)
    api("/api/admin/agents").then(r => r.json()).then(data => {
      setAgents(Array.isArray(data) ? data : [])
    }).catch(() => setAgents([]))
      .finally(() => endRefresh())
  }, [beginRefresh, endRefresh])
```

4. In the mount `useEffect`, change the `loadAll()` call to `loadAll(true)`. Leave the `brain_settings` GET in that same effect unchanged.
5. Leave argument-less `loadAll()` on: `handleEditSave` success, `handleAddSave` success, `handleDeleteConfirm` success, and `onReverted`.
6. Keep add/edit/delete/preview `Modal`s as siblings **after** `<ListPage … loading={loading} />`. `loadAll` must not touch `editOpen` / `editContent` / `addOpen` / `addContent`.
7. Do not change `LIST_COLUMNS`, brain-setting fields, or delete-disable rules.

### 2b. Scheduled Queries — `src/ui/frontend/src/pages/AdminScheduledQueries.tsx`

1. Add the hook import. Replace `const [loading, setLoading] = useState(true)` with the hook destructure after `clearToast` / `confirm`.
2. Replace `load`:

```typescript
  const load = useCallback(async (showSpinner = false) => {
    beginRefresh(showSpinner)
    try {
      const res = await api("/api/admin/scheduled_queries")
      const data = await res.json().catch(() => [])
      if (!res.ok) {
        throw new Error(
          (typeof data.error === "string" && data.error) || `HTTP ${res.status}`,
        )
      }
      setRows(Array.isArray(data) ? data : [])
    } catch (e) {
      setToast({ text: (e as Error).message, variant: "error" })
      setRows([])
    } finally {
      endRefresh()
    }
  }, [beginRefresh, endRefresh])
```

3. Change the mount effect to `void load(true)`.
4. Leave `await load()` (no argument) in `save`, `toggleActive`, and `remove` (and any other existing post-mutation `load()` in this file).
5. Keep the create/edit `<section>` (the `form` fields) **outside** the `{loading ? ( <p>Loading…</p> ) : …}` list section. `load` must not call `setForm` or `setEditingId`.

### 2c. Manage Email — `src/ui/frontend/src/pages/AdminManageEmail.tsx`

1. Add the hook import. Replace `const [loading, setLoading] = useState(true)` with the hook destructure.
2. Replace `loadMessages` so the first line is `beginRefresh(showSpinner)` instead of `setLoading(true)`, the signature is `async (showSpinner = false)`, `finally` calls `endRefresh()`, and the dependency array is `[beginRefresh, endRefresh]`. Keep the GET `/api/admin/inbox/messages` try/401-equivalent error/toast/`setMessages` body unchanged.
3. Change the mount effect to `void loadMessages(true)`.
4. Leave `await loadMessages()` (no argument) after a successful Land Meteorite (`onLandMeteorite`).
5. Do not change `bodyLoading` / `openMessage` (that is first paint of the selected message body). Do not change Land Meteorite POST semantics.

### 2d. Performance Monitor — `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx`

1. Add `import { useInPlaceLiveRefresh } from "../hooks/useInPlaceLiveRefresh"`.
2. Remove `const [loading, setLoading] = useState(true)`. Add `const { loading, beginRefresh, endRefresh } = useInPlaceLiveRefresh()` in that same place (keep `logsLoading` — that is `LogViewer` first-open, not this ticket).
3. Replace `loadData`:

```typescript
  const loadData = useCallback((showSpinner = false) => {
    beginRefresh(showSpinner)
    const qs = new URLSearchParams(filters).toString()
    api(`/api/admin/dispatch_ledger${qs ? `?${qs}` : ""}`)
      .then(r => r.json())
      .then(data => setRows(Array.isArray(data) ? data : []))
      .catch(() => setRows([]))
      .finally(() => endRefresh())
  }, [filters, beginRefresh, endRefresh])
```

4. Keep the existing effect exactly as:

```typescript
  useEffect(() => {
    loadData(true)
    const id = setInterval(() => loadData(), 15_000)
    return () => clearInterval(id)
  }, [loadData])
```

(`15_000` stays a literal. Do not move it to config.)

5. `loadData` must not call `setExpandedBatch`, `setLogs`, `setLogLevelFilter`, `setAgentDataBatchId`, or `setSearchParams`. Do not edit `LogViewer`. Keep `BatchAgentDataModal` as a sibling after the table ternary.

6. From `src/ui/frontend`, run `npx tsc -b --noEmit` and `npm run lint`. Fix only breaks caused by this stage’s files.

⚠️ **Decision:** Convert Performance Monitor to the hook rather than leave the inline `showSpinner` copy. AST-1409 deferred that on purpose so this child owns DRY consumption. Do not change the 15s cadence.

## Stage 3: Job list pages

**Done when:** Skip / row-action / Retry on Recommended and Skipped, and closing In Review / Skipped job-detail, refresh the table without `Loading...`. An open `JobAnalysisReportModal` / `JobDetailModal` / `CandidateActionNotesModal` stays mounted across those silent `load()` calls and does not wipe modal draft fields (those components own their own state). First visit and `selectedId` change still show `Loading...`. Section expand on In Review / Skipped is unchanged. `tsc` and lint pass.

Mechanical transform on **each** of `JobsRecommended.tsx`, `JobsInReview.tsx`, `JobsSkipped.tsx`:

1. Add `import { useInPlaceLiveRefresh } from "../hooks/useInPlaceLiveRefresh"`.
2. Remove `const [loading, setLoading] = useState(true)`. Add `const { loading, beginRefresh, endRefresh } = useInPlaceLiveRefresh()` in the same spot.
3. Change `load` from `setLoading(true)` / `finally(() => setLoading(false))` to `beginRefresh(showSpinner)` / `endRefresh()`, with signature `useCallback((showSpinner = false) => { … }, [selectedId, beginRefresh, endRefresh])`. Keep `if (!selectedId) return` as the first line inside `load`.
4. Change `useEffect(() => { load() }, [load])` to `useEffect(() => { load(true) }, [load])`.
5. Leave every other `load` call site argument-less: `useCandidateJobActions(load)`, `JobAnalysisReportModal onRefresh={load}`, `JobDetailModal onClose={() => { setViewingId(null); load() }}`, Retry handlers that already call `load()`.
6. Keep those modals as **siblings after** the `{loading ? … : loadState === "loading" ? … : …}` ternary. Do not move them inside the loading branch. Do not change the `loadState` branches (first State UI manifest resolution; AST-1408 already stops `authLoading` from flipping on JWT tick).
7. `JobsSkipped.tsx` only: keep `setSelected(new Set())` inside the successful `then` of `load` (selection reset after Retry / refresh stays).
8. Do not change `useCandidateJobActions`, row action buttons, rubric grouping, or `useSectionExpandPolicy`.

From `src/ui/frontend`, run `npx tsc -b --noEmit` and `npm run lint`. Fix only breaks caused by this stage’s files.

⚠️ **Decision:** `selectedId` change still spinners (`load(true)` via effect deps). Job actions and overlay `onRefresh` / `onClose` are the after-first-paint refetches. Do not add a jobs poll.

## Stage 4: Cancel/reset is in-place, not a browser reload

**Done when:** On an artifact editor page and on Company Search Terms, Cancel with a review snapshot still restores that snapshot (unchanged). Cancel with **no** snapshot re-GETs last-saved content into the current fields, clears dirty, and does **not** call `window.location.reload()`. The editor stays mounted (no `setLoaded(false)` on this path). Log-off still uses `LogOffScreen`’s reload. `tsc` and lint pass.

### 4a. `src/ui/frontend/src/components/ArtifactEditor.tsx`

1. Extract the job-load `.then` body (today’s block that reads `job.job_data?.artifacts`, calls `mapFixedFieldsFromRaw` or `mapJobDictArtifactFromRaw`) into:

```typescript
  function applyJobArtifactResponse(job: { job_data?: { artifacts?: Record<string, unknown> } }) {
    const persistKey = jobPersistence!.artifactKey
    const artifacts = (job.job_data?.artifacts ?? {}) as Record<string, unknown>
    const raw = artifacts[persistKey]
    if (fixedFields) mapFixedFieldsFromRaw(raw)
    else mapJobDictArtifactFromRaw(raw)
  }
```

Place it immediately after `mapJobDictArtifactFromRaw`.

2. Extract the candidate-load `.then` body (today’s block from `const artifacts = (c.candidate_data?.artifacts ?? {})` through `setHasChainData(...)`, **not** including `setLoaded` / `setDirty`) into `applyCandidateArtifactResponse(c)` with the same mapping, empty-criteria fallback (`v_0` / `New Criterion`), and `setHasChainData` logic. Place it immediately after `applyJobArtifactResponse`.

3. Rewrite the job-persistence `useEffect` so after the existing early returns and `setLoaded(false)` / `setSnapshot(null)` / `setJobLoadError(false)` it does:

```typescript
    api(`/api/jobs/${encodeURIComponent(jobPersistence.jobId)}`).then(r => r.json()).then(job => {
      applyJobArtifactResponse(job)
      setLoaded(true)
      setDirty(false)
    }).catch(() => setJobLoadError(true))
```

Keep the same dependency array. Do not add `applyJobArtifactResponse` to that array (it is an in-component function; leave the existing deps).

4. Rewrite the candidate `useEffect` so after the existing early returns, `setLoaded(false)`, `didSeedCriteriaExpandRef.current = ""`, and `setSnapshot(null)` it does:

```typescript
    api(`/api/candidates/${selectedId}`).then(r => r.json()).then(c => {
      applyCandidateArtifactResponse(c)
      setLoaded(true)
      setDirty(false)
    })
```

Keep the same dependency array.

5. Replace `handleCancel`:

```typescript
  function handleCancel() {
    if (snapshot) {
      setTabs(snapshot)
      setSnapshot(null)
      setDirty(false)
      return
    }
    if (jobPersistence) {
      if ((shapesKey || structureMode) && !fixedFields) return
      api(`/api/jobs/${encodeURIComponent(jobPersistence.jobId)}`).then(r => r.json()).then(job => {
        applyJobArtifactResponse(job)
        setDirty(false)
      }).catch(() => setJobLoadError(true))
      return
    }
    if (!selectedId || ((shapesKey || structureMode) && !fixedFields)) return
    api(`/api/candidates/${selectedId}`).then(r => r.json()).then(c => {
      applyCandidateArtifactResponse(c)
      setDirty(false)
    })
  }
```

6. Delete `window.location.reload()` from this file. Do **not** call `setLoaded(false)` on the no-snapshot path. Do **not** edit `LogOffScreen.tsx`. Do **not** change Generate / snapshot-on-generate / autosave.

### 4b. `src/ui/frontend/src/pages/ArtifactsCompanySearchTerms.tsx`

1. Extract the candidate `.then` body (from `const raw = c.company_search_terms` through `setEverSaved(...)`) into `applySearchTermsResponse(c)` immediately above the `selectedId` `useEffect`. Keep `setText` / `setHasChainData` / `setLoaded(true)` / `setDirty(false)` / `setEverSaved` inside that helper so the effect can call it as today.

2. The `selectedId` effect keeps `setLoaded(false)` and `setSnapshot(null)` then `api(...).then(r => r.json()).then(applySearchTermsResponse)`.

3. Replace `handleCancel`:

```typescript
  function handleCancel() {
    if (snapshot !== null) {
      setText(snapshot)
      setSnapshot(null)
      setDirty(false)
      return
    }
    if (!selectedId) return
    api(`/api/candidates/${selectedId}`).then(r => r.json()).then(c => {
      applySearchTermsResponse(c)
    })
  }
```

`applySearchTermsResponse` already `setDirty(false)` / `setLoaded(true)`. Do not `setLoaded(false)` on this Cancel path.

4. Delete `window.location.reload()` from this file. Do not change `TASK_KEY`, generate, or autosave.

5. From `src/ui/frontend`, run `npx tsc -b --noEmit` and `npm run lint`. Fix only breaks caused by this stage’s files.

⚠️ **Decision:** No-snapshot Cancel is a silent re-GET of last-saved server content, not a local undo stack and not a full document reload. Snapshot Cancel stays the review-mode restore. Intentional overlay close / route leave / log-off still discard drafts (parent boundary).

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order across the plan.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.** No fix-on-the-fly.
- Completes a stage on the epic worktree, commits, publishes to `origin/sub/AST-1406/AST-1410-apply-silent-refetch-on-remaining-loading-gate-surfaces`, then proceeds.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Traceability

- AC4 (background poll while overlay open does not close overlay or wipe draft) → Stage 2d (PM 15s `loadData()` silent; `BatchAgentDataModal` stays a sibling) + Stages 1–3 (modals stay outside loading gates; silent `load*` does not reset overlay draft state)
- AC5 (Manage Tasks and other authenticated list surfaces that replace themselves on refetch after first paint) → Stage 1 (Manage Tasks) + Stage 2 (Agents, Scheduled Queries, Email, PM hook) + Stage 3 (job lists)
- AC6 (log-off still clears; Vite still reloads on frontend source change) → `LogOffScreen.tsx` / `vite.config.ts` explicitly out of scope; Stage 4 deletes only the artifact Cancel reloads
- Cancel/reset in-place (child description) → Stage 4
- Boundaries → Files Changed exclusions; no websocket; no Scheduled Actions retouch; no extra polls; no `AUTH_CONFIG` / session-shell edits

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1410
**Overall:** APPROVED
**Publish ref:** `sub/AST-1406/AST-1410-apply-silent-refetch-on-remaining-loading-gate-surfaces` @ `49c4a4e2`

## Traceability

- AC4 → Stage 2d (PM 15s `loadData()` silent; `BatchAgentDataModal` sibling after table gate) + Stages 1–3 (modals outside loading ternaries; silent `load*` does not reset overlay draft fields)
- AC5 → Stage 1 (Manage Tasks) + Stage 2 (Agents, Scheduled Queries, Email, PM hook) + Stage 3 (Recommended / In Review / Skipped)
- AC6 → `LogOffScreen.tsx` / `vite.config.ts` out of scope; Stage 4 removes only artifact Cancel `window.location.reload()` paths
- Cancel/reset in-place (child description) → Stage 4 (`ArtifactEditor.tsx`, `ArtifactsCompanySearchTerms.tsx`)
- Boundaries → Files Changed exclusions; no websocket; no Scheduled Actions / hook-contract / canon edits; excluded surfaces documented with rationale

## Findings

### acceptable

- **Location:** Out of scope — `AdminVectorFeedback.tsx`, `AdminAgentTimesheets.tsx`
- **Finding:** Both still `setLoading(true)` on every `filters` / `searchParams` change (query-identity refetch, not post-mutation poll).
- **Recommendation:** Correct exclusion — `pattern.ui.in-place-live-refresh` allows spinners on new query identity; converting these would be wrong for filter changes.

### acceptable

- **Location:** Stage 3 — `load` early return when `!selectedId`
- **Finding:** `if (!selectedId) return` before `beginRefresh` can leave `loading === true` until a candidate is selected (same pre-existing behavior as today’s early return before `setLoading(false)`).
- **Recommendation:** No plan change — not introduced by this ticket; candidate arrival retriggers `load(true)`.

No `fix-now` or `discuss` blockers. R1–R5 pass. `useInPlaceLiveRefresh` exists on the worktree line (AST-1409); plan correctly consumes it without contract edits. Root causes confirmed on named surfaces (`AdminTaskPrompts` `loadAll` always `setLoading(true)`; job pages same; `ArtifactEditor` / `ArtifactsCompanySearchTerms` Cancel calls `window.location.reload()`). Manage Tasks modal placement verified as siblings after the loading ternary (lines 393–447 vs 449+). Company list exclusions accurate (`CompaniesWatchList` `load()` never re-asserts loading on refetch). Stage 4 extractions match current `ArtifactEditor` job/candidate effect bodies and preserve snapshot-vs-re-GET Cancel semantics. In-scope-only table, DRY hook sweep, and presentation-only boundary conform. Status `Plan Ready`, assignee Joan — gate satisfied. Zero completed `[plan-discuss]` rounds.

context_tokens≈72000

## Review (build)

**Built @ `4b676d7d`** — `origin/sub/AST-1406/AST-1410-apply-silent-refetch-on-remaining-loading-gate-surfaces`

- Stage 1 (`f924addf`): Manage Tasks `loadAll(showSpinner)`; post-save/revert silent; overlays stay outside the list gate
- Stage 2 (`65bbd263`): Agents, Scheduled Queries, Email silent post-mutation refetch; Performance Monitor on the shared hook
- Stage 3 (`990f0ce2`): Recommended / In Review / Skipped `load(showSpinner)`; job-action and modal-close silent
- Stage 4 (`4b676d7d`): Artifact Cancel with no snapshot re-GETs last-saved content; no `window.location.reload`

## Radia review

# Radia review — AST-1410

**Ticket:** AST-1410  
**Parent:** AST-1406  
**Publish ref:** `sub/AST-1406/AST-1410-apply-silent-refetch-on-remaining-loading-gate-surfaces` @ `1e6970bc`  
**Baseline:** `origin/dev`  
**Status gate:** Tests Passed (spawn prompt — trusted)  
**Overall:** DISCUSS

---

[code-rubric] revision=2  
**Rubric:** code-rubric.v2  
**Ticket:** AST-1410  
**Publish ref:** `1e6970bc` (`origin/sub/AST-1406/AST-1410-apply-silent-refetch-on-remaining-loading-gate-surfaces`)

## Statutes checked

Diff change set (three-dot `origin/dev...origin/sub/AST-1406/AST-1410-…`): stacked epic children (AST-1408 session shell, AST-1409 hook/pattern/Scheduled Actions, **AST-1410** silent-refetch sweep, plus sibling AST-1411–1417 backend/Ad Hoc work on publish-ref tip). Layers **ui**, **core**, **data**, **docs**; change_types **add**, **modify**, **delete** (AST-1411 test revert).

AST-1410 engineer `code()` commits (`f924addf`, `65bbd263`, `990f0ce2`, `4b676d7d`) touch only the ten planned UI files. Statute scoring below uses the full publish-ref diff; product findings scoped to AST-1410 commits unless noted.

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | `merge-tests(AST-1410)` pins test SHA `9641ae74`. |
| `orch.git.commit-vocabulary` | universal | conforms | `code`/`test`/`docs`/`merge-*` prefixes with ticket ids. |
| `orch.git.flow-direction-inviolable` | universal | conforms | Sub-branch epic flow. |
| `orch.git.ftr-sub-topology` | universal | conforms | Child `sub/AST-1406/AST-1410-…` topology correct. |
| `orch.git.merge-on-checkout` | universal | conforms | No dirty-merge artifacts in AST-1410 product files. |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | Linear history. |
| `orch.git.no-dev-agent-branches` | universal | conforms | No dev-agent branch refs. |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | AST-1406 epic worktree. |
| `orch.git.three-permanent-branches` | universal | conforms | Work on sub publish ref. |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | Plan decisions documented for AST-1410 scope. |
| `orch.pipeline.plan-is-bible` | universal | conforms | AST-1410 `code()` commits match Stages 1–4 plan. |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Pipeline placement correct. |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Review at Tests Passed. |
| `orch.roles.archie-approves-statutes` | universal | conforms | No statute corpus edits in AST-1410 commits. |
| `orch.roles.betty-owns-test-tree` | universal | conforms | `test(AST-1410)` + merge-tests; engineer `code()` excludes test tree. |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee Katherine; Radia read-only. |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Engineer commits limited to plan Files Changed. |
| `orch.roles.pre-commit-path-bans` | universal | conforms | No banned-path violations in AST-1410 `code()` commits. |
| `astral.agent.confidence-bounds` | scoped | not-applicable | No agent grading changes in AST-1410 product commits. |
| `astral.agent.do-task-delegation` | scoped | not-applicable | No dispatch delegation edits in AST-1410 scope. |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | No grade-vector logic in AST-1410 scope. |
| `astral.batch.batch-id-first` | scoped | not-applicable | No batch paths in AST-1410 product commits. |
| `astral.batch.batch-id-format` | scoped | not-applicable | No batch id emission in AST-1410 scope. |
| `astral.batch.claim-process-release` | scoped | not-applicable | No claim/release helpers in AST-1410 scope. |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | No agent-responses writes in AST-1410 scope. |
| `astral.config.config-source-of-truth` | scoped | not-applicable | No config edits in AST-1410 `code()` commits. |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | No secrets/env wiring in AST-1410 scope. |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | No debug artifact paths. |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | No spike files. |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | `applies_when` paths not in AST-1410 product commits. |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | No dispatcher chain edits in AST-1410 scope. |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | AST-1410 feature doc present. |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty `test(AST-1410)` touches tests/bible only. |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | All four AST-1410 `code()` commits are `src/ui/**` only. |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | No core/external edits in AST-1410 product commits. |
| `astral.layers.import-direction` | scoped | conforms | Page/hook imports stay in UI layer. |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | No `scripts/**` in AST-1410 commits. |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | No new hardcoded state strings; poll cadences unchanged (`15_000` literal preserved). |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | No core coat-check paths in AST-1410 scope. |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | No consult/render-verdict paths in AST-1410 scope. |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | conforms | Presentation-only; no backend route changes in AST-1410 commits. |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | No seed JSON edits in AST-1410 scope. |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | No catalog/seed conflicts in AST-1410 scope. |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | No seed hot-path changes in AST-1410 scope. |
| `astral.seed.define-approved` | scoped | not-applicable | No define/seed work in AST-1410 scope. |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | No seed row mutations in AST-1410 scope. |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | No coverage-join seed logic in AST-1410 scope. |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | No data-layer changes in AST-1410 product commits. |
| `astral.standards.database-header-inventory` | scoped | not-applicable | No `src/data/**` in AST-1410 product commits. |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | No debug emission changes in AST-1410 product commits. |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Shared hook consumed; mechanical `beginRefresh`/`endRefresh` sweep; Stage 4 extractions reduce duplication. |
| `astral.standards.in-scope-only` | scoped | conforms | AST-1410 engineer commits honor plan table; publish-ref sibling leak is branch hygiene (discuss). |
| `astral.standards.logging-via-utils` | scoped | conforms | No `print()` / new loggers in AST-1410 commits. |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | Runtime symbols clean; ticket id in test descriptions only. |
| `astral.standards.no-cross-contamination` | scoped | conforms | AST-1410 product diff focused; publish-ref carries sibling tickets (discuss). |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | No new hardcoded domain sets. |
| `astral.standards.public-then-helpers` | scoped | conforms | Stage 4 helpers placed after mapping functions per plan. |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | No `src/utils/**` in AST-1410 commits. |
| `astral.state.core-decides-transitions` | scoped | not-applicable | No state-machine transitions in AST-1410 scope. |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | No job state logic in AST-1410 scope. |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | No run-chain paths in AST-1410 scope. |
| `astral.ui.frontend-file-placement` | scoped | conforms | Edits in existing `pages/` and `components/` paths. |
| `astral.ui.naming-conventions` | scoped | conforms | `applyJobArtifactResponse`, `loadAll(showSpinner)` follow local style. |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | No worker/process config touched. |

**Sweep count:** 65 active statutes scored (18 universal + 47 scoped).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.ui.in-place-live-refresh` | conforms | Consumes AST-1409 hook on all named surfaces; `status: proposed` — plan correctly does not treat as approved catalog law; Performance Monitor converted to shared hook per Stage 2d decision. |

## Plan adherence

AST-1410 engineer commits match Joan-approved Stages 1–4:

- **Stage 1 (`AdminTaskPrompts.tsx`):** `useInPlaceLiveRefresh`; `loadAll(showSpinner)` with `beginRefresh`/`endRefresh`; mount `loadAll(true)` via `queueMicrotask`; silent `loadAll()` on save/revert; modals remain siblings after loading gate.
- **Stage 2:** Agents, Scheduled Queries, Manage Email, Performance Monitor — same mechanical hook swap; PM keeps `setInterval(() => loadData(), 15_000)` with silent interval ticks.
- **Stage 3:** `JobsRecommended`, `JobsInReview`, `JobsSkipped` — `load(showSpinner)` hook pattern; mount `load(true)`; argument-less `load()` on job actions and modal close.
- **Stage 4:** `ArtifactEditor` / `ArtifactsCompanySearchTerms` — `apply*Response` extractions; no-snapshot Cancel re-GETs server content; `window.location.reload()` removed from both files; snapshot Cancel path unchanged.
- **Boundaries:** No `useInPlaceLiveRefresh.ts`, `AdminScheduledActions.tsx`, `canon/patterns/**`, session-shell, or poll-cadence edits in AST-1410 `code()` commits.
- **Estimate (5):** Footprint matches — ten UI files + Betty component/page tests.

Betty `test(AST-1410)` (`9641ae74`) covers silent refetch on named pages and artifact Cancel without reload; manifest entries in `docs/test-bible/frontend/pages.md` align.

## Findings

### fix-now

(none) — AST-1410 product implementation conforms to plan and `pattern.ui.in-place-live-refresh` Solution shape.

### discuss

- **Location:** Publish ref tip — commits after `4b676d7d` (`34020e29`, `b4ffa3a6`, `1e6970bc`) and intervening sibling history on the same branch
- **Finding:** `merge-resume(AST-1410)` (`34020e29`) lands extensive **non–AST-1410** product and test work: `src/core/agent.py`, `src/data/database.py`, `src/ui/api/api_admin.py`, `AdminAnthropicAdHoc.tsx`, `BatchAgentDataModal.tsx`, `src/utils/config.py`, plus AST-1411/1412/1413/1416/1417 feature docs and `test_AdminAnthropicAdHoc` / `test_api_admin` / `test_candidates` expansions. AST-1410 plan explicitly excludes Flask routes, dispatcher, and `tests/**`. `merge-tests(AST-1410)` further absorbs sibling test-tree commits beyond Betty's clean `test(AST-1410)` (`9641ae74`).
- **Recommendation:** Chuckles / merge-child hygiene before ftr rollup — AST-1410 publish ref should not ship sibling AST-1411–1417 product under AST-1410's banner. Options: rebase/split publish ref so `sub/AST-1406/AST-1410-…` tip contains only stacked 1408+1409+1410 (and their tests), or document intentional epic-stack rollup and accept combined UAT scope. Not a Katherine `resolve-child` product fix.

### advisory

- **Location:** `src/ui/frontend/src/components/ArtifactEditor.tsx` — `handleCancel` candidate re-GET path (lines 902–905)
- **Finding:** No `.catch()` on the candidate Cancel re-GET (job path has `.catch(() => setJobLoadError(true))`). Plan shape matches — pre-existing asymmetry.
- **Recommendation:** Optional hardening in a follow-up if UAT surfaces silent failure on Cancel; not blocking.

- **Location:** Job list pages — `load` early return when `!selectedId`
- **Finding:** Joan already accepted — `loading` may stay true until candidate selected; not introduced by this ticket.
- **Recommendation:** None required.

## What's solid

- Mechanical hook sweep is consistent across all nine list surfaces named in the plan; Performance Monitor DRY'd onto the shared hook without cadence change.
- Stage 4 Cancel semantics correct: snapshot restore unchanged; no-snapshot path re-GETs last-saved server content and stays mounted (no `setLoaded(false)` on Cancel).
- Engineer/test-tree separation clean: four `code(AST-1410)` commits touch only planned UI files; Betty owns `test(AST-1410)` manifest.
- `LogOffScreen.tsx` still owns intentional `window.location.reload()` — AC6 boundary preserved.
- Excluded surfaces (`AdminVectorFeedback`, company lists, detail modals) correctly left untouched.

## Frame diff

(none) — first Radia code-rubric pass on AST-1410. Prior issue-doc sections: plan @ `49c4a4e2`, Joan APPROVED, build stub @ `4b676d7d`; tip now `1e6970bc` after `merge-tests` + `merge-resume` + sync. Publish ref carries stacked siblings beyond AST-1410 — see discuss.

## Notes

- Joan plan-rubric APPROVED attached; no Excluded-statute table — no C4 stragglers.
- AST-1411 test leak from AST-1409 was reverted (`cb045a88`) before AST-1410 plan landed; sibling product commits re-entered later on this branch line.
- §5f / §5g not triggered for AST-1410 product commits (UI-only).

context_tokens≈48000

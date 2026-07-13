# AST-876 — Manage Candidates dispatch-task count and Set button (Add “set dispatch tasks” button)

**Linear:** [AST-876](https://linear.app/astralcareermatch/issue/AST-876/manage-candidates-dispatch-task-count-and-set-button-add-set-dispatch)
**Parent:** [AST-873](https://linear.app/astralcareermatch/issue/AST-873/add-set-dispatch-tasks-button)
**Publish ref:** `origin/sub/AST-873/AST-876-manage-candidates-set-dispatch-tasks`

On the Manage Candidates list, show each candidate’s dispatch-task row count and a **Set dispatch tasks** control that calls the sibling admin set API so an operator can materialize the config template candidate’s full schedule onto the chosen candidate, then refresh the count. Does not implement upsert/prune or template config (AST-875). Does not redesign Scheduled Actions. Does not start dispatcher runs.

**Blocked by:** [AST-875](https://linear.app/astralcareermatch/issue/AST-875/template-candidate-config-and-dispatch-task-set-upsert-add-set) (Linear `blocks`) until `GET /api/admin/dispatch_tasks/counts` and `POST /api/admin/dispatch_tasks/set_from_template` exist on the integration line the epic worktree merges (`origin/ftr/AST-873-set-dispatch-tasks-button` after `merge-child`, or otherwise available for build). Plan contracts below match AST-875’s published plan; do not invent alternate paths or hardcode `somerset` in the UI.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `dispatch_task_count` column to `DATA_SHAPES["candidates"]["list"]["manage"]` | utils |
| `src/ui/frontend/src/pages/AdminManageCandidates.tsx` | Load counts; merge onto rows; render count column; Set button + confirm + POST set_from_template; refresh counts | ui |

**Out of scope:** `database.py` / dispatcher set-from-template / admin route registration (AST-875); Scheduled Actions page edits; Betty tests / test-bible (qa-child); hardcoding template candidate id in React.

---

## Stage 1: Shape column for dispatch-task count

**Done when:** `/api/shapes/candidates` → `list.manage` includes a `dispatch_task_count` column definition after `api_key_status`, and Manage Candidates still loads without runtime errors (value injection is Stage 2).

1. In `src/utils/config.py`, inside `DATA_SHAPES["candidates"]["list"]["manage"]`, after the `api_key_status` entry, append:

   ```python
   {"key": "dispatch_task_count", "label": "Dispatch tasks", "sortable": True, "type": "int"},
   ```

   ⚠️ **Decision:** Column lives in `DATA_SHAPES` (same pattern as `api_key_status`) so ListPage structure stays config-driven. The numeric value is not stored on the candidate row from `/api/candidates`; Stage 2 injects it from the counts API (missing key → `0`).

**Commit message:** `code(AST-876): stage 1 — dispatch_task_count manage column shape`

---

## Stage 2: Load counts, show column, Set dispatch tasks control

**Done when:** Manage Candidates shows an integer per-candidate dispatch-task count (0 when absent from the counts map), an admin can confirm and run **Set dispatch tasks**, the UI calls only the AST-875 admin contracts below, and after success the count for that candidate matches the API response `count` (then a full counts refresh). No call starts a dispatcher run.

### API contracts (from AST-875 — do not redefine)

- `GET /api/admin/dispatch_tasks/counts` → `{ "counts": { "<candidate_id>": <int>, ... } }` — missing keys mean `0`.
- `POST /api/admin/dispatch_tasks/set_from_template` with body `{ "candidate_id": "<target>" }` → `200` with at least `{ "candidate_id", "template_candidate_id", "inserted", "updated", "deleted", "count" }`; `400`/`404` with `{ "error": "..." }`.

### Steps

1. In `src/ui/frontend/src/pages/AdminManageCandidates.tsx`, add state:

   ```ts
   const [dispatchTaskCounts, setDispatchTaskCounts] = useState<Record<string, number>>({})
   const [settingCandidateId, setSettingCandidateId] = useState<string | null>(null)
   ```

2. Add `loadDispatchTaskCounts` (same file, next to `loadAll`):

   ```ts
   const loadDispatchTaskCounts = useCallback(() => {
     api("/api/admin/dispatch_tasks/counts")
       .then(async r => {
         if (!r.ok) {
           const body = await r.json().catch(() => ({}))
           throw new Error((body as { error?: string }).error || "Failed to load dispatch task counts")
         }
         return r.json()
       })
       .then(data => {
         const counts = (data && typeof data === "object" && data.counts && typeof data.counts === "object")
           ? data.counts as Record<string, number>
           : {}
         setDispatchTaskCounts(counts)
       })
       .catch(() => setDispatchTaskCounts({}))
   }, [])
   ```

   Call `loadDispatchTaskCounts()` from the existing initial `useEffect` alongside `loadAll()`, and from every success path that already calls `loadAll()` after mutate (add / edit / delete) so counts stay aligned after candidate list changes. Also call it after a successful set (step 6).

3. When building `rows`, merge the count onto each flattened candidate (do **not** put counts inside `flattenCandidate`):

   ```ts
   const rows = allCandidates.map(c => {
     const flat = flattenCandidate(c)
     const id = String(flat.astral_candidate_id || "")
     return {
       ...flat,
       dispatch_task_count: Number(dispatchTaskCounts[id] ?? 0),
     }
   })
   ```

4. In the `baseColumns` map (same place `api_key_status` gets a custom `render`), when `col.key === "dispatch_task_count"`, return a column that renders the value as a plain integer (coerce with `Number(val ?? 0)`). Leave other shape columns unchanged.

5. In the existing `_actions` column render (View / Edit / Delete icons), add a text button **after** the three icon buttons:

   - `className="dep-btn"` (or existing small admin button class used on this page — match `+ Add Candidate` / Clear key sizing: `padding: "6px 10px", fontSize: 12`).
   - Label: **`Set dispatch tasks`** (exact product string from parent AC).
   - `aria-label={`Set dispatch tasks for ${row.astral_candidate_id}`}`.
   - `disabled={settingCandidateId === row.astral_candidate_id}`.
   - `onClick`: `e.stopPropagation(); void handleSetDispatchTasks(row)`.

6. Implement `handleSetDispatchTasks(c: Candidate)`:

   1. `const ok = await confirm(`Replace dispatch tasks for "${c.astral_candidate_id}" with the template candidate’s full set? Existing extras for this candidate will be removed.`, { title: "Set dispatch tasks", confirmLabel: "Set tasks", variant: "danger" })`.
   2. If not `ok`, return.
   3. `setSettingCandidateId(c.astral_candidate_id)`.
   4. `api("/api/admin/dispatch_tasks/set_from_template", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ candidate_id: c.astral_candidate_id }) })`.
   5. On non-OK: parse JSON `error` (fallback `"Set dispatch tasks failed"`), toast error, clear `settingCandidateId`, return — same `.then(r => { if (!r.ok) return r.json().then(...) })` style as `handleEditSave` / `handleDelete` on this page (do **not** add `readApiError` unless already imported here).
   6. On OK: toast success text `Dispatch tasks set for "<id>" (<count> rows)` using response `count`; optimistically `setDispatchTaskCounts(prev => ({ ...prev, [id]: Number(data.count ?? 0) }))`; call `loadDispatchTaskCounts()`; clear `settingCandidateId`.
   7. Do **not** call any `/run`, `/stop`, scheduler, or other dispatch execution endpoint.

   ⚠️ **Decision:** Confirm dialog is required because set is upsert+prune (extras deleted). Variant `danger` matches Delete on this page.

   ⚠️ **Decision:** Frontend never sends or displays a hardcoded template id; template resolution stays server-side (AST-875 / `template_candidate_id()`).

7. No edits to `AdminScheduledActions.tsx`. AC verification that Scheduled Actions shows the resulting rows is operator/UAT after set (existing page already lists `dispatch_tasks` by candidate).

**Commit message:** `code(AST-876): stage 2 — Manage Candidates counts and Set dispatch tasks`

---

## Execution contract

- Execute stages in order; one commit per stage on `sub/AST-873/AST-876-manage-candidates-set-dispatch-tasks`; publish each stage with `git push origin HEAD:sub/AST-873/AST-876-manage-candidates-set-dispatch-tasks`.
- Do not add files, endpoints, or config keys beyond the Files Changed table.
- Do not implement upsert/prune/data/core/admin route bodies (AST-875).
- Do not edit `tests/` or `docs/test-bible/**`.
- Before Stage 2 runtime verification: ensure AST-875 endpoints are on the merged line (`git merge origin/ftr/AST-873-set-dispatch-tasks-button` after sibling rollup). If endpoints are missing when executing Stage 2 literally — stop and comment on **AST-873** with the Stage N blocked template; do not invent a parallel API.

---

## Self-Assessment

**Scope:** Single-Component — one `DATA_SHAPES` column plus Manage Candidates page wiring to existing admin contracts.

**Conf:** high — AST-875 already specifies exact request/response shapes; AdminManageCandidates already has ListPage columns, confirm, toast, and mutate-refresh patterns.

**Risk:** Medium — wrong client wiring could call set without confirm or fail to refresh counts; prune itself is server-side (AST-875). Mitigated by confirm + toast on error + no Run endpoints.

---

## Rules self-review

| Rule | Status |
|------|--------|
| §1.3 DRY | Reuses ListPage, confirm, toast, `api()`; no new list component |
| §1.4 / §2.1 config | Column structure in `DATA_SHAPES`; no hardcoded template candidate id in UI |
| §2.4 batch processing | UI does not claim batches or invent `batch_id` |
| §2.6 state machine | No candidate state transitions |
| §3.3 imports | Frontend → `/api/admin/*` only; no data/core imports |
| §3.5 naming | Button label matches parent product string; route paths match AST-875 |

## Review (build stub)

**Built:** `astral-AST-873` @ `d474848` on `origin/sub/AST-873/AST-876-manage-candidates-set-dispatch-tasks`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `3ab222c` | Plan doc |
| 1 | `49950d8` | `dispatch_task_count` manage column shape |
| 2 | `d474848` | counts load + Set dispatch tasks UI |

**Verify:** `./node_modules/.bin/tsc -b --noEmit` in `src/ui/frontend` — pass; `python3 -m py_compile src/utils/config.py` — pass.

**Note for Betty:** Manage Candidates calls AST-875 `GET /api/admin/dispatch_tasks/counts` and `POST /api/admin/dispatch_tasks/set_from_template`; no new backend.

## Radia review

**Diff:** `origin/dev...origin/sub/AST-873/AST-876-manage-candidates-set-dispatch-tasks` @ `a9f668d`

### What’s solid

- Plan stages 1–2 match the AST-876-owned product surface: `DATA_SHAPES` `dispatch_task_count` column; Manage Candidates loads `GET …/counts`, merges onto rows (missing → `0`), custom int render, **Set dispatch tasks** with danger confirm + `POST …/set_from_template`, optimistic count + refresh.
- §2.1 / G1: no hardcoded template id / `somerset` in the UI; column structure config-driven.
- §3.3: frontend calls admin API only; no data/core imports; no Run/scheduler endpoints.
- Confirm required before prune; `settingCandidateId` disables in-flight button; mutate paths (add/edit/delete) refresh counts.
- Self-Assessment Scope `Single-Component` matches the UI+shape footprint. Backend upsert/counts on this tip are the AST-875 merge (already reviewed) — no second implementation.

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| — | — | None |

### Recommended actions

| Action | Item |
|--------|------|
| none (ship) | 0 fix-now · 0 discuss · 0 advisory |

**Outcome:** Clean — ready for `resolve-child`.

## Resolution

**Date:** 2026-07-12  
**Review:** Radia clean sign-off @ `e63c6c5` (0 fix-now · 0 discuss · 0 advisory).

No product or plan changes required. Publish tip remains Radia’s review doc on `origin/sub/AST-873/AST-876-manage-candidates-set-dispatch-tasks`.

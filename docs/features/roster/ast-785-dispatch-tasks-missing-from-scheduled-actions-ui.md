# AST-785 — UAT: dispatch_task rows missing from Scheduled Actions UI

- **Linear (this ticket):** [AST-785](https://linear.app/astralcareermatch/issue/AST-785/uat-dispatch-task-rows-missing-from-scheduled-actions-ui-vet-inflow-seems-to)
- **Parent (AC reference only):** [AST-754](https://linear.app/astralcareermatch/issue/AST-754/vet-inflow-seems-to-have-been-skipped)
- **Publish ref:** `origin/sub/AST-754/AST-785-dispatch-tasks-missing-from-scheduled-actions-ui`

## Summary

Susan UAT (post **AST-754** prep-uat): Admin → **Scheduled Actions** shows no usable dispatch rows while `dispatch_task` table rows exist for the active candidate (including **vet_inflow_discovery** / inflow chain keys). Browser console shows no error. This UAT bug restores operational visibility: confirm whether rows are missing from the API payload or hidden by client filters / collapsed sections, then fix the root cause so configured rows are visible without extra clicks and empty states distinguish “no DB rows” from “filters hide rows”. Does **not** reopen **AST-775**/**AST-776** vet split behavior unless investigation proves seeding/dispatch logic (not UI/API) is at fault.

**Builds on:** [AST-568](https://linear.app/astralcareermatch/issue/AST-568) grouped sections (zero expanded allowed), [AST-634](https://linear.app/astralcareermatch/issue/AST-634) explicit Candidate filter, [AST-749](https://linear.app/astralcareermatch/issue/AST-749) retired-key filtering on `task_keys` only.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Auto-open first section once on load; filter-aware empty copy; optional load error toast | ui |
| `src/ui/api/api_admin.py` | Retired-key filter on `list_dtasks`; per-row `available_count` enrichment guard | ui |

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` | Auto-open first section; filter-empty vs true-empty copy; retired row omitted from list mock |
| `tests/component/ui/api/test_api_admin.py` | `list_dtasks` omits `DISPATCH_RETIRED_TASK_KEYS`; enrichment failure does not 500 whole list |

**No changes expected:** `src/utils/config.py`, `src/core/dispatcher.py`, `src/core/roster.py`, dispatch seeding, **AST-775**/**AST-776** product paths (unless Stage 1 investigation proves otherwise — then stop and comment on **AST-754**).

## Stage 1: Reproduce and identify root cause

**Done when:** Engineer records which of the three failure modes below matches Susan’s repro on a DB with known `dispatch_task` rows (local copy of staging or Susan’s `somerset` candidate), before editing product code.

1. **API payload vs DB (network tab — primary):**
   - Log in as admin; open DevTools → Network.
   - Load Admin → **Scheduled Actions**.
   - Inspect **`GET /api/admin/dispatch_tasks`**:
     - **200 + JSON array with N > 0** → rows reach the browser; root cause is client-side (Stage 2).
     - **200 + `[]`** while SQL `SELECT id, candidate_id, task_key FROM dispatch_task WHERE candidate_id = ?` returns rows → server-side list/filter/enrichment bug (Stage 3); check Flask logs for traceback during `list_dtasks`.
     - **4xx/5xx** → frontend keeps prior `data` (`[]` on first load) with **no console error** (matches Susan report); fix Stage 3 enrichment guard + surface toast (Stage 2 step 4).

2. **Candidate filter (client):**
   - With API returning rows, note left-nav selected candidate vs **Candidate** filter value on page (defaults to nav per **AST-634**).
   - If filter candidate ≠ row `candidate_id`, `filteredRows` is empty → page shows **No dispatch tasks configured** (misleading). Record IDs; do **not** change seeding in this ticket unless Stage 1 proves rows were seeded for a different id than nav exposes.

3. **Collapsed sections (client — zero expanded by design since AST-568):**
   - With API returning rows and Candidate filter matching (or **All**), check whether section headers render (e.g. `C. Company Roster (0 / N AUTO)`) but **no `<table>`** until **Expand section** is clicked (`resolvedOpenSection === null` → conditional mount hides `ScheduledPhaseTable`).
   - If Susan’s “empty / nothing usable” matches collapsed headers only → Stage 2 auto-open fixes it without reopening vet split work.

4. **Stop gate:** If Stage 1 proves missing rows are caused by absent/wrong `dispatch_task` seeding or **AST-776** eligibility returning zero for all inflow keys while rows exist in DB with wrong `entity_type`/`trigger_state` stored on the row — post 🛑 on parent **AST-754** with evidence; **do not** proceed to Stages 2–3 in this ticket.

## Stage 2: Scheduled Actions UI — visible rows and honest empty states

**Done when:** With mocked or live API returning inflow-chain rows for the active candidate, Susan sees at least one expanded section with a visible dispatch table on first page load (no manual expand required for first visit); when filters hide all rows, copy says filters are active (not “not configured”).

1. In **`src/ui/frontend/src/pages/AdminScheduledActions.tsx`**, add a one-shot auto-open ref immediately after the `openSection` state declaration:

   ```typescript
   const didAutoOpenSectionRef = useRef(false)
   ```

2. Add a `useEffect` after the `sections` `useMemo` (depends on `[sections]` only):

   ```typescript
   useEffect(() => {
     if (didAutoOpenSectionRef.current || sections.length === 0) return
     didAutoOpenSectionRef.current = true
     setOpenSection(sections[0].sectionKey)
   }, [sections])
   ```

   ⚠️ **Decision:** Auto-open runs **once per page mount** so **AST-568** “collapse all sections” still works after Susan collapses — ref prevents re-expanding on every filter change.

3. Replace the empty-state branch (~lines 714–715) with filter-aware copy:

   ```tsx
   ) : sections.length === 0 ? (
     <div className="list-page-status">
       {data.length > 0
         ? "No dispatch tasks match the current filters. Try Candidate: All or clear Section/Group and Task filters."
         : "No dispatch tasks configured"}
     </div>
   ) : sections.map(sec => (
   ```

4. In **`loadData`**, when `tasksRes.ok` is false on initial load, set a toast (reuse existing `Toast` state):

   ```typescript
   if (!tasksRes.ok) {
     setToast({ text: `Failed to load dispatch tasks (${tasksRes.status})`, variant: "error" })
   }
   ```

   Do not `console.error` — toast is sufficient for admin visibility.

5. Manual sanity (engineer, not a commit artifact): with rows in DB for nav candidate, reload page → first section expanded, table visible; set Candidate filter to a non-matching id → filter-aware message; collapse all sections → stays collapsed.

## Stage 3: Admin API — list robustness (retired keys + enrichment guard)

**Done when:** `GET /api/admin/dispatch_tasks` omits retired consult aliases (parity with **`dispatch_task_keys`**), and a single bad eligibility row cannot 500 the entire list.

1. In **`src/ui/api/api_admin.py`**, inside **`list_dtasks`**, after building `rows` from `list_dispatch_tasks()` and **before** the enrichment loop, filter retired keys (mirror **`dispatch_task_keys`**):

   ```python
   rows = [r for r in rows if r.get("task_key") not in DISPATCH_RETIRED_TASK_KEYS]
   ```

2. Wrap per-row **`available_count`** enrichment in try/except:

   ```python
   for row in rows:
       is_scored = dispatch_claim_uses_score_floor(row.get("trigger_state"))
       row["is_scored"] = is_scored
       if not is_scored:
           row["score_floor"] = None
       elif row.get("score_floor") is None:
           row["score_floor"] = 1.0
       et = row.get("entity_type")
       ts = row.get("trigger_state")
       cid = row.get("candidate_id", "")
       try:
           row["available_count"] = (
               database.count_eligible_for_dispatch_task(row) if et and ts and cid else 0
           )
       except Exception as exc:
           logger.warning(
               "list_dtasks: available_count failed for dispatch_task id=%s task_key=%r: %s",
               row.get("id"),
               row.get("task_key"),
               exc,
           )
           row["available_count"] = 0
   ```

   Use existing module **`logger`** from `src.utils.logging` (add import only if missing).

3. Keep existing **`admin_hidden_dispatch_task_keys()`** filter after enrichment (order: retired filter → enrich → hidden filter).

4. Do **not** add **`req_dict`** behavior changes.

## Stage 4: Verification (build-child handoff)

**Done when:** Product matches Stages 2–3; engineer grep confirms no scope creep into roster/dispatch seeding.

1. Grep **`src/core/roster.py`** **`run_inflow_discovery_batch`** for **`do_task`** / inline vet — must remain absent (**AST-775** boundary).
2. Post **`[qa-handoff]`** on **AST-785** assigning Betty if **`test_AdminScheduledActions.test.tsx`** needs new cases for auto-open / filter-empty copy / API retired filter — **do not** edit **`tests/`** locally (pre-commit hook).

## Execution contract (developer agent)

- Execute stages **1 → 4** in order; **Stage 1 is read-only** until root cause is recorded in a Linear comment on **AST-785** (one paragraph: API status, row count, filter state, collapsed vs empty).
- Stages 2–3: **one commit each** on epic worktree; publish each to **`origin/sub/AST-754/AST-785-dispatch-tasks-missing-from-scheduled-actions-ui`** via **build-child** §6.
- Do **not** add files beyond the table above unless Stage 1 stop gate triggers.
- Blocking ambiguity → comment on parent **AST-754** with 🛑 format from **plan-child**.

## Self-Assessment

**Scope:** `Single-Component` — one admin React page plus narrow **`list_dtasks`** API hardening; no roster inflow or vet dispatch behavior changes in the happy path.

**Conf:** `Medium` — Stage 1 must confirm API vs filter vs collapsed-section failure mode before Stage 2–3; auto-open and filter copy are straightforward once mode is known.

**Risk:** `Medium` — wrong diagnosis could ship UI-only fixes while API still 500s, or touch vet seeding out of scope; Stage 1 stop gate and per-row enrichment guard limit blast radius.

### Justifications

- **Scope:** Two files in the admin UI layer; ticket boundaries exclude **AST-775**/**AST-776** unless investigation escalates.
- **Conf:** Three documented repro branches cover Susan’s “no console error” symptom; Stage 1 is mandatory before code.
- **Risk:** Scheduled Actions is operational surface; API guard prevents total list failure from one bad row; auto-open is one-shot to preserve collapse-all.

## Self-review (ASTRAL_CODE_RULES)

| Rule | Notes |
|------|-------|
| §1.3 DRY | Reuses existing `DISPATCH_RETIRED_TASK_KEYS` and `admin_hidden_dispatch_task_keys` patterns from **`dispatch_task_keys`** |
| §1.5 logging | API guard uses `logger.warning` once per failed row — no debug contract |
| §2.1 config | No new config keys; retired/hidden sets unchanged |
| §3.3 imports | `api_admin.py` stays ui → data/utils only |
| §3.5 naming | Filter message plain English; ref name `didAutoOpenSectionRef` matches page conventions |

No **`conf-!!-NONE`** conflicts identified.

## Review stub (build)

**Publish ref:** `origin/sub/AST-754/AST-785-dispatch-tasks-missing-from-scheduled-actions-ui`  
**Product tip:** `ac0d250` — `58b0f1b` (UI auto-open + filter copy + load toast) + `ac0d250` (list_dtasks retired filter + enrichment guard)

**Stage 1 finding:** Root cause is client-side — AST-568 zero-expanded sections hide `ScheduledPhaseTable` until manual expand; misleading “No dispatch tasks configured” when Candidate filter hides rows. No seeding/dispatch defect found; AST-775 boundary intact (no inline vet in `run_inflow_discovery_batch`).

**Built:** One-shot auto-open first section on load; filter-aware empty copy; toast on failed `GET /api/admin/dispatch_tasks`; `list_dtasks` filters `DISPATCH_RETIRED_TASK_KEYS` and guards per-row `available_count` enrichment.

**QA note:** Betty manifest expected for auto-open first visit, filter-empty copy, retired row omitted from list API, enrichment failure does not 500 — `[qa-handoff]` on AST-785.

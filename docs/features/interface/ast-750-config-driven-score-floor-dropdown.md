<!-- linear-archive: AST-750 archived 2026-06-23 -->

## Linear archive (AST-750)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-750/config-driven-score-floor-dropdown-for-dispatch-task-modal-add-000-to  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-743 — Add 0.00 to score floor selection list  
**Blocked by / blocks / related:** parent: AST-743

### Description

## What this implements

Add **0.00** to the dispatch **score floor** dropdown and make the full allowed-value list config-driven: define the catalog once in product config, expose it through the admin API, and wire the **Edit Dispatch Task** modal on Scheduled Actions to load options from that API instead of a hardcoded React array. Preserve existing scored-row gating (`dispatch_claim_uses_score_floor`), save/display parity for **0.00**, and the **1.00** default when scored and unset.

## Acceptance criteria

1. **0.00 in dropdown:** For a scored dispatch row, the Edit Dispatch Task modal **Score Floor** list includes **0.00** as the first option.
2. **Config-driven:** Allowed values are defined once in `config.py`; no duplicate numeric array remains in `AdminScheduledActions.tsx` for floor options.
3. **API-served:** The modal loads floor options from an admin API response (not client-invented constants).
4. **Persist 0.00:** Saving **0.00** on a scored row stores **0.0** in `dispatch_task.score_floor`; reload/edit shows **0.00** selected and the list row **Floor** column shows **0.00**.
5. **Existing range preserved:** Options from **1.00** through **10.00** in **0.50** steps remain available (plus **0.00** and **0.50** at the low end).
6. **Unscored rows unchanged:** Rows where `is_scored` is false still hide **Score Floor** and persist `score_floor` **null**.

## Boundaries

* Does **not** change `dispatch_claim_uses_score_floor`, dispatcher claim math, or `pass_threshold` grading.
* Does **not** redesign Scheduled Actions layout (**AST-735**).
* Does **not** add score-floor pickers elsewhere beyond fixing the Edit Dispatch Task modal source of truth.

## Notes for planning

* Follow `ASTRAL_CODE_RULES` §1.4 / §2.1 — allowed value sets in `config.py`; admin metadata pattern like `/api/admin/dispatch_tasks/state_options`.
* Primary files: `src/utils/config.py`, `src/ui/api/api_admin.py`, `src/ui/frontend/src/pages/AdminScheduledActions.tsx`.
* Backend already accepts `score_floor` **0.0** on scored updates (existing component tests).

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/AST-743-add-000-to-score-floor-selection-list`, child `sub/AST-743/AST-744-<slug>`. Created at **dispatch-parent**.

### Comments

#### chuckles — 2026-06-18T22:56:56.116Z
QA manifest by Betty.

**Tests Ready manifest (test-child)**

1. Config catalog — tests/component/utils/test_config.py::TestAst750DispatchScoreFloorCatalog
2. Admin API — tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_scheduler_and_run_controls
3. Scheduled Actions — tests/component/frontend/pages/test_AdminScheduledActions.test.tsx — AST-750: edit save sends score_floor 0 when 0.00 selected

Publish ref: origin/sub/AST-743/AST-750-config-driven-score-floor-dropdown @ b2181e0

— Betty

#### katherine — 2026-06-18T22:50:39.551Z
Plan doc: https://github.com/susansomerset/astral/blob/sub/AST-743/AST-750-config-driven-score-floor-dropdown/docs/features/interface/ast-750-config-driven-score-floor-dropdown.md

**Self-assessment**
- **Scope:** Single-Component — config catalog, one admin GET route, one React page; no dispatcher/DB changes.
- **Conf:** high — mirrors `state_options` pattern; backend already accepts 0.0; plan patches frontend `parseFloat || 1` zero-save bug for AC #4.
- **Risk:** low — admin dropdown only; claim gating untouched.

Revision 1 patches Stage 3 save coercion so **0.00** persists (prior draft left `parseFloat(form.score_floor) || 1` unchanged).

#### chuckles — 2026-06-18T22:50:38.793Z
**validate-plan: APPROVED**

Plan matches AST-743 definition: config catalog (0.00–10.00, step 0.50), admin API metadata endpoint, modal wired to API; boundaries preserved (no claim gating / dispatcher changes). Layer table correct (utils + ui only). Betty tests deferred per build ban.

— Chuckles

#### katherine — 2026-06-18T22:50:13.034Z
Plan: [ast-750-config-driven-score-floor-dropdown.md](https://github.com/susansomerset/astral/blob/sub/AST-743/AST-750-config-driven-score-floor-dropdown/docs/features/interface/ast-750-config-driven-score-floor-dropdown.md)

**Self-assessment**
- **Scope:** Single-Component — config tuple + helper, one admin GET route, one React page; no dispatcher/core changes.
- **Conf:** high — mirrors `state_options` metadata pattern; backend already persists `score_floor` 0.0 on scored rows.
- **Risk:** low — catalog mistake only affects admin dropdown labels; claim gating and save coercion unchanged.

Four stages: (1) `DISPATCH_SCORE_FLOOR_VALUES` 0.0–10.0 step 0.5 in config, (2) `GET /api/admin/dispatch_tasks/score_floor_options`, (3) remove hardcoded `useMemo` in `AdminScheduledActions.tsx`, (4) Betty QA manifest notes.

---

# Config-driven score floor dropdown for dispatch task modal (Add 0.00 to score floor selection list)

**Linear:** [AST-750](https://linear.app/astralcareermatch/issue/AST-750/config-driven-score-floor-dropdown-for-dispatch-task-modal-add-000-to)  
**Parent:** [AST-743](https://linear.app/astralcareermatch/issue/AST-743/add-000-to-score-floor-selection-list)  
**Publish ref:** `sub/AST-743/AST-750-config-driven-score-floor-dropdown`

Add **0.00** (and **0.50**) to the dispatch **Score Floor** dropdown and define the full allowed-value catalog once in `config.py`, expose it through a new admin metadata endpoint, and wire the **Edit Dispatch Task** modal on Scheduled Actions to load `<select>` options from that API instead of the hardcoded React `useMemo`. Backend save/display paths for scored vs unscored rows stay unchanged except fixing frontend save coercion so **0.00** persists.

**Verified (plan time):** `handleSave` uses `parseFloat(form.score_floor) || 1`, which coerces **0.00** to **1** on save — must fix in Stage 3. Backend `update_dtask` / `create_dtask` already persist `score_floor` **0.0** when the client sends numeric zero (`test_update_dispatch_task_scored_zero_score_floor` on `origin/dev`).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `DISPATCH_SCORE_FLOOR_VALUES` tuple + `dispatch_score_floor_option_labels()` helper | utils |
| `src/ui/api/api_admin.py` | New `GET /api/admin/dispatch_tasks/score_floor_options` endpoint | ui |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Fetch score-floor options from API; remove hardcoded `useMemo`; fix zero save coercion | ui |

**Out of scope (do not touch):**

| File / area | Reason |
|-------------|--------|
| `dispatch_claim_uses_score_floor`, dispatcher claim math, `pass_threshold` | Parent boundary — AST-586 / AST-617 behavior preserved |
| Scheduled Actions layout/grouping/filters | AST-735 |
| `tests/**` | Betty (qa-child) |

## Stage 1: Config catalog (single source of truth)

**Done when:** `DISPATCH_SCORE_FLOOR_VALUES` exists in `config.py` with the full ordered catalog (0.00 through 10.00 in 0.50 steps) and `dispatch_score_floor_option_labels()` returns two-decimal strings for UI `<select>` labels.

1. In `src/utils/config.py`, immediately after the `PASSED_SCORE_GATED_STATES` block (before `dispatch_claim_uses_score_floor`), add:

   ```python
   # Admin Edit Dispatch Task modal — score_floor dropdown (AST-743 / AST-750).
   DISPATCH_SCORE_FLOOR_VALUES: tuple[float, ...] = tuple(i * 0.5 for i in range(21))  # 0.0 … 10.0
   ```

   ⚠️ **Decision:** `range(21)` yields 21 values: **0.00, 0.50, 1.00, …, 10.00**. This extends today's frontend list (1.00–10.00, 19 values) with **0.00** and **0.50** at the low end per parent open question #1 (Susan confirmed).

2. In the same file, after `DISPATCH_SCORE_FLOOR_VALUES`, add:

   ```python
   def dispatch_score_floor_option_labels() -> list[str]:
       """Two-decimal strings for admin score_floor <select> options."""
       return [f"{v:.2f}" for v in DISPATCH_SCORE_FLOOR_VALUES]
   ```

3. Do **not** change `dispatch_claim_uses_score_floor`, `PASSED_SCORE_GATED_STATES`, or any dispatcher/claim logic.

## Stage 2: Admin API endpoint

**Done when:** Authenticated `GET /api/admin/dispatch_tasks/score_floor_options` returns JSON `{"values": ["0.00", "0.50", …, "10.00"]}` sourced from config; no hardcoded list in `api_admin.py`.

1. In `src/ui/api/api_admin.py`, add `dispatch_score_floor_option_labels` to the existing config import block (alongside `dispatch_claim_uses_score_floor`).

2. Add a new route immediately after `dispatch_task_state_options` (after line ~820):

   ```python
   @admin_bp.route("/dispatch_tasks/score_floor_options")
   @require_admin
   def dispatch_task_score_floor_options():
       return jsonify({"values": dispatch_score_floor_option_labels()})
   ```

3. Do **not** add server-side validation that rejects `score_floor` values outside this catalog on create/update — existing float coercion on scored rows is sufficient (component tests already cover **0.0**). This ticket only fixes the admin dropdown source of truth.

## Stage 3: Scheduled Actions modal wiring

**Done when:** `AdminScheduledActions.tsx` has no client-generated score-floor option array; the modal `<select>` renders options from the API response (first option **0.00**); saving **0.00** on a scored row sends JSON `score_floor: 0` (not **1**); reopening the edit modal shows **0.00** selected; table **Floor** column shows **0.00** for that row; unscored rows still hide **Score Floor** and send `score_floor: null`.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, add state alongside `stateOptions`:

   ```typescript
   const [scoreFloorOptions, setScoreFloorOptions] = useState<string[]>([])
   ```

2. **Delete** the hardcoded `useMemo` block (lines ~258–261):

   ```typescript
   const scoreFloorOptions = useMemo(
     () => Array.from({ length: 19 }, (_, i) => (1 + i * 0.5).toFixed(2)),
     [],
   )
   ```

3. In `loadData`, extend the `Promise.all` call to fetch score-floor options in parallel:

   ```typescript
   const [tasksRes, keysRes, statesRes, floorsRes] = await Promise.all([
     api("/api/admin/dispatch_tasks"),
     api("/api/admin/dispatch_tasks/task_keys"),
     api("/api/admin/dispatch_tasks/state_options"),
     api("/api/admin/dispatch_tasks/score_floor_options"),
   ])
   ```

4. After the existing `statesRes` handling block, parse floors:

   ```typescript
   if (floorsRes.ok) {
     const floors = await floorsRes.json()
     setScoreFloorOptions(Array.isArray(floors?.values) ? floors.values : [])
   }
   ```

5. In `handleSave`, replace both scored-row `score_floor` expressions (~lines 452 and 474):

   ```typescript
   score_floor: form.is_scored
     ? (() => {
         const n = parseFloat(form.score_floor)
         return Number.isFinite(n) ? n : 1
       })()
     : null,
   ```

   ⚠️ **Decision:** Explicit `Number.isFinite` check — **not** `parseFloat(...) || 1` — so **0.00** persists as **0.0**. Default **1.0** applies only when the form value is missing or non-numeric.

6. Leave unchanged:
   - `{form.is_scored && ( … Score Floor select … )}` gating (AC #6).
   - Form default `score_floor: "1.00"` for new rows.
   - `openEdit` display path: `(row.score_floor ?? 1).toFixed(2)`.
   - Table **Floor** column: `(row.score_floor ?? 1).toFixed(2)` for scored rows, `—` for unscored.

7. Do **not** add a client-side fallback that regenerates 1.00–10.00 if the API fails — empty options until reload is acceptable (same pattern as empty `stateOptions` on failure).

## Stage 4: QA handoff expectations (Betty — not engineer)

**Done when:** Betty's qa-child manifest covers new endpoint + frontend fetch; engineer does not commit under `tests/`.

Document for Betty:

| Area | Expected bible/manifest update |
|------|--------------------------------|
| `tests/component/utils/test_config.py` | Assert `DISPATCH_SCORE_FLOOR_VALUES` length 21, first `0.0`, last `10.0`, step `0.5`; assert `dispatch_score_floor_option_labels()[0] == "0.00"` |
| `tests/component/ui/api/test_api_admin.py` | Add GET `/api/admin/dispatch_tasks/score_floor_options` — `"0.00"` first, `"10.00"` last, 21 entries |
| `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` | Mock new URL in `api()` handler; assert scored-row modal save sends `score_floor: 0` when **0.00** selected |

Engineer runs manual smoke only: open Scheduled Actions → edit a scored row (e.g. `PASSED_JD`) → confirm **0.00** is first option → save **0.00** → reload → Floor column and modal show **0.00**.

## Self-Assessment

**Scope:** `Single-Component` — touches config catalog, one admin GET route, and one React page; no core/dispatcher/data changes.

**Conf:** `high` — mirrors existing `state_options` metadata pattern; backend save path for `score_floor` already proven in component tests; frontend zero-save gap identified and specified.

**Risk:** `low` — wrong catalog only affects admin dropdown labels; claim math and scored/unscored gating are untouched.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.4 / §2.1 Config as source of truth | Allowed value set moves from React inline array to `config.py` ✓ |
| §1.3 DRY | Single tuple + one formatter; API and UI both read config ✓ |
| §3.3 Imports | `api_admin` imports from `src.utils.config` only; no layer violations ✓ |
| §2.6 State machine | No state transitions changed ✓ |
| §3.5 Naming | Follows `dispatch_*` / `DISPATCH_*` conventions near score-floor helpers ✓ |

No conflicts requiring `conf-!!-NONE`.

## Revisions

Revision 1 — 2026-06-18  
Driven by: resume-spawn plan pass — AC #4 zero-save gap in existing `handleSave` (`parseFloat(form.score_floor) || 1` coerces 0 → 1).  
Changes: Stage 3 step 5 now fixes save coercion with `Number.isFinite`; Stage 3 **Done when** and Betty manifest updated for zero persist assertion.

## Review (build)

**Built:** `origin/sub/AST-743/AST-750-config-driven-score-floor-dropdown` @ `ab3fb981`

**Product:** Stage 1 — `DISPATCH_SCORE_FLOOR_VALUES` + `dispatch_score_floor_option_labels()` in `config.py`. Stage 2 — `GET /api/admin/dispatch_tasks/score_floor_options`. Stage 3 — API-driven modal dropdown + `Number.isFinite` zero-save fix in `AdminScheduledActions.tsx`.

**Out of build scope (Betty / qa-child):** component/API/frontend tests per Stage 4 table.

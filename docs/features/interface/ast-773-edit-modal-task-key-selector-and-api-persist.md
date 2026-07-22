<!-- linear-archive: AST-773 archived 2026-07-22 -->

## Linear archive (AST-773)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-773/edit-modal-task-key-selector-and-api-persist-cannot-change-task-key-in  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-763 — Cannot change task_key in the scheduled task modal  
**Blocked by / blocks / related:** parent: AST-763

### Description

## What this implements

Enable changing `task_key` when editing an existing scheduled action: show the Task dropdown on Edit Task (same catalog as Add Task), persist `task_key` on save, validate that the chosen key is valid for the row's Input State without resetting Score Floor or Input State, block edit when AUTO is on, and allow edit while a thread is running (changes apply to future runs only).

## Acceptance criteria

1. Open **Edit Task** on a non-AUTO scheduled-action row — the **Task** dropdown is visible with the current task key selected.
2. Choose a different task key, keep or adjust **Input State** / **Score Floor** manually, and **Save** — after reload, the row shows the new task key; **Score Floor** unchanged unless Susan edited it.
3. Save with a `task_key` invalid for the row's **Input State** — explicit validation error; no save.
4. Attempt to save a change that would duplicate `(candidate, task_key, trigger_state)` — explicit error; modal stays open.
5. Row with **AUTO mode** on — **Edit Task** is unavailable or blocked (cannot change task_key while AUTO is on).
6. Row with an active running thread — **Edit Task** and save succeed; in-flight run behavior unchanged; subsequent runs use updated row values.
7. Add Task, run/stop, AUTO/Dbg column toggles, filters, collapsible task groups, and Stop All still behave as before UAT on AST-735.
8. Component tests cover Edit Task task-key selection, validation, AUTO-blocked edit, and successful save with an updated key.

## Boundaries

* Does not allow changing candidate on an existing row.
* Does not auto-reset Input State or Score Floor when Task changes.
* Does not change scheduler tick logic, claim/run behavior, or ledger semantics beyond future runs picking up saved values.
* Does not bulk-migrate or clone scheduled actions.
* Sibling scope: none — single child covers UI + admin API for this bug.

## Notes for planning

* Primary files: `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, `src/ui/api/api_admin.py` (PUT `/dispatch_tasks/<id>` currently omits `task_key` from allowed fields; edit modal hides Task selector when `editRow` is set).
* Preserve row values on task_key change; entity type follows selected key (read-only).
* Regression guard for AST-735/751 Scheduled Actions layout and filters.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/AST-763-edit-modal-task-key`, child `sub/AST-763/<child-id>-edit-modal-task-key-and-api`. Created at dispatch-parent.

### Comments

#### radia — 2026-06-23T21:06:18.676Z
### Review — `origin/dev`…`origin/sub/AST-763/AST-773-edit-modal-task-key-and-api` @ `9219d8c`

**Plan fidelity (A):** PUT accepts `task_key` with `_dispatch_task_key_trigger_error`, derived `entity_type` / `sort_by` / `batch_call_mode`, AUTO guard (`auto_mode`-only when AUTO on), 409 cites attempted triple. UI: Task `<select>` on edit, `taskKeyChangePatch` preserves Input State / Score Floor, AUTO toast + row click block, `task_key` in PUT body.

**Code rules (A):** §3.3 — API imports config/utils + data whitelist only; validation via `dispatch_task_admin_defaults` / state registries; no silent `except`, no `print()`.

**Tests:** Betty `merge-tests` — `TestAst773UpdateDispatchTaskTaskKey` (5), frontend `AST-773 edit modal task_key` (5).

**discuss — sibling bleed at merge-child:** `src/utils/config.py` adds `DISPATCH_SCORE_FLOOR_VALUES` / `dispatch_score_floor_option_labels()` (AST-750) on the three-dot diff via merge ancestry, not Katherine’s `code(AST-773)` commits. No `/dispatch_tasks/score_floor_options` on this ref; UI still hardcodes `scoreFloorOptions`. Confirm strip vs defer to AST-750 rollup on `ftr/AST-763`.

**advisory:** `_dispatch_task_key_trigger_error` runs only when `"task_key" in data` — PUT with `trigger_state` alone does not re-validate against existing `task_key` (pre-PUT behavior; plan scoped to task_key changes).

**advisory:** `taskKeyChangePatch` can show Score Floor when catalog `is_scored` flips but preserved `trigger_state` is non-scored; server coerces via `dispatch_claim_uses_score_floor` on save — acceptable per plan’s preserve-Input-State decision.

Feature doc: `docs/features/interface/ast-773-edit-modal-task-key-selector-and-api-persist.md` (Review section).

#### chuckles — 2026-06-23T21:04:01.327Z
[check-linear]

**Tests updated for [qa-handoff]** — manifest item 3 regression fixed.

**Cause:** AST-751 assertions used `/D\. Job Analysis/` and `/C\. Company Roster/` — ambiguous with AST-768 Section/Group `<option>` labels (same text).

**Fix:** Tightened four AST-751 cases to section-header patterns (`/D\. Job Analysis \(.*AUTO\)/`, `/C\. Company Roster \(.*AUTO\)/`) — matches AST-768 style.

**Publish:** `origin/sub/AST-763/AST-773-edit-modal-task-key-and-api` @ `d811040`
**Tests SHA:** `origin/tests` @ `5ffe40a`

**Re-run (manifest item 3):**
```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-751|AST-768|AST-647"
```

— Betty

#### katherine — 2026-06-23T21:02:24.285Z
[qa-handoff]

@Betty White — manifest items **1** and **2** green on `origin/sub/AST-763/AST-773-edit-modal-task-key-and-api` @ `8571222`. Item **3** (regression) fails — **test/manifest**, not product.

**Green:**
```bash
ASTRAL_PYTHON=/home/susan/astral-AST-763/.venv/bin/python ./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_admin.py::TestAst773UpdateDispatchTaskTaskKey -q
# 5 passed

cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx --testNamePattern="AST-773"
# 5 passed
```

**Red — manifest item 3:**
```bash
cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx --testNamePattern="AST-751|AST-768|AST-647"
# 4 failed | 10 passed
```

Failures (all AST-751):
- `combined AUTO and Task filters intersect`
- `renders em dash for zero or null available count`
- `All-candidate default sort orders same task by available count descending`
- `floor range filter excludes non-scored rows`

**Why test/manifest:** Each failure is `getByText(/D\. Job Analysis/)` or `queryByText(/C\. Company Roster/)` matching **both** the collapsible section header **and** the **Section/Group** filter `<option>` text (AST-768). Example: `getMultipleElementsFoundError` at line 649. Same failures reproduce on product-only commit `03fd877` (before `merge-tests`) — not introduced by AST-773 code.

**Ask:** Tighten AST-751 regression assertions (e.g. `/D\. Job Analysis \(.*AUTO\)/` or scope queries to `.collapsible-panel-label-wrap` / exclude `.admin-filters`) or narrow manifest item 3 to tests that are selector-stable.

No product commits from me — staying **Tests Ready**.

#### chuckles — 2026-06-23T20:57:15.129Z
## Tests Ready — Betty manifest (AST-773)

Publish: `origin/sub/AST-763/AST-773-edit-modal-task-key-and-api` @ `8571222`
Tests SHA: `origin/tests` @ `fb8c8c1`

**Bible shasum (publish ref):**
- `docs/test-bible/frontend/pages.md` — `185d7dd0629343b4076080b6ce23f7686d3f2c63`
- `docs/test-bible/ui/api/api_admin.md` — `6ae53f12c5afc1e35fdc87c4c862978608e2c507`

### Manifest (test-child)

1. **API — PUT `task_key` validation** (required):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst773UpdateDispatchTaskTaskKey \
  -q
```

2. **Scheduled Actions routed page — edit modal task_key** (**§6c**, required):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-773"
```

3. **Regression — existing Scheduled Actions smoke** (required):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-751|AST-768|AST-647"
```

**Pass criterion:** pytest + Vitest green on items 1–3 — not zero-arg harness / full branch-lock gate.

**Coverage map:** `docs/test-bible/frontend/pages.md` (**AST-773**), `docs/test-bible/ui/api/api_admin.md` (**AST-773**).

— Betty

#### katherine — 2026-06-23T20:52:16.802Z
Plan: `docs/features/interface/ast-773-edit-modal-task-key-selector-and-api-persist.md`
GitHub: https://github.com/susansomerset/astral/blob/sub/AST-763/AST-773-edit-modal-task-key-and-api/docs/features/interface/ast-773-edit-modal-task-key-selector-and-api-persist.md
Publish ref @ `ce2de0b`

**Scope:** `Single-Component` — Scheduled Actions edit modal + `PUT /api/admin/dispatch_tasks/<id>` + dispatch_task update whitelist.

**Conf:** `high` — localized gap (hidden Task select + omitted PUT field); mirrors existing Add Task / POST patterns.

**Risk:** `Medium` — UNIQUE triple and AUTO guard must not block legitimate saves; explicit validation helper + UI/server AUTO symmetry.

Two stages: (1) API persist/validate `task_key` with derived catalog columns; (2) UI Task dropdown on edit, preserve Input State/Score Floor on task change, block AUTO-row edit.

---

# Edit modal task_key selector and API persist (Cannot change task_key in the scheduled task modal)

**Linear:** [AST-773](https://linear.app/astralcareermatch/issue/AST-773/edit-modal-task-key-selector-and-api-persist-cannot-change-task-key-in)  
**Parent:** [AST-763](https://linear.app/astralcareermatch/issue/AST-763/cannot-change-task-key-in-the-scheduled-task-modal)  
**Publish ref:** `sub/AST-763/AST-773-edit-modal-task-key-and-api`

Susan cannot change `task_key` when editing an existing Scheduled Actions row — the Add/Edit modal hides the **Task** dropdown whenever `editRow` is set, and `PUT /api/admin/dispatch_tasks/<id>` whitelists scheduling fields only (no `task_key`). This ticket exposes the same Task catalog on **Edit Task**, persists `task_key` on save with validation, blocks edit while **AUTO** is on, and leaves in-flight runs untouched (changes apply to future runs only).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Extend `_DISPATCH_TASK_UPDATE_COLS` with `task_key`, `sort_by`, `batch_call_mode` | data |
| `src/ui/api/api_admin.py` | Validation helper; accept `task_key` on PUT; derive catalog columns; AUTO guard; fix 409 message | ui |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Task dropdown on edit; preserve Input State / Score Floor on task change; block AUTO-row edit; include `task_key` in PUT body | ui |

**Out of scope (this ticket):** candidate change on existing rows; auto-reset of Input State or Score Floor when Task changes; scheduler/dispatch claim logic; bulk clone; `tests/**` (Betty manifest below).

**QA manifest (Betty — not engineer commits):** Extend `tests/component/ui/api/test_api_admin.py` and `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` for: Edit modal shows Task `<select>` with current key selected; task change preserves `trigger_state` / `score_floor` in PUT body; invalid `(task_key, trigger_state)` → 400 with explicit error; duplicate `(candidate_id, task_key, trigger_state)` → 409 modal stays open; AUTO row cannot open Edit Task (or save blocked); non-AUTO row with running thread can edit and save new `task_key`; existing run/stop/filter/grouping tests still pass.

---

## Stage 1: Admin API — persist and validate `task_key` on PUT

**Done when:** `PUT /api/admin/dispatch_tasks/<id>` accepts `task_key`, validates it against the row's `trigger_state`, updates derived dispatch columns, rejects AUTO rows and invalid combinations with explicit JSON errors, and returns 409 with the **new** triple on UNIQUE collision.

1. In `src/data/database.py`, extend `_DISPATCH_TASK_UPDATE_COLS` (~line 5608) to include `"task_key"`, `"sort_by"`, and `"batch_call_mode"` (keep existing columns). No other schema change.

2. In `src/ui/api/api_admin.py`, add imports if not already present: `COMPANY_STATES`, `JOB_STATES`, `dispatch_task_admin_defaults`, `dispatch_task_key_retired_message`, `resume_artifact_compound_state`, `resume_artifact_hop_task_keys` from `src.utils.config`.

3. Immediately above `update_dtask` (~line 870), add helper `_dispatch_task_key_trigger_error(task_key: str, trigger_state: str | None) -> str | None`:
   - Strip `task_key`; empty → return `"task_key is required"`.
   - If `dispatch_task_key_retired_message(task_key)` returns a string, return that string.
   - `try: defaults = dispatch_task_admin_defaults(task_key)` except `KeyError` → return `f"Unknown or non-schedulable task_key: {task_key!r}"`.
   - Let `ts = (trigger_state or "").strip()`; empty → return `"trigger_state is required"`.
   - Let `et = defaults["entity_type"]`. If `et == "job"`, require `ts in JOB_STATES`. If `et == "company"`, require `ts in COMPANY_STATES`. Else return `f"task_key {task_key!r} has unsupported entity_type {et!r}"`.
   - If `task_key in resume_artifact_hop_task_keys()`, require `ts == resume_artifact_compound_state(task_key)`; mismatch → return `f"task_key {task_key!r} requires trigger_state {resume_artifact_compound_state(task_key)!r} (got {ts!r})"`.
   - Return `None` when valid.

   ⚠️ **Decision:** Validation is entity-registry + resume-hop compound alignment only — it does **not** require `trigger_state == dispatch_task_admin_defaults(task_key)["trigger_state"]`, so rows like `qualify_job_listings` @ `VALID_TITLE` remain valid after retargeting (AST-586).

4. Rewrite `update_dtask` body:
   - Keep `row = database.get_dispatch_task(task_id)`; 404 when missing.
   - Add `"task_key"` to `allowed` set (~line 874).
   - **AUTO guard:** when `row.get("auto_mode")` is truthy **and** the request body contains any key other than `"auto_mode"` alone, return `400` with `{"error": "Turn AUTO mode off before editing this row"}`. (Table toggle continues to send only `{auto_mode: …}` and is unaffected.)
   - When `"task_key" in data`:
     - Resolve effective `trigger_state` as `data.get("trigger_state", row.get("trigger_state"))`.
     - Call `_dispatch_task_key_trigger_error(data["task_key"], effective_trigger_state)`; non-`None` → `400` with `{"error": msg}`.
     - `defaults = dispatch_task_admin_defaults(data["task_key"])`.
     - Set `updates["task_key"] = data["task_key"].strip()`.
     - Set `updates["entity_type"] = defaults["entity_type"]`.
     - Set `updates["sort_by"] = defaults["sort_by"]`.
     - Set `updates["batch_call_mode"] = defaults["batch_call_mode"]`.
   - Keep existing field parsing for `min_count`, `batch_size`, `auto_mode`, `debug`, `skip_cache`, `freq_hrs`, `max_runs`, `score_floor`, `trigger_state`.
   - When building `trigger_state` / `score_floor`, if `"task_key" in updates`, use `updates["task_key"]` for `is_scored` side effects only when needed; `is_scored` remains driven by **effective** `trigger_state` via `dispatch_claim_uses_score_floor` (unchanged).
   - In the `except` UNIQUE branch (~lines 901–910), set `tk = updates.get("task_key", (row or {}).get("task_key", ""))` and `ts = updates.get("trigger_state", (row or {}).get("trigger_state", ""))` so the 409 message reflects the **attempted** triple.

5. Do **not** change `POST /api/admin/dispatch_tasks`, list endpoints, or scheduler run/stop routes in this stage.

---

## Stage 2: Scheduled Actions UI — Edit Task Task dropdown and AUTO block

**Done when:** Non-AUTO rows open **Edit Task** with a Task dropdown (current key selected); changing Task updates read-only Entity Type and `is_scored` visibility only — **Input State** and **Score Floor** values stay unless Susan edits them; Save PUT includes `task_key`; AUTO rows cannot open the edit modal; Add Task, run/stop, filters, grouping, and Stop All behave as before AST-735/751.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, add a small helper above the component (or inline in `openEdit` guard):

   ```ts
   function taskKeyChangePatch(form: typeof initialForm, key: string, cfg: TaskKeyMeta | undefined) {
     return {
       ...form,
       task_key: key,
       entity_type: cfg?.entity_type || "",
       is_scored: !!cfg?.is_scored,
       // deliberately omit trigger_state and score_floor — Susan keeps current values
     }
   }
   ```

   (Use the actual `form` state shape; no separate type export required.)

2. Change `openEdit` (~line 488): at the top, if `row.auto_mode` is truthy, call `setToast({ text: "Turn AUTO mode off before editing this row", variant: "error" })` and **return** without opening the modal.

3. Change `ScheduledPhaseTable` row `onClick` (~line 134): pass `openEdit` only when `!row.auto_mode`; when `row.auto_mode`, set `style={{ cursor: "default" }}` and omit `onClick` (or no-op). Keep AUTO badge click propagation unchanged.

4. In the Add/Edit modal body (~lines 738–763), replace `{!editRow && (` wrapper so the **Task** row renders for **both** add and edit:
   - **Candidate** read-only row stays **add-only** (`!editRow`).
   - **Task** `<select>` renders always; `value={form.task_key}`; options from `Object.keys(allTaskKeys).sort()` (same as add).
   - **onChange for edit:** call `setForm(f => taskKeyChangePatch(f, key, allTaskKeys[key]))`.
   - **onChange for add:** keep existing behavior (also sets `trigger_state` and `score_floor: "1.00"` from catalog defaults).

5. In `handleSave` edit branch (~lines 511–524), add `task_key: form.task_key` to the JSON body (after `trigger_state`, before numeric fields). Do not add candidate_id (out of scope).

6. Do **not** change filter bar, section grouping, column freeze, run/stop handlers, or Add Task POST body beyond what is required above.

---

## Self-Assessment

**Scope:** `Single-Component` — touches Scheduled Actions React page, one admin PUT handler, and the dispatch_task update column whitelist only.

**Conf:** `high` — the gap is localized (hidden Task select + omitted PUT field); Add Task and POST validation patterns already exist to mirror.

**Risk:** `Medium` — wrong UNIQUE or AUTO guard could block legitimate saves or allow inconsistent dispatch rows; mitigated by explicit validation helper and UI/server AUTO symmetry.

## Code rules check

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses `dispatch_task_admin_defaults` and existing PUT/POST error shapes; one validation helper shared by PUT path. |
| §2.1 config | Schedulable keys and entity/trigger defaults from config via existing helpers — no inline key sets. |
| §2.4 batch | No batch claim changes. |
| §2.6 state machine | Validation reads `JOB_STATES` / `COMPANY_STATES` registries only — no new transitions. |
| §3.3 imports | API changes stay in `src/ui/api/` importing config/utils; data layer whitelist only. |
| §3.5 naming | Follows `_dispatch_*` / `update_dtask` conventions. |

No conflicts requiring plan revision.

---

## Review (Radia)

**Built:** `origin/sub/AST-763/AST-773-edit-modal-task-key-and-api` @ `d811040` (diff `origin/dev...origin/sub/AST-763/AST-773-edit-modal-task-key-and-api`)

| Axis | Rating |
|------|--------|
| Plan fidelity | **A** — Stages 1–2 match plan: PUT whitelist + `_dispatch_task_key_trigger_error`, derived columns, AUTO guard, 409 triple fix; edit Task `<select>`, `taskKeyChangePatch`, AUTO toast/row block, `task_key` in PUT body. |
| Code rules | **A** — §3.3 layer compliance; config-driven validation via existing helpers; no silent failures or `print()`. |
| Boundaries | **B** — AST-750 `DISPATCH_SCORE_FLOOR_*` on three-dot diff via merge history; not in AST-773 plan and UI still hardcodes `scoreFloorOptions`. |

**Product:** Edit flow delivers the parent epic goal — Susan can retarget `task_key` on non-AUTO rows with preserved Input State / Score Floor; server rejects invalid combos and AUTO edits symmetrically with the UI.

**Tests:** Betty `merge-tests` — `TestAst773UpdateDispatchTaskTaskKey` (5) + frontend `AST-773 edit modal task_key` (5); bible rows in `api_admin.md` / `pages.md`.

### Findings

**discuss — sibling bleed at merge-child**

`src/utils/config.py` adds `DISPATCH_SCORE_FLOOR_VALUES` / `dispatch_score_floor_option_labels()` (AST-750) on the three-dot diff but not from Katherine’s `code(AST-773)` commits — landed via `merge AST-750` ancestry. No `/dispatch_tasks/score_floor_options` on this ref; `AdminScheduledActions.tsx` still uses hardcoded `scoreFloorOptions` (1.00–10.00). Confirm at **merge-child**: strip from sub rollup or defer full AST-750 landing on `ftr/AST-763`.

**advisory — trigger_state-only PUT**

`_dispatch_task_key_trigger_error` runs only when `"task_key" in data`. PUT with `trigger_state` alone does not re-validate against the row’s existing `task_key` (pre-PUT behavior; plan scoped validation to task_key changes). Optional hardening in a follow-up if Susan wants parity with POST.

**advisory — task retarget UX edge**

`taskKeyChangePatch` updates `is_scored` from catalog while preserving `trigger_state`. Retargeting to a scored catalog key with a non-scored trigger_state can briefly show Score Floor until save; server coerces via `dispatch_claim_uses_score_floor(trigger_state)` — acceptable given plan’s “preserve Input State” decision.

---

## Resolution (Katherine — 2026-06-23)

**Review Posted @ `9219d8c`:** Radia **A/A** plan fidelity and code rules; no **fix-now** items.

| Finding | Resolution |
|---------|------------|
| **discuss — AST-750 config bleed** | **Defer strip to `merge-child` on `ftr/AST-763`.** `DISPATCH_SCORE_FLOOR_VALUES` / `dispatch_score_floor_option_labels()` arrived via merge ancestry, not AST-773 product commits. This ref has no `/dispatch_tasks/score_floor_options` route; UI still hardcodes `scoreFloorOptions`. Orphan constants are harmless until AST-750 lands on `ftr` or Chuckles strips at rollup. |
| **advisory — trigger_state-only PUT** | No change — pre-PUT behavior; plan scoped validation to `task_key` changes. |
| **advisory — task retarget UX edge** | No change — server coercion on save matches plan preserve-Input-State decision. |

**§9a dry-run:** `origin/sub/AST-763/AST-773-edit-modal-task-key-and-api` merges cleanly into `origin/dev` and `origin/ftr/AST-763-edit-modal-task-key`.

**Shipped product:** `code(AST-773)` @ `03b8535` + `7b024e5`; tests @ `d811040`; Radia review doc @ `9219d8c`.

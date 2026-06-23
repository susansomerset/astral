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

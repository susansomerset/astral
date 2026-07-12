# AST-875 — Template candidate config and dispatch-task set upsert (Add “set dispatch tasks” button)

**Linear:** [AST-875](https://linear.app/astralcareermatch/issue/AST-875/template-candidate-config-and-dispatch-task-set-upsert-add-set)
**Parent:** [AST-873](https://linear.app/astralcareermatch/issue/AST-873/add-set-dispatch-tasks-button)
**Publish ref:** `origin/sub/AST-873/AST-875-template-dispatch-task-set-upsert`

Define the template candidate id in product config (default `somerset`) and implement the data + admin API path that mirrors that candidate’s live `dispatch_task` set onto a target candidate: upsert matching `(task_key, trigger_state)` rows, prune extras, copy schedule metadata including `auto_mode`, and clear `last_run_at` / `batch_id` on every target row. Expose admin endpoints for per-candidate dispatch-task counts and for running the set. Does not build Manage Candidates UI (AST-876) and does not enqueue or run dispatcher batches.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `ASTRAL_CONFIG["template_candidate_id"] = "somerset"`; helper `template_candidate_id()` | utils |
| `src/data/database.py` | Add `list_dispatch_tasks_for_candidate`, `count_dispatch_tasks_by_candidate`, `delete_dispatch_task`, `set_dispatch_tasks_from_template_rows` (single-transaction upsert+prune+clear run fields) | data |
| `src/core/dispatcher.py` | Thin wrappers + `set_candidate_dispatch_tasks_from_template(target_candidate_id)` that resolves template from config, validates candidates, calls data | core |
| `src/ui/api/api_admin.py` | `GET /api/admin/dispatch_tasks/counts`; `POST /api/admin/dispatch_tasks/set_from_template` — call core only (no new `database` imports on these paths) | ui |

**Out of scope:** `AdminManageCandidates.tsx` / Set button UI (AST-876); Scheduled Actions redesign; copying companies/jobs/ledger/prompts/profile; dispatcher claim/eligibility changes beyond the natural effect of written rows; Betty tests (qa-child).

---

## Stage 1: Template candidate config

**Done when:** `template_candidate_id()` returns `"somerset"` from `ASTRAL_CONFIG` with no env lookup and no hardcoded `"somerset"` outside config.

1. In `src/utils/config.py`, inside `ASTRAL_CONFIG`, in the Dispatcher section (after `dispatch_timeout_seconds` / near other dispatcher keys), add:

   ```python
   # Candidate whose live dispatch_task rows are the default schedule template
   # for Manage Candidates "Set dispatch tasks" (AST-873 / AST-875).
   "template_candidate_id": "somerset",
   ```

2. In `src/utils/config.py`, after `ASTRAL_CONFIG` (near other small getters such as `get_auth_config`), add:

   ```python
   def template_candidate_id() -> str:
       """Product template candidate for dispatch_task set-from-template (AST-875)."""
       return str(ASTRAL_CONFIG["template_candidate_id"]).strip()
   ```

   ⚠️ **Decision:** Key lives on `ASTRAL_CONFIG` (dispatcher product behavior), not `ADMIN_CONFIG`. UI reads the result only via the set API (which resolves the template server-side); the frontend must not hardcode `somerset`.

**Commit message:** `code(AST-875): stage 1 — template_candidate_id in ASTRAL_CONFIG`

---

## Stage 2: Data-layer list / count / delete / set-from-rows

**Done when:** For a given target id, calling `set_dispatch_tasks_from_template_rows` with a list of template row dicts leaves the target’s `dispatch_task` set equal to the template’s `(task_key, trigger_state)` set with schedule columns copied, `last_run_at` and `batch_id` NULL on every surviving target row, and extras deleted — all in one SQLite transaction. Counts and per-candidate list helpers work via SQL `WHERE candidate_id = ?` / `GROUP BY`.

1. In `src/data/database.py`, immediately after `list_dispatch_tasks`, add:

   ```python
   def list_dispatch_tasks_for_candidate(candidate_id: str) -> List[Dict[str, Any]]:
       """All dispatch_task rows for one candidate_id (any order stable by id ASC)."""
   ```

   Implementation: `_ensure_dispatch_task_schema`, then
   `SELECT * FROM dispatch_task WHERE candidate_id = ? ORDER BY id ASC`, return `[_row_to_dict(r) for r in rows]`. Empty / blank `candidate_id` → `[]` without querying.

2. In the same file, add:

   ```python
   def count_dispatch_tasks_by_candidate() -> Dict[str, int]:
       """Map candidate_id → row count for all dispatch_task rows."""
   ```

   Implementation: `SELECT candidate_id, COUNT(*) AS n FROM dispatch_task GROUP BY candidate_id`, build `{str(cid): int(n), ...}`. Candidates with zero rows are omitted (callers treat missing as 0).

3. In the same file, add:

   ```python
   def delete_dispatch_task(task_id: int) -> None:
       """Delete one dispatch_task by primary key. No-op if missing."""
   ```

   Implementation: `DELETE FROM dispatch_task WHERE id = ?` inside `_run_with_retry` / connection pattern used by `update_dispatch_task`.

4. Define the schedule-copy column set as a module-level frozenset next to `_DISPATCH_TASK_UPDATE_COLS`:

   ```python
   _DISPATCH_TASK_TEMPLATE_COPY_COLS = frozenset({
       "task_key", "entity_type", "trigger_state", "sort_by", "batch_call_mode",
       "freq_hrs", "min_count", "batch_size", "auto_mode", "debug", "skip_cache",
       "max_runs", "score_floor",
   })
   ```

   Do **not** copy `id`, `candidate_id`, `last_run_at`, `batch_id`, or `updated_at`.

5. Add `set_dispatch_tasks_from_template_rows(target_candidate_id: str, template_rows: List[Dict[str, Any]]) -> Dict[str, int]`:

   - Strip / validate `target_candidate_id` non-empty; raise `ValueError` if blank.
   - Open one connection; `_ensure_dispatch_task_schema`; begin work on that connection only (no nested `_run_with_retry` per row).
   - Load existing target rows: `SELECT * FROM dispatch_task WHERE candidate_id = ?`.
   - Index target rows by `(task_key, trigger_state)` where both are stripped strings (`trigger_state` empty string if NULL).
   - Build `template_keys` the same way from `template_rows`. If a template row is missing `task_key` or has blank `task_key`, raise `ValueError`.
   - For each template row:
     - Build assign dict from `_DISPATCH_TASK_TEMPLATE_COPY_COLS` present on the template row (use template values; coerce `auto_mode` / `debug` / `skip_cache` / `batch_call_mode` with `int(bool(...))` or `int(value or 0)` matching how `update_dispatch_task` / inserts store integers).
     - Always set `last_run_at = None`, `batch_id = None`, `updated_at = _utc_now()`, `candidate_id = target_candidate_id`.
     - If key exists on target: `UPDATE` all assign + clear columns `WHERE id = ?`; count `updated`.
     - Else: `INSERT` with those columns (include `candidate_id`); do **not** set `last_run_at` to `_utc_now()` (unlike `save_dispatch_task`); count `inserted`.
   - For each target row whose key is **not** in `template_keys`: `DELETE FROM dispatch_task WHERE id = ?`; count `deleted`.
   - `conn.commit()`; return `{"inserted": …, "updated": …, "deleted": …, "count": <final SELECT COUNT(*) for target>}`.

   ⚠️ **Decision:** Dedicated transactional function — do **not** compose `save_dispatch_task` + `update_dispatch_task`. `save_dispatch_task` stamps `last_run_at` to now on insert, which would violate AC3. Also `_DISPATCH_TASK_UPDATE_COLS` does not include `batch_id`; clearing run fields belongs in this SQL path rather than widening the general update whitelist for unrelated callers.

   ⚠️ **Decision:** Empty `template_rows` is valid and deletes all target dispatch_task rows (exact match to an empty template set).

**Commit message:** `code(AST-875): stage 2 — dispatch_task set-from-template data path`

---

## Stage 3: Core orchestration wrappers

**Done when:** `set_candidate_dispatch_tasks_from_template("some-target")` reads the template id from config, 404-style errors if template or target candidate is missing, copies via the data function, and never calls `run_task` / scheduler start helpers.

1. In `src/core/dispatcher.py`, extend the existing dispatch_task wrapper block (near `save_dispatch_task` / `update_dispatch_task`) with:

   - `list_dispatch_tasks_for_candidate(candidate_id)` → `database.list_dispatch_tasks_for_candidate`
   - `count_dispatch_tasks_by_candidate()` → `database.count_dispatch_tasks_by_candidate`
   - `delete_dispatch_task(task_id)` → `database.delete_dispatch_task`

2. Add:

   ```python
   def set_candidate_dispatch_tasks_from_template(target_candidate_id: str) -> Dict[str, Any]:
   ```

   Steps:

   1. `target = str(target_candidate_id or "").strip()`; if empty → raise `ValueError("candidate_id is required")`.
   2. `from src.utils.config import template_candidate_id` (or top-level import if already importing config symbols in this module — match existing import style).
   3. `template_id = template_candidate_id()`; if empty → raise `ValueError("ASTRAL_CONFIG template_candidate_id is empty")`.
   4. `from src.data import database` (already imported in this module as used by other wrappers).
   5. If `database.get_candidate(template_id)` is None → raise a dedicated error the API can map to 404, e.g. `LookupError(f"Template candidate not found: {template_id}")`.
   6. If `database.get_candidate(target)` is None → `LookupError(f"Candidate not found: {target}")`.
   7. `template_rows = database.list_dispatch_tasks_for_candidate(template_id)`.
   8. `stats = database.set_dispatch_tasks_from_template_rows(target, template_rows)`.
   9. Return `{"candidate_id": target, "template_candidate_id": template_id, **stats}`.
   10. Do **not** call `run_task`, `drain_task`, `cancel_task`, or any ledger/batch claim helper.

   ⚠️ **Decision:** Setting the template candidate onto itself is allowed and must be idempotent (upsert all keys, delete none that remain in template, clear run fields). Useful for operators resetting `last_run_at` / `batch_id`.

   ⚠️ **Decision:** Do **not** require the target candidate’s Anthropic API key for set. `_candidate_dispatch_api_key_error` stays on Run/Auto only. Set may copy `auto_mode=1` rows; AUTO/Run still refuse at execution time if the key is missing.

**Commit message:** `code(AST-875): stage 3 — core set_candidate_dispatch_tasks_from_template`

---

## Stage 4: Admin API — counts + set_from_template

**Done when:** An admin can `GET /api/admin/dispatch_tasks/counts` and receive a JSON object of per-candidate counts, and `POST /api/admin/dispatch_tasks/set_from_template` with `{"candidate_id": "<target>"}` performs the upsert+prune without starting a dispatch run. Routes are registered **before** `/dispatch_tasks/<int:task_id>` so Flask does not treat `counts` / `set_from_template` as integer ids.

1. In `src/ui/api/api_admin.py`, import from `src.core.dispatcher` (alongside existing `list_dispatch_tasks`, `save_dispatch_task`, `update_dispatch_task`):

   - `count_dispatch_tasks_by_candidate`
   - `set_candidate_dispatch_tasks_from_template`

   Do **not** add new direct `database.*` calls on these two endpoints (layer §3.3 for new paths).

2. Register **after** the existing `/dispatch_tasks/state_options` route and **before** `POST /dispatch_tasks` / `PUT /dispatch_tasks/<int:task_id>`:

   ```python
   @admin_bp.route("/dispatch_tasks/counts")
   @require_admin
   def dispatch_task_counts():
       """Per-candidate dispatch_task row counts for Manage Candidates (AST-875)."""
       return jsonify({"counts": count_dispatch_tasks_by_candidate()})
   ```

   Response shape (exact):

   ```json
   { "counts": { "somerset": 42, "other": 3 } }
   ```

   Missing candidate keys mean count `0` for AST-876.

3. Register:

   ```python
   @admin_bp.route("/dispatch_tasks/set_from_template", methods=["POST"])
   @require_admin
   def set_dispatch_tasks_from_template():
   ```

   - Parse JSON body; require `candidate_id` (non-empty string after strip); else `400` `{"error": "candidate_id is required"}`.
   - Call `set_candidate_dispatch_tasks_from_template(candidate_id)`.
   - On `LookupError` → `404` `{"error": str(exc)}`.
   - On `ValueError` → `400` `{"error": str(exc)}`.
   - On success → `200` with the core return dict, e.g.:

     ```json
     {
       "candidate_id": "other",
       "template_candidate_id": "somerset",
       "inserted": 5,
       "updated": 10,
       "deleted": 2,
       "count": 15
     }
     ```

   - Must **not** call `run_task` / start scheduler threads.

4. Leave existing create/update/list/run/stop/kill dispatch_task endpoints behavior unchanged.

**Commit message:** `code(AST-875): stage 4 — admin counts and set_from_template endpoints`

---

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree sub line; publish each stage to `origin/sub/AST-873/AST-875-template-dispatch-task-set-upsert`.
- Do not add files, endpoints, or config keys not listed above.
- Do not edit `AdminManageCandidates.tsx` or other AST-876 UI.
- Do not edit `tests/` or test-bible paths.
- If `save_dispatch_task` / schema / unique key assumptions have drifted from this plan — stop and comment on **AST-873** with the Stage N blocked template.

---

## Self-Assessment

**Scope:** Single-Component — config one-liner, focused `dispatch_task` data helpers, thin core wrapper, two admin routes on the existing dispatch_tasks admin surface.

**Conf:** high — unique key, schedule columns, and admin API patterns already exist; the only non-mechanical piece is avoiding `save_dispatch_task`’s `last_run_at=now` insert behavior via a dedicated transactional writer.

**Risk:** Medium — a bug in prune/upsert could delete or overwrite a candidate’s live schedule (including AUTO flags); wrong template id would propagate Somerset’s set incorrectly. Mitigated by requiring both candidate rows to exist and by not touching Run/claim paths.

---

## Rules self-review

| Rule | Status |
|------|--------|
| §1.3 DRY | Reuses existing schema + unique key; one transactional writer instead of duplicating insert column lists across API create |
| §1.4 / §2.1 config | Template id only in `ASTRAL_CONFIG`; no hardcoded `somerset` in core/ui |
| §2.4 batch processing | Set does not claim entities or invent `batch_id` values; clears `batch_id` on target rows only |
| §2.6 state machine | No entity state transitions |
| §3.3 imports | New API paths call core only; data stays under core |
| §3.5 naming | Routes under existing `/api/admin/dispatch_tasks/*` |

## Review (build stub)

**Built:** `astral-AST-873` @ `8bcd5f4` on `origin/sub/AST-873/AST-875-template-dispatch-task-set-upsert`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `6195c22` | Plan doc |
| 1 | `5141062` | `template_candidate_id` in ASTRAL_CONFIG |
| 2 | `200976d` | list/count/delete + set-from-template data path |
| 3 | `112c8cc` | core `set_candidate_dispatch_tasks_from_template` |
| 4 | `8bcd5f4` | admin `counts` + `set_from_template` endpoints |

**Verify:** `python3 -m py_compile` on `config.py`, `database.py`, `dispatcher.py`, `api_admin.py` — pass.

**Note for Betty:** new admin contracts `GET /api/admin/dispatch_tasks/counts` and `POST /api/admin/dispatch_tasks/set_from_template`; transactional upsert+prune clears `last_run_at`/`batch_id`; no UI (AST-876).


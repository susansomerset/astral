# AST-1618 — Persist chosen entity_type on admin create/update

**Linear:** [AST-1618](https://linear.app/astralcareermatch/issue/AST-1618)
**Parent:** [AST-1616](https://linear.app/astralcareermatch/issue/AST-1616) — Make all fields on Add Dispatch Task modal editable
**Publish ref:** `sub/AST-1616/AST-1618-persist-entity-type-admin`

Own the admin API + data insert path so create/update can persist an explicit `entity_type`, validate `trigger_state` against that entity (not only the task-key catalog default), and store `sort_by` for the **chosen** entity + trigger. Does not own the React Entity Type control (AST-1619). After this lands, curl/API can set `entity_type` before the UI ships.

## Explicit scope gate

Ticket **## Scope** covers only:

- `src/ui/api/api_admin.py` — create/update accept `entity_type`; trigger validation uses submitted entity; recompute `sort_by` on entity/trigger/`task_key` changes.
- `src/data/database.py` — `save_dispatch_task` uses caller `entity_type` and derives `sort_by` for that entity + trigger when provided.

No other files. No React. No scheduler/claim runtime changes beyond persisting `entity_type` / `sort_by` on admin saves. Mailbox null-entity path when `entity_type` omitted stays intact.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | In `save_dispatch_task`, when caller supplies a non-empty `entity_type`, keep it and set `sort_by` via `_dispatch_sort_by_for(entity_type, effective_trigger)` instead of always using catalog `defaults["sort_by"]`; mailbox keys keep `sort_by=None` | data |
| `src/ui/api/api_admin.py` | Pass request `entity_type` on create; extend `_dispatch_task_key_trigger_error` with optional entity override; allow `entity_type` on update; recompute `sort_by` when entity/trigger/`task_key` change; reject unknown entity types | ui |

## Stage 1: `save_dispatch_task` honors caller entity_type for sort_by

**Done when:** Calling `save_dispatch_task(..., entity_type=<non-catalog>, trigger_state=<valid for that entity>)` inserts a row whose `entity_type` matches the argument and whose `sort_by` equals `_dispatch_sort_by_for` for that pair. Omitting `entity_type` still inserts the catalog default entity + catalog-derived `sort_by`. Mailbox task keys with omitted `entity_type` still insert `entity_type`/`trigger_state`/`sort_by` from `METEORITE_EMAIL_MAILBOX_CONFIG` (null entity, null sort).

1. In `src/data/database.py` `save_dispatch_task`, before filling defaults, capture whether the caller passed a non-empty entity:

   ```python
   caller_entity = str(entity_type).strip() if (entity_type and str(entity_type).strip()) else None
   ```

2. Keep the existing mailbox / non-mailbox fill of `entity_type` and `trigger_state` from `METEORITE_EMAIL_MAILBOX_CONFIG` / `defaults` when those fields are empty after strip (do not change that control flow).

3. Replace the unconditional `sort_by = defaults["sort_by"]` with:

   - If `is_meteorite_email_mailbox_task_key(tk)`: `sort_by = defaults["sort_by"]` (always `None` for mailbox — do **not** call `_dispatch_sort_by_for` even if caller passed an entity).
   - Elif `caller_entity` is not `None`: late-import `_dispatch_sort_by_for` from `src.utils.config` (same late-import style already used in this function for mailbox helpers) and set `sort_by = _dispatch_sort_by_for(entity_type, trigger_state)` using the **post-fill** `entity_type` / `trigger_state` values that will be inserted. On `KeyError`, raise `ValueError` with the KeyError message (data raises; API maps).
   - Else: `sort_by = defaults["sort_by"]` (current catalog behavior).

4. Leave `batch_call_mode = defaults["batch_call_mode"]` unchanged. Leave `update_dispatch_task` / `_DISPATCH_TASK_UPDATE_COLS` unchanged (`entity_type` and `sort_by` are already whitelisted).

⚠️ **Decision:** Sort recompute for create lives in `save_dispatch_task` when the caller supplied `entity_type`, matching parent Technical scope. Update-path sort recompute stays in the API (Stage 2) because `update_dispatch_task` is a column-whitelist passthrough with no defaults logic.

## Stage 2: Admin create/update accept entity_type + validate/sort against it

**Done when:** `POST /api/admin/dispatch_tasks` with a valid body `entity_type` stores that value; `PUT` with `entity_type` updates the row without requiring a `task_key` change; POST/PUT with an entity+trigger pair that is invalid for that entity's registry returns **400** with a clear error; when saved `entity_type` differs from the task-key catalog default, stored `sort_by` matches `_dispatch_sort_by_for(chosen_entity, trigger)`. Omitting `entity_type` on create keeps today's catalog-default behavior. Mailbox create with omitted `entity_type` still succeeds.

### 2a. `_dispatch_task_key_trigger_error` — optional entity override

1. Change signature to:

   ```python
   def _dispatch_task_key_trigger_error(
       task_key: str,
       trigger_state: str | None,
       entity_type: str | None = None,
   ) -> str | None:
   ```

2. Keep the existing early returns for blank `task_key`, retired keys, and mailbox (null/empty trigger only). Mailbox path ignores `entity_type` override (still returns on non-empty trigger).

3. After the mailbox early-return block, resolve entity type as:

   - If `entity_type` is not `None` and `str(entity_type).strip()` is non-empty: `et = str(entity_type).strip()`. If `et not in ENTITY_TYPES`, return `f"unsupported entity_type {et!r}"` (do not fall through to catalog).
   - Else: keep current `et = _dispatch_entity_type_for_task_key(tk)` / KeyError messaging for unknown/`unsupported entity_type` task keys.

4. Keep the rest of the function (require non-empty trigger for non-mailbox, registry lookup via `dispatch_entity_state_registry(et)`, hop-label parsing, chain hop match) unchanged — it already validates against `et`, so the override is enough for AC5.

### 2b. `create_dtask`

1. After the retired-key check (and before score_floor / auto_mode checks is fine), if `"entity_type" in data` and the value is not `None`:

   - `raw_et = str(data.get("entity_type") or "").strip()`
   - If `raw_et == ""`: return 400 `{"error": "entity_type must be non-empty when provided"}`.
   - If `raw_et not in ENTITY_TYPES`: return 400 `{"error": f"unsupported entity_type {raw_et!r}"}`.
   - Else set `submitted_entity = raw_et`.
   - If `"entity_type"` absent or value is `None`: `submitted_entity = None` (omit → catalog / mailbox defaults in save).

2. Change the trigger validation call to:

   ```python
   tk_err = _dispatch_task_key_trigger_error(
       data.get("task_key", ""),
       data.get("trigger_state"),
       entity_type=submitted_entity,
   )
   ```

3. Pass `entity_type=submitted_entity` into `save_dispatch_task(...)` (positional/keyword alongside existing args). Do not pass `sort_by` from the API on create — Stage 1 owns insert sort derivation.

### 2c. `update_dtask`

1. Add `"entity_type"` to the `allowed` set.

2. Resolve effective fields **before** building catalog defaults on `task_key` change:

   - `effective_task_key = (data["task_key"] if "task_key" in data else row.get("task_key") or "").strip()` (same strip discipline as today for new keys).
   - `effective_trigger_state = data.get("trigger_state", row.get("trigger_state"))`.
   - Entity resolution:
     - If `"entity_type" in data`: strip to `submitted_et`. Empty → 400 `entity_type must be non-empty when provided`. Not in `ENTITY_TYPES` → 400 `unsupported entity_type …`. Use `submitted_et` as `effective_entity_type`.
     - Elif `"task_key" in data`: `effective_entity_type = dispatch_task_admin_defaults(effective_task_key, trigger_state=effective_trigger_state)["entity_type"]` (catalog default for the new key — current behavior when client does not send entity).
     - Else: `effective_entity_type = row.get("entity_type")`.

3. Replace the two existing `_dispatch_task_key_trigger_error(...)` call sites (task_key branch and trigger_state-only branch) with a **single** validation when any of `task_key`, `trigger_state`, or `entity_type` is present in `data`:

   ```python
   tk_err = _dispatch_task_key_trigger_error(
       effective_task_key,
       effective_trigger_state,
       entity_type=effective_entity_type,
   )
   ```

   Skip this call only when none of those three keys appear in `data` (pure schedule-field updates).

4. When `"task_key" in data`: keep setting `updates["task_key"]`, `updates["batch_call_mode"]` from `dispatch_task_admin_defaults(...)`. Set `updates["entity_type"]` to `effective_entity_type` (client override if provided, else catalog). Do **not** set `updates["sort_by"]` from `defaults["sort_by"]` here — step 6 owns sort.

5. When `"entity_type" in data` (with or without `task_key`): `updates["entity_type"] = effective_entity_type`.

6. If any of `task_key`, `trigger_state`, or `entity_type` is in `data` **and** the effective task_key is **not** a mailbox key (`not is_meteorite_email_mailbox_task_key(effective_task_key)`):

   - Import/use `_dispatch_sort_by_for` (add to the existing `src.utils.config` import list next to `_dispatch_entity_type_for_task_key`).
   - Set `updates["sort_by"] = _dispatch_sort_by_for(effective_entity_type, effective_trigger_state)` after normalizing trigger the same way insert does (use the string trigger that will be stored; for hop labels, pass the full `effective_trigger_state` string into `_dispatch_sort_by_for` exactly as `dispatch_task_admin_defaults` does today with `effective_ts`).
   - On `KeyError`: return 400 `{"error": str(exc)}`.

   For mailbox keys: do not write `sort_by` on these field changes (leave existing row sort / null alone unless some other allowed field path already touched it — do not invent mailbox sort).

7. Keep the existing loop that copies other `allowed` fields into `updates` (`min_count`, `batch_size`, flags, `freq_hrs`, `trigger_state`, `score_floor`). Ensure `entity_type` is **not** double-handled inside that loop in a way that overwrites step 5 with a wrong cast — either handle `entity_type` only in steps 4–5, or in the loop as `updates[k] = str(data[k]).strip()` when `k == "entity_type"` **after** validation (same final value as `effective_entity_type`).

8. Keep AUTO-edit guard, uniqueness 409 mapping, and `@require_admin` unchanged.

⚠️ **Decision:** On `task_key` change without client `entity_type`, still apply catalog `entity_type` (preserves today's Edit-Task behavior). On `task_key` change **with** client `entity_type`, prefer the client value (parent Technical scope). Sort always follows the **effective** entity + trigger after that resolution.

⚠️ **Decision:** Recompute `sort_by` on update whenever entity, trigger, or task_key is in the body (non-mailbox), even if the computed sort string equals the previous value — simpler than diffing; `update_dispatch_task` already rewrites `updated_at`.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; push each to `origin/sub/AST-1616/AST-1618-persist-entity-type-admin`.
- Do not touch `src/ui/frontend/**`, scheduler claim paths, or files outside the Files Changed table.
- If a referenced helper signature has drifted, stop and comment on **AST-1616** with the Stage blocked template — do not invent a parallel sort registry.

## Estimate

Confirm Chuckles estimate: 3 — agree

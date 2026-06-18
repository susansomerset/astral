# Task grouping metadata storage and seed (Organizing Tasks)

**Linear:** [AST-738](https://linear.app/astralcareermatch/issue/AST-738/task-grouping-metadata-storage-and-seed-organizing-tasks)  
**Parent:** [AST-734](https://linear.app/astralcareermatch/issue/AST-734/organizing-tasks)  
**Publish ref:** `sub/AST-734/AST-738-task-grouping-metadata-storage-and-seed`

Susan wants task grouping and ordering editable in admin without redeploying config. This ticket adds four global-per-`task_key` fields on `agent_task` rows (`task_group_order`, `task_group_name`, `task_seq`, `task_name`), seeds them once from today’s `TASK_CONFIG` `phase` / `seq`, and wires Manage Tasks API save/load paths to read and write DB values only. React list layout and Scheduled Actions grouping are **AST-739**; removing `phase` / `seq` from config is **AST-740**.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add four columns to `agent_task`; one-time seed migration; extend `save_agent_task` / `_save_agent_task_on_connection` / `sync_agent_tasks` / copy-upsert | data |
| `src/ui/api/api_admin.py` | PUT/GET `/tasks/<task_key>` and `_enrich_tasks` surface DB grouping fields; backward-compat `phase`/`seq` from DB | ui |

**Out of scope (this ticket):** `src/ui/frontend/**` (AST-739), `src/utils/config.py` phase/seq removal (AST-740), `tests/**` (Betty after Code Complete).

## Stage 1: `agent_task` schema columns

**Done when:** Fresh and migrated databases have four new columns on `agent_task`; `_ensure_agent_task_schema` is idempotent; table header inventory in `database.py` documents the columns.

1. In `src/data/database.py`, update the **`agent_task` header inventory** (top-of-file table list) to append: `task_group_order TEXT NOT NULL DEFAULT ''`, `task_group_name TEXT NOT NULL DEFAULT ''`, `task_seq REAL NOT NULL DEFAULT 999.0`, `task_name TEXT NOT NULL DEFAULT ''`.
2. In `_ensure_agent_task_schema`, after existing column migrations and **before** `_apply_ast469_select_job_page_run_next_migration(conn)`, add idempotent `ALTER TABLE agent_task ADD COLUMN …` for each of the four columns if missing (follow the existing `run_next` / `cache_prompt_b` pattern: refresh `cols` set after each add).
3. Do not change the versioned-row semantics for prompt segments.

⚠️ **Decision:** `task_seq` is `REAL` (float) with default `999.0` so unseeded rows sort last consistently with today’s UI `(seq ?? 999)` fallback.

## Stage 2: One-time seed from `TASK_CONFIG`

**Done when:** After first boot on an existing DB, every `agent_task` row with `current = 1` has seeded grouping metadata copied from config; re-running schema ensure does not overwrite operator edits.

1. In `src/data/database.py`, add `_seed_task_grouping_metadata_from_config(conn: sqlite3.Connection) -> None`:
   - Import inside the function (data → utils allowed): `from src.utils.config import TASK_CONFIG, get_task_keys`.
   - Guard: `SELECT COUNT(*) FROM agent_task WHERE current = 1 AND task_group_name != ''`. If count > 0, **return immediately** (already seeded or operator-edited).
   - For each `task_key` in `get_task_keys()`:
     - Load `cfg = TASK_CONFIG.get(task_key) or {}`.
     - `phase = (cfg.get("phase") or "").strip()`
     - `seq_raw = cfg.get("seq")`
     - Compute seed values:
       - `task_group_name = phase if phase else "(unassigned)"`
       - `task_group_order = phase if phase else "ZZZ"`
       - `task_seq = float(seq_raw) if seq_raw is not None else 999.0`
       - `task_name = task_key`
     - `UPDATE agent_task SET task_group_order = ?, task_group_name = ?, task_seq = ?, task_name = ? WHERE task_key = ? AND current = 1` with those values.
   - For any `current = 1` row whose `task_key` is **not** in `get_task_keys()` (orphan dispatch-only keys should not exist on agent_task; if present): set `task_group_name = "(unassigned)"`, `task_group_order = "ZZZ"`, `task_seq = 999.0`, `task_name = task_key`.
2. Add `_apply_ast738_task_grouping_metadata_seed(conn)` that calls `_seed_task_grouping_metadata_from_config(conn)`.
3. At end of `_ensure_agent_task_schema`, after column adds and existing `_apply_ast*` migrations, call `_apply_ast738_task_grouping_metadata_seed(conn)`.

⚠️ **Decision:** Initial `task_group_order` equals config `phase` string (not just the letter prefix). Phase labels already sort correctly (`"A. Candidate Context"` before `"A. Candidate Intake"` before `"B. …"`). Susan can split or rename groups later via admin without schema changes.

⚠️ **Decision:** Seed runs only while **no** current row has non-empty `task_group_name`. After first seed, operators own the data; deploy re-runs must not clobber edits.

## Stage 3: Data-layer read/write (no prompt versioning on metadata)

**Done when:** `save_agent_task`, `get_agent_task`, `list_candidate_tasks`, and `sync_agent_tasks` round-trip all four fields; metadata-only saves do not retire prompt versions; prompt-version inserts copy metadata forward.

1. Extend `_save_agent_task_on_connection` signature with optional kwargs: `task_group_order`, `task_group_name`, `task_seq`, `task_name` (all `Optional`, `None` = leave existing — same as prompt kwargs except copy-upsert path).
2. Extend the `existing` SELECT to include the four grouping columns.
3. **Metadata-only branch** (no prompt segment change): when `content_changed` is false, also apply grouping updates in the same in-place `UPDATE agent_task SET … WHERE task_key_uuid = ?` block used for `agent_id` / `run_next`:
   - Coerce `task_seq` with `float(...)` when kwarg provided; accept any float (no range validation).
   - String fields: strip; allow empty strings (no rejection).
4. **New row INSERT** paths (insert when no existing row; insert after prompt retire): include the four columns in column lists and values — use kwargs when provided, else seed defaults from `_seed_values_for_task_key(task_key)` helper that mirrors Stage 2 logic for a single key (DRY: Stage 2 seed and `sync_agent_tasks` both call this helper).
5. **Prompt version retire INSERT**: when copying forward to a new `task_key_uuid`, copy grouping fields from the retired row unchanged unless kwargs override them in the same save call.
6. Extend public `save_agent_task(...)` to accept and forward the four kwargs.
7. In `sync_agent_tasks`, when inserting a missing catalog key, call `_seed_values_for_task_key(key)` and include the four columns in the `INSERT` (not blank defaults).
8. In `list_candidate_tasks`, add the four columns to the `SELECT` list so list API can avoid N+1 `get_agent_task` calls for grouping (keep existing char-length columns).
9. In `apply_agent_task_copy_upsert` / related import column lists: include the four new columns when present in pasted JSON; absent keys leave DB values untouched on update (follow existing import semantics).

## Stage 4: Admin API — Manage Tasks save/load paths

**Done when:** `GET/PUT /api/admin/tasks/<task_key>`, `GET /api/admin/tasks` (`_enrich_tasks`), and task reload after save expose grouping metadata from DB; existing Manage Tasks UI keeps working via backward-compat `phase` / `seq` keys sourced from DB until AST-739 switches the frontend.

1. In `src/ui/api/api_admin.py`, add helper `_grouping_from_agent_task_row(task: dict | None, task_key: str) -> dict` returning:
   ```python
   {
       "task_group_order": ...,
       "task_group_name": ...,
       "task_seq": ...,  # float
       "task_name": ...,
       "phase": task_group_name if task_group_name else None,  # backward compat
       "seq": task_seq if task_seq != 999.0 else None,  # mirror pre-seed UI: None when unset/default
   }
   ```
   When `task` is None, return empty strings, `task_seq=999.0`, `task_name=task_key`, `phase=None`, `seq=None`.
2. **`get_task` (`GET /tasks/<task_key>`):** Remove `cfg.get("phase")` / `cfg.get("seq")` overlay. Merge `_grouping_from_agent_task_row(task, task_key)` into the JSON response. Keep `entity_type` from `TASK_CONFIG` (execution metadata stays config-owned this epic).
3. **`update_task` (`PUT /tasks/<task_key>`):** Read optional body keys `task_group_order`, `task_group_name`, `task_seq`, `task_name`. Pass them to `database.save_agent_task(...)` (only keys present in body — use the same `if "field" in body` pattern as `run_next` / `system_prompt`). Do not validate business rules; coerce `task_seq` with `float(body["task_seq"])` when key present (400 only on non-numeric).
4. Return `jsonify` of merged `get_agent_task` + `_grouping_from_agent_task_row` (not raw DB row without compat keys).
5. **`_enrich_tasks`:** Remove `cfg.get("phase")` and `cfg.get("seq")` from the appended dict. Instead, load grouping once per row:
   - Prefer columns already on `t` from `list_candidate_tasks` if Stage 3 added them; else `full_task = database.get_agent_task(task_key)`.
   - Spread `_grouping_from_agent_task_row(full_task or t, task_key)` into each enriched row (includes `phase`, `seq`, and the four new keys).
6. **Do not** change `_dispatch_task_key_form_meta` or `/dispatch_tasks/task_keys` in this ticket (AST-739 reads DB for Scheduled Actions).

⚠️ **Decision:** AC #3 (Manage Tasks edit modal exposes four fields) is **API-ready** here; React form inputs land in **AST-739**. Verify this stage with `PUT` then `GET` on `/api/admin/tasks/<task_key>` before closing the ticket.

## Self-Assessment

**Scope:** `Single-Component` — Two production files (`database.py`, `api_admin.py`) at data + admin API layers; no frontend, config cleanup, or dispatch execution changes.

**Conf:** `high` — Follows established `agent_task` column migration, `_apply_ast*` seed, and metadata-only in-place update patterns; AST-568 already documents phase/seq consumption paths being replaced.

**Risk:** `Medium` — Incorrect versioning behavior (retiring rows on metadata-only save, or dropping metadata on prompt edit) would lose operator grouping work or break Manage Tasks ordering; blast radius is admin task management only, not dispatch execution.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | `_seed_values_for_task_key` shared by deploy seed, `sync_agent_tasks`, and new-row insert. |
| §2.1 config | Seed reads `TASK_CONFIG` once at migration; runtime API reads DB only for grouping. Config `phase`/`seq` untouched (AST-740). |
| §2.4 batch | Not applicable — no batch claim changes. |
| §2.6 state machine | Not applicable. |
| §3.3 imports | Data layer imports utils for seed only inside migration helper; API imports data + utils as today. |
| §3.5 naming | Snake_case DB/API fields match ticket spec. |

No conflicts requiring `conf-!!-NONE`.

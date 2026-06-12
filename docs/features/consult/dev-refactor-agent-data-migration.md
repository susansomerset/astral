# dev-refactor-agent-data — Data Migration Plan

## Pre-Requisite: Production Code Fixes

Two production code changes must land before the migration script, since the migration should match the production ID format.

### Fix 1 — Deterministic `agent_data_id` for ALL block types

**Current state** in `src/core/agent.py` lines 142-148: `_save()` uses deterministic IDs (`{batch_id}-{block_type}-{content_hash}`) only for SYSTEM and CACHE_A. TASK, NO_CACHE, and RESPONSE use bare `uuid4()`.

**Problem**: Bare UUIDs are unreadable, untraced, and make migration non-idempotent. NO_CACHE blocks are often shared (e.g., job listing arrays), so they benefit from dedup too.

**Change**: Remove the `deterministic` flag entirely. ALL blocks use the same pattern:

```python
content_hash = hashlib.sha256(f"{batch_id}:{block_type}:{content}".encode()).hexdigest()[:16]
agent_data_id = f"{batch_id}-{block_type.lower()}-{content_hash}"
```

This gives: readability, traceability, natural dedup for shared blocks, and idempotent re-runs for migration.

**Files**: `src/core/agent.py` — `_store_prompt_blocks._save()` and `_store_response_block()`

### Fix 2 — Add `entity_cost` to `dispatch_ledger`

**Current state**: `entity_cost` is calculated inline in `do_task` (`total_cost / batch_size`) and stored only on entity-level `agent_responses` JSON. It does not exist on `dispatch_ledger`.

**Change**:

- `src/data/database.py`: Add `entity_cost REAL DEFAULT 0.0` to `dispatch_ledger` CREATE TABLE and migration list. Add `"entity_cost"` to `_LEDGER_UPDATE_COLS`.
- `src/core/dispatcher.py` line 611-613: After computing `total_cost`, derive `entity_cost` from `total_cost / total_processed` and include in the `update_dispatch_ledger` call.

---

## Migration Script

### Scope

- **Filter**: `agent_responses.created_at >= '2026-03-17'`, candidate-independent
- **Granularity**: Runs one `task_key` at a time, selected via UI dropdown
- **Goal**: Reconstruct `agent_data` blocks from historical `agent_responses` audit records, backfill `dispatch_ledger` columns, archive old-format `company.agent_responses`
- **Execution**: Background thread triggered by UI button, logs to `app_log`

### Implementation File: `scripts/migrations/migrate_agent_data.py` (new)

Public function `run_agent_data_migration(task_key: str)` that calls steps sequentially. Each step is a separate function, idempotent, with logging. A second public helper `get_migratable_task_keys()` returns distinct task_keys from the `agent_responses` audit table within the date range, for the dropdown.

#### Step 0 — Backup tables (first run only)

Create `*_backup_YYYYMMDD` copies of `company`, `dispatch_ledger`, `agent_responses`, `timesheets`. For each table:

- If the backup table does not exist, create it via `CREATE TABLE ... AS SELECT * FROM ...`.
- If the backup table already exists, compare `COUNT(*)` between source and backup. If counts match, skip (backup is complete). If counts differ, drop and recreate the backup — a partial backup from a crashed prior run is not trustworthy.

This preserves the original baseline so we can restore from scratch and rerun after bug fixes on subsequent task_keys.

#### Step 1 — Backfill `dispatch_ledger` inferable columns

UPDATE against existing `dispatch_ledger` rows where columns are NULL, scoped to batches that contain the selected `task_key`:

- `entity_type` from `DISPATCH_TASKS[task_key]["entity_type"]`
- `batch_size` from `total_processed`
- `total_cost` from `sum_cost_by_batch`
- `entity_cost` from `total_cost / batch_size`

#### Step 2 — Archive old-format `company.agent_responses` (company task_keys only)

Only runs when `task_key` is a company entity type. Only runs once (skips if `agent_responses_legacy` column already exists):

- Add `agent_responses_legacy TEXT` column
- Copy old data to legacy column
- Reset `agent_responses` to `'[]'`

#### Step 3 — Populate `agent_data` from historical `agent_responses` audit records

For each audit record in `agent_responses` table matching the selected `task_key` and date filter:

- **Mode A (runtime_prompt exists)**: Parse the compressed `runtime_prompt` JSON to extract SYSTEM, CACHE, NO_CACHE, TASK blocks. Store each as an `agent_data` row using deterministic IDs.
- **Mode B (runtime_prompt is NULL)**: Reconstruct prompts from `TASK_CONFIG` templates + historical entity data. Store as `agent_data` rows.
- **RESPONSE block**: Decompress `parsed_response` or `raw_response` from the audit record. Store as `agent_data` RESPONSE block.
- **Entity `agent_responses` update**: Append lightweight reference (`batch_id`, `task_key`, `created_at`, `entity_cost`, `prompt_blocks`) to the entity's `agent_responses` JSON array.

All `agent_data_id` values use the deterministic `{batch_id}-{block_type}-{content_hash}` format, making the entire step safe to re-run (`INSERT OR IGNORE`).

#### Step 4 — Verify

Count checks per task_key: `agent_data` rows created, `dispatch_ledger` columns populated, entity `agent_responses` entries appended.

---

## API Endpoints — `src/ui/api/api_admin.py`

- `GET /api/admin/script/migrate_agent_data/task_keys` — Returns `{ task_keys: string[] }` from `get_migratable_task_keys()`.
- `POST /api/admin/script/migrate_agent_data` — Accepts `{ task_key: string }`. Starts migration in a background thread. Returns 409 if already running.
- `GET /api/admin/script/migrate_agent_data/status` — Returns `{ status: "idle" | "running" | "done" | "error", message: string, task_key: string | null }`.

Module-level state (`_migration_status`, `_migration_thread`, `_migration_task_key`) tracks the background thread.

---

## UI — `src/ui/frontend/src/pages/AdminDataManagement.tsx`

Add a "Migrate agent_data" section above the SQL query panel:

- **Dropdown**: Select a `task_key` from the list returned by the `task_keys` endpoint. Populated on mount.
- **Button**: "Migrate" (idle), "Running..." (running, disabled), "Done - Run Again?" (done)
- When status is "done" or "error", clicking Migrate again shows a `confirm()` dialog before re-triggering
- While running, polls `GET status` every 3 seconds
- Status message (including which `task_key`) displayed beside the button

---

## Risk Assessment


| Risk                                                                  | Mitigation                                                                                                                             |
| --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Backup tables double database size                                    | SQLite file size is manageable; backups are temporary                                                                                  |
| Partial backup from crashed first run                                 | Count-verified: backup row count must match source, otherwise drop and recreate                                                        |
| `sum_cost_by_batch` for all historical batches is slow                | Scoped to one task_key at a time. One-time cost per task_key.                                                                          |
| Legacy column on company adds permanent schema bloat                  | Can DROP COLUMN after confirming old data isn't needed (SQLite 3.35.0+)                                                                |
| Application reads mixed-format agent_responses during migration       | Step 2 archives old format before Step 3 writes new format. No mixed reads.                                                            |
| Rollback needed                                                       | Backup tables contain full pre-migration state. Restore with INSERT INTO ... SELECT FROM backup.                                       |
| Re-running migration creates duplicate entity agent_responses entries | Deterministic agent_data IDs dedup via INSERT OR IGNORE. Entity agent_responses append needs dedup check by batch_id before appending. |


---

## Code Review

**Commit:** `b90e5da`
**Branch:** `dev-refactor-agent-data`
**Reviewed:** 2026-03-19

---

## What's Solid

- **Fix 1 (deterministic IDs) is clean.** `_save()` simplified — `deterministic` flag removed, all blocks use `{batch_id}-{block_type}-{content_hash}`. `_store_response_block` updated to match. Shared blocks still dedup via INSERT OR IGNORE; per-entity blocks get unique hashes naturally from differing content.
- **Fix 2 (entity_cost on ledger) is correct.** Column added to CREATE TABLE + migration list. `_LEDGER_UPDATE_COLS` extended. Dispatcher computes `entity_cost = total_cost / total_processed` (using total_processed rather than batch_size is better — accounts for partially processed batches).
- **Migration script is well-structured.** Steps are self-contained functions, each idempotent. Deterministic agent_data_ids + INSERT OR IGNORE make the whole thing safe to re-run. `_append_entity_ref` deduplicates by batch_id as the risk assessment called for.
- **Backup logic is count-verified.** Partial backups from crashed runs are detected and recreated. Clean.
- **Step 1 (backfill ledger) handles all four columns.** entity_type from config, batch_size from total_processed, total_cost from timesheet sums (chunked in batches of 100), entity_cost derived. Proper parameterized queries for the cost aggregation.
- **Step 2 (archive company) is safe.** Legacy column check prevents double-archiving. Only runs for company task_keys.
- **Step 3 mode A correctly parses runtime_prompt structure.** The label → block_type mapping (`system_prompt → SYSTEM`, `cached_context → CACHE_A`, `nocache_context → NO_CACHE`, `user_prompt → TASK`) matches the labels used by `_assemble_blocks._track()` in production.
- **API endpoints match the plan exactly.** Three endpoints, proper auth, 409 on concurrent run, module-level thread tracking.
- **UI is minimal and functional.** Dropdown, button state machine (idle/running/done/error), 3-second polling, confirm on re-run. Follows existing component patterns.

---

## Issues

### Issue 1 — Mode B is a no-op ℹ️ advisory

The plan says Mode B should "Reconstruct prompts from `TASK_CONFIG` templates + historical entity data." The implementation (lines 290-293) acknowledges it can't reconstruct and just counts Mode B occurrences. RESPONSE blocks are still stored (the response extraction runs regardless), so the data isn't lost — but prompt blocks are missing for Mode B records.

This is a pragmatic choice (accurate reconstruction is complex and error-prone), but worth documenting: any audit record without `runtime_prompt` will have a RESPONSE block in agent_data but no prompt blocks.

### Issue 2 — `user_prompt` runtime label maps to TASK, but production stores user_content as NO_CACHE ℹ️ advisory

`_mode_a_from_runtime_prompt` maps `"user_prompt"` → `"TASK"` (line 346). In production `_assemble_blocks`, the `"user_prompt"` label tracks `getTimestampPrefix() + user_content + live_content` concatenated together. But `_store_prompt_blocks` stores `user_content` as NO_CACHE and `live_content` as TASK separately.

This means migrated data stores the combined user+live content as one TASK block, while production code stores them as separate NO_CACHE + TASK blocks. For historical data this is close enough, but the block structure won't match exactly. Just documenting the difference.

### Issue 3 — `import threading` placed mid-file in api_admin.py ℹ️ advisory

The `import threading` and the `from scripts.migrations.migrate_agent_data import ...` are placed at line ~762, after all existing endpoint definitions. Standard Python convention puts imports at the top. Moving them to the import section at the top of the file would be cleaner, though this won't cause any bugs.

### Issue 4 — `_migration_status` dict mutated from background thread without lock ℹ️ advisory

The `_run()` function updates `_migration_status` from the background thread while the `/status` endpoint reads it from Flask request threads. CPython's GIL makes dict reads/writes effectively atomic, and the single-worker Gunicorn config means no cross-process issues. Safe in practice for a migration tool, but not formally thread-safe.

---

## Recommended Actions


| #   | Severity | Action                                                                                                             |
| --- | -------- | ------------------------------------------------------------------------------------------------------------------ |
| 1   | Advisory | Document that Mode B records get RESPONSE blocks only (no prompt blocks) — add a note to the plan or a log warning |
| 2   | Advisory | Note the user_prompt → TASK mapping difference from production in a code comment                                   |
| 3   | Advisory | Move `import threading` and migration imports to top of api_admin.py                                               |
| 4   | Advisory | No action needed — GIL + single worker is sufficient for a migration tool                                          |



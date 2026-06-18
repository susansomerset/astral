# Stop dispatch retry auto-seed and startup DB inventory

**Linear:** [AST-745](https://linear.app/astralcareermatch/issue/AST-745/stop-dispatch-retry-auto-seed-and-startup-db-inventory-stop-rebuilding)  
**Parent:** [AST-741](https://linear.app/astralcareermatch/issue/AST-741/stop-rebuilding-unnecessary-dispatch-task-data) (AC reference only)  
**Publish ref:** `origin/sub/AST-741/AST-745-stop-dispatch-retry-seed`

Susan deletes `dispatch_task` rows whose `trigger_state` ends in `_RETRY`; they reappear after server restart because `_ensure_dispatch_task_schema` runs on first DB access and `INSERT OR IGNORE`s companion retry rows from `_RETRY_TASK_SEED`, and `_ensure_gaze_board_dispatch_tasks` re-seeds decommissioned `gaze_board` rows. This ticket removes those **recurring automatic row inserts** while preserving **companion-state claim** on primary rows (`dispatch_claim_states` in config — one primary row still counts entities in both `VALID_TITLE` and `VALID_TITLE_RETRY`). It also delivers a checked-in inventory of every code path that mutates `agent_task` or `dispatch_task`.

**Out of scope:** job/company state machines, consult retry routing, AST-572 retry-flag UI, `sync_agent_tasks` blank-row inserts for missing `TASK_CONFIG` keys, new `gaze_board` task content, `dispatch_ledger`, admin UI redesign.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Remove `_RETRY_TASK_SEED`, retry `INSERT OR IGNORE` loop, `_ensure_gaze_board_dispatch_tasks`, and its call; update module header comments | data |
| `debug/startup_db_inventory.md` | New catalog of all `agent_task` / `dispatch_task` mutators (automatic vs operator-initiated) | docs |
| `.gitignore` | Add `!debug/startup_db_inventory.md` negation so Susan’s inventory is tracked while `debug/` stays ignored | repo |

Betty may add component tests (schema ensure no longer re-inserts deleted `*_RETRY` rows after restart simulation) in **astral-tests** — engineer does **not** edit `tests/` or `docs/test-bible/**`.

---

## Stage 1: Remove automatic retry and gaze_board dispatch row seeding

**Done when:** `_ensure_dispatch_task_schema` no longer contains `_RETRY_TASK_SEED` or `_ensure_gaze_board_dispatch_tasks`; deleted `*_RETRY` and `gaze_board` rows stay absent after process restart / schema ensure; one-time migrations (column adds, triple-unique rebuild, prefilter DELETE/UPDATE, gaze `sort_by`, `locate_job_page` → `find_job_page`, `recheck_no_openings`) remain unchanged; `dispatch_claim_states` in `src/utils/config.py` is **not** modified.

1. In `src/data/database.py`, **delete** the module-level `_RETRY_TASK_SEED` list (~5674–5678):

   ```python
   _RETRY_TASK_SEED = [
       ("qualify_job_listings", "VALID_TITLE_RETRY"),
       ("evaluate_jd",          "JD_READY_RETRY"),
       ("fetch_website",        "WEBSITE_FOUND_RETRY"),
   ]
   ```

2. **Delete** the entire `_ensure_gaze_board_dispatch_tasks(conn)` function (~5681–5727) — both `INSERT OR IGNORE` blocks (gaze-row clone and `board_search` fallback).

3. In `_ensure_dispatch_task_schema`, **delete** the block `# Add retry task rows for each candidate that has the corresponding base task` (~5905–5927): the `for base_key, retry_trigger in _RETRY_TASK_SEED:` loop and its `INSERT OR IGNORE` / `commit`.

4. In `_ensure_dispatch_task_schema`, **delete** the trailing call `_ensure_gaze_board_dispatch_tasks(conn)` (~6014) — keep `_dispatch_task_schema_ensured = True` immediately after the AST-702/703 prefilter migration `commit`.

5. Update the `database.py` file header comment block (~lines 18–22) if it still describes automatic retry companion dispatch rows — replace with: primary dispatch rows only; companion `*_RETRY` entities claimed via `dispatch_claim_states`, not separate dispatch rows.

6. **Do not touch:** `dispatch_claim_states`, `DISPATCH_SCHEDULABLE_TASK_KEYS`, `save_dispatch_task`, `update_dispatch_task`, admin API, dispatcher runners, or one-time migration SQL (including `DELETE FROM dispatch_task WHERE task_key = 'prefilter' AND trigger_state = 'WEBSITE_FOUND_RETRY'`).

7. Manual verification on epic worktree (throwaway DB — do **not** commit):

   - Open SQLite with a candidate that has a primary `qualify_job_listings` row at `VALID_TITLE` and **no** row at `VALID_TITLE_RETRY`.
   - `DELETE` any `*_RETRY` dispatch rows and any `gaze_board` rows for that candidate.
   - Set `database._dispatch_task_schema_ensured = False`, call `_ensure_dispatch_task_schema(conn)`.
   - Assert `SELECT COUNT(*) FROM dispatch_task WHERE trigger_state LIKE '%_RETRY'` is **0** and `task_key = 'gaze_board'` count is **0**.
   - Call `database.count_eligible_for_dispatch_task` on the primary `qualify_job_listings` / `VALID_TITLE` row with a job in `VALID_TITLE_RETRY` — count must include that job (companion claim intact).

⚠️ **Decision:** Remove seeding entirely rather than gating on a config flag — Susan’s deletes must survive restart with no opt-in; companion claim already lives in config, not extra rows.

---

## Stage 2: Startup DB inventory document

**Done when:** `debug/startup_db_inventory.md` exists, is committed (via `.gitignore` exception), and lists every mutating path below with columns: **Path**, **Table**, **Operation**, **Trigger**, **Automatic vs operator**, **Idempotent?**, **Can recreate deleted rows?**, **Notes**.

1. Add to `.gitignore` immediately after the `debug/` line:

   ```
   !debug/startup_db_inventory.md
   ```

2. Create `debug/startup_db_inventory.md` with an intro paragraph (purpose, how to use, last updated AST-745) and two sections: **`dispatch_task`** then **`agent_task`**. Populate from code survey — minimum rows:

   **dispatch_task — automatic (recurring):**

   | Path | Trigger | Can recreate deleted rows? |
   |------|---------|----------------------------|
   | `_ensure_dispatch_task_schema` — NULL-column backfill `UPDATE` | First connection / admin list / upsert ensure | No (updates existing rows only) |
   | `_ensure_dispatch_task_schema` — `score_floor` backfill `UPDATE` | Same | No |
   | `_ensure_dispatch_task_schema` — one-time migration `UPDATE`/`DELETE`/`CREATE TABLE` blocks | Same, once per process until `_dispatch_task_schema_ensured` | No (migrations only; retry/gaze_board **INSERT** seeds removed AST-745) |
   | `ensure_table_schema_for_upsert` → `_ensure_dispatch_task_schema` | Config table upsert / copy upsert | Indirect (schema ensure only) |

   **dispatch_task — operator-initiated:**

   | Path | Trigger | Can recreate deleted rows? |
   |------|---------|----------------------------|
   | `save_dispatch_task` | `POST /api/admin/dispatch_tasks` (Manage Dispatch create) | Yes — explicit create |
   | `update_dispatch_task` | `PUT /api/admin/dispatch_tasks/<id>` | No (updates only) |
   | `update_dispatch_task(last_run_at=…)` | Dispatcher after batch run (`src/core/dispatcher.py`) | No |
   | `apply_config_table_upsert` for `dispatch_task` | `POST /api/admin/data/upsert_config_table`, `scripts/push_tables_to_prod.py`, `scripts/upsert_tables_from_prod.py` | Yes — upserts rows present in payload |
   | Direct SQLite / external DBA | Susan manual | N/A |

   **agent_task — automatic (recurring):**

   | Path | Trigger | Can recreate deleted rows? |
   |------|---------|----------------------------|
   | `sync_agent_tasks` | `bootstrap_runtime()` on server start (`src/core/bootstrap.py`) | Yes — inserts blank `current=1` row for each `TASK_CONFIG` key missing from DB |
   | `_apply_ast738_task_grouping_metadata_seed` | Called from `sync_agent_tasks` and `_ensure_agent_task_schema` | No (metadata UPDATE on existing rows) |
   | `_ensure_agent_task_schema` — v1→versioned migration `INSERT` | First access | One-time only |

   **agent_task — operator-initiated:**

   | Path | Trigger | Can recreate deleted rows? |
   |------|---------|----------------------------|
   | `save_agent_task` / `_save_agent_task_on_connection` | `PUT /api/admin/tasks/<task_key>` (Manage Tasks) | Yes — versions row or inserts if missing |
   | `apply_agent_task_copy_upsert` | `POST /api/admin/data/table_copy_upsert` | Yes |
   | `apply_config_table_upsert` for `agent_task` | upsert_config_table / push / upsert scripts | Yes |
   | One-time scripts: `scripts/migrations/backfill_task_grouping_metadata.py`, rubric token migration helpers in `database.py` | Manual CLI | One-time UPDATE |
   | Direct SQLite / external DBA | Susan manual | N/A |

3. Add a **“Removed AST-745”** subsection noting `_RETRY_TASK_SEED` companion inserts and `_ensure_gaze_board_dispatch_tasks` no longer run.

4. Add a **“Not in scope”** note: `dispatch_ledger`, entity tables, `sync_agent_tasks` blank inserts (explicit parent boundary).

---

## Execution contract (build-child)

- Execute stages **1 → 2** in order; **one commit per stage** on epic worktree (`astral-AST-741`), then publish each to **`origin/sub/AST-741/AST-745-stop-dispatch-retry-seed`** via `git push origin HEAD:sub/AST-741/AST-745-stop-dispatch-retry-seed`.
- Do **not** edit `tests/`, `docs/ASTRAL_TEST_BIBLE.md`, or `docs/test-bible/**`.
- Do **not** modify `src/utils/config.py` except if a compile error references removed symbols (none expected).
- Blocking ambiguity → `🛑 Stage N blocked` comment on **AST-741** parent per plan-child execution contract.

---

## Self-Assessment

**Scope:** `Single-Component` — Primary change is `src/data/database.py` schema-ensure seed removal plus one inventory markdown file and a single `.gitignore` negation line.

**Conf:** `high` — Root cause is explicit `_RETRY_TASK_SEED` / `_ensure_gaze_board_dispatch_tasks` `INSERT OR IGNORE` on every schema ensure; companion claim is already implemented in `dispatch_claim_states` and must remain untouched.

**Risk:** `Medium` — Wrong deletion (e.g. removing one-time prefilter migration) could break admin dispatch on legacy DBs; mitigated by surgical removal of only the two recurring seed blocks and manual verification steps in Stage 1.

---

## Code rules self-review

| Rule | Assessment |
|------|------------|
| §2.1 config / `dispatch_tasks` | Schedulable defaults stay in `dispatch_task_admin_defaults`; no new seed dicts. |
| §2.6 state machine | Job/company states and `retry_state` routing unchanged; claim via `dispatch_claim_states` preserved. |
| §2.4 batch processing | Dispatcher `last_run_at` updates and claim paths unchanged. |
| §1.3 DRY | Deleting dead seed code; inventory doc replaces tribal knowledge. |
| §3.3 imports | No new cross-layer imports. |
| §3.6 debug output | Inventory at Susan-specified `debug/startup_db_inventory.md` with explicit gitignore exception — not under `debug/spikes/`. |

No conflicts requiring **Conf: !!-NONE**.

---

## Built (AST-745)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `88b48ed` | Remove `_RETRY_TASK_SEED`, `_ensure_gaze_board_dispatch_tasks`, and retry insert loop from `_ensure_dispatch_task_schema` |
| 2 | (this commit) | `debug/startup_db_inventory.md` + `.gitignore` exception |

**Publish ref:** `origin/sub/AST-741/AST-745-stop-dispatch-retry-seed`

**Review:** _(Radia — pending)_

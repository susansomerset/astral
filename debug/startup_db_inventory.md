# Startup / runtime inventory — `agent_task` and `dispatch_task` writers

**Purpose:** Catalog every code path that inserts, updates, or deletes rows in `agent_task` or `dispatch_task`, so Susan can tell which paths may recreate rows she deliberately removed.

**How to use:** Check the **Automatic vs operator** and **Can recreate deleted rows?** columns before deleting dispatch or agent task rows. After AST-745, no automatic path re-inserts `*_RETRY` or `gaze_board` dispatch rows.

**Last updated:** AST-745 (2026-06-18)

---

## dispatch_task

### Automatic (recurring)

| Path | Table | Operation | Trigger | Automatic vs operator | Idempotent? | Can recreate deleted rows? | Notes |
|------|-------|-----------|---------|----------------------|-------------|---------------------------|-------|
| `_ensure_dispatch_task_schema` — NULL-column backfill | dispatch_task | UPDATE | First DB connection that ensures dispatch schema | automatic | Yes | No | Fills NULL columns from `dispatch_task_admin_defaults` |
| `_ensure_dispatch_task_schema` — `score_floor` backfill | dispatch_task | UPDATE | Same | automatic | Yes | No | Sets `score_floor = 1.0` where NULL on scored triggers |
| `_ensure_dispatch_task_schema` — one-time migrations | dispatch_task | CREATE / ALTER / UPDATE / DELETE | Same, once per process | automatic | One-time per DB | No | Column adds, triple-unique rebuild, prefilter cutover |
| `ensure_table_schema_for_upsert` → `_ensure_dispatch_task_schema` | dispatch_task | (indirect) | Config upsert / copy upsert preflight | automatic | Same as schema ensure | Indirect only | Does not insert rows by itself |

### Operator-initiated

| Path | Table | Operation | Trigger | Automatic vs operator | Idempotent? | Can recreate deleted rows? | Notes |
|------|-------|-----------|---------|----------------------|-------------|---------------------------|-------|
| `save_dispatch_task` | dispatch_task | INSERT | `POST /api/admin/dispatch_tasks` | operator | No | **Yes** | Manage Dispatch create |
| `update_dispatch_task` | dispatch_task | UPDATE | `PUT /api/admin/dispatch_tasks/<id>` | operator | Yes | No | Manage Dispatch edit |
| `update_dispatch_task(last_run_at=…)` | dispatch_task | UPDATE | Dispatcher after batch run | automatic runtime | Yes | No | Scheduler bookkeeping |
| `update_dispatch_task(enabled=False)` | dispatch_task | UPDATE | Dispatcher max_runs exhausted | automatic runtime | Yes | No | Disables auto_mode |
| `apply_config_table_upsert` | dispatch_task | INSERT or UPDATE | upsert_config_table; push/upsert scripts | operator | Per-row | **Yes** | Upserts rows in payload |
| `apply_generic_table_copy_upsert` | dispatch_task | INSERT or UPDATE | `POST /api/admin/data/table_copy_upsert` | operator | Per-row | **Yes** | Copy Output paste |
| `POST /api/admin/data/sql` | dispatch_task | Arbitrary | Admin raw SQL | operator | N/A | **Yes** | Susan-controlled |
| Direct SQLite / external DBA | dispatch_task | Arbitrary | Manual | operator | N/A | **Yes** | Outside application |

---

## agent_task

### Automatic (recurring)

| Path | Table | Operation | Trigger | Automatic vs operator | Idempotent? | Can recreate deleted rows? | Notes |
|------|-------|-----------|---------|----------------------|-------------|---------------------------|-------|
| `sync_agent_tasks` | agent_task | INSERT | `bootstrap_runtime()` on server start | automatic | Yes for existing keys | **Yes for missing keys** | Blank row per missing `TASK_CONFIG` key |
| `_apply_ast738_task_grouping_metadata_seed` | agent_task | UPDATE | `sync_agent_tasks` / `_ensure_agent_task_schema` | automatic | Yes | No | Metadata backfill on existing rows |
| `_ensure_agent_task_schema` — v1→versioned migration | agent_task | INSERT | First agent_task access on legacy DB | automatic | One-time | One-time only | Legacy schema migration |

### Operator-initiated

| Path | Table | Operation | Trigger | Automatic vs operator | Idempotent? | Can recreate deleted rows? | Notes |
|------|-------|-----------|---------|----------------------|-------------|---------------------------|-------|
| `save_agent_task` / `_save_agent_task_on_connection` | agent_task | INSERT + retire | `PUT /api/admin/tasks/<task_key>` | operator | Versioned | **Yes** | Manage Tasks edit |
| `apply_agent_task_copy_upsert` | agent_task | INSERT / UPDATE | `POST /api/admin/data/table_copy_upsert` | operator | Per-row | **Yes** | Copy Output import |
| `apply_config_table_upsert` | agent_task | INSERT OR REPLACE | upsert_config_table / scripts | operator | Per-row | **Yes** | Full row replace |
| `scripts/migrations/backfill_task_grouping_metadata.py` | agent_task | UPDATE | Manual CLI | operator | One-time | No | Grouping backfill |
| One-time migrations in `database.py` | agent_task | UPDATE / version | First schema ensure | automatic | One-time | One-time prompt migrations |
| `POST /api/admin/data/sql` | agent_task | Arbitrary | Admin raw SQL | operator | N/A | **Yes** | Susan-controlled |
| Direct SQLite / external DBA | agent_task | Arbitrary | Manual | operator | N/A | **Yes** | Outside application |

---

## Removed AST-745

The following **automatic recurring INSERT** paths were removed from `_ensure_dispatch_task_schema`:

- **`_RETRY_TASK_SEED`** — cloned companion `*_RETRY` dispatch rows for each candidate with a primary row.
- **`_ensure_gaze_board_dispatch_tasks`** — `INSERT OR IGNORE` decommissioned `gaze_board` rows.

Companion retry **entity** processing is unchanged: primary dispatch rows claim both primary and `*_RETRY` holding states via `dispatch_claim_states` in `src/utils/config.py`.

---

## Not in scope

- **`dispatch_ledger`** and all other tables.
- **`sync_agent_tasks` blank inserts** — intentional parent boundary; documented above.
- **AST-381** snapshot export/import — not automatic bootstrap.
- **Entity tables** (`job`, `company`, `candidate`, etc.).

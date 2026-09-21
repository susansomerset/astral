# Startup / runtime inventory — `agent_task` and `dispatch_task` writers

**Purpose:** Catalog every code path that inserts, updates, or deletes rows in `agent_task` or `dispatch_task`, so Susan can tell which paths may recreate rows she deliberately removed.

**How to use:** Check the **Automatic vs operator** and **Can recreate deleted rows?** columns before deleting dispatch or agent task rows. After AST-745, no automatic path re-inserts `*_RETRY` or `gaze_board` dispatch rows. After AST-1496, no automatic path inserts or content-updates live `dispatch_task` rows (DDL ensure + runtime bookkeeping only).

**Last updated:** AST-1496 (2026-08-26)

---

## dispatch_task

### Automatic (recurring)

| Path | Table | Operation | Trigger | Automatic vs operator | Idempotent? | Can recreate deleted rows? | Notes |
|------|-------|-----------|---------|----------------------|-------------|---------------------------|-------|
| _(none — content writers banned AST-1496)_ | — | — | — | — | — | — | No automatic INSERT/content-UPDATE of live `dispatch_task` rows |
| `_ensure_dispatch_task_schema` — schema DDL only | dispatch_task | CREATE / ALTER | First DB connection that ensures dispatch schema | automatic (DDL) | Yes | No | Table create, ADD COLUMN, structural unique rebuilds; **no** content backfill/retarget |
| `ensure_table_schema_for_upsert` → `_ensure_dispatch_task_schema` | dispatch_task | (indirect) | Config upsert / copy upsert preflight | automatic (DDL) | Same as schema ensure | No | Schema only |
| `update_dispatch_task(last_run_at=…)` | dispatch_task | UPDATE | Dispatcher after batch run | automatic runtime | Yes | No | Scheduler bookkeeping (not content seed) |
| `update_dispatch_task(enabled=False)` | dispatch_task | UPDATE | Dispatcher max_runs exhausted | automatic runtime | Yes | No | Disables auto_mode |

### Operator-initiated

| Path | Table | Operation | Trigger | Automatic vs operator | Idempotent? | Can recreate deleted rows? | Notes |
|------|-------|-----------|---------|----------------------|-------------|---------------------------|-------|
| `save_dispatch_task` | dispatch_task | INSERT | `POST /api/admin/dispatch_tasks` | operator | No | **Yes** | Manage Dispatch create |
| `update_dispatch_task` | dispatch_task | UPDATE | `PUT /api/admin/dispatch_tasks/<id>` | operator | Yes | No | Manage Dispatch edit |
| `apply_config_table_upsert` | dispatch_task | INSERT or UPDATE | Admin upsert_config_table only | operator | Per-row | **Yes** | Upserts rows in payload; **scripts push/upsert hard-fail on `dispatch_task` (AST-1496)** |
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

## Removed AST-1496

Ban on automatic `dispatch_task` content writers:

- **`start_scheduler` provision** — no longer calls `provision_meteorite_dispatch_tasks`, `provision_meteorite_email_dispatch_tasks`, or `ensure_fetch_email_dispatch_task` (those helpers must not run from boot).
- **`_ensure_dispatch_task_schema` content paths** — NULL-column / `score_floor` backfills and legacy content UPDATE/DELETE/INSERT retargets removed; DDL ensure remains.
- **`scripts/push_tables_to_prod.py` / `scripts/upsert_tables_from_prod.py`** — hard-fail if `dispatch_task` is in the resolved table list.
- **`SEED_CONFIG` `dispatch_task-*` / `METEORITE_DISPATCH_TASKS`** — demoted to Linear copy-paste / non-executable catalog only.

---

## Not in scope

- **`dispatch_ledger`** and all other tables.
- **`sync_agent_tasks` blank inserts** — intentional parent boundary; documented above.
- **AST-381** snapshot export/import — not automatic bootstrap.
- **Entity tables** (`job`, `company`, `candidate`, etc.).

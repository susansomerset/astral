# Task grouping metadata storage and seed (Organizing Tasks)

**Linear:** [AST-738](https://linear.app/astralcareermatch/issue/AST-738/task-grouping-metadata-storage-and-seed-organizing-tasks)  
**Parent:** [AST-734](https://linear.app/astralcareermatch/issue/AST-734/organizing-tasks)  
**Publish ref:** `sub/AST-734/AST-738-task-grouping-metadata-storage-and-seed`

Persist four global-per-`task_key` grouping columns on `agent_task`, seed them once from today's `TASK_CONFIG` `phase` / `seq`, and expose read/write on Manage Tasks admin API paths from the database only. UI layout and Scheduled Actions grouping API remain sibling tickets (AST-739 / AST-740).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add four columns to `agent_task`; extend save/get/list/sync; idempotent AST-738 seed hook in schema ensure; update header inventory | data |
| `scripts/migrations/backfill_task_grouping_metadata.py` | One-time seed logic (callable + CLI); reads `TASK_CONFIG` `phase`/`seq` | scripts |
| `src/ui/api/api_admin.py` | `_enrich_tasks`, `get_task`, `update_task` — four DB fields only; remove config `phase`/`seq` overlay on Manage Tasks paths | ui |

**Out of scope (explicit):** `src/ui/frontend/**`, `src/utils/config.py` (phase/seq removal), `_dispatch_task_key_form_meta` / `/dispatch_tasks/task_keys` (AST-739), `tests/**` (Betty qa-child).

## Stage 1: Schema columns and seed migration

**Done when:** Fresh DB bootstrap creates `agent_task` with the four grouping columns; existing DBs get columns via ALTER; every `current=1` row for each `get_task_keys()` entry has seeded `task_group_order`, `task_group_name`, `task_seq`, and `task_name` after first schema ensure; re-running seed is a no-op.

1. In `scripts/migrations/backfill_task_grouping_metadata.py`, create a module with:
   - Docstring listing CLI usage: `python scripts/migrations/backfill_task_grouping_metadata.py [--dry-run]`
   - `def build_phase_order_map() -> dict[str, str]`: collect unique non-empty `phase` strings from `TASK_CONFIG` via `get_task_keys()`; sort with `sorted(...)` (lexicographic — matches today's Manage Tasks section order, e.g. `"A. Candidate Context"` before `"A. Candidate Intake"` before `"B. …"`); return `{phase: f"{i:02d}" for i, phase in enumerate(sorted_phases, start=1)}`.
   - `def seed_row_values(task_key: str, phase_order: dict[str, str]) -> dict`: read `cfg = TASK_CONFIG.get(task_key, {})`; `phase = cfg.get("phase") or ""`; return:
     - `task_group_name`: `phase`
     - `task_group_order`: `phase_order.get(phase, "")` when `phase` else `""`
     - `task_seq`: `float(cfg["seq"])` when `cfg.get("seq") is not None` else `None`
     - `task_name`: `task_key` (always — no separate display name in config today)
   - `def backfill_task_grouping_metadata(conn, *, dry_run: bool = False) -> dict[str, int]`: assume caller already ran `_ensure_agent_task_schema(conn)`. Loop `get_task_keys()`; for each key SELECT `current=1` row; if none, count `skipped_no_row` and continue. Compute seed values via `seed_row_values`; UPDATE only when **all** of `task_group_name`, `task_group_order`, `task_name` are empty **and** `task_seq IS NULL` (idempotent — never overwrite admin-edited values). Count `updated` / `skipped`. If `dry_run`, do not commit.
   - `if __name__ == "__main__"`: argparse `--dry-run`; connect with `ASTRAL_CONFIG["db_dir"] / "astral.db"`; print counts.

2. In `src/data/database.py` header inventory (top-of-file table list), extend the `agent_task` bullet to document: `task_group_order TEXT`, `task_group_name TEXT`, `task_seq REAL`, `task_name TEXT` — global per `task_key`, carried on versioned rows, not candidate-specific.

3. In `_ensure_agent_task_schema(conn)`, after existing column-migration block (after `cache_prompt_d` adds, before `_apply_ast469…` calls), add idempotent ALTERs:
   ```python
   for col, ddl in (
       ("task_group_order", "TEXT NOT NULL DEFAULT ''"),
       ("task_group_name", "TEXT NOT NULL DEFAULT ''"),
       ("task_seq", "REAL"),
       ("task_name", "TEXT NOT NULL DEFAULT ''"),
   ):
       if col not in cols:
           conn.execute(f"ALTER TABLE agent_task ADD COLUMN {col} {ddl}")
           conn.commit()
           cols = {row[1] for row in conn.execute("PRAGMA table_info(agent_task)").fetchall()}
   ```
   Also add the four columns to the **CREATE TABLE** DDL in both the empty-table branch and the v1-migration CREATE so new installs have columns without ALTER.

4. In `sync_agent_tasks`, extend the INSERT for missing keys to include `task_group_order='', task_group_name='', task_seq=NULL, task_name=<task_key>` (column list + placeholders must match new schema).

5. At the **end** of `sync_agent_tasks` (after the insert loop, before `conn.commit()`), lazy-import and call `backfill_task_grouping_metadata(conn, dry_run=False)`. Bootstrap always calls `sync_agent_tasks(get_task_keys())` first — this guarantees catalog rows exist before seed runs on fresh DBs. No one-shot global flag; per-row empty check makes every call safe.

6. Add `def _apply_ast738_task_grouping_metadata_seed(conn)` that only calls `backfill_task_grouping_metadata(conn)` — invoke it from `_ensure_agent_task_schema` **after** column ADDs (so existing deployments seed on first API touch even before next bootstrap sync). Duplicate call from sync + schema ensure is harmless (idempotent).

⚠️ **Decision:** Seed logic lives in `scripts/migrations/backfill_task_grouping_metadata.py` (CLI + tests); runtime entry points are end-of-`sync_agent_tasks` and `_ensure_agent_task_schema` hook. Idempotency: only fill rows still at factory-empty grouping values so re-deploy never clobber admin edits.

⚠️ **Decision:** `task_group_order` is a two-digit string (`"01"`, `"02"`, …) from sorted unique `phase` labels, not the raw `"A."` prefix alone — operators may later change order strings in Manage Tasks without touching config.

## Stage 2: Data layer read/write

**Done when:** `get_agent_task`, `list_candidate_tasks`, and `save_agent_task` round-trip all four fields; changing grouping metadata alone does not version prompt rows; changing prompt segments copies grouping metadata forward to the new `current=1` row.

1. Extend `_save_agent_task_on_connection` signature with optional kwargs (default `None` = leave untouched, same as `run_next`):
   - `task_group_order: Optional[str] = None`
   - `task_group_name: Optional[str] = None`
   - `task_seq: Optional[float] = None` — accept `int` from callers by coercing with `float(v)` when not None
   - `task_name: Optional[str] = None`

2. Extend the existing-row SELECT to include the four columns (append to SELECT list and index mapping).

3. **Insert path** (no existing row): include seed defaults — `task_name=task_key` when kwarg None; other grouping kwargs default to `''` / `NULL` as appropriate.

4. **Content-changed versioning path** (new row INSERT): copy forward current grouping values unless kwargs explicitly override (same merge rules as `run_next` / `agent_id`).

5. **In-place update path** (no prompt segment change): if any grouping kwarg is not None, append `task_group_order = ?`, etc. to `sets` / `params` alongside `agent_id` / `run_next` — do **not** set `content_changed`.

6. Extend public `save_agent_task(...)` to accept and forward the four kwargs.

7. In `list_candidate_tasks`, add to SELECT: `task_group_order`, `task_group_name`, `task_seq`, `task_name` ( `get_agent_task` already uses `SELECT *` — no change needed once columns exist).

8. Add a small helper in `database.py` (or reuse seed module):
   ```python
   def get_task_grouping_metadata(task_key: str) -> Optional[dict]:
   ```
   Return `{task_group_order, task_group_name, task_seq, task_name}` from current row or None — used by api_admin dispatch helper in AST-739; optional in this ticket but **skip** unless needed (YAGNI — AST-739 can add).

## Stage 3: Manage Tasks admin API

**Done when:** `GET /api/admin/tasks` returns the four fields per row from DB; `GET /api/admin/tasks/<task_key>` returns them from DB; `PUT /api/admin/tasks/<task_key>` persists them; responses no longer include config-sourced `phase` or `seq` on these paths; `entity_type` on single-task GET still comes from `TASK_CONFIG` (execution metadata, not grouping).

1. In `_enrich_tasks`, remove:
   ```python
   "phase": cfg.get("phase"),
   "seq": cfg.get("seq"),
   ```
   Add from list row `t` (DB):
   ```python
   "task_group_order": t.get("task_group_order") or "",
   "task_group_name": t.get("task_group_name") or "",
   "task_seq": t.get("task_seq"),
   "task_name": t.get("task_name") or task_key,
   ```
   Keep `cfg = TASK_CONFIG.get(task_key, {})` only where still needed for non-grouping enrichment (if `cfg` becomes unused, remove the line).

2. In `get_task(task_key)`, remove:
   ```python
   task["phase"] = cfg.get("phase")
   task["seq"] = cfg.get("seq")
   ```
   Keep `task["entity_type"] = cfg.get("entity_type")`. Grouping fields already present via `get_agent_task` dict once Stage 2 lands.

3. In `update_task(task_key)`, read optional body keys and pass through to `save_agent_task`:
   ```python
   task_group_order=body.get("task_group_order") if "task_group_order" in body else None,
   task_group_name=body.get("task_group_name") if "task_group_name" in body else None,
   task_seq=body.get("task_seq") if "task_seq" in body else None,
   task_name=body.get("task_name") if "task_name" in body else None,
   ```
   Coerce `task_seq`: if body value is `""`, treat as `None`; if int/float/str numeric, `float(...)`. Do **not** reject empty strings, duplicate orders, or missing group names (AC #4 — no business validation).

4. Do **not** change `_dispatch_task_key_form_meta`, `/dispatch_tasks/task_keys`, or `/dispatch_tasks` list payloads in this ticket (AST-739 switches Scheduled Actions UI/API to DB metadata).

## Stage 4: Manual verification (build-child)

**Done when:** Local admin API returns seeded grouping metadata for a known task key and accepts edits.

1. Start app against a DB that has run bootstrap (or touch any DB path that triggers `_ensure_agent_task_schema`).
2. `GET /api/admin/tasks?candidate_id=<any>` — confirm `craft_resume_base` (or any known key) has non-empty `task_group_name` matching former config phase and numeric `task_seq`.
3. `PUT /api/admin/tasks/<key>` with altered `task_group_name` and `task_seq`; `GET` same key — values persist.
4. `grep` `api_admin.py` `_enrich_tasks` / `get_task` — no `cfg.get("phase")` or `cfg.get("seq")` on Manage Tasks paths.

## Self-Assessment

**Scope:** `Single-Component` — touches `agent_task` storage, one migration script, and Manage Tasks admin API handlers only; no frontend or TASK_CONFIG edits.

**Conf:** `high` — follows existing `agent_task` column migration, metadata save (run_next pattern), and admin API enrichment patterns; seed mapping from config is fully specified.

**Risk:** `Medium` — wrong seed idempotency could overwrite admin edits or leave blank grouping after deploy; prompt versioning must copy grouping fields or edits would appear to “reset” on prompt save.

## Rules self-review

- **§1.3 DRY:** Seed logic centralized in migration module; schema ALTER follows existing column-add loop.
- **§2.1 config:** Reads `TASK_CONFIG` only in one-time seed — runtime Manage Tasks API stops reading `phase`/`seq` from config.
- **§3.3 imports:** Migration script imports `database` and `config`; lazy import in `_apply_ast738` avoids load-time cycle.
- **§3.5 naming:** Field names match parent epic (`task_group_order`, `task_group_name`, `task_seq`, `task_name`).
- **Table inventory:** Header updated when columns added (§ law line 12).

No conflicts flagged.

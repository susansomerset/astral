# Task grouping metadata storage and seed (Organizing Tasks)

**Linear:** [AST-738](https://linear.app/astralcareermatch/issue/AST-738/task-grouping-metadata-storage-and-seed-organizing-tasks)  
**Parent:** [AST-734](https://linear.app/astralcareermatch/issue/AST-734/organizing-tasks)  
**Publish ref:** `sub/AST-734/AST-738-task-grouping-metadata-storage-and-seed`

Susan wants task grouping and ordering editable in admin without redeploying config. This ticket adds four global-per-`task_key` fields on `agent_task` rows (`task_group_order`, `task_group_name`, `task_seq`, `task_name`), seeds them once from today's `TASK_CONFIG` `phase` / `seq`, and wires Manage Tasks API save/load paths to read and write DB values only. React list layout and Scheduled Actions grouping are **AST-739**; removing `phase` / `seq` from config is **AST-740**.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add four columns; extend save/get/list/sync/copy-upsert; idempotent seed hook | data |
| `scripts/migrations/backfill_task_grouping_metadata.py` | Seed logic (callable + CLI); reads `TASK_CONFIG` `phase`/`seq` | scripts |
| `src/ui/api/api_admin.py` | PUT/GET `/tasks/<task_key>` and `_enrich_tasks` surface DB grouping fields; backward-compat `phase`/`seq` from DB | ui |

**Out of scope (this ticket):** `src/ui/frontend/**` (AST-739), `src/utils/config.py` phase/seq removal (AST-740), `_dispatch_task_key_form_meta` / `/dispatch_tasks/task_keys` (AST-739), `tests/**` (Betty after Code Complete).

## Stage 1: Schema columns and seed migration

**Done when:** Fresh and migrated databases have four new columns on `agent_task`; every `current=1` catalog row is seeded after first bootstrap; re-running seed does not overwrite operator edits.

1. In `scripts/migrations/backfill_task_grouping_metadata.py`, create a module with:
   - Docstring listing CLI usage: `python scripts/migrations/backfill_task_grouping_metadata.py [--dry-run]`
   - `def seed_values_for_task_key(task_key: str) -> dict`: read `cfg = TASK_CONFIG.get(task_key, {})`; `phase = (cfg.get("phase") or "").strip()`; `seq_raw = cfg.get("seq")`; return:
     - `task_group_name`: `phase if phase else "(unassigned)"`
     - `task_group_order`: `phase if phase else "ZZZ"`
     - `task_seq`: `float(seq_raw) if seq_raw is not None else 999.0`
     - `task_name`: `task_key`
   - `def backfill_task_grouping_metadata(conn, *, dry_run: bool = False) -> dict[str, int]`: assume caller ran `_ensure_agent_task_schema(conn)`. **Global guard:** `SELECT COUNT(*) FROM agent_task WHERE current = 1 AND task_group_name != ''` — if count > 0, return immediately (already seeded or operator-edited). Loop `get_task_keys()`; for each key SELECT `current=1` row; if none, count `skipped_no_row`. UPDATE with `seed_values_for_task_key` values. For orphan `current=1` rows whose `task_key` ∉ `get_task_keys()`, set unassigned defaults. Count `updated` / `skipped`. If `dry_run`, do not commit.
   - `if __name__ == "__main__"`: argparse `--dry-run`; connect with `ASTRAL_CONFIG["db_dir"] / "astral.db"`; print counts.

2. In `src/data/database.py` header inventory, extend the `agent_task` bullet: `task_group_order TEXT NOT NULL DEFAULT ''`, `task_group_name TEXT NOT NULL DEFAULT ''`, `task_seq REAL NOT NULL DEFAULT 999.0`, `task_name TEXT NOT NULL DEFAULT ''`.

3. In `_ensure_agent_task_schema(conn)`, after existing column migrations and **before** `_apply_ast469_select_job_page_run_next_migration(conn)`, add idempotent ALTERs for the four columns if missing (refresh `cols` after each add). Add columns to both CREATE TABLE DDL branches (empty table + v1 migration).

4. Add `def _apply_ast738_task_grouping_metadata_seed(conn)` that lazy-imports and calls `backfill_task_grouping_metadata(conn, dry_run=False)`. Call from `_ensure_agent_task_schema` after column adds and existing `_apply_ast*` migrations.

5. In `sync_agent_tasks`, extend INSERT for missing keys to include four columns from `seed_values_for_task_key(key)`.

6. At **end** of `sync_agent_tasks` (after insert loop, before `conn.commit()`), call `_apply_ast738_task_grouping_metadata_seed(conn)` so fresh DBs seed after catalog rows exist.

⚠️ **Decision:** Initial `task_group_order` equals config `phase` string (labels already sort lexicographically). Susan can rename/reorder groups in admin later.

⚠️ **Decision:** `task_seq` default `999.0` matches today's UI `(seq ?? 999)` fallback for unseeded rows.

⚠️ **Decision:** Global seed guard (any non-empty `task_group_name`) prevents deploy re-runs from clobbering operator edits.

## Stage 2: Data layer read/write

**Done when:** `save_agent_task`, `get_agent_task`, `list_candidate_tasks`, and `sync_agent_tasks` round-trip all four fields; metadata-only saves do not retire prompt versions; prompt-version inserts copy metadata forward.

1. Extend `_save_agent_task_on_connection` with optional kwargs: `task_group_order`, `task_group_name`, `task_seq`, `task_name` (`None` = leave existing).

2. Extend existing-row SELECT to include the four grouping columns.

3. **Insert path** (no existing row): use kwargs when provided, else `seed_values_for_task_key(task_key)` (import from migration module or re-export thin wrapper in `database.py`).

4. **Content-changed versioning path**: copy forward grouping fields from retired row unless kwargs override.

5. **In-place update path** (no prompt segment change): apply grouping updates alongside `agent_id` / `run_next`; coerce `task_seq` with `float(...)` when provided; strip strings; allow empty strings; do **not** set `content_changed`.

6. Extend public `save_agent_task(...)` to accept and forward the four kwargs.

7. In `list_candidate_tasks`, add the four columns to SELECT.

8. `apply_agent_task_copy_upsert`: new columns flow automatically via `table_columns(conn, "agent_task")` once schema exists.

## Stage 3: Admin API — Manage Tasks save/load paths

**Done when:** `GET/PUT /api/admin/tasks/<task_key>` and `GET /api/admin/tasks` expose grouping metadata from DB; backward-compat `phase`/`seq` keys come from DB (not config) until AST-739 switches the frontend.

1. In `src/ui/api/api_admin.py`, add helper `_grouping_from_agent_task_row(task: dict | None, task_key: str) -> dict`:
   ```python
   {
       "task_group_order": ...,
       "task_group_name": ...,
       "task_seq": ...,  # float
       "task_name": ...,
       "phase": task_group_name if task_group_name and task_group_name != "(unassigned)" else None,
       "seq": task_seq if task_seq != 999.0 else None,
   }
   ```
   When `task` is None: empty strings, `task_seq=999.0`, `task_name=task_key`, `phase=None`, `seq=None`.

2. **`get_task`:** Remove `cfg.get("phase")` / `cfg.get("seq")` overlay. Merge `_grouping_from_agent_task_row(task, task_key)`. Keep `entity_type` from `TASK_CONFIG`.

3. **`update_task`:** Read optional body keys `task_group_order`, `task_group_name`, `task_seq`, `task_name` using `if "field" in body` pattern. Pass to `save_agent_task`. Coerce `task_seq` with `float(...)` when present (400 only on non-numeric). No business-rule validation.

4. Return merged `get_agent_task` + `_grouping_from_agent_task_row` after PUT.

5. **`_enrich_tasks`:** Remove `cfg.get("phase")` and `cfg.get("seq")`. Spread `_grouping_from_agent_task_row(t, task_key)` into each row (columns from `list_candidate_tasks` after Stage 2).

6. Do **not** change `_dispatch_task_key_form_meta` or `/dispatch_tasks/task_keys` (AST-739).

⚠️ **Decision:** AC #3 (edit modal exposes four fields) is API-ready here; React inputs land in **AST-739**. Verify with PUT then GET before closing.

## Stage 4: Manual verification (build-child)

**Done when:** Local admin API returns seeded grouping metadata and accepts edits.

1. Bootstrap or touch DB to trigger schema ensure + seed.
2. `GET /api/admin/tasks?candidate_id=<any>` — known key has `task_group_name` matching former config phase.
3. `PUT /api/admin/tasks/<key>` with altered grouping fields; `GET` confirms persistence.
4. Confirm `_enrich_tasks` / `get_task` no longer read `phase`/`seq` from `TASK_CONFIG`.

## Self-Assessment

**Scope:** `Single-Component` — `database.py`, one migration script, and `api_admin.py` Manage Tasks paths only.

**Conf:** `high` — Follows established `agent_task` column migration, metadata-only update, and admin enrichment patterns.

**Risk:** `Medium` — Wrong versioning (retire on metadata-only save or drop metadata on prompt edit) would lose operator grouping work; blast radius is admin task management only.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | `seed_values_for_task_key` shared by CLI seed, `sync_agent_tasks`, and new-row insert. |
| §2.1 config | Seed reads `TASK_CONFIG` once; runtime API reads DB for grouping. Config untouched (AST-740). |
| §3.3 imports | Lazy import in `_apply_ast738` avoids load-time cycle. |
| §3.5 naming | Snake_case fields match ticket spec. |

No conflicts requiring `conf-!!-NONE`.

---

## Review (build)

**Built:** `origin/sub/AST-734/AST-738-task-grouping-metadata-storage-and-seed` @ `1e6ab76` (`5b62160` data layer + seed, `1e6ab76` admin API).

**Out of build scope (Betty / qa-child):** component/API tests per build-child test-tree ban; React modal/list (AST-739).

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-734/AST-738-task-grouping-metadata-storage-and-seed` @ `e07e751`

### What's solid

| Area | Notes |
|------|--------|
| Plan fidelity | Stages 1–3 match plan: four columns, idempotent seed, `save`/`list`/`sync` paths, admin GET/PUT/`_enrich_tasks` from DB with backward-compat `phase`/`seq`. |
| Versioning (§2.6 / plan Risk) | `content_changed` excludes grouping-only edits; segment versioning copies grouping via `_resolved_grouping_fields`; tests lock both behaviors. |
| Boundaries (§5d) | No frontend, no `TASK_CONFIG` removal, no `_dispatch_task_key_form_meta` — sibling tickets untouched. |
| Layer / imports (§3.3) | Lazy `_task_grouping_seed_helpers()` documented in plan; `api_admin` uses `database` only. |
| Seed guard | Global `task_group_name != ''` skip matches plan; `sync_agent_tasks` pre-seeds inserts so fresh DBs need no second pass. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| advisory | `docs/features/interface/ast-740-remove-phase-and-seq-from-task-config.md` on this branch | Sibling AST-740 plan doc shipped with AST-738 commits — harmless doc-only; no code boundary leak. |
| advisory | `tests/component/data/database/test_agent_tasks.py` | Stray `# placeholder removed = "qualify_job_listings"` comment — cosmetic cleanup optional in resolve. |
| discuss | `backfill_task_grouping_metadata` guard | If an operator cleared **every** `current=1` row’s `task_group_name` to `''`, the next schema ensure would re-seed from config. AC allows invalid saves; confirm Susan is OK with that reset edge case or tighten guard later. |

### Recommended actions

| Action | Owner |
|--------|-------|
| Proceed to `resolve-child` — no fix-now blockers | Hedy |
| Optional: drop placeholder comment in test file | Hedy (resolve) |
| AST-739: wire React modal to four DB fields | Katherine |

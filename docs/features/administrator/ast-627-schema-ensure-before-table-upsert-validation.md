# AST-627 — Schema ensure before table upsert validation

**Linear:** [AST-627 — Schema ensure before table upsert validation](https://linear.app/astralcareermatch/issue/AST-627/schema-ensure-before-table-upsert-validation-table-upsert-ensure)  
**Parent:** [AST-626 — Table Upsert - ensure schema before running](https://linear.app/astralcareermatch/issue/AST-626/table-upsert-ensure-schema-before-running)  
**Publish ref:** `sub/AST-626/AST-627-schema-ensure-before-table-upsert-validation` (origin only)

## Summary

Susan syncs admin data between environments via **Table Upsert** (Copy Output JSON) and **config-table upsert** (`dispatch_task`, `agent_task`, `candidate`). Column validation runs against the target DB’s current `PRAGMA table_info` layout, but lazy `_ensure_*_schema` migrations only run when normal app code touches a table — not during upsert. On a lightly used database the table can exist with an older column set, so upsert fails with “columns must match exactly” even though deployed code knows the full schema. This ticket adds a data-layer registry mapping table names to existing lazy ensure handlers and invokes it **before** column validation in both upsert entry points, preserving all AST-373 / AST-464 merge semantics.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add `_UPSERT_LAZY_SCHEMA_HANDLERS` registry + public `ensure_table_schema_for_upsert(conn, table)`; call from `apply_config_table_upsert` before column comparison | data |
| `src/core/table_copy_upsert.py` | Call `ensure_table_schema_for_upsert` before `table_columns` / PK checks; remove ad-hoc `_ensure_agent_task_schema` inside the transaction | core |
| `tests/component/data/database/test_table_copy_upsert.py` | Stale-schema Copy Output upsert succeeds after ensure; genuine mismatch still errors; no-handler table unchanged | test (Betty manifest — engineer runs during test-child) |

No changes to `src/ui/`, allowlists, merge rules, or new migrations.

---

## Stage 1: Data-layer ensure registry and public entry point

**Done when:** `ensure_table_schema_for_upsert(conn, table)` exists in `database.py`, maps known upsert-eligible table names to existing `_ensure_*_schema` callables, no-ops for unknown tables, and is invoked at the top of `apply_config_table_upsert` before `table_columns` comparison.

1. In `src/data/database.py`, immediately after `ALLOWED_CONFIG_TABLES` (line ~264), add a private registry and public wrapper:

   ```python
   _UPSERT_LAZY_SCHEMA_HANDLERS: dict[str, Callable[[sqlite3.Connection], None]] = {
       "agent": _ensure_agent_schema,
       "agent_data": _ensure_agent_data_schema,
       "agent_responses": _ensure_agent_responses_schema,
       "agent_task": _ensure_agent_task_schema,
       "app_log": _ensure_app_log_schema,
       "board_search": _ensure_board_search_table,
       "board_search_run": _ensure_board_search_run_table,
       "candidate": _ensure_candidate_schema,
       "candidate_intake_session": _ensure_candidate_intake_session_table,
       "company": _ensure_company_schema,
       "company_job_scan": _ensure_company_job_scan_schema,
       "company_search_terms": _ensure_company_search_terms_table,
       "dispatch_ledger": _ensure_dispatch_ledger_schema,
       "dispatch_task": _ensure_dispatch_task_schema,
       "job": _ensure_job_schema,
   }
   ```

   ⚠️ **Decision:** Registry keys are **SQLite table names** only. Exclude `_ensure_timesheets_schema` (multi-table / rename logic, not a single upsert target name), `_ensure_company_candidate_fk` (FK constraint, not table DDL), and `_ensure_gaze_board_dispatch_tasks` (row seeding, not schema migration). Tables without a registry entry keep today’s behavior (AC5).

   **Import note:** `_ensure_*` functions are defined later in the same module — use forward references by defining the dict **after** all handler functions, or build the dict inside a lazy initializer. Prefer placing **`_UPSERT_LAZY_SCHEMA_HANDLERS`** and **`ensure_table_schema_for_upsert`** immediately **before** `apply_config_table_upsert` (~line 570) so all `_ensure_*` symbols exist. Do **not** move or rewrite any `_ensure_*` bodies.

2. Add public function (same placement):

   ```python
   def ensure_table_schema_for_upsert(conn: sqlite3.Connection, table: str) -> None:
       """Run idempotent lazy schema ensure for ``table`` when registered; no-op otherwise."""
       handler = _UPSERT_LAZY_SCHEMA_HANDLERS.get(table)
       if handler is not None:
           handler(conn)
   ```

3. In **`apply_config_table_upsert`**, as the **first** statement after the allowlist check (`if table not in ALLOWED_CONFIG_TABLES`), add:

   ```python
   ensure_table_schema_for_upsert(conn, table)
   ```

   Leave the existing `expected = table_columns(conn, table)` / column mismatch `ValueError` block unchanged (AC3).

4. Add `Callable` to typing imports if not already present.

5. **`python3 -m py_compile src/data/database.py`**

**Ritual:** commit `plan(AST-627): …` is plan-only; product commit during build-child: `code(AST-627): data-layer upsert schema ensure registry`.

---

## Stage 2: Core Copy Output path — ensure before validation

**Done when:** `apply_copy_output_table_upsert` runs lazy ensure before reading column layout; `agent_task` no longer calls `_ensure_agent_task_schema` inside `BEGIN IMMEDIATE`.

1. In `src/core/table_copy_upsert.py`, after JSON structural validation (after the `parsed_rows` loop, ~line 52) and **before** `database.table_columns(conn, table_name)` (~line 55), insert:

   ```python
   database.ensure_table_schema_for_upsert(conn, table_name)
   ```

   ⚠️ **Decision:** Ensure runs **before** `BEGIN IMMEDIATE` because existing `_ensure_*_schema` handlers call `conn.commit()` internally; calling ensure inside an open transaction would commit the upsert transaction early (today’s `agent_task` path has this smell).

2. Remove the block inside the transaction:

   ```python
   if table_name == "agent_task":
       database._ensure_agent_task_schema(conn)
       counts = ...
   ```

   Replace with:

   ```python
   if table_name == "agent_task":
       counts = database.apply_agent_task_copy_upsert(conn, parsed_rows)
   else:
       counts = database.apply_generic_table_copy_upsert(conn, table_name, parsed_rows)
   ```

   (Keep the `if/else` dispatch; only delete the ensure call.)

3. **`python3 -m py_compile src/core/table_copy_upsert.py`**

**Ritual:** `code(AST-627): ensure schema before copy-output upsert validation`

---

## Stage 3: Component tests for stale-schema upsert (Betty manifest / test-child)

**Done when:** Tests prove ensure runs before validation for Copy Output upsert; config-table path covered at data layer; existing AST-464 tests remain green.

Betty adds these to the **Tests Ready** manifest (engineer implements during **test-child** per ticket Notes). If Betty omits them, engineer adds only the cases below — do not expand scope.

1. In `tests/component/data/database/test_table_copy_upsert.py`, add **`test_copy_upsert_stale_dispatch_task_schema_ensure_before_validate`**:
   - Obtain connection from `sqlite_in_memory._get_connection()`.
   - Drop `dispatch_task` if present; create a **stale** table missing at least one column that `_ensure_dispatch_task_schema` adds on a modern DB (e.g. omit `score_floor` — confirm against `_ensure_dispatch_task_schema` in `database.py` at build time).
   - Reset module global `database._dispatch_task_schema_ensured = False` (and any related globals if ensure short-circuits).
   - Build a JSON payload row dict whose keys match **post-ensure** columns (read via `table_columns` after manually calling ensure once to learn expected layout, or hardcode from `_ensure_dispatch_task_schema` CREATE).
   - Call `apply_copy_output_table_upsert(table_name="dispatch_task", json_payload=...)`.
   - Assert `ok is True` and at least one of `inserted`/`updated`/`skipped` > 0.

2. Add **`test_copy_upsert_genuine_column_mismatch_after_ensure`**:
   - Use `sqlite_in_memory` with a normal table (e.g. `flat_ast464` pattern: `id TEXT PRIMARY KEY, body TEXT`).
   - Call upsert with an extra unknown key in the row dict (wrong keys vs schema).
   - Assert `ok is False` and error mentions columns / keys (existing validation path, AC3).

3. Add **`test_copy_upsert_no_handler_table_unchanged`**:
   - Create ad-hoc table `nopensure_ast627` with PK; upsert one row.
   - Assert success — proves absence of registry entry does not break generic upsert (AC5).

4. In `tests/component/data/database/test_schema.py`, add **`test_config_upsert_stale_candidate_schema_ensure_before_validate`**:
   - Stale `candidate` table missing a column `_ensure_candidate_schema` adds (e.g. `candidate_api_key`).
   - Reset `database._candidate_schema_ensured = False`.
   - Build `columns`/`rows` matching post-ensure layout; call `apply_config_table_upsert(conn, "candidate", columns, rows)`.
   - Assert `ok is True` in result.

5. Run manifest paths from **ASTRAL_TEST_BIBLE** § Copy Output upsert (`test_table_copy_upsert.py`, `test_schema.py` config upsert section) plus full file for regressions.

**Ritual:** `test(AST-627): stale-schema upsert ensure-before-validate coverage`

---

## Execution contract reminders

- Do **not** change upsert merge rules, allowlists, UI, or `_ensure_*` migration bodies.
- Do **not** add bootstrap/deploy ensure (AST-383).
- Blocking ambiguity → `🛑` comment on **AST-626** parent per plan-child execution contract.

---

## Self-Assessment

**Scope:** `Single-Component` — Two production modules (`database.py` registry + one call site, `table_copy_upsert.py` reorder/remove duplicate ensure) plus focused component tests; no UI or config changes.

**Conf:** `high` — Reuses existing `_ensure_*_schema` handlers and the partial `agent_task` pattern already in `table_copy_upsert.py`; registry + call-before-validate is straightforward with clear acceptance criteria from AST-626.

**Risk:** `Medium` — Upsert is Susan’s cross-environment admin workflow; a wrong registry mapping could run the wrong migration, but handlers are idempotent and we only invoke known table→handler pairs without changing merge semantics.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single registry + one public wrapper; removes duplicate `agent_task` ensure call in core. |
| §2.1 config | No config changes. |
| §2.4 batch | N/A — upsert batch paths unchanged. |
| §3.3 imports | Core imports `database.ensure_table_schema_for_upsert` only; UI unchanged. |
| §3.5 naming | `ensure_table_schema_for_upsert` follows existing `_ensure_*_schema` naming; snake_case preserved. |

No conflicts requiring `conf-!!-NONE`.

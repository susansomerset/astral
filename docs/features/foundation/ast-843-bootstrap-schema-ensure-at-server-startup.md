# AST-843 — Bootstrap schema ensure at server startup

**Linear:** [AST-843 — Bootstrap schema ensure at server startup](https://linear.app/astralcareermatch/issue/AST-843/bootstrap-schema-ensure-at-server-startup-database-updates-are-not)  
**Parent:** [AST-842 — Database updates are not running on production deployments](https://linear.app/astralcareermatch/issue/AST-842/database-updates-are-not-running-on-production-deployments)  
**Publish ref:** `origin/sub/AST-842/AST-843-bootstrap-schema-ensure-at-server-startup`

Production Railway can run dispatch against SQLite tables that never received lazy `_ensure_*_schema` migrations in that process. Susan confirmed production `company` is missing `batch_created_at` while localhost has it; `inflow_discovery` and company batch claim paths depend on that column. AST-626 fixed upsert-time ensure but explicitly did **not** run ensure at bootstrap. This ticket wires the existing upsert schema registry into `bootstrap_runtime()` so **every registered table** is migrated idempotently on each server start, **before** `sync_agent_tasks` and `start_scheduler`. Schema only — no data replacement. `agent_responses_legacy` drop stays deferred to AST-777.

## Out of scope (explicit)

| Item | Owner |
|------|--------|
| Data-layer module refactor / migration relocation | AST-777 |
| Upsert merge rules, Data Management UI, config-table push/pull semantics | AST-626 / AST-373 |
| Drop `agent_responses_legacy` or other legacy columns | AST-777 (Susan deferred) |
| Tables **not** in `_UPSERT_LAZY_SCHEMA_HANDLERS` (`rubric_vector`, `vector_feedback`, `anthropic_timesheets`, `agent_timesheets`, …) | Out of ticket — registry is the bootstrap scope Susan confirmed |
| `inflow_discovery` business logic beyond schema repair | This ticket |
| `tests/` / bible edits | Betty `merge-tests` manifest below |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add `ensure_all_upsert_registry_schemas_at_startup()`; company audit — add migration only if audit finds a canonical column gap | data |
| `src/core/bootstrap.py` | Call schema ensure after `apply_repo_admin_json_at_startup()`, before `sync_agent_tasks`; update module docstring | core |
| `src/ui/server.py` | Update bootstrap comment line to reflect new step (comment only) | ui |

**QA manifest (Betty — not engineer commits):** Extend `tests/component/core/test_bootstrap.py`:

1. **`TestBootstrapRuntime::test_runs_validation_sync_and_scheduler_in_order`** — insert `"schema_ensure"` in expected `calls` list **after** `"repo_json"` and **before** `"sync:..."`; monkeypatch `bootstrap_mod.database.ensure_all_upsert_registry_schemas_at_startup` to append `"schema_ensure"`.
2. **New describe `AST-843 bootstrap schema ensure`** in `tests/component/data/test_database.py` (or extend existing database schema tests if present): temp DB file → call `ensure_all_upsert_registry_schemas_at_startup()` twice → `PRAGMA table_info(company)` includes `batch_created_at`; second call is a no-op (no error, column count unchanged). Follow existing component data test patterns for `ASTRAL_DB_DIR` isolation.

Regression: existing `test_bootstrap.py` validation-branch tests unchanged; `server_client` conftest stub of `bootstrap_runtime` unchanged.

## Stage 1: Company-table lazy migration audit

**Done when:** Auditor (build agent) has verified `_ensure_company_schema` + `_ensure_company_candidate_fk` cover every canonical `company` column the running code expects on legacy DBs (including `batch_created_at`). Either (a) audit confirms no product delta needed, or (b) a missing `ALTER TABLE` migration is added in `_ensure_company_schema` before Stage 2.

1. Read `src/data/database.py` module header inventory for `company` and Susan's localhost column list from parent AST-842 **Original brief**: `short_name`, `state`, `company_name`, `company_website`, `job_site`, `batch_id`, `batch_created_at`, `company_data`, `agent_responses`, `created_at`, `updated_at`, `state_updated_at`, `candidate_id`, `last_scan_at`, `state_history`, `agent_responses_legacy`.

2. Trace `_ensure_company_schema` (~line 829):
   - Fresh `CREATE TABLE` path must include `batch_created_at TIMESTAMP`.
   - Legacy migration block must `ALTER TABLE company ADD COLUMN batch_created_at TIMESTAMP` when missing (duplicate-column errors swallowed per existing pattern).
   - Confirm migrations also exist for `last_scan_at`, `state_history`, `agent_responses_legacy` (already present ~lines 872–895).

3. Trace `_ensure_company_candidate_fk` (~line 2637): confirms `candidate_id` is added on legacy DBs missing it. Fresh-create path may omit `candidate_id` until FK ensure runs — acceptable because bootstrap Stage 3 calls the company upsert handler which invokes both functions.

4. Cross-check `_UPDATE_COMPANY_ALLOWED` (~line 823) includes `batch_created_at` and `candidate_id` — confirms runtime UPDATE paths expect these columns post-migration.

5. **If and only if** a canonical column from step 1 is missing from both CREATE and migration blocks, add an idempotent `ALTER TABLE company ADD COLUMN …` stanza in the legacy migration section of `_ensure_company_schema`, matching the existing `batch_created_at` try/except/`duplicate column name` pattern. Do **not** drop columns. Do **not** touch `agent_responses_legacy`.

6. If no gap: proceed to Stage 2 with **zero** Stage 1 product diff. Record "company audit clean" in the Stage 4 build completion Linear comment.

⚠️ **Decision:** Production symptom (missing `batch_created_at`) is explained by lazy ensure never running before dispatch — not by absent migration code. Expect Stage 1 to be verify-only; do not refactor `_ensure_company_schema` structure (AST-777 territory).

## Stage 2: Registry-wide bootstrap schema ensure (data layer)

**Done when:** `ensure_all_upsert_registry_schemas_at_startup()` exists, calls every `_UPSERT_LAZY_SCHEMA_HANDLERS` entry via `ensure_table_schema_for_upsert`, and `python3 -m py_compile src/data/database.py` passes.

1. In `src/data/database.py`, immediately **after** `ensure_table_schema_for_upsert` (~line 5958), add:

```python
def ensure_all_upsert_registry_schemas_at_startup() -> None:
    """Run idempotent lazy schema ensure for every upsert-registry table once at process bootstrap.

    Invokes existing ``_UPSERT_LAZY_SCHEMA_HANDLERS`` only — no parallel migration logic.
    Resets per-table ``_*_schema_ensured`` flags via ``ensure_table_schema_for_upsert`` so
    stale process-global shortcuts cannot skip DDL on a legacy DB file."""
    conn = _get_connection()
    try:
        for table in sorted(_UPSERT_LAZY_SCHEMA_HANDLERS):
            ensure_table_schema_for_upsert(conn, table)
    finally:
        conn.close()
```

2. Do **not** duplicate the handler map. Do **not** iterate tables outside `_UPSERT_LAZY_SCHEMA_HANDLERS`. Sorted key order is intentional (deterministic startup logs / debugging).

3. Do **not** add `commit()` wrapper — individual `_ensure_*` handlers commit when they ALTER; no-op paths may not commit, which matches upsert behavior today.

4. Propagate exceptions (`sqlite3.OperationalError`, `RuntimeError`, etc.) — bootstrap must fail-fast if schema ensure fails; do not catch-and-log-only.

⚠️ **Decision:** Reuse `ensure_table_schema_for_upsert` (flag reset + handler dispatch) rather than calling `_UPSERT_LAZY_SCHEMA_HANDLERS` values directly — same semantics as AST-626 upsert path, including company FK sub-ensure via `_ensure_company_table_for_upsert`.

**Registry tables covered (13 — source: `_UPSERT_LAZY_SCHEMA_HANDLERS` on `origin/dev`):**  
`agent`, `agent_data`, `agent_responses`, `agent_task`, `app_log`, `candidate`, `candidate_intake_session`, `company`, `company_job_scan`, `company_search_terms`, `dispatch_ledger`, `dispatch_task`, `job`.

## Stage 3: Wire into runtime bootstrap (core + ui comment)

**Done when:** `bootstrap_runtime()` order is validation → repo admin json → **schema ensure** → sync_agent_tasks → start_scheduler; module docstrings and `server.py` comment match; `python3 -m py_compile src/core/bootstrap.py src/ui/server.py` passes.

1. In `src/core/bootstrap.py`, update the module docstring (lines 5–7) to:

```
Order: ``_validate_runtime_coupling()`` → ``apply_repo_admin_json_at_startup()``
→ ``database.ensure_all_upsert_registry_schemas_at_startup()``
→ ``database.sync_agent_tasks(get_task_keys())`` → ``start_scheduler()``.
```

2. In `bootstrap_runtime()` (~line 44), insert the schema call **after** `apply_repo_admin_json_at_startup()` and **before** `database.sync_agent_tasks(...)`:

```python
def bootstrap_runtime() -> None:
    _validate_runtime_coupling()
    apply_repo_admin_json_at_startup()
    database.ensure_all_upsert_registry_schemas_at_startup()
    database.sync_agent_tasks(get_task_keys())
    start_scheduler()
```

3. In `src/ui/server.py`, update the bootstrap comment (~line 62) from:

```
# --- Runtime bootstrap (validation → agent_task sync → scheduler) ---
```

to:

```
# --- Runtime bootstrap (validation → repo json → schema ensure → agent_task sync → scheduler) ---
```

4. Do **not** change blueprint registration, Stytch wiring, static routes, or `if __name__ == "__main__"`.

⚠️ **Decision:** Schema ensure runs **after** repo admin JSON apply per Susan's ticket Notes for planning — even though some repo JSON paths touch `agent_task`. Do not reorder without `@susan` escalation on AST-842.

## Stage 4: Verification

**Done when:** Compile checks pass; layer grep unchanged for ui→data ban; optional local stale-DB smoke documented in build completion comment.

1. Compile:

```bash
python3 -m py_compile src/data/database.py src/core/bootstrap.py src/ui/server.py
```

2. Layer grep (must remain clean):

```bash
rg "from src.data|import database" src/ui/server.py
```

Expected: **no matches** (bootstrap stays in core).

3. Optional local smoke (when `ASTRAL_DB_DIR` points at a copy of production or a synthetic legacy DB **without** `batch_created_at` on `company`):

```bash
sqlite3 "$ASTRAL_DB_DIR/astral.db" "PRAGMA table_info(company);" | rg batch_created_at || echo "MISSING before"
cd src/ui && python3 -c "from src.core.bootstrap import bootstrap_runtime; bootstrap_runtime()" 2>/dev/null || true
sqlite3 "$ASTRAL_DB_DIR/astral.db" "PRAGMA table_info(company);" | rg batch_created_at
```

Expect `batch_created_at` present after bootstrap. Do **not** commit test DB files. Skip if env not configured — Betty component test covers the contract.

4. **Flask debug reloader:** unchanged from AST-654 — module-level bootstrap may run twice under Werkzeug reloader; schema ensure is idempotent.

## Execution contract (for build-child)

- Execute stages **in order**; one **`code(AST-843)`** commit per stage on **`epic worktree`**, publish each to **`origin/sub/AST-842/AST-843-bootstrap-schema-ensure-at-server-startup`** before the next stage.
- Do **not** add files beyond the plan table.
- Do **not** drop legacy columns or refactor `database.py` module layout.
- Blocking ambiguity → comment on **AST-842** parent with 🛑 template from **plan-child** §6.

## Self-Assessment

**Scope:** `Single-Component` — One new data-layer bootstrap entrypoint, one call site in `src/core/bootstrap.py`, and a comment tweak in `src/ui/server.py`; company audit is read-only unless a migration gap is found.

**Conf:** `high` — Reuses the existing `_UPSERT_LAZY_SCHEMA_HANDLERS` / `ensure_table_schema_for_upsert` machinery from AST-626; Susan confirmed registry scope and bootstrap ordering in AST-843 description.

**Risk:** `Medium` — Startup now touches all 13 registry tables on every process start; idempotent DDL should be safe, but a bug in ensure logic could block server boot — mitigated by fail-fast exceptions and existing per-table ensure patterns.

## Plan vs ASTRAL_CODE_RULES

| Rule | Compliance |
|------|------------|
| §3.3 ui imports | `server.py` still imports core only for bootstrap; no new `src.data` in ui |
| §3.3 core imports | `bootstrap.py` already imports `database`; one additional call — allowed |
| §2.1 config | No new config blocks; ensure uses existing data-layer handlers |
| Database table inventory (header) | No new tables; company audit preserves header authority |
| DRY §1.3 | Single registry loop — no duplicate migration logic |
| AST-626 boundary | Upsert paths unchanged; bootstrap adds the startup hook AST-626 explicitly excluded |

No conflicts requiring `conf-!!-NONE`.

## Review (build stub)

**Built:** `origin/sub/AST-842/AST-843-bootstrap-schema-ensure-at-server-startup` @ `ef2f5e6`.

**Stages delivered:**
- Stage 1: Company audit clean — `_ensure_company_schema` / `_ensure_company_candidate_fk` already cover `batch_created_at` and canonical columns; no product delta.
- Stage 2: `ensure_all_upsert_registry_schemas_at_startup()` in `src/data/database.py` — `375f454`.
- Stage 3: `bootstrap_runtime()` calls schema ensure before sync/scheduler; `server.py` comment updated — `ef2f5e6`.
- Stage 4: `py_compile` pass; `rg` clean (no `src.data` in `server.py`).

**Betty:** manifest at **Code Complete** — bootstrap ordering test + `ensure_all_upsert_registry_schemas_at_startup` idempotency on legacy `company` without `batch_created_at`.

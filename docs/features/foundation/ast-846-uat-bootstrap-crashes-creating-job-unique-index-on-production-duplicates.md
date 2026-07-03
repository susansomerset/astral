# AST-846 — UAT: bootstrap crashes creating job unique index on production duplicates

**Linear:** [AST-846 — UAT: bootstrap crashes creating job unique index on production duplicates](https://linear.app/astralcareermatch/issue/AST-846/uat-bootstrap-crashes-creating-job-unique-index-on-production-duplicates)  
**Parent:** [AST-842 — Database updates are not running on production deployments](https://linear.app/astralcareermatch/issue/AST-842/database-updates-are-not-running-on-production-deployments)  
**Publish ref:** `origin/sub/AST-842/AST-846-bootstrap-job-unique-index-dedup`

After **AST-843** shipped bootstrap schema ensure, Railway production gunicorn workers fail to boot: `ensure_all_upsert_registry_schemas_at_startup()` → `_ensure_job_schema` raises `sqlite3.IntegrityError: UNIQUE constraint failed: job.company, job.job_title, job.company_job_id` while creating **`idx_job_identity_unique`** (AST-732). Production SQLite still contains legacy duplicate complete identity triples that were never cleaned by the one-time **AST-729** migration script. This UAT fix dedupes those rows **inside `_ensure_job_schema` immediately before index creation**, using the same survivor rules as AST-729, so bootstrap is idempotent and the worker can start on every restart without a manual operator script.

## Out of scope (explicit)

| Item | Owner / reason |
|------|----------------|
| Company-table bootstrap ensure, registry loop, bootstrap ordering | **AST-843** — unchanged |
| Upsert merge rules, Data Management UI, table upsert validation | AST-373 / AST-626 / AST-637 |
| `database.py` module layout refactor, migration relocation | **AST-777** |
| Drop `agent_responses_legacy` or other legacy columns | **AST-777** / Susan deferred |
| `save_job` insert duplicate tolerance, ingest wiring | **AST-732** — unchanged |
| Post-qualify collision delete | **AST-733** — unchanged |
| Re-pointing or deleting related rows (`agent_data`, `agent_responses`, timesheets, ledger) for deleted job rows | AST-729 contract — still untouched |
| `tests/` / bible edits | Betty **`merge-tests`** manifest below |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Board placeholder DELETE + identity triple dedupe helpers; call both in `_ensure_job_schema` before `CREATE UNIQUE INDEX` when index missing | data |
| `scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py` | Live paths call new database helpers (DRY with bootstrap); dry-run preview logic unchanged | scripts |

**QA manifest (Betty — not engineer commits):** Add describe **`AST-846 job schema ensure dedupe before unique index`** in `tests/component/data/test_database.py`:

1. **Duplicate triples → index succeeds:** Temp in-memory DB via existing database test patterns → insert two `job` rows with identical complete `(company, job_title, company_job_id)` and different `astral_job_id` / `created_at` → call `_ensure_job_schema(conn)` → assert `idx_job_identity_unique` exists in `sqlite_master`; assert exactly one survivor row remains with earliest `created_at` (tie-break `astral_job_id ASC` when `created_at` equal).
2. **Board placeholders removed before index:** Insert two duplicate complete triple rows under `company='__board__indeed'` → `_ensure_job_schema(conn)` → assert zero `__board__%` job rows; index created without error.
3. **Idempotent second ensure:** After step 1, reset `db_mod._job_schema_ensured = False` → call `_ensure_job_schema(conn)` again → no error; row count unchanged; index still present.
4. **Incomplete triples untouched:** Insert two rows with same `company` but `company_job_id IS NULL` → `_ensure_job_schema(conn)` → both rows remain (partial index excludes them); no IntegrityError.
5. **Bootstrap registry path:** Temp DB with duplicate triples → call `ensure_all_upsert_registry_schemas_at_startup()` (monkeypatch `_get_connection` to temp DB per AST-843 patterns) → does not raise; survivor + index assertions same as (1).

Regression: existing AST-843 `TestAst843BootstrapSchemaEnsure` and AST-729 migration script component tests still pass (script live path behavior unchanged; dry-run tests unchanged).

## Stage 1: Identity dedupe + board cleanup helpers (data layer)

**Done when:** `_delete_board_placeholder_jobs(conn)` and `_dedupe_job_identity_triples(conn)` exist in `src/data/database.py`, match AST-729 survivor semantics, and `python3 -m py_compile src/data/database.py` passes. No `_ensure_job_schema` wiring yet.

1. Near module constant **`_JOB_IDENTITY_UNIQUE_INDEX`** (~line 157), add:

```python
_BOARD_PLACEHOLDER_COMPANY_LIKE = "__board__%"
```

Use the literal prefix **`__board__`** — same as `scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py` and test bible (AST-765 removed `BOARDS_CONFIG`).

2. Add **`_delete_board_placeholder_jobs(conn: sqlite3.Connection) -> int`** immediately **before** `_ensure_job_schema` (~line 1333):

```python
def _delete_board_placeholder_jobs(conn: sqlite3.Connection) -> int:
    """Remove decommissioned board-gaze placeholder job rows (AST-729 / AST-846)."""
    cursor = conn.execute(
        "DELETE FROM job WHERE company LIKE ?",
        (_BOARD_PLACEHOLDER_COMPANY_LIKE,),
    )
    deleted = cursor.rowcount or 0
    if deleted:
        conn.commit()
    return deleted
```

3. Add **`_dedupe_job_identity_triples(conn: sqlite3.Connection) -> int`** after step 2 helper. Port survivor logic from `scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py` **`find_duplicate_identity_groups`** + **`delete_jobs_by_astral_job_ids`** — inline in this helper (no new public API):

   - Find groups with SQL equivalent to script lines 71–84: `company`, `job_title`, `company_job_id` all non-NULL and non-empty after TRIM; `company NOT LIKE '__board__%'`; `GROUP BY … HAVING COUNT(*) > 1`.
   - For each group, select members `ORDER BY created_at ASC NULLS LAST, astral_job_id ASC`.
   - Keep index 0; **`DELETE FROM job WHERE astral_job_id IN (...)`** for remaining member ids.
   - `conn.commit()` after each group delete (or once at end — either is fine if committed before index create).
   - Return total rows deleted.
   - Do **not** log (data layer §1.5).
   - Do **not** catch-and-swallow delete errors.

4. Do **not** export helpers on `__all__`. Do **not** add config keys.

⚠️ **Decision:** Survivor rule matches AST-729 exactly (earliest `created_at`, `astral_job_id ASC` tie-break) so bootstrap cleanup and operator migration script stay consistent.

⚠️ **Decision:** Board placeholder DELETE runs as part of schema ensure prep, not only in the migration script — board-gaze is decommissioned (AST-766/765) and duplicate board triples would also block index creation.

## Stage 2: Wire dedupe into `_ensure_job_schema` before unique index

**Done when:** `_ensure_job_schema` deletes board placeholders and dedupes identity triples **only when** `idx_job_identity_unique` is missing, then creates the index without IntegrityError on legacy duplicate data; compile passes.

1. In `_ensure_job_schema`, locate the AST-732 index block (~lines 1374–1389):

```python
    idx_row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='index' AND name=?",
        (_JOB_IDENTITY_UNIQUE_INDEX,),
    ).fetchone()
    if idx_row is None:
        ...
```

2. **Inside** `if idx_row is None:` and **before** `CREATE UNIQUE INDEX`, insert:

```python
        _delete_board_placeholder_jobs(conn)
        _dedupe_job_identity_triples(conn)
```

3. Keep existing **`CREATE UNIQUE INDEX`** SQL unchanged (partial index on complete triples — AST-732).

4. Keep **`conn.commit()`** after successful index create.

5. Do **not** swallow **`IntegrityError`** on index create — if dedupe + board delete still leave duplicates, fail-fast (operator escalation). Do **not** wrap index create in try/except.

6. Do **not** run dedupe when index already exists (idempotent no-op on warm DBs).

7. Add one inline comment above the new calls:

```python
        # AST-846: production legacy duplicates block idx_job_identity_unique; dedupe before create (AST-729 rules).
```

⚠️ **Decision:** Dedupe runs inside lazy `_ensure_job_schema`, not only in `ensure_all_upsert_registry_schemas_at_startup` — any code path that first creates the index on a legacy DB is safe (bootstrap, upsert ensure, migration script via `_ensure_job_schema`).

## Stage 3: DRY migration script with database helpers

**Done when:** `scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py` live runs delegate to `_delete_board_placeholder_jobs` / `_dedupe_job_identity_triples`; dry-run behavior and CLI unchanged; `python3 -m py_compile scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py` passes.

1. In script imports from `src.data.database`, add **`_delete_board_placeholder_jobs`**, **`_dedupe_job_identity_triples`**.

2. In **`run_board_gaze_cleanup`**, when **`not dry_run`**, replace inline `DELETE FROM job WHERE company LIKE ?` with:

```python
            deleted = _delete_board_placeholder_jobs(conn)
            counts["board_jobs_deleted"] = deleted
            counts["board_jobs_scanned"] = deleted  # live run: deleted count is sufficient for summary
```

   Keep dry-run branch unchanged (COUNT + print preview).

3. In **`run_identity_dedupe`**, when **`not dry_run`**, after `_ensure_job_schema(conn)`:

   - Option A (preferred): call **`deleted = _dedupe_job_identity_triples(conn)`** and set **`counts["dedupe_deleted"] = deleted`**, **`counts["dedupe_groups"]`** from a pre-dedupe dry query using existing **`find_duplicate_identity_groups`** for logging only, OR
   - Replace per-group loop body with a single **`_dedupe_job_identity_triples(conn)`** call; keep **`find_duplicate_identity_groups`** for dry-run and for live-run print lines (query groups first, print survivor plan, then call dedupe helper).

4. Keep **`find_duplicate_identity_groups`**, **`delete_jobs_by_astral_job_ids`**, and dry-run paths in the script for operator preview — do **not** remove CLI flags.

5. Do **not** change script module docstring operator order (backup → dry-run → live).

⚠️ **Decision:** Script remains the operator-facing tool; bootstrap path shares the same delete/dedupe implementation to prevent drift (§1.3 DRY).

## Stage 4: Verification

**Done when:** Compile checks pass; optional local smoke documented in build completion comment.

1. Compile:

```bash
python3 -m py_compile src/data/database.py scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py
```

2. Optional local smoke (when `ASTRAL_DB_DIR` has a copy with known duplicate triples and **without** `idx_job_identity_unique`):

```bash
sqlite3 "$ASTRAL_DB_DIR/astral.db" "
  SELECT company, job_title, company_job_id, COUNT(*) c
  FROM job
  WHERE company_job_id IS NOT NULL AND TRIM(company_job_id) != ''
    AND job_title IS NOT NULL AND TRIM(job_title) != ''
  GROUP BY 1,2,3 HAVING c > 1 LIMIT 5;"
python3 -c "
from src.data.database import _get_connection, _ensure_job_schema
c = _get_connection()
try:
    _ensure_job_schema(c)
finally:
    c.close()
"
sqlite3 "$ASTRAL_DB_DIR/astral.db" "SELECT name FROM sqlite_master WHERE name='idx_job_identity_unique';"
```

Expect index present after run; duplicate group count drops to zero for complete triples. Skip if env not configured — Betty component tests cover the contract.

3. Confirm **`ensure_all_upsert_registry_schemas_at_startup()`** still iterates sorted registry only — no change to AST-843 function body.

## Execution contract (for build-child)

- Execute stages **in order**; one **`code(AST-846)`** commit per stage on **`epic worktree`**, publish each to **`origin/sub/AST-842/AST-846-bootstrap-job-unique-index-dedup`** before the next stage.
- Do **not** add files beyond the plan table.
- Do **not** change AST-843 bootstrap ordering or company ensure paths.
- Blocking ambiguity → comment on **AST-842** parent with 🛑 template from **plan-child** §6.

## Self-Assessment

**Scope:** `Single-Component` — Two new private helpers and a guarded pre-index block in `src/data/database.py`, plus a thin DRY refactor of the existing AST-729 migration script; no core, UI, or bootstrap ordering changes.

**Conf:** `high` — Root cause is confirmed (AST-732 index create on uncleansed duplicates); AST-729 survivor SQL and board prefix already exist in the migration script and component tests; wiring point in `_ensure_job_schema` is explicit.

**Risk:** `Medium` — Bootstrap now DELETEs duplicate job rows on first index migration in a process; wrong survivor logic would drop the wrong `astral_job_id`, but rules match shipped AST-729; related tables remain orphaned by design (same as AST-729).

## Plan vs ASTRAL_CODE_RULES

| Rule | Compliance |
|------|------------|
| §1.3 DRY | Shared dedupe helpers used by bootstrap and migration script |
| §1.5 data layer | Helpers raise on failure; no logging added |
| §2.1 config | No new config blocks; `__board__` literal matches existing migration script |
| §3.3 imports | Script already imports `database`; no new cross-layer violations |
| Database header inventory | No new tables or columns |
| AST-732 boundary | Index SQL unchanged; insert bounce behavior unchanged |
| AST-843 boundary | Bootstrap registry loop unchanged; only `_ensure_job_schema` behavior extended |

No conflicts requiring `conf-!!-NONE`.

## Review (build stub)

**Built:** `origin/sub/AST-842/AST-846-bootstrap-job-unique-index-dedup` @ `cef6c09`

**Stages delivered:**
- Stage 1: `_delete_board_placeholder_jobs` + `_dedupe_job_identity_triples` in `src/data/database.py` — `826d8c9`.
- Stage 2: `_ensure_job_schema` calls board cleanup + identity dedupe before `idx_job_identity_unique` CREATE — `1837eae`.
- Stage 3: `cleanup_duplicate_and_board_gaze_jobs.py` live paths delegate to database helpers — `cef6c09`.
- Stage 4: `python3 -m py_compile` pass on `database.py` + migration script.

**Betty:** manifest at **Code Complete** — `TestAst846JobSchemaEnsureDedupeBeforeUniqueIndex` in `tests/component/data/test_database.py` (5 cases per plan).

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-842/AST-846-bootstrap-job-unique-index-dedup` @ `277fbe8`  
**Session:** `97db2d6d-6e0c-4489-9e48-01cbeada3930`

### What's solid

- Stages 1–3 match plan: `_delete_board_placeholder_jobs` / `_dedupe_job_identity_triples` in `src/data/database.py`; wired only when `idx_job_identity_unique` is missing; migration script live paths delegate to the same helpers (§1.3 DRY).
- Survivor SQL aligns with AST-729 (`created_at ASC NULLS LAST`, `astral_job_id ASC` tie-break); partial unique index SQL unchanged (AST-732 boundary held).
- Data layer discipline: no logging, no try/except swallow on delete or index create; fail-fast preserved.
- AST-843 boundary intact — `ensure_all_upsert_registry_schemas_at_startup` unchanged; `ensure_table_schema_for_upsert` resets `_job_schema_ensured` so bootstrap path exercises dedupe (`test_bootstrap_registry_path`).
- Component tests: `TestAst846JobSchemaEnsureDedupeBeforeUniqueIndex` (5/5) + AST-843 / AST-729 regression green locally.

### Issues

| Severity | Item | Location |
| --- | --- | --- |
| — | None | — |

### Recommended actions

| Severity | Item | Location |
| --- | --- | --- |
| advisory | Manifest tie-break (`created_at` equal → `astral_job_id ASC`) not an explicit test case; covered by shared ORDER BY in helper | `tests/component/data/test_database.py` |
| advisory | No-filter live migration run prints per-group `deleted` before bulk `_dedupe_job_identity_triples` at loop end — operator log timing only | `scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py` `run_identity_dedupe` |

## Resolution (Hedy)

**Resolved:** 2026-07-03 · publish ref @ `522723d`

Radia **Review Posted** @ `277fbe8`: **fix-now** and **discuss** empty; advisory items (tie-break test gap, migration log timing) accepted per plan — no additional product changes required.

**Shipped:**
- `src/data/database.py` — `_delete_board_placeholder_jobs` + `_dedupe_job_identity_triples`; `_ensure_job_schema` runs both before `idx_job_identity_unique` CREATE when index missing.
- `scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py` — live paths delegate to database helpers (DRY).

**§9a dry-run:** `origin/sub/AST-842/AST-846-bootstrap-job-unique-index-dedup` merges cleanly into `origin/dev` and `origin/ftr/AST-842-production-schema-ensure-on-bootstrap`.

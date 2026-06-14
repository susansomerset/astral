# AST-637 — UAT: company table upsert wrong-keys after AST-629

**Linear:** [AST-637 — UAT: company table upsert wrong-keys after AST-629](https://linear.app/astralcareermatch/issue/AST-637/uat-company-table-upsert-wrong-keys-after-ast-629)  
**Parent:** [AST-626 — Table Upsert - ensure schema before running](https://linear.app/astralcareermatch/issue/AST-626/table-upsert-ensure-schema-before-running)  
**Publish ref:** `sub/AST-626/AST-637-uat-company-table-upsert-wrong-keys-after-ast-629` (origin only)

## Summary

AST-627/629 fixed upsert schema ensure for most registry tables (including clearing stale process-global flags in AST-629), but **`company` upsert still fails with `columns must exactly match table layout (wrong keys)`** when Copy Output rows carry the full 16-column layout Susan sees on staging (`candidate_id`, `agent_responses_legacy`, etc.). Root cause: `_UPSERT_LAZY_SCHEMA_HANDLERS["company"]` points at **`_ensure_company_schema` only**. AST-627 deliberately excluded `_ensure_company_candidate_fk` (mislabeled “FK constraint, not table DDL”) even though that function **ADD COLUMN candidate_id**. **`agent_responses_legacy`** is never added by any lazy ensure in `database.py` (only by the one-off `scripts/migrations/migrate_agent_data.py` archive step). After ensure, `table_columns` on a stale target is missing those columns while paste keys include them → `_validate_copy_row_keys` rejects. This bug chains the existing company ensure functions on the upsert path and adds idempotent `agent_responses_legacy` DDL to `_ensure_company_schema` (column add only — no archive UPDATE).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | `_ensure_company_table_for_upsert` wrapper; `agent_responses_legacy` in company DDL/migration; registry + flag map for company | data |
| `tests/component/data/database/test_table_copy_upsert.py` | Regression: stale `company` missing `candidate_id` + `agent_responses_legacy` → upsert succeeds | test (Betty manifest — engineer runs during test-child) |

No changes to `src/core/table_copy_upsert.py`, UI, allowlists, merge rules, or `migrate_agent_data.py` data archive behavior.

---

## Stage 1: Complete company schema ensure on upsert path

**Done when:** `ensure_table_schema_for_upsert(conn, "company")` leaves the connection’s `company` table with the same column set Copy Output expects (including `candidate_id` and `agent_responses_legacy`) before `table_columns` / `_validate_copy_row_keys`.

1. In `src/data/database.py`, immediately **after** `_ensure_company_candidate_fk` (~line 2378), add a private upsert-only orchestrator:

   ```python
   def _ensure_company_table_for_upsert(conn: sqlite3.Connection) -> None:
       """Run all lazy company DDL needed before Copy Output key validation."""
       _ensure_company_schema(conn)
       _ensure_company_candidate_fk(conn)
   ```

   ⚠️ **Decision:** Upsert uses a dedicated wrapper instead of expanding `_ensure_company_schema` to call FK ensure everywhere — normal app paths keep today’s `_ensure_company_schema`-only call sites; upsert registry gets the full chain AST-627 omitted.

2. In `_ensure_company_schema`, add **`agent_responses_legacy`** using the same idempotent ALTER pattern as `state_history` / `last_scan_at`:

   - In the **`CREATE TABLE company`** DDL (~line 657), add a line after `agent_responses TEXT DEFAULT '[]',`:

     ```sql
     agent_responses_legacy TEXT,
     ```

   - In the **`else`** migration branch (after the `state_history` block, before `_company_schema_ensured = True`), add:

     ```python
     if "agent_responses_legacy" not in cols:
         try:
             conn.execute("ALTER TABLE company ADD COLUMN agent_responses_legacy TEXT")
             conn.commit()
         except sqlite3.OperationalError as e:
             if "duplicate column name" not in str(e).lower():
                 raise
     ```

   ⚠️ **Decision:** Column add only — do **not** run `migrate_agent_data.py` archive UPDATE (reset `agent_responses` to `'[]'`). Upsert paste carries explicit values; archive is a separate migration concern.

3. In `_UPSERT_LAZY_SCHEMA_HANDLERS` (~line 5032), change:

   ```python
   "company": _ensure_company_schema,
   ```

   to:

   ```python
   "company": _ensure_company_table_for_upsert,
   ```

4. In `_UPSERT_SCHEMA_ENSURE_FLAGS` (~line 5011), change:

   ```python
   "company": ("_company_schema_ensured",),
   ```

   to:

   ```python
   "company": ("_company_schema_ensured", "_company_candidate_fk_ensured"),
   ```

   so AST-629 flag clearing resets both globals before the wrapper runs.

5. `python3 -m py_compile src/data/database.py`

**Ritual:** `code(AST-637): company upsert ensure adds candidate_id and agent_responses_legacy columns`

---

## Stage 2: Regression test — stale company missing upsert columns (Betty manifest / test-child)

**Done when:** Component test proves Copy Output upsert for `company` succeeds when the table exists with an older DDL missing `candidate_id` and `agent_responses_legacy`, and row keys match post-ensure layout.

Betty adds to **Tests Ready** manifest. If omitted, engineer adds only the case below.

1. In `tests/component/data/database/test_table_copy_upsert.py`, add class **`TestAst637CompanyUpsertSchemaEnsure`** (or extend `TestAst627EnsureBeforeValidate`) with **`test_copy_upsert_stale_company_missing_candidate_and_legacy_columns`**:

   - Use `sqlite_in_memory`.
   - `DROP TABLE IF EXISTS company`; create **stale** DDL matching pre-migration layout — include columns through `state_history` but **omit** `candidate_id` and `agent_responses_legacy` (mirror `_ensure_company_schema` CREATE minus those two).
   - On a throwaway connection, call `_ensure_company_table_for_upsert` (or `ensure_table_schema_for_upsert(conn, "company")`) and read `cols = db.table_columns(conn, "company")`.
   - Build one row dict `{c: None for c in cols}`; set required PK/non-null fields: `short_name`, `state` (e.g. `"komodohealth"`, `"NEW"`).
   - Optionally set `db._company_schema_ensured = True` and `db._company_candidate_fk_ensured = True` **immediately before** upsert (AST-629 regression combo) — assert upsert still succeeds.
   - Call `apply_copy_output_table_upsert(table_name="company", json_payload=json.dumps([row]))`.
   - Assert `out["ok"]` and `inserted + updated + skipped > 0`.

2. Re-run manifest paths from **ASTRAL_TEST_BIBLE** § Copy Output upsert (`test_table_copy_upsert.py`).

**Ritual:** `test(AST-637): company upsert ensure before validate stale columns`

---

## Execution contract reminders

- Do **not** revert AST-627 registry, AST-629 flag clearing, or remove `ensure_table_schema_for_upsert` call sites.
- Do **not** change upsert merge rules, allowlists, UI, or invoke `migrate_agent_data.py` from upsert.
- Genuine wrong keys after full ensure (extra/missing keys vs real schema) must still fail — keep `test_copy_upsert_genuine_column_mismatch_after_ensure`.
- Blocking ambiguity → `🛑` comment on **AST-626** parent per plan-child execution contract.

---

## Self-Assessment

**Scope:** `Single-Component` — Company upsert ensure chain + one column migration in `_ensure_company_schema`; one focused component test.

**Conf:** `high` — AST-627/629 established the upsert ensure pattern; Susan’s repro keys match columns missing from the current company handler; fix reuses existing `_ensure_company_candidate_fk` and mirrors existing ALTER patterns for `agent_responses_legacy`.

**Risk:** `Medium` — Table Upsert is Susan’s cross-environment admin path; incomplete ensure leaves wrong-keys; over-broad DDL changes could affect normal company paths — wrapper limits FK ensure to upsert registry only, and legacy column add is idempotent ALTER only.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses `_ensure_company_schema`, `_ensure_company_candidate_fk`; wrapper avoids duplicating ALTER logic. |
| §2.1 config | No config changes. |
| §2.4 batch | Company batch/claim paths unchanged; upsert-only wrapper. |
| §3.3 imports | Data-layer only. |
| §3.5 naming | `_ensure_company_table_for_upsert` matches existing `_ensure_*` convention. |

No conflicts requiring `conf-!!-NONE`.

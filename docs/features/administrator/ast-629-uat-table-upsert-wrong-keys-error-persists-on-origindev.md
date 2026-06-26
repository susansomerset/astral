# AST-629 — UAT: Table upsert wrong-keys error persists on origin/dev

**Linear:** [AST-629 — UAT: Table upsert wrong-keys error persists on origin/dev](https://linear.app/astralcareermatch/issue/AST-629/uat-table-upsert-wrong-keys-error-persists-on-origindev)  
**Parent:** [AST-626 — Table Upsert - ensure schema before running](https://linear.app/astralcareermatch/issue/AST-626/table-upsert-ensure-schema-before-running)  
**Publish ref:** `sub/AST-626/AST-629-uat-table-upsert-wrong-keys-error-persists-on-origindev` (origin only)

## Summary

AST-627 correctly calls `ensure_table_schema_for_upsert` before `table_columns` / `_validate_copy_row_keys`, but Susan still sees `columns must exactly match table layout (wrong keys)` on **origin/dev** when pasting same-version Copy Output into a target whose table layout is behind the deployed code. Root cause: each `_ensure_*_schema` handler short-circuits on **process-global** `_*_schema_ensured` flags. If the flag is already `True` in the running interpreter (prior request, import side path, or DB file swap without process restart) while the **current** SQLite file still has a stale table, `ensure_table_schema_for_upsert` becomes a no-op, `table_columns` returns the old column set, and row keys from Copy Output (full schema) fail `_validate_copy_row_keys`. AST-627 tests always reset flags via `sqlite_in_memory` and explicit `monkeypatch` — they never exercised “flag already True + stale table”. This bug clears the relevant flag(s) inside `ensure_table_schema_for_upsert` before invoking the registered handler so upsert always runs idempotent migrations against the connection’s current DB file.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Map upsert registry tables → ensure flags; clear flags before handler in `ensure_table_schema_for_upsert` | data |
| `tests/component/data/database/test_table_copy_upsert.py` | Regression: stale table + flag already True → upsert succeeds | test (Betty manifest — engineer runs during test-child) |
| `tests/component/data/database/test_schema.py` | Same regression for `apply_config_table_upsert` on `candidate` (optional mirror of AST-627 stale test) | test |

No changes to `src/core/table_copy_upsert.py`, UI, allowlists, merge rules, or `_ensure_*` migration bodies.

---

## Stage 1: Force lazy ensure on upsert path (clear process flags)

**Done when:** `ensure_table_schema_for_upsert` always runs the registered handler’s migration logic against the target connection, even when `_*_schema_ensured` was already set `True` earlier in the same Python process.

1. In `src/data/database.py`, immediately above `_UPSERT_LAZY_SCHEMA_HANDLERS` (~line 5000), add a private map from registry table name → tuple of module-level flag attribute names to reset before ensure:

   ```python
   _UPSERT_SCHEMA_ENSURE_FLAGS: dict[str, tuple[str, ...]] = {
       "agent": ("_agent_schema_ensured",),
       "agent_data": ("_agent_data_schema_ensured",),
       "agent_responses": ("_agent_responses_schema_ensured",),
       "agent_task": ("_agent_task_schema_ensured",),
       "app_log": ("_app_log_schema_ensured",),
       "board_search": ("_board_search_schema_ensured",),
       "board_search_run": ("_board_search_run_schema_ensured",),
       "candidate": ("_candidate_schema_ensured",),
       "candidate_intake_session": ("_intake_session_schema_ensured",),
       "company": ("_company_schema_ensured",),
       "company_job_scan": ("_company_job_scan_schema_ensured",),
       "company_search_terms": (
           "_company_search_terms_schema_ensured",
           "_company_search_terms_migration_swept",
       ),
       "dispatch_ledger": ("_dispatch_ledger_schema_ensured",),
       "dispatch_task": ("_dispatch_task_schema_ensured",),
       "job": ("_job_schema_ensured",),
   }
   ```

   ⚠️ **Decision:** Keys mirror `_UPSERT_LAZY_SCHEMA_HANDLERS` exactly. `company_search_terms` clears both `_company_search_terms_schema_ensured` and `_company_search_terms_migration_swept` because `_ensure_company_search_terms_table` gates on both globals.

2. Replace the body of `ensure_table_schema_for_upsert` (~line 5020) with:

   ```python
   def ensure_table_schema_for_upsert(conn: sqlite3.Connection, table: str) -> None:
       """Run idempotent lazy schema ensure for ``table`` when registered; no-op otherwise.

       Upsert must not trust process-global ``_*_schema_ensured`` shortcuts: the target DB file
       may be stale while flags were set by a prior request or DB swap in the same process."""
       handler = _UPSERT_LAZY_SCHEMA_HANDLERS.get(table)
       if handler is None:
           return
       for flag_name in _UPSERT_SCHEMA_ENSURE_FLAGS.get(table, ()):
           globals()[flag_name] = False
       handler(conn)
   ```

   Do **not** change any `_ensure_*_schema` function bodies or remove their global flags (normal app paths keep the performance shortcut).

3. `python3 -m py_compile src/data/database.py`

**Ritual:** `code(AST-629): upsert schema ensure ignores stale process flags`

---

## Stage 2: Regression tests — flag True + stale table (Betty manifest / test-child)

**Done when:** Component tests prove Copy Output upsert succeeds when the stale-table scenario is combined with `_dispatch_task_schema_ensured = True` (no monkeypatch reset before upsert). Existing AST-627 stale tests remain green.

Betty adds these to the **Tests Ready** manifest. If omitted, engineer adds only the cases below.

1. In `tests/component/data/database/test_table_copy_upsert.py`, inside `TestAst627EnsureBeforeValidate` (or new `TestAst629UpsertFlagBypass`), add **`test_copy_upsert_stale_dispatch_task_when_schema_flag_already_true`**:
   - Use `sqlite_in_memory` (fixture resets flags at start — that is fine).
   - Create stale `dispatch_task` table **missing** at least one column `_ensure_dispatch_task_schema` adds (same DDL as `test_copy_upsert_stale_dispatch_task_schema_ensure_before_validate` — omit `score_floor`).
   - Build row dict whose keys match **post-ensure** layout (call `_ensure_dispatch_task_schema` once on a throwaway connection to learn `table_columns`, or reuse the learn-block pattern from AST-627 test).
   - Set `db._dispatch_task_schema_ensured = True` **immediately before** `apply_copy_output_table_upsert` — do **not** set it back to `False`.
   - Assert `out["ok"]` and `inserted + updated + skipped > 0`.

   ⚠️ **Decision:** This is the regression AST-627 missed: ensure hook present but global flag prevents migration on stale file.

2. (Recommended) In `tests/component/data/database/test_schema.py`, add **`test_config_upsert_stale_candidate_when_schema_flag_already_true`** mirroring AST-627’s `test_config_upsert_stale_candidate_schema_ensure_before_validate` but set `db._candidate_schema_ensured = True` before `apply_config_table_upsert` without resetting.

3. Re-run manifest paths from **ASTRAL_TEST_BIBLE** § Copy Output upsert (`test_table_copy_upsert.py`, `test_schema.py` config upsert section).

**Ritual:** `test(AST-629): upsert ensure runs when process schema flags already true`

---

## Execution contract reminders

- Do **not** revert AST-627 registry or remove `ensure_table_schema_for_upsert` call sites.
- Do **not** change upsert merge rules, allowlists, UI, or bootstrap ensure (AST-383).
- Genuine wrong keys after ensure (extra/missing keys vs real schema) must still fail — AST-627 `test_copy_upsert_genuine_column_mismatch_after_ensure` stays valid.
- Blocking ambiguity → `🛑` comment on **AST-626** parent per plan-child execution contract.

---

## Self-Assessment

**Scope:** `Single-Component` — One behavioral change in `ensure_table_schema_for_upsert` plus flag map in `database.py`; focused component tests only.

**Conf:** `high` — AST-627 tests and code review show ensure runs before validate; the gap is global-flag short-circuit; fix is a small, explicit flag reset on the upsert-only entry point without rewriting migrations.

**Risk:** `Medium` — Table Upsert is Susan’s cross-environment admin path; clearing flags on upsert re-runs idempotent DDL checks (slight cost) but must not skip migrations on stale targets; wrong flag map would call wrong handler’s migrations (map mirrors existing registry).

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Flag map parallels `_UPSERT_LAZY_SCHEMA_HANDLERS`; no duplicate migration logic. |
| §2.1 config | No config changes. |
| §2.4 batch | Upsert batch paths unchanged. |
| §3.3 imports | Data-layer only; core/UI unchanged. |
| §3.5 naming | `_UPSERT_SCHEMA_ENSURE_FLAGS` matches existing `_UPSERT_LAZY_SCHEMA_HANDLERS` convention. |

No conflicts requiring `conf-!!-NONE`.

---

## Review

**Diff:** `origin/dev...origin/sub/AST-626/AST-629-uat-table-upsert-wrong-keys-error-persists-on-origindev`  
**Radia:** 2026-06-14 — clean

### What's solid

- Root-cause fix matches plan: `ensure_table_schema_for_upsert` clears process-global `_*_schema_ensured` (and `company_search_terms` sweep flag) before invoking the registered handler, so stale SQLite files cannot skip idempotent migrations when flags were set earlier in the same interpreter.
- `_UPSERT_SCHEMA_ENSURE_FLAGS` keys are **symmetric** with `_UPSERT_LAZY_SCHEMA_HANDLERS` (15 tables); no orphan entries.
- Scope stays inside `database.py`; no changes to merge rules, allowlists, UI, or `_ensure_*` bodies — aligns with ticket boundaries and AST-626 parent AC.
- Regression tests cover both Copy Output (`TestAst629UpsertFlagBypass`) and config upsert (`test_config_upsert_stale_candidate_when_schema_flag_already_true`) with flag pre-set `True` and stale DDL — the gap AST-627 missed.
- `_config_upsert_columns` helper in `test_schema.py` correctly routes column discovery through `ensure_table_schema_for_upsert`, keeping sibling config-upsert tests aligned with post-ensure layout.
- **ASTRAL_TEST_BIBLE** manifest updated; narrowed run **13 passed**.

### Issues

| Severity | Location | Note |
| --- | --- | --- |
| — | — | No fix-now or discuss items. |

### Recommended actions

- Proceed to **resolve-child** (no engineer changes required from this review).

---

## Resolution

**2026-06-14 — Ada (resolve-child)**

Radia review (`2c6c2400`): **0 fix-now · 0 discuss · 0 advisory** — no product changes required.

- Re-ran Betty manifest (13 passed) on publish ref tip `2c6c2400`.
- §9a dry-run: publish ref merges cleanly into `origin/dev` and `origin/ftr/ast-626-table-upsert-ensure-schema-before-running`.

**Ship tip:** `origin/sub/AST-626/AST-629-uat-table-upsert-wrong-keys-error-persists-on-origindev` @ `2c6c2400`

# AST-627 — Schema ensure before table upsert validation (Table Upsert - ensure schema before running)

<!-- linear-archive: AST-627 archived 2026-06-23 -->

## Linear archive (AST-627)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-627/schema-ensure-before-table-upsert-validation-table-upsert-ensure  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-626 — Table Upsert - ensure schema before running  
**Blocked by / blocks / related:** parent: AST-626

### Description

## What this implements

Run idempotent lazy schema ensure on the target table **before** column validation in both table upsert entry points: Data Management Copy Output upsert and config-table upsert (`dispatch_task`, `agent_task`, `candidate`). Introduce or use a data-layer registry that maps table names to existing `_ensure_*_schema` handlers; tables without a handler skip ensure. Preserve all AST-373 merge semantics (PK required, FK all-or-nothing, `agent_task` versioning, non-destructive merge).

## Acceptance criteria

1. On a database where a upsert-eligible table exists but lazy migrations have never run for that table, pasting valid Copy Output JSON from a same-version source via Data Management **Table Upsert** completes successfully (or fails only on real validation/constraint errors — not column mismatch caused by missing ALTER columns).
2. Pushing or pulling `dispatch_task`, `agent_task`, or `candidate` between local and staging succeeds when the target table was previously "fresh" (no prior code path had triggered ensure for that table).
3. After ensure runs, if columns still differ (genuine skew), Susan sees the existing explicit mismatch error with got vs expected column lists — not a silent partial write.
4. `agent_task` upsert still honors Manage Tasks versioning: unchanged historical rows are no-ops; changed content creates new versions as today.
5. Tables without a lazy ensure handler upsert exactly as they do now.

## Boundaries

* Does **not** change upsert merge rules, allowlists, or Data Management UI layout.
* Does **not** invent new migrations — only invokes existing `_ensure_*_schema` logic.
* Does **not** add bootstrap/deploy ensure (AST-383).
* Does **not** add a standalone "migrate schema only" admin action.

## Notes for planning

* Primary touch: `src/data/database.py` (config upsert path + ensure registry), `src/core/table_copy_upsert.py` (generic upsert path). `agent_task` already calls `_ensure_agent_task_schema` in one path — generalize pattern.
* Tests: `tests/component/data/database/test_table_copy_upsert.py` and admin API tests per ASTRAL_TEST_BIBLE.
* Layer law: data owns ensure registry; core orchestrator calls it before validation.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/ast-626-table-upsert-ensure-schema-before-running`, child `sub/AST-626/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-06-14T06:05:33.951Z
**Diff:** `origin/dev...origin/sub/AST-626/AST-627-schema-ensure-before-table-upsert-validation` (`1f9d2ec0`)

### What's solid

- Registry + `ensure_table_schema_for_upsert` in data layer; config upsert calls ensure after allowlist, before column compare.
- Copy Output path ensures before `table_columns` / PK validation; removed in-transaction `_ensure_agent_task_schema` (correct — handlers commit internally).
- Registry matches plan (15 table handlers; excluded timesheets / FK-only / standalone gaze seeding).
- §3.3 layer law holds (core → public data API only); no data-layer logging added.
- `TestAst627EnsureBeforeValidate` + config stale-candidate test cover AC1–AC5; Betty bible §7.13zzl manifest aligned.

### Issues

**0 fix-now · 0 discuss · 0 advisory**

Doc: `docs/features/administrator/ast-627-schema-ensure-before-table-upsert-validation.md` (Review section)

#### betty — 2026-06-14T06:02:53.226Z
## QA test manifest (AST-627)

**Publish ref:** `origin/sub/AST-626/AST-627-schema-ensure-before-table-upsert-validation` @ `645f12ee`  
**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `284eb9e27286409be073926e83046f09d50e97ed` (**§7.13zzl**)

### Existing coverage (run for regressions)

1. **`tests/component/data/database/test_table_copy_upsert.py`** — full file (AST-464 Copy Output upsert: malformed JSON, PK/FK, generic/agent_task paths).
2. **`tests/component/data/database/test_schema.py::TestApplyConfigTableUpsert`** — config-table upsert validation + candidate/dispatch_task/agent_task paths (minus new stale-schema test below if duplicative).

### New / expanded (AST-627)

3. **`tests/component/data/database/test_table_copy_upsert.py::TestAst627EnsureBeforeValidate::test_copy_upsert_stale_dispatch_task_schema_ensure_before_validate`** — stale `dispatch_task` (missing `score_floor`); ensure runs before validate; upsert succeeds.
4. **`tests/component/data/database/test_table_copy_upsert.py::TestAst627EnsureBeforeValidate::test_copy_upsert_genuine_column_mismatch_after_ensure`** — wrong row keys after ensure → explicit column/key error (AC3).
5. **`tests/component/data/database/test_table_copy_upsert.py::TestAst627EnsureBeforeValidate::test_copy_upsert_no_handler_table_unchanged`** — unregistered table name; generic upsert unchanged (AC5).
6. **`tests/component/data/database/test_schema.py::TestApplyConfigTableUpsert::test_config_upsert_stale_candidate_schema_ensure_before_validate`** — stale `candidate` (missing `candidate_api_key`); config upsert path ensure-before-validate.

### Narrowed run

```bash
.venv/bin/python -m pytest \
  tests/component/data/database/test_table_copy_upsert.py::TestAst627EnsureBeforeValidate \
  tests/component/data/database/test_schema.py::TestApplyConfigTableUpsert::test_config_upsert_stale_candidate_schema_ensure_before_validate \
  tests/component/data/database/test_table_copy_upsert.py \
  tests/component/data/database/test_schema.py::TestApplyConfigTableUpsert \
  -q
```

Manifest-only for **`src/`** — product commits `ada989ae`, `b9a071a9` already on publish ref. **test-child** runs manifest; no new product work expected unless a test exposes a real bug.

#### ada — 2026-06-14T05:56:54.061Z
Plan: [`docs/features/administrator/ast-627-schema-ensure-before-table-upsert-validation.md`](https://github.com/susansomerset/astral/blob/sub/AST-626/AST-627-schema-ensure-before-table-upsert-validation/docs/features/administrator/ast-627-schema-ensure-before-table-upsert-validation.md)

**Approach:** Data-layer `_UPSERT_LAZY_SCHEMA_HANDLERS` registry + `ensure_table_schema_for_upsert(conn, table)`; invoke before column validation in `apply_config_table_upsert` and `apply_copy_output_table_upsert` (ensure moved before `BEGIN` / `table_columns`; remove duplicate `agent_task` ensure inside the transaction).

**Self-assessment**
- **Scope:** `Single-Component` — registry + two call sites + component tests; no UI or merge-rule changes.
- **Conf:** `high` — extends the existing partial `agent_task` ensure pattern with a explicit table→handler map.
- **Risk:** `Medium` — admin upsert path is critical, but handlers stay idempotent and merge semantics are untouched.

---

_Implementation detail may live in git history on `origin/dev`._

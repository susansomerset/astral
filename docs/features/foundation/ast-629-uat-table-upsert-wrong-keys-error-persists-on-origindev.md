# AST-629 — UAT: Table upsert wrong-keys error persists on origin/dev

<!-- linear-archive: AST-629 archived 2026-06-23 -->

## Linear archive (AST-629)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-629/uat-table-upsert-wrong-keys-error-persists-on-origindev  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-626 — Table Upsert - ensure schema before running  
**Blocked by / blocks / related:** parent: AST-626

### Description

## What failed

On **origin/dev** (post AST-627), Table Upsert still rejects valid Copy Output JSON with:

`columns must exactly match table layout (wrong keys)`

Susan reports the original staging/local sync issue **persists** after the schema-ensure fix shipped.

## Expected

Same-version Copy Output paste via Data Management **Table Upsert** completes successfully on a target where lazy migrations had not yet run — or fails only on real validation/constraint errors, not a wrong-keys rejection when source and target schemas match after ensure.

## Repro

1. Deploy or use environment on **origin/dev** (includes AST-627 ensure-before-validate).
2. On a target DB where upsert-eligible table(s) exist but lazy ensure has not run for that table (or reproduce Susan's local ↔ staging sync path).
3. Copy Output JSON from a same-version source for a config or admin table (e.g. `dispatch_task`, `agent_task`, or `candidate`).
4. Data Management → **Table Upsert** → paste JSON → submit.
5. Observe error: `columns must exactly match table layout (wrong keys)` (Susan confirmed on origin/dev).

## Parent AC (quoted inline)

> On a database where a upsert-eligible table exists but lazy migrations have never run for that table, pasting valid Copy Output JSON from a same-version source via Data Management **Table Upsert** completes successfully (or fails only on real validation/constraint errors — not column mismatch caused by missing ALTER columns).

> Pushing or pulling `dispatch_task`, `agent_task`, or `candidate` between local and staging succeeds when the target table was previously "fresh" (no prior code path had triggered ensure for that table).

## Boundaries

* This bug does **not** change upsert merge rules, allowlists, or Data Management UI layout.
* This bug does **not** invent new migrations — only fixes why ensure + validation still rejects valid same-version Copy Output.
* This bug does **not** add bootstrap/deploy ensure (AST-383).
* Does **not** revert AST-627 registry; fix the remaining wrong-keys path (likely `_validate_copy_row_keys` / Copy Output column alignment vs `table_columns` after ensure).

## Git branch (authoritative)

Parent `ftr/ast-626-table-upsert-ensure-schema-before-running`, child `sub/AST-626/<bug-segment>` seeded at fix-uat dispatch.

### Comments

#### radia — 2026-06-14T17:34:59.498Z
**Review** — `origin/dev...origin/sub/AST-626/AST-629-uat-table-upsert-wrong-keys-error-persists-on-origindev`

### fix-now
None.

### discuss
None.

### advisory
None blocking. Plan doc updated: [ast-629 plan § Review](https://github.com/susansomerset/astral/blob/sub/AST-626/AST-629-uat-table-upsert-wrong-keys-error-persists-on-origindev/docs/features/administrator/ast-629-uat-table-upsert-wrong-keys-error-persists-on-origindev.md).

### sign-off notes
- **Plan fidelity:** Stage 1 flag reset + Stage 2 regression tests (flag already `True` + stale DDL) match the combined plan. Scope stays in `database.py`; boundaries respected (no UI/merge/allowlist/bootstrap changes).
- **§1.3 / §3.5:** `_UPSERT_SCHEMA_ENSURE_FLAGS` mirrors `_UPSERT_LAZY_SCHEMA_HANDLERS` exactly (15 keys, verified symmetric). `company_search_terms` clears both globals as planned.
- **Mechanism:** Clearing flags then calling the handler fixes the process-global short-circuit that left AST-627 ensure a no-op on stale DB files; idempotent `_ensure_*` bodies unchanged.
- **Tests:** `TestAst629UpsertFlagBypass` + config mirror; bible manifest narrowed run **13 passed**.
- **Doc commit:** `docs(AST-629): Radia review — clean` on publish ref.

Ada may proceed to **resolve-child** with no code changes required from this review.

#### betty — 2026-06-14T17:33:06.163Z
## QA test manifest (AST-629)

**Publish ref:** `origin/sub/AST-626/AST-629-uat-table-upsert-wrong-keys-error-persists-on-origindev` @ `4ee39109` (`merge-tests(AST-629): origin/tests 8af2e5e7`)

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `53a403f1af98cf999f32e6359d2a8c2086cb96d2` (§7.13zzl — AST-629 row added)

### 1. New regression (AST-629 — flag already True + stale table)

1. `tests/component/data/database/test_table_copy_upsert.py::TestAst629UpsertFlagBypass::test_copy_upsert_stale_dispatch_task_when_schema_flag_already_true`
2. `tests/component/data/database/test_schema.py::TestApplyConfigTableUpsert::test_config_upsert_stale_candidate_when_schema_flag_already_true`

### 2. Revised tests (AST-629 product change — ensure always re-runs)

- `tests/component/data/database/test_schema.py` — `_config_upsert_columns` helper; config upsert tests refresh column list post-ensure (`test_rejects_non_list_row`, `test_rejects_row_length_mismatch`, `test_upserts_candidate_rows`, `test_inserts_and_updates_dispatch_task`, `test_replaces_agent_task_rows`)

### 3. AST-627 / AST-464 regression guard

3. `tests/component/data/database/test_table_copy_upsert.py::TestAst627EnsureBeforeValidate` (full class)
4. `tests/component/data/database/test_schema.py::TestApplyConfigTableUpsert` (full class)

### Run command

```bash
.venv/bin/python -m pytest \
  tests/component/data/database/test_table_copy_upsert.py::TestAst629UpsertFlagBypass \
  tests/component/data/database/test_schema.py::TestApplyConfigTableUpsert::test_config_upsert_stale_candidate_when_schema_flag_already_true \
  tests/component/data/database/test_table_copy_upsert.py::TestAst627EnsureBeforeValidate \
  tests/component/data/database/test_schema.py::TestApplyConfigTableUpsert \
  -q
```

— Betty

#### ada — 2026-06-14T17:29:52.448Z
Plan: [docs/features/administrator/ast-629-uat-table-upsert-wrong-keys-error-persists-on-origindev.md](https://github.com/susansomerset/astral/blob/sub/AST-626/AST-629-uat-table-upsert-wrong-keys-error-persists-on-origindev/docs/features/administrator/ast-629-uat-table-upsert-wrong-keys-error-persists-on-origindev.md) on `origin/sub/AST-626/AST-629-uat-table-upsert-wrong-keys-error-persists-on-origindev`.

**Root cause:** `_ensure_*_schema` handlers skip work when process-global `_*_schema_ensured` is already `True`. AST-627 calls ensure before validate, but on a stale target DB (local ↔ staging sync, or DB swap without process restart) the flag can be `True` while `PRAGMA table_info` is still old → `_validate_copy_row_keys` reports wrong keys. AST-627 tests reset flags; they never covered flag-already-True + stale table.

**Fix (planned):** In `ensure_table_schema_for_upsert`, clear the table’s ensure flag(s) before invoking the registered handler; add regression tests with `_dispatch_task_schema_ensured = True` and stale `dispatch_task`.

**Self-Assessment**
- **Scope:** `Single-Component` — `ensure_table_schema_for_upsert` + flag map in `database.py`; component tests.
- **Conf:** `high` — flag short-circuit matches repro path; upsert-only flag reset without changing migration bodies.
- **Risk:** `Medium` — admin Table Upsert path; idempotent re-ensure on upsert only.

---

_Implementation detail may live in git history on `origin/dev`._

# AST-637 — UAT: company table upsert wrong-keys after AST-629

<!-- linear-archive: AST-637 archived 2026-06-23 -->

## Linear archive (AST-637)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-637/uat-company-table-upsert-wrong-keys-after-ast-629  
**Status at archive:** Done  
**Project:** Astral Foundation (inherited from AST-626)  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-626 — Table Upsert - ensure schema before running  
**Blocked by / blocks / related:** parent: AST-626

### Description

## What failed

After **AST-629** landed on **origin/dev**, Susan still gets on Data Management **Table Upsert** (table `company`, Copy Output JSON paste):

`row N: columns must exactly match table layout (wrong keys)`

Paste includes 16 keys (`short_name`, `state`, `company_name`, `company_website`, `job_site`, `batch_id`, `batch_created_at`, `company_data`, `agent_responses`, `created_at`, `updated_at`, `state_updated_at`, `candidate_id`, `last_scan_at`, `state_history`, `agent_responses_legacy`) matching staging `PRAGMA table_info(company)` — upsert still rejects.

## Expected

Same-version Copy Output for `company` completes on target after upsert schema ensure — or fails only on real validation/constraint errors, not wrong-keys when paste keys match post-ensure layout.

## Repro

1. Use **origin/dev** (includes AST-627 + AST-629).
2. Copy Output from local `company` rows (sample: `komodohealth`, `pagerduty` with `candidate_id: somerset`).
3. Data Management → **Table Upsert** → table `company` → paste JSON → Upsert.
4. Observe wrong-keys error despite paste keys matching staging schema (Susan attached sample rows + staging `PRAGMA table_info` on parent **2026-06-14**).

## Parent AC (quoted inline)

> On a database where a upsert-eligible table exists but lazy migrations have never run for that table, pasting valid Copy Output JSON from a same-version source via Data Management **Table Upsert** completes successfully (or fails only on real validation/constraint errors — not column mismatch caused by missing ALTER columns).

## Boundaries

* This bug does **not** change: upsert merge rules, UI layout, config-table allowlist, or `agent_task` versioning.
* Fix must use **existing** lazy ensure/migration logic (`_ensure_company_schema`, `_ensure_company_candidate_fk`, `agent_responses_legacy` column path) — no new standalone admin migrate action.

### Comments

#### radia — 2026-06-14T18:41:22.192Z
**Radia review** — `origin/dev...origin/sub/AST-626/AST-637-uat-company-table-upsert-wrong-keys-after-ast-629`

**Clean.** Plan Stage 1 + Stage 2 match the diff; no fix-now or discuss.

**Solid**
- Upsert registry handler → `_ensure_company_table_for_upsert` (schema + `candidate_id` ensure); app paths still `_ensure_company_schema`-only.
- `agent_responses_legacy` in CREATE + idempotent ALTER; no archive UPDATE on upsert path.
- Flag map lists both `_company_schema_ensured` and `_company_candidate_fk_ensured` for AST-629 clearing.
- Regression test: stale `company` missing `candidate_id` + `agent_responses_legacy`, flags True before upsert → success.

**Advisory (§3 data, out of scope)**
- `_UPDATE_COMPANY_ALLOWED` omits `agent_responses_legacy` (pre-existing). Copy upsert uses all `table_columns`; only affects kwargs-based `update_company` if legacy column updates are needed later.

Plan doc: `docs/features/administrator/ast-637-uat-company-table-upsert-wrong-keys-after-ast-629.md` (Review section).

#### betty — 2026-06-14T18:39:48.593Z
## QA test manifest (AST-637)

**Publish ref:** `origin/sub/AST-626/AST-637-uat-company-table-upsert-wrong-keys-after-ast-629` @ `4924daf6` (`merge-tests(AST-637): origin/tests 217f39b2`)

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` §7.13zzl — AST-637 row added; shasum on publish ref: `a1fd16272b88825a21d52def4ceadcb03ee96a7a32c2ee381b7f8e7bbb418661`

### Manifest (run in order)

1. **`tests/component/data/database/test_table_copy_upsert.py::TestAst637CompanyUpsertSchemaEnsure::test_copy_upsert_stale_company_missing_candidate_and_legacy_columns`** — stale `company` DDL missing `candidate_id` + `agent_responses_legacy`; flags pre-set True (AST-629 combo); Copy Output upsert succeeds after full ensure chain.

2. **AST-626/629 regressions:**
   - `tests/component/data/database/test_table_copy_upsert.py::TestAst627EnsureBeforeValidate`
   - `tests/component/data/database/test_table_copy_upsert.py::TestAst629UpsertFlagBypass`

3. **Full Copy Output upsert suite (AST-464 guard):**
   - `tests/component/data/database/test_table_copy_upsert.py`

### Narrowed run

```bash
.venv/bin/python -m pytest \
  tests/component/data/database/test_table_copy_upsert.py::TestAst637CompanyUpsertSchemaEnsure \
  tests/component/data/database/test_table_copy_upsert.py::TestAst627EnsureBeforeValidate \
  tests/component/data/database/test_table_copy_upsert.py::TestAst629UpsertFlagBypass \
  -q
```

### Coverage notes

- **New test** implements plan Stage 2 — no UI changes; no §6c page render required.
- **Existing coverage** sufficient for registry/flag-clear paths (AST-627/629); gap was company-specific ensure chain + `agent_responses_legacy` DDL.

— Betty

#### ada — 2026-06-14T18:37:14.061Z
Plan doc: https://github.com/susansomerset/astral/blob/sub/AST-626/AST-637-uat-company-table-upsert-wrong-keys-after-ast-629/docs/features/administrator/ast-637-uat-company-table-upsert-wrong-keys-after-ast-629.md

**Root cause:** `company` upsert registry handler runs `_ensure_company_schema` only. Copy Output includes `candidate_id` (from `_ensure_company_candidate_fk`, excluded in AST-627) and `agent_responses_legacy` (no lazy ensure in `database.py`). Stale targets fail `_validate_copy_row_keys` even after AST-629 flag fix.

**Fix:** `_ensure_company_table_for_upsert` wrapper + `agent_responses_legacy` idempotent ALTER in `_ensure_company_schema`; extend `_UPSERT_SCHEMA_ENSURE_FLAGS` for `_company_candidate_fk_ensured`.

**Self-Assessment**
- **Scope:** `Single-Component` — company upsert ensure chain and one column migration in `database.py` only.
- **Conf:** `high` — repro keys map directly to missing ensure steps; reuses existing FK ensure and established ALTER patterns.
- **Risk:** `Medium` — admin Table Upsert path; wrapper scopes FK ensure to upsert registry without changing normal company call sites.

---

_Implementation detail may live in git history on `origin/dev`._

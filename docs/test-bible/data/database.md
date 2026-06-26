# Database

**Test module:** `tests/component/data/test_database.py`

## Cluster index

| Source | Test files | Branch lock |
| --- | --- | --- |
| `src/data/database.py` | `tests/component/data/test_database.py`; clusters under `tests/component/data/database/` | pending |

**AST-524:** `company_search_terms` table cluster — **`freq_hrs<=0`** stale semantics (**AST-814**) — `tests/component/data/database/test_company_search_terms.py` (sync, migration, `last_scan_at` preservation; no branch lock on `database.py`).

**AST-723:** `sync_rubric_vectors_from_criteria` + AST-723 token migration — extends `test_rubric_vectors.py` (**AST-722** cluster).

**AST-722:** `rubric_vector` + `vector_feedback` table cluster — `tests/component/data/database/test_rubric_vectors.py`; backfill script — `tests/component/scripts/test_backfill_rubric_vectors.py` (see `data/database/rubric_vectors.md`).

**AST-558:** `candidate_intake_session` table — exercised via `tests/component/core/test_intake.py` (real SQLite `seeded_db`; no separate database cluster).

Per-cluster manifest blocks: `data/database/<cluster>.md`.

---

### AST-454 · AST-453

Seven prompt segments on `agent_task`: `system_prompt`; **`cache_prompt`** as Anthropic cache block A; **`cache_prompt_b|c|d`** as blocks B–D; **`nocache_prompt`**; **`user_prompt`**. Segment edits retire the prior `current` row and insert a new `current = 1` version; **`agent_id` / `run_next`**-only edits update `updated_at` without versioning. **`list_candidate_tasks`** surfaces `cache_prompt_b_len|c_len|d_len` for admin task-manager probes (**AST-454** **`_enrich_tasks`**).

| Area | Source | Component tests |
| --- | --- | --- |
| Migration, versioning, round-trip lengths | `src/data/database.py` (**`_ensure_agent_task_schema`**, **`save_agent_task`**, **`get_agent_task`**, **`list_candidate_tasks`**) | `tests/component/data/database/test_agent_tasks.py` (**`TestAst454SevenSegmentPersistence`**, **`TestSaveAgentTask`**) |
| Admin task GET/PUT segment fields | `src/ui/api/api_admin.py` | Covered by `./scripts/testing/run_component_tests.sh` (includes **`test_api_admin`**) |

---

### AST-482 · AST-379 (historical — SUNSET AST-757)

**RETIRED (AST-757):** Board search **`last_scan_at`** cadence removed with boards channel. No active manifest. See **`docs/ASTRAL_CODE_RULES.md` §3.7**.

---

### AST-586 · AST-617 · AST-600

Restores **`database.py`** **`count_eligible_for_dispatch_task`** / schema backfill and **`api_admin.py`** **`is_scored`** / **`score_floor`** call sites to **`dispatch_claim_uses_score_floor`**. Config helper + **`dispatcher.py`** claim path already on **`origin/dev`** / sibling **AST-615** (**§7.13zzb**). **Manifest-only** — reuse **§7.13zv** (**AST-586**) narrowed run; no new test files.

| Child | Behavior | Sources | Manifest |
| --- | --- | --- | --- |
| **AST-617** | DB eligible count + admin dispatch rows align with claim helper (not grading metadata) | `src/data/database.py`, `src/ui/api/api_admin.py` | **§7.13zv** narrowed run |

---

### AST-627 · AST-626

**AST-626 (parent):** Lazy `_ensure_*_schema` handlers run **before** column validation in both Copy Output upsert (`apply_copy_output_table_upsert`) and config-table upsert (`apply_config_table_upsert`). Data-layer registry **`ensure_table_schema_for_upsert`** maps known table names to existing handlers; unregistered tables unchanged. Preserves AST-373 / AST-464 merge semantics — no UI or allowlist changes.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-627** | Registry + ensure hook in config upsert; core path calls ensure before `table_columns`; removes duplicate in-transaction `agent_task` ensure | `src/data/database.py`, `src/core/table_copy_upsert.py` | **`tests/component/data/database/test_table_copy_upsert.py::TestAst627EnsureBeforeValidate`**; **`tests/component/data/database/test_schema.py::TestApplyConfigTableUpsert::test_config_upsert_stale_candidate_schema_ensure_before_validate`**; full **`test_table_copy_upsert.py`** + config upsert rows in **`test_schema.py`** for AST-464 regressions |
| **AST-629** | UAT bug: `ensure_table_schema_for_upsert` clears process-global `_*_schema_ensured` flags before handler so stale DB + flag-already-True still migrates | `src/data/database.py` (`_UPSERT_SCHEMA_ENSURE_FLAGS`, `ensure_table_schema_for_upsert`) | **`tests/component/data/database/test_table_copy_upsert.py::TestAst629UpsertFlagBypass::test_copy_upsert_stale_dispatch_task_when_schema_flag_already_true`**; **`tests/component/data/database/test_schema.py::TestApplyConfigTableUpsert::test_config_upsert_stale_candidate_when_schema_flag_already_true`**; full **`TestAst627EnsureBeforeValidate`** + **`TestApplyConfigTableUpsert`** for AST-627/464 regressions |
| **AST-637** | UAT bug: `company` upsert handler chains `_ensure_company_candidate_fk` + adds `agent_responses_legacy` DDL; registry flags reset both globals (AST-629 combo) | `src/data/database.py` (`_ensure_company_table_for_upsert`, `_ensure_company_schema`) | **`tests/component/data/database/test_table_copy_upsert.py::TestAst637CompanyUpsertSchemaEnsure::test_copy_upsert_stale_company_missing_candidate_and_legacy_columns`**; full **`TestAst627EnsureBeforeValidate`** + **`TestAst629UpsertFlagBypass`** for AST-626/629 regressions |

**AST-627** narrowed run:

```bash
.venv/bin/python -m pytest \
  tests/component/data/database/test_table_copy_upsert.py::TestAst627EnsureBeforeValidate \
  tests/component/data/database/test_schema.py::TestApplyConfigTableUpsert::test_config_upsert_stale_candidate_schema_ensure_before_validate \
  tests/component/data/database/test_table_copy_upsert.py \
  tests/component/data/database/test_schema.py::TestApplyConfigTableUpsert \
  -q
```

**AST-629** narrowed run:

```bash
.venv/bin/python -m pytest \
  tests/component/data/database/test_table_copy_upsert.py::TestAst629UpsertFlagBypass \
  tests/component/data/database/test_schema.py::TestApplyConfigTableUpsert::test_config_upsert_stale_candidate_when_schema_flag_already_true \
  tests/component/data/database/test_table_copy_upsert.py::TestAst627EnsureBeforeValidate \
  tests/component/data/database/test_schema.py::TestApplyConfigTableUpsert \
  -q
```

**AST-637** narrowed run:

```bash
.venv/bin/python -m pytest \
  tests/component/data/database/test_table_copy_upsert.py::TestAst637CompanyUpsertSchemaEnsure \
  tests/component/data/database/test_table_copy_upsert.py::TestAst627EnsureBeforeValidate \
  tests/component/data/database/test_table_copy_upsert.py::TestAst629UpsertFlagBypass \
  -q
```

---

### AST-685 · AST-655

**AST-685 (UAT revert):** Removes **AST-678** `_apply_ast678_craft_rubric_importance_migration` and related helpers from **`database.py`**. No forward migration auto-patches **`agent_task.user_prompt`** at schema init; Susan pastes approved explainer via Manage Tasks (sibling UAT explainer-text bug). **AST-676** schema + **AST-677** UI task key unchanged.

| AC | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| Revert | Zero AST-678 symbols in **`database.py`**; migration not called from **`_ensure_agent_task_schema`** | `src/data/database.py` | **`tests/component/data/test_database.py`** — existing import/smoke; **`test_ast678_craft_rubric_importance_migration.py`** deleted |
| Regression | **`importance`** schema validation intact | `src/utils/config.py`, `src/core/agent.py` | **AST-676** narrowed run (see **`docs/test-bible/utils/config.md`**) |
| Regression | UI **`craft_prefilter_rubric`** task key | `src/ui/frontend/src/pages/ArtifactsCompanyWatchCriteria.tsx` | **AST-677** narrowed run (see **`docs/test-bible/frontend/pages.md`**) |

**AST-685** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/test_database.py \
  tests/component/utils/test_config.py::TestAst676CraftRubricSchema \
  tests/component/core/test_agent.py::TestResponseSchemaBranches::test_ast676_int_bounds_and_bool_rejection \
  tests/component/core/test_agent.py::TestResponseSchemaBranches::test_ast676_craft_rubric_criteria_schema
```

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_ArtifactsCompanyWatchCriteria.test.tsx
```

### AST-766 · AST-757

**Sunset `board_search` schema** — see `docs/test-bible/data/database/dispatch_tasks.md` § AST-766.

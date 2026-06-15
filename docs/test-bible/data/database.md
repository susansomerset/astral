# Database

**Test module:** `tests/component/data/test_database.py`

## Cluster index

| Source | Test files | Branch lock |
| --- | --- | --- |
| `src/data/database.py` | `tests/component/data/test_database.py`; clusters under `tests/component/data/database/` | pending |

**AST-524:** `company_search_terms` table cluster — `tests/component/data/database/test_company_search_terms.py` (sync, migration, `last_scan_at` preservation; no branch lock on `database.py`).

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

### AST-482 · AST-379

Mirror company **`WATCH` / `gaze`**: nullable **`board_search.last_scan_at`**, **`BOARDS_CONFIG["gaze_board"]["scan_interval_hours"]`** (default **24**), staleness **`AND`** in **`claim_board_search_batch`** matches **`count_eligible_for_dispatch_task`** ( **`freq_hrs` override** when **> 0**). **`dispatch_task`** seed **`sort_by`** **`last_scan_at`** (+ migration **`updated_at` → `last_scan_at`** for legacy rows). **`update_board_search_last_scan_at`** bumps **only success path** after **`run_board_search_gaze`** in **`process_gaze_board_batch`** (no bump on **`except`**). Dispatcher passes **`scan_interval_hours`** + **`sort_by`** into **`claim_board_search_batch`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Claim staleness **`NULL`** / stale / fresh + **`count_eligible`** parity + **`freq_hrs`** tightening | `src/data/database.py` | `tests/component/data/database/test_board_search_integration.py` (**`TestBoardSearchLastScanCadenceAst482`**) |
| Success bump vs failure silent | `src/core/gazer.py` | `tests/component/core/test_gazer.py` (**`TestProcessGazeBoardBatch`**) |
| **`_run_unified`** board_search **`scan_interval_hours`** / **`sort_by`** kwargs | `src/core/dispatcher.py` | `tests/component/core/test_dispatcher.py` (**`TestRunUnified`**) |
| **`BOARDS_CONFIG["gaze_board"]["scan_interval_hours"]`** | `src/utils/config.py` | `tests/component/utils/test_config.py` (**`TestAst471DispatchConfigHelpers::test_gaze_board_boards_config_scan_interval_hours`**) |

Narrow (**`test-astral`** **AST-482** tip):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_board_search_integration.py::TestBoardSearchLastScanCadenceAst482 \
  tests/component/core/test_gazer.py::TestProcessGazeBoardBatch \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_claims_board_search_batch_and_clears \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_board_search_claim_passes_freq_and_sort_kw \
  tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers::test_gaze_board_boards_config_scan_interval_hours
```

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

### AST-678 · AST-655

**AST-678 (child):** Shared **`_AST678_CRAFT_RUBRIC_IMPORTANCE_EXPLAINER`** constant + idempotent **`_apply_ast678_craft_rubric_importance_migration`** in **`database.py`**: renames **`craft_company_prefilter`** → **`craft_prefilter_rubric`** in **`agent_task`** store and inserts importance explainer (marker **`AST-678_VECTOR_IMPORTANCE`**) into all six **`craft_*_rubric`** **`user_prompt`** bodies before **`{$RESPONSE_SCHEMA}`**. Schema validation (**AST-676**) and UI task key (**AST-677**) are sibling scope.

| AC | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| 2 | Explainer inserted before **`{$RESPONSE_SCHEMA}`**; idempotent patch | `src/data/database.py` (`_patch_ast678_importance_into_user_prompt`) | **`tests/component/data/test_ast678_craft_rubric_importance_migration.py::TestAst678PatchHelper::test_patch_inserts_before_response_schema`** |
| 2–3 | Migration idempotent; all six keys receive marker | `src/data/database.py` (`_apply_ast678_craft_rubric_importance_migration`) | **`::TestAst678CraftRubricImportanceMigration::test_migration_idempotent`**; **`::test_all_six_keys_receive_marker`** |
| 2 | Prefilter task-key rename in **`agent_task`** | `src/data/database.py` | **`::TestAst678CraftRubricImportanceMigration::test_prefilter_task_key_rename`** |
| 3–4 | Generate returns **`importance`** (manual smoke post-**AST-677** on ftr) | admin **`agent_task`** + **AST-676** schema | Engineer manual per plan Stage 3 — not automated here |

**AST-678** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/test_ast678_craft_rubric_importance_migration.py
```

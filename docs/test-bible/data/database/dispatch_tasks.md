# Dispatch Tasks

**Test module:** `tests/component/data/database/test_dispatch_tasks.py`

_(Coverage map and manifest blocks appended by Betty `qa-child`.)_

---

### AST-745 · AST-741

**AST-745:** Remove recurring automatic `INSERT OR IGNORE` of separate `*_RETRY` companion dispatch rows and decommissioned `gaze_board` rows from `_ensure_dispatch_task_schema`. Companion entity claim stays on primary rows via `dispatch_claim_states` in config (no config diff). **`debug/startup_db_inventory.md`** catalogs all `agent_task` / `dispatch_task` mutators.

| AC | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| No retry re-seed | Deleted `*_RETRY` dispatch rows stay absent after schema ensure restart simulation | `src/data/database.py` | **`TestAst745StopAutomaticDispatchRowSeeding::test_schema_ensure_does_not_reinsert_deleted_retry_rows`** |
| Companion claim intact | Primary `qualify_job_listings` / `VALID_TITLE` row counts jobs in `VALID_TITLE_RETRY` without a retry dispatch row | `src/data/database.py`, `src/utils/config.py` (`dispatch_claim_states`) | **`TestAst745StopAutomaticDispatchRowSeeding::test_primary_row_claims_retry_entities_without_retry_dispatch_row`**; regression **`TestAst641UnionClaimCount`** |
| One-time migrations unchanged | Prefilter HOMEPAGE_READY cutover still runs | `src/data/database.py` | **`TestAst702PrefilterDispatchMigration`**, **`TestAst703PrefilterMigrationUniqueCollision`** |
| Inventory doc | Checked-in mutator catalog | `debug/startup_db_inventory.md` | Artifact audit (item 5) |

**Broken / obsolete (Betty revised):** **`TestAst701FetchWebsiteRetrySeed`** (asserted retry row auto-insert — removed AST-745); **`TestAst702PrefilterDispatchMigration::test_retry_task_seed_omits_prefilter_website_found_retry`** (`_RETRY_TASK_SEED` symbol deleted).

**AST-745** narrowed run:

```bash
.venv/bin/python -m pytest \
  tests/component/data/database/test_dispatch_tasks.py::TestAst745StopAutomaticDispatchRowSeeding \
  tests/component/data/database/test_dispatch_tasks.py::TestAst641UnionClaimCount \
  tests/component/data/database/test_dispatch_tasks.py::TestAst702PrefilterDispatchMigration \
  tests/component/data/database/test_dispatch_tasks.py::TestAst703PrefilterMigrationUniqueCollision \
  -q
```

**Pass criterion:** pytest green on items 1–4; item 5 confirms `debug/startup_db_inventory.md` on publish ref lists dispatch_task + agent_task writers and **Removed AST-745** subsection — not zero-arg harness / branch-lock gate.

### AST-748 · AST-736

Idempotent **`consult_*` → `grade_*`** row rename in **`_ensure_dispatch_task_schema`** (delete legacy row when canonical triple exists).

| Behavior | Sources | Manifest tests |
| --- | --- | --- |
| Rename + scheduling preserve | `src/data/database.py` | **`TestAst748ConsultToGradeDispatchMigration::test_schema_renames_consult_do_row_to_grade_do`** |
| Collision → delete legacy | same | **`TestAst748ConsultToGradeDispatchMigration::test_schema_deletes_consult_row_when_grade_triple_exists`** |


### AST-766 · AST-757

**Board schema sunset:** `_apply_board_schema_sunset` drops `board_search` / `board_search_run` and rebuilds `job` without `board_search_id`; board DDL helpers removed; `count_eligible_for_dispatch_task` has no `board_search` branch.

| Area | Source | Component tests |
| --- | --- | --- |
| Sunset migration + fresh schema | `src/data/database.py` | **`TestAst766BoardSchemaSunset`** |
| Dead DDL surface | same | **`test_board_search_ddl_helpers_removed`** |
| Eligibility board_search unknown entity | same | **`test_count_eligible_board_search_entity_raises`** |

**Retired (AST-766):** `test_board_ingest.py`; `test_board_search_integration.py` (AST-765); **`TestAst745StopAutomaticDispatchRowSeeding::test_schema_ensure_does_not_reinsert_gaze_board_rows`**.

**AST-766** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_dispatch_tasks.py::TestAst766BoardSchemaSunset \
  -q
```

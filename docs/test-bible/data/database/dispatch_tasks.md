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


Prior board integration retired (**AST-765** product, **AST-766** schema); active test is schema sunset only. See **`docs/ASTRAL_CODE_RULES.md` §3.7**.

### AST-766 · AST-757

**Board schema sunset:** `_apply_board_schema_sunset` drops `board_search` / `board_search_run` and rebuilds `job` without `board_search_id`; board DDL helpers removed; `count_eligible_for_dispatch_task` has no `board_search` branch.

| Area | Source | Component tests |
| --- | --- | --- |
| Sunset migration + fresh schema | `src/data/database.py` | **`TestAst766BoardSchemaSunset`** |
| Dead DDL surface | same | **`test_board_search_ddl_helpers_removed`** |
| Eligibility board_search unknown entity (pre-AST-781) | same | superseded by **AST-781** — **`test_count_eligible_board_search_entity_returns_zero`** |

**Retired (AST-766):** `test_board_ingest.py`; `test_board_search_integration.py` (AST-765); **`TestAst745StopAutomaticDispatchRowSeeding::test_schema_ensure_does_not_reinsert_gaze_board_rows`**.

**AST-766** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_dispatch_tasks.py::TestAst766BoardSchemaSunset \
  -q
```

### AST-797 · AST-794

Idempotent **`_ensure_dispatch_task_schema`** migration: **`scrape_jd` → `fetch_jd`** (DELETE-before-UPDATE collision); purge **`validate_title`** / **`gaze_board`**; **`qualify_job_listings`/`VALID_TITLE` → `NEW`** + seed **`VALID_TITLE_RETRY`** companion.

| Area | Source | Component tests |
| --- | --- | --- |
| Migration cutover | `src/data/database.py` | `TestAst797DispatchKeyCutoverMigration` |

**AST-797** narrowed pytest:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_dispatch_tasks.py::TestAst797DispatchKeyCutoverMigration \
  -q
```

Consult runtime: **`docs/test-bible/core/consult.md`** (**AST-797**).

### AST-781 · AST-763

UAT: **`GET /api/admin/dispatch_tasks`** returned **500** when legacy `dispatch_task` rows still had `entity_type='board_search'` (boards sunset **AST-766** left DB rows). **`count_eligible_for_dispatch_task`** returns **`0`** when `entity_type not in ENTITY_TYPES` — list loads; legacy rows show **Available = 0**.

| Area | Source | Component tests |
| --- | --- | --- |
| Retired entity_type guard | `src/data/database.py` | **`TestAst766BoardSchemaSunset::test_count_eligible_board_search_entity_returns_zero`** |
| Admin list enrichment | `src/ui/api/api_admin.py` | **`TestAst781ListDtasksRetiredEntityType::test_list_dtasks_legacy_board_search_row_returns_zero_available_count`** |

**AST-781** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_dispatch_tasks.py::TestAst766BoardSchemaSunset::test_count_eligible_board_search_entity_returns_zero \
  tests/component/ui/api/test_api_admin.py::TestAst781ListDtasksRetiredEntityType \
  -q
```

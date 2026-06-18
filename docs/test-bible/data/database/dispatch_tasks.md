# Dispatch Tasks

**Test module:** `tests/component/data/database/test_dispatch_tasks.py`

_(Coverage map and manifest blocks appended by Betty `qa-child`.)_

---

### AST-745 · AST-741

**AST-745:** Remove recurring automatic `INSERT OR IGNORE` of separate `*_RETRY` companion dispatch rows and decommissioned `gaze_board` rows from `_ensure_dispatch_task_schema`. Companion entity claim stays on primary rows via `dispatch_claim_states` in config (no config diff). **`debug/startup_db_inventory.md`** catalogs all `agent_task` / `dispatch_task` mutators.

| AC | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| No retry re-seed | Deleted `*_RETRY` dispatch rows stay absent after schema ensure restart simulation | `src/data/database.py` | **`TestAst745StopAutomaticDispatchRowSeeding::test_schema_ensure_does_not_reinsert_deleted_retry_rows`** |
| No gaze_board re-seed | Deleted / never-present `gaze_board` rows stay absent when `gaze` + `board_search` exist | `src/data/database.py` | **`TestAst745StopAutomaticDispatchRowSeeding::test_schema_ensure_does_not_reinsert_gaze_board_rows`** |
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

# Telescope Data

**Test module:** `tests/component/data/database/test_telescope_data.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/data/database.py` (`telescope_data` schema / save / read by id(s)) | `tests/component/data/database/test_telescope_data.py` | no |

**Migration script (AST-2135):** existing company scrape text → `telescope_data` rows; see [`../../dev/migrate_company_scrape_to_telescope_data.md`](../../dev/migrate_company_scrape_to_telescope_data.md).

---

### AST-2131 · AST-2130 (telescope_data table and config)

**Publish:** `origin/sub/AST-2130/AST-2131-telescope-data-table`. Plan: `docs/features/foundation/ast-2131-telescope-data-table-and-config.md`.

New `telescope_data` table (uuid PK, `candidate_id`, `url`, free-text `data_type`, zlib `content` BLOB, `created_at`) + index `(candidate_id, created_at)`; `_ensure_telescope_data_schema` registered in both upsert-registry maps; `save_telescope_data` returns the new id with no `data_type` allow-list; `get_telescope_data` / `get_telescope_data_for_ids` return plain content, missing ids omitted / `None`. No callers yet (siblings AST-2132–AST-2135).

| Area | Source | Component tests |
| --- | --- | --- |
| AC1 — registry entries; startup ensure on an existing DB creates the table + index; second pass through DDL is a no-op; existing rows untouched | `_ensure_telescope_data_schema`, `_UPSERT_*` maps | **`TestAst2131TelescopeData::test_registry_creates_table_and_index_idempotently`** |
| AC2 — `data_type="JSON"` (not configured) saves and reads back; uuid return; content compressed at rest | `save_telescope_data` | **`TestAst2131TelescopeData::test_save_accepts_any_data_type_and_returns_uuid`** |
| Read by id / ids — hit, missing id, empty list | `get_telescope_data`, `get_telescope_data_for_ids` | **`TestAst2131TelescopeData::test_reads_return_plain_content_and_skip_missing`** |
| Config — `TELESCOPE_DATA_CONFIG` shape, id-key guard fires, `jd_telescope_data_id` | `src/utils/config.py` | [`../../utils/config.md`](../../utils/config.md) § AST-2131 |

**Fixture:** `_telescope_data_schema_ensured` added to `_SCHEMA_FLAGS` in `tests/component/data/conftest.py` — without it the process-global flag leaks True across tests and later fresh DBs never get the table.

**Broken / obsolete:** none — the diff is additive; no test enumerates the full registry, table list, or `job_data_keys`. `tests/component/data` + `tests/component/utils/test_config.py` failure set equals `origin/ftr/AST-2130-telescope-data` (75 failed + 2 collection errors — `test_meteorites.py`, `test_surfer_batches.py` — pre-existing, includes Ada's AST-846 / AST-984 reds).

**Integration:** none (no callers yet).

## QA test manifest

1. `tests/component/data/database/test_telescope_data.py` — all 3 pass.
2. `tests/component/utils/test_config.py::TestAst2131TelescopeDataConfig` — all 3 pass.
3. Neighbors on the shared fixture / registry: `tests/component/data/database/test_agent_data.py`, `tests/component/core/test_bootstrap.py`, `tests/component/data/database/test_terminal_state_remap.py` — green.
4. No-regression: `tests/component/data` + `tests/component/utils/test_config.py` (with `--continue-on-collection-errors`) failure set must equal the ftr baseline above — no new failures.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_telescope_data.py \
  tests/component/utils/test_config.py::TestAst2131TelescopeDataConfig \
  tests/component/data/database/test_agent_data.py \
  tests/component/core/test_bootstrap.py \
  tests/component/data/database/test_terminal_state_remap.py -q
```

**Pass criterion:** pytest green on items 1–3 and item 4 baseline parity — not zero-arg harness / branch-lock gate (pre-existing reds on the ftr tip).

**Bible shasum (after publish):** `git show origin/sub/AST-2130/AST-2131-telescope-data-table:docs/test-bible/data/database/telescope_data.md | shasum` · same for `docs/test-bible/data/database.md` and `docs/test-bible/utils/config.md`

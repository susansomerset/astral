# Search

**Test module:** `tests/component/core/test_search.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/search.py` | `tests/component/core/test_search.py` | no (100% branch at AST-2173; not in `LOCKED_AT_100`) |

---

### AST-2173 · AST-2168 (search backend: config, read, core, route)

**Parent:** [AST-2168](https://linear.app/astralcareermatch/issue/AST-2168) (Add Universal Entity Search). **Publish:** `origin/sub/AST-2168/AST-2173-search-backend`. Plan: `docs/features/interface/ast-2173-search-backend-config-reads-core-route.md`. Sibling UI child **AST-2174** (search box, `/search` page, modal hosting) is out of scope here.

`search_entities(candidate_id, query)` → `{"job": [...], "company": [...], "meteorite": [...]}` (all three keys always). Per type: one `database.search_entity_rows` read; a result is `base` tier if any matched field is a base field, else `payload`; base list then payload list, read order (newest `state_changed_at`) kept inside each. Each result: `entity_id`, `display_name` (non-blank `name_fields` joined `" — "`, else `str(entity_id)`), `state`, `tier`, `matched_fields`; jobs add `jobs_list` + `modal_kind`. `_jobs_list`: READY → `ready`, REVIEW → `review`, APPLIED → `applied`, SKIPPED_STATES **or** below dispatch score floor → `skipped`, else `processing`; floors read once per search via `tracker.score_floor_by_trigger_for_candidate`.

| AC (child) | Component tests |
| --- | --- |
| 1 candidate scope (job / company / meteorite) | data: **`TestAst2173CandidateScope`**; route end to end: **`test_api_search.py::TestAst2173SearchRealDb::test_candidate_scope_and_exact_keys`** |
| 2 blank `q` / missing or blank `candidate_id` → 400 `error` | **`test_api_search.py::TestAst2173SearchParams`** |
| 3 ids findable as `base` (full / `company_job_id` / 6-char middle of `astral_job_id`; meteorite numeric `id` + `astral_job_id`) | data: **`TestAst2173IdsFindable`** (3); tier = base whenever a base field matched: **`TestAst2173Tiering`** |
| 4 base before payload, each once (payload hit newer than base hit) | **`TestAst2173BaseBeforePayloadReal`** (real SQLite); stubbed ordering: **`TestAst2173Tiering::test_base_before_payload_with_stable_order`** |
| 5 case-insensitive; `%` / `_` (and `\`) literal | data: **`TestAst2173CaseAndLiteralWildcards`** |
| 6 no cap (600 rows) | data: **`TestAst2173NoCap`**; `LIMIT` grep in manifest item 3 |
| 7 field lists from config (drop `job_link` → link-only job vanishes) | data: **`TestAst2173FieldsFromConfig`**; config lists: **`test_config.py::TestAst2173SearchConfig`**; literal grep in manifest item 3 |
| 8 (API half) Jobs list + modal kind: Ready / Review / Applied / Processing / Skipped / below-floor Processing (+ above-floor Processing stays `processing`) | **`TestAst2173JobsListAndModal::test_six_jobs_on_real_sqlite`** (floor read stubbed; miss comparison real) |
| 9 (API half) keys exactly `job` / `company` / `meteorite`, lists; no match → three empty lists | **`TestAst2173Keys`**; route: **`TestAst2173SearchRealDb`** |
| 10 no info line | route asserts `logger.info` never called on the error path (**`TestAst2173SearchError`**); grep in manifest item 3 |
| 11 (Python half) import check | manifest item 4 |
| Result shape: display-name join / blank skip / id fallback; non-job results carry no `jobs_list` / `modal_kind` | **`TestAst2173ResultShape`** |

Route, data read, config and server pages: [`../ui/api/api_search.md`](../ui/api/api_search.md), [`../data/database/search.md`](../data/database/search.md), [`../utils/config.md`](../utils/config.md) § AST-2173, [`../ui/server.md`](../ui/server.md) § AST-2173.

**Red check:** n/a — `src/core/search.py`, `src/ui/api/api_search.py` and `search_entity_rows` are new; every new test fails at import / attribute lookup on `origin/dev`.

**Broken / obsolete:** none. Nothing enumerates blueprints or config constants; the two `database.__doc__` inventory checks (`test_jobs.py::TestAst1598JobCandidateId::test_inventory_lists_job_candidate_id`, `test_app_log.py::TestAst1598AppLogCandidateId::test_inventory_and_fresh_column_nullable`) only look for their own substrings and stay green with the new Search line. `config.py` / `server.py` (both `LOCKED_AT_100`) gain no branches.

**Pre-existing (not this ticket):** `tests/component/data/database/test_meteorites.py` (`METEORITE_STATES_RETENTION`) and `test_surfer_batches.py` (`SURFER_BATCH_CONFIG`) fail at collection on this tip with or without AST-2173 — do not pass the whole `tests/component/data/database/` directory in the manifest run.

**Integration:** none. No `tests/integration/` scenario registers `search_bp` or calls `/api/search`. Do not invent one.

## QA test manifest — AST-2173

1. New + touched (needs the full requirements venv — `asyncpg` for the server reload):

```bash
ASTRAL_DB_DIR=$(mktemp -d) ./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_search.py \
  tests/component/core/test_search.py \
  tests/component/ui/api/test_api_search.py \
  tests/component/utils/test_config.py::TestAst2173SearchConfig \
  tests/component/ui/test_server.py \
  tests/component/data/database/test_jobs.py::TestAst1598JobCandidateId::test_inventory_lists_job_candidate_id \
  tests/component/data/database/test_app_log.py::TestAst1598AppLogCandidateId::test_inventory_and_fresh_column_nullable \
  -q
```

   Expect **all passed**; coverage report shows `src/core/search.py` and `src/ui/api/api_search.py` at **100%** branch.
2. No-regression on the existing suites this diff touches: `pytest tests/component/utils/test_config.py tests/component/ui/ -q` — at qa time **36 failed / 1447 passed**, and the 36 `FAILED` node ids are identical with the AST-2173 test tree stashed (pre-existing on this tip: `test_api_contact.py` upstream-502s, `test_api_jobs.py`, `test_api_system.py`, etc.). Pass = no `FAILED` id outside that baseline set.
3. AC 6 / 7 / 10 by hand:

```bash
rg -n "LIMIT" src/core/search.py                                                        # no output
rg -n "company_job_id|originating_search_term|electronic_contact" src/core/search.py src/ui/api/api_search.py   # no output
rg -n "logger.info" src/ui/api/api_search.py src/core/search.py                         # no output
sed -n '/^def search_entity_rows/,/^# ---- Timesheets/p' src/data/database.py | rg -n "LIMIT"   # docstring "no LIMIT" only
```

4. AC 11 (Python half): `PYTHONPATH=.:src python -c "import src.utils.config, src.core.search, ui.api.api_search"` exits 0.

**Pass criterion:** items 1–4. Narrowed run, not the zero-arg harness / branch-lock gate.

**Bible shasum (after publish):** `git show origin/sub/AST-2168/AST-2173-search-backend:docs/test-bible/core/search.md | shasum`

# Api Companies

**Test module:** `tests/component/ui/api/test_api_companies.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_companies.py` | `tests/component/ui/api/test_api_companies.py` | yes |

---

### AST-1495 · AST-1484

**Parent:** [AST-1484 — Create meteorite companies per email address](https://linear.app/astralcareermatch/issue/AST-1484/create-meteorite-companies-per-email-address). **Publish:** `origin/sub/AST-1484/AST-1495-email-land-paths-apply-stem-company-attach`.

`GET /api/companies?view=meteorite_list` filters **METEORITE** state; counts key `/companies/meteorite_list`. Page: **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| meteorite_list view + counts badge key | `src/ui/api/api_companies.py` | revised **`TestCompaniesRoutes`** |

**Broken / obsolete:** none — additive view branch.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_companies.py::TestCompaniesRoutes \
  -q
```

### AST-2071 · AST-2054

**Parent:** [AST-2054](https://linear.app/astralcareermatch/issue/AST-2054). **Publish:** `origin/sub/AST-2054/AST-2071-upshot-display`. UI side + manifest: [`../../frontend/components.md`](../../frontend/components.md) § AST-2071.

`_flatten_for_view` lifts `company_data.company_upshot` to top-level `company_upshot` (`""` when absent) on list and detail payloads (AC12).

| Area | Source | Component tests |
| --- | --- | --- |
| upshot lift + `""` default | `src/ui/api/api_companies.py` | new **`TestFlattenForView::test_lifts_company_upshot_default_empty`**; revised **`TestCompaniesRoutes::test_detail_returns_story_and_counts`** (asserts `company_upshot == ""`) |

**Broken / obsolete:** none — additive key. No new branch (branch lock unaffected).

**Integration:** none.

### AST-2320 · AST-2318 (watch_list enrichment + jobs-by-bucket)

**Parent:** [AST-2318](https://linear.app/astralcareermatch/issue/AST-2318). **Publish:** `origin/sub/AST-2318/AST-2320-watch-list-aggregates-api-and-shapes`.

**`GET ?view=watch_list`**: attaches `scan_start`, `best_fit_label`/`best_fit_at`, `jobs`, bucket counts + `*_newest_at`. **`GET /<short_name>/jobs?bucket=&candidate_id=`**: bucket-filtered jobs; drops `job_data` / `state_history`. No `logger.info` on these GETs.

| Area | Component tests |
| --- | --- |
| Enrichment + jobs route | new **`TestAst2320WatchListEnrichmentAndJobs`** |

## QA test manifest — AST-2320

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst2320WatchListConfig \
  tests/component/utils/test_config.py::TestAst2319TestWatchConfig::test_seed_sql_and_ui_manifest_boundary \
  tests/component/core/test_roster.py::TestAst2320WatchListAggregates \
  tests/component/ui/api/test_api_companies.py::TestAst2320WatchListEnrichmentAndJobs \
  tests/component/data/database/test_jobs.py::TestAst2320CompanyJobStateStats \
  -q
```

**Pass criterion:** pytest green on the nodes above. Not the zero-arg harness.

**Bible shasums (after publish):** `git show origin/sub/AST-2318/AST-2320-watch-list-aggregates-api-and-shapes:docs/test-bible/<path> | shasum`
### AST-2322 · AST-2318 (add route + transition-gated bulk_state)

**Parent:** [AST-2318](https://linear.app/astralcareermatch/issue/AST-2318). **Publish:** `origin/sub/AST-2318/AST-2322-add-company-and-ignore-restore`. Core create: [`../../core/roster.md`](../../core/roster.md) § AST-2322. Pages: [`../../frontend/pages.md`](../../frontend/pages.md) § AST-2322.

**`POST /api/companies/add`** → `201` `{short_name, state: TEST_WATCH}`; missing fields / core `ValueError` → `400`. **`bulk_state`**: pre-validate `(from_state, to_state)` against **`ASTRAL_CONFIG["company_state_transitions"]`**, then **`transition_company_state`**; skip missing rows; reject e.g. `WATCH`→`WEBSITE_FOUND`; allow `IGNORE`→`TEST_WATCH` / `WATCH`→`IGNORE`. Completion `logger.info` on both mutating routes.

| Area | Source | Component tests |
| --- | --- | --- |
| Add success / 400 | `api_companies.py` | new **`TestAst2322AddCompanyAndBulkState`** |
| bulk_state allow / reject / prevalidate | `api_companies.py` | same class; revised **`TestCompaniesRoutes::test_bulk_state_updates_companies`** |

**Broken / obsolete (revised this pass):** `test_bulk_state_updates_companies` (was `update_company` mock; now `get_company` + `transition_company_state`).

## QA test manifest — AST-2322

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestAst2322AddCompanyForTestWatch \
  tests/component/ui/api/test_api_companies.py::TestAst2322AddCompanyAndBulkState \
  tests/component/ui/api/test_api_companies.py::TestCompaniesRoutes::test_bulk_state_updates_companies \
  tests/component/ui/api/test_api_companies.py::TestCompaniesRoutes::test_bulk_state_requires_body \
  -q
```

Frontend (Vitest; §6c page renders):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CompaniesWatchList.test.tsx \
  ../../../tests/component/frontend/pages/test_CompaniesIgnored.test.tsx
```

**Pass criterion:** pytest + Vitest green on the nodes above. Not the zero-arg harness / branch-lock gate.

**Bible shasums (after publish):** fill from `git show origin/sub/AST-2318/AST-2322-add-company-and-ignore-restore:docs/test-bible/<path> | shasum`.

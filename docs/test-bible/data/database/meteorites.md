# Meteorites

**Test module:** `tests/component/data/database/test_meteorites.py`

_(Coverage map and manifest blocks appended by Betty `qa-child`.)_

### AST-1557 · AST-1555

**Parent:** [AST-1555 — Meteorite ingress: staging table + inbox/meteorite consolidation](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation). **Publish:** `origin/sub/AST-1555/AST-1557-meteorite-table-claim-helpers`.

Flat `meteorite` staging table + data-layer claim/insert/update/retention helpers. Config registry `METEORITE_STATES` / `METEORITE_STATES_RETENTION`: **`docs/test-bible/utils/config.md`** § AST-1557. No inbox verbs, classify runner, Estelle, or retention **runner** (siblings AST-1558–AST-1562).

| Area | Source | Component tests |
| --- | --- | --- |
| Schema + indexes | `src/data/database.py` | **`TestAst1557MeteoriteSchema`** |
| Insert fan-out forces NEW; empty no-op | same | **`TestAst1557InsertMeteoriteRows`** |
| Claim → get → clear; states union | same | **`TestAst1557MeteoriteBatchClaim`** |
| get / list-by-state / update whitelist + state key gate | same | **`TestAst1557MeteoriteReadUpdate`** |
| Retention list + delete by ids | same | **`TestAst1557MeteoriteRetention`** |

**Broken / obsolete:** none — additive table/helpers.

**Integration:** none revised (no existing scenario exercises `meteorite` table).

## QA test manifest

1. Schema: `tests/component/data/database/test_meteorites.py::TestAst1557MeteoriteSchema`
2. Insert fan-out: `tests/component/data/database/test_meteorites.py::TestAst1557InsertMeteoriteRows`
3. Claim pool: `tests/component/data/database/test_meteorites.py::TestAst1557MeteoriteBatchClaim`
4. Read/update: `tests/component/data/database/test_meteorites.py::TestAst1557MeteoriteReadUpdate`
5. Retention helpers: `tests/component/data/database/test_meteorites.py::TestAst1557MeteoriteRetention`
6. Config registry: `tests/component/utils/test_config.py::TestAst1557MeteoriteStates`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_meteorites.py \
  tests/component/utils/test_config.py::TestAst1557MeteoriteStates \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-1689 · AST-1684

**Parent:** [AST-1684](https://linear.app/astralcareermatch/issue/AST-1684/reply-to-emails-in-meteorite-when-single-jd-no-link). **Publish:** `origin/sub/AST-1684/AST-1689-meteorite-row-contact-column-map-persist-soft-fail`.

Meteorite-table `electronic_contact` column (CREATE + ALTER ensure), `_UPDATE_METEORITE_ALLOWED`, and `insert_meteorite_rows` bind via `METEORITE_CONFIG["electronic_contact_column"]` (literal from AST-1688). Map/persist/Style D: **`docs/test-bible/core/meteorite.md`** § AST-1689.

| Area | Source | Component tests |
| --- | --- | --- |
| Schema CREATE + ALTER + allowlist + insert bind | `src/data/database.py` | **`TestAst1689ElectronicContactColumn`** |

**Broken / obsolete this pass:** none — additive column on AST-1557 table.

**Integration:** none — no existing scenario asserts meteorite contact column; do not invent.

## QA test manifest

1. Column schema/allowlist/insert: `tests/component/data/database/test_meteorites.py::TestAst1689ElectronicContactColumn`
2. Map/persist/BOT_BLOCKED/land/debug: `tests/component/core/test_meteorite.py::TestAst1689ElectronicContactMapPersist`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_meteorites.py::TestAst1689ElectronicContactColumn \
  tests/component/core/test_meteorite.py::TestAst1689ElectronicContactMapPersist \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/data/database/meteorites.md` — *(filled after publish)*
- `docs/test-bible/core/meteorite.md` — *(filled after publish)*

### AST-1691 · AST-1685

**Publish:** `origin/sub/AST-1685/AST-1691-meteorite-lookup-report-config-api`.

`get_meteorite_by_astral_job_id`. Primary QA manifest for AST-1691.

| Area | Source | Component tests |
| --- | --- | --- |
| Reverse-link helper | `src/data/database.py` | **`TestAst1691GetMeteoriteByAstralJobId`** |

## QA test manifest

1. `tests/component/data/database/test_meteorites.py::TestAst1691GetMeteoriteByAstralJobId`
2. `tests/component/utils/test_config.py::TestAst1691MeteoriteReportConfig`
3. `tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast565_recommended_report_manifest_tabs`
4. `tests/component/utils/test_config.py::TestAst1550DiscussionHopKeys::test_top_tabs_discussion_after_artifacts`
5. `tests/component/ui/api/test_api_system.py::TestAst1691ReportMeteoriteSections`
6. `tests/component/ui/api/test_api_system.py::TestAst1550ReportDiscussionSections`
7. `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_detail_related_meteorite_object`
8. `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_detail_related_meteorite_soft_fail`
9. revised detail null: `test_detail_returns_agent_story`, `test_detail_soft_fails_agent_story`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_meteorites.py::TestAst1691GetMeteoriteByAstralJobId \
  tests/component/utils/test_config.py::TestAst1691MeteoriteReportConfig \
  tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast565_recommended_report_manifest_tabs \
  tests/component/utils/test_config.py::TestAst1550DiscussionHopKeys::test_top_tabs_discussion_after_artifacts \
  tests/component/ui/api/test_api_system.py::TestAst1691ReportMeteoriteSections \
  tests/component/ui/api/test_api_system.py::TestAst1550ReportDiscussionSections \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_detail_returns_agent_story \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_detail_soft_fails_agent_story \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_detail_related_meteorite_object \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_detail_related_meteorite_soft_fail \
  -q
```

### AST-1694 · AST-1686

**Parent:** [AST-1686](https://linear.app/astralcareermatch/issue/AST-1686/hyperlink-to-job-with-meteorite-http-link). **Publish:** `origin/sub/AST-1686/AST-1694-minimal-listing-href-job-get`.

`get_meteorite_link_by_astral_job_id(astral_job_id)` — link-column-only reverse read for listing-href fallback; blank/None → `None` without query; blank `link` cell → `None`; `ORDER BY id DESC LIMIT 1`. Does **not** return a full meteorite row (AST-1685 / AST-1691 provenance). API attach: **`docs/test-bible/ui/api/api_jobs.md`** § AST-1694.

| Area | Source | Component tests |
| --- | --- | --- |
| Link-only reverse lookup | `src/data/database.py` | **`TestAst1694GetMeteoriteLinkByAstralJobId`** |

**Broken / obsolete:** none — additive helper.

**Integration:** none revised; do not invent.

## QA test manifest

1. Data helper: `tests/component/data/database/test_meteorites.py::TestAst1694GetMeteoriteLinkByAstralJobId`
2. Job detail `listing_href`: `tests/component/ui/api/test_api_jobs_ast1694_listing_href.py::TestAst1694ListingHref`
3. Detail key / hydrate kwargs: `tests/component/ui/api/test_api_jobs_ast1694_listing_href.py::TestAst1694DetailListingHrefKey`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_meteorites.py::TestAst1694GetMeteoriteLinkByAstralJobId \
  tests/component/ui/api/test_api_jobs_ast1694_listing_href.py \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-1748 · AST-1741

**Parent:** [AST-1741 — Add "Meteorites" to the Jobs navigation](https://linear.app/astralcareermatch/issue/AST-1741/add-meteorites-to-the-jobs-navigation). **Publish:** `origin/sub/AST-1741/AST-1748-candidate-meteorite-list-detail-api`.

`list_meteorites_for_candidate(candidate_id)` — blank/None/`""` → `[]` without querying; otherwise all surviving rows for that candidate ordered by `state_changed_at DESC`. API list/detail: **`docs/test-bible/ui/api/api_meteorite.md`** § AST-1748. Config constants `JOBS_METEORITES_*` consumed by the API (not asserted here).

| Area | Source | Component tests |
| --- | --- | --- |
| Candidate-scoped list + empty honesty + order | `src/data/database.py` | **`TestAst1748ListMeteoritesForCandidate`** |

**Broken / obsolete this pass:** AST-1557 insert/claim seeds assumed insert forced `NEW` and state `ERROR` — revised for AST-1713 caller-state insert + live `SCRAPE_ERROR` (no product change on this ticket; tree drift after sync).

**Integration:** none — no existing scenario exercises candidate meteorite list; do not invent.

## QA test manifest

1. Data helper: `tests/component/data/database/test_meteorites.py::TestAst1748ListMeteoritesForCandidate`
2. API list/detail: `tests/component/ui/api/test_api_meteorite.py::TestAst1748MeteoriteListDetailApi`
3. Regression (same modules): existing AST-1557 / AST-1689 / AST-1691 / AST-1694 / land classes in those files

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_meteorites.py \
  tests/component/ui/api/test_api_meteorite.py \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):** fill after `merge-tests`.

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
2. Job detail `listing_href`: `tests/component/ui/api/test_api_jobs.py::TestAst1694ListingHref` (+ revised `TestJobsRoutes::test_detail_returns_agent_story` / `test_detail_soft_fails_agent_story`)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_meteorites.py::TestAst1694GetMeteoriteLinkByAstralJobId \
  tests/component/ui/api/test_api_jobs.py::TestAst1694ListingHref \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_detail_returns_agent_story \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_detail_soft_fails_agent_story \
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

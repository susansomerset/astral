# API meteorite

**Test module:** `tests/component/ui/api/test_api_meteorite.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_meteorite.py` | `tests/component/ui/api/test_api_meteorite.py` | no |

---

### AST-1042 · AST-1034

**Parent:** [AST-1034 — Support meteorite jobs](https://linear.app/astralcareermatch/issue/AST-1034/support-meteorite-jobs). **Publish:** `origin/sub/AST-1034/AST-1042-api-create-job-under-meteorite-from-raw-html`.

`POST /api/candidates/<candidate_id>/meteorite/jobs` under `@require_auth` — **AST-1471** alias of `/meteorite/land` → `land_meteorite` (land outcome shape; was `create_meteorite_job`). Core: **`docs/test-bible/core/meteorite.md`**. See **### AST-1471**.

| Area | Source | Component tests |
| --- | --- | --- |
| 201 / 400 / 404 / 502 / 401 / non-admin allowed | `src/ui/api/api_meteorite.py` | **`TestAst1042MeteoriteCreateApi`** |

**Broken / obsolete:** none — new blueprint.

**Integration:** no existing scenario asserts this route — no revision; do not invent new integration coverage.

**AST-1042** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite.py::TestAst1042CreateMeteoriteJob \
  tests/component/ui/api/test_api_meteorite.py \
  -q
```

### AST-1471 · AST-1457

**Parent:** [AST-1457 — Meteorite component](https://linear.app/astralcareermatch/issue/AST-1457/meteorite-component). **Publish:** `origin/sub/AST-1457/AST-1471-meteorite-intake-api-contact-land-path`.

`POST /api/candidates/<id>/meteorite/land` (+ legacy `/meteorite/jobs` alias) wraps `asyncio.run(land_meteorite)` under `@require_auth`. HTTP status from land rollup (`created`→201, skip/supersede→200, error→400/404). Response is land outcome shape — not AST-1042 flat create fields. Contact: **`docs/test-bible/core/contact.md`**. Core land: **`docs/test-bible/core/meteorite.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Land + jobs alias + auth | `src/ui/api/api_meteorite.py` | **`TestAst1471MeteoriteLandApi`** + revised **`TestAst1042MeteoriteCreateApi`** |

**Broken / obsolete:** AST-1042 assertions on `create_meteorite_job` flat `{astral_job_id, state, latest_score}` — revised to land outcome shape / `land_meteorite` mock.

**Integration:** none revised.

## QA test manifest

1. API land + revised jobs alias: `tests/component/ui/api/test_api_meteorite.py`
2. Contact wrapper + Estelle `land_calls`: `tests/component/core/test_contact.py::TestAst1471ContactLandMeteorite`

**AST-1471** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_meteorite.py \
  tests/component/core/test_contact.py::TestAst1471ContactLandMeteorite \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-1748 · AST-1741

**Parent:** [AST-1741 — Add "Meteorites" to the Jobs navigation](https://linear.app/astralcareermatch/issue/AST-1741/add-meteorites-to-the-jobs-navigation). **Publish:** `origin/sub/AST-1741/AST-1748-candidate-meteorite-list-detail-api`.

Authenticated `GET /api/candidates/<candidate_id>/meteorites` → `{columns, meteorites}` (list projection, no `content`); `GET /api/meteorites/<id>` → `{sections, meteorite}` or 404. `link` / `astral_job_id` returned as stored. No `logger.info` on either GET. Data helper: **`docs/test-bible/data/database/meteorites.md`** § AST-1748.

| Area | Source | Component tests |
| --- | --- | --- |
| List scope / empty / columns / no info | `src/ui/api/api_meteorite.py` | **`TestAst1748MeteoriteListDetailApi`** |
| Detail content+metadata / link honesty / 404 / 500 | same | **`TestAst1748MeteoriteListDetailApi`** |

**Broken / obsolete:** none for land/create routes — additive GETs only.

**Integration:** harness registers system+candidate only — no existing meteorite scenario to revise; do not invent.

## QA test manifest

1. `tests/component/ui/api/test_api_meteorite.py::TestAst1748MeteoriteListDetailApi`
2. `tests/component/data/database/test_meteorites.py::TestAst1748ListMeteoritesForCandidate`
3. Land regression in same API module: `TestAst1042MeteoriteCreateApi` + `TestAst1471MeteoriteLandApi`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_meteorites.py \
  tests/component/ui/api/test_api_meteorite.py \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):** fill after `merge-tests`.

---

### AST-1974 · AST-1970

`_LIST_KEYS` gains `job_state` (landed job's current state; null when unlanded). **New:** `test_list_projects_landed_job_state_ast1974`. DB join: [`data/database/jobs.md`](../../data/database/jobs.md) § AST-1974. Manifest: [`api_jobs.md`](api_jobs.md) § AST-1974 item 4.

### AST-1980 · AST-1971 (Meteorites Created from landed job)

**Parent:** [AST-1971 — Add Created to the job list table](https://linear.app/astralcareermatch/issue/AST-1971). **Publish:** `origin/sub/AST-1971/AST-1980-created-col`. Job list pages are sibling AST-1979 ([`frontend/pages.md`](../../frontend/pages.md) § AST-1979).

`list_meteorites_for_candidate` adds `j.created_at AS job_created_at` to the existing AST-1974 `LEFT JOIN job` select. `_LIST_KEYS` carries `job_created_at`. `JOBS_METEORITES_LIST_COLUMNS` gains `{"key": "job_created_at", "label": "Created", "sortable": True, "type": "datetime"}` immediately before `state_changed_at`. `JobsMeteorites.tsx` is unchanged, and `ListPage` formats and sorts the column.

This is the single block for the ticket. It covers four test files across layers, so there are no per-file blocks.

| AC | Source | Component tests |
| --- | --- | --- |
| 6 `job_created_at` = `job.created_at`; null when unlanded or the job row is gone; `meteorite.created_at` kept | `database.list_meteorites_for_candidate` | **`tests/component/data/database/test_jobs.py`** › **`TestAst1980MeteoriteJobCreatedAt::test_job_created_at_is_landed_jobs_and_meteorite_created_at_kept`** (real SQLite; the job row's `created_at` is set far from the meteorite's) |
| 6 / 9 API projects `job_created_at` (null preserved) beside its own `created_at`; success path logs nothing | `api_meteorite._LIST_KEYS` | **`test_api_meteorite.py`** › **`test_list_projects_landed_job_created_at_ast1980`** |
| 7 Created entry, exact dict, immediately before `state_changed_at` | `config.JOBS_METEORITES_LIST_COLUMNS` | **`tests/component/utils/test_config.py`** › **`TestAst1974JobsListPartition::test_meteorites_columns_gain_created_before_state_changed_ast1980`**. API `columns` equals config via the existing **`test_list_scopes_candidate_and_returns_columns`** |
| 7 page: Created left of State Changed, `fmtTime(job_created_at)`, `—` when unlanded, first click ascending, second reverses, ▲/▼ on Created | `ListPage` (no page code) | **`tests/component/frontend/pages/test_JobsMeteorites.test.tsx`** › **`JobsMeteorites — AST-1980 Created column`** |
| 8 one SELECT carries both landed-job fields; no per-row `get_job` | same read | **`TestAst1980MeteoriteJobCreatedAt::test_one_select_and_no_per_row_get_job`** (sqlite `set_trace_callback`; `get_job` patched to fail) |
| 9 / 10 no new logger lines; config imports | source | greps below |

The DB, API, and config cases are red with the three product files reverted to `origin/ftr/AST-1971-created-col` and green on the publish tip. The page case passes both ways, because `JobsMeteorites.tsx` is unchanged and the test serves the columns. It guards the `ListPage` side of the contract.

**Test-tree notes:**
- The DB cases sit in `test_jobs.py` beside the AST-1974 join case, because `test_meteorites.py` is still collection-red on dev (`METEORITE_STATES_RETENTION` import). `test_jobs.py` gains `import sqlite3`.
- `test_JobsMeteorites.test.tsx` lifts the AST-1976 `PROD_COLUMNS` production mirror to module scope and adds the Created entry, so it matches `config.py` again. The AST-1976 cases find columns by label and stay green.
- The page case primes `ListPage`'s module-level ui_config cache with `loadUiConfig`, sets production `column_types.datetime` on it, and restores it in `finally`. The result does not depend on test order.

**Broken / obsolete:** none. The existing `job_state` config and API cases assert relative position and membership only.

**Baseline red (not this ticket):** 21 cases in `test_config.py` across retention, meteorite, telescope, `TestResolveTokens`, and other classes. The failing set is identical with AST-1980's product reverted.

## QA test manifest

1. **Backend (required):**

```bash
.venv/bin/python -m pytest -q \
  "tests/component/data/database/test_jobs.py::TestAst1980MeteoriteJobCreatedAt" \
  "tests/component/data/database/test_jobs.py::TestAst1974ExcludeStatesAndMeteoriteJobState" \
  tests/component/ui/api/test_api_meteorite.py \
  "tests/component/utils/test_config.py::TestAst1974JobsListPartition"
```

Expect all green.

2. **Page (required):** `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_JobsMeteorites.test.tsx` gives 9 passed.

3. **AC 7 / 8 / 9 / 10 greps:** `git diff origin/dev -- src/ui/frontend/src/pages/JobsMeteorites.tsx` is empty. `git diff origin/dev -- src/ui/api/api_meteorite.py | rg "^\+.*logger\.(info|exception|warning|error)"` returns nothing. `rg -n "job_created_at" src/data/database.py` shows only the one `SELECT` (plus the docstring). `python -c "import src.utils.config"` exits 0.

**Pass criterion:** items 1–3 hold. Narrowed runs, not the zero-arg harness. Full `test_config.py` shows only the baseline reds above.

**Bible shasum (after publish):** `git show origin/sub/AST-1971/AST-1980-created-col:docs/test-bible/ui/api/api_meteorite.md | shasum`

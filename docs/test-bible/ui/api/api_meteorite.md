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

# API meteorite

**Test module:** `tests/component/ui/api/test_api_meteorite.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_meteorite.py` | `tests/component/ui/api/test_api_meteorite.py` | no |

---

### AST-1042 · AST-1034

**Parent:** [AST-1034 — Support meteorite jobs](https://linear.app/astralcareermatch/issue/AST-1034/support-meteorite-jobs). **Publish:** `origin/sub/AST-1034/AST-1042-api-create-job-under-meteorite-from-raw-html`.

`POST /api/candidates/<candidate_id>/meteorite/jobs` under `@require_auth` — thin wrapper over `create_meteorite_job`. Maps ValueError → 400/404, other errors → 502, success → 201 (no nested `job` blob). Core: **`docs/test-bible/core/meteorite.md`**.

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

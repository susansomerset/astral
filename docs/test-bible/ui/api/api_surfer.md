# API surfer

**Test module:** `tests/component/ui/api/test_api_surfer.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_surfer.py` | `tests/component/ui/api/test_api_surfer.py` | no |

---

### AST-1236 · AST-1174

**Parent:** [AST-1174 — Human-paced fan-out over the batch worklist](https://linear.app/astralcareermatch/issue/AST-1174/human-paced-fan-out-over-the-batch-worklist). **Publish:** `origin/sub/AST-1174/AST-1236-pacing-config`.

Authenticated `GET /api/surfer/pacing_config` returns a plain-dict copy of `SURFER_PACING_CONFIG` (dwell centre/spread, `max_tabs`, `mv3_idle_ceiling_seconds`). Blueprint registered on `server.py`. Config block: **`docs/test-bible/utils/config.md`**. Extension `dwell` / `createTabBudget`: **`docs/test-bible/frontend/lib.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| 200 / 401 / non-admin / response copy | `src/ui/api/api_surfer.py` | **`TestAst1236SurferPacingConfigApi`** |
| Blueprint registration | `src/ui/server.py` | covered by import via **`server_client`** / **`surfer_client`** |

**Broken / obsolete:** none — new blueprint.

**Integration:** no existing scenario asserts this route — no revision; do not invent new integration coverage.

**AST-1236** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1236SurferPacingConfig \
  tests/component/ui/api/test_api_surfer.py \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_surferPacingConfig.test.ts
```

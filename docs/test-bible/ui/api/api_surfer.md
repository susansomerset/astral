# API surfer

**Test module:** `tests/component/ui/api/test_api_surfer.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_surfer.py` | `tests/component/ui/api/test_api_surfer.py` | no |

---

### AST-1236 · AST-1174

**Parent:** [AST-1174 — Human-paced fan-out over the batch worklist](https://linear.app/astralcareermatch/issue/AST-1174/human-paced-fan-out-over-the-batch-worklist). **Publish:** `origin/sub/AST-1174/AST-1236-pacing-config`.

Authenticated `GET /api/surfer/pacing_config` returns a plain-dict copy of `SURFER_PACING_CONFIG` (dwell centre/spread, `max_tabs`, `mv3_idle_ceiling_seconds`). Blueprint registered on `server.py`. Config block: **`docs/test-bible/utils/config.md`**. Extension `dwell` / `createTabBudget`: **`docs/test-bible/extension/lib.md`**.

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
cd src/ui/extension && npm run test:component -- \
  ../../../tests/component/extension/lib/test_surferPacingConfig.test.ts
```


### AST-1235 · AST-1173

**Parent:** [AST-1173 — Consent — install disclosure, affirmative opt-in, and off-switch](https://linear.app/astralcareermatch/issue/AST-1173/consent-install-disclosure-affirmative-opt-in-and-off-switch). **Publish:** `origin/sub/AST-1173/AST-1235-versioned-consent-record-and-api`.

Authenticated `GET`/`PUT /api/candidates/<id>/surfer/consent` — DTO includes `disclosure_copy` + `current_version` + `is_current`; PUT `action` `opt_in` (requires matching `accepted_version`) or `opt_out`; 404 missing candidate; 400 validation / bad action; `@require_auth`. Core: **`docs/test-bible/core/candidate.md`**. Config: **`docs/test-bible/utils/config.md`**. Registration: **`docs/test-bible/ui/server.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| GET DTO / PUT opt_in+opt_out / 400 / 404 / 401 | `src/ui/api/api_surfer.py` | **`TestAst1235SurferConsentApi`** |
| Blueprint registration | `src/ui/server.py` | **`surfer_consent_client`** fixture |

**Broken / obsolete:** none — consent routes additive on this module (pacing remains AST-1236). Pacing config import is lazy inside `TestAst1236SurferPacingConfigApi` so `::TestAst1235SurferConsentApi` collects on tips without `SURFER_PACING_CONFIG`. Consent API monkeypatches target `ui.api.api_surfer` (not `src.ui.api…`) so patches hit the live blueprint under dual `sys.path`.

**Integration:** no existing scenario asserts this route — no revision; do not invent new integration coverage.

**AST-1235** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1235SurferConsentConfig \
  tests/component/core/test_candidate.py::TestAst1235SurferConsent \
  tests/component/ui/api/test_api_surfer.py::TestAst1235SurferConsentApi \
  -q
```

# Railway

**Test module:** `tests/component/external/test_railway.py`

Catalog env names live in `src/utils/config.py` and are asserted from `tests/component/utils/test_config.py` (branch lock on `config.py`).

### AST-2250 · AST-2246 (Railway variable client)

**Parent:** [AST-2246](https://linear.app/astralcareermatch/issue/AST-2246). **Publish:** `origin/sub/AST-2246/AST-2250-railway-variable-client`. Plan: `docs/features/foundation/ast-2250-railway-variable-client.md`.

Write, delete, and deploy-trigger for one service variable. No variable read. Catalog maps each LLM server id plus `google_cse_api_key` and `google_cse_id` to a production variable-name shape and a local stub env name. `env.example` comments those names and does not assign them. Admin set and the status/expiry database write are later siblings.

| Area | Source | Component tests |
| --- | --- | --- |
| Target env names, catalog rows, `ada-1` → `CANDIDATE_ADA_1_ANTHROPIC`, stub names, commented `env.example` | `src/utils/config.py`, `env.example` | **`TestAst2250CandidateSecretCatalog`** |
| Upsert one key with `skipDeploys: true`; delete without `skipDeploys`; deploy returns id | `src/external/railway.py` | **`TestAst2250RailwayVariableClient`** |
| Failure logs once, redacts secret and token, raises `RailwayCallFailed` with operation and name only | same | same class |
| Blank name/value is `ValueError` before HTTP; missing `ASTRAL_RAILWAY_*` is bare `KeyError` | same | same class |

**Broken / obsolete:** none. **Integration:** none — this child does not change an existing `tests/integration/` scenario.

## QA test manifest — AST-2250

1. `tests/component/utils/test_config.py::TestAst2250CandidateSecretCatalog`
2. `tests/component/external/test_railway.py::TestAst2250RailwayVariableClient`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst2250CandidateSecretCatalog \
  tests/component/external/test_railway.py::TestAst2250RailwayVariableClient
```

**Pass criterion:** pytest green on those two classes. Not the zero-arg harness.

**Bible shasum (after publish):** `git show origin/sub/AST-2246/AST-2250-railway-variable-client:docs/test-bible/external/railway.md | shasum`

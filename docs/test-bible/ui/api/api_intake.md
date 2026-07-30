# Api Intake

**Test module:** `tests/component/ui/api/test_api_intake.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_intake.py` | `tests/component/ui/api/test_api_intake.py` | yes |


### AST-1015 · AST-952

**AST-1015:** Authenticated `POST /api/candidates/<id>/preamble/validate` — thin wrapper over `validate_preamble_answer`; 200 with structured failure; 404 candidate missing; 400 validation. Primary core: **`docs/test-bible/core/intake.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Route auth / shape / errors | `src/ui/api/api_intake.py` | **`TestAst1015PreambleValidateRoute`** |


---

### AST-1075 · AST-953

**Parent:** [AST-953 — Topic Menu Generation](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation). **Publish:** `origin/sub/AST-953/AST-1075-estelle-preamble-confirm-and-topic-menu-generation`.

Authenticated `POST /api/candidates/<id>/topic-menu/confirm` and `…/topic-menu/generate` — thin wrappers over intake callables. Confirm structured failure → **500** (unlike preamble validate 200). Generate without confirm stamp → **400**. Primary core: **`docs/test-bible/core/intake.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Route auth / shape / errors | `src/ui/api/api_intake.py` | **`TestAst1075TopicMenuRoutes`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_intake.py::TestAst1075TopicMenuRoutes \
  -q
```

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

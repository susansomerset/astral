# Api Candidate

**Test module:** `tests/component/ui/api/test_api_candidate.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_candidate.py` | `tests/component/ui/api/test_api_candidate.py` | yes |

### AST-723 · AST-378

PUT **`/api/candidates/:id/data`** calls **`apply_rubric_vectors_save`** after rubric normalization; GET detail calls **`hydrate_rubric_artifacts_for_response`** for Artifacts overlay (mirrors **AST-526** company_search_terms pattern).

| Area | Source | Component tests |
| --- | --- | --- |
| PUT sync + GET hydrate | `src/ui/api/api_candidate.py` | `TestAst723RubricVectorsApi` |


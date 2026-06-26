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

### AST-802 · AST-801

PUT **`/api/candidates/:id/data`** with **`artifacts.company_search_terms`** syncs table via **`apply_company_search_terms_save`**; blob key is not persisted (**AST-524** path unchanged; **AST-802** reconcile is eligibility-side — see **`data/database/dispatch_tasks.md`**).

| Area | Source | Component tests |
| --- | --- | --- |
| PUT table sync, no blob persist | `src/ui/api/api_candidate.py` | **`TestCandidateRoutes::test_put_company_search_terms_populates_table_without_persisting_blob`** |

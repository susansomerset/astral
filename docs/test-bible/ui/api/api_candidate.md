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

### AST-901 · AST-900

**`GET /api/candidates/:id/generate/<task_key>/pending`** recovers completed craft rubric generate; PUT **`artifacts.<rubric_key>`** clears **`pending_craft_generations`** for the matching craft task. Primary manifest: **`docs/test-bible/core/candidate.md`** § AST-901.

| Area | Source | Component tests |
| --- | --- | --- |
| Pending GET + clear on Save | `src/ui/api/api_candidate.py` | **`TestAst901PendingCraftGenerationApi`** |

### AST-904 · AST-900 (UAT fix)

PUT Save: clear pending **after** successful persist (keys captured before `apply_rubric_vectors_save` deletes them); on Save failure **re-stash** submitted criteria for page-return recovery. UI toast: **`docs/test-bible/frontend/components.md`** § AST-904.

| Area | Source | Component tests |
| --- | --- | --- |
| Clear after success (apply dels keys) | `src/ui/api/api_candidate.py` | **`TestAst901PendingCraftGenerationApi::test_put_artifact_clears_matching_pending`** (revised) |
| Re-stash on Save failure | `src/ui/api/api_candidate.py` | **`TestAst904SavePendingRecovery::test_put_save_failure_restashes_pending`** |

**AST-904** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_candidate.py::TestAst901PendingCraftGenerationApi::test_put_artifact_clears_matching_pending \
  tests/component/ui/api/test_api_candidate.py::TestAst904SavePendingRecovery \
  -q
```

### AST-906 · AST-900 (UAT fix)

PUT **`artifacts.get_rubric`** with craft-shaped literal `\n` criteria coerces via **`rubric_text`** and returns **200**; empty / single-grade content still **400**. Primary: **`docs/test-bible/utils/rubric_text.md`** § AST-906.

| Area | Source | Component tests |
| --- | --- | --- |
| Literal `\n` get_rubric Save | `src/ui/api/api_candidate.py` | **`TestAst906GetRubricLiteralNewlineSave`** |

### AST-970 · AST-871

Primary manifest: **`docs/test-bible/core/candidate.md`** § AST-970. Admin PUT state → **`transition_candidate_state`** (**`TestAst970AdminStateOverride`**).

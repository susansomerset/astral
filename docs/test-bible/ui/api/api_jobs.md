# Api Jobs

**Test module:** `tests/component/ui/api/test_api_jobs.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_jobs.py` | `tests/component/ui/api/test_api_jobs.py` | yes |

### AST-1100 · AST-1091

**Parent:** [AST-1091](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved). **Publish:** `origin/sub/AST-1091/AST-1100-resolve-artifact-agent-data-id`.

Job GET runs `hydrate_job_artifacts_for_display` (overlay only). PUT aliases `…/artifacts/job_resume` and `…/artifacts/proposed_answers` write body dicts onto those keys.

| Area | Source | Component tests |
| --- | --- | --- |
| GET hydrate + PUT aliases | `src/ui/api/api_jobs.py` | **`TestAst1100JobArtifactPinResolveApi`** |

**Broken / obsolete:** none — legacy `resume_content` / `application_responses` PUT routes retained.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestAst1100JobArtifactPinResolveApi \
  -q
```

### AST-1156 · AST-1150

**Parent:** [AST-1150](https://linear.app/astralcareermatch/issue/AST-1150/technical-fail-for-do-prompt). **Publish:** `origin/sub/AST-1150/AST-1156-skipped-retry-hop-correct-dispatchable-state`.

`POST /api/jobs/bulk_state` uses `transition_job_state` (priors + history) instead of `save_job` bypass; partial success on per-id `ValueError`.

| Area | Source | Component tests |
| --- | --- | --- |
| bulk_state transition | `api_jobs.py` | revised **`TestJobsRoutes::test_bulk_state_updates_jobs`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_bulk_state_updates_jobs \
  -q
```

### AST-1347 · AST-1346

**Parent:** [AST-1346](https://linear.app/astralcareermatch/issue/AST-1346/add-rubric-score-to-analysis-header). **Publish:** `origin/sub/AST-1346/AST-1347-persist-phase-score-breakdown`.

`_flatten_grades` lifts `{jd,do,get,like}_score_breakdown` when present on `job_data` (same loop as grades/scores/rubrics). Does not invent when absent. Persist math: **`docs/test-bible/core/consult.md`** (**AST-1347**).

| Area | Source | Component tests |
| --- | --- | --- |
| Flatten lift + absent | `src/ui/api/api_jobs.py` (`_flatten_grades`) | **`TestAst1347FlattenScoreBreakdown`** |

**Broken / obsolete:** none.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestAst1347FlattenScoreBreakdown \
  tests/component/ui/api/test_api_jobs.py::TestFlattenGrades \
  -q
```

### AST-1348 · AST-1346

**Parent:** [AST-1346](https://linear.app/astralcareermatch/issue/AST-1346/add-rubric-score-to-analysis-header). **Publish:** `origin/sub/AST-1346/AST-1348-analysis-header-score-title-chrome`.

After stored-trio lift, `_flatten_grades` derives missing `{jd,do,get,like}_score_breakdown` via `_phase_score_breakdown` when `{prefix}_score` + grades + job-carried rubric are present (response only). Header chrome: **`docs/test-bible/frontend/components.md`** / **`docs/test-bible/frontend/lib.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Derive / keep stored / omit unscored | `src/ui/api/api_jobs.py` (`_flatten_grades`) | **`TestAst1348FlattenDeriveBreakdown`** |

**Broken / obsolete:** none — AST-1347 absent-without-rubric case still holds.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestAst1348FlattenDeriveBreakdown \
  tests/component/ui/api/test_api_jobs.py::TestAst1347FlattenScoreBreakdown \
  -q
```

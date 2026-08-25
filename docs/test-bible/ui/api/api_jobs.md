# Api Jobs

**Test module:** `tests/component/ui/api/test_api_jobs.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_jobs.py` | `tests/component/ui/api/test_api_jobs.py` | yes |

### AST-1100 · AST-1091

**Parent:** [AST-1091](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved). **Publish:** `origin/sub/AST-1091/AST-1100-resolve-artifact-agent-data-id`.

Job GET runs `hydrate_job_artifacts_for_display` (overlay only). PUT `…/artifacts/proposed_answers` still writes a body dict onto that key. PUT `…/artifacts/job_resume` keep-pin rewrite is **AST-1430**.

| Area | Source | Component tests |
| --- | --- | --- |
| GET hydrate + PUT aliases | `src/ui/api/api_jobs.py` | **`TestAst1100JobArtifactPinResolveApi`** |

**Broken / obsolete:** `test_put_job_resume_writes_body_dict` — AST-1430 (dict-onto-pin). Legacy `resume_content` / `application_responses` PUT routes retained.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestAst1100JobArtifactPinResolveApi \
  -q
```

### AST-1430 · AST-1422

**Parent:** [AST-1422](https://linear.app/astralcareermatch/issue/AST-1422/finalize-job-resume-isnt-getting-parsed-into-the-job-resume-renderer). **Publish:** `origin/sub/AST-1422/AST-1430-test-gap-resume-content-copy-put-pin`. Product fix: **AST-1428**.

`PUT /api/jobs/<id>/artifacts/job_resume` keeps `artifact_key: "job_resume"` but calls `save_job_artifact_resume_content` (sibling blob). Never `save_job_data` a dict onto `artifacts.job_resume`. Copy-after-pin: **`docs/test-bible/core/agent.md`** § AST-1430.

| Area | Source | Component tests |
| --- | --- | --- |
| PUT keep-pin | `src/ui/api/api_jobs.py` | **`TestAst1100JobArtifactPinResolveApi::test_put_job_resume_writes_resume_content_keeps_pin`** |

**Broken / obsolete:** `test_put_job_resume_writes_body_dict` (dict onto pin).

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestAst1100JobArtifactPinResolveApi::test_put_job_resume_writes_resume_content_keeps_pin \
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

---

### AST-1420 · AST-1419

**Parent:** [AST-1419 — Create a Copy button on the Job Modal](https://linear.app/astralcareermatch/issue/AST-1419/create-a-copy-button-on-the-job-modal). **Publish:** `origin/sub/AST-1419/AST-1420-job-copy-snapshot-payload`.

`GET /api/jobs/<astral_job_id>/copy` (`@require_auth`) returns `assemble_job_copy_snapshot` JSON: 401 unauthenticated, 404 missing job, 500 assembler exception. Does not hydrate artifacts, flatten grades, or attach `agent_story`. Assembler contract: **`docs/test-bible/core/tracker.md`**. Copy button: AST-1421.

| Area | Source | Component tests |
| --- | --- | --- |
| Copy route wrap | `src/ui/api/api_jobs.py` | **`TestAst1420CopySnapshotRoute`** |

**Broken / obsolete:** none — detail hydrate (**AST-1100**) unchanged.

**Integration:** none — no existing jobs copy/detail scenario to revise.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestAst1420CopySnapshotRoute \
  tests/component/core/test_tracker.py::TestAst1420AssembleJobCopySnapshot \
  -q
```

### AST-1479 · AST-1464

**Parent:** [AST-1464 — Add means to mark job as applied for](https://linear.app/astralcareermatch/issue/AST-1464). **Publish:** `origin/sub/AST-1464/AST-1479-applied-jobs-list-home`.

`GET /api/jobs?view=applied` lists `APPLIED_JOB_STATES` ordered by `state_changed_at`. Page: **`docs/test-bible/frontend/pages.md`** § AST-1479.

| Area | Source | Component tests |
| --- | --- | --- |
| Applied view list | `src/ui/api/api_jobs.py` | **`test_list_applied_uses_applied_job_states`**; revised **`test_list_recommended_and_default`** (unknown view → `[]`, not `view=applied`) |

**Broken / obsolete:** `test_list_recommended_and_default` asserting `view=applied` → `[]`.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_applied_uses_applied_job_states \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_recommended_and_default \
  -q
```

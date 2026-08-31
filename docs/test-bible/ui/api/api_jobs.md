# Api Jobs

**Test module:** `tests/component/ui/api/test_api_jobs.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_jobs.py` | `tests/component/ui/api/test_api_jobs.py` | yes |

### AST-1100 · AST-1091

**Parent:** [AST-1091](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved). **Publish:** `origin/sub/AST-1091/AST-1100-resolve-artifact-agent-data-id`.

Job GET runs `hydrate_job_artifacts_for_display` (overlay only). PUT `…/artifacts/proposed_answers` still writes a body dict onto that key. PUT `…/artifacts/job_resume` body dual-write is **AST-1548 / AST-1554** (was keep-pin under AST-1430).

| Area | Source | Component tests |
| --- | --- | --- |
| GET hydrate + PUT aliases | `src/ui/api/api_jobs.py` | **`TestAst1100JobArtifactPinResolveApi`** |

**Broken / obsolete:** `test_put_job_resume_writes_body_dict` (pre-AST-1430); `test_put_job_resume_writes_resume_content_keeps_pin` — AST-1554 (keep-pin).

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestAst1100JobArtifactPinResolveApi \
  -q
```

### AST-1430 · AST-1422

**Parent:** [AST-1422](https://linear.app/astralcareermatch/issue/AST-1422/finalize-job-resume-isnt-getting-parsed-into-the-job-resume-renderer). **Publish:** `origin/sub/AST-1422/AST-1430-test-gap-resume-content-copy-put-pin`. Product fix: **AST-1428**.

**Broken / obsolete under AST-1548/AST-1554:** PUT keep-pin (`test_put_job_resume_writes_resume_content_keeps_pin`) — see AST-1554 dual-write node.

### AST-1554 · AST-1547 (gap — PUT body dual-write)

**Parent:** [AST-1547](https://linear.app/astralcareermatch/issue/AST-1547/job-resume-content-is-not-saving-to-the-job-record). Product: **AST-1548**.

`PUT /api/jobs/<id>/artifacts/job_resume` calls `save_job_artifact_job_resume_body` (dual-write `job_resume` + `resume_content`). Never writes an `agent_data_id` string onto the operator slot.

| Area | Source | Component tests |
| --- | --- | --- |
| PUT body dual-write | `src/ui/api/api_jobs.py` | **`TestAst1100JobArtifactPinResolveApi::test_put_job_resume_dual_writes_job_resume_body`** |

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestAst1100JobArtifactPinResolveApi::test_put_job_resume_dual_writes_job_resume_body \
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

### AST-1453 · AST-1446

**Parent:** [AST-1446 — When a job is in a Skipped state, make all fields editable](https://linear.app/astralcareermatch/issue/AST-1446/when-a-job-is-in-a-skipped-state-make-all-fields-editable). **Publish:** `origin/sub/AST-1446/AST-1453-persist-skipped-job-field-and-state-edits`.

GET detail attaches `fields_editable` + `legal_next_states` (empty when not skipped). Authenticated `PUT /api/jobs/<id>` persists via `persist_skipped_job_edits` (409 not-skipped / illegal hop / identity collision; 400 empty title/link/state/body; 404 missing). Core contract: **`docs/test-bible/core/tracker.md`**. Form chrome: AST-1454.

| Area | Source | Component tests |
| --- | --- | --- |
| GET meta + PUT status map | `src/ui/api/api_jobs.py` | **`TestAst1453SkippedEditMetaAndPut`** |

**Broken / obsolete:** none — additive keys on GET detail; existing story/hydrate suites still hold.

**Integration:** none — no existing jobs detail/persist scenario to revise.

## QA test manifest

1. Core successors + persist gate/writes/hop ordering: `tests/component/core/test_tracker.py::TestAst1453LegalJobSuccessorStates` + `::TestAst1453PersistSkippedJobEdits`
2. GET meta + PUT auth/status/detail shape: `tests/component/ui/api/test_api_jobs.py::TestAst1453SkippedEditMetaAndPut`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1453LegalJobSuccessorStates \
  tests/component/core/test_tracker.py::TestAst1453PersistSkippedJobEdits \
  tests/component/ui/api/test_api_jobs.py::TestAst1453SkippedEditMetaAndPut \
  -q
```

**Bible shasum (this pass):** `docs/test-bible/ui/api/api_jobs.md` → `0dc463232d8241a0f85e6a85c71b9073aa9a7143` (pre-line)

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

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

### AST-1488 · AST-1485

**Parent:** [AST-1485 — Enable Applied job list in nav](https://linear.app/astralcareermatch/issue/AST-1485). **Publish:** `origin/sub/AST-1485/AST-1488-applied-jobs-list-home-re-land`.

**Re-land of AST-1479** — same `view=applied` list branch. **Existing coverage — no new tests.** Full manifest: **`docs/test-bible/frontend/pages.md`** § AST-1488.

| Area | Source | Component tests |
| --- | --- | --- |
| Applied view list | `src/ui/api/api_jobs.py` | **`test_list_applied_uses_applied_job_states`**; **`test_list_recommended_and_default`** |

**Broken / obsolete:** none.

**Integration:** none.

### AST-1498 · AST-1485

**Parent:** [AST-1485 — Enable Applied job list in nav](https://linear.app/astralcareermatch/issue/AST-1485). **Publish:** `origin/sub/AST-1485/AST-1498-candidate-applied-missing-from-applied-screen`.

Applied list must include post-applied jobs on stem/meteorite companies when `company.candidate_id` is NULL — supplement + repair pass on `view=applied` only. Page POST body: **`docs/test-bible/frontend/pages.md`** § AST-1498.

| Area | Source | Component tests |
| --- | --- | --- |
| Applied view stem linkage (**[bug-repro]**) | `src/ui/api/api_jobs.py` | **`test_list_applied_includes_stem_job_null_company_candidate_id_ast1498`** |
| Primary pass params (regression) | same | revised **`test_list_applied_uses_applied_job_states`** (multi-call safe) |

**Broken / obsolete:** none pre-fix — **`test_list_applied_uses_applied_job_states`** revised so supplement pass does not false-fail post-fix.

**Integration:** none.

## QA test manifest

1. **[bug-repro]** API stem NULL linkage: `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_applied_includes_stem_job_null_company_candidate_id_ast1498`
2. Applied primary pass regression: `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_applied_uses_applied_job_states`
3. **[bug-repro]** Page POST `candidate_id`: `tests/component/frontend/pages/test_JobsApplied.test.tsx` — **`AST-1498 [bug-repro]`**

**AST-1498** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_applied_includes_stem_job_null_company_candidate_id_ast1498 \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_applied_uses_applied_job_states \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_JobsApplied.test.tsx \
  --testNamePattern="AST-1498"
```

**Pass criterion:** repro lines flip red→green after `make-fix`; regression line stays green — not zero-arg harness / branch-lock gate.

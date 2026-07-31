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

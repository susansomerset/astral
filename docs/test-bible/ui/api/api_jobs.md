# Api Jobs

**Test module:** `tests/component/ui/api/test_api_jobs.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_jobs.py` | `tests/component/ui/api/test_api_jobs.py` | yes |

### AST-1063 · AST-1059

**Publish:** `origin/sub/AST-1059/AST-1063-job-carried-rubric-hydration-for-list-columns`.

`_flatten_grades` lifts `joblist_rubric` / `jd_rubric` / `get_rubric` / `do_rubric` / `like_rubric` (and existing `*_grades` / `*_score`) for list + detail. Pre-snapshot jobs omit `*_rubric` keys. Write-path snapshot: **`docs/test-bible/core/consult.md`** (**AST-1063**).

| Area | Source | Component tests |
| --- | --- | --- |
| Flatten lift + absent pre-snapshot | `src/ui/api/api_jobs.py` | **`TestFlattenGrades::test_ast1063_lifts_job_carried_rubrics_and_scores`** (+ existing latest_score lift) |

**Broken / obsolete:** none.

**Integration:** none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestFlattenGrades \
  tests/component/core/test_consult.py::TestAst1063JobCarriedRubricHydration \
  -q
```

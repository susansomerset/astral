# Jobs

**Test module:** `tests/component/data/database/test_jobs.py`

_(Coverage map and manifest blocks appended by Betty `qa-child`.)_

### AST-732 · AST-728

Partial unique index **`idx_job_identity_unique`** on **`(company, job_title, company_job_id)`** for complete identity triples (NULL/empty **`company_job_id`** or **`job_title`** excluded). **`save_job`** returns **`False`** on new-row INSERT identity duplicate bounce; UPDATE path unchanged. Prerequisite **AST-729** cleanup in environments with existing duplicate complete triples.

| Area | Source | Component tests |
| --- | --- | --- |
| Index lazy migration + insert bounce | `src/data/database.py` | `tests/component/data/database/test_jobs.py::TestAst732JobIdentityUniqueIndex`, `TestAst732SaveJobDuplicateBounce` |
| Ingest duplicate count wiring | `src/core/tracker.py` | `tests/component/core/test_tracker.py::TestIngestJobs::test_counts_identity_duplicate_bounce_from_save_job`, `TestIngestBoardListings::test_counts_identity_duplicate_bounce_from_save_job` |

**AST-732** narrowed run:

```bash
.venv/bin/python -m pytest \
  tests/component/data/database/test_jobs.py::TestAst732JobIdentityUniqueIndex \
  tests/component/data/database/test_jobs.py::TestAst732SaveJobDuplicateBounce \
  tests/component/core/test_tracker.py::TestIngestJobs::test_counts_identity_duplicate_bounce_from_save_job \
  tests/component/core/test_tracker.py::TestIngestBoardListings::test_counts_identity_duplicate_bounce_from_save_job \
  tests/component/data/database/test_jobs.py::TestSaveJob \
  tests/component/core/test_tracker.py::TestIngestJobs::test_counts_new_and_duplicate_rows \
  -q
```

### AST-733 · AST-728

**`get_job_id_by_identity`** and **`delete_job`** support post-qualify collision handling. **`delete_job`** does not cascade related records.

| Area | Source | Component tests |
| --- | --- | --- |
| Identity lookup + single-row delete | `src/data/database.py` | `tests/component/data/database/test_jobs.py::TestAst733JobIdentityHelpers` |

See **`docs/test-bible/core/tracker.md`** and **`docs/test-bible/core/consult.md`** for **`initialize_job`** / **`qualify_job_listings`** wiring.


### AST-908 · AST-907

Jobs UI below-floor helpers (`score_floor_by_trigger_for_candidate`, `list_jobs_below_dispatch_score_floor`, `count_jobs_below_dispatch_score_floor`) gate on **`dispatch_claim_uses_score_floor`** so **PASSED_JOBLIST** (and every other claim-gated In Review trigger) joins the floors map. Pre-score triggers (**VALID_TITLE**, **JD_READY**) stay out. Virtual Skipped membership only — no DB skip state. Config comment documents UI vs **`PASSED_SCORE_GATED_STATES`** (claim-sort set unchanged).

| Area | Source | Component tests |
| --- | --- | --- |
| Floors map + list/count below floor | `src/data/database.py` | `tests/component/data/database/test_jobs.py::TestAst908BelowDispatchScoreFloorViews` |
| Claim helper (existing; legacy VALID_TITLE assert rewritten post-AST-898) | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst586DispatchClaimScoreFloor` |
| API wiring (existing mocks) | `src/ui/api/api_jobs.py` | `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_in_review_filters_score_floor`, `test_list_skipped_view_appends_virtual_rows` |

**Broken / obsolete:** none — prior floors tests did not assert **PASSED_JOBLIST** exclusion; API route tests mock the helpers.

**AST-908** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_jobs.py::TestAst908BelowDispatchScoreFloorViews \
  tests/component/utils/test_config.py::TestAst586DispatchClaimScoreFloor \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_in_review_filters_score_floor \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_skipped_view_appends_virtual_rows
```

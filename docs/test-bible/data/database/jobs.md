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

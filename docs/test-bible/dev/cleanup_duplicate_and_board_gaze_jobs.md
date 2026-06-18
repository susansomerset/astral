# Cleanup Duplicate and Board-Gaze Jobs (migration script)

**Test module:** `tests/component/scripts/test_cleanup_duplicate_and_board_gaze_jobs.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py` | `tests/component/scripts/test_cleanup_duplicate_and_board_gaze_jobs.py` | no |

**Existing coverage (reuse):** board placeholder prefix — `src/utils/config.py` **`BOARDS_CONFIG["ingest"]["placeholder_company_prefix"]`** (`tests/component/utils/test_config.py`); job schema helpers — `src/data/database.py` **`_ensure_job_schema`** (database cluster tests).

---

### AST-729 (parent AST-728)

One-time cleanup: bulk DELETE board-gaze placeholder companies (`__board__*`), then identity dedupe on `(company, job_title, company_job_id)` triples (earliest `created_at` survivor; `astral_job_id` tie-break). Incomplete identity triples excluded. Related tables untouched. CLI `--dry-run`, `--skip-board-cleanup`, `--skip-dedupe`, `--company`.

| Area | Source | Component tests |
| --- | --- | --- |
| Duplicate group discovery / ordering | `scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py` | `TestFindDuplicateIdentityGroups` |
| Job DELETE helper | same | `TestDeleteJobsByAstralJobIds` |
| Board-gaze phase dry-run / live / empty | same | `TestBoardGazeCleanup` |
| Identity dedupe dry-run / live survivor | same | `TestIdentityDedupe` |
| Phase order, skip flags, summary | same | `TestRunCleanup` |

**AST-729** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/scripts/test_cleanup_duplicate_and_board_gaze_jobs.py \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

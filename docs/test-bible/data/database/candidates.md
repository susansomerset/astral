# Candidates

**Test module:** `tests/component/data/database/test_candidates.py`

_(Coverage map and manifest blocks appended by Betty `qa-child`.)_

### AST-971 · AST-871

Primary manifest: **`docs/test-bible/core/candidate.md`** § AST-971. Column coverage: **`TestAst971CandidateStateHistoryColumn`**.

### AST-973 · AST-871

Primary manifest: **`docs/test-bible/core/candidate.md`** § AST-973. **`hard_delete_candidate`**, **`migrate_legacy_candidate_states`** (ensure = phases BC only).

### AST-1134 · AST-1128

**Parent:** [AST-1128 — gaze_email — candidate-bound dispatch (redesign)](https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign). **Publish:** `origin/sub/AST-1128/AST-1134-retire-null-shell-candidate-bound-config`.

Adds nullable `candidate.last_email_check` (fresh CREATE + ALTER migrate) and `update_candidate_last_email_check` stamp helper. Call site after `gaze_email` run is **AST-1136**.

| Area | Source | Component tests |
| --- | --- | --- |
| Column + stamp helper | `src/data/database.py` | **`TestAst1134LastEmailCheck`** |

**Broken / obsolete:** none — additive column/helper.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_candidates.py::TestAst1134LastEmailCheck \
  -q
```

### AST-1258 · AST-1257

**Parent:** [AST-1257 — candidate table does not have batch_id](https://linear.app/astralcareermatch/issue/AST-1257/candidate-table-does-not-have-batch-id). **Publish:** `origin/sub/AST-1257/AST-1258-candidate-batch-lock-schema-and-pool-claim-apis`.

Candidate row `batch_id` / `batch_created_at` (null/empty = unclaimed) plus data-layer pool claim → get → clear peers of job/company (`claim_candidate_batch` batch_id-first, cross-candidate pool, no single-ctx gate). Eligibility / Avail for non-inflow candidate stage tasks: **`docs/test-bible/data/database/dispatch_tasks.md`** § AST-1258. Dispatcher/core wrappers: sibling **AST-1259**. Canon/docs: **AST-1260**.

| Area | Source | Component tests |
| --- | --- | --- |
| Schema columns + unclaimed save | `src/data/database.py` | **`TestAst1258CandidateBatchClaim::test_schema_has_nullable_batch_columns`**, **`::test_save_leaves_batch_unclaimed`** |
| Claim → get → clear multi-row; concurrent refuse; release all | `src/data/database.py` | **`TestAst1258CandidateBatchClaim::test_claim_get_clear_multi_row_pool`** |
| Claim unions primary + retry states | `src/data/database.py` | **`TestAst1258CandidateBatchClaim::test_claim_unions_retry_states`** |

**Broken / obsolete (Betty revision):** none in this module — claim APIs are additive. Stage Avail assertion revision lives in **`test_dispatch_tasks.py`**.

**Integration:** none (no existing integration scenario asserts unlocked candidate claim / inflow-only stage Avail).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_candidates.py::TestAst1258CandidateBatchClaim \
  -q
```


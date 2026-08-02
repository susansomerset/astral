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

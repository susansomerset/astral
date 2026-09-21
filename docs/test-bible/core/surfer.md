# Surfer

**Test module:** `tests/component/core/test_surfer.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/surfer.py` | `tests/component/core/test_surfer.py` | no |

---

### AST-1229 · AST-1169

**Parent:** [AST-1169 — Surfer batch — durable worklist state and batch-scoped intake](https://linear.app/astralcareermatch/issue/AST-1169/surfer-batch-durable-worklist-state-and-batch-scoped-intake). **Publish:** `origin/sub/AST-1169/AST-1229-surfer-batch-entity`.

Durable Surfer batch entity: create RUNNING worklist + `lifecycle.active_surfer_batch_id` pointer; URL outcomes with auto-COMPLETE when all terminal (`requires_all_urls_terminal`); CANCELLED clears pointer without all-terminal; `job_ids` association survives dispatcher `claim_job_batch` / `clear_job_batch` (does not use `job.batch_id`). Config: **`docs/test-bible/utils/config.md`**. Data: **`docs/test-bible/data/database/surfer_batches.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Create / pointer / validation / one active batch | `src/core/surfer.py` | **`TestAst1229SurferBatchEntity`** |
| URL outcomes + auto-complete + CANCELLED + COMPLETED gate | `src/core/surfer.py` | **`TestAst1229SurferBatchEntity`** |
| Job association vs claim/clear (AC6/AC7) | `src/core/surfer.py` + `database.claim_job_batch` / `clear_job_batch` | **`TestAst1229SurferBatchEntity::test_job_association_survives_dispatcher_claim_and_clear`** |

**Broken / obsolete:** none — new module. Fixture: `_surfer_batch_schema_ensured` added to `tests/component/{core,data,ui}/conftest.py` `_SCHEMA_FLAGS`.

**Integration:** no existing scenario asserts Surfer batch — no revision; do not invent new integration coverage.

**AST-1229** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1229SurferBatchConfig \
  tests/component/data/database/test_surfer_batches.py \
  tests/component/core/test_surfer.py \
  -q
```

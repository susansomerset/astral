# Surfer Batches

**Test module:** `tests/component/data/database/test_surfer_batches.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/data/database.py` (`surfer_batch` helpers) | `tests/component/data/database/test_surfer_batches.py` | no (module-level lock on `database.py` unchanged) |

---

### AST-1229 · AST-1169

**Parent:** [AST-1169 — Surfer batch — durable worklist state and batch-scoped intake](https://linear.app/astralcareermatch/issue/AST-1169/surfer-batch-durable-worklist-state-and-batch-scoped-intake). **Publish:** `origin/sub/AST-1169/AST-1229-surfer-batch-entity`.

New `surfer_batch` table + insert/get/list/update helpers; lazy-ensure + `_UPSERT_*` registry; fixture flag `_surfer_batch_schema_ensured`. Does **not** touch `claim_job_batch` / `clear_job_batch` / `dispatch_ledger`. Core: **`docs/test-bible/core/surfer.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Insert/get/list/duplicate + update + registry | `src/data/database.py` | **`TestAst1229SurferBatchData`** |

**Broken / obsolete:** none — new helpers. `tests/component/data/conftest.py` `_SCHEMA_FLAGS` gains `_surfer_batch_schema_ensured`.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_surfer_batches.py \
  -q
```

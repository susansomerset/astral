# Rubric Vectors

**Test module:** `tests/component/data/database/test_rubric_vectors.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/data/database.py` (`rubric_vector`, `vector_feedback`, purge helper) | `tests/component/data/database/test_rubric_vectors.py` | no |
| `src/utils/rubric_text.py` (`rubric_vector_content_fingerprint`) | `tests/component/scripts/test_backfill_rubric_vectors.py` | no |

---

### AST-722 · AST-378

Normalized **`rubric_vector`** + **`vector_feedback`** SQLite tables, **`FEEDBACK`** in **`BLOCK_TYPES`**, **`RUBRIC_FEEDBACK_CONFIG`**, fingerprint helper, and backfill/purge migration script. No runtime read/write cutover (**AST-723**).

| Area | Source | Component tests |
| --- | --- | --- |
| Schema insert/list/count | `src/data/database.py` | `TestRubricVectorSchema` |
| `vector_feedback` lazy ensure | `src/data/database.py` | `TestRubricVectorSchema::test_vector_feedback_table_ensures_on_connection` |
| Legacy artifact purge helper | `src/data/database.py` | `TestPurgeLegacyRubricArtifacts` |
| `FEEDBACK` block type on `save_agent_data` | `src/data/database.py`, `src/utils/config.py` | `TestFeedbackBlockType`; `TestAst722RubricFeedbackConfig` (`test_config.py`) |
| `RUBRIC_FEEDBACK_CONFIG` shape | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst722RubricFeedbackConfig` |
| Backfill migration script | `scripts/migrations/backfill_rubric_vectors.py` | `tests/component/scripts/test_backfill_rubric_vectors.py` |

**AST-722** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_rubric_vectors.py \
  tests/component/scripts/test_backfill_rubric_vectors.py \
  tests/component/utils/test_config.py::TestAst722RubricFeedbackConfig \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-723 · AST-378

**`sync_rubric_vectors_from_criteria`** fingerprint-gated retire/insert; AST-723 **`agent_task`** token migration (`{$RUBRIC_VECTORS}`). Builds on **AST-722** table.

| Area | Source | Component tests |
| --- | --- | --- |
| Sync importance-only / fingerprint retire / code removal | `src/data/database.py` | `TestAst723SyncRubricVectors` |
| Legacy rubric token migration on `agent_task` | `src/data/database.py` | `TestAst723RubricTokenMigration` |

**AST-723** narrowed run (database cluster):

```bash
./scripts/testing/run_component_tests.sh   tests/component/data/database/test_rubric_vectors.py::TestAst723SyncRubricVectors   tests/component/data/database/test_rubric_vectors.py::TestAst723RubricTokenMigration   -q
```


### AST-724 · AST-378

Runtime **`vector_feedback`** row inserts, **`store_feedback_block`** FEEDBACK persistence, and **`list_rubric_vector_uuid_by_code`** map for lenient envelope capture. Builds on **AST-722** / **AST-723** tables.

| Area | Source | Component tests |
| --- | --- | --- |
| Code → rubric_vector_uuid map | `src/data/database.py` | `TestAst724VectorFeedbackRows::test_list_rubric_vector_uuid_by_code` |
| Parsed vector → 3 feedback rows | `src/data/database.py` | `TestAst724VectorFeedbackRows::test_insert_vector_feedback_rows_writes_three_types_per_vector` |
| Raw FEEDBACK agent_data block | `src/data/database.py` | `TestAst724VectorFeedbackRows::test_store_feedback_block_persists_feedback_agent_data` |

Parse helpers + agent capture: **`docs/test-bible/utils/rubric_feedback.md`**, **`docs/test-bible/core/agent.md`**.

**AST-724** narrowed run (database cluster):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_rubric_vectors.py::TestAst724VectorFeedbackRows \
  -q
```

### AST-725 · AST-378

**`list_vector_feedback`** filters (owner expansion, batch, vector code) and **`aggregate_vector_feedback_by_vector`** per-current-rubric summaries. Builds on **AST-722**–**AST-724** tables.

| Area | Source | Component tests |
| --- | --- | --- |
| Owner task_key → run keys filter | `src/data/database.py` | `TestAst725ListVectorFeedback::test_owner_task_key_expands_to_consumer_and_craft_run_keys` |
| Batch + vector_code filters | `src/data/database.py` | `TestAst725ListVectorFeedback::test_filters_batch_id_and_vector_code` |
| Per-vector distributions | `src/data/database.py` | `TestAst725AggregateVectorFeedback::test_per_vector_distributions_and_zero_feedback_vectors` |

Admin API + page: **`docs/test-bible/ui/api/api_admin.md`**, **`docs/test-bible/frontend/pages.md`**.

### AST-809 · AST-378 (UAT fix)

**`vector_feedback`** rows persist **`batch_size`** and **`completed_at`** with **`batch_id`**; insert skipped when **`batch_id`** falsy. Builds on **AST-724** capture + **AST-725** list.

| Area | Source | Component tests |
| --- | --- | --- |
| Insert skips empty batch_id | `src/data/database.py` | `TestAst809VectorFeedbackBatchMetadata::test_insert_requires_batch_id` |
| batch_size + completed_at on rows | `src/data/database.py` | `TestAst809VectorFeedbackBatchMetadata::test_insert_persists_batch_size_and_completed_at` |

Capture hook: **`docs/test-bible/core/agent.md`**. Admin API columns: **`docs/test-bible/ui/api/api_admin.md`**.

**AST-809** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_rubric_vectors.py::TestAst809VectorFeedbackBatchMetadata \
  tests/component/core/test_agent.py::TestAst809VectorFeedbackBatchMetadata \
  tests/component/ui/api/test_api_admin.py::TestAst809VectorFeedbackBatchMetadata \
  -q
```

---

### AST-808 · AST-378 (UAT fix)

**`list_vector_feedback`** returns **`vector_content`** and **`vector_importance`** from joined **`rubric_vector`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Content + importance on list rows | `src/data/database.py` | `TestAst808ListVectorFeedbackContent` |

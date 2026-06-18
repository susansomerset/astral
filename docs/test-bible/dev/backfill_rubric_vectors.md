# Backfill Rubric Vectors (migration script)

**Test module:** `tests/component/scripts/test_backfill_rubric_vectors.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `scripts/migrations/backfill_rubric_vectors.py` | `tests/component/scripts/test_backfill_rubric_vectors.py` | no |

**Existing coverage (reuse):** database cluster CRUD + purge — `docs/test-bible/data/database/rubric_vectors.md` (**AST-722**).

---

### AST-722 · AST-378

One-time backfill from legacy **`candidate_data.artifacts`** rubric keys into **`rubric_vector`** rows; idempotent per `(candidate_id, task_key)`; optional gated **`--purge-artifacts`** (requires **`--confirm-purge`**).

| Area | Source | Component tests |
| --- | --- | --- |
| `_normalize_importance` bounds/default | `scripts/migrations/backfill_rubric_vectors.py` | `TestNormalizeImportance` |
| `_criterion_from_artifact_item` code gen / empty content | same | `TestCriterionFromArtifactItem` |
| Dry-run vs live backfill; idempotent skip; missing `agent_task` | same | `TestBackfillCandidateRubricVectors` |
| Purge dry-run vs live | same | `TestPurgeRubricArtifacts` |
| CLI `--purge-artifacts` without `--confirm-purge` exits 1 | same | `TestBackfillMain` |

**AST-722** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/scripts/test_backfill_rubric_vectors.py \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

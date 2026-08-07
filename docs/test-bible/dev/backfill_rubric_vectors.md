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

---

### AST-1200 · AST-1198

**Parent:** [AST-1198 — Rubric criteria prompts are not appearing in UI Artifacts](https://linear.app/astralcareermatch/issue/AST-1198/rubric-criteria-prompts-are-not-appearing-in-ui-artifacts). **Publish:** `origin/sub/AST-1198/AST-1200-restore-rubric-criteria-prompts`.

Delete local `_ARTIFACT_KEY_TO_TASK_KEY`; resolve owners via `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` from config so `meteorite_jobdesc_rubric` → `evaluate_meteorite` cannot drift. UI expand-all: **`docs/test-bible/frontend/components.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Config owner map (no local dict; incl. meteorite) | `scripts/migrations/backfill_rubric_vectors.py` | **`TestAst1200OwnerMapFromConfig`** |

**Broken / obsolete:** none — import swap only; dry-run / purge unchanged.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/scripts/test_backfill_rubric_vectors.py::TestAst1200OwnerMapFromConfig \
  -q
```

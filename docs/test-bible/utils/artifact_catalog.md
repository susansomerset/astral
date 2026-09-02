# Artifact catalog

**Test module:** `tests/component/utils/test_artifact_catalog.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/utils/artifact_catalog.py` | `tests/component/utils/test_artifact_catalog.py` | no |
| `src/utils/config.py` (`ARTIFACT_CATALOG` pilot) | same (lookup asserts) | yes (`config.py` lock unchanged) |

---

### AST-1573 · AST-1568 (artifact catalog registry)

**Parent:** [AST-1568 — Implement patt.artifact.manage-catalog](https://linear.app/astralcareermatch/issue/AST-1568/implement-pattartifactmanage-catalog). **Publish:** `origin/sub/AST-1568/AST-1573-artifact-catalog-registry`.

Pilot `ARTIFACT_CATALOG` with sole key `base_resume` (candidate-scoped, `body_shape=resume_content`, `ingestion_owner=candidate`) plus read-only helpers `get_catalog_entry` / `require_catalog_entry` / `is_candidate_scoped`. Unknown keys fail fast (`ValueError` / soft `None`). Scaffold proves catalog-derived identity plugs into existing `save_artifact` → `get_current_artifact` — not write-operative / read-current product paths (AST-1569+), not coat-check retirement (AST-1572).

| Area | Source | Component tests |
| --- | --- | --- |
| Catalog lookup + fail-fast + shallow copy | `src/utils/artifact_catalog.py`, `ARTIFACT_CATALOG` | **`TestAst1573ArtifactCatalog`** |
| Catalog identity → data-layer round-trip | `src/data/database.py` (existing APIs) | **`TestAst1573ArtifactCatalog::test_catalog_identity_save_get_round_trip`** |

**Broken / obsolete:** none for this slice. Existing `tests/component/data/database/test_artifacts.py` base_resume table coverage stays (data-layer identity). Candidate `artifacts.base_resume` blob / coat-check retargets remain siblings AST-1569–AST-1572 — do not invent coat-check or blob-read expectations here.

**Integration:** none (no existing scenario invalidated; artifact-pipeline integration gap stays should-have — do not invent).

## QA test manifest

1. **Lookup + fail-fast + copy (required):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_artifact_catalog.py::TestAst1573ArtifactCatalog::test_pilot_entry_lookup_and_scope \
  tests/component/utils/test_artifact_catalog.py::TestAst1573ArtifactCatalog::test_unknown_and_blank_fail_fast \
  tests/component/utils/test_artifact_catalog.py::TestAst1573ArtifactCatalog::test_require_returns_shallow_copy \
  -q
```

2. **Scaffold round-trip (required — AC3):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_artifact_catalog.py::TestAst1573ArtifactCatalog::test_catalog_identity_save_get_round_trip \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.

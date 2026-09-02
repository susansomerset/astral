# Artifact catalog

**Test module:** `tests/component/utils/test_artifact_catalog.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/utils/artifact_catalog.py` | `tests/component/utils/test_artifact_catalog.py` | no |
| `src/utils/config.py` (`ARTIFACT_CONFIG` pilot) | same (lookup asserts) | yes (`config.py` lock unchanged) |

---

### AST-1573 · AST-1568 (artifact catalog registry)

**Parent:** [AST-1568 — Implement patt.artifact.manage-catalog](https://linear.app/astralcareermatch/issue/AST-1568/implement-pattartifactmanage-catalog). **Publish:** `origin/sub/AST-1568/AST-1573-artifact-catalog-registry`.

Pilot registry + read-only helpers `get_catalog_entry` / `require_catalog_entry` / `is_candidate_scoped`. Scaffold proves catalog-derived identity plugs into existing `save_artifact` → `get_current_artifact`. **AST-1575** retargets block/key naming (see below) — do not assert flat `ARTIFACT_CATALOG` / bare `base_resume` catalog keys.

| Area | Source | Component tests |
| --- | --- | --- |
| Catalog lookup + fail-fast + shallow copy | `src/utils/artifact_catalog.py`, `ARTIFACT_CONFIG` | **`TestAst1573ArtifactCatalog`** |
| Catalog identity → data-layer round-trip | `src/data/database.py` (existing APIs) | **`TestAst1573ArtifactCatalog::test_catalog_identity_save_get_round_trip`** |

**Broken / obsolete:** flat-key / `ARTIFACT_CATALOG` asserts retired by **AST-1575**.

**Integration:** none.

## QA test manifest (AST-1573 — superseded naming by AST-1575)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_artifact_catalog.py::TestAst1573ArtifactCatalog \
  -q
```

**Pass criterion:** pytest green on those node ids — not zero-arg harness / branch-lock gate unless **`test-child`** widens.

---

### AST-1575 · AST-1568 (bug — ARTIFACT_CONFIG + hierarchical keys)

**Parent:** [AST-1568](https://linear.app/astralcareermatch/issue/AST-1568/implement-pattartifactmanage-catalog). **Publish:** `origin/sub/AST-1568/AST-1575-artifact-config-hierarchical-keys`.

Rename `ARTIFACT_CATALOG` → `ARTIFACT_CONFIG`; pilot key `candidate.artifacts.base_resume`; error prefix `unknown catalog key:`; flat `base_resume` must not resolve via helpers. Data-layer `artifact_type` leaf remains `base_resume`.

| Area | Source | Component tests |
| --- | --- | --- |
| Config rename + hierarchical pilot ([bug-repro]) | `config.py`, `artifact_catalog.py` | **`TestAst1575ArtifactConfigRename::test_artifact_config_symbol_and_hierarchical_pilot`** |
| Retargeted scaffold (lookup / fail-fast / flat reject / round-trip) | same | **`TestAst1573ArtifactCatalog`** (rewritten) |

**Broken / obsolete (this pass):** prior AST-1573 asserts on `ARTIFACT_CATALOG` / flat `base_resume` / `unknown artifact type` — rewritten in-place.

**Integration:** none.

## QA test manifest (AST-1575 — test-fix)

1. **[bug-repro] (required):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_artifact_catalog.py::TestAst1575ArtifactConfigRename::test_artifact_config_symbol_and_hierarchical_pilot \
  -q
```

Expect **red** on pre-fix tree (`ImportError: cannot import name 'ARTIFACT_CONFIG'`); **green** after make-fix.

2. **Retargeted scaffold (required with make-fix):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_artifact_catalog.py::TestAst1573ArtifactCatalog \
  -q
```

**Pass criterion (test-fix):** item 1 flips red→green; item 2 green — not zero-arg harness.

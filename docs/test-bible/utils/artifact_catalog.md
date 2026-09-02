# Artifact catalog (retired)

**Test module:** removed — `src/utils/artifact_catalog.py` deleted **AST-1576**.

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/utils/artifact_catalog.py` | **gone** | n/a |
| `src/utils/config.py` (`ARTIFACT_CONFIG` + `craft_resume_base.artifact_key`) | `tests/component/utils/test_config.py` | yes |

---

### AST-1573 / AST-1575 (historical)

Lookup helpers `get_catalog_entry` / `require_catalog_entry` / `is_candidate_scoped` lived on the deleted module. Hierarchical `ARTIFACT_CONFIG` + `candidate.artifacts.base_resume` remain config SoT — see **`docs/test-bible/utils/config.md`** § AST-1576 and **`docs/test-bible/core/candidate.md`** § AST-1576.

**Broken / obsolete:** `tests/component/utils/test_artifact_catalog.py` (`TestAst1573ArtifactCatalog`, `TestAst1575ArtifactConfigRename`) — ImportError after module delete; coverage retargeted.

**Integration:** none.

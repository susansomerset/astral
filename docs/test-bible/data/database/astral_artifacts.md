# Astral Artifacts

**Test module:** `tests/component/data/database/test_astral_artifacts.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/data/database.py` (`astral_artifacts` ensure + save/get/list) | `tests/component/data/database/test_astral_artifacts.py` | no (module-level lock on `database.py` unchanged) |

---

### AST-1352 · AST-1340

**Parent:** [AST-1340 — Create a table called astral_artifacts](https://linear.app/astralcareermatch/issue/AST-1340/create-a-table-called-astral-artifacts). **Publish:** `origin/sub/AST-1340/AST-1352-astral-artifacts-table-writers`.

New `astral_artifacts` table (lazy ensure + header inventory) and public `save_astral_artifact` / `get_current_astral_artifact` / `list_astral_artifacts` helpers with natural-key retire-and-insert (`current=1`). Does **not** wire Save Base Resume (**AST-1353**). Fixture flag `_astral_artifacts_schema_ensured` reset in data/core/ui confests.

| Area | Source | Component tests |
| --- | --- | --- |
| Ensure table + inventory + columns/index | `src/data/database.py` | **`TestAst1352AstralArtifacts::test_ensure_creates_table_and_inventory_lists_it`** |
| Save/get dict payload | `src/data/database.py` | **`TestAst1352AstralArtifacts::test_save_get_round_trip_dict_payload`** |
| Second save retires prior; list history / current_only | `src/data/database.py` | **`TestAst1352AstralArtifacts::test_second_save_retires_prior_and_keeps_history`** |
| Identical payload still new UUID | `src/data/database.py` | **`TestAst1352AstralArtifacts::test_identical_payload_still_inserts_new_uuid`** |
| Empty get/list | `src/data/database.py` | **`TestAst1352AstralArtifacts::test_get_current_none_when_empty`** |
| String payload / JSON-text parse | `src/data/database.py` | **`TestAst1352AstralArtifacts::test_string_payload_stored_as_is_non_json_round_trips`** |
| Identity + None validation | `src/data/database.py` | **`TestAst1352AstralArtifacts::test_identity_and_payload_validation`** |

**Broken / obsolete:** none — new helpers; no existing component tests call these symbols.

**Integration:** no existing `tests/integration/` scenario exercises `astral_artifacts` writers — no revision (artifact pipeline remains a should-have gap; Save wiring is **AST-1353**).

## QA test manifest

1. New table + writers: `tests/component/data/database/test_astral_artifacts.py::TestAst1352AstralArtifacts`

**AST-1352** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_astral_artifacts.py \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

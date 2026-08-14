# Artifacts

**Test module:** `tests/component/data/database/test_artifacts.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/data/database.py` (`artifacts` ensure + save/get/list) | `tests/component/data/database/test_artifacts.py` | no (module-level lock on `database.py` unchanged) |

---

### AST-1352 · AST-1340

**Parent:** [AST-1340 — Create a table called astral_artifacts](https://linear.app/astralcareermatch/issue/AST-1340/create-a-table-called-astral-artifacts). **Publish:** `origin/sub/AST-1340/AST-1352-astral-artifacts-table-writers` (table originally shipped as `astral_artifacts`; **AST-1364** renames to `artifacts`).

Versioned entity-scoped artifact blobs with public `save_artifact` / `get_current_artifact` / `list_artifacts` (natural-key retire-and-insert, `current=1`). Does **not** wire Save Base Resume (**AST-1353**). Fixture flag `_artifacts_schema_ensured` reset in data/core/ui confests.

| Area | Source | Component tests |
| --- | --- | --- |
| Ensure table + inventory + columns/index | `src/data/database.py` | **`TestAst1352Artifacts::test_ensure_creates_table_and_inventory_lists_it`** |
| Save/get dict payload | `src/data/database.py` | **`TestAst1352Artifacts::test_save_get_round_trip_dict_payload`** |
| Second save retires prior; list history / current_only | `src/data/database.py` | **`TestAst1352Artifacts::test_second_save_retires_prior_and_keeps_history`** |
| Identical payload still new UUID | `src/data/database.py` | **`TestAst1352Artifacts::test_identical_payload_still_inserts_new_uuid`** |
| Empty get/list | `src/data/database.py` | **`TestAst1352Artifacts::test_get_current_none_when_empty`** |
| String payload / JSON-text parse | `src/data/database.py` | **`TestAst1352Artifacts::test_string_payload_stored_as_is_non_json_round_trips`** |
| Identity + None validation | `src/data/database.py` | **`TestAst1352Artifacts::test_identity_and_payload_validation`** |

**Integration:** no existing `tests/integration/` scenario exercises `artifacts` writers — no revision (Save wiring is **AST-1353**).

---

### AST-1364 · AST-1340 (bug — rename)

**Publish:** `origin/sub/AST-1340/AST-1364-rename-astral-artifacts-to-artifacts`.

Rename table/API from `astral_artifacts` / `save_astral_artifact` / `astral_artifact_uuid` to unprefixed `artifacts` / `save_artifact` / `artifact_uuid` (plus ensure/index/schema flag + AST-1353 call sites). Pre-rename DBs migrate via `ALTER TABLE … RENAME` in `_ensure_artifacts_table`.

| Area | Source | Component tests |
| --- | --- | --- |
| Public API + inventory + table/PK names (no legacy astral_*) | `src/data/database.py` | **`TestAst1364RenameArtifacts::test_public_api_and_table_use_unprefixed_names`** ([bug-repro]) |
| Writer suite retargeted to renamed symbols | `src/data/database.py` | **`TestAst1352Artifacts`** (was `TestAst1352AstralArtifacts`) |

**Broken / obsolete this pass:** `tests/component/data/database/test_astral_artifacts.py` deleted (replaced by `test_artifacts.py`); confest flag `_astral_artifacts_schema_ensured` → `_artifacts_schema_ensured`; AST-1353 core/API cases retargeted (see `docs/test-bible/core/candidate.md` / `ui/api/api_candidate.md`).

**Integration:** none.

## QA test manifest (AST-1364)

1. **[bug-repro]** Rename surface: `tests/component/data/database/test_artifacts.py::TestAst1364RenameArtifacts`
2. Retargeted writers: `tests/component/data/database/test_artifacts.py::TestAst1352Artifacts`
3. Retargeted Save wire: `TestAst1353SnapshotSavedBaseResume` + `TestAst1353SaveBaseResumeSnapshotApi`

**AST-1364** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_artifacts.py \
  tests/component/core/test_candidate.py::TestAst1353SnapshotSavedBaseResume \
  tests/component/ui/api/test_api_candidate.py::TestAst1353SaveBaseResumeSnapshotApi \
  -q
```

**Pass criterion (test-fix):** [bug-repro] flips red→green after make-fix; remaining lines green — not zero-arg harness / branch-lock gate.

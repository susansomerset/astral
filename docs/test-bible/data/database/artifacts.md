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

---

### AST-1584 · AST-1571

**Parent:** [AST-1571 — Implement patt.artifact.read-operative](https://linear.app/astralcareermatch/issue/AST-1571/implement-pattartifactread-operative). **Publish:** `origin/sub/AST-1571/AST-1584-get-by-uuid-candidate-read-operative-traceability`.

`database.get_artifact(artifact_uuid)` PK fetch (full row dict via `_artifact_row_dict`, including retired `current=0` rows); blank uuid → `ValueError`. No coat-check / blob. Core pin→body: **`docs/test-bible/core/candidate.md`** § AST-1584. Traceability draft is docs-acceptance only (canon path on publish tip).

| Area | Source | Component tests |
| --- | --- | --- |
| PK hit / retired pin / miss+blank | `src/data/database.py` | **`TestAst1584GetArtifact`** |

**Broken / obsolete this pass:** none — additive PK reader; existing `TestAst1352Artifacts` / `TestAst1364RenameArtifacts` stay.

**Integration:** none — no existing `tests/integration/` scenario asserts by-uuid operative read.

## QA test manifest (AST-1584)

1. Data PK fetch: `tests/component/data/database/test_artifacts.py::TestAst1584GetArtifact`
2. Candidate pin→body: `tests/component/core/test_candidate.py::TestAst1584GetOperativeBaseResume`
3. **docs-acceptance** — draft `canon/directives/draft/patt.artifacts.traceability.md` on publish tip (id + versioned agent_id / agent_task_id / seed artifact id array / manual-edit inheritance; no product persist)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_artifacts.py::TestAst1584GetArtifact \
  tests/component/core/test_candidate.py::TestAst1584GetOperativeBaseResume \
  -q
```

```bash
# docs-acceptance (publish tip)
test -f canon/directives/draft/patt.artifacts.traceability.md
rg -n 'id: patt.artifacts.traceability|versioned `agent_id`|versioned `agent_task_id`|seed `artifact_id\[\]`|manual' \
  canon/directives/draft/patt.artifacts.traceability.md
```

**Pass criterion:** pytest green on lines 1–2 + docs-acceptance line 3 — not zero-arg harness / branch-lock gate.


---

### AST-1591 · AST-1588

**Parent:** [AST-1588 — Support job.artifacts.job_resume and job.artifacts.cover_letter as artifacts](https://linear.app/astralcareermatch/issue/AST-1588/support-jobartifactsjob-resume-and-jobartifactscover-letteras). **Publish:** `origin/sub/AST-1588/AST-1591-artifacts-table-source-references`.

Data-layer `artifacts.source_artifact_ids` (TEXT JSON array of artifact_uuid strings, default `[]`): DDL/ensure + ALTER migrate; `save_artifact(..., source_artifact_ids=None)` persists; `get_current_artifact` / `get_artifact` / `list_artifacts` return `list[str]`. No UUID-existence or catalog validation. Catalog keys / tracker citation are siblings **AST-1590** / **AST-1592**. Draft alignment note on `canon/directives/draft/patt.artifacts.traceability.md` is docs-acceptance.

| Area | Source | Component tests |
| --- | --- | --- |
| Fresh CREATE + inventory lists column | `src/data/database.py` | **`TestAst1352Artifacts::test_ensure_creates_table_and_inventory_lists_it`** (revised) |
| ALTER-add on pre-AST-1591 table | `src/data/database.py` | **`TestAst1591SourceArtifactIds::test_ensure_adds_column_on_preexisting_table`** |
| Omit sources → `[]` on get-current / get-by-uuid | `src/data/database.py` | **`TestAst1591SourceArtifactIds::test_save_omitted_sources_default_empty_list`** |
| Persist + strip empties; readers + list | `src/data/database.py` | **`TestAst1591SourceArtifactIds::test_save_persist_and_readers_return_sources`** |
| Per-version sources across retire+insert | `src/data/database.py` | **`TestAst1591SourceArtifactIds::test_second_save_can_change_sources_independently`** |
| Bad type → ValueError | `src/data/database.py` | **`TestAst1591SourceArtifactIds::test_source_artifact_ids_bad_type_raises`** |

**Broken / obsolete this pass:** `TestAst1352Artifacts::test_ensure_creates_table_and_inventory_lists_it` — exact column set + inventory must include `source_artifact_ids` (revised in place). Existing writer / rename / get-by-uuid suites stay.

**Integration:** none — no existing `tests/integration/` scenario asserts `source_artifact_ids` or artifacts provenance columns.

## QA test manifest (AST-1591)

1. Revised ensure/inventory: `tests/component/data/database/test_artifacts.py::TestAst1352Artifacts::test_ensure_creates_table_and_inventory_lists_it`
2. Source refs suite: `tests/component/data/database/test_artifacts.py::TestAst1591SourceArtifactIds`
3. Regression writers: `tests/component/data/database/test_artifacts.py::TestAst1352Artifacts`
4. Regression rename: `tests/component/data/database/test_artifacts.py::TestAst1364RenameArtifacts`
5. Regression get-by-uuid: `tests/component/data/database/test_artifacts.py::TestAst1584GetArtifact`
6. **docs-acceptance** — draft `canon/directives/draft/patt.artifacts.traceability.md` on publish tip names AST-1588 `source_artifact_ids` alignment

```bash
./scripts/testing/run_component_tests.sh   tests/component/data/database/test_artifacts.py   -q
```

```bash
# docs-acceptance (publish tip)
rg -n 'AST-1588|source_artifact_ids'   canon/directives/draft/patt.artifacts.traceability.md
```

**Pass criterion:** pytest green on lines 1–5 + docs-acceptance line 6 — not zero-arg harness / branch-lock gate.

**Bible path shasum (record after publish):** `docs/test-bible/data/database/artifacts.md`

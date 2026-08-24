# Api Candidate

**Test module:** `tests/component/ui/api/test_api_candidate.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_candidate.py` | `tests/component/ui/api/test_api_candidate.py` | yes |

### AST-723 · AST-378

PUT **`/api/candidates/:id/data`** calls **`apply_rubric_vectors_save`** after rubric normalization; GET detail calls **`hydrate_rubric_artifacts_for_response`** for Artifacts overlay (mirrors **AST-526** company_search_terms pattern).

| Area | Source | Component tests |
| --- | --- | --- |
| PUT sync + GET hydrate | `src/ui/api/api_candidate.py` | `TestAst723RubricVectorsApi` |

### AST-802 · AST-801

PUT **`/api/candidates/:id/data`** with **`artifacts.company_search_terms`** syncs table via **`apply_company_search_terms_save`**; blob key is not persisted (**AST-524** path unchanged; **AST-802** reconcile is eligibility-side — see **`data/database/dispatch_tasks.md`**).

| Area | Source | Component tests |
| --- | --- | --- |
| PUT table sync, no blob persist | `src/ui/api/api_candidate.py` | **`TestCandidateRoutes::test_put_company_search_terms_populates_table_without_persisting_blob`** |

### AST-901 · AST-900

**`GET /api/candidates/:id/generate/<task_key>/pending`** recovers completed craft rubric generate; PUT **`artifacts.<rubric_key>`** clears **`pending_craft_generations`** for the matching craft task. Primary manifest: **`docs/test-bible/core/candidate.md`** § AST-901.

| Area | Source | Component tests |
| --- | --- | --- |
| Pending GET + clear on Save | `src/ui/api/api_candidate.py` | **`TestAst901PendingCraftGenerationApi`** |

### AST-904 · AST-900 (UAT fix)

PUT Save: clear pending **after** successful persist (keys captured before `apply_rubric_vectors_save` deletes them); on Save failure **re-stash** submitted criteria for page-return recovery. UI toast: **`docs/test-bible/frontend/components.md`** § AST-904.

| Area | Source | Component tests |
| --- | --- | --- |
| Clear after success (apply dels keys) | `src/ui/api/api_candidate.py` | **`TestAst901PendingCraftGenerationApi::test_put_artifact_clears_matching_pending`** (revised) |
| Re-stash on Save failure | `src/ui/api/api_candidate.py` | **`TestAst904SavePendingRecovery::test_put_save_failure_restashes_pending`** |

**AST-904** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_candidate.py::TestAst901PendingCraftGenerationApi::test_put_artifact_clears_matching_pending \
  tests/component/ui/api/test_api_candidate.py::TestAst904SavePendingRecovery \
  -q
```

### AST-906 · AST-900 (UAT fix)

PUT **`artifacts.get_rubric`** with craft-shaped literal `\n` criteria coerces via **`rubric_text`** and returns **200**; empty / single-grade content still **400**. Primary: **`docs/test-bible/utils/rubric_text.md`** § AST-906.

| Area | Source | Component tests |
| --- | --- | --- |
| Literal `\n` get_rubric Save | `src/ui/api/api_candidate.py` | **`TestAst906GetRubricLiteralNewlineSave`** |

### AST-970 · AST-871

Primary manifest: **`docs/test-bible/core/candidate.md`** § AST-970. Admin PUT state → **`transition_candidate_state`** (**`TestAst970AdminStateOverride`**).

### AST-1287 · AST-1285

**Publish:** `origin/sub/AST-1285/AST-1287-admin-confirm-override`.

Admin `confirm_state_override` + structured illegal-hop 400 + same-state skip. Primary: **`docs/test-bible/core/candidate.md`** § AST-1287 — **`TestAst1287AdminConfirmOverride`** (+ revised **`TestAst970AdminStateOverride`**).

### AST-1253 · AST-1243

**Publish:** `origin/sub/AST-1243/AST-1253-generate-regenerate-handoff`.

`POST /api/candidates/<id>/generate_artifacts` → `start_requested_artifacts`; chain-key `POST …/generate/<craft_*>` returns core 409. Primary core: **`docs/test-bible/core/candidate.md`** § AST-1253.

| Area | Source | Component tests |
| --- | --- | --- |
| generate_artifacts + chain 409 | `src/ui/api/api_candidate.py` | **`TestAst1253GenerateArtifactsApi`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_candidate.py::TestAst1253GenerateArtifactsApi \
  -q
```

### AST-1014 · AST-952

PUT refuse legacy `profile`; signature under `contact`. Primary: **`docs/test-bible/core/candidate.md`** § AST-1014 — **`TestCandidateRoutes::test_update_rejects_legacy_profile_body`**.

---

### AST-1353 · AST-1340

**Publish:** `origin/sub/AST-1340/AST-1353-save-base-resume-snapshot`.

After successful **`save_candidate_data`** on PUT `/data` when the request included dict/list **`artifacts.base_resume`**, call **`snapshot_saved_base_resume_artifact`**. Primary core helper + craft non-wire: **`docs/test-bible/core/candidate.md`** § AST-1353.

| Area | Source | Component tests |
| --- | --- | --- |
| PUT Save snapshots + second Save history + AC4 craft overwrite | `src/ui/api/api_candidate.py` | **`TestAst1353SaveBaseResumeSnapshotApi`** |
| Mocked PUT base_resume still green (snapshot stubbed) | `src/ui/api/api_candidate.py` | revised **`TestAst519ResumeStructureApi::test_put_base_resume_strips_orphan_keys`**; revised **`TestAst1305LegacyLabelIngestApi`** |

**Broken / obsolete this pass:** mocked `save_candidate_data` PUT tests that include `base_resume` must stub **`snapshot_saved_base_resume_artifact`** (otherwise snapshot hits real DB / missing candidate).

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_candidate.py::TestAst1353SaveBaseResumeSnapshotApi \
  tests/component/ui/api/test_api_candidate.py::TestAst519ResumeStructureApi::test_put_base_resume_strips_orphan_keys \
  tests/component/ui/api/test_api_candidate.py::TestAst1305LegacyLabelIngestApi \
  -q
```

---

### AST-1364 · AST-1340 (bug — rename)

PUT Save stubs / real-DB AST-1353 cases call **`snapshot_saved_base_resume_artifact`** and read **`get_current_artifact`** / **`list_artifacts`** / **`artifact_uuid`**. Primary: **`docs/test-bible/data/database/artifacts.md`** § AST-1364.

| Area | Source | Component tests |
| --- | --- | --- |
| Save snapshot API (retargeted) | `src/ui/api/api_candidate.py` | **`TestAst1353SaveBaseResumeSnapshotApi`** |
| Mocked PUT base_resume snapshot stub | `src/ui/api/api_candidate.py` | **`TestAst519…`** / **`TestAst1305…`** stub renamed helper |

---

### AST-1474 · AST-1462

**Publish:** `origin/sub/AST-1462/AST-1474-page-break-policy-config-resume-structure-schema`.

GET `/resume_structure` catalog exposes page-break policy lists/labels/defaults; each `all_sections` row includes resolved `page_break_policy`; PUT persists via existing normalize. Primary normalize/config: **`docs/test-bible/core/candidate.md`** § AST-1474.

| Area | Source | Component tests |
| --- | --- | --- |
| Catalog + all_sections + PUT | `src/ui/api/api_candidate.py` | **`TestAst1474PageBreakPolicyCatalogApi`** |

**Broken / obsolete this pass:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_candidate.py::TestAst1474PageBreakPolicyCatalogApi \
  -q
```

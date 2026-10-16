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
| PUT Save snapshots + second Save history + AC4 craft overwrite | `src/ui/api/api_candidate.py` | **`TestAst1353SaveBaseResumeSnapshotApi`** (**rewritten AST-1576** as **`TestAst1576PutBaseResumeOperativeApi`**) |
| Mocked PUT base_resume still green (snapshot stubbed) | `src/ui/api/api_candidate.py` | revised **`TestAst519…`** / **`TestAst1305…`** — snapshot stub removed AST-1576 |

**Superseded by AST-1576:** PUT pops `base_resume` and calls generic `save_candidate_data(candidate_id, artifact_key, blob)`.

**Broken / obsolete this pass:** mocked `save_candidate_data` PUT tests that include `base_resume` must stub **`snapshot_saved_base_resume_artifact`** (otherwise snapshot hits real DB / missing candidate).

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_candidate.py::TestAst1576PutBaseResumeOperativeApi \
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

---

### AST-1576 · AST-1569

**Publish:** `origin/sub/AST-1569/AST-1576-generic-save-candidate-data`.

PUT `/data` pops `artifacts.base_resume` then `save_candidate_data(candidate_id, TASK_CONFIG["craft_resume_base"]["artifact_key"], blob)`. GET/PUT response hydrate overlays operative current. Primary: **`docs/test-bible/core/candidate.md`** § AST-1576.

| Area | Source | Component tests |
| --- | --- | --- |
| PUT operative write + retire + library blob isolation | `src/ui/api/api_candidate.py` | **`TestAst1576PutBaseResumeOperativeApi`** |
| Mocked PUT dual-call (library vs artifact_key) | same | revised **`TestAst519ResumeStructureApi::test_put_base_resume_strips_orphan_keys`**; **`TestAst1305LegacyLabelIngestApi`** |

**Broken / obsolete:** `TestAst1353SaveBaseResumeSnapshotApi`; snapshot stub on mocked PUT.

**Integration:** none.

---

### AST-1585 · AST-1571

**Publish:** `origin/sub/AST-1571/AST-1585-ui-contact-pilot-base-resume-operative-resolve`.

`GET /api/candidates/<id>/operative/base_resume?artifact_id=` → `resolve_pinned_base_resume` → `{"base_resume": body}` (400 missing id; 404 unknown candidate / miss / wrong owner). No blob / `get_current_artifact` on this path. Primary Contact helper: **`docs/test-bible/core/contact.md`** § AST-1585.

| Area | Source | Component tests |
| --- | --- | --- |
| Operative GET pin→body | `src/ui/api/api_candidate.py` | **`TestAst1585OperativeBaseResumeApi`** |

**Broken / obsolete:** none.

**Integration:** none.

---

### AST-1586 · AST-1570

**Publish:** `origin/sub/AST-1570/AST-1586-current-read-helper-get-hydrate-pattern-revise`.

`GET /<id>` and `GET /<id>/resume_structure` obtain `base_resume` only through `get_candidate` → `hydrate_operative_base_resume_for_response` (stale blob stripped on miss). Operative pin GET unchanged (**AST-1585**). Primary helper: **`docs/test-bible/core/candidate.md`** § AST-1586.

| Area | Source | Component tests |
| --- | --- | --- |
| GET detail / resume_structure read-current | `src/ui/api/api_candidate.py` | **`TestAst1586ReadCurrentGetApi`** |

**Broken / obsolete:** none.

**Integration:** none.

### AST-1633 · AST-1629

**Parent:** [AST-1629 — Migrate candidate_data.context.strengths to use the artifact table](https://linear.app/astralcareermatch/issue/AST-1629). **Publish:** `origin/sub/AST-1629/AST-1633-operative-save-hydrate-blob-retirement`.

PUT `/data` pops `context.strengths` then `save_candidate_data(candidate_id, "candidate.context.strengths", body)`; sibling context keys still library-merge; GET detail hydrates Strengths (miss leaves legacy blob). Primary core: **`docs/test-bible/core/candidate.md`** § AST-1633.

| Area | Source | Component tests |
| --- | --- | --- |
| PUT operative + retire + sibling merge + GET hydrate + empty 400 | `src/ui/api/api_candidate.py` | **`TestAst1633StrengthsOperativeApi`** |

**Broken / obsolete:** none.

**Integration:** none.

## QA test manifest

1. Core: `tests/component/core/test_candidate.py::TestAst1633StrengthsOperativeSaveHydrate`
2. API: `tests/component/ui/api/test_api_candidate.py::TestAst1633StrengthsOperativeApi`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1633StrengthsOperativeSaveHydrate \
  tests/component/ui/api/test_api_candidate.py::TestAst1633StrengthsOperativeApi \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/core/candidate.md` — *(filled after publish)*
- `docs/test-bible/ui/api/api_candidate.md` — *(filled after publish)*


### AST-1649 · AST-1647

**Parent:** [AST-1647 — Migrate candidate bio summary to use the artifact table and remove from candidate profile page](https://linear.app/astralcareermatch/issue/AST-1647). **Publish:** `origin/sub/AST-1647/AST-1649-operative-save-hydrate-blob-retirement`.

PUT `/data` pops `context.bio_summary` then `save_candidate_data(candidate_id, "candidate.context.bio_summary", body)`; sibling context keys still library-merge; GET detail hydrates Bio Summary (miss leaves legacy blob). Primary core: **`docs/test-bible/core/candidate.md`** § AST-1649.

| Area | Source | Component tests |
| --- | --- | --- |
| PUT operative + retire + sibling merge + GET hydrate + empty 400 | `src/ui/api/api_candidate.py` | **`TestAst1649BioSummaryOperativeApi`** |

**Broken / obsolete:** none.

**Integration:** none.

## QA test manifest

1. Core: `tests/component/core/test_candidate.py::TestAst1649BioSummaryOperativeSaveHydrate`
2. API: `tests/component/ui/api/test_api_candidate.py::TestAst1649BioSummaryOperativeApi`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1649BioSummaryOperativeSaveHydrate \
  tests/component/ui/api/test_api_candidate.py::TestAst1649BioSummaryOperativeApi \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/core/candidate.md` — *(filled after publish)*
- `docs/test-bible/ui/api/api_candidate.md` — *(filled after publish)*

### AST-1655 · AST-1642

**Parent:** [AST-1642 — Migrate candidate_data.context.deal_breakers to use the artifact table](https://linear.app/astralcareermatch/issue/AST-1642). **Publish:** `origin/sub/AST-1642/AST-1655-operative-save-hydrate-blob-retirement`.

Operative `plain_text` validate on str-path (reuse AST-1633); Deal Breakers `save_artifact` retire+insert + identical no-op (AST-1635 shared); dict-path strips `context.deal_breakers` (siblings keep library-merge); `hydrate_operative_deal_breakers_for_response` overlays current / leaves legacy blob on miss; `get_candidate` hydrates. Catalog/token: sibling **AST-1654**. API PUT/GET: **`docs/test-bible/ui/api/api_candidate.md`** § AST-1655. No React / backfill.

| Area | Source | Component tests |
| --- | --- | --- |
| plain_text validate + save/retire + identical no-op + dict strip + hydrate + get_candidate | `src/core/candidate.py` | **`TestAst1655DealBreakersOperativeSaveHydrate`** |

**Broken / obsolete this pass:** none for Strengths strip (priorities still library sibling on this tip). Parallel **AST-1649** Bio Summary suite `skipif` when `bio_summary` catalog key absent.

**Integration:** none — no existing scenario asserts Deal Breakers operative save/hydrate; do not invent.

## QA test manifest

1. Core Deal Breakers operative: `tests/component/core/test_candidate.py::TestAst1655DealBreakersOperativeSaveHydrate`
2. API PUT/GET Deal Breakers: `tests/component/ui/api/test_api_candidate.py::TestAst1655DealBreakersOperativeApi`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1655DealBreakersOperativeSaveHydrate \
  tests/component/ui/api/test_api_candidate.py::TestAst1655DealBreakersOperativeApi \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/core/candidate.md` — *(filled after publish)*
- `docs/test-bible/ui/api/api_candidate.md` — *(filled after publish)*

### AST-1652 · AST-1641

**Parent:** [AST-1641 — Migrate candidate_data.context.priorities to use the artifact table](https://linear.app/astralcareermatch/issue/AST-1641). **Publish:** `origin/sub/AST-1641/AST-1652-operative-save-hydrate-blob-retirement`.

PUT `/data` pops `context.priorities` (with strengths in one combined pop) then `save_candidate_data(candidate_id, "candidate.context.priorities", body)`; sibling context keys still library-merge; GET detail hydrates Priorities (miss leaves legacy blob). Primary core: **`docs/test-bible/core/candidate.md`** § AST-1652.

| Area | Source | Component tests |
| --- | --- | --- |
| PUT operative + retire + sibling merge + GET hydrate + empty 400 | `src/ui/api/api_candidate.py` | **`TestAst1652PrioritiesOperativeApi`** |

**Broken / obsolete:** AST-1633 / AST-1649 PUT sibling asserts that library-merged `priorities` — revised to `deal_breakers`.

**Integration:** none.

## QA test manifest

1. Core: `tests/component/core/test_candidate.py::TestAst1652PrioritiesOperativeSaveHydrate`
2. API: `tests/component/ui/api/test_api_candidate.py::TestAst1652PrioritiesOperativeApi`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1652PrioritiesOperativeSaveHydrate \
  tests/component/ui/api/test_api_candidate.py::TestAst1652PrioritiesOperativeApi \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/core/candidate.md` — *(filled after publish)*
- `docs/test-bible/ui/api/api_candidate.md` — *(filled after publish)*

### AST-1659 · AST-1643

**Parent:** [AST-1643 — Migrate candidate_data.context.ideal_day to use the artifact table](https://linear.app/astralcareermatch/issue/AST-1643). **Publish:** `origin/sub/AST-1643/AST-1659-operative-save-hydrate-blob-retirement`.

PUT `/data` pops `context.ideal_day` then `save_candidate_data(candidate_id, "candidate.context.ideal_day", body)`; sibling context keys still library-merge (`backstory` after merge(dev) priorities epic); GET detail hydrates Ideal Day (miss leaves legacy blob). Primary core: **`docs/test-bible/core/candidate.md`** § AST-1659.

| Area | Source | Component tests |
| --- | --- | --- |
| PUT operative + retire + sibling merge + GET hydrate + empty 400 | `src/ui/api/api_candidate.py` | **`TestAst1659IdealDayOperativeApi`** |

**Broken / obsolete:** AST-1633 / AST-1649 / AST-1655 / AST-1659 PUT sibling asserts that library-merged `priorities` after merge(dev) — revised to `backstory`.

**Integration:** none.

## QA test manifest

1. Core: `tests/component/core/test_candidate.py::TestAst1659IdealDayOperativeSaveHydrate`
2. API: `tests/component/ui/api/test_api_candidate.py::TestAst1659IdealDayOperativeApi`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1659IdealDayOperativeSaveHydrate \
  tests/component/ui/api/test_api_candidate.py::TestAst1659IdealDayOperativeApi \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/core/candidate.md` — *(filled after publish)*
- `docs/test-bible/ui/api/api_candidate.md` — *(filled after publish)*

### AST-1662 · AST-1644

**Parent:** [AST-1644 — Migrate candidate_data.context.backstory to use the artifact table](https://linear.app/astralcareermatch/issue/AST-1644). **Publish:** `origin/sub/AST-1644/AST-1662-operative-save-hydrate-blob-retirement`.

PUT `/data` pops `context.backstory` then `save_candidate_data(candidate_id, "candidate.context.backstory", body)`; sibling context keys still library-merge (`hopes`); GET detail hydrates Backstory (miss leaves legacy blob). Primary core: **`docs/test-bible/core/candidate.md`** § AST-1662.

| Area | Source | Component tests |
| --- | --- | --- |
| PUT operative + retire + sibling merge + GET hydrate + empty 400 | `src/ui/api/api_candidate.py` | **`TestAst1662BackstoryOperativeApi`** |

**Broken / obsolete:** AST-1633 / AST-1649 / AST-1655 / AST-1652 / AST-1659 PUT sibling asserts that library-merged `backstory` — revised to `hopes`.

**Integration:** none.

## QA test manifest

1. Core: `tests/component/core/test_candidate.py::TestAst1662BackstoryOperativeSaveHydrate`
2. API: `tests/component/ui/api/test_api_candidate.py::TestAst1662BackstoryOperativeApi`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1662BackstoryOperativeSaveHydrate \
  tests/component/ui/api/test_api_candidate.py::TestAst1662BackstoryOperativeApi \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/core/candidate.md` — *(filled after publish)*
- `docs/test-bible/ui/api/api_candidate.md` — *(filled after publish)*

### AST-1665 · AST-1645

**Parent:** [AST-1645 — Migrate candidate_data.context.writing_preferences to use the artifact table](https://linear.app/astralcareermatch/issue/AST-1645). **Publish:** `origin/sub/AST-1645/AST-1665-operative-save-hydrate-blob-retirement`.

PUT `/data` pops `context.writing_preferences` then `save_candidate_data(candidate_id, "candidate.context.writing_preferences", body)`; sibling context keys still library-merge (`backstory`); GET detail hydrates Writing Preferences (miss leaves legacy blob). Primary core: **`docs/test-bible/core/candidate.md`** § AST-1665.

| Area | Source | Component tests |
| --- | --- | --- |
| PUT operative + retire + sibling merge + GET hydrate + empty 400 | `src/ui/api/api_candidate.py` | **`TestAst1665WritingPreferencesOperativeApi`** |

**Broken / obsolete:** AST-1652 Priorities PUT sibling asserting `deal_breakers` library-merge — revised to `backstory`.

**Integration:** none.

## QA test manifest

1. Core: `tests/component/core/test_candidate.py::TestAst1665WritingPreferencesOperativeSaveHydrate`
2. API: `tests/component/ui/api/test_api_candidate.py::TestAst1665WritingPreferencesOperativeApi`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1665WritingPreferencesOperativeSaveHydrate \
  tests/component/ui/api/test_api_candidate.py::TestAst1665WritingPreferencesOperativeApi \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/core/candidate.md` — *(filled after publish)*
- `docs/test-bible/ui/api/api_candidate.md` — *(filled after publish)*

### AST-1679 · AST-1677

**Parent:** [AST-1677](https://linear.app/astralcareermatch/issue/AST-1677). **Publish:** `origin/sub/AST-1677/AST-1679-operative-save-hydrate-blob-retirement`.

PUT `/data` pops `artifacts.resume_structure` after normalize/ingest then `save_candidate_data(..., "candidate.artifacts.resume_structure", body)`; GET detail hydrates via `get_candidate` (miss leaves legacy blob). Leaf-only `base_resume` PUT must still operative-save pilot body **and** ingested structure (AC6). Primary core: **`docs/test-bible/core/candidate.md`** § AST-1679.

| Area | Source | Component tests |
| --- | --- | --- |
| PUT operative + retire + GET hydrate + leaf-only base_resume gate | `src/ui/api/api_candidate.py` | **`TestAst1679ResumeStructureOperativeApi`** |
| Revised PUT structure asserts (operative, not library) | same | revised **`TestAst519ResumeStructureApi`**, **`TestAst1305LegacyLabelIngestApi`** |

**Broken / obsolete:** AST-519 / AST-1305 asserts that expected `resume_structure` in the library blob or assumed pilot was `operative[0]` — retargeted to catalog key / pilot hit filter.

**Integration:** none.

## QA test manifest

See **`docs/test-bible/core/candidate.md`** § AST-1679 (shared numbered list).

**Bible shasum (publish tip):**
- `docs/test-bible/ui/api/api_candidate.md` — *(filled after publish)*

### AST-1768 · AST-1687 (bug)

`GET /api/candidates/by_email?email=` (`@require_auth`, registered before `/<candidate_id>`) → `{"candidate_id": <id|null>}` via `get_candidate_id_for_query`; missing / no-`@` email → 400. Tests: **`test_api_candidate.py::TestAst1768CandidateByEmailApi`**. Full manifest: [`../../frontend/lib.md`](../../frontend/lib.md) § AST-1768.

### AST-1880 · AST-1851 (per-server platform keys)

`_sanitize_candidate` pops `candidate_api_keys` + `candidate_api_key` and adds `api_keys: {server_id: {label, set}}` for every catalog server (list rows load the map via `get_candidate`); `has_api_key` is gone. `PUT …/data` `api_keys: {sid: key|""}` sets (stripped) / clears per server; non-dict, unknown server or non-string key → 400 before any write; non-admin → 403. Tests: **`test_api_candidate.py::TestSanitizeCandidate`** (3 new), **`TestCandidateRoutes`** (`test_list_rows_carry_per_server_key_flags_only`, `test_get_returns_sanitized_candidate`, `test_update_sets_and_clears_api_keys_per_server`, `test_update_rejects_malformed_api_keys` ×5, `test_non_admin_cannot_create_delete_or_override_state`, AC 4 end-to-end `test_put_two_server_keys_stores_ciphertext_and_get_shows_flags_only` — two `candidate_key` ciphertext rows, GET flags only, clear one). Retired `test_strips_api_key_and_sets_flag`; `test_update_merges_data_state_and_api_key` → `test_update_merges_data_and_state` (key half moved; still red pre-existing on the `joblist_rubric` 400). Full manifest: [`api_admin.md`](api_admin.md) § AST-1880.

### AST-1901 · AST-1851 (bug: api_keys array)

> Supersedes the AST-1880 `api_keys` shapes above (`_api_keys_flags` helper removed).

`_sanitize_candidate` sets `api_keys: [{server, label}]`, one entry per stored key in array order (label from `LLM_SERVER_CONFIG`, or the id itself when the id isn't in the catalog). It never looks candidates up per row, because list rows arrive hydrated. `PUT …/data` takes `api_keys: [{server, key}]` and makes one `update_candidate_api_keys` call with the stripped edits (`""` = remove). A non-array body gets 400 "api_keys must be an array of {server, key}"; a bad entry gets "Invalid api_keys entry for server …"; a duplicate server gets "Duplicate api_keys entry for server …". Error bodies never echo a key. Tests: **`TestSanitizeCandidate`** (3, rewritten) and **`TestCandidateRoutes`**:
- `test_list_rows_carry_stored_key_servers_only`
- `test_get_returns_sanitized_candidate`
- `test_update_sends_api_keys_array_edits`
- `test_update_rejects_malformed_api_keys` ×7, with exact error text
- `test_update_rejects_duplicate_server_without_echoing_keys`
- the end-to-end `test_put_two_server_keys_stores_ciphertext_array_and_get_lists_servers_only`: two ciphertext entries in `candidate.api_keys`, then GET, then remove one
- the non-admin 403, now with an array body

Full manifest: [`../../data/database/candidates.md`](../../data/database/candidates.md) § QA test manifest (AST-1901).

**AST-2048 (pointer):** `test_update_rejects_unselectable_theme` — `PUT /api/candidates/<id>/data` with an unknown or examples-only theme → 400 via the real core allowlist, no DB write. Manifest: [`../../frontend/pages.md`](../../frontend/pages.md) § AST-2048.

### AST-2067 · AST-2043 (version list / set-current routes)

**Publish:** `origin/sub/AST-2043/AST-2067-version-api`. Four authenticated routes: `GET|PUT /api/candidates/<cid>/artifacts/<catalog_key>/{versions,current}` and `GET|PUT /api/candidates/<cid>/rubric/<rubric_key>/<code>/{versions,current}`. Version map = AST-2066's uuid-keyed map. The JSON keys come back **alphabetical** (Flask `sort_keys`), so tests order versions by `position`, never by key order.

| Area | Source | Component tests |
| --- | --- | --- |
| 200 list + PUT (completion info line), real SQLite | `src/ui/api/api_candidate.py` | **`TestAst2067CandidateVersionRoutes::test_artifact_list_and_set_current_200`**, **`…::test_rubric_list_and_set_current_200`** |
| AC7 cross-key guard (other key / other candidate / other code → 400, current unchanged) | same | **`…::test_artifact_cross_key_uuid_400_current_unchanged`**, **`…::test_rubric_cross_code_uuid_400_current_unchanged`** |
| 404 missing candidate; PUT body 400; bad key 400; unexpected error → one ERROR log + 500 payload | same | **`…::test_missing_candidate_404`** (4), **`…::test_put_bad_body_400`** (10), **`…::test_bad_key_400`** (4), **`…::test_unexpected_error_logged_once_500`** (4) |

New route lines are fully branch-covered for `LOCKED_AT_100`. **Fixture fix:** `tests/component/ui/conftest.py` `_DB_SCHEMA_FLAGS` gains `_rubric_vector_schema_ensured`; without it, the second real-SQLite rubric test in a run hits `no such table: rubric_vector`.

**Broken / obsolete:** none. `tests/component/ui` shows the same 22 failures with and without AST-2067's two route files (they predate this ticket). No integration scenario hits these paths.

**Manifest (test-child) — narrowed:**

1. Candidate + rubric routes: `tests/component/ui/api/test_api_candidate.py::TestAst2067CandidateVersionRoutes`
2. Job routes: `tests/component/ui/api/test_api_jobs.py::TestAst2067JobVersionRoutes` ([`api_jobs.md`](api_jobs.md) § AST-2067)
3. Regression (AST-2066 core the routes call): [`../../core/candidate.md`](../../core/candidate.md) § AST-2066 manifest

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_candidate.py::TestAst2067CandidateVersionRoutes \
  tests/component/ui/api/test_api_jobs.py::TestAst2067JobVersionRoutes \
  tests/component/data/database/test_artifacts.py::TestAst2066SetCurrentArtifact \
  tests/component/data/database/test_rubric_vectors.py::TestAst2066RubricCriterionVersions \
  tests/component/core/test_candidate.py::TestAst2066CandidateVersions \
  tests/component/core/test_tracker.py::TestAst2066JobVersions \
  -q
```

**Pass criterion:** 69 passed (40 AST-2067 + 29 AST-2066). Narrowed run, not the zero-arg harness / branch-lock gate.

### AST-2081 · AST-2046 (candidate resume_structure GET → shared payload)

`get_candidate_resume_structure` now returns `resume_structure_editor_payload(resolved)` ([`../../core/candidate.md`](../../core/candidate.md) § AST-2081), and the ten `RESUME_STRUCTURE_*` imports are gone from the route module. The response is a superset of the old one: `catalog` gains `body_format_details` and `hidden_flow_label`.

**New:** **`TestAst1306ResumeStructureAuthorApi::test_get_delegates_to_shared_editor_payload`** (the route body equals the helper's output). The existing AST-1306 GET/PUT tests stay green without edits. Manifest: [`../../core/tracker.md`](../../core/tracker.md) § AST-2081.

### AST-2127 · AST-2112 (AST-2067 fixture codes — AST-2126)

`TestAst2067CandidateVersionRoutes::_seed_rubric` seeded `V01`/`V02` through `sync_rubric_vectors_from_criteria`, which now rejects codes that aren't `[A-Z]{2}`. Renamed to `VA`/`VB` across the class (`_RUB` route path `/rubric/do_rubric/VA`, `code=` history filter, current-map assertions, 404 / bad-key route params). Unblocks **`…::test_rubric_list_and_set_current_200`** and **`…::test_rubric_cross_code_uuid_400_current_unchanged`**; § AST-2067 manifest and pass count unchanged. Primary manifest: [`../../core/consult.md`](../../core/consult.md) § AST-2127.

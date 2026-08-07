# Candidate

**Test module:** `tests/component/core/test_candidate.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/candidate.py` | `tests/component/core/test_candidate.py` | yes |

---

### AST-517 · AST-518 · AST-519 · AST-477

**`artifacts.resume_structure`** holds the candidate-owned section catalog (id, title, enabled, order, **`job_agent_editable`**); **`artifacts.base_resume`** holds string content keyed by enabled section ids. **`craft_resume_base`** response schema requires **`resume_structure`**; **`parse_candidate_resume`** persists both blobs. Legacy global **`base_resume_structure`** and **`base_resume.accent_color`** are read shims only. **AST-518** drives **`builder.py`** body emission and **`tracker.py`** job **`resume_content`** filtering to catalog subset + contact snapshot; cover letter stored as **`Subject`** / **`Letter`** with legacy **`re_line`** / **`body`** read shims. **AST-519** exposes **`GET …/resume_structure`**, filters **`base_resume`** keys on PUT, and drives **Base Resume Content** tabs + accent from per-candidate structure (not global shapes).

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-517** | Config defaults + normalize/resolve/split helpers; parse persistence; candidate isolation | `src/utils/config.py`, `src/core/candidate.py` | `tests/component/utils/test_config.py::TestAst517ResumeStructureConfig`; `tests/component/utils/test_config.py::TestStringifyResponseSchema::test_builds_schema_example_envelope`; `tests/component/core/test_candidate.py::TestAst517ResumeStructure`; `tests/component/core/test_candidate.py::TestParseCandidateResume`; `tests/component/core/test_candidate.py::TestParseCandidateResumeExtended` |
| **AST-518** | Structure-ordered builder HTML; accent from structure; job **`resume_content`** orphan strip + contact snapshot; cover letter **`Subject`**/**`Letter`** | `src/core/builder.py`, `src/core/candidate.py`, `src/core/tracker.py`, `src/utils/config.py` | `tests/component/core/test_candidate.py::TestAst518ResumeStructureProjection`; `tests/component/core/test_builder.py::TestAst518BuilderResumeStructure`; `tests/component/core/test_tracker.py::TestAst518JobResumeArtifacts`; `tests/component/core/test_builder.py::TestBuilderHelpers`; `tests/component/core/test_tracker.py::{TestAst302JobArtifacts,TestAst309CoverLetterArtifact,TestPersistJobArtifactFromParsed}` |
| **AST-519** | **`enabled_resume_structure_sections`** / **`filter_base_resume_to_structure`**; **`GET /api/candidates/<id>/resume_structure`**; PUT orphan strip + structure accent merge; Base Resume Content page + **`useCandidateResumeStructure`** | `src/core/candidate.py`, `src/ui/api/api_candidate.py`, `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx`, `src/ui/frontend/src/components/ArtifactEditor.tsx` | `tests/component/core/test_candidate.py::TestAst519ResumeStructureUiHelpers`; `tests/component/ui/api/test_api_candidate.py::TestAst519ResumeStructureApi`; `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx` (**§6c** routed page); `tests/component/frontend/components/test_ArtifactEditor.test.tsx` (structureSections mode) |

**AST-517** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst517ResumeStructureConfig \
  tests/component/utils/test_config.py::TestStringifyResponseSchema::test_builds_schema_example_envelope \
  tests/component/core/test_candidate.py::TestAst517ResumeStructure \
  tests/component/core/test_candidate.py::TestParseCandidateResume \
  tests/component/core/test_candidate.py::TestParseCandidateResumeExtended
```

**AST-518** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst518ResumeStructureProjection \
  tests/component/core/test_builder.py::TestAst518BuilderResumeStructure \
  tests/component/core/test_tracker.py::TestAst518JobResumeArtifacts \
  tests/component/core/test_builder.py::TestBuilderHelpers \
  tests/component/core/test_tracker.py::TestAst302JobArtifacts \
  tests/component/core/test_tracker.py::TestAst309CoverLetterArtifact \
  tests/component/core/test_tracker.py::TestPersistJobArtifactFromParsed
```

**AST-519** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst519ResumeStructureUiHelpers \
  tests/component/ui/api/test_api_candidate.py::TestAst519ResumeStructureApi
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  -t "structureSections|Base Resume Content|resume_structure"
```

---

### AST-594 · AST-592

Retire **AST-450** graded-consult contract on **`draft_job_resume`**: metadata-only **`TASK_CONFIG`** with **`resume_section_payload: True`**; runtime catalog whitelist via **`normalize_draft_job_resume_agent_payload`** / **`validate_draft_job_resume_payload`** (**AST-536**-style flatten); hop failures surface **`Validation failed:`** RESPONSE bodies + ERROR logs (**AST-531** ledger unchanged).

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-594** | Structure-keyed section JSON; reject `grades` / unknown keys; validation message on hop row | `src/utils/config.py`, `src/core/candidate.py`, `src/core/agent.py` | `tests/component/utils/test_config.py::TestAst594DraftJobResumeSchema`; `tests/component/core/test_candidate.py::TestAst594DraftJobResumePayload`; `tests/component/core/test_agent.py` — `-k "draft_job_resume"` (acceptance, unknown key, disallowed `grades`, RESPONSE **`Validation failed:`** prefix) |
| **AST-604** | Section key aliases (`candidate_contact` → `candidate_contact_detail`) before catalog whitelist | `src/core/candidate.py` | `tests/component/core/test_candidate.py::TestAst594DraftJobResumePayload::test_normalize_renames_candidate_contact_alias` |
| **AST-607** | `{$BASE_RESUME}` token emits section-id-keyed JSON (not markdown `###` sections); legacy label/content arrays map via structure title | `src/core/candidate.py` (`format_base_resume_for_token`), `src/utils/config.py` (`resume_sections_json` serialize) | `tests/component/core/test_candidate.py::TestAst607BaseResumeToken`; `tests/component/utils/test_config.py::TestResolveTokens::test_base_resume_token_emits_section_json_not_markdown` |

**AST-594** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst594DraftJobResumeSchema \
  tests/component/core/test_candidate.py::TestAst594DraftJobResumePayload \
  tests/component/core/test_agent.py -k "draft_job_resume"
```

---

### AST-644 · AST-601

**AST-644 (UAT bug):** Model returns **`craft_resume_base`** success envelope with content fields only — no **`resume_structure`** key — so **`_validate_response_schema`** hard-failed before **`split_craft_resume_base_payload`** could apply **`default_resume_structure()`** (AST-517). Fix: **`normalize_craft_resume_base_agent_payload`** injects config default when structure is missing or has empty **`sections`**, mirroring split path. No UI / schema / AST-517 storage changes.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-644** | Pre-validation default **`resume_structure`** injection | `src/core/candidate.py` | **`tests/component/core/test_candidate.py::TestAst517ResumeStructure`** — **`test_normalize_injects_default_when_resume_structure_missing`**, **`test_normalize_injects_default_when_resume_structure_sections_empty`**, **`test_normalize_preserves_valid_custom_resume_structure`**; reuse **`test_split_uses_default_when_structure_missing`** (split path unchanged) |

**AST-644** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst517ResumeStructure
```

---

### AST-650 · AST-601

**AST-650 (UAT bug):** UI **Generate** POST for **`craft_resume_base`** returned HTTP 200 with **`parsed_response`** but never wrote **`artifacts.resume_structure`** / **`artifacts.base_resume`** — persistence existed only on **`parse_candidate_resume`**. Fix: after successful **`do_task`** in **`run_candidate_artifact_generation`**, **`split_craft_resume_base_payload`** + **`save_candidate(..., merge=True)`** for **`craft_resume_base`** only (mirrors parse path). No UI / schema / prompt changes.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-650** | UI Generate success persists structure + base_resume | `src/core/candidate.py` **`run_candidate_artifact_generation`** | **`tests/component/core/test_candidate.py::TestRunCandidateArtifactGeneration`** — **`test_persists_artifacts_on_craft_resume_base_success`**, **`test_does_not_persist_artifacts_on_other_task_success`**; revised **`test_returns_200_on_success`** (mock **`save_candidate`**) |

**AST-650** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestRunCandidateArtifactGeneration
```

### AST-901 · AST-900

**AST-901:** Harden craft rubric UI generate delivery — empty **`criteria`** → HTTP 500 + ledger **`FAILED`**; successful **`craft_*_rubric`** stashes **`candidate_data.pending_craft_generations[task_key]`** (not artifact Save); **`get_pending_craft_generation`** recovers from stash or ledger+`agent_data`. API: **`GET …/generate/<task_key>/pending`**; clear pending when matching rubric artifact is Saved. Config: **`CRAFT_RUBRIC_UI_TASK_KEYS`**. UI page-return wiring is sibling **AST-902**.

| Area | Source | Component tests |
| --- | --- | --- |
| Stash + empty-criteria + recovery helpers | `src/core/candidate.py` | **`TestAst901CraftRubricGenerateDelivery`** |
| Pending GET + clear on Save | `src/ui/api/api_candidate.py` | **`TestAst901PendingCraftGenerationApi`** (`test_api_candidate.py`) |
| UI task-key frozenset | `src/utils/config.py` | **`TestAst901CraftRubricUiTaskKeys`** (`test_config.py`) |
| Resume-base auto-persist unchanged | `src/core/candidate.py` | **`TestRunCandidateArtifactGeneration`** (existing) |

**AST-901** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst901CraftRubricGenerateDelivery \
  tests/component/core/test_candidate.py::TestRunCandidateArtifactGeneration \
  tests/component/ui/api/test_api_candidate.py::TestAst901PendingCraftGenerationApi \
  tests/component/utils/test_config.py::TestAst901CraftRubricUiTaskKeys
```

### AST-905 · AST-900 (UAT fix)

**AST-905:** `get_pending_craft_generation` returns **404** `No recoverable generation` when `rubric_criteria_for_task` already has one or more criteria for the craft task's owner — do not recover over a populated stored rubric. Empty stored list still recovers (stash/ledger). UI belt: **`docs/test-bible/frontend/components.md`** § AST-905.

| Area | Source | Component tests |
| --- | --- | --- |
| Pending 404 when stored non-empty | `src/core/candidate.py` | **`TestAst905RecoverOnlyWhenEmpty`** |

**AST-905** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst905RecoverOnlyWhenEmpty \
  -q
```

### AST-723 · AST-378

Rubric authority cutover: **`apply_rubric_vectors_save`**, **`hydrate_rubric_artifacts_for_response`**, **`rubric_criteria_for_task`** (table-backed; embedded RC merge for **`prefilter_company`**); preview injects **`_astral_candidate_id`** for **`{$RUBRIC_VECTORS}`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Save sync + GET overlay helpers | `src/core/candidate.py` | `TestAst723RubricVectorsCutover` |
| API PUT/GET wiring | `src/ui/api/api_candidate.py` | `TestAst723RubricVectorsApi` (`test_api_candidate.py`) |


### AST-970 · AST-871

Config-backed candidate state registry (`prior_states`, companions, `progress_rank`); enforced `transition_candidate_state`; DELETED reap timer on `candidate_data.lifecycle`; `age_stale_candidate_states` helper (no scheduler — AST-972). Retired four-step names (`NEW` / `PROFILE_READY` / `CONTEXT_READY` / `LIVE_PROMPTS`). Parse / `check_context_complete` no longer write state.

| Area | Source | Component tests |
| --- | --- | --- |
| Registry + nav/inflow string gates | `src/utils/config.py` | **`TestAst970CandidateStateRegistry`** (`test_config.py`); revised **`TestAst505InflowDiscoveryConfig`** trigger → **`ACTIVE_SEARCH`** |
| Transitions, reap, stale aging | `src/core/candidate.py` | **`TestAst970CandidateStateMachine`**; revised initiate / transition / delete / context-complete / parse classes |
| Admin state override fail-closed | `src/ui/api/api_candidate.py` | **`TestAst970AdminStateOverride`**; revised **`TestCandidateRoutes`** state path |
| `progress_rank` nav gates | `src/ui/api/api_system.py` | revised **`TestSystemNavHelpers`** |
| Candidate dispatch state_options vocab | `src/ui/api/api_admin.py` | revised **`TestAst804CandidateDispatchAdminValidation`** (`ACTIVE_SEARCH` / `intake_initiate_candidate`) |
| Frontend fixture / SA options | fixtures + Scheduled Actions | `stateUiManifestFixture.ts`; AST-804 describe in **`test_AdminScheduledActions.test.tsx`** |

**AST-970** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst970CandidateStateRegistry \
  tests/component/core/test_candidate.py::TestAst970CandidateStateMachine \
  tests/component/core/test_candidate.py::TestInitiateCandidate \
  tests/component/core/test_candidate.py::TestTransitionCandidateState \
  tests/component/core/test_candidate.py::TestTransitionCandidateStateSuccess \
  tests/component/core/test_candidate.py::TestDeleteCandidate \
  tests/component/core/test_candidate.py::TestCheckContextComplete \
  tests/component/core/test_candidate.py::TestCheckContextCompleteExtended \
  tests/component/core/test_candidate.py::TestParseCandidateResume \
  tests/component/core/test_candidate.py::TestParseCandidateResumeExtended \
  tests/component/ui/api/test_api_candidate.py::TestAst970AdminStateOverride \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_update_merges_data_state_and_api_key \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_list_candidates_and_states \
  tests/component/ui/api/test_api_system.py::TestSystemNavHelpers \
  tests/component/ui/api/test_api_admin.py::TestAst804CandidateDispatchAdminValidation \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_inflow_config_discovery_literals \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_inflow_discovery_dispatch_admin_defaults \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-804"
```

**Note:** **AST-972** revised dispatcher + `test_dispatch_tasks` inflow fixtures to **`ACTIVE_SEARCH`**. **AST-973** sweeps remaining roster/integration/frontend legacy vocab fixtures.

### AST-971 · AST-871

Persist company-shaped **`state_history`** on create seed and every successful **`transition_candidate_state`** (sole path — delete/admin do not double-append). Data column + parse/preserve-when-omitted on **`save_candidate`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Append helper + sole-path write | `src/core/candidate.py` | **`TestAst971CandidateTransitionHistory`**; revised initiate / transition / delete / AST-970 asserts for `state_history` kwarg |
| Column persist / preserve / parse | `src/data/database.py` | **`TestAst971CandidateStateHistoryColumn`** (`test_candidates.py`); revised vocab in **`TestSaveCandidate`** / migrations |

**AST-971** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst971CandidateTransitionHistory \
  tests/component/core/test_candidate.py::TestInitiateCandidate \
  tests/component/core/test_candidate.py::TestTransitionCandidateStateSuccess \
  tests/component/core/test_candidate.py::TestDeleteCandidate \
  tests/component/core/test_candidate.py::TestAst970CandidateStateMachine \
  tests/component/data/database/test_candidates.py \
  tests/component/data/database/test_candidate_migrations.py \
  -q
```


### AST-972 · AST-871

Wire **`REQUESTED_RESUME` / `REQUESTED_ARTIFACTS`** claim workers (ready / retry / error), stage **`dispatch_task`** provision, tick → **`age_stale_candidate_states`**, and **`ACTIVE_SEARCH`**-only company/job search eligibility (replacing **`LIVE_PROMPTS`**).

| Area | Source | Component tests |
| --- | --- | --- |
| Stage map + claim/trigger helpers | `src/utils/config.py` | **`TestAst972CandidateStageDispatch`** (`test_config.py`) |
| Ensure/provision rows; claim gate; tick aging; scheduler provision | `src/core/dispatcher.py` | **`TestAst972CandidateStageDispatch`**; **`TestScheduler`** (tick mock ages stale) |
| Resume/artifacts workers | `src/core/candidate.py` | **`TestAst972RequestedStageDispatch`** |
| Consult routing | `src/core/consult.py` | **`TestAst972CandidateStageConsultRouting`** |
| Eligibility split (stage keys vs inflow) | `src/data/database.py` | **`TestAst972CandidateStageEligibility`**; revised AST-525/802 inflow fixtures (`ACTIVE_SEARCH` + `task_key`) |

**AST-972** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst972CandidateStageDispatch \
  tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch \
  tests/component/core/test_dispatcher.py::TestScheduler \
  tests/component/core/test_candidate.py::TestAst972RequestedStageDispatch \
  tests/component/core/test_consult.py::TestAst972CandidateStageConsultRouting \
  tests/component/data/database/test_dispatch_tasks.py::TestAst972CandidateStageEligibility \
  tests/component/data/database/test_dispatch_tasks.py::TestAst525InflowDiscoveryEligible \
  tests/component/data/database/test_dispatch_tasks.py::TestAst802InflowDiscoveryEligible \
  -q
```


### AST-1113 · AST-1109

**Parent:** [AST-1109 — Hard-coded daisy chain in config.py](https://linear.app/astralcareermatch/issue/AST-1109/hard-coded-daisy-chain-in-configpy). **Publish:** `origin/sub/AST-1109/AST-1113-anomaly-craft-task-keys-boot-run-next`.

Primary config/migration map: **`docs/test-bible/utils/config.md`** / **`docs/test-bible/data/database/agent_tasks.md`** AST-1113. Candidate walk: `run_requested_artifacts_dispatch` uses singular `craft_task_key` + `_current_agent_task_run_next` with `suppress_run_next=True` per hop; UI generate also suppresses auto-recurse.

| Area | Source | Component tests |
| --- | --- | --- |
| Artifacts dispatch walk / mid-fail | `src/core/candidate.py` | revised **`TestAst972RequestedStageDispatch`** |

**Broken / obsolete (Betty revision):** **`test_artifacts_dispatch_success_runs_all_crafts`** reading `craft_task_keys`.



### AST-973 · AST-871

Legacy candidate state remap + hard-delete of pre-cutover `DELETED`; dispatch trigger remap; reap-due purge; consumer fixture sweep off retired four-step names.

| Area | Source | Component tests |
| --- | --- | --- |
| Legacy map + remap helper | `src/utils/config.py` | **`TestAst973LegacyCandidateRemap`** |
| hard_delete + migrate A/B/C; ensure = BC only | `src/data/database.py` | **`TestAst973LegacyCandidateMigration`** |
| Core wrappers | `src/core/candidate.py` | **`TestAst973HardDeleteAndReapPurge`** |
| Fixture vocab sweep | roster / integration / frontend | `LIVE_PROMPTS`→`ACTIVE_SEARCH`; `CONTEXT_READY`→`ACTIVE_SEARCH` |

**AST-973** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst973LegacyCandidateRemap \
  tests/component/core/test_candidate.py::TestAst973HardDeleteAndReapPurge \
  tests/component/data/database/test_candidates.py::TestAst973LegacyCandidateMigration \
  -q
```


### AST-986 · AST-985

**AST-986:** Admin session resume parse — paste → response-only JSON (`resume_structure` / `base_resume` / `parsed_response`). Synthetic ctx omits `astral_candidate_id`; ledger sentinel `candidate_id="session"`; **never** `get_candidate` / `save_candidate`. Route: `POST /api/admin/session_resume/parse` (`@require_admin`). UI / HTML tab / session retention = sibling **AST-987**. **Task key:** originally `craft_resume_base`; **AST-1038** re-keys to Ruth `simple_resume_parse` (revised **`TestAst986SessionResumeParse`**).

| Area | Source | Component tests |
| --- | --- | --- |
| Core session parse (no persist / no bind) | `src/core/candidate.py` **`run_session_resume_parse`** | **`TestAst986SessionResumeParse`** |
| Admin POST delegate + auth | `src/ui/api/api_admin.py` **`session_resume_parse`** | **`TestAst986SessionResumeParseApi`** (`test_api_admin.py`) |

**Broken / obsolete:** none — new surface; **`TestRunCandidateArtifactGeneration`** persist path unchanged.

**AST-986** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst986SessionResumeParse \
  tests/component/ui/api/test_api_admin.py::TestAst986SessionResumeParseApi \
  -q
```

---

### AST-996 · AST-994

**AST-996:** Judith `craft_resume_base` Experience is an ordered **job array** (`company` / `title` / `dates` / `location` / `accomplishments`). Config shares `_EXPERIENCE_JOB_ARRAY_FIELD` across TASK + `resume_content` shapes; `DATA_SHAPES` marks experience as `experience_jobs`. Candidate split/filter/flatten/token preserve job lists (no `str(list)`); legacy string experience still readable. Style D debug lists recorded jobs on session parse / parse_candidate_resume / craft generate when `debug=True`. ArtifactEditor JSON round-trip for experience tabs — see **`docs/test-bible/frontend/components.md`**. HTML emit / job-tailored highlights = siblings **AST-998** / **AST-997**.

| Area | Source | Component tests |
| --- | --- | --- |
| Preserve / split / filter / token / Style D debug / prompt contract | `src/core/candidate.py`, `data/admin/agent_task.json` | **`TestAst996ExperienceJobArray`**; revised **`TestAst517ResumeStructure`** schema fixtures; revised **`TestAst519ResumeStructureUiHelpers::test_filter_base_resume_to_structure_drops_orphans_and_accent`**; revised **`TestAst986SessionResumeParse::test_200_success_debug_style_d`** |
| Shared schema + stringify example | `src/utils/config.py` | **`TestAst996ExperienceJobArrayConfig`** (primary: **`docs/test-bible/utils/config.md`**) |
| Base Resume Content JSON load/Save | `ArtifactEditor.tsx` | **`test_ArtifactEditor.test.tsx`** — **`AST-996:*`** (primary: **`docs/test-bible/frontend/components.md`**) |

**Broken / obsolete this pass:** schema-validation fixtures that used string `experience`; filter helper that expected `str(99)` coercion; session debug assert on `debug_detail_block` (replaced by job-focused `debug_detail`).

**AST-996** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst996ExperienceJobArray \
  tests/component/core/test_candidate.py::TestAst517ResumeStructure \
  tests/component/core/test_candidate.py::TestAst519ResumeStructureUiHelpers \
  tests/component/core/test_candidate.py::TestAst986SessionResumeParse \
  tests/component/core/test_candidate.py::TestRunCandidateArtifactGeneration \
  tests/component/utils/test_config.py::TestAst996ExperienceJobArrayConfig \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  --testNamePattern="AST-996"
```

---

### AST-1027 · AST-1019

**AST-1027 (UAT):** Repo `data/admin/agent_task.json` → `craft_resume_base` `cache_prompt` preserves `__` / `~~` typography digraphs (FORMATTING RULES + QUALITY CHECKLIST + skills/contact/prior/competencies separator fidelity). Builder expand remains **AST-1007** / **`TestAst1027UatMarkerExpand`** in **`docs/test-bible/core/builder.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Prompt preserve / no-strip contract | `data/admin/agent_task.json` | **`TestAst1027CraftResumeBaseMarkerPreserve`** |
| Experience job-array prompt still present | same | **`TestAst996ExperienceJobArray::test_craft_resume_base_prompt_requires_job_array_contract`** (regression) |

**Broken / obsolete this pass:** none.

**Integration:** no existing scenario asserts craft_resume_base marker preserve language — no revision.

**AST-1027** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1027CraftResumeBaseMarkerPreserve \
  tests/component/core/test_candidate.py::TestAst996ExperienceJobArray::test_craft_resume_base_prompt_requires_job_array_contract \
  tests/component/core/test_builder.py::TestAst1027UatMarkerExpand \
  tests/component/core/test_builder.py::TestAst1007NestedTypographyMarkers \
  -q
```

---

### AST-1028 · AST-1019

**AST-1028 (UAT):** Repo `data/admin/agent_task.json` → `craft_resume_base` `cache_prompt` adds `### candidate_tagline` (between title and contact) and tightens `### candidate_title` to title-only (no specialty/keyword / em-dash tails). Builder header/meta emit unchanged when fields are split (**AST-1010** / **AST-1021**). Primary prompt assert here; emit UAT sample: **`docs/test-bible/core/builder.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Prompt title/tagline split + checklist | `data/admin/agent_task.json` | **`TestAst1028CraftResumeBaseTitleTaglineSplit`** |
| Marker preserve still present | same | **`TestAst1027CraftResumeBaseMarkerPreserve`** (regression) |
| Job-array prompt still present | same | **`TestAst996ExperienceJobArray::test_craft_resume_base_prompt_requires_job_array_contract`** (regression) |

**Broken / obsolete this pass:** none — emit already excluded tagline from body; bug was parse folding keywords into title.

**Integration:** no existing scenario asserts craft_resume_base title/tagline split — no revision.

**AST-1028** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1028CraftResumeBaseTitleTaglineSplit \
  tests/component/core/test_candidate.py::TestAst1027CraftResumeBaseMarkerPreserve \
  tests/component/core/test_candidate.py::TestAst996ExperienceJobArray::test_craft_resume_base_prompt_requires_job_array_contract \
  tests/component/core/test_builder.py::TestAst1028UatKeywordsMetaEmit \
  tests/component/core/test_builder.py::TestAst1010HeaderContactMetaStyles \
  tests/component/core/test_builder.py::TestAst1021DocumentTitleChrome \
  -q
```

---

### AST-1030 · AST-1019

**AST-1030 (UAT):** Repo `data/admin/agent_task.json` → `craft_resume_base` `cache_prompt` requires preserving paste `<no bullet>` on role lead lines (do not invent). Builder `_split_role_accomplishments` already maps that prefix to `.role-description` (**AST-1008**); stripped prefix makes the lead a first `<li>`. Emit proof: **`docs/test-bible/core/builder.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Prompt preserve / do-not-invent + checklist | `data/admin/agent_task.json` | **`TestAst1030CraftResumeBaseNoBulletPreserve`** |
| Marker / competencies / title-tagline / job-array regressions | same | **`TestAst1027CraftResumeBaseMarkerPreserve`**, **`TestAst1029CraftResumeBaseCompetenciesBullets`**, **`TestAst1028CraftResumeBaseTitleTaglineSplit`**, **`TestAst996ExperienceJobArray::test_craft_resume_base_prompt_requires_job_array_contract`** |

**Broken / obsolete this pass:** none — emit path unchanged; prompt was the gap.

**Integration:** no existing scenario asserts `<no bullet>` preserve — no revision.

**AST-1030** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1030CraftResumeBaseNoBulletPreserve \
  tests/component/core/test_candidate.py::TestAst1027CraftResumeBaseMarkerPreserve \
  tests/component/core/test_candidate.py::TestAst1029CraftResumeBaseCompetenciesBullets \
  tests/component/core/test_candidate.py::TestAst1028CraftResumeBaseTitleTaglineSplit \
  tests/component/core/test_candidate.py::TestAst996ExperienceJobArray::test_craft_resume_base_prompt_requires_job_array_contract \
  tests/component/core/test_builder.py::TestAst1030UatNoBulletLeadEmit \
  tests/component/core/test_builder.py::TestAst1008ExperienceGoldenLayout \
  -q
```

---

### AST-1029 · AST-1019

**AST-1029 (UAT):** Repo `data/admin/agent_task.json` → `craft_resume_base` `cache_prompt` hardens `### core_competencies` (and `### prior_experience`) to require `•` item separators and forbid `|` / `" | "` — replacing AST-1027 soft “prefer” language. Builder competencies emit remains escape-only (**AST-1009**). Emit proof: **`docs/test-bible/core/builder.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Prompt •-required / pipe-forbidden + checklist | `data/admin/agent_task.json` | **`TestAst1029CraftResumeBaseCompetenciesBullets`** |
| Marker / title-tagline / job-array prompt regressions | same | **`TestAst1027CraftResumeBaseMarkerPreserve`**, **`TestAst1028CraftResumeBaseTitleTaglineSplit`**, **`TestAst996ExperienceJobArray::test_craft_resume_base_prompt_requires_job_array_contract`** |

**Broken / obsolete this pass:** none — soft prefer language retired by prompt harden (asserted gone).

**Integration:** no existing scenario asserts competencies separators — no revision.

**AST-1029** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1029CraftResumeBaseCompetenciesBullets \
  tests/component/core/test_candidate.py::TestAst1027CraftResumeBaseMarkerPreserve \
  tests/component/core/test_candidate.py::TestAst1028CraftResumeBaseTitleTaglineSplit \
  tests/component/core/test_candidate.py::TestAst996ExperienceJobArray::test_craft_resume_base_prompt_requires_job_array_contract \
  tests/component/core/test_builder.py::TestAst1029UatCompetenciesBulletsEmit \
  tests/component/core/test_builder.py::TestAst1009EducationSkillsPrior \
  -q
```

---

### AST-997 · AST-994

**AST-997:** Job-tailored hops (`draft_job_resume` / `finalize_job_resume`) accept/emit the AST-996 experience job-array shape. `pin_experience_job_facts_from_base` restores company/title/dates/location by `(company, title)` match (no index fallback); accomplishments may tailor. Tracker persist/match gates keep job arrays. Style D debug on tailor hops when `debug=True`. HTML emit = **AST-998**.

| Area | Source | Component tests |
| --- | --- | --- |
| Normalize / validate / pin / hop prompts | `src/core/candidate.py`, `data/admin/agent_task.json` | **`TestAst997JobTailoredExperience`**; reuse **`TestAst594DraftJobResumePayload`** (legacy string still OK) |
| Finalize optional schema | `src/utils/config.py` | **`TestAst997FinalizeExperienceJobArray`** (primary: **`docs/test-bible/utils/config.md`**) |
| Persist / match gates | `src/core/tracker.py` | **`TestAst997ExperienceJobArrayPersist`** (primary: **`docs/test-bible/core/tracker.md`**) |

**Broken / obsolete this pass:** none — legacy string experience still accepted on draft validate.

**AST-997** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst997JobTailoredExperience \
  tests/component/core/test_candidate.py::TestAst594DraftJobResumePayload \
  tests/component/core/test_tracker.py::TestAst997ExperienceJobArrayPersist \
  tests/component/utils/test_config.py::TestAst997FinalizeExperienceJobArray \
  -q
```

---

### AST-1005 · AST-994

**AST-1005 (UAT bug):** Craft-base normalize promotes known section ids from **direct keys** on `resume_structure` (e.g. `candidate_name`, experience job arrays) even when `sections` is missing — before `default_resume_structure()` replace — so validation no longer false-misses `candidate_name` beside a well-formed experience job array. Does not loosen required `candidate_name`. Items-schema hardening: **`docs/test-bible/core/agent.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Direct-key promote + validate matrix | `src/core/candidate.py` | **`TestAst1005FalseMissingCandidateName`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1005FalseMissingCandidateName \
  tests/component/core/test_candidate.py::TestAst996ExperienceJobArray \
  tests/component/core/test_candidate.py::TestAst517ResumeStructure \
  -q
```

---

### AST-1014 · AST-952

**AST-1014:** Contact / context / artifacts library under `candidate_data` plus table columns `first` / `last` / `full` / `pronouns`. Remaps `profile`→`contact`, context `starting_resume_text`→`raw_resume` (and LinkedIn/sample siblings), seeds empty `hopes`/`interests`/`concerns`. `build_candidate_token_view`, URL normalize, refuse `profile` writes, library `debug=` contract. Boundaries: Ruth (AST-1015), PREAMBLE_CONFIG (AST-1016), mechanical UI (AST-1017).

| Area | Source | Component tests |
| --- | --- | --- |
| Token view / URL normalize / save refuse+columns / debug | `src/core/candidate.py` | **`TestAst1014CandidateLibrary`** |
| Library config + shapes/tokens + middle retired | `src/utils/config.py` | **`TestAst1014CandidateLibraryConfig`**, revised **`TestAst510MiddleNameConfig`**, **`TestAst575PronounTokens`** |
| Contact render + coerce columns | `src/core/builder.py` | **`TestAst1014BuilderContact`**, revised **`TestBuilderHelpers`** |
| Idempotent library migration | `src/data/database.py` | **`TestAst1014CandidateLibraryMigration`** (primary map: **`docs/test-bible/data/database/candidate_migrations.md`**) |
| PUT refuse `profile`; signature under `contact` | `src/ui/api/api_candidate.py` | **`TestCandidateRoutes::test_update_rejects_legacy_profile_body`** (+ revised signature path) |
| Profile / Admin one-home UI (§6c) | pages | **`test_CandidateProfile.test.tsx`**, **`test_AdminManageCandidates.test.tsx`** |
| Gazer title_patterns under `contact` | `src/core/gazer.py` | revised **`TestCompiledTitlePatterns`** |
| Intake context `raw_*` persist | `src/core/intake.py` | revised **`TestIntakeSessionFlow`** |

**Broken / obsolete (Betty revision):** fixtures using `candidate_data.profile`, `starting_resume_text` / `linkedin_profile_text` / `sample_cover_text`, `_apply_profile_to_render_dict`, `pronoun_preference` nested under profile, `state="NEW"` in core `seeded_db`, AST-510 middle shape/token asserts, Profile/Admin middle + `profile.*` payloads; AST-575 migration end-state now columns after library migrate.

**Integration:** no existing scenario asserts profile/contact library homes — no revision; do not invent new integration coverage.

**AST-1014** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1014CandidateLibrary \
  tests/component/utils/test_config.py::TestAst1014CandidateLibraryConfig \
  tests/component/utils/test_config.py::TestAst510MiddleNameConfig \
  tests/component/utils/test_config.py::TestAst575PronounTokens \
  tests/component/core/test_builder.py::TestAst1014BuilderContact \
  tests/component/core/test_builder.py::TestBuilderHelpers \
  tests/component/data/database/test_candidate_migrations.py \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_update_rejects_legacy_profile_body \
  tests/component/core/test_gazer.py::TestCompiledTitlePatterns \
  tests/component/core/test_intake.py::TestIntakeSessionFlow::test_create_session_persists_source_materials \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateProfile.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminManageCandidates.test.tsx
```

---

### AST-1038 · AST-1036

**AST-1038:** `run_session_resume_parse` `do_task` key → `simple_resume_parse` (Ruth); non-dict error string + docstring; Admin `session_resume_parse` docstring only. Preserves AST-986 sentinel / no-persist / Style D. Judith `craft_resume_base` candidate craft unchanged. Catalog/seed = **AST-1037**.

| Area | Source | Component tests |
| --- | --- | --- |
| Core wire + craft-path unchanged | `src/core/candidate.py` | **`TestAst1038SessionResumeWire`**; revised **`TestAst986SessionResumeParse`** (`task_key` / error string) |
| Admin thin route (docstring only) | `src/ui/api/api_admin.py` | **`TestAst986SessionResumeParseApi`** (existing — contract unchanged) |

**Broken / obsolete:** **`TestAst986SessionResumeParse`** assertions on `craft_resume_base` task_key and non-dict error string → `simple_resume_parse`.

**Integration:** no existing scenario asserts session-parse task key — no revision; do not invent new integration coverage.

**AST-1038** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1038SessionResumeWire \
  tests/component/core/test_candidate.py::TestAst986SessionResumeParse \
  tests/component/ui/api/test_api_admin.py::TestAst986SessionResumeParseApi \
  -q
```


### AST-1047 · AST-1044

**Parent:** [AST-1044 — Bind email to candidate](https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate). **Publish:** `origin/sub/AST-1044/AST-1047-reusable-get-candidate-string-lookup-from-bind`.

`get_candidate_id_for_query`: unique email/name hit via `CANDIDATE_LOOKUP_CONFIG`; `parseaddr` for display-name From; ambiguous/none → None; ID `get_candidate` unchanged. Style D when `debug=True`.

| Area | Source | Component tests |
| --- | --- | --- |
| String → unique id / none / ambiguous / empty / parseaddr / casefold / Style D | `src/core/candidate.py` | **`TestAst1047GetCandidateIdForQuery`** |

**Broken / obsolete:** none — additive lookup API.

**Integration:** no existing scenario asserts string→candidate lookup — no revision; do not invent new integration coverage.


---

### AST-1068 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id`.

`get_candidate_id_for_query` scans `slack_user_id_paths`; `initiate_prospect_candidate` creates `PROSPECT` with **name columns** (`first=`/`last=`) and `candidate_data.contact.slack_user_id` only — **no** legacy `profile` blob (AST-1014). Contact: **`docs/test-bible/core/contact.md`**. Config: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Slack id lookup + prospect initiate (columns + contact) | `src/core/candidate.py` | **`TestAst1068CandidateSlackLookup`** |

**Broken / obsolete:** initiate cases that put names under `candidate_data.profile` — revised for AST-1014 columns.

**Integration:** no existing scenario — no revision.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1068CandidateSlackLookup \
  -q
```


---

### AST-1074 · AST-953

**Parent:** [AST-953 — Topic Menu Generation](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation). **Publish:** `origin/sub/AST-953/AST-1074-topic-menu-model-and-persistence`.

`candidate_data.topic_menu` meta sibling: `empty_topic_menu` / `normalize_topic_menu` / `get_topic_menu` / `validate_topic` / `validate_topic_menu` / `revise_topic_menu` (missing ids → `retired`, no wipe) / `save_topic_menu` (default `revise=True`; Style D when `debug=True`). Config vocabulary: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Validate / revise / get / save Topic Menu | `src/core/candidate.py` | **`TestAst1074TopicMenuPersistence`** |

**Broken / obsolete:** none — additive Topic Menu library API.

**Integration:** no existing scenario asserts `topic_menu` persistence — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1074TopicMenuPersistence \
  tests/component/utils/test_config.py::TestAst1074TopicMenuConfig \
  -q
```


---

### AST-1075 · AST-953

**Parent:** [AST-953 — Topic Menu Generation](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation). **Publish:** `origin/sub/AST-953/AST-1075-estelle-preamble-confirm-and-topic-menu-generation`.

Optional `preamble_confirmed_at` on `candidate_data.topic_menu` (normalize / validate / revise prefer-incoming-else-existing) + `mark_topic_menu_preamble_confirmed` (stamp without wiping topics; Style D when `debug=True`). Orchestration: **`docs/test-bible/core/intake.md`**. Config: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Stamp preserve + mark helper | `src/core/candidate.py` | **`TestAst1075PreambleConfirmedAt`** |

**Broken / obsolete:** none — additive meta key on AST-1074 Topic Menu envelope.

**Integration:** no existing scenario — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1075PreambleConfirmedAt \
  tests/component/core/test_candidate.py::TestAst1074TopicMenuPersistence \
  -q
```


---

### AST-1081 · AST-1065

**Parent:** [AST-1065 — Update candidate ui for contact info](https://linear.app/astralcareermatch/issue/AST-1065/update-candidate-ui-for-contact-info). **Publish:** `origin/sub/AST-1065/AST-1081-contact-shapes-websites-full`.

`save_candidate_data`: empty/whitespace `full` → `recompute_full_name` (submitted first/last with existing-column fallback); non-empty `full` strip-persists as override; `contact.websites` coerced to trimmed non-empty `list[str]` (`None`→`[]`; non-list → `ValueError`). Shapes + FormFields: **`docs/test-bible/utils/config.md`**, **`docs/test-bible/frontend/components.md`**. Profile page/nav = **AST-1082**.

| Area | Source | Component tests |
| --- | --- | --- |
| Empty-full recompute + websites coerce | `src/core/candidate.py` | **`TestAst1081ContactShapesSaveContract`** |
| Contact Information shapes (`full` / `string_list` / reason_codes) | `src/utils/config.py` | **`TestAst1081ContactShapesConfig`** (map: **`docs/test-bible/utils/config.md`**) |
| FormFields `string_list` Add/edit/Remove | `FormFields.tsx` | **`test_FormFields.test.tsx`** — **`FormFields string_list (AST-1081)`** (map: **`docs/test-bible/frontend/components.md`**) |

**Existing coverage (still required):** **`TestAst1014CandidateLibrary`** (omit-full when first/last change; refuse `profile`; URL normalize).

**Broken / obsolete:** none — additive empty-full branch + websites coerce; AST-1014 omit-full path unchanged.

**Integration:** no existing scenario asserts Profile contact shapes / websites list / empty-full save — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1081ContactShapesSaveContract \
  tests/component/core/test_candidate.py::TestAst1014CandidateLibrary \
  tests/component/utils/test_config.py::TestAst1081ContactShapesConfig \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_FormFields.test.tsx
```


### AST-1080 · AST-1045

**Parent:** [AST-1045 — Verify unique contact info](https://linear.app/astralcareermatch/issue/AST-1045/verify-unique-contact-info). **Publish:** `origin/sub/AST-1045/AST-1080-enforce-uniqueness-on-candidate-contact-save`.

Contact uniqueness gate on `save_candidate_data` / `initiate_candidate` / `initiate_prospect_candidate`: within-candidate collapse (duplicate reply/websites), cross-candidate hard-fail `ValueError` (toast-ready), Style D when `debug=True`. Vocabulary: **AST-1079** (`CANDIDATE_CONTACT_UNIQUENESS_CONFIG`).

| Area | Source | Component tests |
| --- | --- | --- |
| Within collapse + cross hard-fail + debug + initiate | `src/core/candidate.py` | **`TestAst1080ContactUniqueness`** |

**Broken / obsolete:** none — additive gate; existing library save paths unchanged when no collision.

**Integration:** none — do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1080ContactUniqueness \
  -q
```

---

### AST-1085 · AST-1077

**Parent:** [AST-1077 — Add a constant set of rubric vectors to generated JD evaluate vectors](https://linear.app/astralcareermatch/issue/AST-1077/add-a-constant-set-of-rubric-vectors-to-generated-jd-evaluate-vectors). **Publish:** `origin/sub/AST-1077/AST-1085-wire-constants-evaluate-jd`.

Append-merge `EMBEDDED_EVALUATE_JD_CRITERIA` (QC then GC; AST-1084) into `evaluate_jd` / `jobdesc_rubric` / `craft_jobdesc_rubric` hydrate, save, and generate — embedded wins on duplicate code; other rubric owners unchanged. Config definitions: **`docs/test-bible/utils/config.md`** (**AST-1084**).

| Area | Source | Component tests |
| --- | --- | --- |
| Helper + hydrate / save / craft generate / persist | `src/core/candidate.py` | **`TestAst1085EvaluateJdEmbeddedMerge`** |

**Broken / obsolete:** none — additive owner-gated merge; AST-723 prefilter prepend path unchanged.

**Integration:** none revised (no existing scenario asserts QC/GC append on evaluate_jd hydrate).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1085EvaluateJdEmbeddedMerge \
  tests/component/utils/test_config.py::TestAst1084EvaluateJdCriteria \
  -q
```


---

### AST-1092 · AST-1065 (UAT)

**Parent:** [AST-1065 — Update candidate ui for contact info](https://linear.app/astralcareermatch/issue/AST-1065/update-candidate-ui-for-contact-info). **Publish:** `origin/sub/AST-1065/AST-1092-uat-extra-binding-emails-labels`.

`save_candidate_data` coerces `contact.extra_emails` like websites; `get_candidate_id_for_query` expands `email_list_paths` only (not uniqueness websites). Config/Profile: **`docs/test-bible/utils/config.md`**, **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Coerce + bind via extra_emails | `src/core/candidate.py` | **`TestAst1092ExtraBindingEmails`** |

**Broken / obsolete:** none for core — websites coerce path shared; AST-1081 websites asserts still match.

**Integration:** none — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1092ExtraBindingEmails \
  tests/component/core/test_candidate.py::TestAst1081ContactShapesSaveContract \
  -q
```

### AST-1095 · AST-1045 (UAT)

**Parent:** [AST-1045 — Verify unique contact info](https://linear.app/astralcareermatch/issue/AST-1045/verify-unique-contact-info). **Publish:** `origin/sub/AST-1045/AST-1095-uat-email-unique-root-and-extra`.

Shared email uniqueness pool: root `email_paths` + `email_list_paths` (`extra_emails`) under casefold email compare on save/initiate; within-candidate root+extra collapse; cross root↔extra / extra↔extra hard-fail toast `ValueError`; initiate coerce parity for `extra_emails`. Config: **`docs/test-bible/utils/config.md`**. Base gate: **AST-1080**.

| Area | Source | Component tests |
| --- | --- | --- |
| Root↔extra / extra↔extra cross + within + initiate | `src/core/candidate.py` | **`TestAst1095EmailUniqueRootAndExtra`** |

**Broken / obsolete:** none for AST-1080 scalar/website cases — additive email-list pool walk.

**Integration:** none — do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1095EmailUniqueRootAndExtra \
  tests/component/core/test_candidate.py::TestAst1080ContactUniqueness \
  -q
```

### AST-1137 · AST-1124

**Parent:** [AST-1124 — Cover Letter Header is incorrect](https://linear.app/astralcareermatch/issue/AST-1124/cover-letter-header-is-incorrect). **Publish:** `origin/sub/AST-1124/AST-1137-candidate-from-block-text-contact-defaults`.

`resolve_cover_from_block` returns custom `contact.cover_letter_from_block` (`source=candidate`) or expands `default_template` (`source=default`); empty segments/lines omitted; accepts DB row or token-view contact shape. Config: **`docs/test-bible/utils/config.md`**. Token expand / `|`→`•` = **AST-1148** (`expand_cover_from_block_text`). Job/session HTML emit = siblings **AST-1138** / **AST-1139**.

| Area | Source | Component tests |
| --- | --- | --- |
| Custom vs default resolve + omit empties + debug | `src/core/candidate.py` | **`TestAst1137ResolveCoverFromBlock`** (revised by **AST-1148** — template expand / Style D) |
| COVER_FROM_BLOCK_CONFIG + profile textarea | `src/utils/config.py` | **`TestAst1137CoverFromBlockConfig`** |

**Broken / obsolete:** path-composed default + `line*_segments` debug — revised by **AST-1148**.

**Integration:** none — no existing integration scenario asserts from-block composition; do not invent new coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1137ResolveCoverFromBlock \
  tests/component/utils/test_config.py::TestAst1137CoverFromBlockConfig \
  -q
```


### AST-1148 · AST-1145

**Parent:** [AST-1145 — Allow contact info tokens and | chars in fromBlock](https://linear.app/astralcareermatch/issue/AST-1145/allow-contact-info-tokens-and-or-chars-in-fromblock). **Publish:** `origin/sub/AST-1145/AST-1148-resolve-tokens-in-from-block-emit-debug`.

`expand_cover_from_block_text` expands allowlisted `{$TOKEN}` via `TOKEN_SOURCES`, rewrites `|`→`emit_separator`, drops empty segments per `empty_segment_policy`. `resolve_cover_from_block` selects custom authoring or `default_template` then expands (no path-based default composition). Brief aliases left as-is. Style D on expand + resolve when `debug=True`. Session-typed From: **`docs/test-bible/core/builder.md`**. Config keys: **AST-1147**.

| Area | Source | Component tests |
| --- | --- | --- |
| Expand tokens / pipe / drop / aliases / Style D | `src/core/candidate.py` | **`TestAst1148ExpandCoverFromBlock`** |
| Resolve custom+default via expand (revised) | same | **`TestAst1137ResolveCoverFromBlock`** |

**Broken / obsolete:** AST-1137 path-composed default asserts + `line*_segments` debug — revised this pass.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1148ExpandCoverFromBlock \
  tests/component/core/test_candidate.py::TestAst1137ResolveCoverFromBlock \
  tests/component/core/test_builder.py::TestAst1148SessionTypedFromBlockExpand \
  -q
```



### AST-1235 · AST-1173

**Parent:** [AST-1173 — Consent — install disclosure, affirmative opt-in, and off-switch](https://linear.app/astralcareermatch/issue/AST-1173/consent-install-disclosure-affirmative-opt-in-and-off-switch). **Publish:** `origin/sub/AST-1173/AST-1235-versioned-consent-record-and-api`.

`candidate_data.surfer_consent` meta sibling: `empty_surfer_consent` / `normalize_surfer_consent` / `get_surfer_consent` / `is_surfer_consent_current` / `surfer_consent_dto` / `opt_in_surfer_consent` / `opt_out_surfer_consent` (preserve last `accepted_version` on opt-out; Style D when `debug=True`). `is_current` only when `opted_in` **and** `accepted_version == SURFER_CONSENT_CONFIG["current_version"]`. Config: **`docs/test-bible/utils/config.md`**. API: **`docs/test-bible/ui/api/api_surfer.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Normalize / is_current / get / opt-in / opt-out / Style D | `src/core/candidate.py` | **`TestAst1235SurferConsent`** |

**Broken / obsolete:** none — additive Surfer consent helpers.

**Integration:** no existing scenario asserts `surfer_consent` — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1235SurferConsent \
  tests/component/utils/test_config.py::TestAst1235SurferConsentConfig \
  -q
```

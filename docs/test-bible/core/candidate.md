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

**Note:** Broader opaque `LIVE_PROMPTS` / `CONTEXT_READY` fixtures in roster/dispatcher/integration remain until sibling **AST-973** consumer/migration sweep — they are not registry membership asserts.

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


# Pages

**Test tree:** `tests/component/pages/`

### AST-436 · AST-442

Parent UAT on **`origin/ftr/AST-436-quickie-bugs`** surfaced gaps when manifests tested components or API defaults only. Use **§6c** for all future UI QA.

| Route / page | Source | Minimum component test | Required mocks (first paint) |
| --- | --- | --- | --- |
| Candidate Profile | `src/ui/frontend/src/pages/CandidateProfile.tsx` | `tests/component/frontend/pages/test_CandidateProfile.test.tsx` — must render page + open signature-image tab | `/api/shapes/candidates`, `/api/ui_config`, `/api/candidates/{id}`, `/api/state_ui_manifest` (reject OK) |
| Execution History | `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` | `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx` — include date blur / clear behavior per **§6c** | `/api/candidates`, `/api/admin/dispatch_ledger`, ledger logs as needed |
| Scheduled Actions | `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` | candidates, dispatch tasks, thread status |
| Signature image tab wiring | `TabbedTextArea.tsx` + `CandidateProfile.tsx` | **Both** `test_TabbedTextArea.test.tsx` (panel slot) **and** `test_CandidateProfile.test.tsx` (routed page) | see Candidate Profile row |

---

### AST-456 · AST-453

**`AdminTaskPrompts`** loads **`/api/admin/tasks/meta/tokens`** and **`meta/chain_tokens`**, merges for **`TokenTextarea`** pickers across all segments, and exposes **seven** accordion panels (**System**, **Cache Block A–D**, **No cache**, **User**) plus **`PREVIEW_TABS`** for resolved preview per segment.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed Manage Tasks UX | `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx` (**`AST-456`**), `tests/component/frontend/lib/test_manageTasksTokenPicker.test.ts` (**merged picker**) |

---

### AST-464 · AST-373

Generic **`apply_copy_output_table_upsert(table_name, json_payload)`**: parse JSON array, FK pragma on, transactional generic upsert-by-PK or **`agent_task`** import (**`apply_agent_task_copy_upsert`** + **`_save_agent_task_on_connection`**). **AST-464** is core + **`database.py`**; **AST-465** adds Data Management UI + **`POST /api/admin/data/table_copy_upsert`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Orchestrator (**malformed payload, FK rollback, composite PK, nested cell reject**) | `src/core/table_copy_upsert.py` | `tests/component/data/database/test_table_copy_upsert.py` |
| PK enforcement + generic / **`agent_task`** batch paths | `src/data/database.py` (**`primary_key_column_names`**, **`apply_generic_table_copy_upsert`**, **`apply_agent_task_copy_upsert`**, **`save_agent_task`**) | `tests/component/data/database/test_table_copy_upsert.py`; versioning round-trip **`tests/component/data/database/test_agent_tasks.py`**, **`tests/component/ui/api/test_api_admin.py`** |
| Data Management **Table Upsert** + admin route (**AST-465**) | `src/ui/frontend/src/pages/AdminDataManagement.tsx`, `src/ui/api/api_admin.py` (**`admin_table_copy_upsert`**) | `tests/component/frontend/pages/test_AdminDataManagement.test.tsx` (**§6c** — page + modal + toast paths); **`tests/component/ui/api/test_api_admin.py`** (**`test_table_copy_upsert_paths`**) |

---

### AST-522 · AST-498

Rebuild **`JobsRecommended.tsx`**: config-driven sections (**Recommended** / **In Progress** / **Ready**), plain numeric **JD / DO / GET / LIKE** from flattened API fields (no LIKE rubric grade-dot columns, no **`latest_score`** column). **`build_state_ui_manifest()["jobs"]["recommended"]`** + **`StateUiContext`** defaults mirror **`JOBS_RECOMMENDED_UI_SECTIONS`** / **`JOBS_RECOMMENDED_PHASE_SCORE_COLUMNS`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Recommended UI manifest | `src/utils/config.py` | **`TestBuildStateUiManifest::test_ast522_recommended_manifest_sections_and_phase_columns`** (`test_config.py`) |
| Routed Recommended page (**§6c**) | `src/ui/frontend/src/pages/JobsRecommended.tsx` | **`tests/component/frontend/pages/test_JobsRecommended.test.tsx`** — three sections, phase headers, score + em dash, per-section Company sort, Skip / View Job Analysis, row → detail modal |
| Jobs API recommended view | `src/ui/api/api_jobs.py` | **`test_list_recommended_and_default`** (`test_api_jobs.py`) — regression |
| **`RECOMMENDED_JOB_STATES`** membership | `src/utils/config.py` | **`TestAst479LikePassStates`** (`test_config.py`) — regression |

**AST-522** narrowed run (Vitest paths are **not** forwarded by `run_component_tests.sh` trailing args — run Vitest explicitly):

```bash
python3 -m pytest tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast522_recommended_manifest_sections_and_phase_columns tests/component/ui/api/test_api_jobs.py::test_list_recommended_and_default -q

cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx
```

---

### AST-524 · AST-525 · AST-526 · AST-523

Replaces Phase 0 artifact blob as **source of truth**: one SQLite row per candidate per search term with nullable **`last_scan_at`**, upsert-and-delete sync, legacy artifact migration (**AST-524**). **AST-525** retargets inflow discovery cadence; **AST-526** Artifacts UI/API wiring.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-524** | Table DDL + migration; sync preserves **`last_scan_at`**; core/API sync helpers; stop persisting artifact on save | `src/data/database.py`, `src/core/candidate.py`, `src/ui/api/api_candidate.py`, `src/utils/config.py` (comment only) | `tests/component/data/database/test_company_search_terms.py::TestAst524CompanySearchTermsTable`; `tests/component/core/test_candidate.py::{TestNormalizeCompanySearchTermsOnSave,TestCompanySearchTermsLines,TestAst524CompanySearchTermsTable}`; `tests/component/ui/api/test_api_candidate.py::{TestCandidateRoutes::test_update_rejects_blank_company_search_terms,TestAst524CompanySearchTermsSync}` |
| **AST-525** | Per-term **`last_scan_at`** cadence; CSE only for stale terms; bump after successful CSE; **`COMPANY_SEARCH_TERMS`** from table overlay | `src/utils/config.py`, `src/data/database.py`, `src/core/roster.py`, `src/core/candidate.py`, `src/core/agent.py` | `tests/component/utils/test_config.py::TestAst525InflowDiscoveryConfig`; `tests/component/data/database/test_company_search_terms.py::TestAst524CompanySearchTermsTable::test_list_stale_company_search_terms_ordered`; `tests/component/data/database/test_dispatch_tasks.py::TestAst525InflowDiscoveryEligible`; `tests/component/core/test_roster.py::TestAst505InflowDiscovery::{test_run_batch_no_stale_terms_returns_zero_errors,test_run_batch_happy_path,test_run_batch_cse_failure_continues,test_run_batch_searches_only_stale_terms}`; `tests/component/core/test_candidate.py::{TestCompanySearchTermsLines,TestAst525CompanySearchTermsTokenOverlay}` |

| **AST-526** | Artifacts GET injects table-backed **`company_search_terms`**; PUT intercept syncs table, strips artifact blob; page loads top-level field (**§6c**) | `src/ui/api/api_candidate.py`, `src/ui/frontend/src/pages/ArtifactsCompanySearchTerms.tsx` | `tests/component/ui/api/test_api_candidate.py::TestAst526ArtifactsCompanySearchTermsApi`; `tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx` |


**AST-524** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_company_search_terms.py::TestAst524CompanySearchTermsTable \
  tests/component/core/test_candidate.py::TestNormalizeCompanySearchTermsOnSave \
  tests/component/core/test_candidate.py::TestCompanySearchTermsLines \
  tests/component/core/test_candidate.py::TestAst524CompanySearchTermsTable \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_update_rejects_blank_company_search_terms \
  tests/component/ui/api/test_api_candidate.py::TestAst524CompanySearchTermsSync
```

**AST-525** narrowed run (blocker **AST-524** tests optional smoke):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst525InflowDiscoveryConfig \
  tests/component/data/database/test_company_search_terms.py::TestAst524CompanySearchTermsTable::test_list_stale_company_search_terms_ordered \
  tests/component/data/database/test_dispatch_tasks.py::TestAst525InflowDiscoveryEligible \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_no_stale_terms_returns_zero_errors \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_happy_path \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_cse_failure_continues \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_searches_only_stale_terms \
  tests/component/core/test_candidate.py::TestCompanySearchTermsLines \
  tests/component/core/test_candidate.py::TestAst525CompanySearchTermsTokenOverlay
```


**AST-526** narrowed run (blocker **AST-524** tests optional smoke):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_candidate.py::TestAst526ArtifactsCompanySearchTermsApi \
  tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx
```

---

### AST-515 · AST-521 · AST-514

Parent **AST-514** labels non-dispatch UI provider calls in **`dispatch_ledger`**. **AST-515**: Ad Hoc workbench **Test** → **`adhoc-<workbench_task_key>`**. **AST-521**: Artifacts **Generate / Regenerate** and Board Searches craft **Generate** → **`user-<task_key>`** with prefixed **`batch_id`**; **`do_task`** still uses the real craft key for **`agent_data`**. **Preview** paths stay ledger-free. **Dispatch** / Scheduled Actions **Run** keep plain **`task_key`**. Execution History UI (**`AdminPerformanceMonitor`**) unchanged — list/expand/inspect use existing ledger + **`/api/agent_data/<batch_id>`** APIs.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-515** | Ledger + agent_data wrapper; **`adhoc_test`** route swap | `src/core/agent.py` (`run_adhoc_workbench_test`), `src/ui/api/api_admin.py` (`adhoc_test`) | `tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger`; `tests/component/ui/api/test_api_admin.py::{TestAdhocRoutes,TestApiAdminBranchGaps}` (adhoc preview/test paths) |
| **AST-521** | **`user-`** ledger prefix on candidate artifact + board search craft generate | `src/core/candidate.py` (`run_candidate_artifact_generation`), `src/core/boards.py` (`run_board_search_generation`), `src/ui/api/api_candidate.py`, `src/ui/api/api_boards.py` (delegates only) | `tests/component/core/test_candidate.py::TestRunCandidateArtifactGeneration`; `tests/component/core/test_boards_generate_ast521.py::TestRunBoardSearchGenerationAst521`; optional API smoke: `tests/component/ui/api/test_api_boards.py::TestBoardSearchRoutes::test_generate_delegates_to_core` |

**AST-515** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger \
  tests/component/ui/api/test_api_admin.py::TestAdhocRoutes \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_adhoc_test_decodes_encoded_payload \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_adhoc_test_hydrates_encoded_payload_with_entities \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_adhoc_test_skips_decode_without_response_text
```

Dispatch-only Execution History regression (no UI diff this child): **`tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx`** per **§7.13k** when parent UAT runs full epic.
**AST-521** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestRunCandidateArtifactGeneration \
  tests/component/core/test_boards_generate_ast521.py::TestRunBoardSearchGenerationAst521
```

Dispatch-only Execution History regression (no UI diff these children): **`tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx`** per **§7.13k** when parent UAT runs full epic.

---

### AST-513 · AST-313

Five **`{$VISIBLE_JD}`** / **`{$ANALYSIS_*}`** tokens register in **`TOKEN_SOURCES`** with **`source: job`**. Values are precomputed in **`build_job_token_context`** (`consult.py`) and threaded as **`job_context`** through **`resolve_tokens`**, **`do_task`**, **`preview_task_prompt`**, admin preview, and Ad-hoc **`_resolve_adhoc`** when **`entity_type === job`**. Single-job scope only (**`_single_job_in_scope`**).

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-513** | Registry + formatter + single-job threading + Manage Tasks preview job id | `src/utils/config.py`, `src/core/consult.py`, `src/core/agent.py`, `src/core/candidate.py`, `src/ui/api/api_admin.py`, `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | `tests/component/utils/test_config.py::TestAst513JobTokens`; `tests/component/core/test_consult.py::TestAst513JobTokenContext`; `tests/component/core/test_agent.py::TestAst513JobContext`; `tests/component/ui/api/test_api_admin.py::{TestTaskRoutes::test_preview_task_forwards_astral_job_id,TestAdhocHelpers::test_resolve_adhoc_job_entity_resolves_visible_jd_token}`; `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx` (job preview **`astral_job_id`**) |

**AST-513** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst513JobTokens \
  tests/component/core/test_consult.py::TestAst513JobTokenContext \
  tests/component/core/test_agent.py::TestAst513JobContext \
  tests/component/ui/api/test_api_admin.py::TestTaskRoutes::test_preview_task_forwards_astral_job_id \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_resolve_adhoc_job_entity_resolves_visible_jd_token
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx \
  -t "astral_job_id"
```

---

### AST-510 · AST-511 · AST-509

Optional **`profile.middle`** on candidate data contract (**AST-510**); **`{$MIDDLE_NAME}`** token; **`profile_display_name`** composes **`First Middle Last`** for resume HTML header (**AST-510**). **AST-511** wires shape-driven Candidate Profile contact grid and Admin Manage Candidates add/edit modals. No migration.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-510** | DATA_SHAPES + TOKEN_SOURCES; display helper; builder wiring; merge round-trip | `src/utils/config.py`, `src/utils/formatting.py`, `src/core/builder.py`, `src/core/candidate.py` | `tests/component/utils/test_formatting.py::TestProfileDisplayName`; `tests/component/utils/test_config.py::{TestGetTokens,TestResolveTokens::test_resolves_middle_name_token,TestAst510MiddleNameConfig}`; `tests/component/core/test_builder.py::TestBuilderHelpers::{test_applies_profile_middle_to_candidate_name,test_build_resume_from_job_emits_middle_name_in_html}`; `tests/component/core/test_candidate.py::TestAst510ProfileMiddleRoundTrip` |
| **AST-511** | Candidate Profile shape-driven middle field + save; Admin create/edit **`profile.middle`** | `src/ui/frontend/src/pages/AdminManageCandidates.tsx`, `src/ui/frontend/src/pages/CandidateProfile.tsx` (verify only) | `tests/component/frontend/pages/test_CandidateProfile.test.tsx` (**§6c** — routed page + middle save payload); `tests/component/frontend/pages/test_AdminManageCandidates.test.tsx` (middle in POST/PUT; empty middle create) |

**AST-510** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_formatting.py::TestProfileDisplayName \
  tests/component/utils/test_config.py::TestGetTokens \
  tests/component/utils/test_config.py::TestResolveTokens::test_resolves_middle_name_token \
  tests/component/utils/test_config.py::TestAst510MiddleNameConfig \
  tests/component/core/test_builder.py::TestBuilderHelpers::test_applies_profile_middle_to_candidate_name \
  tests/component/core/test_builder.py::TestBuilderHelpers::test_build_resume_from_job_emits_middle_name_in_html \
  tests/component/core/test_candidate.py::TestAst510ProfileMiddleRoundTrip
```

**AST-511** narrowed run (Vitest — run from repo root; **`run_component_tests.sh`** with only these paths skips pytest and may not invoke Vitest):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateProfile.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminManageCandidates.test.tsx
```

---

### AST-531 · AST-532 · AST-528

**AST-528 (parent):** Execution History lists **one `dispatch_ledger` row per executed LLM hop** in a **`run_next`** chain — distinct **`batch_id`**, hop **`task_key`**, scoped **`agent_data`** and app logs per hop (reverses **AST-303** single-batch-across-hops for history only). **AST-531**: backend — hop open/close in **`do_task`**, dispatcher **`entity_batch_id`** (entity claim) vs hop audit **`batch_id`**, craft/board outer-ledger skip when **`run_next`** is set. **AST-532**: Execution History UI verification (sibling). Does **not** cover hop debug logging (**AST-530**, **AST-527**) or caller-token propagation (**AST-529**).

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-531** | Per-hop ledger rows; dispatch-level ledger skipped when chain planned | `src/core/agent.py`, `src/core/dispatcher.py`, `src/core/candidate.py`, `src/core/boards.py` | `tests/component/core/test_agent.py::TestAst531RunNextHopLedger`; `tests/component/core/test_dispatcher.py::TestDispatchOne::test_run_next_chain_skips_dispatch_level_ledger` |
| **AST-532** | Execution History UI — one row per hop; batch_id-scoped logs + agent_data inspect; adhoc/user/dispatch regression | `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` (no source diff expected — **AST-515** batch scoping) | `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx` — **`AST-532 per-hop execution history UI`** describe |

**AST-531** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst531RunNextHopLedger \
  tests/component/core/test_dispatcher.py::TestDispatchOne::test_run_next_chain_skips_dispatch_level_ledger
```

**AST-532** narrowed run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx \
  -t "AST-532 per-hop"
```

Dispatch-only Execution History regression when parent UAT runs full epic: full **`test_AdminPerformanceMonitor.test.tsx`** per **§7.13k**.

---

### AST-549 · AST-550 · AST-484

**AST-484 (parent):** Admin dispatch and job/company UI vocabulary must track live config — no parallel seed dicts or hardcoded frontend manifest. **AST-549** removes **`_DISPATCH_TASK_SEED`**, **`dispatch_task_seed_templates()`**, and **`_DISPATCH_TASK_TRIGGER_SEED`** / **`DISPATCH_TASK_SEED_KEYS`**. **`dispatch_task_admin_defaults(task_key)`** derives **`entity_type`**, **`trigger_state`**, **`sort_by`**, **`batch_call_mode`** from **`TASK_CONFIG`**, roster/inflow/board config blocks, and state registries; **`DISPATCH_SCHEDULABLE_TASK_KEYS`** bounds schedulable rows (artifact-only keys like **`anticipate_scan`** stay out). **`GET /api/admin/dispatch_tasks/task_keys`** is **TASK_CONFIG-first** with schedulable merge — seed cannot override config. **AST-550** deletes **`StateUiContext.EMPTY`** (duplicate of **`build_state_ui_manifest()`**); runtime vocabulary from **`GET /api/state_ui_manifest`** only; **`loadState`** loading/error guards on manifest consumers; legacy sections for row states absent from the current manifest.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-549** | Config defaults; scored-trigger scan without seed loop; admin **`task_keys`** + adhoc preview | `src/utils/config.py`, `src/data/database.py`, `src/ui/api/api_admin.py` | **`TestAst549DispatchAdminDefaults`**; **`TestAst471DispatchConfigHelpers`** (updated); **`TestAst505InflowDiscoveryConfig::test_inflow_discovery_dispatch_admin_defaults`**; **`TestAst506InflowResolveConfig::test_inflow_resolve_website_dispatch_admin_defaults`**; **`TestApiAdminBranchGaps::test_ast549_task_keys_config_derivation_authoritative`**; **`TestDispatchTasks::test_list_dispatch_tasks_and_keys`** |
| **AST-550** | API-only **`StateUiContext`**; legacy job sections; shared test fixture (not production seed) | `StateUiContext.tsx`, `lib/stateUiSections.ts`, `JobsInReview.tsx`, `JobsSkipped.tsx`, `JobsRecommended.tsx`, company pages + modals | **`tests/component/frontend/contexts/test_StateUiContext.test.tsx`** (loading → ready; error → null manifest); **`tests/component/frontend/pages/test_JobsInReview.test.tsx`** (legacy unmapped state section); **`tests/component/frontend/pages/test_JobsRecommended.test.tsx`** (§6c routed page regression); **`tests/component/frontend/fixtures/stateUiManifestFixture.ts`** + **`page-mocks.ts`** (`installBaseApiMocks` serves fixture) |

**AST-549** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst549DispatchAdminDefaults \
  tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_inflow_discovery_dispatch_admin_defaults \
  tests/component/utils/test_config.py::TestAst506InflowResolveConfig::test_inflow_resolve_website_dispatch_admin_defaults \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast549_task_keys_config_derivation_authoritative \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast485_dispatch_task_keys_roster_seeds_minus_locate_template \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast485_adhoc_entities_select_job_page_fallbacks_to_config_defaults \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_dispatch_task_keys_includes_task_config_registry \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_list_dispatch_tasks_and_keys
```

**AST-550** narrowed run (Vitest paths are **not** forwarded by `run_component_tests.sh` trailing args — run Vitest explicitly):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/contexts/test_StateUiContext.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsInReview.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx \
  ../../../tests/component/frontend/test_App.test.tsx
```

---

### AST-539

Estelle-led intake: **`candidate_intake_session`** store (resume-after-close), REST under **`/api/candidates/<id>/intake/…`**, three **`do_task`** keys with ledger prefix **`intake-{task_key}`**, interview JSON validation, one **`build_request`** per session, build persistence via **`save_candidate_data`** + **`sync_company_search_terms_from_text`** + **`check_context_complete`**. Katherine modal UI (**AST-559**) consumes Ada's API (**AST-558**) — UI mocks must match **`IntakeSessionDto`** (`session_id`, `transcript[].text`, `can_build`, `build_completed`).

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-558** | Session CRUD + turns + build; source material persistence; ledger parity | `src/utils/config.py` (`INTAKE_CONFIG`, three `TASK_CONFIG` rows), `src/data/database.py`, `src/core/intake.py`, `src/core/agent.py` (snapshot hook), `src/ui/api/api_intake.py`, `src/ui/server.py` | `tests/component/core/test_intake.py`; `tests/component/ui/api/test_api_intake.py` |
| **AST-559** | Intake nav confirm gate; auto-start from persisted `context.*` (no modal paste / Start interview); thread, `can_build` gate, one build per session, resume-after-close | `src/utils/config.py` (`NAV_CONFIG`), `src/ui/frontend/src/routes.tsx`, `src/ui/frontend/src/pages/CandidateIntake.tsx`, `src/ui/frontend/src/components/IntakeChatModal.tsx`, `src/ui/frontend/src/App.css` | `tests/component/frontend/pages/test_CandidateIntake.test.tsx` (§6c routed page — confirm gate; modal — auto-start, gate, build-once) |
| **AST-578** | UAT: hide `initiate_candidate` user payload; hold copy while loading / when active session lacks visible assistant message | `src/ui/frontend/src/components/IntakeChatModal.tsx` | `tests/component/frontend/pages/test_CandidateIntake.test.tsx` — `IntakeChatModal` describe: transcript filter, hold on empty / assistant-less resume |
| **AST-579** | UAT: force `ready_to_build` false on initiate turn (never enable Generate Profile on turn 1) | `src/core/intake.py` (`create_intake_session_and_start`) | `tests/component/core/test_intake.py` — `test_initiate_turn_forces_ready_to_build_false_when_model_returns_true` |

**AST-558** narrowed run (pytest-only — harness skips Vitest when trailing paths are set):

```bash
./scripts/testing/run_component_tests.sh tests/component/core/test_intake.py
./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_intake.py
```

Equivalent direct gate:

```bash
.venv/bin/python -m pytest tests/component/core/test_intake.py tests/component/ui/api/test_api_intake.py -q
```

**AST-559** narrowed run (merge **`origin/sub/AST-539/AST-558-intake-session-api`** on engineer tree before replay if API symbols missing):

```bash
cd src/ui/frontend && npx tsc -b --noEmit
cd src/ui/frontend && npm run test:component -- --run tests/component/frontend/pages/test_CandidateIntake.test.tsx
```

**AST-578** narrowed run (Vitest — transcript filter + hold regressions only; merge this **`sub/*`** tip on engineer tree):

```bash
cd src/ui/frontend && npx tsc -b --noEmit
cd src/ui/frontend && npm run test:component -- --run tests/component/frontend/pages/test_CandidateIntake.test.tsx
```

**AST-579** narrowed run (pytest-only — initiate turn readiness gate; merge this **`sub/*`** tip on engineer tree):

```bash
.venv/bin/python -m pytest tests/component/core/test_intake.py::TestIntakeSessionFlow::test_initiate_turn_forces_ready_to_build_false_when_model_returns_true -q
```

**`[qa-handoff]` return (2026-06-03):** **AST-559** mocks updated for AST-558 REST paths (`/intake/sessions`, `/sessions/active`, `…/turns`, `…/build`); materials sent in session **POST** body (no **`PUT …/data`** on start).

**UAT UX delta (2026-06-05):** Page **Start Intake** confirm before modal; **`IntakeChatModal`** receives persisted **`materials`** + **`autoStart`** — no in-modal paste or **Start interview**; session **POST** fires after active **GET** when no session. **AST-578:** hide synthetic **`initiate_candidate`** user row; show **`INTAKE_HOLD_COPY`** until a visible assistant bubble exists.

**Rollup reconcile (AST-578):** Betty publish ref **`origin/sub/AST-539/AST-578-uat-intake-hold-on-resume-estelle-first-transcript-empty`** — one **§7.13zr** table row; **`rollup-child`** merges into **`origin/ftr/ast-539-candidate-intake-chat-session`**.

**Rollup reconcile (AST-579):** Betty publish ref **`origin/sub/AST-539/AST-579-uat-force-ready-to-build-false-on-initiate-candidate-turn`** — one **§7.13zr** table row; **`rollup-child`** merges into **`origin/ftr/ast-539-candidate-intake-chat-session`**. **Stale sub reconcile (2026-06-05):** bible base from **`origin/ftr/ast-539-candidate-intake-chat-session`** **AST-578** rows; kept **AST-579** manifest rows only.

---

### AST-555 · AST-538

**`NAV_CONFIG`** Admin item and **`AdminAnthropicAdHoc`** page **`<h1>`** show **Agent Ad Hoc** (path unchanged **`/admin/anthropic_ad_hoc`**). No API route or component rename.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-555** | Sidebar + page title label rename | `src/utils/config.py` (`NAV_CONFIG`), `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` | `tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_nav_config_admin_agent_ad_hoc_label`; `tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx` (**§6c** routed page) |

**AST-555** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_nav_config_admin_agent_ad_hoc_label
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx
```

---

### AST-519 · AST-616 · AST-601

Restores **AST-519** per-candidate **Base Resume Content** behavior lost in git merges: **`GET …/resume_structure`**, structure-driven tabs (not global shapes), **`base_resume`** orphan strip on PUT, accent on **`artifacts.resume_structure.accent_color`**. Core helpers and **`ArtifactEditor`** structure mode already on **`origin/dev`** / **AST-517** lineage. **Betty** updates **`test_ArtifactsBaseResumeContent.test.tsx`** to mock structure GET + assert accent PUT path (**§6c** routed page).

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-616** | API GET route + imports; Base Resume Content wired to structure sections + accent | `src/ui/api/api_candidate.py`, `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` | **§7.13zl** **AST-519** narrowed run (reuse **`TestAst519ResumeStructureApi`**, **`TestAst519ResumeStructureUiHelpers`**, **`test_ArtifactEditor.test.tsx`** structureSections rows); **`tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx`** (structure GET, orphan hidden, accent PUT, candidate switch) |

**AST-616** narrowed run:

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

### AST-631 · AST-574

**AST-574 (parent):** Agent `content` resolves registry tokens when used as the direct system block or when injected behind task `system_prompt` **`{$SELECTED_AGENT}`** — same `resolve_tokens` call context as task segments. **AST-632** (Katherine) covers Manage Agents autocomplete + preview UI only.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-631** | `resolved_agent_content`; `_chain_context` puts resolved body in `SELECTED_AGENT`; `do_task` / `preview_prompt` / admin enrich use shared path | `src/core/agent.py`, `src/ui/api/api_admin.py` | `tests/component/core/test_agent.py::TestAst631AgentContentTokens`; `tests/component/core/test_agent.py::TestChainContext::test_merges_extra_chain_tokens`; `tests/component/core/test_candidate.py::TestPreviewTaskPrompt::test_preview_resolves_agent_body_when_system_is_selected_agent`; full **`tests/component/core/test_agent.py`** (**`LOCKED_AT_100`**) |
| **AST-632** | `get_manage_agents_tokens`; `GET /agents/meta/tokens`; `POST /agents/preview`; Manage Agents `TokenTextarea` + resolved preview (literal save) | `src/utils/config.py`, `src/ui/api/api_admin.py`, `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` | `tests/component/utils/test_config.py::TestGetManageAgentsTokens`; `tests/component/ui/api/test_api_admin.py::TestAdminConfigAndAgents::test_ast632_manage_agents_token_meta_and_preview`; `tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx` (**`AST-632`** routed page + preview) |
| **AST-636** | UAT fix: portaled `TokenTextarea` menu (modal clipping); `useAgentTokenList` ignores non-OK `/agents/meta/tokens` | `src/ui/frontend/src/components/TokenTextarea.tsx`, `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` | `tests/component/frontend/components/test_TokenTextarea.test.tsx` (**`AST-636`** portal); `tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx` (**`AST-636`** edit-modal autocomplete + non-OK meta) |

**AST-631** narrowed run:

```bash
.venv/bin/python -m pytest \
  tests/component/core/test_agent.py::TestAst631AgentContentTokens \
  tests/component/core/test_agent.py::TestChainContext::test_merges_extra_chain_tokens \
  tests/component/core/test_candidate.py::TestPreviewTaskPrompt::test_preview_resolves_agent_body_when_system_is_selected_agent \
  -q
```

**AST-632** narrowed run:

```bash
.venv/bin/python -m pytest \
  tests/component/utils/test_config.py::TestGetManageAgentsTokens \
  tests/component/ui/api/test_api_admin.py::TestAdminConfigAndAgents::test_ast632_manage_agents_token_meta_and_preview \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx
```

**AST-636** narrowed run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_TokenTextarea.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx
```

---

### AST-634 · AST-628

**AST-628 (parent):** Shared **`AdminCandidateFilterControl`** + **`useAdminCandidateFilter`** on Scheduled Actions (client-side row filter), Execution History (URL-backed ledger scope), and Agent Timesheets (URL-backed list + export). Default tracks left-nav until Susan picks manually; **All** shows cross-candidate rows; Execution History dropdown lists global **`/api/candidates`** even when ledger rows omit a candidate.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-634** | Hook + label helpers; three routed admin pages | `src/ui/frontend/src/hooks/useAdminCandidateFilter.ts`, `src/ui/frontend/src/components/AdminCandidateFilterControl.tsx`, `src/ui/frontend/src/lib/candidateLabel.ts`, `AdminScheduledActions.tsx`, `AdminPerformanceMonitor.tsx`, `AdminAgentTimesheets.tsx` | `tests/component/frontend/hooks/test_useAdminCandidateFilter.test.tsx`; `tests/component/frontend/lib/test_candidateLabel.test.ts`; **`AST-634`** describe in `test_AdminScheduledActions.test.tsx`, `test_AdminPerformanceMonitor.test.tsx`, `test_AdminAgentTimesheets.test.tsx` |

**RTL note (Execution History):** page tests seed **`candidate_id`** on the initial route when **`urlPresentDisablesSync`** applies — bare mount without URL param can hang on nav-sync effects.

**AST-634** narrowed run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/hooks/test_useAdminCandidateFilter.test.tsx \
  ../../../tests/component/frontend/lib/test_candidateLabel.test.ts \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminAgentTimesheets.test.tsx \
  -t "AST-634|useAdminCandidateFilter|candidateLabel"
```

**Regression guard:** full **`test_AdminPerformanceMonitor.test.tsx`** after **`merge-tests(AST-634)`** — existing cases use **`renderPerformanceMonitor()`** helper (adds **`candidate_id=c1`** when absent).

---

### AST-672 · AST-670

**AST-670 (parent):** Left-align the **Copy logs to clipboard** control in the Execution History expanded batch log toolbar (`.dispatch-log-toolbar` **`justify-content: flex-start`**). Copy payload, **Copied** feedback, and all other Execution History behavior unchanged.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-672** | Log toolbar copy control left-aligned (CSS only) | `src/ui/frontend/src/App.css` (`.dispatch-log-toolbar`) | **`tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx`** — **`loads ledger rows, filters, expands logs, and opens batch modal`**: import **`App.css`**; assert toolbar **`justify-content`** is **`flex-start`** after expand; clipboard copy regression |

**AST-672** narrowed run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx \
  -t "loads ledger rows"
```

**Regression guard:** full **`test_AdminPerformanceMonitor.test.tsx`** when parent UAT runs full epic.

---

### AST-677 · AST-655

**AST-677 (child):** Company Watch Criteria Artifacts page **`taskKey`** rename only — **`craft_company_prefilter`** → **`craft_prefilter_rubric`**. Stored artifact **`company_prefilter`** unchanged. Backend **`TASK_CONFIG`** + schema validation covered by **AST-676**; admin prompt bodies: Susan pastes approved explainer via Manage Tasks (**AST-685** reverts auto-migration; see sibling UAT explainer-text bug).

| AC | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1 | **Generate** / **Regenerate** POST **`/api/candidates/{id}/generate/craft_prefilter_rubric`** via **`ArtifactEditor`** | `src/ui/frontend/src/pages/ArtifactsCompanyWatchCriteria.tsx` | **`tests/component/frontend/pages/test_ArtifactsCompanyWatchCriteria.test.tsx`** — routed page render (**§6c**); **`AST-677: Generate POSTs craft_prefilter_rubric`** |
| — | Backend task key + rubric **`importance`** schema (regression) | `src/utils/config.py`, `src/core/agent.py` | **`TestAst676CraftRubricSchema`** (`test_config.py`); **`TestResponseSchemaBranches::test_ast676_*`** (`test_agent.py`) |

**AST-677** narrowed run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_ArtifactsCompanyWatchCriteria.test.tsx
```

---

### AST-659 · AST-639

**AST-639 (parent epic):** Replace production **`window.confirm`** in admin pages with shared **`useUserConfirm`** / **`UserPromptProvider`** (app-wide via **`renderWithProviders`**). Documented fallbacks remain only in **`UserPrompt.tsx`** and **`Modal.tsx`** when no provider is present.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-659** | Data Management upsert apply; Manage Candidates logical delete + clear API key → themed **`alertdialog`** (confirm/cancel) | `src/ui/frontend/src/pages/AdminDataManagement.tsx`, `AdminManageCandidates.tsx` | **`tests/component/frontend/pages/test_AdminDataManagement.test.tsx`** — **`alertdialog`** **"Apply upsert"** → **Apply** on upsert success + API **`ok:false`** paths (**§6c** routed page); **`tests/component/frontend/pages/test_AdminManageCandidates.test.tsx`** — **"Clear API key"** / **"Delete candidate"** confirm paths; **AC5 regression:** **`tests/component/frontend/pages/test_CandidateIntake.test.tsx`** (existing **`useUserConfirm`** — unchanged) |

**AST-659** narrowed run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminDataManagement.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminManageCandidates.test.tsx \
  ../../../tests/component/frontend/pages/test_CandidateIntake.test.tsx
```

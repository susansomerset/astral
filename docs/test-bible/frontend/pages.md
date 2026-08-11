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

Parent **AST-514** labels non-dispatch UI provider calls in **`dispatch_ledger`**. **AST-515**: Ad Hoc workbench **Test** → **`adhoc-<workbench_task_key>`**. **AST-521**: Artifacts **Generate / Regenerate** → **`user-<task_key>`** with prefixed **`batch_id`**; **`do_task`** still uses the real craft key for **`agent_data`**. Board search craft generate removed with boards module (**AST-765**). **Preview** paths stay ledger-free. **Dispatch** / Scheduled Actions **Run** keep plain **`task_key`**. Execution History UI (**`AdminPerformanceMonitor`**) unchanged — list/expand/inspect use existing ledger + **`/api/agent_data/<batch_id>`** APIs.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-515** | Ledger + agent_data wrapper; **`adhoc_test`** route swap | `src/core/agent.py` (`run_adhoc_workbench_test`), `src/ui/api/api_admin.py` (`adhoc_test`) | `tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger`; `tests/component/ui/api/test_api_admin.py::{TestAdhocRoutes,TestApiAdminBranchGaps}` (adhoc preview/test paths) |
| **AST-521** | **`user-`** ledger prefix on candidate artifact generate (historical: board search craft removed **AST-765**) | `src/core/candidate.py` (`run_candidate_artifact_generation`), `src/ui/api/api_candidate.py` | `tests/component/core/test_candidate.py::TestRunCandidateArtifactGeneration` |

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
  tests/component/core/test_candidate.py::TestRunCandidateArtifactGeneration
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
| **AST-531** | Per-hop ledger rows; dispatch-level ledger skipped when chain planned | `src/core/agent.py`, `src/core/dispatcher.py`, `src/core/candidate.py` | `tests/component/core/test_agent.py::TestAst531RunNextHopLedger`; `tests/component/core/test_dispatcher.py::TestDispatchOne::test_run_next_chain_skips_dispatch_level_ledger` |
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

### AST-709 · AST-705

**AST-705 (parent):** Nav menu stops working while on Agent Timesheets — sidebar clicks flicker then snap back to `/admin/agent_timesheets`. Root cause: inline **`urlBacked`** object on **`AdminAgentTimesheets`** plus unstable **`applyFilter`** deps on whole **`urlBacked`** in shared hook (AST-662 fixed Execution History only).

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-709** | Stabilize **`applyFilter`** via **`urlSetValue`** dep; memoize **`urlBacked`** on Agent Timesheets (AST-662 parity) | `useAdminCandidateFilter.ts`, `AdminAgentTimesheets.tsx` | **`AST-709 nav and candidate filter`** describe in **`test_AdminAgentTimesheets.test.tsx`**; **`inline urlBacked identity churn does not spam setValue from nav sync`** in **`test_useAdminCandidateFilter.test.tsx`**; regression **`AST-634 admin candidate filter`** describe in same page file |

**AST-709** narrowed run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/hooks/test_useAdminCandidateFilter.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminAgentTimesheets.test.tsx \
  -t "AST-709|inline urlBacked|AST-634 admin candidate filter"
```

**Regression guard:** full **`test_useAdminCandidateFilter.test.tsx`** when sibling URL-backed admin pages change shared hook.

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

### AST-840 · AST-838

**AST-838 (parent):** Susan triages failed dispatch runs from Execution History (`/admin/performance`); verbose INFO lines bury ERROR/WARNING rows. **AST-840**: URL-persisted **Level** filter (`log_level` param) in the filter bar; client-side filtering on expanded log viewer and **Copy** only — ledger fetch and `/api/admin/dispatch_ledger` query params unchanged.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-840** | **Level** dropdown (All/DEBUG/INFO/WARNING/ERROR); `log_level` URL param; `LogViewer` `visibleLogs` filter; filtered-empty message; filtered **Copy** | `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` | **`tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx`** — **`AST-840 log level filter`** describe |

**AST-840** narrowed run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx \
  -t "AST-840 log level filter"
```

**Regression guard:** full **`test_AdminPerformanceMonitor.test.tsx`** — default **All** preserves **AST-532**, **AST-634**, and copy-toolbar describes.

### AST-980 · AST-976

**AST-976 (parent):** Add level **DEBUG** to `app_log` / Execution History. **AST-980** owns the Execution History Level-list UI portion of parent AC4. Build was **confirm-only / no-op product delta** — AST-840 already ships `LOG_LEVELS` including **DEBUG**, URL `log_level`, generic `visibleLogs` filter/Copy/empty-state, and `.dispatch-log-level-debug`. Persistence of real DEBUG rows is **AST-979**.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-980** | Confirm DEBUG on Level list + client filter (no product delta) | `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx`, `App.css` (unchanged this ticket) | **Existing** **`AST-840 log level filter`** describe in **`test_AdminPerformanceMonitor.test.tsx`** (dropdown includes DEBUG; filter/Copy/empty-state generic) — **no new tests** |

**AST-980** narrowed run (same gate as AST-840):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx \
  -t "AST-840 log level filter"
```

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

### AST-1253 · AST-1243

**Parent:** [AST-1243](https://linear.app/astralcareermatch/issue/AST-1243/candidate-artifacts-now-daisy-chain). **Publish:** `origin/sub/AST-1243/AST-1253-generate-regenerate-handoff`.

Company Search Terms + Company Watch Criteria (via shared **`ArtifactEditor`**) hand off Generate/Regenerate to **`POST …/generate_artifacts`**. Primary component: **`docs/test-bible/frontend/components.md`** § AST-1253.

| Area | Source | Component tests |
| --- | --- | --- |
| Search Terms Generate / Regenerate handoff | `ArtifactsCompanySearchTerms.tsx` | **`test_ArtifactsCompanySearchTerms.test.tsx`** — **`AST-1253:*`** (+ revised **AST-645** in-flight) |
| Watch Criteria Regenerate Yes → handoff | `ArtifactsCompanyWatchCriteria.tsx` → `ArtifactEditor` | **`test_ArtifactsCompanyWatchCriteria.test.tsx`** — **`AST-1253: Regenerate Yes POSTs generate_artifacts`** (replaces AST-677 craft POST) |

**Broken / obsolete:** AST-677 craft_prefilter_rubric ad-hoc generate assert; Search Terms populate-textarea-from-craft generate.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx \
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

---

### AST-725 · AST-378

Admin **Vector Feedback** page — per-vector summary (active rubric) + detail row list; batch link opens **`BatchAgentDataModal`** with **FEEDBACK** tab support.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page summary + detail + filters | `src/ui/frontend/src/pages/AdminVectorFeedback.tsx` | `tests/component/frontend/pages/test_AdminVectorFeedback.test.tsx` |
| FEEDBACK block tab in batch modal | `src/ui/frontend/src/components/BatchAgentDataModal.tsx` | `tests/component/frontend/components/test_BatchAgentDataModal.test.tsx` (FEEDBACK tab case) |

**AST-725** narrowed Vitest run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminVectorFeedback.test.tsx \
  ../../../tests/component/frontend/components/test_BatchAgentDataModal.test.tsx
```

API manifest: **`docs/test-bible/ui/api/api_admin.md`** (**AST-725**).

### AST-739 · AST-734

Manage Tasks + Scheduled Actions React screens consume DB grouping metadata (`task_group_order`, `task_group_name`, `task_seq`, `task_name`) from `_enrich_tasks` / `GET /api/admin/dispatch_tasks/task_keys` — no `TASK_CONFIG` `phase`/`seq` on these surfaces. Manage Tasks edit modal exposes four grouping inputs; list drops visible seq column; row Task cell shows `task_name` fallback `task_key`.

| Area | Source | Component tests |
| --- | --- | --- |
| Manage Tasks routed page (**§6c**) | `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx` (**`AST-739`** describe + revised fixtures) |
| Scheduled Actions routed page (**§6c**) | `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` (**`AST-739`** + revised `task_keys` mocks) |
| `dispatch_task_keys` API | `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py::TestAst739DispatchTaskKeysGrouping`; revised **`test_ast549_task_keys_config_derivation_authoritative`** |

**AST-739** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst739DispatchTaskKeysGrouping \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast549_task_keys_config_derivation_authoritative \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx
```

**Prerequisite:** **AST-738** data/API grouping on publish tip (sibling `merge-tests`).

### AST-749 · AST-736

Scheduled Actions: `grade_do` dispatch row buckets under **`task_keys.grade_do.task_group_name`** (e.g. **D. Job Analysis**) — not **`(unassigned)`** when grouping metadata is present on the direct dispatch key (no consult alias).

| Area | Source | Component tests |
| --- | --- | --- |
| Scheduled Actions routed page (**§6c**) | `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — **`AST-749: grade_do row groups under task_keys metadata not (unassigned)`** |

**AST-749** narrowed Vitest:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-749"
```

API retirement filter: **`docs/test-bible/ui/api/api_admin.md`** (**AST-749**).

### AST-746 · AST-744

Susan UAT: visible gap between **Candidate** / **Task** and **Entity** overlapping **State** on Scheduled Actions phase tables. Root cause: `useListTableColumnMeasure` ran while `CollapsiblePanel` body was `hidden` (`offsetWidth === 0` → 120px `stickyLeftPx` fallback). Fix mounts `ScheduledPhaseTable` only when section expanded; locks frozen column widths; defers sticky `left` until predecessor columns measure.

| Area | Source | Component tests |
| --- | --- | --- |
| Scheduled Actions routed page (**§6c**) | `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — **`AST-746: phase table mounts on expand; measured sticky left avoids 120px fallback gap`**; re-run **`AST-647: phase table freezes first three data columns`** |

**AST-746** narrowed Vitest run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-746|AST-647"
```

**Manual UAT (Susan):** Scheduled Actions with multiple phase sections — expand each; confirm no gap between Candidate/Task, Entity does not cover State, horizontal scroll keeps three frozen columns aligned.

**Pass criterion:** Vitest green on narrowed run (items above) + Susan manual multi-phase UAT.

**Builds on:** **AST-647**, **AST-652**, **AST-657** list-table layout manifests in **`docs/test-bible/frontend/components.md`**.

### AST-760 · AST-744

Susan UAT (post AST-758): **Entity** frozen `th` overlaying **State** header. AST-746 width/`minWidth` lock on frozen cells forced Entity sticky box over State (`z-index` 3 vs 2). Fix drops width lock — **left-only** sticky aligned with ListPage; keeps mount-on-expand + `predecessorsReady`.

| Area | Source | Component tests |
| --- | --- | --- |
| Scheduled Actions routed page (**§6c**) | `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — **`AST-760: frozen headers use left-only sticky; Entity does not width-lock over State`**; re-run **`AST-746`** + **`AST-647`** |

**AST-760** narrowed Vitest run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-760|AST-746|AST-647"
```

**Manual UAT (Susan):** local `dev`, `zsh launch.sh --flask` → Scheduled Actions → expand phase — Candidate, Task, Entity, State headers all visible/clickable; Entity must not cover State; no Candidate/Task gap; horizontal scroll frozen alignment holds.

**Builds on:** **AST-746** (mount-on-expand + measured `left`), **AST-758** (stale-dist delivery — unchanged).

### AST-751 · AST-735

Scheduled Actions: expanded client-side filter bar (Floor min/max, AUTO, Debug, Freq, Min count, Batch size, Run counts — AND intersection with Candidate/Task); section headers show `{groupName} ({autoOnCount} / {rows.length} AUTO)` on filtered rows; Candidate / Avail / Last Run rightmost; `formatAvailableCount` renders **—** for `0` or `null`; All-candidate default sort within section orders same `task_key` by `available_count` descending. No API change.

| Area | Source | Component tests |
| --- | --- | --- |
| Scheduled Actions routed page (**§6c**) | `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — **`AST-751 filters, AUTO summary, and All-candidate layout`** describe (7 cases); revised section-header expectations for **`groups rows…`**, **`AST-739`**, **`sorts columns…`** |

**AST-751** narrowed Vitest run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx
```

**Builds on:** **AST-634** (Candidate filter), **AST-739** (DB grouping sections), **AST-746** (phase table on expand).

**Note:** Score-floor **0.00** option + zero-save: **AST-1278** (restores prior **AST-750** UX). Catalog/API: **`docs/test-bible/utils/config.md`**, **`docs/test-bible/ui/api/api_admin.md`**.

### AST-768 · AST-572

Scheduled Actions: **Section/Group** filter control sourced from **`allTaskKeys`** catalog metadata (composite `${task_group_order}\u0000${task_group_name}` key); **`filteredRows`** AND intersection after Candidate, before Task; section panels and `{autoOn} / {total} AUTO` headers consume filtered rows. Client-side only — no API change.

| Area | Source | Component tests |
| --- | --- | --- |
| Scheduled Actions routed page (**§6c**) | `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — **`AST-768 section/group filter`** describe (6 cases) |

**AST-768** narrowed Vitest run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-768"
```

**Builds on:** **AST-751** (filter bar + AUTO summary), **AST-739** (DB grouping sections), **AST-634** (Candidate filter).

### AST-773 · AST-763

Scheduled Actions **Edit Task** exposes the **Task** `<select>` (same catalog as Add Task); **PUT** `/api/admin/dispatch_tasks/<id>` accepts `task_key` with entity-registry validation, derived `entity_type` / `sort_by` / `batch_call_mode`, AUTO guard (non-`auto_mode` fields blocked while AUTO on), and 409 UNIQUE message reflecting attempted triple. UI preserves **Input State** and **Score Floor** on task change (`taskKeyChangePatch`); AUTO rows cannot open edit (toast).

| Area | Source | Component tests |
| --- | --- | --- |
| PUT `task_key` validation + AUTO guard | `src/ui/api/api_admin.py`, `src/data/database.py` | `tests/component/ui/api/test_api_admin.py` — **`TestAst773UpdateDispatchTaskTaskKey`** (5 cases) |
| Scheduled Actions routed page (**§6c**) | `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — **`AST-773 edit modal task_key`** describe (5 cases) |

**AST-773** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst773UpdateDispatchTaskTaskKey \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-773"
```

**Builds on:** **AST-768** (Section/Group filter), **AST-751** (filter bar), **AST-739** (grouping sections), **AST-750** (score floor options on edit save).

### AST-804 · AST-799

Scheduled Actions edit modal uses **`candidate`** entries from **`GET /api/admin/dispatch_tasks/state_options`** for Input State when the row's **`entity_type`** is **`candidate`** (e.g. **`inflow_discovery`** → **LIVE_PROMPTS**). Normalizes non-array **`candidate`** payloads to `[]` alongside job/company.

| Area | Source | Component tests |
| --- | --- | --- |
| Scheduled Actions routed page (**§6c**) | `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — **`AST-804 candidate Input State options`** describe (1 case) |

Admin API validation: **`docs/test-bible/ui/api/api_admin.md`** (**AST-804**).

**AST-804** narrowed Vitest run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-804"
```

**Builds on:** **AST-773** (edit modal task_key), **AST-505** (**inflow_discovery** defaults).

### AST-785 · AST-754

UAT: Scheduled Actions looked empty when `dispatch_task` rows existed — collapsed default sections, misleading empty copy when filters hid rows, and brittle `available_count` enrichment could break the list. **AST-785** auto-opens the first section once on load, shows filter-aware empty text when `data.length > 0` but no section matches, and toasts on failed `GET /api/admin/dispatch_tasks`. API **`list_dtasks`** omits **`DISPATCH_RETIRED_TASK_KEYS`** (parity with **`task_keys`** AST-749) and logs enrichment failures with `available_count=0` instead of 500.

| Area | Source | Component tests |
| --- | --- | --- |
| Scheduled Actions routed page (**§6c**) | `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — **`AST-785 dispatch_tasks list UX`** describe (3 cases); revised **`groups rows…`**, **`AST-746`**, **`AST-768`** filter-empty copy |
| **`GET /api/admin/dispatch_tasks`** list robustness | `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py` — **`TestAst785ListDtasksRobustness`** (2 cases) |

**AST-785** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst785ListDtasksRobustness \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-785|groups rows into DB grouping|AST-746|AST-768 section"
```

**Builds on:** **AST-749** (retired-key filter on read paths), **AST-768** (Section/Group filter), **AST-739** (grouping sections), **AST-751** (filter bar).

### AST-780 · AST-761

Susan UAT: Scheduled Actions still used native **`alert()`** on four API failure paths (AUTO toggle, manual Run, edit save PUT, add save POST). **AST-780** replaces those with **`readApiError`** + **`errorToastFromApiError`** (same pattern as **AST-779** / Manage Agents) so server **`error`** text shows in the shared **`<Toast>`** and click-to-copy diagnostics attach on failure.

| Area | Source | Component tests |
| --- | --- | --- |
| Scheduled Actions routed page (**§6c**) | `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — **`AST-780 error toast replaces alert`** describe (3 cases: auto toggle + run, edit PUT, add POST); re-run **`AST-785 dispatch_tasks list UX`** load-failure toast |

**AST-780** narrowed run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-780|AST-785"
```

**Builds on:** **AST-779** (error toast diagnostics), **AST-785** (load-failure toast on same page).

### AST-887 · AST-885

Scheduled Actions: **Avail** filter control (`All` / `> 0`) on the existing client-side filter bar; when `gt0`, `filteredRows` keeps only `(available_count ?? 0) > 0` (excludes em-dash Avail: `0` or `null`). ANDs with Candidate / Section/Group / Task / Floor / AUTO / Debug / Freq / Min count / Batch size / Run counts. Empty sections omit via existing `filteredRows` bucketing; section AUTO summaries inherit. **Default engaged as `gt0` (AST-894)** — was All under AST-887 alone. No API / Available math / column-format change.

| Area | Source | Component tests |
| --- | --- | --- |
| Scheduled Actions routed page (**§6c**) | `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — **`AST-887 Avail > 0 filter`** describe (4 cases: default gt0 omits zero/null, hides + empty omit, AND with AUTO, clear restores); revised **`expandFirstPhaseSection`** + **AST-751** em-dash case for **AST-785**/**AST-894** landing expand |

**AST-887** narrowed Vitest run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-887|AST-751|AST-768"
```

**Builds on:** **AST-751** (filter bar + AUTO summary + em-dash Avail), **AST-768** (Section/Group AND intersection), **AST-785** (first-section auto-open → **AST-894** expand-all).

---

### AST-783 · AST-756

**Repo JSON divergence warning** on Manage Agents and Manage Tasks: each routed page mounts **`RepoJsonDivergenceBanner`** with `tableKey` **`agent`** / **`agent_task`**; banner refetches after successful save via `refreshToken` increment.

| Area | Source | Component tests |
| --- | --- | --- |
| Manage Agents routed page (**§6c**) | `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` | `tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx` — **`AST-783: shows agent repo JSON divergence banner on routed page`** |
| Manage Tasks routed page (**§6c**) | `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx` — **`AST-783: shows task repo JSON divergence banner on routed page`** |

**AST-783** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst783RepoAdminJsonDivergence \
  tests/component/ui/api/test_api_admin.py::TestAst783RepoJsonApi \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_RepoJsonDivergenceBanner.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx \
  -t "AST-783"
```

---

### AST-808 · AST-378 (UAT fix)

Assessment column + expandable criterion on **Admin Vector Feedback**; **FEEDBACK** batch modal hydrates compact **`vector_reviews`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Assessment column on page | `src/ui/frontend/src/pages/AdminVectorFeedback.tsx` | `test_AdminVectorFeedback.test.tsx` |
| Hydrated FEEDBACK table in modal | `src/ui/frontend/src/components/BatchAgentDataModal.tsx` | `test_BatchAgentDataModal.test.tsx` (AST-808 hydrated case) |
| Ledger `candidate_id` when prop omitted (AST-816) | `src/ui/frontend/src/components/BatchAgentDataModal.tsx` | `test_BatchAgentDataModal.test.tsx` (AST-816 ledger case) |

Vitest:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminVectorFeedback.test.tsx \
  ../../../tests/component/frontend/components/test_BatchAgentDataModal.test.tsx
```

### AST-816 · AST-378 (UAT fix)

**Performance Monitor** and **Vector Feedback** pass row **`candidate_id`** into **`BatchAgentDataModal`**; modal resolves **`candidate_id`** from ledger when prop absent so **`hydrate_reviews`** POST succeeds.

| Area | Source | Component tests |
| --- | --- | --- |
| Ledger-only hydrate (no prop) | `BatchAgentDataModal.tsx` | `test_BatchAgentDataModal.test.tsx` (AST-816) |

**AST-816** narrowed Vitest:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_BatchAgentDataModal.test.tsx
```


### AST-876 · AST-873

**Manage Candidates:** shape column **`dispatch_task_count`**; load **`GET /api/admin/dispatch_tasks/counts`**; merge onto rows; **Set dispatch tasks** confirm → **`POST /api/admin/dispatch_tasks/set_from_template`**; refresh counts; no run/stop. (§6c routed page.)

| # | Scenario | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1 | Count column + confirm set + toast + count refresh; no `/run` | `AdminManageCandidates.tsx` | **`test_AdminManageCandidates.test.tsx`** — shows count / sets from template |
| 2 | Cancel confirm → no POST | same | **`::does not POST set_from_template when confirm is cancelled`** |
| 3 | API error toast | same | **`::surfaces set_from_template API errors`** |
| 4 | Regression: existing Manage Candidates flows still green (counts mock) | same | full **`test_AdminManageCandidates.test.tsx`** file |

Config shape: **`docs/test-bible/utils/config.md`** (**AST-876**).

**Broken / obsolete (Betty revision):** existing **`test_AdminManageCandidates`** mocks — must stub **`/api/admin/dispatch_tasks/counts`** or first-paint throws unhandled api.

**AST-876** narrowed Vitest:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageCandidates.test.tsx
```

Plus config:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst876DispatchTaskCountShape \
  -q
```

**Pass criterion:** Vitest green on file + config pytest green — not zero-arg harness / branch-lock gate.

### AST-893 · AST-886

Optional Expand All policy on sectioned lists: **Expand One** default (Manage Tasks list, In Review, Skipped) vs **Expand All** opt-in (Scheduled Actions) with **Expand all** / **Collapse all** chrome. Hook + chrome maps: `docs/test-bible/frontend/hooks.md`, `docs/test-bible/frontend/components.md`.

| # | Scenario | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1 | Hook Expand One / Expand All policy (AC 1–5 at state layer) | `useSectionExpandPolicy.ts` | `test_useSectionExpandPolicy.test.tsx` |
| 2 | Chrome labels + callbacks | `SectionExpandChrome.tsx` | `test_SectionExpandChrome.test.tsx` |
| 3 | Manage Tasks list Expand One — second section closes first; no bulk chrome (§6c) | `AdminTaskPrompts.tsx` | `test_AdminTaskPrompts.test.tsx` — **`AST-893 Expand One on Manage Tasks list`** |
| 4 | In Review Expand One — second section closes first; no bulk chrome (§6c) | `JobsInReview.tsx` | `test_JobsInReview.test.tsx` — **`AST-893 Expand One default`** |
| 5 | Skipped Expand One — second section closes first; no bulk chrome (§6c) | `JobsSkipped.tsx` | `test_JobsSkipped.test.tsx` — **`AST-893 Expand One default`** |
| 6 | Scheduled Actions Expand All — bulk chrome, multi-open, Expand all / Collapse all (§6c) | `AdminScheduledActions.tsx` | `test_AdminScheduledActions.test.tsx` — **`AST-893 Expand All policy + bulk chrome`** |

**Broken / obsolete (Betty revision):** Scheduled Actions **`groups rows… allows zero expanded`** assumed Expand One `openSection` string survived temporary section absence during nav-candidate sync; Expand All stale-key cleanup drops those keys — test now re-expands via `expandFirstPhaseSection` after All-candidates. Jobs In Review / Skipped api mocks revised to `importOriginal` so AuthContext named exports resolve under full-file runs.

**Existing coverage kept:** full suite files above also re-run accordion / Scheduled Actions regressions.

**AST-893** narrowed Vitest:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/hooks/test_useSectionExpandPolicy.test.tsx \
  ../../../tests/component/frontend/components/test_SectionExpandChrome.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsInReview.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsSkipped.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-893|useSectionExpandPolicy|SectionExpandChrome"
```

**Pass criterion:** Vitest green on narrowed pattern (and engineer `test-child` may widen to full files if wiring side-effects appear).

### AST-894 · AST-888

Scheduled Actions landing defaults: Avail filter initial state `"gt0"`; one-shot `expandAllSections()` behind `didAutoOpenSectionRef` (replaces AST-785 first-section-only auto-open). Operator collapse after landing is not overwritten. Avail → All restores zero/empty Avail rows; empty-section omission follows the filtered set. Frontend-only; reuses AST-886/893 Expand All policy.

| # | Scenario | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1 | Default Avail `gt0` omits zero/null Avail (§6c) | `AdminScheduledActions.tsx` | **`AST-887 Avail > 0 filter`** — default gt0 + clear restores (revised); **`AST-894 default Avail > 0 and expand-all on landing`** — Avail All restores |
| 2 | Landing expand-all opens every matching section under default filters (§6c) | same | **`AST-894`** — landing expands every matching section |
| 3 | Once-gate: collapse after landing stays collapsed | same | **`AST-894`** — operator collapse not overwritten |
| 4 | Regression: Expand All chrome + Avail predicate still green | same | **`AST-893 Expand All policy + bulk chrome`**; full **`test_AdminScheduledActions.test.tsx`** |

**Broken / obsolete (Betty revision this pass):**
- **`AST-887`** “defaults Avail to All…” → rewritten for default `gt0`.
- Suites that expected zero/null Avail sections under prior All default (`groups rows…`, **AST-739**, **AST-751** em-dash / AUTO+Task, **AST-768** roster group, **AST-773** AUTO row, **AST-634** All-candidates roster, **AST-893** multi-section chrome) now call **`selectAvailAll()`** when they need those rows.

**AST-894** narrowed Vitest:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-894|AST-887|AST-893|AST-751|AST-768|AST-785"
```

**Pass criterion:** Vitest green on narrowed pattern; engineer may widen to full file.

---

### AST-948 · AST-858

**List entry regression only** — **`JobsRecommended.tsx`** unchanged this ticket. Row-click still opens JAR; Vitest updated for horizontal **Summary** / **Analysis** / **Artifacts** chrome (no `.side-tab-list`).

| Area | Source | Component tests |
| --- | --- | --- |
| Recommended list → JAR shell | `JobsRecommended.tsx` (untouched) + JAR shell | **`test_JobsRecommended.test.tsx`** — **`opens the report modal from a row click`** (AST-948 horizontal tabs) |

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx
```


### AST-1035 · AST-1019

**AST-1035 (UAT):** Admin **Session Resume Paste** — **View Parsed JSON** between Parse and Open HTML; read-only Modal shows the exact `lastParse` (`resume_structure` + `base_resume`) Open HTML POSTs; disabled when no successful parse; close does not clear `lastParse`. No new API. Parse/HTML contracts unchanged (**AST-987** / **AST-986**).

| Area | Source | Component tests |
| --- | --- | --- |
| View Parsed JSON button order + modal payload (§6c) | `AdminSessionResumePaste.tsx` | **`test_AdminSessionResumePaste.test.tsx`** — AST-1035 modal case + Parse/Open HTML regressions |

**Broken / obsolete this pass:** none — additive UI control; AST-987 page tests extended in place.

**Integration:** no existing scenario asserts Session Resume Paste JSON inspect — no revision; do not invent new integration coverage.

**AST-1035** narrowed run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminSessionResumePaste.test.tsx
```

---

### AST-987 · AST-985

**AST-987:** Admin **Session Resume Paste** page + session HTML — paste → AST-986 parse API; `useLocalStorage` retention (`session_resume:paste_text` / `session_resume:last_parse`); Open HTML via `POST /api/admin/session_resume/html` → blob URL tab. Builder `build_session_base_resume` emits print HTML from in-memory structure/content (**no** `get_candidate` / profile overlay). Failed parse/HTML never opens a tab. Sibling **AST-986** owns parse core/route. View Parsed JSON control = **AST-1035**.

| Area | Source | Component tests |
| --- | --- | --- |
| Session HTML builder (no bind) | `src/core/builder.py` **`build_session_base_resume`** | **`TestAst987BuildSessionBaseResume`** (`test_builder.py`) |
| Admin HTML POST | `src/ui/api/api_admin.py` **`session_resume_html`** | **`TestAst987SessionResumeHtmlApi`** (`test_api_admin.py`) |
| Admin paste page (§6c) | `AdminSessionResumePaste.tsx` + nav/route | **`test_AdminSessionResumePaste.test.tsx`** — render, parse success/fail, View Parsed JSON modal, Open HTML blob/error, localStorage restore |

**Broken / obsolete:** none — new surface; candidate-bound `/candidate/resume/base` and craft persist paths unchanged.

**AST-987** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst987BuildSessionBaseResume \
  tests/component/ui/api/test_api_admin.py::TestAst987SessionResumeHtmlApi \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminSessionResumePaste.test.tsx
```

---

### AST-1025 · AST-1023

**AST-1025:** Admin **Session Cover Letter** page (§6c) — field form mirroring `BUILD_CONFIG["session_cover_letter"]["fields"]`; `useLocalStorage` (`session_cover_letter:fields` / `session_cover_letter:last_render`); Open HTML → `POST /api/admin/session_cover_letter/html` (AST-1024) → blob URL tab; failed/empty HTML never opens a tab; optional `candidate_id` from selected candidate. Nav item after Session Resume Paste. Core emit = sibling **AST-1024**.

| Area | Source | Component tests |
| --- | --- | --- |
| Admin page render + Open HTML + localStorage (§6c) | `AdminSessionCoverLetter.tsx` + route | **`test_AdminSessionCoverLetter.test.tsx`** |
| Nav label/path order | `src/utils/config.py` `NAV_CONFIG` | **`TestAst1025SessionCoverLetterNav`** (`test_config.py`) |

**Broken / obsolete this pass:** none — additive Admin page; Session Resume Paste unchanged.

**Integration:** existing `tests/integration/scenarios/test_candidate_nav_api.py` asserts Jobs group gates only — no Admin item inventory; no revision; do not invent new integration coverage.

**AST-1025** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1025SessionCoverLetterNav \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminSessionCoverLetter.test.tsx
```

---

### AST-1139 · AST-1124

**Parent:** [AST-1124 — Cover Letter Header is incorrect](https://linear.app/astralcareermatch/issue/AST-1124/cover-letter-header-is-incorrect). **Publish:** `origin/sub/AST-1124/AST-1139-session-cover-letter-golden-parity`.

Admin **Session Cover Letter** (§6c): empty From block does not block Open HTML when a candidate is selected (server resolves via AST-1137); without a candidate, From block stays required; help copy documents empty-from-block defaults (fetch-failure intro fallback kept by **AST-1149**). Core emit: **`docs/test-bible/core/builder.md`**. Config: **`docs/test-bible/utils/config.md`**. Live authoring chrome = **AST-1149**.

| Area | Source | Component tests |
| --- | --- | --- |
| Empty from-block gating + fallback help + POST body (§6c) | `AdminSessionCoverLetter.tsx` | **`test_AdminSessionCoverLetter.test.tsx`** — **`AdminSessionCoverLetter — AST-1139`** describe |

**Broken / obsolete:** none — gating unchanged; config-driven intro = **AST-1149**.

**Integration:** none.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminSessionCoverLetter.test.tsx
```

---


### AST-1149 · AST-1145

**Parent:** [AST-1145 — Allow contact info tokens and | chars in fromBlock](https://linear.app/astralcareermatch/issue/AST-1145/allow-contact-info-tokens-and-or-chars-in-fromblock). **Publish:** `origin/sub/AST-1145/AST-1149-from-block-authoring-help-profile-session`.

Authoring help chrome (§6c): Candidate Profile **Cover Letter From** tab renders shapes `help` + `placeholder` (= default template); Admin Session Cover Letter loads `/api/ui_config` `cover_from_block` for intro / From help / placeholder. Config + ui_config: **`docs/test-bible/utils/config.md`**, **`docs/test-bible/ui/api/api_system.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Profile Cover Letter From tab (§6c) | `CandidateProfile.tsx` | **`test_CandidateProfile.test.tsx`** — **`CandidateProfile — AST-1149`** |
| Session config-driven help (§6c) | `AdminSessionCoverLetter.tsx` | **`test_AdminSessionCoverLetter.test.tsx`** — **`AdminSessionCoverLetter — AST-1149`** |
| Tab help rendering | `TabbedTextArea.tsx` | **`test_TabbedTextArea.test.tsx`** (help above textarea) |

**Broken / obsolete:** AST-1137 profile section placement (config) — revised; AST-1139 gating kept (fallback intro when ui_config empty).

**Integration:** none.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateProfile.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminSessionCoverLetter.test.tsx \
  ../../../tests/component/frontend/components/test_TabbedTextArea.test.tsx
```

---

### AST-1033 · AST-1031

**Parent:** [AST-1031 — Receive email on gmail account for astral](https://linear.app/astralcareermatch/issue/AST-1031/receive-email-on-gmail-account-for-astral). **Publish:** `origin/sub/AST-1031/AST-1033-read-email-admin-screen`.

Admin **Read email** page (§6c): first-paint list via `GET /api/admin/inbox/messages`; row click → wide `Modal` + body panel for `html_body` (**AST-1040** revised presentation to escaped `<pre>` raw source — was sandboxed iframe); empty subject → title `Message`; list/body errors inline (+ toast on list). API: **`docs/test-bible/ui/api/api_inbox.md`**. Nav: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page list + modal body (§6c) | `AdminReadEmail.tsx` + route | **`test_AdminReadEmail.test.tsx`** (modal body assertions revised by **AST-1040**) |
| Nav label/path order | `src/utils/config.py` `NAV_CONFIG` | **`TestAst1033ReadEmailNav`** (`test_config.py`) |
| Auth-gated list/get API | `src/ui/api/api_inbox.py` | **`TestAst1033InboxApi`** (`test_api_inbox.py`) |

**Broken / obsolete this pass:** none — additive Admin seed; AST-1032 Gmail/core coverage unchanged.

**Integration:** no existing scenarios inventory Admin Read email or `/api/admin/inbox/*` — none revised; do not invent new integration coverage.

**AST-1033** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_inbox.py \
  tests/component/utils/test_config.py::TestAst1033ReadEmailNav \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminReadEmail.test.tsx
```

---

### AST-1040 · AST-1031 (UAT)

**Parent:** [AST-1031 — Receive email on gmail account for astral](https://linear.app/astralcareermatch/issue/AST-1031/receive-email-on-gmail-account-for-astral). **Publish:** `origin/sub/AST-1031/AST-1040-uat-read-email-modal-raw-html`.

UAT: modal must show Gmail `html_body` as **escaped raw source** (`<pre class="email-html-source">`), not a rendered iframe/`srcDoc` preview. API/nav/list unchanged.

| Area | Source | Component tests |
| --- | --- | --- |
| Modal raw HTML source (revises AST-1033 iframe cases) | `AdminReadEmail.tsx` + `App.css` | **`test_AdminReadEmail.test.tsx`** — click → `<pre title="Email body">` text content; no `iframe` |

**Broken / obsolete this pass:** AST-1033 Vitest cases that asserted `sandbox` / `srcdoc` on iframe — revised in place.

**Integration:** none touched.

**AST-1040** narrowed run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminReadEmail.test.tsx
```

---

### AST-1014 · AST-952

Candidate Profile + Admin Manage Candidates edit columns + `contact` (no `profile.*`); §6c routed Profile page; middle skipped. Primary: **`docs/test-bible/core/candidate.md`** § AST-1014.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateProfile.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminManageCandidates.test.tsx
```


### AST-1048 · AST-1044

**Parent:** [AST-1044 — Bind email to candidate](https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate). **Publish:** `origin/sub/AST-1044/AST-1048-manage-email-match-indicator-create-control`.

Rename **Read email** → **Manage Email** (`AdminManageEmail.tsx`, route `/admin/manage_email`). List **Candidate** column + modal bind from AST-1047 `candidate_match`; **Create** enabled only when `candidate_match.matched` (stub click — AST-1049 wires meteorite). Unmatched browse (list + HTML modal) unchanged. Nav: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page rename + match column/modal + Create enablement (§6c) | `AdminManageEmail.tsx` + route + `App.css` | **`test_AdminManageEmail.test.tsx`** (replaces **`test_AdminReadEmail.test.tsx`**) |
| Nav label/path | `src/utils/config.py` | revised **`TestAst1033ReadEmailNav`** (`test_manage_email_follows_session_cover_letter`) |

**Broken / obsolete:** **`test_AdminReadEmail.test.tsx`** (page rename); **`TestAst1033ReadEmailNav.test_read_email_follows_session_cover_letter`** (`/admin/read_email` / "Read email") — revised in place.

**Integration:** no existing Admin Manage Email scenarios — no revision; do not invent new integration coverage.

**AST-1048** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1033ReadEmailNav \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageEmail.test.tsx
```


### AST-1049 · AST-1044

**Parent:** [AST-1044 — Bind email to candidate](https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate). **Publish:** `origin/sub/AST-1044/AST-1049-strip-extract-create-job-matched-email-meteorite`.

Manage Email **Create** wired `POST .../create-job` with success/error toast (historical). **Retired by AST-1142** (Land Meteorite). API route may remain: **`docs/test-bible/ui/api/api_inbox.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Create POST + toast (§6c page) | `AdminManageEmail.tsx` | historical — superseded by **AST-1142** Create retirement |

**Broken / obsolete:** Create POST cases — removed in **AST-1142** suite revision.

**Integration:** none.


### AST-1051 · AST-1044 (UAT)

**Parent:** [AST-1044 — Bind email to candidate](https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate). **Publish:** `origin/sub/AST-1044/AST-1051-uat-create-button-on-manage-email-list-rows`.

UAT (historical): **Create** on matched list-row **Actions** column. **AST-1142** retires Actions/Create entirely.

| Area | Source | Component tests |
| --- | --- | --- |
| List-row Create + no modal Create (§6c) | `AdminManageEmail.tsx` + `App.css` | historical — **AST-1142** asserts Create absent |

**Broken / obsolete:** Actions/Create column cases — superseded by **AST-1142**.

**Integration:** none.

---

### AST-1057 · AST-1052

**Parent:** [AST-1052 — Processing meteorites](https://linear.app/astralcareermatch/issue/AST-1052/processing-meteorites). **Publish:** `origin/sub/AST-1052/AST-1057-recommended-page-meteorites-section`.

Recommended list partitions jobs whose `company` starts with manifest `meteorite_section.company_prefix` into a prepended **Meteorites** section; vetted-company Recommended / In Progress / Ready unchanged. Config: **`docs/test-bible/utils/config.md`** (**AST-1057**). Fixture: **`stateUiManifestFixture.ts`** carries `meteorite_section`.

| Area | Source | Component tests |
| --- | --- | --- |
| Partition + prepend Meteorites | `JobsRecommended.tsx` + `StateUiContext` type | **`test_JobsRecommended.test.tsx`** — AST-1057 cases |

**Broken / obsolete:** none — additive partition; existing section/sort/Skip cases still hold without meteorite rows.

**Integration:** none.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx
```

### AST-1061 · AST-1058

**Parent:** [AST-1058 — Qualify Meteorite](https://linear.app/astralcareermatch/issue/AST-1058/qualify-meteorite). **Publish:** `origin/sub/AST-1058/AST-1061-gazer-email-meteorite-jobs-playwright-dedupe`.

Manage Email Create toasts used `created`/`skipped` arrays (historical). **AST-1142** retires Create; Land Meteorite shows server `outcome` strings instead.

| Area | Source | Component tests |
| --- | --- | --- |
| Multi-result toasts | `AdminManageEmail.tsx` | historical Create toasts — superseded by **AST-1142** results panel |

**Broken / obsolete:** Create multi-result toast cases — removed in **AST-1142**.

**Integration:** none.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageEmail.test.tsx
```

### AST-1142 · AST-1129

**Parent:** [AST-1129 — Manage Email — select inbox messages and Land Meteorite](https://linear.app/astralcareermatch/issue/AST-1129/manage-email-select-inbox-messages-and-land-meteorite). **Publish:** `origin/sub/AST-1129/AST-1142-manage-email-multi-select-land-meteorite-retire-create`. **Blocked by:** AST-1141.

Manage Email (§6c): row + header multi-select; toolbar Select all / Clear / **Land Meteorite** (enabled only when selection non-empty); `POST /api/admin/inbox/land-meteorite` with selected ids; on-page **Land Meteorite results** (subject snapshot + raw `outcome` + candidate id); retire per-row **Create** / Actions column / `.manage-email-create`. Never calls `/create-job`. API: **`docs/test-bible/ui/api/api_inbox.md`** (**AST-1141**). Core: **`docs/test-bible/core/gaze_email.md`** (**AST-1140**).

| Area | Source | Component tests |
| --- | --- | --- |
| Multi-select + enablement + Land POST + outcomes + Create retired (§6c) | `AdminManageEmail.tsx` + `App.css` | **`test_AdminManageEmail.test.tsx`** — **`AdminManageEmail — AST-1142`** (+ revised Create-absent cases in older describe) |

**Broken / obsolete (revised this pass):** AST-1049/1051/1061 list-row Create POST/toast cases; Actions column assertions.

**Integration:** none — no existing scenario asserts Manage Email Land Meteorite; do not invent new coverage.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageEmail.test.tsx
```

### AST-1064 · AST-1059

**Parent:** [AST-1059 — Issue with the rubric grade displays on the Jobs List pages](https://linear.app/astralcareermatch/issue/AST-1059/issue-with-the-rubric-grade-displays-on-the-jobs-list-pages). **Publish:** `origin/sub/AST-1059/AST-1064-group-by-aligned-rubric-jobs-list-tables`.

Skipped + In Review list tables group by job-carried rubric fingerprint; columns from `*_rubric` (grades fallback); Score from `{prefix}_score` then `latest_score`. Helpers: **`docs/test-bible/frontend/components.md`** (**AST-1064**). Hydration payload: sibling **AST-1063**.

| Area | Source | Component tests |
| --- | --- | --- |
| Group-by tables + phase score (Skipped) | `JobsSkipped.tsx` | **`test_JobsSkipped.test.tsx`** — **`AST-1064 group-by job-carried rubric`** |
| Group-by tables + phase score (In Review) | `JobsInReview.tsx` | **`test_JobsInReview.test.tsx`** — **`AST-1064 group-by job-carried rubric`** |
| Fingerprint / group / columns / score helpers | `lib/rubricDisplay.ts` | **`test_rubricDisplay.test.ts`** — **`AST-1064 job-carried list helpers`** |

**Broken / obsolete:** none — additive grouping; existing Expand One / resurrect / floor cases still green without `*_rubric`.

**Integration:** none revised.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_rubricDisplay.test.ts \
  ../../../tests/component/frontend/pages/test_JobsSkipped.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsInReview.test.tsx
```

---

### AST-1086 · AST-1078

**Parent:** [AST-1078 — Small bug: Headers for Job Lists](https://linear.app/astralcareermatch/issue/AST-1078/small-bug-headers-for-job-lists). **Publish:** `origin/sub/AST-1078/AST-1086-compact-vector-codes-grade-dot-tooltips`.

Skipped + In Review (§6c): grade `<th>` paints compact `headerCode` with full-name `title`; grade-dot hover includes rubric text + confidence parenthetical when confidence is 1–5. Helpers: **`docs/test-bible/frontend/lib.md`** (**AST-1086**).

| Area | Source | Component tests |
| --- | --- | --- |
| Compact header + grade-dot tooltip (Skipped) | `JobsSkipped.tsx` | **`test_JobsSkipped.test.tsx`** — **`AST-1086 compact headers and grade-dot tooltips`** |
| Compact header + grade-dot tooltip (In Review) | `JobsInReview.tsx` | **`test_JobsInReview.test.tsx`** — **`AST-1086 compact headers and grade-dot tooltips`** |
| Grades-only parse / tooltip helpers | `lib/rubricDisplay.ts` | **`test_rubricDisplay.test.ts`** — **`AST-1086 compact headers and grade-dot confidence tooltips`** |

**Broken / obsolete:** `test_rubricDisplay` grades-only `headerCode === "Technical (TE)"` — revised to compact `"TE"`.

**Integration:** none revised (UI display only; no existing scenario maps these headers).

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_rubricDisplay.test.ts \
  ../../../tests/component/frontend/pages/test_JobsSkipped.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsInReview.test.tsx
```

---

### AST-1067 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1067-manage-slack-admin-listen-switch`.

Admin **Manage Slack** page (§6c): first-paint listen state via `GET /api/admin/contact/listen`; toggle `PUT` enables/disables listen for this environment; non-prod copy notes `[<environment>]` reply prefix. API: **`docs/test-bible/ui/api/api_contact.md`**. Nav: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page render + toggle (§6c) | `AdminManageSlack.tsx` + route | **`test_AdminManageSlack.test.tsx`** |

**Broken / obsolete:** none — new Admin page.

**Integration:** no existing Manage Slack scenario — no revision; do not invent new integration coverage.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageSlack.test.tsx
```


### AST-1094 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1094-uat-manage-slack-estelle-activity-list`.

Admin **Manage Slack** (§6c): below listen controls, **@Estelle users** table from `GET /api/admin/contact/estelle_activity` — Slack user, bind ok/fail, candidate, message count, last channel/ts. Empty copy when no rows. API: **`docs/test-bible/ui/api/api_contact.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Activity table + empty state (§6c) | `AdminManageSlack.tsx` | revised **`test_AdminManageSlack.test.tsx`** (AST-1094 cases) |

**Broken / obsolete:** none — additive table on existing Manage Slack page; listen tests still require listen GET (activity GET mocked empty).

**Integration:** none.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageSlack.test.tsx
```


---

### AST-1075 · AST-953

**Parent:** [AST-953 — Topic Menu Generation](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation). **Publish:** `origin/sub/AST-953/AST-1075-estelle-preamble-confirm-and-topic-menu-generation`.

`CandidateIntake` (§6c): after mechanical preamble complete → **`topic_menu`** phase (`IntakeTopicMenuPanel`), not auto-open legacy Estelle chat. Active-session resume still opens chat. Panel: **`docs/test-bible/frontend/components.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page preamble → Topic Menu (§6c) | `CandidateIntake.tsx` | revised **`test_CandidateIntake.test.tsx`** — **`preamble Valid handoff opens Topic Menu confirm`** |
| Topic Menu panel | `IntakeTopicMenuPanel.tsx` | **`test_IntakeTopicMenuPanel.test.tsx`** |

**Broken / obsolete:** **`preamble Valid handoff opens Estelle chat`** — product now routes to Topic Menu confirm (AST-1075); revised in-place.

**Integration:** no existing intake Topic Menu scenario — no revision; do not invent new integration coverage.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateIntake.test.tsx \
  ../../../tests/component/frontend/components/test_IntakeTopicMenuPanel.test.tsx
```


---

### AST-1082 · AST-1065

**Parent:** [AST-1065 — Update candidate ui for contact info](https://linear.app/astralcareermatch/issue/AST-1065/update-candidate-ui-for-contact-info). **Publish:** `origin/sub/AST-1065/AST-1082-profile-contact-manage-nav`.

Candidate Profile (§6c): `editValuesFromCandidate` always includes top-level `full` and normalizes `contact.websites` to `string[]` on load/post-Save remap; PUT body has columns + `contact.*` (never `profile`); shapes labels GitHub/LinkedIn username-or-URL; Title Patterns tab stays on Profile. Nav/route hygiene: **`docs/test-bible/utils/config.md`**, **`test_routes.test.tsx`**. Shapes/`string_list`/empty-full coerce = **AST-1081**.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed Profile load/save `full` + websites (§6c) | `CandidateProfile.tsx` | **`test_CandidateProfile.test.tsx`** — **`CandidateProfile AST-1082 contact manage`** |
| Labels + Candidate NAV omit Title Patterns | `src/utils/config.py` | **`TestAst1082ProfileContactLabelsNav`** (map: **`docs/test-bible/utils/config.md`**) |
| Route absent | `routes.tsx` | existing **`test_routes.test.tsx`** (`candidate/title_patterns` false) |

**Broken / obsolete:** Profile GET mock omitted top-level `full` — revised in-place so load maps `c.full`. No product assertion breakage from AST-1014 Profile cases.

**Integration:** no existing Profile contact round-trip scenario — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1082ProfileContactLabelsNav \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateProfile.test.tsx \
  ../../../tests/component/frontend/test_routes.test.tsx
```


---

### AST-1092 · AST-1065 (UAT)

**Parent:** [AST-1065 — Update candidate ui for contact info](https://linear.app/astralcareermatch/issue/AST-1065/update-candidate-ui-for-contact-info). **Publish:** `origin/sub/AST-1065/AST-1092-uat-extra-binding-emails-labels`.

Candidate Profile (§6c): Resume/Messages labels; `extra_emails` normalize to `string[]` + Add round-trip. Config/core: **`docs/test-bible/utils/config.md`**, **`docs/test-bible/core/candidate.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed Profile labels + extra_emails (§6c) | `CandidateProfile.tsx` | **`test_CandidateProfile.test.tsx`** — **`CandidateProfile AST-1092 extra binding emails`**; revised AST-1082 websites Add scoped to Websites field |

**Broken / obsolete:** AST-1082 websites Add used global `getByRole('Add')` — revised to scope under Websites label (second `string_list`).

**Integration:** none — no revision; do not invent new integration coverage.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateProfile.test.tsx
```

### AST-1105 · AST-1043 (UAT)

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1105-uat-slack-username-display-activity-profile`.

Manage Slack activity table: **Username** + **Display** columns (`—` when null).

| Area | Source | Component tests |
| --- | --- | --- |
| Username/Display columns (§6c) | `AdminManageSlack.tsx` | revised **`test_AdminManageSlack.test.tsx`** |

**Broken / obsolete:** AST-1094 activity mock without identity — revised.

**Integration:** none.

```bash
cd src/ui/frontend && npm run test:component -- AdminManageSlack
```

---

### AST-1208 · AST-1203

**Parent:** [AST-1203 — Need to be able to set the "Debug" flag for Slack messages](https://linear.app/astralcareermatch/issue/AST-1203/need-to-be-able-to-set-the-debug-flag-for-slack-messages). **Publish:** `origin/sub/AST-1203/AST-1208-manage-slack-ui-debug-toggle`.

Admin **Manage Slack** (§6c): Debug On/Off beside Listen via `GET`/`PUT` `/api/admin/contact/debug` (`debug_enabled`). Debug load failure toasts + shows `—` / disables Debug button — does **not** set page `error` or hide Listen / @Estelle activity. API foundation: **`docs/test-bible/ui/api/api_contact.md`** (AST-1206).

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page Debug toggle + isolation (§6c) | `AdminManageSlack.tsx` | revised **`test_AdminManageSlack.test.tsx`** (AST-1208 cases + listen Off/On scoped) |

**Broken / obsolete:** AST-1067/1094/1105 cases that assumed only one `"Off"`/`"On"` and no `/debug` GET — revised: default mock includes debug GET; listen assertions scoped to Listen label / Enable listen button.

**Integration:** no existing Manage Slack debug scenario — no revision; do not invent new integration coverage.

```bash
cd src/ui/frontend && npm run test:component -- AdminManageSlack
```

### AST-1104 · AST-1102

**Parent:** [AST-1102 — Bug when select All candidates and All avail count](https://linear.app/astralcareermatch/issue/AST-1102/bug-when-select-all-candidates-and-all-avail-count). **Publish:** `origin/sub/AST-1102/AST-1104-fix-sa-blank-candidate-all-avail-all`.

Scheduled Actions blank-page survival (§6c): Candidate All + Avail All must keep title/filters/list mounted when nav-selected candidate `contact.timezone` is a non-IANA string — Last Run `<Time>` → `fmtTime` absorbs `RangeError` (UTC retry). Avail All still shows zero/empty Avail rows; default Avail `gt0` unchanged. Product fix is `fmt.ts` only (Branch A).

| # | Scenario | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1 | Candidate All + Avail All keeps chrome + zero-Avail Last Run (§6c) | `AdminScheduledActions.tsx` (untouched) + `fmt.ts` / `Time` | **`test_AdminScheduledActions_AST1104.test.tsx`** — **`AST-1104 Candidate All + Avail All blank-page survival`** (2 cases) |
| 2 | Invalid IANA zone → UTC fallback (lib) | `fmt.ts` | **`test_fmt.test.ts`** — falls back to UTC when timezone invalid |
| 3 | `<Time>` invalid `contact.timezone` → UTC | `Time.tsx` | **`test_Time.test.tsx`** — invalid timezone case; fixtures use `contact.timezone` |
| 4 | Regression: Avail default / Expand All / filters | same | **`test_AdminScheduledActions.test.tsx`** — **`AST-894\|AST-887\|AST-893\|AST-751\|AST-768\|AST-785`** |

**Broken / obsolete:** **`test_Time.test.tsx`** still mocked `candidate_data.profile.timezone` after contact-path product — revised to `contact.timezone`.

**Integration:** no existing SA blank-page / timezone scenario — no revision; do not invent new integration coverage.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions_AST1104.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  ../../../tests/component/frontend/lib/test_fmt.test.ts \
  ../../../tests/component/frontend/components/test_Time.test.tsx \
  --testNamePattern="AST-1104|AST-894|AST-887|AST-893|AST-751|AST-768|AST-785|fmtTime|Time"
```

### AST-1106 · AST-1087

**Parent:** [AST-1087](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task). **Publish:** `origin/sub/AST-1087/AST-1106-uat-gaze-email-missing-from-scheduled-actions-default-view`.

Scheduled Actions Avail **gt0** keeps rows where API `always_visible_under_avail_gt0` is true (mailbox shell with intentional zero avail); other zero-avail rows still omitted. Default remains `gt0` (AST-894). Candidate cell is null-safe (`candidate_id || "—"`) so shared mailbox rows do not crash. No React `"gaze_email"` set.

| # | Area | Source | Component tests |
| --- | --- | --- | --- |
| 1 | Routed page Avail gt0 carve-out (§6c) | `AdminScheduledActions.tsx` | **`test_AdminScheduledActions_AST1106.test.tsx`** — **`AST-1106 gaze_email always visible under Avail gt0`** (2 cases) |
| 2 | Regression: default gt0 still hides non-flag zero-avail | same | case 2 in that file; re-run **`AST-887`/`AST-894`** in **`test_AdminScheduledActions.test.tsx`** |

**Broken / obsolete:** none (predicate widened via API flag only).

**Integration:** none.

```bash
cd src/ui/frontend && npx vitest run \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions_AST1106.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-1106|AST-887|AST-894"
```

### AST-1156 · AST-1150

**Parent:** [AST-1150 — Technical fail for Do prompt](https://linear.app/astralcareermatch/issue/AST-1150/technical-fail-for-do-prompt). **Publish:** `origin/sub/AST-1150/AST-1156-skipped-retry-hop-correct-dispatchable-state`.

Skipped Retry groups selection by current `job.state`, looks up `bulk_retry_to_state_by_from_state`, and POSTs one `/api/jobs/bulk_state` per destination (meteorite Do fail → `METEORITE_PASSED_JD`; regular Get fail → `PASSED_DO`). Config map: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Hop-correct Retry grouping | `JobsSkipped.tsx`, `StateUiContext.tsx`, fixture | **`test_JobsSkipped.test.tsx`** — **AST-1156 hop-correct Skipped Retry**; revised fixture map; existing Retry toast row asserts `CULTURE_READY` |

**Broken / obsolete:** fixture `bulk_retry_to_state: "NEW"` → map; Retry no longer assumes universal NEW.

**Integration:** none.

```bash
cd src/ui/frontend && npx vitest run \
  ../../../tests/component/frontend/pages/test_JobsSkipped.test.tsx
```

### AST-1195 · AST-1188

**Parent:** [AST-1188 — Errors for qualify_meteorite dispatch task](https://linear.app/astralcareermatch/issue/AST-1188/errors-for-qualify-meteorite-dispatch-task). **Publish:** `origin/sub/AST-1188/AST-1195-schema-nulls-bot-blocked`.

Shared `stateUiManifestFixture.ts` skipped `section_order` + `bulk_retry_to_state_by_from_state`: `JD_SCRAPE_FAIL_BOT` → **`BOT_BLOCKED`** (aligned with config rename). Primary config/schema: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Fixture rename | `tests/component/frontend/fixtures/stateUiManifestFixture.ts` | Consumers via **`page-mocks.ts`** / StateUiContext (no new page cases) |

**Broken / obsolete:** fixture pinned old bot scrape-fail id — revised this pass.

**Integration:** none.

```bash
cd src/ui/frontend && npx vitest run \
  ../../../tests/component/frontend/contexts/test_StateUiContext.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsSkipped.test.tsx
```

---

### AST-1200 · AST-1198

**Parent:** [AST-1198 — Rubric criteria prompts are not appearing in UI Artifacts](https://linear.app/astralcareermatch/issue/AST-1198/rubric-criteria-prompts-are-not-appearing-in-ui-artifacts). **Publish:** `origin/sub/AST-1198/AST-1200-restore-rubric-criteria-prompts`.

Primary coverage is shared **`ArtifactEditor`** (**`docs/test-bible/frontend/components.md`**). Additive Job List Criteria page smoke for AC1 (prompt textarea visible without expand). No page-file product diff — §6c new-page rule N/A.

| Area | Source | Component tests |
| --- | --- | --- |
| Job List Criteria prompt visible on first paint | `ArtifactsJobListCriteria.tsx` → `ArtifactEditor` | **`test_ArtifactsJobListCriteria.test.tsx`** — **`AST-1200: criterion prompt textarea visible without expand click`** |

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_ArtifactsJobListCriteria.test.tsx \
  --testNamePattern="AST-1200"
```


### AST-1237 · AST-1173

**Parent:** [AST-1173 — Consent — install disclosure, affirmative opt-in, and off-switch](https://linear.app/astralcareermatch/issue/AST-1173/consent-install-disclosure-affirmative-opt-in-and-off-switch). **Publish:** `origin/sub/AST-1173/AST-1237-install-disclosure-and-affirmative-opt-in`.

Routed **`CandidateSurferConsent`** (`/candidate/surfer_consent`): GET DTO chrome; affirmative PUT `opt_in` with `accepted_version: dto.current_version`; **Not now** navigates `/jobs/recommended` with **no** PUT; `is_current` shows ok chrome without opt-out. Config: **`docs/test-bible/utils/config.md`**. Extension lib: **`docs/test-bible/extension/lib.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| §6c page — empty / disclosure / opt-in / decline / current-ok | `CandidateSurferConsent.tsx` | **`test_CandidateSurferConsent.test.tsx`** |

**Broken / obsolete:** none.

**Integration:** none revised; do not invent new integration coverage.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateSurferConsent.test.tsx
```


### AST-1238 · AST-1173

**Parent:** [AST-1173 — Consent — install disclosure, affirmative opt-in, and off-switch](https://linear.app/astralcareermatch/issue/AST-1173/consent-install-disclosure-affirmative-opt-in-and-off-switch). **Publish:** `origin/sub/AST-1173/AST-1238-off-switch-and-pre-consent-no-op`.

Routed **`CandidateSurfer`** (`/candidate/surfer`): GET status (on / stale / off); off-switch when `status === opted_in` via `useUserConfirm` then PUT `opt_out`; always shows `uninstall_guidance`; no disclosure/opt-in chrome. Config: **`docs/test-bible/utils/config.md`**. Extension gate: **`docs/test-bible/extension/lib.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| §6c page — empty / on+opt-out / stale / cancel / off | `CandidateSurfer.tsx` | **`test_CandidateSurfer.test.tsx`** |

**Broken / obsolete:** none.

**Integration:** none.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateSurfer.test.tsx
```

### AST-1215 · AST-1185

**Parent:** [AST-1185 — UI groupings/sequences + alphabetical task key/alias dropdowns](https://linear.app/astralcareermatch/issue/AST-1185/ui-groupingssequences-alphabetical-task-keyalias-dropdowns-data-driven). **Publish:** `origin/sub/AST-1185/AST-1215-admin-ui-grouping-honesty-alphabetical-dropdowns`.

Admin React honesty: Scheduled Actions / Manage Tasks keep section headers + within-section order from `agent_task` grouping metadata; in-scope task-key dropdowns (SA Add/Edit, Manage Tasks run_next, Agent Ad Hoc Task Key + Save As) use shared lexicographic `taskKeySort` (match AST-1214 / Python `sorted` — not `localeCompare`). Helper unit tests: **`docs/test-bible/frontend/lib.md`** (**AST-1215**). Vector Feedback / Jobs UI out of scope.

| Area | Source | Component tests |
| --- | --- | --- |
| Scheduled Actions §6c Add Task option order | `AdminScheduledActions.tsx` | **`test_AdminScheduledActions.test.tsx`** — **`AST-1215 alphabetical task_key dropdown`** |
| Manage Tasks §6c run_next option order | `AdminTaskPrompts.tsx` | **`test_AdminTaskPrompts.test.tsx`** — **`AST-1215 alphabetical run_next options`** |
| Agent Ad Hoc §6c Task Key + Save As | `AdminAnthropicAdHoc.tsx` | **`test_AdminAnthropicAdHoc.test.tsx`** — **`AST-1215`** (+ api mock `importOriginal` fix for AuthContext) |

**Broken / obsolete:** Ad Hoc `vi.mock(api)` without named auth exports — revised to `importOriginal` (AuthContext `setAuthTokenGetter` / `setUnauthorizedHandler`).

**Integration:** none revised.

```bash
cd src/ui/frontend && npx tsc -b --noEmit && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_taskKeySort.test.ts \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx
```

### AST-1278 · AST-1275

**Parent:** [AST-1275 — Remove pass_threshold from task_config](https://linear.app/astralcareermatch/issue/AST-1275/remove-pass-threshold-from-task-config). **Publish:** `origin/sub/AST-1275/AST-1278-admin-score-floor-dropdown-allows-0`.

Scheduled Actions Edit Dispatch Task: Score Floor options from **`GET /api/admin/dispatch_tasks/score_floor_options`** (config catalog; first **`0.00`**); save uses **`Number.isFinite`** so selecting **`0.00`** sends JSON **`score_floor: 0`**. Restores the **AST-750** zero-save case that was held out while product hardcoding mins at **1.00**. Catalog + admin GET + API zero-persist: **`docs/test-bible/utils/config.md`**, **`docs/test-bible/ui/api/api_admin.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Scheduled Actions routed page (**§6c**) | `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | **`test_AdminScheduledActions.test.tsx`** — **`AST-1278: edit save sends score_floor 0 when 0.00 selected`** |
| Catalog (existing) | `src/utils/config.py` | **`TestAst750DispatchScoreFloorCatalog`** |
| Admin GET + zero persist (existing) | `src/ui/api/api_admin.py` | **`TestDispatchTasks::test_scheduler_and_run_controls`** (floors); **`TestApiAdminBranchGaps::test_update_dispatch_task_scored_zero_score_floor`** |

**Broken / obsolete:** none — mocks already called `score_floor_options`; product regression was hardcoded React **1.00–10.00** plus falsy `parseFloat` coercion to **1**.

**Integration:** none revised (admin UI only).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst750DispatchScoreFloorCatalog \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_scheduler_and_run_controls \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_update_dispatch_task_scored_zero_score_floor \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  -t "AST-1278"
```

---

### AST-1288 · AST-1285

**Parent:** [AST-1285 — State transition validation for candidates is broken](https://linear.app/astralcareermatch/issue/AST-1285/state-transition-validation-for-candidates-is-broken). **Publish:** `origin/sub/AST-1285/AST-1288-manage-candidates-are-you-sure`.

Manage Candidates edit-save are-you-sure on API `code=illegal_candidate_transition` (from → to); confirm retries PUT with `confirm_state_override: true` (**AST-1287**); cancel skips state-only (modal stays open, state select reset); legal / same-state / unknown-state 400 stay quiet (no illegal dialog). Does **not** own core/API force path.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page (**§6c**) illegal-hop confirm | `src/ui/frontend/src/pages/AdminManageCandidates.tsx` | **`test_AdminManageCandidates.test.tsx`** — **`AST-1288:`** confirm retry / cancel / legal quiet / unknown-state no dialog |

**Broken / obsolete this pass:** none — existing Manage Candidates PUT mocks still return 200; new cases use dedicated illegal-hop mock.

**Integration:** none — UI confirm only; do not invent integration coverage (API contract covered under **AST-1287**).

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageCandidates.test.tsx \
  -t "AST-1288"
```

---

### AST-1295 · AST-1291

**Parent:** [AST-1291 — Move table lookup and field lookup objects on Data Management page](https://linear.app/astralcareermatch/issue/AST-1291/move-table-lookup-and-field-lookup-objects-on-data-management-page). **Publish:** `origin/sub/AST-1291/AST-1295-move-data-management-schema-browser-right-of-sql`.

Layout-only: Data Management workbench flex row places **Main query panel** before **Schema browser** so Tables (+ Fields for selected table) render to the **right** of the SQL textarea. Selection / discovery SQL / Run / history / Copy Output / Table Upsert unchanged.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page (**§6c**) schema-browser DOM order | `src/ui/frontend/src/pages/AdminDataManagement.tsx` | **`test_AdminDataManagement.test.tsx`** — **`AST-1295:`** Tables/Fields follow SQL textarea in document order; fields still load after table click |
| Existing §6c regression (AC3) | same page | same file — sql / copy / schema click / upsert modal / toast / sql-error paths (labels + behavior, not left/right) |

**Broken / obsolete this pass:** none — prior AdminDataManagement cases assert labels and flows, not left/right adjacency.

**Integration:** none — page chrome reorder only; do not invent integration coverage.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminDataManagement.test.tsx \
  -t "AST-1295"
```

---

### AST-1306 · AST-1299

**Parent:** [AST-1299 — Support alternative resume sections](https://linear.app/astralcareermatch/issue/AST-1299/support-alternative-resume-sections). **Publish:** `origin/sub/AST-1299/AST-1306-author-extra-sections-title-and-format`.

Operators author extra sections (title / format / enable / reorder / remove optional) on **Base Resume Content**. Format list comes from GET `catalog.body_formats` (not a TSX tuple). PUT `/data` **replaces** `sections` when that key is sent; accent-only PUT leaves sections. Required seven cannot be omitted or disabled. New extras slug from title in core (`_pending_*`). Does **not** own HTML emit (**AST-1304**) or hop/legacy ingest (**AST-1305**).

| Area | Source | Component tests |
| --- | --- | --- |
| New-extra default format | `src/utils/config.py` | **`TestAst1306ResumeStructureCatalog`** |
| Slug + prepare-for-save | `src/core/candidate.py` | **`TestAst1306ResumeStructureSavePrep`** |
| GET `all_sections`+`catalog`; PUT replace | `src/ui/api/api_candidate.py` | **`TestAst1306ResumeStructureAuthorApi`**; revised **`TestAst519ResumeStructureApi`** (normalize-valid fixture; 400 text) |
| Editor (catalog options, no Remove on required) | `src/ui/frontend/src/components/ResumeStructureEditor.tsx` | **`test_ResumeStructureEditor.test.tsx`** |
| Routed page (**§6c**) editor + first-paint mocks | `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` | **`test_ArtifactsBaseResumeContent.test.tsx`** — existing tab/accent cases + **`AST-1306:`** catalog editor / sections PUT |

**Broken / obsolete this pass:** AST-519 GET fixture was a three-id blob — `resolve_resume_structure` now falls back to DEFAULT (AST-1303 required seven). Fixture is a normalize-valid ten-id catalog with `technical_skills` disabled. PUT invalid-sections 400 now returns the normalize message (`missing required`), not `invalid resume_structure`.

**Integration:** none — existing `test_candidate_nav_api.py` is nav only; do not invent editor integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1306ResumeStructureCatalog \
  tests/component/core/test_candidate.py::TestAst1306ResumeStructureSavePrep \
  tests/component/ui/api/test_api_candidate.py::TestAst1306ResumeStructureAuthorApi \
  tests/component/ui/api/test_api_candidate.py::TestAst519ResumeStructureApi \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx \
  ../../../tests/component/frontend/components/test_ResumeStructureEditor.test.tsx
```

---

### AST-1318 · AST-1309 (apply in-row size on table-row labeled buttons)

**Parent:** [AST-1309 — Add a button style for in-row buttons](https://linear.app/astralcareermatch/issue/AST-1309/add-a-button-style-for-in-row-buttons). **Publish:** `origin/sub/AST-1309/AST-1318-apply-in-row-size-on-table-row-labeled-buttons`.

Consume AST-1317 `.btn.in-row`: Scheduled Actions row Run / Stop (busy label `Draining…`) gain `in-row` on the existing role classes. Presentation only — handlers, `disabled`, overlay `inset`, AUTO / running gating unchanged. Toolbar Stop All / Add Task, both modal footers, and icon-controls stay full-size / `icon-control`. Inventory on this tree: only those two labeled `btn`s sit in a `<td>`.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page (**§6c**) row size + leave-alone | `AdminScheduledActions.tsx` | **`test_AdminScheduledActions.test.tsx`** — **`AST-1318: row Run uses in-row; toolbar and modals stay full size`**; **`AST-1318: row Stop uses in-row`**; **`AST-1318: row Draining uses in-row`** |
| Existing catalog / enablement | same | **`AST-1301: labeled actions use catalog classes`**; **`renders tasks, edits, runs, and stops threads`** |

**Broken / obsolete this pass:** none — AST-1301 `toHaveClass("btn", "danger")` still holds with the added size token. Leave-alone modal case uses `mockApi(true)` (running thread) so toolbar Stop All is enabled — `mockApi(false)` leaves `activeThreads` empty and the click never opens Kill Running Threads.

**Integration:** no existing scenario asserts labeled-button class catalogs — no drift. Do not invent integration coverage.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  -t "AST-1318|AST-1301"
```

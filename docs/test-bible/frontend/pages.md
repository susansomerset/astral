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

**Note:** Full-file run excludes **AST-750** score-floor edit test until sibling `AST-750` ships on publish tip (product still hardcodes `1.00…10.00` options).

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

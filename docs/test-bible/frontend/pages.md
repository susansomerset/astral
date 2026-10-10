# Pages

**Test tree:** `tests/component/pages/`

Local-deploy `/authenticate` skip handoff: **`docs/test-bible/frontend/lib.md`** § AST-1441.

### AST-1357 · AST-1356

Unlock Candidate Profile **Original Resume Text** when `artifacts.base_resume` exists — remove `hasBaseResume` / `disabled` / lock placeholder on the resume tab. Field stays on existing Profile `values` / PUT / Cancel / dirty-leave (AST-1336); no Artifacts UI change.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed Profile unlock (§6c) | `CandidateProfile.tsx` | `tests/component/frontend/pages/test_CandidateProfile.test.tsx` — **`CandidateProfile — AST-1357 unlock original resume text`**: with base resume → enabled + no lock placeholder; Save PUT `context.raw_resume`; Cancel restores; without base resume still editable |
| Cancel (non-resume) | same | Revised **`restores values on cancel`** (dropped obsolete `toBeDisabled` on resume) |

**Broken / obsolete:** `restores values on cancel and locks resume text when base resume exists` — asserted resume `toBeDisabled()` when base resume present; product unlock makes that red.

**Integration:** no existing scenario asserts Profile resume lock — no drift.

**AST-1357** narrowed Vitest:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateProfile.test.tsx
```

### AST-1336 · AST-1315

Wire Candidate Profile to `useDirtyLeaveSaveThenNavigate` (sibling **AST-1335**): dirty vs last loaded/saved snapshot (`JSON.stringify`), shared `persistProfile` Promise for header Save + dirty-leave `onSave`, header Cancel unchanged. Profile only.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed Profile dirty-leave (§6c) | `CandidateProfile.tsx` | `tests/component/frontend/pages/test_CandidateProfile.test.tsx` — **`CandidateProfile — AST-1336 dirty-leave wiring`**: helper wired; clean→dirty on edit; in-page tab keeps draft; Cancel reverts; `onSave` PUT then clears dirty; save reject stays dirty + error |
| Helper contract | `useDirtyLeaveSaveThenNavigate.ts` | `docs/test-bible/frontend/hooks.md` (**AST-1335**) — not re-tested here |

**Broken / obsolete:** entire prior Profile suite under `renderWithProviders` (`MemoryRouter`) — Profile now calls `useBlocker` via the helper; mock `useDirtyLeaveSaveThenNavigate` in `test_CandidateProfile.test.tsx` so existing §6c cases stay green without a data-router harness. Header Save failure assert uses helper `onSave` (persistProfile rethrows; `void handleSave()` would leave Vitest unhandled rejection).

**Integration:** no existing scenario asserts Profile leave prompts — no drift.

**AST-1336** narrowed Vitest:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateProfile.test.tsx
```

### AST-1343 · AST-1315 (bug — virgin restore dirty)

**Parent:** AST-1315. **Publish:** `origin/sub/AST-1315/AST-1343-dirty-flag-not-cleared-after-undo-virgin-restore`. Board: `[board-betty] TESTS: REVISE` — nullish nested field touch+clear/Undo misses FormFields null↔`""` coerce.

| Area | Source | Component tests |
| --- | --- | --- |
| Virgin empty after touch+clear (§6c) | `CandidateProfile.tsx` `isDirty` | `test_CandidateProfile.test.tsx` — **`AST-1343: nullish nested field touch+clear clears dirty (virgin empty)`** — load `contact.phone: null`, type then clear; expect `isDirty` false (fails pre-fix on raw stringify; passes after compare-time normalize) |

**Broken / obsolete:** none in existing AST-1336 Cancel/exact-string cases (those still pass).

**AST-1343** narrowed Vitest (bug-repro):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateProfile.test.tsx \
  --testNamePattern="AST-1343"
```

### AST-436 · AST-442

Parent UAT on **`origin/ftr/AST-436-quickie-bugs`** surfaced gaps when manifests tested components or API defaults only. Use **§6c** for all future UI QA.

| Route / page | Source | Minimum component test | Required mocks (first paint) |
| --- | --- | --- | --- |
| Candidate Profile | `src/ui/frontend/src/pages/CandidateProfile.tsx` | `tests/component/frontend/pages/test_CandidateProfile.test.tsx` — must render page + open signature-image tab | `/api/shapes/candidates`, `/api/ui_config`, `/api/candidates/{id}`, `/api/state_ui_manifest` (reject OK) |
| Execution History | `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` | `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx` — include date blur / clear behavior per **§6c** | `/api/candidates`, `/api/admin/dispatch_ledger`, ledger logs as needed |
| Scheduled Actions | `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx`; header cap dropdown in `test_AdminScheduledActions_AST1917.test.tsx` | candidates, dispatch tasks, thread status, `/api/admin/scheduler/auto_thread_cap` (unmocked → caught, dropdown hidden) |
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

**Revised by AST-1975.** `JobsRecommended.tsx` now serves Jobs → Review (`view=review`) and Jobs → Ready (`view=ready`), one state section each; the three-section page is gone. Current coverage: § AST-1975 below.

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

**AST-1975:** `JobsInReview.tsx` became `JobsProcessing.tsx` and `test_JobsInReview.test.tsx` was renamed `test_JobsProcessing.test.tsx` (`view=processing`). The legacy unmapped-state case moved with it. Fixture key `in_review_sections` is now `processing_sections`. See § AST-1975.

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

**Log viewer:** `visibleLogs` is oldest-first by `created_at` (then `id`); Copy uses that order. API `list_log_entries` is still `ORDER BY created_at DESC`. Log cells use `.list-page-table .dispatch-log-table tbody td` so they beat `.list-page-table tbody td` (5px padding); vertical padding and line-height are 80% of those prior values. **`renders and copies log rows oldest-first by created_at`**.

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

**Manual UAT (Susan):** Scheduled Actions with multiple phase sections — expand each; confirm no gap between Candidate/Task, Entity does not cover State, horizontal scroll keeps three frozen columns aligned. *(Superseded by **AST-1818**: only Task is frozen.)*

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

Scheduled Actions: **Avail** filter control (`All` / `> 0`) on the existing client-side filter bar; when `gt0`, `filteredRows` keeps only `(available_count ?? 0) > 0` (excludes em-dash Avail: `0` or `null`). ANDs with Candidate / Section/Group / Task / Floor / AUTO / Debug / Freq / Min count / Batch size / Run counts. Empty sections omit via existing `filteredRows` bucketing; section AUTO summaries inherit. **Default engaged as `gt0` (AST-894)** — was All under AST-887 alone. *(Superseded by **AST-1818**: default is All again.)* No API / Available math / column-format change.

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

**AST-1975:** `JobsInReview.tsx` became `JobsProcessing.tsx` and `test_JobsInReview.test.tsx` was renamed `test_JobsProcessing.test.tsx` (`view=processing`). The **`AST-893 Expand One default`** describe moved with it unchanged.

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

Scheduled Actions landing defaults: Avail filter initial state `"gt0"` *(superseded by **AST-1818**: `""` / All)*; one-shot `expandAllSections()` behind `didAutoOpenSectionRef` (replaces AST-785 first-section-only auto-open). Operator collapse after landing is not overwritten. Avail → All restores zero/empty Avail rows; empty-section omission follows the filtered set. Frontend-only; reuses AST-886/893 Expand All policy.

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

**AST-987:** Admin **Session Resume Paste** page + session HTML — paste → AST-986 parse API; `useLocalStorage` retention (`session_resume:paste_text` / `session_resume:last_parse`); Open HTML via `POST /api/admin/session_resume/html` → blob URL tab (`window.open(url, "_blank")` then `opener = null`; success must not toast popup-blocked — **AST-1546**). Builder `build_session_base_resume` emits print HTML from in-memory structure/content (**no** `get_candidate` / profile overlay). Failed parse/HTML never opens a tab. Sibling **AST-986** owns parse core/route. View Parsed JSON control = **AST-1035**.

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

**AST-1025:** Admin **Session Cover Letter** page (§6c) — field form mirroring `BUILD_CONFIG["session_cover_letter"]["fields"]`; `useLocalStorage` (`session_cover_letter:fields` / `session_cover_letter:last_render`); Open HTML → `POST /api/admin/session_cover_letter/html` (AST-1024) → blob URL tab (`window.open(url, "_blank")` then `opener = null`; success must not toast popup-blocked — **AST-1546**); failed/empty HTML never opens a tab; optional `candidate_id` from selected candidate. Nav: **Cover Letter Paste** after **Resume Paste** in Tools (AST-1386 labels; paths unchanged). Core emit = sibling **AST-1024**.

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

**Retired by AST-1975.** Meteorite-track jobs stay in their state section; the Meteorites sub-section, manifest `meteorite_section`, and the AST-1057 cases are gone. Current coverage: § AST-1975 below (no Meteorites heading; Source column).

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

### AST-1709 · AST-1707

**Retired by AST-1975.** The meteorite partition is gone; the null-company no-throw check lives on in § AST-1975's **`AST-1975: no Meteorites sub-section…`** case.

**Parent:** [AST-1707](https://linear.app/astralcareermatch/issue/AST-1707). **Publish:** `origin/sub/AST-1707/AST-1709-null-company-recommended-partition-test`. **Sibling product guard:** AST-1708 (`(job.company ?? "").startsWith(prefix)` on `JobsRecommended.tsx`).

Null `company` through Recommended meteorite partition (`isMeteoriteJob` / sections `useMemo`): page must not throw; row stays out of Meteorites and in the normal state section. Product null-guard is AST-1708 — this gap does not re-edit `JobsRecommended.tsx`.

| Area | Source | Component tests |
| --- | --- | --- |
| Null-company partition ([bug-repro]) | `JobsRecommended.tsx` | **`test_JobsRecommended.test.tsx`** — **`AST-1708/AST-1709: null company does not throw; stays out of Meteorites`** |

**Broken / obsolete:** none — additive repro next to AST-1057 cases.

**Integration:** none.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx \
  --testNamePattern="AST-1708/AST-1709"
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

**AST-1975:** `JobsInReview.tsx` became `JobsProcessing.tsx` and `test_JobsInReview.test.tsx` was renamed `test_JobsProcessing.test.tsx` (`view=processing`). The **`AST-1064`** describe moved with it unchanged.

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

**AST-1975:** `JobsInReview.tsx` became `JobsProcessing.tsx` and `test_JobsInReview.test.tsx` was renamed `test_JobsProcessing.test.tsx` (`view=processing`). The **`AST-1086`** describe moved with it (tooltip job title now `Tooltip Processing`).

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

Admin **Manage Slack** page (§6c): first-paint listen state via `GET /api/admin/contact/listen`; toggle `PUT` enables/disables listen for this environment; no reply-prefix copy (AST-2085 retired the `[<environment>]` prefix). API: **`docs/test-bible/ui/api/api_contact.md`**. Nav: **`docs/test-bible/utils/config.md`**.

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

Scheduled Actions Avail **gt0** keeps rows where API `always_visible_under_avail_gt0` is true (mailbox shell with intentional zero avail); other zero-avail rows still omitted. Default remains `gt0` (AST-894) *(superseded by **AST-1818**: default All)*. Candidate cell is null-safe (`candidate_id || "—"`) so shared mailbox rows do not crash. No React `"gaze_email"` set.

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

**AST-1975:** **Not now** navigates to `/` (Jobs home redirect), not `/jobs/recommended`.

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
| Types-only catalog / section row shapes | `src/ui/frontend/src/components/ResumeStructureEditor.tsx` | no dedicated component test (module exports types only after AST-1323) |
| Routed page (**§6c**) header authoring + sections PUT | `ArtifactsBaseResumeContent.tsx`, `ArtifactEditor.tsx` | **`test_ArtifactsBaseResumeContent.test.tsx`** — **`AST-1306:`** catalog formats / no Remove on required / sections PUT; chrome covered under **AST-1323** |

**Broken / obsolete this pass:** AST-519 GET fixture was a three-id blob — `resolve_resume_structure` now falls back to DEFAULT (AST-1303 required seven). Fixture is a normalize-valid ten-id catalog with `technical_skills` disabled. PUT invalid-sections 400 now returns the normalize message (`missing required`), not `invalid resume_structure`. Flat `test_ResumeStructureEditor.test.tsx` deleted (UI removed; assertions live on the page suite).

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
  -t "AST-1306"
```

---

### AST-1323 · AST-1299 (bug — AST-1306 editor chrome)

**Parent:** [AST-1299 — Support alternative resume sections](https://linear.app/astralcareermatch/issue/AST-1299/support-alternative-resume-sections). **Publish:** `origin/sub/AST-1299/AST-1323-structure-editor-collapsible-header-row-body-between`.

Structure authoring moves onto each `ArtifactEditor` `CollapsiblePanel` header (title / format / enabled / **Job Edit** / up-down); section body text stays in the panel body between headers. Standalone flat `ResumeStructureEditor` panel removed from the page. Catalog-driven formats and required-no-Remove still hold.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page (**§6c**) header-row + body-between | `ArtifactsBaseResumeContent.tsx`, `ArtifactEditor.tsx` | **`test_ArtifactsBaseResumeContent.test.tsx`** — **`AST-1323: structure controls on collapsible header with body between`** (bug-repro); **`AST-1306:`** catalog PUT / no Remove (migrated off deleted flat editor test) |

**Broken / obsolete this pass:** none — flat `ResumeStructureEditor` UI + `test_ResumeStructureEditor.test.tsx` removed; module is types-only. Header label copy (`Job edit` → `Job Edit:`) locked under **AST-1325**.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx \
  -t "AST-1323|AST-1306"
```

---

### AST-1325 · AST-1299 (bug — structure header row layout)

**Parent:** [AST-1299 — Support alternative resume sections](https://linear.app/astralcareermatch/issue/AST-1299/support-alternative-resume-sections). **Publish:** `origin/sub/AST-1299/AST-1325-structure-header-row-name-style-enabled-job-edit-up-down-sup`.

Single header row: name | style | `Enabled:` | `Job Edit:` | up/down (label-before-checkbox). Body still between headers (AST-1323). UI/CSS only.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page (**§6c**) header row contract | `ArtifactEditor.tsx`, `App.css` | **`test_ArtifactsBaseResumeContent.test.tsx`** — **`AST-1325: header row is name | style | Enabled: | Job Edit: | up/down`** (bug-repro); AST-1323/1306 no longer lock old `Job edit` copy |

**Broken / obsolete this pass:** AST-1323/1306 cases that asserted `Job edit` — rewritten to `.structure-authoring-header` / catalog PUT only. **`[qa-handoff]`:** publish tip had duplicate `const headers` + leftover `Job edit` from a bad merge-tests conflict resolve — fixed; suite must load under vitest.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx \
  -t "AST-1325"
```

---

### AST-1324 · AST-1299 (bug — hydrate GET from base_resume)

**Parent:** [AST-1299 — Support alternative resume sections](https://linear.app/astralcareermatch/issue/AST-1299/support-alternative-resume-sections). **Publish:** `origin/sub/AST-1299/AST-1324-base-resume-content-must-load-render-existing-artifact-secti`.

Read-time hydrate: `GET /resume_structure` unions usable `artifacts.base_resume` keys into structure rows; missing body format defaults to `free_prose` (not Add-section `bullet_list`). Page panels follow hydrated enabled sections — no Save required to discover content already on the artifact.

| Area | Source | Component tests |
| --- | --- | --- |
| GET hydrate from base_resume | `src/core/candidate.py`, `src/ui/api/api_candidate.py` | **`TestAst1324HydrateResumeStructureFromBaseResumeGet`** (bug-repro) |

**Broken / obsolete this pass:** none for this repro — AST-519 page “hides orphan” still mocks a non-hydrated GET; revisit if make-fix changes client orphan filtering.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_candidate.py::TestAst1324HydrateResumeStructureFromBaseResumeGet \
  -q
```

---

### AST-1318 · AST-1309 (apply in-row size on table-row labeled buttons)

**Parent:** [AST-1309 — Add a button style for in-row buttons](https://linear.app/astralcareermatch/issue/AST-1309/add-a-button-style-for-in-row-buttons). **Publish:** `origin/sub/AST-1309/AST-1318-apply-in-row-size-on-table-row-labeled-buttons`.

Consume AST-1317 `.btn.in-row`: Scheduled Actions row Run / Stop (busy label `Draining…`) gain `in-row` on the existing role classes. Presentation only — handlers, `disabled`, overlay `inset`, AUTO / running gating unchanged. Toolbar Stop All / Add Task, both modal footers, and icon-controls stay full-size / `icon-control`. Inventory on this tree: only those two labeled `btn`s sit in a `<td>`.

**Run vs Sweep:** AUTO off is always **Run** (loop to `max_runs`). AUTO on and Avail > 0 is **Sweep** (one batch; min_count disable unchanged).

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page (**§6c**) row size + leave-alone | `AdminScheduledActions.tsx` | **`test_AdminScheduledActions.test.tsx`** — **`AST-1318: row Run uses in-row; toolbar and modals stay full size`**; **`AST-1318: row Stop uses in-row`**; **`AST-1318: row Draining uses in-row`** |
| Run vs Sweep label | same | **`AUTO off always labels Run; AUTO on with Avail > 0 labels Sweep`**; **`AUTO on with Avail > 0 labels Sweep`** |
| Existing catalog / enablement | same | **`AST-1301: labeled actions use catalog classes`**; **`renders tasks, edits, runs, and stops threads`** |

**Broken / obsolete this pass:** none — AST-1301 `toHaveClass("btn", "danger")` still holds with the added size token. Leave-alone modal case uses `mockApi(true)` (running thread) so toolbar Stop All is enabled — `mockApi(false)` leaves `activeThreads` empty and the click never opens Kill Running Threads.

**Integration:** no existing scenario asserts labeled-button class catalogs — no drift. Do not invent integration coverage.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  -t "AST-1318|AST-1301"
```

---

### AST-1337 · AST-1314

**Parent:** [AST-1314 — Add a Print button to Base Resume Content](https://linear.app/astralcareermatch/issue/AST-1314/add-a-print-button-to-base-resume-content). **Publish:** `origin/sub/AST-1314/AST-1337-print-control-on-base-resume-content`.

**Print** on Artifacts → Base Resume Content: Session-style validate-then-blob via `api()` `GET /candidate/resume/base?candidate_id=…` (saved **body** content, not editor buffer / session admin POST / job Print). **AST-1489:** structure `page_break_policy` auto-persisted from editor rows immediately before print GET. `btn secondary`; disabled without candidate or while in-flight (`Opening…`). Failed / empty HTML → on-page error + toast; **no** `window.open`. Success blob open: `window.open(url, "_blank")` then `opener = null` (no features string); must not toast popup-blocked (**AST-1546**).

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page (**§6c**) Print enable + blob / error | `ArtifactsBaseResumeContent.tsx` | **`test_ArtifactsBaseResumeContent.test.tsx`** — **`AST-1337: Print disabled with no candidate; success opens blob tab (§6c)`**; **`AST-1337: Print error and empty HTML never open a tab`** |

**Broken / obsolete this pass:** none for AST-1337 ship. **AST-1341** revises the Print 404 error assert to `No printable base resume content for this candidate` (replaces `Candidate missing artifacts.base_resume`).

**Integration:** no existing scenario asserts Base Resume Content Print — no drift. Do not invent integration coverage.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx \
  -t "AST-1337"
```

---

### AST-1342 · AST-1314 (bug — Print next to Regenerate)

**Parent:** [AST-1314 — Add a Print button to Base Resume Content](https://linear.app/astralcareermatch/issue/AST-1314/add-a-print-button-to-base-resume-content). **Publish:** `origin/sub/AST-1314/AST-1342-print-button-placement-next-to-regenerate`.

UAT chrome: Print must sit in ArtifactEditor `dep-actions` **immediately after** Generate/Regenerate (`headerActions` slot), not in the orphaned page-level row above the editor. Validate-then-blob behavior stays AST-1337.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page (**§6c**) placement bug-repro | `ArtifactsBaseResumeContent.tsx`, `ArtifactEditor.tsx` | **`test_ArtifactsBaseResumeContent.test.tsx`** — **`AST-1342: Print sits in dep-actions next to Regenerate`** (bug-repro) |
| No-candidate unavailable (AST-1337 revised) | same | **`AST-1337:`** no-candidate: Print absent **or** disabled (survives headerActions early-return) |

**Broken / obsolete this pass:** AST-1337 “Print must exist and be disabled with no candidate” — rewritten to allow absent (post-fix) or disabled (pre-fix page-level).

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx \
  -t "AST-1342|AST-1337"
```

---

### AST-1341 · AST-1314 (bug — Print false-missing base_resume)

**Parent:** [AST-1314](https://linear.app/astralcareermatch/issue/AST-1314). **Publish:** `origin/sub/AST-1314/AST-1341-print-base-resume-missing-artifacts-error`.

Primary coverage: **`docs/test-bible/core/builder.md`** (`test_ast1341_list_shaped_base_resume_prints`). Page suite: AST-1337 Print error case asserts **`No printable base resume content for this candidate`**.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestBuildBaseResume::test_ast1341_list_shaped_base_resume_prints \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx \
  -t "AST-1337: Print error"
```


### AST-1366 · AST-1360

**Parent:** [AST-1360 — Add ideal_day to candidate context](https://linear.app/astralcareermatch/issue/AST-1360/add-ideal-day-to-the-set-of-candidate-context-strengths-priorities-etc). **Publish:** `origin/sub/AST-1360/AST-1366-ideal-day-candidate-edit-surface`.

Candidate nav + Ideal Day edit page (`ContextTextPage` wrapper, `contextKey="ideal_day"`) peer of Strengths/Priorities/Deal Breakers/Backstory. Route `candidate/ideal_day` + `NAV_CONFIG` Ideal Day between Backstory and Writing Preferences. Save/load via existing `PUT /api/candidates/<id>/data` — no API change. Does **not** own Topic Menu informs (**AST-1367**) or craft prompts (**AST-1368**). Library/token/gate: **AST-1365**.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed Ideal Day page (§6c) | `CandidateIdealDay.tsx` | **`test_CandidateIdealDay.test.tsx`** — render heading + `ideal_day` prose; Save PUT `context.ideal_day` |
| Nav order | `src/utils/config.py` `NAV_CONFIG` | **`TestAst1366IdealDayCandidateNav`** (`test_config.py`; map also **`docs/test-bible/utils/config.md`**) |
| Shared editor behavior (existing) | `ContextTextPage.tsx` | **`test_ContextTextPage.test.tsx`** — unchanged; Ideal Day is another caller |

**Broken / obsolete this pass:** none — new page + nav item only.

**Integration:** no existing scenario asserts Candidate Ideal Day nav/page — no revision; do not invent new integration coverage.

## QA test manifest

1. Routed Ideal Day page (§6c): `tests/component/frontend/pages/test_CandidateIdealDay.test.tsx`
2. Nav placement: `tests/component/utils/test_config.py::TestAst1366IdealDayCandidateNav`
3. Shared ContextTextPage regression: `tests/component/frontend/components/test_ContextTextPage.test.tsx`

**AST-1366** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1366IdealDayCandidateNav \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateIdealDay.test.tsx \
  ../../../tests/component/frontend/components/test_ContextTextPage.test.tsx
```

**Pass criterion:** pytest + Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-1394 · AST-1392 (show Ad Hoc Test body without type invalidation)

**Parent:** [AST-1392](https://linear.app/astralcareermatch/issue/AST-1392). **Publish:** `origin/sub/AST-1392/AST-1394-show-ad-hoc-test-body-without-type-invalidation`.

Agent Ad Hoc **Test** success path coerces `response_text` via **`responseBodyToText`** before `setResponse`, then existing **`formatResponse`** pretty-prints JSON strings. Nested object/list bodies still display as JSON text — never an `ERROR:` overlay and never a React child type crash. Plain text is unchanged. HTTP / `success: false` still set `ERROR:`. API stringify: **`docs/test-bible/ui/api/api_admin.md`** § AST-1394.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page first paint + compact JSON pretty-print (**§6c**) | `AdminAnthropicAdHoc.tsx` | **`test_AdminAnthropicAdHoc.test.tsx`** — existing `previews, tests, fetches prompts, and saves as`; **`AST-1394: object payload JSON text pretty-prints`** |
| Nested object defense (not ERROR) | same | **`AST-1394: nested object response_text still displays`** |
| Plain text unchanged | same | **`AST-1394: plain text displays unchanged`** |
| Failure overlay | same | **`AST-1394: provider failure still shows ERROR overlay`** |

**Broken / obsolete this pass:** none — existing `"ok": true` pretty-print case still holds.

**Integration:** no existing scenario asserts Agent Ad Hoc Test display — no revision; do not invent new integration coverage.

## QA test manifest

1. Routed Agent Ad Hoc page (**§6c**) + object/plain/failure chrome: `tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx`

**AST-1394** narrowed run (page; API in **`ui/api/api_admin.md`**):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx
```

### AST-1409 · AST-1406

**Parent:** [AST-1406 — Page refreshes and modals are closed (lost!)](https://linear.app/astralcareermatch/issue/AST-1406). **Publish:** `origin/sub/AST-1406/AST-1409-in-place-live-updates-on-scheduled-actions`.

Scheduled Actions consumes shared `useInPlaceLiveRefresh`: first paint may show `Loading…`; AUTO/Dbg post-PUT and running→idle `loadData()` are silent. Add/edit overlay stays outside the list gate and keeps its draft. Proposed `pattern.ui.in-place-live-refresh` is catalog docs (not pytest). Session-shell mount is **AST-1408**. Remaining list pages are **AST-1410**.

| Area | Source | Component tests |
| --- | --- | --- |
| Hook contract | `useInPlaceLiveRefresh.ts` | **`test_useInPlaceLiveRefresh.test.tsx`** |
| Routed Scheduled Actions (**§6c**) silent AUTO/Dbg | `AdminScheduledActions.tsx` | **`test_AdminScheduledActions.test.tsx`** — **`AST-1409 in-place live refresh`** → AUTO/Dbg without `Loading…` |
| Avail / last-run + overlay draft | same | **`running→idle merges Avail and last-run; open Add Task draft survives`** |
| Existing run-complete Avail | same | **`reloads dispatch tasks when a manual run thread finishes`** (regression) |
| Fast Run never seen in thread_status | same | **`reloads Avail after Run even when thread_status never reports running`** |

**Broken / obsolete:** none — first-paint `Loading…` and existing AUTO click / run-complete Avail cases stay. Filters stay client-side (no query-identity spinner on this page).

**Integration:** no existing scenario asserts Scheduled Actions list remount / overlay draft — no revision. Do not invent new integration coverage.

## QA test manifest

1. Hook: `tests/component/frontend/hooks/test_useInPlaceLiveRefresh.test.tsx`
2. Routed page (**§6c**): `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — `--testNamePattern="AST-1409"`

**AST-1409** narrowed run (Vitest — from `src/ui/frontend/`):

```bash
npm run test:component -- \
  ../../../tests/component/frontend/hooks/test_useInPlaceLiveRefresh.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-1409|useInPlaceLiveRefresh"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-1410 · AST-1406

**AST-1975:** `JobsInReview.tsx` became `JobsProcessing.tsx` and `test_JobsInReview.test.tsx` was renamed `test_JobsProcessing.test.tsx` (`view=processing`). Its **`AST-1410 silent refetch`** case matches `view=processing`; the Recommended case matches `view=review`.

**Parent:** [AST-1406 — Page refreshes and modals are closed (lost!)](https://linear.app/astralcareermatch/issue/AST-1406). **Publish:** `origin/sub/AST-1406/AST-1410-apply-silent-refetch-on-remaining-loading-gate-surfaces`.

Remaining authenticated list surfaces consume `useInPlaceLiveRefresh` from **AST-1409**: first paint (and query-identity) may show `Loading…`; post-mutation / poll / modal-close `load*` is silent. Manage Tasks edit overlay stays outside the list gate. Artifact Cancel with no snapshot re-GETs last-saved tabs (no `window.location.reload`). Company Search Terms Cancel chrome stays snapshot-gated (`inReview = snapshot !== null`); the no-snapshot re-GET branch is covered on **`ArtifactEditor`**. Session-shell is **AST-1408**. Scheduled Actions is **AST-1409**.

| Area | Source | Component tests |
| --- | --- | --- |
| Hook contract | `useInPlaceLiveRefresh.ts` | **`test_useInPlaceLiveRefresh.test.tsx`** (AST-1409) |
| Manage Tasks overlay + silent revert (**§6c**) | `AdminTaskPrompts.tsx` | **`test_AdminTaskPrompts.test.tsx`** — **`AST-1410 silent refetch`** |
| Manage Agents post-save (**§6c**) | `AdminAgentPrompts.tsx` | **`test_AdminAgentPrompts.test.tsx`** — **`AST-1410 silent refetch`** |
| Scheduled Queries first paint + Deactivate (**§6c**) | `AdminScheduledQueries.tsx` | **`test_AdminScheduledQueries.test.tsx`** |
| Manage Email Land Meteorite (**§6c**) | `AdminManageEmail.tsx` | **`test_AdminManageEmail.test.tsx`** — **`AST-1410 silent refetch`** |
| Performance Monitor 15s poll + overlay (**§6c**) | `AdminPerformanceMonitor.tsx` | **`test_AdminPerformanceMonitor.test.tsx`** — **`AST-1410 silent refetch`** |
| Recommended Skip (**§6c**) | `JobsRecommended.tsx` | **`test_JobsRecommended.test.tsx`** — **`AST-1410 silent refetch`** |
| In Review modal-close (**§6c**) | `JobsInReview.tsx` | **`test_JobsInReview.test.tsx`** — **`AST-1410 silent refetch`** |
| Skipped Retry (**§6c**) | `JobsSkipped.tsx` | **`test_JobsSkipped.test.tsx`** — **`AST-1410 silent refetch`** |
| Artifact no-snapshot Cancel | `ArtifactEditor.tsx` | **`test_ArtifactEditor.test.tsx`** — **`AST-1410: no-snapshot Cancel re-GETs last-saved tabs without location.reload`** |
| Company Search Terms first paint (**§6c**) | `ArtifactsCompanySearchTerms.tsx` | existing **`test_ArtifactsCompanySearchTerms.test.tsx`** |

**Broken / obsolete this pass:** none — first-paint `Loading…` and existing save/skip/retry cases stay. `test_AdminScheduledQueries.test.tsx` is new (bible listed it earlier; file was missing). Company Search Terms Cancel remains review/snapshot-only; no RTL path for the no-snapshot branch on that page.

**Integration:** no existing scenario asserts list remount / overlay draft / artifact Cancel reload — no revision. Do not invent new integration coverage.

## QA test manifest

1. Hook (existing): `tests/component/frontend/hooks/test_useInPlaceLiveRefresh.test.tsx`
2. Manage Tasks: `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx` — `--testNamePattern="AST-1410"`
3. Manage Agents: `tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx` — `--testNamePattern="AST-1410"`
4. Scheduled Queries: `tests/component/frontend/pages/test_AdminScheduledQueries.test.tsx`
5. Manage Email: `tests/component/frontend/pages/test_AdminManageEmail.test.tsx` — `--testNamePattern="AST-1410"`
6. Performance Monitor: `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx` — `--testNamePattern="AST-1410"`
7. Recommended: `tests/component/frontend/pages/test_JobsRecommended.test.tsx` — `--testNamePattern="AST-1410"`
8. In Review: `tests/component/frontend/pages/test_JobsInReview.test.tsx` — `--testNamePattern="AST-1410"`
9. Skipped: `tests/component/frontend/pages/test_JobsSkipped.test.tsx` — `--testNamePattern="AST-1410"`
10. ArtifactEditor Cancel: `tests/component/frontend/components/test_ArtifactEditor.test.tsx` — `--testNamePattern="AST-1410"`
11. Search Terms first paint: `tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx`

**AST-1410** narrowed run (Vitest — from `src/ui/frontend/`):

```bash
npm run test:component -- \
  ../../../tests/component/frontend/hooks/test_useInPlaceLiveRefresh.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminScheduledQueries.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminManageEmail.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsInReview.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsSkipped.test.tsx \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  ../../../tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx \
  --testNamePattern="AST-1410|useInPlaceLiveRefresh|renders company search terms page"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-1412 · AST-1403

**Parent:** [AST-1403](https://linear.app/astralcareermatch/issue/AST-1403). **Publish:** `origin/sub/AST-1403/AST-1412-ad-hoc-seven-segment-editors-and-save`.

Agent Ad Hoc editors match Manage Tasks’ seven segments (System, Cache A–D, No Cache, User). Fetch-from-task and Save As read/write all seven columns; overwrite ● / `hasContent` treat any populated segment as content. Preview and Test POST always include all seven keys, including `system_prompt: ""`. Preview modal / agent_data panes: sibling **AST-1413**. Backend assemble/store: **AST-1411**. `_enrich_tasks` `*_len` passthrough: **`docs/test-bible/ui/api/api_admin.md`** § AST-1412.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page first paint + seven tab labels (**§6c**) | `AdminAnthropicAdHoc.tsx` | **`test_AdminAnthropicAdHoc.test.tsx`** — **`AST-1412: seven editor tabs match Manage Tasks labels`** |
| Cache-B-only fetch isolation; Save As enabled from B | same | **`AST-1412: Cache B loads into B not A; Save As lights from B-only content`** |
| Preview / Test / Save As seven keys; empty System is `""` | same | **`AST-1412: Preview, Test, and Save As send all seven keys; empty System is empty string`** |
| Overwrite ● from Cache-B-only `*_len` | same | **`AST-1412: overwrite marker treats Cache-B-only list lens as existing content`** |
| Existing kitchen-sink + AST-1215 + AST-1394 | same | keep **`previews, tests, fetches prompts, and saves as`**; **`AST-1215`**; **`AST-1394`** |

**Broken / obsolete this pass:** `GET /tasks/task_a` mock and `/tasks` fixture were three-slot (`user` / `cache` / `nocache`). Revised to seven columns + Cache-B-only list row so fetch/overwrite match product. Kitchen-sink still uses default User tab + `"User prompt content..."`.

**Integration:** no existing scenario asserts Ad Hoc editor tabs / Save As body — no revision; do not invent new integration coverage.

## QA test manifest

1. Routed Agent Ad Hoc page (**§6c**): `tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx`
2. `_enrich_tasks` seven `*_len`: `tests/component/ui/api/test_api_admin.py::TestAst1412EnrichTaskLens`

**AST-1412** narrowed run (page; API lens in **`ui/api/api_admin.md`**):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx \
  --testNamePattern="AST-1412|previews, tests, fetches|AST-1215|AST-1394"
```

**Pass criterion:** Vitest + `TestAst1412EnrichTaskLens` green — not zero-arg harness / branch-lock gate.

### AST-1413 · AST-1403

**Parent:** [AST-1403](https://linear.app/astralcareermatch/issue/AST-1403). **Publish:** `origin/sub/AST-1403/AST-1413-ad-hoc-preview-modal-and-agent-data-panes`.

Preview Prompt opens the shared `Modal` with eight resolved tabs (System, Cache A–D, No Cache, User, Live Content). The page has no inline “Resolved Prompt Preview” block. Cache A reads `cache_a` falling back to `cache`; empty slots show `(empty)`. After HTTP 200 + `success` + non-empty `batch_id`, the workbench mounts `BatchAgentDataPanes` (same body as Execution History, including RESPONSE + Tokens & Cost). Preview does not GET `/api/agent_data/…` or clear those panes. Soft-fail / missing `batch_id` toasts only. Editors / Save As: **AST-1412**. Assemble/store: **AST-1411**. Execution History still uses default `BatchAgentDataModal` — **`test_BatchAgentDataModal.test.tsx`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page first paint + Preview modal (**§6c**) | `AdminAnthropicAdHoc.tsx` | **`test_AdminAnthropicAdHoc.test.tsx`** — **`AST-1413: Preview Prompt opens eight-tab modal; page has no inline preview block`** |
| Post-Test panes; Preview does not refresh | same | **`AST-1413: successful Test mounts panes; Preview does not clear them`** |
| Success without `batch_id` | same | **`AST-1413: Test without batch_id toasts and leaves panes unmounted`** |
| Kitchen-sink + seven-segment POST + AST-1394 chrome | same | **`previews, tests, fetches prompts, and saves as`** waits for modal `sys` + **Tokens & Cost**; **`AST-1412`** Preview/Test wait retargeted; **`AST-1394`** overlay/pretty-print retargeted to panes/toast |
| Execution History wrapper unchanged | `BatchAgentDataModal.tsx` | **`test_BatchAgentDataModal.test.tsx`** (default export still wide `Modal`) |

**Broken / obsolete this pass:** Inline “Resolved Prompt Preview” + Response `<pre>` dump (including AST-1394 pretty-print / `ERROR:` overlay on the page) are gone. Page cases now assert modal tabs + `BatchAgentDataPanes`. API stringify of `response_text` stays in **`docs/test-bible/ui/api/api_admin.md`** § AST-1394.

**Integration:** no existing scenario asserts Ad Hoc Preview modal / post-Test panes — no revision; do not invent new integration coverage.

## QA test manifest

1. Routed Agent Ad Hoc page (**§6c**): `tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx`
2. Execution History modal wrapper (extract regression): `tests/component/frontend/components/test_BatchAgentDataModal.test.tsx`

**AST-1413** narrowed run (from `src/ui/frontend/`):

```bash
npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx \
  ../../../tests/component/frontend/components/test_BatchAgentDataModal.test.tsx
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-1452 · AST-1439

**Parent:** [AST-1439](https://linear.app/astralcareermatch/issue/AST-1439). **Publish:** `origin/sub/AST-1439/AST-1452-ad-hoc-import-picker-and-load`.

Agent Ad Hoc import picker table (list GET — sibling **AST-1451**; **AST-1535** scopes refetch with `candidate_id` / `task_key`), row select, **Load** into seven editors from `GET /api/agent_data/<batch_id>` (TASK → User; missing slots empty), `BatchAgentDataPanes` on imported `batch_id`, one leading `adhoc-` strip on workbench task key with `skipCatalogFetchRef` (no catalog fetch-from-task), `importEntityLock` for Preview/Test `entity_id`, dirty-editor replace confirm matching fetch-from-task. Does **not** own list query implementation or Test persist prefix (**AST-1451**).

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page + import list with candidate (**§6c**) | `AdminAnthropicAdHoc.tsx` | **`test_AdminAnthropicAdHoc.test.tsx`** — **`AST-1452: with candidate selected loads import runs into the table`** (revised **AST-1535**) |
| Load → editors + panes (**AC2**) | same | **`AST-1452: Load fills editors and mounts panes for the imported batch`** |
| Strip `adhoc-`; skip catalog fetch (**AC4**) | same | **`AST-1452: Load strips one adhoc- prefix without catalog fetch-from-task`** |
| `importEntityLock` + orphan entity option (**AC5**) | same | **`AST-1452: importEntityLock sends restored entity_id on Preview`** |
| Dirty replace confirm (**AC6**) | same | **`AST-1452: dirty editors confirm Load; Cancel leaves content unchanged`**; **`AST-1452: dirty confirm Yes replaces editor content`** |
| List/load GET contracts | **AST-1451** | **`docs/test-bible/core/agent.md`** § AST-1451 (no duplicate API tests here) |
| Preview modal / post-Test panes baseline | **AST-1413** | existing **`AST-1413`** cases (unchanged) |

**Broken / obsolete this pass:** all `mockApi` paths must stub **`GET /api/admin/adhoc/runs`** (empty array default) — revised under **AST-1535** to `startsWith` + candidate query. Originally: shared handler + AST-1215 inline mock.

**Integration:** no existing scenario covers Ad Hoc import picker/load — do not invent new integration coverage.

## QA test manifest

1. Routed Agent Ad Hoc page + import picker/load (**§6c**): `tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx` — pattern **`AST-1452`**
2. Regression: existing **`AST-1413`** / **`AST-1412`** / kitchen-sink cases in the same file (full file run)

**AST-1452** narrowed run (from `src/ui/frontend/`):

```bash
npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx \
  --testNamePattern="AST-1452|AST-1413|previews, tests, fetches|AST-1215|AST-1394|AST-1412"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-1478 · AST-1464

**Parent:** [AST-1464 — Add means to mark job as applied for](https://linear.app/astralcareermatch/issue/AST-1464). **Publish:** `origin/sub/AST-1464/AST-1478-report-applied-and-skip`.

Recommended opens JAR with shared-hook **Skip** / **Applied**; report strip uses labeled `.btn` roles; successful Skip/Applied refreshes the list and closes the report when the job leaves rows; CLIENT **Apply** stays absent. Modal unit cases: **`docs/test-bible/frontend/components.md`** § AST-1478.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed Recommended → report Skip/Applied (**§6c**) | `JobsRecommended.tsx` + JAR | **`test_JobsRecommended.test.tsx`** — **`AST-1478 report Applied and Skip`** (strip visible; Skip → `/skip` + close; Applied → notes → `candidate_action` applied + close; no **Apply**) |

**Broken / obsolete:** none — additive report wiring; existing open-report / list Skip / AST-1410 / AST-1477 list Applied asserts still hold.

**Integration:** no existing scenario — no revision.

## QA test manifest

1. JAR callbacks: `test_JobAnalysisReportModal.test.tsx` — **`AST-1478`**
2. Recommended page (**§6c**): `test_JobsRecommended.test.tsx` — **`AST-1478`**

**AST-1478** narrowed run (from `src/ui/frontend/`):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx \
  --testNamePattern="AST-1478|sticky header|opens the report|AST-1410"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-1479 · AST-1464

**Parent:** [AST-1464 — Add means to mark job as applied for](https://linear.app/astralcareermatch/issue/AST-1464). **Publish:** `origin/sub/AST-1464/AST-1479-applied-jobs-list-home`.

Applied list home: `view=applied` rows, empty copy, post-applied R/I/X/G via shared notes + `candidate_action`, error toast on illegal transition. Config/API: **`docs/test-bible/utils/config.md`** / **`docs/test-bible/ui/api/api_jobs.md`** § AST-1479.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed Applied page (**§6c**) | `JobsApplied.tsx` | **`test_JobsApplied.test.tsx`** — **`JobsApplied — AST-1479 applied list home`** (rows + Actions; empty; Interview → notes → `candidate_action`; 409 toast) |

**Broken / obsolete:** prior stub assert `"No records found."` — product empty copy is `"No applied jobs yet"`.

**Integration:** no existing scenario — no revision.

## QA test manifest

1. Applied page (**§6c**): `tests/component/frontend/pages/test_JobsApplied.test.tsx` — **`AST-1479`**
2. API `view=applied`: `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_applied_uses_applied_job_states` (+ revised `test_list_recommended_and_default`)
3. Config states + nav: `tests/component/utils/test_config.py::TestAst1479AppliedJobStatesAndNav`

**AST-1479** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_applied_uses_applied_job_states \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_recommended_and_default \
  tests/component/utils/test_config.py::TestAst1479AppliedJobStatesAndNav \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_JobsApplied.test.tsx \
  --testNamePattern="AST-1479"
```

**Pass criterion:** pytest + Vitest green on manifest lines — not zero-arg harness / branch-lock gate.


### AST-1454 · AST-1446

**AST-1975:** `JobsInReview.tsx` became `JobsProcessing.tsx` and `test_JobsInReview.test.tsx` was renamed `test_JobsProcessing.test.tsx` (`view=processing`). Drift: the **`AST-1454`** case cited below was already absent from `test_JobsInReview.test.tsx` before the rename (`git log -S AST-1454` on the file finds nothing); not reconstructed.

**Parent:** [AST-1446 — When a job is in a Skipped state, make all fields editable](https://linear.app/astralcareermatch/issue/AST-1446/when-a-job-is-in-a-skipped-state-make-all-fields-editable). **Publish:** `origin/sub/AST-1446/AST-1454-job-detail-skipped-field-editors`.

`JobsSkipped` / `JobsInReview` pass `onRefresh={load}` into `JobDetailModal` so Save refreshes the list. Editor chrome: **`docs/test-bible/frontend/components.md`** § AST-1454.

| Area | Source | Component tests |
| --- | --- | --- |
| Skipped list refresh after Save (**§6c**) | `JobsSkipped.tsx` | **`test_JobsSkipped.test.tsx`** — **`AST-1454 onRefresh after skipped-field Save`** |
| In Review list refresh after Save (**§6c**) | `JobsInReview.tsx` | **`test_JobsInReview.test.tsx`** — **`AST-1454 onRefresh wiring`** |

**Broken / obsolete:** none.

**Integration:** none.

## QA test manifest

1. `tests/component/frontend/pages/test_JobsSkipped.test.tsx` — **`AST-1454`**
2. `tests/component/frontend/pages/test_JobsInReview.test.tsx` — **`AST-1454`**
3. Modal editors: `test_JobDetailModal.test.tsx` — **`AST-1454`** (primary: **components.md**)

```bash
cd src/ui/frontend && npx vitest run \
  ../../../tests/component/frontend/pages/test_JobsSkipped.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsInReview.test.tsx \
  ../../../tests/component/frontend/components/test_JobDetailModal.test.tsx \
  --testNamePattern="AST-1454"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-1476 · AST-1462

**Parent:** [AST-1462 — Create and position page break](https://linear.app/astralcareermatch/issue/AST-1462). **Publish:** `origin/sub/AST-1462/AST-1476-structure-editor-page-break-dropdown-base-and-job`.

Base Resume Content **Save sections** PUTs `page_break_policy` on each section; header shows catalog-driven Page break control. Primary ArtifactEditor / JAR: **`docs/test-bible/frontend/components.md`** § AST-1476.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page (**§6c**) dropdown + Save sections | `ArtifactsBaseResumeContent.tsx` | **`test_ArtifactsBaseResumeContent.test.tsx`** — **`AST-1476:`**; revised **AST-1306** PUT asserts policy |

**Broken / obsolete this pass:** AST-1306 catalog/all_sections fixtures lacked page-break fields — extended.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx \
  --testNamePattern="AST-1476|AST-1306"
```

### AST-1489 · AST-1483 (bug — Print ignores unsaved page-break)

**Parent:** [AST-1483 — Resume page break settings don't work](https://linear.app/astralcareermatch/issue/AST-1483/resume-page-break-settings-dont-work). **Publish:** `origin/sub/AST-1483/AST-1489-page-break-settings-still-ignored-on-print`. Auto-save structure rows (incl. `page_break_policy`) before validate-then-blob print GET on Base Resume Content and JAR Job Resume. **Body content** still from saved artifacts — not editor buffer.

| Area | Source | Component tests |
| --- | --- | --- |
| Base Print without Save sections (bug-repro) | `ArtifactsBaseResumeContent.tsx` | **`test_ArtifactsBaseResumeContent.test.tsx`** — **`AST-1489:`** |
| JAR Print Resume without Save sections | `JobAnalysisReportModal.tsx` | **`test_JobAnalysisReportModal.test.tsx`** — **`AST-1489:`** |
| Reorder + Print full body (AST-1490) | `ArtifactEditor.tsx`, Base/JAR pages | **`docs/test-bible/frontend/components.md`** § AST-1490 |
| Print mock handlers (AST-1337 / AST-1350) | same | revised **`AST-1337:`** / **`AST-1350:`** — tolerate structure PUT before resume GET |

**Broken / obsolete this pass:** AST-1337 Print mocks lacked structure PUT handler — extended for make-fix blast radius.

**Integration:** none — do not invent new integration coverage.

## QA test manifest

1. Base print-before-PUT (bug-repro): `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx` — `--testNamePattern="AST-1489"`
2. JAR print-before-PUT (bug-repro): `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` — `--testNamePattern="AST-1489"`
3. Print regression mocks: same files — `--testNamePattern="AST-1337|AST-1350"`

**AST-1489** narrowed run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  --testNamePattern="AST-1489|AST-1337|AST-1350"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-1481 · AST-1463

**AST-1975:** blank jobId and modal close navigate to `/`; the error link reads **Back to Jobs** (`href="/"`).

**Parent:** [AST-1463 — Candidate single page job report](https://linear.app/astralcareermatch/issue/AST-1463). **Publish:** `origin/sub/AST-1463/AST-1481-detail-deeplink-opens-existing-report-modal`.

Thin deeplink host at `/jobs/detail/:jobId` opens the **existing** `JobAnalysisReportModal` (same shell as Recommended row-click), prefetches job for early 404/candidate gate, admin candidate alignment via company → `candidate_id`, close → `/jobs/recommended`. Does **not** own post-auth return-path (**AST-1482**). **`JobsRecommended.tsx`** unchanged — list regression stays on existing **`opens the report modal from a row click`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed deeplink page (**§6c**) | `JobsJobDetail.tsx` | **`test_JobsJobDetail.test.tsx`** — **`AST-1481`** (modal shell; skipped job; 404 + API error UI + back link; close → recommended; blank id redirect; prefetch then company alignment before modal) |
| Admin candidate alignment helper | `CandidateContext.tsx` | **`test_CandidateContext.test.tsx`** — **`AST-1481 alignSelectedCandidateForJobCompany`** (admin switch; non-admin no-op; company lookup soft-fail) |
| Recommended list regression | `JobsRecommended.tsx` (untouched) | **`test_JobsRecommended.test.tsx`** — **`opens the report modal from a row click`** (existing) |

**Broken / obsolete:** none — additive route/host; JAR component tests unchanged.

**Integration:** no existing scenario — no revision.

## QA test manifest

1. Deeplink page (**§6c**): `tests/component/frontend/pages/test_JobsJobDetail.test.tsx` — **`AST-1481`**
2. Candidate alignment: `tests/component/frontend/contexts/test_CandidateContext.test.tsx` — **`AST-1481`**
3. Recommended list regression: `tests/component/frontend/pages/test_JobsRecommended.test.tsx` — **`opens the report modal from a row click`**

**AST-1481** narrowed run (from `src/ui/frontend/`):

```bash
npm run test:component -- \
  ../../../tests/component/frontend/pages/test_JobsJobDetail.test.tsx \
  ../../../tests/component/frontend/contexts/test_CandidateContext.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx \
  --testNamePattern="AST-1481|opens the report modal"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasums (publish tip):**

- `docs/test-bible/frontend/pages.md` — `ab00a069b7566ed95635137118159ef65ffbd3d8`
- `docs/test-bible/frontend/contexts.md` — `839d8fc16fcda5db81fc374b0177717f44d7cc3c`

### AST-1488 · AST-1485

**Parent:** [AST-1485 — Enable Applied job list in nav](https://linear.app/astralcareermatch/issue/AST-1485). **Publish:** `origin/sub/AST-1485/AST-1488-applied-jobs-list-home-re-land`.

**Re-land of AST-1479** product slice (`APPLIED_JOB_STATES` + Applied nav + `view=applied` API + real `JobsApplied`). **Existing coverage — no new tests.** Config/API: **`docs/test-bible/utils/config.md`** / **`docs/test-bible/ui/api/api_jobs.md`** § AST-1488.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed Applied page (**§6c**) | `JobsApplied.tsx` | **`test_JobsApplied.test.tsx`** — **`JobsApplied — AST-1479 applied list home`** (rows + Actions; empty; Interview → notes → `candidate_action`; 409 toast) |
| API `view=applied` | `api_jobs.py` | **`test_list_applied_uses_applied_job_states`** (+ **`test_list_recommended_and_default`**) |
| Config states + nav | `config.py` | **`TestAst1479AppliedJobStatesAndNav`** |

**Broken / obsolete:** none — product restore makes the AST-1479 suites green again; do not rename test ids.

**Integration:** no existing scenario — no revision.

## QA test manifest

1. Applied page (**§6c**): `tests/component/frontend/pages/test_JobsApplied.test.tsx` — **`AST-1479`**
2. API `view=applied`: `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_applied_uses_applied_job_states` (+ `test_list_recommended_and_default`)
3. Config states + nav: `tests/component/utils/test_config.py::TestAst1479AppliedJobStatesAndNav`

**AST-1488** narrowed run (same paths as AST-1479):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_applied_uses_applied_job_states \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_recommended_and_default \
  tests/component/utils/test_config.py::TestAst1479AppliedJobStatesAndNav \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_JobsApplied.test.tsx \
  --testNamePattern="AST-1479"
```

**Pass criterion:** pytest + Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-1498 · AST-1485

**Parent:** [AST-1485 — Enable Applied job list in nav](https://linear.app/astralcareermatch/issue/AST-1485). **Publish:** `origin/sub/AST-1485/AST-1498-candidate-applied-missing-from-applied-screen`.

Fix-lane bug: Applied page must list stem/meteorite jobs with NULL `company.candidate_id`; post-applied `candidate_action` must send `candidate_id` for linkage repair. API repro: **`docs/test-bible/ui/api/api_jobs.md`** § AST-1498.

| Area | Source | Component tests |
| --- | --- | --- |
| POST includes `candidate_id` (**[bug-repro]**) | `JobsApplied.tsx` | **`test_JobsApplied.test.tsx`** — **`AST-1498 [bug-repro]: candidate_action POST includes candidate_id`** |

**Broken / obsolete:** **`JobsApplied — AST-1479`** Interview case still asserts body without `candidate_id` — keep for pre-fix regression; AST-1498 repro is separate `it`.

**Integration:** none.

---

### AST-1495 · AST-1484

**Parent:** [AST-1484 — Create meteorite companies per email address](https://linear.app/astralcareermatch/issue/AST-1484/create-meteorite-companies-per-email-address). **Publish:** `origin/sub/AST-1484/AST-1495-email-land-paths-apply-stem-company-attach`.

Read-only **Meteorite** companies list (`CompaniesMeteorite.tsx`): inline columns; fetches `view=meteorite_list`; row click → `CompanyDetailModal`; no bulk actions. API: **`docs/test-bible/ui/api/api_companies.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page load + modal (§6c) | `CompaniesMeteorite.tsx` | **`test_CompaniesMeteorite.test.tsx`** |
| Non-array payload empty state | same | **`test_CompaniesMeteorite.test.tsx`** |

**Broken / obsolete:** none — new page.

**Integration:** none.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CompaniesMeteorite.test.tsx
```


### AST-1538 · AST-1533

**Parent:** [AST-1533 — Manage Email gives HTML for the body of the message, not for the header, and it must include both.](https://linear.app/astralcareermatch/issue/AST-1533/manage-email-gives-html-for-the-body-of-the-message-not-for-the-header). **Publish:** `origin/sub/AST-1533/AST-1538-manage-email-modal-copy-dark-purple`.

Manage Email modal (§6c): render `assembled_html` in `<pre class="email-html-source">` (no `html_body` fallback); Copy (`btn secondary`) clips that string + success toast; `.email-html-source` background is `var(--bg-elevated)` (not `#fff`). Land Meteorite multi-select unchanged — covered by **AST-1142**. Assembly API: **`docs/test-bible/core/inbox.md`** / **`docs/test-bible/ui/api/api_inbox.md`** (**AST-1537**).

| Area | Source | Component tests |
| --- | --- | --- |
| Assembled modal source + no body-only fallback (§6c) | `AdminManageEmail.tsx` | revised matched-row modal case; **`AdminManageEmail — AST-1538`** |
| Copy control + toast (§6c) | `AdminManageEmail.tsx` | **`AdminManageEmail — AST-1538`** · Copy clips `assembled_html` |
| Dark purple reading surface | `App.css` | **`AdminManageEmail — AST-1538`** · `.email-html-source` uses `--bg-elevated` |
| Land Meteorite multi-select regression (AC4) | `AdminManageEmail.tsx` | existing **`AdminManageEmail — AST-1142`** |

**Broken / obsolete:** AST-1040/1051 modal case that mocked `html_body` only and asserted that string in the `<pre>` — revised to `assembled_html`.

**Integration:** none — no existing Manage Email modal scenario; do not invent.

## QA test manifest

1. Routed page + assembled modal + copy + CSS: `tests/component/frontend/pages/test_AdminManageEmail.test.tsx`
2. Land Meteorite regression (same file): describe **`AST-1142`**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageEmail.test.tsx
```

**Pass criterion:** Vitest green on narrowed args — not zero-arg harness / branch-lock gate.


### AST-1535 · AST-1532 (Compact filtered import picker UI)

**Parent:** [AST-1532](https://linear.app/astralcareermatch/issue/AST-1532). **Publish:** `origin/sub/AST-1532/AST-1535-compact-filtered-import-picker-ui`.

Picker chrome only on `AdminAnthropicAdHoc.tsx`: refetch `GET /api/admin/adhoc/runs?candidate_id=…&task_key=…` on `[selectedId, taskKey]` (skip when no candidate); read `adhoc_import_picker_visible_rows` from `GET /api/ui_config`; scroll wrap `maxHeight` = head + N×row layout mirrors; preserve Load / confirmLoad. API filter/cap: **AST-1534**.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page §6c + candidate-scoped list | `AdminAnthropicAdHoc.tsx` | revised **`AST-1452: with candidate selected loads import runs into the table`** |
| Empty candidate → no runs GET | same | **`AST-1535: no candidate skips runs fetch and leaves picker empty`** |
| Task key → `task_key` query | same | **`AST-1535: task key selection adds task_key query param on runs refetch`** |
| ui_config visible rows → scroll maxHeight | same | **`AST-1535: ui_config visible rows set scroll wrap maxHeight`** |
| Load / agent_data unchanged | same | **`AST-1535: Load still fills editors from agent_data batch`** + existing **`AST-1452`** Load suite |

**Broken / obsolete this pass:** AST-1452 bare `/api/admin/adhoc/runs` on mount; `selectImportRow` race before filtered list arrives — revised in place. `mockApi` / AST-1215 mocks use `startsWith` + optional `uiConfig` / empty `candidates`.

**Integration:** no existing scenario covers Agent Ad Hoc picker — do not invent.

## QA test manifest

1. Routed Agent Ad Hoc + filtered picker / Load (**§6c**): `tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx` — patterns **`AST-1535`** + **`AST-1452`**

**AST-1535** narrowed run (from `src/ui/frontend/`):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx \
  --testNamePattern="AST-1535|AST-1452"
```

**Pass criterion:** Vitest green on narrowed args — not zero-arg harness / branch-lock gate.

### AST-1558 · AST-1555

**Parent:** [AST-1555](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation). **Publish:** `origin/sub/AST-1555/AST-1558-inbox-candidate-verbs-manage-email-filter`.

Manage Email (§6c): candidate filter default **All**; no Candidate/Matched column or modal match line; Land Meteorite disabled until a candidate is selected; list reload with `?candidate_id=`; Land POST includes `candidate_id`. API: **`docs/test-bible/ui/api/api_inbox.md`** § AST-1558.

| Area | Source | Component tests |
| --- | --- | --- |
| Filter default All + candidate_id reload + no Matched (§6c) | `AdminManageEmail.tsx` | **`AdminManageEmail — AST-1558`** |
| Land requires filter + POST body | same | revised **`AdminManageEmail — AST-1142`** / **AST-1410** |
| Assembled modal without match line | same | revised older describe + **AST-1538** |

**Broken / obsolete:** Candidate column / `Matched: …` / `manage-email-match` assertions (AST-1048/1051) — revised away. Land-enabled-on-selection-alone (AST-1142) — now requires candidate filter.

**Integration:** none — do not invent.

```bash
cd src/ui/frontend && npx vitest run ../../../tests/component/frontend/pages/test_AdminManageEmail.test.tsx
```

---

### AST-1577 · AST-1569

**Parent:** [AST-1569 — Implement patt.artifact.write-operative](https://linear.app/astralcareermatch/issue/AST-1569/implement-pattartifactwrite-operative). **Publish:** `origin/sub/AST-1569/AST-1577-ui-consistency-base-resume-editor`.

Base Resume Content passes `bodyShape="resume_content"` (drops `useCandidateResumeStructure` on this page only); Save still PUTs leaf `artifacts.base_resume`. Draft `patt.artifact.ui-consistency` with no write-operative cross-link. Editor prop: **`docs/test-bible/frontend/components.md`** § AST-1577. (**AST-1628** retargeted plural → singular draft path/id.)

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page (**§6c**) bodyShape + leaf Save (autosave since AST-2056) | `ArtifactsBaseResumeContent.tsx` | **`test_ArtifactsBaseResumeContent.test.tsx`** — **`AST-1577:`** |
| Draft pattern (no write-operative link) | `canon/directives/draft/patt.artifact.ui-consistency.md` | same **`AST-1577: page and draft follow ui-consistency`** |

**Broken / obsolete:** none — existing structure/print/accent cases still render via `bodyShape`.

**Integration:** none — do not invent.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  --testNamePattern="AST-1577|loads fixed tabs from structureSections|renders structure-driven tabs"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-1619 · AST-1616

**Parent:** [AST-1616](https://linear.app/astralcareermatch/issue/AST-1616). **Publish:** `origin/sub/AST-1616/AST-1619-editable-entity-type-modal`.

Scheduled Actions Add/Edit modal: Entity Type is an editable `<select>` bound to `stateOptions` keys (not readOnly); changing entity refreshes Input State options and clears an invalid `trigger_state`; POST/PUT Save bodies include `entity_type`. Candidate on Add stays read-only / context-bound. API persist = sibling **AST-1618**.

| AC | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| AC1 editable Entity Type (§6c) | `<select>` not `readOnly` text | `AdminScheduledActions.tsx` | **`test_AdminScheduledActions.test.tsx` — `AST-1619 editable Entity Type` → `Add Task Entity Type is a select (not readOnly text)`** |
| AC2 Input State follows entity | Options swap; invalid trigger cleared | same | **`changing Entity Type swaps Input State options and clears invalid trigger`** |
| AC3 Candidate bound on Add | Candidate row stays `readOnly` | same | asserted in AC1 case |
| Save payload | POST/PUT include `entity_type` | same | **`Edit Save PUT body includes entity_type`**, **`Add Save POST body includes entity_type`** |

**Broken / obsolete (Betty revised this pass):** modal `combobox` indices — Entity Type inserted at index 1; Input State is now `[2]` in **`add task modal: company task sets WATCH state options`**, **AST-780** add-POST toast, **AST-804** candidate Input State case.

**Integration:** no existing scenario covers Scheduled Actions Entity Type modal — do not invent new integration coverage.

## QA test manifest

1. Routed Scheduled Actions page (§6c): `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — pattern **`AST-1619`**
2. Revised combobox-index regressions: same file — **`company task sets WATCH`**, **`AST-780` add save POST fails**, **`AST-804 candidate Input State`**

**AST-1619** narrowed run (from `src/ui/frontend/`):

```bash
npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-1619|company task sets WATCH|add save POST fails|AST-804 candidate Input State"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-1634 · AST-1629

**Parent:** [AST-1629 — Migrate candidate_data.context.strengths to use the artifact table](https://linear.app/astralcareermatch/issue/AST-1629). **Publish:** `origin/sub/AST-1629/AST-1634-strengths-contexttextpage-plain-text-path`.

Strengths page passes `bodyShape="plain_text"` into `ContextTextPage`; shared editor keeps `{ context: { strengths } }` GET/PUT (AST-1633 operative intercept); empty/whitespace Save disabled + client toast; `ArtifactEditor` untouched; sibling context pages omit `bodyShape`. Catalog/API: siblings **AST-1632** / **AST-1633**.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed Strengths page (§6c) — load / save reload / empty gate | `CandidateStrengths.tsx` | **`test_CandidateStrengths.test.tsx`** — `AST-1634` |
| Shared plain_text empty gate + legacy callers | `ContextTextPage.tsx` | **`test_ContextTextPage.test.tsx`** — `AST-1634` |

**Broken / obsolete this pass:** none — prior Strengths render case expanded under AST-1634 names.

**Integration:** none — no existing scenario asserts Strengths ContextTextPage `bodyShape`; do not invent.

## QA test manifest

1. Routed Strengths page (§6c): `tests/component/frontend/pages/test_CandidateStrengths.test.tsx` — pattern **`AST-1634`**
2. Shared ContextTextPage plain_text gate: `tests/component/frontend/components/test_ContextTextPage.test.tsx` — pattern **`AST-1634`**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateStrengths.test.tsx \
  ../../../tests/component/frontend/components/test_ContextTextPage.test.tsx \
  --testNamePattern="AST-1634"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/frontend/pages.md` — *(filled after publish)*

### AST-1650 · AST-1647

**Parent:** [AST-1647 — Migrate candidate bio summary to use the artifact table and remove from candidate profile page](https://linear.app/astralcareermatch/issue/AST-1647). **Publish:** `origin/sub/AST-1647/AST-1650-bio-summary-page-route`.

Thin `CandidateBioSummary.tsx` (`contextKey="bio_summary"`, `bodyShape="plain_text"`) + route `candidate/bio_summary`. Reuses `ContextTextPage` (no edits this ticket — shared gate covered by **AST-1634**). Nav/catalog: **AST-1648**. Operative PUT/GET: **AST-1649**. `ArtifactEditor` untouched.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed Bio Summary page (§6c) — load / save reload / empty gate | `CandidateBioSummary.tsx` | **`test_CandidateBioSummary.test.tsx`** — `AST-1650` |

**Broken / obsolete this pass:** none — profile Bio Summary section already removed in config (**AST-1648**); page-level profile Vitest mocks are local fixtures, not live `DATA_SHAPES`.

**Integration:** none — no existing scenario asserts Bio Summary route / ContextTextPage wrapper; do not invent.

## QA test manifest

1. Routed Bio Summary page (§6c): `tests/component/frontend/pages/test_CandidateBioSummary.test.tsx` — pattern **`AST-1650`**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateBioSummary.test.tsx \
  --testNamePattern="AST-1650"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/frontend/pages.md` — *(filled after publish)*

### AST-1656 · AST-1642

**Parent:** [AST-1642 — Migrate candidate_data.context.deal_breakers to use the artifact table](https://linear.app/astralcareermatch/issue/AST-1642). **Publish:** `origin/sub/AST-1642/AST-1656-deal-breakers-contexttextpage-wire-up`.

Deal Breakers page passes `bodyShape="plain_text"` into `ContextTextPage`; shared editor keeps `{ context: { deal_breakers } }` GET/PUT (AST-1655 operative intercept); empty/whitespace Save disabled via shared gate; `ArtifactEditor` / `ContextTextPage` untouched this ticket. Catalog/API: siblings **AST-1654** / **AST-1655**. Mirror AST-1634.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed Deal Breakers page (§6c) — load / save reload / empty gate / bodyShape assert | `CandidateDealBreakers.tsx` | **`test_CandidateDealBreakers.test.tsx`** — `AST-1656` |
| Shared plain_text empty gate (existing) | `ContextTextPage.tsx` | **`test_ContextTextPage.test.tsx`** — `AST-1634` |

**Broken / obsolete this pass:** prior Deal Breakers render-only case expanded under AST-1656 names.

**Integration:** none — no existing scenario asserts Deal Breakers ContextTextPage `bodyShape`; do not invent.

## QA test manifest

1. Routed Deal Breakers page (§6c): `tests/component/frontend/pages/test_CandidateDealBreakers.test.tsx` — pattern **`AST-1656`**
2. Shared ContextTextPage plain_text gate (existing): `tests/component/frontend/components/test_ContextTextPage.test.tsx` — pattern **`AST-1634`**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateDealBreakers.test.tsx \
  ../../../tests/component/frontend/components/test_ContextTextPage.test.tsx \
  --testNamePattern="AST-1656|AST-1634"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/frontend/pages.md` — *(filled after publish)*

### AST-1653 · AST-1641

**Parent:** [AST-1641 — Migrate candidate_data.context.priorities to use the artifact table](https://linear.app/astralcareermatch/issue/AST-1641). **Publish:** `origin/sub/AST-1641/AST-1653-priorities-contexttextpage-wire-up`.

Priorities page passes `bodyShape="plain_text"` into `ContextTextPage`; shared editor keeps `{ context: { priorities } }` GET/PUT (AST-1652 operative intercept); empty/whitespace Save disabled via shared gate; `ArtifactEditor` / `ContextTextPage` untouched this ticket. Catalog/API: siblings **AST-1651** / **AST-1652**. Mirror AST-1634 / AST-1656.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed Priorities page (§6c) — load / save reload / empty gate / bodyShape assert | `CandidatePriorities.tsx` | **`test_CandidatePriorities.test.tsx`** — `AST-1653` |
| Shared plain_text empty gate (existing) | `ContextTextPage.tsx` | **`test_ContextTextPage.test.tsx`** — `AST-1634` |

**Broken / obsolete this pass:** prior Priorities render-only case expanded under AST-1653 names.

**Integration:** none — no existing scenario asserts Priorities ContextTextPage `bodyShape`; do not invent.

## QA test manifest

1. Routed Priorities page (§6c): `tests/component/frontend/pages/test_CandidatePriorities.test.tsx` — pattern **`AST-1653`**
2. Shared ContextTextPage plain_text gate (existing): `tests/component/frontend/components/test_ContextTextPage.test.tsx` — pattern **`AST-1634`**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidatePriorities.test.tsx \
  ../../../tests/component/frontend/components/test_ContextTextPage.test.tsx \
  --testNamePattern="AST-1653|AST-1634"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/frontend/pages.md` — *(filled after publish)*

### AST-1660 · AST-1643

**Parent:** [AST-1643 — Migrate candidate_data.context.ideal_day to use the artifact table](https://linear.app/astralcareermatch/issue/AST-1643). **Publish:** `origin/sub/AST-1643/AST-1660-ideal-day-contexttextpage-wire-up`.

Ideal Day page passes `bodyShape="plain_text"` into `ContextTextPage`; shared editor keeps `{ context: { ideal_day } }` GET/PUT (AST-1659 operative intercept); empty/whitespace Save disabled via shared gate; `ArtifactEditor` / `ContextTextPage` untouched this ticket. Catalog/API: siblings **AST-1658** / **AST-1659**. Mirror AST-1634 / AST-1656.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed Ideal Day page (§6c) — load / save reload / empty gate / bodyShape assert | `CandidateIdealDay.tsx` | **`test_CandidateIdealDay.test.tsx`** — `AST-1660` |
| Shared plain_text empty gate (existing) | `ContextTextPage.tsx` | **`test_ContextTextPage.test.tsx`** — `AST-1634` |

**Broken / obsolete this pass:** prior Ideal Day AST-1366 render/save cases expanded under AST-1660 names (plain_text empty gate + bodyShape source assert).

**Integration:** none — no existing scenario asserts Ideal Day ContextTextPage `bodyShape`; do not invent.

## QA test manifest

1. Routed Ideal Day page (§6c): `tests/component/frontend/pages/test_CandidateIdealDay.test.tsx` — pattern **`AST-1660`**
2. Shared ContextTextPage plain_text gate (existing): `tests/component/frontend/components/test_ContextTextPage.test.tsx` — pattern **`AST-1634`**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateIdealDay.test.tsx \
  ../../../tests/component/frontend/components/test_ContextTextPage.test.tsx \
  --testNamePattern="AST-1660|AST-1634"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/frontend/pages.md` — *(filled after publish)*

### AST-1666 · AST-1645

**Parent:** [AST-1645 — Migrate candidate_data.context.writing_preferences to use the artifact table](https://linear.app/astralcareermatch/issue/AST-1645). **Publish:** `origin/sub/AST-1645/AST-1666-writing-preferences-contexttextpage-wire-up`.

Writing Preferences page passes `bodyShape="plain_text"` into `ContextTextPage`; shared editor keeps `{ context: { writing_preferences } }` GET/PUT (AST-1665 operative intercept); empty/whitespace Save disabled via shared gate; `ArtifactEditor` / `ContextTextPage` untouched this ticket. Catalog/API: siblings **AST-1664** / **AST-1665**. Mirror AST-1634 / AST-1660.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed Writing Preferences page (§6c) — load / save reload / empty gate / bodyShape assert | `CandidateWritingPreferences.tsx` | **`test_CandidateWritingPreferences.test.tsx`** — `AST-1666` |
| Shared plain_text empty gate (existing) | `ContextTextPage.tsx` | **`test_ContextTextPage.test.tsx`** — `AST-1634` |

**Broken / obsolete this pass:** none — page was a ContextTextPage caller without `bodyShape`; new Vitest covers the wire-up.

**Integration:** none — no existing scenario asserts Writing Preferences ContextTextPage `bodyShape`; do not invent.

## QA test manifest

1. Routed Writing Preferences page (§6c): `tests/component/frontend/pages/test_CandidateWritingPreferences.test.tsx` — pattern **`AST-1666`**
2. Shared ContextTextPage plain_text gate (existing): `tests/component/frontend/components/test_ContextTextPage.test.tsx` — pattern **`AST-1634`**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateWritingPreferences.test.tsx \
  ../../../tests/component/frontend/components/test_ContextTextPage.test.tsx \
  --testNamePattern="AST-1666|AST-1634"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/frontend/pages.md` — *(filled after publish)*

### AST-1663 · AST-1644

**Parent:** [AST-1644 — Migrate candidate_data.context.backstory to use the artifact table](https://linear.app/astralcareermatch/issue/AST-1644). **Publish:** `origin/sub/AST-1644/AST-1663-backstory-contexttextpage-wire-up`.

Backstory page passes `bodyShape="plain_text"` into `ContextTextPage`; shared editor keeps `{ context: { backstory } }` GET/PUT (AST-1662 operative intercept); empty/whitespace Save disabled via shared gate; `ArtifactEditor` / `ContextTextPage` untouched this ticket. Catalog/API: siblings **AST-1661** / **AST-1662**. Mirror AST-1634 / AST-1660.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed Backstory page (§6c) — load / save reload / empty gate / bodyShape assert | `CandidateBackstory.tsx` | **`test_CandidateBackstory.test.tsx`** — `AST-1663` |
| Shared plain_text empty gate (existing) | `ContextTextPage.tsx` | **`test_ContextTextPage.test.tsx`** — `AST-1634` |

**Broken / obsolete this pass:** prior Backstory render-only case expanded under AST-1663 names (plain_text empty gate + bodyShape source assert).

**Integration:** none — no existing scenario asserts Backstory ContextTextPage `bodyShape`; do not invent.

## QA test manifest

1. Routed Backstory page (§6c): `tests/component/frontend/pages/test_CandidateBackstory.test.tsx` — pattern **`AST-1663`**
2. Shared ContextTextPage plain_text gate (existing): `tests/component/frontend/components/test_ContextTextPage.test.tsx` — pattern **`AST-1634`**

```bash
cd src/ui/frontend && npx vitest run \
  ../../../tests/component/frontend/pages/test_CandidateBackstory.test.tsx \
  ../../../tests/component/frontend/components/test_ContextTextPage.test.tsx \
  --testNamePattern="AST-1663|AST-1634"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/frontend/pages.md` — *(filled after publish)*

---

### AST-1669 · AST-1636

**Parent:** [AST-1636 — Bind new Slack contacts to existing candidates by metadata before creating a prospect](https://linear.app/astralcareermatch/issue/AST-1636). **Publish:** `origin/sub/AST-1636/AST-1669-manage-candidates-slack-bind-dropdown`.

Manage Candidates add/edit Slack username `<select>` from `GET /api/admin/contact/unbound_slack_users`; stamps both `contact.slack_user_id` + `contact.slack_username` on save; edit prepends current bind; empty selection omits Slack keys; no Slack Web API from React. Unbound API: **`docs/test-bible/ui/api/api_contact.md`** § AST-1668. Poster pool: **`docs/test-bible/external/slack.md`** § AST-1667.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed Manage Candidates page (§6c) — dropdown + bind stamp + omit-on-empty | `AdminManageCandidates.tsx` | **`test_AdminManageCandidates.test.tsx`** — **`AST-1669`** |
| Unbound GET mock on existing suites | same | revised **`mockApi`** / suite mocks stub `/api/admin/contact/unbound_slack_users` |

**Broken / obsolete this pass:** existing Add/Edit opens would `Unhandled api` unbound GET — revised mocks return `{ users: [] }` by default.

**Integration:** none — no existing scenario asserts Manage Candidates Slack bind; do not invent.

## QA test manifest

1. Routed Manage Candidates Slack bind (§6c): `tests/component/frontend/pages/test_AdminManageCandidates.test.tsx` — pattern **`AST-1669`**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageCandidates.test.tsx \
  --testNamePattern='AST-1669'
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/frontend/pages.md` — *(filled after publish)*

### AST-1704 · AST-1640

**Parent:** [AST-1640 — Job source_entity parent](https://linear.app/astralcareermatch/issue/AST-1640). **Publish:** `origin/sub/AST-1640/AST-1704-track-routing-job-detail-jobs-api-consumers`.

`JobsJobDetail` prefetch prefers `company_id` over legacy `company` for admin candidate align (§6c routed page). FE href chrome: **`docs/test-bible/frontend/components.md`** § AST-1704. Primary manifest: **`docs/test-bible/core/consult.md`** § AST-1704.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed deeplink host — company_id align | `JobsJobDetail.tsx` | **`test_JobsJobDetail.test.tsx`** — **`AST-1704`** |

**Broken / obsolete this pass:** none.

**Integration:** none.

---

### AST-1728 · AST-1721 (qa-fix bug-repro — AdminTelescope §6c)

| Area | Component tests |
| --- | --- |
| Page module exists / loads | `tests/component/frontend/pages/test_AdminTelescope.test.tsx` — **`AST-1728: AdminTelescope page module exports a component`** (**bug-repro**) |
| Path / file presence (py) | `test_api_admin_telescope.py::test_admin_telescope_page_module_exists` + `test_routes_register_admin_telescope` |

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminTelescope.test.tsx
```

---

### AST-1730 · AST-1721 (qa-fix bug-repro — scrollable selectable response)

**Board REVISE:** raw / full-JSON panes must be read-only scrollable wrapping `<textarea className="admin-telescope-pre">` (`maxHeight: 60vh`, `overflow: auto`, `white-space: pre-wrap`).

| Area | Component tests |
| --- | --- |
| Raw pane textarea + scroll/wrap styles | `test_AdminTelescope.test.tsx` — **`AST-1730: raw response is read-only scrollable wrapping textarea`** (**bug-repro**) |
| Full JSON pane same shape | `test_AdminTelescope.test.tsx` — **`AST-1730: full JSON dump uses the same read-only textarea shape`** (**bug-repro**) |

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminTelescope.test.tsx
```

---

### AST-1734 · AST-1721 (qa-fix bug-repro — page scroll unlock)

**Board REVISE:** root `.list-page` must use `height: auto` / `overflow: visible` (or free-flow shell) so `.content` scrolls; AST-1730 only asserts textarea inner scroll.

| Area | Component tests |
| --- | --- |
| Page scroll unlock on root | `test_AdminTelescope.test.tsx` — **`AST-1734: root unlocks page scroll (list-page height auto / overflow visible)`** (**bug-repro**) |

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminTelescope.test.tsx
```

---

### AST-1744 · AST-1721 (qa-fix bug-repro — Admin single Tag primary)

**Board REVISE:** remove separate Selector; Tag is sole primary; Class always enabled (secondary).

| Area | Component tests |
| --- | --- |
| No Selector; Class enabled with Tag | `test_AdminTelescope.test.tsx` — **`AST-1744: single Tag primary + Class always enabled; no Selector slot`** (**bug-repro**) |

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminTelescope.test.tsx -t 'AST-1744'
```

---

### AST-1749 · AST-1741

**AST-1976:** the same page file adds the landed-job **Job State** cell and an in-page job report link. Coverage: § AST-1976 below.

**Parent:** [AST-1741 — Add "Meteorites" to the Jobs navigation](https://linear.app/astralcareermatch/issue/AST-1741/add-meteorites-to-the-jobs-navigation). **Publish:** `origin/sub/AST-1741/AST-1749-jobs-meteorites-nav-list-page-detail-modal`.

Jobs → Meteorites routed page (`JobsMeteorites.tsx`): candidate-scoped list from AST-1748 APIs, empty honesty, candidate switch refetch, row → detail modal. Nav/route/config: **`docs/test-bible/utils/config.md`** § AST-1749. Modal: **`docs/test-bible/frontend/components.md`** § AST-1749. §6c page render required.

| Area | Source | Component tests |
| --- | --- | --- |
| Page list / empty / candidate switch / modal open | `JobsMeteorites.tsx` | **`test_JobsMeteorites.test.tsx`** |
| Route registration | `routes.tsx` | **`test_routes.test.tsx`** (`jobs/meteorites`) |

**Broken / obsolete:** none — additive page + route.

**Integration:** `test_candidate_nav_api.py` asserts In Review by path lookup — not an exhaustive Jobs item list; no revision. Do not invent new integration scenarios.

## QA test manifest

1. Page: `tests/component/frontend/pages/test_JobsMeteorites.test.tsx`
2. Modal: `tests/component/frontend/components/test_MeteoriteDetailModal.test.tsx`
3. Nav config: `tests/component/utils/test_config.py::TestAst1749JobsMeteoritesNav`
4. Route: `tests/component/frontend/test_routes.test.tsx` (jobs/meteorites assert)

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_JobsMeteorites.test.tsx \
  ../../../tests/component/frontend/components/test_MeteoriteDetailModal.test.tsx \
  ../../../tests/component/frontend/test_routes.test.tsx
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1749JobsMeteoritesNav \
  -q
```

**Pass criterion:** Vitest + pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):** fill after `merge-tests`.

### AST-1782 · AST-1766 (Scheduled Actions mute AUTO + Run/Sweep on empty_render)

**Parent:** [AST-1766 — Dispatch Validation](https://linear.app/astralcareermatch/issue/AST-1766). **Publish:** `origin/sub/AST-1766/AST-1782-scheduled-actions-disable-auto-run-sweep`.

Routed page **`AdminScheduledActions.tsx`** honors list boolean `empty_render` (AST-1780): mute + block AUTO badge and Run/Sweep; handler no-ops; Debug/Stop/Drain unchanged. No client `resolve_tokens` / `TOKEN_SOURCES`. Predicate/API: siblings **AST-1779** / **AST-1780**.

| Area | Source | Component tests |
| --- | --- | --- |
| empty_render blocks AUTO + Run | `AdminScheduledActions.tsx` | **`test_AdminScheduledActions.test.tsx`** — **`AST-1782 empty_render mutes AUTO and Run/Sweep`** (`blocks…`, `allows…`, `Debug…`, `source file…`) |

**Broken / obsolete:** none.

**Integration:** none — no existing scenario asserts Scheduled Actions `empty_render` mute; do not invent new integration coverage.

## QA test manifest

1. Routed page (§6c) empty_render mute suite: `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — describe **`AST-1782 empty_render mutes AUTO and Run/Sweep`**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  -t 'AST-1782'
```

**Pass criterion:** Vitest green on manifest — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):** fill after `merge-tests` —
- `docs/test-bible/frontend/pages.md`

---

### AST-1789 · AST-1786

**Parent:** [AST-1786 — Manage Candidates Snapshot Slack Channel + candidate mapping](https://linear.app/astralcareermatch/issue/AST-1786/manage-candidates-snapshot-slack-channel-candidate-mapping). **Publish:** `origin/sub/AST-1786/AST-1789-manage-candidates-channel-column-s-snapshot`.

Manage Candidates UI: `slack_username` list column (em dash when empty); Slack channel `<select>` from admin GET; membership `role="alert"` warn (unbound / not_member); stamp `contact.slack_channel_id` + `contact.slack_channel_name` on save; row **S** `icon-control` copies snapshot JSON via admin GET. No Slack Web API in TSX. Core/API/shapes: siblings AST-1787 / AST-1788.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed Manage Candidates page (§6c) — column / select+warn / S clipboard | `AdminManageCandidates.tsx` | **`test_AdminManageCandidates.test.tsx`** — **`AST-1789`** |
| Drift: row icon-control set includes **S** | same | revised **`AST-1302`** |
| Drift: add/edit mocks stub `/slack_channels` | same | existing suites that open Add/Edit |

**Broken / obsolete this pass:** AST-1302 icon-control assert omitted **S**; Add/Edit mocks needed `/api/admin/contact/slack_channels` stub after product load on modal open.

**Integration:** no existing scenario exercises Manage Candidates Slack channel UI — no revision; do not invent.

## QA test manifest

1. Routed Manage Candidates channel UX (§6c): `tests/component/frontend/pages/test_AdminManageCandidates.test.tsx` — pattern **`AST-1789`** (+ revised **`AST-1302`**)

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageCandidates.test.tsx
```

**Pass criterion:** Vitest green on file — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/frontend/pages.md` — *(filled after publish)*

---

### AST-1818 · AST-1817 (Scheduled Actions Invalid label, zero-avail Run block, Avail All default, Task-only freeze)

**Parent:** [AST-1817 — Invalid vs 0 Avail scheduled actions](https://linear.app/astralcareermatch/issue/AST-1817). **Publish:** `origin/sub/AST-1817/AST-1818-scheduled-actions-invalid-label-zero-avail-run-block`.

Routed page **`AdminScheduledActions.tsx`** only: `empty_render` rows show a full-opacity disabled **`btn secondary in-row`** button named **Invalid** (wins over Run/Sweep); valid rows with `available_count` 0 get the muted (0.25) disabled Run; Avail filter initial state `""` (All) — `> 0` predicate unchanged; `FROZEN_DATA_COLUMNS` 3 → 1 (Task only; shared `list_table_frozen_data_columns` untouched). No API / config / `listTableLayout.ts` / `App.css` change.

| Area | Source | Component tests |
| --- | --- | --- |
| AC1–2 Invalid button (name, classes, disabled, no 0.25, no `/run` POST) | `AdminScheduledActions.tsx` | **`test_AdminScheduledActions.test.tsx`** — **`AST-1782 … > blocks AUTO toggle and shows disabled Invalid button when empty_render is true`** (revised) |
| AC3 zero-avail Run muted/disabled, no POST | same | **`AST-1818 zero-avail Run block > valid row with available_count 0 …`** (new) |
| AC4 avail > 0 Run POSTs | same | **`AST-1782 … > allows AUTO toggle and Run when empty_render is false`** (existing) |
| AC5 running zero-avail row Stop POSTs | same | **`AST-1818 zero-avail Run block > running row with available_count 0 …`** (new) |
| AC6–7 Avail default All; `> 0` still filters | same | **`AST-887 Avail > 0 filter`** (4, revised); **`AST-894 expand-all on landing (Avail default All per AST-1818)`** (revised); **`test_AdminScheduledActions_AST1104.test.tsx`** landing value (revised) |
| AC8 only Task frozen, no sticky `left` on Entity/State | same | **`AST-647: phase table freezes only the Task column`** (renamed); **`AST-746`**, **`AST-760`** (revised) |

**Broken / obsolete this pass (revised, not deleted):** AST-647 / AST-746 / AST-760 (three frozen columns + measured `left` on Entity/State); AST-887 ×4, AST-894 ×2, AST-1104 landing (default `gt0`); AST-1782 `blocks…` (button named Run). **Pre-existing drift fixed:** AST-751 + AST-768 default-sort cases read Candidate at `cells[11]` — Mode column (`fabcf747`) shifted it; now `cells[length - 3]`.

**Integration:** none — no existing scenario exercises Scheduled Actions frontend; do not invent.

## QA test manifest

1. Full Scheduled Actions routed-page suite (§6c; AC 11): both `test_AdminScheduledActions*.test.tsx` files — 71 cases.
2. AC 9 / AC 10 gates (product diff shape).
3. `npm run build` + `npm run lint` (lint: no new problems vs `origin/dev`; engineer baseline 33).

```bash
cd src/ui/frontend && npx vitest run --config vite.config.ts test_AdminScheduledActions
git diff origin/dev -- src/ui/frontend/src/App.css src/ui/frontend/src/lib/listTableLayout.ts src/ui/api src/utils/config.py
git diff origin/dev -- src/ui/frontend/src/pages/AdminScheduledActions.tsx | rg -n '^\+.*(#[0-9a-fA-F]{3,6}|rgb\()'
cd src/ui/frontend && npm run build && npm run lint
```

**Pass criterion:** 71/71 Vitest green; both diffs/greps empty; build green; lint count unchanged — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):** see issue doc `## QA test manifest`.

---

### AST-1819 · AST-1817 (qa-fix bug-repro — Invalid tooltip lists missing tokens)

**Parent:** [AST-1817](https://linear.app/astralcareermatch/issue/AST-1817). **Publish:** `origin/sub/AST-1817/AST-1819-invalid-button-missing-token-tooltip`.

Scheduled Actions: native `title` on the Run-cell wrapper `<div>` of an `empty_render` row — `empty_tokens.join(", ")`, or `Could not validate prompts` when the list is empty; no `title` while the row is running. The Invalid button itself is unchanged (AST-1818 AC 1–2 still hold).

| Area | Source | Component tests |
| --- | --- | --- |
| Token-list title; button keeps name Invalid, disabled, no own title `[bug-repro]` | `AdminScheduledActions.tsx` | **`test_AdminScheduledActions.test.tsx`** — **`AST-1819 Invalid tooltip lists missing tokens > wrapper title is the comma-separated token list…`** |
| Empty list fallback `[bug-repro]` | same | **`… > empty token list falls back to 'Could not validate prompts'`** |
| No title while running (guard, green pre-fix) | same | **`… > no tooltip while the Invalid row is running…`** |

```bash
cd src/ui/frontend && npx vitest run --config vite.config.ts test_AdminScheduledActions
```

### AST-1830 · AST-1824 (Scheduled Actions sweep_hrs input + list column)

**Parent:** [AST-1824](https://linear.app/astralcareermatch/issue/AST-1824). **Publish:** `origin/sub/AST-1824/AST-1830-sweep-interval-admin-api-ui`.

`AdminScheduledActions.tsx`: a `Sweep (hrs)` numeric input in the Add and Edit modals (blank = off; prefilled from the row on Edit). Save sends `sweep_hrs` as a number, or `null` when blank. A sortable **Sweep** list column shows the value or `—`. Run/Sweep button logic (`sweepDisabled`) is unchanged.

| Area | Component tests |
| --- | --- |
| List shows value or `—`; Sweep header sorts both directions | **`test_AdminScheduledActions.test.tsx`**: **`AST-1830 sweep_hrs modal input + list column > list shows sweep_hrs or — and the Sweep column sorts`** |
| Edit prefills; PUT sends new value; clearing sends `null` | **`… > edit modal prefills sweep_hrs, PUT sends the new value, and clearing sends null`** |
| Add starts blank; POST sends value; blank sends `null` | **`… > add modal starts blank and POST sends sweep_hrs (null when blank)`** |

All three fail on the pre-AST-1830 page and pass with it (checked at QA). **Broken / obsolete:** none. The existing 74 tests across both Scheduled Actions files stay green.

Primary numbered manifest: **`docs/test-bible/ui/api/api_admin.md`** § AST-1830.

**AST-1874 (pointer):** `JobsRecommended` imports `formatPhaseScore` from `lib/recommendedJobReport` (list cells unchanged); row-click and `JobsJobDetail` deeplink tests now expect the report to open on **Analysis**. Manifest: **`docs/test-bible/frontend/components.md`** § AST-1874.

### AST-1880 · AST-1851 (admin pickers + per-server keys)

| Page | Tests |
| --- | --- |
| `AdminAgentPrompts.tsx`: Model select, then that model's own sizes (from `/agents/models` `order`). A model change keeps the size if offered, otherwise uses the first size plus its defaults. Model column label; POST/PUT carry `model_id` + `brain_setting` | `test_AdminAgentPrompts.test.tsx`: fixtures moved to the keyed catalog (`brain_settings` mocks removed); new **AST-1880: Add picks a model…**, **AST-1880: Edit shows the agent's model + size…** |
| `AdminManageCandidates.tsx`: one key field per `api_keys` server (label, set/not set, Show, Clear only when set, per-server confirm). PUT sends only the changed servers (`""` = clear). The column lists the set labels | `test_AdminManageCandidates.test.tsx`: main CRUD test drives the DeepSeek type + Show and the Kimi Clear → `api_keys: {kimi: "", deepseek: "sk-ds-new"}`; new **AST-1880: no keys set…** (no Clear, Save omits `api_keys`); **AST-1880: API Key column lists the labels…** is **red: product bug** (renderer still tests `val === "Set"`) |
| `AdminScheduledActions.tsx`: Invalid tooltip prefers `invalid_reason`, else tokens, else "Could not validate prompts" | `test_AdminScheduledActions.test.tsx` › AST-1819 describe: new **AST-1880: missing platform key reason wins…**, **AST-1880: empty invalid_reason falls back to tokens** |
| `AdminSessionResumePaste.tsx`: Parse needs a selected candidate (disabled with a title otherwise); POST body `{resume_text, candidate_id}` | `test_AdminSessionResumePaste.test.tsx`: `mockApis` serves a candidate list; Parse-success test asserts the exact body; new **AST-1880: no selected candidate keeps Parse disabled…** |

Manifest: **`docs/test-bible/ui/api/api_admin.md`** § AST-1880.

### AST-1901 · AST-1851 (bug: Manage Candidates keys as an array)

> Supersedes the AST-1880 `AdminManageCandidates` row above (no fixed per-server fields; the column red is closed).

> **AST-1920:** the UI half below (stored-only fields, "Add API key for…" picker, `(new)` rows, Remove) is superseded. The Edit modal shows one key field per catalog server again; see § AST-1920. The array storage and PUT contract stay.

`test_AdminManageCandidates.test.tsx`: the fixture `api_keys` is `[{server, label}]` (Kimi, OpenRouter). A file-local `installBaseApiMocks` wrapper serves `/api/admin/agents/models`; the catalog has two DeepSeek models, so the picker de-dupes by server.
- **Main CRUD test:** fields appear only for stored entries (Clear on each). The picker lists servers without a row, in catalog order. Adding DeepSeek gives a "(new)" field (no Clear; Show; typed key). Kimi Clear goes through the confirm dialog. The PUT carries `api_keys: [{kimi, ""}, {deepseek, "sk-ds-new"}]`.
- **AST-1901: API Key column joins the stored entries' labels.**
- **AST-1901: no keys…:** Not set, no key fields, all four servers in the picker, and Save omits `api_keys`.
- **AST-1901: Remove drops an unsaved row…:** the picker disappears once every server has a row. Remove returns that server to the picker, and a blank added row isn't sent.

Manifest: **`docs/test-bible/data/database/candidates.md`** § QA test manifest (AST-1901).

### AST-1909 · AST-1851 (bug: Manage Task modal model + brain size)

**Retired by AST-1939.** The modal's Model / Brain size selects, the agent catalog/row fetches, and the post-save agent `PUT` were removed (Susan: the agent row is the only model source). The 7-test **AST-1909 task modal model + brain size** describe and its file-local catalog/agent mock wrapper are gone. Current coverage: § AST-1939 below.

### AST-1939 · AST-1937 (remove the Manage Task model picker)

`AdminTaskPrompts.tsx`: the modal drops the AST-1909 **Model** / **Brain size** selects, the "Applies to agent" hint, the `GET /api/admin/agents/models` and `GET /api/admin/agents/<id>` fetches, and the post-save `PUT /api/admin/agents/<id>`. The Agent select, the task `PUT` (which still carries `agent_id`), and the list's read-only **Model** column (`model_code`) are unchanged.

| AC 9 bullet | Tests (`test_AdminTaskPrompts.test.tsx`, describe **AST-1939 no task-level model picker**) |
| --- | --- |
| No Model / Brain size select in the modal | **modal has no Model or Brain size select and fetches neither the catalog nor the agent row** |
| Save issues only the task update, no `/api/admin/agents/<id>` request | **changing the Agent then saving issues only the task PUT — no agent request** |
| List keeps the read-only Model column | **task list keeps the read-only Model column showing model_code** |
| No `agents/models` / `editModelId` / `editBrainSetting` / `loadAgentModel` / `Brain size` in the page | grep in manifest below |

The first two tests are red against the `origin/dev` page and green on the publish tip; the column test is a guard and stays green on both (checked at QA). **Broken / obsolete (revised):** the 7 AST-1909 modal tests (removed, replaced by the describe above) and the file-local `installBaseApiMocks` wrapper (removed; the file now uses `test-utils` `installBaseApiMocks` directly, which throws on any unhandled URL). The other 12 tests in the file are unchanged and green. **Integration:** no scenario covers the Manage Task modal, so nothing to revise.

## QA test manifest (AST-1939)

1. **Page Vitest (§6c routed page):** the whole file, 15 tests (12 existing + 3 AST-1939).
2. **Manage Agents unchanged:** `test_AdminAgentPrompts.test.tsx` green (Boundaries).
3. **AC 9 grep** on the publish tip — expect nothing.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx
cd ../../.. && rg -n "agents/models|editModelId|editBrainSetting|loadAgentModel|Brain size" src/ui/frontend/src/pages/AdminTaskPrompts.tsx
```

**Pass criterion:** both files green, grep empty.

### AST-1908 · AST-1899 (Save to Candidate on Session Resume Paste)

`AdminSessionResumePaste.tsx`: a fourth row button, **Save to Candidate** (after Open HTML), PUTs the last parse to the existing `PUT /api/candidates/<selectedId>/data` with `{artifacts: {resume_structure: {sections}, base_resume}}`. The body has no `accent_color` and no `artifact_id`, and `base_resume` is sent as parsed. A `saving` state labels the button **Saving…** and disables all four buttons. Save is also disabled with no candidate, with no `lastParse`, or while Parse / Open HTML is in flight. OK → success toast. Non-OK → the JSON `error` (else `HTTP <status>`) goes to both the error toast and the inline error line, and `lastParse` is kept. The intro copy drops "does not save to the database". No backend change: the route's ingest/filter/operative write is reused, and its coverage stays with `api_candidate`.

| AC | Tests (`test_AdminSessionResumePaste.test.tsx`, AST-987 describe) |
| --- | --- |
| 1 Button present + gated | **AST-1908 AC1: Save to Candidate is the fourth button…** · **…no selected candidate keeps Save disabled…** · **…Save disabled while Parse is in flight** · **…Save disabled while Open HTML is in flight** |
| 2 Correct request (+ Saving… lock, success toast) | **AST-1908 AC2/AC6: one PUT with the exact parse body…** |
| 6 Error feedback | **AST-1908 AC6: 400 error shows server message in toast + inline…** |
| 8 Copy | **AST-1908 AC8: intro copy names Save to Candidate…** |
| 3 / 4 / 5 persistence, layout, experience | UAT (DB row `current=1`, Base Resume Content editor) — product reuses the existing route unchanged |
| 7 No backend change | grep/diff in manifest below |

All 7 new tests are red against the `origin/dev` page and green on the publish tip (checked at QA). **Broken / obsolete:** none. The AST-1035 button-order assertion only lists the three original buttons, and the 7 existing tests stay green. **Integration:** no scenario covers Session Resume Paste or the candidate data PUT from this page, so nothing to revise.

## QA test manifest (AST-1908)

1. **Page Vitest (§6c routed page):** the whole file, 14 tests (7 existing + 7 AST-1908).
2. **AC7 / AC8 greps** on the publish tip.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminSessionResumePaste.test.tsx
cd ../../.. && git diff origin/dev --stat -- src/ui/api src/core src/data src/utils   # expect empty
grep -rn "session_resume/save" src/                                                    # expect nothing
grep -n "does not save to the database" src/ui/frontend/src/pages/AdminSessionResumePaste.tsx   # expect nothing
```

**Pass criterion:** 14/14 green and all three commands print nothing.

### AST-1917 · AST-1875 (Scheduled Actions header Max AUTO threads dropdown)

**Parent:** [AST-1875](https://linear.app/astralcareermatch/issue/AST-1875). **Publish:** `origin/sub/AST-1875/AST-1917-header-dropdown`. `AdminScheduledActions.tsx` loads `GET /api/admin/scheduler/auto_thread_cap` once on mount (failure → dropdown hidden, no toast) and renders a "Max AUTO threads" `<select>` with options `min..max` from the payload. A pick POSTs `{"max_auto_threads": <number>}` optimistically; success shows the server-returned value, failure reverts and toasts. Backend contract: [`../ui/api/api_admin.md`](../ui/api/api_admin.md) § AST-1916.

| AC | Source | Component tests (`tests/component/frontend/pages/test_AdminScheduledActions_AST1917.test.tsx`) |
| --- | --- | --- |
| 1 default pre-selected · 2 exactly 1..100 | page mount load + `<select>` | **`AC1/AC2: shows the live cap pre-selected with exactly 1..100 options`** |
| 3 bounds from API, not literals | `<select>` options | **`AC3: option range follows the API bounds, not page literals`** (2..6 payload) + grep (manifest item 2) |
| POST body is a JSON number; server value wins | `handleAutoThreadCapChange` | **`POSTs the pick as a JSON number and shows the server-returned value`** |
| 400 → revert + API error toast · throw → revert + fallback toast | same | **`reverts to the prior cap and toasts the API error on a 400`**, **`reverts and shows the fallback toast when the POST throws`** |
| load failure hides dropdown silently (non-ok / throw) | mount effect | **`hides the dropdown silently when the cap load fails`** (2 cases) |

**Existing coverage (unchanged, must stay green):** `test_AdminScheduledActions.test.tsx` + `test_AdminScheduledActions_AST1104.test.tsx` — they don't mock the cap route; `installBaseApiMocks` throws `Unhandled api`, the page catches it, the dropdown stays hidden. **Broken / obsolete:** none. **Integration:** none.

## QA test manifest (AST-1917)

1. **Page Vitest (§6c routed page, required, green):** new file (7) + both existing Scheduled Actions files (79).

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions_AST1917.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions_AST1104.test.tsx
```

Expect **86 passed**.

2. **AC3 grep + scope:**

```bash
grep -nE '\b100\b' src/ui/frontend/src/pages/AdminScheduledActions.tsx    # expect nothing
git diff --stat origin/ftr/AST-1875-runtime-auto-thread-cap...HEAD -- src/   # expect only AdminScheduledActions.tsx
```

**Pass criterion:** 86/86 green and both commands as stated. `test_AdminSessionResumePaste.test.tsx` (AST-1908; product AST-1899 not on dev) is red on this tip pre-existing — out of scope.

**Bible shasum (publish tip):** fill after `merge-tests` — `docs/test-bible/frontend/pages.md`

### AST-1920 · AST-1851 (bug: Manage Candidate key fields for every server)

`AdminManageCandidates.tsx` Edit shows one API key field per server in `/api/admin/agents/models`, deduped by server, in catalog order. A server with a stored `api_keys` entry shows `(set — leave blank to keep current)` with Show and Clear; a server without one shows `(not set)` with Show only. A stored entry whose server isn't in the catalog is appended after the catalog rows and stays clearable. There is no picker and no Remove. Save sends only changed rows as `[{server, key}]` in row order (`""` = clear a stored entry) and omits `api_keys` when nothing changed. The array storage, PUT contract and list column are unchanged from AST-1901.

| Area | Tests (`test_AdminManageCandidates.test.tsx`) |
| --- | --- |
| Rewritten (AST-1901 picker assertions removed) | main CRUD test: the four catalog-order labels (Kimi and OpenRouter set), 2 Clear buttons, no picker or Remove. DeepSeek `(not set)` gets Show plus a typed key, Kimi gets Clear, and the PUT carries `[{kimi, ""}, {deepseek, "sk-ds-new"}]` |
| Repro (bug-repro) | **AST-1920: no keys shows Not set and a (not set) field for every catalog server…** (4 fields, 4 Show, no Clear, Save omits `api_keys`) · **AST-1920: a stored key for a server not in the catalog stays visible and clearable…** (5th row `retired_srv`; a whitespace-only Anthropic input isn't sent; PUT `[{retired_srv, ""}]`) |
| Retired | **AST-1901: no keys … full picker**, **AST-1901: Remove drops an unsaved row …** |

## QA test manifest (AST-1920)

**Bug-repro (qa-fix):** the main CRUD test and both AST-1920 tests are red on the pre-fix tree (`origin/sub/AST-1851/AST-1920-manage-candidate-key-fields` @ `098705380`): only stored entries render (2 fields, or 0 with no keys). test-fix must see all 3 flip green, with the rest of the file still green.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageCandidates.test.tsx
```

**Pass criterion:** the whole file green.

### AST-1949 · AST-1946 (Manage Agents Mode select; temperature controls removed)

`AdminAgentPrompts.tsx`: the add/edit form's Temperature input becomes a required **Mode** select. Its options are exactly `Deterministic` / `Creative` (the page-local `AGENT_MODES`, which mirrors `src/utils/config.py`). The selected value is sent as `mode` on both POST and PUT, and neither body has `temperature`. Add opens on `Deterministic`. Edit pre-selects the row's mode. A row with `mode: null` (not yet migrated by AST-1950) shows a `— choose mode —` placeholder until a mode is picked. Size and model changes pre-fill max tokens only and never touch the mode. The list swaps **Temp** for **Mode**, and a null mode shows `—`. The `Agent` / model types drop `temperature`, `model_code` and `default_temperature`. Backend contract: [`../ui/api/api_admin.md`](../ui/api/api_admin.md) § AST-1948.

| AC | Tests (`test_AdminAgentPrompts.test.tsx`) |
| --- | --- |
| 8 Mode column, no Temp column | describe **AST-1949 Manage Agents mode** › **list has a Mode column showing each row's mode and no Temp column** |
| 8 No temperature input for any model | › **no Temperature field renders in Add or Edit for any model or size** (every fixture model × size in Add, plus Edit) |
| 8 Mode select with exactly two options; `mode` sent, no `temperature` | › **Edit switches mode and PUT sends the new mode without temperature** · revised **AST-1880: Add picks a model…** (options, Deterministic default, mode kept across size/model change, POST `mode: "Creative"` and no `temperature`) · revised **AST-1880: Edit shows the agent's model + size…** (pre-selected Deterministic, PUT carries `mode`, no `temperature`) |
| Unmigrated row (plan discuss) | › **an unmigrated row (mode null) shows — in the list and a choose-mode placeholder in Edit** |
| 7 (UI half) no `temperature` on the page | grep in manifest below |

**Broken / obsolete (revised):** fixtures drop `default_temperature` / `model_code` / `temperature` and add `mode` (agent_a Deterministic, agent_b Creative). The two AST-1880 tests lose their `field("Temperature")` assertions and `temperature: 0.6` body. The other 8 tests are unchanged and green. **Repro:** with the `origin/ftr/AST-1946-big-brain-openrouter` page swapped in, all 6 revised or new tests are red and the other 8 green. On the publish tip all 14 are green. **Integration:** no scenario drives Manage Agents, so nothing to revise. AC 7's catalog / `src/` greps belong to AST-1947 / AST-1948 (composite on `ftr`, [`../core/agent.md`](../core/agent.md) § AST-1948).

## QA test manifest (AST-1949)

1. **Page Vitest (§6c routed page):** the whole file, 14 tests.
2. **AC 7 grep (UI half)** on the publish tip. Expect nothing.
3. **Scope:** only the page changed under `src/`.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx
cd ../../.. && rg -n "temperature" src/ui/frontend/src/pages/AdminAgentPrompts.tsx
git diff --stat origin/ftr/AST-1946-big-brain-openrouter...HEAD -- src/   # expect only AdminAgentPrompts.tsx
```

**Pass criterion:** 14/14 green, the grep prints nothing, and the scope diff lists only the page.

### AST-1957 · AST-1953 (Manage Agents edits the plain settings; brain size and mode removed)

Supersedes § AST-1880's size UX and § AST-1949's Mode select. `AdminAgentPrompts.tsx`: the form has Model, Max Tokens and seven settings inputs: **Quantization**, **Temperature** (number), **Effort**, an **Allow provider fallbacks** checkbox, **Provider only**, **Provider ignore** (comma-separated) and **Provider sort**. Brain size, Mode, `AGENT_MODES` and the size pre-fill are gone. Max Tokens is never pre-filled; its placeholder shows `default <n>` from the model's `default_max_tokens`. Add opens on the first catalog model with every setting empty and fallbacks checked. Edit fills the inputs from the row, and a stored null fallbacks reads as checked. Save sends **every** settings key: strings trimmed with blank → `null`, temperature as a number or `null`, lists split on commas with blank → `null`, and fallbacks as the checkbox value. So clearing an input clears the setting. Neither body has `brain_setting` or `mode`. The list swaps **Brain setting** / **Mode** for **Quant · Temp · Effort · Fallbacks · Only · Ignore · Sort**: lists comma-joined, fallbacks `yes` / `no`, empty `—`. Backend: [`../ui/api/api_admin.md`](../ui/api/api_admin.md) § AST-1957.

| AC | Tests (`test_AdminAgentPrompts.test.tsx`, describe **AST-1957 Manage Agents plain settings**) |
| --- | --- |
| 10 The edit form renders the seven settings inputs and saves them under the settings keys, with no `brain_setting` / `mode` in the body | › **AC 10: Edit renders the seven settings from the row and saves them under the settings keys** (exact PUT body: set, cleared → `null`, fallbacks toggled) · › **Add saves every setting under its key (trimmed, lists split) with no brain_setting or mode** (exact POST body) |
| 10 No retired control remains | Brain size / Mode label absence in both Add and Edit tests · › **list shows the settings columns, not Brain setting / Mode** · grep in manifest below |
| Scope: list shows the settings; model types drop sizes | › **list shows the settings columns…** (headers + per-row cells) · › **Add opens on the first model, empty settings with fallbacks on; Max Tokens placeholder follows the model** |
| Plan decision: a stored null fallbacks reads as the default and is saved explicitly | › **a row with every setting empty shows — in the list, blanks in Edit with fallbacks checked, and saves fallbacks true** |

**Broken / obsolete (revised):** fixtures move to the flat catalog (`claude-haiku-4-5` 8192, `kimi-k2.6` 16000) and settings rows. Agent_b's GET mock is added, and PUT mocks for agent_a / agent_b return a settings row. **Retired:** **AST-1880: Add picks a model, then only that model's sizes…**, **AST-1880: Edit shows the agent's model + size…**, and the whole **AST-1949 Manage Agents mode** describe (4). Their surviving intent (model select, catalog order, model label column, no stray keys) is carried by the five new tests. The other 8 tests are unchanged. **Repro:** with the pre-epic page (`origin/tests`) swapped in, all 5 new tests are red. On the publish tip all 13 are green. **Integration:** no scenario drives Manage Agents.

## QA test manifest (AST-1957)

1. **Page Vitest (§6c routed page):** the whole file, 13 tests, green on the publish tip.
2. **AC 10 grep (UI)** and the Stage 1 grep (API). Both must print nothing.
3. **Admin API:** `test_api_admin.py` errors at collection on this sub until **AST-1956** lands on `ftr` ([`../ui/api/api_admin.md`](../ui/api/api_admin.md) § AST-1957 **Sequencing**). Once AST-1956 is merged, run it on `ftr`: everything green except the 5 pre-existing reds listed there.
4. **Scope:** only the two product files changed under `src/`.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx
cd ../../.. && rg -n "brain_setting|AGENT_MODES|Deterministic|Creative" src/ui/frontend/src/pages/AdminAgentPrompts.tsx
rg -n 'brain_setting|brain_sizes|resolve_model_brain|AGENT_MODE|"mode"|\bmode\b *=' src/ui/api/api_admin.py
git diff --stat origin/ftr/AST-1953-agent-settings...origin/sub/AST-1953/AST-1957-manage-agents-settings -- src/   # api_admin.py + AdminAgentPrompts.tsx
# after AST-1956 is on ftr:
./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_admin.py
```

**Pass criterion:** 13/13 green, both greps print nothing, and the scope diff lists only the two files. Step 3 is informational on this sub.

**Bible shasums (after publish):** `for p in frontend/pages.md ui/api/api_admin.md; do git show origin/sub/AST-1953/AST-1957-manage-agents-settings:docs/test-bible/$p | shasum; done`

### AST-1968 · AST-1967 (Recommended list triage upgrades)

**Revised by AST-1975.** Sections are per view now (Review / Ready; no In Progress). AC2: the generated job leaves Review. AC7: bulk Generate posts the selected Review rows. Ready: no row Generate, bulk Generate disabled at (0). See § AST-1975.

**Parent:** [AST-1967](https://linear.app/astralcareermatch/issue/AST-1967). **Publish:** `origin/sub/AST-1967/AST-1968-recommended-list-triage-upgrades`.

`JobsRecommended.tsx`: a checkbox column plus a header bulk bar (`Skip (N)` / `Applied (N)` / `Generate Artifacts (n)`, where n counts the selected jobs whose manifest `primary_actions_by_state` includes `generate_artifacts`). A row **G** Generate icon shows only where the manifest allows it. A default-on **Analysis** toggle adds a `tr.recommended-analysis-row` under each job with JD/DO/GET/LIKE lines of letterless circles, built by `buildPhaseListGradeRow`, which shares `phaseGradeCells` with the modal row. A sortable **Total** column (sum of the four phase scores, `—` if any is missing) sorts through `sortRecommendedJobs`. `useCandidateJobActions` gains `generateJob` / `skipJobs` / `generateJobs` / `requestBulkAction` (one notes modal for many jobs); `postGenerateArtifacts` lives in `lib/candidateJobActions.ts`. The list API already flattens `*_grades` / `*_rubric` to top level (`_flatten_grades`), which is where `buildJobListRubricColumnsForGroup` reads columns.

| AC | Source | Component tests |
| --- | --- | --- |
| 1, 15 row Generate only on RECOMMENDED; other callers omit it | `JobsRecommended.tsx`, `CandidateJobRowActions.tsx` | **`test_JobsRecommended.test.tsx`** › **`JobsRecommended — AST-1968 triage upgrades > AC1/AC15…`**; **`test_CandidateJobRowActions.test.tsx`** › **`CandidateJobRowActions — AST-1968 Generate`** |
| 2 row Generate → POST, job moves to In Progress | page + hook + `candidateJobActions.ts` | **`… > AC2…`** |
| 4 bulk bar counts | page | **`… > AC4…`** |
| 5, 8 bulk Skip | page + hook | **`… > AC5/AC8…`** |
| 6, 8 bulk Applied, one notes modal, same note | page + hook | **`… > AC6/AC8…`** |
| 7, 8 bulk Generate sends eligible only | page + hook | **`… > AC7/AC8…`** |
| 9 toggle default on, four lines, off removes rows | page | **`… > AC9…`** |
| 10 letterless, no confidence (page) | page + `recommendedJobReport.tsx` | **`… > AC10…`** |
| 10, 11 circles/colours/order/tooltips equal the modal row | `recommendedJobReport.tsx` | **`test_recommendedJobReport.test.tsx`** › **`recommendedJobReport — AST-1968 letterless list grade row`** (3 cases, incl. modal row unchanged after refactor) |
| 13 Total value / `—` | page | **`… > AC13…`** |
| 14 Total sort + null placement like LIKE | page | **`… > AC14…`** |
| 3, 12, 14 (single call sites), 16 (build/lint) | source | greps + build/lint below |

**Broken / obsolete (revised this pass):** `test_JobsRecommended.test.tsx` › **`sorts by company within a section`** read every `row`; with Analysis on by default each job row is followed by an expanded row. It now filters out `.recommended-analysis-row` (default-on stays exercised).

**Baseline reds (also red on `origin/dev` with the AST-1968 product reverted, checked at QA; not this ticket):** `test_JobsApplied.test.tsx` › **`AST-1479 … Interview → notes modal → candidate_action interview`** (15 s timeout); `test_JobAnalysisReportModal.test.tsx` › **`AST-1546: Print Resume success…`** and **`AST-1350: Print Resume unsupported toast…`** (no Print Resume button).

**Bible drift noted, not reconstructed:** the AST-1477 / AST-1478 rows (`components.md`, `pages.md`) cite `test_JobsRecommended.test.tsx` cases (`AST-1477 mark applied from Recommended`, `AST-1478 report Applied and Skip`) that are not in that file (`git log -S` finds none).

## QA test manifest

1. **AST-1968 + revised + touched-module suites (required, all green):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx \
  ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx \
  ../../../tests/component/frontend/components/test_CandidateJobRowActions.test.tsx
```

2. **AC 15 / hook regression (green except the baseline reds above):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_JobsSkipped.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsApplied.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsInReview.test.tsx \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx
```

3. **Greps (AC 3 / 12 / 14):**

```bash
rg -n "generate_artifacts" src/ui/frontend/src/lib/candidateJobActions.ts            # ≥1 hit
rg -n "/generate_artifacts" src/ui/frontend/src/pages/JobsRecommended.tsx src/ui/frontend/src/components/CandidateJobRowActions.tsx  # nothing
rg -n "sortRubricColumnsByImportanceAndGrade\(" src/ui/frontend/src/lib/recommendedJobReport.tsx  # exactly 1
rg -n "sortRubricColumnsByImportanceAndGrade" src/ui/frontend/src/pages/JobsRecommended.tsx      # nothing
rg -n "function sortRecommendedJobs" src/ui/frontend/src/pages/JobsRecommended.tsx             # exactly 1
```

4. **AC 16:** in `src/ui/frontend`, `npm run build` exits 0; `npx tsc -b --noEmit` exits 0; `npm run lint` problem list has nothing absent on `origin/dev`, and the `react-hooks/set-state-in-effect` hit in `JobsRecommended.tsx` is gone.

**Pass criterion:** items 1, 3, 4 hold; item 2 green apart from the three named baseline reds. Narrowed runs, not the zero-arg harness.

**Bible shasums (after publish):** `for p in frontend/pages.md frontend/components.md frontend/lib.md; do git show origin/sub/AST-1967/AST-1968-recommended-list-triage-upgrades:docs/test-bible/$p | shasum; done`

**AST-1973 (pointer):** the analysis-row phase lines moved out of `JobsRecommended.tsx` into the shared `components/PhaseAnalysisLines.tsx`, which the Job Detail modal Info tab also renders. The page's AC9 / AC10 cases above are unedited and still own list parity. Manifest: **`docs/test-bible/frontend/components.md`** § AST-1973.

### AST-1975 · AST-1970 (Ready / Review / Processing pages, landing, and Jobs routes)

**Parent:** [AST-1970 — Jobs Navigation changes](https://linear.app/astralcareermatch/issue/AST-1970). **Publish:** `origin/sub/AST-1970/AST-1975-jobs-nav`. Backend views / nav counts: **`docs/test-bible/ui/api/api_jobs.md`** § AST-1974.

`JobsHomeRedirect` chooses the landing page: the first Jobs nav item with `count > 0`, else the first Jobs item. It waits for candidate hydration and serves `/` and `*`. Every old Recommended target (AdminRoute, surfer-consent decline, job-detail close / blank id / error link) now goes to `/`. `JobsRecommended.tsx` takes `view` / `title` and serves `/jobs/review` (`view=review`, RECOMMENDED) and `/jobs/ready` (`view=ready`, CANDIDATE_REVIEW). It adds a sortable **Source** column and drops the Meteorites split. `JobsInReview.tsx` became `JobsProcessing.tsx` (`view=processing`, manifest `processing_sections`). Responded is deleted.

| AC | Source | Component tests |
| --- | --- | --- |
| 11 landing = first non-zero Jobs item, else first; waits for hydration; failure state | `components/JobsHomeRedirect.tsx` | **`components/test_JobsHomeRedirect.test.tsx`** › **`JobsHomeRedirect — AST-1975 landing page`** (8 cases) |
| 11 index / catch-all; old targets → `/` | `routes.tsx`, `AdminRoute.tsx`, `CandidateSurferConsent.tsx`, `JobsJobDetail.tsx` | **`test_routes.test.tsx`** (ready / review / processing present; recommended / in_review / responded absent); revised **`test_AdminRoute`**, **`test_CandidateSurferConsent`** (decline → `/`), **`test_JobsJobDetail`** (close / blank id → `/`, **Back to Jobs**) |
| 12 Processing replaces In Review; Responded gone | `pages/JobsProcessing.tsx` | **`pages/test_JobsProcessing.test.tsx`** (git-mv of `test_JobsInReview`; new **`titled Processing; fetches view=processing; BUILD_ARTIFACTS…`**); `test_JobsResponded.test.tsx` deleted |
| 13 title, per-view fetch, Source cell + sort, no Meteorites, Generate only on Review | `pages/JobsRecommended.tsx`, `StateUiContext.tsx` | **`pages/test_JobsRecommended.test.tsx`** — **`Review: titled Review…`**, **`Ready: titled Ready, fetches view=ready…`**, **`AST-1975: no Meteorites sub-section; Source cell shows job.source; Source sorts`**, **`AC1/AC15`** (both), **`AC9: Ready keeps the Analysis toggle and Total`**; **`contexts/test_StateUiContext.test.tsx`** (`processing_sections`) |

**Fixture:** `stateUiManifestFixture.ts` renames `in_review_sections` to `processing_sections` and adds BUILD_ARTIFACTS. It adds ERROR_BUILD_ARTIFACTS / BUILD_FAILED to Skipped (order, labels, retry map), sets `recommended.sections` to RECOMMENDED "Review" + CANDIDATE_REVIEW "Ready", and drops `meteorite_section`. All of this mirrors AST-1974 config.

**Broken / obsolete (revised this pass):** the whole of `test_JobsRecommended.test.tsx` is rebuilt on per-view data, because each backend view returns only its own state. The stateful AST-1968 handler is view-scoped and every action drops the row. The AST-1057 / AST-1708 Meteorites cases are retired (one AST-1975 case replaces them). The AdminRoute ×2, CandidateSurferConsent ×1, JobsJobDetail ×4, and test_routes ×1 cases are retargeted to `/`. Historical blocks above carry **AST-1975** pointers.

**Not revised:** `lib/test_sessionAuthMark.test.ts` uses `/jobs/recommended?foo=1` only as a sample in-app path for the generic `isSafeAuthReturnPath` guard. It still passes, and a stale saved return path lands on the catch-all redirect. The plan doc's Notes for QA expected it to fail; it does not.

**Baseline reds (also red with this ticket's product reverted to `origin/ftr/AST-1970-jobs-nav`; not this ticket):** 40 cases across Artifacts* / Companies* / CandidateContext / candidateLabel / sessionExtend / JobAnalysisReportModal (Print Resume) / JobDetailModal (listing_href) / ProfileTextPage / CandidateIntake / JobsApplied (AST-1479 timeout).

## QA test manifest

1. **AST-1975 + revised suites (required, all green):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobsHomeRedirect.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsProcessing.test.tsx \
  ../../../tests/component/frontend/test_routes.test.tsx \
  ../../../tests/component/frontend/contexts/test_StateUiContext.test.tsx \
  ../../../tests/component/frontend/components/test_AdminRoute.test.tsx \
  ../../../tests/component/frontend/pages/test_CandidateSurferConsent.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsJobDetail.test.tsx
```

2. **Full frontend component suite:** `cd src/ui/frontend && npm run test:component`. It is green apart from the 40 baseline reds above (no new failures).

3. **Greps (AC 12 / 13):**

```bash
rg -n "JobsInReview|JobsResponded|jobs/recommended|in_review_sections|\bmeteorite_section\b" src/ui/frontend/src -g '!lib/rubricDisplay.ts'   # nothing (rubricDisplay.ts:75 comment = plan's optional "discuss" finding, not AC)
ls tests/component/frontend/pages/test_JobsInReview.test.tsx tests/component/frontend/pages/test_JobsResponded.test.tsx   # both absent
```

4. **AC 14:** in `src/ui/frontend`, `npm run build` exits 0 and `npm run lint` adds no problems absent on `origin/ftr/AST-1970-jobs-nav`.

**Pass criterion:** items 1, 3, 4 hold; item 2 shows only the named baseline reds. Narrowed runs, not the zero-arg harness.

**Bible shasums (after publish):** `for p in frontend/pages.md frontend/components.md; do git show origin/sub/AST-1970/AST-1975-jobs-nav:docs/test-bible/$p | shasum; done`

### AST-1976 · AST-1970 (Meteorites landed-job state and job link)

**Parent:** [AST-1970 — Jobs Navigation changes](https://linear.app/astralcareermatch/issue/AST-1970). **Publish:** `origin/sub/AST-1970/AST-1976-jobs-nav`. Backend `job_state` (live `LEFT JOIN job`, null when unlanded): **`docs/test-bible/ui/api/api_meteorite.md`** § AST-1974 and **`docs/test-bible/data/database/jobs.md`** § AST-1974.

On `JobsMeteorites.tsx`, the **Job** cell is now a button that opens `JobAnalysisReportModal` in place (`stopPropagation`, so the row click doesn't also fire). The **Job State** cell shows raw `job_state` and falls back to `—`. The report's `onRefresh` reloads the list. The row click still opens `MeteoriteDetailModal`.

| AC | Source | Component tests |
| --- | --- | --- |
| 14 Job State = job's state; `—` when unlanded (Job and Job State) | `pages/JobsMeteorites.tsx` | **`test_JobsMeteorites.test.tsx`** › **`JobsMeteorites — AST-1976 landed-job state and job link > Job State cell shows the landed job's state…`** |
| 14 job link → report modal; URL stays `/jobs/meteorites`; no Meteorite modal | page + `JobAnalysisReportModal` | **`… > job link opens the Job Analysis Report in place…`** |
| 14 elsewhere on the row → Meteorite modal, not the report | page | **`… > clicking elsewhere on a landed row opens the Meteorite modal…`** (regression guard; also green pre-ticket) |
| 14 not stale: a report action reloads the list | page `onRefresh={load}` | **`… > Skip in the report reloads the list so Job State is not stale`** |
| 15 build / lint / config import | source | commands below |

The tests use the production `JOBS_METEORITES_LIST_COLUMNS` keys and labels (Job then Job State). On the pre-ticket page (`origin/ftr/AST-1970-jobs-nav`), the state-cell, job-link, and Skip-refresh cases are red, which proves they guard the change.

**Broken / obsolete:** none. The four AST-1749 cases are unchanged and green, because their 3-column mock has no Job column.

## QA test manifest

1. **AST-1976 + AST-1749 page suite (required, all green):**

```bash
cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_JobsMeteorites.test.tsx
```

2. **AC 15:** `python -c "import src.utils.config"` exits 0. In `src/ui/frontend`, `npm run build` exits 0 and `npm run lint` adds no problems absent on `origin/dev`.

**Pass criterion:** items 1 and 2 hold. Narrowed runs, not the zero-arg harness.

**Bible shasums (after publish):** `git show origin/sub/AST-1970/AST-1976-jobs-nav:docs/test-bible/frontend/pages.md | shasum`

### AST-1979 · AST-1971 (Created column on Jobs list tables)

**Parent:** [AST-1971 — Add Created to the job list table](https://linear.app/astralcareermatch/issue/AST-1971). **Publish:** `origin/sub/AST-1971/AST-1979-created-col`. Meteorites Created (backend + config) is sibling AST-1971 #2, not covered here.

Every job table on Ready / Review (`JobsRecommended.tsx`), Processing, Skipped (below-floor and regular), and Applied gets a sortable **Created** header just left of **Updated** / **Failed At**. Its cell is `<Time value={job.created_at} />`, and each page's existing sorter gains a `created_at` branch.

**Shared helper:** `tests/component/frontend/pages/created-column.ts` holds `createdColumnJobs(base)` (3 rows whose created order — null, mid, late — differs from the default `state_changed_at`-desc order), `installTzCandidate` (candidate tz `Asia/Tokyo`, so a cell rendered in the wrong zone shows a different day), and `expectCreatedColumn(table, updatedLabel)`, which runs AC 1–4 on one table. Headers are read with `thead th`, not `getAllByRole`, because Skipped's below-floor spacer `<th aria-hidden>` still takes a cell slot.

| AC | Source | Component tests |
| --- | --- | --- |
| 1 Created header immediately left of Updated / Failed At | all four pages | **`expectCreatedColumn`** via each page's **`… — AST-1979 Created column`** describe |
| 2 cell = `fmtTime(created_at, candidate tz)`; Updated in the same tz; null → `—` | `<Time>` cell | same (`Asia/Tokyo` candidate; `12/15 23:30Z` → `12/16/25`) |
| 3 first click ascending (null first, like null `state_changed_at`), second reverses, ▲/▼ on Created only | page sorters (`created_at` branch) | same |
| 4 default load still `state_changed_at` desc; Created shows no indicator | unchanged sort defaults | same; Applied also asserts **`Updated▼`** at load |
| 5 sorter count unchanged; `created_at` compare inside the existing sorter | source | grep below |
| 6 build / lint | source | commands below |

Cases: **`test_JobsRecommended`** › **`JobsRecommended — AST-1979 Created column`** (`review`, `ready`); **`test_JobsProcessing`** › **`JobsProcessing — AST-1979 Created column`**; **`test_JobsSkipped`** › **`JobsSkipped — AST-1979 Created column`** (`below-floor` → Updated, `regular` → Failed At); **`test_JobsApplied`** › **`JobsApplied — AST-1979 Created column`**. All six are red with the four pages reverted to `origin/dev`, so they guard the change.

**AC 4 wording vs product:** AC 4 says the indicator is on Updated / Failed At at first load. On the section pages (Ready / Review, Processing, Skipped), `sortIndicator` only renders after a header click, so no header shows an indicator at load. That is true on `origin/dev` too. The plan makes no change to `sortIndicator`, and AC 4's Fail line only covers the default switching. The tests assert the default *order* plus no indicator on Created on every page, and **`Updated▼`** only on Applied, which seeds its sort state.

**Broken / obsolete:** none. The existing header-index lookups find columns by label, `children[2]` (Job Title) sits left of the insert, and no test asserts `colSpan`. Lint cleanup: removed the unused `jsonResponse` import from `test_JobsSkipped.test.tsx`.

**Baseline red (not this ticket):** `test_JobsApplied` › **`Interview → notes modal → candidate_action interview`** times out. It asserts the exact pre-AST-1498 POST body `{action, notes}`, but the product now adds `candidate_id` (see AST-1498 `[bug-repro]` beside it). It is already listed under § AST-1975's baseline reds.

## QA test manifest

1. **Four job page suites (required):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsProcessing.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsSkipped.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsApplied.test.tsx
```

Expect 54 passed and 1 failed (the baseline red above), with all six **`AST-1979`** cases green.

2. **AC 5:** `rg -c "function sort" src/ui/frontend/src/pages/Jobs{Recommended,Processing,Skipped,Applied}.tsx` gives 2 per file (the same as `origin/dev`). `rg -n '"created_at"' src/ui/frontend/src/pages/Jobs{Recommended,Processing,Skipped,Applied}.tsx` shows each compare inside that file's existing sorter.

3. **AC 6:** in `src/ui/frontend`, `npx tsc -b --noEmit` and `npm run build` exit 0, and `npm run lint` adds no problems absent on `origin/dev`.

**Pass criterion:** items 1–3 hold. Narrowed runs, not the zero-arg harness.

**Bible shasums (after publish):** `git show origin/sub/AST-1971/AST-1979-created-col:docs/test-bible/frontend/pages.md | shasum`

**AST-1982 (pointer):** Job Title cell on `JobsRecommended` (Ready + Review), `JobsProcessing`, `JobsSkipped` (both table variants), `JobsApplied`, and the Meteorites `job_title` column now renders `JobTitleText` (cut at 50 + `…`, portaled full-title tooltip). Page tests are named **`AST-1982 …`** and use the shared helper `tests/component/frontend/pages/job-title-cell.ts`. Manifest: **`docs/test-bible/frontend/components.md`** § AST-1982.

---

### AST-2056 · AST-2041 (gap — Base Resume Content autosave; product AST-2051)

**Publish:** `origin/sub/AST-2041/AST-2056-resume-autosave-tests`. Base Resume Content (`bodyShape="resume_content"`) section bodies **autosave after 2000ms**; no header Save/Cancel outside Generate review (AST-2051). Editor contract, new cases, red/green and manifest: **`docs/test-bible/frontend/components.md`** § AST-2056.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page (**§6c**) bodyShape + leaf autosave PUT | `ArtifactsBaseResumeContent.tsx` → `ArtifactEditor.tsx` | **`test_ArtifactsBaseResumeContent.test.tsx`** — **`AST-1577 / AST-2051: wires bodyShape resume_content; autosave PUTs base_resume leaf (§6c)`** (retargeted from header Save; red pre-fix — Save still rendered) |

**Pre-existing red, not this ticket:** **`AST-1577: page and draft follow ui-consistency`** — draft path moved to `canon/directives/active/`; name-skipped in the § AST-2056 manifest.

---

### AST-2047 · AST-2042 (theme registry, palettes, Theme Examples page)

**Publish:** `origin/sub/AST-2042/AST-2047-theme-registry-palettes`. `UI_CONFIG["themes"]` (four palette ids: `dark`, `light`, examples-only `light_parchment` / `light_slate`) + `default_theme` drive the profile **Theme** select (selectable entries only), a Tools nav item `/admin/theme_examples`, and one `[data-theme="<id>"]` block per id in `App.css` (Dark = `:root, [data-theme="dark"]`). New admin page `AdminThemeExamples.tsx` renders the same shared-class sample once per registry id.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page (**§6c**) — one labeled panel per registry id, button / table row / select / grade dots A–X / toast in each; GET-only | `pages/AdminThemeExamples.tsx` | **`test_AdminThemeExamples.test.tsx`** — **`renders one labeled panel per registry id with the shared sample; read-only (§6c, AC6)`** |
| `App.css` token blocks — one per registry id; Light name sets equal Dark's; Lights pairwise differ on `--bg-deep` / `--bg-card` / `--accent-contrast` (AC4; renamed from `--accent-gold` by AST-2076) | `App.css` § 1 | same file — **`App.css theme token blocks — AST-2047`** (3 cases) |
| `App.css` rule bodies — no hex / non-black `rgba()` outside token blocks; every `var(--x)` in `App.css` defined in a token block (AC5, `App.css` half only — `.tsx` half is AST-2049) | `App.css` | same file — **`no hex or non-black rgba outside token blocks; …`** |
| Registry ids / selectable / default; profile Theme options generated from the registry; Tools item admin-only; every id has an `App.css` block (AC1, AC2) | `src/utils/config.py` | **`tests/component/utils/test_config.py::TestAst2047ThemeRegistry`** (4) — see [`../utils/config.md`](../utils/config.md) § AST-2047 pointer |
| `ui_config` serves `themes` + `default_theme` (AC1) | `src/ui/api/api_system.py` (unchanged; `{**UI_CONFIG}` spread) | **`tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_ui_config_serves_theme_registry`** |

**Broken / obsolete:** none. Full Vitest (1021 cases) and `test_config.py` / `test_api_system.py` / `test_candidate.py` show the **same** failure set with and without the AST-2047 product merged onto `origin/tests` @ `032ecabed` (pre-existing reds only). No `tests/integration/` scenario reads `ui_config`, Tools items, profile fields, or `App.css`.

**Not covered by component tests (jsdom has no cascade):** AC6 computed panel backgrounds pairwise different, non-admin redirect from `/admin/theme_examples` (generic `AdminRoute` behavior — `test_AdminRoute.test.tsx`), Tools item hidden for non-admins (generic `admin_only` — `test_api_system.py::TestSystemAuthRoutes::test_nav_config_omits_admin_group_for_non_admin`). AC3 (Dark token values unchanged) is a one-shot diff against `origin/dev`, not a durable pin — later palette tweaks are allowed.

**Note — served key order:** Flask 3's JSON provider sorts keys, so `/api/system/ui_config` serves `themes` alphabetically, not in registry order (plan assumed order survives `jsonify`). Panels render alphabetically; today that equals registry order. Tests compare served keys as a set.

#### QA test manifest (AST-2047)

1. **New tests (required, all green):**

```bash
cd src/ui/frontend && npx vitest run --config vite.config.ts ../../../tests/component/frontend/pages/test_AdminThemeExamples.test.tsx
cd ../../.. && ./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst2047ThemeRegistry \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_ui_config_serves_theme_registry
```

Expect 4 Vitest + 5 pytest passed.

2. **Regression (required):** failure set unchanged vs `origin/dev` (pre-existing reds: 24 in `test_config.py`, 1 in `test_api_system.py` — e.g. `TestAst1386ThreeSegmentAdminNav`, `TestAst1375InflightHideStatesManifest`; none name themes):

```bash
./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py tests/component/ui/api/test_api_system.py
cd src/ui/frontend && npx vitest run --config vite.config.ts \
  ../../../tests/component/frontend/test_routes.test.tsx \
  ../../../tests/component/frontend/components/test_AdminRoute.test.tsx \
  ../../../tests/component/frontend/components/test_JobTitleText.test.tsx \
  ../../../tests/component/frontend/components/test_Modal.test.tsx \
  ../../../tests/component/frontend/components/test_ListPage.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminManageEmail.test.tsx \
  ../../../tests/component/frontend/pages/test_CandidateProfile.test.tsx
```

Vitest files above: all green.

3. **AC2 / AC5 (`.ts`/`.tsx` hex half is AST-2049's):** `rg -n '"light"' src/ui/frontend/src --glob '*.{ts,tsx}'` returns nothing.

4. **AC3 Dark unchanged (one-shot):** every declaration in the `origin/dev` `:root { … }` block appears with the same value in the publish tip's `:root, [data-theme="dark"] { … }` block (plan Stage 2 step 6 check 1, `App.before.css` = `git show origin/dev:src/ui/frontend/src/App.css`).

5. **AC7:** in `src/ui/frontend`, `npx tsc -b --noEmit` and `npm run build` exit 0; `npm run lint` adds no problem absent on `origin/dev`.

6. **AC6 manual (browser, optional for test-child — UAT):** as admin, Tools → Theme Examples shows four panels with visibly different backgrounds; as non-admin, no Tools group and the URL redirects.

**Pass criterion:** items 1–5 hold. Narrowed runs, not the zero-arg harness.

**Bible shasums (after publish):** `git show origin/sub/AST-2042/AST-2047-theme-registry-palettes:docs/test-bible/frontend/pages.md | shasum` (also `utils/config.md`, `ui/api/api_system.md`)

---

### AST-2048 · AST-2042 (save and apply the candidate's theme)

**Publish:** `origin/sub/AST-2042/AST-2048-theme-save-apply`. `save_candidate_data` rejects any `theme` that is not a profile-selectable `UI_CONFIG["themes"]` id (`ValueError` → existing 400). `CandidateProfile.tsx` reads `default_theme` from its existing `/api/ui_config` fetch, **waits for it** before loading the candidate, and loads `theme` from `candidate_data.theme` (else the default). `CandidateContext.tsx` sets `<html data-theme>` from the selected candidate, removes it when none / no stored theme / unmount.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed page (**§6c**) — Theme select shows served default when none stored; choose Light → PUT body `theme: "light"`; reload from save response keeps Light (AC3) | `pages/CandidateProfile.tsx` | **`test_CandidateProfile.test.tsx`** — **`AST-2048: no stored theme loads the served default; …`**, **`AST-2048: stored theme loads selected`** |
| Root `data-theme` from selected candidate; picker switch flips without reload; no theme / no candidates / unmount → no attribute (AC5/AC6 attribute half) | `contexts/CandidateContext.tsx` | **`test_CandidateContext.test.tsx`** — **`CandidateProvider — AST-2048 data-theme follows the selected candidate`** (2) |
| Allowlist: `dark` / `light` saved; `neon`, `light_parchment`, `light_slate`, `""`, `null`, list → `ValueError`, nothing saved (AC3/AC4) | `src/core/candidate.py` (`LOCKED_AT_100` — new lines fully branch-covered) | **`tests/component/core/test_candidate.py::TestAst2048ThemeAllowlist`** (8) — pointer [`../core/candidate.md`](../core/candidate.md) |
| `PUT /api/candidates/<id>/data` with `neon` / `light_parchment` → 400, no DB write (AC4) | `src/ui/api/api_candidate.py` (unchanged) | **`tests/component/ui/api/test_api_candidate.py::…::test_update_rejects_unselectable_theme`** — pointer [`../ui/api/api_candidate.md`](../ui/api/api_candidate.md) |

**Broken / obsolete (revised this pass):** `test_CandidateProfile.test.tsx` — the shared `installProfileMocks` `/api/ui_config` response now carries `default_theme: "dark"` (the real served contract after AST-2047); without it the page waits forever and **17** cases stuck on "Loading...". Mocked profile shape gains the `theme` select (mirrors `DATA_SHAPES`). No other Vitest or pytest failure changed vs the same tree without AST-2048 (base = `origin/tests` + `origin/ftr/AST-2042-user-theme`). Pre-existing red unchanged: `CandidateProvider — AST-1311 … restores the persisted selection's Full Name after load`.

**Not covered by component tests (jsdom has no cascade):** AC5/AC6 computed `body` background (`rgb(15, 11, 24)` on Dark, different on Light) — browser/UAT only. **Plan-documented tradeoff:** if `/api/ui_config` fails, Candidate Profile stays on "Loading..." (previously only the signature limits were lost) — no test pins this either way.

**Finding (AST-2047, not this ticket):** `lib/uiConfig.ts` `loadUiConfig` fetches **`/api/system/ui_config`**; Flask only serves **`/api/ui_config`** (`system_bp` `url_prefix="/api"`), so at runtime `getUiConfig()?.themes` is undefined and **Theme Examples stays on "Loading..."**. § AST-2047's page test mocks `/api/system/ui_config` and cannot catch the mismatch. Flagged on the parent for Susan.

#### QA test manifest (AST-2048)

1. **New + revised tests (required, all green):**

```bash
cd src/ui/frontend && npx vitest run --config vite.config.ts \
  ../../../tests/component/frontend/pages/test_CandidateProfile.test.tsx \
  ../../../tests/component/frontend/contexts/test_CandidateContext.test.tsx
cd ../../.. && ./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst2048ThemeAllowlist \
  "tests/component/ui/api/test_api_candidate.py" -k "Ast2048 or unselectable_theme"
```

Expect `test_CandidateProfile` 19 passed / 1 skipped; `test_CandidateContext` all green except the pre-existing AST-1311 restore case; 9 pytest passed.

2. **Regression (required):** `./scripts/testing/run_component_tests.sh tests/component/core/test_candidate.py tests/component/ui/api/test_api_candidate.py` — failure set unchanged vs `origin/ftr/AST-2042-user-theme` (pre-existing reds only; none name theme).

3. **AC5 `.tsx` hex half for this file:** `rg -n "#[0-9a-fA-F]{3,8}\b" src/ui/frontend/src/pages/CandidateProfile.tsx` returns nothing.

4. **AC7:** in `src/ui/frontend`, `npx tsc -b --noEmit` and `npm run build` exit 0; `npm run lint` adds no problem absent on `origin/dev`.

5. **AC5/AC6 browser (UAT):** Light candidate → `<html data-theme="light">` and body background ≠ `rgb(15, 11, 24)`; switch to a no-theme candidate → no attribute, `rgb(15, 11, 24)`, no reload.

**Pass criterion:** items 1–4 hold. Narrowed runs, not the zero-arg harness.

**Bible shasums (after publish):** `git show origin/sub/AST-2042/AST-2048-theme-save-apply:docs/test-bible/frontend/pages.md | shasum` (also `frontend/contexts.md`, `core/candidate.md`, `ui/api/api_candidate.md`)

---

### AST-2049 · AST-2042 (component/page inline colors onto tokens)

**Publish:** `origin/sub/AST-2042/AST-2049-inline-color-tokens`. 49 inline literal colors / `var(--x, #…)` fallbacks / undefined custom-property refs in 7 components + 12 pages moved onto `App.css` token-block names. No layout or logic change; does not touch `App.css` (AST-2047) or `CandidateProfile.tsx` (AST-2048).

| Area | Source | Component tests |
| --- | --- | --- |
| AC9 epic-wide guard — no hex (`["' ,(]#…`) in non-test `.ts`/`.tsx` under `src/ui/frontend/src`; every `var(--x)` in `.ts`/`.tsx`/`.css` names a property declared in an `App.css` theme block | whole SPA source tree | **`test_AdminThemeExamples.test.tsx`** — **`AST-2049: no hex in .ts/.tsx source and every var(--x) in source is defined in a token block (AC9, epic-wide)`** (in the § AST-2047 `App.css` describe; red on `ftr` before this child, green after) |
| Touched components/pages render unchanged | 19 files in the ticket Scope | existing per-file Vitests (manifest item 2) — no color values asserted |

**Broken / obsolete:** none. Full Vitest (1029 cases) shows the same failure set with and without AST-2049 on `origin/tests` + `origin/ftr/AST-2042-user-theme`; the only swaps were `AdminScheduledActions … save disabled on add when no candidate selected` and `AdminAnthropicAdHoc AST-1452 …`, both green twice in isolation on the ticket tree (load flakes). Engineer's "no test asserts old color values" confirmed.

**Not covered by component tests (jsdom has no cascade):** whether each swapped token reads well on the Light palettes — UAT / Theme Examples.

#### QA test manifest (AST-2049)

1. **New guard (required, green):**

```bash
cd src/ui/frontend && npx vitest run --config vite.config.ts ../../../tests/component/frontend/pages/test_AdminThemeExamples.test.tsx
```

Expect 5 passed.

2. **Regression (required):** same Vitest command over the touched files' tests — failure set unchanged vs `origin/ftr/AST-2042-user-theme`. Pre-existing reds (not this ticket): `test_ArtifactEditor` 13 (AST-2056 bug-repros), `test_ProfileTextPage` 6, `test_CompaniesWatchHistory` 6, `test_ArtifactsBaseResumeContent` 2.

```bash
cd src/ui/frontend && npx vitest run --config vite.config.ts \
  ../../../tests/component/frontend/components/test_{ArtifactEditor,ContextTextPage,NavigationShell,ProfileTextPage,RepoJsonDivergenceBanner,StateTimeline,TabbedTextArea}.test.tsx \
  ../../../tests/component/frontend/pages/test_{AdminCostReconciliation,AdminDataManagement,AdminManageCandidates,AdminScheduledActions,AdminScheduledActions_AST1104,AdminScheduledActions_AST1917,AdminScheduledQueries,AdminSessionCoverLetter,AdminSessionResumePaste,AdminTaskPrompts,ArtifactsBaseResumeContent,ArtifactsCompanySearchTerms,CompaniesNewList,CompaniesWatchHistory}.test.tsx
```

3. **AC9 grep (ticket form):** `rg -n "[\"' ,(]#[0-9a-fA-F]{3,8}\b" src/ui/frontend/src --glob '*.{ts,tsx}' --glob '!*.test.*'` returns nothing.

4. **AC10:** in `src/ui/frontend`, `npx tsc -b --noEmit` and `npm run build` exit 0; `npm run lint` adds no problem absent on `origin/dev`.

**Pass criterion:** items 1–4 hold. Narrowed runs, not the zero-arg harness.

**Bible shasums (after publish):** `git show origin/sub/AST-2042/AST-2049-inline-color-tokens:docs/test-bible/frontend/pages.md | shasum` (also `frontend/components.md`)

### AST-2065 · AST-2042 (UI config URL; UAT-batch bug)

**Publish:** `origin/sub/AST-2042/AST-2065-ui-config-url`. **Scope from** `[board-betty] TESTS: REVISE`. Plan: `docs/features/interface/ast-2047-theme-registry-palettes-and-theme-examples-page-user-theme.md` § Bug: AST-2065.

Contract: Flask serves `UI_CONFIG` only at **`GET /api/ui_config`** (`system_bp` url_prefix `/api`). `/api/system/ui_config` falls through to the SPA catch-all, so `loadUiConfig` (`lib/uiConfig.ts`), `ArtifactEditor.tsx` and `ArtifactsBaseResumeContent.tsx` silently ran on fallbacks. Fix = those three literals → `/api/ui_config`.

| Area | Source | Component tests |
| --- | --- | --- |
| Loader requests the served route **[bug-repro]** | `lib/uiConfig.ts` | `tests/component/frontend/lib/test_uiConfig.test.ts` — **`uiConfig URL — AST-2065`** › **`[bug-repro] loadUiConfig fetches /api/ui_config`** (`vi.resetModules` + mocked `api`; module-level cache) |
| No stale URL anywhere in the SPA **[bug-repro]** | all non-test `.ts`/`.tsx` under `src/ui/frontend/src` | same describe › **`[bug-repro] no frontend source references /api/system/ui_config`** |
| Server route | `api_system.py` | existing **`test_api_system.py::TestSystemAuthRoutes::test_ui_config_*`** (already hit `/api/ui_config`) — unchanged |

**Broken / obsolete (retargeted in place, `/api/system/ui_config` → `/api/ui_config`, 52 lines):** these mocks encoded the bug, so they would lose their config post-fix. Components: `test_ArtifactEditor`, `test_ContextTextPage`, `test_JobTitleText`, `test_ListPage`, `test_ListPage_listTableLayout`, `test_ListPage_ui_config_fail`. Pages: `page-mocks.ts` (shared — 21 page files consume it), `test_AdminThemeExamples`, `test_ArtifactsBaseResumeContent`, `test_CompaniesWatchHistory`, `test_CompaniesWatchList`, `test_JobsJobDetail`. **Left alone** (already match both URLs): `test-utils.tsx`, `test_CandidateProfile`, `test_AdminSessionCoverLetter`, `test_AdminAnthropicAdHoc`, `test_CandidateIntake`.

**Red / green:** pre-fix sub tip `27ebac8c1` — both `[bug-repro]` cases red (loader called `/api/system/ui_config`; scan lists `components/ArtifactEditor.tsx`, `lib/uiConfig.ts`, `pages/ArtifactsBaseResumeContent.tsx`); the retargeted mocks are expected red until the fix lands. Same tree + the three-literal fix applied locally — guard green, manifest item 2 failure set equals the pre-existing set below (except `test_CandidateIntake`, a timing flake: 4–10 of 24 red on the pre-fix tree alone, file mocks both URLs).

**Integration:** none — frontend-only; do not invent.

#### QA test manifest (AST-2065)

1. **[bug-repro] flip (test-fix):** red pre-fix, green post-fix — 3 passed.

```bash
cd src/ui/frontend && npx vitest run --config vite.config.ts ../../../tests/component/frontend/lib/test_uiConfig.test.ts
```

2. **Regression (required):** retargeted files + `page-mocks.ts` consumers — failure set must equal the pre-existing reds (not this ticket): `test_ArtifactEditor` 13 (AST-2056 bug-repros), `test_CompaniesWatchHistory` 6, `test_ArtifactsBaseResumeContent` 2; `test_CandidateIntake` timing flakes.

```bash
cd src/ui/frontend && npx vitest run --config vite.config.ts \
  ../../../tests/component/frontend/components/test_{ArtifactEditor,ContextTextPage,JobTitleText,ListPage,ListPage_listTableLayout,ListPage_ui_config_fail}.test.tsx \
  $(cd ../../.. && rg -l "page-mocks" tests/component/frontend/pages --glob '*.test.tsx' | sed 's#^#../../../#') \
  ../../../tests/component/frontend/pages/test_{AdminThemeExamples,ArtifactsBaseResumeContent,CompaniesWatchHistory,CompaniesWatchList,JobsJobDetail}.test.tsx
```

3. **Grep:** `rg -n "/api/system/ui_config" src/ui/frontend/src` returns nothing.

4. In `src/ui/frontend`, `npx tsc -b --noEmit` and `npm run build` exit 0; `npm run lint` adds no problem absent on `origin/dev`.

**Pass criterion:** items 1–4 hold. Narrowed runs, not the zero-arg harness.

---

### AST-2064 · AST-2042 (bug — Light grade-color set + Theme Examples grade options)

**Publish:** `origin/sub/AST-2042/AST-2064-light-grade-colors`. Fix (plan doc § Bug: AST-2064): shared "Deep" grade values in the three Light blocks; `UI_CONFIG["theme_example_grade_sets"]` (deep / soft / classic, examples-only) rendered as a **Grade color options** block in every Theme Examples panel, each row overriding the panel's `--grade-*` / `--text-on-grade*` via inline custom properties.

| Area | Source | Component tests |
| --- | --- | --- |
| **[bug-repro]** options block per panel; one labeled row per set; row inline style carries the set's tokens; each row A–X; panel's own `.theme-examples-grade` row still exactly one A–X | `pages/AdminThemeExamples.tsx` | **`test_AdminThemeExamples.test.tsx`** — **`AdminThemeExamples — AST-2064 grade color options > [bug-repro] each panel shows one labeled row per grade set …`** (fresh module graph — `uiConfig` caches) |
| **[bug-repro]** sets are `deep` / `soft` / `classic` with labels; each set's `tokens` keys are exactly the 8 grade tokens declared in `App.css`'s Dark block, values `#rrggbb` | `src/utils/config.py` | **`tests/component/utils/test_config.py::TestAst2064ThemeExampleGradeSets`** (2) |

**Red on pre-fix tree** (`origin/sub/…/AST-2064` @ `4b8964c3e`): page case — no `.theme-examples-grade-options`; config cases — `UI_CONFIG has no theme_example_grade_sets`. **Green** against the plan's Proposed change steps 2–4 applied locally (not committed). Light "Deep" values themselves are not pinned (palette choice → UAT). The repro mocks **both** `/api/ui_config` and `/api/system/ui_config`, so it is unaffected by the sibling **AST-2065** URL fix. **Known red on this sub, not AST-2064 scope:** `AdminThemeExamples — AST-2047 > renders one labeled panel per registry id …` — AST-2065 retargeted its mock to `/api/ui_config`, and this sub's `uiConfig.ts` still fetches `/api/system/ui_config`. It turns green when AST-2065's fix merges; do not change the loader URL here.

#### QA test manifest (AST-2064)

```bash
cd src/ui/frontend && npx vitest run --config vite.config.ts ../../../tests/component/frontend/pages/test_AdminThemeExamples.test.tsx
cd ../../.. && ./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py -k "Ast2064 or Ast2047"
```

**Pass criterion (test-fix):** the three `[bug-repro]` nodes flip red → green; the 4 App.css Vitest cases + 4 `TestAst2047ThemeRegistry` cases stay green. The AST-2047 page case stays red until AST-2065 merges (see above).

---

### AST-2077 · AST-2042 (bug — compact letterless grade-dot sample beside each grade-color option)

**Publish:** `origin/sub/AST-2042/AST-2077-compact-grade-dots`. **Scope from** `[board-betty] TESTS: REVISE`. Fix (plan doc § Bug: AST-2077): each Theme Examples grade-color option gets a sibling `.recommended-list-phase-grade-row` of letterless A–X dots in the Recommended Job List's markup (`buildPhaseListGradeRow`), carrying the same inline set tokens as its lettered row.

| Area | Source | Component tests |
| --- | --- | --- |
| **[bug-repro]** per panel: one compact row per grade set, in order; shares a parent with its lettered option row (beside, not nested); inline style carries the set's tokens; children are `span > span.grade-dot.dot-<g>.grade-dot-letterless` for A, B, C, D, F, X with no text | `pages/AdminThemeExamples.tsx` | **`test_AdminThemeExamples.test.tsx`** — **`AdminThemeExamples — AST-2077 compact grade-dot samples > [bug-repro] each grade-color option has a letterless Recommended-list grade row beside it …`** (fresh module graph — `uiConfig` caches) |
| Lettered option rows + panel grade row unchanged | same | existing **AST-2064** `[bug-repro]` (unchanged — compact row is not a `.theme-examples-row`, wrapper is not `.theme-examples-grade`) |

**Red on pre-fix tree** (`origin/sub/…/AST-2077` @ `e23ee4c5c`): `dark: expected [] to have a length of 2`. **Green** (7/7) with the plan's Proposed change step 1 applied locally (not committed); `tsc -b --noEmit` clean. The wrapper class name and the Recommended Job List's own rendering are not pinned here (the latter stays with `test_recommendedJobReport` AST-1968). Not tested: letterless dot size/colour (jsdom has no cascade → UAT).

**Integration:** none — frontend-only; do not invent.

#### QA test manifest (AST-2077)

```bash
cd src/ui/frontend && npx vitest run --config vite.config.ts ../../../tests/component/frontend/pages/test_AdminThemeExamples.test.tsx
```

**Pass criterion (test-fix):** the AST-2077 `[bug-repro]` flips red → green; the other 6 cases (AST-2047 page, AST-2064 options, 4 App.css) stay green.

### AST-2068 · AST-2043 (routed pages — blur-save + version arrows)

§6c routed-page coverage for the AST-2068 component change: **`ArtifactsBaseResumeContent`** (AC1/AC2 blur + AC4 arrows), **`ArtifactsDoJobCriteria`** (AC4 per criterion + AC2; stale `api` mock / manifest fixture repaired), **`CandidateBioSummary`** (AC4 + save-before-move). Full-paint mocks include the `/versions` and `/current` routes. Manifest: [`components.md`](components.md) § AST-2068.


---

### AST-2076 · AST-2042 (bug — Light accent → header purple; `--accent-gold*` renamed `--accent-contrast*`)

**Publish:** `origin/sub/AST-2042/AST-2076-light-accent-contrast`. **Scope from** `[board-betty] TESTS: REVISE` (stale AC4 key + bible renames), plus the red-first repro qa-fix requires. Fix (plan doc § Bug: AST-2076): six-file `--accent-gold` → `--accent-contrast` rename; in `light` / `light_parchment`, accent family = header purple, `--heading` / `--nav-group-label` → `var(--accent-contrast)`.

| Area | Source | Component tests |
| --- | --- | --- |
| **[bug-repro]** in `light` and `light_parchment`, `--accent-contrast` and `--nav-group-label` resolve (following `var()` within the block) to the same value as `--heading` | `App.css` token blocks | **`test_AdminThemeExamples.test.tsx`** — **`App.css theme token blocks — AST-2047 > [bug-repro] AST-2076: in light and light_parchment, the accent and nav group label resolve to the header colour`** |
| AC4 pairwise-differ key list retargeted `--accent-gold` → `--accent-contrast` | same | existing **`… > every Light block declares exactly the Dark token names, and the Lights pairwise differ (AC4)`** (still passes via `--bg-deep`) |
| Rename complete (no `var()` left pointing at a removed name) | all `.ts`/`.tsx`/`.css` | existing AC5 + AST-2049 guards (unchanged) |

**Red on pre-fix tree** (`origin/sub/…/AST-2076` @ `f3186d4c5`): `light --accent-contrast: expected undefined to be '#241b33'`. **Green** (8/8) with the plan's Proposed change steps 1–2 applied locally (not committed); `tsc -b --noEmit` clean. Purple hex values, hover/dim values, and Dark/Slate values are not pinned (palette choice → UAT; Dark-value equality is plan Verify step, not a test).

**Integration:** none — frontend-only; do not invent.

#### QA test manifest (AST-2076)

```bash
cd src/ui/frontend && npx vitest run --config vite.config.ts ../../../tests/component/frontend/pages/test_AdminThemeExamples.test.tsx
```

**Pass criterion (test-fix):** the AST-2076 `[bug-repro]` flips red → green; the other 7 cases stay green.

### AST-2083 · AST-2046 (theme gate on resume editor CSS)

**Unchanged test, product red:** `test_AdminThemeExamples.test.tsx` (8). Its AST-2047/AST-2049 token gates catch `var(--accent-gold)` (retired on dev, now `--accent-contrast`) and a literal `#fff` in AST-2083's App.css §10e2. That's 2 red until the product fix lands. Manifest and detail: [`components.md`](components.md) § AST-2083.

### AST-2084 · AST-2046 (Base Resume Content on the split pane)

**Rewritten:** `test_ArtifactsBaseResumeContent.test.tsx` (8). The 15 old cases are retired with the page they tested (structure tabs, accent bar, structure authoring, the page's own Print and Generate). It covers:
- **§6c page render** with full first-paint mocks: editor left (`Search sections`, sections, accent swatches) and base print preview right.
- **Preview refresh:** the preview refetches once per editor save and never while typing (one `PUT …/data`).
- **AC2/AC3:** no Generate/Regenerate/Save/Cancel.
- **Candidate switch:** retargets both panes.
- **No candidate:** shows the message, and no editor or print fetch happens.
- **Source gates:** no `Save sections` and no `useCandidateResumeStructure|structureCatalog|onStructureSave` anywhere in `src/ui/frontend/src` (AC2/AC5). The page has no `craft_resume_base` and no `ArtifactEditor` (AC3). Both resume surfaces use `ResumeContentEditor`. The AST-1577 ui-consistency directive check is kept.

Manifest: [`components.md`](components.md) § AST-2084.

### AST-2106 · AST-2102 (grouped, collapsible Skipped page)

**Publish:** `origin/sub/AST-2102/AST-2106-grouped-skipped-page`. Plan: `docs/features/interface/ast-2106-grouped-collapsible-skipped-page.md`. Rules come from manifest `jobs.skipped.groups` (AST-2105 — [`../utils/config.md`](../utils/config.md) § AST-2105).

`JobsSkipped.tsx` buckets every built section (below-floor, normal, legacy) by manifest rules — member, then first matching prefix, then the catch-all — and renders one collapsible heading `<label> (<total jobs>)` per non-empty group, in manifest order. Group collapse is a second `useSectionExpandPolicy` (`expandAll`) holding *collapsed* group keys, so groups start open and section Expand One is untouched. `StateUiContext.tsx` types `groups`.

| AC | Source | Component tests |
| --- | --- | --- |
| 4 Error / Bot block / Fail order + counts; each section inside its own group; no Other | `pages/JobsSkipped.tsx` | **`test_JobsSkipped.test.tsx`** › **`JobsSkipped — AST-2106 grouped, collapsible Skipped page`** › **`AC4: …`** |
| 5 `INVALID_TITLE` → Other (1) last; legacy `ERROR_SOMETHING_OLD` → Error, `MYSTERY_STATE` → Other after Fail | same | **`AC5: INVALID_TITLE adds Other (1) last`** · **`AC5: unmapped legacy …`** |
| 6 `virtual_skip` floor section under Fail, below Error | same | **`AC6: …`** |
| 7 group heading hides / restores its sections; open section stays open, closed stays closed; other groups untouched | same | **`AC7: …`** |
| 8 lone `FAILED_JD` → only Fail heading; empty → "No skipped jobs", no heading | same | **`AC8: …`** (×2) |
| 9 mixed `ERROR_EVALUATE_JD` + `FAILED_DO` Retry → exactly one `bulk_state` POST per target (`JD_READY`, `PASSED_JD`) | same (`handleRetry` unchanged) | **`AC9: …`**; sort / Resurrect / hop-correct Retry stay pinned by the existing AST-893 / AST-1064 / AST-1156 / AST-1410 / AST-1979 / AST-1982 cases |
| 10 no state / prefix literals in the page | source | grep below |
| 11 build / lint | source | commands below |

Group headings are located by exact text `▼<label> (<n>)`. Section membership is checked by DOM containment, and each group's button count equals 1 + its sections, which pins "nothing else in this group".

**Broken / obsolete (revised this pass):** `tests/component/frontend/fixtures/stateUiManifestFixture.ts`: `skipped` gains `groups`, mirroring AST-2105's manifest exactly. Without it, all 16 existing `test_JobsSkipped` cases throw on `sk.groups.find` and time out. No existing case needed a selector change: groups start open, and no section label collides with a group heading.

**Baseline red (not this ticket):** `test_JobDetailModal` › **`AST-1695 listing_href > read-only: null listing_href → no Link <a> …`** is red with and without this pass's test changes. It is already listed under § AST-1975's baseline reds.

**Integration:** none — frontend-only; do not invent.

## QA test manifest

1. **Skipped page suite (required, all green):** expect 24 passed (16 existing + 8 AST-2106).

```bash
cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_JobsSkipped.test.tsx
```

2. **Fixture consumers (regression):** only the baseline red above.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/contexts/test_StateUiContext.test.tsx \
  ../../../tests/component/frontend/components/test_NavigationShell.test.tsx \
  ../../../tests/component/frontend/components/test_JobDetailModal.test.tsx
```

3. **AC 10:** `rg -n '"[A-Z]+(_[A-Z]+)*_"|"[A-Z]+(_[A-Z]+)+"' src/ui/frontend/src/pages/JobsSkipped.tsx` returns nothing.

4. **AC 11:** in `src/ui/frontend`, `npx tsc -b --noEmit` and `npm run build` exit 0; `npm run lint` adds no problem absent on `origin/dev` (plan baseline `✖ 29 problems (25 errors, 4 warnings)`).

**Pass criterion:** items 1–4 hold. Narrowed runs, not the zero-arg harness.

**Bible shasums (after publish):** `git show origin/sub/AST-2102/AST-2106-grouped-skipped-page:docs/test-bible/frontend/pages.md | shasum`

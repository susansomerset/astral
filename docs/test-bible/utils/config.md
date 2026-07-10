# Config

**Test module:** `tests/component/utils/test_config.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/utils/config.py` | `tests/component/utils/test_config.py` | yes |

---

### AST-428 · AST-358

**`GRADE_VALUES`**, **`RUBRIC_TOTAL`**, **`grade_value()`** in `config.py`; graded consult tasks use encoded batch shapes — **`draft_job_resume`** is structure-keyed per **AST-594** (no `grades` / vectors on that hop).

| Area | Source | Component tests |
| --- | --- | --- |
| Grade constants + accessor | `src/utils/config.py` | `tests/component/utils/test_config.py` (`TestGradeValuesConfig`) |

---

### AST-468 · AST-376

**`resolve_dispatch_task_config_key`**, **`dispatch_task_key_is_scored`**, **`dispatch_claim_uses_score_floor`**, **`trigger_state_used_by_scored_dispatch_task`**, **`DISPATCH_SCHEDULABLE_TASK_KEYS`** / **`dispatch_task_admin_defaults`** centralize **`consult_*` → `grade_*`** indirection and admin form defaults for **`dispatcher.py`**, **`database.py`**, and **`api_admin.py`**. **`pass_threshold`** vs **`score_floor`**: **`docs/ASTRAL_CODE_RULES.md`** subsection under §2.1; claim gating vs grading metadata: **§7.13zv** (**AST-586**).

| Area | Source | Component tests |
| --- | --- | --- |
| Resolution helpers | `src/utils/config.py` | `tests/component/utils/test_config.py` (imports exercised via callers); **`tests/component/ui/api/test_api_admin.py`**, **`tests/component/core/test_dispatcher.py`**, `tests/component/data/` dispatch paths |
| Admin dispatch metadata + forms | `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py` (**`TestAdhocHelpers::test_trigger_state_helpers`**) |

Manifest default ( **`test-astral`** on publish tip — dispatch/admin resolution scope): `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_trigger_state_helpers tests/component/core/test_dispatcher.py tests/component/data/database/test_dispatch_tasks.py`.

---

### AST-479 · AST-480 · AST-478

**`consult_like`** success lands in **`PASSED_LIKE`** (not **`BUILD_ARTIFACTS`**). **`RECOMMENDED_JOB_STATES`** lists **`RECOMMENDED`**, **`BUILD_ARTIFACTS`**, **`CANDIDATE_REVIEW`** — pre-upshot **`PASSED_LIKE`** stays in **`IN_REVIEW`** / score-gated consult views. **`analysis_upshot`** dispatch (**AST-480**) runs at **`PASSED_LIKE`** / **`PASSED_LIKE_RETRY`** (scored claim), persists **`job_data["analysis_upshot"]`**, transitions **`PASSED_LIKE` → `RECOMMENDED`** (or **`PASSED_LIKE_RETRY`** on failure).

| Area | Source | Component tests |
| --- | --- | --- |
| `JOB_STATES` / `TASK_CONFIG["grade_like"]` / Recommended vs In-review lists | `src/utils/config.py` | **`TestAst479LikePassStates`** (`test_config.py`) |
| **`analysis_upshot`** task + trigger seed + PASSED_LIKE scored dispatch | `src/utils/config.py`, `src/data/database.py`, `src/core/consult.py` | **`TestAst480AnalysisUpshotConfig`**, **`TestAst471DispatchConfigHelpers`** (`test_config.py`); **`TestRunConsultTaskRoutes::test_routes_passed_like_to_analysis_upshot_batch`** (`test_consult.py`) |
| Jobs API recommended view passes `RECOMMENDED_JOB_STATES` | `src/ui/api/api_jobs.py` | **`test_list_recommended_and_default`** (`test_api_jobs.py`) |
| Recommended page + actions for review-like rows | `JobsRecommended.tsx`, `CandidateJobRowActions.tsx` | **`test_JobsRecommended.test.tsx`** (rubric-era; superseded for phase-score UI by **§7.13zm** **AST-522**) |

---

### AST-586 · AST-547

**`dispatch_claim_uses_score_floor`** gates **`get_new_job_batch`** / admin **`is_scored`** / **`count_eligible_for_dispatch_task`** — distinct from **`trigger_state_used_by_scored_dispatch_task`** (task grading metadata). Input triggers such as **VALID_TITLE** run scored **`qualify_job_listings`** but jobs lack **`latest_score`** until that step completes; claim must pass **`score_floor=None`**. Post-score outcomes (**PASSED_JD**, **PASSED_JOBLIST**, **PASSED_SCORE_GATED_STATES**) keep floor behavior.

| Area | Source | Component tests |
| --- | --- | --- |
| Claim helper | `src/utils/config.py` | **`TestAst586DispatchClaimScoreFloor`** in `tests/component/utils/test_config.py` |
| Dispatcher claim | `src/core/dispatcher.py` | **`TestRunUnified::test_qualify_valid_title_claim_without_score_floor`** |
| Admin list/create | `src/ui/api/api_admin.py` | **`TestDispatchTasks`** + **`TestAdhocHelpers::test_trigger_state_helpers`** in `tests/component/ui/api/test_api_admin.py` |

**AST-586** narrowed run (**`test-astral`** manifest):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst586DispatchClaimScoreFloor \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_qualify_valid_title_claim_without_score_floor \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_trigger_state_helpers
```

---

### AST-483 · AST-472

**`_decode_payload`** classifies pipe fields using **`norm`** (drop ASCII space, hyphen, colon before **`_GRADE_SEG.match`**). **`grades_meta`** / **`grades_encoded_notes`** metadata retains the pipe-stripped **original** fragment so **`job_title`** and **`key:value`** tails stay unchanged.

**`test-astral`** gate for **`AST-483`:** Use **only** the narrowed command below. With **no pytest args**, `run_component_tests.sh` runs the full **`tests/component`** tree and **`check_per_file_coverage.py`** (`LOCKED_AT_100`); that gate currently trips on **`src/utils/config.py`**, **`src/core/roster.py`**, and **`src/core/consult.py`** (and similarly on **`origin/dev`**) independently of **`AST-483`** — so listing the zero-arg invocation in the **`Tests Ready`** manifest is **not** a reproducible merge path until those locks regain 100%. Narrow args skip the **`$# == 0`** branch-lock step per `run_component_tests.sh`; Vitest still runs after pytest.

| Area | Source | Component tests |
| --- | --- | --- |
| **`evaluate_jd`** prettified **`grades`** vs compact; **`grades_meta`** title spaces | `src/core/agent.py` (`_decode_payload`) | **`TestDecodePayload::test_decodes_whitespace_inside_grade_tokens_preserves_meta`** (`tests/component/core/test_agent.py`) |

Narrow (**`test-astral`** **AST-483** tip):

```bash
./scripts/testing/run_component_tests.sh tests/component/core/test_agent.py::TestDecodePayload::test_decodes_whitespace_inside_grade_tokens_preserves_meta
```

---

### AST-775 · AST-754

**AST-775:** Register **`VET_FAILED`** in **`COMPANY_STATES`** and **`("NEW", "VET_FAILED")`** in **`company_state_transitions`** — vet dispatch wiring is **AST-776**. Discovery batch record-only path: **`docs/test-bible/core/roster.md`** (**AST-775**).

| Area | Manifest tests |
| --- | --- |
| **`VET_FAILED`** state + transition | `tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_failed_state_and_transition` |

---

### AST-814 · AST-813

**AST-814:** Remove **`scan_interval_hours`** / **`dispatch_freq_hrs`** from **`INFLOW_CONFIG["discovery"]`**; cadence is **`dispatch_task.freq_hrs`** only.

| # | Scenario | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1 | Discovery config has no scan interval literals | `src/utils/config.py` | **`TestAst525InflowDiscoveryConfig::test_discovery_config_has_no_scan_interval_literals`** |
| 2 | **`test_inflow_config_discovery_literals`** omits removed keys | same | **`TestAst505InflowDiscoveryConfig::test_inflow_config_discovery_literals`** |

**Broken / obsolete:** **`TestAst525InflowDiscoveryConfig::test_scan_interval_hours_literal`** removed.


### AST-776 · AST-754

**AST-776:** **`INFLOW_CONFIG["vet"]`** block; **`vet_inflow_discovery`** schedulable as company/**`NEW`**; **`_dispatch_trigger_state_for_task_key`** vet branch; eligibility counters **`count_company_new_pending_inflow_vet`** / narrowed **`count_company_new_without_website`**. Roster vet execution: **`docs/test-bible/core/roster.md`** (**AST-776**).

| AC | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1 | **`INFLOW_CONFIG["vet"]`** literals + admin defaults | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_inflow_config_vet_literals`; `::test_vet_inflow_discovery_task`; `::test_vet_inflow_discovery_dispatch_admin_defaults` |
| 2 | Eligibility split vet vs resolve | `src/data/database.py` | `tests/component/data/database/test_dispatch_tasks.py::TestAst776InflowVetEligible` |

**AST-776** narrowed run (config + database slice):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_inflow_config_vet_literals \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_inflow_discovery_task \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_inflow_discovery_dispatch_admin_defaults \
  tests/component/data/database/test_dispatch_tasks.py::TestAst776InflowVetEligible \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless **`test-child`** widens.

---

### AST-504 · AST-505 · AST-506 · AST-490

Phase 0: newline-delimited **`artifacts.company_search_terms`**, **`craft_company_search_terms`** (on-demand generate only — no **`dispatch_tasks`** row), Artifacts page + save normalization. Phase 1 (**AST-505**): weekly **`inflow_discovery`** candidate dispatch, Google CSE per term, **`vet_inflow_discovery`**, **`ingest_new_companies`** with candidate-scoped URL dedupe, **`NEW`** / **`WEBSITE_FOUND`** company states. Phase 2 (**AST-506**): **`inflow_resolve_website`** company dispatch for **`NEW`** rows with empty **`company_website`**; CSE resolution (20 results, no date restrict) + **`find_company_website`** → **`WEBSITE_FOUND`** or **`NO_WEBSITE`**.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-504** | String artifact + craft task config; normalize on PUT; Artifacts UI generate/regenerate/edit | `src/utils/config.py`, `src/core/candidate.py`, `src/ui/api/api_candidate.py`, `src/ui/frontend/src/pages/ArtifactsCompanySearchTerms.tsx`, `src/ui/frontend/src/routes.tsx` | `tests/component/utils/test_config.py::TestAst504CompanySearchTermsConfig`; `tests/component/core/test_candidate.py::{TestNormalizeCompanySearchTermsOnSave,TestCompanySearchTermsLines}`; `tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_update_rejects_blank_company_search_terms`; `tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx` |
| **AST-505** | Candidate dispatch eligibility; CSE + vet + ingest; **`NEW`** / **`WEBSITE_FOUND`** | `src/utils/config.py`, `src/data/database.py`, `src/core/dispatcher.py`, `src/core/consult.py`, `src/core/roster.py` | `tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig`; `tests/component/data/database/test_dispatch_tasks.py::TestAst505InflowDiscoveryEligible`; `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast505_candidate_entity_routes_ctx_without_company_clear`; `tests/component/core/test_roster.py::TestAst505InflowDiscovery` |
| **AST-505** | CSE + vet + ingest; **`NEW`** / **`WEBSITE_FOUND`** (eligibility cadence → **AST-525** when table is source of truth) | `src/utils/config.py`, `src/data/database.py`, `src/core/dispatcher.py`, `src/core/consult.py`, `src/core/roster.py` | `tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig`; `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast505_candidate_entity_routes_ctx_without_company_clear`; `tests/component/core/test_roster.py::TestAst505InflowDiscovery` |
| **AST-506** | Empty-website claim filter; CSE resolution + **`find_company_website`**; **`NEW → WEBSITE_FOUND \| NO_WEBSITE`** | `src/utils/config.py`, `src/data/database.py`, `src/core/dispatcher.py`, `src/core/roster.py` | `tests/component/utils/test_config.py::TestAst506InflowResolveConfig`; `tests/component/data/database/test_dispatch_tasks.py::TestAst506InflowResolveEligible`; `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast506_inflow_resolve_claims_empty_website_only`; `tests/component/core/test_roster.py::TestAst506InflowResolve` |

**AST-504** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst504CompanySearchTermsConfig \
  tests/component/core/test_candidate.py::TestNormalizeCompanySearchTermsOnSave \
  tests/component/core/test_candidate.py::TestCompanySearchTermsLines \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_update_rejects_blank_company_search_terms \
  tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx
```

**Harness tail (items 1–4):** `run_component_tests.sh` always runs full Vitest coverage after pytest. Cross-ticket page tests must stay green — notably **`test_AdminManageCandidates.test.tsx`** (AST-511 middle-name field selectors).

**AST-505** narrowed run (blocker **AST-504** tests optional smoke — terms artifact must exist for dispatch eligibility):
**AST-505** narrowed run (blocker **AST-504** tests optional smoke — terms artifact must exist for legacy artifact path; per-term eligibility → **AST-525**):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig \
  tests/component/data/database/test_dispatch_tasks.py::TestAst505InflowDiscoveryEligible \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast505_candidate_entity_routes_ctx_without_company_clear \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery
```

**AST-506** narrowed run (blocker **AST-505** tests optional smoke — **`NEW`** ingest path must exist):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst506InflowResolveConfig \
  tests/component/data/database/test_dispatch_tasks.py::TestAst506InflowResolveEligible \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast506_inflow_resolve_claims_empty_website_only \
  tests/component/core/test_roster.py::TestAst506InflowResolve
```

**Admin prerequisite (Stage 5):** **`craft_company_search_terms`** task prompt row must exist in Admin → Task Prompts before Generate works in UAT (not seeded in product code). **`vet_inflow_discovery`** prompt row required before Phase 1 vet runs in UAT. **Blocker:** **AST-504** (`company_search_terms` artifact) must be on the integration line before dispatch eligibility and discovery batch run in UAT.

---

### AST-507 · AST-508 · AST-490

Phase 3 (**AST-507**): **`prefilter_company`** uses **`grades_encoded`** decode shape (`jobs[0].grades`), dealbreaker-only **F** with confidence ≥ 2, **`prefilter_score`** on pass, inflow **`NEW → WEBSITE_FOUND`** history → **PREFILTER_PASSED** / **PREFILTER_FAILED**; legacy manual path → **TO_WATCH** / **IGNORE**. Phase 4–5 (**AST-508**): **`PREFILTER_PASSED`** companies enter existing **`find_job_page` → `select_job_page` → `parse_job_list`** via dispatch with **`score_floor`** on the **`dispatch_task`** row (JSON **`company_data.prefilter_score`**); below-floor rows stay unclaimed. Depends on **AST-506** (**WEBSITE_FOUND**). Blocker bible: **AST-506** (**§7.13zg**); **AST-508** build gate **AST-507**.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-507** | Encoded rubric prefilter; dual state targets via `state_history`; config states/transitions | `src/utils/config.py`, `src/core/roster.py` | `tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig`; `tests/component/core/test_roster.py::{TestPrefilterCompany::test_pass_and_fail_grades_persist_data,TestAst507EncodedPrefilter,TestRunCompanyTask::test_prefilter_pass_and_fail}` |
| **AST-508** | **`dispatch_input_states`** + **`INFLOW_CONFIG.locate`**; company **`score_floor`** claim/count; dispatcher passthrough; **`PREFILTER_PASSED → find_job_page`** | `src/utils/config.py`, `src/data/database.py`, `src/core/dispatcher.py`, `src/core/roster.py` | `tests/component/utils/test_config.py::TestAst508InflowLocateConfig`; `tests/component/data/database/test_dispatch_tasks.py::TestAst508PrefilterPassedEligible`; `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast508_prefilter_passed_dispatch_passes_score_floor`; `tests/component/core/test_roster.py::TestRunCompanyTask::test_prefilter_passed_routes_to_find_job_page` |

**AST-507** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig \
  tests/component/core/test_roster.py::TestPrefilterCompany::test_pass_and_fail_grades_persist_data \
  tests/component/core/test_roster.py::TestAst507EncodedPrefilter \
  tests/component/core/test_roster.py::TestRunCompanyTask::test_prefilter_pass_and_fail
```

**AST-508** narrowed run (blocker **AST-507** tests optional smoke — **`PREFILTER_PASSED`** + **`prefilter_score`** must exist):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst508InflowLocateConfig \
  tests/component/data/database/test_dispatch_tasks.py::TestAst508PrefilterPassedEligible \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast508_prefilter_passed_dispatch_passes_score_floor \
  tests/component/core/test_roster.py::TestRunCompanyTask::test_prefilter_passed_routes_to_find_job_page
```

---

### AST-515 · AST-514

Workbench **Test** (`POST /api/admin/adhoc/test`) creates **`dispatch_ledger`** rows with **`task_key`** `adhoc-<workbench_task_key>`, **`log_batch_id`**, and **`agent_data`** blocks via **`run_adhoc_workbench_test`** in **`agent.py`**. **Preview** stays ledger-free. Execution History UI (**`AdminPerformanceMonitor`**) unchanged — list/expand/inspect use existing ledger + **`/api/agent_data/<batch_id>`** APIs.

---

### AST-530 · AST-527

Structured **`run_next`** hop observability: parent → child **`task_key`**, **`batch_id`**, per-**`CALLER_*`** populated/empty + length; chain-entry vs mid-chain warning shape in **`resolve_tokens`**; mid-chain fail-fast when a referenced **`{$CALLER_*}`** resolves empty (no LLM call). Debug on the dispatch entry hop propagates to recursive hops. Does **not** fix caller propagation (**AST-529**) or Execution History rows (**AST-528**).

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-530** | **`CALLER_HOP_TOKEN_NAMES`**; hop-boundary INFO logs; chain-entry marker; mid-chain empty-caller guard | `src/utils/config.py` (`resolve_tokens`, `CALLER_HOP_TOKEN_NAMES`), `src/core/agent.py` (`do_task` hop helpers) | `tests/component/utils/test_config.py::TestAst530ChainHopResolveTokens`; `tests/component/core/test_agent.py::TestDoTask::{test_chain_entry_log,test_hop_boundary_log_on_run_next,test_mid_chain_empty_caller_skips_api,test_debug_flag_passed_to_child}` |

**AST-530** narrowed run (include daisy-chain regression from parent AC #5). Chain-hop **`TestDoTask`** cases pin **`get_active_llm_provider`** to **`anthropic`** and use the AST-501 envelope in mocks — no **`ASTRAL_LLM_PROVIDER`** export required for pytest-only runs:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst530ChainHopResolveTokens \
  tests/component/core/test_agent.py::TestDoTask::test_chain_entry_log \
  tests/component/core/test_agent.py::TestDoTask::test_hop_boundary_log_on_run_next \
  tests/component/core/test_agent.py::TestDoTask::test_mid_chain_empty_caller_skips_api \
  tests/component/core/test_agent.py::TestDoTask::test_debug_flag_passed_to_child \
  tests/component/core/test_agent.py::TestDoTask::test_chains_run_next_when_configured \
  tests/component/core/test_agent.py::TestChainContext
```

---

### AST-641 · AST-642 · AST-630

**AST-630 (parent):** Primary dispatch `trigger_state` rows (not ending in `_RETRY`) **count** and **claim** eligible entities in both the primary state and its registry companion `trigger_state + "_RETRY"` when that companion exists in `JOB_STATES` / `COMPANY_STATES`. Retry-only rows stay single-state. Score-floor gating remains keyed off the dispatch row’s `trigger_state` via **`dispatch_claim_uses_score_floor`** — one floor across the combined pool when scored. Mixed consult batches route envelope/hydration/missing-ID/bad-grade failures **per entity** — primary → `retry_state`, `*_RETRY` → terminal `error_state`; `analysis_upshot` second failure → `FAILED_TECHNICAL`.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-641** | `dispatch_claim_states`; multi-state SQL in claim/count; dispatcher passes `states=` into batch helpers | `src/utils/config.py`, `src/data/database.py`, `src/core/tracker.py`, `src/core/roster.py`, `src/core/dispatcher.py` | `tests/component/utils/test_config.py::TestAst641DispatchClaimStates`; `tests/component/data/database/test_dispatch_tasks.py::TestAst641UnionClaimCount`; `tests/component/core/test_dispatcher.py` **`test_ast641_*`** |
| **AST-642** | `_consult_batch_fail_dest`; `_transition_batch_consult_failures`; per-entity routing in `_run_batch_consult`, `_run_analysis_upshot_batch`, qualify short-title path | `src/core/consult.py` | `tests/component/core/test_consult.py::TestConsultBatchFailDest`; `tests/component/core/test_consult.py::TestAst642PerEntityBatchRetry` |

**AST-641** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst641DispatchClaimStates \
  tests/component/data/database/test_dispatch_tasks.py::TestAst641UnionClaimCount \
  tests/component/core/test_dispatcher.py -k ast641
```

**AST-642** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestConsultBatchFailDest \
  tests/component/core/test_consult.py::TestAst642PerEntityBatchRetry
```

---

### AST-676 · AST-655

Rename craft task key **`craft_company_prefilter`** → **`craft_prefilter_rubric`** (stored artifact **`company_prefilter`** unchanged). All six Phase B rubric craft tasks share **`_CRAFT_RUBRIC_CRITERIA_RESPONSE_SCHEMA`** — each `criteria` item requires integer **`importance`** in **1–10** at **`do_task`** schema validation. UI rename (**AST-677**) is sibling scope; admin prompt bodies are manual paste (**AST-685** reverts **AST-678** auto-migration).

| Area | Source | Component tests |
| --- | --- | --- |
| Task key + shared rubric schema | `src/utils/config.py` | **`TestAst676CraftRubricSchema`** (`tests/component/utils/test_config.py`) |
| Int min/max + bool rejection in validator | `src/core/agent.py` (`_validate_response_schema`) | **`TestResponseSchemaBranches::test_ast676_*`** (`tests/component/core/test_agent.py`) |

**AST-676** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst676CraftRubricSchema \
  tests/component/core/test_agent.py::TestResponseSchemaBranches::test_ast676_int_bounds_and_bool_rejection \
  tests/component/core/test_agent.py::TestResponseSchemaBranches::test_ast676_craft_rubric_criteria_schema
```

---

### AST-697 · AST-696

**`stringify_response_schema("prefilter_company")`** shows Susan's canonical bracket **link_set** example; **`grades_encoded_prefilter_links`** payload instructions document positional tails before **`JOB:`** / **`CULT:`** alternates. Decode wiring lives in **`docs/test-bible/core/consult.md`** and **`docs/test-bible/core/agent.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Schema example | `src/utils/config.py` (`stringify_response_schema`) | `tests/component/utils/test_config.py::TestStringifyResponseSchema::test_prefilter_company_schema_shows_bracket_link_set_tails` |
| Output type key | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig::test_prefilter_company_grades_encoded` |

---

### AST-701 · AST-700

**AST-701:** **`HOMEPAGE_READY`** company state; **`WEBSITE_FOUND`** / **`WEBSITE_FOUND_RETRY`** → **`HOMEPAGE_READY`** / **`CANNOT_READ_WEBSITE`** transitions; **`GAZER_CONFIG["fetch_website"]`**; **`homepage_text`** in **`ROSTER_CONFIG["company_data_keys"]`**; **`fetch_website`** schedulable dispatch key (**`trigger_state=WEBSITE_FOUND`**).

| Area | Source | Component tests |
| --- | --- | --- |
| State + transitions + gazer config | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst701FetchWebsiteConfig` |

---

### AST-718 · AST-716

**`NO_PREFILTER_JOBLISTS`** terminal state + **`HOMEPAGE_READY` / `WEBSITE_FOUND` / `WEBSITE_FOUND_RETRY`** transitions; **`ROSTER_CONFIG["prefilter"]["no_pjl_state"]`**, **`pjl_url_data_key`**, **`company_data_keys.possible_joblist_links`**. Not in **`pass_states`**.

| Area | Source | Component tests |
| --- | --- | --- |
| State + routing keys | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig::test_company_states_and_transitions` |

Roster routing + hydration: **`docs/test-bible/core/roster.md`** (**AST-718**).

---

### AST-720 · AST-716

**`JOBLIST_IDENTIFIED`**, **`PREFILTER_PASSED_RETRY`**, **`NO_PJL_SELECTED`**; **`ROSTER_CONFIG["select_job_page"]`**; **`_dispatch_trigger_state_for_task_key("select_job_page")` → `PJL_READY`**; **`fetch_job_pages_trigger_states`** includes retry loop input.

| Area | Source | Component tests |
| --- | --- | --- |
| Selection states + select dispatch config | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst720SelectJobPageConfig` |

Roster decomposed select: **`docs/test-bible/core/roster.md`** (**AST-720**).

---

### AST-721 · AST-716

**`JOBLIST_IDENTIFIED_RETRY`**, **`COULD_NOT_PARSE_JOBLIST`**; **`ROSTER_CONFIG["parse_job_list"]`**; **`_dispatch_trigger_state_for_task_key("parse_job_list")` → `JOBLIST_IDENTIFIED`**; **`find_job_page`** removed from **`DISPATCH_SCHEDULABLE_TASK_KEYS`**; **`locate_job_page.dispatch_input_states`** → **`JOBS_FOUND`** only.

| Area | Source | Component tests |
| --- | --- | --- |
| Parse states + dispatch config | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst721ParseJobListConfig` |

Roster decomposed parse: **`docs/test-bible/core/roster.md`** (**AST-721**).

---

### AST-719 · AST-716

**`PJL_READY`** state + **`PREFILTER_PASSED → PJL_READY|JOBSITE_SCRAPE_ISSUE`** transitions; **`GAZER_CONFIG["fetch_job_pages"]`**; **`pjl_scrape_pages`**, **`pjl_assembled_content`**, **`pjl_nav_links`** company_data keys; schedulable **`fetch_job_pages`** @ **`PREFILTER_PASSED`**.

| Area | Source | Component tests |
| --- | --- | --- |
| State + gazer orch + dispatch registry | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst719FetchJobPagesConfig` |

Gazer batch + roster helpers: **`docs/test-bible/core/gazer.md`** · **`docs/test-bible/core/roster.md`** (**AST-719**).

---

### AST-702 · AST-700

**AST-702:** **`ROSTER_CONFIG["prefilter"]["input_state"]` → `HOMEPAGE_READY`**; **`HOMEPAGE_READY.retry_state` → `WEBSITE_FOUND_RETRY`**; evaluate-outcome transitions; **`prefilter`** in **`_DISPATCH_BATCH_CALL_MODE_ONE`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Input state + batch mode + transitions | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst702PrefilterBatchConfig` |

---

### AST-707 · AST-700

**AST-707:** **`EMBEDDED_COMPANY_PREFILTER_CRITERIA`** — canonical **RC** row prepended for **`company_prefilter`** hydration (artifact rows with duplicate **RC** code deduped).

| Area | Source | Component tests |
| --- | --- | --- |
| Embedded RC registry | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst707EmbeddedPrefilterConfig` |

Consult merge + roster batch regression: **`docs/test-bible/core/consult.md`** · **`docs/test-bible/core/roster.md`** (**AST-707**).

---

### AST-695 · AST-694

**Scope:** `LLM_PROVIDER_CONFIG["tier_map"]["deepseek"][BRAIN_MEDIUM]` — Medium retargets from `deepseek-v4-flash` + thinking to `deepseek-v4-pro` non-thinking (**AST-694** ladder). Little and Big unchanged; runtime dispatch reads tier meta from config — no `agent.py` / `deepseek.py` edits.

| Area | Source | Component tests |
| --- | --- | --- |
| DeepSeek tier meta resolution | `src/utils/config.py` | **`TestAst492LlmBrainTierConfig::test_resolve_deepseek_tier_meta`** |
| **`do_task`** DeepSeek vendor_model + tier_meta | `src/core/agent.py` | **`TestAst492BrainSettingDoTask::test_send_to_deepseek_receives_vendor_model_and_tier_meta`** |
| Admin **`_resolve_adhoc`** DeepSeek payload | `src/ui/api/api_admin.py` | **`TestAst492ResolveAdhocApiAdmin::test_resolve_adhoc_deepseek_sets_tier_meta_and_vendor_as_model_code`** |

**AST-695** narrowed run (**pass criterion:** pytest green — not zero-arg harness / branch-lock gate):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst492LlmBrainTierConfig::test_resolve_deepseek_tier_meta \
  tests/component/core/test_agent.py::TestAst492BrainSettingDoTask::test_send_to_deepseek_receives_vendor_model_and_tier_meta \
  tests/component/ui/api/test_api_admin.py::TestAst492ResolveAdhocApiAdmin::test_resolve_adhoc_deepseek_sets_tier_meta_and_vendor_as_model_code
```

---

### AST-722 · AST-378

**`FEEDBACK`** added to **`BLOCK_TYPES`** for future **`vector_feedback`** agent_data rows (**AST-724** writes). **`RUBRIC_FEEDBACK_CONFIG`** defines relevance/clarity/verdict type codes and single-letter value codes for envelope validation.

| Area | Source | Component tests |
| --- | --- | --- |
| `FEEDBACK` block type | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst722RubricFeedbackConfig::test_feedback_in_block_types` |
| Feedback type/value registry | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst722RubricFeedbackConfig::test_rubric_feedback_config_shapes` |
| `save_agent_data` accepts `FEEDBACK` | `src/data/database.py` | `tests/component/data/database/test_rubric_vectors.py::TestFeedbackBlockType` |

Database schema + backfill script: **`docs/test-bible/data/database/rubric_vectors.md`**, **`docs/test-bible/dev/backfill_rubric_vectors.md`**.


### AST-726 (parent AST-717)

**Scope:** `TASK_CONFIG["prefilter_company"]` adds `grades_key: "prefilter_grades"` for scored entity-story hydration.

| Area | Source | Component tests |
| --- | --- | --- |
| `prefilter_company` `grades_key` | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst726PrefilterGradesKey::test_prefilter_company_grades_key` |

Roster story + consult saves: **`docs/test-bible/core/roster.md`**, **`docs/test-bible/core/consult.md`** (**AST-726**).

### AST-723 · AST-378

**`RUBRIC_VECTORS`** token registry; legacy per-artifact rubric tokens removed from **`TOKEN_SOURCES`**; **`rubric_owner_task_key`** + **`JOB_TOKEN_CONFIG["analysis_phases"].rubric_owner_task_key`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Token registry + owner mapping | `src/utils/config.py` | `TestAst723RubricVectorsToken` |
| `resolve_tokens` rubric source | `src/utils/config.py` | `TestResolveTokens::test_resolves_candidate_config_output_and_chain_tokens` (updated for **`{$RUBRIC_VECTORS}`**) |

**AST-723** narrowed run:

```bash
./scripts/testing/run_component_tests.sh   tests/component/data/database/test_rubric_vectors.py::TestAst723SyncRubricVectors   tests/component/data/database/test_rubric_vectors.py::TestAst723RubricTokenMigration   tests/component/core/test_candidate.py::TestAst723RubricVectorsCutover   tests/component/core/test_consult.py::TestRubricHelpers   tests/component/utils/test_config.py::TestAst723RubricVectorsToken   tests/component/utils/test_config.py::TestResolveTokens::test_resolves_candidate_config_output_and_chain_tokens   tests/component/ui/api/test_api_candidate.py::TestAst723RubricVectorsApi   -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.


### AST-724 · AST-378

**`is_rubric_backed_task`** gates rubric-backed **`do_task`** prompt suffix injection and vector-feedback capture; **`RUBRIC_FEEDBACK_CONFIG["prompt_suffix"]`** documents the **`vector_reviews`** envelope contract.

| Area | Source | Component tests |
| --- | --- | --- |
| Rubric-backed consumer/craft gate | `src/utils/config.py` | `TestAst724RubricBackedTask::test_is_rubric_backed_consumer_and_craft` |
| Prompt suffix in config | `src/utils/config.py` | `TestAst724RubricBackedTask::test_prompt_suffix_present_in_rubric_feedback_config` |

**AST-724** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst724RubricBackedTask \
  tests/component/utils/test_rubric_feedback.py \
  tests/component/core/test_agent.py::TestAst724VectorFeedbackCapture \
  tests/component/data/database/test_rubric_vectors.py::TestAst724VectorFeedbackRows \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-859 · AST-378 (UAT fix)

**`RUBRIC_FEEDBACK_CONFIG["prompt_suffix"]`** — fix contradictory **`Q1RAOCVK`** example to **`Q1RACOVK`** so model output matches **`parse_vector_review_string`** delimiter regex.

| Area | Source | Component tests |
| --- | --- | --- |
| Prompt suffix example | `src/utils/config.py` | `TestAst859VectorReviewsPromptExample::test_prompt_suffix_example_is_racovk_not_raocvk` |

Parse regression (Susan staging **`CLRAOCVK`** vs correct **`CLRRACOVK`**): **`docs/test-bible/utils/rubric_feedback.md`**.

**AST-859** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst859VectorReviewsPromptExample \
  tests/component/utils/test_rubric_feedback.py::TestAst859CompactStringParseExamples \
  -q
```

### AST-725 · AST-378

**`task_keys_for_rubric_owner`** and **`rubric_owner_task_key_choices`** for Admin Vector Feedback task filter and data-layer owner expansion.

| Area | Source | Component tests |
| --- | --- | --- |
| Consumer + craft run keys | `src/utils/config.py` | `TestAst725RubricOwnerRunKeys::test_task_keys_for_rubric_owner_includes_consumer_and_craft` |
| Sorted owner choices | `src/utils/config.py` | `TestAst725RubricOwnerRunKeys::test_rubric_owner_task_key_choices_sorted_owner_keys` |

### AST-740 · AST-734

Removes legacy `phase` / `seq` from every `TASK_CONFIG` entry; adds explicit `JOB_ARTIFACT_ENTRY_TASK_KEYS` for consult job-artifact dispatch hops (replaces phase-string probe). UI grouping is DB-only (**AST-738** / **AST-739**).

| Area | Source | Component tests |
| --- | --- | --- |
| No `phase`/`seq` in `TASK_CONFIG` | `src/utils/config.py` | `TestAst740RemoveConfigGrouping::test_task_config_entries_lack_phase_and_seq` |
| Artifact hop frozenset | `src/utils/config.py`, `src/core/consult.py` | `TestAst740RemoveConfigGrouping::test_job_artifact_entry_task_keys_membership` |
| Revised AST-520/504/505 config assertions | `tests/component/utils/test_config.py` | `TestAst520AnticipateScanTaskKey`, `TestAst504CompanySearchTermsConfig`, `TestAst505InflowDiscoveryConfig` |
| Seed defaults without config phase | `scripts/migrations/backfill_task_grouping_metadata.py` | `TestAst738TaskGroupingMetadata` (revised unassigned defaults) |
| API drops backward-compat `phase`/`seq` | `src/ui/api/api_admin.py` | `TestAst740NoConfigPhaseSeqInApi`; revised `TestAst738TaskGroupingApi` |

**AST-740** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst740RemoveConfigGrouping \
  tests/component/utils/test_config.py::TestAst520AnticipateScanTaskKey \
  tests/component/utils/test_config.py::TestAst504CompanySearchTermsConfig \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_inflow_discovery_task \
  tests/component/data/database/test_agent_tasks.py::TestAst738TaskGroupingMetadata \
  tests/component/ui/api/test_api_admin.py::TestAst740NoConfigPhaseSeqInApi \
  tests/component/ui/api/test_api_admin.py::TestAst738TaskGroupingApi \
  tests/component/ui/api/test_api_admin.py::TestTaskRoutes::test_preview_task_and_get_update \
  -q
```

### AST-750 · AST-743

**`DISPATCH_SCORE_FLOOR_VALUES`** (0.0–10.0 in 0.5 steps) and **`dispatch_score_floor_option_labels()`** are the single source of truth for the admin Edit Dispatch Task **Score Floor** `<select>`. **`GET /api/admin/dispatch_tasks/score_floor_options`** exposes the label list; **`AdminScheduledActions.tsx`** fetches options on load and persists **0.00** via `Number.isFinite` save coercion (not `parseFloat(...) || 1`).

| Area | Source | Component tests |
| --- | --- | --- |
| Catalog tuple + label helper | `src/utils/config.py` | `TestAst750DispatchScoreFloorCatalog` (`test_config.py`) |
| Admin metadata endpoint | `src/ui/api/api_admin.py` | `TestDispatchTasks::test_scheduler_and_run_controls` (score_floor_options assertion) |
| Scheduled Actions modal (**§6c**) | `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | `test_AdminScheduledActions.test.tsx` — **`AST-750: edit save sends score_floor 0 when 0.00 selected`** |

**AST-750** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst750DispatchScoreFloorCatalog \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_scheduler_and_run_controls \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  -t "AST-750"
```


---

### AST-796 · AST-794

**Scope:** **`GAZER_CONFIG`** rename **`scrape_jd` → `fetch_jd`** (+ transitional read alias removed in **AST-797**); **`DISPATCH_SCHEDULABLE_TASK_KEYS`** / **`DISPATCH_RETIRED_TASK_KEYS`** cutover; extended **`dispatch_task_key_retired_message`**. Runtime routing: **AST-797**.

| Area | Source | Component tests |
| --- | --- | --- |
| Schedulable + retired catalogs | `src/utils/config.py` | `TestAst796FetchJdSchedulableCutover` |
| Admin POST + **`task_keys`** | `src/ui/api/api_admin.py` | `TestAst796FetchJdRetiredDispatchKeys` |

**AST-796** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst796FetchJdSchedulableCutover \
  tests/component/ui/api/test_api_admin.py::TestAst796FetchJdRetiredDispatchKeys \
  -q
```

---

### AST-797 · AST-794

**Runtime config:** remove **`GAZER_CONFIG["scrape_jd"]`** alias; **`dispatch_task_admin_defaults("qualify_job_listings")`** → **`trigger_state=NEW`**; primary NEW row claims **NEW** only (**VALID_TITLE_RETRY** companion seeded by migration).

| Area | Source | Component tests |
| --- | --- | --- |
| Qualify @ NEW + alias removal | `src/utils/config.py` | `TestAst797ConfigRuntimeCutover`; revised **`TestAst549DispatchAdminDefaults::test_qualify_job_listings_batch_call_mode_and_sort`**; revised **`TestAst796FetchJdSchedulableCutover::test_gazer_config_fetch_jd_without_transitional_alias`** |

**AST-797** narrowed run: see **`docs/test-bible/core/consult.md`** (**AST-797**).

---

### AST-848 · AST-847

**Dispatch hop label helpers** — **`dispatch_hop_label`**, **`parse_dispatch_hop_label`**, **`DISPATCH_CHAIN_TERMINAL_GRADUATION`**, **`dispatch_chain_graduation_target`**; **`is_valid_job_batch_claim_state`** accepts runtime **`{trigger}.{hop}`** labels when trigger is in graduation map.

| Area | Source | Component tests |
| --- | --- | --- |
| Label helpers + claim predicate | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst848DispatchHopLabels` |

Primary manifest: **`docs/test-bible/core/agent.md`** AST-848.

---

### AST-849 · AST-847

**`dispatch_chain_claim_states_for_row`**, **`dispatch_chain_row_matches_job`**, **`is_dispatch_chain_trigger`**, **`_agent_task_parents_with_run_next`** — claim states derived from live **`agent_task.run_next`** graph (not **`resume_artifact_hop_task_keys()`**).

| Area | Source | Component tests |
| --- | --- | --- |
| Claim states + row match | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst849DispatchChainClaimStates` |

Primary manifest: **`docs/test-bible/core/agent.md`** AST-849.

---

### AST-828 · AST-752 (UAT bug)

**`is_valid_job_batch_claim_state`:** true for **`JOB_STATES`** keys and legacy **`BUILD_ARTIFACTS.<hop>`** via **`legacy_build_artifacts_hop`** — batch claim boundary only; does not expand **`JOB_STATES`** registry.

| Area | Source | Component tests |
| --- | --- | --- |
| Helper true/false cases | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst828JobBatchClaimStateValidation` |

Tracker batch API manifest: **`docs/test-bible/core/tracker.md`** (**AST-828**).

---

### AST-853 · AST-850

**`PLAYWRIGHT_CONFIG`:** launch timeouts/retries, page goto timeout, connectivity timeout, context recovery cap, per-company scrape wall clock, Firefox sandbox prefs (AST-853).

| Area | Source | Component tests |
| --- | --- | --- |
| Config literals | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst853PlaywrightConfig` |

External + gazer manifests: **`docs/test-bible/external/playwright.md`** (**AST-853**).

---

### AST-854 · AST-850

**`GAZER_CONFIG["fetch_website"]["retry_state"]`** — **`WEBSITE_FOUND_RETRY`** for infra fail routing (**AST-854**).

| Area | Source | Component tests |
| --- | --- | --- |
| **`retry_state`** on **`fetch_website`** gazer entry | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst701FetchWebsiteConfig`, `::TestAst854FetchWebsiteRetryConfig` |

Gazer routing manifest: **`docs/test-bible/core/gazer.md`** (**AST-854**).

---

### AST-765 · AST-757 (SUNSET — documentation)

**RETIRED (AST-757):** Boards channel removed from product (**AST-765**) and schema (**AST-766**). No active boards manifest obligations. See **`docs/ASTRAL_CODE_RULES.md` §3.7**.

---

### AST-782 · AST-756

**`REPO_ADMIN_JSON_CONFIG`:** repo-relative paths under `data/admin/`, agent export column list (excludes legacy `model_code`), fixed apply order **agent → agent_task**.

| Area | Source | Component tests |
| --- | --- | --- |
| Path helpers + table key order | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst782RepoAdminJsonConfig` |

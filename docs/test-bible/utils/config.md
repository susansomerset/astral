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

**`resolve_dispatch_task_config_key`**, **`dispatch_task_key_is_scored`**, **`dispatch_claim_uses_score_floor`**, **`trigger_state_used_by_scored_dispatch_task`**, **`dispatch_task_admin_defaults`** centralize **`consult_*` → `grade_*`** indirection and admin form defaults for **`dispatcher.py`**, **`database.py`**, and **`api_admin.py`**. **AST-960** deleted **`DISPATCH_SCHEDULABLE_TASK_KEYS`** — catalog membership is **`TASK_CONFIG`** only (gazer/roster/inflow gap keys stay on derivation helpers, not admin defaults). **`pass_threshold`** vs **`score_floor`**: **`docs/ASTRAL_CODE_RULES.md`** subsection under §2.1; claim gating vs grading metadata: **§7.13zv** (**AST-586**).

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


**AST-908 return pass:** `test_legacy_helper_may_still_classify_valid_title_graded` rewritten — `trigger_state_used_by_scored_dispatch_task("VALID_TITLE")` is **False** after qualify defaults moved to **NEW** (AST-898); assert **NEW** True instead.

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

### AST-880 · AST-879

**AST-880:** **`TASK_CONFIG["vet_inflow_discovery"]`** → **`output_type: grades_encoded_vet_meta`**; **`response_schema.results`** items use **`grade` + `website`** (no **`action`**). **`INFLOW_CONFIG["vet"]`** exposes **`pass_grades` / `fail_grades` / `grade_vector_code`**. Registry key **`grades_encoded_vet_meta`** in **`ASTRAL_CONFIG["output_types"]`**.

| AC | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1 | Encoded task contract + grade frozensets | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::{test_vet_inflow_discovery_task,test_inflow_config_vet_literals,test_vet_grades_encoded_vet_meta_output_type}` |

Roster apply + batch decode: **`docs/test-bible/core/roster.md`** (**AST-880**). Agent decode: **`docs/test-bible/core/agent.md`** (**AST-880**).

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

Removes legacy `phase` / `seq` from every `TASK_CONFIG` entry. **AST-740** originally added explicit `JOB_ARTIFACT_ENTRY_TASK_KEYS` for consult job-artifact hops; **AST-1111** deletes that frozenset (and the cover-letter carve-out wrapper) — chain membership is `agent_task.run_next` / §2.6.0 helpers. UI grouping is DB-only (**AST-738** / **AST-739**).

| Area | Source | Component tests |
| --- | --- | --- |
| No `phase`/`seq` in `TASK_CONFIG` | `src/utils/config.py` | `TestAst740RemoveConfigGrouping::test_task_config_entries_lack_phase_and_seq` |
| Artifact hop frozenset absent (**AST-1111**) | `src/utils/config.py` | `TestAst740RemoveConfigGrouping::test_job_artifact_entry_task_keys_absent`; **`TestAst1111JobArtifactEntryShadowDeleted`** |
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

**Runtime config:** remove **`GAZER_CONFIG["scrape_jd"]`** alias; **`dispatch_task_admin_defaults("qualify_job_listings")`** → **`trigger_state=NEW`**; primary NEW row claims **NEW** + companion (**AST-898:** **`NEW_RETRY`**; pre-898 migration also seeded **VALID_TITLE_RETRY** drain row).

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

### AST-863 · AST-752 (UAT bug)

**Mid-chain dispatch row `trigger_state`:** hop holding labels (e.g. **`BUILD_ARTIFACTS.anticipate_scan`**) normalize via **`dispatch_chain_registry_trigger`** → bare registry key; **`is_dispatch_chain_trigger`** true for hop labels; **`dispatch_chain_claim_states_for_row`** returns **`[ts]`** only for mid-chain rows (entry rows keep AST-849 parent expansion).

| Area | Source | Component tests |
| --- | --- | --- |
| Registry trigger + claim states | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst863MidChainHopLabelChainTrigger` |

Consult routing manifest: **`docs/test-bible/core/consult.md`** (**AST-863**).

**Regression (required):** **AST-849** **`TestAst849DispatchChainClaimStates`**.

**AST-863** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst863MidChainHopLabelChainTrigger \
  tests/component/utils/test_config.py::TestAst849DispatchChainClaimStates \
  -q
```

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

---

### AST-874 · AST-872

**`CULTURE_READY` / `NEED_CULTURE_CONTENT` / `NO_CULTURE_LINKS`** job states; **`GAZER_CONFIG["fetch_culture_pages"]`**; schedulable **`fetch_culture_pages`** @ **`PASSED_GET`**; **`grade_like`** admin default trigger **`CULTURE_READY`**; **`CULTURE_READY`** in **`PASSED_SCORE_GATED_STATES`** + in-review / skipped UI manifests.

| Area | Source | Component tests |
| --- | --- | --- |
| States, gazer entry, dispatch registry, UI manifests | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst874FetchCulturePagesConfig` |

Gazer batch + migration: **`docs/test-bible/core/gazer.md`** · **`docs/test-bible/data/database/dispatch_tasks.md`** (**AST-874**).

### AST-875 · AST-873

**`ASTRAL_CONFIG["template_candidate_id"]`** default **`somerset`**; **`template_candidate_id()`** getter — no env lookup, no hardcoded id outside config.

| Area | Source | Component tests |
| --- | --- | --- |
| Template candidate id | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst875TemplateCandidateId` |

Primary data/API manifest: **`docs/test-bible/data/database/dispatch_tasks.md`** (**AST-875**).

### AST-876 · AST-873

**`DATA_SHAPES["candidates"]["list"]["manage"]`** includes **`dispatch_task_count`** (`label` Dispatch tasks, `type` int) after **`api_key_status`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Manage list column | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst876DispatchTaskCountShape` |

UI wiring: **`docs/test-bible/frontend/pages.md`** (**AST-876**).

### AST-882 · AST-881

**`dispatch_claim_states`** prefers registry **`retry_state`** over **`{ts}_RETRY`** name convention — **`HOMEPAGE_READY`** claims **`WEBSITE_FOUND_RETRY`**. **`WEBSITE_FOUND`** companion claim unchanged.

| Area | Source | Component tests |
| --- | --- | --- |
| HOMEPAGE_READY → WFR claim list | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst882DispatchClaimStates` |

Roster / gazer / dispatch: **`docs/test-bible/core/roster.md`** · **`docs/test-bible/core/gazer.md`** · **`docs/test-bible/data/database/dispatch_tasks.md`** (**AST-882**).

**AST-892:** **`fetch_website_prefilter_second_strike_filter()`** — claim/count exclusion keys; primary manifest **`docs/test-bible/data/database/dispatch_tasks.md`** (**AST-892**).

---

### AST-891 · AST-890

**`ROSTER_CONFIG["parse_job_list"]["max_concurrent"]`** — integer semaphore width for **`parse_job_list_batch`** (default **`3`**). Strike destinations / trigger states unchanged from **AST-721**.

| Area | Source | Component tests |
| --- | --- | --- |
| **`max_concurrent`** on parse hop | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst721ParseJobListConfig::test_parse_job_list_roster_config` |

Primary roster batch manifest: **`docs/test-bible/core/roster.md`** (**AST-891**).

---

### AST-898 · AST-895

**`NEW_RETRY`** qualify holding; **`NEW`** / **`VALID_TITLE`** `retry_state` → **`NEW_RETRY`**; primary qualify claim **`["NEW","NEW_RETRY"]`**; **`VALID_TITLE_RETRY`** remains in registry for drain only (no new writes from NEW qualify path). UI: **`NEW_RETRY`** / **"New (retry)"** + grade field.

| Area | Source | Component tests |
| --- | --- | --- |
| Registry, claim companions, UI, fail-dest matrix | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst898NewRetryQualifyHolding`; revised **`TestAst641DispatchClaimStates`**, **`TestAst882DispatchClaimStates`**, **`TestAst797ConfigRuntimeCutover`** |

Consult qualify hop: **`docs/test-bible/core/consult.md`** (**AST-898**).


### AST-1189 · AST-1164

**`PROVIDER_CALL_BUDGET`** — 600s timeout + 10s grace, `max_retries=0`, `failure_class=provider_call_timeout`. Primary manifest: **`docs/test-bible/utils/llm_external.md`** § AST-1189.

| Area | Source | Component tests |
| --- | --- | --- |
| Config block | `src/utils/config.py` | **`TestAst1189ProviderCallBudgetConfig`** |

### AST-1190 · AST-1164

**`PROVIDER_EMPTY_RESPONSE`** — `failure_class` + canonical error string for hollow / unusable LLM responses. Primary manifest: **`docs/test-bible/utils/llm_external.md`** § AST-1190.

| Area | Source | Component tests |
| --- | --- | --- |
| Config block | `src/utils/config.py` | **`TestAst1190ProviderEmptyResponseConfig`** |

### AST-903 · AST-900 (UAT fix)

**`CRAFT_RUBRIC_MAX_TOKENS = 32000`** floor for craft rubric UI generate. Primary manifest: **`docs/test-bible/core/agent.md`** § AST-903.

| Area | Source | Component tests |
| --- | --- | --- |
| Token floor literal | `src/utils/config.py` | **`TestAst903CraftRubricMaxTokens`** |

**AST-955:** Save membership = registered **`TASK_CONFIG`** (optional trigger override on **`dispatch_task_admin_defaults`**). Primary manifest: **`docs/test-bible/ui/api/api_admin.md`** (**AST-955**).

---

### AST-960 · AST-957

**Scope:** Delete **`DISPATCH_SCHEDULABLE_TASK_KEYS`**. **`trigger_state_used_by_scored_dispatch_task`** walks scored **`TASK_CONFIG`** keys via **`dispatch_task_admin_defaults`** (KeyError → continue). Gap keys (`fetch_jd`, `prefilter`, `fetch_website`, …) remain on derivation helpers / gazer·roster·inflow config — **not** admin-defaults catalog. **AST-955** Save + optional trigger override unchanged.

| Area | Source | Component tests |
| --- | --- | --- |
| Frozenset gone + scored-trigger rewrite | `src/utils/config.py` | `TestAst960DropSchedulableFrozensetInventory` |
| Registered-key defaults (AST-955 keep) | same | `TestAst955RegisteredKeyDispatchAdminDefaults` |
| Gap-key revisions (helpers / KeyError) | same | revised **`TestAst796FetchJdSchedulableCutover`**, **`TestAst702PrefilterBatchConfig`**, **`TestAst719FetchJobPagesConfig`**, **`TestAst701FetchWebsiteConfig`**, **`TestAst874FetchCulturePagesConfig`**, **`TestAst505InflowDiscoveryConfig`**, **`TestAst506InflowResolveConfig`**, **`TestAst471DispatchConfigHelpers`** |

**Broken / obsolete (Betty revision this pass):** any assert on **`DISPATCH_SCHEDULABLE_TASK_KEYS`**; **`dispatch_task_admin_defaults(<gap_key>)`** without expecting **`unknown task_key`**.

Bootstrap / admin: **`docs/test-bible/core/bootstrap.md`** · **`docs/test-bible/ui/api/api_admin.md`** (**AST-960**). Narrowed run listed on **`docs/test-bible/core/bootstrap.md`**.


### AST-962 · AST-856 (UAT fix)

**Scope (historical AST-962):** mid-hop cover-letter defaults so form meta + **`dispatch_task_admin_defaults`** / **`save_dispatch_task`** succeed without a hand-picked Input State. **Superseded default value:** **AST-1108** retargets those defaults from **`CANDIDATE_REVIEW`** → **`BUILD_ARTIFACTS`** (`CANDIDATE_REVIEW` remains graduation *output*). AST-955 Save membership unchanged; no schedulable frozenset (AST-960). Override-based tests may still use **`CANDIDATE_REVIEW`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Mid-hop default trigger + admin defaults | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst962CoverLetterMidHopDefaultTrigger` (**AST-1108** expects **`BUILD_ARTIFACTS`**) |
| AST-955 obsolete revise | same | `TestAst955RegisteredKeyDispatchAdminDefaults::test_check_cover_letter_without_override_defaults_build_artifacts` |
| DB insert omits trigger | `src/data/database.py` | `tests/component/data/database/test_dispatch_tasks.py::TestAst962SaveDispatchTaskCoverLetterDefaults` |

**Broken / obsolete (Betty revision this pass):** see **### AST-1108** (defaults were **`CANDIDATE_REVIEW`**; now **`BUILD_ARTIFACTS`**).

**AST-962** narrowed run (post–AST-1108 values):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst962CoverLetterMidHopDefaultTrigger \
  tests/component/utils/test_config.py::TestAst955RegisteredKeyDispatchAdminDefaults \
  tests/component/data/database/test_dispatch_tasks.py::TestAst962SaveDispatchTaskCoverLetterDefaults \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-948 · AST-858

**AST-948:** `build_state_ui_manifest()["jobs"]["recommended"]` drops **`report_fixed_tabs`**; adds **`report_top_tabs`** (Summary / Analysis / Artifacts) and **`report_summary_sections`**; phase/artifact `nav_label`s become section chrome labels.

| Area | Source | Component tests |
| --- | --- | --- |
| Recommended report manifest keys | `src/utils/config.py` | **`TestBuildStateUiManifest::test_ast565_recommended_report_manifest_tabs`** (revised for AST-948) |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast565_recommended_report_manifest_tabs
```

### AST-970 · AST-871

Primary manifest: **`docs/test-bible/core/candidate.md`** § AST-970. Config coverage: **`TestAst970CandidateStateRegistry`**; inflow discovery trigger string **`ACTIVE_SEARCH`**.

### AST-972 · AST-871

Primary manifest: **`docs/test-bible/core/candidate.md`** § AST-972. **`CANDIDATE_STAGE_DISPATCH`** + claim/trigger/entity helpers for **`candidate_requested_*`**.

### AST-1022 · AST-1018

Primary manifest: **`docs/test-bible/core/dispatcher.md`** § AST-1022. Config seed: **`CANDIDATE_STAGE_DISPATCH[*].auto_mode`** is **`False`** — **`TestAst1022HonorAutoOffStageDispatch`**.

### AST-973 · AST-871

Primary manifest: **`docs/test-bible/core/candidate.md`** § AST-973. **`CANDIDATE_LEGACY_STATE_MAP`** / **`remap_legacy_candidate_state`**.

---

### AST-996 · AST-994

**AST-996:** Shared `_EXPERIENCE_JOB_ARRAY_FIELD` on `TASK_CONFIG["craft_resume_base"]` + `BUILD_CONFIG["artifact_shapes"]["resume_content"]`; `DATA_SHAPES` base_resume_structure experience type `experience_jobs`. Primary preserve/debug coverage: **`docs/test-bible/core/candidate.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Job-array schema + stringify example | `src/utils/config.py` | **`TestAst996ExperienceJobArrayConfig`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst996ExperienceJobArrayConfig \
  -q
```

---

### AST-997 · AST-994

**AST-997:** `finalize_job_resume` experience uses `_EXPERIENCE_JOB_ARRAY_FIELD_OPTIONAL` sharing `items_schema` with craft-base. Primary pin/persist coverage: **`docs/test-bible/core/candidate.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Finalize optional job-array schema | `src/utils/config.py` | **`TestAst997FinalizeExperienceJobArray`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst997FinalizeExperienceJobArray \
  -q
```

---

### AST-998 · AST-994

**AST-998:** `BUILD_CONFIG["supported_sections"]["experience"]["body_kind"]` = `"experience_jobs"`. Primary HTML emit coverage: **`docs/test-bible/core/builder.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| experience body_kind | `src/utils/config.py` | **`TestAst998ExperienceBodyKind`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst998ExperienceBodyKind \
  -q
```

---

### AST-1008 · AST-993

**AST-1008:** `BUILD_CONFIG["experience_role_layout"]` — `lead_line_prefix` (`<no bullet>`) + `location_arrangement_sep` (` / `). Primary emit coverage: **`docs/test-bible/core/builder.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| experience_role_layout keys | `src/utils/config.py` | **`TestAst1008ExperienceGoldenLayout::test_experience_role_layout_config_keys`** (in `test_builder.py`) |
| experience body_kind unchanged | `src/utils/config.py` | **`TestAst998ExperienceBodyKind`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1008ExperienceGoldenLayout::test_experience_role_layout_config_keys \
  tests/component/utils/test_config.py::TestAst998ExperienceBodyKind \
  -q
```

---

### AST-1010 · AST-993

**AST-1010:** Optional `candidate_tagline` on craft_resume_base + resume_content shapes; contact-adjacent id in `RESUME_STRUCTURE_CONTACT_SECTION_IDS` / `KNOWN` / `DEFAULT` (order 2; contact bumped to 3); `DATA_SHAPES` base_resume_structure field. Primary HTML header/meta/CSS: **`docs/test-bible/core/builder.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Tagline contract + structure orders | `src/utils/config.py` | **`TestAst1010CandidateTaglineConfig`** |
| Default catalog still equals known ids | `src/utils/config.py` | **`TestAst517ResumeStructureConfig`** (regression) |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1010CandidateTaglineConfig \
  tests/component/utils/test_config.py::TestAst517ResumeStructureConfig \
  -q
```

---

### AST-1020 · AST-1019

**AST-1020:** `BUILD_CONFIG["default_style"]["colors"]` adds golden `text_primary` / `text_secondary` / `text_tertiary` / `border_light` / `border_medium` (existing `ink` / `muted` / `rule` / `surface` retained). Primary stylesheet emit: **`docs/test-bible/core/builder.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Golden text/border tokens + accent/header/page_bg | `src/utils/config.py` | **`TestAst1020DefaultStyleColorTokens`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1020DefaultStyleColorTokens \
  -q
```

---

### AST-1024 · AST-1023

**AST-1024:** `BUILD_CONFIG["session_cover_letter"]` — `document_title` `SomersetCover` + field map (`from_block` / `letter_date` / `letter` / `signoff_closing` / `signature` required; `to_block` / `subject` optional). Does **not** change `artifact_shapes["cover_letter"]`. Primary emit + admin route: **`docs/test-bible/core/builder.md`**, **`docs/test-bible/ui/api/api_admin.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Field contract + title | `src/utils/config.py` | **`TestAst1024SessionCoverLetterConfig`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1024SessionCoverLetterConfig \
  -q
```

---

### AST-1025 · AST-1023

**AST-1025:** Admin `NAV_CONFIG` item **Session Cover Letter** (`/admin/session_cover_letter`) immediately after **Session Resume Paste**. Primary page §6c: **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Nav order + label | `src/utils/config.py` | **`TestAst1025SessionCoverLetterNav`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1025SessionCoverLetterNav \
  -q
```

---

### AST-1033 · AST-1031

**AST-1033:** Admin `NAV_CONFIG` item **Read email** (`/admin/read_email`) immediately after **Session Cover Letter**. Primary page §6c: **`docs/test-bible/frontend/pages.md`**. API: **`docs/test-bible/ui/api/api_inbox.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Nav order + label | `src/utils/config.py` | **`TestAst1033ReadEmailNav`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1033ReadEmailNav \
  -q
```

---

### AST-1014 · AST-952

`CANDIDATE_LIBRARY_CONFIG` + DATA_SHAPES/TOKEN_SOURCES column/`contact`/`context.raw_*` paths; middle retired. Primary: **`docs/test-bible/core/candidate.md`** § AST-1014 — **`TestAst1014CandidateLibraryConfig`**, revised **`TestAst510MiddleNameConfig`**.

---

---

### AST-1015 · AST-952

**AST-1015:** `PREAMBLE_VALIDATION_CONFIG` — task_key `preamble_validate_response`, closed outcomes Valid / Try Again / Escalate; `TASK_CONFIG` schema; equality with `PREAMBLE_CONFIG["validation_task_key"]` when both present. Ruth agent_task + core/API: **`docs/test-bible/core/intake.md`**, **`docs/test-bible/ui/api/api_intake.md`**, catalog: **`docs/test-bible/data/database/agent_tasks.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Validation config + TASK_CONFIG | `src/utils/config.py` | **`TestAst1015PreambleValidationConfig`** |

**Broken / obsolete:** AST-786 catalog count 38→39 — see agent_tasks.md.

**Integration:** no existing scenario asserts preamble Ruth validation — no revision; do not invent new integration coverage.

**AST-1015** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1015PreambleValidationConfig \
  tests/component/core/test_intake.py::TestAst1015ValidatePreambleAnswer \
  tests/component/ui/api/test_api_intake.py::TestAst1015PreambleValidateRoute \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1015PreambleValidateCatalogRow \
  -q
```

---

### AST-1016 · AST-952

**AST-1016:** `PREAMBLE_CONFIG` — Intro + three ordered mechanical steps targeting `context.raw_resume` / `raw_profile` / `raw_sample`, Archie placeholder 1st/2nd Try copy, `validation_task_key` = `preamble_validate_response`. Asserts step targets ⊆ `CANDIDATE_LIBRARY_CONFIG["context_keys"]`. Exposed on `GET /api/ui_config` as `preamble` (**AST-1017** renders; **AST-1015** owns Ruth task body).

| Area | Source | Component tests |
| --- | --- | --- |
| PREAMBLE_CONFIG contract | `src/utils/config.py` | **`TestAst1016PreambleConfig`** |
| ui_config `preamble` expose | `src/ui/api/api_system.py` | **`TestSystemAuthRoutes::test_ui_config_includes_preamble_config`** (map: **`docs/test-bible/ui/api/api_system.md`**) |

**Broken / obsolete:** none — additive config + one ui_config key.

**Integration:** no existing scenario asserts preamble script — no revision; do not invent new integration coverage.

**AST-1016** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1016PreambleConfig \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_ui_config_includes_preamble_config \
  -q
```

---

### AST-1037 · AST-1036

**AST-1037:** `TASK_CONFIG["simple_resume_parse"]` shares `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` with `craft_resume_base`; `_CRAFT_RESUME_NORMALIZE_TASK_KEYS` frozenset in config (§1.4). Session wire = **AST-1038**. Agent gate: **`docs/test-bible/core/agent.md`**. Catalog seed: **`docs/test-bible/core/repo_admin_json.md`** / **`docs/test-bible/data/database/agent_tasks.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Shared schema + meta + normalize frozenset | `src/utils/config.py` | **`TestAst1037SimpleResumeParseConfig`** |

**Broken / obsolete:** AST-786 catalog frozenset membership — `simple_resume_parse` on this tip (see agent_tasks.md).

**Integration:** no existing scenario asserts simple_resume_parse — no revision; do not invent new integration coverage.

**AST-1037** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1037SimpleResumeParseConfig \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1037SimpleResumeParseCatalogRow \
  tests/component/core/test_agent.py::TestAst1037NormalizeGateMembership \
  -q
```
---

### AST-1041 · AST-1034

**Parent:** [AST-1034 — Support meteorite jobs](https://linear.app/astralcareermatch/issue/AST-1034/support-meteorite-jobs). **Publish:** `origin/sub/AST-1034/AST-1041-meteorite-company-config-lazy-ensure`.

`METEORITE_CONFIG` seed template after `JOB_STATES`: `meteorite-{candidate_id}` shape, **IGNORE**, unidentified-employer note, plus AST-1042 job-create defaults (landing state + score; landing retargeted **METEORITE_NEW** in **AST-1056**). Ensure path: **`docs/test-bible/core/meteorite.md`**. Claim exclusion: **`docs/test-bible/data/database/companies.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Template keys + IGNORE/`job_create_state` registry asserts + prefix/template shape | `src/utils/config.py` | **`TestAst1041MeteoriteConfig`** (landing assert revised **AST-1056**) |

**Broken / obsolete:** none — additive config block.

**Integration:** no existing scenario asserts METEORITE_CONFIG — no revision.


### AST-1047 · AST-1044

**Parent:** [AST-1044 — Bind email to candidate](https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate). **Publish:** `origin/sub/AST-1044/AST-1047-reusable-get-candidate-string-lookup-from-bind`.

`CANDIDATE_LOOKUP_CONFIG`: email/name dotted paths + `match_casefold` for reusable string→id lookup (Manage Email From bind first caller).

| Area | Source | Component tests |
| --- | --- | --- |
| Lookup path tuples + casefold | `src/utils/config.py` | **`TestAst1047CandidateLookupConfig`** |

**Broken / obsolete:** none — additive config block.

**Integration:** no existing scenario asserts CANDIDATE_LOOKUP_CONFIG — no revision.


### AST-1048 · AST-1044

**Parent:** [AST-1044 — Bind email to candidate](https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate). **Publish:** `origin/sub/AST-1044/AST-1048-manage-email-match-indicator-create-control`.

Admin `NAV_CONFIG`: **Manage Email** at `/admin/manage_email` (replaces **Read email** / `/admin/read_email`), still immediately after **Session Cover Letter**. Page §6c: **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Nav order + label/path rename | `src/utils/config.py` | revised **`TestAst1033ReadEmailNav`** |

**Broken / obsolete:** AST-1033 assertions on `/admin/read_email` and label **Read email** — revised for Manage Email.

**Integration:** none.


### AST-1049 · AST-1044

**Parent:** [AST-1044 — Bind email to candidate](https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate). **Publish:** `origin/sub/AST-1044/AST-1049-strip-extract-create-job-matched-email-meteorite`.

`INBOX_CREATE_JOB_CONFIG`: strip tag/attr sets + `subject_html_template` for Manage Email Create.

| Area | Source | Component tests |
| --- | --- | --- |
| Strip sets + subject template | `src/utils/config.py` | **`TestAst1049InboxCreateJobConfig`** |

**Broken / obsolete:** none — additive.

**Integration:** none.

---

### AST-1053 · AST-1052

**Parent:** [AST-1052 — Processing meteorites](https://linear.app/astralcareermatch/issue/AST-1052/processing-meteorites). **Publish:** `origin/sub/AST-1052/AST-1053-meteorite-gdl-parallel-job-states`.

Parallel meteorite GDL `JOB_STATES` track (`METEORITE_NEW` → PASSED_JD/DO/GET/LIKE + fail/technical/ERROR + `METEORITE_PASSED_LIKE_RETRY`); In Review / Skipped UI manifests + grade-field maps. Score-floor gating for meteorite pass hops is **AST-1054**; RECOMMENDED meteorite LIKE priors are **AST-1055**; create landing retarget is **AST-1056**. **AST-1060** inserts **METEORITE_QUALIFIED** (+ fail/error qualify) and retargets GDL priors from **METEORITE_NEW** → **METEORITE_QUALIFIED**.

| Area | Source | Component tests |
| --- | --- | --- |
| Meteorite priors + UI manifests + non-meteorite smoke | `src/utils/config.py` | **`TestAst1053MeteoriteGdlJobStates`** (priors/labels revised **AST-1060**) |

**Broken / obsolete:** RECOMMENDED prior absence assert superseded by **AST-1055**; score-gated membership smoke revised by **AST-1054**; create-state smoke superseded by **AST-1056** / **`TestAst1056MeteoriteCreateLanding`**; GDL-entry priors + NEW label + QUALIFIED UI revised by **AST-1060**.

**Integration:** no existing scenarios assert meteorite JOB_STATES — none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates \
  -q
```

### AST-1054 · AST-1052

**Parent:** [AST-1052 — Processing meteorites](https://linear.app/astralcareermatch/issue/AST-1052/processing-meteorites). **Publish:** `origin/sub/AST-1052/AST-1054-meteorite-gdl-dispatch-rows-score-floor-0`.

`METEORITE_DISPATCH_TASKS` (shared GDL + twin keys; `score_floor` None @ GDL entry, `0.0` on gated hops); `METEORITE_GDL_OUTCOME_BY_TASK`; `PASSED_SCORE_GATED_STATES` + `_dispatch_trigger_state_for_task_key` for `meteorite_like` / `meteorite_upshot`. Does **not** add twin `TASK_CONFIG` shells (AST-1055). **AST-1060** retargets `evaluate_jd` trigger to **METEORITE_QUALIFIED** and prepends `qualify_meteorite`@**METEORITE_NEW**.

| Area | Source | Component tests |
| --- | --- | --- |
| Dispatch specs + score-floor gating + twin triggers | `src/utils/config.py` | **`TestAst1054MeteoriteGdlDispatch`** (evaluate_jd trigger revised **AST-1060**) |
| Revised ungated smoke | `src/utils/config.py` | revised **`TestAst1053MeteoriteGdlJobStates::test_non_meteorite_gdl_and_recommended_untouched`** |

**Broken / obsolete:** AST-1053 score-gated membership smoke — see above; evaluate_jd@METEORITE_NEW row assert superseded by **AST-1060**.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates \
  tests/component/utils/test_config.py::TestAst1054MeteoriteGdlDispatch \
  -q
```

### AST-1055 · AST-1052

**Parent:** [AST-1052 — Processing meteorites](https://linear.app/astralcareermatch/issue/AST-1052/processing-meteorites). **Publish:** `origin/sub/AST-1052/AST-1055-meteorite-like-meteorite-upshot-agent-tasks`.

`TASK_CONFIG` twins `meteorite_like` / `meteorite_upshot` (`requires_company: False`; meteorite pass/fail/error; upshot → `RECOMMENDED` / `METEORITE_PASSED_LIKE_RETRY`); `RECOMMENDED` priors gain meteorite LIKE states; `rubric_owner_task_key("meteorite_like")` → `grade_like`; `meteorite_like` in batch-mode / strict-encoded / chunk-exhaust frozensets.

| Area | Source | Component tests |
| --- | --- | --- |
| Twins + RECOMMENDED priors + rubric/batch/encoded membership | `src/utils/config.py`, `src/core/agent.py`, `src/core/dispatcher.py` | **`TestAst1055MeteoriteLikeUpshotTasks`** |
| Catalog rows + 41-key seed | `data/admin/agent_task.json` | **`TestAst1055MeteoriteCatalogRows`**, revised **`TestAst786AgentTaskRepoJsonSeed`** |
| Consult routes + upshot persist key | `src/core/consult.py` | **`TestAst1055MeteoriteConsultRoutes`** |

**Broken / obsolete:** AST-1053 RECOMMENDED prior absence assert; AST-786 catalog **39 → 41** (+ UAT fixture byte lock).

**Integration:** no existing scenarios assert these task keys — none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1055MeteoriteLikeUpshotTasks \
  tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates::test_non_meteorite_gdl_and_recommended_untouched \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1055MeteoriteCatalogRows \
  tests/component/core/test_consult.py::TestAst1055MeteoriteConsultRoutes \
  -q
```

---

### AST-1056 · AST-1052

**Parent:** [AST-1052 — Processing meteorites](https://linear.app/astralcareermatch/issue/AST-1052/processing-meteorites). **Publish:** `origin/sub/AST-1052/AST-1056-create-lands-meteorite-jobs-in-meteorite-new`.

`METEORITE_CONFIG["job_create_state"]` → **`METEORITE_NEW`** (meteorite GDL entry). Core `create_meteorite_job` already reads the config key (docstring honesty only). Score stand-in unchanged. Does **not** own dispatch / agent prompts / Recommended UI.

| Area | Source | Component tests |
| --- | --- | --- |
| Create landing key + unrestricted entry | `src/utils/config.py` | **`TestAst1056MeteoriteCreateLanding`**; revised **`TestAst1041MeteoriteConfig`** |
| Insert uses config landing | `src/core/meteorite.py` | revised **`TestAst1042CreateMeteoriteJob`** |
| API / inbox / Manage Email mock honesty | passthrough layers | revised **`TestAst1042MeteoriteCreateApi`**, **`TestAst1049CreateMeteoriteJobFromInboxMessage`**, **`TestAst1049InboxCreateJobApi`**, **`test_AdminManageEmail`** Create mock |

**Broken / obsolete:** AST-1041 / AST-1042 / AST-1053 asserts that expected `JD_READY` create landing.

**Integration:** no existing scenarios assert meteorite create landing state — none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1056MeteoriteCreateLanding \
  tests/component/utils/test_config.py::TestAst1041MeteoriteConfig \
  tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates::test_non_meteorite_gdl_and_recommended_untouched \
  tests/component/core/test_meteorite.py::TestAst1042CreateMeteoriteJob \
  tests/component/ui/api/test_api_meteorite.py \
  tests/component/core/test_inbox.py::TestAst1049CreateMeteoriteJobFromInboxMessage \
  tests/component/ui/api/test_api_inbox.py::TestAst1049InboxCreateJobApi \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageEmail.test.tsx
```

---

### AST-1057 · AST-1052

**Parent:** [AST-1052 — Processing meteorites](https://linear.app/astralcareermatch/issue/AST-1052/processing-meteorites). **Publish:** `origin/sub/AST-1052/AST-1057-recommended-page-meteorites-section`.

`JOBS_RECOMMENDED_METEORITE_SECTION` (`section_id` / `label` / `company_prefix` from `METEORITE_CONFIG["short_name_prefix"]`); `build_state_ui_manifest()["jobs"]["recommended"]["meteorite_section"]`. UI partition: **`docs/test-bible/frontend/pages.md`** (**AST-1057**).

| Area | Source | Component tests |
| --- | --- | --- |
| Section block + manifest wire | `src/utils/config.py` | **`TestAst1057MeteoriteRecommendedSection`** |

**Broken / obsolete:** none — additive manifest field; existing Recommended section asserts stay.

**Integration:** no existing scenarios assert Recommended meteorite membership — none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1057MeteoriteRecommendedSection \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx
```

### AST-1060 · AST-1058

**Parent:** [AST-1058 — Qualify Meteorite](https://linear.app/astralcareermatch/issue/AST-1058/qualify-meteorite). **Publish:** `origin/sub/AST-1058/AST-1060-meteorite-qualified-qualify-meteorite-config-dispatch`.

Registers **METEORITE_QUALIFIED** / **METEORITE_FAILED_QUALIFY** / **METEORITE_ERROR_QUALIFY**; reframes **METEORITE_NEW** as pre-AI; retargets meteorite `evaluate_jd` claim to **METEORITE_QUALIFIED**; `TASK_CONFIG["qualify_meteorite"]` + `METEORITE_DISPATCH_TASKS` row @ **METEORITE_NEW**. Apply / gazer are siblings.

| Area | Source | Component tests |
| --- | --- | --- |
| Qualify states + TASK_CONFIG + dispatch row + helpers | `src/utils/config.py` | **`TestAst1060QualifyMeteoriteConfig`**; revised **`TestAst1053MeteoriteGdlJobStates`**, **`TestAst1054MeteoriteGdlDispatch`** |
| Catalog shell | `data/admin/agent_task.json` | **`TestAst1060QualifyMeteoriteCatalogRow`**, revised **`TestAst786AgentTaskRepoJsonSeed`** (42 keys) |
| Retire stale `evaluate_jd`@METEORITE_NEW | `src/core/dispatcher.py` | revised **`TestAst1054MeteoriteDispatchProvision`** (+ retire case) — see **`docs/test-bible/core/dispatcher.md`** |

**Broken / obsolete:** AST-1053 GDL priors from METEORITE_NEW; AST-1054 evaluate_jd@METEORITE_NEW + insert counts; AST-786 **41 → 42** (+ UAT fixture byte lock).

**Integration:** no existing scenarios assert qualify_meteorite / METEORITE_QUALIFIED — none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates \
  tests/component/utils/test_config.py::TestAst1054MeteoriteGdlDispatch \
  tests/component/utils/test_config.py::TestAst1060QualifyMeteoriteConfig \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1060QualifyMeteoriteCatalogRow \
  -q
```

### AST-1061 · AST-1058

**Parent:** [AST-1058 — Qualify Meteorite](https://linear.app/astralcareermatch/issue/AST-1058/qualify-meteorite). **Publish:** `origin/sub/AST-1058/AST-1061-gazer-email-meteorite-jobs-playwright-dedupe`.

`METEORITE_EMAIL_INGEST_CONFIG`: link schemes, exclude substrings, Playwright concurrency, `min_jd_chars` for gazer email→meteorite ingest.

| Area | Source | Component tests |
| --- | --- | --- |
| Email ingest config | `src/utils/config.py` | **`TestAst1061MeteoriteEmailIngestConfig`** |

**Broken / obsolete:** none — additive config dict.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1061MeteoriteEmailIngestConfig \
  -q
```

### AST-1062 · AST-1058

**Parent:** [AST-1058 — Qualify Meteorite](https://linear.app/astralcareermatch/issue/AST-1058/qualify-meteorite). **Publish:** `origin/sub/AST-1058/AST-1062-qualify-meteorite-batch-apply-meteorite-qualified`.

`TASK_CONFIG["qualify_meteorite"]` content-gate mins: `min_job_title_length` + `min_jd_chars`.

| Area | Source | Component tests |
| --- | --- | --- |
| Threshold keys | `src/utils/config.py` | **`TestAst1062QualifyMeteoriteThresholds`** |

**Broken / obsolete:** none — additive keys on existing AST-1060 task block.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1062QualifyMeteoriteThresholds \
  -q
```

### AST-1066 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1066-contact-core-module-and-contact-config`.

`CONTACT_CONFIG`: listen flag (default off), non-production reply prefix template, Slack env-**name** contracts, `skills` ACL home (empty at AST-1066; populated **AST-1071**). `CANDIDATE_LOOKUP_CONFIG["slack_user_id_paths"]` = `("contact.slack_user_id",)`. Core scaffold: **`docs/test-bible/core/contact.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| CONTACT_CONFIG defaults + env names; slack lookup path home | `src/utils/config.py` | **`TestAst1066ContactConfig`** (empty-skills assert revised **AST-1071**) |

**Broken / obsolete:** empty-`skills == {}` — revised by **AST-1071**.

**Integration:** no existing scenario asserts CONTACT_CONFIG / slack_user_id_paths — no revision.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1066ContactConfig \
  tests/component/core/test_contact.py::TestAst1066ContactScaffold \
  -q
```

### AST-1071 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1071-contact-config-acl-entity-save-skills`.

`CONTACT_CONFIG["skills"]`: `save_candidate_profile` + `save_candidate_contact` with `entity`/`write`/`description`/`allowed_paths` (no `contact.slack_user_id`; keys ∉ `TASK_CONFIG`). Core runners + admin API: **`docs/test-bible/core/contact.md`**, **`docs/test-bible/ui/api/api_contact.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Two skill ACL entries + path inventory | `src/utils/config.py` | **`TestAst1071ContactSkillsConfig`** |

**Broken / obsolete:** AST-1066 empty-skills asserts — revised above.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1071ContactSkillsConfig \
  tests/component/core/test_contact.py::TestAst1071ContactSkillRunners \
  tests/component/ui/api/test_api_contact.py::TestAst1071ContactSkillsApi \
  -q
```

### AST-1069 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1069-slack-events-api-webhook-ingress`.

`CONTACT_CONFIG` Events/Socket Mode keys: `events_http_path`, `bot_event_types`, `event_id_dedupe_max`, `app_token_env`. Ingress handlers: **`docs/test-bible/core/contact.md`**. External verify/post: **`docs/test-bible/external/slack.md`**. HTTP blueprint: **`docs/test-bible/ui/api/api_slack.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Events path / bot types / dedupe / app token env | `src/utils/config.py` | **`TestAst1069ContactEventsConfig`** |

**Broken / obsolete:** none — additive keys on CONTACT_CONFIG.

**Integration:** no existing scenario asserts Slack Events ingress — no revision.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1069ContactEventsConfig \
  tests/component/external/test_slack.py::TestAst1069ExternalSlack \
  tests/component/core/test_contact.py::TestAst1069ContactSlackIngress \
  tests/component/ui/api/test_api_slack.py::TestAst1069SlackEventsApi \
  -q
```


### AST-1070 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1070-slack-sourced-conversation-context`.

`CONTACT_CONFIG` context keys: `context_history_limit`, `context_cache_max_conversations`, `context_cache_ttl_seconds`. Core load/append: **`docs/test-bible/core/contact.md`**. External fetch: **`docs/test-bible/external/slack.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| History limit / cache max / TTL | `src/utils/config.py` | **`TestAst1070ContactContextConfig`** |

**Broken / obsolete:** none — additive keys on CONTACT_CONFIG.

**Integration:** no existing scenario asserts context cache config — no revision.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1070ContactContextConfig \
  tests/component/external/test_slack.py::TestAst1070FetchConversationHistory \
  tests/component/core/test_contact.py::TestAst1070ContactConversationContext \
  -q
```




### AST-1068 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id`.

`CANDIDATE_STATES["PROSPECT"]`; `CONTACT_CONFIG["prospect_candidate_id_template"]`. Revised **`TestAst970CandidateStateRegistry`**.

| Area | Source | Component tests |
| --- | --- | --- |
| PROSPECT registry + id template | `src/utils/config.py` | **`TestAst1068ProspectConfig`**; revised **`TestAst970CandidateStateRegistry`** |

**Broken / obsolete:** AST-970 `assert "PROSPECT" not in CANDIDATE_STATES` — revised this pass.

**Integration:** no existing scenario — no revision.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1068ProspectConfig \
  tests/component/utils/test_config.py::TestAst970CandidateStateRegistry \
  -q
```


### AST-1072 · AST-1046

**Parent:** [AST-1046 — Contact Estelle conversational envelope](https://linear.app/astralcareermatch/issue/AST-1046/contact-estelle-conversational-envelope). **Publish:** `origin/sub/AST-1046/AST-1072-conversational-agent-envelope`.

CHAT-only conversational envelope: `CONVERSATIONAL_OUTCOMES` / `CONVERSATIONAL_PERFORMANCE_SCHEMA` (do **not** mutate `BASE_SCHEMA`); `CONTACT_ESTELLE_CONFIG` Medium brain; `TASK_CONFIG["contact_estelle_turn"]` (`task_type="CHAT"`); `is_conversational_task` / `stringify_response_schema` concern path. Core `do_task` contract: **`docs/test-bible/core/agent.md`**. Catalog seed: **`docs/test-bible/core/repo_admin_json.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Schema + CHAT registration + stringify | `src/utils/config.py` | **`TestAst1072ConversationalEnvelopeConfig`** |

**Broken / obsolete:** AST-786 catalog **42 → 43** (`contact_estelle_turn`) — see repo_admin_json bible.

**Integration:** no existing scenario asserts CHAT / contact_estelle_turn envelope — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1072ConversationalEnvelopeConfig \
  tests/component/core/test_agent.py::TestAst1072ConversationalEnvelope \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1072ContactEstelleTurnCatalogRow \
  -q
```


---

### AST-1074 · AST-953

**Parent:** [AST-953 — Topic Menu Generation](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation). **Publish:** `origin/sub/AST-953/AST-1074-topic-menu-model-and-persistence`.

`TOPIC_MENU_CONFIG`: closed `informs` (`rubrics`, `base_resume`, `strengths`, `priorities`, `deal_breakers`, `backstory`), statuses `open`/`ready`/`retired`, `candidate_data_key: topic_menu`, required topic fields. Library homes for context informs live under `CANDIDATE_LIBRARY_CONFIG`. Core persistence: **`docs/test-bible/core/candidate.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Closed informs + status triad | `src/utils/config.py` | **`TestAst1074TopicMenuConfig`** |

**Broken / obsolete:** none — additive config.

**Integration:** no existing scenario — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1074TopicMenuConfig \
  tests/component/core/test_candidate.py::TestAst1074TopicMenuPersistence \
  -q
```


---

### AST-1075 · AST-953

**Parent:** [AST-953 — Topic Menu Generation](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation). **Publish:** `origin/sub/AST-953/AST-1075-estelle-preamble-confirm-and-topic-menu-generation`.

`TOPIC_MENU_GEN_CONFIG`: confirm/generate task keys, `continue`/`accepted` outcomes, packet field whitelist (context + real `contact_keys` + `name_columns`; no fabricated `preferred_name`), patchable context keys, Estelle agent id, UI copy. Matching `TASK_CONFIG` schemas. Persistence catalog remains **AST-1074** (`TOPIC_MENU_CONFIG`). Core: **`docs/test-bible/core/intake.md`** / **`docs/test-bible/core/candidate.md`**. Catalog: **`docs/test-bible/core/repo_admin_json.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Gen config + TASK_CONFIG schemas | `src/utils/config.py` | **`TestAst1075TopicMenuGenConfig`** |

**Broken / obsolete:** none — additive generation config beside AST-1074 persistence.

**Integration:** no existing scenario covers Topic Menu confirm/generate — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1075TopicMenuGenConfig \
  tests/component/core/test_intake.py::TestAst1075TopicMenuConfirmGenerate \
  tests/component/core/test_candidate.py::TestAst1075PreambleConfirmedAt \
  -q
```


### AST-1079 · AST-1045

**Parent:** [AST-1045 — Verify unique contact info](https://linear.app/astralcareermatch/issue/AST-1045/verify-unique-contact-info). **Publish:** `origin/sub/AST-1045/AST-1079-unique-contact-field-contract`.

`CANDIDATE_CONTACT_UNIQUENESS_CONFIG`: save-gate field vocabulary (paths + compare + scopes) sibling to `CANDIDATE_LOOKUP_CONFIG`; email/slack path **objects** shared by identity. Enforcement is **AST-1080**.

| Area | Source | Component tests |
| --- | --- | --- |
| Shared email/slack paths + scalar/list/compare/scopes | `src/utils/config.py` | **`TestAst1079ContactUniquenessConfig`** |

**Broken / obsolete:** none — additive config block; no callers yet.

**Integration:** none — config vocabulary only; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1079ContactUniquenessConfig \
  -q
```

### AST-1073 · AST-1046

**Parent:** [AST-1046 — Contact Estelle conversational envelope](https://linear.app/astralcareermatch/issue/AST-1046/contact-estelle-conversational-envelope). **Publish:** `origin/sub/AST-1046/AST-1073-contact-estelle-turn-loop`.

`CONTACT_ESTELLE_CONFIG` turn trim keys (`turn_context_message_limit`, `turn_context_text_max_chars`); optional `skill_calls` on `TASK_CONFIG["contact_estelle_turn"]["response_schema"]`. Core turn: **`docs/test-bible/core/contact.md`**. Envelope base: **AST-1072**.

| Area | Source | Component tests |
| --- | --- | --- |
| Trim keys + skill_calls schema | `src/utils/config.py` | **`TestAst1073ContactEstelleTurnConfig`** |

**Broken / obsolete:** none for config asserts — additive keys on AST-1072 block.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1073ContactEstelleTurnConfig \
  -q
```


---

### AST-1081 · AST-1065

**Parent:** [AST-1065 — Update candidate ui for contact info](https://linear.app/astralcareermatch/issue/AST-1065/update-candidate-ui-for-contact-info). **Publish:** `origin/sub/AST-1065/AST-1081-contact-shapes-websites-full`.

`DATA_SHAPES["candidates"]["detail"]["profile"]` Contact Information: editable `full`, `contact.websites` (`type: string_list`), `contact.reason_codes` (`textarea`); Admin `list.manage` / `edit.manage` unchanged. Save contract + FormFields: **`docs/test-bible/core/candidate.md`**, **`docs/test-bible/frontend/components.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Contact shapes + Admin boundary | `src/utils/config.py` | **`TestAst1081ContactShapesConfig`** |

**Broken / obsolete:** none — additive shape fields.

**Integration:** none — shapes vocabulary only; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1081ContactShapesConfig \
  -q
```


---

### AST-1082 · AST-1065

**Parent:** [AST-1065 — Update candidate ui for contact info](https://linear.app/astralcareermatch/issue/AST-1065/update-candidate-ui-for-contact-info). **Publish:** `origin/sub/AST-1065/AST-1082-profile-contact-manage-nav`.

`DATA_SHAPES` Contact labels: GitHub/LinkedIn → username-or-URL copy (keys/types unchanged). Candidate `NAV_CONFIG` has no Title Patterns item; Profile `Title Patterns` section (`contact.title_patterns`) retained. Profile page: **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Labels + NAV + Profile Title Patterns section | `src/utils/config.py` | **`TestAst1082ProfileContactLabelsNav`** |

**Broken / obsolete:** none — label strings + nav verify-or-remove.

**Integration:** none — config/nav vocabulary; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1082ProfileContactLabelsNav \
  -q
```


---

### AST-1084 · AST-1077

**Parent:** [AST-1077 — Add a constant set of rubric vectors to generated JD evaluate vectors](https://linear.app/astralcareermatch/issue/AST-1077/add-a-constant-set-of-rubric-vectors-to-generated-jd-evaluate-vectors). **Publish:** `origin/sub/AST-1077/AST-1084-config-constant-jd-vectors`.

`EMBEDDED_EVALUATE_JD_CRITERIA` — QC then GC (importance **1**; grade letters/descriptions from parent Original brief). Definitions only; wire-up into evaluate_jd hydrate/save/generate is **AST-1085** (`docs/test-bible/core/candidate.md`). Sibling of **`EMBEDDED_COMPANY_PREFILTER_CRITERIA`** (**AST-707**).

| Area | Source | Component tests |
| --- | --- | --- |
| Embedded QC/GC registry | `src/utils/config.py` | **`TestAst1084EvaluateJdCriteria`** |

**Broken / obsolete:** none — additive constant; consume path covered under **AST-1085**.

**Integration:** none — config definitions only; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1084EvaluateJdCriteria \
  -q
```

### AST-1088 · AST-1087

**Parent:** [AST-1087 — Add gaze_email as a dispatch task](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task). **Publish:** `origin/sub/AST-1087/AST-1088-gaze-email-config-null-candidate-dispatch-shell-gmail-archive-trash`.

`GAZE_EMAIL_CONFIG` (task key, account expectation, unbound retention days, row seed) + `TASK_CONFIG["gaze_email"]` shell (`requires_candidate_key: False`; null entity/trigger — mailbox poller, no claim queue). `dispatch_task_admin_defaults("gaze_email")` returns null entity/trigger/sort_by and `batch_call_mode=0`. Secrets stay environ. Data/provision/Gmail: **`docs/test-bible/data/database/dispatch_tasks.md`** · **`docs/test-bible/core/dispatcher.md`** · **`docs/test-bible/external/gmail.md`**. Ruth parse / runner are siblings **AST-1089** / **AST-1090**.

| Area | Source | Component tests |
| --- | --- | --- |
| Config block + TASK_CONFIG shell + admin defaults | `src/utils/config.py` | **`TestAst1088GazeEmailConfig`** |

**Broken / obsolete:** none for config (additive).

**Integration:** no existing scenarios assert `GAZE_EMAIL_CONFIG` / `gaze_email` task key — none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1088GazeEmailConfig \
  -q
```

### AST-1090 · AST-1087

**Parent:** [AST-1087 — Add gaze_email as a dispatch task](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task). **Publish:** `origin/sub/AST-1087/AST-1090-gaze-email-runner-bind-route-scrape-dedupe-create-mailbox`.

Extends `GAZE_EMAIL_CONFIG` with runner literals: `subject_url_schemes`, `dispatch_ledger_candidate_id`, `debug_func`. Shell keys from **AST-1088** unchanged. Primary runner: **`docs/test-bible/core/gaze_email.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Runner config literals | `src/utils/config.py` | **`TestAst1090GazeEmailRunnerConfig`** |

**Broken / obsolete:** none — additive keys on `GAZE_EMAIL_CONFIG`.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1090GazeEmailRunnerConfig \
  -q
```

### AST-1089 · AST-1087

**Parent:** [AST-1087 — Add gaze_email as a dispatch task](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task). **Publish:** `origin/sub/AST-1087/AST-1089-ruth-little-brain-meteorite-email-parse-task`.

`METEORITE_EMAIL_PARSE_CONFIG` (`task_key` + `parse_modes` `html_links` / `subject_body`) + `TASK_CONFIG["parse_meteorite_email"]` (fields schema; `requires_candidate_key: True`; `entity_type` / `trigger_state` None — **not** a meteorite dispatch claim). Catalog shell: **`docs/test-bible/core/repo_admin_json.md`**. Gaze shell / runner are siblings **AST-1088** / **AST-1090**.

| Area | Source | Component tests |
| --- | --- | --- |
| Parse config + TASK_CONFIG (not dispatch) | `src/utils/config.py` | **`TestAst1089ParseMeteoriteEmailConfig`** |
| Catalog + AST-756 byte lock | `data/admin/agent_task.json` | **`TestAst1089ParseMeteoriteEmailCatalogRow`**, revised **`TestAst786AgentTaskRepoJsonSeed`** (47 keys) |

**Broken / obsolete:** AST-786 **46 → 47** (+ UAT fixture byte lock for `parse_meteorite_email`).

**Integration:** no existing scenarios assert parse_meteorite_email / METEORITE_EMAIL_PARSE_CONFIG — none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1089ParseMeteoriteEmailConfig \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1089ParseMeteoriteEmailCatalogRow \
  -q
```


---

### AST-1092 · AST-1065 (UAT)

**Parent:** [AST-1065 — Update candidate ui for contact info](https://linear.app/astralcareermatch/issue/AST-1065/update-candidate-ui-for-contact-info). **Publish:** `origin/sub/AST-1065/AST-1092-uat-extra-binding-emails-labels`.

Resume/Messages email labels; `contact.extra_emails` (`string_list`) in library + lookup `email_list_paths`. (Uniqueness email pool via **`email_list_paths`** is **AST-1095** — not `list_paths`.) Save/bind + Profile: **`docs/test-bible/core/candidate.md`**, **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Labels + key + email_list_paths + uniqueness align | `src/utils/config.py` | **`TestAst1092ExtraBindingEmailsConfig`**; revised **`TestAst1079ContactUniquenessConfig`** / **AST-1095** for pool |

**Broken / obsolete:** AST-1079 originally websites-only `list_paths`; AST-1092 briefly parked extras on `list_paths` — **AST-1095** moves extras to uniqueness `email_list_paths`.

**Integration:** no existing Profile extra-email bind scenario — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1092ExtraBindingEmailsConfig \
  tests/component/utils/test_config.py::TestAst1079ContactUniquenessConfig \
  -q
```



### AST-1095 · AST-1045 (UAT)

**Parent:** [AST-1045 — Verify unique contact info](https://linear.app/astralcareermatch/issue/AST-1045/verify-unique-contact-info). **Publish:** `origin/sub/AST-1045/AST-1095-uat-email-unique-root-and-extra`.

`CANDIDATE_CONTACT_UNIQUENESS_CONFIG["email_list_paths"]` (identity with lookup); `list_paths` websites-only. Email pool = `email_paths` ∪ `email_list_paths` under `compare["email"]`. Gate: **`docs/test-bible/core/candidate.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| email_list_paths identity + websites-only list_paths | `src/utils/config.py` | **`TestAst1095EmailUniqueRootAndExtraConfig`**; revised **`TestAst1079ContactUniquenessConfig`**, **`TestAst1092ExtraBindingEmailsConfig`** |

**Broken / obsolete:** AST-1079 / AST-1092 asserts that put `contact.extra_emails` on uniqueness `list_paths` — revised to `email_list_paths`.

**Integration:** none — do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1095EmailUniqueRootAndExtraConfig \
  tests/component/utils/test_config.py::TestAst1079ContactUniquenessConfig \
  tests/component/utils/test_config.py::TestAst1092ExtraBindingEmailsConfig \
  -q
```

### AST-1094 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1094-uat-manage-slack-estelle-activity-list`.

`CONTACT_CONFIG["activity_state_filename"]` = `contact_estelle_activity.json` (durable @Estelle activity summary under `db_dir`). Data/core/API/UI: **`docs/test-bible/core/contact.md`**, **`docs/test-bible/ui/api/api_contact.md`**, **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| activity_state_filename | `src/utils/config.py` | **`TestAst1094ActivityConfig`** |

**Broken / obsolete:** none — additive CONTACT_CONFIG key.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1094ActivityConfig \
  -q
```


### AST-1101 · AST-1043 (UAT)

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1101-uat-channel-at-estelle-no-hear-evidence`.

`CONTACT_CONFIG["hear_ack_reply_text"]` — fallback Slack copy when accept succeeds but Estelle turn does not post. Core hear-ack / listen re-read: **`docs/test-bible/core/contact.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| hear_ack_reply_text | `src/utils/config.py` | **`TestAst1101HearAckConfig`** |

**Broken / obsolete:** none — additive CONTACT_CONFIG key.

**Integration:** none — do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1101HearAckConfig \
  -q
```


### AST-1206 · AST-1203

**Parent:** [AST-1203 — Need to be able to set the "Debug" flag for Slack messages](https://linear.app/astralcareermatch/issue/AST-1203/need-to-be-able-to-set-the-debug-flag-for-slack-messages). **Publish:** `origin/sub/AST-1203/AST-1206-contact-debug-flag-foundation`.

`CONTACT_CONFIG["debug_enabled"]` (default `False`) + `debug_state_filename` (`contact_slack_debug.json`) — separate durable file from listen. Core/data/API: **`docs/test-bible/core/contact.md`**, **`docs/test-bible/data/contact_debug.md`**, **`docs/test-bible/ui/api/api_contact.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| debug default + filename ≠ listen filename | `src/utils/config.py` | **`TestAst1206ContactDebugConfig`** |

**Broken / obsolete:** none — additive CONTACT_CONFIG keys.

**Integration:** none — do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1206ContactDebugConfig \
  -q
```

### AST-1098 · AST-1093

**Parent:** [AST-1093 — Gnarly looking deploy logs on railway](https://linear.app/astralcareermatch/issue/AST-1093/gnarly-looking-deploy-logs-on-railway). **Publish:** `origin/sub/AST-1093/AST-1098-seed-gaze-email-click-statute-seed-auto-false`.

`GAZE_EMAIL_CONFIG["auto_mode"]` → **False** (CLICK seed); module asserts keep meteorite + candidate-stage seed catalogs CLICK. Statute `astral.dispatch.seed-auto-false` + README/HARVEST register. Reconcile: **`docs/test-bible/core/dispatcher.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Seed CLICK + catalog locks + statute register | `src/utils/config.py`, `canon/statutes/**` | **`TestAst1098GazeEmailSeedClick`**; revised **`TestAst1088GazeEmailConfig`** |

**Broken / obsolete:** AST-1088 `auto_mode is True` assert — superseded by seed law CLICK.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1098GazeEmailSeedClick \
  tests/component/utils/test_config.py::TestAst1088GazeEmailConfig \
  -q
```

### AST-1099 · AST-1091

**Parent:** [AST-1091 — Job resume artifact, cover letter and suggested responses is not saved in job_data](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved). **Publish:** `origin/sub/AST-1091/AST-1099-pin-agent-data-id`.

`JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` maps the three hop keys → `job_resume` / `cover_letter` / `proposed_answers`. `JOB_BUILD_ARTIFACT_CLEAR_KEYS` includes those pin slots (legacy body keys retained). Primary pin/do_task coverage: **`docs/test-bible/core/tracker.md`**, **`docs/test-bible/core/agent.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Pin map + clear keys | `src/utils/config.py` | **`TestAst1099JobArtifactAgentDataPinConfig`** |

**Broken / obsolete:** none.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1099JobArtifactAgentDataPinConfig \
  -q
```

### AST-1100 · AST-1091

**Parent:** [AST-1091](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved). **Publish:** `origin/sub/AST-1091/AST-1100-resolve-artifact-agent-data-id`.

`JOBS_RECOMMENDED_ARTIFACT_TABS` `artifact_key`s remap to pin slots `job_resume` / `cover_letter` / `proposed_answers`. Resolve/hydrate: **`docs/test-bible/core/tracker.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Tab key remap | `src/utils/config.py` | **`TestAst1100ArtifactTabPinKeys`** |

**Broken / obsolete:** fixture `report_artifact_tabs` keys — see **`docs/test-bible/frontend/lib.md`**.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1100ArtifactTabPinKeys \
  -q
```

### AST-1105 · AST-1043 (UAT)

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1105-uat-slack-username-display-activity-profile`.

Profile Contact Information: `contact.slack_user_id` + `contact.slack_username` (not Contact skill ACL).

| Area | Source | Component tests |
| --- | --- | --- |
| Profile Slack fields | `src/utils/config.py` | **`TestAst1105ProfileSlackFields`** |

**Broken / obsolete:** none — additive Profile fields.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1105ProfileSlackFields \
  -q
```

### AST-1106 · AST-1087

**Parent:** [AST-1087 — Add gaze_email as a dispatch task](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task). **Publish:** `origin/sub/AST-1087/AST-1106-uat-gaze-email-missing-from-scheduled-actions-default-view`.

`ADMIN_CONFIG["always_visible_under_avail_gt0_dispatch_task_keys"]` seeded from `GAZE_EMAIL_CONFIG["task_key"]`; helper `admin_always_visible_under_avail_gt0_dispatch_task_keys()`. API stamp + SA filter: **`docs/test-bible/ui/api/api_admin.md`**, **`docs/test-bible/frontend/pages.md`**. Catalog: **`docs/test-bible/core/repo_admin_json.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Avail-gt0 always-visible keys | `src/utils/config.py` | **`TestAst1106AlwaysVisibleUnderAvailGt0`** |

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1106AlwaysVisibleUnderAvailGt0 \
  -q
```

### AST-1111 · AST-1109

**Parent:** [AST-1109 — Hard-coded daisy chain in config.py](https://linear.app/astralcareermatch/issue/AST-1109/hard-coded-daisy-chain-in-configpy). **Publish:** `origin/sub/AST-1109/AST-1111-anomaly-job-artifact-entry-task-keys`.

Deletes dead `JOB_ARTIFACT_ENTRY_TASK_KEYS` and `build_artifacts_chain_task_keys()` (cover-letter frozenset carve-out) against statute `astral.dispatch.run-next-is-chain-authority`. No replacement membership set — §2.6.0 / `run_next` helpers remain authority. Does **not** own hop_task_keys (**AST-1112**) or craft_task_keys / boot SQL (**AST-1113**).

| Area | Source | Component tests |
| --- | --- | --- |
| Entry frozenset + wrapper absent | `src/utils/config.py` | **`TestAst1111JobArtifactEntryShadowDeleted`**; revised **`TestAst740RemoveConfigGrouping::test_job_artifact_entry_task_keys_absent`** |

**Broken / obsolete (Betty revision):** **`TestAst740RemoveConfigGrouping::test_job_artifact_entry_task_keys_membership`**; **`TestAst844BuildArtifactsChainTaskKeys`** (config hop-registry frozenset).

**Regression (required):** **AST-848** hop labels / claim helpers; **AST-849** dispatch-chain claim states (unchanged product path).

**AST-1111** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1111JobArtifactEntryShadowDeleted \
  tests/component/utils/test_config.py::TestAst740RemoveConfigGrouping \
  tests/component/utils/test_config.py::TestAst848DispatchHopLabels \
  tests/component/utils/test_config.py::TestAst849DispatchChainClaimStates \
  -q
```

### AST-1112 · AST-1109

**Parent:** [AST-1109 — Hard-coded daisy chain in config.py](https://linear.app/astralcareermatch/issue/AST-1109/hard-coded-daisy-chain-in-configpy). **Publish:** `origin/sub/AST-1109/AST-1112-anomaly-resume-hop-task-keys`.

Retires `BUILD_CONFIG.resume_artifact_chain.hop_task_keys` / `_RESUME_ARTIFACT_HOP_TASK_KEYS` / `resume_artifact_hop_task_keys()` as chain-membership authority. Resume/artifact parent resolution uses `_parent_hop_task_key_for_child` (live `agent_task.run_next`). Legacy compound labels keep `TASK_CONFIG` membership via `legacy_build_artifacts_hop`. Does **not** own `JOB_ARTIFACT_ENTRY_TASK_KEYS` (**AST-1111**) or craft_task_keys / boot SQL (**AST-1113**).

| Area | Source | Component tests |
| --- | --- | --- |
| Hop-list authority absent | `src/utils/config.py` | **`TestAst1112ResumeHopTaskKeysShadowDeleted`** |
| Parent via `run_next` (+ ambiguous → None) | `src/core/agent.py` | **`TestAst597MidChainResumeHydrationAndTransitions::test_parent_hop_task_key_*`** |
| Hydrate uses run_next parents | `src/core/agent.py` | revised **`test_hydrate_resume_entry_chain_context_*`** (same class) |
| Flat BUILD_ARTIFACTS + CHAIN triggers | `src/utils/config.py` | **`TestAst803FlatBuildArtifactsChainDispatch`** (unchanged surface; no hop-list helper) |

**Broken / obsolete (Betty revision):** **`_resume_artifact_parent_hop_key`** tests; any assert on `resume_artifact_hop_task_keys` / `hop_task_keys` / `_RESUME_ARTIFACT_HOP_TASK_KEYS`.

**Regression (required):** **AST-848** hop labels; **AST-849** claim states; **AST-855** dispatch-chain hop debug (ctx path — not config hop tuple).

**AST-1112** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1112ResumeHopTaskKeysShadowDeleted \
  tests/component/utils/test_config.py::TestAst803FlatBuildArtifactsChainDispatch \
  tests/component/utils/test_config.py::TestAst848DispatchHopLabels \
  tests/component/utils/test_config.py::TestAst849DispatchChainClaimStates \
  tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions \
  -q
```

### AST-1113 · AST-1109

**Parent:** [AST-1109 — Hard-coded daisy chain in config.py](https://linear.app/astralcareermatch/issue/AST-1109/hard-coded-daisy-chain-in-configpy). **Publish:** `origin/sub/AST-1109/AST-1113-anomaly-craft-task-keys-boot-run-next`.

Retires `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["craft_task_keys"]` as craft succession authority; singular `craft_task_key` entry only. Walk via `_current_agent_task_run_next` with `suppress_run_next`. Boot migration confirm/corrects craft `run_next` links. Does **not** own JOB_ARTIFACT_ENTRY (**AST-1111**) or hop_task_keys (**AST-1112**).

| Area | Source | Component tests |
| --- | --- | --- |
| Entry key only (no `craft_task_keys`) | `src/utils/config.py` | **`TestAst1113CraftTaskKeysShadowDeleted`**; revised **`TestAst972CandidateStageDispatch`** |
| Walk + suppress + mid-fail | `src/core/candidate.py` | revised **`TestAst972RequestedStageDispatch::test_artifacts_dispatch_*`** |
| Boot craft run_next migration | `src/data/database.py` | **`TestAst1113CraftRunNextChainMigration`** |

**Broken / obsolete (Betty revision):** asserts on `arts["craft_task_keys"]`; artifacts dispatch that reads the list for hop order.

**AST-1113** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1113CraftTaskKeysShadowDeleted \
  tests/component/utils/test_config.py::TestAst972CandidateStageDispatch \
  tests/component/core/test_candidate.py::TestAst972RequestedStageDispatch \
  tests/component/data/database/test_agent_tasks.py::TestAst1113CraftRunNextChainMigration \
  -q
```

### AST-1108 (standalone — Track 3 cover-letter defaults)

**Publish:** `origin/ftr/AST-1108-fix-broken-seed-data`.

**Scope (Betty test lane):** Artifact-chain / cover-letter dispatch defaults claim **`BUILD_ARTIFACTS`**, not graduation output **`CANDIDATE_REVIEW`**. Product already on ftr (`_dispatch_trigger_state_for_task_key` + retarget migration). Override-based tests that pass **`trigger_state="CANDIDATE_REVIEW"`** stay. **No new integration scenarios.**

| Area | Source | Component tests |
| --- | --- | --- |
| Mid-hop + draft defaults | `src/utils/config.py` | revised **`TestAst962CoverLetterMidHopDefaultTrigger`** (all four keys → **`BUILD_ARTIFACTS`**; `grade_do` → **`PASSED_JD`** unchanged) |
| AST-955 without-override | same | renamed/revised **`test_check_cover_letter_without_override_defaults_build_artifacts`** |
| DB insert omits trigger | `src/data/database.py` | revised **`TestAst962SaveDispatchTaskCoverLetterDefaults`** |

**Broken / obsolete (Betty revision this pass):** prior AST-962 asserts that default Input State is **`CANDIDATE_REVIEW`** for `draft_cover_letter` / `check_cover_letter` / `finalize_cover_letter` / `propose_application_responses`.

**Out of scope for this pass:** Track 1 compliance, Topic Menu grouping polish, unrelated pre-existing `test_config.py` / `test_api_admin.py` reds (gaze_email `freq_hrs`, seed-statute registration, prefilter grouping, resolve-tokens) — do not misattribute to Track 3.

**AST-1108** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst962CoverLetterMidHopDefaultTrigger \
  tests/component/utils/test_config.py::TestAst955RegisteredKeyDispatchAdminDefaults \
  tests/component/data/database/test_dispatch_tasks.py::TestAst962SaveDispatchTaskCoverLetterDefaults \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.


### AST-1116 · AST-1091 (UAT)

**Parent:** [AST-1091](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved). **Publish:** `origin/sub/AST-1091/AST-1116-cover-letter-field-defs`.

`DATA_SHAPES["candidates"]["detail"]["cover_letter"]` field defs (`Subject` / `Letter` / `signature`) for ArtifactEditor `shapes_key=cover_letter`. Hydrate normalize: **`docs/test-bible/core/tracker.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Cover field defs + tab shapes_key | `src/utils/config.py` | **`TestAst1116CoverLetterDataShapes`** |
| Shapes API detail.cover_letter | `src/ui/api` shapes route | **`TestAst1116ShapesCoverLetter`** |

**Broken / obsolete:** none.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1116CoverLetterDataShapes \
  tests/component/ui/api/test_api_system.py::TestAst1116ShapesCoverLetter \
  -q
```

### AST-1120 · AST-1119

**Parent:** [AST-1119 — Fallback for company job id](https://linear.app/astralcareermatch/issue/AST-1119/fallback-for-company-job-id). **Publish:** `origin/sub/AST-1119/AST-1120-uuid-from-job-link-company-job-id-fallback`.

`TRACKER_CONFIG["uuid_path_segment_pattern"]` — anchored UUID-shaped full path-segment regex for `job_link` fallback (no host allowlist). Apply: **`docs/test-bible/core/consult.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| UUID path pattern | `src/utils/config.py` | **`TestAst1120UuidPathSegmentPattern`** |

**Broken / obsolete:** none.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1120UuidPathSegmentPattern \
  -q
```

### AST-1127 · AST-1119 (UAT)

**Parent:** [AST-1119 — Fallback for company job id](https://linear.app/astralcareermatch/issue/AST-1119/fallback-for-company-job-id). **Publish:** `origin/sub/AST-1119/AST-1127-uat-qualify-meteorite-schema-company-job-id-omitted`.

`TASK_CONFIG["qualify_meteorite"].response_schema` `company_job_id.required` → `False` so omit/`null` reach AST-1120 consult resolve (not `Missing required field`). Sibling item fields stay required. Apply omit path: **`docs/test-bible/core/consult.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Schema optional + `_validate_response_schema` omit/null/empty | `src/utils/config.py` / `src/core/agent.py` | **`TestAst1127QualifyMeteoriteCompanyJobIdOptional`**; revised **`TestAst1060QualifyMeteoriteConfig`** |

**Broken / obsolete:** `TestAst1060QualifyMeteoriteConfig` asserted `company_job_id` `required is True` — revised this pass.

**Integration:** none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1127QualifyMeteoriteCompanyJobIdOptional \
  tests/component/utils/test_config.py::TestAst1060QualifyMeteoriteConfig \
  tests/component/core/test_consult.py::TestAst1127QualifyMeteoriteOmitCompanyJobId \
  -q
```

### AST-1125 · AST-1123

**Parent:** [AST-1123 — Support Signature_Image as a token in the cover letter](https://linear.app/astralcareermatch/issue/AST-1123/support-signature-image-as-a-token-in-the-cover-letter). **Publish:** `origin/sub/AST-1123/AST-1125-cover-letter-signature-image-token-contract`.

`BUILD_CONFIG["cover_letter_render_tokens"]["SIGNATURE_IMAGE"]` — cover-only render contract (`{$SIGNATURE_IMAGE}` → `contact.cover_letter_signature_image`, omit policies). Accessor `get_cover_letter_render_token`. **Not** in `TOKEN_SOURCES` / `resolve_tokens`. Emit placement = sibling **AST-1126**.

| Area | Source | Component tests |
| --- | --- | --- |
| Cover render-token contract + accessor + TOKEN_SOURCES exclusion | `src/utils/config.py` | **`TestAst1125CoverLetterRenderTokenContract`** |

**Broken / obsolete:** none.

**Integration:** none (config-only; no existing integration scenario invalidated).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1125CoverLetterRenderTokenContract \
  -q
```

### AST-1131 · AST-1130

**Parent:** [AST-1130 — Manage Email create button for job lists isn't working](https://linear.app/astralcareermatch/issue/AST-1130/manage-email-create-button-for-job-lists-isnt-working). **Publish:** `origin/sub/AST-1130/AST-1131-normalize-pasted-list-email-html`.

`METEORITE_EMAIL_INGEST_CONFIG` paste-normalize knobs: `entity_unescape_marker` / min count / max passes, `nested_autolink_attr_names`, `promote_bare_http_urls`. Primary behavior: **`docs/test-bible/utils/formatting.md`** (**AST-1131**).

| Area | Source | Component tests |
| --- | --- | --- |
| Paste-normalize config | `src/utils/config.py` | **`TestAst1131MeteoriteEmailIngestPasteNormalizeConfig`** |

**Broken / obsolete:** none — additive keys on existing AST-1061 ingest config.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1131MeteoriteEmailIngestPasteNormalizeConfig \
  -q
```

### AST-1134 · AST-1128

**Parent:** [AST-1128 — gaze_email — candidate-bound dispatch (redesign)](https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign). **Publish:** `origin/sub/AST-1128/AST-1134-retire-null-shell-candidate-bound-config`.

Candidate-bound `GAZE_EMAIL_CONFIG` / `TASK_CONFIG["gaze_email"]` (null entity/trigger kept — mailbox poller, not claim queue). Removes `dispatch_ledger_candidate_id`. Empties `ADMIN_CONFIG["always_visible_under_avail_gt0_dispatch_task_keys"]` (helper + API/React generic stamp remain). Secrets stay environ; `unbound_retention_days` kept. Provision / schema / ledger: **`docs/test-bible/core/dispatcher.md`** · **`docs/test-bible/data/database/dispatch_tasks.md`** · **`docs/test-bible/data/database/candidates.md`**. Live Avail / runner: siblings **AST-1135** / **AST-1136**.

| Area | Source | Component tests |
| --- | --- | --- |
| Candidate-bound shell + no ledger placeholder | `src/utils/config.py` | revised **`TestAst1088GazeEmailConfig`**, **`TestAst1090GazeEmailRunnerConfig`** |
| Empty always-visible carve-out | `src/utils/config.py` | revised **`TestAst1106AlwaysVisibleUnderAvailGt0`** |

**Broken / obsolete (Betty revision):** null-shell wording / `dispatch_ledger_candidate_id == ""` / gaze_email membership in always-visible keys (AST-1088 / AST-1090 / AST-1106 config asserts).

**Integration:** no existing scenarios assert null-shell gaze_email config — none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1088GazeEmailConfig \
  tests/component/utils/test_config.py::TestAst1090GazeEmailRunnerConfig \
  tests/component/utils/test_config.py::TestAst1106AlwaysVisibleUnderAvailGt0 \
  -q
```

### AST-1132 · AST-1130

**Parent:** [AST-1130 — Manage Email create button for job lists isn't working](https://linear.app/astralcareermatch/issue/AST-1130/manage-email-create-button-for-job-lists-isnt-working). **Publish:** `origin/sub/AST-1130/AST-1132-job-link-hygiene-non-job-create-skip`.

`METEORITE_EMAIL_INGEST_CONFIG` hygiene: expanded `link_exclude_substrings`, empty `link_allow_substrings`, `non_job_visible_substrings`. Primary ingest behavior: **`docs/test-bible/core/gazer.md`** (**AST-1132**).

| Area | Source | Component tests |
| --- | --- | --- |
| Hygiene / non-job config | `src/utils/config.py` | **`TestAst1132MeteoriteEmailIngestHygieneConfig`** |

**Broken / obsolete:** none — additive keys + expanded exclude tuple (AST-1061 exclude membership asserts still hold).

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1132MeteoriteEmailIngestHygieneConfig \
  -q
```

### AST-1137 · AST-1124

**Parent:** [AST-1124 — Cover Letter Header is incorrect](https://linear.app/astralcareermatch/issue/AST-1124/cover-letter-header-is-incorrect). **Publish:** `origin/sub/AST-1124/AST-1137-candidate-from-block-text-contact-defaults`.

`COVER_FROM_BLOCK_CONFIG` + `CANDIDATE_LIBRARY_CONFIG["contact_keys"]` entry `cover_letter_from_block`. Profile field placement: own **Cover Letter From** section (**AST-1149**; originally under Cover Letter Signature). Not in `TOPIC_MENU_GEN_CONFIG["packet_contact_keys"]` / `TOKEN_SOURCES`. Primary resolve: **`docs/test-bible/core/candidate.md`** (**AST-1137**).

| Area | Source | Component tests |
| --- | --- | --- |
| From-block config + signature-group exclusion | `src/utils/config.py` | **`TestAst1137CoverFromBlockConfig`** (profile section assert revised by **AST-1149**) |

**Broken / obsolete:** profile “under Cover Letter Signature” assert → revised to signature-only (**AST-1149**).

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1137CoverFromBlockConfig \
  tests/component/core/test_candidate.py::TestAst1137ResolveCoverFromBlock \
  -q
```

### AST-1147 · AST-1145

**Parent:** [AST-1145 — Allow contact info tokens and | chars in fromBlock](https://linear.app/astralcareermatch/issue/AST-1145/allow-contact-info-tokens-and-or-chars-in-fromblock). **Publish:** `origin/sub/AST-1145/AST-1147-from-block-token-template-config-contract`.

Extends `COVER_FROM_BLOCK_CONFIG` with `default_template`, `allowed_token_ids` (`FULL_NAME` / `LOCATION` / `CONTACT_EMAIL` / `PHONE`), `authoring_separator` `|`, `emit_separator` ` • `, `empty_segment_policy` `drop_with_adjacent_separator`. Keeps AST-1137 path/separator keys. Brief aliases not registered. Resolve/emit = sibling **AST-1148**; help chrome = **AST-1149**.

| Area | Source | Component tests |
| --- | --- | --- |
| Token template + rewrite + alias exclusion | `src/utils/config.py` | **`TestAst1147CoverFromBlockTokenTemplateConfig`** |
| Prior from-block field contract | same | **`TestAst1137CoverFromBlockConfig`** (unchanged keys) |

**Broken / obsolete:** none — additive keys on existing block.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1147CoverFromBlockTokenTemplateConfig \
  tests/component/utils/test_config.py::TestAst1137CoverFromBlockConfig \
  -q
```


### AST-1149 · AST-1145

**Parent:** [AST-1145 — Allow contact info tokens and | chars in fromBlock](https://linear.app/astralcareermatch/issue/AST-1145/allow-contact-info-tokens-and-or-chars-in-fromblock). **Publish:** `origin/sub/AST-1145/AST-1149-from-block-authoring-help-profile-session`.

`COVER_FROM_BLOCK_CONFIG` `authoring_help` / `session_authoring_help`; `DATA_SHAPES` own **Cover Letter From** section with `placeholder`=`default_template` and `help`=`authoring_help`. UI `/api/ui_config` `cover_from_block` slice + pages: **`docs/test-bible/ui/api/api_system.md`**, **`docs/test-bible/frontend/pages.md`**. Resolve/emit = **AST-1148**.

| Area | Source | Component tests |
| --- | --- | --- |
| Authoring help + Cover Letter From section | `src/utils/config.py` | **`TestAst1149CoverFromBlockAuthoringHelpConfig`** |
| Revised signature-group (from-block removed) | same | **`TestAst1137CoverFromBlockConfig`** |

**Broken / obsolete:** AST-1137 profile placement under Cover Letter Signature — revised this pass.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1149CoverFromBlockAuthoringHelpConfig \
  tests/component/utils/test_config.py::TestAst1137CoverFromBlockConfig \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_ui_config_includes_cover_from_block \
  -q
```

### AST-1138 · AST-1124

**Parent:** [AST-1124 — Cover Letter Header is incorrect](https://linear.app/astralcareermatch/issue/AST-1124/cover-letter-header-is-incorrect). **Publish:** `origin/sub/AST-1124/AST-1138-job-cover-html-somersetcover-fromblock-golden-css`.

`BUILD_CONFIG["job_cover_somerset"]` — `document_title_key` → session title, `artifact_to_fields` (`re_line`/`body`/`signature` → `subject`/`letter`/`signature`), `unset_fields` for layout-only session keys. Does **not** change `session_cover_letter` required flags or `artifact_shapes["cover_letter"]`. Primary emit: **`docs/test-bible/core/builder.md`** (**AST-1138**).

| Area | Source | Component tests |
| --- | --- | --- |
| Job→Somerset field map | `src/utils/config.py` | **`TestAst1138JobCoverSomersetConfig`** |

**Broken / obsolete:** none — additive `BUILD_CONFIG` block.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1138JobCoverSomersetConfig \
  tests/component/core/test_builder.py::TestAst1138JobCoverSomersetFromBlock \
  -q
```

### AST-1139 · AST-1124

**Parent:** [AST-1124 — Cover Letter Header is incorrect](https://linear.app/astralcareermatch/issue/AST-1124/cover-letter-header-is-incorrect). **Publish:** `origin/sub/AST-1124/AST-1139-session-cover-letter-golden-parity`.

`BUILD_CONFIG["session_cover_letter"]`: `fields.from_block.empty_uses_candidate_resolve` + block-level `from_block_sources` (`session` / `candidate` / `default`). Keeps `from_block.required` True. Does **not** change other session field required flags or job `job_cover_somerset`. Primary emit + Admin page: **`docs/test-bible/core/builder.md`**, **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Empty-resolve flag + source labels | `src/utils/config.py` | **`TestAst1139SessionCoverEmptyResolveConfig`** |

**Broken / obsolete:** none — additive keys on existing `session_cover_letter`.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1139SessionCoverEmptyResolveConfig \
  tests/component/core/test_builder.py::TestAst1139SessionCoverEmptyFromBlock \
  -q
```

### AST-1140 · AST-1129

**Parent:** [AST-1129 — Manage Email — select inbox messages and Land Meteorite](https://linear.app/astralcareermatch/issue/AST-1129/manage-email-select-inbox-messages-and-land-meteorite). **Publish:** `origin/sub/AST-1129/AST-1140-selected-ids-gaze-email-ingest-entrypoint`.

`GAZE_EMAIL_CONFIG` selected-ids literals: `debug_func_selected`, `selected_outcome_skipped_unbound` / `_not_in_inbox` / `_unmatched`. No parallel Land-Meteorite config block. Primary runner: **`docs/test-bible/core/gaze_email.md`** (**AST-1140**).

| Area | Source | Component tests |
| --- | --- | --- |
| Selected-ids config vocabulary | `src/utils/config.py` | **`TestAst1140GazeEmailSelectedConfig`** |

**Broken / obsolete:** none — additive keys on existing `GAZE_EMAIL_CONFIG`.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1140GazeEmailSelectedConfig \
  tests/component/core/test_gaze_email.py::TestAst1140RunGazeEmailSelectedIds \
  -q
```

### AST-1144 · AST-1128

**Parent:** [AST-1128 — gaze_email — candidate-bound dispatch (redesign)](https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign). **Publish:** `origin/sub/AST-1128/AST-1144-uat-parse-meteorite-email-metadata-dict-str`.

UAT: `TASK_CONFIG["parse_meteorite_email"].response_schema.jobs.items_schema.metadata` type `str` → `dict` (optional) so Ruth structured company/location objects validate. Prompt/fixture: **`docs/test-bible/core/repo_admin_json.md`**. Validation + runner: **`docs/test-bible/core/agent.md`** · **`docs/test-bible/core/gaze_email.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Schema type dict | `src/utils/config.py` | **`TestAst1144ParseMeteoriteEmailMetadataDict`** |

**Broken / obsolete:** none — type flip; AST-1089 shell asserts still hold (did not lock `metadata` type).

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1144ParseMeteoriteEmailMetadataDict \
  -q
```

### AST-1146 · AST-1130 (UAT)

**Parent:** [AST-1130 — Manage Email create button for job lists isn't working](https://linear.app/astralcareermatch/issue/AST-1130/manage-email-create-button-for-job-lists-isnt-working). **Publish:** `origin/sub/AST-1130/AST-1146-uat-create-skips-null-company-job-id-dedupe`.

`METEORITE_EMAIL_INGEST_CONFIG["min_company_job_id_match_chars"]` = `8`. Primary behavior: **`docs/test-bible/data/database/jobs.md`** (**AST-1146**).

| Area | Source | Component tests |
| --- | --- | --- |
| Id-match min length | `src/utils/config.py` | **`TestAst1146MeteoriteEmailIngestMinCompanyJobIdChars`** |

**Broken / obsolete:** none — additive key.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1146MeteoriteEmailIngestMinCompanyJobIdChars \
  -q
```

### AST-1154 · AST-1150

**Parent:** [AST-1150 — Technical fail for Do prompt](https://linear.app/astralcareermatch/issue/AST-1150/technical-fail-for-do-prompt). **Publish:** `origin/sub/AST-1150/AST-1154-rubric-completeness-contracts-all-graded-tasks`.

Shared `_ENCODED_GRADE_SET_COMPLETENESS` clause on multi-vector encoded `payload_instructions` (`grades_encoded`, `_notes`, `_meta`, `_prefilter_links`); not on `grades_encoded_vet_meta` / `grades_json`. Seven graded `agent_task` `cache_prompt`s carry the same AST-1154 marker + VALIDATE/Rules tighteners; AST-756 fixture stays byte-identical. Retry/Skipped Retry remain AST-1155 / AST-1156.

| Area | Source | Component tests |
| --- | --- | --- |
| Shared encoded completeness clause | `src/utils/config.py` | **`TestAst1154EncodedGradeSetCompleteness`** |
| Graded task prompts + fixture lock | `data/admin/agent_task.json` | **`TestAst1154GradedTaskCompletenessPrompts`**; existing **`TestAst786AgentTaskRepoJsonSeed::test_repo_json_matches_uat_fixture_byte_for_byte`** |

**Broken / obsolete:** none — additive prompt/contract text; catalog count unchanged.

**Integration:** none — prompt/config contract only; no existing integration scenario asserts these strings.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1154EncodedGradeSetCompleteness \
  tests/component/core/test_repo_admin_json.py::TestAst1154GradedTaskCompletenessPrompts \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed::test_repo_json_matches_uat_fixture_byte_for_byte \
  -q
```

### AST-1155 · AST-1150

**Parent:** [AST-1150 — Technical fail for Do prompt](https://linear.app/astralcareermatch/issue/AST-1150/technical-fail-for-do-prompt). **Publish:** `origin/sub/AST-1150/AST-1155-incomplete-grades-retry-holding-never-technical-fail`.

Seven graded-trigger `*_RETRY` holdings + `retry_state` on primaries; `dispatch_claim_states` companions; In Review UI/labels/grade-field maps. Apply/retry routing: **`docs/test-bible/core/consult.md`** (**AST-1155**).

| Area | Source | Component tests |
| --- | --- | --- |
| Holdings + claim companions + UI maps | `src/utils/config.py` | **`TestAst1155GradedRetryHoldings`**; revised **`TestAst874FetchCulturePagesConfig`**, **`TestAst1053MeteoriteGdlJobStates`** |

**Broken / obsolete:** LIKE / meteorite GDL exact `prior_states` lists and meteorite In Review membership expanded for holdings.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1155GradedRetryHoldings \
  tests/component/utils/test_config.py::TestAst874FetchCulturePagesConfig \
  tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates \
  -q
```

### AST-1156 · AST-1150

**Parent:** [AST-1150 — Technical fail for Do prompt](https://linear.app/astralcareermatch/issue/AST-1150/technical-fail-for-do-prompt). **Publish:** `origin/sub/AST-1150/AST-1156-skipped-retry-hop-correct-dispatchable-state`.

`JOBS_SKIPPED_BULK_RETRY_TO_STATE` maps every Skipped section state (except `CANDIDATE_SKIPPED`) to a claimable **primary** trigger; manifest exposes `bulk_retry_to_state_by_from_state` (scalar `bulk_retry_to_state` removed). Target `prior_states` expanded so `transition_job_state` accepts Retry. UI/API: **`docs/test-bible/frontend/pages.md`**, **`docs/test-bible/ui/api/api_jobs.md`** (or ui/api bible if present).

| Area | Source | Component tests |
| --- | --- | --- |
| Retry map + priors + manifest | `src/utils/config.py` | **`TestAst1156SkippedBulkRetryMap`**; revised **`TestBuildStateUiManifest`**, **`TestAst874FetchCulturePagesConfig`**, **`TestAst1053MeteoriteGdlJobStates`** |

**Broken / obsolete:** scalar `bulk_retry_to_state == "NEW"`; exact prior lists on CULTURE_READY / PASSED_JD / meteorite pass targets expanded for Skipped Retry from-states.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1156SkippedBulkRetryMap \
  tests/component/utils/test_config.py::TestBuildStateUiManifest::test_manifest_contains_expected_sections \
  -q
```

### AST-1195 · AST-1188

**Parent:** [AST-1188 — Errors for qualify_meteorite dispatch task](https://linear.app/astralcareermatch/issue/AST-1188/errors-for-qualify-meteorite-dispatch-task). **Publish:** `origin/sub/AST-1188/AST-1195-schema-nulls-bot-blocked`.

`qualify_meteorite` schema: `job_link` / `job_title` → `required: False` so omit/`null` do not abort `do_task`. Universal rename `JD_SCRAPE_FAIL_BOT` → **`BOT_BLOCKED`** in `JOB_STATES` (priors `PASSED_JOBLIST` + `METEORITE_NEW`), `GAZER_CONFIG` fetch_jd error_states, `SKIPPED_STATES`, skipped section order + bulk-retry map (retry → `PASSED_JOBLIST`). Gazer map: **`docs/test-bible/core/gazer.md`**. Fixture: **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Schema optional + `_validate_response_schema` omit/null | `src/utils/config.py` / `src/core/agent.py` | **`TestAst1195SchemaNullsAndBotBlocked`**; revised **`TestAst1127QualifyMeteoriteCompanyJobIdOptional`**, **`TestAst1060QualifyMeteoriteConfig`** |
| `BOT_BLOCKED` registry + skipped UI + gazer error_states | `src/utils/config.py` | **`TestAst1195SchemaNullsAndBotBlocked::test_bot_blocked_registry_and_skipped_ui`**; **`TestAst1156SkippedBulkRetryMap`** (covers map completeness / priors) |

**Broken / obsolete:** AST-1060 / AST-1127 asserts that `job_title` / `job_link` stay `required: True`; AST-1127 sibling-missing check on `job_title` → `jd_text`. Frontend fixture `JD_SCRAPE_FAIL_BOT` → `BOT_BLOCKED` (see pages bible).

**Integration:** none revised (no existing scenarios pin `JD_SCRAPE_FAIL_BOT` / qualify schema required flags).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1195SchemaNullsAndBotBlocked \
  tests/component/utils/test_config.py::TestAst1127QualifyMeteoriteCompanyJobIdOptional \
  tests/component/utils/test_config.py::TestAst1060QualifyMeteoriteConfig \
  tests/component/utils/test_config.py::TestAst1156SkippedBulkRetryMap \
  tests/component/core/test_gazer.py::TestAst1195BotBlockedErrorState \
  -q
```

### AST-1197 · AST-1188

**Parent:** [AST-1188 — Errors for qualify_meteorite dispatch task](https://linear.app/astralcareermatch/issue/AST-1188/errors-for-qualify-meteorite-dispatch-task). **Publish:** `origin/sub/AST-1188/AST-1197-consult-apply-email-link-bot-blocked`.

`TASK_CONFIG["qualify_meteorite"]`: `email_link_prefix="email-"`, `bot_blocked_state="BOT_BLOCKED"`. `TRACKER_CONFIG["jd_classifier"]["bot_signals"]` gains parent challenge phrases (2-hit threshold). Apply: **`docs/test-bible/core/consult.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Knobs + challenge signals | `src/utils/config.py` | **`TestAst1197QualifyMeteoriteApplyKnobs`** |

**Broken / obsolete:** none in config tests.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1197QualifyMeteoriteApplyKnobs \
  tests/component/core/test_gazer.py::TestAst1197ChallengeBotSignals \
  -q
```


### AST-1212 · AST-1182

**Parent:** [AST-1182 — Rename task to meteorite_email + AI payload as visible text/links](https://linear.app/astralcareermatch/issue/AST-1182/rename-task-to-meteorite-email-ai-payload-as-visible-textlinks). **Publish:** `origin/sub/AST-1182/AST-1212-rename-parse-meteorite-email-to-meteorite-email`.

Live product key rename: `TASK_CONFIG` / `METEORITE_EMAIL_PARSE_CONFIG["task_key"]` / `context_format` / `agent_task` → **`meteorite_email`**; `parse_meteorite_email` absent as a live key (no compat shim). Parse modes + response schema unchanged. Catalog: **`docs/test-bible/core/repo_admin_json.md`**. Schema validation: **`docs/test-bible/core/agent.md`**. Payload shape / groupings / aliases are siblings **AST-1213** / **AST-1183** / **AST-1184**.

| Area | Source | Component tests |
| --- | --- | --- |
| Parse config + TASK_CONFIG identity | `src/utils/config.py` | revised **`TestAst1089ParseMeteoriteEmailConfig`**, **`TestAst1144ParseMeteoriteEmailMetadataDict`** |

**Broken / obsolete:** AST-1089 / AST-1144 asserts and skipifs that indexed `TASK_CONFIG["parse_meteorite_email"]` / `task_key == "parse_meteorite_email"`.

**Integration:** no existing scenarios assert parse/meteorite_email task key — none revised; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1089ParseMeteoriteEmailConfig \
  tests/component/utils/test_config.py::TestAst1144ParseMeteoriteEmailMetadataDict \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1089ParseMeteoriteEmailCatalogRow \
  tests/component/core/test_repo_admin_json.py::TestAst1106GazeEmailCatalogRow \
  tests/component/core/test_repo_admin_json.py::TestAst1144ParseMeteoriteEmailMetadataPrompt \
  tests/component/core/test_agent.py::TestAst1144ParseMeteoriteEmailMetadataDict \
  -q
```

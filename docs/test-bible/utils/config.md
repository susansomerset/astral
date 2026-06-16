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

```

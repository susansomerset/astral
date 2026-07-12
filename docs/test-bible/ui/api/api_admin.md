# Api Admin

**Test module:** `tests/component/ui/api/test_api_admin.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py` | yes |

---

### AST-485 · AST-461 · AST-549 · AST-721

Decomposed PJL roster hops **`select_job_page`** (**`PJL_READY`**) and **`parse_job_list`** (**`JOBLIST_IDENTIFIED`**); **`find_job_page`** monolith removed from schedulable keys (**AST-721**). **`locate_job_page`** is not schedulable (legacy **`UPDATE`** during schema ensure). **AST-549** retired **`database._DISPATCH_TASK_SEED`** / **`config._DISPATCH_TASK_TRIGGER_SEED`** — schedulable defaults now come from **`dispatch_task_admin_defaults`** (**§7.13zq**). **`get_dispatch_row_or_seed_preview_meta`** supplies admin **`adhoc`** when no sample DB row exists. **`GET /api/admin/dispatch_tasks/task_keys`** lists every **`TASK_CONFIG`** key (**AST-516**); schedulable keys merge config derivation.

| Area | Source | Component tests |
| --- | --- | --- |
| Schedulable roster defaults | `src/utils/config.py` | **`TestAst471DispatchConfigHelpers::test_ast485_roster_dispatch_trio_matches_config_defaults`** (`tests/component/utils/test_config.py`) |
| **`task_keys`** decomposed roster + **`adhoc_entities`** config fallback | `src/ui/api/api_admin.py`, `src/data/database.py` | **`test_ast485_dispatch_task_keys_roster_seeds_minus_locate_template`**, **`test_ast485_adhoc_entities_select_job_page_fallbacks_to_config_defaults`** (`tests/component/ui/api/test_api_admin.py` **`TestApiAdminBranchGaps`**) |
| Nav-links preview (**`select`** / legacy **`locate`**) + parse DOM | `src/ui/api/api_admin.py` | **`TestAdhocHelpers::test_build_adhoc_live_content_company_paths`** (`test_api_admin.py`) |

Narrow (**`test-astral`** **AST-485** / **AST-549** regression tip):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers::test_ast485_roster_dispatch_trio_matches_config_defaults \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast485_dispatch_task_keys_roster_seeds_minus_locate_template \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast485_adhoc_entities_select_job_page_fallbacks_to_config_defaults \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_build_adhoc_live_content_company_paths
```

---

### AST-492 · AST-495 · AST-491

**`LLM_PROVIDER_CONFIG`**, **`DEEPSEEK_MODEL_PRICING`**, Ada tier helpers (**`resolve_brain_setting_to_anthropic_agent_key`**, **`resolve_brain_setting_to_deepseek_tier_meta`**, **`validate_allowed_brain_setting`**, **`infer_brain_setting_from_legacy_model_code`**); product may keep thin wrappers (**`admin_brain_setting_catalog()`**, **`anthropic_agent_key_for_brain_setting`**). **`component` tests compare admin payloads using resolve + **`get_model`** only. **`save_agent`** / **`get_agent`** / **`list_agents`** **`brain_setting`** column + migration off legacy **`model_code`**. **`do_task`** resolves tiers to **`AGENT_CONFIG`** keys and calls **`send_to_anthropic`** when **`active_provider`** is **`anthropic`**; when **`deepseek`**, **`resolve_brain_setting_to_deepseek_tier_meta`** feeds **`send_to_deepseek`** (**`vendor_model`**, **`tier_meta`**, same block assembly as Anthropic) per **AST-493**. **`GET /api/admin/agents/brain_settings`** returns tier rows (label + default temperature / max tokens from **`AGENT_CONFIG`**) for Manage Agents (**AST-495**). **`AdminAgentPrompts`** loads that catalog and posts **`brain_setting`** on create/update.

| Area | Source | Component tests |
| --- | --- | --- |
| Tier helpers + env gate + DeepSeek tier meta + tier rows vs resolve | `src/utils/config.py` | **`TestAst492LlmBrainTierConfig`** (`tests/component/utils/test_config.py`) |
| Agent persistence + insert requires **`brain_setting`** | `src/data/database.py` | **`tests/component/data/database/test_agents.py`** |
| **`do_task`** — Anthropic (**`send_to_anthropic`**) vs DeepSeek (**`send_to_deepseek`**) | `src/core/agent.py` | **`TestAst492BrainSettingDoTask`** (`tests/component/core/test_agent.py`) |
| Agent CRUD + **`/agents/brain_settings`** catalog; PUT **`model_code`** present but empty after strip skips infer shim when other kwargs update | `src/ui/api/api_admin.py` | **`TestAdminConfigAndAgents`** (`tests/component/ui/api/test_api_admin.py`) |
| Admin **`_resolve_adhoc`** — infer **`Medium`** when **`brain_setting`** / legacy **`model_code`** absent (**`infer_brain_setting_from_legacy_model_code`**); DeepSeek **`tier_meta`** + unknown provider | `src/ui/api/api_admin.py`, `src/utils/config.py` | **`TestAdhocHelpers::test_adhoc_entities_and_resolve`**, **`TestAst492ResolveAdhocApiAdmin`** (`tests/component/ui/api/test_api_admin.py`) |
| **`_enrich_tasks`** — unknown **`LLM_PROVIDER_CONFIG.active_provider`** (neither **`anthropic`** nor **`deepseek`**) skips catalog pricing | `src/ui/api/api_admin.py` | **`TestEnrichTasks::test_enrich_tasks_unknown_llm_provider_skips_tier_catalog_lookups`** |
| Manage Agents page (**`brain_settings`** + **`brain_setting`** column) | `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` | **`AdminAgentPrompts`** (`tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx`) |

Manifest (**`AST-492`** + **`AST-495`** on **`dev-betty`** after merging both publish tips + conflict resolution):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst492LlmBrainTierConfig \
  tests/component/data/database/test_agents.py \
  tests/component/core/test_agent.py::TestAst492BrainSettingDoTask \
  tests/component/ui/api/test_api_admin.py::TestAdminConfigAndAgents \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_adhoc_entities_and_resolve \
  tests/component/ui/api/test_api_admin.py::TestAst492ResolveAdhocApiAdmin \
  tests/component/ui/api/test_api_admin.py::TestEnrichTasks::test_enrich_tasks_unknown_llm_provider_skips_tier_catalog_lookups
```

**`AdminAgentPrompts`** Vitest (**`AST-495`**): from repo root,

`cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx`

(or rely on the full **`./scripts/testing/run_component_tests.sh`** with no args — that runs all Vitest component tests too).

### AST-725 · AST-378

Read-only **`GET /api/admin/vector_feedback`**, **`/vector_feedback/summary`**, **`/vector_feedback/task_keys`** for Admin Vector Feedback screen.

| Area | Source | Component tests |
| --- | --- | --- |
| Detail list + `req_dict` enrichment | `src/ui/api/api_admin.py` | `TestAst725VectorFeedback::test_list_vector_feedback_and_req_dict` |
| Summary 400 + shaped response | `src/ui/api/api_admin.py` | `TestAst725VectorFeedback::test_summary_requires_candidate_and_owner_task_key`, `test_summary_and_task_keys` |

**AST-725** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst725VectorFeedback \
  tests/component/utils/test_config.py::TestAst725RubricOwnerRunKeys \
  tests/component/data/database/test_rubric_vectors.py::TestAst725ListVectorFeedback \
  tests/component/data/database/test_rubric_vectors.py::TestAst725AggregateVectorFeedback \
  -q
```

Routed page: **`docs/test-bible/frontend/pages.md`** (**AST-725**).

### AST-738 · AST-734

Manage Tasks grouping metadata reads/writes DB columns only — backward-compat `phase`/`seq` keys derived from `task_group_name` / `task_seq` until **AST-740**. `_enrich_tasks` spreads `_grouping_from_agent_task_row`; `/dispatch_tasks/task_keys` unchanged (still config-derived).

| Area | Source | Component tests |
| --- | --- | --- |
| `_grouping_from_agent_task_row` + GET/PUT `/tasks/<task_key>` | `src/ui/api/api_admin.py` | `TestAst738TaskGroupingApi` |
| Obsolete assumption fix | `tests/component/ui/api/test_api_admin.py` | `TestTaskRoutes::test_preview_task_and_get_update` (mock must include DB grouping fields) |

See primary data manifest: `docs/test-bible/data/database/agent_tasks.md` (**AST-738**).

### AST-739 · AST-734

`GET /api/admin/dispatch_tasks/task_keys` returns `task_group_*` fields via `_catalog_task_grouping_meta` / `_dispatch_task_key_form_meta`; drops `phase`/`seq`. Orphan dispatch-only keys get empty grouping defaults.

| Area | Source | Component tests |
| --- | --- | --- |
| Catalog resolution + orphan fallback | `src/ui/api/api_admin.py` | `TestAst739DispatchTaskKeysGrouping` |
| AST-549 schedulable derivation regression | same | `test_ast549_task_keys_config_derivation_authoritative` (no config `phase`/`seq`) |

Routed pages: **`docs/test-bible/frontend/pages.md`** (**AST-739**).

### AST-750 · AST-743

**`GET /api/admin/dispatch_tasks/score_floor_options`** returns `{"values": ["0.00", …, "10.00"]}` from **`dispatch_score_floor_option_labels()`** — mirrors **`state_options`** metadata pattern for the Scheduled Actions edit modal.

| Area | Source | Component tests |
| --- | --- | --- |
| Score floor catalog endpoint | `src/ui/api/api_admin.py` | `TestDispatchTasks::test_scheduler_and_run_controls` (floors GET) |

Routed page + zero-save UX: **`docs/test-bible/frontend/pages.md`** (**AST-750**).

### AST-740 · AST-734

`_grouping_from_agent_task_row` returns DB grouping fields only — drops backward-compat `phase`/`seq` keys from Manage Tasks GET/PUT payloads.

| Area | Source | Component tests |
| --- | --- | --- |
| No `phase`/`seq` on task routes | `src/ui/api/api_admin.py` | `TestAst740NoConfigPhaseSeqInApi`; revised `TestAst738TaskGroupingApi`, `TestTaskRoutes::test_preview_task_and_get_update` |

### AST-747 · AST-736

Retired **`consult_*`** on **`POST /api/admin/dispatch_tasks`**; schedulable **`grade_*`**; **`task_keys`** grouping on **`grade_do`** catalog rows (no alias).

| Area | Source | Component tests |
| --- | --- | --- |
| Retired-key guard | `src/ui/api/api_admin.py` | `TestDispatchTasks::test_create_dispatch_task_rejects_retired_consult_key` |
| **`task_keys`** derivation | same | `TestAst739DispatchTaskKeysGrouping`, `test_ast549_task_keys_config_derivation_authoritative`, `TestAdhocHelpers::test_trigger_state_helpers` |

Config helpers: **`docs/test-bible/utils/config.md`** (**AST-747**). **AST-748** owns **`test_consult.py`**.

### AST-749 · AST-736

`GET /api/admin/dispatch_tasks/task_keys` filters **`DISPATCH_RETIRED_TASK_KEYS`** on the `list_dispatch_tasks` loop and final pop — legacy `consult_*` rows never appear in the Add Task picker; `grade_*` keys retain schedulable defaults from **`dispatch_task_admin_defaults`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Retirement filter on read path | `src/ui/api/api_admin.py` | `TestAst749DispatchTaskKeysRetiredFilter::test_dispatch_task_keys_excludes_retired_consult_keys` |
| POST guard (verify only) | same | `TestDispatchTasks::test_create_dispatch_task_rejects_retired_consult_key` (**AST-747**) |

Routed page grouping: **`docs/test-bible/frontend/pages.md`** (**AST-749**).

### AST-796 · AST-794

**`fetch_jd`** schedulable @ **`PASSED_JOBLIST`**; **`scrape_jd`**, **`validate_title`**, **`gaze_board`** in **`DISPATCH_RETIRED_TASK_KEYS`** — filtered from **`task_keys`** and rejected on **`POST /api/admin/dispatch_tasks`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Retirement filter + POST guard | `src/ui/api/api_admin.py` (unchanged; config-driven) | `TestAst796FetchJdRetiredDispatchKeys` |

Config catalog: **`docs/test-bible/utils/config.md`** (**AST-796**).

### AST-797 · AST-794

Runtime: **`fetch_jd_batch`** routing; **`validate_title`** adhoc preview removed; qualify inline validate via consult (**AST-797**).

| Area | Source | Component tests |
| --- | --- | --- |
| Adhoc preview | `src/ui/api/api_admin.py` | `TestAdhocHelpers::test_trigger_state_helpers` — **`validate_title`** returns empty; **`qualify_job_listings`** still builds batch content |

Consult + migration: **`docs/test-bible/core/consult.md`** (**AST-797**).

**AST-796** narrowed pytest:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst796FetchJdSchedulableCutover \
  tests/component/ui/api/test_api_admin.py::TestAst796FetchJdRetiredDispatchKeys \
  -q
```

### AST-773 · AST-763

`PUT /api/admin/dispatch_tasks/<id>` whitelists `task_key` on update; `_dispatch_task_key_trigger_error` validates schedulable keys against `JOB_STATES` / `COMPANY_STATES` and resume-hop compound states; derives catalog columns via `dispatch_task_admin_defaults`; blocks edits on AUTO rows except `auto_mode` toggle; 409 UNIQUE cites attempted `(candidate_id, task_key, trigger_state)`.

| Area | Source | Component tests |
| --- | --- | --- |
| PUT `task_key` + validation helper | `src/ui/api/api_admin.py` | `TestAst773UpdateDispatchTaskTaskKey` |
| Update column whitelist | `src/data/database.py` (`_DISPATCH_TASK_UPDATE_COLS`) | same (integration via PUT) |

Routed page edit modal: **`docs/test-bible/frontend/pages.md`** (**AST-773**).

### AST-781 · AST-763

`GET /api/admin/dispatch_tasks` enriches each row via **`count_eligible_for_dispatch_task`**; legacy rows with retired **`entity_type`** (e.g. **`board_search`**) get **`available_count=0`** instead of raising through **`count_entities_in_state`**.

| Area | Source | Component tests |
| --- | --- | --- |
| List enrichment tolerance | `src/ui/api/api_admin.py` | `TestAst781ListDtasksRetiredEntityType::test_list_dtasks_legacy_board_search_row_returns_zero_available_count` |
| Data-layer guard | `src/data/database.py` | `TestAst766BoardSchemaSunset::test_count_eligible_board_search_entity_returns_zero` (**`docs/test-bible/data/database/dispatch_tasks.md`**) |

**AST-781** narrowed pytest:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst781ListDtasksRetiredEntityType \
  tests/component/data/database/test_dispatch_tasks.py::TestAst766BoardSchemaSunset::test_count_eligible_board_search_entity_returns_zero \
  -q
```

**AST-773** narrowed pytest:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst773UpdateDispatchTaskTaskKey \
  -q
```

### AST-825 · AST-821

**AST-825 (UAT bug):** Schedulable dispatch key **`prefilter`** resolves admin **`task_keys`** grouping via **`dispatch_task_grouping_catalog_key`** → **`prefilter_company`** **`agent_task`** row (**Company Roster**, seq **5** between **`fetch_website`** and **`fetch_job_pages`**). Entity/trigger/scored metadata still keyed by dispatch **`prefilter`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Grouping catalog resolver | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers::test_dispatch_task_grouping_catalog_key_prefilter_maps_to_company` |
| **`task_keys`** grouping lookup | `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py::TestAst825PrefilterDispatchTaskKeysGrouping::test_dispatch_task_keys_prefilter_grouping_from_prefilter_company_catalog` |

Regression: **`TestAst739DispatchTaskKeysGrouping`** (**AST-739** direct catalog grouping).

**AST-825** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers::test_dispatch_task_grouping_catalog_key_prefilter_maps_to_company \
  tests/component/ui/api/test_api_admin.py::TestAst825PrefilterDispatchTaskKeysGrouping \
  tests/component/ui/api/test_api_admin.py::TestAst739DispatchTaskKeysGrouping \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-785 · AST-754

`GET /api/admin/dispatch_tasks` (`list_dtasks`) filters **`DISPATCH_RETIRED_TASK_KEYS`** before enrichment (parity with **`task_keys`** AST-749); wraps **`count_eligible_for_dispatch_task`** in try/except — logs warning, sets **`available_count=0`** on failure instead of 500ing the list.

| Area | Source | Component tests |
| --- | --- | --- |
| Retirement filter on list path | `src/ui/api/api_admin.py` | `TestAst785ListDtasksRobustness::test_list_dtasks_omits_retired_task_keys` |
| Enrichment failure tolerance | same | `TestAst785ListDtasksRobustness::test_list_dtasks_enrichment_failure_returns_zero_count_not_500` |

Routed page auto-open + filter-empty copy: **`docs/test-bible/frontend/pages.md`** (**AST-785**).

**AST-785** narrowed pytest:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst785ListDtasksRobustness \
  -q
```

**AST-749** narrowed pytest:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst749DispatchTaskKeysRetiredFilter \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_create_dispatch_task_rejects_retired_consult_key \
  -q
```


---

### AST-804 · AST-799

Admin **`_dispatch_task_key_trigger_error`** validates all **`ENTITY_TYPES`** members via **`dispatch_entity_state_registry`** (**`CANDIDATE_STATES`** for candidate-scoped keys such as **`inflow_discovery`**); POST create and PUT trigger_state-only updates call the helper; **`GET /api/admin/dispatch_tasks/state_options`** exposes **`candidate`**. Scheduled Actions edit modal loads **`candidate`** state options and uses them for Input State when **`entity_type === "candidate"`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Validation helper + POST/PUT + state_options | `src/ui/api/api_admin.py`, `src/utils/config.py` (`dispatch_entity_state_registry`) | `tests/component/ui/api/test_api_admin.py` — **`TestAst804CandidateDispatchAdminValidation`** (5 cases) |
| Scheduled Actions routed page (**§6c**) | `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — **`AST-804 candidate Input State options`** describe (1 case); revised normalization test includes malformed **`candidate`** payload |

**AST-804** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst804CandidateDispatchAdminValidation \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-804"
```

**Builds on:** **AST-773** (edit modal task_key + validation helper), **AST-505** (**inflow_discovery** admin defaults).

---

### AST-783 · AST-756

**Repo JSON divergence API:** **`GET /api/admin/repo_json/status`** returns per-table `{ diverged, repo_relative_path }`; **`POST /api/admin/repo_json/revert/<table_key>`** restores one table from checked-in JSON (400 for invalid `table_key`).

| Area | Source | Component tests |
| --- | --- | --- |
| Status + revert routes | `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py::TestAst783RepoJsonApi` |

Core compare/revert: **`docs/test-bible/core/repo_admin_json.md`**. UI banner: **`docs/test-bible/frontend/components.md`** (**AST-783**).

**AST-783** narrowed pytest:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst783RepoJsonApi \
  -q
```

---

### AST-809 · AST-378 (UAT fix)

**`_VECTOR_FEEDBACK_COLUMNS`** exposes **`batch_size`** and **`completed_at`**; list query returns both fields.

| Area | Source | Component tests |
| --- | --- | --- |
| req_dict column keys + row fields | `src/ui/api/api_admin.py` | `TestAst809VectorFeedbackBatchMetadata::test_list_returns_batch_metadata_fields` |
| Column registry (with AST-725) | `src/ui/api/api_admin.py` | `TestAst725VectorFeedback::test_list_vector_feedback_and_req_dict` |

---

### AST-808 · AST-378 (UAT fix)

Assessment enrichment, **`/vector_feedback/rubric_lookup`**, and **`POST /vector_feedback/hydrate_reviews`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Assessment header + column defs | `src/ui/api/api_admin.py` | `TestAst808VectorFeedbackHydration::test_list_enriches_assessment_header_and_columns` |
| Rubric lookup map | `src/ui/api/api_admin.py` | `TestAst808VectorFeedbackHydration::test_rubric_lookup_returns_code_map` |
| Hydrate reviews POST | `src/ui/api/api_admin.py` | `TestAst808VectorFeedbackHydration::test_hydrate_reviews_endpoint` |

**AST-808** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_rubric_feedback.py::TestAst808HydrateVectorReviewStrings \
  tests/component/data/database/test_rubric_vectors.py::TestAst808ListVectorFeedbackContent \
  tests/component/ui/api/test_api_admin.py::TestAst808VectorFeedbackHydration \
  -q
```

### AST-875 · AST-873

**`GET /api/admin/dispatch_tasks/counts`** → `{counts: {candidate_id: n}}`; **`POST /api/admin/dispatch_tasks/set_from_template`** with `{candidate_id}` → upsert+prune stats (400/404 on ValueError/LookupError). No **`run_task`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Counts + set_from_template | `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py::TestAst875DispatchTasksSetFromTemplate` |

Primary data manifest: **`docs/test-bible/data/database/dispatch_tasks.md`** (**AST-875**).

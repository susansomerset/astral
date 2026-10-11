# Api Admin

**Test module:** `tests/component/ui/api/test_api_admin.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py` | yes |

---

### AST-485 · AST-461 · AST-549 · AST-721

Decomposed PJL roster hops **`select_job_page`** (**`PJL_READY`**) and **`parse_job_list`** (**`JOBLIST_IDENTIFIED`**); **`find_job_page`** monolith removed (**AST-721**). **`locate_job_page`** is not a catalog key (legacy **`UPDATE`** during schema ensure). **AST-549** retired **`database._DISPATCH_TASK_SEED`** / **`config._DISPATCH_TASK_TRIGGER_SEED`** — defaults from **`dispatch_task_admin_defaults`** (**§7.13zq**). **`get_dispatch_row_or_seed_preview_meta`** supplies admin **`adhoc`** when no sample DB row exists. **`GET /api/admin/dispatch_tasks/task_keys`** lists every **`TASK_CONFIG`** key (**AST-516**); **AST-960** drops frozenset merge — gap keys appear only via existing DB rows.

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

> **AST-1880:** Historical. The global `active_provider`, `DEEPSEEK_MODEL_PRICING`, `resolve_brain_setting_to_deepseek_tier_meta`, `/agents/brain_settings`, the DeepSeek-only client, and `TestAst492ResolveAdhocApiAdmin` are retired. Each agent routes by its own model → server. Current coverage: [§ AST-1880](#ast-1880--ast-1851-admin-model-pickers--per-server-platform-keys).

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

**`GET /api/admin/dispatch_tasks/score_floor_options`** returns `{"values": ["0.00", …, "10.00"]}` from **`dispatch_score_floor_option_labels()`** — mirrors **`state_options`** metadata pattern for the Scheduled Actions edit modal. Zero-persist update: **`test_update_dispatch_task_scored_zero_score_floor`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Score floor catalog endpoint | `src/ui/api/api_admin.py` | `TestDispatchTasks::test_scheduler_and_run_controls` (floors GET) |
| Zero persist on update | same | `TestApiAdminBranchGaps::test_update_dispatch_task_scored_zero_score_floor` |

Routed page + zero-save UX restored on **AST-1278**: **`docs/test-bible/frontend/pages.md`** (**AST-1278**).

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

**AST-970 vocab revise:** state_options / trigger cases use **`ACTIVE_SEARCH`** / **`NEW_CANDIDATE`**; candidate trigger happy-path uses **`intake_initiate_candidate`** (inflow_discovery not in TASK_CONFIG — AST-960). Full manifest: **`docs/test-bible/core/candidate.md`** § AST-970.

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

### AST-955 · AST-856

**Scope:** Scheduled Actions Save accepts any registered non-retired **`TASK_CONFIG`** key (same catalog as the picker). Drops save-time **`DISPATCH_SCHEDULABLE_TASK_KEYS`** membership gate that 400'd **`check_cover_letter`**. Optional **`trigger_state`** on **`dispatch_task_admin_defaults`**; **`save_dispatch_task`** passes request trigger; retired keys still blocked. No dispatcher / Manage Tasks / frontend picker changes.

| Area | Source | Component tests |
| --- | --- | --- |
| Registered-key defaults + override | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst955RegisteredKeyDispatchAdminDefaults` |
| AST-549 unknown-key wording | same | `TestAst549DispatchAdminDefaults::test_unknown_task_key_raises` (revised — junk key / `unknown task_key`) |
| Helper + POST/PUT Save | `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py::TestAst955AlignScheduledActionsSave` |
| Branch-gap create paths | same | `TestDispatchTasks::test_create_dispatch_task_paths` (revised — real `grade_do` keys) |
| DB insert + rejected wording | `src/data/database.py` | `tests/component/data/database/test_dispatch_tasks.py::TestAst955SaveDispatchTaskRegisteredKeys` |

**Broken / obsolete (Betty revision this pass):**
- `TestAst549DispatchAdminDefaults::test_unknown_task_key_raises` — `anticipate_scan` is registered (hop-derived `BUILD_ARTIFACTS`); assert unknown junk key + `unknown task_key`.
- `TestDispatchTasks::test_create_dispatch_task_paths` — fake `custom`/`WATCH` now 400 before save; use `grade_do`/`PASSED_JD`.

**AST-955** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst955RegisteredKeyDispatchAdminDefaults \
  tests/component/utils/test_config.py::TestAst549DispatchAdminDefaults::test_unknown_task_key_raises \
  tests/component/ui/api/test_api_admin.py::TestAst955AlignScheduledActionsSave \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_create_dispatch_task_paths \
  tests/component/data/database/test_dispatch_tasks.py::TestAst955SaveDispatchTaskRegisteredKeys \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-960 · AST-957

**Scope:** `GET /api/admin/dispatch_tasks/task_keys` and `_dispatch_task_key_form_meta` enrich from **`TASK_CONFIG`** + **`dispatch_task_admin_defaults`** only — no frozenset merge. Gap keys leave the picker unless a DB row exists. **AST-955** Save for **`check_cover_letter`** unchanged.

| Area | Source | Component tests |
| --- | --- | --- |
| No frozenset inventory / gap absent | `src/ui/api/api_admin.py` | `TestAst960TaskKeysNoFrozensetInventory` |
| fetch_jd gap + retired rejects | same | revised **`TestAst796FetchJdRetiredDispatchKeys`** |
| AST-856/955 Save regression | same | `TestAst955AlignScheduledActionsSave` |

**Broken / obsolete (Betty revision this pass):** `test_dispatch_task_keys_includes_fetch_jd_excludes_retired` assumed frozenset merge — replaced with gap-absent + DB-row merge cases.

Narrowed run: **`docs/test-bible/core/bootstrap.md`** (**AST-960**).

**AST-962 (UAT):** cover-letter mid-hop default Input State — primary manifest **`docs/test-bible/utils/config.md`** (**AST-962**).

---

### AST-1024 · AST-1023

**AST-1024:** Admin **`POST /api/admin/session_cover_letter/html`** (`@require_admin`) — JSON field keys from **`BUILD_CONFIG["session_cover_letter"]["fields"]`**; optional `candidate_id`; success **`text/html`**; validation / builder **`ValueError`** → **`{success:false,error}`** 400. Core emit: **`docs/test-bible/core/builder.md`** (**AST-1024**). React / localStorage = sibling **AST-1025**.

| Area | Source | Component tests |
| --- | --- | --- |
| Auth + body object + ValueError JSON | `src/ui/api/api_admin.py` | **`TestAst1024SessionCoverLetterHtmlApi`** |
| Fields from config keys; candidate_id strip/null/non-str | same | same class |
| Core SomersetCover emit | `src/core/builder.py` | **`TestAst1024BuildSessionCoverLetter`** |
| Config spine | `src/utils/config.py` | **`TestAst1024SessionCoverLetterConfig`** |

**Broken / obsolete this pass:** none.

**Integration:** no existing scenario asserts this Admin HTML route — no revision.

**AST-1024** narrowed run: **`docs/test-bible/core/builder.md`** (**AST-1024**).

### AST-1062 · AST-1058

**Parent:** [AST-1058 — Qualify Meteorite](https://linear.app/astralcareermatch/issue/AST-1058/qualify-meteorite). **Publish:** `origin/sub/AST-1058/AST-1062-qualify-meteorite-batch-apply-meteorite-qualified`.

Ad Hoc `_build_adhoc_live_content("qualify_meteorite")` lockstep with consult assemble (`METEORITE JOBS:` + job_link/jd).

| Area | Source | Component tests |
| --- | --- | --- |
| Ad Hoc assemble | `src/ui/api/api_admin.py` | **`TestAdhocHelpers::test_build_adhoc_live_content_qualify_meteorite`** |

**Broken / obsolete:** none — additive branch.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_build_adhoc_live_content_qualify_meteorite \
  -q
```

### AST-1106 · AST-1087

**Parent:** [AST-1087](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task). **Publish:** `origin/sub/AST-1087/AST-1106-uat-gaze-email-missing-from-scheduled-actions-default-view`.

`list_dtasks` stamps boolean `always_visible_under_avail_gt0` from config helper; does **not** fake `available_count`. Config / SA: **`docs/test-bible/utils/config.md`**, **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Stamp flag; avail gate unchanged | `src/ui/api/api_admin.py` | **`TestAst1106ListDtasksAlwaysVisibleFlag`** |

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst1106ListDtasksAlwaysVisibleFlag \
  -q
```


### AST-1135 · AST-1128

**Parent:** [AST-1128 — gaze_email — candidate-bound dispatch (redesign)](https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign). **Publish:** `origin/sub/AST-1128/AST-1135-candidate-bound-avail-dispatch-eligibility`.

`list_dtasks` stamps live bind-filtered `available_count` for candidate-bound `gaze_email` rows from one `count_inbox_bound_by_candidate()` snapshot. Always-visible flag remains generic (empty after AST-1134). Inbox: **`docs/test-bible/core/inbox.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Gaze Avail stamp | `src/ui/api/api_admin.py` | **`TestAst1135ListDtasksGazeAvail`** |

**Broken / obsolete:** none — additive stamp path; AST-1106 flag test still valid with mocked helper.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst1135ListDtasksGazeAvail \
  -q
```

### AST-1197 · AST-1188

**Parent:** [AST-1188 — Errors for qualify_meteorite dispatch task](https://linear.app/astralcareermatch/issue/AST-1188/errors-for-qualify-meteorite-dispatch-task). **Publish:** `origin/sub/AST-1188/AST-1197-consult-apply-email-link-bot-blocked`.

Ad-hoc `qualify_meteorite` assemble lockstep with consult: numbered `job_link:` + `CONTENT:` body. Primary apply: **`docs/test-bible/core/consult.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| CONTENT label lockstep | `src/ui/api/api_admin.py` | revised **`TestAdhocHelpers::test_build_adhoc_live_content_qualify_meteorite`** |

**Broken / obsolete:** none — additive `CONTENT:` assert.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_build_adhoc_live_content_qualify_meteorite \
  -q
```

### AST-1214 · AST-1185

**Parent:** [AST-1185 — UI groupings/sequences + alphabetical task key/alias dropdowns](https://linear.app/astralcareermatch/issue/AST-1185/ui-groupingssequences-alphabetical-task-keyalias-dropdowns-data-driven). **Publish:** `origin/sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists`.

`GET /api/admin/dispatch_tasks/task_keys` is the live union of `TASK_CONFIG` ∪ `agent_task` ∪ dispatch orphans, built with `sorted(membership)` (no gap frozenset). Helper-resolvable hops + meteorite mailbox fold (`parse_meteorite_email` / `meteorite_email`) are first-class writable; mailbox trigger is null-only; `list_dtasks` Avail shares gaze_email inbox counts for mailbox keys. Config defaults: **`docs/test-bible/utils/config.md`** (**AST-1214**). React dropdown polish = sibling **AST-1215**.

| Area | Source | Component tests |
| --- | --- | --- |
| Live alpha catalog + eight agent_task-only keys | `src/ui/api/api_admin.py` | revised **`TestAst796FetchJdRetiredDispatchKeys`**, **`TestAst960TaskKeysNoFrozensetInventory`**; **`TestAst1214AdminCatalogAlphabeticalWritable`** |
| Validator (inflow_discovery accept; mailbox null-only; craft unsupported) | same | revised **`TestAst804CandidateDispatchAdminValidation`**; **`TestAst1214AdminCatalogAlphabeticalWritable`** |
| POST create fetch_jd + parse_meteorite_email; mailbox Avail | same | **`TestAst1214AdminCatalogAlphabeticalWritable`** |

**Broken / obsolete (Betty revision this pass):** AST-960 gap-absent picker asserts (`test_dispatch_task_keys_omits_fetch_jd_gap_excludes_retired`, `test_gap_key_absent_without_db_row`); `inflow_discovery` → `Unknown task_key` in **`test_dispatch_task_key_trigger_error_candidate_paths`**.

**Integration:** no existing scenarios assert Admin `task_keys` membership / mailbox Avail — none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst796FetchJdRetiredDispatchKeys \
  tests/component/ui/api/test_api_admin.py::TestAst960TaskKeysNoFrozensetInventory \
  tests/component/ui/api/test_api_admin.py::TestAst804CandidateDispatchAdminValidation::test_dispatch_task_key_trigger_error_candidate_paths \
  tests/component/ui/api/test_api_admin.py::TestAst1214AdminCatalogAlphabeticalWritable \
  tests/component/utils/test_config.py::TestAst796FetchJdSchedulableCutover::test_fetch_jd_gazer_hop_not_task_config_catalog \
  tests/component/utils/test_config.py::TestAst702PrefilterBatchConfig::test_prefilter_dispatch_batch_mode_and_defaults \
  tests/component/utils/test_config.py::TestAst719FetchJobPagesConfig::test_dispatch_registry_and_pjl_data_keys \
  tests/component/utils/test_config.py::TestAst701FetchWebsiteConfig::test_dispatch_registry_and_homepage_text_key \
  tests/component/utils/test_config.py::TestAst874FetchCulturePagesConfig::test_gazer_and_dispatch_registry \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_inflow_discovery_dispatch_admin_defaults \
  tests/component/utils/test_config.py::TestAst506InflowResolveConfig::test_inflow_resolve_website_dispatch_admin_defaults \
  tests/component/utils/test_config.py::TestAst1089ParseMeteoriteEmailConfig \
  tests/component/utils/test_config.py::TestAst1214DispatchAdminDefaultsWidened \
  -q
```

### AST-1394 · AST-1392 (show Ad Hoc Test body without type invalidation)

**Parent:** [AST-1392](https://linear.app/astralcareermatch/issue/AST-1392). **Publish:** `origin/sub/AST-1392/AST-1394-show-ad-hoc-test-body-without-type-invalidation`.

`POST /api/admin/adhoc/test` stringifies the extracted workbench body via **`_caller_response_blob`** so `response_text` is always a `str` (compact JSON for dict/list; already-`str` unchanged). Envelope still extracts **`agent_payload`** when present. Failure stays HTTP 500 / `success: false` — no fake success body. Persist/debug: **AST-1393**. Workbench chrome: **`docs/test-bible/frontend/pages.md`** § AST-1394.

| Area | Source | Component tests |
| --- | --- | --- |
| Object/list/plain/numeric `response_text` | `src/ui/api/api_admin.py` (`adhoc_test`) | **`TestAst1394AdhocTestResponseText::test_success_response_text_is_serialized_str`** |
| Provider failure 500, no `response_text` | same | **`test_failure_stays_500_without_success_body`**; existing **`TestAdhocRoutes::test_adhoc_preview_and_test`** |
| String payload + numeric regression | same | **`TestAdhocRoutes::test_adhoc_preview_and_test`** (`"payload"` / `"123"`) |

**Broken / obsolete this pass:** none — existing string/numeric assertions still hold.

**Integration:** no existing scenario asserts Ad Hoc Test `response_text` — no revision; do not invent new integration coverage.

## QA test manifest

1. Existing string/numeric + 500: `tests/component/ui/api/test_api_admin.py::TestAdhocRoutes::test_adhoc_preview_and_test`
2. Object/list/plain stringify + failure envelope: `tests/component/ui/api/test_api_admin.py::TestAst1394AdhocTestResponseText`

**AST-1394** narrowed run (API; page chrome in **`frontend/pages.md`**):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAdhocRoutes::test_adhoc_preview_and_test \
  tests/component/ui/api/test_api_admin.py::TestAst1394AdhocTestResponseText \
  -q
```

### AST-1411 · AST-1403 (Ad Hoc seven-segment resolve, assemble, persist)

**Parent:** [AST-1403](https://linear.app/astralcareermatch/issue/AST-1403). **Publish:** `origin/sub/AST-1403/AST-1411-ad-hoc-seven-segment-resolve-assemble-persist`.

`_resolve_adhoc` token-resolves seven body segments; Preview JSON always includes `cache_a`–`cache_d` (`cache` remains Cache A alias). Empty `system_prompt` in the body falls back to agent `content`; omitted key keeps the DB task system. Test forwards four caches into `run_adhoc_workbench_test` and returns `batch_id` on HTTP 200 and soft-fail 500. Persist/debug: **`docs/test-bible/core/agent.md`** § AST-1411. React editors / panes: sibling #2 / #3.

| Area | Source | Component tests |
| --- | --- | --- |
| Seven-segment resolve + Preview keys; empty vs omitted System | `src/ui/api/api_admin.py` (`_resolve_adhoc`, `adhoc_preview`) | **`TestAst1411AdhocSevenSegment::test_resolve_preview_seven_segment_and_system_fallback`** |
| Test forwards A/C; `batch_id` on 200 and 500 | same (`adhoc_test`) | **`test_adhoc_test_forwards_caches_and_returns_batch_id`** |
| Preview mock shape (cache_a–d required by jsonify) | same | revised **`TestAdhocRoutes`** preview mocks |

**Broken / obsolete this pass:** `TestAdhocRoutes` `_resolve_adhoc` mocks used by Preview lacked `cache_a`–`cache_d` (KeyError after Stage 1 jsonify). Test-only mocks that never hit Preview stay on `.get`.

**Integration:** no existing scenario asserts Ad Hoc Preview cache_b–d / Test `batch_id` — no revision; do not invent new integration coverage.

## QA test manifest

1. Existing preview/test envelopes (revised mocks): `tests/component/ui/api/test_api_admin.py::TestAdhocRoutes::test_adhoc_preview_and_test`
2. Preview still ledger-free: `tests/component/ui/api/test_api_admin.py::TestAdhocRoutes::test_adhoc_preview_does_not_create_dispatch_ledger`
3. Stringify regression: `tests/component/ui/api/test_api_admin.py::TestAst1394AdhocTestResponseText`
4. Seven-segment resolve/preview + Test identity: `tests/component/ui/api/test_api_admin.py::TestAst1411AdhocSevenSegment`

**AST-1411** narrowed run (API; persist/debug in **`core/agent.md`**):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAdhocRoutes::test_adhoc_preview_and_test \
  tests/component/ui/api/test_api_admin.py::TestAdhocRoutes::test_adhoc_preview_does_not_create_dispatch_ledger \
  tests/component/ui/api/test_api_admin.py::TestAst1394AdhocTestResponseText \
  tests/component/ui/api/test_api_admin.py::TestAst1411AdhocSevenSegment \
  -q
```

### AST-1412 · AST-1403 (Ad Hoc seven-segment `*_len` passthrough)

**Parent:** [AST-1403](https://linear.app/astralcareermatch/issue/AST-1403). **Publish:** `origin/sub/AST-1403/AST-1412-ad-hoc-seven-segment-editors-and-save`.

`_enrich_tasks` copies seven prompt-length ints onto list rows (`user_prompt_len`, `cache_prompt_len`, `cache_prompt_b/c/d_len`, `nocache_prompt_len`, `system_prompt_len`) so Agent Ad Hoc overwrite ● / `taskHasExistingPrompts` can see Cache-B-only content. Editors / Save As / Preview-Test bodies: **`docs/test-bible/frontend/pages.md`** § AST-1412.

| Area | Source | Component tests |
| --- | --- | --- |
| Seven `*_len` including Cache-B-only | `src/ui/api/api_admin.py` (`_enrich_tasks`) | **`TestAst1412EnrichTaskLens::test_enrich_tasks_passes_seven_segment_lens_including_cache_b_only`** |

**Broken / obsolete this pass:** none — existing `TestEnrichTasks` rows still assert token/cache branches; they did not pin B–D lens.

**Integration:** no existing scenario asserts Ad Hoc overwrite ● from `*_len` — no revision; do not invent new integration coverage.

## QA test manifest

1. Seven `*_len` passthrough: `tests/component/ui/api/test_api_admin.py::TestAst1412EnrichTaskLens`

**AST-1412** narrowed run (API; page in **`frontend/pages.md`**):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst1412EnrichTaskLens \
  -q
```

Ad Hoc import list route lives with parent **AST-1451** / scoped **AST-1534** in **`docs/test-bible/core/agent.md`** (`TestAst1451AdhocRuns`, `TestAst1534AdhocRunsScoped`).

### AST-1618 · AST-1616

**Parent:** [AST-1616](https://linear.app/astralcareermatch/issue/AST-1616). **Publish:** `origin/sub/AST-1616/AST-1618-persist-entity-type-admin`.

Persist explicit `entity_type` on admin create/update; validate `trigger_state` against the submitted entity; recompute `sort_by` for the chosen entity + trigger. React Entity Type control = sibling **AST-1619**. Data insert sort path: **`docs/test-bible/data/database/dispatch_tasks.md`** § AST-1618.

| AC | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| AC3 create entity | POST forwards `entity_type` into `save_dispatch_task` | `src/ui/api/api_admin.py` | **`TestAst1618PersistEntityTypeAdmin::test_create_forwards_entity_type`** |
| AC4 update entity | PUT `entity_type` without `task_key` change; sort recomputed | same | **`test_update_entity_type_without_task_key`** |
| AC5 validate pair | Helper + POST/PUT 400 on entity/trigger mismatch | same | **`test_trigger_error_honors_entity_override`**, **`test_create_rejects_entity_trigger_mismatch`**, **`test_update_rejects_mismatched_entity_trigger`** |
| Empty/unknown/null | Empty/unknown 400; PUT `null` = omit | same | **`test_create_rejects_empty_and_unknown_entity`**, **`test_update_null_entity_type_treated_as_omit`** |

**Broken / obsolete (Betty revised this pass):**

- `TestAst773UpdateDispatchTaskTaskKey::test_update_dispatch_task_task_key_persists_derived_columns` — assert `sort_by` for effective trigger (`NEW`), not catalog default `PASSED_JD`.
- `TestAst804CandidateDispatchAdminValidation::test_update_dispatch_task_trigger_state_only_candidate_row` — mock row must include `entity_type` (update sort recompute).
- `TestDispatchTasks::test_update_dispatch_task_paths` — schedule-only PUT (no blank `trigger_state`); mock includes `entity_type`.

**Integration:** no existing scenario covers admin entity_type persist — do not invent new integration coverage.

## QA test manifest

1. API entity_type create/update/validate: `tests/component/ui/api/test_api_admin.py::TestAst1618PersistEntityTypeAdmin`
2. Revised update regressions: `TestAst773UpdateDispatchTaskTaskKey::test_update_dispatch_task_task_key_persists_derived_columns`, `TestAst804CandidateDispatchAdminValidation::test_update_dispatch_task_trigger_state_only_candidate_row`, `TestDispatchTasks::test_update_dispatch_task_paths`
3. Data `save_dispatch_task` caller entity / sort: `tests/component/data/database/test_dispatch_tasks.py::TestAst1618SaveDispatchTaskCallerEntity` (primary map: **`docs/test-bible/data/database/dispatch_tasks.md`**)

**AST-1618** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst1618PersistEntityTypeAdmin \
  tests/component/ui/api/test_api_admin.py::TestAst773UpdateDispatchTaskTaskKey::test_update_dispatch_task_task_key_persists_derived_columns \
  tests/component/ui/api/test_api_admin.py::TestAst804CandidateDispatchAdminValidation::test_update_dispatch_task_trigger_state_only_candidate_row \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_update_dispatch_task_paths \
  tests/component/data/database/test_dispatch_tasks.py::TestAst1618SaveDispatchTaskCallerEntity \
  -q
```

**Pass criterion:** pytest green on items 1–3 — not zero-arg harness / branch-lock gate.

**Product note for test-child:** `test_caller_entity_overrides_catalog_sort` encodes Stage 1 Done-when (`entity_type=company` + `trigger_state=WATCH` on `grade_do`). Today `save_dispatch_task` calls `dispatch_task_admin_defaults(tk, trigger_state=…)` before applying the caller entity, so a trigger valid only for the chosen entity raises `ValueError` (API 500). Fix the data path so defaults fill does not require the request trigger to be valid for the catalog entity when the caller supplied `entity_type`.

### AST-1623 · AST-1620

**Parent:** [AST-1620 — Treat meteorite as a first-class dispatch entity_type](https://linear.app/astralcareermatch/issue/AST-1620/treat-meteorite-as-a-first-class-dispatch-entity-type). **Publish:** `origin/sub/AST-1620/AST-1623-admin-available-state-options-ledger`.

Admin `state_options` exposes `meteorite` via `dispatch_entity_state_registry`; `list_dtasks` Available counts meteorite rows without requiring `candidate_id`; create/update accept `meteorite` via `ENTITY_TYPES` (no parallel enum). Dispatcher ingress/notify ledger writes `entity_type="meteorite"`; `correct_meteorite_ingress_dispatch_entity_types` UPDATE-only NULL→meteorite for ingress/notify keys (boot from `start_scheduler`). Count helper: **AST-1622**; registries/seeds: **AST-1621**.

| Area | Source | Component tests |
| --- | --- | --- |
| state_options + Available + create | `src/ui/api/api_admin.py` | **`TestAst1623AdminMeteoriteStateOptionsAvail`** |
| Ledger entity_type + correction + boot | `src/core/dispatcher.py` | **`TestAst1623MeteoriteLedgerAndBackfill`** |
| Boot stub for correction | same | revised **`_stub_scheduler_boot_provisions`** |

**Broken / obsolete:** `_stub_scheduler_boot_provisions` — stub `correct_meteorite_ingress_dispatch_entity_types` so start_scheduler unit tests stay DB-free (correction was try/except-swallowed before).

**Integration:** none — no existing scenario asserts meteorite state_options / NULL-cid Available / ingress ledger entity_type; do not invent.

## QA test manifest

1. Admin state_options + Available + create: `tests/component/ui/api/test_api_admin.py::TestAst1623AdminMeteoriteStateOptionsAvail`
2. Ledger + correction + boot: `tests/component/core/test_dispatcher.py::TestAst1623MeteoriteLedgerAndBackfill`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst1623AdminMeteoriteStateOptionsAvail \
  tests/component/core/test_dispatcher.py::TestAst1623MeteoriteLedgerAndBackfill \
  -q
```

**Pass criterion:** pytest green on items 1–2 — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/ui/api/api_admin.md` — *(filled after publish)*


### AST-1675 · AST-1671

**Scope:** Admin form/meta and adhoc live-content key on **`prefilter_company`**. Grouping uses identity catalog key (shim deleted). Bare `prefilter` absent from picker.

| Area | Source | Component tests |
| --- | --- | --- |
| task_keys grouping + form meta | `src/ui/api/api_admin.py` | revised **`TestAst825PrefilterDispatchTaskKeysGrouping`** |
| Adhoc homepage+nav | same | revised **`TestAdhocHelpers::test_build_adhoc_live_content_company_paths`**; **`TestApiAdminBranchGaps::test_build_adhoc_live_content_remaining_company_and_job_edges`** |

**Broken / obsolete this pass:** AST-825 expecting `keys["prefilter"]`; adhoc live-content keyed on bare `prefilter`.

**Integration:** none.

## QA test manifest

1. Picker grouping: `tests/component/ui/api/test_api_admin.py::TestAst825PrefilterDispatchTaskKeysGrouping`
2. Adhoc live-content: `tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_build_adhoc_live_content_company_paths` + `::TestApiAdminBranchGaps::test_build_adhoc_live_content_remaining_company_and_job_edges`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst825PrefilterDispatchTaskKeysGrouping \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_build_adhoc_live_content_company_paths \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_build_adhoc_live_content_remaining_company_and_job_edges \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/ui/api/api_admin.md` — *(filled after publish)*

---

### AST-1728 · AST-1721 (qa-fix bug-repro — admin Telescope API)

**Board REVISE:** `POST /api/admin/telescope` + `admin_telescope_scrape` + nav Tools entry.

| Area | Component tests |
| --- | --- |
| Route / helper / nav / page file | `tests/component/ui/api/test_api_admin_telescope.py::TestAst1728AdminTelescopeRepro` (**bug-repro**) |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin_telescope.py -q
```

### AST-1780 · AST-1766 (list enrich, AUTO/Run gates, force AUTO off)

**Parent:** [AST-1766 — Dispatch Validation](https://linear.app/astralcareermatch/issue/AST-1766). **Publish:** `origin/sub/AST-1766/AST-1780-list-enrich-auto-run-gates-force-auto-off`.

`GET /api/admin/dispatch_tasks` stamps `empty_render` via `_evaluate_dispatch_empty_render` → AST-1779 `empty_render_for_prompts` (no `entity_contexts`); forces `auto_mode` off when true. Create/PUT AUTO-on and `POST …/run` return 400 via `_candidate_dispatch_empty_render_error` after the API-key gate. Predicate helper: **`docs/test-bible/utils/config.md`** § AST-1779. Version hooks: sibling **AST-1781**. React: sibling **AST-1782**.

| Area | Source | Component tests |
| --- | --- | --- |
| List flag + force AUTO off | `src/ui/api/api_admin.py` | **`TestAst1780EmptyRenderListGatesForceOff::test_list_sets_empty_render_and_forces_auto_off`** |
| List keeps AUTO when false | same | **`…::test_list_empty_render_false_keeps_auto`** |
| Create AUTO-on 400 | same | **`…::test_create_auto_on_empty_render_400`** |
| PUT AUTO-on 400 | same | **`…::test_put_auto_on_empty_render_400`** |
| Run 400 `started: false` | same | **`…::test_run_empty_render_400_started_false`** |
| Error helper None when clear | same | **`…::test_error_helper_none_when_evaluate_false`** |

**Broken / obsolete this pass:** AUTO-on / run success paths that only stubbed `_candidate_dispatch_api_key_error` — revised to also stub `_candidate_dispatch_empty_render_error` → None:
- **`TestDispatchTasks::test_scheduler_and_run_controls`**
- **`TestApiAdminBranchGaps::test_create_dispatch_task_auto_mode_success`**
- **`TestApiAdminBranchGaps::test_update_dispatch_task_scored_score_floor_and_auto_mode_success`**

**Integration:** none — no existing scenario asserts `empty_render` on dispatch list / AUTO-Run gates; do not invent new integration coverage.

### AST-1792 · AST-1790 (gap: no-prompt ValueError → empty_render false)

**Parent:** [AST-1790](https://linear.app/astralcareermatch/issue/AST-1790). **Sibling product:** AST-1791. **Publish:** `origin/sub/AST-1790/AST-1792-no-prompt-valueerror-empty-render-tests`.

AST-1791 / AST-1790 — prompt-load `ValueError` soft-miss → `empty_render: false` (no monkeypatch of `_evaluate_dispatch_empty_render`). Stub `_dispatch_empty_render_prompt_texts` to raise; candidate present. Red on pre-AST-1791 product; green after AST-1791.

| Area | Source | Component tests |
| --- | --- | --- |
| Helper ValueError → false `[bug-repro]` | `src/ui/api/api_admin.py` | **`TestAst1791NoPromptValueErrorEmptyRender::test_evaluate_valueerror_no_agent_task_empty_render_false`** |
| List keeps AUTO on soft-miss | same | **`…::test_list_valueerror_no_prompts_keeps_auto`** |
| Run allowed on soft-miss | same | **`…::test_run_valueerror_no_prompts_allowed`** |

Keep AST-1780 monkeypatched wiring rows above; do not mark them obsolete.

**Integration:** none — do not invent new integration scenarios.

### AST-1795 · AST-1793 (gap: soft-miss warning silence)

**Parent:** [AST-1793](https://linear.app/astralcareermatch/issue/AST-1793). **Sibling product:** AST-1794. **Publish:** `origin/sub/AST-1793/AST-1795-no-agent-empty-render-warning-tests`.

AST-1794 — ValueError soft-miss stays `empty_render: false` **and** emits no `no prompts to validate` warning. Same stubs as AST-1792; spy `admin_mod.logger.warning`. Red on pre-AST-1794 product; green after silence.

| Area | Source | Component tests |
| --- | --- | --- |
| Helper soft-miss silence `[bug-repro]` | `src/ui/api/api_admin.py` | **`TestAst1791NoPromptValueErrorEmptyRender::test_evaluate_valueerror_soft_miss_no_warning`** |

Keep AST-1780 / AST-1792 rows; do not mark them obsolete.

**Integration:** none — do not invent new integration scenarios.

### AST-1855 · AST-1852 (gap: hydrated candidate view for dispatch empty-render)

**Parent:** [AST-1852](https://linear.app/astralcareermatch/issue/AST-1852) (orphaned-bug mini-parent). **Sibling product:** AST-1854 (`b5a72977` on `origin/sub/AST-1852/AST-1854-dispatch-gate-hydrated-candidate`). **Publish:** `origin/sub/AST-1852/AST-1855-dispatch-gate-hydrated-candidate-tests`.

AST-1854 — dispatch empty-render (and `_enrich_tasks` / `_resolve_adhoc`) loads the hydrated candidate (operative artifact overlay onto `candidate_data.context`), not the raw row. Only `database.get_candidate`, `database.get_current_artifact`, and `_dispatch_empty_render_prompt_texts` are stubbed; loader, `hydrate_operative_*`, `build_candidate_token_view`, `resolve_tokens`, `empty_render_for_prompts` stay real. One `_evaluate_dispatch_empty_render` repro gates all three call sites (same one-token loader swap).

**Sequencing deviation (gap child):** product not on ftr yet. `[bug-repro]` proven both ways — **RED at ftr base `3dd7f249`** (`c1` → `{"empty_render": True, "empty_tokens": ["IDEAL_DAY"]}`) and **GREEN with `b5a72977`'s `api_admin.py` overlaid** (scratch worktree, not committed).

| Area | Source | Component tests |
| --- | --- | --- |
| Artifact-only Ideal Day → false `[bug-repro]` | `src/ui/api/api_admin.py` | **`TestAst1854HydratedCandidateEmptyRender::test_evaluate_artifact_only_ideal_day_empty_render_false`** |
| No artifact, no legacy blob → true, `["IDEAL_DAY"]` | same | **`…::test_evaluate_no_ideal_day_anywhere_empty_render_true`** |
| Legacy `context.ideal_day` only → false | same | **`…::test_evaluate_legacy_blob_ideal_day_empty_render_false`** |

**Revised (hermeticity, not obsolete):** seven existing row-returning `database.get_candidate` stubs on swapped paths now also stub `database.get_current_artifact → None`, so the hydrated loader never reads the repo `data/astral.db`: `TestEnrichTasks::test_enrich_tasks_covers_agent_and_cache_branches`, `TestAdhocHelpers::test_adhoc_entities_and_resolve`, `TestAdhocHelpers::test_resolve_adhoc_job_entity_resolves_visible_jd_token`, and the four `TestAst1791NoPromptValueErrorEmptyRender` tests (via `_stub_no_agent_task_prompts`). Keep AST-1780 / AST-1792 / AST-1795 rows unchanged.

Pre-existing unrelated reds in this file (same 5 as AST-1819, red at base without these edits) — not in this manifest.

**Integration:** none — do not invent new integration scenarios.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst1854HydratedCandidateEmptyRender \
  tests/component/ui/api/test_api_admin.py::TestEnrichTasks::test_enrich_tasks_covers_agent_and_cache_branches \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_adhoc_entities_and_resolve \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_resolve_adhoc_job_entity_resolves_visible_jd_token \
  tests/component/ui/api/test_api_admin.py::TestAst1791NoPromptValueErrorEmptyRender \
  -q
```

**Pass criterion:** pytest green on these nodes with AST-1854 product on the tree under test; the `[bug-repro]` stays red until then.

## QA test manifest

1. List force off: `tests/component/ui/api/test_api_admin.py::TestAst1780EmptyRenderListGatesForceOff::test_list_sets_empty_render_and_forces_auto_off`
2. List keeps AUTO: `tests/component/ui/api/test_api_admin.py::TestAst1780EmptyRenderListGatesForceOff::test_list_empty_render_false_keeps_auto`
3. Create 400: `tests/component/ui/api/test_api_admin.py::TestAst1780EmptyRenderListGatesForceOff::test_create_auto_on_empty_render_400`
4. PUT 400: `tests/component/ui/api/test_api_admin.py::TestAst1780EmptyRenderListGatesForceOff::test_put_auto_on_empty_render_400`
5. Run 400: `tests/component/ui/api/test_api_admin.py::TestAst1780EmptyRenderListGatesForceOff::test_run_empty_render_400_started_false`
6. Helper None: `tests/component/ui/api/test_api_admin.py::TestAst1780EmptyRenderListGatesForceOff::test_error_helper_none_when_evaluate_false`
7. Revised run success: `tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_scheduler_and_run_controls`
8. Revised create AUTO: `tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_create_dispatch_task_auto_mode_success`
9. Revised update AUTO: `tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_update_dispatch_task_scored_score_floor_and_auto_mode_success`
10. ValueError soft-miss return: `tests/component/ui/api/test_api_admin.py::TestAst1791NoPromptValueErrorEmptyRender::test_evaluate_valueerror_no_agent_task_empty_render_false`
11. **`[bug-repro]`** soft-miss silence: `tests/component/ui/api/test_api_admin.py::TestAst1791NoPromptValueErrorEmptyRender::test_evaluate_valueerror_soft_miss_no_warning`
12. List soft-miss keeps AUTO: `tests/component/ui/api/test_api_admin.py::TestAst1791NoPromptValueErrorEmptyRender::test_list_valueerror_no_prompts_keeps_auto`
13. Run soft-miss allowed: `tests/component/ui/api/test_api_admin.py::TestAst1791NoPromptValueErrorEmptyRender::test_run_valueerror_no_prompts_allowed`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst1780EmptyRenderListGatesForceOff \
  tests/component/ui/api/test_api_admin.py::TestAst1791NoPromptValueErrorEmptyRender \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_scheduler_and_run_controls \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_create_dispatch_task_auto_mode_success \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_update_dispatch_task_scored_score_floor_and_auto_mode_success \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate. AST-1795 `[bug-repro]` stays red until AST-1794 product silence lands on the tree under test.

**Bible shasum (publish tip):** fill after `merge-tests` —
- `docs/test-bible/ui/api/api_admin.md`


### AST-1807 · AST-1805 (implicit _RETRY substate)

**Parent:** [AST-1804](https://linear.app/astralcareermatch/issue/AST-1804). **Publish:** `origin/sub/AST-1804/AST-1807-implicit-retry-tests`. Product: **AST-1805** (`{base}_RETRY` validates through its registered base; retry priors derived by `state_prior_states`). Probe retries are never registry keys, so these stay green through **AST-1806**'s purge. Unregistered base (`NOPE_RETRY`) is still rejected everywhere.

| Area | Source | Component tests |
| --- | --- | --- |
| `_dispatch_task_key_trigger_error` general (job) + mailbox candidate branches accept `{base}_RETRY`, reject `NOPE_RETRY` | `src/ui/api/api_admin.py` | **`TestAst773UpdateDispatchTaskTaskKey::test_ast1807_trigger_error_accepts_implicit_retry`** |

**Broken / obsolete:** none.

**Integration:** none — do not invent.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst773UpdateDispatchTaskTaskKey::test_ast1807_trigger_error_accepts_implicit_retry \
  -q
```

### AST-1819 · AST-1817 (qa-fix bug-repro — list_dtasks `empty_tokens` row field)

**Parent:** [AST-1817](https://linear.app/astralcareermatch/issue/AST-1817). **Publish:** `origin/sub/AST-1817/AST-1819-invalid-button-missing-token-tooltip`.

`GET /api/admin/dispatch_tasks` rows carry `empty_tokens: list[str]` (from the already-computed `_evaluate_dispatch_empty_render`) for the Scheduled Actions Invalid tooltip. Additive key; AUTO force-off unchanged.

| Area | Source | Component tests |
| --- | --- | --- |
| Row `empty_tokens` = token list `[bug-repro]` | `src/ui/api/api_admin.py` | **`TestAst1780EmptyRenderListGatesForceOff::test_list_sets_empty_render_and_forces_auto_off`** (revised: asserts `["FIRST_NAME"]`) |
| Row `empty_tokens` = `[]` when valid `[bug-repro]` | same | **`…::test_list_empty_render_false_keeps_auto`** (revised) |

Red on pre-fix tree: `KeyError: 'empty_tokens'`. Pre-existing unrelated reds in this file (5, also red without AST-1819 edits): AST-781 legacy board_search, `TestDispatchTasks::test_list_dispatch_tasks_and_keys`, `TestApiAdminBranchGaps::test_dispatch_task_keys_db_row_adds_orphan_key`, AST-783 repo_json revert, AST-1214 mailbox wording — not in this manifest.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst1780EmptyRenderListGatesForceOff -q
```

### AST-1830 · AST-1824

**Parent:** [AST-1824](https://linear.app/astralcareermatch/issue/AST-1824). **Publish:** `origin/sub/AST-1824/AST-1830-sweep-interval-admin-api-ui`.

Admin create/update accept `sweep_hrs` via `_parse_sweep_hrs` (null / `""` / blank → NULL; negative or non-numeric → 400; `0` kept as off). PUT adds `sweep_hrs` to the allowed set; AUTO edit lock unchanged. `_DISPATCH_TASK_COLUMNS` gains `sweep_hrs` (float) after `freq_hrs`. Schema, scheduler, and DB persistence are sibling **AST-1829** (`docs/test-bible/core/dispatcher.md` § AST-1829). Page half: **`docs/test-bible/frontend/pages.md`** § AST-1830.

| AC | Source | Component tests |
| --- | --- | --- |
| 11 POST 2.5 persists / null·empty → NULL / omitted → NULL | `create_dtask` / `_parse_sweep_hrs` | `tests/component/ui/api/test_api_admin.py::TestAst1830SweepHrsAdminApi::{test_create_passes_sweep_hrs,test_create_omitted_sweep_hrs_is_null}` |
| 11 negative / non-numeric → 400, no save | same | `::TestAst1830SweepHrsAdminApi::test_create_rejects_bad_sweep_hrs` |
| 11 PUT AUTO-off 4 → 4, null → NULL; bad → 400 | `update_dtask` | `::TestAst1830SweepHrsAdminApi::{test_update_sets_or_clears_sweep_hrs,test_update_rejects_bad_sweep_hrs,test_update_without_sweep_key_leaves_it_untouched}` |
| AUTO edit lock unchanged | `update_dtask` | `::TestAst1830SweepHrsAdminApi::test_update_auto_row_edit_lock_unchanged` |
| 11 list column metadata key | `_DISPATCH_TASK_COLUMNS` (`?req_dict=1`) | `::TestAst1830SweepHrsAdminApi::test_column_metadata_includes_sweep_hrs` |
| 13 UI-initiated AUTO run = one batch, min 1 | `src/core/dispatcher.py` (unchanged here) | `tests/component/core/test_dispatcher.py::TestAst1829ScheduledSweep::test_sweep_one_batch_no_min_gate_and_debug[ui_sweep_contrast]` |

**Broken / obsolete:** none. Existing `test_api_admin.py` and both Scheduled Actions Vitest files stay green with this product. The 5 known-red admin tests (AST-781 legacy board_search, `TestDispatchTasks::test_list_dispatch_tasks_and_keys`, `TestApiAdminBranchGaps::test_dispatch_task_keys_db_row_adds_orphan_key`, AST-783 repo_json revert, AST-1214 mailbox wording) are red on the pre-AST-1830 tip too, so they're out of this manifest. **Integration:** none.

## QA test manifest

1. **API (required, green):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst1830SweepHrsAdminApi \
  "tests/component/core/test_dispatcher.py::TestAst1829ScheduledSweep::test_sweep_one_batch_no_min_gate_and_debug" \
  -q
```

2. **Page Vitest (required, green — whole file, §6c routed page):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions_AST1104.test.tsx
```

3. **AC 12 build:** `cd src/ui/frontend && npm run build` succeeds.
4. **AC 13 grep:** `grep -n "sweepDisabled" src/ui/frontend/src/pages/AdminScheduledActions.tsx` still shows `!!row.auto_mode && avail >= (row.min_count || 1)`.
5. **Regression (no new reds):** whole `tests/component/ui/api/test_api_admin.py`. Pass means the failing set is exactly the 5 known reds above.
6. **Branch lock:** `src/ui/api/api_admin.py` (`LOCKED_AT_100`): no missed lines or arcs in the AST-1830 hunks (`_parse_sweep_hrs`, create 400 + kwarg, update parse + `elif k == "sweep_hrs"`).

**Bible shasum (publish tip):** fill after `merge-tests` —
- `docs/test-bible/ui/api/api_admin.md`
- `docs/test-bible/frontend/pages.md`

### AST-1831 · AST-1820

**Parent:** AST-1820 (UAT-batch). **Publish:** `origin/sub/AST-1820/AST-1831-recheck-no-openings-batch-size-max-runs`.

Admin **`create_dtask`** (POST **`/api/admin/dispatch_tasks`**) persists **`max_runs`** through an **`update_dispatch_task(task_id, max_runs=int(...))`** follow-up (**`save_dispatch_task`** has no **`max_runs`** param; before the fix every form-created row kept column DEFAULT **1**). Absent / JSON null → no follow-up (DEFAULT 1 unchanged).

| Area | Source | Component tests |
| --- | --- | --- |
| Create **`max_runs`** follow-up | `src/ui/api/api_admin.py` (**`create_dtask`**) | `tests/component/ui/api/test_api_admin.py::TestAst1831CreateMaxRuns` (**`test_create_persists_max_runs`** 0 / 5 / `"3"`; **`test_create_without_max_runs_skips_follow_up`** absent / null) |

**Repro:** `test_create_persists_max_runs` red on pre-fix tip (`update_dispatch_task` not called). **Branch lock:** `api_admin.py` (`LOCKED_AT_100`) — both arms of the new `max_runs` guard covered.

---

### AST-1880 · AST-1851 (admin model pickers + per-server platform keys)

The admin API and screens drop the global provider. **Manage Agents** gets `GET /agents/models`: a model → own-brain-size catalog, with an `order` index because jsonify sorts keys. `/agents/brain_settings` and `_agent_admin_view` are gone. Create requires `agent_id` + `model_id` + `brain_setting`; update takes `content` / `model_id` / `brain_setting` / `temperature` / `max_tokens`. A data-layer `ValueError` (for example Kimi + Medium) returns 400 and leaves the row unchanged. `_resolve_adhoc` / `_enrich_tasks` route by `resolve_model_brain`. Ad hoc: an unroutable agent → 400, and core gets `server_id` / `tier` / `candidate_api_keys`. Task manager: the row stays blank and a warning is logged. The dispatch key gate names the task agent's server label, and agentless tasks need no key. `list_dtasks` marks a missing key as Invalid with `invalid_reason` and forces AUTO off; Run returns 400 without starting. Session paste forwards `candidate_id`. `config.py` / `cost_calculator.py` lose the DeepSeek-only symbols, and `src/external/deepseek.py` is deleted. Pointers: [`api_candidate.md`](api_candidate.md), [`../../utils/config.md`](../../utils/config.md), [`../../utils/cost_calculator_deepseek.md`](../../utils/cost_calculator_deepseek.md), [`../../core/monitor.md`](../../core/monitor.md), [`../../data/database/timesheets.md`](../../data/database/timesheets.md), [`../../frontend/pages.md`](../../frontend/pages.md).

| Area | Source | Component tests |
| --- | --- | --- |
| AC 3: `/agents/models` exact shape per catalog model (label, server id/label, own sizes + defaults, `order`); Kimi Little/Big, Claude + DeepSeek Little/Medium/Big | `list_models` | `test_api_admin.py::TestAdminConfigAndAgents::test_list_models_is_per_model_brain_size_catalog` |
| Retired: `/agents/brain_settings` now falls through to `GET /agents/<id>` → 404; `list_brain_settings` / `_agent_admin_view` absent | `api_admin.py` | `…::test_brain_settings_route_and_admin_view_retired` |
| List / get pass through the data-layer row (no admin inference) | `list_agents`, `get_agent` | `…::test_list_agents_and_ids`, `…::test_get_agent_missing_and_found` |
| Create requires id + model + size (six shapes including legacy `model_code`); 409; stripped kwargs to `save_agent`; `ValueError` → 400 | `create_agent` | `…::test_create_agent_requires_id_model_and_brain`, `…::test_create_agent_conflict_success_and_data_layer_rejection` |
| Update key allowlist + strip; legacy `model_code` alone → 400; `ValueError` → 400 | `update_agent` | `…::test_update_agent_fields_strip_and_errors` |
| AC 3 against real sqlite: Kimi + Medium on PUT and POST → 400, row unchanged / not created; Claude Medium accepted | `create_agent` / `update_agent` → `database` | `…::test_kimi_medium_rejected_on_create_and_update_row_unchanged` |
| Delete paths (unchanged, split out of the old CRUD test) | `delete_agent` | `…::test_delete_agent_paths` |
| Task manager SKU + cache threshold from the agent's model + size; unroutable agent (size not offered / unknown model / no model) → blank row + warning | `_enrich_tasks` | `TestEnrichTasks` (revised `test_enrich_tasks_covers_agent_and_cache_branches`; new `test_enrich_tasks_uses_catalog_pricing_for_agent_model`, `test_enrich_tasks_unroutable_agent_leaves_row_blank_and_warns`) |
| Ad hoc resolve: catalog SKU / server / tier / defaults; agent overrides incl. 0; unroutable → 400; whole key map handed to core | `_resolve_adhoc` | `TestAst1880ResolveAdhocCatalogRoute` (replaces `TestAst492ResolveAdhocApiAdmin`), `TestAdhocHelpers::test_adhoc_entities_and_resolve`, `TestApiAdminBranchGaps::test_resolve_adhoc_candidate_and_preview_errors` |
| Ad hoc test route forwards `model_code` / `server_id` / `tier` / temperature / max_tokens / `candidate_api_keys`; no `api_key_override` / `tier_meta` | `adhoc_test` | `TestAst1880ResolveAdhocCatalogRoute::test_adhoc_test_forwards_route_and_key_map_to_core` |
| Key gate: exact messages (no candidate / not found / `Set this candidate's <label> API key …`), key present → None; agentless task → None | `_candidate_dispatch_api_key_error` | `TestBackfillAndCandidateKey::test_candidate_dispatch_api_key_error`, `…::test_candidate_dispatch_api_key_error_agentless_task_needs_no_key` |
| AC 5: missing key → row Invalid + `invalid_reason` + AUTO forced off (warning carries the reason); Run 400 `started: false`, `run_task` not called; `invalid_reason` is `""` when the key is present | `list_dtasks`, `run_dtask` | `TestAst1780EmptyRenderListGatesForceOff` (new `test_list_missing_platform_key_is_invalid_with_reason_and_forces_auto_off`, `test_run_missing_platform_key_400_never_starts`; the two list tests assert `invalid_reason`) |
| AC 8 (route half): `candidate_id` stripped and forwarded, `""` when absent | `session_resume_parse` | `TestAst986SessionResumeParseApi` (4 revised) |
| Revised: stubs follow the two-arg key gate `(candidate_id, task_key)` and the new resolve payload (`server_id`, `tier`, `candidate_api_keys`) | `api_admin.py` routes | `TestDispatchTasks` create / update / scheduler, `TestApiAdminBranchGaps` auto_mode + adhoc_test nodes, `TestAst1394…`, `TestAst1411…`, `TestAst1780…`, `TestAst1791…`, `TestAdhocRoutes`, plus other create-dispatch stubs |
| Retired | — | `test_list_models`, `test_list_brain_settings`, `test_agent_admin_view_branches_strip_and_infer_legacy`, `test_create_agent_validation_and_success` (split into the create / update / delete nodes above), `test_enrich_tasks_uses_deepseek_pricing_when_active_provider_deepseek`, `test_enrich_tasks_unknown_llm_provider_skips_tier_catalog_lookups`, `TestAst492ResolveAdhocApiAdmin` (3) |
| Conftest | `tests/component/core/conftest.py`, `tests/component/ui/conftest.py` | Autouse `_core_default_anthropic_llm_provider` / `_ui_default_anthropic_llm_provider` removed: they patched the deleted `get_active_llm_provider`, which broke ~2800 tests at setup |
| Scope deletion | `src/external/deepseek.py` | `tests/component/external/test_deepseek.py` + `docs/test-bible/external/deepseek.md` removed |

**Product bug returned to the engineer:** `AdminManageCandidates.tsx` `api_key_status` now holds the joined labels (plan Stage 4), but the column renderer still tests `val === "Set"`. Every candidate therefore shows `⚠️ Not set`, even with keys stored. Red test: `test_AdminManageCandidates.test.tsx` › **AST-1880: API Key column lists the labels of servers with a key set**.

**Pre-existing reds outside the manifest** (same on the base tip): `test_api_admin.py` (5: `TestDispatchTasks::test_list_dispatch_tasks_and_keys`, `TestApiAdminBranchGaps::test_dispatch_task_keys_db_row_adds_orphan_key`, `TestAst781…`, `TestAst783…::test_repo_json_revert_invalid_table_key`, `TestAst1214…::test_mailbox_trigger_null_only_and_unsupported_craft_wording`). In `test_api_candidate.py`: `test_list_candidates_and_states` (stale `PROSPECT` assert), and `test_update_merges_data_and_state` (renamed from `…_and_api_key`; `joblist_rubric` artifact → data-layer 400).

**Branch lock:** no AST-1880-changed line or branch of `api_admin.py` / `api_candidate.py` is missing under `test_api_admin.py` + `test_api_candidate.py`. `monitor.py` and `cost_calculator.py` are at 100%.

**Integration:** none.

## QA test manifest (AST-1880)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_cost_calculator_deepseek.py \
  tests/component/utils/test_cost_calculator.py \
  tests/component/data/database/test_timesheets.py::TestBackfillDeepseekAgentTimesheetCosts \
  tests/component/core/test_monitor.py::TestAst1867ProviderBalanceOutage \
  tests/component/utils/test_config.py::TestAst492LlmBrainTierConfig \
  tests/component/utils/test_config.py::TestAst1391DeepseekBigMaxTokensFloor \
  tests/component/utils/test_config.py::TestAst1072ConversationalEnvelopeConfig \
  tests/component/utils/test_config.py::TestAst1073ContactEstelleTurnConfig \
  tests/component/utils/test_config.py::TestAst1877LlmCatalogConfig \
  tests/component/ui/api/test_api_candidate.py::TestSanitizeCandidate \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_non_admin_cannot_create_delete_or_override_state \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_list_rows_carry_per_server_key_flags_only \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_get_returns_sanitized_candidate \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_update_sets_and_clears_api_keys_per_server \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_update_rejects_malformed_api_keys \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_put_two_server_keys_stores_ciphertext_and_get_shows_flags_only \
  tests/component/ui/api/test_api_admin.py::TestAdminConfigAndAgents \
  tests/component/ui/api/test_api_admin.py::TestEnrichTasks \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers \
  tests/component/ui/api/test_api_admin.py::TestAst1880ResolveAdhocCatalogRoute \
  tests/component/ui/api/test_api_admin.py::TestAdhocRoutes \
  tests/component/ui/api/test_api_admin.py::TestBackfillAndCandidateKey \
  tests/component/ui/api/test_api_admin.py::TestAst986SessionResumeParseApi \
  tests/component/ui/api/test_api_admin.py::TestAst1394AdhocTestResponseText \
  tests/component/ui/api/test_api_admin.py::TestAst1411AdhocSevenSegment \
  tests/component/ui/api/test_api_admin.py::TestAst1780EmptyRenderListGatesForceOff \
  tests/component/ui/api/test_api_admin.py::TestAst1791NoPromptValueErrorEmptyRender \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_resolve_adhoc_candidate_and_preview_errors \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_adhoc_test_decodes_encoded_payload \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_adhoc_test_hydrates_encoded_payload_with_entities \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_adhoc_test_skips_decode_without_response_text \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_create_dispatch_task_auto_mode_success \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_update_dispatch_task_score_floor_and_auto_mode_error \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_update_dispatch_task_scored_score_floor_and_auto_mode_success \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_create_dispatch_task_paths \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_update_dispatch_task_paths \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_scheduler_and_run_controls

# Vitest (narrow): the four changed pages
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminManageCandidates.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminSessionResumePaste.test.tsx
```

**Pass criterion:** narrowed pytest green (145) plus narrowed Vitest green. This is not the zero-arg harness. Vitest has exactly **one** red on the publish tip: the ManageCandidates API Key column test (the product bug above), which turns green when the renderer shows the labels. The full `tests/component` baseline diff against the pre-AST-1880 product tip shows zero new failures, apart from the renamed pre-existing `test_update_merges_data_and_state` and one timing flake (`test_intake.py::…::test_background_initiate_failure_writes_assistant_error`, green 3/3 alone and 2/2 as a file).

### AST-1916 · AST-1875 (GET/POST /scheduler/auto_thread_cap)

**Primary manifest:** [`../../core/dispatcher.md`](../../core/dispatcher.md) § AST-1916. Real dispatcher getter/setter behind the routes (no stubs), so GET-after-POST is end-to-end; class autouse `_reset_override` restores `src.core.dispatcher._auto_thread_cap_override`.

| AC | Route | Component tests |
| --- | --- | --- |
| GET payload `{max_auto_threads, default, min, max}` | `GET /api/admin/scheduler/auto_thread_cap` | `tests/component/ui/api/test_api_admin.py::TestAst1916AutoThreadCapApi::test_get_reports_default_and_bounds` |
| 3 POST 1 / 100 → 200 + payload, GET reflects | `POST` same path | `::TestAst1916AutoThreadCapApi::test_post_in_range_returns_payload_and_get_reflects` |
| 3 POST 0 / 101 / `"abc"` / 2.5 / missing key / no body → 400 `error`, prior cap kept | same | `::TestAst1916AutoThreadCapApi::test_post_rejects_and_keeps_prior_cap` |
| 4 no session 401, non-admin 403 (both verbs), cap untouched | both | `::TestAst1916AutoThreadCapApi::test_requires_admin` |

**Broken / obsolete:** none. `TestDispatchTasks::test_scheduler_and_run_controls` (sibling `/scheduler/*` routes) unchanged.

### AST-1938 · AST-1937 (OpenRouter shortlist — agent save respects model-scoped sizes)

**Primary manifest:** **`docs/test-bible/utils/config.md`** § AST-1938. No `api_admin.py` change; the route already validates through the data layer against the catalog.

| Area | Source | Component tests |
| --- | --- | --- |
| AC 4 against real sqlite: PUT `qwen/qwen3-32b` + Little → 200 and re-GET returns both; `gryphe/mythomax-l2-13b` + Medium and `qwen/qwen3-32b` + Big → 400, row unchanged | `update_agent` → `database.update_agent` | `test_api_admin.py::TestAdminConfigAndAgents::test_ast1938_shortlist_model_scoped_sizes_on_put` |
| AC 8: `GET /agents/models` lists 79 ids; shortlist slug served by openrouter; `moonshotai/kimi-k2.6` not a separate id | `list_models` | `…::test_ast1938_models_route_lists_79` |

`test_list_models_is_per_model_brain_size_catalog` (AST-1880) iterates `LLM_MODEL_CONFIG`, so it covers all 79 entries unchanged.

> **AST-1947 / AST-1948:** Frozen record. `test_ast1938_shortlist_model_scoped_sizes_on_put` → `test_ast1947_openrouter_one_size_by_quant_on_put`, and `test_ast1938_models_route_lists_79` → `test_ast1947_models_route_lists_98` (§ AST-1948 below).

### AST-1948 · AST-1946 (admin agent routes: `mode` required, temperature retired)

**Primary manifest:** **`docs/test-bible/core/agent.md`** § AST-1948.

`POST /agents` requires `agent_id`, `model_id`, `brain_setting` and a non-blank string `mode`. Otherwise it returns 400 `agent_id, model_id, brain_setting and mode are required`. `PUT /agents/<id>` returns 400 `mode is required` unless the body has a non-blank string `mode`. The check runs after the 404 check and before any write. Neither route forwards `temperature` or `model_code`. The data layer rejects an unknown mode, which comes back as 400. `GET /agents/models` sizes carry only `order` + `default_max_tokens`. `_enrich_tasks` and `_resolve_adhoc` pass the agent's mode to `resolve_model_brain`, and adhoc `temperature` is `tier["temperature"]`.

| Area | Source | Component tests |
| --- | --- | --- |
| New — AC 7 against real sqlite: PUT `mode: "Creative"` round-trips (PUT body and re-GET show `mode`, with no `temperature` / `model_code` keys). PUT `"Wild"` and PUT without mode → 400, row unchanged. POST `"Wild"` → 400, nothing written | `create_agent` / `update_agent` → `database` | `TestAdminConfigAndAgents::test_ast1948_mode_round_trip_and_rejections` |
| Revised — create needs mode (+3 params: missing, blank, non-string) with the new error string | `create_agent` | `TestAdminConfigAndAgents::test_create_agent_requires_id_model_brain_and_mode` (renamed from `…_requires_id_model_and_brain`; 9 params) |
| Revised — create forwards a stripped `mode` and drops a stray `temperature` | `create_agent` | `…::test_create_agent_conflict_success_and_data_layer_rejection` |
| Revised — PUT with no / blank / non-string mode → `mode is required` (five bodies), no write. A full PUT forwards `mode`, not `temperature` / `model_code` | `update_agent` | `…::test_update_agent_fields_strip_and_errors` |
| Revised — `list_models` sizes have no `default_temperature` | `list_models` | `…::test_list_models_is_per_model_brain_size_catalog` |
| Revised — real-DB size checks send `mode` | routes | `…::test_kimi_medium_rejected_on_create_and_update_row_unchanged` |
| Revised (AST-1947 drift) — each OpenRouter model offers one size, chosen by host quantization: `qwen/qwen3-32b` Medium → 200; qwen Little / Big and mythomax Medium → 400, row unchanged | routes | `…::test_ast1947_openrouter_one_size_by_quant_on_put` (was `test_ast1938_shortlist_model_scoped_sizes_on_put`) |
| Revised (AST-1947 AC 8 / parent AC 11) — `GET /agents/models` = 98 ids; `moonshotai/kimi-k2.6` on openrouter; `kimi-k2.6-openrouter` gone | `list_models` | `…::test_ast1947_models_route_lists_98` (was `test_ast1938_models_route_lists_79`) |
| Revised — task-manager SKU resolves with the agent's mode. A mode-less / `"Wild"` agent blanks its row and warns (no 500) | `_enrich_tasks` | `TestEnrichTasks::test_enrich_tasks_covers_agent_and_cache_branches` · `::test_enrich_tasks_uses_catalog_pricing_for_agent_model` · `::test_enrich_tasks_unroutable_agent_leaves_row_blank_and_warns` (+`no_mode`, `unknown_mode`) |
| Revised — adhoc temperature comes from the mode (Deterministic 0.2 / Creative 0.6, Kimi Big thinking follows mode), a stale row `temperature` is ignored, and the `max_tokens` override still wins. Mode-less / `"Wild"` → 400 | `_resolve_adhoc` | `TestAst1880ResolveAdhocCatalogRoute::test_deepseek_little_uses_catalog_sku_server_tier_and_defaults` · `::test_mode_sets_temperature_and_max_tokens_override_wins` (2; replaces `test_agent_overrides_win_including_zero`, since the row no longer has a temperature override) · `::test_adhoc_test_forwards_route_and_key_map_to_core` · `::test_unroutable_agent_returns_400` (+`no_mode`, `unknown_mode`) |
| Revised — adhoc agent mocks carry `mode` | `_resolve_adhoc` | `TestAdhocHelpers::test_adhoc_entities_and_resolve` · `::test_resolve_adhoc_job_entity_resolves_visible_jd_token` · `TestApiAdminBranchGaps::test_resolve_adhoc_candidate_and_preview_errors` · `TestAst1411AdhocSevenSegment::test_resolve_preview_seven_segment_and_system_fallback` |

**Known window (by design, plan Stage 2):** `AdminAgentPrompts.tsx` sends no `mode` until AST-1949. So on `ftr` between the two merges, UI edits get `400 mode is required` and UI creates get the create error. The frontend tests (`tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx`) are AST-1949's.

**Integration:** none.

### AST-1957 · AST-1953 (admin agent routes take the plain settings; models list drops brain sizes)

Supersedes the agent-route rows of § AST-1880 / § AST-1948 above. `POST /agents` requires only `agent_id` + `model_id` (400 `agent_id and model_id are required`). Create and update pass the seven settings in `AGENT_SETTING_COLUMNS` (`quantization`, `temperature`, `reasoning_effort`, `provider_allow_fallbacks`, `provider_only`, `provider_ignore`, `provider_sort`) exactly as sent: no strip, no route-side checks, and a key that is absent from the body is not passed. Only `model_id` is still stripped. `brain_setting` / `mode` / `model_code` are not read, so on their own they create nothing (create 400) and leave nothing to update (`No updatable fields provided`). `PUT` no longer requires `mode`. The data layer (AST-1955) type-checks, and its `ValueError` comes back as 400. The create response stays `{"created": id}`. `GET /agents/models` = id → `order`, `label`, `server_id`, `server_label`, `default_max_tokens`, with no `brain_sizes`. `_enrich_tasks` and `_resolve_adhoc` call `resolve_agent_settings(model_id, agent)`. The task row drops `brain_setting`. Ad hoc `temperature` = the stored value (0 stays 0, empty → None), and the tier carries `reasoning_effort` plus the OpenRouter `provider` object built from the row. Settings contract: [`../../utils/config.md`](../../utils/config.md) § AST-1955 and [`../../data/database/agents.md`](../../data/database/agents.md) § AST-1955. Page: [`../../frontend/pages.md`](../../frontend/pages.md) § AST-1957.

| Area | Source | Component tests (`test_api_admin.py`) |
| --- | --- | --- |
| New — real sqlite: POST with settings (+ ignored `brain_setting` / `mode`) → GET shows them, fallbacks default true, no retired keys. PUT wrong types (`temperature` str, `provider_only` str, fallbacks str) and a retired `model_id` → 400, row unchanged. PUT `None`s clear and `False` / `"high"` set (PUT body and re-GET). POST `temperature: "hot"` → 400, nothing written | routes → `database` | `TestAdminConfigAndAgents::test_ast1957_settings_round_trip_and_wrong_types_rejected` (replaces `test_kimi_medium_rejected_on_create_and_update_row_unchanged`, `test_ast1947_openrouter_one_size_by_quant_on_put`, `test_ast1948_mode_round_trip_and_rejections`) |
| Revised — `/agents/models` exact flat shape per catalog model, catalog order | `list_models` | `…::test_list_models_is_flat_catalog_with_default_output_budget` (was `…_is_per_model_brain_size_catalog`) |
| Revised — catalog count 101: per-SKU direct ids; `claude` / `deepseek-v4` / `kimi-k2.6-openrouter` absent | `list_models` | `…::test_models_route_lists_whole_catalog` (was `test_ast1947_models_route_lists_98`) |
| Revised — create needs id + model only (6 params, including `legacy_model_code` and `retired_keys_only`) | `create_agent` | `…::test_create_agent_requires_id_and_model` (was `…_requires_id_model_brain_and_mode`, 9 params) |
| Revised — create passes the settings that are present as sent; absent ones not passed; retired keys dropped; 409; `ValueError` → 400 | `create_agent` | `…::test_create_agent_conflict_success_and_data_layer_rejection` |
| Revised — PUT: retired / unknown keys alone → `No updatable fields provided`; content-only PUT goes through (no mode gate); full PUT strips `model_id` only and forwards all seven settings, `None` included; `ValueError` → 400 | `update_agent` | `…::test_update_agent_fields_strip_and_errors` |
| Revised — list / get pass-through mocks carry settings | `list_agents` / `get_agent` | `…::test_list_agents_and_ids` · `…::test_get_agent_missing_and_found` |
| Revised — task-manager SKU via `resolve_agent_settings`; row has no `brain_setting`; unroutable = retired direct id / unknown / no model (blank row + warning) | `_enrich_tasks` | `TestEnrichTasks::test_enrich_tasks_covers_agent_and_cache_branches` · `::test_enrich_tasks_uses_catalog_pricing_for_agent_model` · `::test_enrich_tasks_unroutable_agent_leaves_row_blank_and_warns` (3 params; `size_not_offered` / `no_mode` / `unknown_mode` retired, `retired_direct_id` new) |
| Revised — ad hoc: `deepseek-v4-flash` defaults (temperature None, model `default_max_tokens`); temperature as stored (0 / 0.6 / None) and effort in the tier, no `thinking` key, `max_tokens` override wins; unroutable → 400 | `_resolve_adhoc` | `TestAst1880ResolveAdhocCatalogRoute::test_deepseek_flash_uses_catalog_sku_server_tier_and_defaults` (was `…_deepseek_little_…`) · `::test_temperature_as_stored_and_max_tokens_override_wins` (3; was `test_mode_sets_temperature_…`, 2) · `::test_adhoc_test_forwards_route_and_key_map_to_core` · `::test_unroutable_agent_returns_400` (4 params) |
| New — ad hoc on OpenRouter: the row's quantization / fallbacks / only / sort become `tier["provider"]` (empty `provider_ignore` omitted) | `_resolve_adhoc` | `TestAst1880ResolveAdhocCatalogRoute::test_openrouter_agent_row_settings_become_the_provider_object` |
| Revised — ad hoc agent mocks on `claude-haiku-4-5`, no `brain_setting` / `mode` | `_resolve_adhoc` | `TestAdhocHelpers::test_adhoc_entities_and_resolve` · `::test_resolve_adhoc_job_entity_resolves_visible_jd_token` · `TestApiAdminBranchGaps::test_resolve_adhoc_candidate_and_preview_errors` · `TestAst1411AdhocSevenSegment` `_stub_agent` |

**Sequencing:** `api_admin.py` imports `src.core.agent`, which still imports `resolve_model_brain` until **AST-1956** lands on `ftr`. On this sub, `test_api_admin.py` therefore errors at collection (`ImportError`), the same as AST-1955's `tests/component/core/`. The revisions were verified locally with a throwaway stub for that one import: 227 passed, plus 5 reds that fail identically on `origin/tests` (other epics: `TestAst781ListDtasksRetiredEntityType::test_list_dtasks_legacy_board_search_row_returns_zero_available_count`, `TestDispatchTasks::test_list_dispatch_tasks_and_keys`, `TestApiAdminBranchGaps::test_dispatch_task_keys_db_row_adds_orphan_key`, `TestAst783RepoJsonApi::test_repo_json_revert_invalid_table_key`, `TestAst1214AdminCatalogAlphabeticalWritable::test_mailbox_trigger_null_only_and_unsupported_craft_wording`). They run for real on `ftr` once AST-1956 is merged.

**Integration:** none. No scenario touches agent settings or `/agents/models`.

### AST-1978 · AST-1977 (Manage Tasks RSC column — `response_schema_count`)

**Parent:** [AST-1977 — Indicate if {$RESPONSE_SCHEMA} is used](https://linear.app/astralcareermatch/issue/AST-1977). **Publish:** `origin/sub/AST-1977/AST-1978-rsc-column`.

`_enrich_tasks` serves one new integer per row, `response_schema_count`. It counts the raw (pre-`resolve_tokens`) `{$RESPONSE_SCHEMA}` occurrences across the effective system block (task `system_prompt` when non-blank after `.strip()`, otherwise agent `content`), `cache_prompt`, `cache_prompt_b`–`_d`, `nocache_prompt`, and `user_prompt`. The token is the module-level `_RESPONSE_SCHEMA_TOKEN`, which an import-time assert ties to `get_tokens()`. `AdminTaskPrompts.tsx` renders it in a right-aligned **RSC** column directly left of **System**. No other row field changes.

| AC | Source | Component tests |
| --- | --- | --- |
| 1 int field on every row (including no task / no agent → `0`) | `_enrich_tasks` | `test_api_admin.py::TestAst1978ResponseSchemaCount::test_missing_rows_and_other_tokens` (4 params: `no_task_no_agent`, `agent_only`, `task_without_agent`, `other_tokens_only`) |
| 2 raw count summed across seven segments (8 total); agent content ignored when `system_prompt` non-blank; `resolve_tokens` / `resolved_task_system` mocked to substitute the token away | `_enrich_tasks` | `…::test_sums_raw_token_across_all_seven_segments` |
| 3 blank system prompt → agent content counted (`1`) | `_enrich_tasks` | `…::test_blank_system_prompt_falls_back_to_agent_content` (3 params: `empty`, `whitespace`, `none`) |
| 4 `GET /api/admin/tasks` same count with and without `?candidate_id=` | `list_tasks` → `_enrich_tasks` | `…::test_route_serves_same_count_with_and_without_candidate` |
| 5 header order `Model \| RSC \| System \| Base Cache`; RSC right-aligned; cells `0` and `2` (never blank) | `pages/AdminTaskPrompts.tsx` | `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx` › **`AST-1978 RSC column > header order is Model \| RSC \| System \| Base Cache and cells show served counts`** (fixtures gain `response_schema_count: 0` / `2`) |
| 6 no client-side counting | page | grep (manifest item 3) |
| 7 no bare literal inside `_enrich_tasks` | `api_admin.py` | grep (manifest item 3) |

**Broken / obsolete:** none. There are no exact-key row assertions, `TestTaskRoutes::test_list_tasks_and_tokens` stubs `_enrich_tasks`, and `AdminAnthropicAdHoc` ignores the extra field. The five known cross-epic reds listed under § AST-1957 above still fail identically with and without this ticket. They are not in this manifest.

**Integration:** none. No scenario reads `/api/admin/tasks`.

## QA test manifest

1. **Python (required, all green):**

```bash
.venv/bin/python -m pytest tests/component/ui/api/test_api_admin.py -q \
  -k "Ast1978 or EnrichTasks or TaskRoutes or Ast1412 or test_enrich_tasks_agent_only_system_prompt"
```

2. **Vitest (required, all green — §6c routed page):**

```bash
cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx
```

3. **AC 6 / AC 7 greps:** `grep -n "RESPONSE_SCHEMA" src/ui/frontend/src/pages/AdminTaskPrompts.tsx` prints nothing. `sed -n '/^def _enrich_tasks/,/^def /p' src/ui/api/api_admin.py | grep -nE "\"\{\\\$RESPONSE_SCHEMA\}\"|\"RESPONSE_SCHEMA\""` prints nothing.

4. **Build / import:** item 1 collects without error (it imports `api_admin`, so the import-time `RESPONSE_SCHEMA in get_tokens()` assert holds). In `src/ui/frontend`, `npm run build` exits 0.

**Pass criterion:** items 1–4 hold. Narrowed runs, not the zero-arg harness.

**Bible shasum (after publish):** `git show origin/sub/AST-1977/AST-1978-rsc-column:docs/test-bible/ui/api/api_admin.md | shasum`

### AST-2006 · AST-2000 (bug — runtime empty-token guard)

**Parent:** [AST-1986](https://linear.app/astralcareermatch/issue/AST-1986) (orphaned mini-parent). **Product:** [AST-2000](https://linear.app/astralcareermatch/issue/AST-2000); canon carve-out [AST-2005](https://linear.app/astralcareermatch/issue/AST-2005) (`patt.task.dispatch-retry`). **Publish:** `origin/sub/AST-1986/AST-2006-empty-token-guard-tests`. `_enrich_tasks` resolves with `warn_on_empty=False` (token-count probe, not a model call) → zero `resolved to empty` WARNINGs; counts unchanged. Admin preview keeps default warnings.

| Area | Source | Component tests |
| --- | --- | --- |
| Real resolvers, candidate + no job, `source: job` tokens → zero `resolved to empty`; `system_prompt_tokens > 0` | `_enrich_tasks` | **`TestAst2006EnrichTasksProbeSilent::test_enrich_tasks_job_tokens_without_job_are_silent`** |
| Control: preview resolution still warns (2 job tokens) | `preview_task` → `preview_task_prompt` → `agent.preview_prompt` | **`…::test_preview_resolution_still_warns`** |

**Broken / obsolete:** none — existing `TestEnrichTasks` stubs the resolvers.

Manifest: **`docs/test-bible/core/agent.md`** § AST-2006.

### AST-2025 · AST-2022 (`fetch_relative_jd` in the Scheduled Actions picker — AC6)

**New:** `TestAst2025FetchRelativeJdDispatchTaskKey::test_picker_lists_fetch_relative_jd_job_relative_job_link` — `GET /api/admin/dispatch_tasks/task_keys` lists `fetch_relative_jd` (agent_task catalog only, no dispatch row) as `entity_type: "job"`, `trigger_state: "RELATIVE_JOB_LINK"`. Green pre-AST-2025 too (binding landed in AST-2024) — regression guard. Primary manifest: **`docs/test-bible/core/gazer.md`** § AST-2025.

### AST-2091 · AST-2013 (fix lane — block Auto/Run on duplicate or empty rubric)

**Parent:** AST-2013 (orphaned mini-parent off `origin/dev`). **Publish:** `origin/sub/AST-2013/AST-2091-rubric-dup-dispatch-gate`. Plan: `docs/features/dispatcher/ast-1780-list-enrich-auto-run-gates-force-auto-off.md` § Bug: AST-2091. Primary manifest lives here; component pointers in `core/candidate.md` and `core/dispatcher.md`.

| Area | Source | Component tests |
| --- | --- | --- |
| New — list: duplicate / empty rubric → `empty_render` true, `invalid_reason` = rubric reason, AUTO forced off + WARNING (Repro 1 / 4) | `list_dtasks` | `TestAst2091RubricDispatchGate::test_list_bad_rubric_invalid_and_forces_auto_off` |
| New — list precedence key → rubric → tokens; `empty_tokens` still rides | `list_dtasks` | `…::test_list_precedence_key_then_rubric_then_tokens` |
| Guard — craft / non-rubric rows unaffected by an empty rubric | `list_dtasks` | `…::test_list_craft_and_non_rubric_rows_unaffected_by_empty_rubric` |
| New — AUTO-on create / update → 400 with rubric reason, no write | `create_dtask`, `update_dtask` | `…::test_create_auto_on_bad_rubric_400`, `…::test_put_auto_on_bad_rubric_400` |
| New — Run → 400 `started: false`, rubric outranks tokens (Repro 2) | `run_dtask` | `…::test_run_bad_rubric_400_never_starts` |
| Guard — key reason still outranks rubric on Run (AST-1880 holds) | `run_dtask` | `…::test_run_key_error_outranks_rubric` |

Tests run the **real** `rubric_dispatch_error` behind a stubbed `src.data.database.list_rubric_vectors` (plan Repro fixture: somerset `grade_do` = `TP,TP,SA`; `empty_cand` = `[]`).

**Broken by the fix (stubbed this pass, `rubric_dispatch_error → None`, `raising=False`):** `TestAst1780EmptyRenderListGatesForceOff` (class autouse — 5 tests on `qualify_job_listings` / `c1` read an empty rubric); `TestDispatchTasks::test_scheduler_and_run_controls`; `TestApiAdminBranchGaps::test_create_dispatch_task_auto_mode_success`; `…::test_update_dispatch_task_scored_score_floor_and_auto_mode_success`. Found by running both suites against a scratch apply of the plan's Proposed change (reverted, never committed). `test_dispatcher.py` needed **no** sweep — existing `run_task` cases use `evaluate_jd`, whose embedded QC/GC merge is never empty.

**Pre-existing reds (not AST-2091, not in manifest):** on the dev-based sub, 17 in `test_api_admin.py` / `test_dispatcher.py` (`TestCircuitBreaker` signature, `TestAst841DispatchTerminalLogging`, retry-state lists, repo-JSON wording, …) + 18 in `test_candidate.py` — identical set before and after the scratch fix. On the `tests` tip `test_candidate.py` fails **collection** (`RESUME_STRUCTURE_BODY_FORMAT_DETAILS` — AST-2081 tests ahead of `origin/dev`); it collects on the sub.

**Integration:** none (no `tests/integration/` scenario drives Scheduled Actions gates).

## QA test manifest

1. **[bug-repro] admin gates:** `tests/component/ui/api/test_api_admin.py::TestAst2091RubricDispatchGate`
2. **[bug-repro] run_task gate:** `tests/component/core/test_dispatcher.py::TestAst2091RunTaskRubricGate`
3. **[bug-repro] helper:** `tests/component/core/test_candidate.py::TestAst2091RubricDispatchError`
4. **Regression (swept, green pre- and post-fix):** `test_api_admin.py::TestAst1780EmptyRenderListGatesForceOff`, `…::TestDispatchTasks::test_scheduler_and_run_controls`, `…::TestApiAdminBranchGaps::test_create_dispatch_task_auto_mode_success`, `…::TestApiAdminBranchGaps::test_update_dispatch_task_scored_score_floor_and_auto_mode_success`
5. **Branch locks:** `candidate.py`, `api_admin.py`, `dispatcher.py` stay 100% — new branches covered by items 1–3 (incl. non-dict criterion skip).

**Pass criterion:** items 1–3 red on the pre-fix tree (verified on the sub base: 23 nodes — 11 admin/dispatcher red on assertion, 12 helper red on missing `rubric_dispatch_error`); all green after make-fix (verified against a scratch apply of the plan); item 4 green throughout.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAst2091RubricDispatchGate \
  tests/component/core/test_dispatcher.py::TestAst2091RunTaskRubricGate \
  tests/component/core/test_candidate.py::TestAst2091RubricDispatchError \
  tests/component/ui/api/test_api_admin.py::TestAst1780EmptyRenderListGatesForceOff \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_scheduler_and_run_controls \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_create_dispatch_task_auto_mode_success \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_update_dispatch_task_scored_score_floor_and_auto_mode_success
```

### AST-2134 · AST-2130 (ad-hoc preview on telescope_data)

`_build_adhoc_live_content` company branch resolves `TELESCOPE_DATA_CONFIG["company_data_id_keys"]` via `gazer.resolve_telescope_value` (legacy text passes through); `website_content` page text is stripped in the join. Job branch reads `tracker.compose_job_description` (single-entity falls back to `raw_job_listing`; `qualify_meteorite` CONTENT lines); LIKE's company context resolves `website_content` ids.

**New:** **`TestAst2134AdhocPreviewTelescope`** (6; real `telescope_data` rows on ui `sqlite_in_memory`): AC6 `prefilter_company` / `select_job_page` / `gaze` byte-identical for a legacy text blob vs the same content as ids (incl. a raw unstripped fresh capture), website_content fallback, gone capture → empty, composed JD in job previews, LIKE context. Manifest: [`../../core/roster.md`](../../core/roster.md) § AST-2134.

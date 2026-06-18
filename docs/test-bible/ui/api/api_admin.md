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


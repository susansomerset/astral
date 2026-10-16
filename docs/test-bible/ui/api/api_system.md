# Api System

**Test module:** `tests/component/ui/api/test_api_system.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_system.py` | `tests/component/ui/api/test_api_system.py` | yes |

Public `GET /api/auth_passthrough` (AST-1440): **`docs/test-bible/ui/auth.md`** § AST-1440.

---

### AST-792

`GET /api/deploy_status` imports **`get_deploy_status_payload`** from **`src.core.deploy_status`** (AST-792 filter). **`TestDeployStatus`** monkeypatches **`system_mod.get_deploy_status_payload`** — route contract unchanged (`merge_tickets` key when present).

| Behavior | Tests |
| --- | --- |
| Admin payload incl. `merge_tickets` | `TestDeployStatus::test_admin_returns_payload` |
| Env omitted when unset | `TestDeployStatus::test_admin_omits_environment_when_unset` |
| Uptime samples via utils base builder | `TestDeployStatus::test_admin_uptime_format_samples_via_payload_builder` |

### AST-970 · AST-871

Primary manifest: **`docs/test-bible/core/candidate.md`** § AST-970. **`_is_at_or_past`** uses **`progress_rank`** (INACTIVE/DELETED never unlock) — revised **`TestSystemNavHelpers`**.

### AST-1253 · AST-1243

**Publish:** `origin/sub/AST-1243/AST-1253-generate-regenerate-handoff`.

`GET /api/state_ui_manifest` merges `artifacts_chain_task_keys` / `artifacts_chain_hop_labels` / `artifacts_chain_artifact_keys` from core; walk failure → empty arrays (rest of manifest 200).

| Area | Source | Component tests |
| --- | --- | --- |
| Chain fields + degrade | `src/ui/api/api_system.py` | **`TestAst1253StateUiManifestChainFields`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_system.py::TestAst1253StateUiManifestChainFields \
  -q
```

### AST-1375 · AST-1371

**Publish:** `origin/sub/AST-1371/AST-1375-regenerate-affordance-unsupported-experience`.

`GET /api/state_ui_manifest` includes `candidate.artifact_generate_inflight_hide_states` from `build_state_ui_manifest()` (rides with existing candidate keys; chain merge unchanged). Primary UI: **`docs/test-bible/frontend/components.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Inflight hide key on manifest | `src/ui/api/api_system.py` (via config build) | **`TestAst1375InflightHideStatesManifest`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_system.py::TestAst1375InflightHideStatesManifest \
  -q
```

### AST-1016 · AST-952

`GET /api/ui_config` includes `preamble` from `PREAMBLE_CONFIG`. Primary: **`docs/test-bible/utils/config.md`** § AST-1016 — **`TestSystemAuthRoutes::test_ui_config_includes_preamble_config`**.

### AST-1149 · AST-1145

`GET /api/ui_config` includes `cover_from_block` (`default_template`, `authoring_help`, `session_authoring_help`) from `COVER_FROM_BLOCK_CONFIG`. Primary config: **`docs/test-bible/utils/config.md`** § AST-1149. Pages: **`docs/test-bible/frontend/pages.md`**.

| Behavior | Tests |
| --- | --- |
| ui_config cover_from_block slice | `TestSystemAuthRoutes::test_ui_config_includes_cover_from_block` |

### AST-1351 · AST-1345

**Publish:** `origin/sub/AST-1345/AST-1351-experience-array-ui-render-print-parity`.

`GET /api/ui_config` (system blueprint) exposes `experience_job_ui_fields` + `unsupported_resume_structure_message` from `BUILD_CONFIG`. Primary UI: **`docs/test-bible/frontend/components.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| ui_config field spine + message | `src/ui/api/api_system.py` | **`TestAst1351ExperienceJobUiConfig`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_system.py::TestAst1351ExperienceJobUiConfig \
  -q
```

### AST-1373 · AST-1372

**Publish:** `origin/sub/AST-1372/AST-1373-auth-config-stytch-session-rules`.

Open `GET /api/auth_session_policy` returns non-secret session duration + extend cadence (no Bearer). Primary config helper: **`docs/test-bible/utils/config.md`** § AST-1373.

| Area | Source | Component tests |
| --- | --- | --- |
| Public policy route | `src/ui/api/api_system.py` | **`TestAst1373AuthSessionPolicyRoute`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_system.py::TestAst1373AuthSessionPolicyRoute \
  -q
```

### AST-1386 · AST-1370

**Publish:** `origin/sub/AST-1370/AST-1386-three-segment-admin-nav`.

`_nav_config_for_user` omits every `admin_only` group via `nav_admin_only_group_labels()` (Operations / Admin / Tools). Admin response includes those three segments after Candidate; paste item labels **Resume Paste** / **Cover Letter Paste**; `admin_only` never appears in JSON. Primary config: **`docs/test-bible/utils/config.md`** § AST-1386.

| Area | Source | Component tests |
| --- | --- | --- |
| Admin three segments + paste labels | `src/ui/api/api_system.py` | **`TestSystemAuthRoutes::test_nav_config_three_admin_segments_for_admin`** |
| Non-admin omit all admin_only | same | **`TestSystemAuthRoutes::test_nav_config_omits_admin_group_for_non_admin`** |
| Agent Ad Hoc under Tools (revised) | same | **`TestSystemAuthRoutes::test_nav_config_admin_agent_ad_hoc_label`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_nav_config_three_admin_segments_for_admin \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_nav_config_omits_admin_group_for_non_admin \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_nav_config_admin_agent_ad_hoc_label \
  -q
```

### AST-1449 · AST-1444

**Parent:** [AST-1444 — Remove navigation filter for selected candidate](https://linear.app/astralcareermatch/issue/AST-1444/remove-navigation-filter-for-selected-candidate). **Publish:** `origin/sub/AST-1444/AST-1449-ungate-candidate-facing-nav-by-state`.

`/api/nav_config` no longer skips Jobs / Companies / Artifacts on group-level `visible`. Those groups are present for `NEW_CANDIDATE` and `RESUME_READY`. Applied / Responded stay `"enabled": False`. Non-admin omit of Operations / Admin / Tools unchanged. `NAV_CONFIG` drops the `visible` keys (config test revision). Code Rules §2.1 NAV_CONFIG bullet matches. No page-file product diff — §6c routed-page rule N/A. Sibling chrome line is AST-1450.

| Area | Source | Component tests |
| --- | --- | --- |
| HTTP: early-state candidate-facing groups | `src/ui/api/api_system.py` | **`TestSystemAuthRoutes::test_nav_config_early_state_keeps_candidate_facing_groups`** |
| Resolver: groups present; stubs disabled | same | **`TestSystemNavHelpers::test_resolve_nav_keeps_candidate_facing_groups_and_stubs`** (replaces `test_resolve_nav_honors_visible_and_enabled_gates`) |
| Item-level string `enabled` still gates | same | **`TestSystemNavHelpers::test_resolve_nav_uses_string_enabled_gate`** (existing) |
| Non-admin omit admin_only | same | **`TestSystemAuthRoutes::test_nav_config_omits_admin_group_for_non_admin`** (existing) |
| NAV_CONFIG has no group `visible` | `src/utils/config.py` | revised **`TestAst970CandidateStateRegistry::test_nav_and_gen_states_use_new_vocab`** |
| Docs contract | `docs/ASTRAL_CODE_RULES.md` | grep §2.1 NAV_CONFIG — `Group-level candidate-state \`visible\` is not used` |

**Broken / obsolete:** `test_resolve_nav_honors_visible_and_enabled_gates` (`Jobs not in labels` at `RESUME_READY`); AST-970 `jobs["visible"] == "ACTIVE_SEARCH"` / companies / artifacts asserts; integration `test_nav_config_reflects_seeded_candidate_state` expected Jobs absent for `NEW_CANDIDATE`.

**Integration (revised existing):** `tests/integration/scenarios/test_candidate_nav_api.py` — `NEW_CANDIDATE` still returns Jobs / Companies / Artifacts / Candidate. Map: [`integration/README.md`](../../integration/README.md). Do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_nav_config_early_state_keeps_candidate_facing_groups \
  tests/component/ui/api/test_api_system.py::TestSystemNavHelpers::test_resolve_nav_keeps_candidate_facing_groups_and_stubs \
  tests/component/ui/api/test_api_system.py::TestSystemNavHelpers::test_resolve_nav_uses_string_enabled_gate \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_nav_config_omits_admin_group_for_non_admin \
  tests/component/utils/test_config.py::TestAst970CandidateStateRegistry::test_nav_and_gen_states_use_new_vocab \
  -q
./scripts/testing/run_integration_tests.sh \
  tests/integration/scenarios/test_candidate_nav_api.py \
  -q
```

**Pass criterion:** pytest green on the narrowed component + existing integration scenario — not zero-arg harness / branch-lock gate.


### AST-1550 · AST-1541

**Parent:** [AST-1541](https://linear.app/astralcareermatch/issue/AST-1541/add-discussion-tab-to-recommended-job-modal). **Publish:** `origin/sub/AST-1541/AST-1550-discussion-tab-config-story-task-name`.

`GET /api/state_ui_manifest` attaches `jobs.recommended.report_discussion_sections` (ordered `{section_id, nav_label, default_expanded: false}` from hop walk + live `task_name`; blank name → `task_key`). Walk failure → `[]` (rest of manifest 200). Top-tab Discussion rides `report_top_tabs` from config. Primary hop walk: **`docs/test-bible/utils/config.md`** § AST-1550. Story enrichment: **`docs/test-bible/core/agent.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Sections + labels + soft-fail (length = hop walk) | `src/ui/api/api_system.py` | **`TestAst1550ReportDiscussionSections`** |

**Broken / obsolete:** none for this endpoint (AST-1253 chain fields unchanged).

**Integration:** none — do not invent.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_system.py::TestAst1550ReportDiscussionSections \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.


### AST-1691 · AST-1685

**Publish:** `origin/sub/AST-1685/AST-1691-meteorite-lookup-report-config-api`.

`GET /api/state_ui_manifest` attaches `jobs.recommended.report_meteorite_sections` from `JOBS_RECOMMENDED_REPORT_METEORITE_SECTIONS`. Top-tab Meteorite rides `report_top_tabs` from config. Primary: **`docs/test-bible/data/database/meteorites.md`** § AST-1691.

| Area | Source | Component tests |
| --- | --- | --- |
| Sections + last-tab meteorite | `src/ui/api/api_system.py` | **`TestAst1691ReportMeteoriteSections`** |

**Broken / obsolete:** AST-1550 Discussion last-tab assert — meteorite is now last; Discussion still present.

**Integration:** none — do not invent.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_system.py::TestAst1691ReportMeteoriteSections \
  tests/component/ui/api/test_api_system.py::TestAst1550ReportDiscussionSections \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.


### AST-1808 · AST-1806 (explicit _RETRY registry purge)

**Parent:** [AST-1804](https://linear.app/astralcareermatch/issue/AST-1804). **Publish:** `origin/sub/AST-1804/AST-1808-purge-retry-tests`. Product: **AST-1806** (18 `*_RETRY` registry keys + declared retry priors deleted; retries are implicit substates, priors derived by `state_prior_states`). Green only once AST-1806 is on the tree (ftr `2a419fbf`+); pre-purge `65e3ca6f` is red.

| Area | Source | Component tests |
| --- | --- | --- |
| `_progress_rank(REQUESTED_*_RETRY)` == base (nav gating stays open); `NOPE_RETRY` → -1 | `src/ui/api/api_system.py` | **`TestAst1808ProgressRankRetry`** |

**Broken / obsolete:** none.

**Integration:** none — do not invent.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_system.py::TestAst1808ProgressRankRetry \
  -q
```

---

### AST-1974 · AST-1970

`_get_job_counts` emits six paths: Ready, Review, Applied, Processing (exclude list − below-floor), Skipped (+ below-floor), Meteorites (`len(list_meteorites_for_candidate)`).

**New:** `TestSystemNavHelpers::test_job_counts_six_paths_with_floor_arithmetic`. Real-DB count == list length: `test_api_jobs.py::TestAst1974JobsPartitionRealDb::test_nav_counts_match_list_lengths`.

**Revised:** `TestSystemAuthRoutes::test_nav_config_uses_candidate_state` (`/jobs/ready`); `TestSystemNavHelpers::test_resolve_nav_keeps_candidate_facing_groups_and_stubs` (Responded retired; all six Jobs items enabled — also clears the stale pre-AST-1479 Applied-disabled assert).

**Integration (revised existing):** `tests/integration/scenarios/test_candidate_nav_api.py` — `/jobs/ready` enabled + every Jobs item carries `count`. Map: [`integration/README.md`](../../integration/README.md).

Manifest: [`api_jobs.md`](api_jobs.md) § AST-1974 items 3 + 5.

**AST-2047 (pointer):** `TestSystemAuthRoutes::test_ui_config_serves_theme_registry` — `ui_config` serves `themes` + `default_theme` via the `UI_CONFIG` spread (keys compared as a set: Flask sorts JSON keys). Manifest: [`../../frontend/pages.md`](../../frontend/pages.md) § AST-2047.

**AST-2129 (pointer):** `test_ui_config_serves_theme_registry` revised to pin the exact four-entry `themes` dict (Dark, Light, Shapes - Light, Shapes - Dark, all selectable). Manifest: [`../../frontend/root.md`](../../frontend/root.md) § AST-2129.

### AST-2230 · AST-2225 (nav stage gates + recent/attention)

**Parent:** [AST-2225](https://linear.app/astralcareermatch/issue/AST-2225). **Publish:** `origin/sub/AST-2225/AST-2230-stage-gated-nav`. Config map: [`../../utils/config.md`](../../utils/config.md) § AST-2230.

`_nav_stage` via `candidate_stage`; int min-stage item gates; stage 0 omits facing groups; group `recent` from `NAV_GROUP_RECENT_DEFAULTS`; Profile `attention` from `incomplete_profile`. No progress `logger.info` on GET.

| Area | Component tests |
| --- | --- |
| Criteria disabled below stage 4; stage-0 omit; recent/attention; dropped labels | new **`TestAst2230StageGatedNavApi`** |
| HTTP facing order / Job Opportunities counts; admin segments with live candidate | revised **`TestSystemAuthRoutes`** nav cases |
| `_nav_stage` terminals→0; facing resolve + int gate | revised **`TestSystemNavHelpers`** (retired `_is_at_or_past` / string gate) |
| RETRY inherits base stage | revised **`TestAst1808ProgressRankRetry`** |

**Broken / obsolete:** `_progress_rank` / `_is_at_or_past` tests; Jobs/Companies/Artifacts payload asserts; string `enabled` gate test.

**Integration (harness revise):** `tests/integration/conftest.py` resets `_artifact_schema_ensured` so tmp SQLite creates `artifact` when `nav_config` → `get_candidate` hydrates `base_resume`. Map: [`integration/README.md`](../../integration/README.md).

## QA test manifest — AST-2230

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst2230StageGatedNavConfig \
  tests/component/utils/test_config.py::TestAst970CandidateStateRegistry::test_nav_and_gen_states_use_new_vocab \
  tests/component/utils/test_config.py::TestAst1386ThreeSegmentAdminNav \
  tests/component/utils/test_config.py::TestAst1479AppliedJobStatesAndNav \
  tests/component/utils/test_config.py::TestAst1495MeteoriteCompaniesNav \
  tests/component/utils/test_config.py::TestAst1749JobsMeteoritesNav \
  tests/component/utils/test_config.py::TestAst1974JobsListPartition::test_nav_jobs_items_exact \
  tests/component/ui/api/test_api_system.py::TestAst2230StageGatedNavApi \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes \
  tests/component/ui/api/test_api_system.py::TestSystemNavHelpers::test_nav_stage_compares_registry_stages \
  tests/component/ui/api/test_api_system.py::TestSystemNavHelpers::test_resolve_nav_keeps_candidate_facing_groups_and_stubs \
  tests/component/ui/api/test_api_system.py::TestSystemNavHelpers::test_resolve_nav_uses_int_stage_enabled_gate \
  tests/component/ui/api/test_api_system.py::TestAst1808ProgressRankRetry \
  tests/component/core/test_candidate.py::TestAst1253RequestedArtifactsHandoff::test_walk_helpers_order_labels_and_rubric_keys \
  tests/component/ui/api/test_api_jobs.py::TestAst1974JobsPartitionRealDb::test_nav_counts_match_list_lengths \
  tests/integration/scenarios/test_candidate_nav_api.py \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobsHomeRedirect.test.tsx
```

**Pass criterion:** Python narrowed green; Vitest JobsHomeRedirect green. Not the zero-arg harness.

**Bible shasum (after publish):** `git show origin/sub/AST-2225/AST-2230-stage-gated-nav:docs/test-bible/ui/api/api_system.md | shasum`; same for `utils/config.md`, `core/candidate.md`, `frontend/components.md`, `integration/README.md`.

### AST-2261 · AST-2257 (criteria nav counts)

**Publish:** `origin/sub/AST-2257/AST-2261-version-scoped-grade-rollup`. Primary: [`../../core/candidate.md`](../../core/candidate.md) § AST-2261.

`_get_criteria_nav_counts` sets `count` on the seven criteria paths to `len(rubric_criteria_for_task)` for that path's owner, including `0`. `/artifacts/company_search_terms` is not in the map, so Company Discovery Terms has no `count` key. Empty candidate id returns `{}`. Exceptions are swallowed. Job and company badges are unchanged.

Company Gazing Criteria lives under the Company group, not Criteria. Do the Job Criteria is the Criteria item whose count is the current-vector length.

| Area | Component tests |
| --- | --- |
| Empty id and swallowed error | **`TestAst2261CriteriaNavCounts::test_empty_candidate_and_swallowed_error`** |
| Seven paths (Do the Job = 2, the other six = 0); terms uncounted; Ready badge still 2 | **`…::test_seven_paths_count_current_vectors_terms_stay_uncounted`** |

**Broken / obsolete:** none. Manifest command: [`../../core/candidate.md`](../../core/candidate.md) § QA test manifest — AST-2261.

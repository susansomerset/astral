# Api System

**Test module:** `tests/component/ui/api/test_api_system.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_system.py` | `tests/component/ui/api/test_api_system.py` | yes |

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


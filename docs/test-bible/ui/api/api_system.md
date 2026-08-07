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

### AST-1016 · AST-952

`GET /api/ui_config` includes `preamble` from `PREAMBLE_CONFIG`. Primary: **`docs/test-bible/utils/config.md`** § AST-1016 — **`TestSystemAuthRoutes::test_ui_config_includes_preamble_config`**.

### AST-1149 · AST-1145

`GET /api/ui_config` includes `cover_from_block` (`default_template`, `authoring_help`, `session_authoring_help`) from `COVER_FROM_BLOCK_CONFIG`. Primary config: **`docs/test-bible/utils/config.md`** § AST-1149. Pages: **`docs/test-bible/frontend/pages.md`**.

| Behavior | Tests |
| --- | --- |
| ui_config cover_from_block slice | `TestSystemAuthRoutes::test_ui_config_includes_cover_from_block` |

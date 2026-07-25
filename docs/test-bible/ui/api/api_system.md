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

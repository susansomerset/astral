# Deploy Status

**Test module:** `tests/component/utils/test_deploy_status.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/utils/deploy_status.py` | `tests/component/utils/test_deploy_status.py` | no |
| `src/core/deploy_status.py` | `tests/component/core/test_deploy_status.py` | no |

---

### AST-667 · AST-646

**`get_deploy_label()`** (AST-667): stripped non-empty `ASTRAL_DEPLOY_ENV` verbatim or `"Astral"` when unset/whitespace — used by AUTO alert subject prefix in monitor (AST-660 child).

| Behavior | Tests |
| --- | --- |
| Env set → raw label | `TestGetDeployLabel::test_returns_env_when_set` |
| Unset / whitespace → `Astral` | `TestGetDeployLabel::test_returns_astral_when_unset`, `test_returns_astral_when_whitespace_only` |

---

### AST-679

**AST-658 child:** Remove commit tip from `get_deploy_status_payload()` — no git subprocess; payload is `uptime`, `uptime_seconds`, and optional `environment` only (no `commit_short` / `commit_message` keys).

| Behavior | Tests |
| --- | --- |
| Uptime without env | `TestGetDeployStatusPayload::test_includes_uptime_without_environment` — no commit keys; `"environment" not in payload`; `merge_tickets: []` with **`read_merge_ticket_log` monkeypatched empty** (AST-693 seeded log on disk) |
| Uptime + env when set | `TestGetDeployStatusPayload::test_includes_environment_when_set` — `staging`, `1h1m`; no commit keys; `merge_tickets: []` with **`read_merge_ticket_log` monkeypatched empty** |

---

### AST-681

**Historical:** pre-AST-792, utils `get_deploy_status_payload()` assembled `merge_tickets`. **AST-792** moved full payload + Linear filter to **`src/core/deploy_status.py`**; utils returns uptime/env only. Pure helpers `merge_tickets_recent_first` / `filter_merge_tickets_by_state` remain in utils.

| Behavior | Tests (current) |
| --- | --- |
| API route includes key | `TestDeployStatus::test_admin_returns_payload`, `test_admin_omits_environment_when_unset` in `test_api_system.py` |

---

### AST-792

**Utils layer:** base payload (no `merge_tickets` key); pure filter/order helpers. **Core + API + Linear** — see `core/deploy_status.md`, `external/linear.md`, `ui/api/api_system.md`.

| Behavior | Tests |
| --- | --- |
| Base payload uptime/env only | `TestGetDeployStatusPayload::test_includes_uptime_without_environment`, `test_includes_environment_when_set` |
| Recent-first helper | `TestMergeTicketHelpers::test_merge_tickets_recent_first` |
| UAT state filter helper | `TestMergeTicketHelpers::test_filter_merge_tickets_by_state_keeps_uat_only` |

**Manifest pytest gate (AST-792 — full ticket):**

```bash
.venv/bin/python -m pytest \
  tests/component/external/test_linear.py \
  tests/component/utils/test_merge_ticket_log.py \
  tests/component/utils/test_deploy_status.py \
  tests/component/core/test_deploy_status.py \
  tests/component/ui/api/test_api_system.py::TestDeployStatus \
  -q
```

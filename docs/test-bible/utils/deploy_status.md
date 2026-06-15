# Deploy Status

**Test module:** `tests/component/utils/test_deploy_status.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/utils/deploy_status.py` | `tests/component/utils/test_deploy_status.py` | no |

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
| Uptime without env | `TestGetDeployStatusPayload::test_includes_uptime_without_environment` — no commit keys; `"environment" not in payload`; `merge_tickets: []` |
| Uptime + env when set | `TestGetDeployStatusPayload::test_includes_environment_when_set` — `staging`, `1h1m`; no commit keys; `merge_tickets: []` |

---

### AST-681

**`merge_tickets` on `get_deploy_status_payload()`** — full stored history, most recent first; always present (empty list when log empty). Read-only via `read_merge_ticket_log`; append covered in `merge_ticket_log.md`.

| Behavior | Tests |
| --- | --- |
| Reversed order for API | `TestGetDeployStatusPayload::test_merge_tickets_most_recent_first` |
| Empty log → `[]` | `TestGetDeployStatusPayload::test_merge_tickets_empty_when_log_empty` |
| API route includes key | `TestDeployStatus::test_admin_returns_payload`, `test_admin_omits_environment_when_unset` in `test_api_system.py` |

**Manifest pytest gate (AST-681 — run with merge_ticket_log + API):**

```bash
.venv/bin/python -m pytest \
  tests/component/utils/test_merge_ticket_log.py \
  tests/component/utils/test_deploy_status.py \
  tests/component/ui/api/test_api_system.py::TestDeployStatus \
  -q
```


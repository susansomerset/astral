# Deploy Status (core orchestration)

**Test module:** `tests/component/core/test_deploy_status.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/deploy_status.py` | `tests/component/core/test_deploy_status.py` | no |

---

### AST-792

Core `get_deploy_status_payload()` — base utils fields + `merge_tickets` filtered to **User Testing** via Linear at request time; fail closed (`merge_tickets: []`) on Linear errors. `api_system` imports this module (not utils).

| Behavior | Tests |
| --- | --- |
| UAT-only ids, most recent first | `TestCoreGetDeployStatusPayload::test_payload_includes_filtered_merge_tickets_most_recent_first` |
| Empty log → `[]` | `TestCoreGetDeployStatusPayload::test_payload_empty_merge_tickets_when_log_empty` |
| Linear failure → `[]` | `TestCoreGetDeployStatusPayload::test_payload_empty_merge_tickets_on_linear_failure` |
| Excludes Done / non-UAT | `TestCoreGetDeployStatusPayload::test_payload_excludes_done_parents` |

**Manifest pytest gate (AST-792 — partial; see utils + external bible files):**

```bash
.venv/bin/python -m pytest tests/component/core/test_deploy_status.py -q
```

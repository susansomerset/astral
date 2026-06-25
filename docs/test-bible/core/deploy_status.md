# Deploy Status (core orchestration)

**Test module:** `tests/component/core/test_deploy_status.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/deploy_status.py` | `tests/component/core/test_deploy_status.py` | no |

---

### AST-792

**Superseded at runtime by AST-800:** prep-uat **full log rebuild** + log-only read replaced per-poll Linear filter. Historical AST-792 filter tests removed; see **AST-800**.

---

### AST-800

Log-only `get_deploy_status_payload()` — base utils fields + `merge_tickets` from `read_merge_ticket_log()` most-recent-first; **no** runtime Linear API on admin poll.

| Behavior | Tests |
| --- | --- |
| Log entries, most recent first | `TestCoreGetDeployStatusPayload::test_payload_merge_tickets_from_log_most_recent_first` |
| Empty log → `[]` | `TestCoreGetDeployStatusPayload::test_payload_empty_merge_tickets_when_log_empty` |

**Manifest pytest gate (AST-800 — partial; see external + dev bible files):**

```bash
.venv/bin/python -m pytest tests/component/core/test_deploy_status.py -q
```

# api_slack

**Test module:** `tests/component/ui/api/test_api_slack.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_slack.py` | `tests/component/ui/api/test_api_slack.py` | no |

---

### AST-1069 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1069-slack-events-api-webhook-ingress`.

Transport-only `POST /api` + `CONTACT_CONFIG["events_http_path"]` → `receive_slack_events_http`. No ui→external. Core: **`docs/test-bible/core/contact.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Challenge JSON / empty ack / 401 | `src/ui/api/api_slack.py` | **`TestAst1069SlackEventsApi`** |

**Broken / obsolete:** none — new blueprint.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_slack.py::TestAst1069SlackEventsApi \
  -q
```

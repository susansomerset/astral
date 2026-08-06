# api_slack

**Test module:** `tests/component/ui/api/test_api_slack.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_slack.py` | `tests/component/ui/api/test_api_slack.py` | no |

---

### AST-1069 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1069-slack-events-api-webhook-ingress`.

Thin Events blueprint: `POST /api` + `CONTACT_CONFIG["events_http_path"]` → `receive_slack_events_http`. Core ingress: **`docs/test-bible/core/contact.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| HTTP Events wire | `src/ui/api/api_slack.py` | historically named in AST-1069 manifests; live coverage for durable SoT under **AST-1207** below |

**Broken / obsolete:** none at map create (AST-1207).

**Integration:** none.

### AST-1207 · AST-1203

**Parent:** [AST-1203 — Need to be able to set the "Debug" flag for Slack messages](https://linear.app/astralcareermatch/issue/AST-1203/need-to-be-able-to-set-the-debug-flag-for-slack-messages). **Publish:** `origin/sub/AST-1203/AST-1207-slack-events-contact-inbound-durable-debug`.

Events blueprint passes `debug=slack_debug_enabled()` into `receive_slack_events_http`; **no** `ui_llm_debug`. Core SoT + Style D depth: **`docs/test-bible/core/contact.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Durable SoT wire + no ui_llm_debug | `src/ui/api/api_slack.py` | **`TestAst1207SlackEventsDebugSot`** |

**Broken / obsolete:** none — SoT swap on existing blueprint.

**Integration:** no existing scenario asserts Events debug SoT — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_slack.py::TestAst1207SlackEventsDebugSot \
  -q
```

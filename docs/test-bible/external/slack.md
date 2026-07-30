# slack (external)

**Test module:** `tests/component/external/test_slack.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/external/slack.py` | `tests/component/external/test_slack.py` | no |

---

### AST-1069 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1069-slack-events-api-webhook-ingress`.

Signature verify (HMAC v0 + skew), URL challenge parse, `chat.postMessage` behind `require_controlled_external_io`. Socket Mode helper is local-script only (not component-tested here). Contact HTTP: **`docs/test-bible/core/contact.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Verify / challenge / gated post_message | `src/external/slack.py` | **`TestAst1069ExternalSlack`** |

**Broken / obsolete:** none — new external module.

**Integration:** no existing scenario — no revision.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_slack.py::TestAst1069ExternalSlack \
  -q
```

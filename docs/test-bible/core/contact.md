# Contact

**Test module:** `tests/component/core/test_contact.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/contact.py` | `tests/component/core/test_contact.py` | no |

---

### AST-1066 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1066-contact-core-module-and-contact-config`.

Contact scaffold: `slack_listen_enabled`, `contact_skills` / `contact_skill_keys`, `slack_env_names`, `non_production_reply_prefix`. Config: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Listen default / empty skills copy / env names / prefix / no TASK_CONFIG collision | `src/core/contact.py` | **`TestAst1066ContactScaffold`** |

**Broken / obsolete:** none — new module.

**Integration:** no existing scenario asserts Contact — no revision.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1066ContactConfig \
  tests/component/core/test_contact.py::TestAst1066ContactScaffold \
  -q
```

---

### AST-1069 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1069-slack-events-api-webhook-ingress`.

`receive_slack_events_http` (verify / challenge / ack+schedule) + `handle_slack_event` (listen gate, `event_id` dedupe, `app_mention` + DM `message`). External HMAC/post: **`docs/test-bible/external/slack.md`**. Blueprint: **`docs/test-bible/ui/api/api_slack.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Listen/dedupe/type/DM filters; HTTP 401/challenge/ack | `src/core/contact.py` | **`TestAst1069ContactSlackIngress`** |

**Broken / obsolete:** none — additive Contact ingress.

**Integration:** no existing scenario asserts Slack Events — no revision.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_contact.py::TestAst1069ContactSlackIngress \
  tests/component/external/test_slack.py::TestAst1069ExternalSlack \
  tests/component/ui/api/test_api_slack.py::TestAst1069SlackEventsApi \
  -q
```

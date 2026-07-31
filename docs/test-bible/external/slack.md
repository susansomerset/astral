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

---

### AST-1068 · AST-1043

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1068-slack-resolve-via-get-candidate-id`.

`fetch_user_profile` via `users.info` (gated). Contact: **`docs/test-bible/core/contact.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| users.info profile / gate / ok:false | `src/external/slack.py` | **`TestAst1068FetchUserProfile`** |

**Broken / obsolete:** none — additive.

**Integration:** no existing scenario — no revision.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_slack.py::TestAst1068FetchUserProfile \
  -q
```

### AST-1105 · AST-1043 (UAT)

**Parent:** [AST-1043 — Slack Bot Agent](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent). **Publish:** `origin/sub/AST-1043/AST-1105-uat-slack-username-display-activity-profile`.

`fetch_user_profile` returns Slack `user.name` as `username` (empty when omitted). Core/Profile/UI: **`docs/test-bible/core/contact.md`**, **`docs/test-bible/utils/config.md`**, **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| username on users.info parse | `src/external/slack.py` | revised **`TestAst1068FetchUserProfile`**; **`TestAst1105FetchUserProfileUsername`** |

**Broken / obsolete:** AST-1068 assert omitted `username` — revised.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_slack.py::TestAst1068FetchUserProfile \
  tests/component/external/test_slack.py::TestAst1105FetchUserProfileUsername \
  -q
```

